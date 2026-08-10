[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$InputPath,
    [Parameter(Mandatory)][string]$OutputPath,
    [string]$FfmpegBinDir = '',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$input = (Resolve-Path -LiteralPath $InputPath).Path
$output = [System.IO.Path]::GetFullPath($OutputPath)
$outputDir = Split-Path -Parent $output
New-Item -ItemType Directory -Force $outputDir | Out-Null

$ffmpegPath = $null
$ffprobePath = $null
if ([string]::IsNullOrWhiteSpace($FfmpegBinDir)) {
    $ffmpegCommand = Get-Command ffmpeg -ErrorAction SilentlyContinue
    $ffprobeCommand = Get-Command ffprobe -ErrorAction SilentlyContinue
    if ($null -ne $ffmpegCommand) { $ffmpegPath = $ffmpegCommand.Source }
    if ($null -ne $ffprobeCommand) { $ffprobePath = $ffprobeCommand.Source }
} else {
    $binDir = (Resolve-Path -LiteralPath $FfmpegBinDir).Path
    $ffmpegPath = Join-Path $binDir 'ffmpeg.exe'
    $ffprobePath = Join-Path $binDir 'ffprobe.exe'
}
if ([string]::IsNullOrWhiteSpace($ffmpegPath) -or [string]::IsNullOrWhiteSpace($ffprobePath) -or
    -not (Test-Path -LiteralPath $ffmpegPath -PathType Leaf) -or -not (Test-Path -LiteralPath $ffprobePath -PathType Leaf)) {
    throw 'ffmpeg and ffprobe must be available on PATH or supplied with -FfmpegBinDir.'
}
if ((Test-Path -LiteralPath $output) -and -not $Force) {
    throw "Output already exists. Use -Force: $output"
}

& $ffmpegPath -hide_banner -loglevel error -y -i $input `
    -map 0:v:0 -map 0:a:0? -t 5.000 -frames:v 120 `
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p `
    -c:a aac -b:a 128k -ar 32000 -ac 2 -movflags +faststart $output
if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed with exit code $LASTEXITCODE" }

$probe = (& $ffprobePath -v error -select_streams v:0 `
    -show_entries stream=width,height,nb_frames,duration,r_frame_rate `
    -show_entries format=duration -of json -- $output | Out-String) | ConvertFrom-Json
$stream = @($probe.streams)[0]
$duration = [double]$probe.format.duration
$frames = [int]$stream.nb_frames
if ([int]$stream.width -ne 1280 -or [int]$stream.height -ne 704 -or $frames -ne 120 -or [math]::Abs($duration - 5.0) -gt 0.01) {
    throw "Unexpected exact-5s output: $($stream.width)x$($stream.height), frames=$frames, duration=$duration"
}

[pscustomobject]@{
    path = $output
    bytes = (Get-Item -LiteralPath $output).Length
    width = [int]$stream.width
    height = [int]$stream.height
    frames = $frames
    durationSeconds = $duration
    sha256 = (Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash
} | ConvertTo-Json -Depth 4
