[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$videoDir = Join-Path $projectRoot 'runtime/4090/output/video'
$simDir = Join-Path $projectRoot 'sunwood-x-simulator-h3-image-upscale-2026-08-10'
$assetDir = Join-Path $simDir 'assets'
$outputPath = Join-Path $assetDir 'seedvr2_portrait_vlog_video_comparison_seedvr2_7s.mp4'
$base = Join-Path (Join-Path $projectRoot 'runtime/4090/input') 'seedvr2_portrait_vlog_h3_i2v_7s_720p_baseline.mp4'
$p1080 = Join-Path $videoDir 'seedvr2_portrait_vlog_7s_1080p.mp4'
$p4k = Join-Path $videoDir 'seedvr2_portrait_vlog_7s_4k.mp4'
$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
$ffprobe = (Get-Command ffprobe -ErrorAction Stop).Source
foreach ($input in @($base, $p1080, $p4k)) { if (-not (Test-Path -LiteralPath $input -PathType Leaf)) { throw "Missing input: $input" } }

$filter = "[0:v]setpts=PTS-STARTPTS,scale=360:640:flags=lanczos,drawtext=text='720p H3':fontfile='C\:/Windows/Fonts/arial.ttf':fontsize=24:fontcolor=white:box=1:boxcolor=black@0.68:boxborderw=8:x=12:y=12[v0];[1:v]setpts=PTS-STARTPTS,scale=360:640:flags=lanczos,drawtext=text='1080p SeedVR2':fontfile='C\:/Windows/Fonts/arial.ttf':fontsize=24:fontcolor=white:box=1:boxcolor=black@0.68:boxborderw=8:x=12:y=12[v1];[2:v]setpts=PTS-STARTPTS,scale=360:640:flags=lanczos,drawtext=text='4K SeedVR2':fontfile='C\:/Windows/Fonts/arial.ttf':fontsize=24:fontcolor=white:box=1:boxcolor=black@0.68:boxborderw=8:x=12:y=12[v2];[v0][v1][v2]hstack=inputs=3:shortest=1[tiles];[tiles]pad=1080:720:0:80:color=0x080b12,drawtext=text='MiniMax-H3 I2V / SeedVR2 synchronized video comparison':fontfile='C\:/Windows/Fonts/arial.ttf':fontsize=24:fontcolor=white:x=20:y=25[v]"
$args = @('-y', '-hide_banner', '-loglevel', 'error', '-i', $base, '-i', $p1080, '-i', $p4k, '-filter_complex', $filter, '-map', '[v]', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', $outputPath)
& $ffmpeg @args
if ($LASTEXITCODE -ne 0) { throw "ffmpeg tile failed with exit code $LASTEXITCODE" }

$probe = ((& $ffprobe -v error -show_streams -show_format -of json -- $outputPath | Out-String) | ConvertFrom-Json)
$video = @($probe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)[0]
$audio = @($probe.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)[0]
$evidence = [ordered]@{
    path = [IO.Path]::GetFullPath($outputPath)
    bytes = (Get-Item -LiteralPath $outputPath).Length
    sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $outputPath).Hash
    audioRemoved = ($null -eq $audio)
    synchronized = $true
    layout = 'three simultaneous hstack panels; no temporal concatenation between panels'
    inputs = @($base, $p1080, $p4k)
    ffprobe = [ordered]@{
        videoCodec = $video.codec_name
        width = [int]$video.width
        height = [int]$video.height
        frames = if ($video.nb_frames) { [int]$video.nb_frames } else { $null }
        durationSeconds = [double]$probe.format.duration
        fps = $video.r_frame_rate
        audioStreams = @($probe.streams | Where-Object { $_.codec_type -eq 'audio' }).Count
    }
}
$evidence | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $simDir 'tile-7s-evidence.json') -Encoding UTF8
$evidence | ConvertTo-Json -Depth 20
