[CmdletBinding()]
param(
    [string]$RepoPath = '.'
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath $RepoPath).Path
$errors = [System.Collections.Generic.List[string]]::new()
$records = [System.Collections.Generic.List[object]]::new()
$tracked = @(& git -C $repo ls-files)
$repoPrefix = $repo.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

function Get-RepoRelativePath {
    param([string]$Path)
    $full = [System.IO.Path]::GetFullPath($Path)
    if (-not $full.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) { return $null }
    return $full.Substring($repoPrefix.Length).Replace('\', '/')
}

function Test-TrackedFile {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        $errors.Add("$Label is missing: $Path")
        return $false
    }
    $relative = Get-RepoRelativePath $Path
    if ($null -eq $relative -or $tracked -notcontains $relative) {
        $errors.Add("$Label is not Git-tracked: $relative")
        return $false
    }
    return $true
}

function Test-JsonFile {
    param([string]$Path, [string]$Label)
    if (-not (Test-TrackedFile -Path $Path -Label $Label)) { return }
    try {
        Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json | Out-Null
    } catch {
        $errors.Add("$Label is not valid JSON: $($_.Exception.Message)")
    }
}

function Add-RecordPath {
    param(
        [System.Collections.Generic.List[string]]$List,
        [object]$Value
    )
    if ($null -eq $Value) { return }
    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text) -or $text -match '^<repo-root>' -or $text -match '\.\.\.$') { return }
    if ($text -notin $List) { $List.Add($text) }
}

$requiredRootFiles = @(
    'compose.yaml',
    'Dockerfile',
    '.env.example',
    'docker/download-h3-model.sh',
    'docker/entrypoint.sh',
    'workflows',
    'models/README.md',
    'models/manifest.json',
    'experiments/README.md',
    'experiments/video-links.md',
    'scripts/validate-experiment-lab.ps1'
)
foreach ($relative in $requiredRootFiles) {
    $path = Join-Path $repo $relative.Replace('/', '\')
    if (Test-Path -LiteralPath $path -PathType Container) {
        if (-not (Get-ChildItem -LiteralPath $path -File | Where-Object { $_.Name -ne '.gitkeep' })) {
            $errors.Add("Required directory is empty: $relative")
        }
    } else {
        [void](Test-TrackedFile -Path $path -Label "Required reproducibility file '$relative'")
    }
}

$rootReadme = Get-Content -Raw -LiteralPath (Join-Path $repo 'README.md')
$rootReadmeJa = Get-Content -Raw -LiteralPath (Join-Path $repo 'README.ja.md')
$tilePaths = @(
    'experiments/01-baseline/gpu-baseline/previews/contact-sheet.jpg',
    'experiments/01-baseline/3060-black-output/previews/contact-sheet.jpg',
    'experiments/02-low-step-generation/lightx2v-4step/previews/contact-sheet.jpg',
    'experiments/03-reference-conditioned/i2v-scenes/previews/contact-sheet.jpg',
    'experiments/03-reference-conditioned/ref2va-6v20/previews/contact-sheet.jpg',
    'experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/previews/contact-sheet.jpg',
    'experiments/04-acceleration/sol-sage-easycache-4scenes-7s/previews/contact-sheet.jpg',
    'experiments/05-temporal-continuity/motion-context-3segment/previews/contact-sheet.jpg',
    'experiments/06-production-pipelines/catcafe-vlog-5segment/previews/contact-sheet.jpg',
    'experiments/06-production-pipelines/jpop-mv-5segment/previews/contact-sheet.jpg'
)
foreach ($tileRelative in $tilePaths) {
    $tilePath = Join-Path $repo $tileRelative.Replace('/', '\')
    [void](Test-TrackedFile -Path $tilePath -Label "Public tile '$tileRelative'")
    if ($rootReadme -notmatch [regex]::Escape("./$tileRelative") -or $rootReadmeJa -notmatch [regex]::Escape("./$tileRelative")) {
        $errors.Add("Both root README files must preview the tracked tile: $tileRelative")
    }
}

$modelManifestPath = Join-Path $repo 'models/manifest.json'
$modelManifest = $null
$manifestFilenames = [System.Collections.Generic.List[string]]::new()
if (Test-TrackedFile -Path $modelManifestPath -Label 'Model manifest') {
    try {
        $modelManifest = Get-Content -Raw -LiteralPath $modelManifestPath | ConvertFrom-Json
        foreach ($entry in @($modelManifest.files)) {
            if ($null -ne $entry -and $entry.PSObject.Properties.Name -contains 'filename') {
                $manifestFilenames.Add([string]$entry.filename)
                if ($entry.PSObject.Properties.Name -notcontains 'repository' -or
                    $entry.PSObject.Properties.Name -notcontains 'revision' -or
                    $entry.PSObject.Properties.Name -notcontains 'sourcePath' -or
                    $entry.PSObject.Properties.Name -notcontains 'target' -or
                    $entry.PSObject.Properties.Name -notcontains 'bytes' -or
                    $entry.PSObject.Properties.Name -notcontains 'sha256') {
                    $errors.Add("Model manifest entry is incomplete: $($entry.filename)")
                }
            }
        }
        foreach ($profileName in @('fl2va', 'ref2va', 'fl2va-lightx2v', 'ref2va-lightx2v', 'legacy-turbo')) {
            $profile = @($modelManifest.profiles.PSObject.Properties | Where-Object Name -eq $profileName)
            if ($profile.Count -eq 0) { $errors.Add("Model manifest profile is missing: $profileName") }
        }
    } catch {
        $errors.Add("Model manifest cannot be parsed: $($_.Exception.Message)")
    }
}

$workflowModelNames = [System.Collections.Generic.List[string]]::new()
function Register-WorkflowModels {
    param([string]$Path)
    try {
        $content = Get-Content -Raw -LiteralPath $Path
        foreach ($match in [regex]::Matches($content, '(?i)[A-Za-z0-9][A-Za-z0-9_.-]*\.safetensors')) {
            $name = $match.Value
            if ($name -notin $workflowModelNames) { $workflowModelNames.Add($name) }
        }
    } catch {
        $errors.Add("Workflow model scan failed for $Path`: $($_.Exception.Message)")
    }
}

$rootWorkflowFiles = Get-ChildItem -LiteralPath (Join-Path $repo 'workflows') -File -Filter '*.json' -ErrorAction SilentlyContinue
foreach ($rootWorkflow in $rootWorkflowFiles) {
    Test-JsonFile -Path $rootWorkflow.FullName -Label "Root workflow '$($rootWorkflow.Name)'"
    Register-WorkflowModels -Path $rootWorkflow.FullName
}

$experimentDirs = Get-ChildItem -LiteralPath (Join-Path $repo 'experiments') -Directory -Recurse |
    Where-Object { $_.Name -ne '_template' -and (Test-Path -LiteralPath (Join-Path $_.FullName 'experiment.json')) }

foreach ($dir in $experimentDirs) {
    $recordRelative = $dir.FullName.Substring($repo.Length + 1).Replace('\', '/')
    $jsonPath = Join-Path $dir.FullName 'experiment.json'
    try {
        $record = Get-Content -Raw -LiteralPath $jsonPath | ConvertFrom-Json
    } catch {
        $errors.Add("$recordRelative/experiment.json cannot be parsed: $($_.Exception.Message)")
        continue
    }

    $workflowPaths = [System.Collections.Generic.List[string]]::new()
    foreach ($run in @($record.runs)) {
        if ($run.PSObject.Properties.Name -contains 'workflow') { Add-RecordPath -List $workflowPaths -Value $run.workflow }
    }
    if ($record.PSObject.Properties.Name -contains 'workflows') {
        foreach ($workflow in @($record.workflows)) { Add-RecordPath -List $workflowPaths -Value $workflow }
    }
    if ($record.PSObject.Properties.Name -contains 'scripts' -and $null -ne $record.scripts -and $record.scripts.PSObject.Properties.Name -contains 'workflow_files') {
        foreach ($workflow in @($record.scripts.workflow_files)) { Add-RecordPath -List $workflowPaths -Value $workflow }
    }
    if ($record.PSObject.Properties.Name -contains 'artifacts' -and $null -ne $record.artifacts -and $record.artifacts -isnot [array] -and $record.artifacts.PSObject.Properties.Name -contains 'workflows') {
        foreach ($entry in @($record.artifacts.workflows)) {
            if ($entry -isnot [string] -and $entry.PSObject.Properties.Name -contains 'path') { Add-RecordPath -List $workflowPaths -Value $entry.path }
            else { Add-RecordPath -List $workflowPaths -Value $entry }
        }
    }

    foreach ($workflowRelative in $workflowPaths) {
        $workflowPath = Join-Path $dir.FullName $workflowRelative.Replace('/', '\')
        if (-not (Test-Path -LiteralPath $workflowPath -PathType Leaf)) {
            $errors.Add("$recordRelative workflow does not resolve from the record directory: $workflowRelative")
            continue
        }
        if (-not (Test-TrackedFile -Path $workflowPath -Label "$recordRelative workflow '$workflowRelative'")) { continue }
        Test-JsonFile -Path $workflowPath -Label "$recordRelative workflow '$workflowRelative'"
        Register-WorkflowModels -Path $workflowPath
    }

    foreach ($property in @('composeFile', 'dockerfile', 'envExample', 'modelDownloadScript')) {
        if ($record.PSObject.Properties.Name -contains 'reproduction' -and $record.reproduction.PSObject.Properties.Name -contains $property) {
            $relative = [string]$record.reproduction.$property
            $path = Join-Path $dir.FullName $relative.Replace('/', '\')
            [void](Test-TrackedFile -Path $path -Label "$recordRelative reproduction.$property")
        }
    }

    if ($record.PSObject.Properties.Name -contains 'environment' -and $null -ne $record.environment -and $record.environment.PSObject.Properties.Name -contains 'composeFile') {
        $composeRelative = [string]$record.environment.composeFile
        $composePath = Join-Path $dir.FullName $composeRelative.Replace('/', '\')
        [void](Test-TrackedFile -Path $composePath -Label "$recordRelative environment.composeFile")
    }

    if ($record.PSObject.Properties.Name -contains 'scripts' -and $null -ne $record.scripts) {
        foreach ($property in @('workflow_builder', 'runner', 'merger')) {
            if ($record.scripts.PSObject.Properties.Name -contains $property) {
                $relative = [string]$record.scripts.$property
                $path = Join-Path $dir.FullName $relative.Replace('/', '\')
                [void](Test-TrackedFile -Path $path -Label "$recordRelative scripts.$property")
            }
        }
    }

    $records.Add([pscustomobject]@{ id = $record.id; path = $recordRelative; workflowCount = $workflowPaths.Count })
}

if ($null -ne $modelManifest) {
    foreach ($modelName in $workflowModelNames) {
        $entry = @($modelManifest.files | Where-Object { [string]$_.filename -eq $modelName })
        if ($entry.Count -eq 0) {
            $errors.Add("Workflow model is not covered by models/manifest.json: $modelName")
            continue
        }
        $modelEntry = $entry[0]
        if ([int64]$modelEntry.bytes -le 0 -or [string]$modelEntry.sha256 -notmatch '^[A-Fa-f0-9]{64}$') {
            $errors.Add("Workflow model has invalid size or SHA-256 in manifest: $modelName")
        }
    }
}

$result = [ordered]@{
    ok = ($errors.Count -eq 0)
    repo = $repo
    recordCount = $records.Count
    records = @($records)
    workflowModelNames = @($workflowModelNames | Sort-Object)
    errors = @($errors)
}
$result | ConvertTo-Json -Depth 8
if ($errors.Count -gt 0) { exit 1 }
