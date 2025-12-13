# Ecoride Repository Management Script
# Manages git operations with version-based commits and tags
# Usage:
# # List available versions
# .\manage-repo.ps1

# # Complete release (recommended)
# .\manage-repo.ps1 -Action release -Version v0.1.0-alpha

# # Individual steps
# .\manage-repo.ps1 -Action add
# .\manage-repo.ps1 -Action commit -Version v0.1.0-alpha
# .\manage-repo.ps1 -Action push
# .\manage-repo.ps1 -Action tag -Version v0.1.0-alpha

# # Custom remote/branch
# .\manage-repo.ps1 -Action release -Version v0.1.0-alpha -Remote upstream -Branch develop

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "list",
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Remote = "origin",
    
    [Parameter(Mandatory=$false)]
    [string]$Branch = "main"
)

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Get available versions from .commits directory
function Get-AvailableVersions {
    $commitsDir = Join-Path $PSScriptRoot "..\.commits"
    $txtFiles = Get-ChildItem -Path $commitsDir -Filter "*.txt" | Where-Object { $_.Name -match '^v\d+\.\d+\.\d+.*\.txt$' }
    
    $versions = @()
    foreach ($file in $txtFiles) {
        $versionName = $file.BaseName
        $versions += $versionName
    }
    
    return $versions | Sort-Object
}

# Display available versions
function Show-AvailableVersions {
    Write-Info "Available versions in .commits/ directory:"
    Write-Host ""
    
    $versions = Get-AvailableVersions
    
    if ($versions.Count -eq 0) {
        Write-Warning "No version files found in .commits/ directory"
        Write-Info "Expected format: v*.txt (e.g., v0.1.0-alpha.txt)"
        return $false
    }
    
    foreach ($version in $versions) {
        $filePath = Join-Path $PSScriptRoot "..\.commits\$version.txt"
        $fileInfo = Get-Item $filePath
        Write-Host "  📦 $version" -ForegroundColor Yellow
        Write-Host "     Created: $($fileInfo.CreationTime)" -ForegroundColor DarkGray
        Write-Host "     Size: $($fileInfo.Length) bytes" -ForegroundColor DarkGray
        Write-Host ""
    }
    
    return $true
}

# Validate version exists
function Test-VersionExists {
    param([string]$VersionNumber)
    
    $versionFile = Join-Path $PSScriptRoot "..\.commits\$VersionNumber.txt"
    
    if (-not (Test-Path $versionFile)) {
        Write-Error "Version file not found: $versionFile"
        Write-Info "Available versions:"
        $versions = Get-AvailableVersions
        foreach ($v in $versions) {
            Write-Host "  - $v" -ForegroundColor Yellow
        }
        return $false
    }
    
    return $true
}

# Check if git repository exists
function Test-GitRepository {
    $gitDir = Join-Path (Split-Path $PSScriptRoot -Parent) ".git"
    
    if (-not (Test-Path $gitDir)) {
        Write-Error "Not a git repository. Initialize with: git init"
        return $false
    }
    
    return $true
}

# Check git status
function Show-GitStatus {
    Write-Info "Git Status:"
    Write-Host ""
    git status --short
    Write-Host ""
}

# Stage all changes
function Invoke-GitAdd {
    Write-Info "Staging all changes..."
    git add .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All changes staged successfully"
        return $true
    } else {
        Write-Error "Failed to stage changes"
        return $false
    }
}

# Commit with version message
function Invoke-GitCommit {
    param([string]$VersionNumber)
    
    $commitMessageFile = Join-Path $PSScriptRoot "..\.commits\$VersionNumber.txt"
    
    Write-Info "Committing with message from: $commitMessageFile"
    
    # Read first few lines for preview
    $preview = Get-Content $commitMessageFile -TotalCount 3
    Write-Host ""
    Write-Host "Commit Message Preview:" -ForegroundColor Cyan
    foreach ($line in $preview) {
        Write-Host "  $line" -ForegroundColor DarkGray
    }
    Write-Host "  ..." -ForegroundColor DarkGray
    Write-Host ""
    
    # Ensure there are staged changes. If none, stage all changes automatically.
    git diff --staged --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Warning "No staged changes detected. Staging all changes before commit."
        if (-not (Invoke-GitAdd)) {
            Write-Error "Failed to stage changes; aborting commit."
            return $false
        }
    }

    # Quote the commit message file path to handle spaces
    $commitCmdOutput = & git commit -F "$commitMessageFile" 2>&1
    $exit = $LASTEXITCODE

    if ($exit -eq 0) {
        Write-Success "Commit created successfully"
        return $true
    } else {
        Write-Error "Failed to create commit"
        Write-Host "--- git commit output ---" -ForegroundColor DarkGray
        Write-Host $commitCmdOutput
        Write-Host "--- git status ---" -ForegroundColor DarkGray
        git status --short
        Write-Host "--- staged diff ---" -ForegroundColor DarkGray
        git diff --staged --name-only
        return $false
    }
}

# Create and push tag
function Invoke-GitTag {
    param(
        [string]$VersionNumber,
        [string]$Remote
    )
    
    Write-Info "Creating tag: $VersionNumber"
    
    # Check if tag already exists
    $existingTag = git tag -l $VersionNumber
    if ($existingTag) {
        Write-Warning "Tag $VersionNumber already exists locally"
        $response = Read-Host "Do you want to delete and recreate it? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            git tag -d $VersionNumber
            Write-Info "Deleted existing local tag"
        } else {
            Write-Info "Skipping tag creation"
            return $false
        }
    }
    
    # Create annotated tag with message from file
    $tagMessageFile = Join-Path $PSScriptRoot "..\.commits\$VersionNumber.txt"
    git tag -a $VersionNumber -F $tagMessageFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Tag $VersionNumber created successfully"
        
        # Push tag to remote
        Write-Info "Pushing tag to $Remote..."
        git push $Remote $VersionNumber --force
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Tag pushed to $Remote"
            return $true
        } else {
            Write-Error "Failed to push tag to $Remote"
            return $false
        }
    } else {
        Write-Error "Failed to create tag"
        return $false
    }
}

# Push to remote
function Invoke-GitPush {
    param(
        [string]$Remote,
        [string]$Branch
    )
    
    Write-Info "Pushing to $Remote/$Branch..."
    git push $Remote $Branch
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Pushed to $Remote/$Branch successfully"
        return $true
    } else {
        Write-Error "Failed to push to $Remote/$Branch"
        return $false
    }
}

# Complete release workflow
function Invoke-Release {
    param(
        [string]$VersionNumber,
        [string]$Remote,
        [string]$Branch
    )
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Ecoride Release: $VersionNumber" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Validate
    if (-not (Test-GitRepository)) { return }
    if (-not (Test-VersionExists -VersionNumber $VersionNumber)) { return }
    
    # Show current status
    Show-GitStatus
    
    # Confirm
    Write-Warning "This will:"
    Write-Host "  1. Stage all changes (git add .)" -ForegroundColor Yellow
    Write-Host "  2. Commit with message from .commits/$VersionNumber.txt" -ForegroundColor Yellow
    Write-Host "  3. Create tag $VersionNumber" -ForegroundColor Yellow
    Write-Host "  4. Push to $Remote/$Branch" -ForegroundColor Yellow
    Write-Host "  5. Push tag $VersionNumber to $Remote" -ForegroundColor Yellow
    Write-Host ""
    
    $confirm = Read-Host "Continue? (y/N)"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Info "Release cancelled"
        return
    }
    
    Write-Host ""
    
    # Execute workflow
    if (-not (Invoke-GitAdd)) { return }
    if (-not (Invoke-GitCommit -VersionNumber $VersionNumber)) { return }
    if (-not (Invoke-GitPush -Remote $Remote -Branch $Branch)) { return }
    if (-not (Invoke-GitTag -VersionNumber $VersionNumber -Remote $Remote)) { return }
    
    Write-Host ""
    # Write-Host "========================================" -ForegroundColor Green
    Write-Success "Release $VersionNumber completed!"
    # Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Info "View release on GitHub:"
    Write-Host "  https://github.com/paulnamalomba/paulnamalomba.github.io/releases/tag/$VersionNumber" -ForegroundColor Cyan
    Write-Host ""
}

# Main script logic
switch ($Action.ToLower()) {
    "list" {
        Show-AvailableVersions
    }
    
    "status" {
        if (-not (Test-GitRepository)) { exit 1 }
        Show-GitStatus
    }
    
    "release" {
        if ([string]::IsNullOrWhiteSpace($Version)) {
            Write-Error "Version number required for release action"
            Write-Info "Usage: .\manage-repo.ps1 -Action release -Version v0.1.0-alpha"
            Write-Host ""
            Show-AvailableVersions
            exit 1
        }
        
        Invoke-Release -VersionNumber $Version -Remote $Remote -Branch $Branch
    }
    
    "add" {
        if (-not (Test-GitRepository)) { exit 1 }
        Invoke-GitAdd
    }
    
    "commit" {
        if ([string]::IsNullOrWhiteSpace($Version)) {
            Write-Error "Version number required for commit action"
            Write-Info "Usage: .\manage-repo.ps1 -Action commit -Version v0.1.0-alpha"
            exit 1
        }
        
        if (-not (Test-GitRepository)) { exit 1 }
        if (-not (Test-VersionExists -VersionNumber $Version)) { exit 1 }
        Invoke-GitCommit -VersionNumber $Version
    }
    
    "tag" {
        if ([string]::IsNullOrWhiteSpace($Version)) {
            Write-Error "Version number required for tag action"
            Write-Info "Usage: .\manage-repo.ps1 -Action tag -Version v0.1.0-alpha"
            exit 1
        }
        
        if (-not (Test-GitRepository)) { exit 1 }
        if (-not (Test-VersionExists -VersionNumber $Version)) { exit 1 }
        Invoke-GitTag -VersionNumber $Version -Remote $Remote
    }
    
    "push" {
        if (-not (Test-GitRepository)) { exit 1 }
        Invoke-GitPush -Remote $Remote -Branch $Branch
    }
    
    "help" {
        Write-Host ""
        Write-Host "Ecoride Repository Management Script" -ForegroundColor Cyan
        Write-Host "====================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage:" -ForegroundColor Yellow
        Write-Host "  .\manage-repo.ps1 [-Action <action>] [-Version <version>] [-Remote <remote>] [-Branch <branch>]"
        Write-Host ""
        Write-Host "Actions:" -ForegroundColor Yellow
        Write-Host "  list       - List available versions in .commits/ directory (default)"
        Write-Host "  status     - Show git status"
        Write-Host "  release    - Complete release workflow (add, commit, push, tag)"
        Write-Host "  add        - Stage all changes (git add .)"
        Write-Host "  commit     - Commit with version message (git commit -F .commits/VERSION.txt)"
        Write-Host "  tag        - Create and push tag"
        Write-Host "  push       - Push to remote branch"
        Write-Host "  help       - Show this help message"
        Write-Host ""
        Write-Host "Parameters:" -ForegroundColor Yellow
        Write-Host "  -Version   - Version number (e.g., v0.1.0-alpha)"
        Write-Host "  -Remote    - Git remote name (default: origin)"
        Write-Host "  -Branch    - Git branch name (default: main)"
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\manage-repo.ps1 -Action list"
        Write-Host "  .\manage-repo.ps1 -Action release -Version v0.1.0-alpha"
        Write-Host "  .\manage-repo.ps1 -Action commit -Version v0.1.0-alpha"
        Write-Host "  .\manage-repo.ps1 -Action tag -Version v0.1.0-alpha -Remote origin"
        Write-Host ""
    }
    
    default {
        Write-Error "Unknown action: $Action"
        Write-Info "Use -Action help for usage information"
        exit 1
    }
}
