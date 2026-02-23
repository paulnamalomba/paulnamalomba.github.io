# Utility Functions
# Miscellaneous utility functions for PowerShell

function Get-CurrentTime {
    <#
    .SYNOPSIS
    Gets the current time in HH:mm:ss format
    
    .DESCRIPTION
    Returns the current time formatted as a string
    
    .EXAMPLE
    Get-CurrentTime
    #>
    return (Get-Date).ToString("HH:mm:ss")
}

function InstallBulk-Fonts {
    <#
    .SYNOPSIS
    Installs multiple fonts from a folder
    
    .DESCRIPTION
    Installs all TrueType (.ttf) fonts from a specified folder
    
    .PARAMETER family
    Subfolder name within the font folder
    
    .PARAMETER fontFolder
    Path to the main fonts folder
    
    .EXAMPLE
    InstallBulk-Fonts -family "Arial" -fontFolder "C:\Fonts"
    #>
    param (
        [string]$family,
        [string]$fontFolder = "<path/to/fonts/folder>"
    )
    $fontMicromanagement = Join-Path "$fontFolder" -ChildPath "$family"
    Write-Host "--------------------------------------------------------"
    Write-Host "Installing fonts from: $fontMicromanagement"
    
    if (Test-Path $fontFolder) {
        if (Test-Path $fontMicromanagement) {
            # Define the Windows Shell Application object for font installation
            $shell = New-Object -ComObject Shell.Application
            $fontsFolder = $shell.Namespace(0x14)  # CSIDL_FONTS
            
            # Get all .ttf files in the specified font subfolder
            Get-ChildItem -Path $fontMicromanagement -Filter *.ttf | ForEach-Object {
                $fontPath = $_.FullName
                $fontName = $_.Name
                Write-Host "Installing font: $fontName"
                try {
                    # Copy the font file to the Fonts folder
                    $fontsFolder.CopyHere($fontPath, 0x14)
                    Write-Host "Successfully installed: $fontName" -ForegroundColor Green
                } catch {
                    Write-Host "Failed to install: $fontName - $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "Font subfolder '$fontMicromanagement' does not exist." -ForegroundColor Yellow
        }
        Write-Host "Font installation completed."
    } else {
        Write-Host "Font folder '$fontFolder' does not exist." -ForegroundColor Red
    }
    Write-Host "--------------------------------------------------------"
}

# Export functions
Export-ModuleMember -Function Get-CurrentTime, InstallBulk-Fonts
