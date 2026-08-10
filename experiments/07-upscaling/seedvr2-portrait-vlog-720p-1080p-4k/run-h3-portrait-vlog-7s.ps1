[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent)
$runner = Join-Path $root 'scripts\run-h3-post-condition.ps1'
$workflow = Join-Path $PSScriptRoot 'workflows/h3_portrait_vlog_i2v_7s_704x1280_api.json'

& $runner `
    -Gpu 4090 `
    -Port 8188 `
    -Workflow $workflow `
    -OutputPrefix 'video/seedvr2_portrait_vlog_h3_i2v_7s_704x1280' `
    -LowVram:$false `
    -SageAttention:$false `
    -Seed 2026081013 `
    -TimeoutSeconds 3600 `
    -SkipModelHashes
