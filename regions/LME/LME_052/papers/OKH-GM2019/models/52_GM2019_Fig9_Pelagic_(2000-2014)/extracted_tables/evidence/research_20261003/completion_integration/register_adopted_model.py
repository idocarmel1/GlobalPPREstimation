"""Guarded keyed registration preserving unrelated ZIP parts and central records."""
import copy
import hashlib
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
from researcher_review import S, table_rows, sheet_xml, column, column_index


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def set_cell(row, index, value):
    address = column(index + 1) + row.attrib['r']
    cell = next((c for c in row if column_index(c.attrib['r']) == index + 1), None)
    if cell is None:
        cell = ET.SubElement(row, f'{{{S}}}c', r=address)
    for child in list(cell):
        cell.remove(child)
    cell.attrib.pop('t', None)
    if value is None:
        return
    if isinstance(value, bool):
        cell.set('t', 'b')
        ET.SubElement(cell, f'{{{S}}}v').text = '1' if value else '0'
    elif isinstance(value, (int, float)):
        ET.SubElement(cell, f'{{{S}}}v').text = repr(value)
    else:
        cell.set('t', 'inlineStr')
        text = ET.SubElement(ET.SubElement(cell, f'{{{S}}}is'), f'{{{S}}}t')
        text.text = str(value)
        text.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


def register():
    spec = json.loads((HERE / 'registry_patch_spec.json').read_text(encoding='utf-8'))
    project = ROOT / 'Project.xlsx'
    model = ROOT / spec['model']['model_path']
    expected = spec['expected_model_sha256']
    if sha(model) != expected:
        raise ValueError('Final model hash changed before registry registration')
    before = sha(project)
    replacements = {}
    summaries = []
    with zipfile.ZipFile(project) as archive:
        parts = [(i, archive.read(i.filename)) for i in archive.infolist()]
        for sheet_name, table_name, key_fields, record in [
            ('Models & coverage', 'Models', ('unit_id', 'model_id'), spec['model']),
            ('Papers', 'Papers', ('article_id',), spec['paper']),
        ]:
            sheet_path, sheet = sheet_xml(archive, sheet_name)
            _, headers, header_row, rows = table_rows(archive, sheet_name, table_name)
            headers = list(rows[0][1]) if rows else headers
            matches = [(row, values) for row, values in rows if all(values.get(k) == str(record[k]) for k in key_fields)]
            if len(matches) > 1:
                raise ValueError('Duplicate central key: ' + str(key_fields))
            # The parsed rows returned above are from their own XML tree.
            data = sheet.find(f'{{{S}}}sheetData')
            keyed_r = matches[0][0].attrib['r'] if matches else None
            row = next((r for r in data if r.attrib['r'] == keyed_r), None) if keyed_r else None
            previous = matches[0][1] if matches else None
            if row is None:
                last = max(int(r.attrib['r']) for r in data)
                row = ET.SubElement(data, f'{{{S}}}row', r=str(last + 1))
                # Retain ordinary data cell styles from the last metadata record.
                example = rows[-1][0] if rows else None
                if example is not None:
                    for old in example:
                        c = ET.SubElement(row, f'{{{S}}}c', r=column(column_index(old.attrib['r'])) + row.attrib['r'])
                        if 's' in old.attrib:
                            c.set('s', old.attrib['s'])
            for i, name in enumerate(headers):
                if name in record:
                    set_cell(row, i, record[name])
            end = f'{column(len(headers))}{row.attrib["r"]}'
            dimension = sheet.find(f'{{{S}}}dimension')
            if dimension is not None:
                dimension.set('ref', 'A1:' + end)
            replacements[sheet_path] = ET.tostring(sheet, encoding='utf-8')
            for info, raw in parts:
                if not info.filename.startswith('xl/tables/') or not info.filename.endswith('.xml'):
                    continue
                table = ET.fromstring(raw)
                columns = table.find(f'{{{S}}}tableColumns')
                if columns is None or [c.get('name') for c in columns] != headers:
                    continue
                ref = table.get('ref').split(':')[0] + ':' + end
                table.set('ref', ref)
                auto = table.find(f'{{{S}}}autoFilter')
                if auto is not None:
                    auto.set('ref', ref)
                replacements[info.filename] = ET.tostring(table, encoding='utf-8')
            summaries.append({'sheet': sheet_name, 'key': {k:record[k] for k in key_fields}, 'previous': previous, 'updated': record})

        # Figure1 is sampling stations, not a study polygon. Copy the target
        # envelope explicitly as approximation; preserve every older article.
        path, geometry = sheet_xml(archive, 'Map geography')
        _, headers, _, rows = table_rows(archive, 'Map geography', 'Geometry')
        headers = list(rows[0][1]) if rows else headers
        key_name, chunk_name, text_name = headers[:3]
        key = 'article:' + spec['paper']['article_id']
        source = [(r, v) for r, v in rows if v.get(key_name) == 'LME_052']
        if not source:
            raise ValueError('Target LME052 geometry unavailable')
        existing = [(r, v) for r, v in rows if v.get(key_name) == key]
        if existing:
            if [v.get(text_name) for _,v in existing] != [v.get(text_name) for _,v in source]:
                raise ValueError('Existing new-article geometry differs; review required')
        else:
            data = geometry.find(f'{{{S}}}sheetData')
            last = max(int(r.attrib['r']) for r in data)
            for offset, (_, values) in enumerate(source, 1):
                row = ET.SubElement(data, f'{{{S}}}row', r=str(last + offset))
                for i, name in enumerate(headers):
                    set_cell(row, i, key if name == key_name else values.get(name))
            replacements[path] = ET.tostring(geometry, encoding='utf-8')

    # A recoverable byte-exact backup is kept with this adoption evidence.
    backup = HERE / ('Project.before_registration_' + before[:12] + '.xlsx')
    if not backup.exists():
        backup.write_bytes(project.read_bytes())
    fd, temp = tempfile.mkstemp(suffix='.xlsx', dir=project.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temp, 'w') as archive:
            for info, raw in parts:
                archive.writestr(info, replacements.get(info.filename, raw))
        with zipfile.ZipFile(temp) as archive:
            for sheet, table, field, expected_key in [
                ('Models & coverage','Models','model_id',spec['model']['model_id']),
                ('Papers','Papers','article_id',spec['paper']['article_id']),
            ]:
                values = [v for _,v in table_rows(archive,sheet,table)[3] if v.get(field) == expected_key]
                assert len(values) == 1
            unchanged = [i.filename for i,raw in parts if i.filename not in replacements]
            assert all(archive.read(i.filename) == raw for i,raw in parts if i.filename not in replacements)
        if sha(project) != before:
            raise ValueError('Project.xlsx changed during keyed registration; reload and retry')
        if sha(model) != expected:
            raise ValueError('Final native model changed during registration')
        os.replace(temp, project)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    result = {'schema_version':1, 'run_id':'LME052_balanced_completion_20261003',
        'project_before_sha256':before,'project_after_sha256':sha(project),
        'native_model_sha256':expected,'updated':summaries,
        'article_geometry':'target envelope; approximate whole-sea domain; exact overlap unmeasured',
        'unmodified_zip_members_verified':len(unchanged),'changed_zip_members':sorted(replacements)}
    (HERE / 'registry_registration.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'updated'},indent=2))


if __name__ == '__main__':
    register()
