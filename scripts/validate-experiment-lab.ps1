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
    '06-production-pipelines',
    '07-upscaling'
)
$records = @()
$trackedFiles = @(& git -C $repo ls-files)
$mediaExtensions = @('.mp4', '.webm', '.mov', '.mkv', '.mp3', '.wav', '.m4a')
$repoPrefix = $repo.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

function Get-RepoRelativePath {
    param([string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $fullPath.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $null
    }

    return $fullPath.Substring($repoPrefix.Length).Replace([System.IO.Path]::DirectorySeparatorChar, '/')
}

function Test-TrackedPath {
    param([string]$Path)

    $relativePath = Get-RepoRelativePath -Path $Path
    return ($null -ne $relativePath -and $trackedFiles -contains $relativePath)
}

function Test-RecordFilePath {
    param(
        [string]$RecordDirectory,
        [string]$RelativePath,
        [string]$Label
    )

    if ([string]::IsNullOrWhiteSpace($RelativePath) -or $RelativePath -match '^<repo-root>') {
        return
    }

    $path = Join-Path $RecordDirectory $RelativePath.Replace('/', '\')
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $errors.Add("$Label path does not resolve from the experiment directory: $RelativePath")
    }
}

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
    $readmeJaPath = Join-Path $dir.FullName 'README.ja.md'

    try {
        $record = Get-Content -Raw -LiteralPath $jsonPath | ConvertFrom-Json
    } catch {
        $errors.Add("$relativeDir/experiment.json is not valid JSON: $($_.Exception.Message)")
        continue
    }

    $required = @('id', 'date', 'category', 'status', 'sources', 'conditions', 'runs', 'previews', 'publicEvidence', 'publication')
    foreach ($name in $required) {
        [void](Test-RequiredProperty -Object $record -Name $name -Path "$relativeDir/experiment.json")
    }

    if (($record.status -as [string]) -notin $allowedStatuses) {
        $errors.Add("$relativeDir/experiment.json has unsupported status '$($record.status)'.")
    }

    if (($record.category -as [string]) -ne $category) {
        $errors.Add("$relativeDir/experiment.json category '$($record.category)' does not match directory category '$category'.")
    }

    if ($record.PSObject.Properties.Name -contains 'publication' -and $null -ne $record.publication) {
        if ($record.publication.PSObject.Properties.Name -notcontains 'platform' -or [string]$record.publication.platform -ne 'x') {
            $errors.Add("$relativeDir/experiment.json publication.platform must be 'x'.")
        }
        if ($record.publication.PSObject.Properties.Name -notcontains 'status' -or [string]$record.publication.status -notin @('posted', 'uncertain', 'simulation_only', 'not_posted')) {
            $errors.Add("$relativeDir/experiment.json publication.status is unsupported.")
        }
        if ($record.publication.PSObject.Properties.Name -notcontains 'videoTweets') {
            $errors.Add("$relativeDir/experiment.json publication.videoTweets is missing.")
        } else {
            foreach ($tweet in @($record.publication.videoTweets)) {
                if ($tweet.PSObject.Properties.Name -notcontains 'url' -or [string]$tweet.url -notmatch '^https://x\.com/[^/]+/status/[0-9]+') {
                    $errors.Add("$relativeDir/experiment.json publication.videoTweets contains an invalid X URL.")
                }
            }
        }
    }

    if (-not (Test-Path -LiteralPath $readmePath)) {
        $errors.Add("$relativeDir is missing README.md.")
    } else {
        $readmeText = Get-Content -Raw -LiteralPath $readmePath
        if ($readmeText -notmatch '\]\(\./previews/contact-sheet\.jpg\)') {
            $errors.Add("$relativeDir/README.md must link the tracked previews/contact-sheet.jpg tile.")
        }
        if ($readmeText -notmatch '\]\(\./experiment\.json\)') {
            $warnings.Add("$relativeDir/README.md does not link experiment.json near the top of the record.")
        }
        if ($readmeText -notmatch '(?mi)^## X video .*reference URL') {
            $errors.Add("$relativeDir/README.md must contain the English X video/reference URL section.")
        }

        if ($record.PSObject.Properties.Name -contains 'publication' -and $null -ne $record.publication -and
            $record.publication.PSObject.Properties.Name -contains 'videoTweets') {
            foreach ($tweet in @($record.publication.videoTweets)) {
                if ($null -eq $tweet -or $tweet.PSObject.Properties.Name -notcontains 'url') {
                    continue
                }

                $tweetUrl = [string]$tweet.url
                if (-not [string]::IsNullOrWhiteSpace($tweetUrl) -and
                    $readmeText.IndexOf($tweetUrl, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
                    $errors.Add("$relativeDir/README.md must link publication.videoTweets URL '$tweetUrl'.")
                }
            }
        }

        foreach ($source in @($record.sources)) {
            if ($null -eq $source -or $source.PSObject.Properties.Name -notcontains 'url') {
                continue
            }

            $sourceUrl = [string]$source.url
            if (-not [string]::IsNullOrWhiteSpace($sourceUrl) -and
                $readmeText.IndexOf($sourceUrl, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
                $errors.Add("$relativeDir/README.md must link source URL '$sourceUrl'.")
            }
        }

        $sourceNotesPath = Join-Path $dir.FullName 'sources.md'
        if (Test-Path -LiteralPath $sourceNotesPath -PathType Leaf) {
            $sourceNotesText = Get-Content -Raw -LiteralPath $sourceNotesPath
            $sourceNoteUrls = [regex]::Matches($sourceNotesText, 'https?://[^\s)<>]+') |
                ForEach-Object { $_.Value.TrimEnd('.', ',', ';') } |
                Sort-Object -Unique
            foreach ($sourceNoteUrl in $sourceNoteUrls) {
                if ($readmeText.IndexOf($sourceNoteUrl, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
                    $errors.Add("$relativeDir/README.md must link sources.md URL '$sourceNoteUrl'.")
                }
            }
        }
    }

    if (-not (Test-Path -LiteralPath $readmeJaPath -PathType Leaf)) {
        $errors.Add("$relativeDir is missing README.ja.md.")
    } else {
        $readmeJaText = Get-Content -Raw -LiteralPath $readmeJaPath
        if ($readmeJaText -notmatch '(?m)^## X動画・参照URL\s*$') {
            $errors.Add("$relativeDir/README.ja.md must contain a direct 'X動画・参照URL' section.")
        }
    }

    if ($record.PSObject.Properties.Name -contains 'previews' -and $null -ne $record.previews) {
        foreach ($previewName in @('contactSheet', 'manifest')) {
            if ($record.previews.PSObject.Properties.Name -notcontains $previewName) {
                continue
            }

            $previewRelativePath = [string]$record.previews.$previewName
            if ($previewRelativePath -match '(^|[\\/])\.\.([\\/]|$)') {
                $errors.Add("$relativeDir/experiment.json preview path '$previewRelativePath' escapes the experiment directory.")
                continue
            }

            $previewPath = Join-Path $dir.FullName $previewRelativePath.Replace('/', '\')
            if (-not (Test-Path -LiteralPath $previewPath -PathType Leaf)) {
                $errors.Add("$relativeDir is missing preview artifact '$previewRelativePath'.")
            }

            if ($previewName -eq 'manifest' -and (Test-Path -LiteralPath $previewPath -PathType Leaf)) {
                try {
                    $manifest = Get-Content -Raw -LiteralPath $previewPath | ConvertFrom-Json
                    if ($manifest.PSObject.Properties.Name -notcontains 'sources' -or @($manifest.sources).Count -eq 0) {
                        $errors.Add("$relativeDir/$previewRelativePath must list at least one source video.")
                    }

                    if ($manifest.PSObject.Properties.Name -contains 'output' -and $null -ne $manifest.output) {
                        $manifestOutputRelativePath = [string]$manifest.output.path
                        $manifestOutputPath = Join-Path $repo $manifestOutputRelativePath.Replace('/', '\')
                        if (-not (Test-Path -LiteralPath $manifestOutputPath -PathType Leaf)) {
                            $errors.Add("$relativeDir/$previewRelativePath output path does not resolve: $manifestOutputRelativePath")
                        } elseif ($manifest.output.PSObject.Properties.Name -contains 'sha256') {
                            $actualManifestOutputHash = (Get-FileHash -LiteralPath $manifestOutputPath -Algorithm SHA256).Hash.ToUpperInvariant()
                            $declaredManifestOutputHash = ([string]$manifest.output.sha256).ToUpperInvariant()
                            if ($actualManifestOutputHash -ne $declaredManifestOutputHash) {
                                $errors.Add("$relativeDir/$previewRelativePath output SHA-256 does not match the tracked tile.")
                            }
                        }
                    }
                } catch {
                    $errors.Add("$relativeDir/$previewRelativePath is not a valid contact-sheet manifest: $($_.Exception.Message)")
                }
            }
        }
    }

    if ($record.PSObject.Properties.Name -contains 'publicEvidence' -and $null -ne $record.publicEvidence) {
        foreach ($evidenceName in @('tile', 'manifest', 'videoStatus')) {
            if ($record.publicEvidence.PSObject.Properties.Name -notcontains $evidenceName) {
                $errors.Add("$relativeDir/experiment.json publicEvidence is missing '$evidenceName'.")
            }
        }

        if ($record.publicEvidence.PSObject.Properties.Name -contains 'videoStatus') {
            $videoStatus = [string]$record.publicEvidence.videoStatus
            if ($videoStatus -notin @('tracked', 'local-only', 'not-applicable')) {
                $errors.Add("$relativeDir/experiment.json publicEvidence.videoStatus '$videoStatus' is unsupported.")
            }
        }

        foreach ($evidencePathName in @('tile', 'manifest')) {
            if ($record.publicEvidence.PSObject.Properties.Name -notcontains $evidencePathName) {
                continue
            }

            $evidenceRelativePath = [string]$record.publicEvidence.$evidencePathName
            if ($evidenceRelativePath -match '(^|[\\/])\.\.([\\/]|$)') {
                $errors.Add("$relativeDir/experiment.json public evidence path '$evidenceRelativePath' escapes the experiment directory.")
                continue
            }

            $evidencePath = Join-Path $dir.FullName $evidenceRelativePath.Replace('/', '\')
            if (-not (Test-Path -LiteralPath $evidencePath -PathType Leaf)) {
                $errors.Add("$relativeDir is missing public evidence artifact '$evidenceRelativePath'.")
            }

            if ((Test-Path -LiteralPath $evidencePath -PathType Leaf) -and -not (Test-TrackedPath -Path $evidencePath)) {
                $errors.Add("$relativeDir public evidence '$evidenceRelativePath' is not tracked by Git.")
            }

            if ($record.previews.PSObject.Properties.Name -contains $evidencePathName) {
                $previewPath = [string]$record.previews.$evidencePathName
                if ($previewPath -ne $evidenceRelativePath) {
                    $errors.Add("$relativeDir publicEvidence.$evidencePathName '$evidenceRelativePath' does not match previews.$evidencePathName '$previewPath'.")
                }
            }
        }
    }

    # These fields are intentionally record-directory-relative. Validate the
    # reproducibility-critical inputs and workflows even when generated videos
    # remain local-only and are therefore not required to exist in a clone.
    if ($record.PSObject.Properties.Name -contains 'baselineExperiment') {
        Test-RecordFilePath -RecordDirectory $dir.FullName -RelativePath ([string]$record.baselineExperiment) -Label "$relativeDir/experiment.json baselineExperiment"
    }
    if ($record.PSObject.Properties.Name -contains 'referenceInputs') {
        foreach ($referenceInput in @($record.referenceInputs)) {
            if ($referenceInput.PSObject.Properties.Name -contains 'path') {
                Test-RecordFilePath -RecordDirectory $dir.FullName -RelativePath ([string]$referenceInput.path) -Label "$relativeDir/experiment.json referenceInputs.path"
            }
        }
    }
    if ($record.PSObject.Properties.Name -contains 'runs') {
        foreach ($run in @($record.runs)) {
            if ($run.PSObject.Properties.Name -contains 'workflow') {
                Test-RecordFilePath -RecordDirectory $dir.FullName -RelativePath ([string]$run.workflow) -Label "$relativeDir/experiment.json runs.workflow"
            }
        }
    }
    if ($record.PSObject.Properties.Name -contains 'artifacts' -and $null -ne $record.artifacts -and $record.artifacts -isnot [array]) {
        if ($record.artifacts.PSObject.Properties.Name -contains 'references') {
            foreach ($referencePath in @($record.artifacts.references)) {
                Test-RecordFilePath -RecordDirectory $dir.FullName -RelativePath ([string]$referencePath) -Label "$relativeDir/experiment.json artifacts.references"
            }
        }
        if ($record.artifacts.PSObject.Properties.Name -contains 'workflows') {
            foreach ($workflowEntry in @($record.artifacts.workflows)) {
                $workflowPath = $workflowEntry
                if ($workflowEntry -isnot [string] -and $workflowEntry.PSObject.Properties.Name -contains 'path') {
                    $workflowPath = $workflowEntry.path
                }
                if ([string]$workflowPath -notmatch '\.\.\.$') {
                    Test-RecordFilePath -RecordDirectory $dir.FullName -RelativePath ([string]$workflowPath) -Label "$relativeDir/experiment.json artifacts.workflows"
                }
            }
        }
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

# A local MP4 can exist in the author's checkout while being absent from a fresh
# clone because generated media is intentionally ignored. Never let a Markdown
# link silently point at that private-only artifact; use the tracked tile/poster
# and keep the source path in experiment.json or contact-sheet.json instead.
$markdownFiles = Get-ChildItem -LiteralPath $repo -Recurse -File -Filter '*.md' |
    Where-Object { $_.FullName -notmatch '[/\\](\.git|node_modules|dist|cache)[/\\]' }
foreach ($markdownFile in $markdownFiles) {
    $markdownText = Get-Content -Raw -LiteralPath $markdownFile.FullName
    foreach ($match in [regex]::Matches($markdownText, '\]\(([^)\s]+)(?:\s+["\x27][^)]*["\x27])?\)')) {
        $target = $match.Groups[1].Value.Trim('<>')
        if ($target -match '^(https?:|//|#)') {
            continue
        }

        $targetWithoutFragment = ($target -split '[?#]', 2)[0]
        $extension = [System.IO.Path]::GetExtension($targetWithoutFragment).ToLowerInvariant()
        if ($extension -notin $mediaExtensions) {
            continue
        }

        $resolvedTarget = [System.IO.Path]::GetFullPath((Join-Path $markdownFile.DirectoryName $targetWithoutFragment))
        $relativeTarget = Get-RepoRelativePath -Path $resolvedTarget
        if ($null -eq $relativeTarget) {
            $errors.Add("$($markdownFile.FullName.Substring($repo.Length + 1)) media link escapes the repository: $target")
            continue
        }

        if (-not (Test-Path -LiteralPath $resolvedTarget -PathType Leaf)) {
            $errors.Add("$($markdownFile.FullName.Substring($repo.Length + 1)) media link does not resolve: $target")
        } elseif ($trackedFiles -notcontains $relativeTarget) {
            $errors.Add("$($markdownFile.FullName.Substring($repo.Length + 1)) links to untracked media '$target'; use the tracked frame tile or mark it as local-only text.")
        }
    }
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
