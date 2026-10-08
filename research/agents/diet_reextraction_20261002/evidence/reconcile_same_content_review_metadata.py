"""Bounded, independently verified same-content review metadata reconciliation."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from researcher_review import read_report, table_rows, sheet_xml, column, approved_review

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def join_text(value):
    if isinstance(value, dict):
        return {k: join_text(v) for k, v in value.items()}
    if isinstance(value, list):
        result = []
        for item in value:
            item = join_text(item)
            if (isinstance(item, dict) and set(item) == {'text'} and result
                    and isinstance(result[-1], dict) and set(result[-1]) == {'text'}):
                result[-1]['text'] += item['text']
            else:
                result.append(item)
        return result
    return value

def main(apply):
    project = ROOT / 'Project.xlsx'
    before_hash = sha(project)
    with zipfile.ZipFile(project) as archive:
        _, headers, _, rows = table_rows(archive, 'Models & coverage', 'Models')
        sheet_path, _ = sheet_xml(archive, 'Models & coverage')
        parts = [(info, archive.read(info.filename)) for info in archive.infolist()]
    replacements = {}
    proofs = []
    guards = {project: before_hash}
    expected_rows = copy.deepcopy([data for _, data in rows])
    for unit in ('LME_032', 'LME_036'):
        matches = [(i, row, data) for i, (row, data) in enumerate(rows)
                   if data.get('unit_id') == unit and data.get('researcher_review_status') == 'Validated by researcher']
        assert len(matches) == 1, (unit, 'expected one approved review')
        index, row, metadata = matches[0]
        report = ROOT / metadata['validation_report_path']
        model = ROOT / metadata['model_path']
        region_book = ROOT / 'regions' / unit / (unit + '.xlsx')
        guards.update({report: sha(report), model: sha(model), region_book: sha(region_book)})
        assert sha(model) == metadata['reviewed_model_sha256'], (unit, 'reviewed model changed')
        with zipfile.ZipFile(region_book) as archive:
            _, _, _, settings = table_rows(archive, 'Overview', 'Settings')
            settings = {data['field']: data['value'] for _, data in settings}
        assert settings['selected_model_id'] == metadata['model_id']
        assert settings['calculation_input_sha256'] == metadata['reviewed_calculation_input_sha256']
        name, date, current = read_report(ROOT, report, metadata['model_id'])
        assert (name, date) == (metadata['researcher_name'], metadata['researcher_review_date'])
        stored = json.loads(metadata['researcher_review_summary'])
        stored_content = {k: v for k, v in stored.items() if k != 'excluded_group_ids'}
        assert join_text(stored_content) == join_text(current), (unit, 'review content changed')
        revised = copy.deepcopy(current)
        if 'excluded_group_ids' in stored:
            revised['excluded_group_ids'] = stored['excluded_group_ids']
        changes = {'validation_report_sha256': sha(report)}
        if stored_content != current:
            changes['researcher_review_summary'] = json.dumps(revised, ensure_ascii=False)
        for key, value in changes.items():
            address = column(headers.index(key) + 1) + row.get('r')
            replacements[address] = value
            expected_rows[index][key] = value
        proofs.append({'unit_id': unit, 'researcher_name': name, 'review_date': date,
                       'same_complete_content_after_adjacent_text_join': True,
                       'excluded_group_ids_preserved': stored.get('excluded_group_ids', []),
                       'before_report_sha256': metadata['validation_report_sha256'],
                       'current_report_sha256': sha(report), 'changed_fields': list(changes)})
    xml = dict((info.filename, data) for info, data in parts)[sheet_path].decode('utf-8')
    for address, value in replacements.items():
        pattern = r'<c\b(?=[^>]*\br="' + re.escape(address) + r'")[^>]*>.*?</c>'
        matches = list(re.finditer(pattern, xml, re.S))
        assert len(matches) == 1, address
        original = matches[0].group()
        opening = original[:original.index('>')]
        opening = re.sub(r'\s+t="[^"]*"', '', opening)
        replacement = opening + ' t="inlineStr"><is><t>' + escape(value) + '</t></is></c>'
        xml = xml[:matches[0].start()] + replacement + xml[matches[0].end():]
    evidence = Path(__file__).parent
    candidate = evidence / 'Project_same_content_review_candidate.xlsx'
    with zipfile.ZipFile(candidate, 'w') as archive:
        for info, data in parts:
            archive.writestr(copy.copy(info), xml.encode('utf-8') if info.filename == sheet_path else data)
    with zipfile.ZipFile(candidate) as archive:
        _, _, _, updated_rows = table_rows(archive, 'Models & coverage', 'Models')
        assert [data for _, data in updated_rows] == expected_rows, 'Unexpected central cell changes'
        assert archive.namelist() == [info.filename for info, _ in parts]
        assert all(archive.read(info.filename) == data for info, data in parts if info.filename != sheet_path)
    for unit in ('LME_032', 'LME_036'):
        metadata = next(d for _, d in updated_rows if d.get('unit_id') == unit and d.get('researcher_review_status') == 'Validated by researcher')
        book = {}
        with zipfile.ZipFile(ROOT / 'regions' / unit / (unit + '.xlsx')) as archive:
            for sheet, table in [('Overview', 'Settings'), ('Selected model groups', 'Groups')]:
                _, head, _, rr = table_rows(archive, sheet, table)
                head = head or list(rr[0][1])
                book[sheet] = {table: (head, [[data.get(k) for k in head] for _, data in rr])}
        assert approved_review(ROOT, metadata, book)
    receipt = {'project_before_sha256': before_hash, 'project_candidate_sha256': sha(candidate),
               'changed_cells': replacements, 'proofs': proofs,
               'all_other_project_cells_and_zip_parts_unchanged': True, 'applied': False}
    (evidence / 'same_content_review_metadata_receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding='utf-8')
    if apply:
        assert all(sha(path) == identity for path, identity in guards.items()), 'Concurrent source change'
        backup = evidence / 'original_inputs' / before_hash / 'Project.xlsx'
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(project.read_bytes())
        assert sha(backup) == before_hash
        project.write_bytes(candidate.read_bytes())
        assert sha(project) == receipt['project_candidate_sha256']
        receipt.update(applied=True, project_after_sha256=sha(project))
        (evidence / 'same_content_review_metadata_receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'changed_cells'}, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    main(parser.parse_args().apply)
