[CmdletBinding()]
param(
    [string]$Distro = 'Ubuntu',
    [string]$Session = 'h3-l4-turbo-720p',
    [ValidateSet('T4', 'L4', 'G4', 'H100', 'A100')][string]$Gpu = 'L4',
    [switch]$SkipSetup,
    [switch]$KeepSession,
    [string]$OutputPath = '',
    [string]$FfmpegBinDir = '',
    [int]$SetupTimeoutSeconds = 3600,
    [int]$RunTimeoutSeconds = 3600
)

$ErrorActionPreference = 'Stop'
$experimentRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $experimentRoot '..\..\..')).Path
$colabExe = '/home/makim/.local/bin/colab'

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $videoRoot = [Environment]::GetFolderPath([Environment+SpecialFolder]::MyVideos)
    if ([string]::IsNullOrWhiteSpace($videoRoot)) {
        $videoRoot = [System.IO.Path]::GetTempPath()
    }
    $OutputPath = Join-Path (Join-Path $videoRoot 'minimax-h3-colab') 'colab_l4_turbo_720p_5s_exact.mp4'
}
$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$outputDir = Split-Path -Parent $OutputPath
$rawOutputPath = Join-Path $outputDir 'colab_l4_turbo_720p_5s_raw.mp4'
New-Item -ItemType Directory -Force $outputDir | Out-Null

function Convert-ToWslPath {
    param([Parameter(Mandatory)][string]$WindowsPath)
    $normalized = $WindowsPath.Replace('\', '/')
    $converted = (& wsl.exe -d $Distro -- wslpath -a -u $normalized 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($converted)) {
        throw "wslpath failed for $WindowsPath`: $converted"
    }
    return $converted
}

function Invoke-Colab {
    param(
        [Parameter(Mandatory)][string]$CommandName,
        [string[]]$Arguments = @()
    )
    Write-Host ("wsl.exe -d $Distro -- $colabExe $CommandName " + ($Arguments -join ' '))
    $result = @(& wsl.exe -d $Distro -- $colabExe $CommandName @Arguments 2>&1 | ForEach-Object { $_.ToString() })
    $code = $LASTEXITCODE
    $result | ForEach-Object { Write-Host $_ }
    if ($code -ne 0) {
        throw "Colab CLI command failed ($code): $CommandName"
    }
    return $result
}

$sessionList = (Invoke-Colab -CommandName 'sessions') -join "`n"
$createdHere = $false
try {
    if ($sessionList -notmatch [regex]::Escape($Session)) {
        [void](Invoke-Colab -CommandName 'new' -Arguments @('--session', $Session, '--gpu', $Gpu))
        $createdHere = $true
    } else {
        Write-Host "Reusing active Colab session: $Session"
    }

    $uploads = @(
        @{ local = (Join-Path $experimentRoot 'colab_runtime.json'); remote = '/content/colab_runtime.json' },
        @{ local = (Join-Path $repoRoot 'models\manifest.json'); remote = '/content/models_manifest.json' },
        @{ local = (Join-Path $repoRoot 'docker\h3-runtime-patch.py'); remote = '/content/h3-runtime-patch.py' },
        @{ local = (Join-Path $experimentRoot 'workflows\minimax_h3_turbo_l4_1280x704_api.json'); remote = '/content/colab_h3_turbo_l4_1280x704_api.json' },
        @{ local = (Join-Path $experimentRoot 'scripts\colab_h3_setup.py'); remote = '/content/colab_h3_setup.py' },
        @{ local = (Join-Path $experimentRoot 'scripts\colab_h3_start.py'); remote = '/content/colab_h3_start.py' },
        @{ local = (Join-Path $experimentRoot 'scripts\colab_h3_run.py'); remote = '/content/colab_h3_run.py' }
    )
    foreach ($upload in $uploads) {
        if (-not (Test-Path -LiteralPath $upload.local -PathType Leaf)) {
            throw "Upload source is missing: $($upload.local)"
        }
        $localWsl = Convert-ToWslPath -WindowsPath $upload.local
        [void](Invoke-Colab -CommandName 'upload' -Arguments @('--session', $Session, $localWsl, $upload.remote))
    }

    if (-not $SkipSetup) {
        [void](Invoke-Colab -CommandName 'exec' -Arguments @('--session', $Session, '--file', '/content/colab_h3_setup.py', '--timeout', $SetupTimeoutSeconds.ToString()))
    }
    [void](Invoke-Colab -CommandName 'exec' -Arguments @('--session', $Session, '--file', '/content/colab_h3_start.py', '--timeout', '300'))
    [void](Invoke-Colab -CommandName 'exec' -Arguments @('--session', $Session, '--file', '/content/colab_h3_run.py', '--timeout', $RunTimeoutSeconds.ToString()))
    [void](Invoke-Colab -CommandName 'download' -Arguments @('--session', $Session, '/content/colab_l4_turbo_720p_5s_raw.mp4', (Convert-ToWslPath -WindowsPath $rawOutputPath)))

    $trimArguments = @('-InputPath', $rawOutputPath, '-OutputPath', $OutputPath, '-Force')
    if (-not [string]::IsNullOrWhiteSpace($FfmpegBinDir)) {
        $trimArguments += @('-FfmpegBinDir', $FfmpegBinDir)
    }
    & (Join-Path $experimentRoot 'scripts\trim-exact-5s.ps1') @trimArguments
    Write-Host "Exact 5-second output: $OutputPath"
}
finally {
    if ($createdHere -and -not $KeepSession) {
        try {
            [void](Invoke-Colab -CommandName 'stop' -Arguments @('--session', $Session))
        } catch {
            Write-Warning "Failed to stop Colab session $Session`: $($_.Exception.Message)"
        }
    } elseif ($createdHere) {
        Write-Host "Keeping Colab session active: $Session"
    }
}
