$excelRead = New-Object -ComObject Excel.Application
$excelRead.Visible=$false
$excelRead.DisplayAlerts=$false
$excelRead.AutomationSecurity=3
try {
 $bookRead=$excelRead.Workbooks.Open('C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\קוד\PPR_Ecopath_Atlas\archive\regions\LME_013\HUM-2018\extracted\work\supplement.xlsx',0,$true)
 $exportTables=@(@('Table A-resolved parameters','A1:L44','resolved-parameters'),@('Table B-resolved diet','A1:AN43','resolved-diet'),@('Table C-resolved detritus fate','A1:G42','resolved-fate'),@('Table F-aggregated diet','A1:Y28','aggregated-diet'))
 foreach($spec in $exportTables) {
  $sheetRead=$bookRead.Worksheets.Item($spec[0])
  $sheetRead.PageSetup.PrintArea=$spec[1]
  $sheetRead.PageSetup.Orientation=2
  $sheetRead.PageSetup.Zoom=$false
  $sheetRead.PageSetup.FitToPagesWide=1
  $sheetRead.PageSetup.FitToPagesTall=1
  $sheetRead.ExportAsFixedFormat(0,'C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\קוד\PPR_Ecopath_Atlas\archive\regions\LME_013\HUM-2018\extracted\work\'+$spec[2]+'.pdf')
  Write-Output $spec[2]
 }
 $bookRead.Close($false)
} finally { $excelRead.Quit();[Runtime.InteropServices.Marshal]::ReleaseComObject($excelRead)|Out-Null }

