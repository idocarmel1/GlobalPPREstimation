"""Retained-only adoption with authenticated historical and current roles.

Original preparations, workbooks, raw matrices and executed importers are never
rewritten. The sole replacement promotion is a manifest recording unchanged
arithmetic compatibility after scoped orchestration edits. Current engines are
not claimed equivalent to the pinned engines that executed these results.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve()
SCRIPT_SHA256 = hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
RUN = SCRIPT.parents[1]
ROOT = next(p for p in SCRIPT.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
PACIFIC = RUN.parent / '2026-11-14_160800_floor_adoption'
MID49 = '49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
MODEL49 = ROOT / 'regions/LME/LME_049/papers/KUR-2019/models' / MID49
RUN49 = MODEL49 / 'model_validation/work/2026-11-14_183000_map_adoption'
MODEL38 = ROOT / 'regions/LME/LME_038/papers/INDO-1999/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)'
RUN38 = MODEL38 / 'model_validation/work/2026-11-14_152558_signoff'
UNITS = ('HS_071', 'EEZ_598', 'EEZ_941', 'LME_038', 'LME_049')
ORIGINAL_PLANS = {
    'HS_071': 'e79691939016f1ab1d2f507286037378ec287fb379251a371cced5595e60bf76',
    'EEZ_598': '079a01dd6956417be891337d6baad56949e099e24214e00555fc0b0442846b17',
    'EEZ_941': '467736622e46b01668451836e20fde7332dac3e4ba19db154966e93eae8c1bde',
    'LME_038': 'd710a7dc11ee984e6eafb1852ddeb4fc58f0fa0debf08b664f3fe12b685bb234',
    'LME_049': '3f5625f3d940222996ad11d98a5f8c63c8659002d627ca93dde82f280c7d210a',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(path):
    return sha(path) if Path(path).is_file() else None


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def package(unit):
    if unit in UNITS[:3]:
        directory = PACIFIC / 'outputs' / unit
        verifier = module('_retained_wcpo', PACIFIC / 'code/verified_floor_packages.py')
        staged_model = directory / 'model'
        model = verifier.prepared.model_dir(unit)
    elif unit == 'LME_038':
        directory = RUN38 / 'outputs/current_adoption_v3'
        verifier = module('_retained_java', RUN38 / 'code/adopt_current_diagnostics.py')
        staged_model, model = directory / 'model', MODEL38
    elif unit == 'LME_049':
        directory = RUN49 / 'outputs/current_adoption'
        verifier = module('_retained_watari', RUN49 / 'code/verified_lme049_package.py')
        staged_model, model = directory / 'model' / MID49, MODEL49
    else:
        raise ValueError('Unsupported exact unit')
    plan_path = directory / 'preparation.json'
    if sha(plan_path) != ORIGINAL_PLANS[unit]:
        raise ValueError('Original preparation changed: ' + unit)
    return directory, staged_model, model, verifier, read(plan_path)


def ast_nodes(path):
    tree = ast.parse(Path(path).read_text(encoding='utf-8-sig'))
    result = {}
    for i, node in enumerate(tree.body):
        if hasattr(node, 'name'):
            name = node.name
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            name = 'assignment_' + '_'.join(ast.dump(n, include_attributes=False) for n in targets)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            name = 'import_' + ast.dump(node, include_attributes=False)
        else:
            name = 'statement_' + str(i)
        result[name] = ast.dump(node, include_attributes=False)
    return result


def arithmetic_compatibility(manifest):
    from tools.project_core.calculations import coverage
    previous = manifest['method_coverage']['arithmetic_code_identity']
    current = coverage._arithmetic_identity()
    baseline = RUN / 'inputs/coverage_before_scope.py'
    if sha(baseline) != previous['calculations/coverage.py']:
        raise ValueError('Archived arithmetic identity does not match original manifest')
    changed_files = [name for name in previous if previous[name] != current.get(name)]
    if set(previous) != set(current) or set(changed_files) - {'calculations/coverage.py'}:
        raise ValueError('Unreviewed arithmetic dependency changed: ' + str(changed_files))
    old_nodes, new_nodes = ast_nodes(baseline), ast_nodes(ROOT / 'tools/project_core/calculations/coverage.py')
    differences = [name for name in old_nodes.keys() | new_nodes.keys() if old_nodes.get(name) != new_nodes.get(name)]
    allowed = {'ensure_validated_coverage', 'scoped_validated_metadata'}
    # A module docstring is descriptive only; all numeric helpers stay exact.
    allowed.add('statement_0')
    if set(differences) - allowed:
        raise ValueError('Unreviewed coverage AST difference: ' + str(differences))
    return {'original_arithmetic_code_identity': previous, 'compatible_current_arithmetic_code_identity': current,
            'archived_coverage_path': rel(baseline), 'archived_coverage_sha256': sha(baseline),
            'changed_files': changed_files, 'changed_top_level_ast_nodes': sorted(differences),
            'unchanged_numeric_helpers_and_other_arithmetic_modules': True,
            'scope': 'Only inventory target selection/orchestration and descriptive module text may differ; no arithmetic function or constant may differ.',
            'scientific_solve_performed': False, 'new_mc_draws_performed': False}


def historical_guards(plan):
    originals = {
        'tools/scientific_code/PPREstimation/PPRCalculator.py': MODEL49 / 'results/diagnostics/ee_floor_seabird_accounting_20261114/code/engine/PPRCalculator.py',
        'tools/scientific_helpers/sppr/method_coverage.py': PACIFIC / 'outputs/EEZ_598/model/results/diagnostics/ee_floor/retained_direct_20261114/executed_code/method_coverage.py',
        'tools/project_core/calculations/coverage.py': RUN / 'inputs/coverage_before_scope.py',
    }
    changes = []
    for name, expected in plan['consumed_inputs'].items():
        actual = fingerprint(ROOT / name)
        if actual == expected:
            continue
        original = originals.get(name)
        if original is None or sha(original) != expected:
            raise ValueError('Unreconciled consumed input changed: ' + name)
        changes.append({'historical_live_path': name, 'historical_sha256': expected,
                        'authenticated_original_path': rel(original), 'authenticated_original_sha256': sha(original),
                        'current_shared_sha256': actual,
                        'role': 'Historical consumed-code identity retained separately from current publication orchestration',
                        'current_engine_equivalence_claimed': False})
    return changes


def original_invariants(unit, directory, staged_model, verifier, plan, manifest, *, check_current_inputs=True):
    """Execute the original assertions in their explicitly historical context.

    Only guard-role rebinding, adapter metadata identity and original arithmetic
    file identity are substituted, after separate full-byte authentication.
    No numerical function, outcome or scientific context is replaced.
    """
    from tools.project_core.calculations import coverage
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    changes = historical_guards(plan) if check_current_inputs else []
    regional = directory / 'regional' / (unit + '.xlsx')
    # Java Sea staging contains promoted outputs only; its unchanged canonical
    # model and pinned executed engine stay at the authenticated model location.
    identity_model = MODEL38 if unit == 'LME_038' else staged_model
    flags = resolve_audited_configuration(identity_model, coverage._settings_book(regional), manifest)
    actual_context = coverage._context(ROOT, identity_model / 'model.json', flags)
    if not coverage._same_context(actual_context, plan['context']):
        raise ValueError('Pinned scientific context changed: ' + unit)
    # All listed artifact bytes and original non-code input guards have been
    # checked first. Running the historical verifier adds its detailed invariant
    # checks without demanding that modern adapter bytes executed the old run.
    original_context = coverage._context
    def historical_context(*args, **kwargs):
        context = original_context(*args, **kwargs)
        if not coverage._same_context(context, plan['context']):
            raise ValueError('Scientific context changed during verification')
        return {**context, 'adapter_sha256': plan['context']['adapter_sha256']}
    def qa_only(path, value):
        write(RUN / 'qa/original_verifier' / unit / Path(path).name, value)
    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(coverage, '_arithmetic_identity', return_value=manifest['method_coverage']['arithmetic_code_identity']))
        stack.enter_context(patch.object(coverage, '_context', side_effect=historical_context))
        if unit in UNITS[:3]:
            stack.enter_context(patch.object(verifier.prepared, 'write', side_effect=qa_only))
            verifier.verify_package(unit, check_current_inputs=False)
        elif unit == 'LME_038':
            verifier.verify_package(directory, check_inputs=False)
        else:
            stack.enter_context(patch.object(verifier.base, 'write', side_effect=qa_only))
            verifier.verify_package(directory, check_inputs=False)
    return actual_context, changes


def prepare(unit):
    from tools.project_core.calculations import coverage
    if sha(SCRIPT) != SCRIPT_SHA256:
        raise ValueError('Coordinator source changed after import')
    directory, staged_model, model, verifier, original = package(unit)
    original_manifest = read(staged_model / 'results/result_manifest.json')
    compatibility = arithmetic_compatibility(original_manifest)
    context, drift = original_invariants(unit, directory, staged_model, verifier, original, original_manifest)
    for item in original['promotions']:
        if sha(directory / item['source']) != item['sha256']:
            raise ValueError('Original staged promotion changed')
    out = RUN / 'outputs/retained' / unit
    ledger = {'schema_version': 1, 'unit_id': unit, 'model_id': original['model_id'],
              'original_preparation_path': rel(directory / 'preparation.json'),
              'original_preparation_sha256': ORIGINAL_PLANS[unit],
              'original_manifest_sha256': sha(staged_model / 'results/result_manifest.json'),
              'original_scientific_context_preserved': original['context'],
              'current_context_difference': {'adapter_sha256': context['adapter_sha256']},
              'consumed_code_role_reconciliation': drift, 'arithmetic_compatibility': compatibility,
              'current_shared_engine_equivalence_claimed': False,
              'numerical_artifacts_or_raw_mc_changed': False,
              'scientific_solve_performed': False, 'approval_transferred_to_new_methods': False,
              'verification_source_path': rel(SCRIPT), 'verification_source_sha256': SCRIPT_SHA256}
    ledger_path = out / 'retained_reuse.json'
    write(ledger_path, ledger)
    manifest = copy.deepcopy(original_manifest)
    manifest['method_coverage']['arithmetic_code_identity'] = compatibility['compatible_current_arithmetic_code_identity']
    manifest['retained_publication_reconciliation'] = {
        'original_arithmetic_code_identity': compatibility['original_arithmetic_code_identity'],
        'ledger': 'diagnostics/method_coverage/coordinator_20261114/retained_reuse.json',
        'ledger_sha256': sha(ledger_path),
        'role': 'Metadata-only compatible arithmetic reuse; original numerical execution context, methods and artifacts remain unchanged.',
        'scientific_solve_performed': False, 'current_engine_equivalence_claimed': False}
    manifest_path = out / 'result_manifest.json'
    write(manifest_path, manifest)
    if not coverage._package_cache_valid(staged_model, directory / 'regional' / (unit + '.xlsx'), manifest, context, original['expected_methods']):
        raise ValueError('Current retained cache failed')
    promotions = [{**item, 'source': rel(directory / item['source'])} for item in original['promotions']]
    manifest_target = rel(model / 'results/result_manifest.json')
    for item in promotions:
        if item['target'] == manifest_target:
            item.update(source=rel(manifest_path), sha256=sha(manifest_path))
    target = rel(model / 'results/diagnostics/method_coverage/coordinator_20261114/retained_reuse.json')
    promotions.append({'source': rel(ledger_path), 'target': target, 'sha256': sha(ledger_path)})
    consumed = copy.deepcopy(original['consumed_inputs'])
    for item in drift:
        consumed[item['historical_live_path']] = item['current_shared_sha256']
        consumed[item['authenticated_original_path']] = item['authenticated_original_sha256']
    consumed.update({rel(SCRIPT): sha(SCRIPT), rel(directory / 'preparation.json'): ORIGINAL_PLANS[unit],
                     rel(RUN / 'inputs/coverage_before_scope.py'): sha(RUN / 'inputs/coverage_before_scope.py'),
                     target: fingerprint(ROOT / target)})
    for name, value in compatibility['compatible_current_arithmetic_code_identity'].items():
        consumed['tools/project_core/' + name] = value
    consumed['tools/scientific_helpers/sppr/method_coverage.py'] = context['adapter_sha256']
    result = {'unit_id': unit, 'model_id': original['model_id'], 'original_package': rel(directory),
              'original_preparation_sha256': ORIGINAL_PLANS[unit], 'consumed_inputs': consumed,
              'context': original['context'], 'expected_methods': original['expected_methods'],
              'promotions': promotions, 'ledger_sha256': sha(ledger_path), 'prepared_by': sha(SCRIPT)}
    if sha(SCRIPT) != SCRIPT_SHA256:
        raise ValueError('Coordinator source changed during preparation')
    write(out / 'preparation.json', result)
    return verify_package(unit)


def verify_package(unit, *, check_current_inputs=True, require_guard=False):
    from tools.project_core.calculations import coverage
    from tools.scientific_helpers.sppr.configuration import resolve_audited_configuration
    directory, staged_model, model, verifier, original = package(unit)
    out = RUN / 'outputs/retained' / unit
    plan = read(out / 'preparation.json')
    if plan['prepared_by'] != sha(SCRIPT):
        raise ValueError('Coordinator verifier changed since preparation')
    targets = {p['target'] for p in plan['promotions']}
    installed = all(fingerprint(ROOT / p['target']) == p['sha256'] for p in plan['promotions'])
    if check_current_inputs:
        for name, expected in plan['consumed_inputs'].items():
            if installed and name in targets:
                continue
            if fingerprint(ROOT / name) != expected:
                raise ValueError('Coordinator consumed input changed: ' + name)
    for item in plan['promotions']:
        if sha(ROOT / item['source']) != item['sha256']:
            raise ValueError('Coordinator promotion changed: ' + item['source'])
    manifest = read(out / 'result_manifest.json')
    ledger = read(out / 'retained_reuse.json')
    if sha(out / 'retained_reuse.json') != plan['ledger_sha256']:
        raise ValueError('Retained reconciliation ledger changed')
    if ledger['verification_source_sha256'] != SCRIPT_SHA256:
        raise ValueError('Retained ledger has a different verifier')
    original_manifest = read(staged_model / 'results/result_manifest.json')
    original_science, promoted_science = copy.deepcopy(original_manifest), copy.deepcopy(manifest)
    promoted_science.pop('retained_publication_reconciliation', None)
    promoted_science['method_coverage']['arithmetic_code_identity'] = original_science['method_coverage']['arithmetic_code_identity']
    if original_science != promoted_science:
        raise ValueError('Manifest change exceeded arithmetic compatibility metadata')
    arithmetic_compatibility(read(staged_model / 'results/result_manifest.json'))
    regional = directory / 'regional' / (unit + '.xlsx')
    identity_model = MODEL38 if unit == 'LME_038' else staged_model
    flags = resolve_audited_configuration(identity_model, coverage._settings_book(regional), manifest)
    context = coverage._context(ROOT, identity_model / 'model.json', flags)
    if not coverage._same_context(context, plan['context']):
        raise ValueError('Pinned numerical context changed')
    if not coverage._package_cache_valid(staged_model, regional, manifest, context, plan['expected_methods']):
        raise ValueError('Retained cache no longer valid')
    if unit == 'LME_049' and require_guard:
        verifier.base._guard_installed()
    write(RUN / 'qa' / (unit + '_retained_verification.json'), {
        'passed': True, 'installed': installed, 'promotions': len(plan['promotions']),
        'original_preparation_sha256': ORIGINAL_PLANS[unit], 'ledger_sha256': plan['ledger_sha256'],
        'scientific_solve_performed': False, 'numeric_artifacts_changed': False,
        'current_engine_equivalence_claimed': False, 'canonical_cache_valid': True})
    return plan


def apply(publication, unit):
    from tools.project_core.registry.publication import _ACTIVE, publication_write
    from tools.project_core.calculations import coverage
    if publication not in _ACTIVE.get() or publication.root != ROOT:
        raise ValueError('Active publication transaction required')
    lock = ROOT / '.project-write.lock'
    if not lock.is_file() or lock.read_text().strip() != str(os.getpid()):
        raise ValueError('Current process must hold Project writer lock')
    plan = verify_package(unit, require_guard=True)
    if all(fingerprint(ROOT / p['target']) == p['sha256'] for p in plan['promotions']):
        return {'status': 'already_applied', 'changed_units': [unit], 'written_paths': [], 'written_hashes': {}}
    for item in plan['promotions']:
        source, target = ROOT / item['source'], ROOT / item['target']
        with publication_write(target, fingerprint=item['sha256']):
            coverage._write_bytes(target, source.read_bytes(), expected_sha256=plan['consumed_inputs'][item['target']])
    directory, staged_model, model, verifier, original = package(unit)
    region = ROOT / next(p['target'] for p in plan['promotions'] if p['target'].endswith('/' + unit + '.xlsx'))
    manifest = read(model / 'results/result_manifest.json')
    if not coverage._package_cache_valid(model, region, manifest, plan['context'], plan['expected_methods']):
        raise ValueError('Installed retained cache failed')
    return {'status': 'applied', 'changed_units': [unit],
            'written_paths': [str(ROOT / p['target']) for p in plan['promotions']],
            'written_hashes': {str(ROOT / p['target']): p['sha256'] for p in plan['promotions']}}


def verify_all():
    return {unit: verify_package(unit, require_guard=True) for unit in UNITS}


def apply_all(publication):
    return {unit: apply(publication, unit) for unit in UNITS}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'verify'])
    parser.add_argument('--unit', choices=UNITS, required=True)
    args = parser.parse_args()
    result = prepare(args.unit) if args.command == 'prepare' else verify_package(args.unit, require_guard=True)
    print(json.dumps({'unit': args.unit, 'verified': True, 'promotions': len(result['promotions']), 'scientific_solve_performed': False}), flush=True)
