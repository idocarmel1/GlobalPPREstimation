"""One-time, authorized EEZ_941 signed-review registration; no publication."""
import copy
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from tools.project_core.registry.discovery import project_root, region_directory, resolve_model
from tools.project_core.registry.writes import central_lock
from tools.project_core.validation.researcher_review import (
    FIELDS, S, STATUS, _register_review, column, read_report, sha, sheet_xml, table_rows,
)
from tools.project_core.validation.validation_percentage_format import verify_report


def main():
    root = project_root(Path(__file__))
    unit = 'EEZ_941'
    model_id = '941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
    model = resolve_model(region_directory(root, unit), model_id)
    report = model.parent / 'model_validation/validation.docx'
    destination = Path(__file__).resolve().parent
    project = root / 'Project.xlsx'
    previous = destination / 'Project_before_registration.xlsx'
    if previous.exists():
        raise ValueError('Existing pre-registration snapshot: inspect receipt instead of rerunning')

    with central_lock(root):
        name, date, source = read_report(root, report, model_id)
        assert source.get('status', STATUS) == STATUS
        assert 'EE_floor=0.1' in source['sections'][2]['rows'][0]['text']
        verify_report(report)
        regional = region_directory(root, unit) / (unit + '.xlsx')
        with ZipFile(regional) as archive:
            _, _, _, settings_rows = table_rows(archive, 'Overview', 'Settings')
            settings = {r['field']: r['value'] for _, r in settings_rows}
        assert settings['selected_model_id'] == model_id
        assert (settings.get('results_model_id') or settings['selected_model_id']) == model_id

        protected = [model, report, report.parent/'taxon_mapping.xlsx', regional]
        protected += [p for p in (model.parent/'results').rglob('*') if p.is_file()]
        protected += [p for p in (root/'interactive_map').rglob('*') if p.is_file()]
        before_hashes = {p.relative_to(root).as_posix(): sha(p) for p in protected}
        with ZipFile(project) as archive:
            before_parts = {p: archive.read(p) for p in archive.namelist()}
            sheet_path, _ = sheet_xml(archive, 'Models & coverage')
            _, headers, _, rows = table_rows(archive, 'Models & coverage', 'Models')
            before_rows = [r for _, r in rows]
            matches = [(i, xml, r) for i, (xml, r) in enumerate(rows)
                       if r.get('unit_id') == unit and r.get('model_id') == model_id]
            assert len(matches) == 1
            target_index, target_xml, target = matches[0]
            assert not target.get('researcher_review_status'), 'Already registered; inspect before re-registering'
            assert (root/target['model_path']).resolve() == model.resolve()
            row_number = target_xml.get('r')
        shutil.copyfile(project, previous)
        before_project_sha = sha(previous)
        assert sha(project) == before_project_sha

        # Same registrar used by register_review; the shared lock also protects
        # the required pre-registration snapshot and verification interval.
        values = _register_review(project, report, unit, model_id, [])
        with ZipFile(project) as archive:
            assert archive.testzip() is None
            assert set(archive.namelist()) == set(before_parts)
            changed = [p for p, data in before_parts.items() if archive.read(p) != data]
            allowed = {sheet_path, 'xl/styles.xml'}
            for p, data in before_parts.items():
                if p.startswith('xl/tables/') and p.endswith('.xml'):
                    table = ET.fromstring(data)
                    if [c.get('name') for c in table.find(f'{{{S}}}tableColumns')] == headers:
                        allowed.add(p)
            assert set(changed).issubset(allowed), changed
            sheet, after_headers, _, rows = table_rows(archive, 'Models & coverage', 'Models')
            after_rows = [r for _, r in rows]
            assert headers == after_headers
            assert len(before_rows) == len(after_rows)
            for i, (old, new) in enumerate(zip(before_rows, after_rows)):
                expected = dict(old)
                if i == target_index:
                    expected.update(values)
                assert new == expected, f'Unexpected row change: {i}'
            final = after_rows[target_index]
            fresh_name, fresh_date, fresh_source = read_report(root, report, model_id)
            fresh_source['excluded_group_ids'] = []
            assert json.loads(final['researcher_review_summary']) == fresh_source
            assert final['researcher_name'] == fresh_name == name
            assert final['researcher_review_date'] == fresh_date == date
            assert final['researcher_review_status'] == STATUS
            assert final['validation_report_sha256'] == sha(report)
            assert final['reviewed_model_sha256'] == sha(model)
            assert final['reviewed_calculation_input_sha256'] == settings.get('calculation_input_sha256', '')
            styles = ET.fromstring(archive.read('xl/styles.xml'))
            old_styles = ET.fromstring(before_parts['xl/styles.xml'])
            for tag in ['fonts', 'cellXfs']:
                old_items = list(old_styles.find(f'{{{S}}}{tag}'))
                new_items = list(styles.find(f'{{{S}}}{tag}'))
                assert [ET.tostring(x) for x in old_items] == [ET.tostring(x) for x in new_items[:len(old_items)]]
            for field in ['model_id', 'researcher_review_status']:
                address = column(headers.index(field)+1)+row_number
                cell = sheet.find(f'.//{{{S}}}c[@r="{address}"]')
                style = styles.find(f'{{{S}}}cellXfs')[int(cell.get('s'))]
                font = styles.find(f'{{{S}}}fonts')[int(style.get('fontId'))]
                assert font.find(f'{{{S}}}color').get('rgb') == 'FF187344'

        assert before_hashes == {p.relative_to(root).as_posix(): sha(p) for p in protected}
        receipt = {
            'schema_version': 1,
            'registered_at_utc': datetime.now(timezone.utc).isoformat(),
            'unit_id': unit, 'model_id': model_id,
            'authorization': 'Register edited validated report in Project.xlsx; final EE floor 0.1; defer map and trends.',
            'registration': values,
            'chosen_ee_floor': 0.1, 'excluded_group_ids': [],
            'previous_project': previous.relative_to(root).as_posix(),
            'project_sha256_before': before_project_sha,
            'project_sha256_after': sha(project),
            'changed_workbook_parts': changed,
            'checks': {
                'percentage_format': 'PASS',
                'signed_source_equality': 'PASS',
                'other_model_rows_and_target_nonreview_fields_unchanged': 'PASS',
                'other_workbook_parts_unchanged': 'PASS',
                'prior_fonts_and_styles_preserved': 'PASS',
                'validated_model_and_status_green': 'PASS',
                'protected_files_unchanged': 'PASS',
            },
            'protected_file_sha256': before_hashes,
            'publication': {'map': 'deferred by user', 'trends': 'deferred by user',
                            'pre_registration_snapshot_retained_for_bounded_refresh': True},
            'scientific_state_note': (
                'Signed wording including saved results are for EE_floor=0.1 is preserved verbatim. '
                'Reviewed GE/TE diagnostics and model-local floor-0.1 evidence use that configuration. '
                'The saved regional numerical tables still reflect the earlier no-floor calculation. '
                'This registration changes review metadata only; it does not migrate numerical results '
                'or claim that map/trends publication has occurred.'),
        }
        (destination/'registration_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({k: receipt[k] for k in ['unit_id','model_id','chosen_ee_floor','changed_workbook_parts','checks','publication']}, indent=2))
        print('Registered:', name, date, STATUS)


if __name__ == '__main__':
    main()
