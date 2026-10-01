$ErrorActionPreference = 'Stop'
$taskRegion = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../..')
$taskDocPath = Join-Path $taskRegion 'Model_validation_36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s).docx'
$taskRenderPath = Join-Path $PSScriptRoot 'render'
[void](New-Item -ItemType Directory -Path $taskRenderPath -Force)
$taskPdfPath = Join-Path $taskRenderPath 'report.pdf'
$taskWord = $null
$taskDocument = $null
try {
  $taskWord = New-Object -ComObject Word.Application
  $taskWord.Visible = $false
  $taskWord.DisplayAlerts = 0
  $taskWord.AutomationSecurity = 3
  $taskDocument = $taskWord.Documents.Open($taskDocPath,$false,$true)
  $taskDocument.ExportAsFixedFormat($taskPdfPath,17)
  Write-Output $taskPdfPath
} finally {
  if ($null -ne $taskDocument) { $taskDocument.Close($false); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDocument) }
  if ($null -ne $taskWord) { $taskWord.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord) }
}
