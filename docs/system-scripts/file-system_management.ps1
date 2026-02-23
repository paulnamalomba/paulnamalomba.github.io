# some stuff for file system management
$currentDir = $PWD.Path

# list all directories their sizes in GB, 
# suitable for locating where data storage is centralised
function dirsize-lister {
	Write-Host "Parent-Dir ${currentDir}"
	Get-ChildItem -Path $currentDir -Directory | ForEach-Object {
   		$folderPath = $_.FullName
		$lastElement = Split-Path -Path $folderPath -Leaf
		$sizeInBytes = (Get-ChildItem -Path $folderPath -Recurse -File | Measure-Object -Property Length -Sum).Sum
		$sizeInGB = $sizeInBytes / 1024MB
    		Write-Host "Child-Dir ${lastElement}: $("{0:N2}" -f $sizeInGB) GB"
	}
}

# like an advanced grep function
# usage: findfile "name","name","name" "ext","ext","ext"
function findfile-w-string {
    param (
        [string[]]$inclname,
        [string[]]$filetypes
    )
    Get-ChildItem -Path $PWD -Recurse |
        Where-Object {
            $nameMatch = $false
            $typeMatch = $false
            foreach ($term in $inclname) {
                if ($_.Name -like "*$term*") {
                    $nameMatch = $true
                    break
                }
			}
            foreach ($ext in $filetypes) {
                if ($_.Extension -eq ".$ext") {
                    $typeMatch = $true
                    break
                }
            }
            $nameMatch -and $typeMatch
        }
}

# more file size listing but with thresh-hold for files 
# in particular for managing storage
function dissect {
	$filesizelister = ".\filesize-lister.ps1"
	powershell.exe -File $filesizelister -RootPath $PWD -ThresholdGB 0.1
}