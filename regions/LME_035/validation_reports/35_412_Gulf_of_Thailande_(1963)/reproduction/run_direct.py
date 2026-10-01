import sys,json,hashlib,time,shutil
from pathlib import Path
import numpy as np,pandas as pd
Q=Path(__file__).parent;ROOT=Q.parents[4];R=ROOT/'regions/LME_035';MID='35_412_Gulf_of_Thailande_(1963)';E=R/'validation_reports'/MID/'direct_diagnostics';E.mkdir(parents=True,exist_ok=True)
ENGINE=ROOT/'tools/scientific_code/PPREstimation';sys.path.insert(0,str(ENGINE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(x):
 if isinstance(x,pd.DataFrame):return {'index':list(x.index),'columns':list(x.columns),'data':x.replace([np.inf,-np.inf],np.nan).where(pd.notna(x),None).values.tolist()}
 if isinstance(x,pd.Series):return js(x.to_frame())
 if isinstance(x,dict):return {str(k):js(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [js(v)for v in x]
 if isinstance(x,np.ndarray):return js(x.tolist())
 if isinstance(x,np.generic):return js(x.item())
 if isinstance(x,float)and not np.isfinite(x):return None
 return x
def write(n,x):(E/n).write_text(json.dumps(js(x),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
inp=R/'models'/MID/'model.json';assert sha(inp)=='dc6b45d6a5f532a5ebd294b3365e43b8bd74b66ca0dea5a035793fcad8f836e9'
settings=dict(underdetermined=True,zero_biomass_accum=False,DC_tol=.001,normalize_DC=True)
calc=PPRCalculator.from_modeldata(ModelData(str(inp)),**settings)
write('loaded_groups.json',calc.get_groups_df())
state={k:js(v)for k,v in calc.__dict__.items()if isinstance(v,(pd.DataFrame,pd.Series,np.ndarray))}
write('loaded_state.json',state)
reports={};solutions={};timings={}
for option in ['GE','TE','With Egestion']:
 start=time.time()
 try:
  report,SPPR,A,L=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,det_open_mode='none',det_theta=1.,det_external_sppr=0.,det_collapse_mode='never')
  reports[option]=report;solutions[option]={'SPPR':SPPR,'A':A,'L':L}
 except Exception as e:reports[option]={'status':'NOT_RUN/exception','exception_type':type(e).__name__,'exception':str(e)}
 timings[option]=time.time()-start;write('direct_reports.json',reports);write('direct_solutions.json',solutions);print(option,js(reports[option]).get('status'),timings[option],flush=True)
enginedir=E/'engine';enginedir.mkdir(exist_ok=True)
for n in ['PPRCalculator.py','ModelData.py','utils.py']:shutil.copy2(ENGINE/n,enginedir/n)
write('execution_evidence.json',dict(date='2026-10-01',canonical_input='../../../models/'+MID+'/model.json',canonical_sha256=sha(inp),constructor_settings=settings,settings_basis='Inherited create_PPRS_excel.load_model constructor and HEALTH_DET_CONFIG; exact loaded group values must be compared to accepted workbook before use.',diagnostic_settings=dict(short=False,flat=False,return_sppr=True,det_open_mode='none',det_theta=1.,det_external_sppr=0.,det_collapse_mode='never'),engine_sha256={n:sha(enginedir/n)for n in ['PPRCalculator.py','ModelData.py','utils.py']},timings_seconds=timings,scope='direct GE/TE/With Egestion only; no Monte Carlo/global; no coefficient adoption or parameter repair'))
