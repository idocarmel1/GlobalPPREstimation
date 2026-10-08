$ErrorActionPreference='Stop'
$taskRun=Split-Path -Parent $PSScriptRoot
$taskValidation=Split-Path -Parent (Split-Path -Parent $taskRun)
$taskInput=Join-Path $taskValidation 'validation.docx'
$taskOutput=Join-Path $taskRun 'qa/report.pdf'
$taskWord=$null
$taskDocument=$null
try {
    $taskWord=New-Object -ComObject Word.Application
    $taskWord.Visible=$false
    $taskWord.DisplayAlerts=0
    $taskWord.AutomationSecurity=3
    $taskDocument=$taskWord.Documents.Open($taskInput,$false,$true,$false)
    $taskDocument.ExportAsFixedFormat($taskOutput,17)
    Write-Output $taskOutput
} finally {
    if ($null -ne $taskDocument) { $taskDocument.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDocument) }
    if ($null -ne $taskWord) { $taskWord.Quit(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord) }
}
