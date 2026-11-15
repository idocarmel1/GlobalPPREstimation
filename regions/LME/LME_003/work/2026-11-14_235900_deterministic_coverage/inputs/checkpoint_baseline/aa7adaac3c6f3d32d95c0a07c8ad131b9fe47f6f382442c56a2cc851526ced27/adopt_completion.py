"""Verify cached deterministic results; adopt/publish only with explicit --apply.

No engine calculation is called. The default command performs read-only preflight.
All cache/model/retained-row checks complete before the first publication write.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path, PureWindowsPath
import sys

ROOT = next(path for path in Path(__file__).resolve().parents if (path/'Project.xlsx').is_file())
WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RUN_ID = 'deterministic_completion_20261114'
ADAPTER_CAVEAT = ('The literal recorded adapter_sha256 identifies the adapter file at invocation. '
    'Earlier concurrent edits mean it may differ from the already-loaded adapter revision; '
    'it is not attested as an import-time execution digest. Computational engine and runtime '
    'evidence hashes are independently verified. No recorded hash has been corrected or replaced.')

from tools.project_core.calculations import coverage
from tools.project_core.workbooks.workbooks import read_book, records, rows, overview, finite, digest_tables
from tools.scientific_helpers.sppr import method_coverage as adapter


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def check_hashes(expected):
    for path, fingerprint in expected.items():
        if not path.is_file() or sha(path) != fingerprint:
            raise ValueError('Consumed evidence changed or hash mismatch: ' + str(path))


def reference(root, ref):
    name = ref.get('path', ref.get('relative_path'))
    if not isinstance(name, str) or Path(name).is_absolute() or PureWindowsPath(name).anchor:
        raise ValueError('Evidence reference must be relative')
    path = (Path(root)/name).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('Evidence reference escaped its owned directory')
    check_hashes({path: ref.get('sha256')})
    return path


def authenticate_identity(identity, model):
    """Authenticate exact model/runtime/engine bytes without constructing a model."""
    from tools.scientific_helpers.sppr.configuration import _validate_evidence
    from tools.scientific_helpers.sppr.audited_runtime import validate_replay
    model = Path(model).resolve()
    if identity.get('model_id') != model.parent.name or identity.get('model_sha256') != sha(model):
        raise ValueError('Cached execution model identity differs')
    flags = identity.get('flags')
    _validate_evidence(model.parent, flags, sha(model))
    replay = validate_replay(flags, model)
    if replay is None:
        raise ValueError('Cached execution has no authenticated replay descriptor')
    if adapter.engine_identity(flags, model) != identity.get('engine_hashes'):
        raise ValueError('Cached computational engine hashes differ from retained source bytes')
    paths = {model: sha(model)}
    for ref in [*flags.get('configuration_evidence', []), replay['provenance'],
                *[replay[key] for key in ('runtime', 'symbolic_repair', 'ew_e_optimized') if key in replay]]:
        path = reference(model.parent, ref)
        paths[path] = ref['sha256']
    for path in adapter._engine_paths(flags, model).values():
        paths[path.resolve()] = sha(path)
    for path in (adapter._calculation_engine_path(flags, model), adapter._derivative_engine_path(flags, model)):
        if path is not None:
            paths[path.resolve()] = sha(path)
    return paths


def verify_method(model, cache_dir, key, outcome):
    from provenance_admission import verify_initialization
    if key.startswith('MC_'):
        raise ValueError('Monte Carlo adoption is outside this request')
    method_path = reference(cache_dir, outcome['evidence'])
    constructor_path = reference(cache_dir, outcome['constructor_evidence'])
    document, constructor = read(method_path), read(constructor_path)
    identity = document['identity']
    if identity != outcome.get('execution_identity') or constructor.get('identity') != identity:
        raise ValueError('Cached method/constructor execution identity differs')
    initialization = verify_initialization(model, cache_dir, key, outcome, document)
    if document.get('settings', {}).get('method') != key:
        raise ValueError('Cached method identity differs from its requested key')
    for field, value in outcome.items():
        if field in ('evidence', 'constructor_evidence', 'execution_identity',
                     'runtime_verification_evidence', 'initialization_provenance_caveat'):
            continue
        if field not in document or adapter.encode_lossless(value) != document[field]:
            raise ValueError('Cached summary differs from immutable return at ' + key + '/' + field)
    if outcome.get('status') not in {'ok', 'failed', 'timeout', 'crashed', 'unavailable', 'NOT_RUN'}:
        raise ValueError('Cached method has no terminal execution outcome: ' + key)
    if outcome['status'] != 'ok' and not outcome.get('reason'):
        raise ValueError('Unavailable cached method has no recorded reason: ' + key)
    consumed = authenticate_identity(identity, Path(model))
    consumed.update({method_path: outcome['evidence']['sha256'], constructor_path: outcome['constructor_evidence']['sha256']})
    consumed.update(initialization['consumed'])
    return {'identity': copy.deepcopy(identity), 'outcome': copy.deepcopy(outcome),
            'method_path': method_path, 'constructor_path': constructor_path,
            'initialization': initialization, 'consumed': consumed}


class CachedBatch:
    """Compute-shaped callback that only copies authenticated completed returns."""
    def __init__(self, model, cache_path, verified):
        self.model = Path(model).resolve()
        self.cache_path = Path(cache_path).resolve()
        self.verified = verified
        self.identity = copy.deepcopy(next(iter(verified.values()))['identity'])
        self.constructor = next(iter(verified.values()))['constructor_path']
        self.initialization = next(iter(verified.values()))['initialization']
        if any(record['identity'] != self.identity or record['constructor_path'] != self.constructor
               or record['initialization']['path'] != self.initialization['path']
               for record in verified.values()):
            raise ValueError('Mixed execution identities or constructors require separate adoption batches')
        self.consumed = {self.cache_path: sha(self.cache_path)}
        for record in verified.values():
            self.consumed.update(record['consumed'])

    def __call__(self, model, flags, keys, directory, *, progress):
        keys = list(keys)
        if (Path(model).resolve() != self.model or flags != self.identity['flags']
                or any(key not in self.verified or key.startswith('MC_') for key in keys)):
            raise ValueError('Cached adoption differs from requested methods/model/execution flags')
        check_hashes(self.consumed)
        # Complete all validations before creating even a staged output file.
        for key in keys:
            again = verify_method(self.model, self.cache_path.parent, key, self.verified[key]['outcome'])
            if again['identity'] != self.identity:
                raise ValueError('Cached identity changed before adoption')
        directory = Path(directory)
        constructor_name = 'constructor-' + sha(self.constructor)[:16] + '.json.gz'
        (directory/constructor_name).write_bytes(self.constructor.read_bytes())
        constructor_ref = {'path': constructor_name, 'sha256': sha(self.constructor), 'availability': 'present'}
        verification_ref = None
        if self.initialization['evidence_kind'] == 'retrospective_runtime_authentication':
            verification = self.initialization['path']
            name = 'runtime-verification-' + sha(verification)[:16] + '.json.gz'
            (directory/name).write_bytes(verification.read_bytes())
            verification_ref = {'path': name, 'sha256': sha(verification), 'availability': 'present',
                                'evidence_kind': 'retrospective_runtime_authentication'}
        outcomes = {}
        for key in keys:
            record = self.verified[key]
            name = key + '.json.gz'
            (directory/name).write_bytes(record['method_path'].read_bytes())
            outcome = copy.deepcopy(record['outcome'])
            outcome['evidence'] = {'path': name, 'sha256': sha(record['method_path']), 'availability': 'present'}
            outcome['constructor_evidence'] = copy.deepcopy(constructor_ref)
            if verification_ref:
                outcome['runtime_verification_evidence'] = copy.deepcopy(verification_ref)
                outcome['initialization_provenance_caveat'] = self.initialization['limitation']
            outcome['cached_execution_source'] = {'path': record['method_path'].relative_to(self.model.parent).as_posix(),
                                                 'sha256': sha(record['method_path'])}
            outcome['adapter_identity_caveat'] = ADAPTER_CAVEAT
            outcomes[key] = outcome
        index = {'schema_version': 1, 'evidence_kind': 'authenticated_cached_adoption',
                 'scientific_execution_performed': False, 'execution_identity': self.identity,
                 'adapter_identity_caveat': ADAPTER_CAVEAT,
                 'cache': {'path': self.cache_path.relative_to(self.model.parent).as_posix(), 'sha256': sha(self.cache_path)},
                 'constructor_evidence': constructor_ref,
                 'methods': {key: {'evidence': value['evidence'], 'execution_identity': value['execution_identity']}
                             for key, value in outcomes.items()}}
        index_path = directory/'cached_adoption.json.gz'
        index_path.write_bytes(gzip.compress(json.dumps(index, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8'), mtime=0))
        check_hashes(self.consumed)
        result = {'methods': outcomes, 'constructor_evidence': constructor_ref,
                  'evidence_index': {'path': index_path.name, 'sha256': sha(index_path), 'availability': 'present'}}
        if verification_ref:
            result['runtime_verification_evidence'] = verification_ref
        return result


def protected_book(book, retained=None):
    by_method = coverage._method_rows(book)[0]
    if retained is None:
        retained = {key for key, values in by_method.items() if key.startswith('MC_') or any(finite(row[4]) for row in values)}
    result = {'retained_methods': sorted(retained),
        'selection': {key: value for key, value in overview(book).items()
                      if key in ('selected_model_id', 'selection_rationale', 'model_path') or 'exclu' in key.lower()},
        'independent': {sheet: book.get(sheet, {}) for sheet in ('Catch', 'Classic PPR', 'NPP')},
        'inputs': {(sheet + '/' + table): book.get(sheet, {}).get(table) for sheet, table in (
            ('Selected model groups', 'Groups'), ('PPR', 'Matching'), ('PPR', 'Allocation assumptions'), ('PPR', 'Mapping review'))},
        'coefficients': {key: by_method.get(key) for key in sorted(retained)}, 'dependent': {}, 'diagnostics': {}}
    for sheet, table in [('PPR', 'Annual'), ('PPR', 'Taxon SPPR'), ('PPR', 'Taxon PPR inspected year'), ('PPR–NPP', 'Ratios')]:
        selected = [row for row in records(book, sheet, table) if row.get('method') in retained]
        result['dependent'][sheet + '/' + table] = selected
    options = {key: value for key, value in {'new_GE': 'GE', 'new_TE_EEfix': 'TE', 'new_WithEgestion': 'With Egestion'}.items() if key in retained}
    for name, table in book.get('Diagnostics', {}).items():
        if name == 'Method coverage':
            continue
        if name == 'model_health':
            result['diagnostics'][name] = [row for row in records(book, 'Diagnostics', name)
                if (row.get('TE_option') or row.get('config_TE_option') or row.get('method')) in options.values()]
        else:
            result['diagnostics'][name] = table
    return copy.deepcopy(result)


def source_state(path, retained):
    import openpyxl
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
    result = {}
    try:
        for name in workbook.sheetnames:
            values = list(workbook[name].values)
            if not values:
                continue
            header, body = values[0], values[1:]
            if name.startswith('sppr_'):
                columns = [i for i, key in enumerate(header) if key in retained or key in ('seq', 'group_name')]
                result[name] = [[row[i] if i < len(row) else None for i in columns] for row in values]
            elif name == 'model_health':
                options = {value for key, value in {'new_GE': 'GE', 'new_TE_EEfix': 'TE', 'new_WithEgestion': 'With Egestion'}.items() if key in retained}
                result[name] = [dict(zip(header, row)) for row in body if any(
                    dict(zip(header, row)).get(key) in options for key in ('TE_option', 'config_TE_option', 'method'))]
            elif name not in ('method_coverage', 'run_notes'):
                result[name] = values
    finally:
        workbook.close()
    return result


def unchanged_projection(before, after, label):
    """Compare every previously stored field and row exactly."""
    if isinstance(before, dict) and isinstance(after, dict):
        if any(key not in after for key in before):
            raise ValueError('Protected keys disappeared: ' + label)
        for key in before:
            unchanged_projection(before[key], after[key], label + '/' + str(key))
    elif isinstance(before, (list, tuple)) and isinstance(after, (list, tuple)):
        if len(before) != len(after):
            raise ValueError('Protected row count changed: ' + label)
        for index, (old, new) in enumerate(zip(before, after)):
            unchanged_projection(old, new, label + '/' + str(index))
    elif type(before) is bool or type(after) is bool:
        if type(before) is not type(after) or before != after:
            raise ValueError('Protected boolean changed: ' + label)
    elif before != after:
        raise ValueError('Protected value changed: ' + label)


def central_state():
    book = read_book(ROOT/'Project.xlsx')
    return {sheet: [{key: value for key, value in row.items() if key != 'atlas_region_rank'}
                    for row in records(book, sheet, table)]
            for sheet, table in (('Models & coverage', 'Models'), ('Papers', 'Papers'))}


def check_control_settings(control, executed, model):
    """Compare scientific settings, authenticating metadata-only equivalences.

    Return separate pre-write and immutable guards for consumed dependencies.
    The saved control and execution flags are never changed.
    """
    coverage._execution_flags(control, executed)
    model = Path(model).resolve()
    consumed = {model: sha(model)}
    immutable = dict(consumed)
    live_manifest = (model.parent / 'results/result_manifest.json').resolve()

    def authenticate(ref, *, original_provenance=False):
        path = reference(model.parent, ref)
        consumed[path] = ref['sha256']
        # The original control may point at the live manifest that adoption
        # replaces. Its bytes remain guarded before any write. Every archive
        # and every dependency authenticated in another role stays immutable.
        if not (original_provenance and path == live_manifest):
            immutable[path] = ref['sha256']

    original_proof=control.get('audited_replay',{}).get('provenance',{})
    executed_proof=executed.get('audited_replay',{}).get('provenance',{})
    relocated_proof=bool(original_proof.get('sha256') and
                         original_proof.get('sha256')==executed_proof.get('sha256'))
    if relocated_proof and original_proof.get('relative_path') != executed_proof.get('relative_path'):
        authenticate(original_proof, original_provenance=True)
        authenticate(executed_proof)
    def scientific(flags):
        flags = copy.deepcopy(flags)
        for key in ('method_timeout_seconds', 'method_timeout_overrides_seconds'):
            flags.pop(key, None)
        flags.get('audited_replay', {}).pop('symbolic_repair', None)
        flags.get('audited_replay', {}).pop('ew_e_optimized', None)
        if relocated_proof:
            # The accepted manifest was frozen before publication. Its exact
            # validated bytes are unchanged; only the model-local path moved.
            flags['audited_replay']['provenance'].pop('relative_path',None)
        return flags
    original, requested = scientific(control), scientific(executed)
    old_sources, new_sources = control.get('engine_sources', {}), executed.get('engine_sources', {})
    authenticated = set()

    def dependency(name):
        digest = control.get('engine_source_hashes', {}).get(name)
        if (name not in old_sources or name not in new_sources or not digest
                or digest != executed.get('engine_source_hashes', {}).get(name)):
            raise ValueError('Control engine dependency identity differs: ' + name)
        if name not in authenticated:
            for sources in (old_sources, new_sources):
                authenticate({'relative_path': sources[name], 'sha256': digest})
            authenticated.add(name)
        return digest

    for name in old_sources.keys() & new_sources.keys():
        if old_sources[name] == new_sources[name]:
            continue
        digest = dependency(name)
        requested['engine_sources'][name] = old_sources[name]
        # Only a dependency's path changes; all other evidence fields survive.
        for flags, sources in ((original, old_sources), (requested, new_sources)):
            for ref in flags.get('configuration_evidence', []):
                if ref.get('relative_path') == sources[name]:
                    if ref.get('sha256') != digest or ref.get('original_source_hash') != consumed[model]:
                        raise ValueError('Relocated control dependency evidence identity differs')
                    ref['relative_path'] = old_sources[name]

    old_evidence = original.get('configuration_evidence', [])
    new_evidence = requested.get('configuration_evidence', [])
    if old_evidence != new_evidence:
        kept, position = [], 0
        for ref in new_evidence:
            if position < len(old_evidence) and ref == old_evidence[position]:
                kept.append(ref)
                position += 1
                continue
            names = [name for name, path in original.get('engine_sources', {}).items()
                     if path == ref.get('relative_path') and name in new_sources]
            redundant = (set(ref) == {'relative_path', 'sha256', 'original_source_hash'}
                         and ref.get('original_source_hash') == consumed[model]
                         and any(ref.get('sha256') == dependency(name) for name in names))
            if not redundant:
                kept.append(ref)
        if 'configuration_evidence' in original or kept:
            requested['configuration_evidence'] = kept
        else:
            requested.pop('configuration_evidence', None)
    if original != requested:
        raise ValueError('Cached method runtime/scientific flags differ from its retained GE/TE control')
    return {'consumed': consumed, 'immutable': immutable}


def prepare(units=None):
    from tools.project_core.registry.discovery import region_directory, resolve_model
    inventory_path = WORK/'inputs/validated_inventory.json'
    inventory = read(inventory_path)
    if sha(ROOT/'Project.xlsx') != inventory['project_sha256']:
        raise ValueError('Project registration changed since the authorized inventory; re-audit before adoption')
    metadata = coverage._metadata(ROOT)
    validated = {(row['unit_id'], row['model_id']): row for row in metadata
                 if row.get('researcher_review_status') == 'Validated by researcher'}
    items = [item for item in inventory['pairs'] if units is None or item['unit_id'] in units]
    if not items or (units is not None and units - {item['unit_id'] for item in items}):
        raise ValueError('Requested units are absent from the validated inventory')
    if {(item['unit_id'], item['model_id']) for item in inventory['pairs']} != set(validated):
        raise ValueError('Registered validated identities differ from the inventory')
    canonical = set(inventory['canonical_non_mc_methods'])
    consumed = {inventory_path: sha(inventory_path), ROOT/'Project.xlsx': sha(ROOT/'Project.xlsx')}
    immutable = {Path(adapter.__file__).resolve(): sha(Path(adapter.__file__))}
    plans = []
    for item in items:
        pair = item['unit_id'], item['model_id']
        print('Preflight '+pair[0]+': checking inputs, retained results and execution evidence',flush=True)
        row = validated[pair]
        region = region_directory(ROOT, pair[0])
        model = resolve_model(region, pair[1])
        if model.parent != (ROOT/item['model_dir']).resolve() or sha(model) != item['canonical_model_sha256']:
            raise ValueError('Canonical discovery/model identity differs: ' + str(pair))
        source = model.parent/'sppr_source.xlsx'
        manifest_path = model.parent/'results/result_manifest.json'
        snapshot = model.parent/'results/regional_snapshot.xlsx'
        manifest = read(manifest_path)
        if sha(source) != manifest.get('coefficient_source_sha256') or sha(snapshot) != manifest.get('snapshot_sha256'):
            raise ValueError('Saved source/snapshot disagrees with its manifest: ' + str(pair))
        regional = region/(region.name+'.xlsx')
        regional_book = read_book(regional)
        is_current = all(overview(regional_book).get(key) == pair[1] for key in ('selected_model_id', 'results_model_id'))
        workbook = regional if is_current else snapshot
        book = regional_book if is_current else read_book(snapshot)
        if (overview(book).get('results_model_id') != pair[1]
                or any(value and value != sha(model) for value in
                       (overview(book).get('results_model_sha256'), row.get('reviewed_model_sha256')))):
            raise ValueError('Saved calculation/review model identity differs: ' + str(pair))
        protected = protected_book(book)
        retained = set(protected['retained_methods'])
        wanted = list(item['pending_non_mc_methods'])
        if set(wanted) - canonical or set(wanted) & retained or any(key.startswith('MC_') for key in wanted):
            raise ValueError('Requested missing-method scope conflicts with retained finite/MC results: ' + str(pair))
        from tools.scientific_helpers.sppr.ppr_scopes import read_scopes
        for columns, groups in read_scopes(source).values():
            for key in set(wanted).intersection(columns):
                if any(finite(values[columns.index(key)]) for values in groups.values()):
                    raise ValueError('Requested missing method has finite saved source coefficients: ' + str(pair) + '/' + key)
        report = ROOT/row['validation_report_path']
        if not report.resolve().is_relative_to(ROOT.resolve()) or sha(report) != row['validation_report_sha256']:
            raise ValueError('Signed review source changed: ' + str(pair))
        immutable.update({model: sha(model), report: sha(report)})
        mapping = model.parent/'model_validation/taxon_mapping.xlsx'
        if mapping.is_file():
            immutable[mapping] = sha(mapping)
        # These files exist before adoption and must never be overwritten by it.
        evidence_root = model.parent/'results/diagnostics/method_coverage'
        if evidence_root.is_dir():
            immutable.update({path: sha(path) for path in evidence_root.rglob('*') if path.is_file()})
        consumed.update({path: sha(path) for path in (model, source, manifest_path, snapshot, regional)})
        batches = []
        if wanted:
            calculated = evidence_root/RUN_ID/'calculated/calculated.json'
            result = read(calculated)
            control_path = evidence_root/RUN_ID/'controls/verification.json'
            control = read(control_path)
            if (not control.get('passed') or control['identity']['model_sha256'] != sha(model)
                    or control['identity']['source_sha256'] != sha(source)
                    or adapter.engine_identity(control['identity']['flags'], model) != control['identity']['engine_identity']):
                raise ValueError('Retained GE/TE control is absent or incompatible: ' + str(pair))
            if set(wanted) - set(result.get('methods', {})):
                raise ValueError('Cached outcomes do not account for every requested method: ' + str(pair))
            groups = {}
            for key in wanted:
                verified = verify_method(model, calculated.parent, key, result['methods'][key])
                control_guards = check_control_settings(control['identity']['flags'], verified['identity']['flags'], model)
                consumed.update(control_guards['consumed'])
                immutable.update(control_guards['immutable'])
                identity_key = (json.dumps(verified['identity'], sort_keys=True)
                                + str(verified['constructor_path']) + sha(verified['constructor_path'])
                                + str(verified['initialization']['path']) + sha(verified['initialization']['path']))
                groups.setdefault(identity_key, {})[key] = verified
                immutable.update(verified['consumed'])
            for group in groups.values():
                batches.append(CachedBatch(model, calculated, group))
            immutable.update({calculated: sha(calculated), control_path: sha(control_path)})
        original_methods = manifest.get('method_coverage', {}).get('methods', {})
        original_context = manifest.get('method_coverage', {}).get('context')
        invalid_records = set(coverage._cached_methods(model.parent,
            {'context': original_context, 'methods': original_methods}, original_context, book, tuple(original_methods)))
        plans.append({'pair': pair, 'metadata': row, 'model': model, 'source': source, 'manifest': manifest_path,
                      'workbook': workbook, 'regional': regional, 'current': is_current, 'batches': batches,
                      'protected': protected, 'source_protected': source_state(source, retained),
                      'original_method_records': copy.deepcopy(original_methods),
                      'authentic_method_records': set(original_methods) - invalid_records,
                      'original_row_hashes': coverage._method_rows(book)[1],
                      'wanted': wanted})
        print('Preflight '+pair[0]+': verified '+str(len(wanted))+' requested methods',flush=True)
    check_hashes(consumed)
    check_hashes(immutable)
    return plans, consumed, immutable, central_state()


def assert_retained(plan):
    retained = set(plan['protected']['retained_methods'])
    unchanged_projection(plan['protected'], protected_book(read_book(plan['workbook']), retained), str(plan['pair']))
    unchanged_projection(plan['source_protected'], source_state(plan['source'], retained), str(plan['pair']) + '/source')
    methods = read(plan['manifest']).get('method_coverage', {}).get('methods', {})
    for key, record in plan['original_method_records'].items():
        if key not in plan['wanted'] and methods.get(key) != record:
            current = methods.get(key, {})
            if key in plan['authentic_method_records'] or current.get('preserve_saved') is not True:
                raise ValueError('Retained method provenance changed: ' + str(plan['pair']) + '/' + key)
            certificate = read(reference(plan['model'].parent/'results/diagnostics', current.get('evidence', {})))
            trace = certificate.get('prior_method_trace') or {}
            row_invalid = record.get('group_rows_sha256') != plan['original_row_hashes'].get(key)
            if (certificate.get('evidence_kind') != 'retained_saved_method'
                    or trace.get('recorded_outcome') != record
                    or (trace.get('evidence_check', {}).get('status') not in ('missing', 'hash_mismatch') and not row_invalid)):
                raise ValueError('Changed retained record lacks an honest original-evidence trace: ' + key)


def stamp_actual_execution(plan, batch, publication):
    """Keep current adoption software context separate from recorded execution."""
    path = plan['manifest']
    before = sha(path)
    manifest = read(path)
    result = manifest['method_coverage']
    for key, verified in batch.verified.items():
        outcome = result['methods'][key]
        identity = verified['identity']
        if outcome.get('execution_identity') != identity:
            raise ValueError('Adopted execution identity was not retained: ' + key)
        outcome['adoption_context'] = outcome['execution_context']
        actual = {'model_sha256': identity['model_sha256'], 'flags': identity['flags'],
                  'code_identity': identity['engine_hashes'], 'recorded_adapter_sha256': identity['adapter_sha256'],
                  'environment': identity.get('environment'), 'adapter_identity_caveat': ADAPTER_CAVEAT}
        outcome['execution_context'] = actual
        result.setdefault('method_contexts', {})[key] = copy.deepcopy(actual)
        for reference_key in ('constructor_evidence', 'runtime_verification_evidence'):
            if reference_key in outcome:
                copied = outcome[reference_key]
                copied['path'] = (Path(outcome['evidence']['path']).parent/Path(copied['path']).name).as_posix()
                reference(plan['model'].parent/'results/diagnostics', copied)
    publication.before_write(path)
    coverage._write_json(path, manifest, expected_sha256=before)
    publication.checkpoint([path], fingerprints={str(path): sha(path)})


def apply(plans, consumed, immutable, central, review):
    from tools.project_core.registry.writes import central_lock
    from tools.project_core.registry.publication import publication_transaction
    from tools.project_core.registry.update_project import update
    from tools.project_core.maps.build_html import build
    from promote_humboldt_review import publish_review
    from completion_checkpoints import make_bindings, load_model_checkpoint, restore_model_checkpoint, capture_model_checkpoint
    pairs = {plan['pair'] for plan in plans}
    reports = []
    restorations = []
    cache_root = WORK/'outputs/completion_checkpoints'
    producer_paths = [Path(__file__), WORK/'code/completion_checkpoints.py',
                      ROOT/'tools/project_core/calculations/coverage.py',
                      ROOT/'tools/project_core/registry/publication.py',
                      ROOT/'tools/project_core/workbooks/workbooks.py']
    producer = {p.resolve(): sha(p) for p in producer_paths}
    producer.update({(ROOT/'tools/project_core'/name).resolve(): h for name, h in coverage._arithmetic_identity().items()})
    bindings = {plan['pair']: make_bindings(ROOT, plan, consumed, immutable, producer) for plan in plans if plan['batches']}
    journal = WORK/'outputs'/('adoption_ownership_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.jsonl')
    with central_lock(ROOT), publication_transaction(ROOT, model_pairs=pairs) as publication:
        publication.journal_path = journal
        if any(cache_root.resolve().is_relative_to(p.resolve()) for p in publication.generated_directories):
            raise ValueError('Checkpoint cache is inside publication rollback scope')
        recovery = read(WORK/'tmp/adoption_recovery_attempt3/manifest.json')
        if any((ROOT/e['path']).resolve().is_relative_to(cache_root.resolve()) for e in recovery['entries']):
            raise ValueError('Checkpoint cache is inside durable rollback inventory')
        check_hashes(consumed)
        check_hashes(immutable)
        # Exact input-file hashes bind the parsed preflight protection records;
        # rereading every workbook here would duplicate the same verification.
        for plan in plans:
            if not plan['batches']:
                continue
            binding = bindings[plan['pair']]
            checkpoint = load_model_checkpoint(ROOT, plan, cache_root, binding)
            if checkpoint:
                restored = restore_model_checkpoint(ROOT, plan, checkpoint, publication)
                check_hashes(immutable)
                assert_retained(plan)
                reports.extend(restored['batch_reports'])
                restorations.append(restored['cache_restoration'])
                print(plan['pair'][0]+': restored verified COMPLETE package without execution or stamping', flush=True)
                continue
            model_reports = []
            written_paths = set()
            for batch in plan['batches']:
                check_hashes(immutable)
                changed, report = coverage._complete_model(ROOT, plan['metadata'], tuple(batch.verified),
                    progress=lambda message: print(message, flush=True), compute=batch,
                    retry_unavailable=True, execution_flags=batch.identity['flags'])
                publication.checkpoint(report.get('written_paths', ()), fingerprints=report.get('written_hashes'))
                written_paths.update(report.get('written_paths', ()))
                if changed:
                    stamp_actual_execution(plan, batch, publication)
                model_reports.append({'unit_id': plan['pair'][0], 'model_id': plan['pair'][1],
                                'methods': list(batch.verified), 'changed': changed,
                                'execution_identity': batch.identity})
                check_hashes(immutable)
            if plan['batches']:
                assert_retained(plan)
                check_hashes(producer)
                from completion_checkpoints import base_destinations
                output_paths = {Path(p).resolve() for p in written_paths} | base_destinations(plan)
                exact_outputs = {p: publication.owned[p] for p in output_paths}
                seal = capture_model_checkpoint(ROOT, plan, cache_root, binding, model_reports, exact_outputs)
                reports.extend(model_reports)
                print(plan['pair'][0]+': COMPLETE checkpoint sealed '+sha(seal), flush=True)
        paths = sorted({plan['regional'] for plan in plans if plan['batches'] and plan['current']})
        if paths:
            # Explicit empty scientific scope prevents update() invoking coverage.
            update(ROOT, paths, lock_held=True, coverage_units=set())
        build(ROOT/'Project.xlsx', only_units={plan['pair'][0] for plan in plans}, lock_held=True)
        unchanged_projection(central, central_state(), 'Project human metadata/reviews/selections')
        check_hashes(immutable)
        for plan in plans:
            assert_retained(plan)
        print('Scientific adoption verified; promoting the approved Humboldt EE-floor report', flush=True)
        amended_review = publish_review(ROOT, WORK, review)
        # Every old immutable expectation was checked above. Only this one
        # explicitly authorized signed-source amendment changes that contract.
        immutable[review['canonical']] = review['handoff']['staged_sha256']
        check_hashes(immutable)
        summary = {'schema_version': 1, 'timestamp': datetime.now(timezone.utc).isoformat(),
                   'scientific_execution_performed': False, 'adapter_identity_caveat': ADAPTER_CAVEAT,
                   'models': reports, 'project_sha256': sha(ROOT/'Project.xlsx'),
                   'checkpoint_restorations': restorations, 'ownership_journal': journal.relative_to(ROOT).as_posix(),
                   'humboldt_review_amendment': amended_review,
                   'checks': ['all canonical inputs and consumed evidence unchanged',
                              'retained finite/MC coefficients, arithmetic and diagnostics unchanged',
                              'Catch, Classic PPR, NPP, groups, matching and selections unchanged',
                              'signed reviews unchanged except the authorized Humboldt GE/TE amendment',
                              'all validated decisions and researcher exclusions preserved', 'saved-data publication only']}
        output = WORK/'outputs/adoption_publication.json'
        publication.before_write(output)
        coverage._write_json(output, summary, expected_sha256=sha(output) if output.is_file() else None)
        publication.checkpoint([output], fingerprints={str(output): sha(output)})
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--units', nargs='+', help='Optional explicit subset of validated units')
    parser.add_argument('--apply', action='store_true', help='Adopt authenticated caches and publish; otherwise read-only preflight')
    parser.add_argument('--review-handoff', type=Path, help='SHA-bound staged Humboldt amendment handoff')
    args = parser.parse_args()
    if args.apply and args.units:
        parser.error('Final adoption covers every validated pair; --units is available only for read-only preflight')
    if args.apply and not args.review_handoff:
        parser.error('Final adoption requires the reviewed Humboldt DOCX handoff')
    review = None
    if args.review_handoff:
        from promote_humboldt_review import prepare_review
        review = prepare_review(ROOT, args.review_handoff)
    plans, consumed, immutable, central = prepare(set(args.units) if args.units else None)
    if review:
        immutable.update({review['staged']: review['handoff']['staged_sha256'],
                          review['handoff_path']: review['handoff_sha256']})
        immutable.update(review['consumed'])
    if args.apply:
        result = apply(plans, consumed, immutable, central, review)
    else:
        result = {'read_only': True, 'pairs': [{'unit_id': plan['pair'][0], 'model_id': plan['pair'][1],
                  'requested_methods': plan['wanted'], 'execution_batches': len(plan['batches']),
                  'retained_finite_or_mc_methods': plan['protected']['retained_methods']} for plan in plans],
                  'immutable_files_verified': len(immutable), 'adapter_identity_caveat': ADAPTER_CAVEAT}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
