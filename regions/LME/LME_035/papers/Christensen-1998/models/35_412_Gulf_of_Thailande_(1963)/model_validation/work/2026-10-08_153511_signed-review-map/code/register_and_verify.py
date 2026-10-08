"""Bounded LME035 signed review transaction, retaining other publications."""
import copy, hashlib, json, re, shutil, sys, zipfile
from pathlib import Path

root = Path.cwd().resolve()
sys.path.insert(0, str(root))
sys.stdout.reconfigure(encoding='utf-8')
from tools.project_core.registry.discovery import region_directory, resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.validation.researcher_review import (
    read_report, _register_review, approved_review, table_rows, sha, FIELDS)
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.maps.build_html import _refresh_reviews

unit = 'LME_035'
mid = '35_412_Gulf_of_Thailande_(1963)'
region = region_directory(root, unit)
model = resolve_model(region, mid)
report = model.parent / 'model_validation/validation.docx'
work = Path(__file__).resolve().parent.parent
project = root / 'Project.xlsx'
previous = work / 'inputs/Project_before_registration.xlsx'
pages = [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]

def payload(path, variable):
    text = path.read_text(encoding='utf-8')
    start = text.index('const ' + variable + '=') + len('const ' + variable + '=')
    value, _ = json.JSONDecoder().raw_decode(text, start)
    fingerprint = re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">', text).group(1)
    return value, fingerprint

def units(value, variable):
    return value['network']['units'] if variable == 'DB' else value['units']

def small_book(path):
    result = {}
    with zipfile.ZipFile(path) as z:
        for sheet, table in [('Overview', 'Settings'), ('Selected model groups', 'Groups')]:
            rows = table_rows(z, sheet, table)[3]
            headers = list(rows[0][1])
            result.setdefault(sheet, {})[table] = (headers, [[r.get(h) for h in headers] for _, r in rows])
    return result

verify_report(report)
name, date, source = read_report(root, report, mid)
assert (name, date) == ('Ido Carmel', '2026-10-08')
assert 'm. mammals are excluded from displayed PPR' in source['note']
book = small_book(region / (unit + '.xlsx'))
settings = dict(book['Overview']['Settings'][1])
assert (settings.get('results_model_id') or settings['selected_model_id']) == mid
headers, rows = book['Selected model groups']['Groups']
groups = [dict(zip(headers, r)) for r in rows]
matched = [r for r in groups if r['group_name'] == 'M. mammals']
assert len(matched) == 1 and matched[0]['seq'] == '1'
seq = [int(matched[0]['seq'])]
protected = [model, region / (unit + '.xlsx'), report,
             report.parent / 'taxon_mapping.xlsx', model.parent / 'model_notes.md',
             root / 'interactive_map/sources.html']
protected += list((model.parent / 'results').glob('*.xlsx'))
protected += list(model.parent.glob('*.xlsx'))
protected = [p for p in protected if p.is_file()]
hashes = {p.relative_to(root).as_posix(): sha(p) for p in protected}

with central_lock(root):
    assert not previous.exists(), 'Do not overwrite the retained transaction baseline'
    baseline_sha = sha(project)
    before = {}
    for filename, variable in pages:
        path = root / 'interactive_map' / filename
        before[filename], fingerprint = payload(path, variable)
        assert fingerprint == baseline_sha, (filename, 'stale baseline fingerprint')
        shutil.copyfile(path, work / 'inputs' / filename)
    shutil.copyfile(project, previous)
    print('Baseline retained; registering LME_035 only.', flush=True)
    values = _register_review(project, report, unit, mid, seq)
    _refresh_reviews(project, previous, [unit], model_ids={unit: mid})
    with zipfile.ZipFile(project) as z:
        metadata = next(r for _, r in table_rows(z, 'Models & coverage', 'Models')[3]
                        if (r['unit_id'], r['model_id']) == (unit, mid))
    assert all(metadata[k] == values[k] for k in FIELDS)
    expected = copy.deepcopy(source)
    expected['excluded_group_ids'] = ['M. mammals']
    assert json.loads(metadata['researcher_review_summary']) == expected
    approved = approved_review(root, metadata, book)
    assert approved['status'] == 'Validated by researcher'
    assert approved['report_sha256'] == sha(report)
    results = []
    for filename, variable in pages:
        after, fingerprint = payload(root / 'interactive_map' / filename, variable)
        assert fingerprint == sha(project)
        chosen = next(m for m in units(after, variable)[unit]['models'] if m['id'] == mid)
        assert chosen['researcher_review'] == approved
        assert chosen['display_ppr_excluded_group_ids'] == ['M. mammals']
        assert 'recorded_review_pending' not in chosen
        restored = copy.deepcopy(after)
        old_model = next(m for m in units(before[filename], variable)[unit]['models'] if m['id'] == mid)
        restored_model = next(m for m in units(restored, variable)[unit]['models'] if m['id'] == mid)
        for field in ['researcher_review', 'display_ppr_excluded_group_ids', 'recorded_review_pending']:
            restored_model.pop(field, None)
            if field in old_model:
                restored_model[field] = copy.deepcopy(old_model[field])
        assert restored == before[filename], filename + ': unrelated payload changed'
        assert units(after, variable)['LME_013'] == units(before[filename], variable)['LME_013']
        results.append({'page': filename, 'source_review_exact': True,
                        'unrelated_payload_preserved': True, 'LME_013_preserved': True})
    assert all(sha(root / p) == value for p, value in hashes.items())
    # Confirm that all other central model rows are unchanged as well.
    with zipfile.ZipFile(previous) as a, zipfile.ZipFile(project) as b:
        old_rows = {(r['unit_id'], r['model_id']): r for _, r in table_rows(a, 'Models & coverage', 'Models')[3]}
        new_rows = {(r['unit_id'], r['model_id']): r for _, r in table_rows(b, 'Models & coverage', 'Models')[3]}
        assert old_rows.keys() == new_rows.keys()
        assert all(old_rows[k] == new_rows[k] for k in old_rows if k != (unit, mid))
        changed_parts = [n for n in a.namelist() if a.read(n) != b.read(n)]
    evidence = {'unit': unit, 'model': mid, 'reviewer': name, 'date': date,
                'excluded_seq': seq, 'excluded_group_ids': ['M. mammals'],
                'before_project_sha256': baseline_sha, 'project_sha256': sha(project),
                'report_sha256': sha(report), 'central_changed_parts': changed_parts,
                'other_central_model_rows_preserved': True, 'pages': results,
                'protected_file_sha256': hashes,
                'note': 'One shared writer lock covered baseline, registration, replay gate, publication and verification.'}
    (work / 'qa/registration_preservation.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps({k: evidence[k] for k in ['unit', 'model', 'reviewer', 'date', 'excluded_group_ids', 'pages']}, indent=2), flush=True)
