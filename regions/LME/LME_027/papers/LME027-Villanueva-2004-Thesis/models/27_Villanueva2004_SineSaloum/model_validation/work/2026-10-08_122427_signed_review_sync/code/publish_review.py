"""Publish the actual signed candidate rejection and prove bounded preservation."""
import copy
import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from tools.project_core.registry.writes import central_lock
from tools.project_core.registry.discovery import project_root, resolve_model, region_directory
from tools.project_core.validation.researcher_review import (
    FIELDS, sha, read_report, _register_review, table_rows, approved_review)
from tools.project_core.maps.build_html import _refresh_reviews, atomic_text


def embedded(path, variable):
    text = path.read_text(encoding='utf-8')
    start = text.index('const '+variable+'=')+len('const '+variable+'=')
    return json.JSONDecoder().raw_decode(text, start)[0]


def model_rows(path):
    with zipfile.ZipFile(path) as archive:
        return {(r['unit_id'], r['model_id']): r for _, r in table_rows(archive, 'Models & coverage', 'Models')[3]}


def main():
    root = project_root(Path(__file__))
    work = Path(__file__).resolve().parents[1]
    unit_id = 'LME_027'
    model_id = '27_Villanueva2004_SineSaloum'
    key = (unit_id, model_id)
    model = resolve_model(region_directory(root, unit_id), model_id)
    report = model.parent/'model_validation/validation.docx'
    regional = region_directory(root, unit_id)/(unit_id+'.xlsx')
    project = root/'Project.xlsx'
    pages = {name: root/'interactive_map'/name for name in ['index.html', 'trends.html']}
    prior = work/'inputs/Project_before_registration.xlsx'
    prior.parent.mkdir(parents=True, exist_ok=True)
    evidence = work/'qa/registration_result.json'
    evidence.parent.mkdir(parents=True, exist_ok=True)
    with central_lock(root):
        name, date, source_summary = read_report(root, report, model_id)
        assert source_summary['status'] == 'Disqualified by researcher'
        assert name == 'Ido Carmel' and date == '2026-10-08'
        before_rows = model_rows(project)
        assert before_rows[key]['selected'] in {'0', 'False', 'false'}
        # Hash all region scientific/researcher artifacts, excluding only this
        # administrative work directory. No source/Word/snapshot is rewritten.
        protected = {str(p.relative_to(root)): sha(p)
                     for p in regional.parent.rglob('*') if p.is_file()
                     and not p.is_relative_to(work)}
        before_pages = {name: path.read_text(encoding='utf-8') for name, path in pages.items()}
        payloads = {name: embedded(path, 'DB' if name == 'index.html' else 'SERIES_DB')
                    for name, path in pages.items()}
        before_project = sha(project)
        shutil.copyfile(project, prior)
        try:
            values = _register_review(project, report, unit_id, model_id, [])
            _refresh_reviews(project, prior, [unit_id], model_ids={unit_id: model_id})
            after_rows = model_rows(project)
            assert before_rows.keys() == after_rows.keys()
            for identity, old in before_rows.items():
                for field, value in old.items():
                    if identity != key or field not in FIELDS:
                        assert after_rows[identity].get(field) == value, (identity, field)
            review = approved_review(root, after_rows[key], {})
            assert review['reason'] == source_summary['reason']
            assert (review['researcher_name'], review['review_date']) == (name, date)
            assert review['report_sha256'] == sha(report) and review['model_sha256'] == sha(model)
            assert review['review_scope'] == 'model_source'
            assert not values['reviewed_calculation_input_sha256']
            page_checks = {}
            for filename, old in payloads.items():
                new = embedded(pages[filename], 'DB' if filename == 'index.html' else 'SERIES_DB')
                old_units = old['network']['units'] if filename == 'index.html' else old['units']
                new_units = new['network']['units'] if filename == 'index.html' else new['units']
                old_unit, new_unit = old_units[unit_id], new_units[unit_id]
                assert new_unit['default_model'] == old_unit['default_model']
                assert new_units['LME_047'] == old_units['LME_047']
                entries = [m for m in new_unit['models'] if m['id'] == model_id]
                assert len(entries) == 1
                candidate = entries[0]
                assert candidate['researcher_review'] == review
                assert candidate['display_ppr_excluded_group_ids'] == []
                assert candidate['verified'] is False and candidate['scopes'] == {}
                assert 'workbook' not in candidate and 'group_data' not in candidate
                assert candidate['source'] == str(model.relative_to(root)).replace('\\', '/')
                # Removing the newly added candidate must recover the entire
                # previous payload exactly, including missing and FAIL values.
                comparable = copy.deepcopy(new)
                units = comparable['network']['units'] if filename == 'index.html' else comparable['units']
                units[unit_id]['models'] = [m for m in units[unit_id]['models'] if m['id'] != model_id]
                assert comparable == old
                assert f'<meta name="ppr-project-sha256" content="{sha(project)}">' in pages[filename].read_text(encoding='utf-8')
                page_checks[filename] = {'default_model_unchanged': new_unit['default_model'],
                                         'model_ids': [m['id'] for m in new_unit['models']],
                                         'all_previous_embedded_data_unchanged': True,
                                         'LME_047_unchanged': True, 'sha256': sha(pages[filename])}
            assert all(sha(root/path) == value for path, value in protected.items())
            qa = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
                  'unit_id': unit_id, 'model_id': model_id,
                  'project_sha256_before': before_project, 'project_sha256_after': sha(project),
                  'source_review': review, 'protected_artifact_sha256': protected,
                  'regional_workbook_sha256': sha(regional), 'page_checks': page_checks,
                  'central_changes': 'Target model review fields and native red styles only; registration replay checked every decompressed ZIP part.',
                  'scientific_changes': False, 'selection_changes': False,
                  'temporary_project_snapshot_removed_after_success': True}
            evidence.write_text(json.dumps(qa, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        except Exception:
            # Restore coherently while holding the shared writer lock.
            fd, rollback = tempfile.mkstemp(suffix='.xlsx', dir=root); os.close(fd)
            shutil.copyfile(prior, rollback); os.replace(rollback, project)
            for filename, text in before_pages.items(): atomic_text(pages[filename], text)
            raise
        prior.unlink()
    print(json.dumps({'status': 'published and verified', 'model_id': model_id,
                      'verdict': review['verdict'], 'reason': review['reason'],
                      'researcher': name, 'review_date': date,
                      'default_unchanged': True, 'qa': str(evidence.relative_to(root))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
