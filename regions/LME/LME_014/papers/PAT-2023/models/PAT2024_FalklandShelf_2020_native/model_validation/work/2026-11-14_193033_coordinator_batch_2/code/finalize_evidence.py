"""Save exact batch-2 receipts after publication and UI acceptance."""
from pathlib import Path
import hashlib
import importlib.util
import json

RUN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('batch2', RUN / 'code/combined_publication.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
ROOT = batch.ROOT

def read(path):
    return json.loads(path.read_text('utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

result = read(RUN / 'qa/combined_publication.json')
controls = read(RUN / 'qa/published_controls.json')
ui = read(RUN / 'qa/ui_verification.json')
authority = read(RUN / 'inputs/authorized_scope.json')
assert result['passed'] and controls['passed']
assert ui['passed'] or ui.get('status') == 'blocked_by_computer_use_policy'
assert ui['project_sha256'] == result['project_sha256'] == sha(ROOT / 'Project.xlsx')
assert not (ROOT / '.project-write.lock').exists()
for name, digest in result['page_hashes'].items():
    assert sha(ROOT / 'interactive_map' / name) == digest
for unit in batch.ORDER:
    model = batch.MODELS[unit]
    name, date, summary = __import__(
        'tools.project_core.validation.researcher_review', fromlist=['read_report']
    ).read_report(ROOT, model / 'model_validation/validation.docx', model.name)
    receipt = {
        'schema_version': 1, 'unit_id': unit, 'model_id': model.name,
        'report_sha256': sha(model / 'model_validation/validation.docx'),
        'canonical_sha256': sha(model / 'model.json'),
        'researcher_name': name, 'review_date': date,
        'status': summary.get('status', 'Validated by researcher'),
        'excluded_seq': authority['units'][unit]['excluded_seq'],
        'project_sha256': result['project_sha256'], 'pages': result['page_hashes'],
        'publication_timestamp_utc': result['timestamp_utc'],
        'scientific_runs': 0, 'new_monte_carlo_draws': 0,
        'browser_acceptance_passed': ui['passed'],
        'browser_acceptance_limitation': ui.get('reason'),
        'scope': 'Authorized signed decision and retained package publication; no renewed scientific approval.',
        'retained_numeric_adoption': unit != 'LME_037',
        'evidence': {key: (RUN / 'qa' / filename).relative_to(ROOT).as_posix()
                     for key, filename in [('publication', 'combined_publication.json'),
                                           ('controls', 'published_controls.json'),
                                           ('browser', 'ui_verification.json')]},
    }
    target = model / 'model_validation/evidence/source_review/coordinator_publication_20261114.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'publication_receipts': len(batch.ORDER), 'removed_files': 0,
                  'retained': 'Prepared package and baseline evidence retained for provenance.'}))
