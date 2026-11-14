param([string]$InputDocx, [string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$wordInstance = $null
$openedDocument = $null
try {
    $wordInstance = New-Object -ComObject Word.Application
    $wordInstance.Visible = $false
    $wordInstance.DisplayAlerts = 0
    $wordInstance.AutomationSecurity = 3
    $wordInstance.Options.UpdateLinksAtOpen = $false
    $inputAbsolute = [IO.Path]::GetFullPath($InputDocx)
    $outputAbsolute = [IO.Path]::GetFullPath($OutputPdf)
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($outputAbsolute)) | Out-Null
    $openedDocument = $wordInstance.Documents.Open($inputAbsolute, $false, $true, $false)
    $openedDocument.ExportAsFixedFormat($outputAbsolute, 17)
    Write-Output $outputAbsolute
} finally {
    if ($openedDocument) { $openedDocument.Close(0); [Runtime.InteropServices.Marshal]::FinalReleaseComObject($openedDocument) | Out-Null }
    if ($wordInstance) { $wordInstance.Quit(0); [Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordInstance) | Out-Null }
}
