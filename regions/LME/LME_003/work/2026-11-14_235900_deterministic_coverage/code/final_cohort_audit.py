"""Authenticate the two-field CAL patch and audit all 16 retained/staged models.

No solver, constructor, Monte Carlo, publication or canonical workbook write is
called. --apply-cal-patch permits only the exact SHA-bound cache metadata patch.
The default mode verifies the already patched cache and writes the audit report.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(WORK / 'code'))
sys.path.insert(0, str(ROOT))

import adopt_completion as adoption
import provenance_admission as admission

PATCH_SHA = '007ae186e9acd02e174572c4e1a99dc8e02e583beabc6f0b06dff878517e15da'
BEFORE_SHA = '148e5788acae2882e7390a6583d5f050f51c669a6803642f958e1e66fec2021c'
VERIFICATION_SHA = '51f1772198d32f1d0e7dd21b3316829cb42b124c7c35a310a134b93c7f8492a2'
PATCH_FIELDS = {'runtime_verification_evidence', 'initialization_provenance_caveat'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def object_sha(value):
    # Annual table records mix integer year keys with text column names. Retain
    # those key types explicitly instead of sorting incomparable Python keys or
    # coercing 1950 and "1950" into the same JSON key.
    def typed_keys(item):
        if isinstance(item, dict):
            return {'mapping': sorted([[type(key).__name__, str(key), typed_keys(val)]
                                       for key, val in item.items()], key=lambda row: (row[0], row[1]))}
        if isinstance(item, (tuple, list)):
            return {type(item).__name__: [typed_keys(val) for val in item]}
        return item
    return hashlib.sha256(json.dumps(typed_keys(value), ensure_ascii=False, sort_keys=True,
                                    allow_nan=False, default=str).encode()).hexdigest()


def cache_bytes(value):
    # Match the existing cache serializer exactly, retaining CRLF and no EOF LF.
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).replace('\n', '\r\n').encode('utf-8')


def authenticate_patch(inventory, apply_patch):
    item = next(p for p in inventory['pairs'] if p['unit_id'] == 'LME_003')
    model = ROOT / item['model_dir'] / 'model.json'
    directory = model.parent / 'results/diagnostics/method_coverage' / adoption.RUN_ID / 'calculated'
    cache = directory / 'calculated.json'
    patch_path = WORK / 'outputs/california_v1_initialization_patches.json'
    require(adoption.sha(patch_path) == PATCH_SHA, 'CAL patch digest differs')
    patch = adoption.read(patch_path)
    require(patch['cache_sha256_before_patch'] == BEFORE_SHA, 'CAL baseline digest differs')
    require(set(patch['method_outcome_patches']) == set(admission.CAL_METHOD_HASHES), 'CAL patch method scope differs')
    require(patch['original_method_sha256'] == admission.CAL_METHOD_HASHES, 'Original CAL method pins differ')
    verification_path = adoption.reference(directory, patch['evidence'])
    require(adoption.sha(verification_path) == VERIFICATION_SHA, 'Retrospective evidence digest differs')
    verification = adoption.read(verification_path)
    require(verification['verification_identity'] == patch['verification_identity'], 'Verification identity differs')
    require(verification['runtime_sha256'] == patch['runtime_sha256'] == admission.CAL_RUNTIME_SHA256,
            'Runtime authentication digest differs')
    custody_path = directory / 'retrospective_v1/verification_sources/source_custody.json'
    custody = adoption.read(custody_path)
    require(set(custody['sources']) == {'verification_helper', 'verification_adapter'}, 'Source custody roles differ')
    protected = {patch_path: PATCH_SHA, verification_path: VERIFICATION_SHA,
                 custody_path: adoption.sha(custody_path)}
    source_records = {}
    for role, field in [('verification_helper', 'verification_helper_sha256'),
                        ('verification_adapter', 'adapter_sha256')]:
        ref = custody['sources'][role]
        path = adoption.reference(model.parent, ref)
        require(ref['sha256'] == verification['verification_identity'][field], 'Retrospective source custody differs: ' + role)
        protected[path] = ref['sha256']
        source_records[role] = {'path': relative(path), 'sha256': ref['sha256']}
    before = cache.read_bytes()
    current = json.loads(before)
    unpatched = copy.deepcopy(current)
    patch_already_present = all(PATCH_FIELDS <= set(current['methods'][key]) for key in admission.CAL_METHOD_HASHES)
    for key, fields in patch['method_outcome_patches'].items():
        require(set(fields) == PATCH_FIELDS, 'CAL patch field scope differs')
        require(fields['initialization_provenance_caveat'] == admission.LIMITATION, 'CAL caveat differs')
        for field in PATCH_FIELDS:
            if field in unpatched['methods'][key]:
                require(unpatched['methods'][key].pop(field) == fields[field], 'Existing CAL patch field differs')
    require(hashlib.sha256(cache_bytes(unpatched)).hexdigest() == BEFORE_SHA,
            'CAL cache contains changes beyond the exact supplied patch')
    expected = copy.deepcopy(unpatched)
    initialization = {}
    for key, fields in patch['method_outcome_patches'].items():
        expected['methods'][key].update(copy.deepcopy(fields))
        verified = adoption.verify_method(model, directory, key, expected['methods'][key])
        require(verified['initialization']['evidence_kind'] == admission.KIND, 'CAL evidence kind differs')
        protected.update(verified['consumed'])
        original_constructor = adoption.read(verified['constructor_path'])
        require(original_constructor['constructor_outcome']['status'] == 'constructor_failed',
                'Historical failed constructor must remain failed')
        initialization[key] = {'method_sha256': adoption.sha(verified['method_path']),
                               'constructor_sha256': adoption.sha(verified['constructor_path']),
                               'constructor_status': 'constructor_failed',
                               'evidence_kind': verified['initialization']['evidence_kind']}
    expected_bytes = cache_bytes(expected)
    expected_sha = hashlib.sha256(expected_bytes).hexdigest()
    if patch_already_present:
        require(current == expected and adoption.sha(cache) == expected_sha, 'Patched CAL cache differs')
    else:
        require(adoption.sha(cache) == BEFORE_SHA and current == unpatched, 'CAL cache baseline changed')
        require(apply_patch, 'CAL cache patch remains unapplied; pass --apply-cal-patch')
        adoption.check_hashes(protected)
        require(cache.read_bytes() == before, 'CAL cache changed before bounded metadata write')
        cache.write_bytes(expected_bytes)
    require(adoption.sha(cache) == expected_sha, 'CAL patch write did not verify')
    adoption.check_hashes(protected)
    return {'cache_path': relative(cache), 'before_sha256': BEFORE_SHA, 'after_sha256': expected_sha,
            'patch_sha256': PATCH_SHA, 'verification_evidence_sha256': VERIFICATION_SHA,
            'patch_applied_this_run': not patch_already_present, 'methods': initialization,
            'changed_fields_per_method': sorted(PATCH_FIELDS), 'source_custody': source_records,
            'original_evidence_unchanged': True, 'limitation': admission.LIMITATION}, protected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply-cal-patch', action='store_true')
    args = parser.parse_args()
    inventory_path = WORK / 'inputs/validated_inventory.json'
    inventory = adoption.read(inventory_path)
    implementation = {Path(path).resolve(): adoption.sha(path) for path in
                      (__file__, adoption.__file__, admission.__file__)}
    patch_report, patch_protected = authenticate_patch(inventory, args.apply_cal_patch)
    initial_cache_hashes = {}
    for item in inventory['pairs']:
        if item['pending_non_mc_methods']:
            path = ROOT / item['model_dir'] / 'results/diagnostics/method_coverage' / adoption.RUN_ID / 'calculated/calculated.json'
            initial_cache_hashes[path.resolve()] = adoption.sha(path)
    print('CAL metadata authenticated; starting no-solver all16 preflight', flush=True)
    plans, consumed, immutable, central = adoption.prepare()
    require(len(plans) == 16, 'Expected exactly 16 validated pairs')
    require(len(inventory['canonical_non_mc_methods']) == 20, 'Expected exactly 20 deterministic methods')
    by_pair = {(p['unit_id'], p['model_id']): p for p in inventory['pairs']}
    counts = {'total': 0, 'finite_including_flagged': 0, 'finite_flagged_subset': 0,
              'finite_with_any_scope_restriction': 0,
              'unsupported_formulation': 0, 'scientifically_unavailable': 0}
    initialization_counts = {}
    reports, restrictions, cache_hashes = [], [], {}
    for plan in plans:
        pair = plan['pair']
        item = by_pair[pair]
        require(adoption.sha(plan['manifest']) == item['manifest']['sha256'], 'Original manifest changed: ' + str(pair))
        staged = {k: v for batch in plan['batches'] for k, v in batch.verified.items()}
        methods = []
        for key in inventory['canonical_non_mc_methods']:
            counts['total'] += 1
            outcome = staged[key]['outcome'] if key in staged else plan['original_method_records'].get(key, {})
            if key in staged:
                values = {scope: list(groups.values()) for scope, groups in outcome.get('scopes', {}).items()}
                init = staged[key]['initialization']['evidence_kind']
                initialization_counts[init] = initialization_counts.get(init, 0) + 1
            else:
                values = {}
                for row in plan['protected']['coefficients'].get(key, []):
                    values.setdefault(row[2], []).append(row[4])
                init = 'retained_saved_coefficients; no new initialization admission required'
            finite_counts = {scope: sum(adoption.finite(v) for v in values) for scope, values in values.items()}
            has_finite = any(finite_counts.values())
            status_by_scope = outcome.get('annual_status', {})
            if not status_by_scope:
                for row in plan['protected']['dependent']['PPR/Annual']:
                    if row.get('method') == key:
                        status_by_scope[row.get('scope')] = row.get('status')
            restricted = any(status != 'ok' and finite_counts.get(scope, 0) > 0
                             for scope, status in status_by_scope.items())
            if has_finite:
                classification = 'finite_flagged' if restricted else 'finite'
                counts['finite_including_flagged'] += 1
                counts['finite_flagged_subset'] += int(restricted)
                counts['finite_with_any_scope_restriction'] += int(any(status != 'ok' for status in status_by_scope.values()))
            else:
                reason = outcome.get('reason', '')
                if pair[0] in {'LME_014', 'LME_022'} and 'NotImplementedError:' in reason and 'source-backed discard returns' in reason:
                    classification = 'unsupported_formulation'
                elif pair[0] == 'LME_013' and key == 'sym_TE_asDC' and 'b=5.4380 >= 1' in reason:
                    classification = 'scientifically_unavailable'
                elif pair[0] == 'LME_013' and key == 'sym_WithEgestion_asDC' and 'unrepresented nonzero recipient weights: [40]' in reason:
                    classification = 'scientifically_unavailable'
                else:
                    raise ValueError('Unexpected unavailable deterministic slot: ' + str(pair) + '/' + key + ': ' + reason)
                counts[classification] += 1
                restrictions.append({'unit_id': pair[0], 'model_id': pair[1], 'method': key,
                                     'classification': classification, 'execution_status': outcome.get('status'), 'reason': reason})
            methods.append({'method': key, 'origin': 'staged' if key in staged else 'retained',
                            'classification': classification, 'execution_status': outcome.get('status'),
                            'finite_group_counts_by_scope': finite_counts,
                            'annual_status': status_by_scope, 'initialization': init})
        fixed = next(m for m in methods if m['method'] == 'SPPR_1995_TE0.1')
        require(all(fixed['finite_group_counts_by_scope'].get(s, 0) > 0 for s in ('all', 'inner')),
                'Fixed 1995 missing a finite scope: ' + str(pair))
        require(fixed['finite_group_counts_by_scope'].get('PP', 0) == 0,
                'Fixed 1995 unsupported PP scope must remain unavailable: ' + str(pair))
        mc = {}
        for key, outcome in plan['original_method_records'].items():
            if not key.startswith('MC_'):
                continue
            ref = outcome.get('evidence')
            record = {'outcome_sha256': object_sha(outcome), 'group_rows_sha256': plan['original_row_hashes'].get(key)}
            if ref:
                path = adoption.reference(plan['model'].parent / 'results/diagnostics', ref)
                patch_protected[path] = adoption.sha(path)
                record.update({'evidence_path': relative(path), 'evidence_sha256': adoption.sha(path)})
            mc[key] = record
        if plan['batches']:
            path = plan['batches'][0].cache_path
            cache_hashes[relative(path)] = {'before_audit_sha256': initial_cache_hashes[path.resolve()],
                                           'after_audit_sha256': adoption.sha(path)}
        reports.append({'unit_id': pair[0], 'model_id': pair[1], 'selected': item['registry_selected'],
                        'model_sha256': adoption.sha(plan['model']), 'manifest_sha256': adoption.sha(plan['manifest']),
                        'coefficient_source_sha256': adoption.sha(plan['source']), 'workbook_sha256': adoption.sha(plan['workbook']),
                        'protected_workbook_projection_sha256': object_sha(plan['protected']),
                        'protected_source_projection_sha256': object_sha(plan['source_protected']),
                        'review_sha256': plan['metadata']['validation_report_sha256'],
                        'mc': mc, 'mc_absent': not mc, 'methods': methods})
    require(counts['total'] == 320 and counts['finite_including_flagged'] == 294
            and counts['unsupported_formulation'] == 24 and counts['scientifically_unavailable'] == 2,
            'Final cohort counts differ from the expected science scope: ' + str(counts))
    adoption.check_hashes(consumed)
    adoption.check_hashes(immutable)
    adoption.check_hashes(patch_protected)
    adoption.check_hashes(initial_cache_hashes)
    adoption.check_hashes(implementation)
    all_protected = {**consumed, **immutable, **patch_protected}
    report = {'schema_version': 1, 'status': 'PASS_PRE_PUBLICATION',
              'timestamp': datetime.now(timezone.utc).isoformat(),
              'scientific_execution_performed': False, 'publication_performed': False,
              'audit_helper_sha256': adoption.sha(__file__), 'inventory_sha256': adoption.sha(inventory_path),
              'audit_implementation_sha256': {relative(p): digest for p, digest in implementation.items()},
              'california_metadata_patch': patch_report, 'counts': counts,
              'sppr_1995_te01_all16_finite': True,
              'sppr_1995_te01_scopes': {'all': 'finite for all16', 'inner': 'finite for all16',
                                       'PP': 'unsupported source scope remains unavailable for all16'},
              'count_definitions': {'finite_including_flagged': 'At least one finite saved coefficient in a supported scope; no validity claim.',
                                    'finite_flagged_subset': 'At least one finite scope has an annual status other than ok.',
                                    'finite_with_any_scope_restriction': 'Any scope has an annual status other than ok, including unsupported empty scopes.'},
              'staged_initialization_admission_counts': initialization_counts,
              'monte_carlo': {'existing_evidence_files_verified': sum(len(p['mc']) for p in reports),
                              'absence_preserved_for_units': [p['unit_id'] for p in reports if p['mc_absent']],
                              'draws_rerun': False},
              'cache_hashes': cache_hashes, 'restrictions': restrictions, 'pairs': reports,
              'protected_files': {relative(p): digest for p, digest in sorted(all_protected.items(), key=lambda x: str(x[0]))},
              'protected_files_verified': len(all_protected), 'central_human_metadata_sha256': object_sha(central),
              'checks': ['Canonical discovery, exact validated cohort, source model and registered review identities',
                         'All staged immutable method summaries/settings/returns and replay/engine/initialization references',
                         'Exact original manifest and source/snapshot hashes; protected scientific inputs and retained coefficients',
                         'Original MC evidence bytes and absence retained; no new Monte Carlo or deterministic solve',
                         'All 26 unsupported/scientific restrictions retained; finite flagged values remain flagged',
                         'Only two supplied metadata fields added to each of two CAL outcome summaries'],
              'limitations': [adoption.ADAPTER_CAVEAT, admission.LIMITATION,
                             'This is a pre-publication cache and preservation audit. It does not establish new scientific eligibility or approve any result.']}
    output = WORK / 'outputs/final_cohort_audit.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    require(adoption.read(output) == report, 'Written final audit report differs')
    print(json.dumps({'report': relative(output), 'sha256': adoption.sha(output), 'counts': counts,
                      'initialization': initialization_counts, 'protected_files_verified': len(all_protected),
                      'cal_cache_after_sha256': patch_report['after_sha256']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
