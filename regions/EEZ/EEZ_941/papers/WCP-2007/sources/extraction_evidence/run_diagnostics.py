"""Bounded single-model diagnostics; no exporter, Monte Carlo, or regional writes."""
from pathlib import Path
import json, sys, shutil, hashlib, traceback, contextlib, importlib.metadata
from datetime import datetime, timezone
import numpy as np
import pandas as pd
SCRIPT=Path(__file__).resolve()
ROOT=next(p for p in SCRIPT.parents if (p/'Project.xlsx').is_file())
HERE=ROOT/'regions/EEZ_941/papers/WCP-2007/extraction_evidence'
ENGINE=SCRIPT.parent if SCRIPT.parent.name=='executed_code' else ROOT/'tools/scientific_code/PPREstimation'
MODEL_ID='941_200701_WCPO_Warm_Pool_Final_(mixed_periods)'
BASE=ROOT/'regions/EEZ_941/models'/MODEL_ID
OUT=BASE/'diagnostics'; OUT.mkdir(exist_ok=True)
CODE=OUT/'executed_code'; CODE.mkdir(exist_ok=True)
for name in ['ModelData.py','PPRCalculator.py','utils.py']:
    if (ENGINE/name).resolve()!=(CODE/name).resolve(): shutil.copyfile(ENGINE/name,CODE/name)
if SCRIPT!=(CODE/'run_diagnostics.py').resolve(): shutil.copyfile(SCRIPT,CODE/'run_diagnostics.py')
sys.path.insert(0,str(CODE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator

def safe(v):
    if isinstance(v,dict): return {str(k):safe(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)): return [safe(x) for x in v]
    if isinstance(v,np.ndarray): return safe(v.tolist())
    if isinstance(v,np.generic): return safe(v.item())
    if isinstance(v,float) and not np.isfinite(v): return None
    return v
def write(name,v): (OUT/name).write_text(json.dumps(safe(v),indent=2,allow_nan=False),encoding='utf-8')

settings=dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,weight_flow=1.0,weight_guess=1.0,DC_tol=0.001,normalize_DC=True)
source=BASE/(MODEL_ID+'.json')
shutil.copyfile(source,OUT/'canonical_run_input.json')
provenance={'model_id':MODEL_ID,'canonical_model_sha256':hashlib.sha256(source.read_bytes()).hexdigest(), 'source_pdf_sha256':hashlib.sha256((HERE.parent/'download-0adcf55e.pdf').read_bytes()).hexdigest(), 'utc':datetime.now(timezone.utc).isoformat(),'loader_settings':settings,'diagnostic_settings':{'short':False,'flat':False,'TE_options':['GE','TE','With Egestion'],'return_sppr':False,'sppr_kwargs':{}},'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CODE.glob('*.py')},'python':sys.version,'packages':{p:importlib.metadata.version(p) for p in ['numpy','pandas','sympy','scipy','igraph']}}
write('RUN_PROVENANCE.json',provenance)
with (OUT/'execution.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    try:
        data=ModelData(str(source))
        before=data.groups_data.copy(deep=True)
        data.DC.to_csv(OUT/'canonical_loaded_diet.csv')
        before.to_csv(OUT/'modeldata_groups_before_defaults.csv')
        try:
            PPRCalculator.from_modeldata(ModelData(str(source)),**{**settings,'normalize_DC':False})
            strict={'status':'loaded'}
        except Exception as e:
            strict={'status':'unavailable','exception':type(e).__name__+': '+str(e)}
        write('STRICT_SOURCE_LOAD.json',strict)
        model=PPRCalculator.from_modeldata(data,**settings)
        after=model.get_groups_df()
        after.to_csv(OUT/'computational_groups.csv')
        model._DC.to_csv(OUT/'computational_diet.csv')
        model._det_fate.to_csv(OUT/'computational_detritus_fate.csv')
        changes=[]
        for seq in before.index:
            for field in before.columns:
                a,b=before.loc[seq,field],after.loc[seq,field]
                if pd.isna(a) and pd.isna(b): continue
                if str(a)!=str(b):
                    changes.append({'seq':int(seq),'group':model.seq2name[seq],'field':field,'before':None if pd.isna(a) else a,'after':None if pd.isna(b) else b})
        write('LOADER_TRANSFORMATIONS.json',changes)
        summaries={}
        for option in ['GE','TE','With Egestion']:
            print('CALL diagnose_sppr',option,flush=True)
            try:
                result=model.diagnose_sppr(TE_option=option,short=False,flat=False)
                write('diagnose_'+option.replace(' ','_')+'.json',result)
                summaries[option]={'call_status':'returned','diagnostic_status':result['status']}
            except Exception as e:
                result={'call_status':'exception','exception_type':type(e).__name__,'message':str(e)}
                write('diagnose_'+option.replace(' ','_')+'_EXCEPTION.json',result)
                summaries[option]=result
                traceback.print_exc()
        write('CALL_OUTCOMES.json',summaries)
    except Exception as e:
        write('LOAD_EXCEPTION.json',{'exception_type':type(e).__name__,'message':str(e)})
        traceback.print_exc()
        raise
print(json.dumps(summaries,indent=2))
