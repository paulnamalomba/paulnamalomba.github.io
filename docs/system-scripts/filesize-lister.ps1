<#
.SYNOPSIS
  Lists all (first-level) subdirectories under a given folder whose total size exceeds 1 GB.

.DESCRIPTION
  For each immediate child folder of the specified root, this script
  sums the size of *all files* (recursively) and prints only those
  whose size is ≥ the threshold (default: 1 GB).

.PARAMETER RootPath
  The directory under which to scan subfolders. Defaults to the current location.

.PARAMETER ThresholdGB
  The size threshold in gigabytes. Defaults to 1 GB.

.EXAMPLE
  # List subfolders of C:\Data larger than 1 GB
  .\Get-LargeSubfolders.ps1 -RootPath 'C:\Data'

.EXAMPLE
  # List subfolders of current folder larger than 5 GB
  .\Get-LargeSubfolders.ps1 -ThresholdGB 5
#>

param(
    [Parameter(Mandatory = $false)]
    [string] $RootPath    = (Get-Location).Path,

    [Parameter(Mandatory = $false)]
    [int]    $ThresholdGB = 0.2
)

# Convert GB threshold to bytes
$thresholdBytes = $ThresholdGB * 1GB

# Scan only immediate subdirectories
Get-ChildItem -Path $RootPath -Directory | ForEach-Object {
    $folder = $_
    # Sum file sizes under this folder
    $sizeBytes = Get-ChildItem `
        -Path $folder.FullName `
        -File `
        -Recurse `
        -ErrorAction SilentlyContinue |
      Measure-Object -Property Length -Sum |
      Select-Object -ExpandProperty Sum

    if ($sizeBytes -ge $thresholdBytes) {
        [PSCustomObject]@{
            Folder = $folder.FullName
            SizeGB = '{0:N2}' -f ($sizeBytes / 1GB)
        }
    }
} |

# Sort largest first
Sort-Object SizeGB -Descending | ForEach-Object {
    "Folder: $($_.Folder)"
    "Size (GB): $($_.SizeGB)"
    ""
}

