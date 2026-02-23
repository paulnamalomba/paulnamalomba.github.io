# Profile Management Functions
# Functions for managing PowerShell profiles

function Load-Profile {
    <#
    .SYNOPSIS
    Reloads the PowerShell profile
    
    .DESCRIPTION
    Sources the PowerShell profile script to reload all functions and settings
    
    .PARAMETER profilePath
    Path to the PowerShell profile script (default: $PROFILE)
    
    .EXAMPLE
    Load-Profile
    Load-Profile -profilePath "C:\Users\Username\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
    #>
    param (
        [string]$profilePath = $PROFILE
    )
    Write-Host "--------------------------------------------------------"
    Write-Host "Loading profile from: $profilePath"
    if (Test-Path $profilePath) {
        . $profilePath
        Write-Host "Profile loaded from '$profilePath'." -ForegroundColor Green
    } else {
        Write-Host "Profile file '$profilePath' not found." -ForegroundColor Yellow
    }
    Write-Host "--------------------------------------------------------"
}

# Export functions
Export-ModuleMember -Function Load-Profile
