"""Run only requested full direct diagnose_sppr configurations on audited staging."""
from pathlib import Path
import sys,json,hashlib,copy,warnings,time,traceback
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
MODEL=ROOT/'regions/LME_003/models/CAL-2016_California_Current_2000-2014'
TABLES=MODEL/'extracted_tables';OUT=MODEL/'diagnostics';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from PPRCalculator import PPRCalculator
from ModelData import ModelData
def encode(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if hasattr(x,'to_dict'):return x.to_dict()
 raise TypeError(str(type(x)))
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,default=encode),encoding='utf-8')
if len(sys.argv)==1:
 source=next(TABLES.glob('3_California*.json'))
 canonical=json.loads(source.read_text())
 # Explicit paper statement: no migration (PDF p2 printed88). Preserve other missing source values.
 for g in canonical['group']:
  g['immigration']='0';g['emigration']='0';g['emigration_rate']='0'
 canonical['source_metadata']={'model_id':MODEL.name,'paper_id':'CAL-2016','period':'2000-2014','area_km2':302000,'source_unknown_B_count':26,'source_unknown_EE_count':67,'gs':'not reported','detritus_fate_basis':'Author R pools unused living production; egestion not parameterized','catch':'total removals including discards; no landings/discards split','model_selected':False}
 dump(MODEL/'model.json',canonical)
 staged=copy.deepcopy(canonical)
 solved=json.loads((TABLES/'author_equation_solution.json').read_text())['groups']
 changes=[]
 for g,s in zip(staged['group'],solved):
  for key,sk in [('biomass','biomass'),('ee','ee')]:
   if g[key]=='-9999':
    changes.append({'seq':g['group_seq'],'group_name':g['group_name'],'field':key,'source':g[key],'derived':s[sk],'basis':'author coupled Ecopath equations; not observed source input'})
    g[key]=str(s[sk])
    if key=='biomass':g['biomass_habitat_area']=g[key]
 dump(OUT/'author_solved_diagnostic_input.json',staged)
 dump(OUT/'staging_transformations.json',{'canonical_sha256':hashlib.sha256((MODEL/'model.json').read_bytes()).hexdigest(),'source_to_staging':changes,'runtime_settings':{'underdetermined':False,'zero_catch':False,'zero_biomass_accum':False,'default_gs':True,'normalize_DC':False},'documented_loader_transforms':['GS=0.2 for 91 consumer groups: source unknown preserved in canonical; no named-small-zooplankton whitelist match','Adds modeled egestion to source-code-supported single-pool unused-production routing; this extends author detritus accounting','Detritus EE overwritten to 1 by loader; q and p equal completed inflow 3090.057754953629, not source detritus EE=0.2568634606282932','Synthetic diet_import group appended; its synthetic missing biomass defaults to 1, not a biological-group estimate','Habitat area 1 conversion convention: author biomass already model-area density','No missing biological B is passed to loader; source unknowns solved independently','No diet normalization; printed rounding retained','Loader filename adapter uses numeric token 2016 solely for parsing, not an EcoBase accession; in-memory lme corrected from loader hardcoded13 to3','Detritus self-fate identity inserted by loader; absent source self-fate remains blank in import files','Missing detritus import filled0 by loader; canonical -9999 unchanged'],'strict_source_admission':'qualified: missing GS and no catch split; source equations complete for living production, source detritus ignores egestion','production_eligible':False})
 print('staged',len(changes),'derived values')
else:
 option=sys.argv[1];key=option.lower().replace(' ','_');start=time.time()
 try:
  with warnings.catch_warnings(record=True) as caught:
   warnings.simplefilter('always')
   adapter=OUT/'3_2016_Author_solved_California_Current_(2000-2014).json'
   adapter.write_text(json.dumps(json.loads((OUT/'author_solved_diagnostic_input.json').read_text(encoding='utf-8')),indent=2,ensure_ascii=True),encoding='ascii')
   md=ModelData(str(adapter.resolve()))
   md.lme=3 # loader otherwise hardcodes 13; metadata correction only
   m=PPRCalculator.from_modeldata(md,underdetermined=False,zero_catch=False,zero_biomass_accum=False,default_gs=True,normalize_DC=False)
   m._groups_df.to_csv(OUT/'loaded_groups.csv',encoding='utf-8')
   report=m.diagnose_sppr(TE_option=option,short=False,flat=False)
  dump(OUT/f'{key}_direct_return.json',report)
  dump(OUT/f'{key}_execution.json',{'status':'completed','seconds':time.time()-start,'call':f'PPRCalculator.diagnose_sppr(TE_option={option!r},short=False,flat=False)','warnings':[str(w.message) for w in caught]})
  print(option,'completed',time.time()-start,report.get('status'),list(report))
 except Exception as e:
  dump(OUT/f'{key}_execution.json',{'status':'failed','seconds':time.time()-start,'error':str(e),'traceback':traceback.format_exc()})
  print(option,'FAILED',str(e));raise
