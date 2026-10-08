$ErrorActionPreference='Stop'
$runPath=Split-Path -Parent $PSScriptRoot
$modelPath=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $runPath))
foreach ($variant in @('baseline','current')) {
    $shortTaskFile=Join-Path $env:TEMP ('LME013_' + $variant + '_' + [Guid]::NewGuid().ToString('N') + '.xlsx')
    $sourceTaskFile=if ($variant -eq 'baseline') {Join-Path $runPath 'inputs/taxon_mapping.xlsx'} else {Join-Path $modelPath 'model_validation/taxon_mapping.xlsx'}
    Copy-Item -LiteralPath $sourceTaskFile -Destination $shortTaskFile
    $taskExcel=$null; $taskBook=$null
    try {
        $taskExcel=New-Object -ComObject Excel.Application
        $taskExcel.Visible=$false; $taskExcel.DisplayAlerts=$false; $taskExcel.AutomationSecurity=3
        $taskBook=$taskExcel.Workbooks.Open($shortTaskFile,0,$true)
        Write-Output ($variant + ' opened successfully without repair')
        if ($variant -eq 'current') {
            foreach ($spec in @(@('Taxon mappings','A1:G12','excel_mapping.pdf'),@('Sources','A1:D27','excel_mapping_sources.pdf'))) {
                Write-Output ('Rendering ' + $spec[0])
                $s=$taskBook.Worksheets.Item($spec[0]);$s.PageSetup.PrintArea=$spec[1]
                $s.PageSetup.Orientation=2;$s.PageSetup.Zoom=$false;$s.PageSetup.FitToPagesWide=1;$s.PageSetup.FitToPagesTall=1
                $shortTaskPDF=Join-Path $env:TEMP ('LME013_QA_' + [Guid]::NewGuid().ToString('N') + '.pdf')
                try {
                    $s.ExportAsFixedFormat(0,$shortTaskPDF)
                    Copy-Item -LiteralPath $shortTaskPDF -Destination (Join-Path $runPath ('qa/'+$spec[2]))
                } finally { if (Test-Path -LiteralPath $shortTaskPDF) {Remove-Item -LiteralPath $shortTaskPDF} }
            }
        }
    } catch { Write-Output ($variant + ' failed: ' + $_.Exception.Message + ' at ' + $_.ScriptStackTrace) }
    finally {
        if ($null -ne $taskBook) {try {$taskBook.Close($false)} catch {}}
        if ($null -ne $taskExcel) {try {$taskExcel.Quit()} catch {}}
        Remove-Item -LiteralPath $shortTaskFile
    }
}
