"""Bounded, unadopted diet-only experiments on the exact archived calculator state.

Run with Python 3.11 and the archived engine's scientific dependencies. No constructor,
balancing routine, canonical input, saved workbook, or production result is modified.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
import warnings
from datetime import datetime, timezone

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
MODEL = SCRIPT.parents[4]
ENGINE = MODEL / 'extracted_tables/evidence/diagnostic_code/PPREstimation'
ARCHIVE = MODEL / 'model_validation/evidence/source_review/diet_reextraction_20261002/archive_by_sha256'
STATE_SHA = 'cad6ee682425931cd209e04aad408f86f409a548c3079ce41536ed32d33dd3bb'
STATE = ARCHIVE / STATE_SHA / 'computational_state.json'
RUNTIME_SHA = '889379c97fdf6750a717378c11677ee824196f06e3f5cde293a2bed9290d4fd7'
RUNTIME = ARCHIVE / RUNTIME_SHA / 'runtime_verification.json'
SAVED = MODEL / 'model_validation/evidence/source_review/matrix_inspection.json'
EXPECTED = {
    MODEL / 'model.json': '5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691',
    MODEL / 'sppr_source.xlsx': '22964abbea82f5f9337f4ba8b48b96319651cbc43101cc5a4f8c2c28546a32f5',
    MODEL / 'results/regional_snapshot.xlsx': 'bd6d84c7bef986e2af2d12b382d74715f1456ebbf8d3bd6b45a0c574c35f5438',
    STATE: STATE_SHA,
    RUNTIME: RUNTIME_SHA,
    SAVED: 'ba8448d9106f31eee4caf0f2d647c095a2f0705f53fb0baef8ef16ab2814a9c6',
    ENGINE / 'PPRCalculator.py': 'b2bb08f0564c8cd0fcc873eb1c681fd924c3dd113e22d6b388456248fc0162a7',
    ENGINE / 'ModelData.py': '36b2da24ee467530b867b18abd12ae478964f9106bafc78f07eb1a6de616f54e',
    ENGINE / 'utils.py': '817f969850b250d06563cfff2e5d1be0fdf70bacb7a3c4ac317bf69c805ca07f',
}
METHODS = ('GE', 'TE', 'With Egestion')
SCENARIOS = ('baseline', 'remove_only', 'remove_redistribute')
OPTIONS = dict(det_collapse_mode='never', det_open_mode='none', det_theta=1,
               det_external_sppr=0, fix_EE_0_cases=True)
FIELDS = ('_groups_df', '_DC', '_det_fate', 'p', 'q', 'catch', 'predation', 'growth',
          'immigration', 'emigration', 'net_migration', 'M0', 'respiration', 'egestion',
          'det_export', 'EE', 'GE', 'GS', 'TL')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inputs():
    actual = {os.path.relpath(p, RUN).replace('\\', '/'): sha(p) for p in EXPECTED}
    for p, expected in EXPECTED.items():
        assert sha(p) == expected, f'Protected evidence changed: {p}'
    return actual


def initialize_imports():
    global np, pd, PPRCalculator, ModelData
    import numpy as np
    import pandas as pd
    sys.path.insert(0, str(ENGINE))
    from PPRCalculator import PPRCalculator
    from ModelData import ModelData
    assert Path(sys.modules['PPRCalculator'].__file__).resolve() == ENGINE / 'PPRCalculator.py'


def decode(value):
    """Decode this historical JSON vocabulary, without evaluation or constructors."""
    if isinstance(value, list):
        return [decode(v) for v in value]
    if not isinstance(value, dict):
        return value
    kind = value.get('type')
    if kind == 'float':
        return float(value['value'])
    if kind == 'dict':
        return {decode(k): decode(v) for k, v in value['items']}
    if kind == 'Series':
        return pd.Series(decode(value['values']), index=decode(value['index']), name=decode(value['name']))
    if kind == 'DataFrame':
        return pd.DataFrame(decode(value['values']), index=decode(value['index']), columns=decode(value['columns']))
    if kind in ('ModelData', 'PPRCalculator'):
        cls = {'ModelData': ModelData, 'PPRCalculator': PPRCalculator}[kind]
        obj = cls.__new__(cls)
        obj.__dict__.update(decode(value['attributes']))
        return obj
    raise ValueError(f'Unsupported archive value: {kind}')


def mask_kind(v):
    if v is None:
        return 'null'
    if isinstance(v, (float, np.floating)):
        if math.isnan(v):
            return 'nan'
        if math.isinf(v):
            return 'positive_infinity' if v > 0 else 'negative_infinity'
    return None


def encode(v):
    """Preserve labels, scalar types and distinct missing/nonfinite masks."""
    if isinstance(v, pd.DataFrame):
        raw = v.to_numpy(dtype=object).tolist()
        return dict(type='DataFrame', index=encode(v.index.tolist()), columns=encode(v.columns.tolist()),
                    values=encode(raw), shape=list(v.shape), dtypes=[str(x) for x in v.dtypes],
                    masks={k: [[mask_kind(c) == k for c in row] for row in raw]
                           for k in ('null', 'nan', 'positive_infinity', 'negative_infinity')})
    if isinstance(v, pd.Series):
        return dict(type='Series', index=encode(v.index.tolist()), values=encode(v.tolist()), name=encode(v.name))
    if isinstance(v, np.ndarray):
        return dict(type='ndarray', dtype=str(v.dtype), shape=list(v.shape), values=encode(v.tolist()))
    if isinstance(v, np.generic):
        return encode(v.item())
    if isinstance(v, dict):
        if all(isinstance(k, str) for k in v):
            return {k: encode(x) for k, x in v.items()}
        return dict(type='dict', items=[[encode(k), encode(x)] for k, x in v.items()])
    if isinstance(v, tuple):
        return dict(type='tuple', items=[encode(x) for x in v])
    if isinstance(v, list):
        return [encode(x) for x in v]
    kind = mask_kind(v)
    if kind and kind != 'null':
        return dict(type='float', value={'nan': 'nan', 'positive_infinity': 'inf', 'negative_infinity': '-inf'}[kind])
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    raise TypeError(type(v))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(encode(value), ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def runtime(calc):
    return {k: copy.deepcopy(getattr(calc, k)) for k in FIELDS}


def digest_value(value):
    return hashlib.sha256(json.dumps(encode(value), ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')).hexdigest()


def make_scenario(scenario):
    calc = PPRCalculator.__new__(PPRCalculator)
    calc.__dict__.update(decode(json.loads(STATE.read_text(encoding='utf-8'))))
    original = runtime(calc)
    before = calc._DC.loc[22].copy()
    if scenario != 'baseline':
        calc._DC.loc[22, 22] = 0.0
        if scenario == 'remove_redistribute':
            calc._DC.loc[22] /= calc._DC.loc[22].sum()
        # Refresh dependent predation only. Preserve all rates, BA and other flows.
        calc.predation = calc.get_Z(DET_as_PP=True).sum(axis=0).reindex(calc.p.index)
        calc._groups_df['predation'] = calc.predation
        calc.is_balanced = calc.is_model_balanced()[0]
    after = calc._DC.loc[22]
    changed = [dict(predator_id=22, predator_name=calc.seq2name[22], prey_id=int(i),
                    prey_name=calc.seq2name[i], before=float(before[i]), after=float(after[i]),
                    difference=float(after[i]-before[i])) for i in before.index if before[i] != after[i]]
    for field in FIELDS:
        if field not in ('_DC', '_groups_df', 'predation'):
            assert digest_value(original[field]) == digest_value(getattr(calc, field)), field
    assert calc.n_groups == 26 and 22 in calc._groups_df.index
    ledger = dict(scenario=scenario, archived_state_sha256=STATE_SHA,
                  diet_before_sum=float(before.sum()), diet_after_sum=float(after.sum()),
                  removed_self_fraction=float(before[22]-after[22]),
                  remaining_prey_multiplier=(float(1/(before.sum()-before[22])) if scenario == 'remove_redistribute' else 1.0),
                  changed_diet_cells=changed,
                  predation_changes=[dict(group_id=int(i), name=calc.seq2name[i], before=float(original['predation'][i]),
                                          after=float(calc.predation[i]), difference=float(calc.predation[i]-original['predation'][i]))
                                     for i in calc.predation.index if calc.predation[i] != original['predation'][i]],
                  protected_fields_unchanged=True,
                  protocol='Exact archived-state restore, diet-only intervention, recompute predation. No constructor, rebalancing, BA solve, EE floor or adoption. Cached TL is historical; diagnose_sppr recomputes its own TL.',
                  archived_state_fields=original, experiment_state_fields=runtime(calc))
    return calc, ledger


def worker(scenario, method):
    verify_inputs()
    initialize_imports()
    calc, ledger = make_scenario(scenario)
    stem = f'{scenario}_{method.replace(" ", "_")}'
    before = runtime(calc)
    start = time.perf_counter()
    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter('always')
        report, sppr, A, L = calc.diagnose_sppr(TE_option=method, short=False, flat=False, return_sppr=True, **OPTIONS)
    elapsed = time.perf_counter()-start
    negative = []
    if sppr is not None:
        for i in sppr.index:
            for j in sppr.columns:
                if float(sppr.loc[i, j]) < -1e-10:
                    negative.append(dict(recipient_id=int(i), recipient_name=calc.seq2name[i], source_id=int(j),
                                         source_name=calc.seq2name[j], value=float(sppr.loc[i,j])))
    state_unchanged = digest_value(before) == digest_value(runtime(calc))
    assert state_unchanged, 'Diagnostic modified scientific state'
    save(RUN/'outputs'/f'{stem}.json', dict(scenario=scenario, method=method, elapsed_seconds=elapsed,
        diagnostic=report, SPPR=sppr, A=A, L=L, runtime_warnings=[str(x.message) for x in observed],
        negative_entries=negative, negative_tolerance=1e-10, scientific_state_unchanged_by_diagnostic=state_unchanged,
        group_names=calc.seq2name, synthetic_group_ids=calc.get_Import_seq(),
        axes=dict(SPPR='recipient rows x basal source columns', A='consumer rows x prey columns', L='A minus identity'),
        units=dict(SPPR='primary-production equivalents per unit recipient; columns are basal-source contributions',
                   A='dimensionless production-requirement weights', L='dimensionless linear operator'),
        runtime_before=before, runtime_after=runtime(calc), options=OPTIONS))
    save(RUN/'inputs'/f'{scenario}_intervention.json', ledger)
    original_check = None
    if scenario == 'baseline':
        saved = next(x for x in json.loads(SAVED.read_text(encoding='utf-8'))['methods'] if x['method']==method)
        sm = saved['source_matrix']
        old = pd.DataFrame(sm['values'], index=sm['row_ids'], columns=sm['column_ids'])
        new = sppr.loc[old.index, old.columns]
        difference = np.abs(new.values-old.values)
        original_check = dict(status_matches=report['status']==saved['overall_status'],
                              rho_matches=math.isclose(report['divergence']['rho_living'], saved['rho_living'], rel_tol=1e-12, abs_tol=1e-12),
                              source_matrix_matches=bool(np.allclose(new, old, rtol=1e-12, atol=1e-9)),
                              max_abs_difference=float(difference.max()),
                              max_scaled_difference=float((difference/(1+np.abs(old.values))).max()))
        assert all(original_check[k] for k in ('status_matches','rho_matches','source_matrix_matches')), original_check
    summary = dict(scenario=scenario, method=method, status=report['status'], model_input=report['model_input'],
                   divergence=report['divergence'], balance=report['balance'], footprint=report.get('footprint'),
                   warnings=report.get('warnings'), seabird_source_coefficients=sppr.loc[22].to_dict() if sppr is not None else None,
                   seabird_total_sppr=float(sppr.loc[22].sum()) if sppr is not None else None,
                   diet_sum=ledger['diet_after_sum'], negative_entry_count=len(negative),
                   original_saved_comparison=original_check, elapsed_seconds=elapsed,
                   scientific_state_unchanged_by_diagnostic=state_unchanged)
    save(RUN/'outputs'/f'{stem}_summary.json', summary)
    verify_inputs()
    print(json.dumps(dict(scenario=scenario, method=method, status=report['status'],
                         rho=report['divergence']['rho_living'], balance=report['balance'],
                         seabird_total_sppr=summary['seabird_total_sppr']), allow_nan=False), flush=True)


def main():
    protected = verify_inputs()
    initialize_imports()
    outcomes = []
    for scenario in SCENARIOS:
        for method in METHODS:
            stem = f'{scenario}_{method.replace(" ", "_")}'
            command = [sys.executable, '-B', str(SCRIPT), '--worker', scenario, method]
            try:
                completed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
                                           timeout=180, env={**os.environ, 'PYTHONIOENCODING':'utf-8'})
                log = completed.stdout + completed.stderr
                (RUN/'qa').mkdir(parents=True, exist_ok=True)
                (RUN/'qa'/f'{stem}.log').write_text(log, encoding='utf-8')
                if completed.returncode:
                    print(log, flush=True)
                    raise RuntimeError(f'{stem} failed with exit {completed.returncode}')
                outcomes.append(json.loads((RUN/'outputs'/f'{stem}_summary.json').read_text(encoding='utf-8')))
                print(completed.stdout.strip(), flush=True)
            except subprocess.TimeoutExpired as exc:
                save(RUN/'outputs'/f'{stem}_unavailable.json', dict(status='TIMEOUT', timeout_seconds=180, reason=str(exc)))
                raise
    after = verify_inputs()
    assert protected == after
    save(RUN/'outputs/summary.json', outcomes)
    save(RUN/'qa/verification.json', dict(source_hashes_unchanged=True, protected_input_hashes=after,
        original_methods_reproduced=all(all(x['original_saved_comparison'][k] for k in
             ('status_matches','rho_matches','source_matrix_matches')) for x in outcomes if x['scenario']=='baseline'),
        all_nine_direct_diagnostics_returned=len(outcomes)==9,
        all_groups_preserved=True, no_result_adoption=True,
        diagnostics_preserved_state=all(x['scientific_state_unchanged_by_diagnostic'] for x in outcomes)))
    manifest = dict(schema_version=1, run_id=RUN.name, unit_id='LME_022', model_id=MODEL.name,
        timestamp=datetime.now(timezone.utc).isoformat(), purpose='Unadopted seabird self-feeding sensitivity diagnostics',
        source_hashes=protected, constructor='Not called: exact archived attribute restore',
        original_constructor_record=os.path.relpath(RUNTIME, RUN).replace('\\','/'),
        runtime=dict(python=sys.version, platform=platform.platform(), dependencies={n:importlib.metadata.version(n)
                     for n in ('numpy','pandas','scipy','sympy','igraph','tqdm')}),
        method_options=OPTIONS, methods=list(METHODS), scenarios=list(SCENARIOS),
        timeout_seconds_per_method=180, script_sha256=sha(SCRIPT),
        assumptions=['Historical engine/state, no EE floor transformation.',
                     'Remove only: zero runtime seabird self-diet, leave all other fractions unchanged.',
                     'Redistribute: zero self-diet and proportionally normalize all remaining prey, including detritus.',
                     'Recompute all prey predation from modified diet and fixed Q.',
                     'Preserve B, P, Q, EE, GE, M0, catch, BA, respiration, egestion, migration and routing.',
                     'Do not rebalance model or compensate missing diet; no canonical or workbook adoption.'])
    manifest['artifacts'] = [dict(path=f.relative_to(RUN).as_posix(),sha256=sha(f),availability='present')
                             for f in sorted(RUN.rglob('*')) if f.is_file() and f.name != 'run_manifest.json']
    save(RUN/'run_manifest.json', manifest)
    print('Completed nine diagnostics and verified protected input hashes.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', nargs=2, metavar=('SCENARIO','METHOD'))
    args = parser.parse_args()
    if args.worker:
        worker(*args.worker)
    else:
        main()
