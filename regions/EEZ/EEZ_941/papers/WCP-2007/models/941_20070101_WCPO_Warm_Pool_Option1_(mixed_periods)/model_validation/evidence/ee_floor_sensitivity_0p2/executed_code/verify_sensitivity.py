"""Reopen and verify matched sensitivity evidence, with no solver invocation."""
from pathlib import Path
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import sys

HERE = Path(__file__).resolve()
MODEL = next(p for p in HERE.parents if (p / 'model.json').is_file())
ROOT = next(p for p in HERE.parents if (p / 'Project.xlsx').is_file())
OUT = MODEL / 'model_validation/evidence/ee_floor_sensitivity_0p2'
REFERENCE = MODEL / 'model_validation/evidence/ee_floor_on'


def read(path):
    if path.suffix == '.gz':
        with gzip.open(path, 'rt', encoding='utf-8') as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


comparison = read(OUT / 'comparison.json')
groups = {g['id']: g for g in read(OUT / 'group_axes.json')}
qa = {'configurations': {}, 'timestamp_utc': datetime.now(timezone.utc).isoformat()}
footprints = {}
for label in ('OFF', '0.1', '0.2'):
    dest = OUT / ('floor_' + label.replace('.', 'p').lower())
    qa['configurations'][label] = {}
    footprints[label] = {}
    for option, key in [('GE', 'new_GE'), ('TE', 'new_TE_EEfix')]:
        path = (REFERENCE if label == '0.1' else dest) / (key + '_full_return.json.gz')
        full = read(path)
        assert full['status'] == 'ok'
        matrix = full['source_matrix']
        assert full['return']['type'] == 'tuple' and len(full['return']['items']) == 4
        raw = full['return']['items'][1]
        assert {k:v for k,v in raw.items() if k != 'index_names'} == {k:v for k,v in matrix.items() if k != 'index_names'}
        assert full['return']['items'][0] == full['diagnostics']
        rows, cols, values = matrix['index'], matrix['columns'], matrix['data']
        assert len(set(rows)) == len(rows) and len(set(cols)) == len(cols)
        assert set(rows) == set(groups) and set(cols) <= set(groups)
        negatives = []
        max_error = 0
        for i, row in enumerate(values):
            for j, value in enumerate(row):
                assert isinstance(value, (int, float)) and math.isfinite(value)
                assert not any(matrix['masks'][mask][i][j] for mask in ('null','nan','positive_infinity','negative_infinity'))
                if value < 0:
                    negatives.append({'recipient_id': rows[i], 'source_id': cols[j], 'value': value})
            for scope in ('all', 'inner', 'PP'):
                selected = [j for j, seq in enumerate(cols) if scope == 'all'
                    or (scope == 'inner' and groups[seq]['type'] != 'Import')
                    or (scope == 'PP' and groups[seq]['type'] == 'PP')]
                actual = sum(row[j] for j in selected)
                expected = full['scopes'][scope][groups[rows[i]]['name']]
                max_error = max(max_error, abs(actual - expected))
                assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)
        assert full['runtime_before_sha256'] == full['runtime_after_sha256']
        assert full['scopes'] == comparison['configurations'][label]['methods'][option]['scopes']
        qa['configurations'][label][option] = {'matrix_shape': matrix['shape'], 'axes_unique_complete': True,
            'all_entries_finite': True, 'literal_negative_entries': negatives,
            'scope_sum_max_absolute_error': max_error, 'scope_sum_relative_tolerance': 1e-12,
            'exact_full_return_retained': True, 'runtime_unchanged_by_diagnosis': True,
            'source': path.relative_to(MODEL).as_posix(), 'sha256': sha(path)}
        footprints[label][option] = full['diagnostics']['footprint']
diffs = {}
for option in ('GE', 'TE'):
    diffs[option] = {}
    for field in ('ppr_all', 'ppr_inner', 'ppr_pp_only'):
        vals = {label: footprints[label][option][field] for label in footprints}
        diffs[option][field] = {'values': vals,
            '0p2_minus_0p1': vals['0.2']-vals['0.1'],
            '0p2_vs_0p1_percent': 100*(vals['0.2']-vals['0.1'])/vals['0.1'],
            '0p1_vs_OFF_percent': 100*(vals['0.1']-vals['OFF'])/vals['OFF'],
            '0p2_vs_OFF_percent': 100*(vals['0.2']-vals['OFF'])/vals['OFF']}
protected = read(OUT / 'protected_files.json')
assert all(sha(ROOT / path) == digest for path,digest in protected['before'].items())
qa['protected_files_unchanged'] = True
qa['no_adoption_or_parameter_changes'] = True
(OUT / 'verification.json').write_text(json.dumps(qa, indent=2), encoding='utf-8')
(OUT / 'source_model_catch_comparison.json').write_text(json.dumps(diffs, indent=2), encoding='utf-8')
(OUT / 'executed_code/verify_sensitivity.py').write_bytes(HERE.read_bytes())
if '--manifest' in sys.argv:
    artifacts = [{'path': p.relative_to(OUT).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size}
        for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'artifact_manifest.json']
    (OUT / 'artifact_manifest.json').write_text(json.dumps({'files': artifacts}, indent=2), encoding='utf-8')
print(json.dumps({'verification': qa, 'source_model_catch': diffs}, indent=2))
