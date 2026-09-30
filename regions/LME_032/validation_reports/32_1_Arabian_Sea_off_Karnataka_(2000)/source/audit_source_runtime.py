"""Bounded reproduction of the selected input and its source-stated zero BA variant."""
from pathlib import Path
import sys, json, hashlib, warnings, platform
import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
REVIEW = Path(__file__).resolve().parent.parent
MODEL = ROOT/'regions/LME_032/models/32_1_Arabian_Sea_off_Karnataka_(2000)/model.json'
ENGINE = ROOT/'tools/scientific_code/PPREstimation'
sys.path.insert(0, str(ENGINE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encode(x):
    if isinstance(x, pd.DataFrame):
        a=x.to_numpy(); numeric=np.asarray(a,dtype=float) if all(pd.api.types.is_numeric_dtype(t) for t in x.dtypes) else None
        return {'type':'DataFrame','index':encode(x.index.tolist()),'columns':encode(x.columns.tolist()),
                'index_name':x.index.name,'columns_name':x.columns.name,'dtypes':[str(t) for t in x.dtypes],
                'values':encode(a.tolist()),'masks':None if numeric is None else {
                    'nan':np.isnan(numeric).tolist(),'posinf':np.isposinf(numeric).tolist(),'neginf':np.isneginf(numeric).tolist()}}
    if isinstance(x, pd.Series): return {'type':'Series','index':encode(x.index.tolist()),'name':x.name,'dtype':str(x.dtype),'values':encode(x.tolist())}
    if isinstance(x, dict): return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x, (list,tuple,np.ndarray)): return [encode(v) for v in x]
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, (np.bool_,)): return bool(x)
    if isinstance(x, (float,np.floating)):
        return float(x) if np.isfinite(x) else {'type':'float','nonfinite':'nan' if np.isnan(x) else ('+inf' if x>0 else '-inf')}
    if x is pd.NA: return {'type':'pandas.NA'}
    return x
def save(name,x): (REVIEW/name).write_text(json.dumps(encode(x),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

source=json.loads(MODEL.read_text(encoding='utf-8-sig'))
save('source/baseline_model.json',source)
variant=json.loads(json.dumps(source))
for g in variant['group']: g['biomass_accum']='0'
vpath=REVIEW/'source/zero_ba_source_variant.json'
vpath.write_text(json.dumps(variant,ensure_ascii=False,indent=2),encoding='utf-8')
settings={'underdetermined':True,'zero_catch':True,'zero_biomass_accum':False,'default_gs':True,
          'weight_flow':1.0,'weight_guess':1.0,'normalize_DC':True,'DC_tol':0.001}
provenance={'source_model_sha256':sha(MODEL),'variant_sha256':sha(vpath),'constructor_settings':settings,
            'python':sys.version,'platform':platform.platform(),'engine_hashes':{p.name:sha(p) for p in [ENGINE/'ModelData.py',ENGINE/'PPRCalculator.py',ENGINE/'utils.py']},
            'methods':{'TE_option':['GE','TE','With Egestion'],'short':False,'flat':False,'return_sppr':True,
                       'det_collapse_mode':'never','det_open_mode':'none','det_theta':1.0,'det_external_sppr':0.0,'fix_EE_0_cases':True},
            'source_zero_BA_locator':'Mohamed et al. 2008, CMFRI Bulletin 51, printed p.21 / PDF p.31'}
save('diagnostics/runtime_provenance.json',provenance)
summary={}
for label,path in [('saved_input',MODEL),('source_zero_ba',vpath)]:
    md=ModelData(str(path))
    raw=md.groups_data.copy()
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always')
        calc=PPRCalculator.from_modeldata(md,**settings)
    loaded=calc._groups_df.copy()
    ledger=[]
    for seq in sorted(set(raw.index)|set(loaded.index)):
        for field in sorted(set(raw.columns)&set(loaded.columns)):
            a,b=raw.at[seq,field],loaded.at[seq,field]
            if pd.isna(a) and pd.isna(b): continue
            if not (a==b or (isinstance(a,(float,int)) and isinstance(b,(float,int)) and np.isfinite(a) and np.isfinite(b) and abs(a-b)<=1e-13*max(1,abs(a)))):
                ledger.append({'group_id':int(seq),'group_name':calc.seq2name.get(seq),'field':field,'before':a,'after':b})
    save(f'diagnostics/{label}_state.json',{'raw_groups':raw,'loaded_groups':loaded,'DC':calc._DC,'detritus_fate':calc._det_fate,'ledger':ledger,'constructor_warnings':[str(w.message) for w in ws]})
    summary[label]={}
    for option in ('GE','TE','With Egestion'):
        key=option.replace(' ','_')
        try:
            with warnings.catch_warnings(record=True) as ws:
                warnings.simplefilter('always')
                report,sppr,A,L=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
            negatives=[]
            if sppr is not None:
                for recipient in sppr.index:
                    for src in sppr.columns:
                        val=sppr.at[recipient,src]
                        if np.isfinite(val) and val<0: negatives.append({'method':option,'source_id':int(src),'source_name':calc.seq2name.get(src),'group_id':int(recipient),'group_name':calc.seq2name.get(recipient),'value':float(val),'comparison_tolerance':0})
            save(f'diagnostics/{label}_{key}.json',{'report':report,'SPPR':sppr,'A':A,'L':L,'axis_names':calc.seq2name,'orientation':'rows=recipient group, columns=basal source','units':'wet-weight equivalent per unit group wet weight','warnings':[str(w.message) for w in ws],'negative_entries':negatives})
            summary[label][option]={'status':report.get('status'),'report_keys':list(report),'negative_entries':len(negatives),
                                    'divergence':report.get('divergence'),'model_input':report.get('model_input'),'balance':report.get('balance')}
        except Exception as e:
            import traceback
            save(f'diagnostics/{label}_{key}.json',{'status':'execution_exception','exception':repr(e),'traceback':traceback.format_exc()})
            summary[label][option]={'status':'execution_exception','exception':repr(e)}
    print(label, json.dumps(encode(summary[label]),ensure_ascii=False),flush=True)
save('diagnostics/comparison_summary.json',summary)
