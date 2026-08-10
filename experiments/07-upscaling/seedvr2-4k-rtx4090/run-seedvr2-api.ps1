[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Workflow,
    [Parameter(Mandatory)]
    [string]$ReportName,
    [Nullable[double]]$StartTime,
    [Nullable[double]]$Duration,
    [string]$OutputPrefix,
    [string]$ReportDir,
    [int]$Port = 8188,
    [int]$TimeoutSeconds = 7200
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$ReportDir = if ([string]::IsNullOrWhiteSpace($ReportDir)) { Join-Path $PSScriptRoot 'runs' } else { $ReportDir }
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$ReportDir = (Resolve-Path -LiteralPath $ReportDir).Path
$workflowPath = (Resolve-Path -LiteralPath $Workflow).Path
$reportJsonPath = Join-Path $ReportDir "$ReportName.json"
$reportMarkdownPath = Join-Path $ReportDir "$ReportName.md"
$vramPath = Join-Path $ReportDir "$ReportName-vram.csv"
$vramErrorPath = Join-Path $ReportDir "$ReportName-vram.err"
$outputDir = Join-Path $root 'runtime/4090/output'
$baseUrl = "http://127.0.0.1:$Port"

$graph = Get-Content -Raw -LiteralPath $workflowPath | ConvertFrom-Json
$nodes = @($graph.PSObject.Properties)
$sliceNode = $nodes | Where-Object { $_.Value.class_type -eq 'Video Slice' } | Select-Object -First 1
if ($null -ne $sliceNode) {
    if ($null -ne $StartTime) { $sliceNode.Value.inputs.start_time = $StartTime }
    if ($null -ne $Duration) { $sliceNode.Value.inputs.duration = $Duration }
}
$saveNode = $nodes | Where-Object { $_.Value.class_type -eq 'SaveVideo' } | Select-Object -First 1
if ($null -ne $saveNode -and -not [string]::IsNullOrWhiteSpace($OutputPrefix)) {
    $saveNode.Value.inputs.filename_prefix = $OutputPrefix
}
$before = @{}
Get-ChildItem -LiteralPath $outputDir -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    $before[$_.FullName] = $_.LastWriteTimeUtc
}

$monitor = $null
$started = Get-Date
$promptId = $null
$historyItem = $null
$monitorCommand = Get-Command nvidia-smi -ErrorAction SilentlyContinue
try {
    if ($null -ne $monitorCommand) {
        $monitor = Start-Process -FilePath $monitorCommand.Source -WindowStyle Hidden -PassThru -RedirectStandardOutput $vramPath -RedirectStandardError $vramErrorPath -ArgumentList @(
            '--query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu',
            '--format=csv,noheader',
            '--loop-ms=1000'
        )
    }

    $request = @{ prompt = $graph; client_id = [guid]::NewGuid().Guid } | ConvertTo-Json -Depth 50
    $response = Invoke-RestMethod -Method Post -Uri "$baseUrl/prompt" -ContentType 'application/json' -Body $request
    $promptId = [string]$response.prompt_id
    Write-Host "Prompt ID: $promptId"

    $deadline = $started.AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 5
        try {
            $history = Invoke-RestMethod -Uri "$baseUrl/history/$promptId"
            $property = $history.PSObject.Properties | Where-Object Name -eq $promptId | Select-Object -First 1
            if ($null -ne $property) {
                $historyItem = $property.Value
                $status = [string]$historyItem.status.status_str
                Write-Host "Status: $status"
                if ($status -in @('success', 'error')) {
                    break
                }
            }
        } catch {
            Write-Verbose $_.Exception.Message
        }
    }
}
finally {
    if ($null -ne $monitor -and -not $monitor.HasExited) {
        Stop-Process -Id $monitor.Id -Force -ErrorAction SilentlyContinue
    }
}

$ended = Get-Date
$status = if ($null -eq $historyItem) { 'timeout' } else { [string]$historyItem.status.status_str }
$after = @(
    Get-ChildItem -LiteralPath $outputDir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { -not $before.ContainsKey($_.FullName) -or $_.LastWriteTimeUtc -gt $before[$_.FullName] } |
        Select-Object FullName, Length, LastWriteTime
)
$errorMessage = $null
if ($null -ne $historyItem) {
    $errorEntry = @($historyItem.status.messages | Where-Object { $_[0] -eq 'execution_error' } | Select-Object -First 1)
    if ($errorEntry.Count -gt 0) {
        $errorMessage = $errorEntry[0][1].exception_message
    }
}

$report = [ordered]@{
    experiment = 'MiniMax-H3 4090 SeedVR2 upscale'
    captured_local = (Get-Date).ToString('o')
    workflow = $workflowPath
    port = $Port
    prompt_id = $promptId
    status = $status
    started_local = $started.ToString('o')
    ended_local = $ended.ToString('o')
    wall_seconds = [math]::Round(($ended - $started).TotalSeconds, 3)
    error_message = $errorMessage
    history_status = if ($null -eq $historyItem) { $null } else { $historyItem.status }
    output_files = $after
    vram_trace = $vramPath
    parameters = [ordered]@{
        start_time = $StartTime
        duration = $Duration
        output_prefix = $OutputPrefix
    }
}
$report | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $reportJsonPath -Encoding UTF8

$markdown = @(
    '# MiniMax-H3 / SeedVR2 4090 実験記録',
    '',
    "- Status: $status",
    "- Prompt ID: $promptId",
    "- Started: $($started.ToString('o'))",
    "- Ended: $($ended.ToString('o'))",
    "- Wall time: $($report.wall_seconds) seconds",
    "- Workflow: $workflowPath",
    "- JSON: $reportJsonPath",
    "- VRAM trace: $vramPath",
    '',
    '## 出力',
    '',
    '| Path | Bytes | Last write time |',
    '|---|---:|---|'
)
foreach ($file in $after) {
    $markdown += "| $($file.FullName) | $($file.Length) | $($file.LastWriteTime) |"
}
if ($after.Count -eq 0) {
    $markdown += '| (none) |  |  |'
}
$errorText = if ([string]::IsNullOrWhiteSpace($errorMessage)) { '(none)' } else { $errorMessage }
$markdown += @('', '## Error', '', $errorText)
$markdown | Set-Content -LiteralPath $reportMarkdownPath -Encoding UTF8

Write-Host "Status: $status"
Write-Host "Wall seconds: $($report.wall_seconds)"
Write-Host "Report: $reportJsonPath"
Write-Host "Markdown: $reportMarkdownPath"
if ($status -eq 'error') {
    exit 1
}
