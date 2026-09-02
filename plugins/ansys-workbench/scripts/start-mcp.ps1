$ErrorActionPreference = "Stop"

$pluginRoot = Split-Path -Parent $PSScriptRoot
$serverRoot = Join-Path $pluginRoot "server"
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
$python = Join-Path $runtimeBase "ansys-workbench\.venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    [Console]::Error.WriteLine("Ansys Workbench runtime is missing. Run scripts\Install-CodexPortable.ps1 -InstallDependencies from the migration bundle.")
    exit 1
}

if (-not $env:ANSYS_ROOT) {
    $awp = Get-ChildItem Env: -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^AWP_ROOT\d+$' -and (Test-Path -LiteralPath $_.Value) } |
        Sort-Object Name -Descending |
        Select-Object -First 1
    if ($awp) { $env:ANSYS_ROOT = $awp.Value }
}
if (-not $env:ANSYS_ROOT) {
    $candidates = foreach ($drive in @("C", "D", "E")) {
        $base = "${drive}:\\Program Files\\ANSYS Inc"
        if (Test-Path -LiteralPath $base) {
            Get-ChildItem -LiteralPath $base -Directory -Filter "v*" -ErrorAction SilentlyContinue
        }
    }
    $detected = $candidates | Sort-Object Name -Descending | Select-Object -First 1
    if ($detected) { $env:ANSYS_ROOT = $detected.FullName }
}
if ($env:ANSYS_ROOT -and -not $env:ANSYS_WB_EXE) {
    $env:ANSYS_WB_EXE = Join-Path $env:ANSYS_ROOT "Framework\bin\Win64\RunWB2.exe"
}

$state = Join-Path $stateBase "ansys-workbench"
$env:WORKBENCH_MCP_ROOT = $serverRoot
$env:WORKBENCH_MCP_QUEUE_ROOT = Join-Path $state "workbench_queue"
$env:JOBS_DIR = Join-Path $state "jobs"
if (-not $env:WORKBENCH_MCP_HOST) { $env:WORKBENCH_MCP_HOST = "127.0.0.1" }
if (-not $env:WORKBENCH_MCP_PORT) { $env:WORKBENCH_MCP_PORT = "9885" }
New-Item -ItemType Directory -Path $env:WORKBENCH_MCP_QUEUE_ROOT, $env:JOBS_DIR -Force | Out-Null

& $python -X utf8 (Join-Path $serverRoot "server.py")
exit $LASTEXITCODE
