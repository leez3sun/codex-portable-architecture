$ErrorActionPreference = "Stop"

$server = Join-Path $PSScriptRoot "mcp_server.py"
if ($env:CODEX_PORTABLE_PYTHON -and (Test-Path -LiteralPath $env:CODEX_PORTABLE_PYTHON)) {
    & $env:CODEX_PORTABLE_PYTHON -X utf8 $server
    exit $LASTEXITCODE
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    & $py.Source -3 $server
    exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & $python.Source -X utf8 $server
    exit $LASTEXITCODE
}

[Console]::Error.WriteLine("No Python interpreter was found. Install Python 3 or set CODEX_PORTABLE_PYTHON.")
exit 1
