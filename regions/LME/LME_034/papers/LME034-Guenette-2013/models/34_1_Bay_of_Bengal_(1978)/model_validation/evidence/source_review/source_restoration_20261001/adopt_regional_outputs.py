"""Adopt the fresh SPPR export and recalculate only model-dependent outputs."""
from __future__ import annotations

import copy
import json
import math
import os
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
from workbooks import read_book, write_book, records, rows, overview, sha, input_hash, validate_region, finite
from regional import recalculate, set_setting, set_result_hash

PATH = ROOT / 'regions/LME_034/LME_034.xlsx'
MODEL = ROOT / 'regions/LME_034/models/34_1_Bay_of_Bengal_(1978)/model.json'
SPPR = MODEL.parent / 'sppr_source.xlsx'
NOTE = ('Canonical diets retain printed Table17 proportions and Import without normalization. '
        'The researcher-authored 3 Meiobenthos→Detritus=1 override is retained. '
        'The45 omitted prey46–48 cells remain unknown (-9999), loaded numerically as zero. '
        'Normalization occurs only on the calculator copy and emits a warning. '
        'Derived biomass accumulation and detritus EE completion remain computational conventions. '
        'Native source fidelity remains unverified; model PPR remains provisional. '
        'Reviewed memberships and pooled1978 catch allocations retain their original transfer assumptions.')


def preserve_protected_xml():
    """Keep original sheet XML and mapping decimals, avoiding reserialization loss."""
    original_path = OUT / 'baseline/LME_034.xlsx'
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(original_path) as old, zipfile.ZipFile(PATH) as fresh:
        assert old.read('xl/styles.xml') == fresh.read('xl/styles.xml')
        replacements = {f'xl/worksheets/sheet{i}.xml': old.read(f'xl/worksheets/sheet{i}.xml')
                        for i in [2, 3, 6]}
        name = 'xl/worksheets/sheet5.xml'
        a, b = ET.fromstring(old.read(name)), ET.fromstring(fresh.read(name))
        old_data, new_data = a.find('m:sheetData', ns), b.find('m:sheetData', ns)
        def block_ranges(data):
            starts = []
            for row in data:
                vals = {cell.attrib['r'].rstrip('0123456789'): ''.join(cell.itertext()) for cell in row}
                if vals.get('A') == '@table':
                    starts.append((int(row.attrib['r']), vals['B']))
            return {n: (start, starts[i+1][0] if i+1 < len(starts) else 10**9)
                    for i, (start, n) in enumerate(starts)}
        old_ranges, new_ranges = block_ranges(old_data), block_ranges(new_data)
        protected = ['Matching', 'Mapping review', 'Allocation assumptions']
        for table in protected:
            assert old_ranges[table] == new_ranges[table]
        intervals = [old_ranges[n] for n in protected]
        keep_old = {int(row.attrib['r']): row for row in old_data
                    if any(start <= int(row.attrib['r']) < end for start, end in intervals)}
        all_rows = {int(row.attrib['r']): row for row in new_data}
        for number in list(all_rows):
            if any(start <= number < end for start, end in intervals):
                del all_rows[number]
        all_rows.update(keep_old)
        new_data[:] = [all_rows[n] for n in sorted(all_rows)]
        replacements[name] = ET.tostring(b, encoding='utf-8')
        fd, staged = tempfile.mkstemp(suffix='.xlsx', dir=PATH.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(staged, 'w', compression=zipfile.ZIP_DEFLATED) as target:
                for item in fresh.infolist():
                    target.writestr(item, replacements.get(item.filename, fresh.read(item.filename)))
            fresh.close()
            old.close()
            os.replace(staged, PATH)
        finally:
            if os.path.exists(staged):
                os.unlink(staged)


def main():
    baseline = read_book(OUT / 'baseline/LME_034.xlsx')
    current_sha = sha(PATH)
    disk = read_book(PATH)
    if disk != baseline:
        assert overview(disk).get('source_note') == NOTE, 'Regional workbook changed outside this adoption'
        assert overview(disk).get('results_model_sha256') == sha(MODEL)
    current = baseline
    b = copy.deepcopy(current)
    o = overview(b)
    selected = o['selected_model_id']
    config = json.loads((OUT / 'refresh_configuration.json').read_text(encoding='utf-8'))
    assert config['canonical_model_sha256'] == sha(MODEL)
    assert config['fresh_sppr_sha256'] == sha(SPPR)
    w = openpyxl.load_workbook(SPPR, read_only=True, data_only=True)
    source = list(w['groups_df'].values)
    b['Selected model groups']['Groups'] = (list(source[0]), [list(r) for r in source[1:]])
    group_rows = []
    for scope in ['all', 'inner', 'PP']:
        source = list(w['sppr_' + scope].values)
        group_rows.extend([[selected, r[1], scope, m, r[i]]
                           for r in source[1:] for i, m in enumerate(source[0]) if i >= 2])
    b['Selected model groups']['Group SPPR'] = (['model_id', 'group', 'scope', 'method', 'sppr'], group_rows)
    for name in ['model_health', 'mc_diagnostics', 'run_notes']:
        source = list(w[name].values)
        b['Diagnostics'][name] = (list(source[0]), [list(r) for r in source[1:]])
    w.close()
    prior_methods = {r['method'] for r in records(current, 'Selected model groups', 'Group SPPR')}
    fresh_methods = {r[3] for r in group_rows}
    assert fresh_methods == prior_methods == set(config['methods'])
    method_grades = {}
    for r in records(b, 'Diagnostics', 'model_health'):
        method_grades[r.get('TE_option')] = r.get('status')
    direct_options = {'new_GE': 'GE', 'new_TE_EEfix': 'TE', 'new_WithEgestion': 'With Egestion'}
    for r in rows(b, 'PPR', 'Annual'):
        method, scope = r[2], r[1]
        values = [g[4] for g in group_rows if g[2] == scope and g[3] == method]
        execution = config['method_status'][method]
        if execution != 'ok' or not any(finite(v) for v in values):
            r[6] = 'unavailable: fresh source-diet refresh ' + execution
        else:
            r[6] = ('provisional: raw Table17 input; runtime normalization; researcher Meiobenthos override; '
                    'derived biomass accumulation; source fidelity unverified')
            if method in direct_options:
                r[6] += '; diagnostic ' + str(method_grades.get(direct_options[method], 'unavailable'))
    # These hashes authenticate the freshly loaded SPPR artifact, not reused stale results.
    set_setting(b, 'results_model_id', selected)
    set_setting(b, 'results_model_sha256', sha(MODEL))
    recalculate(b, PATH)
    # Keep independent classic calculations, bounds and denominator views exactly.
    b['Classic PPR'] = copy.deepcopy(current['Classic PPR'])
    rh, rr = b['PPR–NPP']['Ratios']
    old_classic_ratios = [copy.deepcopy(r) for r in rows(current, 'PPR–NPP', 'Ratios') if not r[0]]
    b['PPR–NPP']['Ratios'] = (rh, old_classic_ratios + [r for r in rr if r[0]])
    set_setting(b, 'source_note', NOTE)
    set_setting(b, 'production_eligible', False)
    set_setting(b, 'calculation_status', 'Recalculated22 methods from raw Table17 diets; runtime normalization and researcher Meiobenthos override; provisional')
    # Source correction evidence is a terminal diagnostic record, not configuration.
    b['Diagnostics']['Source diet restoration'] = (
        ['run_id', 'canonical_model_sha256', 'source_proportions', 'researcher_override', 'missing_source_cells', 'runtime_policy', 'evidence'],
        [['LME034_source_restoration_20261001', sha(MODEL), 'Printed Table17 values, unnormalized',
          '3 Meiobenthos→Detritus=1 retained by explicit researcher instruction', 45,
          'normalize_DC=True on calculator copy;8-consumer RuntimeWarning; missing cells numerically zero',
          'validation_reports/34_1_Bay_of_Bengal_(1978)/source_restoration_20261001/table17_source_ledger.json']])
    set_setting(b, 'calculation_input_sha256', input_hash(b))
    set_result_hash(b)
    protected = [('Catch', None), ('Classic PPR', None), ('NPP', None),
                 ('PPR', 'Matching'), ('PPR', 'Mapping review'), ('PPR', 'Allocation assumptions')]
    for sheet, table in protected:
        assert (b[sheet] if table is None else b[sheet][table]) == (current[sheet] if table is None else current[sheet][table])
    assert sha(PATH) == current_sha
    write_book(PATH, b)
    preserve_protected_xml()
    saved = read_book(PATH)
    validate_region(saved, PATH)
    for sheet, table in protected:
        assert (saved[sheet] if table is None else saved[sheet][table]) == (current[sheet] if table is None else current[sheet][table])
    old_group = {(r[1], r[2], r[3]): r[4] for r in rows(current, 'Selected model groups', 'Group SPPR')}
    changes = []
    for r in rows(saved, 'Selected model groups', 'Group SPPR'):
        a, z = old_group[r[1], r[2], r[3]], r[4]
        if a != z:
            changes.append({'group': r[1], 'scope': r[2], 'method': r[3], 'prior': a, 'fresh': z,
                            'abs_difference': abs(z-a) if finite(a) and finite(z) else None})
    summary = {'schema_version': 1, 'run_id': 'LME034_source_restoration_20261001',
               'canonical_model_sha256': sha(MODEL), 'sppr_export_sha256': sha(SPPR),
               'regional_workbook_sha256': sha(PATH), 'prior_workbook_sha256': sha(OUT / 'baseline/LME_034.xlsx'),
               'methods': sorted(fresh_methods), 'group_coefficient_rows': len(group_rows),
               'method_grades': method_grades, 'protected_tables_unchanged': True,
               'protected_tables': protected, 'group_coefficient_changes': changes,
               'raw_input_warning_preserved': True, 'researcher_meiobenthos_override_preserved': True,
               'user_word_and_notebooks_written': False, 'central_integration': 'pending coordinator'}
    (OUT / 'regional_adoption.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: summary[k] for k in ['regional_workbook_sha256', 'method_grades', 'group_coefficient_rows', 'protected_tables_unchanged']}, ensure_ascii=False))


def finish_saved_adoption():
    # Resume only our own already-calculated saved output after an XML preservation
    # step failed while its ZIP reader still held the Windows file open.
    config = json.loads((OUT / 'refresh_configuration.json').read_text(encoding='utf-8'))
    assert config['canonical_model_sha256'] == sha(MODEL)
    assert config['fresh_sppr_sha256'] == sha(SPPR)
    preserve_protected_xml()
    prior, saved = read_book(OUT / 'baseline/LME_034.xlsx'), read_book(PATH)
    assert overview(saved)['results_model_sha256'] == sha(MODEL)
    assert overview(saved)['source_note'] == NOTE
    validate_region(saved, PATH)
    protected = [('Catch', None), ('Classic PPR', None), ('NPP', None),
                 ('PPR', 'Matching'), ('PPR', 'Mapping review'), ('PPR', 'Allocation assumptions')]
    for sheet, table in protected:
        assert (saved[sheet] if table is None else saved[sheet][table]) == (prior[sheet] if table is None else prior[sheet][table])
    old = {(r[1],r[2],r[3]):r[4] for r in rows(prior,'Selected model groups','Group SPPR')}
    changes=[]
    for r in rows(saved,'Selected model groups','Group SPPR'):
        a,z=old[r[1],r[2],r[3]],r[4]
        if a!=z: changes.append({'group':r[1],'scope':r[2],'method':r[3],'prior':a,'fresh':z,
                                'abs_difference':abs(z-a) if finite(a) and finite(z) else None})
    summary={'schema_version':1,'run_id':'LME034_source_restoration_20261001',
             'canonical_model_sha256':sha(MODEL),'sppr_export_sha256':sha(SPPR),
             'regional_workbook_sha256':sha(PATH),'prior_workbook_sha256':sha(OUT/'baseline/LME_034.xlsx'),
             'methods':config['methods'],'group_coefficient_rows':len(rows(saved,'Selected model groups','Group SPPR')),
             'method_grades':{r['TE_option']:r['status'] for r in records(saved,'Diagnostics','model_health')},
             'protected_tables_unchanged':True,'protected_tables':protected,'group_coefficient_changes':changes,
             'protected_xml_preserved':True,'raw_input_warning_preserved':True,
             'researcher_meiobenthos_override_preserved':True,'user_word_and_notebooks_written':False,
             'central_integration':'pending serialized update'}
    (OUT/'regional_adoption.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['regional_workbook_sha256','method_grades','group_coefficient_rows','protected_tables_unchanged']},ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    finish_saved_adoption() if '--finish-saved' in sys.argv else main()
