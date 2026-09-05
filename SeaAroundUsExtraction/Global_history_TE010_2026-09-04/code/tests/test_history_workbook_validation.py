"""Independent saved-XLSX checks, using hand-calculated XML/CSV fixtures."""
import csv
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import pytest

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'


def validator():
    path = Path(__file__).resolve().parents[1] / 'tools/validate_history_workbook.py'
    assert path.exists(), 'Independent saved-workbook validator is missing'
    spec = importlib.util.spec_from_file_location('history_workbook_validator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(path, sheets, *, styles=False, table=False, second_numfmt=0):
    """Minimal standard ZIP/XML fixture; no workbook authoring dependency."""
    workbook = ET.Element(f'{{{NS}}}workbook')
    listing = ET.SubElement(workbook, f'{{{NS}}}sheets')
    relationships = ET.Element(f'{{{PKG}}}Relationships')
    with zipfile.ZipFile(path, 'w') as archive:
        for index, (name, details) in enumerate(sheets.items(), 1):
            rid = f'rId{index}'
            ET.SubElement(listing, f'{{{NS}}}sheet', name=name, sheetId=str(index), **{f'{{{REL}}}id': rid})
            ET.SubElement(relationships, f'{{{PKG}}}Relationship', Id=rid, Target=f'worksheets/sheet{index}.xml')
            sheet = ET.Element(f'{{{NS}}}worksheet')
            if details.get('freeze'):
                views = ET.SubElement(sheet, f'{{{NS}}}sheetViews')
                view = ET.SubElement(views, f'{{{NS}}}sheetView', workbookViewId='0')
                ET.SubElement(view, f'{{{NS}}}pane', state='frozen', ySplit=str(details['freeze']), topLeftCell=f'A{details["freeze"]+1}')
            data = ET.SubElement(sheet, f'{{{NS}}}sheetData')
            for address, raw in details['cells'].items():
                attrs = {'r': address}
                formula = None
                if isinstance(raw, tuple):
                    formula, raw = raw
                if isinstance(raw, str):
                    attrs['t'] = 'e' if raw.startswith('#') else 'str'
                if styles:
                    attrs['s'] = str(details.get('style_id', 0))
                cell = ET.SubElement(ET.SubElement(data, f'{{{NS}}}row'), f'{{{NS}}}c', attrs)
                if formula is not None:
                    ET.SubElement(cell, f'{{{NS}}}f').text = formula
                if raw is not None:
                    ET.SubElement(cell, f'{{{NS}}}v').text = str(raw)
            if details.get('validation'):
                validations = ET.SubElement(sheet, f'{{{NS}}}dataValidations', count='1')
                validation = ET.SubElement(validations, f'{{{NS}}}dataValidation', sqref='B3', type='list')
                ET.SubElement(validation, f'{{{NS}}}formula1').text = "'Available Years'!$A$2:$A$3"
            if table and name == 'Original':
                parts = ET.SubElement(sheet, f'{{{NS}}}tableParts', count='1')
                ET.SubElement(parts, f'{{{NS}}}tablePart', {f'{{{REL}}}id': 'tableRelation'})
                rels = ET.Element(f'{{{PKG}}}Relationships')
                ET.SubElement(rels, f'{{{PKG}}}Relationship', Id='tableRelation', Target='../tables/table55.xml')
                archive.writestr(f'xl/worksheets/_rels/sheet{index}.xml.rels', ET.tostring(rels))
                tbl = ET.Element(f'{{{NS}}}table', id=str(details.get('table_id', 55)), name='OriginalTable', ref=details.get('table_ref', 'A1:B2'))
                columns = ET.SubElement(tbl, f'{{{NS}}}tableColumns', count='2')
                for col_index, label in enumerate(['Label', 'Value'], 1):
                    ET.SubElement(columns, f'{{{NS}}}tableColumn', id=str(col_index), name=label)
                archive.writestr('xl/tables/table55.xml', ET.tostring(tbl))
            archive.writestr(f'xl/worksheets/sheet{index}.xml', ET.tostring(sheet))
        archive.writestr('xl/workbook.xml', ET.tostring(workbook))
        archive.writestr('xl/_rels/workbook.xml.rels', ET.tostring(relationships))
        if styles:
            archive.writestr('xl/styles.xml', f'<styleSheet xmlns="{NS}"><fonts count="1"><font><name val="Arial"/><sz val="10"/></font></fonts><fills count="1"><fill><patternFill patternType="none"/></fill></fills><borders count="1"><border/></borders><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/><xf numFmtId="{second_numfmt}" fontId="0" fillId="0" borderId="0"/></cellXfs></styleSheet>')


def fixture(tmp_path):
    annual = [dict(unit_id='EEZ_A', region_name='A', region_type='EEZ', year=2019,
        total_catch_tonnes=2, matched_catch_tonnes=2, missing_tl_catch_tonnes=0,
        ppr_species=20, source_data_status='available'),
        dict(unit_id='LME_B', region_name='B', region_type='LME', year=2019,
        total_catch_tonnes=0, matched_catch_tonnes=0, missing_tl_catch_tonnes=0,
        ppr_species=0, source_data_status='available'),
        dict(unit_id='HS_C', region_name='C', region_type='High Seas', year=2019,
        total_catch_tonnes='', matched_catch_tonnes='', missing_tl_catch_tonnes='',
        ppr_species='', source_data_status='empty_catch_archive'),
        dict(unit_id='EEZ_X', region_name='X', region_type='EEZ', year=1950,
        total_catch_tonnes=100, matched_catch_tonnes=100, missing_tl_catch_tonnes=0,
        ppr_species=1000, source_data_status='available')]
    selected = [dict(unit_id='EEZ_A'), dict(unit_id='LME_B'), dict(unit_id='HS_C')]
    annual_path, selected_path = tmp_path/'annual.csv', tmp_path/'selected.csv'
    write_csv(annual_path, annual)
    write_csv(selected_path, selected)
    original = {'Original': {'freeze': 1, 'cells': {'A1': 'Label', 'B1': 'Value', 'A2': 'base', 'B2': ('1+1', 2)}}}
    source, final = tmp_path/'source.xlsx', tmp_path/'final.xlsx'
    write_xlsx(source, original, styles=True, table=True)
    sheets = {**original}
    sheets['Original'] = {**original['Original'], 'style_id': 1, 'table_id': 99}
    summary = {'B3': 2019, 'B4': 3, 'B5': ('SUM(E11:E13)', 20), 'B6': ('SUM(D11:D13)', 2),
        'B7': ('0', 0), 'B8': ('1', 1)}
    for row, uid, name, kind, catch, ppr, rank, fraction, coverage, status in [
        (11, 'EEZ_A', 'A', 'EEZ', 2, 20, 1, 1, 1, 'available'),
        (12, 'LME_B', 'B', 'LME', 0, 0, 2, 0, '', 'available'),
        (13, 'HS_C', 'C', 'High Seas', '', '', '', '', '', 'empty_catch_archive')]:
        for col, value in zip('ABCDEFGHIJ', [uid, name, kind, catch, ppr, fraction, rank, 1 if rank else '', coverage, status]):
            summary[f'{col}{row}'] = ('INDEX(A1,1)', value)
    sheets['Global Estimation'] = {'validation': True, 'cells': summary}
    annual_cells = {f'{chr(65+i)}1': field for i, field in enumerate(annual[0])}
    for row, values in enumerate(annual, 2):
        annual_cells.update({f'{chr(65+i)}{row}': value for i, value in enumerate(values.values())})
    sheets['Annual Regional PPR'] = {'cells': annual_cells}
    sheets['Selected Regions'] = {'cells': {'A1': 'unit_id', 'A2': 'EEZ_A', 'A3': 'LME_B', 'A4': 'HS_C'}}
    sheets['Available Years'] = {'cells': {'A1': 'year', 'A2': 1950, 'A3': 2019}}
    sheets['Selected Year'] = {'cells': {}}
    sheets['Spatial Coverage'] = {'cells': {'A1': 'Definition'}}
    write_xlsx(final, sheets, styles=True, table=True)
    return source, final, annual_path, selected_path, sheets


def check(paths):
    return validator().validate_workbooks(*paths[:4], expected_original_count=1)


def test_validates_saved_values_with_real_zero_missing_and_changed_xml_ids(tmp_path):
    paths = fixture(tmp_path)
    report = check(paths)
    assert report['status'] == 'passed'
    assert report['annual_row_count'] == 4
    assert report['selected_count'] == 3
    assert report['default_year_ppr'] == 20
    assert report['original_sheets_preserved'] == ['Original']


@pytest.mark.parametrize('location,value,message', [
    ('Original/B2', ('1+1', 3), 'Original/B2'),
    ('Original/B2', ('2+0', 2), 'formula'),
    ('Global Estimation/B5', ('SUM(E11:E13)', 99), 'B5'),
    ('Global Estimation/E12', ('INDEX(A1,1)', ''), 'E12'),
    ('Global Estimation/E13', ('INDEX(A1,1)', 0), 'E13'),
    ('Global Estimation/A11', ('INDEX(A1,1)', 'EEZ_X'), 'membership'),
    ('Global Estimation/G12', ('INDEX(A1,1)', 1), 'G12'),
    ('Global Estimation/H12', ('INDEX(A1,1)', .5), 'H12'),
    ('Global Estimation/B3', 1950, 'B3'),
    ('Global Estimation/G12', 2, 'live formula'),
    ('Annual Regional PPR/H2', 21, 'ppr_species'),
    ('Selected Year/Z99', ('1/0', '#DIV/0!'), 'Excel error'),
])
def test_rejects_changed_source_and_plausible_but_wrong_saved_outputs(tmp_path, location, value, message):
    paths = fixture(tmp_path)
    name, address = location.split('/')
    paths[4][name]['cells'][address] = value
    write_xlsx(paths[1], paths[4], styles=True, table=True)
    with pytest.raises(AssertionError, match=message):
        check(paths)


@pytest.mark.parametrize('change,message', [('validation', 'validation'), ('freeze', 'freeze'), ('table', 'table'), ('row', 'annual row')])
def test_rejects_lost_controls_original_features_and_data_rows(tmp_path, change, message):
    paths = fixture(tmp_path)
    if change == 'validation':
        paths[4]['Global Estimation']['validation'] = False
    elif change == 'freeze':
        paths[4]['Original']['freeze'] = 2
    elif change == 'table':
        paths[4]['Original']['table_ref'] = 'A1:B3'
    else:
        paths[4]['Annual Regional PPR']['cells']['A6'] = 'unexpected'
    write_xlsx(paths[1], paths[4], styles=True, table=True)
    with pytest.raises(AssertionError, match=message):
        check(paths)


def test_allows_numeric_roundoff_without_changing_original_meaning(tmp_path):
    paths = fixture(tmp_path)
    paths[4]['Original']['cells']['B2'] = ('1+1', 2.0000000001)
    write_xlsx(paths[1], paths[4], styles=True, table=True)
    assert check(paths)['status'] == 'passed'


def test_reports_changed_number_format_instead_of_treating_style_ids_as_meaning(tmp_path):
    paths = fixture(tmp_path)
    write_xlsx(paths[1], paths[4], styles=True, table=True, second_numfmt=2)
    report = check(paths)
    assert report['semantic_style_change_count'] == 4
    assert report['semantic_style_changes_first_25'][0]['saved']['number_format'] == '0.00'
