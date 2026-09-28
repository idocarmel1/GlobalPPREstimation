from pathlib import Path
import json,sys,traceback,shutil,hashlib,warnings,pickle
import numpy as np
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
MD=ROOT/'regions/LME_024/models/Hernvann_2020_Celtic_Sea_1985'
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str),encoding='utf8')
source=json.loads((MD/'model.json').read_text(encoding='utf8'))
inp=json.loads((OUT/'extraction_input.json').read_text(encoding='utf8'))
groups=inp['groups'];D=np.zeros((54,54))
for pred,preys in inp['diet'].items():
 for prey,v in preys.items():
  if prey!='import' and v is not None:D[int(pred)-1,int(prey)-1]=float(v)
B=np.array([float(g['biomass']) for g in groups]);PB=np.array([float(g['pb']) if g.get('pb') else np.nan for g in groups]);QB=np.array([float(g['qb']) if g.get('qb') else 0 for g in groups]);EE=np.array([float(g['ee']) if g.get('ee') else np.nan for g in groups]);BA=np.array([float(g['ba_rate'])*float(g['biomass']) for g in groups]);Y=np.array([float(source['group'][i]['export']) for i in range(54)])
predation=(B*QB)@D
rows=[]
for i,g in enumerate(groups):
 ee=(predation[i]+Y[i]+BA[i])/(B[i]*PB[i]) if B[i]*PB[i]>0 else None
 pq=PB[i]/QB[i] if QB[i] and np.isfinite(PB[i]) else None
 rows.append({'seq':i+1,'name':g['name'],'predation':predation[i],'catch':Y[i],'BA_from_source_rate_times_B':BA[i],'printed_EE':g['ee'],'recomputed_EE':ee,'EE_residual':ee-EE[i] if ee is not None and np.isfinite(EE[i]) else None,'printed_PQ':g['pq'],'PB_over_QB':pq,'diet_sum':str(sum((Decimal(v) for v in inp['diet'].get(str(i+1),{}).values() if v is not None),Decimal(0))) if i<50 else None})
save('independent_source_balance.json',rows)
# Native unknown EE can be solved; no biomass is missing, and printed zero B remains zero.
derived=[]
for i,g in enumerate(groups):
 if g['ee'] is None and rows[i]['recomputed_EE'] is not None:derived.append({'group_seq':i+1,'field':'ee','derived':rows[i]['recomputed_EE'],'equation':'EE_i=(Y_i+BA_i+sum_j B_j*QB_j*DC_ji)/(B_i*PB_i)','source_value':None,'assumptions':'No unstated net migration; published rounded diet unchanged.'})
 if g['pb'] is None and g['pq'] is not None:
  derived.append({'group_seq':i+1,'field':'pb','derived':str(Decimal(g['pq'])*Decimal(g['qb'])),'equation':'PB=PQ*QB','source_value':None,'limitation':'B4 reported rounded multistanza PQ; does not reconstruct age-transfer terms.'})
save('computable_unknowns.json',derived)
comp=json.loads(json.dumps(source))
for d in derived:comp['group'][d['group_seq']-1][d['field']]=str(d['derived'])
save('computational_copy.json',comp)
path=OUT/'24_2402020_Celtic_Sea_Hernvann_(1985).json'
shutil.copy2(MD/'model.json',path)
results=[];loader={}
from ModelData import ModelData
from PPRCalculator import PPRCalculator
data=ModelData(str(path))
data.groups_data.to_csv(OUT/'loader_groups_before_defaults.csv',index=True)
data.DC.to_csv(OUT/'loader_diet.csv',index=True)
data.det_fate.to_csv(OUT/'loader_detritus_fate.csv',index=True)
loader['changes']=['Filename-only staging copy for ModelData parser; source model.json bytes unchanged.', 'ModelData converts -9999 sentinels to NaN parameters and zero diet/fate entries.', 'ModelData adds synthetic diet_import group (55) and import diet column.', 'ModelData hardcodes lme=13 internally; actual region remains LME_024, not inferred from this field.', 'ModelData forces detritus self-routing identity for 53 and 54; living routing remains all zero.', 'No pooling, invented routing, source parameter repair, LIM, broad method inventory or Monte Carlo.']
for label,fn in [('strict_source',lambda:PPRCalculator.from_modeldata(data,zero_catch=False,zero_biomass_accum=False,default_gs=False)),('standard_loader_defaults',lambda:PPRCalculator.from_modeldata(data,zero_catch=True,zero_biomass_accum=True,default_gs=True)),('documented_normalize_DC_staging',lambda:PPRCalculator.from_modeldata(data,zero_catch=True,zero_biomass_accum=True,default_gs=True,normalize_DC=True))]:
 try:
  with warnings.catch_warnings(record=True) as w:
   warnings.simplefilter('always');calc=fn()
  loader[label]={'status':'LOADED','warnings':[str(x.message) for x in w]}
 except Exception as exc:
  loader[label]={'status':'EXCEPTION','exception_type':type(exc).__name__,'exception':str(exc),'traceback':traceback.format_exc()}
  continue
 if label=='standard_loader_defaults':
  for te in ['GE','TE','With Egestion']:
   try:
    result=calc.diagnose_sppr(TE_option=te,short=False,flat=False)
    (OUT/f'diagnose_{te.replace(" ","_")}_raw.pkl').write_bytes(pickle.dumps(result))
    save(f'diagnose_{te.replace(" ","_")}_raw.json',result)
    results.append({'TE_option':te,'status':'RETURNED','raw_result':result})
   except Exception as exc:results.append({'TE_option':te,'status':'EXCEPTION','exception':str(exc),'traceback':traceback.format_exc()})
if not results:
 for te in ['GE','TE','With Egestion']:results.append({'TE_option':te,'call':f'PPRCalculator.diagnose_sppr(TE_option={te!r}, short=False, flat=False)','status':'NOT_RUN','raw_return':None,'reason':'Constructor admission failed before diagnose_sppr could run. See exact exceptions in loader_audit.json.','production_eligible':False})
save('loader_audit.json',loader);save('diagnostics_results.json',results)
print(json.dumps(loader,indent=2));print(json.dumps(results,indent=2))
