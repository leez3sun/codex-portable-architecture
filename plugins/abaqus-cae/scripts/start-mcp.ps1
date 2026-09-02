$ErrorActionPreference = "Stop"

$server = Join-Path $PSScriptRoot "abaqus_mcp_server.py"

if (-not $env:ABAQUS_COMMAND) {
    $commandCandidates = @("abaqus", "abq2026", "abq2025", "abq2024")
    foreach ($candidate in $commandCandidates) {
        $resolved = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($resolved) {
            $env:ABAQUS_COMMAND = $resolved.Source
            break
        }
    }
}

if (-not $env:ABAQUS_COMMAND) {
    $commandFolders = @(
        "C:\\SIMULIA\\Commands",
        "D:\\SIMULIA\\Commands",
        "C:\\DassaultSystemes\\SimulationServices\\V6R2024x\\win_b64\\SMA\\site",
        "D:\\SoftWareforWork\\Abaqus\\commands"
    )
    foreach ($folder in $commandFolders) {
        if (-not (Test-Path -LiteralPath $folder)) { continue }
        $match = Get-ChildItem -LiteralPath $folder -Filter "abq*.bat" -File -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            Select-Object -First 1
        if ($match) {
            $env:ABAQUS_COMMAND = $match.FullName
            break
        }
    }
}

if (-not $env:ABAQUS_COMMAND) {
    $env:ABAQUS_COMMAND = "abaqus"
}

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
