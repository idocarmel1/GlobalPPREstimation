"""Bounded direct-only audit; never adopts normalized coefficients or edits workbooks."""
from pathlib import Path
import sys, json, hashlib, shutil, traceback, warnings
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REGION = HERE.parents[1]
ENGINE = ROOT / 'tools/scientific_code/PPREstimation'
sys.path.insert(0, str(HERE / 'engine_snapshot' if (HERE / 'engine_snapshot').exists() else ENGINE))
sys.path.insert(0, str(ROOT / 'tools'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
from workbooks import read_book, overview, records

def clean(v):
    if isinstance(v, pd.DataFrame):
        return {'index':clean(v.index.tolist()), 'columns':clean(v.columns.tolist()), 'data':clean(v.values.tolist())}
    if isinstance(v, pd.Series): return clean(v.to_dict())
    if isinstance(v, dict): return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v, (list,tuple)): return [clean(x) for x in v]
    if isinstance(v, np.generic): return clean(v.item())
    if isinstance(v, float) and not np.isfinite(v): return None
    return v
def save(name, v):
    (HERE/name).write_text(json.dumps(clean(v),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    bookpath = REGION/'HS_077.xlsx'
    book=read_book(bookpath); o=overview(book)
    model=REGION/o['model_path']
    backup=HERE/'HS_077_before_audit.xlsx'
    if not backup.exists(): shutil.copy2(bookpath,backup)
    snapshot=HERE/'engine_snapshot'; snapshot.mkdir(exist_ok=True)
    for name in ('PPRCalculator.py','ModelData.py','utils.py'):
        if not (snapshot/name).exists(): shutil.copy2(ENGINE/name,snapshot/name)
    inputdir=HERE/'computational_input'; inputdir.mkdir(exist_ok=True)
    source=inputdir/(o['selected_model_id']+'.json')
    if not source.exists(): shutil.copy2(model,source)
    assert sha(source)==sha(model)
    settings=dict(underdetermined=True,zero_catch=True,zero_biomass_accum=False,default_gs=True,weight_flow=1.0,weight_guess=1.0,DC_tol=0.001,normalize_DC=True)
    manifest={'model':o['selected_model_id'],'model_sha256':sha(model),'workbook_backup_sha256':sha(backup),'constructor':settings,'purpose':'Reproduce existing exporter transformations for audit only; no adoption or source repair.', 'code_sha256':{p.name:sha(p) for p in snapshot.glob('*.py')},'runtime':{'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__}}
    save('manifest.json',manifest)
    md=ModelData(str(source));save('pre_constructor_state.json',{'groups':md.groups_data,'DC':md.DC,'det_fate':md.det_fate})
    strict_settings=dict(settings,normalize_DC=False)
    try:
        PPRCalculator.from_modeldata(ModelData(str(source)),**strict_settings)
        strict={'status':'constructed'}
    except Exception as exc:
        strict={'status':'NOT_RUN','constructor':strict_settings,'exception':type(exc).__name__+': '+str(exc),'traceback':traceback.format_exc(),'methods':{m:'NOT_RUN: constructor rejected unchanged source diets' for m in ['GE','TE','With Egestion']}}
    save('source_preserving_constructor.json',strict)
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always')
        calc=PPRCalculator.from_modeldata(ModelData(str(source)),**settings)
    before=md.groups_data; after=calc._groups_df
    changes=[]
    for seq,row in after.iterrows():
        for col,value in row.items():
            old=before.loc[seq,col] if seq in before.index and col in before.columns else None
            if clean(old)!=clean(value): changes.append({'seq':int(seq),'group':row['group_name'],'field':col,'before':clean(old),'after':clean(value)})
    diet_changes=[]
    for seq in calc._DC.index:
        for prey in calc._DC.columns:
            old=md.DC.loc[seq,prey];new=calc._DC.loc[seq,prey]
            if clean(old)!=clean(new): diet_changes.append({'consumer':int(seq),'prey':int(prey),'before':clean(old),'after':clean(new)})
    save('transformation_ledger.json',{'groups':changes,'diet':diet_changes,'warnings':[str(w.message) for w in ws]})
    save('loaded_state.json',{'groups':after,'DC':calc._DC,'det_fate':calc._det_fate})
    reports={};coefficients={}
    for method in ('GE','TE','With Egestion'):
        try:
            report,sppr,A,L=calc.diagnose_sppr(TE_option=method,short=False,flat=False,return_sppr=True)
            reports[method]=report;coefficients[method]={'sppr':sppr,'A':A,'L':L}
        except Exception as exc: reports[method]={'status':'EXCEPTION','exception':str(exc),'traceback':traceback.format_exc()}
        save('direct_diagnostics.json',reports)
    save('historical_runtime_coefficients_NOT_ADOPTED.json',coefficients)
    reloaded=PPRCalculator.from_modeldata(ModelData(str(source)),**settings)
    save('reload_verification.json',{'groups_equal':after.equals(reloaded._groups_df),'diet_equal':calc._DC.equals(reloaded._DC),'det_fate_equal':calc._det_fate.equals(reloaded._det_fate),'canonical_unchanged':sha(model)==manifest['model_sha256'],'workbook_unchanged':sha(bookpath)==sha(backup)})
    print(json.dumps({k:v.get('status') for k,v in reports.items()}))
if __name__=='__main__': main()
