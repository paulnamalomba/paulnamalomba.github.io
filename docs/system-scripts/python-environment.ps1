# Python Environment Management Functions
# Functions for managing Python virtual environments

function ActivatePyEnv-Py3Env {
    <#
    .SYNOPSIS
    Activates a Python virtual environment
    
    .DESCRIPTION
    Activates the specified Python virtual environment by running its activation script
    
    .PARAMETER envName
    Name of the virtual environment folder (default: py3env)
    
    .PARAMETER envBasePath
    Base path where virtual environments are stored (default: user profile)
    
    .EXAMPLE
    ActivatePyEnv-Py3Env
    ActivatePyEnv-Py3Env -envName "myenv"
    ActivatePyEnv-Py3Env -envName "myenv" -envBasePath "C:\VirtualEnvs"
    #>
    param (
        [string]$envName = "py3env",
        [string]$envBasePath = "$env:USERPROFILE"
    )
    Write-Host "--------------------------------------------------------"
    Write-Host "Activating Python environment: $envName"
    $envPath = Join-Path $envBasePath "$envName\Scripts\Activate.ps1"
    if (Test-Path $envPath) {
        . $envPath
        Write-Host "Environment '$envName' activated." -ForegroundColor Green
    } else {
        Write-Host "Environment '$envName' not found at '$envPath'." -ForegroundColor Yellow
    }
    Write-Host "--------------------------------------------------------"
}

# Export functions
Export-ModuleMember -Function ActivatePyEnv-Py3Env
