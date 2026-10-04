"""Render the offline report from computed, finite-or-null study records only."""
from pathlib import Path
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    assert data.get('schema_version') == 1
    models = {m['model_id'] for m in data['models']}
    assert models and len(models) == len(data['models']), 'Models must be nonempty and unique'
    numeric = lambda value: type(value) in (float, int) and math.isfinite(value)
    grid = data['fraction_grid']
    assert grid and all(numeric(f) and 0 <= f <= 1 for f in grid)
    assert grid == sorted(set(grid)), 'Fraction grid must be increasing and unique'
    seen = set()
    coordinates = set()
    for row in data['records']:
        assert row['model_id'] in models
        assert row['scenario_id'] not in seen
        seen.add(row['scenario_id'])
        assert numeric(row['fraction']) and row['fraction'] in grid
        assert row['method'] in data['methods'] and row['scope'] in data['scopes']
        assert row['route'] in data['routes'] or (row['route'] == 'S0' and row['fraction'] == 0)
        coordinate = tuple(row[k] for k in ('model_id', 'method', 'scope', 'route', 'fraction'))
        assert coordinate not in coordinates, 'Duplicate scenario coordinate would be ambiguous'
        coordinates.add(coordinate)
        assert isinstance(row['valid'], bool)
        if row['valid']:
            assert row['scenario_id'] in data['groups'], 'Valid result requires group coefficients'
            assert all(numeric(row[k])
                       for k in ('ppr_fixed_H_tC', 'ppr_retained_L_tC'))
        else:
            assert row.get('reasons') and all(isinstance(reason, str) and reason.strip() for reason in row['reasons']), 'Unavailable results need a reason'
    assert set(data['groups']).issubset(seen), 'Orphan group coefficients'
    def finite_tree(value):
        if isinstance(value, float):
            assert math.isfinite(value), 'Nonfinite values must be explicit nulls with a reason'
        elif isinstance(value, dict):
            for item in value.values(): finite_tree(item)
        elif isinstance(value, list):
            for item in value: finite_tree(item)
    finite_tree(data)


def render():
    data_path = ROOT / 'results/study.json'
    data = json.loads(data_path.read_text(encoding='utf-8'))
    validate(data)
    evidence_path = ROOT / 'results/source_evidence.json'
    evidence = json.loads(evidence_path.read_text(encoding='utf-8')) if evidence_path.exists() else {}
    with (ROOT / 'results/external_reference_audit.csv').open(encoding='utf-8', newline='') as stream:
        external = list(csv.DictReader(stream))
    package = {'study': data, 'evidence': evidence, 'external_reference': external}
    embedded = json.dumps(package, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    template = (ROOT / 'src/report_template.html').read_text(encoding='utf-8')
    assert template.count('__STUDY_DATA__') == 1
    html = template.replace('__STUDY_DATA__', embedded)
    (ROOT / 'report.html').write_text(html, encoding='utf-8', newline='\n')
    check = {'status': 'ok', 'records': len(data['records']), 'models': len(data['models']),
             'study_sha256': hashlib.sha256(data_path.read_bytes()).hexdigest(),
             'html_sha256': hashlib.sha256(html.encode('utf-8')).hexdigest(),
             'evidence_sha256': hashlib.sha256(evidence_path.read_bytes()).hexdigest() if evidence_path.exists() else None,
             'embedded_only': True, 'browser_verified': False,
             'browser_verification_reason': 'direct_file_navigation_blocked'}
    (ROOT / 'verification/report_data.json').write_text(json.dumps(check, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(check))


if __name__ == '__main__':
    render()
