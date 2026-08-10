[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = 'D:\Prj\minimax-h3-compose'
$experiment = Join-Path $root 'experiments\07-upscaling\seedvr2-portrait-vlog-720p-1080p-4k'
$runner = Join-Path $root 'scripts\run-h3-post-condition.ps1'
$workflow = Join-Path $experiment 'workflows\h3_portrait_vlog_i2v_720p_api.json'

& $runner `
  -Gpu 4090 `
  -Port 8188 `
  -Workflow $workflow `
    -OutputPrefix 'video/seedvr2_portrait_vlog_h3_i2v_704x1280' `
  -LowVram:$false `
  -SageAttention:$false `
  -Seed 2026081010 `
  -TimeoutSeconds 3600 `
  -SkipModelHashes
exit $LASTEXITCODE
