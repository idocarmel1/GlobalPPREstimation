$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSCommandPath
$repoRoot = (Resolve-Path -LiteralPath '.').Path
$sourcePath = Join-Path $repoRoot 'regions/LME_013/papers/HUM-2018/Supplementary material revised and final.xls'
$outDir = Join-Path $taskRoot 'evidence'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$excel = $null
$book = $null
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $book = $excel.Workbooks.Open($sourcePath, 0, $true)
    $sheets = @()
    foreach ($sheet in $book.Worksheets) {
        $used = $sheet.UsedRange
        $cells = @()
        for ($row = $used.Row; $row -lt $used.Row + $used.Rows.Count; $row++) {
            for ($col = $used.Column; $col -lt $used.Column + $used.Columns.Count; $col++) {
                $cell = $sheet.Cells.Item($row, $col)
                if ($null -ne $cell.Value2 -or $cell.Text -ne '') {
                    $cells += [ordered]@{ row=$row; column=$col; address=$cell.Address($false,$false); value=$cell.Value2; display=$cell.Text; number_format=$cell.NumberFormat; formula=$cell.Formula; bold=[bool]$cell.Font.Bold; italic=[bool]$cell.Font.Italic }
                }
                [void][Runtime.InteropServices.Marshal]::ReleaseComObject($cell)
            }
        }
        $sheets += [ordered]@{name=$sheet.Name; rows=$used.Rows.Count; columns=$used.Columns.Count; start_row=$used.Row; start_column=$used.Column; visible=$sheet.Visible; cells=$cells}
        Write-Output "$($sheet.Name): $($used.Rows.Count) rows x $($used.Columns.Count) columns; $($cells.Count) nonempty cells"
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($used)
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($sheet)
    }
    $snapshot = [ordered]@{source='../../../papers/HUM-2018/Supplementary material revised and final.xls';source_sha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLower();read_only=$true;extraction_method='Excel COM Value2, displayed Text, NumberFormat, Formula and style; source opened read-only';sheets=$sheets}
    $json = $snapshot | ConvertTo-Json -Depth 12
    [IO.File]::WriteAllText((Join-Path $outDir 'supplement_cells.json'),$json,[Text.UTF8Encoding]::new($false))
}
finally {
    if ($book) { $book.Close($false); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($book) }
    if ($excel) { $excel.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($excel) }
    [GC]::Collect();[GC]::WaitForPendingFinalizers()
}
