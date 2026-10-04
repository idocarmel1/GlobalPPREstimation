param([Parameter(Mandatory=$true)][string[]]$ReportPaths)
$ErrorActionPreference = 'Stop'
foreach ($requestedPath in $ReportPaths) {
    $resolvedReportPath = (Resolve-Path -LiteralPath $requestedPath).Path
    $reportStem = [IO.Path]::GetFileNameWithoutExtension($resolvedReportPath)
    $taskRenderName = if ($reportStem.StartsWith('Article_departures_')) { 'departures' } elseif ($reportStem.StartsWith('Model_validation_52_')) { 'validation' } else { $reportStem }
    $taskRenderDirectory = Join-Path $PSScriptRoot ('qa/' + $taskRenderName)
    New-Item -ItemType Directory -Path $taskRenderDirectory -Force | Out-Null
    $taskPdfPath = Join-Path $taskRenderDirectory 'report.pdf'
    $taskTempRenderDirectory = Join-Path ([IO.Path]::GetTempPath()) ('lme052-render-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $taskTempRenderDirectory -Force | Out-Null
    $taskShortPdfPath = Join-Path $taskTempRenderDirectory 'report.pdf'
    $taskWordInstance = New-Object -ComObject Word.Application
    $taskOwnsInstance = $taskWordInstance.Documents.Count -eq 0
    if (-not $taskOwnsInstance) { throw 'New Word COM instance has existing documents; refuse active-instance interaction.' }
    $taskOpenedDocument = $null
    try {
        $taskWordInstance.Visible = $false
        $taskWordInstance.DisplayAlerts = 0
        $taskWordInstance.AutomationSecurity = 3
        $taskOpenedDocument = $taskWordInstance.Documents.Open($resolvedReportPath, $false, $true, $false)
        $taskOpenedDocument.ExportAsFixedFormat($taskShortPdfPath, 17)
        Copy-Item -LiteralPath $taskShortPdfPath -Destination $taskPdfPath -Force
        Write-Output ('Read-only independent Word export: ' + $taskPdfPath)
    } finally {
        if ($null -ne $taskOpenedDocument) {
            $taskOpenedDocument.Close(0)
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskOpenedDocument)
        }
        if ($taskOwnsInstance) { $taskWordInstance.Quit(0) }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskWordInstance)
    }
}
