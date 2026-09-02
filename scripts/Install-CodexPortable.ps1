[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$InstallRoot = (Join-Path $env:USERPROFILE "CodexPortable\architecture"),
    [string]$Python,
    [switch]$InstallDependencies,
    [switch]$SkipPluginInstall,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$bundleRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$codexHomePath = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$runtimeRoot = if ($env:CODEX_PORTABLE_RUNTIME_ROOT) {
    $env:CODEX_PORTABLE_RUNTIME_ROOT
} else {
    Join-Path $env:LOCALAPPDATA "CodexPortable\runtimes"
}
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = Join-Path $codexHomePath "migration-backups\$timestamp"

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $Executable $($Arguments -join ' ')"
    }
}

function Resolve-PythonCommand {
    if ($Python) {
        $resolvedPath = (Resolve-Path -LiteralPath $Python -ErrorAction Stop).Path
        return [pscustomobject]@{ Exe = $resolvedPath; Prefix = @() }
    }
    if ($env:CODEX_PORTABLE_PYTHON -and (Test-Path -LiteralPath $env:CODEX_PORTABLE_PYTHON)) {
        return [pscustomobject]@{ Exe = $env:CODEX_PORTABLE_PYTHON; Prefix = @() }
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return [pscustomobject]@{ Exe = $py.Source; Prefix = @("-3") } }
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { return [pscustomobject]@{ Exe = $pythonCommand.Source; Prefix = @() } }
    throw "Python 3 was not found. Install Python 3.11+ or pass -Python C:\path\to\python.exe."
}

function Install-VenvRequirements {
    param(
        [pscustomobject]$PythonCommand,
        [string]$Name,
        [string[]]$PipArguments
    )
    $componentRoot = Join-Path $runtimeRoot $Name
    $venvRoot = Join-Path $componentRoot ".venv"
    $venvPython = Join-Path $venvRoot "Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython)) {
        New-Item -ItemType Directory -Path $componentRoot -Force | Out-Null
        Invoke-Checked $PythonCommand.Exe ($PythonCommand.Prefix + @("-m", "venv", $venvRoot))
    }
    Invoke-Checked $venvPython (@("-m", "pip", "install", "--disable-pip-version-check") + $PipArguments)
}

Write-Host "Bundle: $bundleRoot"
Write-Host "Stable install root: $InstallRoot"
Write-Host "Codex home: $codexHomePath"

$sameRoot = [System.StringComparer]::OrdinalIgnoreCase.Equals(
    [System.IO.Path]::GetFullPath($bundleRoot).TrimEnd('\'),
    [System.IO.Path]::GetFullPath($InstallRoot).TrimEnd('\')
)

if (-not $sameRoot) {
    if (Test-Path -LiteralPath $InstallRoot) {
        if (-not $Force) {
            throw "InstallRoot already exists: $InstallRoot. Re-run with -Force to move it to a timestamped backup first."
        }
        $portableBackupRoot = Join-Path $env:USERPROFILE "CodexPortable\backups"
        $portableBackup = Join-Path $portableBackupRoot "architecture-$timestamp"
        if ($PSCmdlet.ShouldProcess($InstallRoot, "Move existing portable architecture to $portableBackup")) {
            New-Item -ItemType Directory -Path $portableBackupRoot -Force | Out-Null
            Move-Item -LiteralPath $InstallRoot -Destination $portableBackup
        }
    }
    if ($PSCmdlet.ShouldProcess($InstallRoot, "Copy portable architecture bundle")) {
        New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
        Get-ChildItem -LiteralPath $bundleRoot -Force |
            Where-Object { $_.Name -notin @(".git", "release") } |
            Copy-Item -Destination $InstallRoot -Recurse -Force
    }
}

$sourceRoot = if ($sameRoot -or $WhatIfPreference) { $bundleRoot } else { $InstallRoot }
$skillsSource = Join-Path $sourceRoot "skills"
$skillsDestination = Join-Path $codexHomePath "skills"
if ($PSCmdlet.ShouldProcess($skillsDestination, "Create Codex skills directory")) {
    New-Item -ItemType Directory -Path $skillsDestination -Force | Out-Null
}

Get-ChildItem -LiteralPath $skillsSource -Directory | ForEach-Object {
    $destination = Join-Path $skillsDestination $_.Name
    if (Test-Path -LiteralPath $destination) {
        if (-not $Force) {
            Write-Warning "Skill already exists and was left unchanged: $destination (use -Force to back up and replace it)."
            return
        }
        $skillBackup = Join-Path $backupRoot "skills\$($_.Name)"
        if ($PSCmdlet.ShouldProcess($destination, "Move existing skill to $skillBackup")) {
            New-Item -ItemType Directory -Path (Split-Path -Parent $skillBackup) -Force | Out-Null
            Move-Item -LiteralPath $destination -Destination $skillBackup
        }
    }
    if ($PSCmdlet.ShouldProcess($destination, "Install skill $($_.Name)")) {
        Copy-Item -LiteralPath $_.FullName -Destination $destination -Recurse -Force
    }
}

if ($InstallDependencies) {
    if ($PSCmdlet.ShouldProcess($runtimeRoot, "Create Python virtual environments and install portable dependencies")) {
        $pythonCommand = Resolve-PythonCommand
        New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null

        Install-VenvRequirements $pythonCommand "browser-use-enhanced" @(
            "-r", (Join-Path $sourceRoot "plugins\browser-use-enhanced\requirements.txt")
        )
        Install-VenvRequirements $pythonCommand "scientific-media-studio" @(
            "-r", (Join-Path $sourceRoot "plugins\scientific-media-studio\requirements.txt")
        )
        Install-VenvRequirements $pythonCommand "ansys-workbench" @(
            "-e", ((Join-Path $sourceRoot "plugins\ansys-workbench\server") + "[mechanical]")
        )
    }
} else {
    Write-Warning "Dependency environments were not created. Re-run with -InstallDependencies before using Browser Use Enhanced, Scientific Media Studio, or Ansys Workbench."
}

if (-not $SkipPluginInstall) {
    $codex = Get-Command codex -ErrorAction SilentlyContinue
    if (-not $codex) {
        Write-Warning "Codex CLI was not found. Install the plugins later from the Codex Portable marketplace in the desktop app."
    } else {
        $marketplaces = & $codex.Source plugin marketplace list 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) { throw "Unable to list Codex plugin marketplaces: $marketplaces" }
        if ($marketplaces -notmatch '(?m)^codex-portable\s+') {
            if ($PSCmdlet.ShouldProcess("Codex plugin configuration", "Add marketplace source $sourceRoot")) {
                Invoke-Checked $codex.Source @("plugin", "marketplace", "add", $sourceRoot)
            }
        } else {
            Write-Warning "Marketplace 'codex-portable' already exists. Its existing source was preserved."
        }

        foreach ($plugin in @(
            "abaqus-cae",
            "ansys-fluent",
            "browser-use-enhanced",
            "scientific-media-studio",
            "abaqus-live-bridge",
            "ansys-workbench"
        )) {
            if ($PSCmdlet.ShouldProcess("Codex plugin configuration", "Install $plugin@codex-portable")) {
                & $codex.Source plugin add "$plugin@codex-portable" --json
                if ($LASTEXITCODE -ne 0) {
                    Write-Warning "Plugin '$plugin' may already be installed or needs installation from the desktop Plugins page."
                }
            }
        }
    }
}

Write-Host ""
if ($WhatIfPreference) {
    Write-Host "Preview complete. No migration files, dependencies, marketplaces, or plugins were changed."
} else {
    Write-Host "Migration files are installed. Restart Codex, open Plugins, select 'Codex Portable', and verify the six personal plugins."
    Write-Host "Official plugins/apps and account authorizations must be reinstalled or reconnected from the Codex Plugins page."
    Write-Host "Run scripts\Test-CodexPortable.ps1 from $sourceRoot for a structural check."
}
exit 0
