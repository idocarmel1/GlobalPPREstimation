"""Independent result checks across every solved scenario, without rerunning engines."""
from pathlib import Path
from collections import Counter
import json,hashlib
import numpy as np
import pandas as pd
from baseline import ROOT,FRACTIONS,METHODS,SCOPES

def verify():
    failures=[];count=Counter();maxima=Counter()
    def check(condition,name,detail=''):
        count[name]+=1
        if not condition:failures.append(dict(check=name,detail=detail))
    manifest=json.loads((ROOT/'input_manifest.json').read_text(encoding='utf-8'))
    for f in manifest['files']:
        p=ROOT/f['snapshot_path'];check(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],'immutable_snapshot_hash',f['snapshot_path'])
    for manifest_path in ROOT.glob('workbook_input_manifest*.json'):
        workbook_manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        for f in workbook_manifest['files']:
            p=ROOT/f['snapshot_path'];check(hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],'immutable_workbook_hash',f['snapshot_path'])
    for p in (ROOT/'src/experimental_engine').glob('*.py'):
        check(p.read_bytes()==(ROOT/'inputs/frozen_engine'/p.name).read_bytes(),'unchanged_engine',p.name)
    selected=json.loads((ROOT/'results/selected_models.json').read_text(encoding='utf-8'))
    check(len(selected)==20,'exact_twenty_additions');check(len(set(r['ecological_sha256'] for r in selected))==20,'distinct_ecological_inputs')
    for s in selected:
        p=s['screening']['physical'];check(s['status']=='eligible' and s['screening']['native_harvest']>0 and p['ledger_closes'] and not p['negative_physical_flows'],'selected_eligibility',s['model_id'])
        check(s['screening']['inferred_living_accumulation_max_relative']<=1e-4,'no_material_invented_living_accumulation',s['model_id'])
        fate=s['screening']['detritus_source_checks']
        check(not fate['nonzero_fate_overwritten'] and not fate['negative_inferred_detritus_accumulation_groups'],'source_faithful_detritus_baseline',s['model_id'])
    nmodels=0;totalrecords=0;totalgroups=0
    for path in sorted((ROOT/'results/models').glob('*/study.validated.json')):
        study=json.loads(path.read_text(encoding='utf-8'));meta=study['models'][0];mid=meta['model_id'];nmodels+=1
        rr=study['records'];gg=study['groups'];totalrecords+=len(rr);totalgroups+=sum(map(len,gg.values()))
        check(study['fraction_grid']==FRACTIONS and len(rr)==2616,'complete_dense_grid',mid)
        rows={(r['method'],r['scope'],r['route'],r['fraction']):r for r in rr}
        def coefficients(r):return np.array([g['sppr'] if g['sppr'] is not None else np.nan for g in gg.get(r['scenario_id'],[])],float)
        def same(a,b):return a.shape==b.shape and np.allclose(a,b,rtol=2e-7,atol=1e-7,equal_nan=True)
        for r in rr:
            sid=r['scenario_id'];count['records_checked']+=1
            if not r['valid']:
                check(r['ppr_fixed_H_tC'] is None and r['ppr_retained_L_tC'] is None,'invalid_is_null',sid)
            else:
                d=r['diagnostics'];check(d['ledger_closes'] and not d['negative_physical_flows'],'valid_physical_ledger',sid)
                check(not d.get('nonfinite_cells') and not d.get('negative_source_cells') and all(d.get(k) is None or d[k]<1 for k in ['rho_living','rho_detritus']),'valid_finite_convergent_nonnegative',sid)
                g=gg[sid];fixed=sum(x['sppr']*x['H']/9 for x in g if x['H']>0)
                check(np.isclose(fixed,r['ppr_fixed_H_tC'],rtol=1e-12,atol=1e-9),'independent_fixed_support_total',sid)
                check(np.isclose(r['ppr_retained_L_tC'],(1-r['fraction'])*r['ppr_fixed_H_tC'],rtol=1e-12,atol=1e-9),'landings_identity',sid)
            d=r['decomposition']
            if d['residual'] is not None:
                maxima['decomposition_absolute_residual']=max(maxima['decomposition_absolute_residual'],abs(d['residual']))
                check(abs(d['residual'])<=1e-8*max(1,abs(d['total_change'])),'decomposition_reconciles',sid)
            if r['scope']=='all' and meta['native_import_production_tC']>0:
                check(r['ppr_to_native_pp_pct'] is None and r['ppr_retained_to_native_pp_pct'] is None,'import_boundary_guard',sid)
            if meta['cohort']=='additional' and r['route']=='SR':check(not r['valid'],'no_invented_discard_destination',sid)
            if r['method']=='SPPR_1986' and r['fraction']==1 and r['route'] in ['SM','SE']:
                check(not r['valid'],'zero_catch_1986_undefined',sid)
        for method in METHODS:
            for scope in SCOPES:
                base=rows[method,scope,'S0',0.]
                for route in ['SC','SM','SE']:
                    z=rows[method,scope,route,0.]
                    check(same(coefficients(base),coefficients(z)) and base['valid']==z['valid'],'zero_fraction_identity',z['scenario_id'])
                for f in FRACTIONS:
                    sc=rows[method,scope,'SC',f];se=rows[method,scope,'SE',f]
                    check(same(coefficients(sc),coefficients(base)) and sc['valid']==base['valid'],'SC_invariance',sc['scenario_id'])
                    if f<1:check(same(coefficients(sc),coefficients(se)) and sc['valid']==se['valid'],'SC_SE_equivalence_below_endpoint',se['scenario_id'])
        ledger=pd.read_csv(path.parent/'flow_ledger.csv');baseline=ledger[ledger.route=='S0'].set_index('group_id')
        living=[g['group_id'] for g in next(iter(gg.values())) if g['trophic_info'] in ['PP','Regular']]
        for (route,f),frame in ledger.groupby(['route','fraction']):
            a=frame.set_index('group_id').reindex(baseline.index);h=baseline.harvest
            check(np.allclose(a.designated_discard,f*h,rtol=1e-12,atol=1e-10) and np.allclose(a.retained,(1-f)*h,rtol=1e-12,atol=1e-10),'exact_designated_amount',f'{mid}|{route}|{f}')
            check(np.allclose(a.production_residual.loc[living],baseline.production_residual.loc[living],rtol=1e-6,atol=1e-9),'living_budget_residual_preserved',f'{mid}|{route}|{f}')
            if route=='SM':
                check(np.allclose(a.mortality,baseline.mortality+f*h,rtol=1e-12,atol=1e-9),'SM_adds_discard_once',f'{mid}|{f}')
                expected=baseline.ee.loc[living]-f*h.loc[living]/baseline.production.loc[living]
                check(np.allclose(a.ee.loc[living],expected,rtol=1e-10,atol=1e-10,equal_nan=True),'SM_EE_adjustment_preserved',f'{mid}|{f}')
                check(np.allclose(a.explicit_discard_return,0),'no_double_counted_SM_return',f'{mid}|{f}')
            if route=='SE':
                check(np.allclose(a.external_loss,f*h) and np.allclose(a.migration,baseline.migration),'SE_distinct_sink_no_migration',f'{mid}|{f}')
        for c in study['baseline_checks']:
            if c.get('provenance')=='existing_saved_workbook' and c.get('passed') is True:
                check(c['finite_mask_matches'],'saved_finite_support_matches',c)
            if c.get('passed') is False and c.get('provenance')=='existing_saved_workbook':
                check(c.get('configuration_difference_verified',False),'saved_configuration_difference_reproduced',c)
            elif c.get('passed') is not None:check(c['passed'],'baseline_comparison',c)
        print('VERIFIED',mid,flush=True)
    check(nmodels==24,'twenty_plus_four_models');check(totalrecords==62784,'expected_scenario_count')
    overlap=json.loads((ROOT/'verification/original_overlap.json').read_text(encoding='utf-8'))
    check(overlap['n_compared']==3936 and overlap['passed'],'original_overlap_matches',dict(n=overlap['n_compared'],failed=[x for x in overlap['checks'] if not all(x[k] for k in ['coefficients_match','valid_mask_match','ppr_match'])][:15]))
    result=dict(passed=not failures,check_counts=dict(count),maxima=dict(maxima),failures=failures,scenario_records=totalrecords,group_rows=totalgroups)
    (ROOT/'verification/output_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PASS' if not failures else 'FAIL',sum(count.values()),'checks;',len(failures),'failures')
    if failures:raise SystemExit(1)
if __name__=='__main__':verify()
