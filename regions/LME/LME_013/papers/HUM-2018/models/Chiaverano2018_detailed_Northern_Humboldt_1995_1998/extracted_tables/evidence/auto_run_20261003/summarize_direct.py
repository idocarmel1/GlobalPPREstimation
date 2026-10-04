"""Reopen and reconcile retained direct diagnostics without a new scientific run."""
from pathlib import Path
import csv, hashlib, json, math

HERE=Path(__file__).resolve().parent
METHODS=('GE','TE','With Egestion')
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def attributes(encoded): return {k['value']:v for k,v in encoded['items']}

before=read(HERE/'runtime_before_methods_lossless.json')
after=read(HERE/'runtime_after_methods_lossless.json')
ba,aa=attributes(before),attributes(after)
biological=[k for k in set(ba)|set(aa) if k!='detritus_resolution_info' and ba.get(k)!=aa.get(k)]
assert not biological, biological
bundle={'schema_version':1,'scope':'All three full actual direct return tuples; no new calculator execution',
        'run_manifest_sha256':sha(HERE/'run_manifest.json'),'methods':{}}
text=['# Full direct diagnostic returns','',
      'These are the unabridged diagnostic dictionaries from the actual direct calls. Each companion lossless return retains the entire tuple including SPPR, A and L matrices.','']
state=before
cache_ledger=[]
for method in METHODS:
    key=method.replace(' ','_');folder=HERE/key
    report=read(folder/'diagnostic_return.json')
    ret=read(folder/'full_return_lossless.json')
    bundle['methods'][method]={'availability':'present','full_return':ret}
    text+=['## '+method,'','```json',json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2),'```','',
           f'Full returned tuple: [{key}/full_return_lossless.json]({key}/full_return_lossless.json).',
           f'Matrices: [SPPR]({key}/SPPR.csv), [A]({key}/A.csv), [L]({key}/L.csv).','']
    cache=read(folder/'detritus_resolution_info_lossless.json')
    pre_state=json.loads(json.dumps(state))
    items=[item for item in state['items'] if item[0].get('value')!='detritus_resolution_info']
    state={'type':'dict','items':items+[[{'type':'str','value':'detritus_resolution_info'},cache]]}
    cache_ledger.append({'method':method,'only_changed_runtime_attribute':'detritus_resolution_info',
        'biological_fields_unchanged':True,'cache_after_call':f'{key}/detritus_resolution_info_lossless.json',
        'TE_cache_note':'TE leaves preceding GE cache on calculator; actual TE report explicitly discards that cache and uses b=0 convention.' if method=='TE' else None,
        'state_retention':'Exact per-method state assembled from observed immutable before-state and actual retained per-method cache; final assembled state equals observed after-state.'})
    save(folder/'runtime_before_exact.json',pre_state)
    save(folder/'runtime_after_exact.json',state)
assert state==after
save(HERE/'method_runtime_state_ledger.json',{'biological_fields_changed':biological,'final_state_matches_observed':True,'calls':cache_ledger})
save(HERE/'full_direct_report.json',bundle)
(HERE/'full_direct_report.md').write_text('\n'.join(text),encoding='utf-8')

with (HERE/'runtime_group_budget_residuals.csv').open(encoding='utf-8',newline='') as f: budgets=list(csv.DictReader(f))
with (HERE/'group_scope_coefficients.csv').open(encoding='utf-8',newline='') as f: coefficients=list(csv.DictReader(f))
with (HERE/'all_negative_matrix_entries.csv').open(encoding='utf-8',newline='') as f: negatives=list(csv.DictReader(f))
weighted=[];records=[]
for method in METHODS:
    report=read(HERE/method.replace(' ','_')/'diagnostic_return.json')
    contrib=[]
    for r in budgets:
        c=next(x for x in coefficients if x['method']==method and x['scope']=='all' and x['group_id']==r['group_seq'])
        value=float(r['production_residual'])*float(c['sppr_wet'])
        weighted.append({'method':method,'group_id':int(r['group_seq']),'group_name':r['group_name'],
            'production_rhs_minus_p':float(r['production_residual']),'sppr_all':float(c['sppr_wet']),
            'weighted_group_residual':value,'unfished':float(r['catch'])==0})
        contrib.append(value)
    weighted_sum=math.fsum(contrib)
    observed=report['balance']['outflow']-report['balance']['inflow']
    reconciles=math.isclose(weighted_sum,observed,rel_tol=1e-10,abs_tol=1e-9)
    rows=[n for n in negatives if n['method']==method and n['matrix']=='SPPR']
    source_negative=sorted(set(int(n['source_column_id']) for n in rows))
    assert len(source_negative)==report['divergence']['n_negative_sources']
    records.append({'method':method,'weighted_production_residual_sum':weighted_sum,'outflow_minus_inflow':observed,
        'remainder_not_assigned_to_groups':observed-weighted_sum,
        'identity_supported_for_this_configuration':reconciles,
        'interpretation':'Weighted production residual identity numerically reproduces PP budget gap.' if reconciles else
                         'TE EE=0 severing/mortality-writeoff formulation prevents this residual-only identity; remainder remains explicit.',
        'negative_SPPR_entries':len(rows),'negative_source_ids':source_negative,
        'negative_entries_unfished_recipients':sum(n['unfished_recipient']=='True' for n in rows)})
with (HERE/'weighted_group_budget_residuals.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(weighted[0]));w.writeheader();w.writerows(weighted)
save(HERE/'budget_gap_decomposition.json',records)
save(HERE/'direct_reopen_verification.json',{'all_returned_methods':list(METHODS),
    'full_returns_readable':True,'negative_source_counts_match':True,
    'all_biological_runtime_fields_unchanged_by_methods':not biological,
    'method_cache_states_reconcile_final':state==after,
    'method_specific_budget_decompositions':records})
print(json.dumps({'methods':len(METHODS),'biology_unchanged':not biological,'negative_entries_total':len(negatives)}))
