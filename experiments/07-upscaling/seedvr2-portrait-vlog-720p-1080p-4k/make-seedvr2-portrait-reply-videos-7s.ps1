[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$videoDir = Join-Path $projectRoot 'runtime/4090/output/video'
$input720 = Join-Path (Join-Path $projectRoot 'runtime/4090/input') 'seedvr2_portrait_vlog_h3_i2v_7s_720p_baseline.mp4'
$simDir = Join-Path $projectRoot 'sunwood-x-simulator-h3-image-upscale-2026-08-10'
$assetDir = Join-Path $simDir 'assets'
$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
$ffprobe = (Get-Command ffprobe -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path $assetDir | Out-Null

$jobs = @(
    [ordered]@{ id = '720p'; label = '720p H3 baseline'; input = $input720; output = (Join-Path $assetDir 'seedvr2_portrait_vlog_7s_720p_reply.mp4') },
    [ordered]@{ id = '1080p'; label = '1080p SeedVR2'; input = (Join-Path $videoDir 'seedvr2_portrait_vlog_7s_1080p.mp4'); output = (Join-Path $assetDir 'seedvr2_portrait_vlog_7s_1080p_reply.mp4') },
    [ordered]@{ id = '4k'; label = '4K SeedVR2'; input = (Join-Path $videoDir 'seedvr2_portrait_vlog_7s_4k.mp4'); output = (Join-Path $assetDir 'seedvr2_portrait_vlog_7s_4k_reply.mp4') }
)

$rows = @()
foreach ($job in $jobs) {
    if (-not (Test-Path -LiteralPath $job.input -PathType Leaf)) { throw "Missing input: $($job.input)" }
    $filter = "[0:v]setpts=PTS-STARTPTS,scale=404:720:flags=lanczos,pad=1080:720:338:0:color=0x080b12,drawtext=text='$($job.label)':fontfile='C\:/Windows/Fonts/arial.ttf':fontsize=28:fontcolor=white:box=1:boxcolor=black@0.68:boxborderw=8:x=20:y=20[v]"
    $args = @('-y', '-hide_banner', '-loglevel', 'error', '-i', $job.input, '-filter_complex', $filter, '-map', '[v]', '-map', '0:a?', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', $job.output)
    & $ffmpeg @args
    if ($LASTEXITCODE -ne 0) { throw "reply video encode failed: $($job.id)" }
    $probe = ((& $ffprobe -v error -show_streams -show_format -of json -- $job.output | Out-String) | ConvertFrom-Json)
    $video = @($probe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)[0]
    $audioStreams = @($probe.streams | Where-Object { $_.codec_type -eq 'audio' })
    $rows += [ordered]@{
        id = $job.id
        label = $job.label
        sourcePath = [IO.Path]::GetFullPath($job.input)
        attachmentPath = [IO.Path]::GetFullPath($job.output)
        sourceSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $job.input).Hash
        attachmentSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $job.output).Hash
        bytes = (Get-Item -LiteralPath $job.output).Length
        width = [int]$video.width
        height = [int]$video.height
        frames = if ($video.nb_frames) { [int]$video.nb_frames } else { $null }
        fps = $video.r_frame_rate
        durationSeconds = [double]$probe.format.duration
        audioStreams = $audioStreams.Count
        method = 'centered portrait source on 1080x720 black canvas; libx264 crf 18; AAC 128k'
    }
}
$rows | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $simDir 'reply-video-evidence.json') -Encoding UTF8
$rows | ConvertTo-Json -Depth 20
