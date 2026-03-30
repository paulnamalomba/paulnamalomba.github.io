param(
    # Path to the system-management_scripts repo root (the folder that contains 'guides/')
    [string]$SourceRepoPath = (Join-Path $PSScriptRoot '..\..\system-management_scripts'),

    # Destination folder to copy guides into (default: this repo's docs/guides)
    [string]$TargetDocsGuidesPath = (Join-Path $PSScriptRoot '..\docs\guides'),

    [switch]$Clean
)

$ErrorActionPreference = 'Stop'

$resolvedSourceRepoPath = (Resolve-Path -Path $SourceRepoPath -ErrorAction Stop).Path
$resolvedTargetGuidesPath = (Resolve-Path -Path $TargetDocsGuidesPath -ErrorAction SilentlyContinue)
if ($null -ne $resolvedTargetGuidesPath) {
    $resolvedTargetGuidesPath = $resolvedTargetGuidesPath.Path
}

if (-not (Test-Path $resolvedSourceRepoPath)) {
    throw "Source repo not found: $resolvedSourceRepoPath"
}

$sourceGuides = Join-Path $resolvedSourceRepoPath 'guides'
if (-not (Test-Path $sourceGuides)) {
    throw "Source guides folder not found: $sourceGuides"
}

$targetGuides = if ($resolvedTargetGuidesPath) { $resolvedTargetGuidesPath } else { $TargetDocsGuidesPath }

if (-not (Test-Path $targetGuides)) {
    New-Item -ItemType Directory -Force -Path $targetGuides | Out-Null
}

# If docs/guides is a symlink (common in this repo), replace it with a real directory.
# GitHub Pages and copy operations are more predictable with real files.
$targetItem = Get-Item -LiteralPath $targetGuides -Force
if ($targetItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
    $linkType = $targetItem.LinkType
    $linkTarget = $targetItem.Target
    Write-Host "Target guides folder is a reparse point ($linkType -> $linkTarget). Replacing with a real directory..." -ForegroundColor Yellow
    Remove-Item -LiteralPath $targetGuides -Force
    New-Item -ItemType Directory -Force -Path $targetGuides | Out-Null
}

$resolvedSourceGuides = (Resolve-Path -Path $sourceGuides -ErrorAction Stop).Path
$resolvedTargetGuides = (Resolve-Path -Path $targetGuides -ErrorAction Stop).Path

if ($resolvedSourceGuides -eq $resolvedTargetGuides) {
    throw (
        "Refusing to copy guides because source and destination are the same folder:`n" +
        "  Source: $resolvedSourceGuides`n" +
        "  Target: $resolvedTargetGuides`n" +
        "Hint: pass -SourceRepoPath ..\\system-management_scripts (repo root), not a docs/guides path."
    )
}

if ($Clean) {
    Get-ChildItem -Path $targetGuides -Force | Remove-Item -Recurse -Force
}

Copy-Item -Path (Join-Path $resolvedSourceGuides '*') -Destination $resolvedTargetGuides -Recurse -Force

Write-Host "Synced guides:" -ForegroundColor Cyan
Write-Host "  From: $resolvedSourceGuides" -ForegroundColor DarkGray
Write-Host "  To:   $resolvedTargetGuides" -ForegroundColor DarkGray
