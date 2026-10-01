$ErrorActionPreference = 'Stop'
$qaDirectory = $PSScriptRoot
$regionDirectory = Split-Path (Split-Path (Split-Path $qaDirectory -Parent) -Parent) -Parent
$sourcePath = Join-Path $regionDirectory 'Model_validation_32_1_Arabian_Sea_off_Karnataka_(2000).docx'
$renderDirectory = Join-Path $qaDirectory 'render'
New-Item -ItemType Directory -Force -Path $renderDirectory | Out-Null
$copyPath = Join-Path $renderDirectory 'render_input.docx'
Copy-Item -LiteralPath $sourcePath -Destination $copyPath -Force
$pdfPath = Join-Path $renderDirectory 'report.pdf'
$wordInstance = $null
$reviewCopy = $null
try {
    $wordInstance = New-Object -ComObject Word.Application
    $wordInstance.Visible = $false
    $wordInstance.DisplayAlerts = 0
    $reviewCopy = $wordInstance.Documents.Open($copyPath, $false, $true)
    $reviewCopy.ExportAsFixedFormat($pdfPath, 17)
    Write-Output "Rendered review copy to $pdfPath"
} finally {
    if ($null -ne $reviewCopy) { $reviewCopy.Close(0) }
    if ($null -ne $wordInstance) { $wordInstance.Quit(0) }
    if ($null -ne $reviewCopy) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($reviewCopy) }
    if ($null -ne $wordInstance) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordInstance) }
}
