[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Prompt,

    [string]$WorkingDirectory = (Get-Location).Path,

    [ValidateRange(1, 50)]
    [int]$MaxTurns = 8,

    [ValidateSet('low', 'medium', 'high')]
    [string]$ReasoningEffort = 'medium'
)

$ErrorActionPreference = 'Stop'

$resolvedWorkingDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).Path
if (-not (Test-Path -LiteralPath $resolvedWorkingDirectory -PathType Container)) {
    throw "Working directory is not a directory: $resolvedWorkingDirectory"
}

$grokCommand = Get-Command grok -ErrorAction SilentlyContinue
if (-not $grokCommand) {
    $fallbackExe = Join-Path $env:USERPROFILE '.grok\bin\grok.exe'
    if (-not (Test-Path -LiteralPath $fallbackExe -PathType Leaf)) {
        throw 'grok.exe was not found. Install Grok Build or add it to PATH.'
    }
    $grokExe = $fallbackExe
} else {
    $grokExe = $grokCommand.Source
}

$canonicalGrokHome = if ([string]::IsNullOrWhiteSpace($env:GROK_HOME)) {
    Join-Path $env:USERPROFILE '.grok'
} else {
    (Resolve-Path -LiteralPath $env:GROK_HOME).Path
}
$canonicalAuthPath = Join-Path $canonicalGrokHome 'auth.json'

if (-not (Test-Path -LiteralPath $canonicalAuthPath -PathType Leaf)) {
    throw @"
SAFE_GROK_AUTH_MISSING: $canonicalAuthPath was not found.
This wrapper never runs 'grok login' or 'grok logout'. Authenticate separately,
verify that the session works, then run this wrapper again.
"@
}

# Run against a temporary copy so a failed refresh/re-login path cannot delete
# the user's canonical auth.json. Commit the refreshed copy only after success.
$tempGrokHome = Join-Path ([System.IO.Path]::GetTempPath()) ('grok-safe-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempGrokHome -Force | Out-Null
$tempAuthPath = Join-Path $tempGrokHome 'auth.json'
Copy-Item -LiteralPath $canonicalAuthPath -Destination $tempAuthPath -Force

$previousGrokHome = $env:GROK_HOME
$previousDisableAutoUpdater = $env:GROK_DISABLE_AUTOUPDATER
$env:GROK_HOME = $tempGrokHome
$env:GROK_DISABLE_AUTOUPDATER = '1'

$guard = @'
This is a read-only research task. Do not create, edit, rename, or delete files.
Do not run grok login, grok logout, or any other authentication-changing command.
Do not post, reply, like, repost, follow, DM, or change any external account state.
'@
$effectivePrompt = "$guard`n`n$Prompt"

$arguments = @(
    '--cwd', $resolvedWorkingDirectory,
    '--max-turns', [string]$MaxTurns,
    '--reasoning-effort', $ReasoningEffort,
    '--no-subagents',
    '--output-format', 'json',
    '-p', $effectivePrompt
)

$exitCode = 1
try {
    & $grokExe @arguments
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        throw "Grok Build exited with code $exitCode. The canonical auth file was not changed."
    }

    if (-not (Test-Path -LiteralPath $tempAuthPath -PathType Leaf)) {
        throw 'SAFE_GROK_AUTH_LOST: the isolated auth file disappeared during the run; canonical auth was preserved.'
    }

    Copy-Item -LiteralPath $tempAuthPath -Destination $canonicalAuthPath -Force
} finally {
    if ($null -eq $previousGrokHome) {
        Remove-Item Env:GROK_HOME -ErrorAction SilentlyContinue
    } else {
        $env:GROK_HOME = $previousGrokHome
    }

    if ($null -eq $previousDisableAutoUpdater) {
        Remove-Item Env:GROK_DISABLE_AUTOUPDATER -ErrorAction SilentlyContinue
    } else {
        $env:GROK_DISABLE_AUTOUPDATER = $previousDisableAutoUpdater
    }

    if (Test-Path -LiteralPath $tempGrokHome) {
        Remove-Item -LiteralPath $tempGrokHome -Recurse -Force -ErrorAction SilentlyContinue
    }
}

if ($exitCode -ne 0) {
    exit $exitCode
}
