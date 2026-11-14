"""Register the latest signed rejection, preserving a deferred-publication baseline."""
from pathlib import Path
from datetime import datetime, timezone
from zipfile import ZipFile
import hashlib
import json
import shutil
import sys
import time

ROOT = Path.cwd().resolve()
sys.path.insert(0, str(ROOT))
from tools.project_core.registry.discovery import region_directory, resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.validation.researcher_review import (
    FIELDS, S, _register_review, approved_review, read_report, sheet_xml, table_rows,
)
from tools.project_core.workbooks.workbooks import read_book

UNIT = 'LME_050'
MODEL_ID = '50_502013_Coastal_Kyoto_Inoue_(2013)'
MODEL = resolve_model(region_directory(ROOT, UNIT), MODEL_ID)
REPORT = MODEL.parent / 'model_validation/validation.docx'
PROJECT = ROOT / 'Project.xlsx'
REGIONAL = region_directory(ROOT, UNIT) / (UNIT + '.xlsx')
RUN = Path(__file__).resolve().parents[1]
EXPECTED_REPORT_SHA = '94b703cf96da99a1626878b65e6005abe0e8afd4e16cd644e14c3c785f225683'

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def relative(path):
    return path.relative_to(ROOT).as_posix()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def row_record(path):
    with ZipFile(path) as archive:
        sheet, headers, header, rows = table_rows(archive, 'Models & coverage', 'Models')
        target = [(r, d) for r, d in rows if (d.get('unit_id'), d.get('model_id')) == (UNIT, MODEL_ID)]
        assert len(target) == 1
        return sheet_xml(archive, 'Models & coverage')[0], headers, header, rows, target[0]

def register_locked():
    # This is exactly the canonical register_review wrapper's locked core;
    # keeping its lock here also makes the snapshot and acceptance checks atomic.
    assert sha(REPORT) == EXPECTED_REPORT_SHA, 'Signed report changed; re-read before registration'
    reviewer, date, source = read_report(ROOT, REPORT, MODEL_ID)
    assert source['status'] == 'Disqualified by researcher'
    assert source['verdict'] == 'MODEL DISQUALIFIED' and source['sections'] == []
    protected = {MODEL, MODEL.parent/'model_notes.md', REPORT,
                 MODEL.parent/'model_validation/taxon_mapping.xlsx', REGIONAL}
    for folder in [MODEL.parent/'results', MODEL.parent/'extracted_tables',
                   MODEL.parent/'model_validation/evidence/ee_floor_on']:
        protected.update(p for p in folder.rglob('*') if p.is_file())
    before_hashes = {relative(p): sha(p) for p in sorted(protected) if p.is_file()}
    pages = {relative(p): sha(p) for p in (ROOT/'interactive_map').glob('*.html')}
    before = RUN/'inputs/Project_before_registration_retry.xlsx'
    before.parent.mkdir(parents=True, exist_ok=True)
    assert not before.exists(), 'Pre-registration snapshot already exists; do not overwrite'
    shutil.copyfile(PROJECT, before)
    assert sha(before) == sha(PROJECT)
    write(RUN/'qa/pre_registration_fingerprints.json', {
        'project_snapshot': relative(before), 'project_sha256': sha(before),
        'protected_file_sha256': before_hashes, 'publication_sha256': pages,
    })
    returned = _register_review(PROJECT, REPORT, UNIT, MODEL_ID, [])
    before_sheet, before_headers, _, before_rows, (before_element, before_row) = row_record(before)
    after_sheet, after_headers, _, after_rows, (after_element, after_row) = row_record(PROJECT)
    assert before_sheet == after_sheet and before_headers == after_headers
    assert len(before_rows) == len(after_rows)
    changed_rows = []
    for (old_element, old), (new_element, new) in zip(before_rows, after_rows):
        assert old_element.get('r') == new_element.get('r')
        changed = {key for key in old.keys() | new.keys() if old.get(key) != new.get(key)}
        if changed:
            assert (new.get('unit_id'), new.get('model_id')) == (UNIT, MODEL_ID)
            assert changed <= set(FIELDS)
            changed_rows.append({'row': new_element.get('r'), 'fields': sorted(changed)})
    assert len(changed_rows) == 1
    for key, value in returned.items():
        assert after_row[key] == value
    summary = json.loads(after_row['researcher_review_summary'])
    assert summary == dict(source, excluded_group_ids=[])
    assert (after_row['researcher_name'], after_row['researcher_review_date']) == (reviewer, date)
    assert after_row['validation_report_sha256'] == sha(REPORT) == EXPECTED_REPORT_SHA
    assert after_row['reviewed_model_sha256'] == sha(MODEL)
    active_review = approved_review(ROOT, after_row, read_book(REGIONAL))
    assert active_review['status'] == source['status'] and active_review['reason'] == source['reason']
    assert active_review['excluded_group_ids'] == []
    with ZipFile(before) as old, ZipFile(PROJECT) as new:
        assert set(old.namelist()) == set(new.namelist())
        changed_parts = [name for name in old.namelist() if old.read(name) != new.read(name)]
        assert all(name in {before_sheet, 'xl/styles.xml'} or name.startswith('xl/tables/') for name in changed_parts)
        # Preserve every other sheet cell, including rows outside the Models table.
        old_sheet = sheet_xml(old, 'Models & coverage')[1]
        new_sheet = sheet_xml(new, 'Models & coverage')[1]
        row_number = after_element.get('r')
        for sheet in [old_sheet, new_sheet]:
            data = sheet.find(f'{{{S}}}sheetData')
            for row in data:
                if row.get('r') == row_number:
                    for cell in list(row):
                        col = ''.join(c for c in cell.get('r') if c.isalpha())
                        from tools.project_core.validation.researcher_review import column_index
                        field = after_headers[column_index(col)-1] if column_index(col) <= len(after_headers) else None
                        if field in FIELDS:
                            row.remove(cell)
                        elif field == 'model_id':
                            cell.attrib.pop('s', None)
        from xml.etree import ElementTree as ET
        assert ET.tostring(old_sheet.find(f'{{{S}}}sheetData')) == ET.tostring(new_sheet.find(f'{{{S}}}sheetData'))
    assert all(sha(ROOT/path) == digest for path, digest in before_hashes.items()), 'Protected local inputs changed'
    assert all(sha(ROOT/path) == digest for path, digest in pages.items()), 'Publication files changed during registration'
    receipt = {
        'schema_version': 1, 'registered_at_utc': datetime.now(timezone.utc).isoformat(),
        'unit_id': UNIT, 'model_id': MODEL_ID, 'registration': returned,
        'pre_registration_project': {'path': relative(before), 'sha256': sha(before)},
        'registered_project_sha256': sha(PROJECT), 'changed_rows': changed_rows,
        'changed_workbook_parts': changed_parts, 'source_to_project_verification': 'PASS',
        'review_freshness_verification': 'PASS', 'protected_file_sha256': before_hashes,
        'unchanged_publication_sha256': pages,
        'map_and_trends': {'status': 'DEFERRED_BY_USER', 'coordinator_chat': 'Validate EEZ_598',
                           'publication_called': False,
                           'snapshot_retention': 'Retain until coordinator publication and source-equality checks pass'},
        'registrar': 'Canonical _register_review under central_lock, with no science or selection changes',
    }
    receipt_path = MODEL.parent/'model_validation/evidence/source_review/researcher_review_registration_20261114.json'
    write(receipt_path, receipt)
    write(RUN/'qa/registration_verification.json', receipt)
    print(json.dumps({'registered': True, 'status': source['status'], 'reviewer': reviewer,
                      'review_date': date, 'reason': source['reason'], 'changed_rows': changed_rows,
                      'changed_parts': changed_parts, 'protected_files': len(before_hashes),
                      'receipt': relative(receipt_path), 'snapshot': relative(before)}, ensure_ascii=True), flush=True)

if __name__ == '__main__':
    while True:
        try:
            with central_lock(ROOT):
                register_locked()
            break
        except ValueError as error:
            if not str(error).startswith('Another central writer holds .project-write.lock'):
                raise
            print('Waiting for the active central writer; no project or publication changes made.', flush=True)
            time.sleep(30)
