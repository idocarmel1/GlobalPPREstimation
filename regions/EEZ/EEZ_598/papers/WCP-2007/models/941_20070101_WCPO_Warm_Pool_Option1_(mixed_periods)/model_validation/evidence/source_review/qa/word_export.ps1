param([string]$InputFile,[string]$PdfFile)
$ownedWord=$null;$ownedDocument=$null
try {
 $ownedWord=New-Object -ComObject Word.Application
 $ownedWord.Visible=$false
 $ownedWord.DisplayAlerts=0
 $ownedWord.AutomationSecurity=3
 $ownedDocument=$ownedWord.Documents.Open($InputFile,$false,$true,$false)
 $ownedDocument.ExportAsFixedFormat($PdfFile,17)
 Write-Output "Exported $PdfFile"
} finally {
 if($null -ne $ownedDocument){$ownedDocument.Close(0);[void][Runtime.InteropServices.Marshal]::ReleaseComObject($ownedDocument)}
 if($null -ne $ownedWord){$ownedWord.Quit(0);[void][Runtime.InteropServices.Marshal]::ReleaseComObject($ownedWord)}
 [GC]::Collect();[GC]::WaitForPendingFinalizers()
}
