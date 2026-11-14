param([Parameter(Mandatory=$true)][string]$DocumentPath, [Parameter(Mandatory=$true)][string]$PdfPath)
$ErrorActionPreference = 'Stop'
$docAbsolute = (Resolve-Path -LiteralPath $DocumentPath).Path
$pdfAbsolute = [System.IO.Path]::GetFullPath($PdfPath)
$wordRender = $null
$readDoc = $null
try {
    $wordRender = New-Object -ComObject Word.Application
    $wordRender.Visible = $false
    $wordRender.DisplayAlerts = 0
    $wordRender.AutomationSecurity = 3
    $readDoc = $wordRender.Documents.Open($docAbsolute, $false, $true, $false)
    $readDoc.ExportAsFixedFormat($pdfAbsolute, 17)
    $readDoc.Close(0)
    $readDoc = $null
    Write-Output "Rendered read-only document to $pdfAbsolute"
} finally {
    if ($null -ne $readDoc) { $readDoc.Close(0) }
    if ($null -ne $wordRender) {
        $wordRender.Quit(0)
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordRender) | Out-Null
    }
}
