param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$taskInput = (Resolve-Path -LiteralPath $InputDocx).Path
$taskOutput = [System.IO.Path]::GetFullPath($OutputPdf)
New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($taskOutput)) | Out-Null
$taskWord = $null
$taskDocument = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskDocument = $taskWord.Documents.Open($taskInput, $false, $true, $false)
    $taskDocument.Repaginate()
    $taskDocument.ExportAsFixedFormat($taskOutput, 17)
    Write-Output $taskOutput
} finally {
    if ($null -ne $taskDocument) { $taskDocument.Close(0); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskDocument) }
    if ($null -ne $taskWord) { $taskWord.Quit(0); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskWord) }
}
