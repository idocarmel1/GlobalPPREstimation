"""Reproduce direct diagnostics from the retained P/Q-completed computational copy."""
from pathlib import Path
import sys, json, hashlib, warnings, math, platform
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'engine'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator

INPUT = HERE / '29_20201978_Southern_Benguela_PQ_completed_(1978).json'
SETTINGS = dict(underdetermined=False, zero_catch=False, zero_biomass_accum=True,
                default_gs=True, weight_flow=1., weight_guess=1., normalize_DC=False, DC_tol=.001)
DIAGNOSTIC = dict(det_collapse_mode='never', det_open_mode='none', det_theta=1., det_external_sppr=0.)

def clean(v):
    if isinstance(v, pd.DataFrame):
        return {'index': clean(v.index.tolist()), 'columns': clean(v.columns.tolist()), 'data': clean(v.values.tolist())}
    if isinstance(v, pd.Series): return {'index': clean(v.index.tolist()), 'data': clean(v.tolist())}
    if isinstance(v, np.ndarray): return clean(v.tolist())
    if isinstance(v, dict): return {str(k): clean(x) for k,x in v.items()}
    if isinstance(v, (list,tuple)): return [clean(x) for x in v]
    if isinstance(v, np.generic): return clean(v.item())
    if isinstance(v, float) and not math.isfinite(v): return None
    return v

def save(name, value):
    (HERE/name).write_text(json.dumps(clean(value), ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

def state(c):
    return {k:clean(v) for k,v in vars(c).items() if isinstance(v,(pd.DataFrame,pd.Series))}

def run():
    m=ModelData(str(INPUT)); m.lme=29
    before=m.groups_data.copy(deep=True)
    dc=m.DC.copy(deep=True)
    with warnings.catch_warnings(record=True) as ww:
        warnings.simplefilter('always')
        c=PPRCalculator.from_modeldata(m, **SETTINGS)
    st=state(c)
    reports={};solutions={};notices={}
    for option in ['GE','TE','With Egestion']:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            try:
                report,sppr,a,l=c.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,**DIAGNOSTIC)
                reports[option]=report
                solutions[option]={'SPPR':sppr,'A':a,'L':l}
            except Exception as ex:
                reports[option]={'status':'EXCEPTION','exception':type(ex).__name__,'message':str(ex)}
            notices[option]=[str(x.message) for x in w]
    return c,before,dc,st,reports,solutions,[str(x.message) for x in ww],notices

if __name__=='__main__':
    c,before,dc,st,reports,solutions,ww,notices=run()
    c2,b2,d2,st2,r2,s2,_,_=run()
    assert clean(st)==clean(st2), 'Persisted-input reload changed loaded state'
    assert clean(reports)==clean(r2), 'Persisted-input reload changed reports'
    assert clean(solutions)==clean(s2), 'Persisted-input reload changed coefficients/flows'
    ledger=[]
    for i in before.index:
        for col in before.columns.intersection(c._groups_df.columns):
            a=clean(before.loc[i,col]);b=clean(c._groups_df.loc[i,col])
            if a != b: ledger.append(dict(seq=int(i),group=c.seq2name[i],field=col,source_loaded=a,runtime=b))
    for i in dc.index:
        for j in dc.columns:
            a=clean(dc.loc[i,j]);b=clean(c._DC.loc[i,j])
            if a!=b: ledger.append(dict(seq=int(i),group=c.seq2name[i],field=f'diet:{j}',source_loaded=a,runtime=b))
    save('loaded_state.json',st)
    save('source_loaded_groups.json',before)
    save('transformation_ledger.json',ledger)
    save('direct_reports.json',reports)
    save('direct_solutions.json',solutions)
    save('execution_evidence.json',dict(input_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),
         constructor=SETTINGS,diagnostic=DIAGNOSTIC,python=platform.python_version(),
         numpy=np.__version__,pandas=pd.__version__,engine_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'engine').glob('*.py')},
         constructor_warnings=ww,diagnostic_python_warnings=notices,
         persisted_input_reload_equal=True,state_unchanged_by_diagnostics=st==state(c)))
    (HERE/'DIRECT_DIAGNOSTICS.md').write_text('# Full direct SPPR diagnostic returns\n\n'+
        '\n\n'.join('## '+k+'\n\n```json\n'+json.dumps(clean(v),ensure_ascii=False,indent=2)+'\n```' for k,v in reports.items()),encoding='utf-8')
    groups=c._groups_df.copy();groups.insert(0,'seq',groups.index)
    groups.to_csv(HERE/'runtime_groups.csv',index=False,encoding='utf-8')
    rows=[]
    for option,solution in solutions.items():
        sppr=solution['SPPR']
        for scope in ['all','inner','PP']:
            cols=[j for j in sppr.columns if scope=='all' or (j not in c.get_Import_seq() and (scope!='PP' or j not in c.get_DET_seq()))]
            vals=sppr[cols].sum(axis=1,min_count=1).reindex(c._groups_df.index)
            for i,v in vals.items():rows.append(dict(seq=int(i),group=c.seq2name[i],scope=scope,method={'GE':'new_GE','TE':'new_TE_EEfix','With Egestion':'new_WithEgestion'}[option],sppr=float(v)))
    pd.DataFrame(rows).to_csv(HERE/'direct_group_sppr.csv',index=False,encoding='utf-8')
    print({k:v['status'] for k,v in reports.items()})
