"""Read-only, exact-source verification of the authorized LME038 signoff publication.

Run with the bundled Python after publication and pass the pre-coverage regional
workbook via --before-region. Only the JSON report under this run's qa/ is written.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as E
import zipfile

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from tools.project_core.validation.researcher_review import approved_review, read_report, table_rows
from tools.project_core.validation.validation_percentage_format import verify_report
from tools.project_core.workbooks.workbooks import digest_tables, overview, read_book, records

RUN = Path(__file__).resolve().parent.parent
UNIT = 'LME_038'
MODEL_ID = '38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
MODEL = ROOT / 'regions/LME/LME_038/papers/INDO-1999/models' / MODEL_ID
REPORT = MODEL / 'model_validation/validation.docx'
REGION = ROOT / 'regions/LME/LME_038/LME_038.xlsx'
APPENDIX = MODEL / 'model_validation/taxon_mapping.xlsx'
PROJECT = ROOT / 'Project.xlsx'
EXPECTED_HASHES = {
    REPORT: 'fb953ee0db8171931e70802643bc578700b6e66f50104e49362b37651f0b5ae5',
    MODEL / 'model.json': 'dae4aa0106a4c47d7db6fa9764791e656d1ba75ae0e1756e6d20ec202180c9ba',
    APPENDIX: '508fb7c4abf972c8b516235ec05091e52f6f0974f3fdfb01b2471468f8295078',
}
EXPECTED_NOTE = ('Following researcher review, marine mammals are excluded from displayed PPR. '
                 'Model loading, diagnostics and saved workbook calculations retain all groups.')
EXPECTED_REFERENCE = [
    'Reference: 2019 landings; all recorded catch labels, including zero catch and residual categories; no group filter.',
    '28 source groups (+1 computational import); 181 catch taxa.',
    'Simple-chain PPR totals 177,164,712.36 t C in 2019.',
    '39 labels lack a classic TL/coefficient; all have zero 2019 landings and zero annual PPR. Their TL and coefficient remain unavailable.',
    'Method: simple trophic chain using the saved taxon coefficients.',
]
EXPECTED_TABLE = [
    ['Overall confidence', 'Taxa (n)', 'Catch (%)', 'Simple-chain PPR (%)'],
    ['High', '56', '34%', '29%'], ['Medium', '75', '33%', '49%'],
    ['Low', '14', '2.1%', '2.7%'], ['Very low', '36', '31%', '20%'],
    ['Unresolved', '0', '0%', '0%'],
]
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
S = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
SCIENCE_TABLES = [('Catch', 'Catch'), ('Classic PPR', 'Taxa'), ('Classic PPR', 'Annual'),
                  ('NPP', 'NPP'), ('NPP', 'Provenance'), ('PPR', 'Matching'),
                  ('Selected model groups', 'Groups')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def visible_text(element):
    return ''.join((node.text or '') if node.tag == W + 't' else
                   '\n' if node.tag in {W + 'br', W + 'cr'} else
                   '\t' if node.tag == W + 'tab' else '' for node in element.iter())


def _verify(before_region):
    checks = []
    evidence = {'schema_version': 1, 'unit_id': UNIT, 'model_id': MODEL_ID,
                'checked_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks}

    def check(name, condition, detail=None):
        row = {'check': name, 'passed': bool(condition)}
        if detail is not None:
            row['detail'] = detail
        checks.append(row)

    watched = [PROJECT, REGION, REPORT, APPENDIX, MODEL / 'model.json', before_region,
               ROOT / 'interactive_map/index.html', ROOT / 'interactive_map/trends.html']
    before_hashes = {p: sha(p) for p in watched}
    evidence['input_sha256'] = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): h
                                for p, h in before_hashes.items()}
    for path, expected in EXPECTED_HASHES.items():
        check('preserved_source:' + path.name, before_hashes[path] == expected)

    name, date, summary = read_report(ROOT, REPORT, MODEL_ID)
    check('signed_identity_and_date', (name, date) == ('Ido Carmel', '2026-11-14'))
    check('validated_verdict', summary.get('status', 'Validated by researcher') == 'Validated by researcher')
    verify_report(REPORT)
    check('all_word_table_percentages_two_significant_digits', True)
    check('computed_exclusion_note', summary['note'] == EXPECTED_NOTE)

    with zipfile.ZipFile(REPORT) as archive:
        document = E.fromstring(archive.read('word/document.xml'))
        targets = {r.get('Id'): r.get('Target')
                   for r in E.fromstring(archive.read('word/_rels/document.xml.rels'))}
    fields = {}
    for table in document.findall('.//' + W + 'tbl'):
        for row in table.findall(W + 'tr'):
            cells = row.findall(W + 'tc')
            if len(cells) == 2:
                fields[visible_text(cells[0])] = '\n'.join(visible_text(p) for p in cells[1].findall(W + 'p'))
    check('exact_model_in_word', fields['Selected model'].startswith(MODEL_ID + '.'))
    check('exact_signed_verdict', fields['Review and reproducibility'] ==
          'Researcher name: Ido Carmel | review date: 14/11/2026\n\nMODEL VALIDATED')
    field_map = [('Model extraction', 0, 0), ('GE diagnostics', 1, 0), ('TE diagnostics', 1, 1),
                 ('SPPR calculation', 2, 0), ('Geographic fit', 3, 0)]
    for field, section, row in field_map:
        parsed = summary['sections'][section]['rows'][row]
        check('independent_word_text:' + field, fields[field] == parsed['text'])
        check('paragraph_segments:' + field,
              '\n'.join(''.join(segment['text'] for segment in paragraph)
                        for paragraph in parsed['paragraphs']) == fields[field])
    check('exact_removal_wording', fields['SPPR calculation'] == 'Removed groups from calculation:\nMarine mammals')
    manual = {tag: len(document.findall('.//' + W + tag)) for tag in ['br', 'cr', 'tab']}
    check('manual_breaks_preserved', manual == {'br': 2, 'cr': 0, 'tab': 0}, manual)
    intro, omitted, confidence_table, heading_index, table_index = [], [], None, None, None
    for index, child in enumerate(document.find(W + 'body')):
        if child.tag == W + 'p' and visible_text(child) == 'Taxon mapping and coverage':
            heading_index = index
            continue
        if heading_index is None:
            continue
        if child.tag == W + 'tbl':
            cells = [[visible_text(c) for c in row.findall(W + 'tc')] for row in child.findall(W + 'tr')]
            if cells and cells[0][0] == 'Overall confidence':
                confidence_table, table_index = cells, index
                break
        if child.tag == W + 'p':
            links = [targets.get(h.get(R + 'id'), '') for h in child.findall(W + 'hyperlink')]
            if any(unquote(urlsplit(link).path).lower().endswith('taxon_mapping.xlsx') for link in links):
                omitted.append({'body_index': index, 'text': visible_text(child), 'targets': links})
            else:
                intro.append(visible_text(child))
    confidence = summary['sections'][-1]
    check('confidence_body_boundary', (heading_index, table_index) == (2, 9))
    check('confidence_intro_exact', intro == EXPECTED_REFERENCE == confidence['reference'])
    check('confidence_table_exact', confidence_table == EXPECTED_TABLE == confidence['table'])
    check('appendix_link_paragraph_omitted', len(omitted) == 1 and omitted[0]['body_index'] == 8, omitted)
    check('appendix_path', confidence['appendix_path'] == APPENDIX.relative_to(ROOT).as_posix())

    sheets = ['Overview', 'Catch', 'Classic PPR', 'NPP', 'PPR', 'Selected model groups']
    current = read_book(REGION, sheets=sheets)
    previous = read_book(before_region, sheets=sheets)
    settings, previous_settings = overview(current), overview(previous)
    check('selection_preserved', settings.get('selected_model_id') == previous_settings.get('selected_model_id') == MODEL_ID)
    check('selection_rationale_preserved', settings.get('selection_rationale') == previous_settings.get('selection_rationale'))
    check('result_identity', (settings.get('results_model_id') or settings.get('selected_model_id')) == MODEL_ID)
    science = []
    for sheet, table in SCIENCE_TABLES:
        old = previous.get(sheet, {}).get(table)
        new = current.get(sheet, {}).get(table)
        old_hash = digest_tables([old]) if old is not None else None
        new_hash = digest_tables([new]) if new is not None else None
        check('scientific_table_preserved:' + sheet + '/' + table, old_hash == new_hash)
        science.append({'sheet': sheet, 'table': table, 'before_sha256': old_hash,
                        'after_sha256': new_hash, 'before_rows': len(old[1]) if old else None,
                        'after_rows': len(new[1]) if new else None})
    evidence['preserved_scientific_tables'] = science
    groups = records(current, 'Selected model groups', 'Groups')
    mammals = [g for g in groups if g['group_name'] == 'Marine mammals']
    check('marine_mammals_exact_seq', len(mammals) == 1 and int(float(mammals[0]['seq'])) == 27)

    with zipfile.ZipFile(PROJECT) as archive:
        _, headers, _, rows = table_rows(archive, 'Models & coverage', 'Models')
        matches = [(row, data) for row, data in rows if data.get('unit_id') == UNIT and data.get('model_id') == MODEL_ID]
        check('one_central_model_record', len(matches) == 1)
        if len(matches) != 1:
            raise ValueError('Expected one exact central model record')
        xml_row, metadata = matches[0]
        styles = E.fromstring(archive.read('xl/styles.xml'))
        fonts, formats = styles.find(S + 'fonts'), styles.find(S + 'cellXfs')
        for field in ['model_id', 'researcher_review_status']:
            column = headers.index(field) + 1
            cells = {re.match(r'[A-Z]+', cell.get('r')).group(): cell for cell in xml_row}
            letters, number = '', column
            while number:
                number, remainder = divmod(number - 1, 26)
                letters = chr(65 + remainder) + letters
            cell = cells.get(letters)
            if cell is None:
                check('central_green_style:' + field, False, 'Cell is absent before registration')
                continue
            font = fonts[int(formats[int(cell.get('s', '0'))].get('fontId', '0'))]
            color = font.find(S + 'color')
            check('central_green_style:' + field, color is not None and color.get('rgb') == 'FF187344')
    central = json.loads(metadata.get('researcher_review_summary') or '{}')
    for field, expected in {
        'researcher_name': name, 'researcher_review_date': date,
        'researcher_review_status': 'Validated by researcher',
        'validation_report_path': REPORT.relative_to(ROOT).as_posix(),
        'validation_report_sha256': EXPECTED_HASHES[REPORT],
        'reviewed_model_sha256': EXPECTED_HASHES[MODEL / 'model.json'],
    }.items():
        check('central_metadata:' + field, metadata.get(field) == expected)
    check('central_source_sections', central.get('sections') == summary['sections'])
    check('central_excluded_groups', central.get('excluded_group_ids') == ['Marine mammals'])
    check('central_exclusion_note', central.get('note') == EXPECTED_NOTE)
    review = approved_review(ROOT, metadata, current)
    check('approved_review_source_gate', review is not None)
    evidence['review_scope'] = (review or {}).get('review_scope')
    evidence['diagnostic_scope_note'] = (review or {}).get('diagnostic_scope_note')
    for filename, variable in [('index.html', 'DB'), ('trends.html', 'SERIES_DB')]:
        page = (ROOT / 'interactive_map' / filename).read_text(encoding='utf-8')
        fingerprint = re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">', page)
        check(filename + ':project_fingerprint', fingerprint is not None and fingerprint.group(1) == before_hashes[PROJECT])
        marker = 'const ' + variable + '='
        payload, _ = json.JSONDecoder().raw_decode(page, page.index(marker) + len(marker))
        unit = (payload['network']['units'] if variable == 'DB' else payload['units'])[UNIT]
        models = [m for m in unit['models'] if m['id'] == MODEL_ID]
        check(filename + ':exact_model_once', len(models) == 1)
        if len(models) != 1:
            raise ValueError(filename + ': expected one exact model')
        model = models[0]
        chosen = unit['models'][unit['default_model']]['id'] if variable == 'DB' else unit['default_model']
        check(filename + ':selected_model', chosen == MODEL_ID)
        check(filename + ':review_exact', review is not None and model.get('researcher_review') == review)
        check(filename + ':no_pending_review', not model.get('recorded_review_pending'))
        excluded = model.get('display_ppr_excluded_group_ids')
        check(filename + ':excluded_groups', excluded == ['Marine mammals'])
        displayed_groups = model.get('group_data', {}).get('groups', [])
        matches = [g for g in displayed_groups if g.get('id') == 'Marine mammals']
        check(filename + ':marine_mammals_retained', len(matches) == 1 and matches[0].get('name') == 'Marine mammals')
        default_ids = [g['id'] for g in displayed_groups if g['id'] not in (excluded or [])]
        check(filename + ':default_policy_excludes_mammals', 'Marine mammals' not in default_ids and len(default_ids) == len(displayed_groups) - 1)
    check('inputs_unchanged_during_verification', all(sha(p) == value for p, value in before_hashes.items()))
    evidence['passed'] = all(row['passed'] for row in checks)
    evidence['failed_checks'] = [row['check'] for row in checks if not row['passed']]
    return evidence


def verify(before_region: Path, output: Path = None):
    """Write scoped QA and return evidence; raise on any failed publication check."""
    output = (output or RUN / 'qa/registration_verification.json').resolve()
    if not output.is_relative_to((RUN / 'qa').resolve()):
        raise ValueError('QA output must remain inside this run\'s qa directory')
    try:
        evidence = _verify(Path(before_region).resolve(strict=True))
    except Exception as error:
        evidence = {'schema_version': 1, 'unit_id': UNIT, 'model_id': MODEL_ID,
                    'passed': False, 'checked_utc': datetime.now(timezone.utc).isoformat(),
                    'error': type(error).__name__ + ': ' + str(error)}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        raise
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not evidence['passed']:
        raise ValueError('Registration verification failed: ' + ', '.join(evidence['failed_checks']))
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before-region', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=RUN / 'qa/registration_verification.json')
    args = parser.parse_args()
    try:
        evidence = verify(args.before_region, args.output)
    except Exception as error:
        print(json.dumps({'passed': False, 'error': type(error).__name__ + ': ' + str(error),
                          'qa': str(args.output.resolve())}, ensure_ascii=True))
        return 1
    print(json.dumps({'passed': evidence['passed'], 'checks': len(evidence.get('checks', [])),
                      'failed_checks': evidence.get('failed_checks', []), 'error': evidence.get('error'),
                      'qa': str(args.output.resolve())}, ensure_ascii=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
