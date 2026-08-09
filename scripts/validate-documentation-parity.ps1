[CmdletBinding()]
param(
    [string]$RepoPath = '.'
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath $RepoPath).Path
$errors = [System.Collections.Generic.List[string]]::new()

function Test-Pair {
    param(
        [string]$English,
        [string]$Japanese,
        [string]$Label
    )

    $englishPath = Join-Path $repo $English.Replace('/', '\\')
    $japanesePath = Join-Path $repo $Japanese.Replace('/', '\\')
    if (-not (Test-Path -LiteralPath $englishPath -PathType Leaf)) {
        $errors.Add("$Label is missing English Markdown: $English")
    }
    if (-not (Test-Path -LiteralPath $japanesePath -PathType Leaf)) {
        $errors.Add("$Label is missing Japanese Markdown: $Japanese")
    }
}

$pairs = @(
    @{ English = 'README.md'; Japanese = 'README.ja.md'; Label = 'root README' },
    @{ English = 'LAB.en.md'; Japanese = 'LAB.md'; Label = 'lab guide' },
    @{ English = 'experiments/index.en.md'; Japanese = 'experiments/index.md'; Label = 'experiment ledger' },
    @{ English = 'experiments/video-links.md'; Japanese = 'experiments/video-links.ja.md'; Label = 'video link index' },
    @{ English = 'social/README.en.md'; Japanese = 'social/README.md'; Label = 'social index' },
    @{ English = 'models/README.md'; Japanese = 'models/README.ja.md'; Label = 'model guide' },
    @{ English = 'experiments/_template/README.en.md'; Japanese = 'experiments/_template/README.md'; Label = 'experiment template' },
    @{ English = 'DESIGN.md'; Japanese = 'DESIGN.ja.md'; Label = 'design guide' },
    @{ English = 'SECURITY.md'; Japanese = 'SECURITY.ja.md'; Label = 'security policy' },
    @{ English = 'CONTRIBUTING.md'; Japanese = 'CONTRIBUTING.ja.md'; Label = 'contribution guide' },
    @{ English = 'assets/i2v_start_frame_generation.en.md'; Japanese = 'assets/i2v_start_frame_generation.md'; Label = 'I2V start-frame record' },
    @{ English = 'docs/guide/documentation.md'; Japanese = 'docs/ja/guide/documentation.md'; Label = 'documentation policy' },
    @{ English = 'docs/index.md'; Japanese = 'docs/ja/index.md'; Label = 'documentation home' },
    @{ English = 'docs/guide/artifacts.md'; Japanese = 'docs/ja/guide/artifacts.md'; Label = 'artifact guide' },
    @{ English = 'docs/guide/experiments.md'; Japanese = 'docs/ja/guide/experiments.md'; Label = 'experiment guide' },
    @{ English = 'docs/guide/records.md'; Japanese = 'docs/ja/guide/records.md'; Label = 'record guide' },
    @{ English = 'docs/guide/reproduce.md'; Japanese = 'docs/ja/guide/reproduce.md'; Label = 'reproduction guide' },
    @{ English = 'research-notes.en.md'; Japanese = 'research-notes.md'; Label = 'research notes' },
    @{ English = 'verification-log.en.md'; Japanese = 'verification-log.md'; Label = 'verification log' },
    @{ English = 'runtime/3060/benchmark/index.md'; Japanese = 'runtime/3060/benchmark/index.ja.md'; Label = '3060 benchmark index' },
    @{ English = 'runtime/4090/benchmark/index.md'; Japanese = 'runtime/4090/benchmark/index.ja.md'; Label = '4090 benchmark index' },
    @{ English = 'experiments/02-low-step-generation/lightx2v-4step/sources.md'; Japanese = 'experiments/02-low-step-generation/lightx2v-4step/sources.ja.md'; Label = 'LightX2V source note' },
    @{ English = 'experiments/03-reference-conditioned/i2v-scenes/sources.md'; Japanese = 'experiments/03-reference-conditioned/i2v-scenes/sources.ja.md'; Label = 'I2V source note' },
    @{ English = 'experiments/03-reference-conditioned/ref2va-6v20/sources.en.md'; Japanese = 'experiments/03-reference-conditioned/ref2va-6v20/sources.md'; Label = 'ref2va source note' },
    @{ English = 'experiments/03-reference-conditioned/i2v-scenes/imagegen-prompts.md'; Japanese = 'experiments/03-reference-conditioned/i2v-scenes/imagegen-prompts.ja.md'; Label = 'I2V prompt note' },
    @{ English = 'experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/reference-prompts.md'; Japanese = 'experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/reference-prompts.ja.md'; Label = 'R2V prompt note' },
    @{ English = 'experiments/_template/sources.md'; Japanese = 'experiments/_template/sources.ja.md'; Label = 'source-note template' }
)

foreach ($pair in $pairs) {
    Test-Pair -English $pair.English -Japanese $pair.Japanese -Label $pair.Label
}

$experimentDirs = Get-ChildItem -LiteralPath (Join-Path $repo 'experiments') -Directory -Recurse |
    Where-Object { $_.Name -ne '_template' -and (Test-Path -LiteralPath (Join-Path $_.FullName 'experiment.json')) }

foreach ($dir in $experimentDirs) {
    $relative = $dir.FullName.Substring($repo.Length + 1).Replace('\\', '/')
    $readme = Join-Path $dir.FullName 'README.md'
    $english = Join-Path $dir.FullName 'README.en.md'
    if (-not (Test-Path -LiteralPath $readme -PathType Leaf)) {
        $errors.Add("$relative is missing Japanese/default README.md")
        continue
    }
    if (-not (Test-Path -LiteralPath $english -PathType Leaf)) {
        $errors.Add("$relative is missing English README.en.md")
        continue
    }

    $readmeText = Get-Content -Raw -LiteralPath $readme
    $englishText = Get-Content -Raw -LiteralPath $english
    if ($readmeText -notmatch 'README\.en\.md') {
        $errors.Add("$relative/README.md must link README.en.md")
    }
    if ($englishText -notmatch 'README\.md') {
        $errors.Add("$relative/README.en.md must link README.md")
    }
    foreach ($required in @('experiment.json', 'previews/contact-sheet.jpg', 'X')) {
        if ($englishText -notmatch [regex]::Escape($required)) {
            $errors.Add("$relative/README.en.md is missing required discoverability token '$required'")
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

[pscustomobject]@{
    ok = $true
    requiredPairs = $pairs.Count
    experimentReadmePairs = $experimentDirs.Count
    exempt = @('runtime/**/benchmark/*.md', 'tool-owned AGENTS.md / CLAUDE.md', 'social-copy drafts')
} | ConvertTo-Json -Depth 4
