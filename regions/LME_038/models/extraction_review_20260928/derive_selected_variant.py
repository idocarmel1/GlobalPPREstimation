"""Materialize only user-authorized diet normalization and solved BA; verify reload."""
from pathlib import Path
import json,hashlib,sys,shutil,tempfile,math,csv
import openpyxl
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_038';SOURCE='38_38001_Java_Sea_(mid1970s)';MID='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
src=REG/'models'/SOURCE;dest=REG/'models'/MID;ev=dest/'evidence';ev.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original_hash=sha(src/'model.json');raw=json.loads((src/'model.json').read_text(encoding='utf8'));derived=json.loads(json.dumps(raw))
w=openpyxl.load_workbook(src/'sppr_source.xlsx',read_only=True,data_only=True);rr=list(w['groups_df'].values);old={int(r[0]):dict(zip(rr[0],r)) for r in rr[1:]};changes=[]
for g in derived['group']:
 seq=int(g['group_seq']);d=(g.get('diet_descr') or {}).get('diet',[]);d=[d] if isinstance(d,dict) else d;total=math.fsum(float(item['proportion']) for item in d)+float(g.get('diet_imp',0))
 if g['pp']=='0' and abs(total-1)>1e-12:
  for item in d:
   before=item['proportion'];after=float(before)/total;item['proportion']=repr(after);changes.append({'seq':seq,'group':g['group_name'],'field':'diet','prey':item['prey_seq'],'source':before,'derived':item['proportion'],'factor':1/total,'basis':'User-authorized proportional normalization, not recovery of omitted prey'})
 before=g['biomass_accum'];g['biomass_accum']=repr(float(old[seq]['biomass_accum']));g['biomass_accum_rate']='-9999';changes.append({'seq':seq,'group':g['group_name'],'field':'biomass_accum','source':before,'derived':g['biomass_accum'],'basis':'Computational completion from exact saved loader state, not observed source BA'})
derived['source_audit']={'source_model_id':SOURCE,'source_model_sha256':original_hash,'source_status':'Printed source fails strict diet admission; source canonical preserved','variant_status':'User-selected computational variant, source-derived rather than recovered published model','user_rationale':'best available model','user_authorized_transformations':['Normalize deficient Macrozoobenthos diet0.660 to1','Persist loader-completed signed BA for all28 groups'],'BA_provenance':'Source BA remains unknown in source canonical JSON; this variant stores computationally completed BA from retained diagnostic groups_df','diet_provenance':'Divides existing Macrozoobenthos fractions by0.660, adds no prey','retained_engine_caveat':'TE WARN near-zero transfer efficiency at Marine mammals group27','source_archive':'regions/LME_038/papers/BUCHARY-1991/ubc_1999-0254.pdf.pdf'}
(dest/'model.json').write_text(json.dumps(derived,indent=2,ensure_ascii=False),encoding='utf8');(ev/'SOURCE_TO_DERIVED.json').write_text(json.dumps(changes,indent=2),encoding='utf8')
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'));import create_PPRS_excel as cpe
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/(MID+'.json');shutil.copy2(dest/'model.json',p);model,label=cpe.load_model(str(p));new=model.get_groups_df()
 new.to_csv(ev/'reloaded_groups.csv')
 fields=['biomass','pb','qb','p','q','ee','catch','M0','gs','egestion','respiration','biomass_accum','emigration','immigration','net_migration','predation','flow_to_det','detritus_import'];diff=[]
 for seq,row in old.items():
  for field in fields:
   a=row.get(field);b=new.loc[seq,field]
   if a is None:continue
   if not math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-9):diff.append({'seq':seq,'field':field,'saved_loaded':a,'reloaded':float(b)})
 audit={'source_sha256':original_hash,'derived_sha256':sha(dest/'model.json'),'reference_loaded_workbook':(src/'sppr_source.xlsx').relative_to(ROOT).as_posix(),'reference_sha256':sha(src/'sppr_source.xlsx'),'loader':'create_PPRS_excel.load_model; underdetermined=True;zero_biomass_accum=False;DC_tol=.001;normalize_DC=True','loaded_state_comparison_fields':fields,'comparison_tolerance':{'relative':1e-10,'absolute':1e-9},'differences':diff,'source_canonical_unchanged':sha(src/'model.json')==original_hash,'source_groups':28,'additional_Import_bookkeeping_row':1,'note':'Basal QB/EE and default absent migration are existing engine conventions; no extra source parameters modified. Absolute BA is explicitly computed, rate remains source-unknown sentinel.'}
 (ev/'DERIVED_RELOAD_VALIDATION.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
 assert not diff,diff
 assert sha(src/'model.json')==original_hash
print(json.dumps({'id':MID,'derived_sha256':sha(dest/'model.json'),'reload_differences':len(diff),'BA_values':28,'diet_normalization':1/.66}))
