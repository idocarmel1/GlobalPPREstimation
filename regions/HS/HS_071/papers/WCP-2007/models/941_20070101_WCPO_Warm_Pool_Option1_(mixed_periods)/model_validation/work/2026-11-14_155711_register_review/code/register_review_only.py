"""One-shot, explicitly gated HS_071 review registration; never publishes pages.

Run only after the coordinating chat verifies the other central writers finished:
  <bundled-python> -X utf8 <this-file> --confirmed-writers-finished
The signed report is read-only. The current Project snapshot is retained for the
later, separately authorized map/trends reconciliation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
from tools.project_core.registry.writes import central_lock
from tools.project_core.validation.researcher_review import (
    FIELDS, S, STATUS, _register_review, approved_review, column, column_index,
    read_report, sheet_xml, table_rows,
)
from tools.project_core.validation.validation_percentage_format import verify_report

UNIT = 'HS_071'
MODEL_ID = '941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
MODEL = ROOT / 'regions/HS/HS_071/papers/WCP-2007/models' / MODEL_ID
VALIDATION = MODEL / 'model_validation'
RUN = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'Project.xlsx'
REPORT = VALIDATION / 'validation.docx'
EXPECTED_REPORT_SHA = '944cfbc6087fe0e543353d9135d8feb7f063765a5bb22b4a8bbea209321e1983'
EXPECTED_SIGNER = 'Ido Carmel'
EXPECTED_DATE = '2026-11-14'
SNAPSHOT = RUN / 'inputs/Project_before_registration.xlsx'
EVIDENCE = VALIDATION / 'evidence/source_review/researcher_registration_20261114.json'
PROOF = RUN / 'qa/registration_proof.json'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path, start=ROOT):
    return Path(os.path.relpath(path, start)).as_posix()


def xml_value(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text, node.tail,
            tuple(xml_value(child) for child in node))


def archive_parts(path):
    with zipfile.ZipFile(path) as archive:
        return archive.namelist(), {n: archive.read(n) for n in archive.namelist()}


def narrow_regional_book(path):
    book = {}
    with zipfile.ZipFile(path) as archive:
        for sheet, table in [('Overview', 'Settings'), ('Selected model groups', 'Groups')]:
            _, headers, _, rows = table_rows(archive, sheet, table)
            headers = list(rows[0][1]) if rows else headers
            book.setdefault(sheet, {})[table] = (headers, [[r.get(h) for h in headers] for _, r in rows])
    return book


def model_metadata(path):
    with zipfile.ZipFile(path) as archive:
        sheet, headers, header, rows = table_rows(archive, 'Models & coverage', 'Models')
        sheet_path = sheet_xml(archive, 'Models & coverage')[0]
    matches = [(r, d) for r, d in rows if d.get('unit_id') == UNIT and d.get('model_id') == MODEL_ID]
    require(len(matches) == 1, 'Expected one exact HS_071 central model row')
    return sheet_path, sheet, headers, header, rows, matches[0]


def verify_package_change(before_path, after_path, registered_values):
    old_order, old_parts = archive_parts(before_path)
    new_order, new_parts = archive_parts(after_path)
    require(old_order == new_order, 'Project ZIP part inventory/order changed')
    old_path, old_sheet, old_headers, old_header, old_rows, (old_row, old_model) = model_metadata(before_path)
    new_path, new_sheet, new_headers, new_header, new_rows, (new_row, new_model) = model_metadata(after_path)
    require(old_path == new_path, 'Models sheet location changed')
    require(new_headers == old_headers + [f for f in FIELDS if f not in old_headers], 'Unexpected header changes')
    require(old_row.get('r') == new_row.get('r'), 'Target model row moved')
    require({k: new_model.get(k) for k in FIELDS} == registered_values, 'Registered fields differ from saved values')
    require({k: v for k, v in old_model.items() if k not in FIELDS} ==
            {k: v for k, v in new_model.items() if k not in FIELDS}, 'Target scientific/selection fields changed')
    old_others = [(r.get('r'), d, xml_value(r)) for r, d in old_rows if r.get('r') != old_row.get('r')]
    new_others = [(r.get('r'), {k: d.get(k) for k in old_headers}, xml_value(r))
                  for r, d in new_rows if r.get('r') != new_row.get('r')]
    require(old_others == new_others, 'Another central model row changed')
    review_cols = {new_headers.index(f) + 1 for f in FIELDS}
    model_col = new_headers.index('model_id') + 1
    for before, after, is_header in [(old_row, new_row, False), (old_header, new_header, True)]:
        a = {column_index(c.get('r')): copy.deepcopy(c) for c in before}
        b = {column_index(c.get('r')): copy.deepcopy(c) for c in after}
        for key in set(a) | set(b):
            if key in review_cols:
                continue
            require(key in a and key in b, 'Unrelated cell added/removed')
            if key == model_col and not is_header:
                a[key].attrib.pop('s', None)
                b[key].attrib.pop('s', None)
            require(xml_value(a[key]) == xml_value(b[key]), 'Non-review target/header cell changed')
    # Every other sheet child, row and column definition remains identical.
    old_copy, new_copy = copy.deepcopy(old_sheet), copy.deepcopy(new_sheet)
    for sheet in [old_copy, new_copy]:
        data = sheet.find(f'{{{S}}}sheetData')
        for row in list(data):
            if row.get('r') in {old_row.get('r'), old_header.get('r')}:
                data.remove(row)
        cols = sheet.find(f'{{{S}}}cols')
        if cols is not None:
            for col in list(cols):
                if int(col.get('min')) == int(col.get('max')) and int(col.get('min')) in review_cols:
                    cols.remove(col)
    require(xml_value(old_copy) == xml_value(new_copy), 'Unrelated Models worksheet content changed')
    for f in FIELDS:
        idx = new_headers.index(f) + 1
        cols = [c for c in new_sheet.find(f'{{{S}}}cols') if c.get('min') == c.get('max') == str(idx)]
        require(len(cols) == 1, 'Review column definition not unique')
        require(cols[0].get('width') == ('65' if f == 'validation_report_path' else '28'), 'Review column width mismatch')
        require(cols[0].get('hidden') == ('1' if f.endswith('sha256') or f == 'researcher_review_summary' else '0'), 'Review column hidden flag mismatch')
    # The registration may only extend existing style collections by its two cells.
    old_styles, new_styles = ET.fromstring(old_parts['xl/styles.xml']), ET.fromstring(new_parts['xl/styles.xml'])
    for tag in ['fonts', 'cellXfs']:
        a, b = old_styles.find(f'{{{S}}}{tag}'), new_styles.find(f'{{{S}}}{tag}')
        require(len(b) == len(a) + 2, 'Unexpected style extension')
        require([xml_value(x) for x in a] == [xml_value(x) for x in list(b)[:len(a)]], 'Existing styles changed')
    a, b = copy.deepcopy(old_styles), copy.deepcopy(new_styles)
    for tag in ['fonts', 'cellXfs']:
        a.remove(a.find(f'{{{S}}}{tag}')); b.remove(b.find(f'{{{S}}}{tag}'))
    require(xml_value(a) == xml_value(b), 'Unrelated style collections changed')
    fonts, formats = new_styles.find(f'{{{S}}}fonts'), new_styles.find(f'{{{S}}}cellXfs')
    for field in ['model_id', 'researcher_review_status']:
        idx = new_headers.index(field) + 1
        cell = next(c for c in new_row if column_index(c.get('r')) == idx)
        font = fonts[int(formats[int(cell.get('s'))].get('fontId'))]
        require(font.find(f'{{{S}}}color').get('rgb') == 'FF187344', 'Target status/model font is not green')
        require(font.find(f'{{{S}}}b') is not None, 'Target status/model font is not bold')
    table_parts = []
    for name, raw in old_parts.items():
        if name.startswith('xl/tables/') and name.endswith('.xml'):
            table = ET.fromstring(raw)
            if [c.get('name') for c in table.find(f'{{{S}}}tableColumns')] == old_headers:
                table_parts.append(name)
                expected = copy.deepcopy(table)
                ref = expected.get('ref')
                new_ref = ref.split(':')[0] + ':' + column(len(new_headers)) + re.search(r'\d+$', ref)[0]
                expected.set('ref', new_ref)
                if expected.find(f'{{{S}}}autoFilter') is not None:
                    expected.find(f'{{{S}}}autoFilter').set('ref', new_ref)
                columns = expected.find(f'{{{S}}}tableColumns')
                columns[:] = [ET.Element(f'{{{S}}}tableColumn', id=str(i), name=h) for i, h in enumerate(new_headers, 1)]
                columns.set('count', str(len(new_headers)))
                require(xml_value(expected) == xml_value(ET.fromstring(new_parts[name])), 'Unexpected Models native-table change')
    require(len(table_parts) == 1, 'Expected exactly one Models native table')
    allowed = {old_path, 'xl/styles.xml', *table_parts}
    changed = [n for n in old_order if old_parts[n] != new_parts[n]]
    require(set(changed) <= allowed, 'Unrelated Project ZIP parts changed: ' + str(set(changed) - allowed))
    return {'changed_zip_parts': changed, 'other_model_rows_unchanged': len(old_others),
            'non_review_target_fields_unchanged': True, 'all_other_zip_parts_byte_identical': True,
            'existing_styles_preserved': True, 'target_model_and_status_green_bold': True,
            'models_sheet_cells_and_column_scope_verified': True, 'models_native_table_verified': True}


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.registration-', suffix='.json', dir=path.parent)
    os.close(fd)
    try:
        Path(tmp).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--confirmed-writers-finished', action='store_true', required=True)
    parser.parse_args()
    require(not SNAPSHOT.exists(), 'One-shot snapshot already exists; inspect prior attempt before retrying')
    require(not EVIDENCE.exists() and not PROOF.exists(), 'Registration proof already exists; do not overwrite')
    regional = ROOT / 'regions/HS/HS_071/HS_071.xlsx'
    protected_paths = [REPORT, VALIDATION / 'taxon_mapping.xlsx', regional, MODEL / 'model.json', MODEL / 'model_notes.md']
    protected_paths += sorted(p for p in (MODEL / 'results').rglob('*') if p.is_file())
    protected_paths += [ROOT / 'interactive_map' / n for n in ['index.html', 'trends.html', 'sources.html']]
    post_sha = None
    written_proofs = {}
    with central_lock(ROOT):
        protected = {p: sha(p) for p in protected_paths}
        require(protected[REPORT] == EXPECTED_REPORT_SHA, 'Signed DOCX changed; reread the latest researcher source')
        name, date, source = read_report(ROOT, REPORT, MODEL_ID)
        require((name, date) == (EXPECTED_SIGNER, EXPECTED_DATE), 'Signer/date differ from reviewed source')
        require(source.get('status', STATUS) == STATUS, 'Signed source is not a positive validation')
        sppr_text = source['sections'][2]['rows'][0]['text']
        require('NOE GROUPS REMOVED FROM CALCULATION' in sppr_text, 'No-removals source text changed')
        require('EE_floor=0.1' in sppr_text, 'Signed EE-floor condition changed')
        verify_report(REPORT)
        book = narrow_regional_book(regional)
        settings = dict(book['Overview']['Settings'][1])
        require((settings.get('results_model_id') or settings.get('selected_model_id')) == MODEL_ID, 'Regional result identity mismatch')
        before_sha = sha(PROJECT)
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT, SNAPSHOT)
        require(sha(SNAPSHOT) == before_sha == sha(PROJECT), 'Project changed during snapshot')
        try:
            # The outer lock deliberately includes snapshot and verification.
            # Do not call the public lock-taking wrapper within this lock.
            values = _register_review(PROJECT, REPORT, UNIT, MODEL_ID, [])
            post_sha = sha(PROJECT)
            package_proof = verify_package_change(SNAPSHOT, PROJECT, values)
            _, _, _, _, _, (_, metadata) = model_metadata(PROJECT)
            review = approved_review(ROOT, metadata, book)
            require(review['status'] == STATUS and review['excluded_group_ids'] == [], 'Registered status/exclusions mismatch')
            require((review['researcher_name'], review['review_date']) == (name, date), 'Registered signer/date mismatch')
            require(review['sections'] == source['sections'], 'Saved review sections differ from signed Word')
            require(review['report_sha256'] == EXPECTED_REPORT_SHA, 'Saved signed-source hash mismatch')
            require(read_report(ROOT, REPORT, MODEL_ID) == (name, date, source), 'Signed source changed during registration')
            require(all(sha(p) == h for p, h in protected.items()), 'A protected scientific/review/page file changed')
            require(sha(PROJECT) == post_sha, 'Project changed during preservation verification')
            page_fingerprints = {}
            for n in ['index.html', 'trends.html']:
                m = re.search(r'<meta name="ppr-project-sha256" content="([0-9a-f]{64})">',
                              (ROOT / 'interactive_map' / n).read_text(encoding='utf-8'))
                page_fingerprints[n] = m.group(1) if m else None
            result = {
                'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'unit_id': UNIT, 'model_id': MODEL_ID,
                'status': STATUS, 'researcher_name': name, 'researcher_review_date': date,
                'report_path': relative(REPORT, EVIDENCE.parent), 'report_sha256': EXPECTED_REPORT_SHA,
                'reviewed_model_sha256': metadata['reviewed_model_sha256'], 'excluded_seq': [], 'excluded_group_names': [],
                'signed_sppr_notes_preserved': sppr_text, 'signed_configuration_condition': 'EE_floor=0.1',
                'project_before_sha256': before_sha, 'project_after_sha256': post_sha,
                'pre_registration_snapshot': relative(SNAPSHOT, EVIDENCE.parent),
                'scope': 'Project.xlsx review metadata only. No recalculation, scientific adoption, map, trends or sources refresh.',
                'publication_status': 'Deferred by explicit user instruction; retain snapshot for later reconciliation.',
                'unchanged_page_embedded_project_fingerprints': page_fingerprints,
                'package_preservation': package_proof,
                'protected_file_hashes': {relative(p, EVIDENCE.parent): h for p, h in protected.items()},
                'registered_fields': values, 'source_to_metadata_verified': True,
            }
            qa = {**result, 'protected_file_hashes': {relative(p, PROOF.parent): h for p, h in protected.items()},
                  'report_path': relative(REPORT, PROOF.parent),
                  'pre_registration_snapshot': relative(SNAPSHOT, PROOF.parent)}
            atomic_json(PROOF, qa); written_proofs[PROOF] = sha(PROOF)
            atomic_json(EVIDENCE, result); written_proofs[EVIDENCE] = sha(EVIDENCE)
        except BaseException:
            # Restore only our own observed write, never an unknown concurrent change.
            if post_sha is not None and sha(PROJECT) == post_sha:
                fd, temporary = tempfile.mkstemp(prefix='.review-rollback-', suffix='.xlsx', dir=ROOT)
                os.close(fd)
                try:
                    shutil.copyfile(SNAPSHOT, temporary)
                    require(sha(PROJECT) == post_sha, 'Unsafe rollback: Project changed after our write')
                    os.replace(temporary, PROJECT)
                finally:
                    if os.path.exists(temporary):
                        os.unlink(temporary)
                require(sha(PROJECT) == before_sha, 'Project rollback failed')
            for path, digest in written_proofs.items():
                if path.exists() and sha(path) == digest:
                    path.unlink()
            raise
    print(json.dumps({'registered': True, 'unit_id': UNIT, 'model_id': MODEL_ID,
                      'status': STATUS, 'project_sha256': post_sha,
                      'map_trends_sources_updated': False, 'evidence': relative(EVIDENCE)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
