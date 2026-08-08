[CmdletBinding()]
param(
    [ValidateSet('4090', '3060')]
    [string]$Gpu = '3060',
    [ValidateRange(1, 65535)]
    [int]$Port = 8189,
    [string]$Workflow = (Join-Path (Split-Path $PSScriptRoot -Parent) 'workflows/post_conditions_turbo_864x480_api.json'),
    [string]$OutputPrefix = 'video/MiniMax_H3_post_conditions_864x480_8step_turbo',
    [bool]$LowVram = $true,
    [long]$Seed = -1,
    [int]$TimeoutSeconds = 7200,
    [switch]$SkipModelHashes
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$baseUrl = "http://localhost:$Port"
$outputDir = Join-Path $projectRoot "runtime/$Gpu/output"
$reportDir = Join-Path $projectRoot "runtime/$Gpu/benchmark"
$ffprobeCommand = Get-Command ffprobe -ErrorAction SilentlyContinue
$ffmpegCommand = Get-Command ffmpeg -ErrorAction SilentlyContinue

if (-not (Test-Path -LiteralPath $Workflow)) {
    throw "Workflow not found: $Workflow"
}

New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$graph = Get-Content -Raw -LiteralPath $Workflow | ConvertFrom-Json
$nodes = @($graph.PSObject.Properties)
$randomNode = $nodes | Where-Object { $_.Value.class_type -eq 'RandomNoise' } | Select-Object -First 1
if ($null -ne $randomNode -and $Seed -ge 0) {
    $randomNode.Value.inputs.noise_seed = $Seed
}
$loraNode = $nodes | Where-Object { $_.Value.class_type -eq 'MiniMaxH3TurboLoRA' } | Select-Object -First 1
if ($null -ne $loraNode) {
    $loraNode.Value.inputs.low_vram = $LowVram
}
$lowVramApplied = $null -ne $loraNode
$saveNode = $nodes | Where-Object { $_.Value.class_type -eq 'SaveVideo' } | Select-Object -First 1
if ($null -eq $saveNode) {
    throw 'SaveVideo node was not found in the workflow'
}
$saveNode.Value.inputs.filename_prefix = $OutputPrefix
$request = @{ prompt = $graph; client_id = [guid]::NewGuid().Guid } | ConvertTo-Json -Depth 50

$started = Get-Date
$before = @{}
Get-ChildItem -LiteralPath $outputDir -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    $before[$_.FullName] = $_.LastWriteTimeUtc
}

$response = Invoke-RestMethod -Method Post -Uri "$baseUrl/prompt" -ContentType 'application/json' -Body $request
$promptId = [string]$response.prompt_id
Write-Host "Started $promptId at $($started.ToString('o'))"

$historyItem = $null
$deadline = $started.AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 5
    try {
        $history = Invoke-RestMethod -Uri "$baseUrl/history/$promptId"
        $property = $history.PSObject.Properties | Where-Object Name -eq $promptId | Select-Object -First 1
        if ($null -ne $property) {
            $historyItem = $property.Value
            $status = [string]$historyItem.status.status_str
            if ($status -in @('success', 'error')) {
                break
            }
        }
    } catch {
        # The prompt may not be in history until execution has started.
    }
}

$ended = Get-Date
$after = @(
    Get-ChildItem -LiteralPath $outputDir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { -not $before.ContainsKey($_.FullName) -or $_.LastWriteTimeUtc -gt $before[$_.FullName] } |
        Select-Object FullName, Length, LastWriteTime
)

$mediaEvidence = @()
$nullSink = if ($IsWindows) { 'NUL' } else { '/dev/null' }
foreach ($file in $after | Where-Object { $_.FullName -match '\.(mp4|webm|mov)$' }) {
    $probe = $null
    $probeError = $null
    if ($null -ne $ffprobeCommand) {
        try {
            $probeRaw = (& $ffprobeCommand.Source -v error -show_streams -show_format -of json $file.FullName 2>&1 | Out-String).Trim()
            $probe = $probeRaw | ConvertFrom-Json
        } catch {
            $probeError = $_.Exception.Message
        }
    } else {
        $probeError = 'ffprobe was not found on PATH'
    }

    $blackEvents = @()
    $signalStats = @()
    $mediaError = $null
    $previousErrorActionPreference = $ErrorActionPreference
    if ($null -ne $ffmpegCommand) {
        try {
            $ErrorActionPreference = 'Continue'
            $blackEvents = @(
                & $ffmpegCommand.Source -hide_banner -loglevel info -i $file.FullName -vf 'blackdetect=d=0.1:pic_th=0.98' -an -f null $nullSink 2>&1 |
                    ForEach-Object { $_.ToString() } |
                    Where-Object { $_ -match 'black_(start|end)' }
            )
            $signalStats = @(
                & $ffmpegCommand.Source -hide_banner -loglevel info -i $file.FullName -vf 'signalstats,metadata=mode=print:file=-' -frames:v 1 -an -f null $nullSink 2>&1 |
                    ForEach-Object { $_.ToString() } |
                    Where-Object { $_ -match 'lavfi\.signalstats\.' }
            )
        } catch {
            $mediaError = $_.Exception.Message
        } finally {
            $ErrorActionPreference = $previousErrorActionPreference
        }
    } else {
        $mediaError = 'ffmpeg was not found on PATH'
    }

    $mediaEvidence += [ordered]@{
        path = $file.FullName
        bytes = $file.Length
        last_write_time = $file.LastWriteTime
        ffprobe = $probe
        ffprobe_error = $probeError
        blackdetect = [ordered]@{
            interval_count = $blackEvents.Count
            events = $blackEvents
        }
        signalstats_first_frame = $signalStats
        media_check_error = $mediaError
    }
}

$composeService = "h3-$Gpu"
$composeLog = @(& docker compose logs --no-color --timestamps $composeService 2>$null | Select-String -Pattern 'Prompt executed in' | Select-Object -Last 1)
$status = if ($null -eq $historyItem) { 'timeout' } else { [string]$historyItem.status.status_str }
$conditions = [ordered]@{
    workflow = (Resolve-Path -LiteralPath $Workflow).Path
    low_vram_requested = $LowVram
    low_vram_applied = $lowVramApplied
    runtime = [ordered]@{
        compose_service = $composeService
        dynamic_vram = ($Gpu -eq '3060')
        sage_attention_requested = ($Gpu -eq '3060')
        cuda_module_loading = 'LAZY'
    }
}
$videoNode = $nodes | Where-Object { $_.Value.class_type -eq 'MiniMaxH3ImageToVideo' } | Select-Object -First 1
if ($null -ne $videoNode) {
    $conditions.width = $videoNode.Value.inputs.width
    $conditions.height = $videoNode.Value.inputs.height
    $conditions.frames = $videoNode.Value.inputs.length
}
$schedulerNode = $nodes | Where-Object { $_.Value.class_type -eq 'BasicScheduler' } | Select-Object -First 1
if ($null -ne $schedulerNode) {
    $conditions.steps = $schedulerNode.Value.inputs.steps
    $conditions.scheduler = $schedulerNode.Value.inputs.scheduler
}
$samplerNode = $nodes | Where-Object { $_.Value.class_type -eq 'KSamplerSelect' } | Select-Object -First 1
if ($null -ne $samplerNode) {
    $conditions.sampler = $samplerNode.Value.inputs.sampler_name
}
$unetNode = $nodes | Where-Object { $_.Value.class_type -eq 'UNETLoader' } | Select-Object -First 1
if ($null -ne $unetNode) {
    $conditions.base = $unetNode.Value.inputs.unet_name
}
$clipNode = $nodes | Where-Object { $_.Value.class_type -eq 'CLIPLoader' } | Select-Object -First 1
if ($null -ne $clipNode) {
    $conditions.text_encoder = $clipNode.Value.inputs.clip_name
}
$vaeSnapshot = @(
    $nodes |
        Where-Object { $_.Value.class_type -eq 'VAELoader' } |
        ForEach-Object {
            [ordered]@{
                node_id = $_.Name
                vae_name = $_.Value.inputs.vae_name
            }
        }
)
if ($vaeSnapshot.Count -gt 0) {
    $conditions.vae = $vaeSnapshot
}
$easyCacheNode = $nodes | Where-Object { $_.Value.class_type -eq 'EasyCache' } | Select-Object -First 1
if ($null -ne $easyCacheNode) {
    $conditions.easycache = [ordered]@{
        reuse_threshold = $easyCacheNode.Value.inputs.reuse_threshold
        start_percent = $easyCacheNode.Value.inputs.start_percent
        end_percent = $easyCacheNode.Value.inputs.end_percent
        verbose = $easyCacheNode.Value.inputs.verbose
    }
}
$loraSnapshot = $nodes | Where-Object { $_.Value.class_type -eq 'MiniMaxH3TurboLoRA' } | Select-Object -First 1
if ($null -ne $loraSnapshot) {
    $conditions.lora = $loraSnapshot.Value.inputs.lora_name
    $conditions.lora_low_vram = $loraSnapshot.Value.inputs.low_vram
}
$modelOnlyLoraSnapshot = $nodes | Where-Object { $_.Value.class_type -eq 'LoraLoaderModelOnly' } | Select-Object -First 1
if ($null -ne $modelOnlyLoraSnapshot) {
    $conditions.lora_loader = 'LoraLoaderModelOnly'
    $conditions.lora = $modelOnlyLoraSnapshot.Value.inputs.lora_name
    $conditions.lora_strength_model = $modelOnlyLoraSnapshot.Value.inputs.strength_model
}
$inputImageNodes = @($nodes | Where-Object { $_.Value.class_type -eq 'LoadImage' })
if ($inputImageNodes.Count -gt 0) {
    $conditions.input_images = @($inputImageNodes | ForEach-Object { [string]$_.Value.inputs.image })
}
if ($null -ne $randomNode) {
    $conditions.seed = $randomNode.Value.inputs.noise_seed
}

function Invoke-H3Tool {
    param(
        [Parameter(Mandatory)]
        [string]$CommandName,
        [string[]]$Arguments = @()
    )

    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        return [ordered]@{
            available = $false
            path = $null
            exit_code = $null
            output = @()
        }
    }

    try {
        $output = @(
            & $command.Source @Arguments 2>&1 |
                ForEach-Object { $_.ToString() }
        )
        return [ordered]@{
            available = $true
            path = $command.Source
            exit_code = $LASTEXITCODE
            output = $output
        }
    } catch {
        return [ordered]@{
            available = $true
            path = $command.Source
            exit_code = $LASTEXITCODE
            output = @($_.Exception.Message)
        }
    }
}

$hostOs = $null
$hostComputer = $null
try {
    $hostOs = Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture, LastBootUpTime
    $hostComputer = Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, TotalPhysicalMemory
} catch {
    $hostOs = [ordered]@{ error = $_.Exception.Message }
}

$containerId = ((& docker compose ps -q $composeService 2>$null | Select-Object -First 1 | Out-String).Trim())
$imageId = $null
$imageInfo = $null
if ($containerId) {
    $imageId = ((& docker inspect --format '{{.Image}}' $containerId 2>$null | Select-Object -First 1 | Out-String).Trim())
}
if ($imageId) {
    try {
        $imageRaw = (& docker image inspect $imageId 2>&1 | Out-String).Trim()
        $imageObject = @($imageRaw | ConvertFrom-Json)[0]
        $imageInfo = [ordered]@{
            id = $imageObject.Id
            repo_tags = @($imageObject.RepoTags)
            repo_digests = @($imageObject.RepoDigests)
            created = $imageObject.Created
            size = $imageObject.Size
        }
    } catch {
        $imageInfo = [ordered]@{ error = $_.Exception.Message }
    }
}

$systemStats = $null
try {
    $systemStats = Invoke-RestMethod -Uri "$baseUrl/system_stats"
} catch {
    $systemStats = [ordered]@{ error = $_.Exception.Message }
}

$trackedFiles = @(
    (Resolve-Path -LiteralPath $Workflow).Path,
    (Join-Path $projectRoot 'compose.yaml'),
    (Join-Path $projectRoot 'Dockerfile'),
    (Join-Path $projectRoot 'scripts/run-h3-post-condition.ps1'),
    (Join-Path $projectRoot 'docker/entrypoint.sh'),
    (Join-Path $projectRoot 'docker/h3-runtime-patch.py'),
    (Join-Path $projectRoot 'docker/download-h3-model.sh'),
    (Join-Path $projectRoot 'assets/i2v_start_frame_generation.md'),
    (Join-Path $projectRoot 'assets/i2v_start_frame_1280x704.png'),
    (Join-Path $projectRoot 'assets/i2v_start_frame_864x480.png')
)
$projectFileEvidence = @()
foreach ($trackedFile in $trackedFiles | Select-Object -Unique) {
    if (Test-Path -LiteralPath $trackedFile) {
        $hash = Get-FileHash -LiteralPath $trackedFile -Algorithm SHA256
        $relative = $trackedFile.Substring($projectRoot.Length).TrimStart('\', '/')
        $projectFileEvidence += [ordered]@{
            path = $relative
            bytes = (Get-Item -LiteralPath $trackedFile).Length
            sha256 = $hash.Hash
        }
    }
}

$modelNames = @()
if ($null -ne $conditions.base) {
    $modelNames += [string]$conditions.base
}
if ($null -ne $conditions.text_encoder) {
    $modelNames += [string]$conditions.text_encoder
}
foreach ($vae in @($conditions.vae)) {
    if ($null -ne $vae -and $null -ne $vae.vae_name) {
        $modelNames += [string]$vae.vae_name
    }
}
if ($null -ne $conditions.lora) {
    $modelNames += [string]$conditions.lora
}
$modelEvidence = @()
foreach ($modelName in $modelNames | Sort-Object -Unique) {
    $matches = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot 'models') -Recurse -File -Filter $modelName -ErrorAction SilentlyContinue)
    if ($matches.Count -eq 0) {
        $modelEvidence += [ordered]@{
            file_name = $modelName
            found = $false
        }
        continue
    }
    foreach ($modelFile in $matches) {
        $modelHash = $null
        $hashStatus = if ($SkipModelHashes) { 'skipped_by_parameter' } else { 'sha256' }
        if (-not $SkipModelHashes) {
            try {
                $modelHash = (Get-FileHash -LiteralPath $modelFile.FullName -Algorithm SHA256).Hash
            } catch {
                $hashStatus = "error: $($_.Exception.Message)"
            }
        }
        $modelRelative = $modelFile.FullName.Substring($projectRoot.Length).TrimStart('\', '/')
        $modelEvidence += [ordered]@{
            file_name = $modelName
            found = $true
            path = $modelRelative
            bytes = $modelFile.Length
            sha256 = $modelHash
            hash_status = $hashStatus
        }
    }
}

$inputAssetEvidence = @()
foreach ($inputImageName in @($conditions.input_images)) {
    if ([string]::IsNullOrWhiteSpace($inputImageName)) {
        continue
    }
    $inputPath = Join-Path $projectRoot "runtime/$Gpu/input/$inputImageName"
    if (-not (Test-Path -LiteralPath $inputPath)) {
        $inputAssetEvidence += [ordered]@{
            file_name = $inputImageName
            found = $false
        }
        continue
    }
    $inputFile = Get-Item -LiteralPath $inputPath
    $inputHash = (Get-FileHash -LiteralPath $inputPath -Algorithm SHA256).Hash
    $inputProbe = $null
    if ($null -ne $ffprobeCommand) {
        try {
            $inputProbeRaw = (& $ffprobeCommand.Source -v error -show_streams -show_format -of json $inputPath 2>&1 | Out-String).Trim()
            $inputProbe = $inputProbeRaw | ConvertFrom-Json
        } catch {
            $inputProbe = [ordered]@{ error = $_.Exception.Message }
        }
    }
    $inputRelative = $inputPath.Substring($projectRoot.Length).TrimStart('\', '/')
    $inputAssetEvidence += [ordered]@{
        file_name = $inputImageName
        found = $true
        path = $inputRelative
        bytes = $inputFile.Length
        sha256 = $inputHash
        ffprobe = $inputProbe
    }
}

$environment = [ordered]@{
    captured_local = (Get-Date).ToString('o')
    host = [ordered]@{
        os = $hostOs
        computer = $hostComputer
        powershell = $PSVersionTable.PSVersion.ToString()
        culture = [System.Globalization.CultureInfo]::CurrentCulture.Name
        timezone = [System.TimeZoneInfo]::Local.Id
    }
    docker = [ordered]@{
        server = (Invoke-H3Tool -CommandName 'docker' -Arguments @('version', '--format', '{{.Server.Version}}'))
        compose = (Invoke-H3Tool -CommandName 'docker' -Arguments @('compose', 'version', '--short'))
        container_id = $containerId
        image_id = $imageId
        image = $imageInfo
    }
    container_system_stats = $systemStats
    nvidia_smi = (Invoke-H3Tool -CommandName 'nvidia-smi' -Arguments @('--query-gpu=name,uuid,driver_version,memory.total,memory.used,temperature.gpu', '--format=csv,noheader'))
    project_files = $projectFileEvidence
    model_files = $modelEvidence
    input_assets = $inputAssetEvidence
    model_hashes_skipped = [bool]$SkipModelHashes
}
$report = [ordered]@{
    gpu = $Gpu
    port = $Port
    prompt_id = $promptId
    started_local = $started.ToString('o')
    ended_local = $ended.ToString('o')
    wall_seconds = [math]::Round(($ended - $started).TotalSeconds, 3)
    status = $status
    low_vram = $LowVram
    low_vram_applied = $lowVramApplied
    invocation = [ordered]@{
        gpu = $Gpu
        port = $Port
        workflow = (Resolve-Path -LiteralPath $Workflow).Path
        output_prefix = $OutputPrefix
        low_vram = $LowVram
        seed = $Seed
        timeout_seconds = $TimeoutSeconds
        skip_model_hashes = [bool]$SkipModelHashes
    }
    conditions = $conditions
    environment = $environment
    comfyui_log = ($composeLog | ForEach-Object { $_.Line })
    history_status = if ($null -eq $historyItem) { $null } else { $historyItem.status }
    output_files = $after
    media_evidence = $mediaEvidence
}
$reportPath = Join-Path $reportDir "h3-$promptId.json"
$reportJson = $report | ConvertTo-Json -Depth 40
$reportJson | Set-Content -LiteralPath $reportPath -Encoding UTF8

$markdownPath = Join-Path $reportDir "h3-$promptId.md"
$historyJson = if ($null -eq $historyItem) { 'null' } else { $historyItem.status | ConvertTo-Json -Depth 30 }
$environmentJson = $environment | ConvertTo-Json -Depth 40
$conditionsJson = $conditions | ConvertTo-Json -Depth 30
$mediaJson = $mediaEvidence | ConvertTo-Json -Depth 40
$comfyLogText = @($composeLog | ForEach-Object { $_.Line }) -join [Environment]::NewLine
if ([string]::IsNullOrWhiteSpace($comfyLogText)) {
    $comfyLogText = '(Prompt executed log was not found)'
}
$markdown = @(
    '# MiniMax-H3 実験記録',
    '',
    "- GPU: RTX $Gpu",
    "- Compose service: $composeService",
    "- Prompt ID: $promptId",
    "- Status: $status",
    "- Started: $($started.ToString('o'))",
    "- Ended: $($ended.ToString('o'))",
    "- Wall time: $($report.wall_seconds) seconds",
    "- JSON report: h3-$promptId.json",
    '',
    '## 実行条件',
    '',
    '~~~json',
    $conditionsJson,
    '~~~',
    '',
    '## 実行コマンド・パラメータ',
    '',
    '~~~json',
    ($report.invocation | ConvertTo-Json -Depth 20),
    '~~~',
    '',
    '## 環境スナップショット',
    '',
    'この環境情報は、別PCで同じ条件を再構築するために毎回保存する。モデルはファイルサイズとSHA-256を記録する。SkipModelHashesを指定した場合だけSHA-256は省略される。',
    '',
    '~~~json',
    $environmentJson,
    '~~~',
    '',
    '## ComfyUI実行ログ',
    '',
    '~~~text',
    $comfyLogText,
    '~~~',
    '',
    '## History status',
    '',
    '~~~json',
    $historyJson,
    '~~~',
    '',
    '## 出力ファイル',
    '',
    '| Path | Bytes | Last write time |',
    '|---|---:|---|'
)
foreach ($file in $after) {
    $markdown += "| $($file.FullName) | $($file.Length) | $($file.LastWriteTime) |"
}
if ($after.Count -eq 0) {
    $markdown += '| (none) |  |  |'
}
$markdown += @(
    '',
    '## メディア検証',
    '',
    'ffprobe、blackdetect、signalstatsの結果を保存する。blackdetectのinterval_countが0であることだけでは映像品質を保証しないため、必要に応じて抽出フレームも目視確認する。',
    '',
    '~~~json',
    $mediaJson,
    '~~~',
    '',
    '## 再現メモ',
    '',
    'このMarkdownと同じフォルダのJSON、参照workflow、compose.yaml、Dockerfile、モデルファイルのSHA-256を合わせて再実行する。'
)
$markdown | Set-Content -LiteralPath $markdownPath -Encoding UTF8

$indexPath = Join-Path $reportDir 'index.md'
if (-not (Test-Path -LiteralPath $indexPath)) {
    @(
        "# MiniMax-H3 $Gpu benchmark reports",
        '',
        '| Prompt ID | Status | Wall seconds | Markdown | JSON |',
        '|---|---|---:|---|---|'
    ) | Set-Content -LiteralPath $indexPath -Encoding UTF8
}
$indexContent = Get-Content -Raw -LiteralPath $indexPath
if ($indexContent -notmatch [regex]::Escape($promptId)) {
    Add-Content -LiteralPath $indexPath -Value "| $promptId | $status | $($report.wall_seconds) | [Markdown](./h3-$promptId.md) | [JSON](./h3-$promptId.json) |" -Encoding UTF8
}

Write-Host "Status: $status"
Write-Host "Wall seconds: $($report.wall_seconds)"
Write-Host "Report: $reportPath"
Write-Host "Markdown report: $markdownPath"
if ($status -eq 'error') {
    exit 1
}
