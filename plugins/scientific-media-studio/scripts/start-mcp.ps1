$ErrorActionPreference = "Stop"

$runtimeBase = if ($env:CODEX_PORTABLE_RUNTIME_ROOT) {
    $env:CODEX_PORTABLE_RUNTIME_ROOT
} else {
    Join-Path $env:LOCALAPPDATA "CodexPortable\runtimes"
}
$python = Join-Path $runtimeBase "scientific-media-studio\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    [Console]::Error.WriteLine("Scientific Media Studio runtime is missing. Run scripts\Install-CodexPortable.ps1 -InstallDependencies from the migration bundle.")
    exit 1
}

& $python -X utf8 (Join-Path $PSScriptRoot "scientific_media_mcp.py")
exit $LASTEXITCODE
