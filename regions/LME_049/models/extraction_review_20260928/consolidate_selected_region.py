"""Use current region updater while preserving exact unrelated records and metadata."""
from pathlib import Path
import sys,json,shutil,copy,zipfile,math
import xml.etree.ElementTree as ET
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
import update_project
path=ROOT/'Project.xlsx';initial=sha(path);before=read_book(path)
backup=OUT/f'Project_before_LME049_consolidation_{initial[:12]}.xlsx';shutil.copy2(path,backup);assert sha(backup)==initial
captured=[]
def capture(p,b):assert p==path;captured.append(copy.deepcopy(b))
update_project.write_book=capture
update_project.update(ROOT,[ROOT/'regions/LME_049/LME_049.xlsx'])
assert len(captured)==1;after=captured[0];restorations=[]
# The region updater recomputes selected flags globally. Restore unrelated semantic
# records from this fresh snapshot before its single physical write, preserving user notes.
for sheet,blocks in before.items():
 for table,(h,rr) in blocks.items():
  if 'unit_id' not in h:continue
  old=records(before,sheet,table);nh,nr=after[sheet][table];new=records(after,sheet,table)
  oldother=[r for r in old if r.get('unit_id')!='LME_049'];newother=[r for r in new if r.get('unit_id')!='LME_049']
  if oldother!=newother:restorations.append({'sheet':sheet,'table':table,'restored_unrelated_records':len(oldother)})
  # Preserve original header order/fields and append only legitimately new columns.
  finalh=list(h)+[k for k in nh if k not in h]
  local=[r for r in new if r.get('unit_id')=='LME_049']
  after[sheet][table]=(finalh,[[r.get(k) for k in finalh] for r in oldother+local])
assert sha(path)==initial,'Project changed concurrently; refuse stale write'
write_book(path,after)
readback=read_book(path)
def same(a,b):
 if finite(a) and finite(b):return math.isclose(a,b,rel_tol=2e-15,abs_tol=1e-12)
 return a==b
checks=[]
for sheet,blocks in before.items():
 for table,(h,rr) in blocks.items():
  if 'unit_id' not in h:continue
  old=[r for r in records(before,sheet,table) if r.get('unit_id')!='LME_049'];new=[r for r in records(readback,sheet,table) if r.get('unit_id')!='LME_049']
  assert len(old)==len(new),(sheet,table)
  for a,b in zip(old,new):assert all(same(v,b.get(k)) for k,v in a.items()),(sheet,table,a)
  checks.append({'sheet':sheet,'table':table,'unrelated_records_unchanged':len(old)})
# Verify paper/model source metadata unchanged except targeted selection and rationale.
metadata=[]
for sheet,table,key in [('Papers','Papers','article_id'),('Models & coverage','Models','model_id')]:
 old={r[key]:r for r in records(before,sheet,table)};new={r[key]:r for r in records(readback,sheet,table)}
 for identity,a in old.items():
  for field,value in a.items():
   if same(value,new[identity].get(field)):continue
   assert a.get('unit_id')=='LME_049' and field in ['selected','selection_rationale'],(identity,field,value,new[identity].get(field))
   metadata.append({'sheet':sheet,'key':identity,'field':field,'before':value,'after':new[identity].get(field)})
with zipfile.ZipFile(path) as z:
 tables=[n for n in z.namelist() if n.startswith('xl/tables/') and n.endswith('.xml')];assert len(tables)==13
 for n in tables:
  node=ET.fromstring(z.read(n));af=node.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}autoFilter');assert af is not None and af.get('ref')==node.get('ref')
region=next(r for r in records(readback,'Regions & status','Regions') if r['unit_id']=='LME_049');assert region['selected_model_id']=='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)' and region['production_eligible'] is False
assert region['atlas_region_rank']==12
audit={'status':'PASS','backup':backup.relative_to(ROOT).as_posix(),'before_sha256':initial,'after_sha256':sha(path),'regional_sha256':sha(ROOT/'regions/LME_049/LME_049.xlsx'),'region':region,'tables_and_filters':13,'unrelated_record_verification':checks,'restored_global_updater_side_effects':restorations,'paper_model_cell_changes':metadata,'source_and_derived_metadata':'All prior source/variant metadata unchanged except selected flags/rationale for LME049; ranks preserved','map':'NOT BUILT; parent coordinated'}
(OUT/'SELECTED_CONSOLIDATION_VERIFICATION.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf8');print(json.dumps({'status':'PASS','project_sha256':audit['after_sha256'],'regional_sha256':audit['regional_sha256'],'restorations':restorations,'model_selection_changes':metadata,'tables':13},indent=2))
