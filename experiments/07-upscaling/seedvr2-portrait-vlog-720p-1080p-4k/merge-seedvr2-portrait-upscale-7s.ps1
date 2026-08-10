[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('1080p', '4k')]
    [string]$Target,
    [int]$SegmentCount = 10
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$outputDir = Join-Path $projectRoot 'runtime/4090/output/video'
$experimentDir = $PSScriptRoot
$outputPath = Join-Path $outputDir "seedvr2_portrait_vlog_7s_${Target}.mp4"
$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
$ffprobe = (Get-Command ffprobe -ErrorAction Stop).Source

$inputs = @()
for ($i = 0; $i -lt $SegmentCount; $i++) {
    $leaf = 'seedvr2_portrait_vlog_7s_seedvr2_{0}_seg{1:d2}_*.mp4' -f $Target, $i
    $file = Get-ChildItem -LiteralPath $outputDir -Filter $leaf -File | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $file) { throw "Missing output: $leaf" }
    $inputs += $file.FullName
}

$filterParts = @()
for ($index = 0; $index -lt $inputs.Count; $index++) { $filterParts += "[$index`:v:0][$index`:a:0]" }
$filter = ($filterParts -join '') + "concat=n=$SegmentCount`:v=1:a=1[v][a]"
$ffmpegArgs = @('-y', '-hide_banner', '-loglevel', 'error')
foreach ($input in $inputs) { $ffmpegArgs += @('-i', $input) }
$ffmpegArgs += @('-filter_complex', $filter, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', $outputPath)
& $ffmpeg @ffmpegArgs
if ($LASTEXITCODE -ne 0) { throw "ffmpeg merge failed with exit code $LASTEXITCODE" }

$probe = ((& $ffprobe -v error -show_streams -show_format -of json -- $outputPath | Out-String) | ConvertFrom-Json)
$video = @($probe.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)[0]
$audio = @($probe.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)[0]
$evidence = [ordered]@{
    target = $Target
    path = [IO.Path]::GetFullPath($outputPath)
    inputs = @($inputs | ForEach-Object { [IO.Path]::GetFullPath($_) })
    bytes = (Get-Item -LiteralPath $outputPath).Length
    sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $outputPath).Hash
    method = 'ffmpeg concat filter over ten SeedVR2 temporal segments; libx264 crf 18; AAC 192k; faststart'
    ffprobe = [ordered]@{
        videoCodec = $video.codec_name
        audioCodec = if ($null -ne $audio) { $audio.codec_name } else { $null }
        width = [int]$video.width
        height = [int]$video.height
        frames = if ($video.nb_frames) { [int]$video.nb_frames } else { $null }
        durationSeconds = [double]$probe.format.duration
        fps = $video.r_frame_rate
    }
}
$evidence | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $experimentDir "merge_7s_${Target}.json") -Encoding UTF8
$evidence | ConvertTo-Json -Depth 20
