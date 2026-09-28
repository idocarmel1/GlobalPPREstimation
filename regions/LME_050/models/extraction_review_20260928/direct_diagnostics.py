"""Bounded caller of the three requested direct diagnose_sppr configurations only."""
from pathlib import Path
import sys,json,traceback,shutil,hashlib,time,subprocess,math
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
REG=ROOT/'regions/LME_050';OPTIONS=['GE','TE','With Egestion']
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,float) and not math.isfinite(x):return {'nonfinite':str(x)}
 if hasattr(x,'tolist'):return clean(x.tolist())
 if hasattr(x,'item'):return clean(x.item())
 return x
if len(sys.argv)>1:
 mid,option=sys.argv[1:];dest=REG/'models'/mid;ev=dest/'evidence';ev.mkdir(exist_ok=True)
 sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
 from ModelData import ModelData
 from PPRCalculator import PPRCalculator
 p=ev/(mid+'.json');shutil.copy2(dest/'model.json',p)
 config={'TE_option':option,'short':False,'flat':False,'return_sppr':False,'thresholds':None,'det_collapse_mode':'never','det_open_mode':'none','det_theta':1.0,'det_external_sppr':0.0}
 start=time.monotonic();stage='ModelData';r=None;error=None
 try:
  md=ModelData(str(p))
  if option=='GE':
   md.groups_data.to_csv(ev/'modeldata_groups.csv');md.DC.to_csv(ev/'modeldata_diet.csv');md.det_fate.to_csv(ev/'modeldata_detritus_fate.csv')
  stage='PPRCalculator.from_modeldata'
  m=PPRCalculator.from_modeldata(md,underdetermined=True,zero_biomass_accum=False,DC_tol=0.001,normalize_DC=True)
  if option=='GE':
   m._groups_df.to_csv(ev/'loaded_groups.csv');m._DC.to_csv(ev/'loaded_diet.csv');m._det_fate.to_csv(ev/'loaded_detritus_fate.csv')
  import pandas as pd
  loaded={}
  for key,val in vars(m).items():
   if isinstance(val,pd.DataFrame):loaded[key]={'kind':'DataFrame','index':val.index.tolist(),'columns':val.columns.tolist(),'data':clean(val.values.tolist())}
   elif isinstance(val,pd.Series):loaded[key]={'kind':'Series','index':val.index.tolist(),'data':clean(val.tolist())}
   elif isinstance(val,(str,int,float,bool,dict,list,tuple,type(None))):
    try:json.dumps(clean(val));loaded[key]=clean(val)
    except TypeError:pass
  dump(ev/('exact_loaded_state_'+option.replace(' ','_')+'.json'),loaded)
  if option=='GE':dump(ev/'exact_loaded_state.json',loaded)
  stage='PPRCalculator.diagnose_sppr';r=m.diagnose_sppr(**config)
 except Exception as exc:error={'stage':stage,'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
 out={'model_id':mid,'TE_option':option,'configuration':config,'direct_diagnose_sppr_return':clean(r),'call_error':error,'elapsed_seconds':time.monotonic()-start}
 dump(ev/('diagnose_sppr_'+option.replace(' ','_')+'.json'),out)
 print(option,r['status'] if r is not None else error)
else:
 outcomes=[]
 for dest in sorted((REG/'models').glob('50_*')):
  ev=dest/'evidence';ev.mkdir(exist_ok=True);code=dest/'diagnostic_code';code.mkdir(exist_ok=True)
  for name in ['ModelData.py','PPRCalculator.py','utils.py','create_PPRS_excel.py']:shutil.copy2(ROOT/'tools/scientific_code/PPREstimation'/name,code/name)
  shutil.copy2(__file__,code/Path(__file__).name)
  dump(ev/'diagnostic_provenance.json',{'source_sha256':hashlib.sha256((dest/'model.json').read_bytes()).hexdigest(),'timeout_seconds_per_configuration':180,'loader':{'underdetermined':True,'zero_biomass_accum':False,'DC_tol':.001,'normalize_DC':True,'zero_catch':'default True','default_gs':'default True'},'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in code.glob('*.py')}})
  for option in OPTIONS:
   try:
    r=subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).resolve()),dest.name,option],capture_output=True,text=True,encoding='utf8',timeout=180)
    (ev/('diagnose_sppr_'+option.replace(' ','_')+'.log')).write_text(r.stdout+'\n'+r.stderr,encoding='utf8');print(dest.name,option,r.returncode,flush=True)
   except subprocess.TimeoutExpired as exc:
    dump(ev/('diagnose_sppr_'+option.replace(' ','_')+'.json'),{'model_id':dest.name,'TE_option':option,'direct_diagnose_sppr_return':None,'call_error':{'type':'TimeoutExpired','message':'180 second bound reached; no return'},'elapsed_seconds':180})
   outcomes.append(json.loads((ev/('diagnose_sppr_'+option.replace(' ','_')+'.json')).read_text(encoding='utf8')))
 dump(Path(__file__).parent/'DIAGNOSE_SPPR_RESULTS.json',outcomes)
