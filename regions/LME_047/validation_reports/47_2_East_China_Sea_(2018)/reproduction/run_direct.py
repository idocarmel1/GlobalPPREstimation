from pathlib import Path
import sys,json,hashlib,time,shutil,datetime
import numpy as np,pandas as pd,openpyxl
ROOT=Path.cwd();R=ROOT/'regions/LME_047';MID='47_2_East_China_Sea_(2018)';E=R/'validation_reports'/MID/'direct_diagnostics';E.mkdir(parents=True,exist_ok=True)
ENGINE=ROOT/'tools/scientific_code/PPREstimation';sys.path.insert(0,str(ENGINE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(x):
 if isinstance(x,pd.DataFrame):
  a=x.to_numpy();return {'type':'DataFrame','index':js(list(x.index)),'columns':js(list(x.columns)),'data':js(a.tolist()),'null_mask':pd.isna(x).values.tolist(),'nan_mask':[[bool(isinstance(v,(float,np.floating)) and np.isnan(v)) for v in row]for row in a],'positive_infinity_mask':[[bool(isinstance(v,(float,np.floating)) and np.isposinf(v)) for v in row]for row in a],'negative_infinity_mask':[[bool(isinstance(v,(float,np.floating)) and np.isneginf(v)) for v in row]for row in a]}
 if isinstance(x,pd.Series):return js(x.to_frame())
 if isinstance(x,dict):return {str(k):js(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [js(v)for v in x]
 if isinstance(x,np.ndarray):return js(x.tolist())
 if isinstance(x,np.generic):return js(x.item())
 if isinstance(x,float)and not np.isfinite(x):return None
 return x
def write(n,x):(E/n).write_text(json.dumps(js(x),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
p=R/'models'/MID/'model.json';assert sha(p)=='31b1f6c360ce1d454db528e050100e5521cbf663cdb9d3001f0f39724a14ed16'
settings=dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,weight_flow=1.,weight_guess=1.,normalize_DC=True,DC_tol=.001)
c=PPRCalculator.from_modeldata(ModelData(str(p)),**settings)
g=c.get_groups_df();write('loaded_groups.json',g)
w=openpyxl.load_workbook(R/'models'/MID/'sppr_source.xlsx',read_only=True,data_only=True);a=list(w['groups_df'].values);old=pd.DataFrame(a[1:],columns=a[0]).set_index('seq');w.close()
diff=[]
for seq in old.index:
 for col in old.columns:
  av=old.loc[seq,col];bv=g.loc[seq,col] if col in g else (g.loc[seq,'trophic_info'] if col=='group_type' else None)
  if col=='taxon_descr':continue
  if pd.isna(av)and pd.isna(bv):continue
  if isinstance(av,(float,int,np.number))and isinstance(bv,(float,int,np.number)):
   if np.isclose(av,bv,atol=1e-10,rtol=1e-11):continue
  elif av==bv:continue
  diff.append({'seq':int(seq),'field':col,'accepted':js(av),'loaded':js(bv)})
write('loaded_parity.json',{'against':'../../../models/'+MID+'/sppr_source.xlsx#groups_df','tolerance':{'absolute':1e-10,'relative':1e-11},'differences':diff,'passed':not diff})
assert not diff,diff
write('loaded_state.json',{k:v for k,v in c.__dict__.items()if isinstance(v,(pd.DataFrame,pd.Series,np.ndarray))})
reports={};sol={};tim={}
for opt in ['GE','TE','With Egestion']:
 t=time.time()
 try:
  rep,sppr,A,L=c.diagnose_sppr(TE_option=opt,short=False,flat=False,return_sppr=True,det_open_mode='none',det_theta=1.,det_external_sppr=0.,det_collapse_mode='never')
  reports[opt]=rep;sol[opt]={'SPPR':sppr,'A':A,'L':L}
 except Exception as ex:reports[opt]={'status':'NOT_RUN/exception','exception_type':type(ex).__name__,'exception':str(ex)}
 tim[opt]=time.time()-t;write('direct_reports.json',reports);write('direct_solutions.json',sol);print(opt,js(reports[opt]).get('status'),tim[opt],flush=True)
for n in ['PPRCalculator.py','ModelData.py','utils.py']:
 (E/'engine').mkdir(exist_ok=True);shutil.copy2(ENGINE/n,E/'engine'/n)
write('execution_evidence.json',{'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canonical_input':'../../../models/'+MID+'/model.json','canonical_sha256':sha(p),'constructor_settings':settings,'settings_basis':'Inherited create_PPRS_excel.load_model and HEALTH_DET_CONFIG; independently matched every accepted loaded groups_df field except empty taxonomy text.','diagnostic_settings':{'short':False,'flat':False,'return_sppr':True,'det_open_mode':'none','det_theta':1.,'det_external_sppr':0.,'det_collapse_mode':'never'},'python':sys.version,'engine_hashes':{n:sha(E/'engine'/n)for n in ['PPRCalculator.py','ModelData.py','utils.py']},'timings_seconds':tim,'scope':'Direct GE/TE/With Egestion only. No coefficient adoption, Monte Carlo or parameter change.'})
