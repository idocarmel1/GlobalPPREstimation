from pathlib import Path
import sys,json,hashlib,platform,warnings,math
import numpy as np,pandas as pd
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encode(x):
 if isinstance(x,pd.DataFrame):
  a=x.to_numpy();numeric=np.asarray(a,dtype=float) if all(pd.api.types.is_numeric_dtype(t) for t in x.dtypes) else None
  return {'type':'DataFrame','index':encode(x.index.tolist()),'columns':encode(x.columns.tolist()),'index_name':x.index.name,'columns_name':x.columns.name,'dtypes':[str(v) for v in x.dtypes],'values':encode(a.tolist()),'masks':None if numeric is None else {'nan':np.isnan(numeric).tolist(),'posinf':np.isposinf(numeric).tolist(),'neginf':np.isneginf(numeric).tolist()}}
 if isinstance(x,pd.Series):return {'type':'Series','index':encode(x.index.tolist()),'name':x.name,'dtype':str(x.dtype),'values':encode(x.tolist())}
 if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
 if isinstance(x,(list,tuple,np.ndarray)):return [encode(v) for v in x]
 if isinstance(x,(np.integer,)):return int(x)
 if isinstance(x,(np.bool_,)):return bool(x)
 if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else {'type':'float','nonfinite':'nan' if np.isnan(x) else '+inf' if x>0 else '-inf'}
 return x
def save(p,x):p.write_text(json.dumps(encode(x),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
model=ROOT/'regions/LME_032/models/32_1_Arabian_Sea_off_Karnataka_(2000)/model.json'
settings={'underdetermined':True,'zero_catch':True,'zero_biomass_accum':False,'default_gs':True,'weight_flow':1.,'weight_guess':1.,'normalize_DC':True,'DC_tol':.001}
md=ModelData(str(model));raw=md.groups_data.copy()
with warnings.catch_warnings(record=True) as ws:
 warnings.simplefilter('always');calc=PPRCalculator.from_modeldata(md,**settings)
loaded=calc._groups_df.copy();ledger=[]
for seq in raw.index:
 for field in set(raw.columns)&set(loaded.columns):
  a,b=raw.at[seq,field],loaded.at[seq,field]
  if pd.isna(a) and pd.isna(b):continue
  if a==b:continue
  ledger.append({'group_id':seq,'group_name':calc.seq2name.get(seq),'field':field,'before':a,'after':b})
save(R/'diagnostics/adopted_loaded_state.json',{'raw_groups':raw,'loaded_groups':loaded,'DC':calc._DC,'detritus_fate':calc._det_fate,'mutation_ledger':ledger,'warnings':[str(x.message) for x in ws]})
save(R/'diagnostics/adopted_provenance.json',{'model_path':'regions/LME_032/models/32_1_Arabian_Sea_off_Karnataka_(2000)/model.json','model_sha256':sha(model),'constructor':settings,'engine_hashes':{p.name:sha(p) for p in [ROOT/'tools/scientific_code/PPREstimation'/n for n in ['ModelData.py','PPRCalculator.py','utils.py']]},'python':sys.version,'platform':platform.platform(),'date':'2026-09-30','direct_settings':{'TE_option':['GE','TE','With Egestion'],'short':False,'flat':False,'return_sppr':True,'det_collapse_mode':'never','det_open_mode':'none','det_theta':1.,'det_external_sppr':0.,'fix_EE_0_cases':True}})
summary={}
for method in ['GE','TE','With Egestion']:
 with warnings.catch_warnings(record=True) as ws:
  warnings.simplefilter('always');report,sppr,A,L=calc.diagnose_sppr(TE_option=method,short=False,flat=False,return_sppr=True)
 negatives=[{'source_id':src,'source_name':calc.seq2name[src],'group_id':g,'group_name':calc.seq2name[g],'value':float(sppr.at[g,src])} for g in sppr.index for src in sppr.columns if np.isfinite(sppr.at[g,src]) and sppr.at[g,src]<0]
 save(R/f'diagnostics/adopted_{method.replace(" ","_")}.json',{'report':report,'SPPR':sppr,'A':A,'L':L,'names':calc.seq2name,'orientation':'rows recipient groups; columns basal sources','units':'wet-weight equivalent per unit group wet weight','negative_entries':negatives,'warnings':[str(x.message) for x in ws]})
 summary[method]={'status':report['status'],'negative_entries':len(negatives),'matrix_shape':sppr.shape,'nonfinite':int((~np.isfinite(sppr.to_numpy())).sum()),'divergence':report['divergence'],'model_input':report['model_input'],'balance':report['balance']}
save(R/'diagnostics/adopted_summary.json',summary)
print({m:{k:v for k,v in x.items() if k in ['status','negative_entries','matrix_shape','nonfinite']} for m,x in summary.items()})
