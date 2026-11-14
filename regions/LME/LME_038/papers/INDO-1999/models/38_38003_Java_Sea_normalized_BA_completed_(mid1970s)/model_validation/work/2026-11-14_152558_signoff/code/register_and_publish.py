"""Register the edited LME_038 review, then publish guarded scientific adoption.

Run from the repository root. The signed report is read-only. The same bounded
review gate used by refresh_reviews runs before any calculation artifact changes.
All writes are serialized and journaled so a later failure restores this batch.
"""
from pathlib import Path
import importlib.util
import json
import shutil
import sys
import tempfile
import time

ROOT = Path.cwd().resolve()
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
WORK = HERE.parent
MODEL = WORK.parents[2]
REGION = ROOT / 'regions/LME/LME_038/LME_038.xlsx'
PROJECT = ROOT / 'Project.xlsx'
REPORT = MODEL / 'model_validation/validation.docx'
REPORT_SHA = 'fb953ee0db8171931e70802643bc578700b6e66f50104e49362b37651f0b5ae5'
MODEL_SHA = 'dae4aa0106a4c47d7db6fa9764791e656d1ba75ae0e1756e6d20ec202180c9ba'
APPENDIX_SHA = '508fb7c4abf972c8b516235ec05091e52f6f0974f3fdfb01b2471468f8295078'

from tools.project_core.registry.writes import central_lock
from tools.project_core.registry.publication import publication_transaction
from tools.project_core.registry.discovery import region_directory
from tools.project_core.validation.researcher_review import _register_review, read_report
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.maps.build_html import _refresh_reviews, _build
from tools.project_core.calculations.coverage import ensure_validated_coverage
from tools.project_core.registry.update_project import _update
from tools.project_core.workbooks.workbooks import sha


def load_local(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    started = time.time()
    for directory in ('inputs', 'outputs', 'qa'):
        (WORK / directory).mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(WORK / 'outputs')
    assert sha(REPORT) == REPORT_SHA, 'Signed source changed; reread before registration'
    assert sha(MODEL / 'model.json') == MODEL_SHA, 'Canonical model changed'
    assert sha(MODEL / 'model_validation/taxon_mapping.xlsx') == APPENDIX_SHA
    name, date, summary = read_report(ROOT, REPORT, MODEL.name)
    assert (name, date, summary.get('status', 'Validated by researcher')) == ('Ido Carmel', '2026-11-14', 'Validated by researcher')
    verify_report(REPORT)
    adopter = load_local('adopt_current_diagnostics')
    previous = WORK / 'inputs/Project_before_registration.xlsx'
    with central_lock(ROOT), publication_transaction(
            ROOT, extra_region_paths=[REGION], extra_model_dirs=[MODEL]) as publication:
        # This snapshot is taken while holding the shared writer lock.
        if previous.exists() and sha(previous) != sha(PROJECT):
            raise ValueError('Prior registration snapshot differs; preserve it and inspect sequencing')
        if not previous.exists():
            shutil.copyfile(PROJECT, previous)
        print('Registering actual signed source and Marine mammals seq 27', flush=True)
        _register_review(PROJECT, REPORT, 'LME_038', MODEL.name, [27])
        publication.checkpoint([PROJECT])
        _refresh_reviews(PROJECT, previous, ['LME_038'],
                         model_ids={'LME_038': MODEL.name}, publish=False)
        print('Bounded source, workbook-part and pre-registration page gates passed', flush=True)
        adopted = adopter.apply(publication)
        print('Current reviewed diagnostics adopted; checking full validated inventory', flush=True)
        coverage = ensure_validated_coverage(ROOT, lock_held=True)
        publication.checkpoint(coverage.get('written_paths', coverage.get('written_region_paths', [])),
                               fingerprints=coverage.get('written_hashes'))
        changed = set(coverage['changed_units']) | {'LME_038'}
        _update(ROOT, [region_directory(ROOT, unit) / (unit + '.xlsx') for unit in sorted(changed)], False)
        publication.checkpoint([PROJECT])
        _build(PROJECT, only_units=changed)
        verification = load_local('verify_registration').verify(
            WORK / 'inputs/pre_adoption/LME_038.xlsx',
            WORK / 'qa/registration_verification.json')
        assert sha(REPORT) == REPORT_SHA
        assert sha(MODEL / 'model.json') == MODEL_SHA
        assert sha(MODEL / 'model_validation/taxon_mapping.xlsx') == APPENDIX_SHA
        result = {'unit_id': 'LME_038', 'model_id': MODEL.name,
                  'researcher': name, 'review_date': date, 'excluded_seq': [27],
                  'excluded_group_ids': ['Marine mammals'], 'bounded_gate': 'PASS',
                  'project_before_sha256': sha(previous), 'project_after_sha256': sha(PROJECT),
                  'report_sha256': sha(REPORT), 'changed_units': sorted(changed),
                  'adoption': adopted, 'coverage': coverage,
                  'source_to_page_verification_passed': verification['passed'],
                  'elapsed_seconds': time.time() - started}
        (WORK / 'qa/registration_publication.json').write_text(
            json.dumps(result, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')
    print(json.dumps({'published': True, 'project_sha256': sha(PROJECT),
                      'changed_units': sorted(changed), 'seconds': time.time() - started}), flush=True)


if __name__ == '__main__':
    main()
