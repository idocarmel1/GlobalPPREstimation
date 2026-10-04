param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$docPath = (Resolve-Path -LiteralPath $InputDocx).Path
$pdfPath = [System.IO.Path]::GetFullPath($OutputPdf)
$wordInstance = $null
$openedDocument = $null
try {
    $wordInstance = New-Object -ComObject Word.Application
    $wordInstance.Visible = $false
    $wordInstance.DisplayAlerts = 0
    $wordInstance.AutomationSecurity = 3
    $openedDocument = $wordInstance.Documents.Open($docPath, $false, $true, $false)
    $openedDocument.ExportAsFixedFormat($pdfPath, 17)
    Write-Output "Rendered: $pdfPath"
} finally {
    if ($null -ne $openedDocument) { $openedDocument.Close(0); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($openedDocument) }
    if ($null -ne $wordInstance) { $wordInstance.Quit(0); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordInstance) }
}
