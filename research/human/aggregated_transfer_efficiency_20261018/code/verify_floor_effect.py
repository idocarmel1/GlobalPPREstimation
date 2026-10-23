"""Independently check the saved paired EE-floor flow calculations.

Reads completed manifests, model checkpoints and exported level CSVs. It does
not import the scientific engine, rerun models, repair inputs or change results.
"""
from __future__ import annotations

from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[2]
OUTPUT = STUDY / 'evidence/full_collection_no_floor/paired_checks.json'
FLOW_COLUMNS = ('consumption', 'predation', 'export', 'respiration',
                'flow_to_detritus', 'throughput', 'TE')
CONSUMED = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def consume(path):
    key = path.relative_to(ROOT).as_posix()
    digest = sha(path)
    if key in CONSUMED and CONSUMED[key] != digest:
        raise ValueError('Input changed during verification: ' + key)
    CONSUMED[key] = digest
    return path


def read_json(path):
    return json.loads(consume(path).read_text(encoding='utf-8'))


def numeric(value):
    if isinstance(value, dict):
        return float(value['nonfinite'])
    try:
        return float(value)
    except (ValueError, TypeError):
        return numeric(json.loads(value))


def close(left, right, *, rel=1e-10, absolute=1e-8):
    if math.isnan(left) or math.isnan(right):
        return math.isnan(left) and math.isnan(right)
    return math.isclose(left, right, rel_tol=rel, abs_tol=absolute)


def load_run(folder, manifest_path, verification_path):
    manifest = read_json(manifest_path)
    verification = read_json(verification_path)
    if (verification['original_calculation_started_utc'] != manifest['started_utc']
            or not verification['source_bytes_unchanged']
            or not verification['code_bytes_unchanged']):
        raise ValueError('Calculation run is incomplete or inconsistent: ' + str(folder))
    for mapping in ('source_hashes', 'code_hashes'):
        for relative, digest in manifest[mapping].items():
            if sha(consume(ROOT / relative)) != digest:
                raise ValueError('Recorded ' + mapping + ' no longer match: ' + relative)
    records = {}
    for relative, digest in manifest['source_hashes'].items():
        path = folder / 'models' / (Path(relative).stem + '.json')
        if sha(consume(path)) != verification['output_sha256'].get(path.relative_to(STUDY).as_posix()):
            raise ValueError('Checkpoint bytes differ from completed run: ' + str(path))
        record = read_json(path)
        if (record['source'] != relative or record['source_sha256'] != digest
                or record['flags'] != manifest['initialization_flags']):
            raise ValueError('Checkpoint identity differs from manifest: ' + str(path))
        if record['model_id'] in records:
            raise ValueError('Duplicate checkpoint identity: ' + record['model_id'])
        records[record['model_id']] = record
    if (len(records) != manifest['source_count']
            or len(records) != verification['output_record_count']
            or len(records) != verification['unique_sources']):
        raise ValueError('Completed run record counts disagree.')
    flow_path = folder / 'level_flows.csv'
    if sha(consume(flow_path)) != verification['output_sha256'].get(flow_path.relative_to(STUDY).as_posix()):
        raise ValueError('Level CSV bytes differ from completed run.')
    flows = {}
    with flow_path.open(encoding='utf-8-sig', newline='') as handle:
        for row in csv.DictReader(handle):
            key = (row['model_id'], int(row['trophic_level']))
            if key in flows:
                raise ValueError('Duplicate level CSV row: ' + str(key))
            flows[key] = {column: numeric(row[column]) for column in FLOW_COLUMNS}
    checkpoint_flows = {(record['model_id'], int(row['trophic_level'])): row
                        for record in records.values() for row in record.get('aggregated_flows', [])}
    if set(flows) != set(checkpoint_flows):
        raise ValueError('CSV and checkpoint model-level inventories differ.')
    for key, row in flows.items():
        for column in FLOW_COLUMNS:
            if not close(row[column], numeric(checkpoint_flows[key][column]), rel=1e-13, absolute=1e-13):
                raise ValueError(f'CSV and checkpoint value disagree: {key}, {column}')
    return manifest, records, flows


def main():
    enabled, on_records, on_flows = load_run(
        STUDY / 'results/full_collection', STUDY / 'evidence/full_collection_manifest.json',
        STUDY / 'evidence/full_collection_verification.json')
    disabled, off_records, off_flows = load_run(
        STUDY / 'results/full_collection_no_floor', STUDY / 'evidence/full_collection_no_floor/manifest.json',
        STUDY / 'evidence/full_collection_no_floor/verification.json')
    if enabled['source_hashes'] != disabled['source_hashes']:
        raise ValueError('Paired source inventories or bytes differ.')
    for relative, digest in enabled['code_hashes'].items():
        if disabled['code_hashes'].get(relative) != digest:
            raise ValueError('Baseline engine/runner code identity changed: ' + relative)
    flags_on, flags_off = enabled['initialization_flags'], disabled['initialization_flags']
    flag_changes = {key: {'enabled': flags_on.get(key), 'disabled': flags_off.get(key)}
                    for key in set(flags_on) | set(flags_off) if flags_on.get(key) != flags_off.get(key)}
    if flag_changes != {'use_ee_floor': {'enabled': True, 'disabled': False}}:
        raise ValueError('More than the requested EE-floor flag changed: ' + str(flag_changes))
    if set(on_records) != set(off_records) or set(on_flows) != set(off_flows):
        raise ValueError('Paired models or level inventories differ.')
    for model_id in on_records:
        on, off = on_records[model_id], off_records[model_id]
        for status in ('json_status', 'load_status', 'construction_status', 'aggregation_status'):
            if on.get(status) != off.get(status):
                raise ValueError(f'Changed stage status: {model_id}, {status}')
        if on.get('error') != off.get('error'):
            raise ValueError('Changed load/construction failure: ' + model_id)
        if on.get('aggregation_metadata') != off.get('aggregation_metadata'):
            raise ValueError('Changed cycle-removal/aggregation metadata: ' + model_id)
    failures = []
    maxima = {column: 0. for column in ('consumption', 'predation', 'respiration', 'throughput',
                                      'export_plus_detritus_delta', 'TE_delta_identity')}
    changes = []
    for key in sorted(on_flows):
        on, off = on_flows[key], off_flows[key]
        for column in ('consumption', 'predation', 'respiration', 'throughput'):
            if math.isfinite(on[column]) and math.isfinite(off[column]):
                maxima[column] = max(maxima[column], abs(on[column] - off[column]))
            if not close(on[column], off[column]):
                failures.append({'model_id': key[0], 'level': key[1], 'check': column,
                                 'enabled': on[column], 'disabled': off[column]})
        export_delta = on['export'] - off['export']
        detritus_delta = on['flow_to_detritus'] - off['flow_to_detritus']
        residual = export_delta + detritus_delta
        maxima['export_plus_detritus_delta'] = max(maxima['export_plus_detritus_delta'], abs(residual))
        # Compare full conserved flows so the relative tolerance scales with
        # measured throughput rather than cancellation residuals near zero.
        if not close(on['export'] + on['flow_to_detritus'], off['export'] + off['flow_to_detritus']):
            failures.append({'model_id': key[0], 'level': key[1], 'check': 'export_detritus_conservation',
                             'residual': residual})
        if on['throughput'] > 0 and off['throughput'] > 0:
            difference = on['TE'] - off['TE']
            predicted = export_delta / off['throughput']
            maxima['TE_delta_identity'] = max(maxima['TE_delta_identity'], abs(difference - predicted))
            if not close(difference, predicted, rel=1e-9, absolute=1e-12):
                failures.append({'model_id': key[0], 'level': key[1], 'check': 'TE_delta_identity',
                                 'observed': difference, 'predicted': predicted})
        elif not close(on['TE'], off['TE']):
            failures.append({'model_id': key[0], 'level': key[1], 'check': 'unavailable_TE_classification'})
        changes.append({'model_id': key[0], 'trophic_level': key[1],
                        'TE_enabled': on['TE'], 'TE_disabled': off['TE'],
                        'TE_enabled_minus_disabled': on['TE'] - off['TE'],
                        'export_enabled_minus_disabled': export_delta,
                        'detritus_enabled_minus_disabled': detritus_delta})
    deltas = [row['TE_enabled_minus_disabled'] for row in changes]
    changed = [row for row in changes if abs(row['TE_enabled_minus_disabled']) > 1e-12]
    if not all(sha(ROOT / relative) == digest for relative, digest in CONSUMED.items()):
        raise ValueError('Consumed input changed before verification completed.')
    result = {
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'checker_sha256': sha(Path(__file__)), 'passed': not failures,
        'input_sha256': CONSUMED, 'paired_source_count': len(on_records),
        'paired_constructed_models': sum(row.get('construction_status') == 'ok' for row in on_records.values()),
        'paired_level_count': len(changes), 'flag_changes': flag_changes,
        'checks': {'source_model_bytes_identical': True, 'engine_and_base_runner_bytes_identical': True,
                   'exactly_requested_flag_changed': True, 'record_manifests_and_output_hashes_verified': True,
                   'CSV_matches_checkpoint_values': True, 'stage_statuses_and_failures_unchanged': True,
                   'cycle_removal_metadata_unchanged': True,
                   'consumption_predation_respiration_throughput_unchanged': not any(
                       f['check'] in ('consumption', 'predation', 'respiration', 'throughput') for f in failures),
                   'export_change_cancels_detritus_change': not any(
                       f['check'] == 'export_detritus_conservation' for f in failures),
                   'TE_change_equals_export_change_divided_by_throughput': not any(
                       f['check'] == 'TE_delta_identity' for f in failures)},
        'tolerances': {'flow_relative': 1e-10, 'flow_absolute': 1e-8,
                       'TE_relative': 1e-9, 'TE_absolute': 1e-12},
        'maximum_absolute_residuals': maxima,
        'changed_level_estimates_above_1e_minus_12': len(changed),
        'changed_models_above_1e_minus_12': len({row['model_id'] for row in changed}),
        'TE_enabled_minus_disabled_summary': {
            'mean': statistics.mean(deltas), 'min': min(deltas), 'max': max(deltas),
            'negative_beyond_tolerance_count': sum(value < -1e-12 for value in deltas)},
        'balance_flag_pairs': dict(Counter(
            f'{on_records[key].get("model_balance_status", "not_constructed")} -> '
            f'{off_records[key].get("model_balance_status", "not_constructed")}' for key in on_records)),
        'failures': failures, 'changed_level_estimates': changed,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in (
        'passed', 'paired_source_count', 'paired_constructed_models', 'paired_level_count',
        'maximum_absolute_residuals', 'changed_level_estimates_above_1e_minus_12',
        'changed_models_above_1e_minus_12', 'TE_enabled_minus_disabled_summary', 'failures')}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
