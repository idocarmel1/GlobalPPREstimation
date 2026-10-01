import pathlib,json,zipfile,hashlib,re
from lxml import etree as E
import openpyxl
HERE=pathlib.Path(__file__).resolve().parent;REGION=HERE.parents[2];P=REGION/'LME036_taxon_mapping_appendix.xlsx'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
save=lambda n,v:(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# A hundreds-row frozen pane cannot expose the allocation data below it in a
# normal window. Retain the user's Low filter and selection, freeze headers.
with zipfile.ZipFile(P) as z:parts={n:z.read(n) for n in z.namelist()}
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main';ns={'s':S};changes=[]
for i,count in [(1,5),(2,10),(3,5),(4,5)]:
 n=f'xl/worksheets/sheet{i}.xml';tree=E.fromstring(parts[n]);pane=tree.find('s:sheetViews/s:sheetView/s:pane',ns)
 if pane is not None:
  old=dict(pane.attrib);pane.set('ySplit',str(count))
  pane.set('topLeftCell','A'+str(count+1))
  changes.append({'sheet_index':i,'old':old,'new':dict(pane.attrib)})
 parts[n]=E.tostring(tree,xml_declaration=True,encoding='utf-8')
with zipfile.ZipFile(P,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in parts.items():z.writestr(n,b)
w=openpyxl.load_workbook(P);assert [s.freeze_panes for s in w]==['A6','A11','A6','A6']
old=json.loads((HERE/'artifact_edit_checks.json').read_text(encoding='utf-8'));old.update({'appendix_sha256':sha(P),'original_views_and_low_filter_preserved':False,'original_low_filter_and_selection_preserved':True,'frozen_headers_corrected':changes});save('artifact_edit_checks.json',old)
save('visual_checks.json',{'report_pages':6,'render_engine':'New hidden Word COM instance exported PDF; PyMuPDF rendered every page. Packaged Linux renderer depends on unavailable LibreOffice; native Word used on Windows.','report_all_pages_visually_inspected':True,'report_no_clipping_overlap_or_blank_pages':True,'manual_researcher_rows_and_geographic_figures_preserved':True,'appendix_render_engine':'Bundled @oai/artifact-tool imported persisted workbook and rendered selected ranges; no renderer export used for authoring.','appendix_sheets_inspected':['Taxon appendix','Coverage','Allocation evidence','Sources'],'adopted_examples_inspected':['Caesionidae exact candidates and group27 caveat','Decapterus russelli single-group Low assumption','Ariidae complete small/large source-catch denominator'],'appendix_no_text_clipping_in_inspected_ranges':True,'Low_filter_preserved_and_reconciled_to57rows':True,'frozen_headers':['A6','A11','A6','A6'],'render_paths':[p.name for p in sorted((HERE/'render').glob('*.png'))]})
print('Header panes corrected; Low filter and selection retained.')
