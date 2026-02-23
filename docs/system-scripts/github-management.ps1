# GitHub Management Functions
# Functions for managing GitHub repositories with automated workflows

function Manage-GitHubAppDev {
    <#
    .SYNOPSIS
    Manages GitHub repository development workflow
    
    .DESCRIPTION
    Automates GitHub repository management including commits, tags, and releases
    
    .PARAMETER managerPath
    Path to the GitHub management scripts directory
    
    .PARAMETER appName
    Name of the application/repository
    
    .PARAMETER commitTag
    Tag for the commit (e.g., v1.0.0)
    
    .PARAMETER commitMessage
    Commit message describing changes
    
    .PARAMETER method
    Method to use: 'update', 'init', or 'download'
    
    .EXAMPLE
    Manage-GitHubAppDev -appName "my-app" -commitTag "v0.3.1" -commitMessage "Updated features" -method "update"
    #>
    param (
        [string]$managerPath = "<path/to/github-management-folder>",
        [string]$appName,
        [string]$commitTag,
        [string]$commitMessage,
        [string]$method = "update"
    )
    
    if ($method[0].ToString().ToLower() -eq "u") {
        $method = "update"
    } elseif ($method[0].ToString().ToLower() -eq "i") {
        $method = "init"
    } elseif ($method[0].ToString().ToLower() -eq "d") {
        $method = "download"
    } else {
        Write-Host "Error: Invalid method parameter. Use 'update', 'init', or 'download'." -ForegroundColor Red
        return
    }

    Write-Host "--------------*GITHUB APP MANAGER*---------------------" -ForegroundColor Cyan
    Write-Host "Managing GitHub repository: $appName" -ForegroundColor Cyan
    $confirmation = Read-Host "You are about to make hard to revert changes to '$appName' on your GitHub repository. Type 'y' to continue, any other key to cancel"
    if ($confirmation -ne "y") {
        Write-Host "CANCELLED! Exiting without making changes" -ForegroundColor Red
        return
    }

    $originalDir = Get-Location
    
    Write-Host "--------------------------------------------------------"
    if (Test-Path $managerPath) {
        Set-Location -Path $managerPath
        Write-Host "Changed directory to '$managerPath'."
    } else {
        Write-Host "Directory '$managerPath' does not exist." -ForegroundColor Red
        return
    }
    
    if ($method -eq "update" -or $method -eq "init") {
        $managerApp = "app-manager.ps1"
        
        if ($null -eq $appName -or $appName -eq "" -or
            $null -eq $commitTag -or $commitTag -eq "" -or
            $null -eq $commitMessage -or $commitMessage -eq "") {
            Write-Host "Error: appName, commitTag, and commitMessage parameters are required." -ForegroundColor Red
            Set-Location -Path $originalDir
            return
        }

        $scriptPath = Join-Path $managerPath -ChildPath "$managerApp"
        if (Test-Path $scriptPath) {
            . $scriptPath -appName $appName -commitTag $commitTag -commitMessage $commitMessage -method $method
            Write-Host "Script '$managerApp' executed." -ForegroundColor Green
        } else {
            Write-Host "Script '$managerApp' not found in '$managerPath'." -ForegroundColor Red
        }
    }
    
    Set-Location -Path $originalDir
    Write-Host "--------------------------------------------------------"
}

function Manage-GitTags {
    <#
    .SYNOPSIS
    Manages Git tags for a repository
    
    .DESCRIPTION
    Lists, creates, or deletes Git tags for a repository
    
    .PARAMETER appName
    Name of the application/repository
    
    .PARAMETER commitTag
    Tag name to manage
    
    .PARAMETER method
    Method to use: 'update', 'list', or 'delete'
    
    .EXAMPLE
    Manage-GitTags -appName "my-app" -method "list"
    Manage-GitTags -appName "my-app" -commitTag "v0.3.1" -method "delete"
    #>
    param (
        [string]$managerPath = "<path/to/github-management-folder>",
        [string]$appName,
        [string]$commitTag,
        [string]$method = "list"
    )
    
    Write-Host "-------------*GITHUB TAG MANAGER*----------------------" -ForegroundColor Cyan
    Write-Host "Managing GitHub Tags for repository: $appName" -ForegroundColor Cyan
    
    if ($method[0].ToString().ToLower() -eq "l") {
        $method = "list"
        $managerApp = "tag-list.ps1"
    } elseif ($method[0].ToString().ToLower() -eq "d" -or $method[0].ToString().ToLower() -eq "u") {
        $method = "delete"
        $managerApp = "tag-delete.ps1"
    } else {
        Write-Host "Error: Invalid method parameter. Use 'list', 'delete', or 'update'." -ForegroundColor Red
        return
    }

    $originalDir = Get-Location
    
    if (Test-Path $managerPath) {
        Set-Location -Path $managerPath
    } else {
        Write-Host "Directory '$managerPath' does not exist." -ForegroundColor Red
        return
    }
    
    $scriptPath = Join-Path $managerPath -ChildPath "$managerApp"
    if (Test-Path $scriptPath) {
        . $scriptPath -appName $appName -commitTag $commitTag -method $method
        Write-Host "Script '$managerApp' executed." -ForegroundColor Green
    } else {
        Write-Host "Script '$managerApp' not found." -ForegroundColor Red
    }
    
    Set-Location -Path $originalDir
    Write-Host "--------------------------------------------------------"
}

# Export functions
Export-ModuleMember -Function Manage-GitHubAppDev, Manage-GitTags
