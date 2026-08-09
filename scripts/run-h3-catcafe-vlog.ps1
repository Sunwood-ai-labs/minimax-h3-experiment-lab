[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8188,
    [string]$WorkflowDir = (Join-Path (Split-Path $PSScriptRoot -Parent) 'experiments/2026-08-09/h3-japanese-catcafe-vlog-5segment'),
    [int]$TimeoutSeconds = 7200,
    [ValidateRange(1, 5)]
    [int]$StartSegment = 1
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$baseUrl = "http://127.0.0.1:$Port"
$experimentDir = $WorkflowDir
$outputDir = Join-Path $projectRoot 'runtime/4090/output'
$inputDir = Join-Path $projectRoot 'runtime/4090/input/h3_cat_cafe_vlog'
$videoOutputDir = Join-Path $outputDir 'video/h3_cat_cafe_vlog'
$progressPath = Join-Path $experimentDir 'run-progress.json'
$ffprobe = (Get-Command ffprobe -ErrorAction SilentlyContinue).Source
$ffmpeg = (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source

if (-not (Test-Path -LiteralPath $WorkflowDir -PathType Container)) {
    throw "Workflow directory not found: $WorkflowDir"
}
if ($null -eq $ffprobe -or $null -eq $ffmpeg) {
    throw 'ffprobe and ffmpeg are required on PATH.'
}

New-Item -ItemType Directory -Force -Path $inputDir, $videoOutputDir | Out-Null

function Get-ExecutionTiming {
    param([Parameter(Mandatory = $true)]$HistoryItem, [Parameter(Mandatory = $true)][datetime]$FallbackStart)

    $startMessage = @($HistoryItem.status.messages | Where-Object { $_[0] -eq 'execution_start' } | Select-Object -First 1)
    $endMessage = @($HistoryItem.status.messages | Where-Object { $_[0] -in @('execution_success', 'execution_error') } | Select-Object -Last 1)
    $executionStart = $FallbackStart
    $executionEnd = Get-Date
    if ($startMessage.Count -gt 0) {
        $executionStart = [DateTimeOffset]::FromUnixTimeMilliseconds([long]$startMessage[0][1].timestamp).LocalDateTime
    }
    if ($endMessage.Count -gt 0) {
        $executionEnd = [DateTimeOffset]::FromUnixTimeMilliseconds([long]$endMessage[0][1].timestamp).LocalDateTime
    }
    [pscustomobject]@{
        executionStart = $executionStart.ToString('o')
        executionEnd = $executionEnd.ToString('o')
        executionSeconds = [math]::Round(($executionEnd - $executionStart).TotalSeconds, 3)
    }
}

function Get-VideoEvidence {
    param([Parameter(Mandatory = $true)][string]$Path)

    $probe = (& $ffprobe -v error -show_streams -show_format -of json -- $Path 2>&1 | Out-String).Trim() | ConvertFrom-Json
    $video = @($probe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)[0]
    $audio = @($probe.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)[0]
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $blackEvents = @(
            & $ffmpeg -hide_banner -loglevel info -i $Path -vf 'blackdetect=d=0.1:pic_th=0.98' -an -f null NUL 2>&1 |
                ForEach-Object { $_.ToString() } |
                Where-Object { $_ -match 'black_(start|end)' }
        )
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash
    [ordered]@{
        path = [System.IO.Path]::GetFullPath($Path)
        bytes = (Get-Item -LiteralPath $Path).Length
        sha256 = $hash
        ffprobe = [ordered]@{
            videoCodec = [string]$video.codec_name
            audioCodec = if ($null -ne $audio) { [string]$audio.codec_name } else { $null }
            width = [int]$video.width
            height = [int]$video.height
            frames = if ($null -ne $video.nb_frames) { [int]$video.nb_frames } else { $null }
            durationSeconds = [double]$probe.format.duration
            fps = [string]$video.r_frame_rate
            audioSampleRate = if ($null -ne $audio) { [int]$audio.sample_rate } else { $null }
            audioChannels = if ($null -ne $audio) { [int]$audio.channels } else { $null }
        }
        blackdetectIntervals = [int]($blackEvents.Count / 2)
        blackdetectRaw = @($blackEvents)
    }
}

function Save-Progress {
    param([Parameter(Mandatory = $true)]$Manifest)
    $Manifest | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $progressPath -Encoding UTF8
}

$existingManifest = $null
if (Test-Path -LiteralPath $progressPath -PathType Leaf) {
    try { $existingManifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $progressPath | ConvertFrom-Json } catch { $existingManifest = $null }
}
$manifest = if ($StartSegment -gt 1 -and $null -ne $existingManifest) {
    $existingManifest
} else {
    [ordered]@{
        status = 'running'
        startedAt = (Get-Date).ToString('o')
        endpoint = $baseUrl
        workflowDir = (Resolve-Path -LiteralPath $WorkflowDir).Path
        gpuService = 'h3-4090'
        segments = @()
    }
}
$manifest.status = 'running'
$manifest.resumeFromSegment = $StartSegment
$manifest.segments = @($manifest.segments)
Save-Progress $manifest

for ($segment = $StartSegment; $segment -le 5; $segment++) {
    $workflowPath = Join-Path $WorkflowDir ("segment_{0:00}_api.json" -f $segment)
    if (-not (Test-Path -LiteralPath $workflowPath -PathType Leaf)) {
        throw "Workflow not found: $workflowPath"
    }

    $graph = Get-Content -Raw -Encoding UTF8 -LiteralPath $workflowPath | ConvertFrom-Json
    $request = @{ prompt = $graph; client_id = [guid]::NewGuid().Guid } | ConvertTo-Json -Depth 100 -Compress
    $requestBytes = [System.Text.Encoding]::UTF8.GetBytes($request)
    $submittedAt = Get-Date
    $response = Invoke-RestMethod -Method Post -Uri "$baseUrl/prompt" -ContentType 'application/json; charset=utf-8' -Body $requestBytes
    $promptId = [string]$response.prompt_id
    if ([string]::IsNullOrWhiteSpace($promptId)) {
        throw "ComfyUI did not return prompt_id for segment $segment."
    }

    Write-Host ("segment {0}/5 queued: {1}" -f $segment, $promptId)
    $deadline = $submittedAt.AddSeconds($TimeoutSeconds)
    $historyItem = $null
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 5
        try {
            $history = Invoke-RestMethod -Uri "$baseUrl/history/$promptId"
            $property = $history.PSObject.Properties | Where-Object Name -eq $promptId | Select-Object -First 1
            if ($null -ne $property) {
                $historyItem = $property.Value
                $status = [string]$historyItem.status.status_str
                if ($status -in @('success', 'error')) {
                    break
                }
            }
        } catch {
            # ComfyUI can return a transient error before the history record exists.
        }
    }

    if ($null -eq $historyItem) {
        $manifest.status = 'timeout'
        $manifest.error = "Timed out waiting for segment $segment ($promptId)."
        Save-Progress $manifest
        throw $manifest.error
    }

    $status = [string]$historyItem.status.status_str
    $timing = Get-ExecutionTiming -HistoryItem $historyItem -FallbackStart $submittedAt
    $result = [ordered]@{
        segment = $segment
        promptId = $promptId
        status = $status
        submittedAt = $submittedAt.ToString('o')
        queueWallSeconds = [math]::Round(((Get-Date) - $submittedAt).TotalSeconds, 3)
        timing = $timing
    }

    if ($status -ne 'success') {
        $result.errorMessages = @($historyItem.status.messages)
        $manifest.segments += $result
        $manifest.status = 'error'
        Save-Progress $manifest
        throw ("segment {0} failed: {1}" -f $segment, $promptId)
    }

    $outputLeaf = "segment_{0:00}_*.mp4" -f $segment
    $outputFile = Get-ChildItem -LiteralPath $videoOutputDir -Filter $outputLeaf -File |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    if ($null -eq $outputFile) {
        $manifest.segments += $result
        $manifest.status = 'error'
        $manifest.error = "No output video found for segment $segment."
        Save-Progress $manifest
        throw $manifest.error
    }

    $result.output = Get-VideoEvidence -Path $outputFile.FullName
    if ($segment -lt 5) {
        $contextPath = Join-Path $inputDir ("segment_{0:00}.mp4" -f $segment)
        Copy-Item -LiteralPath $outputFile.FullName -Destination $contextPath -Force
        $result.contextInput = [System.IO.Path]::GetFullPath($contextPath)
    }
    $manifest.segments += $result
    Save-Progress $manifest
    Write-Host ("segment {0}/5 success: {1} sec, {2}" -f $segment, $timing.executionSeconds, $outputFile.FullName)
}

$manifest.status = 'verified_runs_pending_merge'
$manifest | Add-Member -NotePropertyName completedAt -NotePropertyValue ((Get-Date).ToString('o')) -Force
Save-Progress $manifest
$manifest | ConvertTo-Json -Depth 30
