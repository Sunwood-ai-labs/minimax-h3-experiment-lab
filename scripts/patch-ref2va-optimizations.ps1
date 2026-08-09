[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InputWorkflow,
    [Parameter(Mandatory = $true)]
    [string]$OutputWorkflow,
    [Parameter(Mandatory = $true)]
    [string]$OutputPrefix,
    [double]$Tau = 1.3,
    [double]$StartPercent = 0.2,
    [double]$EndPercent = 0.9,
    [int]$MinTokens = 4096,
    [ValidateSet('exact_kv', 'exact_kv_and_rows', 'off')]
    [string]$SinkConditioning = 'exact_kv_and_rows',
    [switch]$DisableSage,
    [switch]$DisableSol,
    [ValidateSet('h3', 'generic')]
    [string]$SageMode = 'h3',
    [ValidateSet('auto', 'sageattn_qk_int8_pv_fp16_cuda', 'sageattn_qk_int8_pv_fp16_triton', 'sageattn_qk_int8_pv_fp8_cuda', 'sageattn_qk_int8_pv_fp8_cuda++')]
    [string]$SageAttentionMode = 'auto',
    [ValidateRange(1, 56)]
    [int]$HeadChunks = 1
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $InputWorkflow -PathType Leaf)) {
    throw "Workflow not found: $InputWorkflow"
}

$graph = Get-Content -Raw -LiteralPath $InputWorkflow | ConvertFrom-Json
$nodes = @($graph.PSObject.Properties)
$unet = $nodes | Where-Object { $_.Value.class_type -eq 'UNETLoader' } | Select-Object -First 1
$guider = $nodes | Where-Object { $_.Value.class_type -eq 'BasicGuider' } | Select-Object -First 1
$scheduler = $nodes | Where-Object { $_.Value.class_type -eq 'BasicScheduler' } | Select-Object -First 1
$save = $nodes | Where-Object { $_.Value.class_type -eq 'SaveVideo' } | Select-Object -First 1

if ($null -eq $unet -or $null -eq $guider -or $null -eq $scheduler -or $null -eq $save) {
    throw 'Expected UNETLoader, BasicGuider, BasicScheduler, and SaveVideo nodes.'
}
if ($nodes.Value.class_type -contains 'EasyCache' -or
    $nodes.Value.class_type -contains 'MiniMaxH3MemoryEfficientSageAttentionPatch' -or
    $nodes.Value.class_type -contains 'MiniMaxLowVRAMAttention' -or
    $nodes.Value.class_type -contains 'SolAttnPatch') {
    throw 'Input workflow already contains an optimization node.'
}

$easyCache = [ordered]@{
    class_type = 'EasyCache'
    inputs = [ordered]@{
        model = @($unet.Name, 0)
        reuse_threshold = 0.3
        start_percent = 0.2
        end_percent = 0.9
        verbose = $false
    }
}
$graph | Add-Member -NotePropertyName '18' -NotePropertyValue ([pscustomobject]$easyCache)
$modelLink = @('18', 0)
$nextNodeId = 19

if (-not $DisableSage) {
    if ($SageMode -eq 'h3') {
        $sageAttention = [ordered]@{
            class_type = 'MiniMaxH3MemoryEfficientSageAttentionPatch'
            inputs = [ordered]@{
                model = $modelLink
            }
        }
    }
    else {
        $sageAttention = [ordered]@{
            class_type = 'PathchSageAttentionKJ'
            inputs = [ordered]@{
                model = $modelLink
                sage_attention = $SageAttentionMode
                allow_compile = $false
            }
        }
    }
    $sageId = [string]$nextNodeId
    $graph | Add-Member -NotePropertyName $sageId -NotePropertyValue ([pscustomobject]$sageAttention)
    $modelLink = @($sageId, 0)
    $nextNodeId++
}

if ($HeadChunks -gt 1) {
    $lowVramAttention = [ordered]@{
        class_type = 'MiniMaxLowVRAMAttention'
        inputs = [ordered]@{
            model = $modelLink
            head_chunks = $HeadChunks
        }
    }
    $lowVramId = [string]$nextNodeId
    $graph | Add-Member -NotePropertyName $lowVramId -NotePropertyValue ([pscustomobject]$lowVramAttention)
    $modelLink = @($lowVramId, 0)
    $nextNodeId++
}

if (-not $DisableSol) {
    $solAttn = [ordered]@{
        class_type = 'SolAttnPatch'
        inputs = [ordered]@{
            model = $modelLink
            tau = $Tau
            start_percent = $StartPercent
            end_percent = $EndPercent
            min_tokens = $MinTokens
            int8_qk = $true
            sink_conditioning = $SinkConditioning
            morton = $false
            morton_curve = '2d_frame'
            int8_pv = $true
            verbose = $true
            use_tma = $false
            dense_blocks = ''
        }
    }
    $solId = [string]$nextNodeId
    $graph | Add-Member -NotePropertyName $solId -NotePropertyValue ([pscustomobject]$solAttn)
    $modelLink = @($solId, 0)
}

$guider.Value.inputs.model = $modelLink
$scheduler.Value.inputs.model = $modelLink
$save.Value.inputs.filename_prefix = $OutputPrefix

$parent = Split-Path -Parent $OutputWorkflow
if ($parent) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
}
$json = $graph | ConvertTo-Json -Depth 100
$outputFullPath = [System.IO.Path]::GetFullPath($OutputWorkflow)
$utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
[System.IO.File]::WriteAllText($outputFullPath, $json, $utf8NoBom)
