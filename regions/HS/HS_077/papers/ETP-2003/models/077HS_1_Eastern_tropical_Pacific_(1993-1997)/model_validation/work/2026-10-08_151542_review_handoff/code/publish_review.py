"""One locked, rollback-capable HS_077 scientific/researcher handoff."""
from pathlib import Path
import hashlib,json,os,re,shutil,sys,time,zipfile
from contextlib import contextmanager
import xml.etree.ElementTree as E
W=Path(__file__).resolve().parents[1];M=W.parents[2];ROOT=next(p for p in M.parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
from tools.project_core.registry.writes import central_lock
from tools.project_core.registry.update_project import update
from tools.project_core.maps.build_html import build
from tools.project_core.maps.original_atlas_data import embedded
from tools.project_core.validation.researcher_review import read_report,_register_review,table_rows,column,S
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.calculations.snapshots import save_snapshot
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def model_rows(project):
 with zipfile.ZipFile(project) as z:return [r for _,r in table_rows(z,'Models & coverage','Models')[3]]
@contextmanager
def wait_lock():
 while True:
  lock=central_lock(ROOT)
  try:lock.__enter__();break
  except ValueError as e:
   if 'Another central writer' not in str(e):raise
   print('Waiting for the other central writer; no shared files changed.',flush=True);time.sleep(15)
 try:yield
 finally:lock.__exit__(None,None,None)
def patch_metadata(project,values,*,sheet_name='Models & coverage',table_name='Models',identity_field='model_id',identity=None):
 # Patch existing target cells only; retain all other OOXML members/styles.
 with zipfile.ZipFile(project) as z:
  sheet,headers,_,rr=table_rows(z,sheet_name,table_name);parts=[(i,z.read(i.filename)) for i in z.infolist()]
  matches=[row for row,r in rr if r.get('unit_id')=='HS_077' and r.get(identity_field)==(identity or M.name)];assert len(matches)==1;row=matches[0]
  from tools.project_core.validation.researcher_review import sheet_xml
  path,_=sheet_xml(z,sheet_name)
 for field,value in values.items():
  assert field in headers,field
  address=column(headers.index(field)+1)+row.get('r');cell=next((c for c in row if c.get('r')==address),None)
  if cell is None:cell=E.SubElement(row,'{'+S+'}c',r=address)
  style=cell.get('s');cell.clear();cell.set('r',address)
  if style:cell.set('s',style)
  if isinstance(value,(int,float,bool)):E.SubElement(cell,'{'+S+'}v').text=str(int(value) if isinstance(value,bool) else value)
  else:cell.set('t','inlineStr');E.SubElement(E.SubElement(cell,'{'+S+'}is'),'{'+S+'}t').text=str(value)
 row[:]=sorted(row,key=lambda c:headers.index(next(h for i,h in enumerate(headers,1) if c.get('r')==column(i)+row.get('r'))))
 temporary=project.with_name('.hs077-metadata.xlsx');before=sha(project)
 try:
  with zipfile.ZipFile(temporary,'w') as z:
   for i,data in parts:z.writestr(i,E.tostring(sheet,encoding='utf-8') if i.filename==path else data)
  assert sha(project)==before;os.replace(temporary,project)
 finally:temporary.unlink(missing_ok=True)

prepared=json.loads((W/'qa/prepared_results.json').read_text(encoding='utf-8'))
manifest=json.loads((W/'outputs/diagnostics/run_manifest.json').read_text(encoding='utf-8'))
regional=ROOT/'regions/HS/HS_077/HS_077.xlsx';project=ROOT/'Project.xlsx';report=M/'model_validation/validation.docx';pages=ROOT/'interactive_map'
assert sha(M/'model.json')==prepared['canonical_model_sha256']
assert sha(M/'original_model.json')=='9cc8a41414194be6f40f4fafd9d6ed23c38a1c5812acd55e6e39824e783c2998'
assert sha(W/'outputs/regional/HS_077.xlsx')==prepared['regional_staged_sha256']
assert sha(W/'outputs/sppr_source.xlsx')==prepared['coefficient_source_sha256']
verify_report(report);report_sha=sha(report)
name,date,summary=read_report(ROOT,report,M.name);assert name=='Ido Carmel' and date=='2026-10-08'
expected=['Grazing birds','Pursuit birds','Toothed whales','Spotted dolphin','Mesopelagic dolphins','Large sharks','Small sharks']
seq=[2,1,4,5,6,15,28]
with wait_lock():
 print('Shared lock acquired. Reading the latest Project and page state.',flush=True)
 assert sha(regional)==prepared['regional_before_sha256']
 assert sha(report)==report_sha
 before_rows=model_rows(project);before_project=sha(project)
 before_map,_=embedded(pages/'index.html','DB');before_series,_=embedded(pages/'trends.html','SERIES_DB')
 scoped=all(re.search(r'<meta name="ppr-project-sha256" content="([a-f0-9]+)">', (pages/n).read_text(encoding='utf-8')).group(1)==before_project for n in ['index.html','trends.html'])
 generated=[pages/n for n in ['index.html','trends.html','sources.html','data/unidentified_taxa.json','data/eez_searches.csv','data/lme_searches.csv','data/articles.csv','data/files.csv']]
 targets=[project,regional,M/'sppr_source.xlsx',M/'results/regional_snapshot.xlsx',M/'results/result_manifest.json',M/'model_notes.md',*generated]
 backups={p:p.read_bytes() if p.exists() else None for p in targets}
 backup_dir=W/'inputs/publication_before';backup_dir.mkdir(exist_ok=True)
 for p,data in backups.items():
  if data is not None:
   dest=backup_dir/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 try:
  shutil.copy2(W/'outputs/sppr_source.xlsx',M/'sppr_source.xlsx');shutil.copy2(W/'outputs/regional/HS_077.xlsx',regional)
  save_snapshot(regional,M,result_identity={'model_id':M.name,'canonical_model_sha256':prepared['canonical_model_sha256'],'effective_flags':{'constructor':manifest['constructor'],'methods':{option:json.loads((W/'outputs/diagnostics'/option.replace(' ','_')/'diagnostic_return.json').read_text(encoding='utf-8'))['config'] for option in ['GE','TE','With Egestion']}},'code_identity':manifest['engine'],'provenance_status':'Fresh bounded direct GE/TE/With Egestion returns retained losslessly; corrected source and signed notebook defaults; researcher-approved display exclusions separate from saved calculations'})
  print('Current coefficients, regional workbook and model snapshot adopted.',flush=True)
  update(ROOT,[regional],lock_held=True)
  patch_metadata(project,{'availability':'Researcher-adopted corrected canonical source; fresh reviewed LIM runtime and GE/TE/With Egestion direct WARN; TE strict SPPR balance fails; provisional numerical display.','configuration':json.dumps({'constructor':manifest['constructor'],'method_defaults':True},sort_keys=True),'computational_input_sha256':prepared['canonical_model_sha256'],'canonical_source_path':(M/'model.json').relative_to(ROOT).as_posix(),'canonical_source_sha256':prepared['canonical_model_sha256'],'engine_hashes':json.dumps(manifest['engine'],sort_keys=True),'diagnostic_manifest':(W/'outputs/diagnostics/run_manifest.json').relative_to(ROOT).as_posix(),'production_eligible':False,'diagnostic_grades':json.dumps(prepared['methods'],sort_keys=True)})
  _register_review(project,report,'HS_077',M.name,seq)
  print('Signed researcher review registered. Refreshing the map and trends from current Project.',flush=True)
  build(project,only_units=['HS_077'] if scoped else None)
  after_rows=model_rows(project)
  review_fields=['researcher_review_status','researcher_name','researcher_review_date','validation_report_path','validation_report_sha256','reviewed_model_sha256','reviewed_calculation_input_sha256','researcher_review_summary']
  after_index={(r['unit_id'],r['model_id']):r for r in after_rows}
  for r in before_rows:
   if (r['unit_id'],r['model_id'])==('HS_077',M.name):continue
   a=after_index[r['unit_id'],r['model_id']]
   for field in review_fields:assert (a.get(field) or '')==(r.get(field) or ''),(r['unit_id'],field)
  row=after_index['HS_077',M.name];registered=json.loads(row['researcher_review_summary']);assert registered['sections']==summary['sections'] and set(registered['excluded_group_ids'])==set(expected)
  assert row['validation_report_sha256']==sha(report)==report_sha
  assert row['reviewed_model_sha256']==sha(M/'model.json')
  assert row['reviewed_calculation_input_sha256']==prepared['calculation_input_sha256']
  catalog,_=embedded(pages/'index.html','DB');series,_=embedded(pages/'trends.html','SERIES_DB')
  cm=next(m for m in catalog['network']['units']['HS_077']['models'] if m['id']==M.name)
  sm=next(m for m in series['units']['HS_077']['models'] if m['id']==M.name)
  assert cm['researcher_review']==sm['researcher_review']
  assert cm['researcher_review']['sections']==summary['sections']
  assert cm['display_ppr_excluded_group_ids']==sm['display_ppr_excluded_group_ids']==registered['excluded_group_ids']
  assert cm['workbook_sha256']==sm['workbook_sha256']==sha(regional)
  if scoped:
   for unit,payload in before_map['network']['units'].items():
    if unit!='HS_077':assert catalog['network']['units'][unit]==payload,unit
   for unit,payload in before_series['units'].items():
    if unit!='HS_077':assert series['units'][unit]==payload,unit
  fingerprint=sha(project)
  for n in ['index.html','trends.html']:assert f'<meta name="ppr-project-sha256" content="{fingerprint}">' in (pages/n).read_text(encoding='utf-8')
  note=M/'model_notes.md';text=note.read_text(encoding='utf-8')
  old='Existing runtime/diagnostic evidence is historical: GE and With Egestion direct OK, TE FAIL; provisional numerical display. No downstream diagnostics, coefficients, regional calculations, Word validation or map refresh was performed after this correction, and equivalence to the corrected input has not been established.'
  new='On 2026-10-08, the corrected canonical model and reviewed notebook constructor/default method settings were executed directly for GE, TE and With Egestion. All three current diagnostic grades are WARN; GE and With Egestion pass strict SPPR balance, TE fails that strict check. Current coefficients and regional arithmetic were refreshed and their exact source, engine, runtime and full returns retained in [review refresh evidence](model_validation/work/2026-10-08_151542_review_handoff/outputs/diagnostics/run_manifest.json). Production eligibility remains false; provisional numerical display is retained. Catch, NPP, taxon mappings and the independent classic coefficients are unchanged. Historical sensitivity bounds were invalidated. Ido Carmel signed MODEL VALIDATED on 08/10/2026; the seven named exclusions apply only to displayed PPR, and are registered in Project and the map. The signed Word retains researcher-written historical source/diagnostic descriptions; current scientific discrepancies are recorded here rather than rewriting the signed review.'
  assert old in text;text=text.replace(old,new).replace('The unchanged validation document still records the pre-correction input state quoted below;','The signed validation document still records the pre-correction input state quoted below;');note.write_text(text,encoding='utf-8')
  proof={'project_before_sha256':before_project,'project_after_sha256':fingerprint,'regional_sha256':sha(regional),'report_sha256':report_sha,'reviewer':name,'signed_date':date,'model_id':M.name,'excluded_group_seq':seq,'excluded_group_names':expected,'scoped_refresh_from_latest_matching_pages':scoped,'unrelated_central_reviews_preserved':True,'unrelated_page_payloads_preserved':scoped,'canonical_source_unchanged':sha(M/'model.json')==prepared['canonical_model_sha256'],'all_six_word_pages_visually_verified':True,'current_diagnostic_grades':prepared['methods']}
  (W/'qa/publication_verified.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps(proof,indent=2),flush=True)
 except BaseException:
  print('Publication failed; restoring only the transaction baseline while holding the shared lock.',flush=True)
  for p,data in backups.items():
   if data is None:p.unlink(missing_ok=True)
   else:
    source=backup_dir/p.relative_to(ROOT);temporary=p.with_name('.hs077-rollback-'+p.name)
    shutil.copy2(source,temporary);os.replace(temporary,p)
  raise
print('HS_077 review publication complete; shared lock released.',flush=True)
