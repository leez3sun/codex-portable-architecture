$ErrorActionPreference = "Stop"

$runtimeBase = if ($env:CODEX_PORTABLE_RUNTIME_ROOT) {
    $env:CODEX_PORTABLE_RUNTIME_ROOT
} else {
    Join-Path $env:LOCALAPPDATA "CodexPortable\runtimes"
}
$stateBase = if ($env:CODEX_PORTABLE_STATE_ROOT) {
    $env:CODEX_PORTABLE_STATE_ROOT
} else {
    Join-Path $env:LOCALAPPDATA "CodexPortable\state"
}

$runtime = Join-Path $runtimeBase "browser-use-enhanced"
$state = Join-Path $stateBase "browser-use-enhanced"
$browserUse = Join-Path $runtime ".venv\Scripts\browser-use.exe"

if (-not (Test-Path -LiteralPath $browserUse)) {
    [Console]::Error.WriteLine("Browser Use runtime is missing. Run scripts\Install-CodexPortable.ps1 -InstallDependencies from the migration bundle.")
    exit 1
}

$env:BH_HOME = $state
$env:BH_AGENT_WORKSPACE = Join-Path $state "agent-workspace"
$env:XDG_CONFIG_HOME = Join-Path $state "config"
$env:XDG_CACHE_HOME = Join-Path $state "cache"
$env:BROWSER_USE_CONFIG_DIR = Join-Path $state "config\browseruse"
$env:ANONYMIZED_TELEMETRY = "false"
$env:BROWSER_USE_CLOUD_SYNC = "false"
$env:BROWSER_USE_VERSION_CHECK = "false"
$env:BROWSER_USE_LOGGING_LEVEL = "critical"
$env:BROWSER_USE_SETUP_LOGGING = "false"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

New-Item -ItemType Directory -Path $env:BH_AGENT_WORKSPACE, $env:XDG_CONFIG_HOME, $env:XDG_CACHE_HOME -Force | Out-Null
& $browserUse --cli-mcp
exit $LASTEXITCODE
