"""Read-only independent ZIP/XML audit of a saved historical summary workbook.

This validates exported caches and formula preservation, not Excel recalculation.
The builder's separate multi-year runtime tests remain necessary. No workbook is
modified; the optional CLI report is the only output written by this tool.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile


NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
ERRORS = {'#REF!', '#DIV/0!', '#VALUE!', '#NAME?', '#N/A', '#NUM!', '#NULL!', '#SPILL!', '#CALC!'}
NEW_SHEETS = {'Global Estimation', 'Annual Regional PPR', 'Selected Regions',
              'Selected Year', 'Available Years', 'Spatial Coverage'}
TEXT_FIELDS = {'lookup_key', 'unit_id', 'region_name', 'region_type', 'source_data_status'}
NUMBER_FORMATS = {0: 'General', 1: '0', 2: '0.00', 3: '#,##0', 4: '#,##0.00',
                  9: '0%', 10: '0.00%', 11: '0.00E+00', 14: 'mm-dd-yy', 49: '@'}


def _target(part, relative):
    return relative.lstrip('/') if relative.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(part), relative))


def _relationships(archive, part):
    path = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part)+'.rels')
    if path not in archive.namelist():
        return {}
    return {r.get('Id'): _target(part, r.get('Target')) for r in ET.fromstring(archive.read(path))}


def _text(element):
    return '' if element is None else ''.join(t.text or '' for t in element.findall('.//m:t', NS))


def _xml_semantics(element, *, ignored=frozenset()):
    if element is None:
        return None
    return (element.tag.split('}')[-1], tuple(sorted((k, v) for k, v in element.attrib.items() if k not in ignored)),
            (element.text or '').strip(), tuple(_xml_semantics(child, ignored=ignored) for child in element))


def _styles(archive):
    if 'xl/styles.xml' not in archive.namelist():
        return [None]
    root = ET.fromstring(archive.read('xl/styles.xml'))
    formats = {int(e.get('numFmtId')): e.get('formatCode') for e in root.findall('m:numFmts/m:numFmt', NS)}
    fonts = root.findall('m:fonts/m:font', NS)
    fills = root.findall('m:fills/m:fill', NS)
    borders = root.findall('m:borders/m:border', NS)
    values = []
    for xf in root.findall('m:cellXfs/m:xf', NS):
        number = int(xf.get('numFmtId', '0'))
        entry = {'number_format': formats.get(number, NUMBER_FORMATS.get(number, f'builtin:{number}'))}
        for label, entries in [('font', fonts), ('fill', fills), ('border', borders)]:
            index = int(xf.get(label+'Id', '0'))
            entry[label] = _xml_semantics(entries[index]) if entries else None
        entry['alignment'] = _xml_semantics(xf.find('m:alignment', NS))
        entry['protection'] = _xml_semantics(xf.find('m:protection', NS))
        values.append(entry)
    return values or [None]


def read_workbook(path):
    """Resolve relationships/shared strings and reject every saved Excel error."""
    result = {}
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [_text(e) for e in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        styles = _styles(archive)
        relationships = _relationships(archive, 'xl/workbook.xml')
        root = ET.fromstring(archive.read('xl/workbook.xml'))
        for entry in root.findall('m:sheets/m:sheet', NS):
            name = entry.get('name')
            assert name not in result, f'Duplicate sheet {name}'
            part = relationships[entry.get(RID)]
            sheet = ET.fromstring(archive.read(part))
            cells = {}
            for cell in sheet.findall('m:sheetData/m:row/m:c', NS):
                address, kind = cell.get('r'), cell.get('t')
                value = cell.find('m:v', NS)
                raw = value.text if value is not None else None
                if kind == 's':
                    raw = strings[int(raw)]
                elif kind == 'inlineStr':
                    raw = _text(cell.find('m:is', NS))
                elif raw is not None and kind not in ('str', 'e', 'd'):
                    raw = float(raw)
                assert kind != 'e' and not (isinstance(raw, str) and raw in ERRORS), f'Excel error {name}/{address}: {raw}'
                formula = cell.find('m:f', NS)
                assert formula is None or formula.get('t') != 'shared', f'Shared formula requires expansion: {name}/{address}'
                cells[address] = {'value': raw, 'formula': formula.text or '' if formula is not None else None,
                                  'style': styles[int(cell.get('s', '0'))]}
            pane = sheet.find('m:sheetViews/m:sheetView/m:pane', NS)
            freeze = None
            if pane is not None and pane.get('state', '').startswith('frozen'):
                freeze = (float(pane.get('xSplit', 0)), float(pane.get('ySplit', 0)), pane.get('topLeftCell'))
            tables = []
            sheet_relations = _relationships(archive, part)
            for item in sheet.findall('m:tableParts/m:tablePart', NS):
                table = ET.fromstring(archive.read(sheet_relations[item.get(RID)]))
                tables.append(_xml_semantics(table, ignored={'id'}))
            validations = [dict(element.attrib, formula1=element.findtext('m:formula1', namespaces=NS))
                           for element in sheet.findall('m:dataValidations/m:dataValidation', NS)]
            result[name] = {'cells': cells, 'freeze': freeze, 'tables': sorted(tables, key=str),
                            'validations': validations, 'state': entry.get('state', 'visible')}
    return result


def _blank(value):
    return value is None or value == ''


def check_value(actual, expected, label, *, tolerance=1e-9):
    if _blank(expected):
        assert _blank(actual), f'{label}: expected blank, found {actual!r}'
    elif isinstance(expected, (int, float)):
        assert isinstance(actual, (int, float)) and math.isfinite(actual) and math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), f'{label}: {actual!r} != {expected!r}'
    else:
        assert actual == expected, f'{label}: {actual!r} != {expected!r}'


def _formula(value):
    return value.lstrip('=') if value is not None else None


def _value(sheet, address):
    return sheet['cells'].get(address, {}).get('value')


def _csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    assert rows, f'Empty input table {path}'
    return rows


def _typed(value, field):
    if field in TEXT_FIELDS or _blank(value):
        return value
    try:
        return float(value)
    except (ValueError, TypeError):
        return value


def _table(sheet):
    headers = {cell['value']: address[:-1] for address, cell in sheet['cells'].items()
               if re.fullmatch(r'[A-Z]+1', address) and not _blank(cell['value'])}
    rows = sorted({int(re.search(r'\d+$', address)[0]) for address, cell in sheet['cells'].items()
                   if int(re.search(r'\d+$', address)[0]) > 1 and not _blank(cell['value'])})
    return headers, [(row, {field: _value(sheet, f'{column}{row}') for field, column in headers.items()}) for row in rows]


def _contains_cell(sqref, column, row):
    def coordinates(value):
        match = re.fullmatch(r'\$?([A-Z]+)\$?(\d+)', value)
        if not match:
            return None
        col = 0
        for letter in match[1]:
            col = col*26 + ord(letter)-64
        return col, int(match[2])
    wanted = coordinates(f'{column}{row}')
    for span in sqref.split():
        parts = span.split(':')
        first, last = coordinates(parts[0]), coordinates(parts[-1])
        if first and last and first[0] <= wanted[0] <= last[0] and first[1] <= wanted[1] <= last[1]:
            return True
    return False


def validate_workbooks(source, workbook, annual_csv, selected_csv, *, expected_original_count=13, default_year=2019):
    original, final = read_workbook(source), read_workbook(workbook)
    assert len(original) == expected_original_count, f'Expected {expected_original_count} original sheets, found {len(original)}'
    assert set(final) == set(original) | NEW_SHEETS, 'Original/new sheet names differ from required inventory'
    assert list(final)[:len(original)] == list(original), 'Original sheet order changed'
    style_changes = []
    original_formula_count = 0
    for name, before in original.items():
        after = final[name]
        assert before['state'] == after['state'], f'{name}: sheet visibility changed'
        assert before['freeze'] == after['freeze'], f'{name}: freeze panes changed'
        assert before['tables'] == after['tables'], f'{name}: table definitions changed'
        for address in set(before['cells']) | set(after['cells']):
            left = before['cells'].get(address, {})
            right = after['cells'].get(address, {})
            check_value(right.get('value'), left.get('value'), f'{name}/{address}')
            assert _formula(left.get('formula')) == _formula(right.get('formula')), f'{name}/{address}: original formula changed'
            original_formula_count += left.get('formula') is not None
            if not _blank(left.get('value')) and left.get('style') != right.get('style'):
                style_changes.append({'sheet': name, 'cell': address, 'source': left.get('style'), 'saved': right.get('style')})
    annual = [{field: _typed(value, field) for field, value in row.items()} for row in _csv(annual_csv)]
    selected = _csv(selected_csv)
    selected_ids = [row['unit_id'] for row in selected]
    assert len(set(selected_ids)) == len(selected_ids), 'Duplicate selected CSV unit'
    headers, data_rows = _table(final['Annual Regional PPR'])
    assert len(data_rows) == len(annual), f'annual row count: {len(data_rows)} != {len(annual)}'
    assert set(annual[0]) <= set(headers), 'Annual data headers missing'
    expected_annual = {(row['unit_id'], int(row['year'])): row for row in annual}
    assert len(expected_annual) == len(annual), 'Duplicate annual CSV unit-year'
    actual_keys = set()
    for row_number, values in data_rows:
        key = (values.get('unit_id'), int(values['year']))
        assert key in expected_annual and key not in actual_keys, f'Unexpected/duplicate annual unit-year {key}'
        actual_keys.add(key)
        for field, value in expected_annual[key].items():
            check_value(values.get(field), value, f'Annual Regional PPR/{headers[field]}{row_number}/{field}')
    _, member_rows = _table(final['Selected Regions'])
    membership = [values.get('unit_id') for _, values in member_rows]
    assert len(membership) == len(selected_ids) and set(membership) == set(selected_ids), 'Selected Regions membership mismatch'
    years = sorted({int(row['year']) for row in annual})
    _, year_rows = _table(final['Available Years'])
    assert [values.get('year') for _, values in year_rows] == years, 'Available Years list differs from annual CSV'
    summary = final['Global Estimation']
    validations = [v for v in summary['validations'] if v.get('type') == 'list' and _contains_cell(v.get('sqref', ''), 'B', 3) and v.get('formula1')]
    assert validations, 'Global Estimation/B3 year-list validation is missing'
    check_value(_value(summary, 'B3'), default_year, 'Global Estimation/B3 default year')
    check_value(_value(summary, 'B4'), len(selected_ids), 'Global Estimation/B4 selected count')
    expected = [r for r in annual if r['year'] == default_year and r['unit_id'] in selected_ids]
    available = sorted((r for r in expected if r['source_data_status'] == 'available'),
                       key=lambda r: (-r['ppr_species'], r['unit_id']))
    total = math.fsum(r['ppr_species'] for r in available)
    for address, value in [('B5', total), ('B6', math.fsum(r['total_catch_tonnes'] for r in available)),
                           ('B7', math.fsum(r['missing_tl_catch_tonnes'] for r in available)),
                           ('B8', len(selected_ids)-len(available))]:
        check_value(_value(summary, address), value, f'Global Estimation/{address}')
        assert summary['cells'][address]['formula'], f'Global Estimation/{address} lost live formula'
    ranking_ids = [_value(summary, f'A{row}') for row in range(11, len(selected_ids)+11)]
    assert len(set(ranking_ids)) == len(selected_ids) and set(ranking_ids) == set(selected_ids), 'Global Estimation membership mismatch'
    cumulative = 0.0
    by_id = {r['unit_id']: r for r in expected}
    for offset, uid in enumerate(ranking_ids):
        row = offset+11
        values = by_id.get(uid)
        for column in 'ABCDEFGHIJ':
            assert summary['cells'].get(f'{column}{row}', {}).get('formula'), f'Global Estimation/{column}{row} lost live formula'
        if offset < len(available):
            expected_row = available[offset]
            assert uid == expected_row['unit_id'], f'Global Estimation/A{row}: ranking order mismatch'
            cumulative += expected_row['ppr_species']
            coverage = expected_row['matched_catch_tonnes']/expected_row['total_catch_tonnes'] if expected_row['total_catch_tonnes'] else ''
            expected_values = {'B': expected_row['region_name'], 'C': expected_row['region_type'],
                'D': expected_row['total_catch_tonnes'], 'E': expected_row['ppr_species'],
                'F': expected_row['ppr_species']/total if total else '', 'G': offset+1,
                'H': cumulative/total if total else '', 'I': coverage, 'J': 'available'}
        else:
            expected_values = {column: '' for column in 'DEFGHI'}
            expected_values['J'] = values['source_data_status'] if values else 'missing_year'
        for column, value in expected_values.items():
            check_value(_value(summary, f'{column}{row}'), value, f'Global Estimation/{column}{row}')
    formula_count = sum(c['formula'] is not None for s in final.values() for c in s['cells'].values())
    return {'status': 'passed', 'source_workbook_sha256': hashlib.sha256(Path(source).read_bytes()).hexdigest(),
            'output_workbook_sha256': hashlib.sha256(Path(workbook).read_bytes()).hexdigest(),
            'original_sheets_preserved': list(original), 'original_formula_count': original_formula_count,
            'saved_formula_count': formula_count, 'annual_row_count': len(annual), 'selected_count': len(selected_ids),
            'default_year': default_year, 'default_year_ppr': total, 'available_selected_regions': len(available),
            'year_list': years, 'year_list_validation_present': True, 'excel_error_cells': 0,
            'original_freeze_panes_and_tables_preserved': True, 'semantic_style_change_count': len(style_changes),
            'semantic_style_changes_first_25': style_changes[:25],
            'limitations': ['Saved cached values and formulas inspected without recalculating Excel.',
                            'Style changes are reported for review, not silently treated as equivalent.',
                            'Multi-year recalculation is checked separately by the workbook builder.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--workbook', type=Path, required=True)
    parser.add_argument('--annual', type=Path, required=True)
    parser.add_argument('--selected', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--expected-original-count', type=int, default=13)
    parser.add_argument('--default-year', type=int, default=2019)
    args = parser.parse_args()
    protected = [args.source.resolve(), args.workbook.resolve(), args.annual.resolve(), args.selected.resolve()]
    assert args.report.resolve() not in protected, 'Report must not overwrite a workbook or input CSV'
    result = validate_workbooks(args.source, args.workbook, args.annual, args.selected,
                                expected_original_count=args.expected_original_count, default_year=args.default_year)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'semantic_style_changes_first_25'}, indent=2))


if __name__ == '__main__':
    main()
