$ErrorActionPreference = "Stop"

function Find-AnsysRoot {
    if ($env:ANSYS_ROOT -and (Test-Path -LiteralPath $env:ANSYS_ROOT)) { return $env:ANSYS_ROOT }

    $awp = Get-ChildItem Env: -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^AWP_ROOT\d+$' -and (Test-Path -LiteralPath $_.Value) } |
        Sort-Object Name -Descending |
        Select-Object -First 1
    if ($awp) { return $awp.Value }

    $candidates = foreach ($drive in @("C", "D", "E")) {
        $base = "${drive}:\\Program Files\\ANSYS Inc"
        if (Test-Path -LiteralPath $base) {
            Get-ChildItem -LiteralPath $base -Directory -Filter "v*" -ErrorAction SilentlyContinue
        }
    }
    return ($candidates | Sort-Object Name -Descending | Select-Object -First 1).FullName
}

$ansysRoot = Find-AnsysRoot
if (-not $ansysRoot) {
    [Console]::Error.WriteLine("ANSYS installation was not found. Set ANSYS_ROOT to the ANSYS v### folder.")
    exit 1
}

$releaseFolder = Split-Path -Leaf $ansysRoot
$digits = $releaseFolder -replace '^v', ''
$version = if ($digits -match '^(\d{2})(\d)$') { "{0}.{1}.0" -f $Matches[1], $Matches[2] } else { "24.1.0" }

$env:ANSYS_ROOT = $ansysRoot
$env:AWP_ROOT241 = $ansysRoot
if (-not $env:ANSYS_VERSION) { $env:ANSYS_VERSION = $version }
if (-not $env:ANSYSLMD_LICENSE_FILE) { $env:ANSYSLMD_LICENSE_FILE = "1055@localhost" }
if (-not $env:FLUENT_EXE) { $env:FLUENT_EXE = Join-Path $ansysRoot "fluent\ntbin\win64\fluent.exe" }
if (-not $env:SPACECLAIM_EXE) { $env:SPACECLAIM_EXE = Join-Path $ansysRoot "scdm\SpaceClaim.exe" }
if (-not $env:ANSYS_LMUTIL) { $env:ANSYS_LMUTIL = Join-Path $ansysRoot "licensingclient\winx64\lmutil.exe" }

$pythonCandidates = @(
    (Join-Path $ansysRoot "commonfiles\CPython\3_12\winx64\Release\python\python.exe"),
    (Join-Path $ansysRoot "commonfiles\CPython\3_11\winx64\Release\python\python.exe"),
    (Join-Path $ansysRoot "commonfiles\CPython\3_10\winx64\Release\python\python.exe")
)
$python = $pythonCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python -and $env:CODEX_PORTABLE_PYTHON -and (Test-Path -LiteralPath $env:CODEX_PORTABLE_PYTHON)) {
    $python = $env:CODEX_PORTABLE_PYTHON
}
if (-not $python) {
    $resolved = Get-Command py -ErrorAction SilentlyContinue
    if ($resolved) { $python = $resolved.Source }
}
if (-not $python) {
    [Console]::Error.WriteLine("No usable Python interpreter was found for the ANSYS Fluent MCP server.")
    exit 1
}

$optiLang = Get-ChildItem -LiteralPath (Join-Path $ansysRoot "optiSLang\lib") -Directory -Filter "python*" -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending |
    ForEach-Object { Join-Path $_.FullName "Lib\site-packages" } |
    Where-Object { Test-Path -LiteralPath $_ } |
    Select-Object -First 1
if ($optiLang -and -not $env:PYTHONPATH) { $env:PYTHONPATH = $optiLang }

$server = Join-Path $PSScriptRoot "ansys_fluent_mcp_server.py"
if ((Split-Path -Leaf $python) -ieq "py.exe") {
    & $python -3 $server
} else {
    & $python -X utf8 $server
}
exit $LASTEXITCODE
