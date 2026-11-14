param([Parameter(Mandatory=$true)][string]$DocumentPath,[Parameter(Mandatory=$true)][string]$PdfPath)
$ErrorActionPreference='Stop'
$documentAbsolute=(Resolve-Path -LiteralPath $DocumentPath).Path
$pdfAbsolute=[System.IO.Path]::GetFullPath($PdfPath)
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($pdfAbsolute)) | Out-Null
$word=$null
$document=$null
try {
  $word=New-Object -ComObject Word.Application
  $word.Visible=$false
  $word.DisplayAlerts=0
  $word.AutomationSecurity=3
  $document=$word.Documents.Open($documentAbsolute,$false,$true,$false)
  $document.ExportAsFixedFormat($pdfAbsolute,17)
  Write-Output $pdfAbsolute
} finally {
  if($null -ne $document){$document.Close(0);[void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)}
  if($null -ne $word){$word.Quit(0);[void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)}
}
