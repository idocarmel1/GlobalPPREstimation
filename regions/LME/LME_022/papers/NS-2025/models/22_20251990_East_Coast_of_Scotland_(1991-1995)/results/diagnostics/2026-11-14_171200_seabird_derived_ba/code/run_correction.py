"""Authorized model-local seabird correction; no canonical or workbook adoption.

Restore exact historical state; change one consumer diet; refresh prey predation;
recompute only affected, provenance-proven loader-derived BA. Never call a loader,
constructor or broad balancing routine. Reuse verified baseline full returns.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import importlib.metadata
import importlib.util
import inspect
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
import traceback
import warnings
from datetime import datetime, timezone, timedelta

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
MODEL = SCRIPT.parents[4]
BASE = MODEL / 'results/diagnostics/2026-11-14_163501_seabird_self_loop'
LEDGER = MODEL / 'extracted_tables/evidence/LOADER_TRANSFORMATIONS.csv'
VARIANT = 'seabird_no_self_loop_proportional_prey_derived_ba'
spec = importlib.util.spec_from_file_location('historical_reproduction', BASE / 'code/check_self_loop.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.initialize_imports()
np, pd = h.np, h.pd

# Extend the existing lossless serializer to retain all calculator attributes,
# including the archived unused balanced_model object and embedded ModelData.
original_encode = h.encode
def encode(value):
    if isinstance(value, (h.PPRCalculator, h.ModelData)):
        return {'type': type(value).__name__, 'attributes': encode(value.__dict__)}
    return original_encode(value)
h.encode = encode

def relative(path):
    return os.path.relpath(path, RUN).replace('\\', '/')

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def save(path, data):
    h.save(path, data)

def decode(value):
    if isinstance(value, list):
        return [decode(x) for x in value]
    if not isinstance(value, dict):
        return value
    kind = value.get('type')
    if kind == 'float': return float(value['value'])
    if kind == 'dict': return {decode(k):decode(v) for k,v in value['items']}
    if kind == 'Series': return pd.Series(decode(value['values']), index=decode(value['index']), name=decode(value['name']))
    if kind == 'DataFrame': return pd.DataFrame(decode(value['values']), index=decode(value['index']), columns=decode(value['columns']))
    if kind == 'ndarray': return np.array(decode(value['values']), dtype=value['dtype'])
    if kind == 'tuple': return tuple(decode(x) for x in value['items'])
    if kind in ('PPRCalculator','ModelData'):
        obj = {'PPRCalculator':h.PPRCalculator,'ModelData':h.ModelData}[kind].__new__({'PPRCalculator':h.PPRCalculator,'ModelData':h.ModelData}[kind])
        obj.__dict__.update(decode(value['attributes']))
        return obj
    return {k:decode(v) for k,v in value.items()}

def verify_baseline():
    index = read(BASE/'evidence_index.json')
    checks = []
    for artifact in index['artifacts']:
        if artifact['availability'] != 'present':
            continue
        path = (BASE/artifact['path']).resolve()
        actual = h.sha(path)
        assert actual == artifact['sha256'], path
        checks.append({'path':relative(path),'sha256':actual})
    assert read(BASE/'qa/completeness.json')['complete']
    return checks

def correct():
    baseline, _ = h.make_scenario('baseline')
    calc, intervention = h.make_scenario('remove_redistribute')
    original = h.runtime(baseline)
    source_groups = {int(g['group_seq']):g for g in read(MODEL/'model.json')['group']}
    rows = list(csv.DictReader(LEDGER.open(encoding='utf-8-sig', newline='')))
    ba_rows = {int(r['seq']):(n+2,r) for n,r in enumerate(rows) if r['field']=='biomass_accum'}
    affected = [int(i) for i in calc.predation.index if calc.predation[i] != baseline.predation[i]]
    provenance, changes, gaps = [], [], []
    for i in calc.growth.index:
        src = source_groups.get(int(i))
        evidence = ba_rows.get(int(i))
        match = bool(evidence and math.isclose(float(evidence[1]['loaded_value']), float(baseline.growth[i]), rel_tol=1e-12, abs_tol=1e-12))
        source_missing = bool(src and str(src.get('biomass_accum')) == '-9999')
        derived = bool(evidence and 'loader-derived' in evidence[1]['authority'])
        eligible = int(i) in affected and match and source_missing and derived
        entry = dict(group_id=int(i), group_name=calc.seq2name[i], affected=int(i) in affected,
                     source_ba=src.get('biomass_accum') if src else None,
                     archived_ba=float(baseline.growth[i]), ledger_line=evidence[0] if evidence else None,
                     ledger_value=float(evidence[1]['loaded_value']) if evidence else None,
                     source_missing=source_missing, ledger_matches_archived=match,
                     documented_loader_derived=derived, recomputation_eligible=eligible)
        provenance.append(entry)
        if eligible:
            after = calc.p[i]-calc.M0[i]-calc.catch[i]-calc.predation[i]-calc.net_migration[i]
            calc.growth[i] = after
            calc._groups_df.loc[i,'biomass_accum'] = after
            changes.append(dict(group_id=int(i), group_name=calc.seq2name[i], before=float(baseline.growth[i]),
                after=float(after), difference=float(after-baseline.growth[i]),
                p=float(calc.p[i]), M0=float(calc.M0[i]), catch=float(calc.catch[i]),
                predation_before=float(baseline.predation[i]), predation_after=float(calc.predation[i]),
                net_migration=float(calc.net_migration[i]), provenance_ledger_line=evidence[0],
                equation='BA = P - M0 - catch - predation - net_migration', units='t wet weight km^-2 year^-1'))
        elif int(i) in affected:
            gaps.append(dict(group_id=int(i),reason='Observed/manual/uncertain or ledger mismatch: preserved BA'))
    # All unchanged fields, including observed/manual/unknown inputs, are exact.
    for key in h.FIELDS:
        if key not in ('_DC','_groups_df','predation','growth'):
            assert h.digest_value(original[key]) == h.digest_value(getattr(calc,key)), key
    assert h.digest_value(baseline._DC.drop(index=22)) == h.digest_value(calc._DC.drop(index=22))
    assert h.digest_value(baseline._groups_df.drop(columns=['predation','biomass_accum'])) == h.digest_value(calc._groups_df.drop(columns=['predation','biomass_accum']))
    assert calc.n_groups == baseline.n_groups == 26
    assert set(calc._groups_df.index) == set(baseline._groups_df.index)
    untouched = [i for i in calc.growth.index if i not in affected]
    pd.testing.assert_series_equal(calc.growth.loc[untouched], baseline.growth.loc[untouched], check_exact=True)
    assert abs(calc._DC.loc[22].sum()-1) < 1e-15
    assert calc._DC.loc[22,22] == 0
    # Validate detritus independently. Diet correction leaves its routed input,
    # mortality, egestion and external export unchanged; only removal and BA vary.
    detritus = []
    for i in calc.get_DET_seq():
        inflow = float(((calc.M0+calc.egestion)*calc._det_fate[i].reindex(calc.p.index).fillna(0)).sum())
        assert math.isclose(inflow, float(calc.p[i]), rel_tol=1e-12, abs_tol=1e-12)
        detritus.append(dict(group_id=int(i),name=calc.seq2name[i],routed_input=inflow,
            retained_p=float(calc.p[i]),retained_q=float(calc.q[i]),catch=float(calc.catch[i]),
            M0=float(calc.M0[i]),predation=float(calc.predation[i]),BA=float(calc.growth[i]),
            net_migration=float(calc.net_migration[i]),det_export=float(calc.det_export[i]),
            residual=float(calc.p[i]-calc.M0[i]-calc.catch[i]-calc.predation[i]-calc.growth[i]-calc.net_migration[i])))
    calc.is_balanced = calc.is_model_balanced()[0]
    source_diet = {int(d['prey_seq']):float(d['proportion']) for d in source_groups[22]['diet_descr']['diet']}
    for cell in intervention['changed_diet_cells']:
        cell['publication_cell'] = f"Table S3!W{cell['prey_id']+2}"
        cell['canonical_source_value'] = source_diet.get(cell['prey_id'],0.0)
    intervention.update(variant_id=VARIANT, scenario='corrected_derived_ba',
        source_seabird_self_diet=source_diet[22], ba_provenance=provenance, ba_changes=changes,
        ba_preservation_gaps=gaps, affected_predation_groups=affected, detritus_accounting=detritus,
        exact_unchanged_consumer_diets=True, all_groups_retained=True,
        protected_fields_unchanged_except_explicit_diet_predation_and_eligible_ba=True,
        archived_state_fields=original, corrected_state_fields=h.runtime(calc),
        protocol='Exact __new__ archive restore; remove seabird self-loop; proportional redistribution including detritus; recompute all prey predation; recompute affected provenance-proven loader BA only; no constructor, broad balance routine, EE floor, canonical edit or adoption.')
    return baseline,calc,intervention

def matrix_checks(path):
    raw=read(path); d=decode(raw); S,A,L=d['SPPR'],d['A'],d['L']
    for name,mat in [('SPPR',S),('A',A),('L',L)]:
        assert mat.index.is_unique and mat.columns.is_unique
        assert list(mat.shape)==raw[name]['shape']
        assert np.isfinite(mat.to_numpy(dtype=float)).all()
        for kind,mask in raw[name]['masks'].items():
            assert np.asarray(mask).shape==mat.shape
            assert not np.any(mask), (name,kind)
        expected={(int(mat.index[i]),int(mat.columns[j])):float(mat.iloc[i,j]) for i,j in np.argwhere(mat.to_numpy() < -1e-10)}
        actual={(x['row_id'],x['column_id']):x['value'] for x in d['negative_entries'] if x['matrix']==name}
        assert expected==actual
    assert set(S.index)==set(range(1,27)) and set(S.columns)=={1,25,26}
    A=A.loc[S.index,S.index]; L=L.loc[S.index,S.index]
    assert np.allclose(L.values,A.values-np.eye(26),rtol=0,atol=2e-15)
    max_scaled=float(np.max(np.abs(L.values@S.values)/(1+np.abs(S.values))))
    assert max_scaled < 1e-12
    living=[i for i in A.index if i not in (1,25,26)]
    rho=float(max(abs(np.linalg.eigvals(A.loc[living,living]))))
    assert math.isclose(rho,d['diagnostic']['divergence']['rho_living'],rel_tol=1e-12,abs_tol=1e-12)
    assert A.loc[22,22] == 0.0
    scopes={'PP':S[[1]].sum(axis=1),'inner':S[[1,25]].sum(axis=1),'all':S.sum(axis=1)}
    saved=decode(read(path.with_name(path.stem+'_scopes.json')))
    for scope,value in scopes.items(): pd.testing.assert_series_equal(value,saved[scope],check_exact=True)
    assert d['scientific_state_unchanged_by_diagnostic']
    return dict(method=d['method'],axes_masks_equations_verified=True,rho=rho,
                maximum_scaled_equation_residual=max_scaled,all_26_groups_retained=True,
                seabird_A_self=0.0,negative_entries_reconciled=True,
                nonfinite_matrix_entries=0,scopes_reconciled=True)

def main():
    started=datetime.now(timezone.utc).isoformat()
    for folder in ('inputs','outputs','qa'): (RUN/folder).mkdir(parents=True,exist_ok=True)
    protected=h.verify_inputs()
    protected[relative(LEDGER)] = h.sha(LEDGER)
    baseline_verified=verify_baseline()
    baseline,calc,intervention=correct()
    save(RUN/'inputs/intervention.json',intervention)
    save(RUN/'inputs/runtime_state_before.json',baseline.__dict__)
    save(RUN/'inputs/runtime_state_corrected.json',calc.__dict__)
    # Verify persisted runtime can be restored without defaults and is exact.
    reopened=h.PPRCalculator.__new__(h.PPRCalculator)
    reopened.__dict__.update(decode(read(RUN/'inputs/runtime_state_corrected.json')))
    assert h.digest_value(h.runtime(reopened)) == h.digest_value(h.runtime(calc))
    save(RUN/'qa/baseline_evidence_verification.json',dict(verified_artifact_count=len(baseline_verified),artifacts=baseline_verified,
        reused_baseline_methods=list(h.METHODS),fresh_baseline_execution=False,
        note='Full returns and original-source-matrix reconciliation from the prior actual nine-run experiment reused only after hash verification. Old result manifest unknown historical execution remains unchanged.'))
    comparisons=[]; checks=[]; failures=[]
    for method in h.METHODS:
        stem='corrected_'+method.replace(' ','_')
        work=h.PPRCalculator.__new__(h.PPRCalculator)
        work.__dict__.update(decode(read(RUN/'inputs/runtime_state_corrected.json')))
        before=copy.deepcopy(work.__dict__)
        start=time.perf_counter()
        try:
            with warnings.catch_warnings(record=True) as observed:
                warnings.simplefilter('always')
                report,S,A,L=work.diagnose_sppr(TE_option=method,short=False,flat=False,return_sppr=True,**h.OPTIONS)
            elapsed=time.perf_counter()-start
            unchanged=h.digest_value(h.runtime(work)) == h.digest_value(h.runtime(calc))
            assert unchanged
            negative=[]
            for name,mat in [('SPPR',S),('A',A),('L',L)]:
                for i in mat.index:
                    for j in mat.columns:
                        if float(mat.loc[i,j]) < -1e-10:
                            negative.append(dict(method=method,matrix=name,row_id=int(i),row_name=work.seq2name[i],
                                column_id=int(j),column_name=work.seq2name[j],value=float(mat.loc[i,j]),tolerance=1e-10))
            save(RUN/'outputs'/f'{stem}.json',dict(variant_id=VARIANT,method=method,elapsed_seconds=elapsed,
                diagnostic=report,SPPR=S,A=A,L=L,negative_entries=negative,
                runtime_before=before,runtime_after=work.__dict__,runtime_warnings=[str(x.message) for x in observed],
                group_names=work.seq2name,synthetic_group_ids=work.get_Import_seq(),
                axes=dict(SPPR='recipient group rows x basal source columns',A='consumer rows x prey columns',L='A minus identity'),
                units=dict(SPPR='primary-production equivalents per unit recipient; basal-source contribution columns',A='dimensionless requirement weights',L='dimensionless linear operator'),
                scope_definitions=dict(PP=[1],inner=[1,25],all=[1,25,26]),
                scientific_state_unchanged_by_diagnostic=unchanged,options=h.OPTIONS))
            scopes={'PP':S[[1]].sum(axis=1),'inner':S[[1,25]].sum(axis=1),'all':S.sum(axis=1)}
            save(RUN/'outputs'/f'{stem}_scopes.json',scopes)
            summary=dict(variant_id=VARIANT,method=method,status=report['status'],model_input=report['model_input'],
                divergence=report['divergence'],balance=report['balance'],footprint=report.get('footprint'),warnings=report.get('warnings'),
                negative_sppr_entries=sum(x['matrix']=='SPPR' for x in negative),seabird_source_coefficients=S.loc[22].to_dict(),
                seabird_total_sppr=float(S.loc[22].sum()),detritus_source_coefficients=S.loc[25].to_dict(),
                detritus_total_sppr=float(S.loc[25].sum()),elapsed_seconds=elapsed)
            save(RUN/'outputs'/f'{stem}_summary.json',summary)
            checks.append(matrix_checks(RUN/'outputs'/f'{stem}.json'))
            for scenario in ('baseline','remove_redistribute'):
                old=read(BASE/'outputs'/f'{scenario}_{method.replace(" ","_")}_summary.json')
                comparisons.append(dict(scenario=scenario,execution='verified retained prior run',method=method,status=old['status'],
                    rho=old['divergence']['rho_living'],recycling_b=old['divergence']['b'],
                    pp_budget_gap_percent=100*old['balance']['rel_gap'],strict_model_balanced=old['model_input']['is_model_balanced'],
                    strict_sppr_balanced=old['balance']['is_balanced'],negative_sppr_entries=old['negative_entry_count'],
                    seabird_total_sppr=old['seabird_total_sppr'],warnings=old['warnings']))
            comparisons.append(dict(scenario=VARIANT,execution='fresh run',method=method,status=report['status'],
                input_status=report['model_input']['status'],divergence_status=report['divergence']['status'],balance_status=report['balance']['status'],
                rho=report['divergence']['rho_living'],recycling_b=report['divergence']['b'],
                pp_budget_gap_percent=100*report['balance']['rel_gap'],strict_model_balanced=report['model_input']['is_model_balanced'],
                strict_sppr_balanced=report['balance']['is_balanced'],negative_sppr_entries=summary['negative_sppr_entries'],
                seabird_total_sppr=summary['seabird_total_sppr'],warnings=report.get('warnings')))
            print(json.dumps(comparisons[-1],ensure_ascii=False),flush=True)
        except Exception as exc:
            failure=dict(method=method,status='EXECUTION_EXCEPTION',reason=str(exc),traceback=traceback.format_exc())
            failures.append(failure);save(RUN/'outputs'/f'{stem}_unavailable.json',failure)
            print(traceback.format_exc(),flush=True)
    save(RUN/'outputs/comparison.json',comparisons)
    save(RUN/'qa/reopened_matrix_checks.json',checks)
    after=h.verify_inputs(); after[relative(LEDGER)]=h.sha(LEDGER)
    assert after==protected
    assert verify_baseline()==baseline_verified
    verified=dict(source_hashes_unchanged=True,baseline_package_unchanged=True,all_groups_preserved=True,
        runtime_roundtrip_exact=True,unchanged_consumers_exact=True,only_eligible_affected_ba_changed=True,
        ba_recomputed_count=len(intervention['ba_changes']),provenance_gaps=intervention['ba_preservation_gaps'],
        all_requested_methods_returned=len(checks)==3,failures=failures,
        no_constructor_or_broad_balance_routine=True,no_ee_floor=True,no_adoption=True)
    save(RUN/'qa/verification.json',verified)
    manifest=dict(schema_version=1,run_id=RUN.name,unit_id='LME_022',model_id=MODEL.name,variant_id=VARIANT,
        started_at_utc=started,completed_at_utc=datetime.now(timezone.utc).isoformat(),
        timezone='Asia/Jerusalem',purpose='Authorized model-local correction for researcher review; unadopted runtime variant',
        selected_model_id_at_review='ICES_WGSAM2015_North_Sea_1991',constructor='Not called; exact __new__ archived-state restore',
        historical_constructor_record=relative(h.RUNTIME),historical_engine_sha256=h.sha(h.ENGINE/'PPRCalculator.py'),
        canonical_model_sha256=h.sha(MODEL/'model.json'),source_hashes=protected,baseline_evidence_index=relative(BASE/'evidence_index.json'),
        runtime=dict(executable=sys.executable,python=sys.version,platform=platform.platform(),
            dependencies={name:importlib.metadata.version(name) for name in ('numpy','pandas','scipy','sympy','igraph','tqdm')}),
        method_options=h.OPTIONS,diagnostic_signature=str(inspect.signature(h.PPRCalculator.diagnose_sppr)),
        thresholds='Unchanged historical engine defaults; see signature and full returns',
        use_ee_floor=False,methods=list(h.METHODS),script_sha256=h.sha(SCRIPT),
        runtime_before_sha256=h.sha(RUN/'inputs/runtime_state_before.json'),runtime_corrected_sha256=h.sha(RUN/'inputs/runtime_state_corrected.json'),
        preserved_original_manifest_unknown_execution=True,biological_parameters_changed=['seabird diet only'],
        dependent_derived_fields_changed=['all prey predation refreshed','affected provenance-proven loader-derived BA only'])
    save(RUN/'run_manifest.json',manifest)
    artifacts=[]
    for rel,sha in protected.items():
        artifacts.append(dict(role='canonical_source' if rel.endswith('/model.json') else 'protected_evidence',path=rel,sha256=sha,availability='present'))
    for artifact in baseline_verified:
        artifacts.append(dict(role='verified_baseline_evidence',availability='present',**artifact))
    for path in sorted(RUN.rglob('*')):
        if not path.is_file() or path.name in ('evidence_index.json','completeness.json'): continue
        role='execution_evidence'
        if path.name=='intervention.json':role='correction_and_ba_provenance'
        elif path.name=='reopened_matrix_checks.json':role='matrix_verification'
        elif path.name=='comparison.json':role='before_after_comparison'
        elif path.name.startswith('runtime_state_'):role='exact_runtime_state'
        elif path.suffix=='.py':role='reproduction_code'
        elif path.name in ('corrected_GE.json','corrected_TE.json','corrected_With_Egestion.json'):role='full_direct_return'
        artifacts.append(dict(role=role,path=relative(path),sha256=h.sha(path),availability='present'))
    save(RUN/'evidence_index.json',dict(schema_version=1,run_id=RUN.name,region_id='LME_022',model_id=MODEL.name,variant_id=VARIANT,
        source_identity={'canonical_model_sha256':h.sha(MODEL/'model.json')},
        computational_input_identity={'archived_state_sha256':h.STATE_SHA,'corrected_runtime_sha256':h.sha(RUN/'inputs/runtime_state_corrected.json')},
        methods=list(h.METHODS),required_roles=['canonical_source','protected_evidence','verified_baseline_evidence','correction_and_ba_provenance',
            'exact_runtime_state','full_direct_return','matrix_verification','before_after_comparison','reproduction_code'],
        artifacts=artifacts,reconciliation={k:v for k,v in verified.items() if isinstance(v,bool)}))
    assert not failures, failures
    print('Completed correction and three fresh full diagnostic returns; no adoption.',flush=True)

if __name__=='__main__': main()
