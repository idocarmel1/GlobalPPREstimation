from pathlib import Path
import json,shutil,hashlib,sys
import pythoncom,win32com.client,win32process
import fitz
ROOT=Path.cwd();Q=Path(__file__).parent;R=ROOT/'regions/LME_047';MID='47_2_East_China_Sea_(2018)';O=R/'validation_reports'/MID;qa=Q/'word_qa';qa.mkdir(exist_ok=True)
proof={'renderer_fallback':'Packaged render_docx.py failed: LibreOffice soffice.exe not found on PATH. Owned hidden native Word used; all pages rasterized withPyMuPDF.'}
pythoncom.CoInitialize();app=None;doc=None
try:
 app=win32com.client.DispatchEx('Word.Application');app.Visible=False;app.DisplayAlerts=0;app.AutomationSecurity=3;proof['owned_hidden_word_dispatch_ex']=True
 doc=app.Documents.Open(str((R/f'Model_validation_{MID}.docx').resolve()),ReadOnly=True,AddToRecentFiles=False,Visible=False);doc.ExportAsFixedFormat(str((qa/'report.pdf').resolve()),17);proof['word_page_count']=doc.ComputeStatistics(2)
finally:
 if doc is not None:doc.Close(0)
 if app is not None:app.Quit(0)
 pythoncom.CoUninitialize()
d=fitz.open(qa/'report.pdf');texts=[]
for i,p in enumerate(d):p.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(qa/f'page_{i+1:02d}.png');texts.append({'page':i+1,'text':p.get_text(),'images':len(p.get_images())})
proof['pdf_pages']=len(d);d.close();(qa/'page_text.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2),encoding='utf-8')
pythoncom.CoInitialize();app=None;book=None
try:
 app=win32com.client.DispatchEx('Excel.Application');app.Visible=False;app.DisplayAlerts=False;app.EnableEvents=False;app.AutomationSecurity=3;proof['owned_excel_pid']=win32process.GetWindowThreadProcessId(app.Hwnd)[1]
 proof['excel_workbooks']=[]
 for p in [R/'LME_047.xlsx',R/'LME047_taxon_mapping_appendix.xlsx']:
  book=app.Workbooks.Open(str(p.resolve()),UpdateLinks=0,ReadOnly=True,AddToMru=False);app.CalculateFull();rows=[]
  for ss in book.Worksheets:rows.append({'sheet':ss.Name,'used_rows':ss.UsedRange.Rows.Count,'used_columns':ss.UsedRange.Columns.Count,'formula_errors':int(app.WorksheetFunction.CountIf(ss.UsedRange,'#REF!'))+int(app.WorksheetFunction.CountIf(ss.UsedRange,'#VALUE!'))})
  if p.name=='LME047_taxon_mapping_appendix.xlsx':
   ss=book.Worksheets('Taxon mapping');ss.ListObjects(1).Range.AutoFilter(6,'Very low');count=int(app.WorksheetFunction.Subtotal(103,ss.Range('A8:A283')));assert count==26;ss.ShowAllData();sort=ss.ListObjects(1).Sort;sort.SortFields.Clear();sort.SortFields.Add(ss.Range('D8:D283'),0,1);sort.Header=1;sort.Apply();asc=ss.Range('D8').Value;sort.SortFields.Clear();sort.SortFields.Add(ss.Range('D8:D283'),0,2);sort.Header=1;sort.Apply();print('NATIVE SORT',asc,ss.Range('A8').Value,ss.Range('D8').Value,flush=True);assert ss.Range('A8').Value=='Trichiurus lepturus';proof['native_filter_sort_test']={'Very_low_visible_rows':count,'ascending_then_descending_sort_restores_top_taxon':True,'save_performed':False}
  proof['excel_workbooks'].append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'opened_read_only':True,'sheets':rows,'repaired':False});book.Close(False);book=None
finally:
 if book is not None:book.Close(False)
 if app is not None:app.Quit()
 pythoncom.CoUninitialize()
(O/'native_office_open_verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8');print('NATIVE OFFICE',proof['pdf_pages'])
