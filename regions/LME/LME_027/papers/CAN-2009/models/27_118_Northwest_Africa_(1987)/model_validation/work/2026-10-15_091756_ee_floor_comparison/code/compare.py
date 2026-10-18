"""Bounded, non-adopting comparison using archived loading and current accounting.

Run with the repository root on sys.path. No existing scientific artifact is written.
"""
from pathlib import Path
import copy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import sys
import traceback
import warnings

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
MODEL = RUN.parents[2]
ROOT = next(p for p in MODEL.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from tools.scientific_helpers.sppr.method_coverage import (
    ENGINE, _audited_engine, _engine, _runtime, encode_lossless, _json_bytes,
)

HIST = MODEL / 'extracted_tables/evidence/integration_20260928'
OUT = RUN / 'outputs'
QA = RUN / 'qa'
for folder in (OUT, QA, RUN / 'inputs'):
    folder.mkdir(parents=True, exist_ok=True)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def typed(path, value):
    save(path, encode_lossless(value))


def equivalent(a, b):
    if isinstance(a, pd.DataFrame):
        pd.testing.assert_frame_equal(a, b, check_exact=False, atol=1e-12, rtol=1e-12)
    elif isinstance(a, pd.Series):
        pd.testing.assert_series_equal(a, b, check_exact=False, atol=1e-12, rtol=1e-12)
    else:
        assert a == b


def state(model):
    return {**_runtime(model), 'ee_threshold': model.ee_threshold}


def main():
    protected_paths = [ROOT/'Project.xlsx', ROOT/'regions/LME/LME_027/LME_027.xlsx',
        MODEL/'model.json', MODEL/'model_notes.md', MODEL/'sppr_source.xlsx',
        MODEL/'model_validation/validation.docx', MODEL/'results/result_manifest.json',
        MODEL/'results/regional_snapshot.xlsx']
    protected_paths += [p for p in HIST.rglob('*') if p.is_file()]
    protected = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected_paths}
    save(RUN/'inputs/protected_hashes.json', protected)
    historical = json.loads((HIST/'execution_evidence.json').read_text(encoding='utf-8'))
    assert sha(MODEL/'model.json') == historical['input_sha256']
    saved_state = json.loads((HIST/'loaded_state.json').read_text(encoding='utf-8'))
    saved_solutions = json.loads((HIST/'direct_solutions.json').read_text(encoding='utf-8'))
    calculation = HERE/'executed_engine/PPRCalculator.py'
    calculation.parent.mkdir(exist_ok=True)
    if not calculation.exists():
        shutil.copyfile(ENGINE/'PPRCalculator.py', calculation)
    assert sha(calculation) == sha(ENGINE/'PPRCalculator.py')
    base_flags = {
        'constructor': historical['constructor'],
        'engine_sources': {name: (HIST/'engine'/name).relative_to(MODEL).as_posix()
                           for name in historical['engine_sha256']},
        'engine_source_hashes': historical['engine_sha256'],
    }
    _, modeldata, loader, _ = _audited_engine(base_flags, MODEL/'model.json')
    constructor = historical['constructor']
    flags = {**base_flags, 'calculation_engine_upgrade': 'ee_floor_v1',
        'calculation_engine_source': calculation.relative_to(MODEL).as_posix(),
        'calculation_engine_sha256': sha(calculation)}
    _, _, calculator, thresholds = _engine(flags, MODEL/'model.json')
    def source_from_canonical():
        # The archived loader parses identity from the old filename convention.
        # A short-lived byte-identical copy supports that convention; no second
        # canonical/computational model is retained or edited.
        temporary = RUN/'inputs'/(MODEL.name+'.json')
        temporary.write_bytes((MODEL/'model.json').read_bytes())
        try:
            assert sha(temporary) == sha(MODEL/'model.json')
            return modeldata(str(temporary))
        finally:
            temporary.unlink()
    diagnostics = {**historical['diagnostic'], 'fix_EE_0_cases': True}
    save(RUN/'inputs/run_configuration.json', {
        'model_id': MODEL.name, 'region_id': 'LME_027', 'canonical_sha256': sha(MODEL/'model.json'),
        'base_loading': base_flags, 'calculation_upgrade': flags,
        'floor_comparison': {'OFF': False, 'ON': True}, 'ee_floor': .1, 'ee_threshold': .1,
        'diagnostics': diagnostics, 'thresholds': thresholds,
        'python': platform.python_version(), 'platform': platform.platform(),
        'packages': {p: importlib.metadata.version(p) for p in
                     ('numpy','pandas','sympy','scipy','igraph','tqdm')},
        'historical_initialization_note': 'Archived loader preserves pre-floor BA and other conventions; current constructor defaults are not substituted.',
        'filename_compatibility': 'Archived loader requires period-bearing filename; loads a temporary byte-identical canonical copy, deleted immediately after parsing.',
        'authorization': 'User requested floor-OFF versus floor-ON diagnostics only; preserve signed review; no adoption/publication.',
        'started_at': datetime.now(timezone.utc).isoformat(),
    })
    checks = {}
    summaries = {}
    models = {}
    negatives = []
    scopes = []
    for label, enabled in [('OFF', False), ('ON', True)]:
        folder = OUT/label
        folder.mkdir(exist_ok=True)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            source = source_from_canonical()
            model = loader.from_modeldata(source, **constructor)
        # Match the actual completed audited state before changing its calculation class.
        for key, old in saved_state.items():
            actual = getattr(model, key)
            if isinstance(actual, pd.DataFrame):
                expected = pd.DataFrame(old['data'], index=old['index'], columns=old['columns'])
                pd.testing.assert_frame_equal(actual, expected, check_dtype=False, check_names=False,
                                              check_exact=False, atol=1e-12, rtol=1e-12)
            elif isinstance(actual, pd.Series):
                expected = pd.Series(old['data'], index=old['index'])
                pd.testing.assert_series_equal(actual, expected, check_dtype=False, check_names=False,
                                               check_exact=False, atol=1e-12, rtol=1e-12)
        checks[label+'_archived_initialization_matches_saved'] = True
        model.__class__ = calculator
        model._initialization_settings = {**constructor, 'use_ee_floor': enabled,
                                         'ee_floor': .1, 'ee_threshold': .1}
        with warnings.catch_warnings(record=True) as floor_warnings:
            warnings.simplefilter('always')
            model.apply_ee_floor(enabled, .1, .1)
        models[label] = model
        # Independent canonical reload verifies initialization without repeating solves.
        fresh = loader.from_modeldata(source_from_canonical(), **constructor)
        fresh.__class__ = calculator
        fresh._initialization_settings = copy.deepcopy(model._initialization_settings)
        fresh.apply_ee_floor(enabled, .1, .1)
        checks[label+'_reload_equal'] = _json_bytes(state(model)) == _json_bytes(state(fresh))
        assert checks[label+'_reload_equal']
        before = state(model)
        save(folder/'runtime_before.json', before)
        typed(folder/'ee_floor_ledger.json', model.ee_floor_ledger)
        save(folder/'ee_floor_info.json', model.ee_floor_info)
        summaries[label] = {}
        notices = {'constructor': [str(w.message) for w in caught],
                   'floor': [str(w.message) for w in floor_warnings], 'diagnostics': {}}
        for option in ('GE','TE','With Egestion'):
            print(label, option, 'starting', flush=True)
            stem = option.replace(' ', '_')
            with warnings.catch_warnings(record=True) as diagnostic_warnings:
                warnings.simplefilter('always')
                try:
                    result = model.diagnose_sppr(TE_option=option, short=False, flat=False,
                        return_sppr=True, **diagnostics)
                    report, sppr, a, l = result
                    typed(folder/(stem+'_full_return.json'), result)
                    typed(folder/(stem+'_report.json'), report)
                    matrices = {'SPPR': sppr, 'A': a, 'L': l}
                    typed(folder/(stem+'_matrices.json'), matrices)
                    metadata = {'groups': [{'id': int(i), 'name': model.seq2name[i],
                        'trophic_info': str(model._groups_df.loc[i,'trophic_info']),
                        'synthetic': i in model.get_Import_seq()} for i in model._groups_df.index],
                        'matrices': {key: {'orientation': 'rows: recipient groups; columns: basal sources' if key=='SPPR' else 'rows and columns: groups',
                            'units': 'basal-source wet-weight equivalents per unit group production' if key=='SPPR' else 'dimensionless',
                            'row_ids': frame.index.tolist(), 'row_names': [model.seq2name[i] for i in frame.index],
                            'column_ids': frame.columns.tolist(), 'column_names': [model.seq2name[i] for i in frame.columns]}
                            for key,frame in matrices.items()},
                        'scope_definitions': {'all':'all basal sources', 'inner':'PP and detritus, excluding import', 'PP':'primary producers only'},
                        'basal_source_membership': {'PP': model.get_PP_seq(), 'DET': model.get_DET_seq(), 'Import': model.get_Import_seq()}}
                    typed(folder/(stem+'_axes.json'), metadata)
                    reopened = json.loads((folder/(stem+'_matrices.json')).read_text(encoding='utf-8'))
                    for key, frame in matrices.items():
                        assert frame.index.is_unique and frame.columns.is_unique
                        assert reopened[key] == encode_lossless(frame)
                        values = frame.to_numpy(dtype=float)
                        for i,j in np.argwhere(values < -1e-10):
                            negatives.append({'case':label,'method':option,'matrix':key,
                                'recipient_id':int(frame.index[i]),'recipient_name':model.seq2name[frame.index[i]],
                                'source_id':int(frame.columns[j]),'source_name':model.seq2name[frame.columns[j]],
                                'value':float(values[i,j]),'tolerance':1e-10})
                    stored = pd.DataFrame(reopened['SPPR']['data'], index=reopened['SPPR']['index'], columns=reopened['SPPR']['columns'])
                    for scope in ('all','inner','PP'):
                        cols = [j for j in sppr.columns if scope=='all' or
                                (j not in model.get_Import_seq() and (scope!='PP' or j in model.get_PP_seq()))]
                        expected = sppr[cols].sum(axis=1, min_count=1)
                        restored = stored[cols].sum(axis=1, min_count=1)
                        np.testing.assert_allclose(expected, restored, rtol=1e-12, atol=1e-12)
                        for i,v in restored.items():
                            scopes.append({'case':label,'method':option,'scope':scope,'group_id':int(i),
                                           'group_name':model.seq2name[i],'sppr':float(v)})
                    checks[label+'_'+stem+'_matrix_and_scope_roundtrip'] = True
                    historical_error = None
                    if label == 'OFF':
                        historical_error = 0.
                        for key, frame in matrices.items():
                            old = saved_solutions[option][key]
                            old_frame = pd.DataFrame(old['data'],index=old['index'],columns=old['columns']).reindex(index=frame.index,columns=frame.columns)
                            np.testing.assert_allclose(frame.to_numpy(dtype=float),old_frame.to_numpy(dtype=float),rtol=1e-10,atol=1e-10)
                            historical_error = max(historical_error,float(np.max(np.abs(frame.to_numpy(dtype=float)-old_frame.to_numpy(dtype=float)))))
                        checks[stem+'_OFF_matches_historical_matrices'] = True
                    summaries[label][option] = {
                        'status':report['status'], 'divergence':report['divergence'],
                        'model_input':report['model_input'], 'balance':report['balance'],
                        'footprint':report['footprint'], 'warnings':report['warnings'],
                        'SPPR_finite':bool(np.isfinite(sppr.to_numpy(dtype=float)).all()),
                        'negative_SPPR_entries':int((sppr.to_numpy(dtype=float)<-1e-10).sum()),
                        'historical_matrix_max_abs_difference':historical_error}
                except Exception as exc:
                    error = {'status':'EXCEPTION','type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
                    save(folder/(stem+'_exception.json'),error)
                    summaries[label][option] = error
            notices['diagnostics'][option] = [str(w.message) for w in diagnostic_warnings]
            print(label, option, summaries[label][option]['status'], flush=True)
        after = state(model)
        save(folder/'runtime_after.json', after)
        checks[label+'_diagnostics_preserve_runtime'] = _json_bytes(before) == _json_bytes(after)
        assert checks[label+'_diagnostics_preserve_runtime']
        save(folder/'warnings.json', notices)
    off,on = models['OFF'],models['ON']
    for key in ('_DC','_det_fate','catch','predation','immigration','emigration','net_migration','respiration','egestion'):
        equivalent(getattr(off,key),getattr(on,key))
    living = [i for i in off.p.index if i not in off.get_DET_seq()+off.get_Import_seq()]
    for key in ('p','q','growth'):
        equivalent(getattr(off,key).loc[living],getattr(on,key).loc[living])
    equivalent(off._groups_df.loc[living,'biomass'],on._groups_df.loc[living,'biomass'])
    checks['protected_biological_flows_equal_OFF_ON'] = True
    ledger = on.ee_floor_ledger
    np.testing.assert_allclose(off.M0, on.M0+on.external_mortality_export,atol=1e-12,rtol=1e-12)
    checks['removed_mortality_equals_external_sink'] = True
    assert all(sha(ROOT/p)==value for p,value in protected.items())
    checks['all_preexisting_protected_files_byte_identical'] = True
    assert all(len(summaries[label])==3 and all('divergence' in r for r in summaries[label].values()) for label in summaries)
    save(OUT/'comparison.json', {'region_id':'LME_027','model_id':MODEL.name,
        'ee_floor':.1,'ee_threshold':.1,'cases':summaries,'floor_info':on.ee_floor_info,
        'changed_groups':ledger.loc[ledger.applied].reset_index().to_dict(orient='records'),
        'review_and_results_adopted':False})
    save(OUT/'negative_entries.json', negatives)
    save(OUT/'group_scope_coefficients.json', scopes)
    save(QA/'reconciliation.json', checks)
    artifacts = []
    for p in sorted(RUN.rglob('*')):
        if p.is_file() and p.name not in ('evidence_index.json','completeness.json'):
            artifacts.append({'role':p.relative_to(RUN).as_posix(),'path':p.relative_to(RUN).as_posix(),
                              'sha256':sha(p),'availability':'present'})
    for role,p in [('canonical_input',MODEL/'model.json'),('original_signed_review',MODEL/'model_validation/validation.docx'),
                   ('historical_configuration',HIST/'execution_evidence.json'),('historical_matrices',HIST/'direct_solutions.json')]:
        artifacts.append({'role':role,'path':os.path.relpath(p,RUN).replace('\\','/'),'sha256':sha(p),'availability':'present'})
    save(RUN/'evidence_index.json', {'schema_version':1,'run_id':RUN.name,'region_id':'LME_027',
        'model_id':MODEL.name,'variant_id':'runtime_EE_floor_OFF_vs_ON_0.1_threshold_0.1',
        'source_identity':{'accession':'EcoBase 118','canonical_sha256':sha(MODEL/'model.json'),
                           'publication_fidelity':'Retained source review limitations remain; no fresh extraction.'},
        'computational_input_identity':{'canonical_sha256':sha(MODEL/'model.json'),'initialization':'archived audited loader'},
        'methods':[label+'/'+option for label in ('OFF','ON') for option in ('GE','TE','With Egestion')],
        'required_roles':[a['role'] for a in artifacts], 'artifacts':artifacts, 'reconciliation':checks})
    print(json.dumps({label:{option:{'status':r['status'],'rho_living':r['divergence']['rho_living'],
        'b':r['divergence']['b'],'balance_gap':r['balance']['rel_gap']} for option,r in results.items()}
        for label,results in summaries.items()},indent=2),flush=True)


if __name__=='__main__':
    main()
