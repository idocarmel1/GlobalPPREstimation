$ErrorActionPreference = 'Stop'
$runPath = Split-Path -Parent $PSScriptRoot
$modelPath = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $runPath))
$qaPath = Join-Path $runPath 'qa'
$wordTask = $null
$wordDoc = $null
try {
    $wordTask = New-Object -ComObject Word.Application
    $wordTask.Visible = $false
    $wordTask.DisplayAlerts = 0
    $wordTask.AutomationSecurity = 3
    $wordDoc = $wordTask.Documents.Open((Join-Path $modelPath 'model_validation/source_value_corrections.docx'),$false,$true)
    $wordDoc.ExportAsFixedFormat((Join-Path $qaPath 'corrections_render.pdf'),17)
} finally {
    if ($null -ne $wordDoc) { $wordDoc.Close($false) }
    if ($null -ne $wordTask) { $wordTask.Quit() }
}
$excelTask = $null
$excelBook = $null
$shortMappingPath = Join-Path $env:TEMP ('LME013_QA_' + [Guid]::NewGuid().ToString('N') + '.xlsx')
try {
    $excelTask = New-Object -ComObject Excel.Application
    $excelTask.Visible = $false
    $excelTask.DisplayAlerts = $false
    $excelTask.AutomationSecurity = 3
    $excelBook = $excelTask.Workbooks.Open((Join-Path $modelPath 'sppr_source.xlsx'),0,$true)
    foreach ($spec in @(@('Validation summary','A1:M7','excel_summary.pdf'),@('Negative SPPR','A1:K8','excel_negatives.pdf'),@('Sources','A1:B6','excel_sources.pdf'))) {
        $sheet = $excelBook.Worksheets.Item($spec[0])
        $sheet.PageSetup.PrintArea = $spec[1]
        $sheet.PageSetup.Zoom = $false
        $sheet.PageSetup.FitToPagesWide = 1
        $sheet.PageSetup.FitToPagesTall = 1
        $sheet.ExportAsFixedFormat(0,(Join-Path $qaPath $spec[2]))
    }
    $excelBook.Close($false)
    $excelBook = $null
    try { $excelTask.Quit() } catch { }
    $excelTask = New-Object -ComObject Excel.Application
    $excelTask.Visible = $false
    $excelTask.DisplayAlerts = $false
    $excelTask.AutomationSecurity = 3
    Copy-Item -LiteralPath (Join-Path $modelPath 'model_validation/taxon_mapping.xlsx') -Destination $shortMappingPath
    $excelBook = $excelTask.Workbooks.Open($shortMappingPath,0,$true)
    foreach ($spec in @(@('Taxon mappings','A1:G12','excel_mapping.pdf'),@('Sources','A1:D14','excel_mapping_sources.pdf'))) {
        $sheet = $excelBook.Worksheets.Item($spec[0])
        $sheet.PageSetup.PrintArea = $spec[1]
        $sheet.PageSetup.Orientation = 2
        $sheet.PageSetup.Zoom = $false
        $sheet.PageSetup.FitToPagesWide = 1
        $sheet.PageSetup.FitToPagesTall = 1
        $sheet.ExportAsFixedFormat(0,(Join-Path $qaPath $spec[2]))
    }
} catch {
    Write-Output $_.Exception.ToString()
    throw
} finally {
    if ($null -ne $excelBook) { try { $excelBook.Close($false) } catch { Write-Output 'Read-only Excel workbook was already disconnected.' } }
    if ($null -ne $excelTask) { try { $excelTask.Quit() } catch { Write-Output 'Created Excel instance was already disconnected.' } }
    if (Test-Path -LiteralPath $shortMappingPath) { Remove-Item -LiteralPath $shortMappingPath }
}
Write-Output 'Read-only Word and Excel render exports completed; no Office file saved.'
