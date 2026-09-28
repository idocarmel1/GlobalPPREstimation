"""Preserve Project.xlsx package, modifying only authorized metadata cells and rows."""
from pathlib import Path
import sys,json,hashlib,zipfile,copy,posixpath,os,tempfile,shutil
import xml.etree.ElementTree as ET
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import records,clean,sha
from openpyxl.utils import get_column_letter,column_index_from_string,range_boundaries
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
ET.register_namespace('',NS);ET.register_namespace('r',R)
def tag(n):return '{'+NS+'}'+n
def val(c):
 t=c.get('t');v=c.find(tag('v'))
 if t=='inlineStr':return ''.join(c.itertext())
 if v is None:return None
 if t=='b':return v.text=='1'
 if t in ['str','e']:return v.text
 if t=='s':return SHARED[int(v.text)]
 f=float(v.text);return int(f) if f.is_integer() else f
def grid(root):return {c.get('r'):val(c) for c in root.iter(tag('c'))}
def parse(root):
 rows=[]
 for row in root.find(tag('sheetData')):
  entries={column_index_from_string(''.join(filter(str.isalpha,c.get('r')))):val(c) for c in row}
  rows.append([entries.get(i) for i in range(1,max(entries,default=0)+1)])
 assert rows[0][0]=='@table';h=rows[1];return rows[0][1],h,[(r+[None]*len(h))[:len(h)] for r in rows[2:] if any(x is not None for x in r)]
def put(row,col,value,style=None):
 ref=f'{get_column_letter(col)}{row.get("r")}';c=next((c for c in row if c.get('r')==ref),None)
 if c is None:
  c=ET.Element(tag('c'),{'r':ref});
  if style is not None:c.set('s',style)
  row.append(c);row[:]=sorted(row,key=lambda x:column_index_from_string(''.join(filter(str.isalpha,x.get('r')))))
 for child in list(c):c.remove(child)
 c.attrib.pop('t',None);value=clean(value)
 if value is None:return c
 if isinstance(value,str):c.set('t','inlineStr');is_=ET.SubElement(c,tag('is'));t=ET.SubElement(is_,tag('t'));t.text=value
 elif isinstance(value,bool):c.set('t','b');ET.SubElement(c,tag('v')).text=str(int(value))
 else:ET.SubElement(c,tag('v')).text=str(value)
 return c

proposal=json.loads((OUT/'central_metadata_proposal.json').read_text(encoding='utf8'));path=ROOT/'Project.xlsx'
# Read current package immediately before staging the authorized mutation.
original_hash=sha(path)
with zipfile.ZipFile(path) as z:infos=z.infolist();raw={i.filename:z.read(i) for i in infos}
SHARED=[''.join(node.itertext()) for node in ET.fromstring(raw['xl/sharedStrings.xml'])] if 'xl/sharedStrings.xml' in raw else []
assert sha(path)==original_hash
wb=ET.fromstring(raw['xl/workbook.xml']);rels=ET.fromstring(raw['xl/_rels/workbook.xml.rels']);targets={r.get('Id'):r.get('Target') for r in rels}
paths={s.get('name'):posixpath.normpath('xl/'+targets[s.get('{'+R+'}id')].lstrip('/')) if not targets[s.get('{'+R+'}id')].startswith('/') else targets[s.get('{'+R+'}id')].lstrip('/') for s in wb.find(tag('sheets'))}
paper_path=paths['Papers'];model_path=paths['Models & coverage'];paper=ET.fromstring(raw[paper_path]);model=ET.fromstring(raw[model_path]);region=ET.fromstring(raw[paths['Regions & status']])
pn,ph,pr=parse(paper);mn,mh,mr=parse(model);rn,rh,rr=parse(region)
book={'Papers':{pn:(ph,pr)},'Models & coverage':{mn:(mh,mr)},'Regions & status':{rn:(rh,rr)}}
existing_models=records(book,'Models & coverage','Models');existing_keys=[(r['unit_id'],r['model_id']) for r in existing_models];assert len(existing_keys)==len(set(existing_keys))
region_rows=[r for r in records(book,'Regions & status','Regions') if r['unit_id']=='LME_038'];assert len(region_rows)==1
rank=region_rows[0]['atlas_region_rank'];assert rank==13
assert all(r['atlas_region_rank']==rank for r in records(book,'Papers','Papers') if r['unit_id']=='LME_038')
backup=OUT/f'Project_before_LME038_registration_{original_hash[:12]}.xlsx';shutil.copy2(path,backup);assert sha(backup)==original_hash
allowed=set();paper_changes=[]
regional_hash=sha(ROOT/'regions/LME_038/LME_038.xlsx')
assert all((ROOT/item['model_path']).is_file() for item in proposal['model_rows_to_register'])
paper_rows=paper.find(tag('sheetData'));by_id={val(next(c for c in row if c.get('r')==f'A{row.get("r")}')):row for row in paper_rows if int(row.get('r'))>=3 and any(c.get('r')==f'A{row.get("r")}' for c in row)}
for update in proposal['paper_updates']:
 row=by_id[update['article_id']];assert val(next(c for c in row if c.get('r')==f'B{row.get("r")}'))=='LME_038'
 for field,value in update['changes'].items():
  col=ph.index(field)+1;ref=f'{get_column_letter(col)}{row.get("r")}';old=grid(paper).get(ref)
  if old==value:continue
  # Preserve earlier textual evidence, labeling the new assessment separately.
  if field in {'notes','recommendation','correction_notes','coverage_note','loadability_evidence','documentation_evidence','quality_rationale','retrieval_audit','legacy_authors','legacy_title'} and isinstance(old,str) and old and isinstance(value,str):value=old+'\n\n[2026-09-28 extraction assessment] '+value
  assert not isinstance(value,str) or len(value)<=32767
  put(row,col,value);allowed.add((paper_path,ref));paper_changes.append({'article_id':update['article_id'],'field':field,'cell':ref,'before':old,'after':value})
sd=model.find(tag('sheetData'));last_data=max(int(r.get('r')) for r in sd if any(c.get('r')==f'A{r.get("r")}' and val(c) is not None for c in r))
template=next(r for r in sd if int(r.get('r'))==last_data);styles={column_index_from_string(''.join(filter(str.isalpha,c.get('r')))):c.get('s') for c in template}
model_added=[]
for item in proposal['model_rows_to_register']:
 assert item['unit_id']=='LME_038' and item['selected'] is False
 assert (item['unit_id'],item['model_id']) not in existing_keys,('Already registered',item['model_id'])
 assert Path(item['model_path']).parent.name==item['model_id'] and (ROOT/item['model_path']).is_file()
 item['atlas_region_rank']=rank;last_data+=1;row=ET.Element(tag('row'),{'r':str(last_data)})
 for col,field in enumerate(mh,1):put(row,col,item.get(field),styles.get(col));allowed.add((model_path,f'{get_column_letter(col)}{last_data}'))
 sd.append(row);model_added.append(item)
sd[:]=sorted(sd,key=lambda r:int(r.get('r')))
dim=model.find(tag('dimension'))
if dim is not None:dim.set('ref',f'A1:{get_column_letter(len(mh))}{last_data}')
table_parts=[p for p in raw if p.startswith('xl/tables/') and p.endswith('.xml')];assert len(table_parts)==13
model_rel_path=posixpath.join(posixpath.dirname(model_path),'_rels',posixpath.basename(model_path)+'.rels');sheet_rels={r.get('Id'):r.get('Target') for r in ET.fromstring(raw[model_rel_path])}
table_nodes=list(model.find(tag('tableParts')));assert len(table_nodes)==1
targ=sheet_rels[table_nodes[0].get('{'+R+'}id')];table_path=targ.lstrip('/') if targ.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(model_path),targ));table=ET.fromstring(raw[table_path]);old_table_ref=table.get('ref');_,first,_,_=range_boundaries(old_table_ref);newref=f'A{first}:{get_column_letter(len(mh))}{last_data}';table.set('ref',newref);table.find(tag('autoFilter')).set('ref',newref)
changed={paper_path:ET.tostring(paper,encoding='utf-8'),model_path:ET.tostring(model,encoding='utf-8'),table_path:ET.tostring(table,encoding='utf-8')}
# Cell-level audit of all touched sheets; untouched ZIP parts must remain identical.
assert sha(ROOT/'regions/LME_038/LME_038.xlsx')==regional_hash
# All existing selected flags, ranks, scores and LME022 cells are outside the allowlist.
for field in ['selected','region_rank','atlas_region_rank','legacy_documentation_score_60','legacy_applicability_score_40','model_loadability_score_55','documentation_score_20','spatial_fit_score_15','recency_validation_score_10','quality_score_cap','quality_score_100']:
 assert all(change['field']!=field for change in paper_changes)

diff=[]
for part in [paper_path,model_path]:
 before=grid(ET.fromstring(raw[part]));after=grid(ET.fromstring(changed[part]))
 for ref in set(before)|set(after):
  if before.get(ref)!=after.get(ref):assert (part,ref) in allowed,(part,ref);diff.append({'sheet_part':part,'cell':ref,'before':before.get(ref),'after':after.get(ref)})
fd,tmp=tempfile.mkstemp(suffix='.xlsx',dir=OUT);os.close(fd)
try:
 with zipfile.ZipFile(tmp,'w') as z:
  for i in infos:z.writestr(i,changed.get(i.filename,raw[i.filename]))
 with zipfile.ZipFile(tmp) as z:
  assert set(z.namelist())==set(raw)
  for name,value in raw.items():
   if name not in changed:assert z.read(name)==value,name
  checked=[]
  for p in table_parts:
   t=ET.fromstring(z.read(p));assert t.find(tag('autoFilter')).get('ref')==t.get('ref');checked.append({'part':p,'name':t.get('name'),'ref':t.get('ref'),'filter_ref':t.find(tag('autoFilter')).get('ref')})
 assert sha(path)==original_hash,'Project.xlsx changed during staging; refusing overwrite'
 try:
  os.replace(tmp,path);applied=True;ready=None
 except PermissionError:
  ready=OUT/'Project_LME038_registration_ready.xlsx';os.replace(tmp,ready);applied=False
finally:
 if os.path.exists(tmp):os.unlink(tmp)
audit={'status':'APPLIED' if applied else 'READY_NOT_APPLIED_EXCEL_FILE_LOCK','before_sha256':original_hash,'after_sha256':sha(path),'backup':str(backup.relative_to(ROOT)),'staged_workbook':str(ready.relative_to(ROOT)) if ready else None,'staged_sha256':sha(ready) if ready else None,'paper_changes':paper_changes,'model_rows_added' if applied else 'model_rows_proposed':model_added,'cells_changed' if applied else 'cells_proposed':diff,'modified_package_parts':list(changed),'other_package_parts_byte_identical':len(raw)-len(changed),'tables_verified':checked,'rank_policy':'No ranking inputs changed; new rows reuse verified existing LME038 atlas rank13. Existing ranks/scores unchanged.','regional_workbook_mutated':False,'production_selection_or_numerical_parts_mutated':False}
(OUT/'CENTRAL_REGISTRATION_VERIFICATION.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
proposal['status']=audit['status']+'; see CENTRAL_REGISTRATION_VERIFICATION.json';(OUT/'central_metadata_proposal.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'status':audit['status'],'paper_fields':len(paper_changes),'new_model_rows':len(model_added),'changed_cells':len(diff),'modified_parts':list(changed),'all_tables_and_filters':len(checked),'backup':str(backup),'ready_workbook':str(ready)}))
