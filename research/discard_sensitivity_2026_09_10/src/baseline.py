"""Frozen source configuration and deterministic workbook reproduction."""
from pathlib import Path
import sys, json, warnings, contextlib, io, hashlib
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
INPUTS=ROOT/'inputs'
sys.path.insert(0,str(ROOT/'src/experimental_engine'))
from PPRCalculator import PPRCalculator
from ModelData import ModelData

FRACTIONS=[0.,.01,.05,.1,.2,.3,.4,.5,.75,1.]
METHODS=['standard_fixed_baseline_TL','SPPR_1995_TE0.1','SPPR_1995_TEmean','SPPR_1986',
         'new_GE','new_TE_EEfix','new_WithEgestion','Ulanowicz_TE']
FLOW_METHODS=METHODS[4:]
SCOPES=['all','inner','PP']
SETTINGS=dict(underdetermined=True,zero_biomass_accum=False,DC_tol=.001,normalize_DC=True)


def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def model_paths():
    return sorted((INPUTS/'PPREstimation/real_models/global_cover_jsons').glob('*.json'))


def load_baseline(path):
    data=ModelData(str(path))
    with warnings.catch_warnings(record=True) as messages,contextlib.redirect_stdout(io.StringIO()) as printed:
        calc=PPRCalculator.from_modeldata(data,**SETTINGS)
    meta=dict(model_id=Path(path).stem,model_label=f'{data.model_name} ({data.model_year})',
              source_json_sha256=sha256(path),settings=SETTINGS.copy(),
              warnings=[str(w.message) for w in messages],initializer_output=printed.getvalue())
    workbook=INPUTS/'PPREstimation/output/top10'/f'{Path(path).stem}.xlsx'
    meta['source_workbook_sha256']=sha256(workbook)
    meta['native_harvest']=float(calc.catch.sum())
    meta['denominator_value']=float(calc.get_NPP()/9.)
    return calc,meta


def calculate(calc,method,baseline_standard=None):
    if method=='standard_fixed_baseline_TL':
        return baseline_standard.copy() if baseline_standard is not None else calc.SPPR_1995(global_TE=.1)
    if method=='SPPR_1995_TE0.1': return calc.SPPR_1995(global_TE=.1)
    if method=='SPPR_1995_TEmean': return calc.SPPR_1995(global_TE='mean')
    if method=='SPPR_1986':
        if calc.catch.sum()==0: raise ValueError('catch-weighted TL is undefined at zero catch; legacy zero suppressed')
        return calc.SPPR_1986()
    if method=='EwE_TE_EE': return calc.SPPR_EwE(TE_option='TE',use_EE=True,return_paths=True,silent=True,max_paths=100_000)[0]
    if method=='Ulanowicz_TE': return calc.SPPR_EwE_Ulanowicz(TE_option='TE',global_TE=None,use_EE=False)[0]
    opts={'new_GE':'GE','new_TE_EEfix':'TE','new_WithEgestion':'With Egestion'}
    return calc.SPPR_new(TE_option=opts[method],fix_EE_0_cases=True,
        det_collapse_mode='never',det_open_mode='none',det_theta=1.,det_external_sppr=0.)[0]


def scoped(calc,frame,scope):
    if 'sppr' in frame.columns:
        if scope!='all': return None
        return frame['sppr'].copy()
    columns=list(frame.columns)
    if scope=='inner': columns=[x for x in columns if x not in calc.get_Import_seq()]
    if scope=='PP': columns=[x for x in columns if x in calc.get_PP_seq()]
    # A missing source value must propagate, rather than skipna giving partial PPR.
    return frame[columns].sum(axis=1,skipna=False)


def compare_saved(calc,meta,outputs):
    book=INPUTS/'PPREstimation/output/top10'/f'{meta["model_id"]}.xlsx'
    checks=[]
    for scope in SCOPES:
        saved=pd.read_excel(book,'sppr_'+scope).set_index('seq')
        for method,result in outputs.items():
            if method not in saved.columns or result is None: continue
            fresh=scoped(calc,result,scope)
            if fresh is None: continue
            expect=saved[method].reindex(fresh.index)
            good=np.isfinite(expect)&np.isfinite(fresh)
            diff=(fresh[good]-expect[good]).abs()
            relative=diff/np.maximum(1.,np.abs(expect[good]))
            checks.append(dict(model_id=meta['model_id'],method=method,scope=scope,
                compared_groups=int(good.sum()),max_absolute_error=float(diff.max()) if len(diff) else None,
                max_scaled_error=float(relative.max()) if len(relative) else None,
                passed=bool(len(relative) and np.allclose(fresh[good],expect[good],rtol=2e-7,atol=1e-7)),
                tolerance='atol=1e-7 + rtol=2e-7*abs(saved)',
                saved_nonfinite_count=int((~np.isfinite(expect)).sum())))
    return checks
