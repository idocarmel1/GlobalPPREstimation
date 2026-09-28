from pathlib import Path
import sys,json,math
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import result_hash
REG=ROOT/'regions/LME_038';b=read_book(REG/'LME_038.xlsx');o=validate_region(b,REG/'LME_038.xlsx');dest=REG/o['model_path'];ev=dest.parent/'evidence';assert o['calculation_result_sha256']==result_hash(b)
sourcechecks=[]
for mid in ['38_38001_Java_Sea_(mid1970s)','38_38002_North_Coast_Central_Java_(1979)']:
 m=json.loads((REG/'models'/mid/'evidence/source_manifest.json').read_text(encoding='utf8'));actual=sha(ROOT/m['file']);assert actual==m['sha256'];sourcechecks.append({'model_id':mid,'original_pdf_sha256_unchanged':actual})
assert sha(REG/'models/38_38001_Java_Sea_(mid1970s)/model.json')=='1740de76fad9cabab2791209cf96c73e8271e431ae4d6e5b858fa9fa6329b4ef'
assert sha(REG/'models/38_38002_North_Coast_Central_Java_(1979)/model.json')=='5b75b4031a2fe321efce78645d6b8a59e332c30fcbe007eb091c70e499318318'
catch={(r['taxon'],r['catch_basis']):r for r in records(b,'Catch','Catch')};taxa={t for t,basis in catch};maxgap=0
for t in taxa:
 for y in YEARS:
  c,l,d=[catch[t,basis][y] for basis in ['catch','landings','discards']]
  if all(finite(v) for v in [c,l,d]):maxgap=max(maxgap,abs(c-l-d));assert math.isclose(c,l+d,rel_tol=1e-12,abs_tol=1e-7)
annual=records(b,'PPR','Annual');a={(r['scope'],r['method'],r['catch_basis'],r['unidentified'],r['metric']):r for r in annual};maxppgap=0
for key,r in a.items():
 scope,method,basis,treatment,metric=key
 if basis!='catch' or metric!='ppr':continue
 for y in YEARS:
  c,l,d=[a[scope,method,bb,treatment,metric][y] for bb in ['catch','landings','discards']]
  if all(finite(v) for v in [c,l,d]):maxppgap=max(maxppgap,abs(c-l-d));assert math.isclose(c,l+d,rel_tol=1e-12,abs_tol=1e-6)
npp={r['method']:r for r in records(b,'NPP','NPP')};ratio_count=0;blank_count=0
for r in records(b,'PPR–NPP','Ratios'):
 if r['model_id']!=o['selected_model_id']:continue
 ar=a[r['scope'],r['method'],r['catch_basis'],r['unidentified'],'ppr']
 for y in YEARS:
  p=ar[y];n=npp[r['npp_method']][y];v=r[y]
  if finite(p) and finite(n) and n>0:assert math.isclose(v,100*p/9/n,rel_tol=1e-12,abs_tol=1e-12);ratio_count+=1
  else:assert v is None;blank_count+=1
out={'status':'PASS','selected_model_id':o['selected_model_id'],'source_PDF_hashes':sourcechecks,'source_canonical_JSON_unchanged':True,'selected_model_sha256':sha(dest),'regional_sha256':sha(REG/'LME_038.xlsx'),'fresh_input_and_result_hashes':True,'taxa':len(taxa),'catch_equals_landings_plus_discards_max_abs_gap_tonnes':maxgap,'annual_PPR_additivity_max_abs_gap_wet_tonnes':maxppgap,'PPR_NPP_nonblank_cells_checked_once_divide_by9':ratio_count,'unavailable_ratio_cells_verified_blank':blank_count,'supported_years':[1950,2019],'TE_WARN_retained':True}
(ev/'FINAL_VALIDATION.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
