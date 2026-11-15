"""Same-runtime archived/current comparison; no scientific input adoption."""
from __future__ import annotations
import argparse
import copy
import gzip
import hashlib
import importlib.util
import inspect
import json
import math
import os
import posixpath
import re
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone

for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
WORK = Path(__file__).resolve().parents[1]
EXECUTED_RUNNER = Path(__file__).read_bytes()
sys.path.insert(0, str(ROOT))
from tools.scientific_helpers.sppr import method_coverage as adapter
from tools.project_core.workbooks.workbooks import read_book, records
from tools.scientific_helpers.sppr.ppr_scopes import read_scopes
import numpy as np

spec = importlib.util.spec_from_file_location('_coverage_completion_driver', Path(__file__).with_name('run_completion.py'))
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
METHODS = ('new_GE', 'new_TE_EEfix', 'SPPR_1995_TE0.1')
YEARS = tuple(range(1950, 2020))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode('utf-8')
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def finite(value):
    return isinstance(value, (int, float, np.number)) and not isinstance(value, bool) and math.isfinite(value)


def pin_current_engine():
    directory = WORK/'inputs/current_engine_comparison'
    directory.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name in adapter.ENGINE_FILES:
        source, target = adapter.ENGINE/name, directory/name
        if not target.exists():
            target.write_bytes(source.read_bytes())
        hashes[name] = sha(target)
    prefix = '_comparison_current_'+hashes['PPRCalculator.py'][:16]
    data = adapter._isolated_module(directory/'ModelData.py', prefix+'_data', {})
    utils = adapter._isolated_module(directory/'utils.py', prefix+'_utils', {})
    module = adapter._isolated_module(directory/'PPRCalculator.py', prefix+'_calculator',
                                     {'ModelData': data, 'utils': utils})
    return module.PPRCalculator, hashes, directory


def comparison_table(path, sheet, table):
    """Read one plain @table directly, without parsing unrelated workbook styles."""
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    relation = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        sheet_id = next(node.attrib[relation] for node in workbook.findall('s:sheets/s:sheet', ns)
                        if node.attrib['name'] == sheet)
        relations = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        target = next(node.attrib['Target'] for node in relations if node.attrib['Id'] == sheet_id)
        target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(node.itertext()) for node in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        active = False; header = None; rows = []
        with archive.open(target) as stream:
            for event, element in ET.iterparse(stream, events=['end']):
                if element.tag != '{'+ns['s']+'}row':
                    continue
                cells = []
                for cell in element:
                    letters = re.match(r'[A-Z]+', cell.attrib['r']).group()
                    column = 0
                    for letter in letters: column = column*26+ord(letter)-64
                    while len(cells) < column: cells.append(None)
                    if cell.find('s:f', ns) is not None:
                        raise ValueError('Formula in authoritative comparison input: '+str(path))
                    value = cell.find('s:v', ns); kind = cell.attrib.get('t')
                    if kind == 'inlineStr':
                        value = ''.join(node.text or '' for node in cell.findall('.//s:t', ns))
                    elif value is None:
                        value = None
                    elif kind == 's':
                        value = strings[int(value.text)]
                    elif kind == 'b':
                        value = value.text == '1'
                    elif kind in ('str', 'e'):
                        value = value.text
                    else:
                        value = float(value.text)
                        if value.is_integer(): value = int(value)
                    cells[column-1] = value
                element.clear()
                while cells and cells[-1] is None: cells.pop()
                if not cells: continue
                if cells[0] == '@table':
                    if active: break
                    active = len(cells) > 1 and cells[1] == table
                elif active and header is None:
                    header = [int(value) if isinstance(value, str) and value.isdigit() and int(value) in YEARS else value for value in cells]
                elif active:
                    rows.append((cells+[None]*len(header))[:len(header)])
    if header is None:
        raise ValueError('Required comparison table absent: '+sheet+'/'+table)
    return {sheet: {table: (header, rows)}}


def catch_context(item, old_model, review, basis='catch'):
    model_dir = ROOT/item['model_dir']
    cached_path = model_dir/'results/diagnostics/engine_comparison_20261114/group_catch_weights.json'
    cached = driver.read(cached_path) if cached_path.exists() else {}
    if (cached.get('schema_version') == 2 and cached.get('model_id') == item['model_id']
            and cached.get('excluded_group_ids') == review.get('excluded_group_ids', [])
            and basis in cached.get('bases', {})):
        entry = cached['bases'][basis]
        context = {**entry['context'], 'group_catch_weights_reference': cached_path.relative_to(ROOT).as_posix(),
                   'group_catch_weights_sha256': sha(cached_path)}
        return {name: np.asarray(values) for name, values in entry['weights'].items()}, context
    region_dir = next(p for p in model_dir.parents if p.name == item['unit_id'])
    region_file = region_dir/(item['unit_id']+'.xlsx')
    snapshot = model_dir/'results/regional_snapshot.xlsx'
    local = comparison_table(region_file, 'Catch', 'Catch')
    saved = comparison_table(snapshot, 'PPR', 'Matching')
    excluded_ids = review.get('excluded_group_ids', [])
    excluded_names = set()
    for identifier in excluded_ids:
        if identifier in old_model.name2seq:
            excluded_names.add(identifier)
        elif identifier in old_model.seq2name:
            excluded_names.add(old_model.seq2name[identifier])
        else:
            raise ValueError('Researcher exclusion absent from runtime: '+str(identifier))
    mappings = {}
    for row in records(saved, 'PPR', 'Matching'):
        if row['model_id'] != item['model_id']:
            raise ValueError('Snapshot mapping belongs to another model')
        if row.get('group') is not None and finite(row.get('weight')):
            mappings.setdefault(row['taxon'], []).append((row['group'], row['weight']))
    catches = {row['taxon']: [row.get(year) for year in YEARS]
               for row in records(local, 'Catch', 'Catch') if row['catch_basis'] == basis}
    weights = {name: np.zeros(len(YEARS)) for name in old_model.name2seq}
    unallocated = np.zeros(len(YEARS)); excluded = np.zeros(len(YEARS))
    missing_catch_cells = []
    for taxon, values in catches.items():
        assignment = mappings.get(taxon, [])
        for i, amount in enumerate(values):
            if not finite(amount):
                missing_catch_cells.append({'taxon': taxon, 'year': YEARS[i]}); continue
            if not assignment:
                unallocated[i] += amount
            for group, fraction in assignment:
                if group not in weights:
                    raise ValueError('Mapped group absent from runtime: '+str(group))
                if group in excluded_names:
                    excluded[i] += amount*fraction
                else:
                    weights[group][i] += amount*fraction
    context = {'catch_basis': basis, 'unidentified_treatment': 'method',
                     'excluded_group_ids': excluded_ids, 'excluded_group_names': sorted(excluded_names),
                     'excluded_shares_renormalized': False,
                     'unallocated_catch_by_year': unallocated.tolist(),
                     'excluded_catch_by_year': excluded.tolist(),
                     'missing_catch_cells': missing_catch_cells,
                     'catch_workbook': str(region_file.relative_to(ROOT)), 'catch_workbook_sha256': sha(region_file),
                     'mapping_snapshot': str(snapshot.relative_to(ROOT)), 'mapping_snapshot_sha256': sha(snapshot)}
    cached.update(schema_version=2, model_id=item['model_id'], excluded_group_ids=excluded_ids)
    cached.setdefault('bases', {})[basis] = {'weights': {name: values.tolist() for name, values in weights.items()}, 'context': context}
    save(cached_path, cached)
    return weights, {**context, 'group_catch_weights_reference': cached_path.relative_to(ROOT).as_posix(),
                     'group_catch_weights_sha256': sha(cached_path)}


def annual_comparison(old, new, weights):
    result = {}
    for scope in ('all', 'inner', 'PP'):
        before = old.get('scopes', {}).get(scope, {})
        after = new.get('scopes', {}).get(scope, {})
        left = np.zeros(len(YEARS)); right = np.zeros(len(YEARS))
        left_support = np.zeros(len(YEARS)); right_support = np.zeros(len(YEARS))
        common_left = np.zeros(len(YEARS)); common_right = np.zeros(len(YEARS)); common_support = np.zeros(len(YEARS))
        missing_before = []; missing_after = []; coefficient_changes = []; absolute_changes = []; relative_changes = []
        for group, catches in weights.items():
            a, b = before.get(group), after.get(group)
            if finite(a): left += catches*a; left_support += catches
            elif catches.any(): missing_before.append(group)
            if finite(b): right += catches*b; right_support += catches
            elif catches.any(): missing_after.append(group)
            if finite(a) and finite(b):
                common_left += catches*a; common_right += catches*b; common_support += catches
                relative = abs(b-a)/abs(a) if a else (0. if b == 0 else None)
                absolute_changes.append(abs(b-a))
                if relative is not None: relative_changes.append(relative)
                if (relative is None or relative > .1 or (a*b < 0)):
                    coefficient_changes.append({'group': group, 'old': a, 'current': b,
                                                'relative_absolute_change': relative,
                                                'sign_change': bool(a*b < 0)})
        rows = []
        for i, year in enumerate(YEARS):
            a, b = (float(left[i]) if left_support[i] > 0 else None), (float(right[i]) if right_support[i] > 0 else None)
            ca = float(common_left[i]) if common_support[i] > 0 else None
            cb = float(common_right[i]) if common_support[i] > 0 else None
            rel = abs(cb-ca)/abs(ca) if ca else (0. if ca == cb == 0 else None)
            rows.append({'year': year, 'old_ppr_wet_tonnes': a, 'current_ppr_wet_tonnes': b,
                         'old_covered_catch_tonnes': float(left_support[i]), 'current_covered_catch_tonnes': float(right_support[i]),
                         'common_old_ppr_wet_tonnes': ca, 'common_current_ppr_wet_tonnes': cb,
                         'common_covered_catch_tonnes': float(common_support[i]),
                         'relative_absolute_change_common': rel,
                         'zero_to_nonzero': bool(ca == 0 and finite(cb) and cb != 0),
                         'sign_change': bool(finite(ca) and finite(cb) and ca*cb < 0),
                         'availability_change': bool((a is None) != (b is None) or not math.isclose(left_support[i], right_support[i], rel_tol=1e-12, abs_tol=1e-12))})
        finite_changes = [row['relative_absolute_change_common'] for row in rows if finite(row['relative_absolute_change_common'])]
        result[scope] = {'annual': rows, 'year_2019': rows[-1],
                         'max_relative_annual_change_common': max(finite_changes) if finite_changes else None,
                         'years_over_10_percent': [row['year'] for row in rows if row['zero_to_nonzero'] or (finite(row['relative_absolute_change_common']) and row['relative_absolute_change_common'] > .1)],
                         'years_with_sign_change': [row['year'] for row in rows if row['sign_change']],
                         'years_with_availability_change': [row['year'] for row in rows if row['availability_change']],
                         'missing_old_positive_catch_groups': missing_before, 'missing_current_positive_catch_groups': missing_after,
                         'max_absolute_coefficient_change': max(absolute_changes) if absolute_changes else None,
                         'max_relative_coefficient_change': max(relative_changes) if relative_changes else None,
                         'coefficient_changes_over_10_percent_or_sign': coefficient_changes}
    return result


def compare_pair(item, current_class, current_hashes, snapshot, review,
                 report_filename='comparison.json', methods=None):
    methods = METHODS if methods is None else methods
    model_dir = ROOT/item['model_dir']; model_path = model_dir/'model.json'
    output = model_dir/'results/diagnostics/engine_comparison_20261114'
    output.mkdir(parents=True, exist_ok=True)
    runner_path = output/'runners'/(hashlib.sha256(EXECUTED_RUNNER).hexdigest()+'.py')
    runner_path.parent.mkdir(parents=True, exist_ok=True)
    runner_path.write_bytes(EXECUTED_RUNNER)
    flags = driver.replay_flags(item)
    constructor = adapter._constructor(flags, model_path)
    old, source, notices = adapter._load(model_path, constructor, flags)
    current = copy.deepcopy(old)
    current.__class__ = current_class
    adaptations = []
    if getattr(current, 'use_ee_floor', False) and not hasattr(current, 'ee_threshold'):
        method = type(old).apply_ee_floor
        body = inspect.getsource(method)
        if 'ee_threshold' in inspect.signature(method).parameters or 'ee < ee_floor' not in body:
            raise ValueError('Old effective floor threshold cannot be authenticated from executed algorithm')
        current.ee_threshold = old.ee_floor
        adaptations.append({'attribute': 'ee_threshold', 'value': old.ee_floor,
                            'basis': 'Executed old apply_ee_floor has no independent threshold and selects ee < ee_floor; metadata for same completed state only',
                            'original_method_sha256': hashlib.sha256(body.encode()).hexdigest()})
    weights, context = catch_context(item, old, review)
    scoped = read_scopes(model_dir/'sppr_source.xlsx')
    report = {'schema_version': 1, 'unit_id': item['unit_id'], 'model_id': item['model_id'],
              'created_utc': datetime.now(timezone.utc).isoformat(), 'model_sha256': sha(model_path),
              'comparison_runner_sha256': hashlib.sha256(EXECUTED_RUNNER).hexdigest(),
              'method_scope': list(methods), 'comparison_basis': 'Identical completed runtime; class rebound only; no new loading, balancing, diet normalization or EE-floor application',
              'current_engine_hashes': current_hashes, 'old_engine_hashes': adapter.engine_identity(flags, model_path),
              'flags': flags, 'runtime_reference': source, 'restoration_notices': notices,
              'current_metadata_adaptations': adaptations, 'regional_weighting': context,
              'material_difference_rule': 'More than 10% annual PPR on common catch support, any sign change, or availability change',
              'methods': {}, 'scientific_input_adoption': False}
    for name in adapter.ENGINE_FILES:
        destination = output/'current_engine'/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((snapshot/name).read_bytes())
    for key in methods:
        settings = adapter.method_settings(key, flags, model_path)
        old_return = adapter._run(copy.deepcopy(old), settings)
        current_return = adapter._run(copy.deepcopy(current), settings)
        save(output/(key+'_old.json.gz'), old_return)
        save(output/(key+'_current.json.gz'), current_return)
        comparisons = annual_comparison(old_return, current_return, weights)
        agreement = {}
        for scope, (methods, groups) in scoped.items():
            if key not in methods: continue
            column = methods.index(key)
            a = old_return.get('scopes', {}).get(scope, {})
            checks = [math.isclose(a.get(name), values[column], rel_tol=1e-10, abs_tol=1e-12)
                      if finite(a.get(name)) and finite(values[column]) else a.get(name) is None and values[column] is None
                      for name, values in groups.items()]
            agreement[scope] = bool(all(checks))
        entry = {'old_execution_status': old_return['status'], 'current_execution_status': current_return['status'],
                 'old_reason': old_return.get('reason'), 'current_reason': current_return.get('reason'),
                 'old_diagnostic_status': (old_return.get('diagnostics') or {}).get('status'),
                 'current_diagnostic_status': (current_return.get('diagnostics') or {}).get('status'),
                 'old_matches_saved_coefficients': agreement, 'scopes': comparisons,
                 'settings': settings}
        entry['materially_different'] = old_return['status'] != current_return['status'] or any(
            value['years_over_10_percent'] or value['years_with_sign_change'] or value['years_with_availability_change']
            for value in comparisons.values())
        report['methods'][key] = entry
        save(output/report_filename, report)
        print(item['unit_id']+' '+key+' '+old_return['status']+'/'+current_return['status']+' material='+str(entry['materially_different']), flush=True)
    report['materially_different'] = any(entry['materially_different'] for entry in report['methods'].values())
    save(output/report_filename, report)
    return report


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--units', nargs='*'); args = parser.parse_args()
    inventory = json.loads((WORK/'inputs/validated_inventory.json').read_text(encoding='utf-8'))
    project = read_book(ROOT/'Project.xlsx', sheets=['Models & coverage'])
    reviews = {(row['unit_id'], row['model_id']): json.loads(row.get('researcher_review_summary') or '{}')
               for row in records(project, 'Models & coverage', 'Models')}
    current, hashes, snapshot = pin_current_engine()
    summary_path = WORK/'outputs/engine_comparison_summary.json'
    summary = (json.loads(summary_path.read_text(encoding='utf-8')) if args.units and summary_path.is_file() else
               {'method_scope': list(METHODS), 'current_engine_hashes': hashes,
                'comparison_scope_note': 'Three methods only; this comparison does not cover every deterministic formulation', 'models': []})
    for item in inventory['pairs']:
        if args.units and item['unit_id'] not in args.units: continue
        try:
            report = compare_pair(item, current, hashes, snapshot, reviews[(item['unit_id'], item['model_id'])])
            compact = {'unit_id': item['unit_id'], 'model_id': item['model_id'], 'materially_different': report['materially_different'],
                       'report_path': item['model_dir']+'/results/diagnostics/engine_comparison_20261114/comparison.json',
                       'methods': {key: {'materially_different': value['materially_different'],
                                         'old_status': value['old_execution_status'], 'current_status': value['current_execution_status'],
                                         'old_matches_saved_coefficients': value['old_matches_saved_coefficients'],
                                         'all_sources_2019': value['scopes']['all']['year_2019'],
                                         'max_relative_annual_all_sources': value['scopes']['all']['max_relative_annual_change_common']}
                                   for key, value in report['methods'].items()}}
        except Exception as error:
            import traceback
            compact = {'unit_id': item['unit_id'], 'model_id': item['model_id'], 'error': str(error), 'traceback': traceback.format_exc()}
            save(ROOT/item['model_dir']/'results/diagnostics/engine_comparison_20261114/error.json', compact)
            print(item['unit_id']+' ERROR '+str(error), flush=True)
        summary['models'] = [row for row in summary['models'] if row['unit_id'] != item['unit_id']]+[compact]
        save(WORK/'outputs/engine_comparison_summary.json', summary)


if __name__ == '__main__':
    main()
