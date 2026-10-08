"""Narrow appendix update for the verified two-group candidate-set correction."""
from pathlib import Path
import hashlib
import json
from zipfile import ZipFile

from lxml import etree as ET
import openpyxl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGION = ROOT / 'regions/EEZ_941'
OUT = REGION / 'validation_reports/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
path = REGION / 'EEZ941_taxon_mapping_appendix.xlsx'
audit = json.loads((OUT / 'taxon_audit.json').read_text(encoding='utf-8'))
taxon = 'Marine pelagic fishes not identified'
item = next(r for r in audit['rows'] if r['taxon'] == taxon)
assert item['candidate_ids'] == [8, 16, 17, 20, 22, 24, 26]
before_hash = hashlib.sha256(path.read_bytes()).hexdigest()


def logical_cells(file):
    w = openpyxl.load_workbook(file, read_only=True)
    try:
        return {(s.title, c.coordinate): c.value for s in w for row in s for c in row if c.value is not None}
    finally:
        w.close()


before = logical_cells(path)
address = next(cell for (sheet, cell), value in before.items() if sheet == 'Taxon mapping' and value == taxon)
row_no = int(address[1:])
new_values = {f'E{row_no}': item['mapping_display'], f'G{row_no}': item['reason'] + ' Sources: ' + '; '.join(item['sources']) + '; source catch and biomass.'}
with ZipFile(path) as package:
    infos = package.infolist()
    old = {entry.filename: package.read(entry) for entry in infos}
new = dict(old)
S = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
doc = ET.fromstring(old['xl/worksheets/sheet1.xml'])
for ref, value in new_values.items():
    cell = next(e for e in doc.iter(S + 'c') if e.get('r') == ref)
    for child in list(cell):
        if child.tag in {S + 'v', S + 'is', S + 'f'}:
            cell.remove(child)
    cell.set('t', 'inlineStr')
    inline = ET.SubElement(cell, S + 'is')
    ET.SubElement(inline, S + 't').text = value
row = next(e for e in doc.iter(S + 'row') if e.get('r') == str(row_no))
row.set('ht', '225')
row.set('customHeight', '1')
new['xl/worksheets/sheet1.xml'] = ET.tostring(doc, encoding='UTF-8', xml_declaration=True, standalone=True)
assert all(new[k] == old[k] for k in old if k != 'xl/worksheets/sheet1.xml')
temp = path.with_name(path.name + '.candidate-update')
with ZipFile(temp, 'w') as package:
    for entry in infos:
        package.writestr(entry, new[entry.filename])
assert hashlib.sha256(path.read_bytes()).hexdigest() == before_hash, 'Appendix changed during update'
temp.replace(path)
after = logical_cells(path)
expected = dict(before)
for ref, value in new_values.items():
    expected['Taxon mapping', ref] = value
assert after == expected, 'Unexpected appendix cell change'
p = HERE / 'verification/EEZ_941_pelagic_followup.json'
proof = json.loads(p.read_text(encoding='utf-8'))
proof.update({'after': item, 'regional_after_sha256': hashlib.sha256((REGION / 'EEZ_941.xlsx').read_bytes()).hexdigest(),
              'appendix_before_sha256': before_hash, 'appendix_after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'appendix_changed_cells': list(new_values), 'all_other_cells_and_parts_unchanged': True, 'row_height_points': 225})
assert hashlib.sha256(next(REGION.glob('Model_validation*.docx')).read_bytes()).hexdigest() == proof['report_before_sha256']
p.write_text(json.dumps(proof, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
print(json.dumps({'row': row_no, 'changed_cells': list(new_values), 'other_content_preserved': True}))
