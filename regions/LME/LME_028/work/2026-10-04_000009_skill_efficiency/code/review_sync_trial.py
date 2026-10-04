"""Real signed rejection re-registration in an isolated copy; no scientific calls."""
import copy
import json
import re
import shutil
import sys
import time
import urllib.parse
import zipfile
from pathlib import Path
from xml.etree import ElementTree as E

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').exists())
RUN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records, sha
from tools.project_core.registry.discovery import resolve_model
from tools.project_core.validation.researcher_review import read_report, register_review
from tools.project_core.validation.researcher_review import STATUS
from tools.project_core.maps.build_html import refresh_reviews

base = RUN / 'outputs/review_project'
unit = sys.argv[1] if len(sys.argv) > 1 else 'LME_027'
region = ROOT / 'regions/LME' / unit
book = read_book(region / (unit + '.xlsx'), sheets=['Overview'])
selected = dict(book['Overview']['Settings'][1])['selected_model_id']
model = resolve_model(region, selected)
report = model.parent / 'model_validation/validation.docx'
paths = [ROOT / 'Project.xlsx', region / (unit + '.xlsx'), model, report,
         ROOT / 'interactive_map/index.html', ROOT / 'interactive_map/trends.html']
directories = []
missing_targets = []
with zipfile.ZipFile(report) as archive:
    for link in E.fromstring(archive.read('word/_rels/document.xml.rels')):
        if not link.get('Type', '').endswith('/hyperlink'): continue
        target = link.get('Target', '')
        if urllib.parse.urlsplit(target).scheme or target.startswith('#'): continue
        source = (report.parent / urllib.parse.unquote(target.split('#')[0])).resolve()
        if not source.is_relative_to(ROOT) or not source.exists():
            missing_targets.append(target)
            continue
        if source.is_file(): paths.append(source)
        else: directories.append(source)
for source in directories: (base / source.relative_to(ROOT)).mkdir(parents=True, exist_ok=True)
for source in paths:
    target = base / source.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
project = base / 'Project.xlsx'; isolated_report = base / report.relative_to(ROOT)
before = base / 'Project_before_registration.xlsx'; shutil.copyfile(project, before)
protected = {p: sha(p) for p in [base / model.relative_to(ROOT), isolated_report, base / (region / (unit + '.xlsx')).relative_to(ROOT)]}
def payload(path, variable):
    text = path.read_text(encoding='utf8'); start = text.index('const ' + variable + '=') + len('const ' + variable + '=')
    return json.JSONDecoder().raw_decode(text, start)[0]
old = {name: payload(base / 'interactive_map' / name, variable) for name, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]}
started = time.perf_counter()
try:
    name, date, source = read_report(base, isolated_report, selected)
except ValueError as error:
    assert missing_targets and all(sha(p) == wanted for p, wanted in protected.items())
    result = {'role': 'real signed source guard trial; no source repair', 'unit_id': unit,
              'model_id': selected, 'source_report_sha256': sha(isolated_report),
              'incomplete_stage': 'review registration and page refresh',
              'blocked_reason': str(error), 'original_missing_local_targets': missing_targets,
              'source_and_copy_bytes_preserved': True, 'engine_calls': 0,
              'live_project_writes': 0, 'isolated_project_writes': 0,
              'full_pipeline_replication': False}
    (RUN / 'qa/review_sync_trial.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result))
    sys.exit(0)
status = source.get('status', STATUS)
values = register_review(project, isolated_report, unit, selected, [])
refresh_reviews(project, before, [unit])
elapsed = time.perf_counter() - started
central = records(read_book(project, sheets=['Models & coverage']), 'Models & coverage', 'Models')
row = next(r for r in central if (r['unit_id'], r['model_id']) == (unit, selected))
assert (row['researcher_name'], row['researcher_review_date']) == (name, date)
assert row['researcher_review_status'] == status
assert row['validation_report_sha256'] == sha(isolated_report)
checks = []
for filename, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]:
    page = base / 'interactive_map' / filename; new = payload(page, variable)
    units = new['network']['units'] if variable == 'DB' else new['units']
    old_units = old[filename]['network']['units'] if variable == 'DB' else old[filename]['units']
    target = next(m for m in units[unit]['models'] if m['id'] == selected)
    original = next(m for m in old_units[unit]['models'] if m['id'] == selected)
    review = target['researcher_review']
    for field in ['verdict', 'reason']:
        assert review.get(field) == source.get(field)
    assert review['researcher_name'] == name and review['review_date'] == date
    assert review['excluded_group_ids'] == [] and review['sections'] == source['sections']
    for field in ['researcher_review', 'display_ppr_excluded_group_ids']:
        original[field] = copy.deepcopy(target[field])
    assert old[filename] == new, 'Unrelated scientific payload changed'
    assert re.search(r'ppr-project-sha256" content="' + sha(project), page.read_text(encoding='utf8'))
    checks.append(filename)
assert all(sha(p) == wanted for p, wanted in protected.items())
result = {'role': 'bounded existing-tool regeneration of actual signed validation registration; saved source intentionally supplied',
          'unit_id': unit, 'model_id': selected, 'signer': name, 'signed_date': date,
          'status': status, 'verdict': source.get('verdict', 'MODEL VALIDATED'), 'reason': source.get('reason'),
          'source_report_sha256': sha(isolated_report), 'elapsed_seconds': elapsed,
          'registered_source_and_pages_equal': True, 'page_fingerprints_equal_current_project': True,
          'unrelated_payload_exact': True, 'canonical_model_regional_workbook_and_report_bytes_exact': True,
          'display_exclusions': [], 'approved_section_count': len(source['sections']), 'validated_filter_eligible': status == STATUS,
          'page_checks': checks, 'engine_calls': 0, 'regional_calculation_calls': 0,
          'full_build_calls': 0, 'source_word_edits': 0, 'live_project_writes': 0,
          'date_change_scenario': 'not fabricated in real signed source; existing synthetic regression covers latest-source date parsing',
          'full_pipeline_replication': False}
(RUN / 'qa/review_sync_validated_trial.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({k: result[k] for k in ['unit_id', 'status', 'signed_date', 'elapsed_seconds', 'unrelated_payload_exact']}))
