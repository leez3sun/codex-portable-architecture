[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Require-Path([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path)) { $errors.Add("Missing $Label`: $Path") }
}

$marketplacePath = Join-Path $root ".agents\plugins\marketplace.json"
Require-Path $marketplacePath "marketplace"
if (Test-Path -LiteralPath $marketplacePath) {
    try { $marketplace = Get-Content -LiteralPath $marketplacePath -Raw | ConvertFrom-Json }
    catch { $errors.Add("Invalid marketplace JSON: $($_.Exception.Message)") }
    if ($marketplace.name -ne "codex-portable") { $errors.Add("Unexpected marketplace name: $($marketplace.name)") }
    foreach ($entry in $marketplace.plugins) {
        $pluginPath = Join-Path $root ($entry.source.path -replace '^\./', '')
        $manifestPath = Join-Path $pluginPath ".codex-plugin\plugin.json"
        $mcpPath = Join-Path $pluginPath ".mcp.json"
        Require-Path $manifestPath "plugin manifest for $($entry.name)"
        Require-Path $mcpPath "MCP manifest for $($entry.name)"
        if (Test-Path -LiteralPath $manifestPath) {
            try { $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json }
            catch { $errors.Add("Invalid plugin JSON ($($entry.name)): $($_.Exception.Message)"); continue }
            if ($manifest.name -ne $entry.name) { $errors.Add("Marketplace/manifest name mismatch: $($entry.name) / $($manifest.name)") }
        }
    }
}

$expectedSkills = @(
    "academic-research-suite",
    "browser-use",
    "ppt-master",
    "thesis-crossref-validate",
    "thesis-openalex-expand",
    "thesis-openalex-search",
    "thesis-research-router"
)
foreach ($skill in $expectedSkills) {
    Require-Path (Join-Path $root "skills\$skill\SKILL.md") "skill $skill"
}

$forbiddenNames = Get-ChildItem -LiteralPath $root -Force -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in @(".venv", "__pycache__", ".env", "auth.json") -or $_.Extension -eq ".pyc" }
foreach ($item in $forbiddenNames) { $errors.Add("Forbidden generated/private artifact: $($item.FullName)") }

$textExtensions = @(".json", ".toml", ".md", ".txt", ".py", ".ps1", ".cmd", ".bat", ".yaml", ".yml", ".xml")
$localPathPatterns = @(
    ("C:\" + "Users\Admin"),
    ("C:\\" + "\\Users\\Admin"),
    ("D:\" + "szy ABAQUS\ANsys_AI"),
    ("D:\\" + "\\szy ABAQUS\\ANsys_AI")
)
$textFiles = Get-ChildItem -LiteralPath $root -Force -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -in $textExtensions } |
    Where-Object { $_.FullName -notmatch '\\.git\\' }
$textFiles | ForEach-Object {
        $file = $_
        foreach ($pattern in $localPathPatterns) {
            if (Select-String -LiteralPath $file.FullName -SimpleMatch $pattern -Quiet) {
                $errors.Add("Machine-specific path remains: $($file.FullName)")
                break
            }
        }
    }

$secretPattern = '(github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|xox[baprs]-[0-9A-Za-z-]{10,}|-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----)'
$knownFixture = [System.IO.Path]::GetFullPath((Join-Path $root "skills\academic-research-suite\codex\tests\test_hook_wrapper.py"))
$textFiles | ForEach-Object {
    if (Select-String -LiteralPath $_.FullName -Pattern $secretPattern -Quiet) {
        if ([System.StringComparer]::OrdinalIgnoreCase.Equals($_.FullName, $knownFixture)) {
            $warnings.Add("Known fake API-key test fixture retained: $($_.FullName)")
        } else {
            $errors.Add("Possible credential pattern (value suppressed): $($_.FullName)")
        }
    }
}

if ($warnings.Count) {
    Write-Host "Warnings:" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}
if ($errors.Count) {
    Write-Host "Validation failed:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

$fileCount = (Get-ChildItem -LiteralPath $root -Force -Recurse -File | Measure-Object).Count
$bytes = (Get-ChildItem -LiteralPath $root -Force -Recurse -File | Measure-Object Length -Sum).Sum
Write-Host "Portable bundle validation passed. files=$fileCount bytes=$bytes" -ForegroundColor Green
exit 0
