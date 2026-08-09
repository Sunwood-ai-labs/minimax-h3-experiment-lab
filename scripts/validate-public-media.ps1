[CmdletBinding()]
param(
    [string]$RepoPath = '.'
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath $RepoPath).Path
$errors = [System.Collections.Generic.List[string]]::new()
$trackedFiles = @(& git -C $repo ls-files)
$videoExtensions = @('.mp4', '.webm', '.mov', '.mkv')
$imageExtensions = @('.jpg', '.jpeg', '.png', '.webp', '.avif')
$repoPrefix = $repo.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar

function Get-RepoRelativePath {
    param([string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $fullPath.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $null
    }

    return $fullPath.Substring($repoPrefix.Length).Replace([System.IO.Path]::DirectorySeparatorChar, '/')
}

$payloadFiles = Get-ChildItem -LiteralPath $repo -Recurse -File -Filter 'payload.json' |
    Where-Object { $_.FullName -match '[/\\]sunwood-x-simulator-' }

foreach ($payloadFile in $payloadFiles) {
    $payloadRelativePath = $payloadFile.FullName.Substring($repo.Length + 1).Replace('\', '/')
    try {
        $payload = Get-Content -Raw -LiteralPath $payloadFile.FullName | ConvertFrom-Json
    } catch {
        $errors.Add("$payloadRelativePath is not valid JSON: $($_.Exception.Message)")
        continue
    }

    if ($payload.PSObject.Properties.Name -notcontains 'media' -or $null -eq $payload.media) {
        continue
    }

    foreach ($mediaProperty in $payload.media.PSObject.Properties) {
        $media = $mediaProperty.Value
        if ($media.PSObject.Properties.Name -notcontains 'src') {
            continue
        }

        $sourceExtension = [System.IO.Path]::GetExtension([string]$media.src).ToLowerInvariant()
        if ($sourceExtension -notin $videoExtensions) {
            continue
        }

        $fallback = $null
        if ($media.PSObject.Properties.Name -contains 'publicTile') {
            $fallback = [string]$media.publicTile
        } elseif ($media.PSObject.Properties.Name -contains 'poster') {
            $fallback = [string]$media.poster
        }

        if ([string]::IsNullOrWhiteSpace($fallback)) {
            $errors.Add("$payloadRelativePath media '$($mediaProperty.Name)' has a video source but no tracked publicTile or poster.")
            continue
        }

        $fallbackExtension = [System.IO.Path]::GetExtension($fallback).ToLowerInvariant()
        if ($fallbackExtension -notin $imageExtensions) {
            $errors.Add("$payloadRelativePath media '$($mediaProperty.Name)' fallback is not an image: $fallback")
            continue
        }

        $fallbackPath = [System.IO.Path]::GetFullPath((Join-Path $payloadFile.DirectoryName $fallback))
        $fallbackRelativePath = Get-RepoRelativePath -Path $fallbackPath
        if ($null -eq $fallbackRelativePath) {
            $errors.Add("$payloadRelativePath media '$($mediaProperty.Name)' fallback escapes the repository: $fallback")
            continue
        }

        if (-not (Test-Path -LiteralPath $fallbackPath -PathType Leaf)) {
            $errors.Add("$payloadRelativePath media '$($mediaProperty.Name)' fallback does not resolve: $fallback")
        } elseif ($trackedFiles -notcontains $fallbackRelativePath) {
            $errors.Add("$payloadRelativePath media '$($mediaProperty.Name)' fallback is not tracked: $fallback")
        }
    }
}

$result = [ordered]@{
    ok = ($errors.Count -eq 0)
    simulatorPayloadCount = @($payloadFiles).Count
    errors = @($errors)
}
$result | ConvertTo-Json -Depth 8
if ($errors.Count -gt 0) {
    exit 1
}
