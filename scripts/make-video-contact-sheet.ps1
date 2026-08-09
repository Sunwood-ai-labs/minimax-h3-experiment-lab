[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string[]]$InputPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$OutputPath,

    [ValidateRange(2, 60)]
    [int]$FrameCount = 8,

    [ValidateRange(1, 12)]
    [int]$Columns = 4,

    [ValidateRange(80, 1200)]
    [int]$TileWidth = 320,

    [ValidateRange(80, 1200)]
    [int]$TileHeight = 180,

    [switch]$Overwrite
)

$ErrorActionPreference = 'Stop'

function Resolve-ToolPath {
    param([string]$Name)

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) {
        throw "$Name.exe was not found in PATH. Install FFmpeg and retry."
    }

    return $command.Source
}

function Resolve-InputPath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return (Resolve-Path -LiteralPath $Path).Path
    }

    return (Resolve-Path -LiteralPath (Join-Path (Get-Location).Path $Path)).Path
}

function Get-RepoRelativePath {
    param(
        [string]$Path,
        [string]$RepoRoot
    )

    $normalizedPath = [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
    $normalizedRoot = [System.IO.Path]::GetFullPath($RepoRoot).TrimEnd('\', '/')
    if ($normalizedPath.Equals($normalizedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return '.'
    }

    $rootPrefix = $normalizedRoot + [System.IO.Path]::DirectorySeparatorChar
    if ($normalizedPath.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $normalizedPath.Substring($rootPrefix.Length).Replace('\', '/')
    }

    return $Path
}

function Get-VideoProbe {
    param(
        [string]$Ffprobe,
        [string]$Path
    )

    $jsonText = & $Ffprobe -v error -select_streams v:0 -show_entries stream=width,height,avg_frame_rate,nb_frames -show_entries format=duration -of json -- $Path 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($jsonText -join ''))) {
        throw "ffprobe failed for $Path"
    }

    $json = ($jsonText -join [Environment]::NewLine) | ConvertFrom-Json
    $stream = @($json.streams)[0]
    if (-not $stream -or -not $json.format.duration) {
        throw "Video stream or duration is missing for $Path"
    }

    return [pscustomobject]@{
        width = [int]$stream.width
        height = [int]$stream.height
        durationSeconds = [double]::Parse([string]$json.format.duration, [Globalization.CultureInfo]::InvariantCulture)
        fps = [string]$stream.avg_frame_rate
        frames = if ($stream.nb_frames) { [int64]$stream.nb_frames } else { $null }
    }
}

if ($InputPath.Count -eq 0) {
    throw 'At least one video input is required.'
}

$ffmpeg = Resolve-ToolPath -Name 'ffmpeg'
$ffprobe = Resolve-ToolPath -Name 'ffprobe'
$repoRoot = (& git rev-parse --show-toplevel 2>$null).Trim()
if ([string]::IsNullOrWhiteSpace($repoRoot)) {
    $repoRoot = (Get-Location).Path
}

$inputs = @($InputPath | ForEach-Object { Resolve-InputPath -Path $_ })
$outputFullPath = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
    [System.IO.Path]::GetFullPath($OutputPath)
} else {
    [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $OutputPath))
}

$outputDirectory = Split-Path -Parent $outputFullPath
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null

if ((Test-Path -LiteralPath $outputFullPath) -and -not $Overwrite) {
    throw "Output already exists. Use -Overwrite to replace it: $outputFullPath"
}

$probes = @()
foreach ($input in $inputs) {
    $probes += Get-VideoProbe -Ffprobe $ffprobe -Path $input
}

$rowsPerSource = [int][Math]::Ceiling($FrameCount / [double]$Columns)
$scaleFilter = 'scale={0}:{1}:force_original_aspect_ratio=decrease' -f $TileWidth, $TileHeight
$padFilter = 'pad={0}:{1}:(ow-iw)/2:(oh-ih)/2:color=black' -f $TileWidth, $TileHeight
$tileFilter = 'tile={0}x{1}:padding=6:margin=6' -f $Columns, $rowsPerSource
$filters = [System.Collections.Generic.List[string]]::new()

for ($index = 0; $index -lt $inputs.Count; $index++) {
    $durationText = $probes[$index].durationSeconds.ToString('0.######', [Globalization.CultureInfo]::InvariantCulture)
    $fpsFilter = '{0}/{1}' -f $FrameCount, $durationText
    $filters.Add(('[{0}:v]fps={1},{2},{3},{4}[sheet{0}]' -f $index, $fpsFilter, $scaleFilter, $padFilter, $tileFilter))
}

$sheetLabels = @((0..($inputs.Count - 1) | ForEach-Object { '[sheet{0}]' -f $_ }))
if ($inputs.Count -eq 1) {
    $filters.Add('[sheet0]copy[contact]')
} else {
    $filters.Add(('{0}vstack=inputs={1}[contact]' -f ($sheetLabels -join ''), $inputs.Count))
}
$filterComplex = $filters -join ';'

$ffmpegArgs = @('-hide_banner', '-loglevel', 'error')
if ($Overwrite) {
    $ffmpegArgs += '-y'
} else {
    $ffmpegArgs += '-n'
}

foreach ($input in $inputs) {
    $ffmpegArgs += @('-i', $input)
}

$ffmpegArgs += @(
    '-filter_complex', $filterComplex,
    '-map', '[contact]',
    '-frames:v', '1',
    '-q:v', '2',
    $outputFullPath
)

& $ffmpeg @ffmpegArgs
if ($LASTEXITCODE -ne 0) {
    throw "FFmpeg failed while creating $outputFullPath"
}

$sourceRecords = @()
for ($index = 0; $index -lt $inputs.Count; $index++) {
    $input = $inputs[$index]
    $probe = $probes[$index]
    $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $input
    $sampleTimes = @(
        0..($FrameCount - 1) | ForEach-Object {
            [Math]::Round((($_ + 0.5) * $probe.durationSeconds / $FrameCount), 3)
        }
    )

    $sourceRecords += [ordered]@{
        row = $index + 1
        path = Get-RepoRelativePath -Path $input -RepoRoot $repoRoot
        bytes = (Get-Item -LiteralPath $input).Length
        sha256 = $hash.Hash
        width = $probe.width
        height = $probe.height
        durationSeconds = [Math]::Round($probe.durationSeconds, 6)
        fps = $probe.fps
        frames = $probe.frames
        sampleTimesSeconds = $sampleTimes
    }
}

$outputHash = Get-FileHash -Algorithm SHA256 -LiteralPath $outputFullPath
$manifestPath = Join-Path $outputDirectory ('{0}.json' -f [System.IO.Path]::GetFileNameWithoutExtension($outputFullPath))
$manifest = [ordered]@{
    schema = 'minimax-h3-video-contact-sheet/v1'
    generatedAt = (Get-Date).ToString('o')
    sources = $sourceRecords
    sampling = [ordered]@{
        frameCountPerSource = $FrameCount
        columns = $Columns
        rowsPerSource = $rowsPerSource
        tileWidth = $TileWidth
        tileHeight = $TileHeight
        order = 'Each source occupies one row block; frames advance left-to-right, then top-to-bottom.'
    }
    output = [ordered]@{
        path = Get-RepoRelativePath -Path $outputFullPath -RepoRoot $repoRoot
        bytes = (Get-Item -LiteralPath $outputFullPath).Length
        sha256 = $outputHash.Hash
        format = [System.IO.Path]::GetExtension($outputFullPath).TrimStart('.').ToLowerInvariant()
    }
}

$manifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding utf8

[pscustomobject]@{
    output = $outputFullPath
    manifest = $manifestPath
    sourceCount = $inputs.Count
    frameCountPerSource = $FrameCount
    columns = $Columns
    rowsPerSource = $rowsPerSource
}
