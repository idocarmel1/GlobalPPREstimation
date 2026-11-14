"""Publication API for the frozen LME003 retained-only preparation.

The preparation file remains unchanged as execution evidence. This wrapper adds
buffer authentication and post-write input checks without rebuilding arithmetic.
Only this wrapper's apply(publication) is the intended publication entry point.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math, os, shutil, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
STAGE_SCRIPT = SCRIPT.with_name('stage_lme003_adoption.py')
spec = importlib.util.spec_from_file_location('_frozen_lme003_staging', STAGE_SCRIPT)
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)
ROOT, MODEL, REGION = stage.ROOT, stage.MODEL, stage.REGION
DEFAULT_PACKAGE = RUN / 'outputs/current_adoption_final'
GUARD = RUN / 'outputs/publication_guard.json'


def _display_tables():
    accounting = stage.read(stage.RAW / 'outputs/floor_accounting.json')['floor_info']
    records = stage.read(stage.RAW / 'outputs/ee_floor_source_provenance.json')
    stage.require(accounting['use_ee_floor'] is True and accounting['ee_floor'] == .1, 'Wrong display floor evidence')
    stage.require(len(records) == 94 and sum(r['applied'] for r in records) == len(accounting['affected_groups']), 'Incomplete display floor ledger')
    summary = [['use_ee_floor', True], ['ee_floor', .1], ['ee_threshold', .1],
        ['affected_group_count', len(accounting['affected_groups'])],
        ['external_mortality_export_total', accounting['external_mortality_export_total']],
        ['assumption', accounting['assumption']], ['application_stage', accounting['application_stage']],
        ['provenance', stage.relative(stage.RAW / 'inventory/evidence_index.json', MODEL)],
        ['source_EE_basis', 'Accepted canonical author-equation variant; source-unknown publication EE remains separately recorded.'],
        ['source_M0_basis', 'Derived by archived ModelData as P*(1-EE); raw independent other_mort remains -9999/unknown.']]
    columns = list(records[0])
    stage.require(all(set(r) == set(columns) for r in records), 'Display ledger columns differ')
    def cell(value):
        if isinstance(value, dict) and value.get('type') == 'float' and value.get('value') in {'nan', 'positive_infinity', 'negative_infinity'}: return None
        return value
    return {'EE floor': (['field', 'value'], summary), 'EE floor groups': (columns, [[cell(r[k]) for k in columns] for r in records])}


def _append_display_tables(path, tables):
    """Add typed table blocks in XML; preserve every existing cell verbatim."""
    from tools.project_core.validation.researcher_review import sheet_xml, S
    from openpyxl.utils import get_column_letter, range_boundaries
    with zipfile.ZipFile(path) as archive:
        member, sheet = sheet_xml(archive, 'Diagnostics')
        data = sheet.find(f'{{{S}}}sheetData')
        old_rows = [ET.tostring(row) for row in data]
        row_id = max(int(row.get('r')) for row in data) + 2
        dimension = sheet.find(f'{{{S}}}dimension')
        width = range_boundaries(dimension.get('ref'))[2] if dimension is not None else 1
        for name, (header, rows) in tables.items():
            for values in [['@table', name], header, *rows]:
                row = ET.SubElement(data, f'{{{S}}}row', {'r': str(row_id)})
                for column, value in enumerate(values, 1):
                    if value is None: continue
                    cell = ET.SubElement(row, f'{{{S}}}c', {'r': get_column_letter(column) + str(row_id)})
                    if isinstance(value, bool):
                        cell.set('t', 'b'); ET.SubElement(cell, f'{{{S}}}v').text = '1' if value else '0'
                    elif isinstance(value, (float, int)):
                        stage.require(math.isfinite(value), 'Nonfinite metadata cell')
                        ET.SubElement(cell, f'{{{S}}}v').text = repr(value)
                    else:
                        cell.set('t', 'inlineStr'); item = ET.SubElement(cell, f'{{{S}}}is')
                        ET.SubElement(item, f'{{{S}}}t', {'{http://www.w3.org/XML/1998/namespace}space': 'preserve'}).text = str(value)
                width = max(width, len(values)); row_id += 1
            row_id += 2
        stage.require(old_rows == [ET.tostring(row) for row in list(data)[:len(old_rows)]], 'Existing diagnostic cells changed')
        if dimension is not None: dimension.set('ref', f'A1:{get_column_letter(width)}{row_id - 1}')
        members = [(item, ET.tostring(sheet, encoding='utf-8') if item.filename == member else archive.read(item.filename)) for item in archive.infolist()]
    with zipfile.ZipFile(path, 'w') as archive:
        for item, data in members: archive.writestr(item, data)


def prepare_display_metadata():
    """Create final staged metadata from the already verified numeric package."""
    base = stage.DEFAULT_PACKAGE
    plan = stage.read(base / 'preparation.json')
    qa = stage.read(RUN / 'qa/package_verification.json')
    stage.require(qa['passed'] and qa['staged_regional_sha256'] == stage.sha(base / 'regional/LME_003.xlsx'), 'Verified numerical package required')
    stage._check_inputs(plan['consumed_inputs'])
    for item in plan['promotions']: stage.require(stage.sha(base / item['source']) == item['sha256'], 'Numeric package changed')
    stage.require(not DEFAULT_PACKAGE.exists(), 'Final package already exists')
    shutil.copytree(base, DEFAULT_PACKAGE)
    path = DEFAULT_PACKAGE / 'regional/LME_003.xlsx'
    tables = _display_tables(); _append_display_tables(path, tables)
    snapshot = DEFAULT_PACKAGE / 'model/results/regional_snapshot.xlsx'; shutil.copyfile(path, snapshot)
    manifest_path = DEFAULT_PACKAGE / 'model/results/result_manifest.json'; manifest = stage.read(manifest_path)
    manifest['snapshot_sha256'] = stage.sha(snapshot)
    manifest['retained_display_metadata'] = {'source': stage.relative(stage.RAW / 'outputs/ee_floor_source_provenance.json', MODEL),
        'source_sha256': stage.sha(stage.RAW / 'outputs/ee_floor_source_provenance.json'), 'numeric_preparation_sha256': stage.sha(base / 'preparation.json'),
        'metadata_script_sha256': stage.sha(SCRIPT), 'existing_cells_unchanged': True, 'scientific_solve_performed': False}
    stage.write(manifest_path, manifest)
    for item in plan['promotions']: item['sha256'] = stage.sha(DEFAULT_PACKAGE / item['source'])
    plan['numeric_preparation'] = {'path': stage.relative(base / 'preparation.json'), 'sha256': stage.sha(base / 'preparation.json')}
    plan['consumed_inputs'][stage.relative(base / 'preparation.json')] = stage.sha(base / 'preparation.json')
    plan['consumed_inputs'][stage.relative(SCRIPT)] = stage.sha(SCRIPT)
    plan['package'] = stage.relative(DEFAULT_PACKAGE)
    stage.write(DEFAULT_PACKAGE / 'preparation.json', plan)
    stage.write(GUARD, {'schema_version': 1, 'package': plan['package'], 'wrapper_sha256': stage.sha(SCRIPT),
        'preparation_script_sha256': stage.sha(STAGE_SCRIPT), 'preparation_json_sha256': stage.sha(DEFAULT_PACKAGE / 'preparation.json'),
        'numeric_preparation_json_sha256': stage.sha(base / 'preparation.json'), 'metadata_only_changes': list(tables), 'scientific_solve_performed': False})
    return verify_package()


def _guard(package):
    guard = stage.read(GUARD)
    stage.require(guard['wrapper_sha256'] == stage.sha(SCRIPT), 'Publication wrapper changed')
    stage.require(guard['preparation_script_sha256'] == stage.sha(STAGE_SCRIPT), 'Frozen preparation changed')
    stage.require(guard['preparation_json_sha256'] == stage.sha(package / 'preparation.json'), 'Frozen preparation plan changed')
    stage.require(guard['package'] == stage.relative(package), 'Publication package differs')
    return guard


def _verified_buffers(package, plan):
    """Authenticate each actual byte buffer once, before any production write."""
    buffers = []
    allowed = {REGION, MODEL / 'sppr_source.xlsx', MODEL / 'results/regional_snapshot.xlsx', MODEL / 'results/result_manifest.json'}
    diagnostic_root = MODEL / 'results/diagnostics' / stage.PREFIX
    seen = set()
    for item in plan['promotions']:
        source = (package / item['source']).resolve()
        target = (ROOT / item['target']).resolve()
        stage.require(source.is_relative_to(package), 'Prepared source outside package')
        stage.require(target in allowed or target.is_relative_to(diagnostic_root), 'Promotion outside approved retained-result destinations')
        stage.require(target not in seen, 'Duplicate publication target'); seen.add(target)
        data = source.read_bytes()
        stage.require(hashlib.sha256(data).hexdigest() == item['sha256'], 'Prepared source buffer changed')
        buffers.append((item, target, data))
    return buffers


def verify_package(package_path=None, *, check_inputs=True):
    package = Path(package_path or DEFAULT_PACKAGE).resolve()
    before = _guard(package)
    plan = stage.verify_package(package, check_inputs=check_inputs)
    from tools.project_core.workbooks.workbooks import read_book
    from tools.project_core.maps.original_atlas_data import calculation_provenance, _group_efficiencies
    book = read_book(package / 'regional/LME_003.xlsx', sheets=['Diagnostics', 'Overview', 'Selected model groups'])
    expected = _display_tables()
    for name, table in expected.items(): stage.require(book['Diagnostics'][name] == table, 'Display floor metadata differs')
    provenance = calculation_provenance(book)
    stage.require(provenance['use_ee_floor'] is True and provenance['ee_floor'] == .1, 'Page floor provenance differs')
    from tools.project_core.workbooks.workbooks import records
    values = _group_efficiencies(records(book, 'Selected model groups', 'Groups'), records(book, 'Diagnostics', 'EE floor groups'))
    for row in records(book, 'Diagnostics', 'EE floor groups'):
        stage.require(values[row['group_name']]['ee'] == row['EE_effective'], 'Page effective EE differs')
    qa = stage.read(RUN / 'qa/package_verification.json')
    qa.update(page_floor_ON_0_1=True, page_effective_EE_exact=True, metadata_only_added_tables=list(expected))
    stage.write(RUN / 'qa/package_verification.json', qa)
    _verified_buffers(package, plan)
    stage.require(_guard(package) == before, 'Publication guard changed during verification')
    if check_inputs: stage._check_inputs(plan['consumed_inputs'])
    return plan


def apply(publication, package_path=None):
    from tools.project_core.registry.publication import _ACTIVE, publication_write
    from tools.project_core.calculations import coverage
    stage.require(publication in _ACTIVE.get() and publication.root == ROOT, 'Active publication transaction required')
    lock = ROOT / '.project-write.lock'
    stage.require(lock.is_file() and lock.read_text().strip() == str(os.getpid()), 'Project writer lock required')
    package = Path(package_path or DEFAULT_PACKAGE).resolve()
    guard = _guard(package)
    plan = verify_package(package, check_inputs=False)
    buffers = _verified_buffers(package, plan)
    targets = {item['target'] for item, _, _ in buffers}
    non_targets = {k: v for k, v in plan['consumed_inputs'].items() if k not in targets}
    stage._check_inputs(non_targets)
    if all(stage.fingerprint(target) == item['sha256'] for item, target, _ in buffers):
        stage.require(_guard(package) == guard, 'Publication guard changed')
        stage._check_inputs(non_targets)
        return {'status': 'already_applied', 'changed_units': [stage.UNIT], 'written_paths': [], 'written_hashes': {}}
    stage._check_inputs(plan['consumed_inputs'])
    for item, target, data in buffers:
        with publication_write(target, fingerprint=item['sha256']):
            coverage._write_bytes(target, data, expected_sha256=plan['consumed_inputs'][item['target']])
    stage.require(all(stage.fingerprint(target) == item['sha256'] for item, target, _ in buffers), 'Installed package differs')
    stage._check_inputs(non_targets)
    stage.require(_guard(package) == guard, 'Publication guard changed during installation')
    return {'status': 'applied', 'changed_units': [stage.UNIT], 'written_paths': [str(target) for _, target, _ in buffers],
            'written_hashes': {str(target): item['sha256'] for item, target, _ in buffers}}


if __name__ == '__main__':
    plan = prepare_display_metadata() if sys.argv[1:] == ['prepare-display'] else verify_package()
    print(json.dumps({'package': plan['package'], 'promotions': len(plan['promotions']), 'scientific_solve_performed': False, 'adoption_performed': False}), flush=True)
