"""Run California's unavailable symbolic methods into an isolated v2 cache.

Scientific attempts write isolated stages only. The separately authorized
--merge-main operation freezes the original cache, preserves finite methods, and
atomically adopts authenticated stages. Published workbooks and the shared WORK
calculation summary are never written. Existing evidence is never overwritten.
"""
from __future__ import annotations

import copy
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path

for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
              'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS'):
    os.environ[_name] = '1'

# Passive stack snapshots in the spawned scientific worker. The authenticated
# adapter and calculator bytes, method arguments, and runtime remain unchanged.
if __name__ == '__mp_main__' and os.environ.get('CAL_SYMBOLIC_PROFILE_DIR'):
    import sys
    import threading
    import time
    import traceback
    _profile_path = Path(os.environ['CAL_SYMBOLIC_PROFILE_DIR']) / ('worker-' + str(os.getpid()) + '.stacks.txt')
    _main_ident = threading.main_thread().ident

    def _sample_python_stack():
        while True:
            time.sleep(60)
            frame = sys._current_frames().get(_main_ident)
            if frame is not None:
                with _profile_path.open('a', encoding='utf-8') as output:
                    output.write('\nUTC ' + datetime.now(timezone.utc).isoformat() + '\n')
                    output.writelines(traceback.format_stack(frame))
    threading.Thread(target=_sample_python_stack, daemon=True, name='passive-python-stack-sampler').start()

from run_completion import (ROOT, WORK, RUN_ID, adapter, sha, read, save,
                            replay_flags, repaired_flags, authenticate_methods)
from adopt_completion import check_control_settings


def has_finite(outcome):
    return any(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
               for values in outcome.get('scopes', {}).values() for value in values.values())


def unchanged(hashes):
    for path, fingerprint in hashes.items():
        if not path.is_file() or sha(path) != fingerprint:
            raise ValueError('Protected scientific evidence changed: ' + str(path))


def summary(result, path):
    return {'unit_id': 'LME_003', 'staged_cache': path.relative_to(ROOT).as_posix(),
            'main_cache_written': False,
            'methods': {key: {'status': outcome['status'], 'reason': outcome.get('reason'),
                              'finite_scoped_coefficients': sum(isinstance(value, (int, float)) and
                                  not isinstance(value, bool) and math.isfinite(value)
                                  for values in outcome.get('scopes', {}).values() for value in values.values())}
                        for key, outcome in result['methods'].items()}}


def merge_staged_in_memory(item, main_result, staged_result, main_directory, stage_directory):
    """Authenticate and return a merged value; deliberately performs no write."""
    main_result = authenticate_methods(item, copy.deepcopy(main_result), main_directory)
    staged_result = authenticate_methods(item, copy.deepcopy(staged_result), stage_directory)
    for key, outcome in staged_result['methods'].items():
        if not key.startswith('sym_'):
            raise ValueError('Staged merge contains a nonsymbolic method')
        current = main_result['methods'].get(key, {})
        if current.get('status') == 'ok' or has_finite(current):
            raise ValueError('Staged merge would replace an available method: ' + key)
        for name in ('evidence', 'constructor_evidence'):
            outcome[name]['path'] = (stage_directory/outcome[name]['path']).relative_to(main_directory).as_posix()
        main_result['methods'][key] = outcome
    return authenticate_methods(item, main_result, main_directory)


def initial_main():
    inventory = read(WORK/'inputs/validated_inventory.json')
    item = next(item for item in inventory['pairs'] if item['unit_id'] == 'LME_003')
    model_dir = ROOT/item['model_dir']
    model = model_dir/'model.json'
    run = model_dir/'results/diagnostics/method_coverage'/RUN_ID
    main_directory = run/'calculated'
    main_cache = main_directory/'calculated.json'
    stage_directory = main_directory/'symbolic_v2'
    staged_cache = stage_directory/'staged_calculated.json'
    if staged_cache.is_file():
        result = authenticate_methods(item, read(staged_cache), stage_directory)
        print(json.dumps(summary(result, staged_cache), indent=2), flush=True)
        return
    if stage_directory.exists() and any(stage_directory.iterdir()):
        raise ValueError('An incomplete v2 attempt already exists; retain it and choose an explicitly new attempt')
    cache_bytes = main_cache.read_bytes()
    cache_hash = __import__('hashlib').sha256(cache_bytes).hexdigest()
    cached = authenticate_methods(item, json.loads(cache_bytes), main_directory)
    symbolic = [key for key in inventory['canonical_non_mc_methods'] if key.startswith('sym_')]
    pending = [key for key in symbolic if cached['methods'].get(key, {}).get('status') != 'ok'
               and not has_finite(cached['methods'].get(key, {}))]
    control_path = run/'controls/verification.json'
    control = read(control_path)
    flags = replay_flags(item)
    if (not control.get('passed') or control['identity']['model_sha256'] != sha(model)
            or control['identity']['source_sha256'] != sha(model_dir/'sppr_source.xlsx')
            or control['identity']['engine_identity'] != adapter.engine_identity(flags, model)):
        raise ValueError('California retained GE/TE control does not authenticate this model/source/base engine')
    check_control_settings(control['identity']['flags'], flags)
    protected = {model: sha(model), model_dir/'sppr_source.xlsx': sha(model_dir/'sppr_source.xlsx'),
                 control_path: sha(control_path)}
    for outcome in cached['methods'].values():
        for name in ('evidence', 'constructor_evidence'):
            reference = outcome.get(name)
            if reference:
                path = (main_directory/reference['path']).resolve()
                if not path.is_relative_to(main_directory.resolve()):
                    raise ValueError('Existing evidence reference escaped the calculation directory')
                protected[path] = reference['sha256']
    if not pending:
        print(json.dumps({'unit_id': 'LME_003', 'pending': [], 'main_cache_written': False}), flush=True)
        return
    flags['method_timeout_seconds'] = 300
    flags['method_timeout_overrides_seconds'] = {
        **flags.get('method_timeout_overrides_seconds', {}), **{key: 300 for key in pending}}
    flags = repaired_flags(item, flags, repair='symbolic_repairs_v2')
    check_control_settings(control['identity']['flags'], flags)
    unchanged(protected)
    stage_directory.mkdir(parents=True, exist_ok=False)
    save(stage_directory/'selection_snapshot.json', {
        'timestamp': datetime.now(timezone.utc).isoformat(), 'model_id': item['model_id'],
        'source_cache_sha256_at_selection': cache_hash,
        'requested_methods': pending,
        'preserved_available_symbolic_methods': [key for key in symbolic if key not in pending],
        'prior_symbolic_outcomes': {key: cached['methods'].get(key) for key in symbolic},
        'main_cache_is_concurrently_owned_by_parent': True})
    print('California isolated symbolic v2: ' + ', '.join(pending), flush=True)
    result = adapter.compute_methods(model, flags, pending, stage_directory,
        progress=lambda message: print(message, flush=True), method_timeout=300)
    result = authenticate_methods(item, result, stage_directory)
    unchanged(protected)
    save(staged_cache, result)
    # Reopen and authenticate the persisted stage, never the concurrently changing main cache.
    verified = authenticate_methods(item, read(staged_cache), stage_directory)
    print(json.dumps(summary(verified, staged_cache), indent=2), flush=True)


def validated_context():
    inventory = read(WORK/'inputs/validated_inventory.json')
    item = next(value for value in inventory['pairs'] if value['unit_id'] == 'LME_003')
    model = ROOT/item['model_dir']/'model.json'
    run = model.parent/'results/diagnostics/method_coverage'/RUN_ID
    control_path = run/'controls/verification.json'
    control = read(control_path)
    flags = replay_flags(item)
    if (not control.get('passed') or control['identity']['model_sha256'] != sha(model)
            or control['identity']['source_sha256'] != sha(model.parent/'sppr_source.xlsx')
            or control['identity']['engine_identity'] != adapter.engine_identity(flags, model)):
        raise ValueError('California GE/TE control does not authenticate this model/source/base engine')
    check_control_settings(control['identity']['flags'], flags)
    protected = {p: sha(p) for p in (model, model.parent/'sppr_source.xlsx', control_path)}
    original = run/'calculated/symbolic_v2'
    protected.update({p: sha(p) for p in original.glob('*.gz')})
    return item, model, run, flags, protected


def recover_completed():
    item, model, run, _, protected = validated_context()
    directory = run/'calculated/symbolic_v2'
    target = directory/'staged_calculated.json'
    if target.is_file():
        recovered = authenticate_methods(item, read(target), directory)
        print(json.dumps(summary(recovered, target), indent=2), flush=True)
        return
    constructor_path = directory/'constructor.json.gz'
    constructor = read(constructor_path)
    if constructor['constructor_outcome']['status'] != 'ready':
        raise ValueError('Interrupted stage has no ready constructor to recover')
    identity = constructor['identity']
    runtime_hash = adapter._hash_bytes(adapter._json_bytes(constructor['constructor_outcome']['runtime']))
    constructor_ref = {'path': constructor_path.name, 'sha256': sha(constructor_path), 'availability': 'present'}
    result = {**copy.deepcopy(identity), 'methods': {}, 'groups': constructor['constructor_outcome']['groups'],
              'diagnostic_rows': [], 'constructor_evidence': constructor_ref}
    fields = ('status', 'reason', 'scopes', 'annual_status', 'diagnostics', 'mc_diagnostics',
              'negative_entries', 'reconciliation', 'elapsed_seconds', 'warnings', 'exception',
              'timeout_seconds', 'runtime_before_sha256', 'runtime_after_sha256', 'settings')
    for path in sorted(directory.glob('sym_*.json.gz')):
        document = read(path)
        key = document['settings']['method']
        if document['identity'] != identity:
            raise ValueError('Recovered method differs from retained constructor identity: ' + key)
        if document.get('runtime_before_sha256', runtime_hash) != runtime_hash:
            raise ValueError('Recovered method differs from retained constructor runtime: ' + key)
        outcome = {key: copy.deepcopy(document[key]) for key in fields if key in document}
        outcome['evidence'] = {'path': path.name, 'sha256': sha(path), 'availability': 'present'}
        outcome['constructor_evidence'] = copy.deepcopy(constructor_ref)
        result['methods'][key] = outcome
        if outcome.get('diagnostics'):
            result['diagnostic_rows'].append({'method': key, **outcome['diagnostics']})
    result = authenticate_methods(item, result, directory)
    unchanged(protected)
    save(target, result)
    save(directory/'recovery_provenance.json', {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'reason': 'Reconstructed summary from immutable completed returns after user-requested interruption',
        'constructor_identity_matches_every_method': True,
        'constructor_runtime_matches_every_available_method': True,
        'method_evidence': {key: outcome['evidence'] for key, outcome in result['methods'].items()},
        'original_evidence_changed': False})
    print(json.dumps(summary(result, target), indent=2), flush=True)


def run_resumed_method(key, budget, attempt=''):
    if key not in ('sym_TE_asDC', 'sym_WithEgestion_asDC') or not 0 < budget <= 1200:
        raise ValueError('Resume scope is limited to the two unavailable methods and <=1200 seconds')
    item, model, run, flags, protected = validated_context()
    if attempt and not attempt.replace('_', '').isalnum():
        raise ValueError('Attempt name must contain only letters, digits, or underscores')
    directory = run/'calculated/symbolic_v2'/('resume_' + key + '_' + str(budget) + ('_' + attempt if attempt else ''))
    target = directory/'staged_calculated.json'
    if target.is_file():
        result = authenticate_methods(item, read(target), directory)
        print(json.dumps(summary(result, target), indent=2), flush=True)
        return
    if directory.exists():
        raise ValueError('A resumed attempt already exists; preserve it and choose a new explicit attempt')
    for cache in (run/'calculated/calculated.json', run/'calculated/symbolic_v2/staged_calculated.json'):
        if cache.is_file():
            current = read(cache).get('methods', {}).get(key, {})
            if current.get('status') == 'ok' or has_finite(current):
                raise ValueError('Refuse to rerun an already available method: ' + key)
    flags['method_timeout_seconds'] = budget
    flags['method_timeout_overrides_seconds'] = {**flags.get('method_timeout_overrides_seconds', {}), key: budget}
    flags = repaired_flags(item, flags, repair='symbolic_repairs_v2')
    check_control_settings(read(run/'controls/verification.json')['identity']['flags'], flags)
    directory.mkdir(parents=True, exist_ok=False)
    if key == 'sym_TE_asDC':
        os.environ['CAL_SYMBOLIC_PROFILE_DIR'] = str(directory.resolve())
    else:
        os.environ.pop('CAL_SYMBOLIC_PROFILE_DIR', None)
    print('California resumed ' + key + ', budget ' + str(budget) + ' seconds; Python stack sampling ' +
          ('enabled' if key == 'sym_TE_asDC' else 'disabled'), flush=True)
    result = adapter.compute_methods(model, flags, [key], directory,
        progress=lambda message: print(message, flush=True), method_timeout=budget)
    result = authenticate_methods(item, result, directory)
    unchanged(protected)
    save(target, result)
    print(json.dumps(summary(authenticate_methods(item, read(target), directory), target), indent=2), flush=True)


def combine_completed(*, merge_main=False):
    inventory = read(WORK/'inputs/validated_inventory.json')
    item = next(value for value in inventory['pairs'] if value['unit_id'] == 'LME_003')
    model = ROOT/item['model_dir']/'model.json'
    directory = model.parent/'results/diagnostics/method_coverage'/RUN_ID/'calculated'
    stage = directory/'symbolic_v2'
    main_path = directory/'calculated.json'
    original_bytes = main_path.read_bytes()
    original_hash = __import__('hashlib').sha256(original_bytes).hexdigest()
    original = json.loads(original_bytes)
    protected = {p: sha(p) for p in (model, model.parent/'sppr_source.xlsx',
                                    directory.parent/'controls/verification.json')}
    combined = authenticate_methods(item, read(stage/'staged_calculated.json'), stage)
    for key, budget in (('sym_TE_asDC', 1200), ('sym_WithEgestion_asDC', 600)):
        attempt = stage/('resume_' + key + '_' + str(budget) + '_python_safe')
        result = authenticate_methods(item, read(attempt/'staged_calculated.json'), attempt)
        if set(result['methods']) != {key} or not has_finite(result['methods'][key]):
            raise ValueError('Final stage has no finite attained result: ' + key)
        combined = merge_staged_in_memory(item, combined, result, stage, attempt)
    combined['mixed_execution_contexts'] = True
    combined['diagnostic_rows'] = [{'method': key, **outcome['diagnostics']}
        for key, outcome in combined['methods'].items() if outcome.get('diagnostics')]
    target = stage/'combined_staged_calculated.json'
    if target.exists() and read(target) != combined:
        raise ValueError('Existing combined stage differs; preserve it')
    if not target.exists():
        save(target, combined)
    authenticate_methods(item, read(target), stage)
    if not merge_main:
        print(json.dumps(summary(combined, target), indent=2), flush=True)
        return
    merged = merge_staged_in_memory(item, original, combined, directory, stage)
    # Exact original records for all other methods must survive the merge,
    # including the v1 constructor references that another reviewer is auditing.
    changed = set(combined['methods'])
    for key, outcome in original['methods'].items():
        if key not in changed and merged['methods'][key] != outcome:
            raise ValueError('Merge changed an untouched method record: ' + key)
        if key in changed and (outcome.get('status') == 'ok' or has_finite(outcome)):
            raise ValueError('Merge would change a finite/ok prior method: ' + key)
    merged['mixed_execution_contexts'] = True
    merged['diagnostic_rows'] = [{'method': key, **outcome['diagnostics']}
        for key, outcome in merged['methods'].items() if outcome.get('diagnostics')]
    unchanged(protected)
    if main_path.read_bytes() != original_bytes:
        raise ValueError('Main cache changed concurrently; refuse write')
    backup = directory/('calculated_before_final_symbolic_merge_' + original_hash[:16] + '.json')
    if backup.exists() and backup.read_bytes() != original_bytes:
        raise ValueError('Original-cache backup name is occupied by different bytes')
    if not backup.exists():
        backup.write_bytes(original_bytes)
    if sha(backup) != original_hash:
        raise ValueError('Original-cache backup failed authentication')
    candidate = directory/('calculated.final_symbolic_merge_candidate_' + original_hash[:16] + '.json')
    save(candidate, merged)
    if authenticate_methods(item, read(candidate), directory) != merged:
        raise ValueError('Merged cache candidate failed authentication')
    candidate_bytes = candidate.read_bytes()
    unchanged(protected)
    if main_path.read_bytes() != original_bytes:
        raise ValueError('Main cache changed concurrently before replacement')
    candidate.replace(main_path)
    try:
        persisted = authenticate_methods(item, read(main_path), directory)
        if persisted != merged:
            raise ValueError('Merged cache failed persisted authentication')
        unchanged(protected)
    except Exception:
        if main_path.read_bytes() == candidate_bytes:
            candidate.write_bytes(original_bytes)
            candidate.replace(main_path)
        raise
    report = {'unit_id': 'LME_003', 'main_cache_written': True,
        'prior_cache': {'path': backup.relative_to(ROOT).as_posix(), 'sha256': original_hash},
        'cache': {'path': main_path.relative_to(ROOT).as_posix(), 'sha256': sha(main_path)},
        'combined_stage': {'path': target.relative_to(ROOT).as_posix(), 'sha256': sha(target)},
        'updated_methods': sorted(changed),
        'untouched_method_records_preserved_exactly': len(original['methods']) - len(changed),
        'method_count': len(persisted['methods']),
        'statuses': {key: value['status'] for key, value in persisted['methods'].items()},
        'outcome_summary': summary(combined, target)['methods'],
        'published_workbooks_changed': False,
        'v1_constructor_provenance_review_pending': ['sym_TE_asPP', 'sym_GE_asPP']}
    save(stage/'final_merge_report.json', report)
    print(json.dumps(report, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recover', action='store_true')
    parser.add_argument('--method', choices=('sym_TE_asDC', 'sym_WithEgestion_asDC'))
    parser.add_argument('--budget', type=int, default=600)
    parser.add_argument('--attempt', default='')
    parser.add_argument('--combine', action='store_true')
    parser.add_argument('--merge-main', action='store_true')
    args = parser.parse_args()
    if args.combine or args.merge_main:
        combine_completed(merge_main=args.merge_main)
    elif args.recover:
        recover_completed()
    elif args.method:
        run_resumed_method(args.method, args.budget, args.attempt)
    else:
        initial_main()


if __name__ == '__main__':
    main()
