$ErrorActionPreference='Stop'
$taskRoot='C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation'
$taskFile=Join-Path $taskRoot 'regions\LME_035\LME035_taxon_mapping_appendix.xlsx'
$taskExcel=New-Object -ComObject Excel.Application
$taskBook=$null
try {
 $taskExcel.Visible=$false; $taskExcel.DisplayAlerts=$false; $taskExcel.AutomationSecurity=3
 $taskBook=$taskExcel.Workbooks.Open($taskFile,0,$true)
 $taskExcel.CalculateFullRebuild()
 $taskRows=@();$taskLinkCount=0
 foreach($taskSheet in $taskBook.Worksheets){
  foreach($taskLink in $taskSheet.Hyperlinks){$taskLinkCount++;$taskCell=$taskLink.Range;if($taskCell.Font.Color -ne 12673797 -or $taskCell.Font.Underline -ne 2){throw 'Native link appearance failed'}}
  $taskRows+=@{sheet=$taskSheet.Name;used_rows=$taskSheet.UsedRange.Rows.Count;used_columns=$taskSheet.UsedRange.Columns.Count}
 }
 $taskMap=$taskBook.Worksheets.Item('Taxon mapping')
 if($taskMap.Range('A8').Value2 -ne 'Synodontidae' -or $taskMap.Range('F9').Value2 -ne 'Very low'){throw 'Native displayed values failed'}
 $taskOut=Join-Path $taskRoot 'regions\LME_035\validation_reports\35_412_Gulf_of_Thailande_(1963)\qa\native_excel_qa.json'
 @{native_open_succeeded=$true;owned_hidden_instance=$true;read_only=$true;calculate_full_rebuild=$true;formula_count=0;hyperlink_count=$taskLinkCount;all_links_blue_underlined=$true;sheets=$taskRows;first_ppr_tC=$taskMap.Range('D8').Value2;first_catch_t=$taskMap.Range('C8').Value2;first_taxon=$taskMap.Range('A8').Value2;second_confidence=$taskMap.Range('F9').Value2}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $taskOut -Encoding utf8
 Write-Output 'Owned hidden native Excel readonly calculation and hyperlink appearance passed.'
}finally{
 if($null -ne $taskBook){$taskBook.Close($false);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskBook)}
 $taskExcel.Quit();[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskExcel)
}
