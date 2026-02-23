# Document Conversion Functions
# Functions for converting between document formats

function ConvertMD-ToPDF {
    <#
    .SYNOPSIS
    Converts Markdown files to PDF using Pandoc
    
    .DESCRIPTION
    Uses Pandoc with XeLaTeX engine to convert MD to PDF with custom formatting
    
    .PARAMETER inputFile
    Path to the input Markdown file
    
    .PARAMETER fontName
    Font to use for the PDF (default: Computer Modern Serif)
    
    .PARAMETER fontSize
    Font size for the PDF (default: 12pt)
    
    .PARAMETER outputFile
    Path for the output PDF file (default: same name as input with .pdf extension)
    
    .EXAMPLE
    ConvertMD-ToPDF -inputFile "document.md"
    ConvertMD-ToPDF -inputFile "document.md" -fontName "Arial" -fontSize "11pt"
    #>
    param (
        [string]$inputFile,
        [string]$fontName="Computer Modern Serif",
        [string]$fontSize="12pt",
        [string]$outputFile="$($inputFile -replace '\.md$', '.pdf')"
    )

    # Check if the input file exists
    if (-Not (Test-Path $inputFile)) {
        Write-Host "Input file '$inputFile' does not exist." -ForegroundColor Yellow
        $currentDir = Get-Location
        $inputFile = Join-Path "$currentDir" -ChildPath "$inputFile"
        if (-Not (Test-Path $inputFile)) {
            Write-Host "Input file '$inputFile' still does not exist. Exiting function." -ForegroundColor Red
            return
        }
        else {
            Write-Host "Found input file at '$inputFile'. Proceeding with conversion." -ForegroundColor Green
            $outputFile = "$($inputFile -replace '\.md$', '.pdf')"
        }
    }

    # Convert MD to PDF using Pandoc
    if ($fontName -ne "Computer Modern Serif") {
        pandoc "$inputFile" -o "$outputFile" --pdf-engine=xelatex -V geometry:margin=0.75in -V fontsize=$fontSize -V mainfont="$fontName"
    } else {
        pandoc "$inputFile" -o "$outputFile" --pdf-engine=xelatex -V geometry:margin=0.75in -V fontsize=$fontSize
    }

    if (Test-Path $outputFile) {
        Write-Host "PDF conversion successful: '$outputFile'."
        Write-Host "Converted '$inputFile' to '$outputFile'." -ForegroundColor Green
    } else {
        Write-Host "PDF conversion failed." -ForegroundColor Red
        return
    }
}

# Export functions
Export-ModuleMember -Function ConvertMD-ToPDF
