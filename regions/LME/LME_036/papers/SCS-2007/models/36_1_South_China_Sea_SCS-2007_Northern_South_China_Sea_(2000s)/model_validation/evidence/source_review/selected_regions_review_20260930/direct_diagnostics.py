"""Bounded direct-only diagnostics; never edits accepted model or workbook inputs."""
import json, pathlib, sys, hashlib, warnings, traceback, shutil
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / 'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator

MID = '36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)'
REGION = ROOT / 'regions/LME_036'
MODEL = REGION / 'models' / MID / 'model.json'
OUT = HERE / 'direct_diagnostics'
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def clean(v):
    if isinstance(v, dict): return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v, (list, tuple)): return [clean(x) for x in v]
    if isinstance(v, np.ndarray): return clean(v.tolist())
    if isinstance(v, np.generic): return clean(v.item())
    if isinstance(v, float) and not np.isfinite(v): return None
    return v

def save(name, data):
    (OUT/name).write_text(json.dumps(clean(data), ensure_ascii=False, indent=2, allow_nan=False)+'\n',encoding='utf-8')

# Reproduce established historical exporter loader conventions, including its
# accepted diet-normalization and LIM completion; no new parameter convention.
snapshot = OUT / (MID+'.json')
shutil.copy2(MODEL, snapshot)
identity = {'reason':'Saved export discarded per-basal-source matrices; full direct returns are required to verify every group/source sign, including unfished groups.',
            'authorization':'Coordinator confirmed existing user authorization covers this necessary direct-only run on 2026-09-30.',
            'model_id':MID,'source_sha256':sha(MODEL),'constructor':{'underdetermined':True,'zero_biomass_accum':False,'DC_tol':0.001,'normalize_DC':True,'zero_catch':True,'default_gs':True},
            'diagnostic_settings':{'det_open_mode':'none','det_theta':1.0,'det_external_sppr':0.0,'det_collapse_mode':'never'},
            'excluded_groups':[], 'engine_files':{p.name:sha(p) for p in [ROOT/'tools/scientific_code/PPREstimation/ModelData.py',ROOT/'tools/scientific_code/PPREstimation/PPRCalculator.py']}}
save('input_identity.json',identity)
with warnings.catch_warnings(record=True) as ww:
    warnings.simplefilter('always')
    pc=PPRCalculator.from_modeldata(ModelData(str(snapshot)), **identity['constructor'])
save('constructor_warnings.json',[str(w.message) for w in ww])
pc._groups_df.to_csv(OUT/'runtime_groups_before.csv',encoding='utf-8',float_format='%.17g')
pc._DC.to_csv(OUT/'runtime_diet.csv',encoding='utf-8',float_format='%.17g')
pc._det_fate.to_csv(OUT/'runtime_detritus_routing.csv',encoding='utf-8',float_format='%.17g')
saved=pd.read_excel(REGION/'models'/MID/'sppr_source.xlsx',sheet_name='groups_df').set_index('seq')
runtime=pc._groups_df.copy()
checks=[]
for idx in runtime.index:
    for col in runtime.columns:
        if col not in saved:continue
        x,y=runtime.loc[idx,col],saved.loc[idx,col]
        if pd.isna(x) and pd.isna(y):continue
        if isinstance(x,(int,float,np.number)) and isinstance(y,(int,float,np.number)):
            same=bool(np.isclose(x,y,rtol=1e-10,atol=1e-10,equal_nan=True))
        else:same=str(x)==str(y)
        if not same:checks.append({'group_id':int(idx),'field':col,'runtime':clean(x),'saved':clean(y)})
save('runtime_vs_saved_groups.json',{'differences':checks,'numeric_tolerance':1e-10,'note':'Source text differences are distinct from protected numerical state.'})
if any(isinstance(r['runtime'],(int,float)) or isinstance(r['saved'],(int,float)) for r in checks):
    raise RuntimeError('Reproduced numerical runtime differs from accepted saved Groups; no diagnostic adoption permitted until reconciled.')
for option in ('GE','TE','With Egestion'):
    stem=option.replace(' ','_')
    try:
        with warnings.catch_warnings(record=True) as ww:
            warnings.simplefilter('always')
            report,sppr,A,L=pc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,**identity['diagnostic_settings'])
        save(stem+'_report.json',report)
        save(stem+'_warnings.json',[str(w.message) for w in ww])
        for name,df in [('SPPR',sppr),('A',A),('L',L)]:
            df.to_csv(OUT/(stem+'_'+name+'.csv'),encoding='utf-8',float_format='%.17g')
            save(stem+'_'+name+'.json',{'row_ids':clean(df.index.tolist()),'column_ids':clean(df.columns.tolist()),'values':clean(df.values)})
        pairs=[]
        for i in sppr.index:
            for j in sppr.columns:
                v=sppr.loc[i,j]
                if pd.notna(v) and v<0:pairs.append({'group_id':i,'source_id':j,'sppr':float(v)})
        save(stem+'_sign_checks.json',{'shape':list(sppr.shape),'rows':clean(sppr.index.tolist()),'sources':clean(sppr.columns.tolist()),'negative_pairs':pairs,'nonfinite_entries':int((~np.isfinite(sppr.values)).sum())})
        print(option,report.get('status'),sppr.shape,'negative entries',len(pairs),flush=True)
    except Exception:
        save(stem+'_exception.json',{'outcome':'EXCEPTION','traceback':traceback.format_exc()})
        print(option,'EXCEPTION',flush=True)
pc._groups_df.to_csv(OUT/'runtime_groups_after.csv',encoding='utf-8',float_format='%.17g')
assert sha(MODEL)==identity['source_sha256']
save('preservation.json',{'canonical_unchanged':True,'runtime_groups_unchanged':sha(OUT/'runtime_groups_before.csv')==sha(OUT/'runtime_groups_after.csv')})
