$ErrorActionPreference = 'Stop'
$reportPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../../..\Model_validation_52_1_Sea_of_Okhotsk_NE_(1980).docx')).Path
$renderDir = Join-Path $PSScriptRoot 'render'
New-Item -ItemType Directory -Path $renderDir -Force | Out-Null
$pdfPath = Join-Path $renderDir 'validation.pdf'
$wordInstance = New-Object -ComObject Word.Application
$ownedInstance = $wordInstance.Documents.Count -eq 0
if (-not $ownedInstance) { throw 'New Word COM object has existing documents; do not operate on it.' }
$openedDocument = $null
try {
    $wordInstance.Visible = $false
    $wordInstance.DisplayAlerts = 0
    $wordInstance.AutomationSecurity = 3
    $openedDocument = $wordInstance.Documents.Open($reportPath, $false, $true, $false)
    $openedDocument.ExportAsFixedFormat($pdfPath, 17)
    Write-Output "Independent read-only Word export: $pdfPath"
} finally {
    if ($null -ne $openedDocument) {
        $openedDocument.Close(0)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($openedDocument)
    }
    if ($ownedInstance) { $wordInstance.Quit(0) }
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordInstance)
}
