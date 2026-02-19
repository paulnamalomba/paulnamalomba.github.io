param(
    [string]$Python = "python",
    [string]$Username = "paulnamalomba",
    [string]$Token = $env:GITHUB_TOKEN,
    [switch]$Commit,
    [switch]$Push
)

$ErrorActionPreference = 'Stop'

if ($Token) {
    $env:GITHUB_TOKEN = $Token
}
$env:GITHUB_USERNAME = $Username

Write-Host "Generating GitHub stats for '$Username'..." -ForegroundColor Cyan
& $Python scripts/generate_stats.py

if ($Commit) {
    git add stats/*.svg stats/cache.json | Out-Null
    $hasChanges = -not (git diff --cached --quiet)
    if ($hasChanges) {
        git -c commit.gpgsign=false commit -m "Update GitHub stats"
        if ($Push) {
            git push origin main
        }
    } else {
        Write-Host "No changes to commit." -ForegroundColor DarkGray
    }
}
