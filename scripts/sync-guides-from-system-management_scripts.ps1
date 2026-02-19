param(
    [string]$SourceRepoPath = "$(Resolve-Path (Join-Path $PSScriptRoot '..\..\system-management_scripts'))",
    [string]$TargetDocsGuidesPath = "$(Resolve-Path (Join-Path $PSScriptRoot '..\docs\guides') -ErrorAction SilentlyContinue)",
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $SourceRepoPath)) {
    throw "Source repo not found: $SourceRepoPath"
}

$sourceGuides = Join-Path $SourceRepoPath 'guides'
if (-not (Test-Path $sourceGuides)) {
    throw "Source guides folder not found: $sourceGuides"
}

$targetDocs = Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..')) 'docs'
$targetGuides = Join-Path $targetDocs 'guides'

if (-not (Test-Path $targetGuides)) {
    New-Item -ItemType Directory -Force -Path $targetGuides | Out-Null
}

if ($Clean) {
    Get-ChildItem -Path $targetGuides -Force | Remove-Item -Recurse -Force
}

Copy-Item -Path (Join-Path $sourceGuides '*') -Destination $targetGuides -Recurse -Force

Write-Host "Synced guides:" -ForegroundColor Cyan
Write-Host "  From: $sourceGuides" -ForegroundColor DarkGray
Write-Host "  To:   $targetGuides" -ForegroundColor DarkGray
