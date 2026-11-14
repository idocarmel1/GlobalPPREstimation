"""Register the actual signed review only; retain all numerical and HTML bytes."""
from pathlib import Path
import copy
import io
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from zipfile import ZipFile

ROOT = Path.cwd().resolve()
sys.path.insert(0, str(ROOT))
from tools.project_core.registry.discovery import region_directory, resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.validation.researcher_review import (
    _register_review, read_report, approved_review, table_rows, sheet_xml, FIELDS, S)
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.workbooks.workbooks import sha, read_book, records, overview

UNIT = 'LME_038'
MID = '38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
WORK = Path(__file__).resolve().parents[1]
REGION = region_directory(ROOT, UNIT) / (UNIT + '.xlsx')
MODEL = resolve_model(REGION.parent, MID).parent
REPORT = MODEL / 'model_validation/validation.docx'
PROJECT = ROOT / 'Project.xlsx'


def central(data):
    with ZipFile(io.BytesIO(data)) as archive:
        member, _ = sheet_xml(archive, 'Models & coverage')
        _, headers, _, values = table_rows(archive, 'Models & coverage', 'Models')
        return member, {(r['unit_id'], r['model_id']): r for _, r in values}, {
            name: archive.read(name) for name in archive.namelist()}


def main():
    watched = [REPORT, MODEL/'model.json', MODEL/'model_validation/taxon_mapping.xlsx', REGION,
               MODEL/'sppr_source.xlsx', MODEL/'results/regional_snapshot.xlsx',
               MODEL/'results/result_manifest.json',
               *(ROOT/'interactive_map'/name for name in ('index.html', 'trends.html', 'sources.html'))]
    with central_lock(ROOT):
        before_hashes = {p: sha(p) for p in watched}
        name, date, source = read_report(ROOT, REPORT, MID)
        assert (name, date, source.get('status', 'Validated by researcher')) == (
            'Ido Carmel', '2026-11-14', 'Validated by researcher')
        assert source['sections'][2]['rows'][0]['text'] == 'Removed groups from calculation:\nMarine mammals'
        assert before_hashes[REPORT] == 'fb953ee0db8171931e70802643bc578700b6e66f50104e49362b37651f0b5ae5'
        verify_report(REPORT)
        book = read_book(REGION, sheets=['Overview', 'Selected model groups'])
        settings = overview(book)
        assert (settings.get('results_model_id') or settings.get('selected_model_id')) == MID
        groups = [r for r in records(book, 'Selected model groups', 'Groups') if r['group_name'] == 'Marine mammals']
        assert len(groups) == 1 and int(groups[0]['seq']) == 27
        before = PROJECT.read_bytes()
        member, previous_rows, previous_parts = central(before)
        backup = WORK/'inputs/Project_before_project_only_registration.xlsx'
        if backup.exists() and backup.read_bytes() != before:
            raise ValueError('Existing Project-only backup differs; preserve it and inspect before retrying')
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(before)
        owned = None
        try:
            print('Registering LME_038 signed review only', flush=True)
            _register_review(PROJECT, REPORT, UNIT, MID, [27])
            owned = sha(PROJECT)
            _, current_rows, current_parts = central(PROJECT.read_bytes())
            target = current_rows[UNIT, MID]
            registered = json.loads(target['researcher_review_summary'])
            expected = copy.deepcopy(source)
            expected['excluded_group_ids'] = ['Marine mammals']
            assert registered == expected
            assert target['researcher_review_status'] == 'Validated by researcher'
            assert target['researcher_name'] == name and target['researcher_review_date'] == date
            assert target['validation_report_sha256'] == before_hashes[REPORT]
            assert target['reviewed_model_sha256'] == before_hashes[MODEL/'model.json']
            assert approved_review(ROOT, target, book) is not None
            assert set(previous_rows) == set(current_rows)
            for key, row in previous_rows.items():
                fields = set(row) - set(FIELDS) if key == (UNIT, MID) else set(row)
                assert all(row[field] == current_rows[key].get(field) for field in fields), key
            assert set(previous_parts) == set(current_parts)
            changed_parts = [name for name in previous_parts if previous_parts[name] != current_parts[name]]
            assert set(changed_parts) <= {member, 'xl/styles.xml'}, changed_parts
            assert all(sha(path) == value for path, value in before_hashes.items())
            assert sha(PROJECT) == owned
            qa = {'registered_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Project.xlsx review registration only',
                  'unit_id': UNIT, 'model_id': MID, 'researcher': name, 'review_date': date,
                  'status': target['researcher_review_status'], 'excluded_seq': [27],
                  'excluded_group_ids': registered['excluded_group_ids'], 'note': registered['note'],
                  'project_before_sha256': sha(backup), 'project_after_sha256': owned,
                  'pre_registration_backup': backup.relative_to(ROOT).as_posix(), 'changed_zip_parts': changed_parts,
                  'source_summary_equal': True, 'unrelated_central_rows_equal': True,
                  'preserved_files': {p.relative_to(ROOT).as_posix(): v for p, v in before_hashes.items()},
                  'map_and_trends_unchanged': True, 'numerical_adoption_performed': False,
                  'deferred_publication_chat': 'Validate EEZ_598'}
            destination = WORK/'qa/project_only_registration.json'
            destination.write_text(json.dumps(qa, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            print(json.dumps({key: qa[key] for key in ('status', 'researcher', 'review_date', 'excluded_group_ids',
                  'project_before_sha256', 'project_after_sha256', 'map_and_trends_unchanged')}), flush=True)
        except Exception:
            if owned and sha(PROJECT) == owned:
                restore = PROJECT.with_name('.lme038-review-rollback.xlsx')
                restore.write_bytes(before)
                os.replace(restore, PROJECT)
            raise


if __name__ == '__main__':
    main()
