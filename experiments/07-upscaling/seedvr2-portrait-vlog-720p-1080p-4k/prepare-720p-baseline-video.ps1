[CmdletBinding()]
param(
    [string]$InputPath,
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$defaultInput = Join-Path (Join-Path $projectRoot 'runtime/4090/output/video') 'seedvr2_portrait_vlog_h3_i2v_7s_704x1280_00001_.mp4'
$defaultOutput = Join-Path (Join-Path $projectRoot 'runtime/4090/input') 'seedvr2_portrait_vlog_h3_i2v_7s_720p_baseline.mp4'
$InputPath = if ([string]::IsNullOrWhiteSpace($InputPath)) { $defaultInput } else { $InputPath }
$OutputPath = if ([string]::IsNullOrWhiteSpace($OutputPath)) { $defaultOutput } else { $OutputPath }
$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) { throw "Missing H3 video: $InputPath" }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPath) | Out-Null

$args = @(
    '-y', '-hide_banner', '-loglevel', 'error',
    '-i', $InputPath,
    '-map', '0:v:0', '-map', '0:a?',
    '-vf', 'scale=720:1280:flags=lanczos',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'copy', '-movflags', '+faststart',
    $OutputPath
)
& $ffmpeg @args
if ($LASTEXITCODE -ne 0) { throw "720p baseline encode failed with exit code $LASTEXITCODE" }

$OutputPath
