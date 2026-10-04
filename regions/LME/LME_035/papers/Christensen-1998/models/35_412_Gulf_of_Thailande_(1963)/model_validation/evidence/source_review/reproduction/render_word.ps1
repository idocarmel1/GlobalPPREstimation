param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$taskWord = $null
$taskDocument = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskDocument = $taskWord.Documents.Open((Resolve-Path -LiteralPath $InputDocx).Path,$false,$true,$false)
    $taskDocument.ExportAsFixedFormat([IO.Path]::GetFullPath($OutputPdf),17)
    Write-Output 'Owned hidden Word instance exported read-only document to PDF.'
} finally {
    if ($null -ne $taskDocument) { $taskDocument.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskDocument) }
    if ($null -ne $taskWord) { $taskWord.Quit(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord) }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
