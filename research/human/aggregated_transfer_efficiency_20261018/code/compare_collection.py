"""Reproducible three-TE comparison over every canonical EcoBase JSON.

Each input is evaluated once with the same declared calculator defaults. Stage
checkpoints preserve failures and bounded subprocess timeouts without repairing
scientific inputs. Output stays within this researcher-owned study.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import warnings
from queue import Queue, Empty

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[2]
ENGINE = ROOT / 'tools/scientific_code/PPREstimation'
CORPUS = ROOT / 'common_reference_data/ecobase/models'
OUT = STUDY / 'results/full_collection'
EVIDENCE = STUDY / 'evidence'
METHODS = ('fixed_0.1', 'consumer_mean_Q', 'aggregated_II_IV')
FLAGS = dict(underdetermined=False, zero_catch=True, zero_biomass_accum=True,
             default_gs=True, weight_flow=1., weight_guess=1., normalize_DC=False,
             DC_tol=.001, balance_BA_after_DC_normalization=True,
             use_ee_floor=True, ee_floor=.1, ee_threshold=.1)
LOCAL = threading.local()
SERVERS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if hasattr(value, 'item'):
        return plain(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return {'nonfinite': str(value)}
    return value


def number(value):
    if isinstance(value, dict) or value is None:
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(plain(data), ensure_ascii=False, indent=2,
                                    allow_nan=False) + '\n', encoding='utf-8')
    # Windows indexers/readers may briefly hold a destination handle open.
    # Retry only the byte-identical output replacement, never scientific work.
    for attempt in range(8):
        try:
            temporary.replace(path)
            break
        except PermissionError:
            if attempt == 7:
                raise
            time.sleep(.05 * (attempt + 1))


def save_csv(path, rows):
    rows = list(rows)
    headers = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False)
                             if isinstance(value, (dict, list)) else value
                             for key, value in row.items()})


def verify_calculation_identity(manifest, records, root=ROOT):
    """Reject stale checkpoints using the original calculation manifest."""
    errors = []
    for category in ('source_hashes', 'code_hashes'):
        for name, digest in manifest[category].items():
            path = root / name
            if not path.is_file() or sha(path) != digest:
                errors.append(f'{category} mismatch: {name}')
    expected = manifest['source_hashes']
    names = [record.get('source') for record in records]
    if len(names) != len(set(names)) or set(names) != set(expected):
        errors.append('Checkpoint source inventory differs from the original manifest.')
    for record in records:
        name = record.get('source')
        if record.get('source_sha256') != expected.get(name):
            errors.append(f'Checkpoint source hash mismatch: {name}')
        if record.get('flags') != manifest['initialization_flags']:
            errors.append(f'Checkpoint initialization flags mismatch: {name}')
    if errors:
        raise ValueError('Calculation identity verification failed: ' + '; '.join(errors))


def worker(source, checkpoint):
    import numpy as np
    sys.path.insert(0, str(ENGINE))
    from ModelData import ModelData
    from PPRCalculator import PPRCalculator

    start = time.monotonic()
    source = Path(source)
    record = dict(source=source.relative_to(ROOT).as_posix(), model_id=source.stem,
                  source_sha256=sha(source), stage='json', json_status='not_run',
                  load_status='not_run', construction_status='not_run',
                  aggregation_status='not_run', flags=FLAGS,
                  methods={method: {'status': 'not_run'} for method in METHODS})

    def checkpoint_now():
        record['elapsed_seconds'] = round(time.monotonic() - start, 3)
        save_json(checkpoint, record)

    checkpoint_now()
    try:
        raw = json.loads(source.read_text(encoding='utf-8-sig'))
        record['json_status'] = 'ok'
        record['source_group_count'] = len(raw.get('group', [])) if isinstance(raw, dict) else None
        record['source_units'] = {key: value for key, value in raw.items()
                                  if any(term in key.lower() for term in ('unit', 'currency', 'area'))}
        record['stage'] = 'load'
        checkpoint_now()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            model_data = ModelData(str(source))
            record['load_status'] = 'ok'
            record['model_name'] = model_data.model_name
            record['model_year'] = model_data.model_year
            record['stage'] = 'construction'
            checkpoint_now()
            calculator = PPRCalculator.from_modeldata(model_data, **FLAGS)
            record['construction_status'] = 'ok'
            record['group_count'] = calculator.n_groups
            record['model_balance_status'] = bool(calculator.is_balanced)
            record['initialization_warnings'] = [str(item.message) for item in caught]
        catch = calculator.catch
        record['total_native_catch'] = float(catch.sum(skipna=False))
        record['negative_catch_group_count'] = int((catch < 0).sum())
        record['missing_catch_group_count'] = int(catch.isna().sum())
        record['stage'] = 'aggregation'
        checkpoint_now()
        try:
            table = calculator.get_aggregated_TE()
            record['aggregation_status'] = 'ok'
            record['aggregated_flows'] = table.reset_index().to_dict(orient='records')
            record['aggregation_metadata'] = dict(table.attrs)
            values = table.TE.to_numpy()
            usable = bool(np.isfinite(values).all() and ((values > 0) & (values <= 1)).all())
            record['aggregated_scalar_valid'] = usable
            record['aggregated_scalar_TE'] = float(np.exp(np.log(values).mean())) if usable else None
        except Exception as error:
            record['aggregation_status'] = 'error'
            record['aggregation_error'] = f'{type(error).__name__}: {error}'
        checkpoint_now()

        groups = calculator.get_groups_df()
        record['groups'] = [{'seq': int(seq), 'name': str(groups.loc[seq, 'group_name']),
                             'trophic_info': str(groups.loc[seq, 'trophic_info']),
                             'native_catch': float(catch.loc[seq])} for seq in groups.index]
        for method in METHODS:
            record['stage'] = method
            checkpoint_now()
            result = record['methods'][method]
            try:
                if method == 'fixed_0.1':
                    result['scalar_TE'] = .1
                    frame = calculator.SPPR_1995(global_TE=.1)
                elif method == 'consumer_mean_Q':
                    scalar = calculator.get_TE('global', global_TE='mean',
                                                weights='consumption', as_matrix=False)
                    result['scalar_TE'] = float(scalar.loc[calculator.get_Regular_seq()].iloc[0])
                    frame = calculator.SPPR_1995(global_TE='mean', weights='consumption')
                else:
                    result['scalar_TE'] = record.get('aggregated_scalar_TE')
                    frame = calculator.SPPR_1995(TE_option='aggregated')
                coefficients = frame.sppr.reindex(catch.index)
                result['nonfinite_sppr_group_count'] = int((~np.isfinite(coefficients)).sum())
                result['negative_sppr_group_count'] = int((coefficients < 0).sum())
                result['status'] = 'ok' if np.isfinite(coefficients).all() else 'nonfinite_sppr'
                active = catch != 0
                terms = coefficients.loc[active] * catch.loc[active]
                ppr = float(terms.sum(skipna=False))
                total_catch = record['total_native_catch']
                result['native_PPR'] = ppr
                result['catch_weighted_SPPR'] = ppr / total_catch if total_catch > 0 else None
                result['catch_weighted_status'] = (
                    'nonfinite_catch' if not np.isfinite(catch).all() else
                    'negative_catch' if (catch < 0).any() else
                    'no_positive_catch' if total_catch <= 0 else
                    'nonfinite_PPR' if not math.isfinite(ppr) else
                    'nonpositive_PPR' if ppr <= 0 else 'ok')
                for group in record['groups']:
                    group[method] = float(coefficients.loc[group['seq']])
            except Exception as error:
                result['status'] = 'error'
                result['error'] = f'{type(error).__name__}: {error}'
            checkpoint_now()
        record['stage'] = 'complete'
        record['run_status'] = 'complete'
    except Exception as error:
        stage = record['stage']
        record[{'json': 'json_status', 'load': 'load_status',
                'construction': 'construction_status'}.get(stage, 'run_status')] = 'error'
        record['run_status'] = 'error'
        record['error'] = f'{type(error).__name__}: {error}'
    checkpoint_now()


class ModelServer:
    """Warm isolated subprocess; each request still has a hard time budget."""
    def __init__(self):
        environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                           MKL_NUM_THREADS='1', PYTHONIOENCODING='utf-8')
        self.process = subprocess.Popen(
            [sys.executable, '-u', str(Path(__file__).resolve()), '--server'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', env=environment,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        self.lines = Queue()
        threading.Thread(target=self._read_lines, daemon=True).start()
        SERVERS.append(self)
        self.wait_for('SERVER_READY', 90.)

    def _read_lines(self):
        for line in self.process.stdout:
            self.lines.put(line.strip())
        self.lines.put('SERVER_EXITED')

    def wait_for(self, marker, timeout):
        deadline = time.monotonic() + timeout
        while True:
            line = self.lines.get(timeout=max(.01, deadline - time.monotonic()))
            if line == marker:
                return
            if line == 'SERVER_EXITED':
                raise RuntimeError('Model worker exited before completing its request.')
            if time.monotonic() >= deadline:
                raise Empty

    def call(self, source, checkpoint, timeout):
        self.process.stdin.write(json.dumps({'source': str(source), 'checkpoint': str(checkpoint)}) + '\n')
        self.process.stdin.flush()
        self.wait_for('MODEL_COMPLETE', timeout)

    def close(self):
        if self.process.poll() is None:
            self.process.kill()
            self.process.wait(timeout=10)


def server():
    # Pay scientific-library imports once, outside each model's arithmetic budget.
    import numpy
    sys.path.insert(0, str(ENGINE))
    import ModelData
    import PPRCalculator
    print('SERVER_READY', flush=True)
    for line in sys.stdin:
        request = json.loads(line)
        worker(request['source'], Path(request['checkpoint']))
        print('MODEL_COMPLETE', flush=True)


def run_one(source, timeout):
    checkpoint = OUT / 'models' / (source.stem + '.json')
    start = time.monotonic()
    # Replace any previous run's record before requesting work; a killed worker
    # can never cause stale successful results to be mistaken for this run.
    save_json(checkpoint, {'source': source.relative_to(ROOT).as_posix(),
                           'source_sha256': sha(source), 'model_id': source.stem,
                           'stage': 'worker_start', 'run_status': 'not_run', 'flags': FLAGS})
    try:
        if getattr(LOCAL, 'server', None) is None:
            LOCAL.server = ModelServer()
        LOCAL.server.call(source, checkpoint, timeout)
        record = json.loads(checkpoint.read_text(encoding='utf-8'))
    except Empty:
        record = json.loads(checkpoint.read_text(encoding='utf-8'))
        record['run_status'] = 'timeout'
        record['timeout_seconds'] = timeout
        record['timeout_stage'] = record.get('stage', 'python_imports')
        if getattr(LOCAL, 'server', None) is not None:
            LOCAL.server.close()
        LOCAL.server = None
    except Exception as error:
        record = json.loads(checkpoint.read_text(encoding='utf-8'))
        record['run_status'] = 'subprocess_error'
        record['subprocess_error'] = f'{type(error).__name__}: {error}'
        if getattr(LOCAL, 'server', None) is not None:
            LOCAL.server.close()
        LOCAL.server = None
    record.setdefault('source', source.relative_to(ROOT).as_posix())
    record.setdefault('source_sha256', sha(source))
    record.setdefault('model_id', source.stem)
    record['wall_seconds'] = round(time.monotonic() - start, 3)
    save_json(checkpoint, record)
    return record


def quantiles(values):
    import numpy as np
    values = [value for value in values if value is not None and math.isfinite(value)]
    return {'n': len(values), **({str(q): float(np.quantile(values, q))
             for q in (0., .05, .25, .5, .75, .95, 1.)} if values else {}),
            'arithmetic_mean': float(np.mean(values)) if values else None,
            'sd': float(np.std(values, ddof=1)) if len(values) > 1 else None,
            'sem': float(np.std(values, ddof=1) / np.sqrt(len(values))) if len(values) > 1 else None}


def summarize(records):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from collections import Counter

    summary = {'inventory_count': len(records),
               'stage_counts': {key: dict(Counter(row.get(key, 'not_run') for row in records))
                                for key in ('json_status', 'load_status', 'construction_status',
                                            'aggregation_status', 'run_status')},
               'method_counts': {method: dict(Counter(row.get('methods', {}).get(method, {}).get(
                   'status', 'not_run') for row in records)) for method in METHODS}}
    summary['failure_reason_counts'] = dict(Counter(
        (record.get('stage', 'unknown') + ': ' + record.get('error', record.get('subprocess_error',
            'timeout' if record.get('run_status') == 'timeout' else 'unknown')))
        for record in records if record.get('run_status') != 'complete'))
    summary['aggregation_failure_reason_counts'] = dict(Counter(
        record.get('aggregation_error', 'not attempted') for record in records
        if record.get('aggregation_status') == 'error'))
    summary['aggregated_SPPR_failure_reason_counts'] = dict(Counter(
        record.get('methods', {}).get('aggregated_II_IV', {}).get('error', 'not attempted')
        for record in records
        if record.get('methods', {}).get('aggregated_II_IV', {}).get('status') == 'error'))
    model_rows, flow_rows, group_rows = [], [], []
    for record in records:
        row = {key: record.get(key) for key in (
            'model_id', 'model_name', 'model_year', 'source', 'source_sha256',
            'json_status', 'load_status', 'construction_status', 'aggregation_status',
            'run_status', 'stage', 'error', 'timeout_stage', 'group_count',
            'model_balance_status', 'total_native_catch', 'negative_catch_group_count',
            'missing_catch_group_count', 'aggregated_scalar_valid', 'aggregated_scalar_TE')}
        for flow in record.get('aggregated_flows', []):
            flow_rows.append({'model_id': record['model_id'], **flow})
            row[f'TE_{flow["trophic_level"]}'] = flow['TE']
        for method, result in record.get('methods', {}).items():
            for field in ('status', 'error', 'scalar_TE', 'native_PPR', 'catch_weighted_SPPR',
                          'catch_weighted_status', 'nonfinite_sppr_group_count'):
                row[f'{method}__{field}'] = result.get(field)
        model_rows.append(row)
        group_rows.extend({'model_id': record['model_id'], **group} for group in record.get('groups', []))
    save_csv(OUT / 'model_comparison.csv', model_rows)
    save_csv(OUT / 'level_flows.csv', flow_rows)
    save_csv(OUT / 'group_sppr.csv', group_rows)
    cohort = [r for r in records if all(
        r.get('methods', {}).get(method, {}).get('status') == 'ok' and
        r['methods'][method].get('catch_weighted_status') == 'ok' for method in METHODS)]
    summary['common_valid_catch_cohort_n'] = len(cohort)
    summary['common_valid_catch_cohort_ids'] = [r['model_id'] for r in cohort]
    summary['per_level_TE_quantiles'] = {
        str(level): quantiles([number(f['TE']) for r in records for f in r.get('aggregated_flows', [])
                              if f['trophic_level'] == level]) for level in (2, 3, 4)}
    summary['TE_validity_counts'] = {}
    for level in (2, 3, 4):
        values = [number(f['TE']) for r in records for f in r.get('aggregated_flows', [])
                  if f['trophic_level'] == level]
        summary['TE_validity_counts'][str(level)] = {
            'finite': sum(v is not None for v in values),
            'missing_or_nonfinite': sum(v is None for v in values),
            'zero': sum(v == 0 for v in values),
            'negative': sum(v is not None and v < 0 for v in values),
            'above_one': sum(v is not None and v > 1 for v in values)}
    ratios = []
    for record in cohort:
        base = record['methods']['fixed_0.1']['native_PPR']
        ratios.append({'model_id': record['model_id'], **{
            method + '_to_fixed': record['methods'][method]['native_PPR'] / base
            for method in METHODS[1:]},
            'aggregated_to_consumer_mean': record['methods']['aggregated_II_IV']['native_PPR'] /
            record['methods']['consumer_mean_Q']['native_PPR']})
    save_csv(OUT / 'paired_ratios.csv', ratios)
    summary['paired_PPR_ratio_quantiles'] = {
        key: quantiles([row[key] for row in ratios]) for key in (
            'consumer_mean_Q_to_fixed', 'aggregated_II_IV_to_fixed', 'aggregated_to_consumer_mean')}
    summary['scalar_TE_quantiles_common_cohort'] = {
        method: quantiles([number(r['methods'][method].get('scalar_TE')) for r in cohort])
        for method in METHODS}
    summary['scalar_aggregated_TE_all_usable'] = quantiles([
        number(record.get('aggregated_scalar_TE')) for record in records
        if record.get('aggregated_scalar_valid')])
    pooled = [number(flow['TE']) for record in records for flow in record.get('aggregated_flows', [])]
    summary['pooled_level_TE_all_finite'] = quantiles(pooled)
    summary['pooled_level_TE_positive_at_most_one'] = quantiles([
        value for value in pooled if value is not None and 0 < value <= 1])
    summary['pooled_level_note'] = 'Levels II–IV within each model are dependent observations; SEM is descriptive, not an independent-model confidence interval.'

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 3, figsize=(13, 5.2), layout='constrained')
    for axis, level, color in zip(axes, (2, 3, 4), ('#286F8E', '#C78128', '#5B8251')):
        values = [number(f['TE']) for r in records for f in r.get('aggregated_flows', [])
                  if f['trophic_level'] == level]
        values = np.array([v for v in values if v is not None]) * 100
        bounded = values[(values >= 0) & (values <= 100)]
        outside = values[(values < 0) | (values > 100)]
        axis.hist(bounded, bins=np.linspace(0, 100, 26), color=color,
                  edgecolor='white', linewidth=.4)
        axis.axvline(10., color='#333333', linestyle='--', linewidth=1)
        outlier_text = (', '.join(f'{value:.3g}%' for value in outside) if len(outside) <= 5
                        else f'{len(outside)} values; range {outside.min():.3g}% to {outside.max():.3g}%')
        axis.text(0, -.24, 'Outside 0–100%: ' + (outlier_text or 'none'),
                  transform=axis.transAxes, fontsize=8, va='top', wrap=True)
        axis.set(title=f'Level {level} | bars n = {len(bounded)}\nall finite n = {len(values)}',
                 xlabel='Transfer efficiency (%)', xlim=(0, 100),
                 ylabel='Number of models')
    fig.suptitle(f'Lindeman flow efficiencies across the EcoBase collection\n'
                 f'{len(records)} JSON inputs; bounded values in bars, invalid outliers listed below', fontsize=13)
    fig.savefig(OUT / 'level_te_histograms.png', dpi=180)
    fig.savefig(OUT / 'level_te_histograms.svg')
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), layout='constrained')
    for axis, method, color, label in zip(axes, METHODS[1:], ('#286F8E', '#C78128'),
                                         ('Consumer Q-weighted TE', 'Aggregated II–IV TE')):
        values = np.array([row[method + '_to_fixed'] for row in ratios])
        axis.hist(np.log10(values), bins=25, color=color, edgecolor='white', linewidth=.4)
        axis.axvline(0, color='#333333', linestyle='--', linewidth=1)
        median = np.median(values) if len(values) else float('nan')
        axis.set(title=f'{label}\nmedian ratio {median:.3g}',
                 xlabel='log10(model-native PPR / fixed-10% PPR)', ylabel='Number of models')
    fig.suptitle(f'Paired PPR comparison | same {len(cohort)} models for all three methods\n'
                 'Ratios also equal catch-weighted SPPR ratios; no cross-model PPR sum', fontsize=12)
    fig.savefig(OUT / 'paired_ppr_ratios.png', dpi=180)
    fig.savefig(OUT / 'paired_ppr_ratios.svg')
    plt.close(fig)
    summary['interpretation_limits'] = [
        'Loadability, construction, numerical eligibility, balance and researcher validation are separate.',
        'The collection is the current 230-file EcoBase inventory, not the historical 140 level estimates from 48 models.',
        'Identical explicit current initialization defaults were used, with no per-model repair or fallback.',
        'Model-native PPR values can have different mass/area/time units and are never summed across systems.',
        'Histograms show finite level efficiencies in 0–100%; invalid outliers are explicitly listed below each panel and retained in CSV/JSON.',
        'Common-cohort ratios require all three methods finite with nonnegative positive-total model catch.',
        'This study computes arithmetic comparison, not researcher approval or current EwE software replication.',
    ]
    save_json(OUT / 'summary.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker')
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--timeout', type=float, default=60.)
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--summarize-only', action='store_true')
    args = parser.parse_args()
    if args.server:
        server()
        return
    if args.worker:
        worker(args.worker, args.checkpoint)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    sources = sorted(CORPUS.glob('*.json'), key=lambda path: path.name)
    source_hashes = {path.relative_to(ROOT).as_posix(): sha(path) for path in sources}
    code_files = [Path(__file__), *(ENGINE / name for name in ('PPRCalculator.py', 'ModelData.py', 'utils.py'))]
    code_hashes = {path.relative_to(ROOT).as_posix(): sha(path) for path in code_files}
    manifest = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    discovery='Sorted nonrecursive *.json in canonical common_reference_data/ecobase/models',
                    source_count=len(sources), source_hashes=source_hashes, code_hashes=code_hashes,
                    initialization_flags=FLAGS, python_executable=sys.executable,
                    timeout_seconds=args.timeout, workers=args.workers,
                    isolation='Three reused subprocesses, fresh calculator per model, hard per-model timeout and worker restart on timeout',
                    technical_rerun_reason='Initial run had four transient Windows output-replacement PermissionErrors; bounded byte-identical write retries added, full run repeated without input or scientific-flag changes.',
                    conventions='Current explicit defaults; no per-model repairs, normalization retries or exclusions')
    if args.summarize_only:
        manifest = json.loads((EVIDENCE / 'full_collection_manifest.json').read_text(encoding='utf-8'))
        completed_path = EVIDENCE / 'full_collection_verification.json'
        if not completed_path.is_file():
            raise ValueError('Summarize-only requires a completed, verified calculation run.')
        completed = json.loads(completed_path.read_text(encoding='utf-8'))
        if (completed.get('original_calculation_started_utc') != manifest['started_utc']
                or not completed.get('source_bytes_unchanged')
                or not completed.get('code_bytes_unchanged')):
            raise ValueError('Summarize-only cannot use an incomplete or interrupted calculation run.')
        original_sources = manifest['source_hashes']
        if set(source_hashes) != set(original_sources):
            raise ValueError('Current source inventory differs from original calculation manifest.')
        for source in sources:
            checkpoint = OUT / 'models' / (source.stem + '.json')
            if sha(checkpoint) != completed['output_sha256'].get(checkpoint.relative_to(STUDY).as_posix()):
                raise ValueError('Checkpoint bytes differ from the completed calculation: ' + source.stem)
        records = [json.loads((OUT / 'models' / (source.stem + '.json')).read_text(encoding='utf-8'))
                   for source in sources]
        verify_calculation_identity(manifest, records)
    else:
        save_json(EVIDENCE / 'full_collection_manifest.json', manifest)
        records = []
        with ThreadPoolExecutor(max_workers=max(1, min(3, args.workers))) as pool:
            pending = {pool.submit(run_one, source, args.timeout): source for source in sources}
            for future in as_completed(pending):
                record = future.result()
                records.append(record)
                if len(records) % 10 == 0 or len(records) == len(sources):
                    constructed = sum(r.get('construction_status') == 'ok' for r in records)
                    aggregated = sum(r.get('methods', {}).get('aggregated_II_IV', {}).get('status') == 'ok'
                                     for r in records)
                    print(f'{len(records)}/{len(sources)} processed; constructed={constructed}; '
                          f'aggregated SPPR={aggregated}', flush=True)
        for model_server in SERVERS:
            model_server.close()
        records.sort(key=lambda row: row['source'])
        verify_calculation_identity(manifest, records)
    summary = summarize(records)
    unchanged_sources = all(sha(ROOT / path) == digest for path, digest in manifest['source_hashes'].items())
    unchanged_code = all(sha(ROOT / path) == digest for path, digest in manifest['code_hashes'].items())
    verification = dict(completed_utc=datetime.now(timezone.utc).isoformat(),
                        original_calculation_started_utc=manifest['started_utc'],
                        source_count=len(sources), output_record_count=len(records),
                        unique_sources=len({r['source'] for r in records}),
                        source_bytes_unchanged=unchanged_sources, code_bytes_unchanged=unchanged_code,
                        output_sha256={p.relative_to(STUDY).as_posix(): sha(p)
                                       for p in sorted(OUT.rglob('*')) if p.is_file()},
                        summary=summary)
    save_json(EVIDENCE / 'full_collection_verification.json', verification)
    print(json.dumps(summary['stage_counts'], indent=2), flush=True)
    print(f'Common valid catch cohort: {summary["common_valid_catch_cohort_n"]}', flush=True)
    if not unchanged_sources or not unchanged_code or len(records) != len(sources):
        raise RuntimeError('Run consistency verification failed; inspect evidence before using results.')


if __name__ == '__main__':
    main()
