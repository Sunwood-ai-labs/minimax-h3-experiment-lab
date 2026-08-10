[CmdletBinding()]
param(
    [int]$StartSegment = 0,
    [int]$SegmentCount = 9,
    [double]$SegmentSeconds = 0.75,
    [double]$TotalSeconds = 6.583333,
    [int]$TimeoutSeconds = 3600
)

$ErrorActionPreference = 'Stop'
$experimentDir = $PSScriptRoot
$runner = Join-Path $experimentDir 'run-seedvr2-api.ps1'
$workflow = Join-Path $experimentDir 'workflows/seedvr2_upscale_4k_segment_api.json'
$runDir = Join-Path $experimentDir 'runs'
$manifestPath = Join-Path $runDir 'seedvr2_4k_segments_manifest.json'
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$rows = @()

for ($i = $StartSegment; $i -lt $SegmentCount; $i++) {
    $start = [math]::Round($i * $SegmentSeconds, 6)
    $duration = if ($i -eq ($SegmentCount - 1)) {
        [math]::Round($TotalSeconds - $start, 6)
    } else {
        $SegmentSeconds
    }
    $name = ('seedvr2_4k_seg{0:d2}' -f $i)
    $prefix = "video/seedvr2_experiment_4k_seg{0:d2}" -f $i
    Write-Host "=== Segment $i start=$start duration=$duration ==="
    & $runner -Workflow $workflow -ReportName $name -ReportDir $runDir -StartTime $start -Duration $duration -OutputPrefix $prefix -TimeoutSeconds $TimeoutSeconds
    $runnerSucceeded = $?
    if (-not $runnerSucceeded) {
        throw "Segment $i failed"
    }
    $rows += [ordered]@{
        segment = $i
        start_time = $start
        duration = $duration
        report = (Join-Path $experimentDir "$name.json")
        output_prefix = $prefix
    }
}

$rows | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
Write-Host "Manifest: $manifestPath"
