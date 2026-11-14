from pathlib import Path
from collections import Counter, defaultdict
from copy import copy
import hashlib
import json
import math
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')
run = Path(__file__).resolve().parents[1]
validation = run.parents[1]
before_path = run / 'inputs/taxon_mapping_before.xlsx'
authored_path = run / 'outputs/taxon_mapping_artifact.xlsx'
staged_path = run / 'outputs/taxon_mapping.xlsx'
qa_path = run / 'qa/appendix_verification.json'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(validation / 'taxon_mapping.xlsx') == sha(before_path), 'Researcher original changed during editing'

new_targets = {
    'C29': 'evidence/discards_reconciliation_20261114/outputs/diagnostics/source_exact_returns_to_36/summary.json',
    'C30': 'evidence/discards_reconciliation_20261114/outputs/source/native_probe_verification.json',
    'C31': 'evidence/physical_detritus_merge_20261114/physical_detritus_merge.md',
}
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
RELNS = 'http://schemas.openxmlformats.org/package/2006/relationships'
sheet_name = 'xl/worksheets/sheet2.xml'
rels_name = 'xl/worksheets/_rels/sheet2.xml.rels'
with zipfile.ZipFile(authored_path) as z:
    sheet_xml = z.read(sheet_name).decode('utf-8')
    rels_xml = z.read(rels_name).decode('utf-8')
    sheet = ET.fromstring(sheet_xml)
    rels = ET.fromstring(rels_xml)
    style = sheet.find(".//m:c[@r='C28']", NS).attrib['s']
    used_ids = {e.attrib['Id'] for e in rels}
    assert not any(sheet.find(f".//m:hyperlink[@ref='{cell}']", NS) is not None for cell in new_targets)
    added_links, added_rels = [], []
    for cell, target in new_targets.items():
        rid_num = 1
        while f'rId{rid_num}' in used_ids:
            rid_num += 1
        rid = f'rId{rid_num}'
        used_ids.add(rid)
        added_links.append(f'<x:hyperlink ref="{cell}" r:id="{rid}" xmlns:r="{NS["r"]}"/>')
        added_rels.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{target}" TargetMode="External"/>')
        # Unsupported public hyperlink authoring: reuse the existing effective
        # blue/underlined link style without changing the authored cell value.
        pattern = rf'<x:c\b[^>]*\br="{cell}"[^>]*>'
        matches = list(re.finditer(pattern, sheet_xml))
        assert len(matches) == 1, cell
        tag = matches[0].group(0)
        patched = re.sub(r'\s+s="[^"]*"', '', tag)
        patched = patched[:-1] + f' s="{style}">'
        sheet_xml = sheet_xml.replace(tag, patched, 1)
    assert sheet_xml.count('</x:hyperlinks>') == 1
    assert rels_xml.count('</Relationships>') == 1
    sheet_xml = sheet_xml.replace('</x:hyperlinks>', ''.join(added_links) + '</x:hyperlinks>')
    rels_xml = rels_xml.replace('</Relationships>', ''.join(added_rels) + '</Relationships>')
    with zipfile.ZipFile(staged_path, 'w', compression=zipfile.ZIP_DEFLATED) as out:
        for member in z.infolist():
            data = sheet_xml.encode('utf-8') if member.filename == sheet_name else rels_xml.encode('utf-8') if member.filename == rels_name else z.read(member.filename)
            out.writestr(member, data)

before = openpyxl.load_workbook(before_path)
after = openpyxl.load_workbook(staged_path)
assert before.sheetnames == after.sheetnames == ['Taxon mapping', 'Sources']
expected_changes = {('Taxon mapping', 'A2'), ('Sources', 'A2'), ('Sources', 'D4'), ('Sources', 'A16'), ('Sources', 'B16'), ('Sources', 'A24'), ('Sources', 'B24')}
changes = []
original_links = []
for name in before.sheetnames:
    old, new = before[name], after[name]
    assert old.freeze_panes == new.freeze_panes
    assert {str(r) for r in old.merged_cells.ranges} == {str(r) for r in new.merged_cells.ranges}
    assert {k: v.width for k, v in old.column_dimensions.items()} == {k: v.width for k, v in new.column_dimensions.items()}
    for row in old:
        for cell in row:
            updated = new[cell.coordinate]
            if cell.value != updated.value:
                changes.append({'sheet': name, 'cell': cell.coordinate, 'before': cell.value, 'after': updated.value})
            assert cell.data_type == updated.data_type, (name, cell.coordinate, 'type')
            assert cell.number_format == updated.number_format, (name, cell.coordinate, 'number format')
            assert cell.comment == updated.comment, (name, cell.coordinate, 'comment')
            assert copy(cell.font) == copy(updated.font), (name, cell.coordinate, 'font')
            assert copy(cell.alignment) == copy(updated.alignment), (name, cell.coordinate, 'alignment')
            if cell.hyperlink:
                assert updated.hyperlink
                assert cell.hyperlink.target == updated.hyperlink.target
                assert cell.hyperlink.location == updated.hyperlink.location
                original_links.append((name, cell.coordinate))
assert {(c['sheet'], c['cell']) for c in changes} == expected_changes
assert len(original_links) == 27
assert after['Taxon mapping'].max_column == 7 and after['Taxon mapping'].max_row == 257
assert after['Sources'].max_column == 4 and after['Sources'].max_row == 31
assert list(before['Taxon mapping'].values)[7:] == list(after['Taxon mapping'].values)[7:]
for name, table_name, ref, header in [('Taxon mapping', 'PatagonianMappingTable', 'A7:G257', 7), ('Sources', 'PatagonianSourcesTable', 'A4:D31', 4)]:
    table = after[name].tables[table_name]
    assert table.ref == table.autoFilter.ref == ref
    assert [c.name for c in table.tableColumns] == [c.value for c in after[name][header]]

links = []
for s in after:
    for row in s:
        for c in row:
            assert c.data_type != 'f', (s.title, c.coordinate, 'unexpected formula')
            if not c.hyperlink:
                continue
            target = c.hyperlink.target
            record = {'sheet': s.title, 'cell': c.coordinate, 'target': target, 'location': c.hyperlink.location}
            assert c.font.u == 'single', (s.title, c.coordinate, 'link underline')
            assert c.font.color and c.font.color.type == 'rgb' and c.font.color.rgb[-6:].upper() in {'0563C1', '0000FF'}, (s.title, c.coordinate, 'link blue')
            if target and not target.startswith(('https://', 'http://')):
                assert not Path(target).is_absolute() and not re.match(r'^[A-Za-z]:', target)
                resolved = (validation / urllib.parse.unquote(target.split('#')[0])).resolve()
                assert resolved.is_file(), f'Broken final-destination-relative target {target}'
                record.update(exists_at_intended_final_destination=True, sha256=sha(resolved))
            links.append(record)
assert len(links) == 30
for cell, target in new_targets.items():
    assert after['Sources'][cell].hyperlink.target == target
with zipfile.ZipFile(staged_path) as z:
    for item in z.namelist():
        if item.endswith('.xml'):
            xml = z.read(item)
            assert b'<HyperlinkBase>' not in xml, item

rows = list(after['Taxon mapping'].values)[7:]
assert len(rows) == len({r[0] for r in rows}) == 250
assert rows == sorted(rows, key=lambda r: (r[3] is None, -(r[3] or 0), r[0]))
catch = math.fsum(r[2] for r in rows)
ppr = math.fsum(r[3] for r in rows)
assert math.isclose(catch, 1497627.61997537, rel_tol=1e-14)
assert math.isclose(ppr, 142458248.78282157, rel_tol=1e-14)
assert sum(r[2] == 0 for r in rows) == 59
assert sum(r[1] == '?' for r in rows) == 55
assert all(r[2] == r[3] == 0 for r in rows if r[1] == '?')
confidence = {}
for category in ['High', 'Medium', 'Low', 'Very low', 'Unresolved']:
    subset = [r for r in rows if r[5] == category]
    confidence[category] = {'count': len(subset), 'catch_t': math.fsum(r[2] for r in subset), 'classic_ppr_tC': math.fsum(r[3] for r in subset)}
    confidence[category]['classic_ppr_percent'] = confidence[category]['classic_ppr_tC'] / ppr * 100
assert [confidence[c]['count'] for c in confidence] == [27, 26, 1, 196, 0]

diagnostic_dir = validation / 'evidence/discards_reconciliation_20261114/outputs/diagnostics/source_exact_returns_to_36'
summary = json.loads((diagnostic_dir / 'summary.json').read_text(encoding='utf-8'))
assert summary['scenario'] == 'source_exact_returns_to_36'
assert summary['floor_info']['use_ee_floor'] and summary['floor_info']['ee_floor'] == 0.1
assert all(summary['living_preservation'].values())
assert summary['pool_budget'][0]['pool_id'] == 35 and summary['pool_budget'][1]['pool_id'] == 36
assert summary['pool_budget'][0]['detritus_stock_residual'] == -0.20750363203745528
assert summary['pool_budget'][1]['fishery_return_inflow'] == 0.005859524956463247
diagnostics = []
for method in summary['methods']:
    assert method['diagnostic']['status'] == 'WARN'
    assert method['diagnostic']['balance']['is_balanced']
    path = diagnostic_dir / f"{method['method']}_full_return.json"
    raw = json.loads(path.read_text(encoding='utf-8'))
    matrix = raw['SPPR']['dataframe']
    assert matrix['shape'] == [37, 5]
    assert set(raw['SPPR']['column_ids']) == {35, 36, 37, 12, 22}
    values = [v for row in matrix['data'] for v in row]
    assert all(isinstance(v, (int, float)) and math.isfinite(v) and v >= 0 for v in values)
    diagnostics.append({'method': method['method'], 'status': 'WARN', 'strict_balance_pass': True, 'balance_relative_gap': method['diagnostic']['balance']['rel_gap'], 'full_matrix_shape': [37, 5], 'negative_matrix_entries': 0, 'matrix_file_sha256': sha(path)})
probe_path = validation / new_targets['C30']
probe = json.loads(probe_path.read_text(encoding='utf-8'))
pool = next(p for p in probe['pools'] if p['sequence'] == 35)
assert pool['Ex'] == pool['stored_source_Export'] == -0.20750363171100616
assert pool['BA'] == pool['explicit_DetImport'] == 0
assert pool['export_equals_original_stored_export_exactly']
retained_evidence = []
old_run = validation / 'work/2026-11-14_152912_discards_reconciliation'
for target in list(new_targets.values())[:2]:
    p = validation / target
    source = old_run / p.relative_to(validation / 'evidence/discards_reconciliation_20261114')
    assert sha(p) == sha(source), f'Retained evidence differs: {p}'
    retained_evidence.append({'target': target, 'sha256': sha(p), 'matches_authenticated_work_source': True})

report = {
    'artifact_tool_authored': True,
    'recalculated_before_export': True,
    'original_sha256': sha(before_path),
    'staged_sha256': sha(staged_path),
    'original_is_unchanged': sha(validation / 'taxon_mapping.xlsx') == sha(before_path),
    'staged_only_not_published': True,
    'intended_link_resolution_base': str(validation),
    'staged_copy_link_caveat': 'Links intentionally target the final model_validation directory. Promote this XLSX unchanged to model_validation/taxon_mapping.xlsx; links are not claimed to resolve from the nested staging directory.',
    'changed_existing_cells': changes,
    'added_sources_rows': [29, 30, 31],
    'all_250_seven_column_data_rows_exactly_preserved': True,
    'original_links_preserved': 27,
    'final_links': 30,
    'all_links_blue_and_underlined': True,
    'all_local_targets_exist_from_intended_final_destination': True,
    'no_machine_specific_link_base': True,
    'all_original_cell_types_number_formats_comments_fonts_alignments_preserved': True,
    'filters': {'Taxon mapping': 'A7:G257', 'Sources': 'A4:D31'},
    'frozen_panes': {'Taxon mapping': 'B8', 'Sources': 'A5'},
    'reference_layout': 'LME037 seven-column appendix; same headings and frozen panes; existing LME014 widths and row order retained.',
    'reference_year': 2019,
    'catch_basis': 'landings',
    'classic_ppr_method': 'saved classic wet coefficient multiplied by catch and divided by 9 once',
    'catch_t': catch,
    'classic_ppr_tC': ppr,
    'zero_catch_rows': 59,
    'unknown_TL_zero_catch_rows': 55,
    'confidence': confidence,
    'diagnostics': diagnostics,
    'regional_GE_TE_contribution_values': 'No such columns in the seven-column appendix. No regional GE/TE shares recalculated; historical shark exposure explicitly labelled as historical coefficient configuration.',
    'native_deficit': pool['Ex'],
    'physical_merge': 'Sensitivity only; not adopted',
    'retained_evidence': retained_evidence,
    'hyperlinks': links,
    'unsupported_feature_patch': {'parts': [sheet_name, rels_name], 'scope': 'Added three portable hyperlink relationships and reused C28 effective blue/underlined style for the three new link cells; no existing values or relationships changed.'},
    'formula_errors': [],
    'visual_review': 'Pending final patched-workbook render inspection',
    'native_excel_ui_opened': False,
    'solver_run_in_this_task': False,
}
qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: report[k] for k in ['staged_sha256', 'original_is_unchanged', 'all_250_seven_column_data_rows_exactly_preserved', 'catch_t', 'classic_ppr_tC', 'final_links', 'diagnostics']}, ensure_ascii=False, indent=2))
