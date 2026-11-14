"""Reopen diagnostic artifacts, independently reconcile arrays, and index evidence."""
from pathlib import Path
import hashlib
import json
import math
import os
import numpy as np
import pandas as pd

RUN = Path(__file__).resolve().parents[1]
MODEL = Path(__file__).resolve().parents[4]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def decode(v):
    if isinstance(v, list):
        return [decode(x) for x in v]
    if not isinstance(v, dict):
        return v
    kind = v.get('type')
    if kind == 'float':
        return float(v['value'])
    if kind == 'dict':
        return {decode(k):decode(x) for k,x in v['items']}
    if kind == 'Series':
        return pd.Series(decode(v['values']),index=v['index'],name=v['name'])
    if kind == 'DataFrame':
        return pd.DataFrame(decode(v['values']), index=v['index'], columns=v['columns'])
    if kind == 'ndarray':
        return np.array(decode(v['values']))
    if kind == 'tuple':
        return tuple(decode(x) for x in v['items'])
    return {k:decode(x) for k,x in v.items()}


def save(p,v):
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


checks=[]
for f in sorted((RUN/'outputs').glob('*.json')):
    if f.name.endswith('_summary.json') or f.name == 'summary.json':
        continue
    raw=json.loads(f.read_text(encoding='utf-8'))
    if 'diagnostic' not in raw:
        raise AssertionError(f'Unavailable outcome: {f}')
    d=decode(raw)
    S,A,L=d['SPPR'],d['A'],d['L']
    assert S is not None and A is not None and L is not None
    for name,mat in [('SPPR',S),('A',A),('L',L)]:
        assert mat.index.is_unique and mat.columns.is_unique
        assert list(mat.shape)==raw[name]['shape']
        assert np.isfinite(mat.to_numpy(dtype=float)).all()
        for kind,mask in raw[name]['masks'].items():
            assert np.asarray(mask).shape==mat.shape
            assert not np.any(mask), (name,kind)
    assert set(S.index)==set(range(1,27)) and set(S.columns)=={1,25,26}
    assert set(A.index)==set(A.columns)==set(range(1,27))
    A=A.loc[S.index,S.index]
    L=L.loc[S.index,S.index]
    assert np.allclose(L.values,A.values-np.eye(26),rtol=0,atol=2e-15)
    residual=L.values@S.values
    max_scaled=float(np.max(np.abs(residual)/(1+np.abs(S.values))))
    assert max_scaled<1e-12,(f.name,max_scaled)
    ids=[i for i in A.index if i not in (1,25,26)]
    rho=float(max(abs(np.linalg.eigvals(A.loc[ids,ids]))))
    assert math.isclose(rho,d['diagnostic']['divergence']['rho_living'],rel_tol=1e-12,abs_tol=1e-12)
    negative=np.argwhere(S.to_numpy() < -1e-10)
    assert len(negative)==len(d['negative_entries'])
    expected={(int(S.index[i]),int(S.columns[j])):float(S.iloc[i,j]) for i,j in negative}
    actual={(x['recipient_id'],x['source_id']):x['value'] for x in d['negative_entries']}
    assert expected==actual
    assert d['scientific_state_unchanged_by_diagnostic']
    before=d['runtime_before'];after=d['runtime_after']
    for key in before:
        if isinstance(before[key],pd.DataFrame):
            pd.testing.assert_frame_equal(before[key],after[key])
        else:
            pd.testing.assert_series_equal(before[key],after[key])
    summary=decode(json.loads((f.parent/(f.stem+'_summary.json')).read_text(encoding='utf-8')))
    assert math.isclose(float(S.loc[22].sum()),summary['seabird_total_sppr'],rel_tol=1e-15)
    scopes={'PP':S[[1]].sum(axis=1),'inner':S[[1,25]].sum(axis=1),'all':S.sum(axis=1)}
    checks.append(dict(file=f.relative_to(RUN).as_posix(),scenario=d['scenario'],method=d['method'],
        status=d['diagnostic']['status'],rho=rho,matrix_scaled_residual=max_scaled,
        negative_entries=len(expected),seabird_scopes={k:float(v.loc[22]) for k,v in scopes.items()},
        all_26_groups_retained=True,axes_masks_equations_verified=True,state_unchanged=True))
assert len(checks)==9

manifest=json.loads((RUN/'run_manifest.json').read_text(encoding='utf-8'))
for rel,expected in manifest['source_hashes'].items():
    assert sha((RUN/rel).resolve())==expected,rel
for artifact in manifest['artifacts']:
    assert sha(RUN/artifact['path'])==artifact['sha256'],artifact['path']
save(RUN/'qa/reopened_matrix_checks.json',checks)

comparison=[]
for scenario in ('baseline','remove_only','remove_redistribute'):
    for method in ('GE','TE','With Egestion'):
        stem=f'{scenario}_{method.replace(" ","_")}'
        d=decode(json.loads((RUN/'outputs'/f'{stem}_summary.json').read_text(encoding='utf-8')))
        comparison.append(dict(scenario=scenario,method=method,overall=d['status'],
            input_status=d['model_input']['status'],divergence_status=d['divergence']['status'],
            balance_status=d['balance']['status'],strict_model_balanced=d['model_input']['is_model_balanced'],
            strict_sppr_balanced=d['balance']['is_balanced'],rho=d['divergence']['rho_living'],
            recycling_b=d['divergence']['b'],pp_budget_gap_percent=100*d['balance']['rel_gap'],
            diet_sum=d['diet_sum'],negative_entries=d['negative_entry_count'],
            seabird_total_sppr=d['seabird_total_sppr'],warnings=d['warnings']))
save(RUN/'outputs/comparison.json',comparison)

artifacts=[]
for rel,expected in manifest['source_hashes'].items():
    role='canonical_source' if rel.endswith('/model.json') else 'archived_input_or_code'
    artifacts.append(dict(role=role,path=rel,sha256=expected,availability='present'))
for f in sorted(RUN.rglob('*')):
    if not f.is_file() or f.name in ('evidence_index.json','completeness.json'):
        continue
    rel=f.relative_to(RUN).as_posix()
    if f.name.startswith('baseline_') and rel.startswith('outputs/'):
        role='baseline'
    elif f.name.startswith('remove_only_') and rel.startswith('outputs/'):
        role='remove_only'
    elif f.name.startswith('remove_redistribute_') and rel.startswith('outputs/'):
        role='remove_redistribute'
    elif f.name=='comparison.json':
        role='comparison'
    elif f.name=='reopened_matrix_checks.json':
        role='matrix_verification'
    elif f.suffix=='.py':
        role='reproduction_code'
    else:
        role='execution_evidence'
    artifacts.append(dict(role=role,path=rel,sha256=sha(f),availability='present'))
save(RUN/'evidence_index.json',dict(schema_version=1,run_id=RUN.name,region_id='LME_022',model_id=MODEL.name,
    variant_id='diagnostic_only_seabird_self_loop_comparison',
    source_identity={'canonical_model_sha256':sha(MODEL/'model.json')},
    computational_input_identity={'archived_state_sha256':'cad6ee682425931cd209e04aad408f86f409a548c3079ce41536ed32d33dd3bb',
                                   'protocol':'Archived baseline and two copied-state diet-only interventions; no adoption'},
    methods=['GE','TE','With Egestion'],required_roles=['canonical_source','archived_input_or_code','baseline',
        'remove_only','remove_redistribute','comparison','matrix_verification','reproduction_code'],
    artifacts=artifacts,reconciliation={'nine_direct_returns':True,'all_groups_preserved':True,
       'source_hashes_unchanged':True,'matrix_axes_masks_equations_verified':True,'negative_entries_reconciled':True,
       'diagnostics_preserve_runtime':True}))
for d in comparison:
    print(json.dumps({k:v for k,v in d.items() if k!='warnings'},allow_nan=False))
print('Verified all nine retained direct results and wrote portable evidence index.')
