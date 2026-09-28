from pathlib import Path
import json,sys,subprocess,shutil,hashlib
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_038'
SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(SKILL))
from workbooks import read_book,write_book,sha
from database_json import EwEConverter
for mid in ['38_38001_Java_Sea_(mid1970s)','38_38002_North_Coast_Central_Java_(1979)']:
 dest=REG/'models'/mid;et=dest/'extracted_tables'
 for args in [['validate.py',str(et)],['massbalance_check.py',str(et)],['database_json.py','-d',str(et),'--update-report']]:
  r=subprocess.run([sys.executable,'-X','utf8',str(SKILL/args[0]),*args[1:]],capture_output=True,text=True,encoding='utf8');(dest/(args[0].replace('.py','')+'.log')).write_text(r.stdout+'\n'+r.stderr,encoding='utf8');print(mid,args[0],r.returncode)
 db=[p for p in et.glob('*.json') if p.name!='model.json'];assert len(db)==1,db
 raw=json.loads((dest/'extraction.json').read_text(encoding='utf8'));data=json.loads(db[0].read_text(encoding='utf8'));shutil.copy2(db[0],dest/'converter_normalized_intermediate.json');changes=[]
 for g in data['group']:
  diet=raw['diet'].get(g['group_seq'],{});items=(g.get('diet_descr') or {}).get('diet',[]);items=[items] if isinstance(items,dict) else items
  for item in items or []:
   val=diet.get(item['prey_seq'])
   if val is not None:
    if float(item['proportion'])!=float(val):changes.append([g['group_seq'],item['prey_seq'],item['proportion'],val])
    item['proportion']=val
  assert g['taxon_descr'] and len(g['taxon_descr'])>8
 cens=json.loads((dest/'evidence/censored_values.json').read_text())
 data['source_audit']={'strict_admission':'blocked: printed source defects; unselected candidate','source_diet_normalized':False,'censored_values':cens,'unknowns':'BA remains -9999; missing GS remains -9999. Habitat area1 and diet import0 are converter representation conventions, not separate source observations. Discards not quantified.','publication_year':1999 if mid.startswith('38_38001') else 2003}
 (dest/'model.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8');db[0].write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
 (dest/'evidence/converter_diet_restoration.json').write_text(json.dumps({'note':'Canonical JSON restores all source diet values after legacy converter normalization. Censored cells stay missing; bounds retained in source_audit and cell evidence.','cells':changes},indent=2),encoding='utf8')
 c=EwEConverter(str(dest/'source_faithful_conversion.log'));c.report_mass_balance(c.check_mass_balance(data['group'],0),db[0].stem,str(et/'MASS_BALANCE.md'));c.json_to_excel(str(db[0]))
 # Check complete membership and exact diet value round trip against canonical JSON.
 from openpyxl import load_workbook
 checks=[]
 for g,rg in zip(data['group'],raw['groups']):
  assert g['group_seq']==str(rg['n']) and g['group_name']==rg['name']
  for key in ['pb','qb','ee']:
   exp=rg.get(key);assert (str(g[key])=='-9999') if exp is None else float(g[key])==float(exp),(g['group_seq'],key,g[key],exp)
  if str(rg['n']) in raw['diet']:
   items=g['diet_descr']['diet'];items=items if isinstance(items,list) else [items]
   got={d['prey_seq']:float(d['proportion']) for d in items if float(d['proportion'])!=0};assert got=={k:float(v) for k,v in raw['diet'][str(rg['n'])].items()}
 checks.append({'groups':len(data['group']),'taxonomy_rows':len(data['group']),'basic_numeric_roundtrip':'pass','source_diet_roundtrip':'pass','strict_source_admission':'fail; source defects retained'})
 (dest/'evidence/roundtrip_validation.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
 if mid.startswith('38_38002'):continue
 b=read_book(REG/'LME_038.xlsx');b={s:{n:(h,[]) for n,(h,r) in tabs.items()} for s,tabs in b.items()}
 b['Overview']['Settings']=(['field','value'],[['unit_id','LME_038'],['region_name','Indonesian Sea'],['selected_model_id','38_38001_Java_Sea_(mid1970s)'],['model_path','model.json'],['selection_rationale','ISOLATED DIAGNOSTIC ONLY; user has not selected production model. Loader normalizes deficient Macrozoobenthos diet from0.660 to1; source admission fails.'],['production_eligible',False],['catch_basis','landings'],['taxon_detail_year',2019]])
 write_book(dest/'candidate_diagnostics.xlsx',b)
 snap=dest/'diagnostic_code';snap.mkdir(exist_ok=True)
 for p in [ROOT/'tools/run_region.py',ROOT/'tools/workbooks.py',ROOT/'tools/regional.py',ROOT/'tools/scientific_helpers/ppr_scopes.py']:
  shutil.copy2(p,snap/p.name)
 eng=ROOT/'tools/scientific_code/PPREstimation'
 for p in eng.rglob('*.py'):
  if '__pycache__' in p.parts:continue
  out=snap/'PPREstimation'/p.relative_to(eng);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
 (dest/'evidence/diagnostic_code_hashes.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in [dest/'model.json',*snap.rglob('*.py')]},indent=2),encoding='utf8')
