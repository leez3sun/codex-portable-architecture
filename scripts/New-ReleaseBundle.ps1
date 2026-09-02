[CmdletBinding()]
param(
    [string]$OutputDirectory = (Join-Path (Split-Path -Parent $PSScriptRoot) "..\release")
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$output = [System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $output -Force | Out-Null

$version = (Get-Content -LiteralPath (Join-Path $root "VERSION") -Raw).Trim()
$zip = Join-Path $output "codex-portable-architecture-$version.zip"
if (Test-Path -LiteralPath $zip) { throw "Output already exists: $zip" }

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    $root,
    $zip,
    [System.IO.Compression.CompressionLevel]::Optimal,
    $true
)
$hash = Get-FileHash -LiteralPath $zip -Algorithm SHA256
$hashLine = "$($hash.Hash.ToLowerInvariant())  $([System.IO.Path]::GetFileName($zip))"
Set-Content -LiteralPath (Join-Path $output "SHA256SUMS.txt") -Value $hashLine -Encoding utf8
Write-Host $zip
Write-Host $hashLine
