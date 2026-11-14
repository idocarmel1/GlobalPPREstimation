"""Independent artifact/arithmetic QA only; no engine imports or execution."""
from pathlib import Path
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import sys

RUN=Path(__file__).resolve().parents[1]
MODEL=RUN.parents[2]
OLD=MODEL/'results/diagnostics/2026-11-14_loader_repair'
DET={67:'DetritusDOMWaterColumn',68:'DetritusPOMSediment',69:'Discards'}
CHECKS={}

def read(p):
    raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def check(label,condition):
    CHECKS[label]=bool(condition)
    assert condition,label

def close(a,b):
    return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10)

def decode(v):
    if isinstance(v,list): return [decode(x) for x in v]
    if not isinstance(v,dict): return v
    kind=v.get('type','').lower()
    if kind=='float': return float(v['value'])
    if kind in ('mapping','dict'): return {decode(k):decode(x) for k,x in v['items']}
    if kind=='series':
        if 'frame' in v:
            return {i:next(iter(row.values())) for i,row in decode(v['frame']).items()}
        return dict(zip(decode(v['index']),decode(v['values'])))
    if kind=='dataframe':
        rows=v.get('data',v.get('values'))
        out={}
        for ri,(i,row) in enumerate(zip(v['index'],rows)):
            out[i]={}
            for ci,(c,x) in enumerate(zip(v['columns'],row)):
                masks=v.get('masks',{})
                if masks.get('nan',[[False]*len(row)]*len(rows))[ri][ci]: x=float('nan')
                elif masks.get('positive_infinity',[[False]*len(row)]*len(rows))[ri][ci]: x=float('inf')
                elif masks.get('negative_infinity',[[False]*len(row)]*len(rows))[ri][ci]: x=-float('inf')
                out[i][c]=decode(x)
        return out
    if kind in ('tuple','ndarray'): return decode(v.get('items',v.get('values',v.get('data'))))
    if kind in ('modeldata','pprcalculator'): return decode(v['attributes'])
    return {k:decode(x) for k,x in v.items()}

def same(a,b):
    if isinstance(a,dict): return isinstance(b,dict) and a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list): return isinstance(b,list) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if isinstance(a,float) and math.isnan(a): return isinstance(b,float) and math.isnan(b)
    return a==b

def same_scientific(a,b):
    """Allow only the observed missing taxon-description null-to-NaN coercion."""
    if isinstance(a,dict):
        if not isinstance(b,dict) or a.keys()!=b.keys(): return False
        return all((k=='taxon_descr' and a[k] is None and isinstance(b[k],float) and math.isnan(b[k])) or same_scientific(a[k],b[k]) for k in a)
    if isinstance(a,list):
        return isinstance(b,list) and len(a)==len(b) and all(same_scientific(x,y) for x,y in zip(a,b))
    return same(a,b)

def matrix_close(a,b):
    return a.keys()==b.keys() and all(a[i].keys()==b[i].keys() and all(close(a[i][j],b[i][j]) for j in a[i]) for i in a)

def main():
    manifest=read(RUN/'run_manifest.json')
    prior_manifest=read(OLD/'run_manifest.json')
    answer=prior_manifest['answer']
    hashes={n:sha(RUN/'code/PPREstimation'/n) for n in ('PPRCalculator.py','ModelData.py','utils.py')}
    check('same_three_engine_files_as_saved_ICES',all(h==answer['engine_hashes'][n] for n,h in hashes.items()))
    check('same_pinned_commit',manifest.get('engine_commit',manifest.get('frozen_engine_commit',manifest.get('code_commit')))=='38cb75d066c5f78d47ba20fc6ab8545a9a6d5c69')
    check('run_complete',manifest.get('complete') is True)
    protected=manifest.get('protected_inputs_before',{})
    check('protected_input_inventory_present',bool(protected))
    check('protected_inputs_unchanged',all(sha((RUN/p).resolve())==h for p,h in protected.items()))
    baseline={method:decode(read(OLD/f'{name}.json.gz')) for method,name in [('GE','new_GE'),('TE','new_TE_EEfix')]}
    original=baseline['GE']['runtime_before']
    check('same_baseline_runtime_between_methods',same(original,baseline['TE']['runtime_before']))
    check('floor_ON_01_retained',original['use_ee_floor'] is True and original['ee_floor']==.1)
    check('all_three_detritus_identities',all(original['_groups_df'][i]['group_name']==name for i,name in DET.items()))
    check('source_discard_return_matrix_present',any(x>0 for row in original['_discard_returns'].values() for x in row.values()))
    mapping_path=MODEL/'model_validation/evidence/mapping/mapping_decisions.json'
    mapping=read(mapping_path)
    mapping_rows=mapping['rows']
    check('all_384_exact_labels_resolved',len(mapping_rows)==384 and len({r['taxon'] for r in mapping_rows})==384 and all(r['groups'] for r in mapping_rows))
    full={}
    for p in (RUN/'outputs').glob('*.json'):
        raw=read(p)
        if isinstance(raw,dict) and all(k in raw for k in ('SPPR','A','L','diagnostic')):
            result=decode(raw)
            method=result['method']
            mode=result.get('options',result.get('diagnostic',{}).get('config',{})).get('det_collapse_mode')
            full[(mode,method)]=(p,raw,result)
    check('two_pooled_methods_present',all(('always',m) in full for m in ('GE','TE')))
    findings={}
    ppr={}
    for (mode,method),(p,raw,result) in full.items():
        label=mode+'_'+method
        old=baseline[method]
        S,A,L=(result[k] for k in ('SPPR','A','L'))
        before=result['runtime_before']
        after=result['runtime_after']
        check(label+'_all_archived_values_and_missingness_preserved',all(k in before and same_scientific(v,before[k]) for k,v in original.items()))
        check(label+'_all_scientific_state_preserved_after',all(k in after and same_scientific(v,after[k]) for k,v in original.items()))
        check(label+'_pre_and_post_state_exact',same(before,after))
        check(label+'_group_identities_preserved',set(S)==set(old['source_matrix']) and set(next(iter(S.values())))==set(next(iter(old['source_matrix'].values()))))
        check(label+'_A_and_L_unchanged',matrix_close(A,old['return'][2]) and matrix_close(L,old['return'][3]))
        check(label+'_PP_and_Import_columns_unchanged',all(close(S[i][j],old['source_matrix'][i][j]) for i in S for j in S[i] if j not in DET))
        finite={key:all(isinstance(v,(int,float)) and math.isfinite(v) for row in result[key].values() for v in row.values()) for key in ('SPPR','A','L')}
        negative={key:sum(v<-1e-10 for row in result[key].values() for v in row.values()) for key in ('SPPR','A','L')}
        check(label+'_all_matrices_finite',all(finite.values()))
        check(label+'_SPPR_nonnegative',negative['SPPR']==0)
        check(label+'_L_equals_A_minus_I',all(close(L[i][j],A[i][j]-(i==j)) for i in A for j in A[i]))
        mask_counts={}
        for name in ('SPPR','A','L'):
            masks=raw[name].get('masks',{})
            mask_counts[name]={kind:sum(bool(x) for row in cells for x in row) for kind,cells in masks.items()}
        check(label+'_matrix_masks_finite',all(count==0 for item in mask_counts.values() for kind,count in item.items() if kind in ('nan','positive_infinity','negative_infinity','null')))
        diag=result['diagnostic']
        check(label+'_floor_and_forcing_options_retained',all(diag['config'][k]==v for k,v in {'use_ee_floor':True,'ee_floor':.1,'det_collapse_mode':mode,'det_open_mode':'none','det_theta':1,'det_external_sppr':0}.items()))
        check(label+'_threshold_in_preserved_floor_ledger',diag['config']['ee_floor_assumption']['ee_threshold']==original['ee_floor_info']['ee_threshold']==.1)
        expected_settings=dict(old['settings']['kwargs'],det_collapse_mode=mode)
        check(label+'_only_pool_setting_differs',result['settings']==expected_settings)
        detail={'status':diag['status'],'strict_model_balanced':diag['model_input']['is_model_balanced'],'strict_sppr_balanced':diag['balance']['is_balanced'],'reported_original_coupled_b':diag['divergence']['b'],'rho_living':diag['divergence']['rho_living'],'warnings':diag['warnings'],'matrix_finite':finite,'negative_counts':negative,'matrix_mask_counts':mask_counts,'diagnostic_header_omissions':{'ee_threshold':diag['config'].get('ee_threshold'),'model':diag['config'].get('model')},'threshold_evidence':'Preserved ee_floor_assumption and archived floor ledger specify 0.1; no floor operation is rerun.'}
        if mode=='always':
            baseS=old['source_matrix']
            raw_basis={i:sum(baseS[i][d]/baseS[d][d] for d in DET) for i in baseS}
            non_det={i:sum(v for j,v in row.items() if j not in DET) for i,row in baseS.items()}
            q_combined=sum(original['q'][d] for d in DET if original['q'][d]>0)
            basal=[i for i,row in original['_groups_df'].items() if row['trophic_info'] in ('PP','Import')]
            fate={i:min(1.,max(0.,sum(original['_det_fate'].get(i,{}).get(d,0.) for d in DET))) for i in original['M0']}
            returns={i:sum(original['_discard_returns'].get(i,{}).get(d,0.) for d in DET) for i in original['M0']}
            m={i:((original['M0'][i] if method=='GE' or i in basal else 0.)*fate[i]+returns[i])/q_combined for i in original['M0']}
            a=sum(m[i]*non_det[i] for i in m)
            b=sum(m[i]*raw_basis[i] for i in m)
            scalar=a/(1-b)
            check(label+'_all_three_share_independent_scalar',all(close(S[d][d],scalar) for d in DET))
            check(label+'_each_detritus_column_matches_independent_pool_arithmetic',all(close(S[i][d],baseS[i][d]/baseS[d][d]*scalar) for i in S for d in DET))
            check(label+'_pooled_loop_converges',b<1)
            info=result.get('detritus_resolution_info',after.get('detritus_resolution_info'))
            check(label+'_full_pool_resolution_info_retained',isinstance(info,dict))
            check(label+'_all_three_pools_recorded',set(info['det_seq'])==set(DET))
            check(label+'_recorded_pool_coefficients_match',close(info['collapse_a'],a) and close(info['collapse_b'],b) and close(info['collapse_scalar'],scalar))
            detail['independent_pool_arithmetic']={'q_combined':q_combined,'internal_discard_returns_total':sum(returns.values()),'a':a,'b':b,'scalar':scalar,'detritus_ids':list(DET),'pool_info':info}
        else:
            check(label+'_saved_unpooled_SPPR_parity',matrix_close(S,old['source_matrix']))
            check(label+'_saved_model_balance_flag_parity',diag['model_input']['is_model_balanced']==old['diagnostics']['model_input']['is_model_balanced'])
            check(label+'_saved_SPPR_balance_flag_parity',diag['balance']['is_balanced']==old['diagnostics']['balance']['is_balanced'])
            detail['retained_original_strict_model_balance']=old['diagnostics']['model_input']['is_model_balanced']
            detail['retained_original_strict_SPPR_balance']=old['diagnostics']['balance']['is_balanced']
        scopes={'PP':{i:sum(v for j,v in row.items() if j not in DET and original['_groups_df'][j]['trophic_info']!='Import') for i,row in S.items()},'inner':{i:sum(v for j,v in row.items() if original['_groups_df'][j]['trophic_info']!='Import') for i,row in S.items()},'all':{i:sum(row.values()) for i,row in S.items()}}
        ppr[label]={scope:sum(r['catch_tonnes']*sum(g['weight']*values[g['group_id']] for g in r['groups'])/9 for r in mapping_rows) for scope,values in scopes.items()}
        saved_ppr=read(RUN/f"outputs/{result['configuration']}_2019_ppr.json")
        check(label+'_saved_2019_PPR_totals_match',all(close(total,saved_ppr['totals_tC'][method][scope]) for scope,total in ppr[label].items()))
        saved_rows={r['taxon']:r for r in saved_ppr['rows']}
        check(label+'_all_mapping_rows_and_catch_unchanged',len(saved_rows)==384 and all(saved_rows[r['taxon']]['groups']==r['groups'] and saved_rows[r['taxon']]['catch_tonnes']==r['catch_tonnes'] for r in mapping_rows))
        check(label+'_all_taxon_PPR_arithmetic',all(close(saved_rows[r['taxon']]['methods'][method][scope]['sppr_wet'],sum(g['weight']*values[g['group_id']] for g in r['groups'])) and close(saved_rows[r['taxon']]['methods'][method][scope]['ppr_tC'],r['catch_tonnes']*sum(g['weight']*values[g['group_id']] for g in r['groups'])/9) for r in mapping_rows for scope,values in scopes.items()))
        findings[label]=detail
    output={'status':'PASS','audit_role':'Independent saved-artifact QA; no engine imports or execution','completed_utc':datetime.now(timezone.utc).isoformat(),'run_id':RUN.name,'check_count':len(CHECKS),'checks':CHECKS,'engine_sha256':hashes,'protected_input_count':len(protected),'mapping_decisions_sha256':sha(mapping_path),'independently_recomputed_2019_PPR_tC':ppr,'diagnostics_and_pool_arithmetic':findings,'restoration_representation_note':'The 69 missing taxon_descr values are NaN rather than archived null in _groups_df, _source_groups_before_completion and _ee_floor_base._groups_df (207 metadata cells). Missingness is preserved. Only this named metadata-column conversion is permitted by the audit; every numerical value, other missing value, diet/fate/discard cell and group identity must compare exactly. Before/after each diagnostic compare exactly, including this representation.','interpretation':['Forced pooling retains all group identities and diet cells while replacing three distinct detritus scaling factors with one common scalar; it is a calculation sensitivity, not a merged source model.','Pooled arithmetic sums inflows, fate-to-modelled shares and internal discard-return amounts across DOM 67 / POM 68 / Discards 69. Destination-specific return scaling is removed; the original routing matrix and total internal return remain intact.','Reported diagnostic b is the original coupled rho_B. The separate independently verified pooled b is collapse_b.','Audit PASS establishes faithful reproducibility and preservation; scientific diagnostic statuses and strict balance flags above retain their independent meanings.','No canonical/source/mapping/workbook/selection/researcher-review changes and no independent engine calls were made by this audit.']}
    out=RUN/'qa/independent_pooled_review.json'
    out.write_text(json.dumps(output,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k!='checks'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
