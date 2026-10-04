$ErrorActionPreference='Stop'
$taskRoot='C:\Users\idoca\.codex\worktrees\e5f1\GlobalPPREstimation'
$taskFile=Join-Path $taskRoot 'regions\LME_038\LME038_taxon_mapping_appendix.xlsx'
$taskEvidence=Join-Path $taskRoot 'regions\LME_038\validation_reports\38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
$taskExcel=New-Object -ComObject Excel.Application
$taskBook=$null
try {
 $taskExcel.Visible=$false;$taskExcel.DisplayAlerts=$false;$taskExcel.AutomationSecurity=3
 $taskBook=$taskExcel.Workbooks.Open($taskFile,0,$true);$taskExcel.CalculateFullRebuild()
 $taskAudit=Get-Content -LiteralPath (Join-Path $taskEvidence 'taxon_audit.json') -Raw -Encoding UTF8|ConvertFrom-Json
 $taskExpected=$taskAudit|Sort-Object -Property @{Expression='simple_chain_ppr_tC';Descending=$true},taxon|Select-Object -First 1
 $taskMap=$taskBook.Worksheets.Item('Taxon mapping')
 if($taskMap.Range('A8').Value2 -ne $taskExpected.taxon){throw 'Native first sorted taxon differs'}
 if([Math]::Abs($taskMap.Range('D8').Value2-$taskExpected.simple_chain_ppr_tC) -gt 0.00001){throw 'Native first PPR differs'}
 $taskRows=@();$taskLinks=0;$taskClipped=@();$taskFitRows=0
 foreach($taskSheet in $taskBook.Worksheets){
  foreach($taskLink in $taskSheet.Hyperlinks){$taskLinks++;$taskCell=$taskLink.Range;if($taskCell.Font.Color -ne 12673797 -or $taskCell.Font.Underline -ne 2){throw 'Native hyperlink appearance differs'}}
  $taskRows+=@{sheet=$taskSheet.Name;rows=$taskSheet.UsedRange.Rows.Count;columns=$taskSheet.UsedRange.Columns.Count}
  $taskStart=if($taskSheet.Name -eq 'Taxon mapping'){8}else{5};$taskEnd=if($taskSheet.Name -eq 'Taxon mapping'){188}else{23}
  for($taskRow=$taskStart;$taskRow -le $taskEnd;$taskRow++){
   $taskRange=$taskSheet.Rows.Item($taskRow);$taskOriginalHeight=$taskRange.RowHeight;[void]$taskRange.AutoFit();$taskRequiredHeight=$taskRange.RowHeight
   if($taskRequiredHeight -gt $taskOriginalHeight+0.2){$taskClipped+=@{sheet=$taskSheet.Name;row=$taskRow;actual_height=$taskOriginalHeight;required_height=$taskRequiredHeight}}
   $taskRange.RowHeight=$taskOriginalHeight;$taskFitRows++
  }
 }
 @{native_open_succeeded=$true;owned_hidden_instance=$true;read_only=$true;full_rebuild=$true;hyperlink_count=$taskLinks;all_links_blue_underlined=$true;sheets=$taskRows;first_taxon=$taskMap.Range('A8').Value2;first_ppr_tC=$taskMap.Range('D8').Value2;fit_rows_checked=$taskFitRows;rows_requiring_expansion=$taskClipped}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $taskEvidence 'qa\native_excel_qa.json') -Encoding utf8
 Write-Output "Owned hidden native Excel read-only checks: $taskLinks links, $taskFitRows row fits, $($taskClipped.Count) rows need expansion."
 if($taskClipped.Count -gt 0){throw 'Native Excel text row clipping detected'}
}finally{
 if($null -ne $taskBook){$taskBook.Close($false);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskBook)}
 $taskExcel.Quit();[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskExcel)
 [GC]::Collect();[GC]::WaitForPendingFinalizers()
}
