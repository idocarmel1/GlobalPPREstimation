"""Independently reconcile the reviewed Northwest Africa source matrices."""
from pathlib import Path
import hashlib
import json
import math
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import workbooks as W
import regional as R

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
unit = 'LME_027'
model = '27_118_Northwest_Africa_(1987)'
ev = ROOT / 'regions' / unit / 'validation_reports' / model
saved = ROOT / 'regions' / unit / 'models' / model / 'integration_20260928'
path = ROOT / 'regions' / unit / (unit + '.xlsx')
fingerprint = sha(path)
book = W.read_book(path)
overview = W.validate_region(book, path)
assert R.result_hash(book) == overview['calculation_result_sha256']
groups = {int(r['seq']): r['group_name'] for r in W.records(book, 'Selected model groups', 'Groups')}
groups[28] = 'diet_import'
assert set(groups) == set(range(1, 29))
rows = W.records(book, 'Selected model groups', 'Group SPPR')
actual = {(r['method'], r['scope'], r['group']): r['sppr'] for r in rows}
assert len(actual) == len(rows) == 252
solutions = read(saved / 'direct_solutions.json')
checks = []
for method, stored in [('GE', 'new_GE'), ('TE', 'new_TE_EEfix'), ('With Egestion', 'new_WithEgestion')]:
    frame = solutions[method]['SPPR']
    recipients, columns, values = frame['index'], frame['columns'], frame['data']
    assert set(recipients) == set(groups) and len(recipients) == 28
    assert columns == [28, 27, 26, 24] and len(values) == 28
    assert all(len(row) == 4 for row in values)
    assert all(math.isfinite(x) and x >= 0 for row in values for x in row)
    for scope, selected in [('all', {28, 27, 26, 24}), ('inner', {27, 26, 24}), ('PP', {26, 24})]:
        for seq, row in zip(recipients, values):
            expected = sum(value for column, value in zip(columns, row) if column in selected)
            observed = actual[stored, scope, groups[seq]]
            assert math.isclose(expected, observed, rel_tol=2e-15, abs_tol=1e-12), (method, scope, seq)
    checks.append({'method': method, 'full_source_entries': 112, 'negative_or_nonfinite': 0,
                   'scoped_group_coefficients_reconciled': 84})
baseline = W.read_book(BASE / 'baseline' / unit / (unit + '.xlsx'))
old_rows = W.records(baseline, 'Selected model groups', 'Group SPPR')
old = {(r['method'], r['scope'], r['group']): r['sppr'] for r in old_rows}
assert len(old) == 84 and all(k[0] == 'new_GE' for k in old)
assert all(actual[k] == v for k, v in old.items())
assert baseline['Classic PPR']['Annual'] == book['Classic PPR']['Annual']
assert sha(path) == fingerprint
proof = {'unit_id': unit, 'workbook_sha256': fingerprint,
         'retained_source_solutions_sha256': sha(saved / 'direct_solutions.json'),
         'matrix_and_projection_checks': checks, 'existing_GE_coefficients_exact': 84,
         'new_TE_and_egestion_coefficients': 168, 'classic_annual_exactly_preserved': True,
         'fresh_result_identity': True,
         'limits': 'Numerical reconciliation of exact retained matrices; WARN, false strict balance, source-version and geographic limitations remain.'}
(BASE / 'verification/LME_027_retained_projection_coordinator_check.json').write_text(
    json.dumps(proof, indent=2) + '\n', encoding='utf-8')
print(json.dumps(proof))
