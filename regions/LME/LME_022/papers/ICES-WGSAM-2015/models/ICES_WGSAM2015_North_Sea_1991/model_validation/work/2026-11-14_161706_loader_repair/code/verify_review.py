from pathlib import Path,PureWindowsPath
import json,hashlib,zipfile,sys,csv,math,subprocess
from urllib.parse import urlsplit,unquote
from lxml import etree as E
from openpyxl import load_workbook
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
RUN=Path(__file__).resolve().parents[1];BASE=RUN.parents[1];RESULTS=BASE.parent/'results/diagnostics/2026-11-14_loader_repair'
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.validation_percentage_format import verify_report
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
proof={}; errors=[]
baseline=read(RUN/'inputs/start_hashes.json')
protected={p:sha(ROOT/p)==s for p,s in baseline.items() if not p.startswith('tools/scientific_code/')}
concurrent=[p for p,ok in protected.items() if not ok and '/NS-2025/' in p and '/model_validation/' in p]
if not protected['Project.xlsx']:
 registration_backup=ROOT/'regions/LME/LME_049/papers/KUR-2019/models/49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)/model_validation/work/2026-11-14_163000_register_review/inputs/Project_before_registration.xlsx'
 assert sha(registration_backup)==baseline['Project.xlsx']
 assert protected['regions/LME/LME_022/LME_022.xlsx']
 concurrent.append('Project.xlsx')
 proof['concurrent_registry_change']={'task_start_sha256':baseline['Project.xlsx'],
  'current_sha256':sha(ROOT/'Project.xlsx'),'registration_before_sha256':sha(registration_backup),
  'owner':'GlobalPPREstimation coordinator, thread 01a1daa4-cbff-7830-8cb0-b8342b49ec5d',
  'evidence':'Coordinator identified separate LME049 registration followed by ongoing shared publication. Its before-registration workbook exactly matches this task baseline. This task issued no Project.xlsx writes; the authoritative LME022 regional workbook is byte-identical.'}
errors += [f'protected file changed: {p}' for p,ok in protected.items() if not ok and p not in concurrent]
proof['protected_files']=protected
proof['concurrent_other_chat_report_changes']=concurrent
proof['concurrent_change_explanation']='Separate user-authorized Scotland correction chat owns its report; the new coordinator owns shared registry updates. This task wrote neither. Canonical sources and the LME022 regional workbook remain protected.'
report=BASE/'validation.docx'; appendix=BASE/'taxon_mapping.xlsx'
verify_report(report)
proof['percentage_format']=True
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W='{'+NS['w']+'}'
def read_zip(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
old=read_zip(RUN/'inputs/validation.docx');new=read_zip(report)
assert old.keys()==new.keys()
changed=[n for n in old if old[n]!=new[n]]
assert set(changed)=={'word/document.xml','word/_rels/document.xml.rels'}
proof['docx_changed_parts']=changed
def fields(xml):
 tree=E.fromstring(xml);tbl=tree.find('.//'+W+'body/'+W+'tbl')
 return {''.join(r.findall(W+'tc')[0].xpath('.//w:t/text()',namespaces=NS)):r.findall(W+'tc')[1] for r in tbl.findall(W+'tr')[1:]}
before=fields(old['word/document.xml']);after=fields(new['word/document.xml'])
updated=set(read(RUN/'inputs/report_update.json')['fields'])
assert all(E.tostring(before[k])==E.tostring(after[k]) for k in before if k not in updated)
proof['all_unedited_field_cells_preserved']=True
manual=''.join(after['Review and reproducibility'].xpath('.//w:t/text()',namespaces=NS))
assert 'MODEL VALIDATED' not in manual and 'MODEL DISQUALIFIED' not in manual
proof['researcher_review_unsigned']=True
links=[]
for rel in E.fromstring(new['word/_rels/document.xml.rels']):
 if not rel.get('Type','').endswith('/hyperlink'):continue
 target=rel.get('Target');url=urlsplit(target)
 if url.scheme in ('http','https','mailto'):continue
 assert not url.scheme and not PureWindowsPath(target).drive and not target.startswith(('/','\\'))
 assert (BASE/unquote(url.path)).resolve().exists(),target
 links.append(target)
tree=E.fromstring(new['word/document.xml'])
for h in tree.xpath('//w:hyperlink',namespaces=NS):
 for r in h.findall(W+'r'):
  assert r.xpath('./w:rPr/w:color[@w:val="0563C1"]',namespaces=NS)
  assert r.xpath('./w:rPr/w:u[@w:val="single"]',namespaces=NS)
proof['docx_local_links']=links
proof['docx_links_blue_underlined']=True
oldx=read_zip(RUN/'inputs/taxon_mapping.xlsx');newx=read_zip(appendix)
names=[n for n in oldx if n in ['xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml'] or n.startswith(('xl/worksheets/_rels/sheet1.','xl/worksheets/_rels/sheet2.'))]
assert all(newx[n]==oldx[n] for n in names)
proof['appendix_preserved_sheet_parts']=names
wb=load_workbook(appendix,data_only=False);oldwb=load_workbook(RUN/'inputs/taxon_mapping.xlsx',data_only=False)
for name in ['Taxon mapping','Sources']:
 ws=wb[name];original=oldwb[name]
 assert ws.max_row==original.max_row and ws.max_column==original.max_column
 for rows in zip(ws.iter_rows(),original.iter_rows()):
  for cell,previous in zip(*rows):
   assert cell.value==previous.value,(name,cell.coordinate)
   assert cell.number_format==previous.number_format,(name,cell.coordinate,'number format')
proof['appendix_mapping_and_sources_values_unchanged']=True
ws=wb['Taxon mapping'];assert ws.max_row==391 and ws.max_column==7 and ws.freeze_panes=='B8'
audit=read(BASE/'evidence/source_review/mapping_audit.json')
assert math.isclose(sum(ws.cell(i,3).value for i in range(8,392)),audit['totals']['catch_tonnes'],rel_tol=1e-13)
assert math.isclose(sum(ws.cell(i,4).value for i in range(8,392)),audit['totals']['known_simple_chain_ppr_tC'],rel_tol=1e-13)
proof['appendix_384_taxa_totals_preserved']=True
summary=read(RESULTS/'report_ready.json')['summary']
assert len(summary)==3 and all(m['status']=='WARN' and m['negative_entries']==0 and m['balance']['is_balanced'] for m in summary)
with (RESULTS/'negative_entries.tsv').open(encoding='utf-8',newline='') as f:assert list(csv.DictReader(f,delimiter='\t'))==[]
proof['current_three_methods']='WARN; complete finite nonnegative matrices and closed PP budgets'
proof['main_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
proof['repair_commit']='38cb75d066c5f78d47ba20fc6ab8545a9a6d5c69'
subprocess.run(['git','merge-base','--is-ancestor',proof['repair_commit'],'HEAD'],cwd=ROOT,check=True)
proof['git_index_empty_at_check']=not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
integration=read(RUN/'qa/integration_manifest.json')
proof['integration_manifest']=integration['status']
assert integration['status']=='integrated'
proof['files']={'report_sha256':sha(report),'appendix_sha256':sha(appendix)}
proof['errors']=errors
proof['ready_for_review']=not errors
proof['scientific_validation_complete']=False
proof['remaining_limitations']='High detritus SPPR and runtime assumptions; exact-model mapping absent; native Key Run equivalence unavailable.'
(RUN/'qa/final_review_verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ready_for_review':not errors,'errors':errors,'protected':len(protected),'concurrent_other_chat_report_changes':len(concurrent),'docx_local_links':len(links),'appendix_taxa':384,'commit':proof['main_commit']},indent=2))
if errors:raise SystemExit(1)
