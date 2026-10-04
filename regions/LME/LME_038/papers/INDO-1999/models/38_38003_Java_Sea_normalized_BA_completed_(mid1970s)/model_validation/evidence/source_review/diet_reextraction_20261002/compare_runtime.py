"""Load both canonical identities using retained actual loader; no SPPR runs."""
from pathlib import Path
import sys, json, hashlib, contextlib
import pandas as pd
import numpy as np

sys.dont_write_bytecode=True
E=Path(__file__).parent.resolve()
R=E.parent
MID='38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
M=R/'models'/MID
sys.path.insert(0,str(M/'diagnostic_code/scientific_code/PPREstimation'))
from create_PPRS_excel import load_model

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def compare_frames(a,b,name):
    assert list(a.index)==list(b.index) and list(a.columns)==list(b.columns),(name,'dimensions')
    exact=[]; significant=[]; maxdiff=0.0
    for i in a.index:
        for c in a.columns:
            x,y=a.loc[i,c],b.loc[i,c]
            if pd.isna(x) and pd.isna(y): continue
            try:
                x,y=float(x),float(y)
                if x==y: continue
                delta=abs(x-y); maxdiff=max(maxdiff,delta)
                row={'row':str(i),'column':str(c),'before':x,'after':y,'abs_difference':delta}
                exact.append(row)
                if not np.isclose(x,y,rtol=0,atol=1e-12,equal_nan=True): significant.append(row)
            except (TypeError,ValueError):
                if x!=y: exact.append({'row':str(i),'column':str(c),'before':str(x),'after':str(y)})
    return {'matrix':name,'shape':list(a.shape),'different_cells_exact':exact,
      'different_cells_at_1e_12':significant,'max_abs_numeric_difference':maxdiff}

receipt=json.loads((E/'root_receipt.json').read_text())
old=E/'original_inputs'/(receipt['canonical_before_sha256']+'_model.json')
new=M/'model.json'
assert sha(new)==receipt['canonical_after_sha256']
for label,p in [('before',old),('after',new)]:
    folder=E/('runtime_'+label); folder.mkdir(exist_ok=True)
    (folder/(MID+'.json')).write_bytes(p.read_bytes())
with (E/'runtime_load.log').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    before,_=load_model(str(E/'runtime_before'/(MID+'.json')))
    after,_=load_model(str(E/'runtime_after'/(MID+'.json')))
comparisons=[compare_frames(before._DC,after._DC,'loaded normalized diet matrix'),
 compare_frames(before._det_fate,after._det_fate,'loaded detritus fate'),
 compare_frames(before._groups_df,after._groups_df,'loaded group parameters and completed flows')]
for label,obj in [('before',before),('after',after)]:
    obj._DC.to_csv(E/('runtime_'+label)/'normalized_DC.csv')
    obj._groups_df.to_csv(E/('runtime_'+label)/'loaded_groups.csv')
    obj._det_fate.to_csv(E/('runtime_'+label)/'detritus_fate.csv')
retained=pd.read_excel(M/'sppr_source.xlsx',sheet_name='groups_df',index_col=0)
retained.index=retained.index.astype(int)
retained=retained.loc[before._groups_df.index]
columns=[c for c in before._groups_df.columns if c in retained.columns]
historical=compare_frames(retained[columns],before._groups_df[columns],'retained runtime workbook versus reloaded old input')
data={'canonical_before_sha256':receipt['canonical_before_sha256'],'canonical_after_sha256':receipt['canonical_after_sha256'],
 'actual_loader_path':str(M/'diagnostic_code/scientific_code/PPREstimation/create_PPRS_excel.py'),
 'settings':{'underdetermined':True,'zero_biomass_accum':False,'DC_tol':0.001,'normalize_DC':True},
 'before_after_comparisons':comparisons,'retained_runtime_workbook':str(M/'sppr_source.xlsx'),'retained_runtime_workbook_sha256':sha(M/'sppr_source.xlsx'),
 'retained_workbook_comparison':historical,
 'exact_before_after_equal':all(not c['different_cells_exact'] for c in comparisons),
 'equivalent_at_1e_12':all(not c['different_cells_at_1e_12'] for c in comparisons),
 'fresh_SPPR_run':False,'adoption_performed':False,
 'equality_criterion':{'atol':1e-12,'rtol':0,'human_preference':'Ignore floating-point differences within absolute 1e-12'},
 'refresh_gate':'Actual before/after loaded normalized state is equal; saved diagnostics/calculations retained, no scientific refresh triggered by canonical hash alone.',
 'runtime_files':{str(p.relative_to(E)):sha(p) for p in E.glob('runtime_*/*') if p.is_file()},
 'loader_code_hashes':{p.name:sha(p) for p in (M/'diagnostic_code/scientific_code/PPREstimation').glob('*.py')}}
(E/'actual_runtime_comparison.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt['actual_runtime_comparison']='regions/LME_038/diet_reextraction_20261002/actual_runtime_comparison.json'
receipt['runtime_equivalent_at_1e_12']=data['equivalent_at_1e_12']
receipt['runtime_exactly_equal']=data['exact_before_after_equal']
receipt['evidence_paths'].append(receipt['actual_runtime_comparison'])
(E/'root_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'exact_before_after_equal':data['exact_before_after_equal'],'equivalent_at_1e_12':data['equivalent_at_1e_12'],
 'differences':[{k:c[k] for k in ['matrix','max_abs_numeric_difference']}|{'exact_count':len(c['different_cells_exact']),'significant_count':len(c['different_cells_at_1e_12'])} for c in comparisons],
 'retained_workbook_max_abs_diff':historical['max_abs_numeric_difference']},indent=2))
