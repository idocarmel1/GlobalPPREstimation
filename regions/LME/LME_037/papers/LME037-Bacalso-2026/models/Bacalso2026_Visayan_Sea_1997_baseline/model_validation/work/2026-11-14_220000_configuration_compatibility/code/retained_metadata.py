"""LME037 retained metadata compatibility; no model solve or workbook write.

The original three-method inventory and scientific payload remain unchanged.
Current verification code hashes are not historical arithmetic identities.
The authenticated historical initializer remains unsupported by the stock
adapter. Only an enclosing coordinator publication transaction may apply.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from unittest.mock import patch

SCRIPT = Path(__file__).resolve()
SCRIPT_SHA256 = hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
RUN = SCRIPT.parents[1]
MODEL = RUN.parents[2]
ROOT = next(p for p in SCRIPT.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
OUTPUT = RUN / 'outputs'
ARCHIVE = RUN / 'inputs/original_result_manifest.json'
RAW = MODEL / 'results/diagnostics/researcher_adjustments_20261114'
REGIONAL = ROOT / 'regions/LME/LME_037/LME_037.xlsx'
TARGET_DIR = MODEL / 'results/diagnostics/configuration_compatibility_20261114'
ORIGINAL_SHA = 'c422ba7826f17b1785bc50d8f9b60b88da8f5608e30a6908a824b7794c7baf2b'
SOURCE_SHA = 'a361c3dbf6abef5cedb0d0d480492e55907efde57b573278c5a7db2b7dbaf270'
REGIONAL_SHA = 'f8b78a3ca0bc1303f3b3a41cf1944c704df1a635a7c709246ec3a83057c94965'
INDEX_SHA = 'ec86567c3eb9398d86fe158d0af71a89d8b02b1794e94cfef69cb125170ef2f0'
REPORT_SHA = 'd28f170b249548a4520000affbe6fc68ff2e3ce1c97220f714c857eed88d6c2e'
METHODS = ['new_GE', 'new_TE_EEfix', 'new_WithEgestion']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(path):
    return sha(path) if Path(path).is_file() else None


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def normalized_flags(original):
    configuration = read(RAW / 'configuration.json')
    execution = read(RAW / 'execution_evidence.json')
    need(configuration == execution['configuration'], 'Execution configuration disagrees')
    need(configuration['canonical_model_sha256'] == SOURCE_SHA, 'Configuration source mismatch')
    old = original['effective_flags']
    need(old == execution['effective_loader_flags'], 'Original effective flags differ from execution')
    constructor = configuration['constructor']
    need(all(old.get(k) == v for k, v in constructor.items()), 'Flattened constructor differs')
    need(constructor['ee_floor'] == 1.0 and constructor['ee_threshold'] == .1
         and constructor['use_ee_floor'] is True, 'Approved special floor configuration changed')
    need(constructor['normalize_DC'] is True and constructor['DC_tol'] == .0021
         and constructor['refresh_missing_biomass_accum'] is True, 'Diet/BA configuration changed')
    sources = read(RAW / 'code_identity.json')
    need(sources['sha256'] == configuration['engine_hashes'], 'Executed engine identity differs')
    for name, expected in sources['sha256'].items():
        need(sha(MODEL / sources['paths'][name]) == expected, 'Executed engine bytes changed: ' + name)
    flags = {k: copy.deepcopy(v) for k, v in old.items()
             if k not in constructor and k != 'configuration_evidence'}
    flags.update(constructor=copy.deepcopy(constructor),
                 diagnostics=copy.deepcopy(configuration['diagnostics']),
                 engine_source_hashes=copy.deepcopy(sources['sha256']),
                 stock_adapter_reconstructible=False,
                 configuration_evidence=[{'relative_path': p.relative_to(MODEL).as_posix(),
                     'sha256': sha(p), 'original_source_hash': SOURCE_SHA}
                     for p in (RAW / 'configuration.json', RAW / 'execution_evidence.json')])
    need(flags['runtime_initialization'] == old['runtime_initialization'], 'Runtime marker changed')
    return flags


def audit(original):
    """Hash and saved-table verification only; no importer or scientific engine."""
    from tools.project_core.workbooks.workbooks import read_book, records, overview, input_hash
    from tools.project_core.calculations import coverage, regional
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    from tools.scientific_helpers.sppr import method_coverage
    expected = {MODEL / 'model.json': SOURCE_SHA, REGIONAL: REGIONAL_SHA,
                MODEL / 'results/regional_snapshot.xlsx': REGIONAL_SHA,
                RAW / 'evidence_index.json': INDEX_SHA,
                MODEL / 'model_validation/validation.docx': REPORT_SHA,
                MODEL / 'sppr_source.xlsx': original['coefficient_source_sha256']}
    for path, digest in expected.items():
        need(sha(path) == digest, 'Authenticated source changed: ' + rel(path))
    index = read(RAW / 'evidence_index.json')
    for item in index['artifacts']:
        path = (RAW / item['path']).resolve()
        need(path.is_relative_to(RAW.resolve()), 'Evidence path outside raw package')
        need(item['availability'] == 'present' and fingerprint(path) == item['sha256'],
             'Authenticated evidence unavailable/changed: ' + item['path'])
    sink = read(RAW / 'mortality_sink_info.json')
    need(sink['affected_groups'] == [1] and sink['external_mortality_export_total'] == .000784,
         'Seabird-only mortality sink differs')
    need(sink['ee_floor'] == 1.0 and sink['ee_threshold'] == .1, 'Floor assumptions differ')
    book = read_book(REGIONAL)
    settings = overview(book)
    need(settings['selected_model_id'] == MODEL.name == settings['results_model_id'], 'Selected identity changed')
    need(settings['calculation_input_sha256'] == input_hash(book), 'Saved input digest failed')
    need(settings['calculation_result_sha256'] == regional.result_hash(book), 'Saved result digest failed')
    group_rows = records(book, 'Selected model groups', 'Group SPPR')
    need(len(group_rows) == 306, 'Saved coefficient count changed')
    _, row_hashes = coverage._method_rows(book)
    cov = original['method_coverage']
    need(cov['expected_methods'] == METHODS and set(cov['methods']) == set(METHODS), 'Three-method scope changed')
    need('context' not in cov and 'arithmetic_code_identity' not in cov, 'Unexpected historical cache claim')
    for key in METHODS:
        outcome = cov['methods'][key]
        need(outcome['group_rows_sha256'] == row_hashes[key], 'Coefficient digest changed: ' + key)
        need(outcome['status'] == 'ok' and outcome['annual_status'] == dict.fromkeys(('all', 'inner', 'PP'), 'ok'),
             'Scientific/annual status changed: ' + key)
    saved = {(r['method'], r['scope'], r['group']): r['sppr'] for r in group_rows}
    raw = {(r['method'], r['scope'], r['group']): r['sppr'] for r in read(RAW / 'group_sppr.json')}
    need(saved.keys() == raw.keys(), 'Raw coefficient identities differ')
    need(all(math.isfinite(v) and v >= 0 and math.isclose(v, raw[k], rel_tol=1e-12, abs_tol=1e-12)
             for k, v in saved.items()), 'Saved/raw coefficient serialization differs')
    runtime_groups = {r['seq']: r for r in read(RAW / 'groups.json')}
    protected_fields = ('biomass', 'pb', 'qb', 'gs', 'catch', 'emigration', 'immigration', 'net_migration')
    for group in records(book, 'Selected model groups', 'Groups'):
        runtime = runtime_groups[group['seq']]
        need(group['group_name'] == runtime['group_name'], 'Group identity changed')
        for field in protected_fields:
            a, b = group.get(field), runtime.get(field)
            need(a == b or (isinstance(a, (float, int)) and isinstance(b, (float, int))
                 and math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)), 'Protected group field differs: ' + field)
    external = [r['seq'] for r in runtime_groups.values() if (r.get('external_mortality_export') or 0) != 0]
    need(external == [1] and runtime_groups[1]['external_mortality_export'] == .000784, 'Runtime sink differs')
    flags = normalized_flags(original)
    candidate = copy.deepcopy(original); candidate['effective_flags'] = flags
    resolved = resolve_audited_configuration(MODEL, book, candidate)
    need(resolved['constructor'] == flags['constructor'] and resolved['diagnostics'] == flags['diagnostics'],
         'Resolver altered executed configuration')
    with patch.object(method_coverage, '_audited_engine', side_effect=AssertionError('Stock engine accessed')):
        try:
            method_coverage._constructor(resolved, MODEL / 'model.json')
        except ValueError as error:
            need('Unsupported retained runtime initialization' in str(error), 'Wrong stock guard failure')
        else:
            raise ValueError('Custom runtime guard failed')
    # Calling the cache predicate is safe: absence of historical arithmetic
    # identity is intentionally terminal before a context/engine is requested.
    need(not coverage._package_cache_valid(MODEL, REGIONAL, candidate, {}, METHODS), 'Unexpected full-cache claim')
    return {'artifact_count': len(index['artifacts']), 'coefficient_rows': len(group_rows),
            'method_scope_statuses': {k: cov['methods'][k]['annual_status'] for k in METHODS},
            'max_saved_raw_coefficient_absolute_difference': max(abs(saved[k] - raw[k]) for k in saved),
            'protected_group_fields_verified': list(protected_fields),
            'stock_runtime_guard_passed_before_engine_access': True,
            'canonical_inventory_cache_valid': False,
            'cache_limitation': 'Historical arithmetic identity/context were not recorded; no full-inventory cache identity is invented.',
            'regional_and_snapshot_sha256': REGIONAL_SHA, 'canonical_sha256': SOURCE_SHA,
            'raw_evidence_index_sha256': INDEX_SHA, 'signed_report_sha256': REPORT_SHA,
            'scientific_solve_performed': False, 'new_MC_draws_performed': False,
            'current_engine_equivalence_claimed': False}


def _path(name):
    path = (ROOT / name).resolve()
    need(path.is_relative_to(ROOT), 'Plan path outside workspace: ' + str(name))
    return path


def _validate_plan_paths(plan):
    targets = [_path(item['target']) for item in plan['promotions']]
    need(len(targets) == len(set(targets)), 'Duplicate promotion target')
    for item in plan['promotions']:
        need(_path(item['source']) not in targets, 'Promotion source overlaps target')
        need(item['target'] in plan['consumed_inputs'], 'Target has no before-write hash')
    for name in plan['consumed_inputs']:
        _path(name)


def _check_inputs(plan, *, installed=False):
    targets = {x['target'] for x in plan['promotions']}
    for name, expected in plan['consumed_inputs'].items():
        if installed and name in targets:
            continue
        need(fingerprint(_path(name)) == expected, 'Consumed input changed: ' + name)
    for item in plan['promotions']:
        need(sha(_path(item['source'])) == item['sha256'], 'Promotion source changed: ' + item['source'])


def prepare():
    need(sha(SCRIPT) == SCRIPT_SHA256, 'Verifier changed after import')
    live = MODEL / 'results/result_manifest.json'
    need(sha(live) == ORIGINAL_SHA, 'Original manifest changed before preparation')
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    if ARCHIVE.exists():
        need(sha(ARCHIVE) == ORIGINAL_SHA, 'Preserved original manifest changed')
    else:
        ARCHIVE.write_bytes(live.read_bytes())
    original = read(ARCHIVE)
    checks = audit(original)
    verification_paths = [ROOT / 'tools' / name for name in (
        'scientific_helpers/sppr/configuration.py', 'scientific_helpers/sppr/method_coverage.py',
        'project_core/calculations/coverage.py', 'project_core/calculations/regional.py',
        'project_core/workbooks/workbooks.py', 'project_core/registry/publication.py')]
    ledger = {'schema_version': 1, 'unit_id': 'LME_037', 'model_id': MODEL.name,
              'original_manifest_sha256': ORIGINAL_SHA,
              'original_manifest_archive': (TARGET_DIR / ARCHIVE.name).relative_to(MODEL).as_posix(),
              'scope': 'Metadata compatibility only; exact retained three-method scientific inventory preserved.',
              'configuration_evidence': normalized_flags(original)['configuration_evidence'],
              'checks': checks, 'current_verification_code_only': {rel(p): sha(p) for p in verification_paths},
              'verification_source_path': rel(SCRIPT), 'verification_source_sha256': SCRIPT_SHA256,
              'historical_arithmetic_identity_inferred': False, 'workbook_bytes_changed': False,
              'raw_scientific_evidence_changed': False, 'current_engine_equivalence_claimed': False}
    ledger_path = OUTPUT / 'retained_compatibility.json'; write(ledger_path, ledger)
    manifest = copy.deepcopy(original)
    manifest['effective_flags'] = normalized_flags(original)
    manifest['retained_configuration_compatibility'] = {
        'ledger': (TARGET_DIR / ledger_path.name).relative_to(MODEL / 'results').as_posix(),
        'ledger_sha256': sha(ledger_path), 'original_manifest_sha256': ORIGINAL_SHA,
        'role': ledger['scope'], 'scientific_solve_performed': False,
        'stock_adapter_reconstructible': False, 'current_engine_equivalence_claimed': False}
    manifest_path = OUTPUT / 'result_manifest.json'; write(manifest_path, manifest)
    promotions = [{'source': rel(src), 'target': rel(dst), 'sha256': sha(src)} for src, dst in (
        (ARCHIVE, TARGET_DIR / ARCHIVE.name), (ledger_path, TARGET_DIR / ledger_path.name),
        (manifest_path, live))]
    paths = {SCRIPT, ARCHIVE, REGIONAL, MODEL / 'model.json', MODEL / 'sppr_source.xlsx',
             MODEL / 'results/regional_snapshot.xlsx', MODEL / 'model_validation/validation.docx',
             MODEL / 'model_validation/taxon_mapping.xlsx', *verification_paths}
    for directory in (RAW, MODEL / 'extracted_tables', MODEL / 'model_validation/evidence/researcher_adjustments_20261114'):
        paths.update(p for p in directory.rglob('*') if p.is_file())
    paths.update(_path(p['target']) for p in promotions)
    plan = {'schema_version': 1, 'unit_id': 'LME_037', 'model_id': MODEL.name,
            'prepared_by': SCRIPT_SHA256, 'expected_methods': METHODS,
            'consumed_inputs': {rel(p): fingerprint(p) for p in sorted(paths)},
            'promotions': promotions, 'scientific_solve_performed': False,
            'original_manifest_sha256': ORIGINAL_SHA}
    write(OUTPUT / 'preparation.json', plan)
    return verify_package()


def verify_package():
    need(sha(SCRIPT) == SCRIPT_SHA256, 'Verifier changed after import')
    plan = read(OUTPUT / 'preparation.json')
    need(plan['prepared_by'] == SCRIPT_SHA256, 'Verifier changed since preparation')
    _validate_plan_paths(plan)
    allowed = {rel(TARGET_DIR / ARCHIVE.name), rel(TARGET_DIR / 'retained_compatibility.json'),
               rel(MODEL / 'results/result_manifest.json')}
    need({p['target'] for p in plan['promotions']} == allowed, 'Promotion scope exceeds metadata package')
    installed = all(fingerprint(_path(p['target'])) == p['sha256'] for p in plan['promotions'])
    _check_inputs(plan, installed=installed)
    need(sha(ARCHIVE) == ORIGINAL_SHA, 'Original manifest archive changed')
    original, staged = read(ARCHIVE), read(OUTPUT / 'result_manifest.json')
    reconstructed = copy.deepcopy(staged)
    reconstructed.pop('retained_configuration_compatibility', None)
    reconstructed['effective_flags'] = original['effective_flags']
    need(reconstructed == original, 'Manifest change exceeded configuration metadata')
    need(staged['effective_flags'] == normalized_flags(original), 'Normalized flags differ from execution evidence')
    ledger = read(OUTPUT / 'retained_compatibility.json')
    need(staged['retained_configuration_compatibility']['ledger_sha256'] == sha(OUTPUT / 'retained_compatibility.json'), 'Ledger binding failed')
    need(ledger['verification_source_sha256'] == SCRIPT_SHA256, 'Ledger verifier changed')
    checks = audit(original)
    need(checks == ledger['checks'], 'Retained verification checks changed')
    _check_inputs(plan, installed=installed)
    write(RUN / 'qa/verification.json', {'passed': True, 'installed': installed,
        'promotions': len(plan['promotions']), 'checks': checks, 'plan_sha256': sha(OUTPUT / 'preparation.json')})
    return plan


def _apply_plan(plan, publication):
    from tools.project_core.registry.publication import _ACTIVE, publication_write
    from tools.project_core.calculations.coverage import _write_bytes
    need(publication in _ACTIVE.get() and publication.root == ROOT, 'Active publication transaction required')
    lock = ROOT / '.project-write.lock'
    need(lock.is_file() and lock.read_text().strip() == str(os.getpid()), 'Current process must hold Project writer lock')
    _validate_plan_paths(plan)
    installed = all(fingerprint(_path(p['target'])) == p['sha256'] for p in plan['promotions'])
    _check_inputs(plan, installed=installed)
    if installed:
        return {'status': 'already_applied', 'changed_units': ['LME_037'], 'written_paths': [], 'written_hashes': {}}
    for item in plan['promotions']:
        source, target = _path(item['source']), _path(item['target'])
        data = source.read_bytes()
        need(hashlib.sha256(data).hexdigest() == item['sha256'], 'Promotion changed immediately before write')
        with publication_write(target, fingerprint=item['sha256']):
            _write_bytes(target, data, expected_sha256=plan['consumed_inputs'][item['target']])
    _check_inputs(plan, installed=True)
    return {'status': 'applied', 'changed_units': ['LME_037'],
            'written_paths': [str(_path(p['target'])) for p in plan['promotions']],
            'written_hashes': {str(_path(p['target'])): p['sha256'] for p in plan['promotions']}}


def apply(publication):
    result = _apply_plan(verify_package(), publication)
    verify_package()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'verify'])
    args = parser.parse_args()
    plan = prepare() if args.command == 'prepare' else verify_package()
    print(json.dumps({'verified': True, 'promotions': len(plan['promotions']), 'scientific_solve_performed': False}))
