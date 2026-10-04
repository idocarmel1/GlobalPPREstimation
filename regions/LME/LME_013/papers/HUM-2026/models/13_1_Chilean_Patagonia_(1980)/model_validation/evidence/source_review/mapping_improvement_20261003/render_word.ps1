param([Parameter(Mandatory=$true)][string]$DocumentPath,[Parameter(Mandatory=$true)][string]$PdfPath)
$ErrorActionPreference='Stop'
$wordTask=$null
$documentTask=$null
try {
  $documentAbsolute=(Resolve-Path -LiteralPath $DocumentPath).Path
  $pdfAbsolute=[System.IO.Path]::GetFullPath($PdfPath)
  [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($pdfAbsolute)) | Out-Null
  $wordTask=New-Object -ComObject Word.Application
  $wordTask.Visible=$false
  $wordTask.DisplayAlerts=0
  $wordTask.AutomationSecurity=3
  $documentTask=$wordTask.Documents.Open($documentAbsolute,$false,$true,$false)
  $documentTask.ExportAsFixedFormat($pdfAbsolute,17)
  Write-Output $pdfAbsolute
} finally {
  if ($null -ne $documentTask) {
    $documentTask.Close(0)
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($documentTask)
  }
  if ($null -ne $wordTask) {
    $wordTask.Quit(0)
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordTask)
  }
}
