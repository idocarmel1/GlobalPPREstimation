"""Reopen saved evidence and build portable index; never execute scientific engine."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys

sys.dont_write_bytecode=True

RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
MODEL=RUN.parents[2]
OLD=MODEL/'results/diagnostics/2026-11-14_171200_seabird_derived_ba'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return os.path.relpath(p,RUN).replace('\\','/')
def save(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main():
    m=read(RUN/'run_manifest.json');assert m['complete']
    assert all(sha((RUN/p).resolve())==value for p,value in m['protected_inputs_before'].items())
    assert all(sha(RUN/'code/PPREstimation'/p)==value for p,value in m['frozen_engine_sha256'].items())
    checks=[];scope_changes={};group_changes={}
    for method in ('GE','TE'):
        group_changes[method]={}
        for config in ('control_off','ee_floor_on'):
            full=read(RUN/f'outputs/{config}_{method}.json')
            scopes=read(RUN/f'outputs/{config}_{method}_scopes.json')
            for label in ('SPPR','A','L'):
                matrix=full[label]
                assert len(set(matrix['index']))==len(matrix['index'])
                assert len(set(matrix['columns']))==len(matrix['columns'])
                assert matrix['shape']==[len(matrix['index']),len(matrix['columns'])]
                assert all(len(row)==len(matrix['columns']) for row in matrix['values'])
                assert all(isinstance(x,(int,float)) and math.isfinite(x) for row in matrix['values'] for x in row)
                assert all(not any(row) for mask in matrix['masks'].values() for row in mask)
                if label=='SPPR':assert all(x>=0 for row in matrix['values'] for x in row)
            matrix=full['SPPR'];assert set(matrix['index'])==set(range(1,27)) and set(matrix['columns'])=={1,25,26}
            values={i:dict(zip(matrix['columns'],row)) for i,row in zip(matrix['index'],matrix['values'])}
            for scope,ids in {'PP':[1],'inner':[1,25],'all':[1,25,26]}.items():
                coefficients=dict(zip(scopes[scope]['index'],scopes[scope]['values']))
                assert all(math.isclose(sum(row[i] for i in ids),coefficients[group],rel_tol=1e-12,abs_tol=1e-12) for group,row in values.items())
            group_changes[method][config]={scope:dict(zip(s['index'],s['values'])) for scope,s in scopes.items()}
            checks.append({'configuration':config,'method':method,'matrix_shape':[26,3],'finite_nonnegative_SPPR':True,'all_masks_empty':True,'all_scopes_reconciled':True})
    off=read(RUN/'outputs/control_off_2019_ppr.json');on=read(RUN/'outputs/ee_floor_on_2019_ppr.json')
    for method in ('GE','TE'):
        scope_changes[method]={}
        for scope in ('PP','inner','all'):
            before=off['totals_tC'][method][scope];after=on['totals_tC'][method][scope]
            scope_changes[method][scope]={'OFF_tC':before,'ON_tC':after,'difference_tC':after-before,'difference_percent':(after/before-1)*100}
    summary={'model_id':MODEL.name,'variant_id':m['variant_id'],'engine_commit':m['frozen_engine_commit'],
        'historical_OFF_parity':m['historical_off_parity'],'diagnostic_summary':m['diagnostic_summary'],
        'matrix_checks':checks,'2019_scope_comparison':scope_changes,'group_scope_coefficients':group_changes,
        'known_subtotals_incomplete_for_unresolved_positive_catch':True,'unresolved_catch_tonnes':on['unresolved_catch_tonnes'],
        'signed_excluded_allocated_catch_tonnes':on['excluded_allocated_catch_tonnes'],
        'preserved_source_and_signed_evidence':True,'adoption_performed':False}
    save(RUN/'qa/comparison_summary.json',summary)
    artifacts=[];required=[]
    def add(role,p,require=True):
        if require:required.append(role)
        artifacts.append({'role':role,'path':rel(p),'sha256':sha(p),'availability':'present'})
    add('canonical_source',MODEL/'model.json')
    add('signed_historical_review',MODEL/'model_validation/validation.docx')
    add('retained_mapping_appendix',MODEL/'model_validation/taxon_mapping.xlsx')
    add('exact_mapping_weights',MODEL/'model_validation/evidence/source_review/taxon_audit.json')
    add('historical_correction_provenance',OLD/'inputs/intervention.json')
    add('historical_evidence_index',OLD/'evidence_index.json')
    add('historical_full_manifest',OLD/'run_manifest.json')
    add('restored_input_identity',OLD/'inputs/runtime_state_corrected.json')
    add('run_manifest',RUN/'run_manifest.json')
    add('reproduction_code',RUN/'code/run_ee_floor.py')
    add('evidence_finalization_code',Path(__file__).resolve())
    for name in m['frozen_engine_sha256']:add('frozen_engine_'+name,RUN/'code/PPREstimation'/name)
    add('exact_restored_state',RUN/'inputs/exact_restored_state.json')
    for config in ('control_off','ee_floor_on'):
        add(config+'_runtime_state',RUN/f'inputs/{config}_state.json')
        add(config+'_floor_ledger',RUN/f'inputs/{config}_floor_ledger.json')
        add(config+'_regional_arithmetic',RUN/f'outputs/{config}_2019_ppr.json')
        for method in ('GE','TE'):
            add(config+'_'+method+'_full_return',RUN/f'outputs/{config}_{method}.json')
            add(config+'_'+method+'_scope_coefficients',RUN/f'outputs/{config}_{method}_scopes.json')
            if config=='control_off':add('historical_'+method+'_full_return',OLD/f'outputs/corrected_{method}.json')
    add('runtime_and_parity_verification',RUN/'qa/verification.json')
    add('comparison_summary',RUN/'qa/comparison_summary.json')
    qa=RUN/'qa/independent_ee_floor_review.json'
    if qa.exists():add('independent_review',qa)
    for path in m['protected_inputs_before']:
        p=(RUN/path).resolve()
        if not any(x['path']==rel(p) for x in artifacts):add('protected_input_'+p.name,p,False)
    artifacts.append({'role':'new_With_Egestion','availability':'inapplicable','reason':'GE and TE only requested; historical With Egestion is preserved unchanged','acquisition_status':'Not requested; not executed'})
    index={'schema_version':1,'run_id':RUN.name,'region_id':'LME_022','model_id':MODEL.name,'variant_id':m['variant_id'],
        'source_identity':{'canonical_sha256':m['canonical_model_sha256']},
        'computational_input_identity':{'restored_runtime_sha256':sha(OLD/'inputs/runtime_state_corrected.json'),'engine_commit':m['frozen_engine_commit'],'EE_floor_ON':.1,'EE_threshold':.1,'same_engine_control':'OFF'},
        'methods':['GE','TE'],'required_roles':required,'artifacts':artifacts,
        'reconciliation':{'protected_inputs_unchanged':True,'matrices_and_scope_sums_verified':True,'same_engine_OFF_matches_historical':all(v['within_1e12_tolerance'] for method in m['historical_off_parity'].values() for v in method.values()),'annual_arithmetic_included':True},
        'restriction':'Scientific comparison only; no selection, mapping, workbook, signature or adoption changes. Unresolved positive-catch model PPR remains unknown.'}
    save(RUN/'evidence_index.json',index)
    checker=ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py'
    spec=importlib.util.spec_from_file_location('evidence_check',checker);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    completeness=module.check(RUN/'evidence_index.json');save(RUN/'qa/completeness.json',completeness);assert completeness['complete'],completeness
    print(json.dumps({'complete':True,'2019_scope_comparison':scope_changes,'matrix_checks':checks,'evidence_index_sha256':sha(RUN/'evidence_index.json')},ensure_ascii=False))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
