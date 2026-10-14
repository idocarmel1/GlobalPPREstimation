"""Reproduce the direct SPPR checks for a Corrales derived-fate candidate."""
from pathlib import Path
import json,sys,hashlib,traceback,warnings,datetime
import numpy as np
import pandas as pd

def serialize(x):
 if isinstance(x,pd.DataFrame):
  a=x.to_numpy();return {'type':'DataFrame','index':[serialize(i) for i in x.index],'columns':[serialize(i) for i in x.columns],'data':[[serialize(v) for v in row] for row in a],'nan_mask':[[bool(isinstance(v,(float,np.floating)) and np.isnan(v)) for v in row] for row in a],'positive_infinity_mask':[[bool(isinstance(v,(float,np.floating)) and np.isposinf(v)) for v in row] for row in a],'negative_infinity_mask':[[bool(isinstance(v,(float,np.floating)) and np.isneginf(v)) for v in row] for row in a],'null_mask':[[v is None for v in row] for row in a]}
 if isinstance(x,pd.Series):return {'type':'Series','index':list(x.index),'name':x.name,'data':[serialize(v) for v in x]}
 if isinstance(x,np.ndarray):return {'type':'ndarray','shape':list(x.shape),'data':serialize(x.tolist())}
 if isinstance(x,dict):return {str(k):serialize(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [serialize(v) for v in x]
 if isinstance(x,(np.integer,)):return int(x)
 if isinstance(x,(np.bool_,)):return bool(x)
 if isinstance(x,(float,np.floating)):
  if np.isnan(x):return {'nonfinite':'NaN'}
  if np.isposinf(x):return {'nonfinite':'+Infinity'}
  if np.isneginf(x):return {'nonfinite':'-Infinity'}
  return float(x)
 if x is None or isinstance(x,(str,int,bool)):return x
 return {'type':type(x).__name__,'text':str(x)}

model=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[2]
root=next(p for p in [model,*model.parents] if (p/'Project.xlsx').exists())
engine=root/'tools/scientific_code/PPREstimation';sys.path.insert(0,str(engine))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
source=model/'model.json';out=model/'results/diagnostics';out.mkdir(parents=True,exist_ok=True)
data=json.loads(source.read_text(encoding='utf-8'));md=ModelData(str(source))
before=md.groups_data.copy();raw_dc=md.DC.copy();raw_fate=md.det_fate.copy()
# Restore the explicitly authorized canonical fate matrix to runtime rows that the
# legacy loader omits for nonfeeding producers. This changes no canonical value.
for group in data['group']:
 sid=int(group['group_seq'])
 for pool,value in group.get('detritus_fate_by_pool',{}).items():
  if value!='-9999':md.det_fate.loc[sid,int(pool)]=float(value)
settings=dict(underdetermined=False,zero_catch=True,zero_biomass_accum=True,default_gs=True,normalize_DC=True,DC_tol=.001,balance_BA_after_DC_normalization=False)
record={'schema_version':1,'model_id':model.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'constructor':'PPRCalculator.from_modeldata','constructor_settings':settings,'python':sys.version,'engine_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [engine/'ModelData.py',engine/'PPRCalculator.py',engine/'utils.py']},'source_gray_cells':'Preserved as -9999; zero conversion occurs only in ModelData.get_DC','fishery_returns':'Separate ledger retained; current PPR engine does not consume native fleet-discard returns','methods':{}}
def save(name,value): (out/name).write_text(json.dumps(serialize(value),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
save('loaded_before.json',{'groups':before,'diet':raw_dc,'fate_before_explicit_matrix_restore':raw_fate,'fate_used':md.det_fate})
try:
 with warnings.catch_warnings(record=True) as ww:
  warnings.simplefilter('always');calc=PPRCalculator.from_modeldata(md,**settings)
 record['constructor_outcome']='passed';record['constructor_warnings']=[str(w.message) for w in ww]
 save('runtime_state.json',{'groups':calc._groups_df,'diet':calc._DC,'fate':calc._det_fate,'normalization':getattr(calc,'diet_normalization_rows',None),'normalization_balance_ledger':getattr(calc,'diet_normalization_balance_ledger',None)})
 balanced,production,consumption=calc.is_model_balanced()
 budget=pd.DataFrame({'group_name':calc._groups_df.group_name,'trophic_info':calc._groups_df.trophic_info,'production':calc.p,'catch':calc.catch,'predation':calc.predation,'biomass_accumulation':calc.growth,'net_migration':calc.net_migration,'other_mortality':calc.M0,'production_sinks':production,'production_residual':production-calc.p,'consumption':calc.q,'egestion':calc.egestion,'respiration':calc.respiration,'consumption_recomputed':consumption,'consumption_residual':consumption-calc.q})
 budget['production_relative_residual']=budget.production_residual/np.maximum(abs(budget.production),1e-12)
 budget['consumption_relative_residual']=budget.consumption_residual/np.maximum(abs(budget.consumption),1e-12)
 budget.index.name='group_seq';budget.to_csv(out/'mass_balance_by_group.csv')
 record['strict_mass_balance']=bool(balanced)
 negative=[]
 for option in ['GE','TE','With Egestion']:
  key=option.replace(' ','_');print(model.name,option,'starting',flush=True)
  try:
   diag,sppr,A,L=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
   save(f'{key}_full_return.json',{'diagnostics':diag,'SPPR':sppr,'A':A,'L':L,'seq2name':calc.seq2name,'matrix_orientation':'rows recipient group; columns basal source; engine original axes retained'})
   for ri in sppr.index:
    for ci in sppr.columns:
     val=sppr.loc[ri,ci]
     if pd.notna(val) and float(val)<-1e-12:negative.append({'method':option,'matrix':'SPPR','source_id':ci,'source_name':calc.seq2name.get(ci,str(ci)),'recipient_id':ri,'recipient_name':calc.seq2name.get(ri,str(ri)),'value':float(val),'tolerance':1e-12})
   record['methods'][option]={'status':'executed','diagnostics':diag,'return_file':f'{key}_full_return.json'}
   print(model.name,option,'completed',diag.get('grade',diag.get('overall',diag.get('status','returned'))),flush=True)
  except Exception as e:record['methods'][option]={'status':'exception','exception':repr(e),'traceback':traceback.format_exc()};print(option,repr(e),flush=True)
 save('negative_entries.json',negative)
except Exception as e:
 record['constructor_outcome']='blocked';record['exception']=repr(e);record['traceback']=traceback.format_exc()
 for option in ['GE','TE','With Egestion']:record['methods'][option]={'status':'NOT_RUN','reason':repr(e)}
save('diagnostic_manifest.json',record)
