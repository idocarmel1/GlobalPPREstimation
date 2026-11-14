from pathlib import Path
import hashlib
import json
import math
import zipfile
import openpyxl

run = Path(__file__).resolve().parents[1]
validation = run.parents[1]
original = run / 'inputs/taxon_mapping_before.xlsx'
authored = run / 'outputs/taxon_mapping_artifact.xlsx'
destination = validation / 'taxon_mapping.xlsx'
summary_path = run / 'qa/mapping_validation_summary.json'
summary = json.loads(summary_path.read_text(encoding='utf-8'))
old_target = summary['source_link_repair']['old_target']
new_target = summary['source_link_repair']['new_target']

assert hashlib.sha256(destination.read_bytes()).digest() == hashlib.sha256(original.read_bytes()).digest(), 'Appendix changed after initial read'
# Hyperlink authoring is absent from the provided public artifact-tool surface.
# Patch only this verified relocated relationship, leaving rendered cells intact.
temporary = run / 'outputs/taxon_mapping_verified.xlsx'
with zipfile.ZipFile(authored) as src, zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as dst:
    patches = 0
    for member in src.infolist():
        data = src.read(member.filename)
        if member.filename == 'xl/worksheets/_rels/sheet2.xml.rels':
            assert data.count(old_target.encode()) == 1
            data = data.replace(old_target.encode(), new_target.encode())
            patches += 1
        dst.writestr(member, data)
    assert patches == 1

before = openpyxl.load_workbook(original)
after = openpyxl.load_workbook(temporary)
expected_cells = {('Taxon mapping','A3'), ('Sources','A2'), ('Sources','D4')}
actual_cells = set()
assert before.sheetnames == after.sheetnames == ['Taxon mapping','Sources']
links = []
for name in before.sheetnames:
    a, b = before[name], after[name]
    assert a.max_row == b.max_row and a.max_column == b.max_column
    assert a.freeze_panes == b.freeze_panes
    assert {str(v) for v in a.merged_cells.ranges} == {str(v) for v in b.merged_cells.ranges}
    for row in a:
        for cell in row:
            revised = b[cell.coordinate]
            if cell.value != revised.value:
                actual_cells.add((name, cell.coordinate))
            assert cell.data_type == revised.data_type
            assert cell.number_format == revised.number_format
            if cell.hyperlink:
                assert revised.hyperlink
                expected_target = new_target if (name,cell.coordinate)==('Sources','C28') else cell.hyperlink.target
                assert revised.hyperlink.target == expected_target
                assert revised.hyperlink.location == cell.hyperlink.location
                if expected_target and not expected_target.startswith(('https://','http://')):
                    target = (validation / expected_target.split('#')[0]).resolve()
                    assert target.is_file(), f'Broken target {name}!{cell.coordinate}: {target}'
                links.append({'sheet':name,'cell':cell.coordinate,'target':revised.hyperlink.target,'location':revised.hyperlink.location})
assert actual_cells == expected_cells
assert len(links) == 27
for sheet_name, table_name, expected_range in [('Taxon mapping','PatagonianMappingTable','A7:G257'),('Sources','PatagonianSourcesTable','A4:D28')]:
    table = after[sheet_name].tables[table_name]
    assert table.ref == table.autoFilter.ref == expected_range
    assert [c.name for c in table.tableColumns] == [c.value for c in after[sheet_name][7 if sheet_name=='Taxon mapping' else 4]]

rows = list(after['Taxon mapping'].values)[7:]
assert len(rows)==250 and len({r[0] for r in rows})==250
assert rows==sorted(rows,key=lambda r: (r[3] is None,-(r[3] or 0),r[0]))
assert math.isclose(sum(r[2] for r in rows),1497627.61997537,rel_tol=1e-14)
assert math.isclose(sum(r[3] for r in rows),142458248.78282157,rel_tol=1e-14)
assert sum(r[2]==0 for r in rows)==59
assert sum(r[1]=='?' for r in rows)==55
assert all(r[2]==r[3]==0 for r in rows if r[1]=='?')
assert all(not (isinstance(c.value,str) and c.value.startswith(('=','#REF!','#DIV/0!','#VALUE!','#NAME?','#N/A','#NUM!'))) for s in after for row in s for c in row)
after.close(); before.close()
temporary.replace(destination)
summary['appendix_final'] = {
    'artifact_tool_authored':True,
    'recalculated_before_export':True,
    'all_250_seven_column_data_rows_exactly_preserved':True,
    'changed_cells':[f'{s}!{c}' for s,c in sorted(actual_cells)],
    'filters':{'Taxon mapping':'A7:G257','Sources':'A4:D28'},
    'frozen_panes':{'Taxon mapping':'B8','Sources':'A5'},
    'all_27_hyperlinks_preserved_with_one_verified_relocation':True,
    'all_local_targets_exist':True,
    'final_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
    'visual_review':'Original top and Sources plus final top, middle, zero rows, Sources top and Sources bottom inspected; no clipped text, hidden numbers or broken row wrapping. Original layout retained.',
    'formula_errors':[],
    'native_excel_ui_not_opened':True,
    'hyperlinks':links,
}
summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary['appendix_final'].items() if k!='hyperlinks'},ensure_ascii=False,indent=2))
