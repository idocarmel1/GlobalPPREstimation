param([string]$InputDocx, [string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$inputResolved = (Resolve-Path -LiteralPath $InputDocx).Path
$outputResolved = [System.IO.Path]::GetFullPath($OutputPdf)
$outputParent = [System.IO.Path]::GetDirectoryName($outputResolved)
[void][System.IO.Directory]::CreateDirectory($outputParent)
$wordRender = $null
$docRender = $null
try {
  $wordRender = New-Object -ComObject Word.Application
  $wordRender.Visible = $false
  $wordRender.DisplayAlerts = 0
  $wordRender.AutomationSecurity = 3
  $wordRender.Options.UpdateLinksAtOpen = $false
  $wordRender.Options.UpdateFieldsAtPrint = $false
  $wordRender.Options.UpdateLinksAtPrint = $false
  $docRender = $wordRender.Documents.Open($inputResolved, $false, $true, $false)
  $docRender.ExportAsFixedFormat($outputResolved, 17)
  Write-Output $outputResolved
} finally {
  if ($null -ne $docRender) { $docRender.Close(0); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($docRender) }
  if ($null -ne $wordRender) { $wordRender.Quit(0); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordRender) }
}
