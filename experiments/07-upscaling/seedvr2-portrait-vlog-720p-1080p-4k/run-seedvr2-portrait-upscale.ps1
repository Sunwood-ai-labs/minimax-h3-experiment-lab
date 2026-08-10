[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('1080p', '4k')]
    [string]$Target,
    [int]$SegmentCount = 7,
    [double]$SegmentSeconds = 0.75,
    [double]$TotalSeconds = 5.166667,
    [int]$TimeoutSeconds = 3600
)

$ErrorActionPreference = 'Stop'
$experimentDir = $PSScriptRoot
$runner = Join-Path (Join-Path $experimentDir '..\seedvr2-4k-rtx4090') 'run-seedvr2-api.ps1'
$workflow = Join-Path $experimentDir "workflows/seedvr2_portrait_vlog_${Target}_segment_api.json"
$runDir = Join-Path $experimentDir 'runs'
$manifestPath = Join-Path $runDir "seedvr2_portrait_vlog_${Target}_segments_manifest.json"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$rows = @()

for ($i = 0; $i -lt $SegmentCount; $i++) {
    $start = [math]::Round($i * $SegmentSeconds, 6)
    $duration = if ($i -eq ($SegmentCount - 1)) {
        [math]::Round($TotalSeconds - $start, 6)
    } else {
        $SegmentSeconds
    }
    $name = ('seedvr2_portrait_vlog_{0}_seg{1:d2}' -f $Target, $i)
    $prefix = 'video/seedvr2_portrait_vlog_seedvr2_{0}_seg{1:d2}' -f $Target, $i
    Write-Host "=== $Target segment $i start=$start duration=$duration ==="
    & $runner -Workflow $workflow -ReportName $name -ReportDir $runDir -StartTime $start -Duration $duration -OutputPrefix $prefix -TimeoutSeconds $TimeoutSeconds
    if (-not $?) { throw "$Target segment $i failed" }
    $rows += [ordered]@{
        target = $Target
        segment = $i
        start_time = $start
        duration = $duration
        report = (Join-Path $runDir "$name.json")
        output_prefix = $prefix
    }
}

$rows | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
Write-Host "Manifest: $manifestPath"
