param([string]$InputXlsx,[string]$OutputPdf)
$inputPath=(Resolve-Path -LiteralPath $InputXlsx).Path
$outputPath=[System.IO.Path]::GetFullPath($OutputPdf)
$excel=$null;$book=$null
try {
 $excel=New-Object -ComObject Excel.Application
 $excel.Visible=$false;$excel.DisplayAlerts=$false;$excel.AutomationSecurity=3
 $book=$excel.Workbooks.Open($inputPath,0,$true)
 $sheet=$book.Worksheets.Item(1)
 $sheet.PageSetup.PrintArea='$A$1:$G$12,$A$255:$G$259,$A$515:$G$519'
 $sheet.PageSetup.PrintTitleRows='';$sheet.PageSetup.Zoom=$false;$sheet.PageSetup.FitToPagesWide=1;$sheet.PageSetup.FitToPagesTall=1;$sheet.PageSetup.Orientation=2;$sheet.PageSetup.PaperSize=8
 $sheet2=$book.Worksheets.Item(2)
 $end=$sheet2.UsedRange.Rows.Count
 $sheet2.PageSetup.PrintArea='$A$1:$D$10,$A$'+($end-5)+':$D$'+$end
 $sheet2.PageSetup.PrintTitleRows='';$sheet2.PageSetup.Zoom=$false;$sheet2.PageSetup.FitToPagesWide=1;$sheet2.PageSetup.FitToPagesTall=1;$sheet2.PageSetup.Orientation=2;$sheet2.PageSetup.PaperSize=8
 $book.ExportAsFixedFormat(0,$outputPath)
 Write-Output "Rendered workbook preview: $outputPath"
} finally {
 if($null -ne $book){$book.Close($false);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($book)}
 if($null -ne $excel){$excel.Quit();[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel)}
}
