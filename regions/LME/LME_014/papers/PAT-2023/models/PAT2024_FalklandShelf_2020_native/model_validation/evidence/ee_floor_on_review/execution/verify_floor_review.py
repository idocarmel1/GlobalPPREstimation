"""Reopen saved evidence, verify matrix/accounting integrity; no scientific solve."""
from pathlib import Path
import json
import hashlib
import math

WORK=Path(__file__).resolve().parents[1]
MODEL=WORK.parents[2]
OUT=MODEL/'model_validation/evidence/ee_floor_on_review'

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def series(value):
    frame=value['frame']
    return dict(zip(frame['index'],[r[0] for r in frame['data']]))

full=load(OUT/'direct_diagnostics_full.json')
state=load(OUT/'initialization_and_floor.json')
effective=state['effective_after_floor']
groups=effective['_groups_df']
group_rows={i:dict(zip(groups['columns'],row)) for i,row in zip(groups['index'],groups['data'])}
catch=series(effective['catch'])
metadata=[{'group_id':i,'name':r['group_name'],'type':r['trophic_info'],
           'synthetic':r['trophic_info']=='Import','unfished':catch[i]==0} for i,r in group_rows.items()]
write(OUT/'group_metadata.json',metadata)
checks={}
for method in full['methods']:
    name=method['method']
    assert method['execution']=='returned'
    for key in ('SPPR','A','L'):
        frame=method[key]
        rows,cols=frame['index'],frame['columns']
        assert len(rows)==len(set(rows)) and len(cols)==len(set(cols))
        assert frame['shape']==[len(rows),len(cols)]
        assert len(frame['data'])==len(rows) and all(len(r)==len(cols) for r in frame['data'])
        for mask_name,mask in frame['masks'].items():
            assert len(mask)==len(rows) and all(len(r)==len(cols) for r in mask)
            assert not any(any(r) for r in mask), (name,key,mask_name)
        assert all(math.isfinite(v) for row in frame['data'] for v in row)
    sppr=method['SPPR']
    assert set(sppr['index'])==set(group_rows)
    assert len(sppr['columns'])==5 and len(sppr['index'])==37
    assert not any(v<0 for r in sppr['data'] for v in r)
    footprint_checks={}
    for scope,ids in method['source_scope'].items():
        columns=[sppr['columns'].index(i) for i in ids]
        sums={g:sum(row[j] for j in columns) for g,row in zip(sppr['index'],sppr['data'])}
        saved=series(method['scope_coefficients'][scope])
        assert all(math.isclose(sums[g],saved[g],rel_tol=1e-12,abs_tol=1e-12) for g in sums)
        actual=sum(catch[g]*sums[g] for g in sums)
        field={'all':'ppr_all','inner':'ppr_inner','PP':'ppr_pp_only'}[scope]
        expected=method['diagnostic']['footprint'][field]
        assert math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-12)
        footprint_checks[scope]={'recomputed':actual,'diagnostic':expected,'passed':True}
    checks[name]={'axes_shapes_masks_finite':True,'all_37_groups_five_sources':True,
                  'no_negative_source_recipient_pairings':True,'scope_and_footprint_reconciliation':footprint_checks}
ledger=state['ledger']
ledger_rows=[dict(zip(ledger['columns'],r)) for r in ledger['data']]
assert all(isinstance(r['source_M0'],dict) and r['source_M0'].get('value')=='nan' for r in ledger_rows)
assert math.isclose(math.fsum(r['external_mortality_export'] for r in ledger_rows),state['info']['external_mortality_export_total'],rel_tol=1e-12,abs_tol=1e-12)
assert all(v for v in state['protected_living_fields'].values())
checks['raw_source_mortality_missingness_preserved']=True
checks['floor_sink_reconciles']=True
checks['living_fields_preserved']=True
write(WORK/'qa/matrix_accounting_verification.json',checks)
paragraphs={
 'GE':[
  'WARN. Living-network spectral radius ρ = 0.281907 and recycling gain b = 0.0386463 are below 1. Detritus-pool SPPR: Discards (35) = 0; Detritus (36) = 1.090900.',
  'No negative or nonfinite source–recipient SPPR entries occur across all 37 groups and five basal sources, including unfished groups. Strict balance passes (relative gap 1.17 × 10⁻¹⁶). The unsupplied Discards pool retains a negative stock residual of −0.207504; this unresolved supply limitation keeps the overall WARN.'
 ],
 'TE':[
  'WARN. Living-network spectral radius ρ = 0.309794 is below 1. Recycling b = 0 is the TE formulation’s convention, not evidence that physical recycling is absent. Detritus-pool SPPR: Discards (35) = 0; Detritus (36) = 0.936570.',
  'No negative or nonfinite source–recipient SPPR entries occur across all 37 groups and five basal sources, including unfished groups. Strict balance now passes (relative gap 1.17 × 10⁻¹⁶); zero-EE and near-zero-TE flags are absent in the effective calculation. The Discards stock residual remains −0.207504, so the overall result remains WARN.'
 ],
 'other':[
  'The EE-floor calculation changes eight accepted groups, including Kelp, and redirects 65.521188 model flow units to a hypothetical nonfishery sink; living biological flows and catch are preserved. These accepted EE values include the documented earlier coupled completion, rather than new observations.',
  'Sharks (27) remains the largest all-source TE coefficient: 399,038.26, compared with the historical 63,225,811.23. Historical regional TE exposure percentages therefore do not describe this floor-on calculation.'
 ]}
write(WORK/'outputs/report_diagnostics.json',paragraphs)
index=load(OUT/'evidence_index.json')
for role,path in [('group-metadata',OUT/'group_metadata.json'),('matrix-accounting-verification',WORK/'qa/matrix_accounting_verification.json')]:
    import os
    index['artifacts'].append({'role':role,'path':Path(os.path.relpath(path,OUT)).as_posix(),
                              'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'availability':'present'})
    index['required_roles'].append(role)
index['reconciliation']['reopened_matrices_and_accounting']=True
write(OUT/'evidence_index.json',index)
print('All saved matrix, scope, footprint, sink, source-missingness and living-flow checks passed.')
print(str(WORK/'outputs/report_diagnostics.json'))
