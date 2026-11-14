"""Stage authenticated, approved GE/TE returns; never construct or solve a model.

Preparation writes only this run. Publication is a separate coordinator action,
guarded by the active publication transaction, writer lock and consumed hashes.
"""
from __future__ import annotations
import argparse, copy, csv, gzip, hashlib, json, math, os, shutil, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
RUN = SCRIPT.parents[1]
ROOT = next(p for p in RUN.parents if (p / 'Project.xlsx').is_file())
MODEL = RUN.parents[2]
UNIT = 'LME_003'
REGION = ROOT / 'regions/LME/LME_003/LME_003.xlsx'
RAW = MODEL / 'results/diagnostics/ee_floor_review_20261114'
PREFIX = 'method_coverage/retained_approved_GE_TE_20261114'
DEFAULT_PACKAGE = RUN / 'outputs/current_adoption_v2'
PROPOSAL = MODEL / 'model_validation/work/2026-11-14_192900_signoff/outputs/proposed_registration.json'
CANONICAL_SHA = '18ed0ba93eb9c95ce305fc03fc36cc189b4cd365d9482fd8be30f398c2508925'
REGIONAL_SHA = '1bcb76f49df4812616141075000a022d4a4d2465b28357c03d18cef9c3617957'
INDEX_SHA = 'ea6b4a364f4b31634a6c9562e7e268f0a1187d2f399c77c96de721ac438d826f'
PROPOSAL_SHA = 'e8a47c8c9f4ab1090ba79ceab68fceebd442374e5b7617e243a46a947bee71c8'
DOCX_SHA = '64d7df9a743268bf9808c988144c8e5a7d0005b4297b8f017b2710e5b0062c3c'
METHODS = {'new_GE': 'GE', 'new_TE_EEfix': 'TE'}
UNAVAILABLE = 'No approved retained result for the EE-floor ON 0.1 runtime; previous-runtime values remain in the byte-preserved historical package. No new execution was requested.'
sys.path.insert(0, str(ROOT))


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def fingerprint(path): return sha(path) if Path(path).is_file() else None
def relative(path, base=ROOT): return Path(path).resolve().relative_to(Path(base).resolve()).as_posix()
def read(path):
    path = Path(path); data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data.decode('utf-8-sig'))
def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
def require(condition, message):
    if not condition: raise ValueError(message)
def _check_inputs(inputs):
    for name, digest in inputs.items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT) and fingerprint(path) == digest, 'Consumed input changed: ' + name)
def _near(a, b): return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def authenticate():
    """Authenticate immutable full returns, matrices, scope reductions and runtime."""
    require(sha(MODEL / 'model.json') == CANONICAL_SHA, 'Canonical input changed')
    require(sha(PROPOSAL) == PROPOSAL_SHA, 'Approved handoff changed')
    require(sha(MODEL / 'model_validation/validation.docx') == DOCX_SHA, 'Signed report changed')
    index = RAW / 'inventory/evidence_index.json'
    require(sha(index) == INDEX_SHA, 'Retained evidence index changed')
    files = {SCRIPT, index, PROPOSAL, MODEL / 'model_validation/validation.docx'}
    for item in read(index)['artifacts']:
        path = (index.parent / item['path']).resolve()
        require(item['availability'] == 'present' and path.is_relative_to(ROOT) and sha(path) == item['sha256'], 'Retained artifact changed: ' + str(path))
        files.add(path)
    identity = read(RAW / 'inventory/execution_identity.json')
    require(identity['canonical_input']['sha256'] == CANONICAL_SHA, 'Execution input differs')
    require(identity['floor_configuration'] == {'use_ee_floor': True, 'ee_floor': .1, 'ee_threshold': .1}, 'Wrong floor configuration')
    require(identity['compatibility']['archived_to_current_ast'] is False, 'Unexpected equivalence claim')
    engines = {name: RAW / 'code/audited' / name for name in ('ModelData.py', 'utils.py')}
    engines['PPRCalculator.py'] = RAW / 'code/floor/PPRCalculator.py'
    hashes = {**identity['archived_base_engine_hashes'], 'PPRCalculator.py': identity['calculation_engine']['sha256']}
    for name, path in engines.items(): require(sha(path) == hashes[name], 'Actual engine hash differs: ' + name)
    with (RAW / 'outputs/effective_groups.csv').open(encoding='utf-8-sig', newline='') as stream:
        groups = list(csv.DictReader(stream))
    names = {int(r['group_seq']): r['group_name'] for r in groups}
    require(len(names) == len(groups) == 94 and names[94] == 'diet_import', 'Effective group identity differs')
    metadata = read(RAW / 'outputs/matrix_metadata.json')
    scopes = {}; diagnostics = {}; audit = {}
    for key, option in METHODS.items():
        full = read(RAW / ('outputs/' + option + '_full_return.json.gz'))
        diagnostic = read(RAW / ('outputs/' + option + '_direct_return.json'))
        matrix = read(RAW / ('outputs/' + option + '_source_matrix.json'))
        scoped = read(RAW / ('outputs/' + option + '_scope_coefficients.json'))
        check = read(RAW / ('outputs/' + option + '_verification.json'))
        require(full['type'] == 'tuple' and len(full['items']) == 4, 'Unexpected full-return schema')
        require(full['items'][0] == diagnostic and full['items'][1] == matrix, 'Full return disagrees with separately retained outputs')
        for position in (2, 3):
            require(full['items'][position] == read(RAW / f'outputs/{option}_returned_matrix_{position}.json'), 'Returned matrix differs')
        require(check['execution_status'] == 'returned' and check['overall_status'] == diagnostic['status'] == 'WARN', 'Direct diagnostic status changed')
        require(all(check['strict_flags'].values()) and check['state_unchanged_by_method'] is True, 'Strict direct reconciliation failed')
        require(matrix['shape'] == scoped['shape'] == [94, 3] and matrix['columns'] == [94, 93, 1] and scoped['columns'] == ['all', 'inner', 'PP'], 'Matrix scope or axes differ')
        require(matrix['index'] == scoped['index'] and set(matrix['index']) == set(names), 'Matrix recipient identities differ')
        require(sha(RAW / f'outputs/{option}_state_before.json.gz') == sha(RAW / f'outputs/{option}_state_after.json.gz') == sha(RAW / 'outputs/effective_state.json.gz'), 'Retained runtime changed around a method')
        for frame in full['items'][1:] + [scoped]:
            require(len(frame['data']) == frame['shape'][0] and len(frame['columns']) == frame['shape'][1], 'Matrix dimensions differ')
            require(all(len(row) == frame['shape'][1] for row in frame['data']), 'Matrix row dimensions differ')
            require(all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for row in frame['data'] for v in row), 'Nonfinite returned matrix')
            require(not any(any(row) for mask in frame['masks'].values() for row in mask), 'Unexpected missing or nonfinite mask')
        require(all(v >= 0 for row in matrix['data'] for v in row), 'Negative source coefficients')
        require(read(RAW / f'outputs/{option}_negative_source_group_pairs.json') == [], 'Negative source evidence changed')
        require([r['id'] for r in metadata['methods'][option]['SPPR']['rows']] == matrix['index'], 'Matrix metadata row order differs')
        scopes[key] = {scope: {} for scope in scoped['columns']}
        for gid, values, retained in zip(matrix['index'], matrix['data'], scoped['data']):
            for position, scope in enumerate(scoped['columns']):
                expected = (math.fsum(values), math.fsum(values[1:]), values[2])[position]
                require(_near(expected, retained[position]), 'Scope reduction does not reconcile')
                scopes[key][scope][names[gid]] = retained[position]
        catch = {int(r['group_seq']): float(r['catch']) for r in groups}
        for scope, label in [('all', 'ppr_all'), ('inner', 'ppr_inner'), ('PP', 'ppr_pp_only')]:
            value = math.fsum(scopes[key][scope][name] * catch[gid] for gid, name in names.items())
            require(_near(value, diagnostic['footprint'][label]), 'Retained direct footprint does not reconcile')
        diagnostics[key] = diagnostic
        audit[key] = {'status': 'WARN', 'shape': matrix['shape'], 'strict_flags': check['strict_flags'], 'finite_nonnegative_coefficients': 282, 'rho_living': check['rho_living'], 'b': check['b'], 'state_unchanged': True}
    flags = {'constructor': copy.deepcopy(identity['constructor']), 'diagnostics': {**identity['method_options'], 'thresholds': identity['diagnostic_thresholds']}, 'methods': {}, 'mc': {},
             'runtime_initialization': {'reexecution_supported': False, 'recipe': 'Archived ModelData metadata-alias parsing, accepted author-equation input, default GS and single-detritus initialization, diet_import bookkeeping, then pinned EE floor applied to the completed audited runtime.',
                 'floor_configuration': identity['floor_configuration'], 'execution_identity': relative(RAW / 'inventory/execution_identity.json', MODEL), 'effective_state': relative(RAW / 'outputs/effective_state.json.gz', MODEL), 'effective_state_sha256': sha(RAW / 'outputs/effective_state.json.gz'), 'current_engine_equivalence': False},
             'engine_sources': {name: relative(path, MODEL) for name, path in engines.items()}, 'engine_source_hashes': hashes,
             'configuration_evidence': [{'relative_path': relative(path, MODEL), 'sha256': sha(path), 'original_source_hash': CANONICAL_SHA} for path in [RAW / 'inventory/execution_identity.json', RAW / 'outputs/effective_state.json.gz', *engines.values()]]}
    # Constructor was called before floor application; do not invent floor kwargs
    # on that constructor. The actual floor call is bound above to saved evidence.
    return flags, files, scopes, diagnostics, names, audit


def _flat(diagnostic):
    result = {}
    def visit(value, prefix=''):
        if isinstance(value, dict):
            for key, item in value.items(): visit(item, prefix + '_' + key if prefix else key)
        elif isinstance(value, list): result[prefix] = json.dumps(value, ensure_ascii=False, allow_nan=False)
        else: result[prefix] = value
    visit(diagnostic)
    result['TE_option'] = diagnostic['config']['TE_option']
    return result


def _exact_source_numbers(path, book):
    """Serialize source coefficients with round-tripping float representations."""
    from tools.project_core.validation.researcher_review import sheet_xml, S
    from tools.project_core.workbooks.workbooks import records
    from openpyxl.utils import get_column_letter
    import openpyxl
    wanted = {(r['scope'], r['group'], r['method']): r['sppr'] for r in records(book, 'Selected model groups', 'Group SPPR')}
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False); cells = {}
    try:
        for scope in ('all', 'inner', 'PP'):
            sheet = wb['sppr_' + scope]; data = list(sheet.values); header = data[0]; gc = header.index('group_name')
            cells[sheet.title] = {get_column_letter(j) + str(i): wanted[scope, row[gc], method]
                for i, row in enumerate(data[1:], 2) for j, method in enumerate(header, 1)
                if (scope, row[gc], method) in wanted and wanted[scope, row[gc], method] is not None}
    finally: wb.close()
    with zipfile.ZipFile(path) as archive:
        replaced = {}
        for name, numbers in cells.items():
            member, sheet = sheet_xml(archive, name); found = set()
            for cell in sheet.iter(f'{{{S}}}c'):
                address = cell.get('r')
                if address not in numbers: continue
                node = cell.find(f'{{{S}}}v')
                require(node is not None and cell.find(f'{{{S}}}f') is None and _near(float(node.text), numbers[address]), 'Source serialization differs')
                node.text = repr(numbers[address]); found.add(address)
            require(found == set(numbers), 'Source coefficient cells missing')
            replaced[member] = ET.tostring(sheet, encoding='utf-8')
        members = [(item, replaced.get(item.filename, archive.read(item.filename))) for item in archive.infolist()]
    with zipfile.ZipFile(path, 'w') as archive:
        for item, data in members: archive.writestr(item, data)


def _guard(flags):
    from tools.scientific_helpers.sppr.method_coverage import _require_supported_runtime_initialization
    try: _require_supported_runtime_initialization(flags)
    except ValueError as error:
        require('Stock reconstruction of this scenario is not supported' in str(error), 'Unexpected runtime guard')
    else: raise ValueError('Custom runtime must fail closed before stock reconstruction')


def prepare(package_path=None, *, progress=print):
    from tools.project_core.calculations import coverage
    from tools.project_core.calculations.regional import set_setting
    from tools.project_core.calculations.snapshots import dependencies
    from tools.project_core.workbooks.workbooks import read_book, records, rows, overview, digest_tables
    package = Path(package_path or DEFAULT_PACKAGE).resolve()
    require(package.is_relative_to(RUN), 'Preparation must stay in this model-local run')
    require(not (package / 'preparation.json').exists(), 'Prepared package already exists; use verify')
    flags, files, scopes, diagnostics, names, direct_audit = authenticate(); _guard(flags)
    require(sha(REGION) == REGIONAL_SHA, 'Regional pre-adoption baseline changed')
    original = read_book(REGION); book = copy.deepcopy(original)
    require({int(r['group_seq']): r['group_name'] for r in records(book, 'Selected model groups', 'Groups')} == names, 'Regional/source group identities differ')
    require(overview(book)['selected_model_id'] == overview(book)['results_model_id'] == MODEL.name, 'Selected/results identity differs')
    keys = list(dict.fromkeys(r['method'] for r in records(book, 'Selected model groups', 'Group SPPR')))
    require(set(METHODS) <= set(keys), 'Prior approved method slots missing')
    files.update([REGION, MODEL / 'model.json', MODEL / 'sppr_source.xlsx', MODEL / 'results/regional_snapshot.xlsx', MODEL / 'results/result_manifest.json'])
    files.update(ROOT / 'tools/project_core' / name for name in coverage._arithmetic_identity())
    files.update([ROOT / 'tools/scientific_helpers/sppr/configuration.py', ROOT / 'tools/scientific_helpers/sppr/method_coverage.py', ROOT / 'tools/project_core/calculations/snapshots.py'])
    consumed = {relative(path): fingerprint(path) for path in files}
    stage_model = package / 'model'; stage_region = package / 'regional/LME_003.xlsx'
    stage_region.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(REGION, stage_region)
    recovery = stage_model / 'results/diagnostics' / PREFIX / 'pre_adoption'; recovery.mkdir(parents=True, exist_ok=True)
    archive = []
    for label, path in [('regional.xlsx', REGION), ('sppr_source.xlsx', MODEL / 'sppr_source.xlsx'), ('regional_snapshot.xlsx', MODEL / 'results/regional_snapshot.xlsx'), ('result_manifest.json', MODEL / 'results/result_manifest.json')]:
        item = {'original': relative(path), 'sha256': fingerprint(path), 'availability': 'present' if path.is_file() else 'absent'}
        if path.is_file():
            target = recovery / label; shutil.copyfile(path, target); item['archive'] = relative(target, stage_model)
        archive.append(item)
    write(recovery / 'inventory.json', {'schema_version': 1, 'role': 'Byte-preserved pre-adoption package; historical execution identity remains unknown as recorded in its original manifest.', 'artifacts': archive, 'methods': keys, 'includes_all_old_method_coefficients_arithmetic_diagnostics': True})
    outcomes = {}
    for key in keys:
        if key in METHODS:
            option = METHODS[key]
            outcomes[key] = {'status': 'reused', 'reason': 'Authenticated retained approved GE/TE direct result; no scientific execution during adoption.', 'scopes': scopes[key], 'annual_status': {s: 'WARN' for s in ('all', 'inner', 'PP')}, 'diagnostics': diagnostics[key], 'retained_diagnostics_flat': _flat(diagnostics[key]),
                'evidence': {'path': f'ee_floor_review_20261114/outputs/{option}_full_return.json.gz', 'sha256': sha(RAW / f'outputs/{option}_full_return.json.gz'), 'availability': 'present'}}
        else:
            evidence = stage_model / 'results/diagnostics' / PREFIX / (key + '.json')
            write(evidence, {'method': key, 'status': 'NOT_RUN', 'reason': UNAVAILABLE, 'historical_package': 'pre_adoption/inventory.json', 'scientific_execution_performed': False})
            outcomes[key] = {'status': 'NOT_RUN', 'reason': UNAVAILABLE, 'scopes': {s: {} for s in ('all', 'inner', 'PP')}, 'annual_status': {s: 'unavailable: NOT_RUN' for s in ('all', 'inner', 'PP')}, 'evidence': {'path': relative(evidence, stage_model / 'results/diagnostics'), 'sha256': sha(evidence), 'availability': 'present'}}
    # Existing human restrictions remain restrictions for the replacement returns.
    old_status = {(r[1], r[2]): r[6] for r in rows(original, 'PPR', 'Annual') if r[3:6] == ['landings', 'method', 'ppr']}
    for key in METHODS:
        for scope in ('all', 'inner', 'PP'):
            prior = old_status.get((scope, key), '')
            if str(prior).startswith('provisional:'): outcomes[key]['annual_status'][scope] = prior + '; retained EE-floor ON 0.1 direct diagnosis: WARN'
    coverage._apply_outcomes(book, MODEL.name, outcomes, keys)
    # The extension helper retains numerically equivalent old cells. This
    # adoption promises exact pinned floats, including the final digit.
    for row in rows(book, 'Selected model groups', 'Group SPPR'):
        if row[3] in METHODS: row[4] = scopes[row[3]][row[2]][row[1]]
    # Existing numeric allocation-impact cells are historical evidence. Preserve
    # them exactly and attach an explicit scope record rather than reinterpreting.
    book['Diagnostics']['Retained adoption provenance'] = (['item', 'value'], [
        ['active_runtime', 'Approved retained EE-floor ON 0.1; GE WARN and TE WARN; With Egestion unavailable.'],
        ['historical_tables', 'Size allocation impact and prior run_notes are pre-floor historical supporting evidence; preserved unchanged and not current-runtime results.'],
        ['historical_package', 'results/diagnostics/' + PREFIX + '/pre_adoption/inventory.json'],
        ['display_exclusions', '31 group exclusions are display/review metadata only; all 94 ecological groups and coefficients remain.'],
        ['scientific_execution_performed', False]])
    progress('Rebuilding only dependent regional arithmetic from exact retained coefficients', flush=True)
    coverage._arithmetic(book, REGION, MODEL / 'model.json', flags, original, invalidated_methods=keys)
    set_setting(book, 'production_eligible', False)
    set_setting(book, 'calculation_status', 'provisional: retained EE-floor ON 0.1 GE/TE WARN; prior mapping restrictions retained; other-runtime methods unavailable')
    # Current arithmetic hashes certify only arithmetic performed here, not the
    # historical scientific execution or equivalence to the current engine.
    saved = coverage._save_calculation(stage_region, book, MODEL / 'model.json', flags, copy.deepcopy(book), invalidated_methods=keys)
    source_book = copy.deepcopy(saved)
    header, values = source_book['Selected model groups']['Groups']
    source_book['Selected model groups']['Groups'] = (['seq' if h == 'group_seq' else h for h in header], values)
    source = stage_model / 'sppr_source.xlsx'; source.parent.mkdir(parents=True, exist_ok=True)
    coverage._update_source(source, source_book, outcomes, replace_methods=keys)
    _exact_source_numbers(source, saved)
    set_setting(saved, 'results_source_sha256', sha(source))
    saved = coverage._save_calculation(stage_region, saved, MODEL / 'model.json', flags, copy.deepcopy(saved), invalidated_methods=keys)
    snapshot = stage_model / 'results/regional_snapshot.xlsx'; shutil.copyfile(stage_region, snapshot)
    row_hashes = coverage._method_rows(saved)[1]
    for key in keys: outcomes[key]['group_rows_sha256'] = row_hashes[key]
    context = {'model_sha256': CANONICAL_SHA, 'flags': flags, 'code_identity': flags['engine_source_hashes'], 'dependencies': read(RAW / 'inventory/execution_identity.json')['environment']['packages'], 'execution_context_role': 'Actual historical diagnostic execution, not current-engine equivalence'}
    manifest = {'schema_version': 1, 'unit_id': UNIT, 'model_id': MODEL.name, 'snapshot_selected_model_id': MODEL.name, 'timestamp': datetime.now(timezone.utc).isoformat(), 'canonical_model_sha256': CANONICAL_SHA, 'present_canonical_model_sha256': CANONICAL_SHA, 'snapshot_sha256': sha(snapshot), 'coefficient_source_sha256': sha(source), 'effective_flags': flags, 'code_identity': flags['engine_source_hashes'], 'provenance_status': 'Authenticated approved retained GE/TE diagnostics adopted; partial inventory only; all prior other-runtime methods unavailable. No new scientific execution or historical provenance invention.', 'dependencies': dependencies(saved), 'artifacts': {'snapshot': 'regional_snapshot.xlsx', 'model': '../model.json', 'coefficients': '../sppr_source.xlsx'}, 'historical_package_backup': archive,
        'retained_reuse': {'raw_evidence_index': relative(RAW / 'inventory/evidence_index.json', MODEL), 'raw_evidence_index_sha256': INDEX_SHA, 'signed_report_sha256': DOCX_SHA, 'proposal_sha256': PROPOSAL_SHA, 'scientific_solve_performed': False, 'current_engine_equivalence': False},
        'method_coverage': {'schema_version': 1, 'inventory_scope': 'approved direct GE/TE only; not a full canonical inventory', 'expected_methods': list(METHODS), 'context': context, 'methods': outcomes, 'arithmetic_code_identity': coverage._arithmetic_identity(), 'protected_inputs_sha256': coverage._preserved_inputs(original)}}
    write(stage_model / 'results/result_manifest.json', manifest)
    promotions = [{'source': relative(stage_region, package), 'target': relative(REGION), 'sha256': sha(stage_region)}]
    for path in sorted(p for p in stage_model.rglob('*') if p.is_file()):
        target = MODEL / path.relative_to(stage_model)
        promotions.append({'source': relative(path, package), 'target': relative(target), 'sha256': sha(path)})
        consumed.setdefault(relative(target), fingerprint(target))
    plan = {'schema_version': 1, 'prepared_utc': datetime.now(timezone.utc).isoformat(), 'package': relative(package), 'unit_id': UNIT, 'model_id': MODEL.name, 'promotions': promotions, 'consumed_inputs': consumed, 'expected_methods': list(METHODS), 'unavailable_methods': [key for key in keys if key not in METHODS], 'context': context, 'protected_inputs_sha256': coverage._preserved_inputs(original), 'old_overview': overview(original), 'direct_reconciliation': direct_audit, 'scientific_solve_performed': False, 'adoption_performed': False}
    _check_inputs(consumed); write(package / 'preparation.json', plan)
    verify_package(package)
    return plan


def verify_package(package_path=None, *, check_inputs=True):
    from tools.project_core.calculations import coverage
    from tools.project_core.calculations.regional import result_hash
    from tools.project_core.workbooks.workbooks import read_book, overview, records, rows, input_hash, digest_tables, finite
    package = Path(package_path or DEFAULT_PACKAGE).resolve(); plan = read(package / 'preparation.json')
    if check_inputs: _check_inputs(plan['consumed_inputs'])
    flags, _, scopes, diagnostics, names, audit = authenticate(); _guard(flags)
    require(flags == plan['context']['flags'], 'Staged flags differ from authenticated execution')
    for item in plan['promotions']:
        source = (package / item['source']).resolve(); target = (ROOT / item['target']).resolve()
        require(source.is_relative_to(package) and target.is_relative_to(ROOT) and sha(source) == item['sha256'], 'Prepared promotion changed')
        require(target == REGION or target.is_relative_to(MODEL), 'Promotion is outside bounded model scope')
    book = read_book(package / 'regional/LME_003.xlsx'); model = package / 'model'; manifest = read(model / 'results/result_manifest.json')
    original = read_book(model / 'results/diagnostics' / PREFIX / 'pre_adoption/regional.xlsx')
    require(sha(model / 'results/diagnostics' / PREFIX / 'pre_adoption/regional.xlsx') == REGIONAL_SHA, 'Historical regional copy differs')
    require(coverage._preserved_inputs(book) == plan['protected_inputs_sha256'], 'Protected scientific inputs changed')
    require(digest_tables(book['Classic PPR']) == digest_tables(original['Classic PPR']), 'Independent Classic PPR changed')
    for key in ('selection_rationale', 'selected_model_id', 'source_note', 'model_path'):
        require(overview(book).get(key) == plan['old_overview'].get(key), 'Manual setting changed: ' + key)
    require(overview(book)['calculation_input_sha256'] == input_hash(book) and overview(book)['calculation_result_sha256'] == result_hash(book), 'Staged calculation hashes are stale')
    require(sha(model / 'results/regional_snapshot.xlsx') == sha(package / 'regional/LME_003.xlsx') == manifest['snapshot_sha256'], 'Snapshot is not complete regional bytes')
    require(sha(model / 'sppr_source.xlsx') == manifest['coefficient_source_sha256'] == overview(book)['results_source_sha256'], 'Source identity differs')
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    require(resolve_audited_configuration(MODEL, book, manifest) == flags, 'Configuration resolver changed authenticated flags')
    require(coverage._source_matches(model, book, list(manifest['method_coverage']['methods'])), 'Source workbook coefficients differ')
    actual = {(r['method'], r['scope'], r['group']): r['sppr'] for r in records(book, 'Selected model groups', 'Group SPPR')}
    for key, values in scopes.items():
        for scope, groups in values.items():
            for name, value in groups.items(): require(actual[key, scope, name] == value, 'Retained coefficient changed during serialization')
    unavailable = set(plan['unavailable_methods'])
    require(all(value is None for (method, _, _), value in actual.items() if method in unavailable), 'Old-runtime coefficients remain current')
    for sheet, table in [('PPR', 'Annual'), ('PPR', 'Taxon SPPR'), ('PPR', 'Taxon PPR inspected year'), ('PPR–NPP', 'Ratios')]:
        for row in records(book, sheet, table):
            if row.get('method') not in unavailable: continue
            # Catch and coverage denominators do not imply available SPPR.
            if table == 'Annual' and row.get('metric') in {'catch', 'covered_catch'}: continue
            values = [v for k, v in row.items() if isinstance(k, int) and 1950 <= k <= 2019 or k in {'sppr', 'ppr', 'ppr_tC', 'ppr_wet_tonnes'}]
            require(not any(finite(v) for v in values), 'Unavailable old method was reaggregated: ' + table)
            if table == 'Annual': require(str(row['status']).startswith('unavailable:'), 'Unavailable annual status lost')
    health = {r.get('TE_option') or r.get('config_TE_option'): r for r in records(book, 'Diagnostics', 'model_health')}
    require(health['GE']['status'] == health['TE']['status'] == 'WARN' and health['With Egestion']['status'] == 'NOT_RUN', 'Diagnostic statuses changed')
    for name, table in original.get('Diagnostics', {}).items():
        if name not in {'model_health', 'Method coverage', 'mc_diagnostics'}:
            require(digest_tables(book['Diagnostics'][name]) == digest_tables(table), 'Manual/historical diagnostic table changed: ' + name)
    for item in manifest['historical_package_backup']:
        if item['availability'] == 'present': require(sha(model / item['archive']) == item['sha256'], 'Historical archive changed')
    changed_tables = {('Overview', 'Settings'), ('Selected model groups', 'Group SPPR'),
        ('PPR', 'Annual'), ('PPR', 'Taxon SPPR'), ('PPR', 'Taxon PPR inspected year'),
        ('PPR–NPP', 'Ratios'), ('Diagnostics', 'model_health')}
    preserved_cells = 0
    for sheet, tables in original.items():
        for name, table in tables.items():
            if (sheet, name) in changed_tables: continue
            require(book[sheet][name] == table, 'Protected table cells differ: ' + sheet + '/' + name)
            preserved_cells += sum(len(row) for row in table[1])
    import openpyxl
    source_book = openpyxl.load_workbook(model / 'sppr_source.xlsx', read_only=True, data_only=False)
    try:
        for scope in ('all', 'inner', 'PP'):
            source_rows = list(source_book['sppr_' + scope].values); header = source_rows[0]
            for row in source_rows[1:]:
                name = row[header.index('group_name')]
                for key in METHODS: require(row[header.index(key)] == scopes[key][scope][name], 'Source coefficient is not the exact retained float')
    finally: source_book.close()
    changed = {key: sum(a[4] != b[4] for a, b in zip([r for r in rows(original, 'Selected model groups', 'Group SPPR') if r[3] == key], [r for r in rows(book, 'Selected model groups', 'Group SPPR') if r[3] == key])) for key in METHODS}
    qa = {'passed': True, 'approved_method_coefficients_exact': 564, 'ecological_groups_retained': len(names), 'cleared_other_runtime_coefficients': sum(method in unavailable for method, _, _ in actual), 'changed_scope_cells': changed, 'diagnostic_status': {'GE': 'WARN', 'TE': 'WARN', 'With Egestion': 'NOT_RUN'}, 'protected_inputs_exact': True, 'classic_all_tables_exact': True, 'manual_and_historical_diagnostic_tables_exact': True, 'all_old_runtime_results_archived': True, 'source_and_snapshot_verified': True, 'partial_inventory_only': True, 'scientific_solve_performed': False, 'adoption_performed': False, 'runtime_reexecution_supported': False, 'fail_closed_guard_installed': True, 'ready_for_apply': True, 'staged_regional_sha256': sha(package / 'regional/LME_003.xlsx'), 'direct_reconciliation': audit}
    qa['protected_table_cells_exact'] = preserved_cells
    write(RUN / 'qa/package_verification.json', qa)
    return plan


def apply(publication, package_path=None):
    from tools.project_core.registry.publication import _ACTIVE, publication_write
    from tools.project_core.calculations import coverage
    require(publication in _ACTIVE.get() and publication.root == ROOT, 'Active publication transaction required')
    lock = ROOT / '.project-write.lock'
    require(lock.is_file() and lock.read_text().strip() == str(os.getpid()), 'Project writer lock required')
    package = Path(package_path or DEFAULT_PACKAGE).resolve(); plan = verify_package(package, check_inputs=False)
    targets = {p['target'] for p in plan['promotions']}
    _check_inputs({k: v for k, v in plan['consumed_inputs'].items() if k not in targets})
    if all(fingerprint(ROOT / p['target']) == p['sha256'] for p in plan['promotions']):
        return {'status': 'already_applied', 'changed_units': [UNIT], 'written_paths': [], 'written_hashes': {}}
    _check_inputs(plan['consumed_inputs'])
    for item in plan['promotions']:
        source, target = package / item['source'], ROOT / item['target']
        with publication_write(target, fingerprint=item['sha256']):
            coverage._write_bytes(target, source.read_bytes(), expected_sha256=plan['consumed_inputs'][item['target']])
    require(all(fingerprint(ROOT / p['target']) == p['sha256'] for p in plan['promotions']), 'Installed package differs')
    return {'status': 'applied', 'changed_units': [UNIT], 'written_paths': [str(ROOT / p['target']) for p in plan['promotions']], 'written_hashes': {str(ROOT / p['target']): p['sha256'] for p in plan['promotions']}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('command', choices=['prepare', 'verify']); parser.add_argument('--package', type=Path)
    args = parser.parse_args(); plan = prepare(args.package) if args.command == 'prepare' else verify_package(args.package)
    print(json.dumps({'package': plan['package'], 'promotions': len(plan['promotions']), 'scientific_solve_performed': False, 'adoption_performed': False}), flush=True)
