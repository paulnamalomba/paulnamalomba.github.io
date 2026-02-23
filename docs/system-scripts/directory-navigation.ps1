# Directory Navigation Functions
# Collection of functions for quickly navigating to common directories

function ChDir-Work {
    param (
        [string]$workPath = "<path/to/work/folder>"
    )
    Write-Host "--------------------------------------------------------"
    Write-Host "Changing directory to Work folder: $workPath"
    if (Test-Path $workPath) {
        Set-Location -Path $workPath
        Write-Host "Changed directory to '$workPath'."
    } else {
        Write-Host "Directory '$workPath' does not exist."
    }
    Write-Host "--------------------------------------------------------"
}

function ChDir-Documents {
    param (
        [string]$docPath = "$env:USERPROFILE\Documents"
    )
    Write-Host "--------------------------------------------------------"
    Write-Host "Changing directory to Documents folder: $docPath"
    if (Test-Path $docPath) {
        Set-Location -Path $docPath
        Write-Host "Changed directory to '$docPath'."
    } else {
        Write-Host "Directory '$docPath' does not exist."
    }
    Write-Host "--------------------------------------------------------"
}

function ChDir-Downloads {
    param (
        [string]$docPath = "$env:USERPROFILE\Downloads"
    )
    Write-Host "--------------------------------------------------------"
    Write-Host "Changing directory to Downloads folder: $docPath"
    if (Test-Path $docPath) {
        Set-Location -Path $docPath
        Write-Host "Changed directory to '$docPath'."
    } else {
        Write-Host "Directory '$docPath' does not exist."
    }
    Write-Host "--------------------------------------------------------"
}

function ChDir-CustomProject {
    <#
    .SYNOPSIS
    Navigate to a custom project directory
    
    .DESCRIPTION
    Template function for navigating to project directories
    
    .PARAMETER projectPath
    The path to the project directory
    
    .EXAMPLE
    ChDir-CustomProject -projectPath "C:\Projects\MyProject"
    #>
    param (
        [string]$projectPath = "<path/to/project/folder>"
    )
    Write-Host "--------------------------------------------------------"
    Write-Host "Changing directory to project folder: $projectPath"
    if (Test-Path $projectPath) {
        Set-Location -Path $projectPath
        Write-Host "Changed directory to '$projectPath'."
    } else {
        Write-Host "Directory '$projectPath' does not exist."
    }
    Write-Host "--------------------------------------------------------"
}

# Export functions
Export-ModuleMember -Function ChDir-Work, ChDir-Documents, ChDir-Downloads, ChDir-CustomProject
