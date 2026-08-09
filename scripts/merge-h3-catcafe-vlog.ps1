[CmdletBinding()]
param(
    [string]$ExperimentDir = (Join-Path (Split-Path $PSScriptRoot -Parent) 'experiments/06-production-pipelines/catcafe-vlog-5segment')
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$outputDir = Join-Path $projectRoot 'runtime/4090/output/video/h3_cat_cafe_vlog'
$mergeDir = Join-Path $ExperimentDir 'outputs'
$mergedPath = Join-Path $mergeDir 'h3_cat_cafe_vlog_5segment_merged.mp4'
$ffmpeg = (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source
$ffprobe = (Get-Command ffprobe -ErrorAction SilentlyContinue).Source
if ($null -eq $ffmpeg -or $null -eq $ffprobe) { throw 'ffmpeg and ffprobe are required on PATH.' }
New-Item -ItemType Directory -Force -Path $mergeDir | Out-Null

$inputs = @()
for ($segment = 1; $segment -le 5; $segment++) {
    $leaf = "segment_{0:00}_*.mp4" -f $segment
    $file = Get-ChildItem -LiteralPath $outputDir -Filter $leaf -File | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $file) { throw "Missing segment output: $leaf" }
    $inputs += $file.FullName
}

$filterParts = @()
for ($index = 0; $index -lt $inputs.Count; $index++) {
    $filterParts += "[$index`:v:0][$index`:a:0]"
}
$filter = ($filterParts -join '') + 'concat=n=5:v=1:a=1[v][a]'
$ffmpegArgs = @('-y', '-hide_banner', '-loglevel', 'error')
foreach ($input in $inputs) { $ffmpegArgs += @('-i', $input) }
$ffmpegArgs += @('-filter_complex', $filter, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', $mergedPath)
$oldEap = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    $ffmpegOutput = & $ffmpeg @ffmpegArgs 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $oldEap
}
if ($exitCode -ne 0) { throw "ffmpeg merge failed: $ffmpegOutput" }

$probe = ((& $ffprobe -v error -show_streams -show_format -of json -- $mergedPath 2>&1 | Out-String).Trim() | ConvertFrom-Json)
$video = @($probe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)[0]
$audio = @($probe.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)[0]
$oldEap = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    $blackEvents = @(& $ffmpeg -hide_banner -loglevel info -i $mergedPath -vf 'blackdetect=d=0.1:pic_th=0.98' -an -f null NUL 2>&1 | ForEach-Object { $_.ToString() } | Where-Object { $_ -match 'black_(start|end)' })
} finally {
    $ErrorActionPreference = $oldEap
}

$evidence = [ordered]@{
    path = [IO.Path]::GetFullPath($mergedPath)
    inputs = @($inputs | ForEach-Object { [IO.Path]::GetFullPath($_) })
    bytes = (Get-Item -LiteralPath $mergedPath).Length
    sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $mergedPath).Hash
    method = 'ffmpeg concat filter; libx264 crf 18; AAC 192k; faststart'
    ffprobe = [ordered]@{
        videoCodec = $video.codec_name
        audioCodec = if ($null -ne $audio) { $audio.codec_name } else { $null }
        width = [int]$video.width
        height = [int]$video.height
        frames = if ($video.nb_frames) { [int]$video.nb_frames } else { $null }
        durationSeconds = [double]$probe.format.duration
        fps = $video.r_frame_rate
        audioSampleRate = if ($null -ne $audio) { [int]$audio.sample_rate } else { $null }
        audioChannels = if ($null -ne $audio) { [int]$audio.channels } else { $null }
    }
    blackdetectIntervals = [int]($blackEvents.Count / 2)
    blackdetectRaw = @($blackEvents)
}
$evidence | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $ExperimentDir 'merge.json') -Encoding UTF8
$progressPath = Join-Path $ExperimentDir 'run-progress.json'
if (Test-Path -LiteralPath $progressPath -PathType Leaf) {
    $progress = Get-Content -Raw -Encoding UTF8 -LiteralPath $progressPath | ConvertFrom-Json
    $progress.status = 'verified'
    $progress | Add-Member -NotePropertyName mergedOutput -NotePropertyValue ([pscustomobject]$evidence) -Force
    $progress | Add-Member -NotePropertyName completedAt -NotePropertyValue ((Get-Date).ToString('o')) -Force
    $progress | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $progressPath -Encoding UTF8
}
$evidence | ConvertTo-Json -Depth 20
