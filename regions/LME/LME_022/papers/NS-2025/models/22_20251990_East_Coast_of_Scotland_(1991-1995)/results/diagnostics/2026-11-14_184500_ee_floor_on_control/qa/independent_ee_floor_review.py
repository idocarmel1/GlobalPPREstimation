"""Read-only independent audit of retained artifacts. Never imports/runs the engine.

Only this QA script and its JSON finding file are written. Input snapshots,
scientific data, workbooks, selections and signed reports are read-only.
"""
from pathlib import Path
import hashlib
import ast
import json
import math
import sys
from datetime import datetime, timezone

RUN = Path(__file__).resolve().parents[1]
MODEL = RUN.parents[2]
ROOT = next(p for p in RUN.parents if (p/'Project.xlsx').exists())
OLD = MODEL/'results/diagnostics/2026-11-14_171200_seabird_derived_ba'
ICES = ROOT/'regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991'

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

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
        return dict(zip(decode(v['index']),decode(v['values'])))
    if kind == 'DataFrame':
        return {i:dict(zip(decode(v['columns']),decode(row))) for i,row in zip(decode(v['index']),v['values'])}
    if kind in ('tuple','ndarray'):
        return decode(v.get('items',v.get('values')))
    if kind in ('PPRCalculator','ModelData'):
        return decode(v['attributes'])
    return {k:decode(x) for k,x in v.items()}

def same(a,b):
    if isinstance(a,dict):
        return isinstance(b,dict) and a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list):
        return isinstance(b,list) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if isinstance(a,float) and math.isnan(a):
        return isinstance(b,float) and math.isnan(b)
    return a==b

def close(a,b,abs_tol=1e-10):
    return math.isclose(a,b,rel_tol=1e-12,abs_tol=abs_tol)

checks = {}
findings = {}

def check(label,condition):
    checks[label] = bool(condition)
    assert condition, label

def main():
    manifest = read(RUN/'run_manifest.json')
    check('manifest_complete',manifest.get('complete') is True)
    check('configuration_floor_on_01',manifest['ee_floor']==.1 and manifest['ee_threshold']==.1 and manifest['configurations']=={'control_off':False,'ee_floor_on':True})
    check('exact_audited_variant',manifest['variant_id']=='seabird_no_self_loop_proportional_prey_derived_ba')
    check('method_settings',manifest['method_options']=={'det_collapse_mode':'never','det_open_mode':'none','det_theta':1,'det_external_sppr':0,'fix_EE_0_cases':True})
    actual_hashes={n:sha(RUN/'code/PPREstimation'/n) for n in manifest['frozen_engine_sha256']}
    check('all_three_pinned_engine_hashes',actual_hashes==manifest['frozen_engine_sha256'])
    protected={n:sha((RUN/n).resolve()) for n in manifest['protected_inputs_before']}
    check('all_protected_input_hashes_unchanged',protected==manifest['protected_inputs_before']==manifest['protected_inputs_after'])
    original = decode(read(OLD/'inputs/runtime_state_corrected.json'))
    restored = decode(read(RUN/'inputs/exact_restored_state.json'))
    off = decode(read(RUN/'inputs/control_off_state.json'))
    on = decode(read(RUN/'inputs/ee_floor_on_state.json'))
    check('exact_restore_all_historical_fields',all(same(v,restored[k]) for k,v in original.items()))
    check('off_preserves_all_original_fields_except_derived_balance_copy',all(same(v,off[k]) for k,v in original.items() if k!='balanced_model'))
    check('source_model_unchanged_on',same(original['_model'],on['_model']))
    check('no_extra_ecological_groups',on['n_groups']==off['n_groups']==26 and set(on['_groups_df'])==set(range(1,27)))
    source={int(g['group_seq']):g for g in read(MODEL/'model.json')['group']}
    check('source_EE_preserved',all(on['source_EE'][i]==float(g['ee']) for i,g in source.items()))
    check('missing_source_M0_preserved',all(float(g['other_mort'])==-9999 for g in source.values()) and all(math.isnan(v) for v in on['source_M0'].values()))
    fields=('_DC','_det_fate','catch','predation','immigration','emigration','net_migration','respiration','egestion','GE','GS','TL')
    check('unchanged_diet_fates_and_protected_flow_vectors',all(same(off[k],on[k]) for k in fields))
    living=list(range(1,25))
    check('living_production_consumption_BA_unchanged',all(same(off[k][i],on[k][i]) for k in ('p','q','growth') for i in living))
    check('living_B_PB_QB_unchanged',all(same(off['_groups_df'][i][c],on['_groups_df'][i][c]) for i in living for c in ('biomass','pb','qb')))
    check('before_floor_vectors_match_OFF',same(off['EE'],on['EE_before_floor']) and same(off['M0'],on['M0_before_floor']))
    affected=[i for i in on['EE'] if not same(off['EE'][i],on['EE'][i])]
    check('exactly_three_EE_changes',set(affected)=={22,23,24})
    ledger=[]
    for i in on['EE']:
        sink=on['external_mortality_export'][i]
        if i in affected:
            expected=off['M0'][i]-off['p'][i]*(1-.1)
            check(f'floor_arithmetic_group_{i}',on['EE'][i]==.1 and close(on['M0'][i],off['p'][i]*.9,1e-15) and close(sink,expected,1e-15) and sink>=0)
            ledger.append({'group_id':i,'name':on['_groups_df'][i]['group_name'],'P':off['p'][i],'EE_before':off['EE'][i],'EE_after':on['EE'][i],'M0_before':off['M0'][i],'M0_after':on['M0'][i],'external_sink':sink})
        else:
            check(f'unaffected_EE_M0_sink_group_{i}',same(off['EE'][i],on['EE'][i]) and same(off['M0'][i],on['M0'][i]) and sink==0)
    check('sink_total_000508',close(sum(on['external_mortality_export'].values()),.000508,1e-15))
    routed=sum(on['external_mortality_export'][i]*on['_det_fate'].get(i,{}).get(25,0) for i in on['external_mortality_export'])
    det={'inflow_before':off['p'][25],'inflow_after':on['p'][25],'residual_before':off['growth'][25],'residual_after':on['growth'][25],'routed_sink':routed}
    check('detritus_inflow_and_stock_residual_reduced_by_routed_sink',close(off['p'][25]-on['p'][25],routed) and close(off['growth'][25]-on['growth'][25],routed))
    check('no_new_detritus_import_or_external_food',same(off['net_migration'],on['net_migration']) and same(off['immigration'],on['immigration']) and same(off['_groups_df'][25]['detritus_import'],on['_groups_df'][25]['detritus_import']))
    residuals={i:on['p'][i]-sum(on[k][i] for k in ('catch','predation','growth','net_migration','M0','external_mortality_export')) for i in living}
    check('living_production_identity_includes_sink',all(abs(x)<1e-9 for x in residuals.values()))
    check('no_negative_detritus_residual',on['growth'][25]>=0)
    findings['floor_ledger']=ledger
    findings['detritus_accounting']=det
    findings['living_production_max_absolute_residual']=max(abs(x) for x in residuals.values())
    matrices={}; scope_values={}; matrix_parity={}
    for config in ('control_off','ee_floor_on'):
        scope_values[config]={}
        for method in ('GE','TE'):
            label=config+'_'+method
            result=decode(read(RUN/f'outputs/{label}.json'))
            S,A,L=(result[k] for k in ('SPPR','A','L'))
            check(label+'_axes',set(S)==set(A)==set(L)==set(range(1,27)) and all(set(r)=={1,25,26} for r in S.values()) and all(set(r)==set(range(1,27)) for M in (A,L) for r in M.values()))
            check(label+'_matrices_finite',all(math.isfinite(v) for M in (S,A,L) for row in M.values() for v in row.values()))
            check(label+'_no_negative_SPPR_or_A',all(v>=0 for M in (S,A) for row in M.values() for v in row.values()))
            check(label+'_L_equals_A_minus_I',all(close(L[i][j],A[i][j]-(i==j)) for i in A for j in A[i]))
            check(label+'_diagnostic_state_unchanged',same(result['runtime_before'],result['runtime_after']))
            check(label+'_runtime_matches_saved_config',all(same(v,(off if config=='control_off' else on)[k]) for k,v in result['runtime_before'].items()))
            scopes=decode(read(RUN/f'outputs/{label}_scopes.json'))
            scope_values[config][method]=scopes
            check(label+'_all_scopes_correct',all(close(scopes[scope][i],sum(S[i][j] for j in cols)) for scope,cols in {'PP':[1],'inner':[1,25],'all':[1,25,26]}.items() for i in S))
            d=result['diagnostic']
            check(label+'_strict_balances',d['model_input']['is_model_balanced'] and d['balance']['is_balanced'])
            check(label+'_convergence',d['divergence']['rho_living']<1 and d['divergence']['b']<1)
            matrices[label]={'status':d['status'],'rho_living':d['divergence']['rho_living'],'b':d['divergence']['b'],'SPPR_negative_count':sum(v<0 for row in S.values() for v in row.values()),'L_negative_count':sum(v<0 for row in L.values() for v in row.values()),'warnings':d['warnings'],'runtime_warnings':result['runtime_warnings']}
            if config=='control_off':
                historical=decode(read(OLD/f'outputs/corrected_{method}.json'))
                matrix_parity[method]={k:same(result[k],historical[k]) for k in ('SPPR','A','L')}
                check(label+'_historical_matrices_exact',all(matrix_parity[method].values()))
    findings['diagnostics']=matrices
    findings['same_engine_OFF_historical_matrix_parity']=matrix_parity
    audit=read(MODEL/'model_validation/evidence/source_review/taxon_audit.json')
    audit_by_taxon={r['taxon']:r for r in audit}
    check('384_unique_exact_mapping_labels',len(audit)==len(audit_by_taxon)==384)
    check('mapping_weights_normalized_where_resolved',all(not r['groups'] or close(sum(g['weight'] for g in r['groups']),1) for r in audit))
    ppr_totals={}
    unresolved=[r for r in audit if not r['groups']]
    for config in scope_values:
        saved=read(RUN/f'outputs/{config}_2019_ppr.json')
        outrows={r['taxon']:r for r in saved['rows']}
        check(config+'_mapping_and_catch_preserved',set(outrows)==set(audit_by_taxon) and all(outrows[t]['groups']==r['groups'] and outrows[t]['catch_tonnes']==r['catch_tonnes'] for t,r in audit_by_taxon.items()))
        ppr_totals[config]={}
        for method,scopes in scope_values[config].items():
            ppr_totals[config][method]={}
            for scope,coeffs in scopes.items():
                total=0.
                for t,r in audit_by_taxon.items():
                    actual=outrows[t]['methods'][method][scope]
                    if not r['groups']:
                        check(config+'_'+method+'_'+scope+'_'+t+'_missing_preserved',actual['sppr_wet'] is None and (actual['ppr_tC'] is None if r['catch_tonnes'] else actual['ppr_tC']==0))
                        continue
                    expected_coef=sum(g['weight']*coeffs[g['seq']] for g in r['groups'] if g['seq'] not in (22,23,24))
                    expected=r['catch_tonnes']*expected_coef/9
                    check(config+'_'+method+'_'+scope+'_'+t+'_arithmetic',close(actual['sppr_wet'],expected_coef) and close(actual['ppr_tC'],expected))
                    total+=expected
                check(config+'_'+method+'_'+scope+'_total_arithmetic',close(total,saved['totals_tC'][method][scope]))
                ppr_totals[config][method][scope]=total
        check(config+'_known_subtotal_label',saved['totals_are_known_subtotals'] is True)
        check(config+'_unresolved_catch',close(saved['unresolved_catch_tonnes'],sum(r['catch_tonnes'] for r in unresolved)))
    findings['PPR_2019_known_subtotals_tC']=ppr_totals
    findings['catch_basis']={'year':2019,'basis':'landings + discards','total_tonnes':sum(r['catch_tonnes'] for r in audit),'unresolved_taxa':len(unresolved),'unresolved_tonnes':sum(r['catch_tonnes'] for r in unresolved),'excluded_allocated_catch_tonnes':sum(r['catch_tonnes']*sum(g['weight'] for g in r['groups'] if g['seq'] in (22,23,24)) for r in audit)}
    # Inspect source text/AST only: no engine import or calculation.
    engine_ast=ast.parse((RUN/'code/PPREstimation/PPRCalculator.py').read_text(encoding='utf-8'))
    threshold_assignment=next(n for n in engine_ast.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEFAULT_DIAGNOSTIC_THRESHOLDS' for t in n.targets))
    threshold_defaults=ast.literal_eval(threshold_assignment.value)
    solver=next(n for n in ast.walk(engine_ast) if isinstance(n,ast.FunctionDef) and n.name=='SPPR_new')
    solver_defaults={arg.arg:ast.literal_eval(value) for arg,value in zip(solver.args.args[-len(solver.args.defaults):],solver.args.defaults)}
    ices_manifest=read(ICES/'results/diagnostics/2026-11-14_loader_repair/run_manifest.json')
    ices_answer=ices_manifest['answer']
    check('ICES_three_engine_hashes_identical',all(ices_answer['engine_hashes'][n]==h for n,h in actual_hashes.items()))
    method_comparison={}
    for name,method in [('new_GE','GE'),('new_TE_EEfix','TE')]:
        m=ices_answer['methods'][name]
        kwargs=m['settings']['kwargs']
        check('ICES_'+method+'_explicit_solver_options_match',all(kwargs[k]==v for k,v in manifest['method_options'].items()))
        check('ICES_'+method+'_DET_TE_vals_matches_Scotland_engine_default',kwargs['DET_TE_vals']==solver_defaults['DET_TE_vals']==1)
        check('ICES_'+method+'_diagnostic_thresholds_match_Scotland_engine_defaults',kwargs['thresholds']==threshold_defaults)
        check('ICES_'+method+'_full_diagnostic_mode_matches',kwargs['TE_option']==method and kwargs['short'] is False and kwargs['flat'] is False and kwargs['return_sppr'] is True)
        cfg=m['diagnostics']['config']
        check('ICES_'+method+'_same_floor_settings',cfg['use_ee_floor'] is True and cfg['ee_floor']==.1 and cfg['ee_threshold']==.1)
        method_comparison[method]={'all_explicit_common_solver_options_match':True,'DET_TE_vals':1,'diagnostic_thresholds_equal':True,'ICES_status':m['diagnostics']['status'],'ICES_b':m['diagnostics']['divergence']['b'],'Scotland_b':matrices['ee_floor_on_'+method]['b']}
    check('Scotland_has_no_internal_discard_return_matrix',on.get('_discard_returns') is None)
    findings['ICES_method_comparability']={'methods':method_comparison,'ICES_constructor':ices_answer['constructor'],'Scotland_initialization':manifest['constructor'],'structural_difference':'Scotland has one detritus pool and no explicit internal discard-return matrix in its audited state. ICES has three detritus pools and source-backed internal discard returns. The identical engine branches on _has_discard_returns: TE without returns reports b=0 and scales direct PP/Import inflow; TE with returns solves coupled recycling. Thus ICES TE b=0.1554967742366123 versus Scotland b=0 is structural, not an option mismatch.','source_locators':['code/PPREstimation/PPRCalculator.py:334-344 (_discard_return_matrix / _has_discard_returns)','code/PPREstimation/PPRCalculator.py:1639-1659 (TE b reporting)','code/PPREstimation/PPRCalculator.py:3185-3189 (TE internal-return branch)','ICES results/diagnostics/2026-11-14_loader_repair/run_manifest.json answer.methods.new_TE_EEfix.settings and diagnostics'],'inference_label':'The branch explanation follows verified identical engine source and saved state/diagnostic records.'}
    findings['environment']={'current':{'python':manifest['python'],'modules':manifest['modules']},'historical_engine_different_but_OFF_matrices_exact':True,'ICES_same_three_engine_hashes':True,'ICES_environment_comparison':'ICES saved run Python 3.13.9, numpy 2.4.6, pandas 2.3.3; source-engine identity is independent of runtime-environment identity.'}
    findings['limitations']=['The floor is an authorized hypothetical external mortality sink, not a source-parameter correction or signed researcher validation of the new scenario.','TE remains WARN for near-zero efficiencies of Seabirds, Seals and Cetaceans; finite matrices and strict balance do not remove that warning.','2019 totals are known subtotals: 12 unresolved labels remain, with positive catch. No missing contribution is asserted to be zero.','Scope includes GE and TE only; no With Egestion rerun or scientific/mapping/selection/workbook/report changes.','Negative L diagonal entries are expected in L=A-I and are not negative SPPR.']
    findings['limitations'].append('Identical engine/options do not harmonize source-specific initialization, model extent, group resolution, mapping assumptions or the distinct single-pool versus coupled-discard detritus representations.')
    output={'auditor':'independent artifact audit; no engine imports or execution','completed_utc':datetime.now(timezone.utc).isoformat(),'run_id':RUN.name,'status':'PASS','check_count':len(checks),'all_checks_pass':all(checks.values()),'engine_sha256':actual_hashes,'protected_inputs_checked':len(protected),'input_identifiers':{'historical_runtime_sha256':sha(OLD/'inputs/runtime_state_corrected.json'),'scotland_mapping_audit_sha256':sha(MODEL/'model_validation/evidence/source_review/taxon_audit.json')},'findings':findings,'checks':checks}
    path=RUN/'qa/independent_ee_floor_review.json'
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k!='checks'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
