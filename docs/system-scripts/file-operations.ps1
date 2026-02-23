# File Operations Functions
# Collection of functions for file and folder operations

function MoveItem-Overwrite {
    <#
    .SYNOPSIS
    Moves an item with overwrite capability
    
    .DESCRIPTION
    Removes the destination if it exists, then moves the source to destination
    
    .PARAMETER Src
    Source path (can be file or folder)
    
    .PARAMETER Dest
    Destination path
    
    .EXAMPLE
    MoveItem-Overwrite -Src "C:\Source\File.txt" -Dest "C:\Destination\File.txt"
    #>
    param (
        [string]$Src,
        [string]$Dest
    )
    Write-Host "--------------------------------------------------------"
    # 1. Remove existing folder (if present)
    if (Test-Path -LiteralPath $Dest) {
        Remove-Item `
            -LiteralPath $Dest `
            -Recurse `
            -Force
        Write-Host "Removed existing folder/file at '$Dest'."
    }

    # 2. Move the source folder
    Move-Item `
        -LiteralPath $Src `
        -Destination $Dest `
        -Force
    if (Test-Path -LiteralPath $Dest) {
        Write-Host "Move operation successful." -ForegroundColor Green
        Write-Host "Moved folder from '$Src' to '$Dest'."
    } else {
        Write-Host "Move operation failed." -ForegroundColor Red
    }
    Write-Host "--------------------------------------------------------"
}

function RenameFolders-FirstLetterUppercase {
    <#
    .SYNOPSIS
    Renames all folders to have first letter uppercase
    
    .DESCRIPTION
    Enumerates all directories and renames them with first letter capitalized
    
    .PARAMETER Path
    The path to process (default is current directory)
    
    .EXAMPLE
    RenameFolders-FirstLetterUppercase -Path "C:\MyFolder"
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory=$false)]
        [string]$Path = '.'
    )

    # Enumerate all directories under the specified path
    Get-ChildItem -Path $Path -Directory | ForEach-Object {
        $oldName = $_.Name
        $parentPath = $_.Parent.FullName
        Write-Host "Processing folder: $oldName"
        if ($oldName.Length -ge 1) {
            # Construct the new folder name
            $newName = $oldName.Substring(0,1).ToUpper() + $oldName.Substring(1)
            Write-Host "New folder name will be: $newName"
            if ($newName -cne $oldName) {
                $oldFullPath = $_.FullName
                $newFullPath = Join-Path -Path $parentPath -ChildPath $newName
                Write-Host "Old full path: $oldFullPath"
                Write-Host "New full path: $newFullPath"
                Write-Host "Considering rename of $oldName to $newName"
                # Handle case-only on NTFS
                if ($oldName.ToLower() -eq $newName.ToLower()) {
                    $tmpName     = "{0}_tmp_{1}" -f $newName, ([guid]::NewGuid().ToString('N'))
                    $tmpFullPath = Join-Path $parentPath $tmpName

                    Move-Item -LiteralPath $oldFullPath -Destination $tmpFullPath -Force
                    Move-Item -LiteralPath $tmpFullPath -Destination $newFullPath -Force

                    Write-Host "Case-only rename: '$oldName' → '$newName' via temp '$tmpName'"
                }
                else {
                    Move-Item -LiteralPath $oldFullPath -Destination $newFullPath -Force
                    Write-Host "Renamed '$oldName' to '$newName'"
                }
            }
        }
    }
}

function ListSize-Directory {
    <#
    .SYNOPSIS
    Lists all directories and their sizes in GB
    
    .DESCRIPTION
    Suitable for locating where data storage is centralized
    
    .PARAMETER Path
    The parent directory to analyze (default is current directory)
    
    .EXAMPLE
    ListSize-Directory
    ListSize-Directory -Path "C:\MyFolder"
    #>
    param(
        [string]$Path = (Get-Location).Path
    )
    
    Write-Host "Parent-Dir ${Path}"
    Get-ChildItem -Path $Path -Directory | ForEach-Object {
        $folderPath = $_.FullName
        $lastElement = Split-Path -Path $folderPath -Leaf
        $sizeInBytes = (Get-ChildItem -Path $folderPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $sizeInGB = $sizeInBytes / 1GB
        Write-Host "Child-Dir ${lastElement}: $("{0:N2}" -f $sizeInGB) GB"
    }
}

# Export functions
Export-ModuleMember -Function MoveItem-Overwrite, RenameFolders-FirstLetterUppercase, ListSize-Directory
