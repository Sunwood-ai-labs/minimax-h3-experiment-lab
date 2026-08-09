[CmdletBinding()]
param(
    [string]$RepoPath = '.'
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath $RepoPath).Path
$experimentRoot = Join-Path $repo 'experiments'
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()
$allowedStatuses = @('planned', 'running', 'verified', 'partial', 'failed')
$functionalCategories = @(
    '01-baseline',
    '02-low-step-generation',
    '03-reference-conditioned',
    '04-acceleration',
    '05-temporal-continuity',
    '06-production-pipelines'
)
$records = @()

function Test-RequiredProperty {
    param(
        [object]$Object,
        [string]$Name,
        [string]$Path
    )

    if (-not ($Object.PSObject.Properties.Name -contains $Name)) {
        $errors.Add("$Path is missing required property '$Name'.")
        return $false
    }

    return $true
}

$experimentDirs = Get-ChildItem -LiteralPath $experimentRoot -Directory -Recurse |
    Where-Object { $_.Name -ne '_template' -and (Test-Path -LiteralPath (Join-Path $_.FullName 'experiment.json')) }

foreach ($dir in $experimentDirs) {
    $relativeDir = $dir.FullName.Substring($repo.Length + 1).Replace('\', '/')
    $category = ($relativeDir -split '/')[1]
    if ($category -notin $functionalCategories) {
        $errors.Add("$relativeDir is outside the functional experiment categories: $($functionalCategories -join ', ').")
    }

    $jsonPath = Join-Path $dir.FullName 'experiment.json'
    $readmePath = Join-Path $dir.FullName 'README.md'

    try {
        $record = Get-Content -Raw -LiteralPath $jsonPath | ConvertFrom-Json
    } catch {
        $errors.Add("$relativeDir/experiment.json is not valid JSON: $($_.Exception.Message)")
        continue
    }

    $required = @('id', 'date', 'category', 'status', 'sources', 'conditions', 'runs')
    foreach ($name in $required) {
        [void](Test-RequiredProperty -Object $record -Name $name -Path "$relativeDir/experiment.json")
    }

    if (($record.status -as [string]) -notin $allowedStatuses) {
        $errors.Add("$relativeDir/experiment.json has unsupported status '$($record.status)'.")
    }

    if (($record.category -as [string]) -ne $category) {
        $errors.Add("$relativeDir/experiment.json category '$($record.category)' does not match directory category '$category'.")
    }

    if (-not (Test-Path -LiteralPath $readmePath)) {
        $errors.Add("$relativeDir is missing README.md.")
    }

    if (@($record.sources).Count -eq 0) {
        $warnings.Add("$relativeDir has no sources; add sources or explain why the experiment is local-only.")
    }

    $records += [pscustomobject]@{
        id = $record.id
        path = $relativeDir
        status = $record.status
    }
}

$indexPath = Join-Path $experimentRoot 'index.md'
if (Test-Path -LiteralPath $indexPath) {
    $indexText = Get-Content -Raw -LiteralPath $indexPath

    foreach ($match in [regex]::Matches($indexText, '\]\(([^)]+)\)')) {
        $link = $match.Groups[1].Value
        if ($link -match '^(https?://|#)') {
            continue
        }

        $cleanLink = $link.Split('#')[0]
        if ([string]::IsNullOrWhiteSpace($cleanLink)) {
            continue
        }

        $resolved = Join-Path (Split-Path $indexPath -Parent) $cleanLink.Replace('/', '\')
        if (-not (Test-Path -LiteralPath $resolved)) {
            $errors.Add("experiments/index.md link does not resolve: $link")
        }
    }
} else {
    $errors.Add('experiments/index.md is missing.')
}

$result = [ordered]@{
    ok = ($errors.Count -eq 0)
    repo = $repo
    experimentCount = $records.Count
    records = $records
    errors = @($errors)
    warnings = @($warnings)
}

$result | ConvertTo-Json -Depth 8
if ($errors.Count -gt 0) {
    exit 1
}
