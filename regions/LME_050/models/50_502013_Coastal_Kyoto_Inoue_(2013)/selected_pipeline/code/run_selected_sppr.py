"""Three bounded direct configurations for the user-selected canonical 2013 model."""
from pathlib import Path
import sys,json,shutil,subprocess,hashlib
import pandas as pd
import numpy as np
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());MID='50_502013_Coastal_Kyoto_Inoue_(2013)';DEST=ROOT/'regions/LME_050/models'/MID;EV=DEST/'selected_pipeline';EV.mkdir(exist_ok=True)
OPTIONS={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if len(sys.argv)>1:
 opt=sys.argv[1];label=opt.replace(' ','_');p=EV/(MID+'.json');shutil.copy2(DEST/'model.json',p)
 sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
 from ModelData import ModelData
 from PPRCalculator import PPRCalculator
 m=PPRCalculator.from_modeldata(ModelData(str(p)),underdetermined=True,zero_biomass_accum=False,DC_tol=.001,normalize_DC=True)
 for name,value in [('loaded_groups',m._groups_df),('loaded_diet',m._DC),('loaded_detritus_fate',m._det_fate)]:
  value.to_csv(EV/(name+'.csv'));assert pd.read_csv(EV/(name+'.csv')).equals(pd.read_csv(DEST/'evidence'/(name+'.csv'))),name
 config=dict(TE_option=opt,short=False,flat=False,return_sppr=True,thresholds=None,det_collapse_mode='never',det_open_mode='none',det_theta=1.,det_external_sppr=0.)
 r,s,a,l=m.diagnose_sppr(**config)
 original=json.loads((DEST/'evidence'/f'diagnose_sppr_{label}.json').read_text(encoding='utf8'))['direct_diagnose_sppr_return']
 assert json.loads(json.dumps(r))==original
 assert np.isfinite(s.values).all() and (s.values>=0).all()
 dump(EV/f'diagnose_sppr_{label}.json',{'configuration':config,'direct_diagnose_sppr_return':r,'all_source_cells_finite_nonnegative':True,'original_direct_return_unchanged':True,'audited_loaded_state_unchanged':True})
 s.to_csv(EV/f'SPPR_{label}.csv');a.to_csv(EV/f'A_{label}.csv');l.to_csv(EV/f'L_{label}.csv')
 print(opt,r['status'])
else:
 for opt in OPTIONS:
  r=subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).resolve()),opt],capture_output=True,text=True,encoding='utf8',timeout=180)
  (EV/f'run_{opt.replace(" ","_")}.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf8');assert r.returncode==0,r.stderr;print(r.stdout.strip())
 code=EV/'code';code.mkdir(exist_ok=True)
 for n in ['PPRCalculator.py','ModelData.py','utils.py']:shutil.copy2(ROOT/'tools/scientific_code/PPREstimation'/n,code/n)
 shutil.copy2(__file__,code/Path(__file__).name)
 dump(EV/'PROVENANCE.json',{'selected_model':MID,'source_sha256':sha(DEST/'model.json'),'timeout_seconds_per_configuration':180,'options':list(OPTIONS),'loaded_state':'Exact equality with original audited groups/diet/detritus_fate; full original state retained in ../evidence/exact_loaded_state*.json','source_admission':'Unresolved year-specific source diets and missing inputs remain; load/health/selection are separate','code_hashes':{p.name:sha(p) for p in code.iterdir()}})
