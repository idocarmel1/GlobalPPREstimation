param([Parameter(Mandatory=$true)][string]$InputFile,[Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference='Stop'
$taskOutput=(New-Item -ItemType Directory -Force -Path $OutputDirectory).FullName
$fileSystem=New-Object -ComObject Scripting.FileSystemObject
$source=$fileSystem.GetFile((Resolve-Path -LiteralPath $InputFile).Path).ShortPath
$destination=$fileSystem.GetFolder($taskOutput).ShortPath
$word=$null
$doc=$null
try {
    Write-Output 'Starting independent Word instance'
    $word=New-Object -ComObject Word.Application
    $word.Visible=$false
    $word.DisplayAlerts=0
    $word.AutomationSecurity=3
    Write-Output 'Opening permitted report read-only'
    $doc=$word.Documents.Open($source,$false,$true,$false)
    Write-Output 'Exporting PDF without saving DOCX'
    $doc.ExportAsFixedFormat((Join-Path $destination 'report.pdf'),17)
    Write-Output ('Pages: '+$doc.ComputeStatistics(2))
} finally {
    if ($null -ne $doc) { $doc.Close(0); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
    if ($null -ne $word) { $word.Quit(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($fileSystem)
}
