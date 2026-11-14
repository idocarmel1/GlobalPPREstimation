"""Read-only numerical reconciliation and portable index; no engine imports/calls."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True
RUN=Path(__file__).resolve().parents[1]
MODEL=RUN.parents[2]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
OLD=MODEL/'results/diagnostics/2026-11-14_loader_repair'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return os.path.relpath(p,RUN).replace('\\','/')
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def close(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10)

def main():
    m=read(RUN/'run_manifest.json');assert m['complete']
    metadata_note={'field':'taxon_descr','cells':207,'groups':69,
        'tables':['_groups_df','_source_groups_before_completion','_ee_floor_base._groups_df'],
        'archived_representation':'None','restored_representation':'NaN',
        'meaning':'Missing descriptive metadata remains unknown; representation differs. Numerical values and numerical missingness are unchanged.',
        'limits':'Numerical runtime restored; descriptive metadata is not byte/type-identical. Canonical/source files and retained raw source_state are unchanged.',
        'diagnostic_header_omissions':{
            'config.ee_threshold':{'saved_return_value':None,'effective_initialization_threshold':0.1,
                'reason':'Archived runtime omits the standalone attribute; retained initialization settings, ee_floor_info and floor ledger preserve threshold0.1. Floor was not replayed.'},
            'config.model':{'saved_return_value':None,'authoritative_model_id':MODEL.name,
                'reason':'No backing ModelData object restored or constructed; model identity and canonical SHA-256 are retained in run_manifest and evidence_index.'}}}
    m['runtime_restore_qualification']=metadata_note
    m['constructor']='No constructor/floor replay; saved numerical runtime restored; see runtime_restore_qualification for missing descriptive metadata.'
    save(RUN/'run_manifest.json',m)
    assert all(sha((RUN/p).resolve())==value for p,value in m['protected_inputs_before'].items())
    assert all(sha(RUN/'code/PPREstimation'/p)==value for p,value in m['engine_sha256'].items())
    matrix_checks=[];effect={}
    for config in ('control_never','pooled_always'):
        arithmetic=read(RUN/f'outputs/{config}_2019_ppr.json')
        assert len(arithmetic['rows'])==384
        for method in ('GE','TE'):
            full=read(RUN/f'outputs/{config}_{method}.json')
            scopes=read(RUN/f'outputs/{config}_{method}_scopes.json')
            S=full['SPPR'];assert set(S['index'])==set(range(1,71)) and set(S['columns'])=={66,67,68,69,70}
            pairs=[];nonfinite=0
            for label in ('SPPR','A','L'):
                mat=full[label];assert mat['shape']==[len(mat['index']),len(mat['columns'])]
                assert len(set(mat['index']))==len(mat['index']) and len(set(mat['columns']))==len(mat['columns'])
                assert all(len(r)==len(mat['columns']) for r in mat['values'])
                assert all(not any(row) for mask in mat['masks'].values() for row in mask)
                assert all(isinstance(x,(int,float)) and math.isfinite(x) for row in mat['values'] for x in row)
                for i,row in enumerate(mat['values']):
                    for j,value in enumerate(row):
                        if value < -1e-10:pairs.append((label,mat['index'][i],mat['columns'][j],value))
            recorded=[(r['matrix'],r['row_id'],r['column_id'],r['value']) for r in full['negative_entries']]
            assert pairs==recorded
            values={i:dict(zip(S['columns'],row)) for i,row in zip(S['index'],S['values'])}
            for scope,ids in {'PP':[66],'inner':[66,67,68,69],'all':[66,67,68,69,70]}.items():
                coef=dict(zip(scopes[scope]['index'],scopes[scope]['values']))
                assert all(close(sum(row[i] for i in ids),coef[group]) for group,row in values.items())
                total=0
                for row in arithmetic['rows']:
                    sppr=sum(g['weight']*coef[g['group_id']] for g in row['groups'])
                    ppr=row['catch_tonnes']*sppr/9
                    assert close(sppr,row['methods'][method][scope]['sppr_wet'])
                    assert close(ppr,row['methods'][method][scope]['ppr_tC'])
                    total+=ppr
                assert close(total,arithmetic['totals_tC'][method][scope])
            matrix_checks.append({'configuration':config,'method':method,'SPPR_shape':[70,5],
                'nonfinite_entries':0,'negative_SPPR_entries':sum(p[0]=='SPPR' for p in pairs),
                'negative_table_exact':True,'scopes_and_384taxon_arithmetic_reconciled':True})
    for method in ('GE','TE'):
        effect[method]={}
        for scope in ('PP','inner','all'):
            before=m['regional_totals_tC']['control_never'][method][scope]
            after=m['regional_totals_tC']['pooled_always'][method][scope]
            effect[method][scope]={'separate_tC':before,'pooled_tC':after,'difference_tC':after-before,'difference_percent':(after/before-1)*100}
    summary={'model_id':MODEL.name,'variant_id':m['variant_id'],'effect_2019':effect,'diagnostics':m['outcomes'],
        'baseline_parity':m['baseline_parity'],'matrix_checks':matrix_checks,'all70group_ids_retained':True,
        'runtime_restore_qualification':metadata_note,
        'interpretation':'Engine-supported shared detritus SPPR scaling; no literal group/diet merge. Original coupled diagnostic b differs from pooled collapse_b.',
        'strict_balance_note':'Model mass balance and SPPR budget flags true; diet-row normalization check remains false.',
        'mapping_status':'Same384taxon proposal, pending review/adoption','adoption_performed':False}
    save(RUN/'qa/comparison_summary.json',summary)
    artifacts=[];required=[]
    def add(role,p,req=True):
        if req:required.append(role)
        artifacts.append({'role':role,'path':rel(p),'availability':'present','sha256':sha(p)})
    add('canonical_source',MODEL/'model.json')
    add('exact_mapping_weights',MODEL/'model_validation/evidence/mapping/mapping_decisions.json')
    add('baseline_evidence_index',OLD/'evidence_index.json')
    add('baseline_manifest',OLD/'run_manifest.json')
    add('baseline_constructor_source_state',OLD/'constructor.json.gz')
    add('runtime_restore',RUN/'inputs/restored_runtime.json')
    add('source_state',RUN/'inputs/source_state.json')
    add('reproduction_code',RUN/'code/run_pooling.py')
    add('finalization_code',Path(__file__).resolve())
    add('run_manifest',RUN/'run_manifest.json')
    for name in m['engine_sha256']:add('pinned_engine_'+name,RUN/'code/PPREstimation'/name)
    for method,oldname in [('GE','new_GE'),('TE','new_TE_EEfix')]:
        add('baseline_'+method,OLD/(oldname+'.json.gz'))
        add('pooled_'+method+'_aggregation_ledger',RUN/f'outputs/pooled_{method}_aggregation_ledger.json')
        for config in ('control_never','pooled_always'):
            add(config+'_'+method+'_full_return',RUN/f'outputs/{config}_{method}.json')
            add(config+'_'+method+'_scope_coefficients',RUN/f'outputs/{config}_{method}_scopes.json')
    for config in ('control_never','pooled_always'):add(config+'_regional_arithmetic',RUN/f'outputs/{config}_2019_ppr.json')
    add('verification',RUN/'qa/verification.json')
    add('comparison_summary',RUN/'qa/comparison_summary.json')
    for name in ('independent_pooled_review.json','mapping_comparability.json'):
        p=RUN/'qa'/name
        if p.exists():add(name,p)
    mapping_review=MODEL/'model_validation/work/2026-11-14_200000_ices_full_review/qa/pooled_detritus_mapping_comparability.json'
    if mapping_review.exists():add('independent_mapping_comparability',mapping_review)
    contributions=MODEL/'model_validation/work/2026-11-14_200000_ices_full_review/qa/pooled_detritus_source_contributions.json'
    if contributions.exists():add('independent_source_contributions',contributions)
    for path in m['protected_inputs_before']:
        p=(RUN/path).resolve()
        if not any(x['path']==rel(p) for x in artifacts):add('protected_'+p.name,p,False)
    artifacts.append({'role':'new_With_Egestion','availability':'inapplicable','reason':'Only GE/TE sensitivity requested; historical With Egestion preserved','acquisition_status':'Not requested or executed'})
    index={'schema_version':1,'run_id':RUN.name,'region_id':'LME_022','model_id':MODEL.name,'variant_id':m['variant_id'],
        'source_identity':{'canonical_sha256':m['canonical_sha256']},
        'computational_input_identity':{'restored_archive_sha256':sha(OLD/'new_GE.json.gz'),'engine_commit':m['engine_commit'],
            'EE_floor_ON':.1,'pool_group_ids':[67,68,69],'det_collapse_mode':'always','control':'never'},
        'methods':['GE','TE'],'required_roles':required,'artifacts':artifacts,
        'reconciliation':{'protected_inputs_unchanged':True,'numerical_runtime_and_unknown_status_preserved':True,'metadata_representation_exception_documented':True,'matrices_and_arithmetic_reconciled':True,
            'baseline_parity':all(v['within_1e12'] for p in m['baseline_parity'].values() for v in p.values())},
        'restriction':'Sensitivity only; source/diet/group/mapping/selection unchanged. Scientific WARN flags remain.'}
    save(RUN/'evidence_index.json',index)
    spec=importlib.util.spec_from_file_location('evidence_check',ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    result=checker.check(RUN/'evidence_index.json');save(RUN/'qa/completeness.json',result);assert result['complete'],result
    print(json.dumps({'complete':True,'effect_2019':effect,'evidence_index_sha256':sha(RUN/'evidence_index.json')}))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
