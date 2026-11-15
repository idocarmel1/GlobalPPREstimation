"""Exercise all actual source updates on owned copies, without scientific solves.

This is a source-export integration preflight, not a full regional calculation
or publication. It uses the same ordered cache batches and source replacement
sets as the coordinator; every original source projection remains strict.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time
import traceback
from unittest.mock import patch

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(WORK / 'code'))
import adopt_completion as adopter
from tools.project_core.calculations import coverage
from tools.project_core.workbooks.workbooks import read_book, overview
from tools.scientific_helpers.sppr import method_coverage as adapter


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def no_solver(*args, **kwargs):
    raise AssertionError('A scientific solver/runtime constructor was called by source-only preflight')


def untouched_source_sheets(path):
    """Include empty sheets and distinguish numeric/bool types exactly."""
    import openpyxl
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
    try:
        return {name: [[(type(value).__name__, repr(value)) for value in row]
                       for row in workbook[name].values]
                for name in workbook.sheetnames
                if not name.startswith('sppr_')
                and name not in ('model_health', 'method_coverage', 'run_notes')}
    finally:
        workbook.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--coverage-sha', required=True)
    args = parser.parse_args()
    coverage_path = ROOT / 'tools/project_core/calculations/coverage.py'
    if sha(coverage_path) != args.coverage_sha:
        raise ValueError('Source fix is not the requested frozen coverage version')
    inventory_path = WORK / 'inputs/validated_inventory.json'
    items = [item for item in read(inventory_path)['pairs'] if item['pending_non_mc_methods']]
    if len(items) != 11:
        raise ValueError('Expected the eleven explicit cached-method update pairs')
    run = Path(tempfile.mkdtemp(prefix='all-source-projection-', dir=WORK / 'tmp')).resolve()
    if not run.is_relative_to((WORK / 'tmp').resolve()):
        raise ValueError('Owned preflight copies escaped WORK/tmp')
    consumed = {inventory_path: sha(inventory_path), coverage_path: args.coverage_sha,
                Path(adopter.__file__): sha(Path(adopter.__file__))}
    results = []
    report = {'schema_version': 1, 'started_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Eleven source workbook copies; exact cache batch order, no regional arithmetic or publication',
              'scientific_solver_called': False, 'canonical_writes': False,
              'coverage_sha256': args.coverage_sha, 'temporary_directory': relative(run), 'pairs': results}
    with patch.object(adapter, 'compute_methods', no_solver), patch.object(adapter, '_run', no_solver), \
            patch.object(adapter, '_load', no_solver), patch.object(coverage, '_arithmetic', no_solver):
        for item in items:
            began = time.monotonic()
            unit, model_id = item['unit_id'], item['model_id']
            print(unit + ': source-only cached-batch projection preflight', flush=True)
            result = {'unit_id': unit, 'model_id': model_id, 'status': 'RUNNING', 'batches': []}
            results.append(result)
            try:
                model_dir = ROOT / item['model_dir']
                source = model_dir / 'sppr_source.xlsx'
                manifest_path = model_dir / 'results/result_manifest.json'
                region = model_dir
                while region.name != unit:
                    if region == ROOT:
                        raise ValueError('Cannot locate exact regional workbook')
                    region = region.parent
                regional = region / (unit + '.xlsx')
                local = read_book(regional)
                current = all(overview(local).get(key) == model_id for key in ('selected_model_id', 'results_model_id'))
                workbook = regional if current else model_dir / 'results/regional_snapshot.xlsx'
                original_book = local if current else read_book(workbook)
                book = copy.deepcopy(original_book)
                cache_path = model_dir / 'results/diagnostics/method_coverage/deterministic_completion_20261114/calculated/calculated.json'
                for p in (source, manifest_path, workbook, cache_path):
                    consumed[p] = sha(p)
                cached = read(cache_path)
                manifest = read(manifest_path)
                wanted = list(item['pending_non_mc_methods'])
                baseline_book = adopter.protected_book(original_book)
                retained = set(baseline_book['retained_methods'])
                if retained.intersection(wanted) or any(k.startswith('MC_') for k in wanted):
                    raise ValueError('Preflight scope overlaps protected finite/MC methods')
                baseline_source = adopter.source_state(source, retained)
                baseline_untouched = untouched_source_sheets(source)
                groups = {}
                for key in wanted:
                    outcome = cached['methods'][key]
                    constructor = adopter.reference(cache_path.parent, outcome['constructor_evidence'])
                    initialization = adopter.reference(cache_path.parent,
                        outcome.get('runtime_verification_evidence', outcome['constructor_evidence']))
                    identity_key = (json.dumps(outcome['execution_identity'], sort_keys=True)
                                    + str(constructor) + sha(constructor)
                                    + str(initialization) + sha(initialization))
                    groups.setdefault(identity_key, {})[key] = copy.deepcopy(outcome)
                    consumed[constructor] = sha(constructor)
                    consumed[initialization] = sha(initialization)
                target_dir = run / unit / model_id
                target_dir.mkdir(parents=True)
                target = target_dir / 'sppr_source.xlsx'
                shutil.copyfile(source, target)
                outcomes = copy.deepcopy(manifest.get('method_coverage', {}).get('methods', {}))
                result.update(source=relative(source), source_sha256=sha(source),
                              workbook=relative(workbook), cache=relative(cache_path),
                              retained_methods=sorted(retained), copy=relative(target),
                              untouched_source_sheets=list(baseline_untouched))
                for number, batch in enumerate(groups.values(), 1):
                    keys = list(batch)
                    saved_rows = coverage._method_rows(book)[0]
                    outcomes.update(copy.deepcopy(batch))
                    coverage._apply_outcomes(book, model_id, outcomes, keys, retried_methods=set(keys))
                    # Same replacement set as non-migration _complete_model.
                    replacements = set(keys).intersection(saved_rows)
                    before_source = sha(target)
                    coverage._update_source(target, book, outcomes,
                        replace_methods=replacements, expected_sha256=before_source)
                    batch_result = {'number': number, 'methods': keys,
                                    'replace_methods': sorted(replacements),
                                    'source_sha256': sha(target), 'status': 'PASS'}
                    result['batches'].append(batch_result)
                    checks = [
                        ('original_source_projection', lambda: adopter.unchanged_projection(
                            baseline_source, adopter.source_state(target, retained), unit + '/source')),
                        ('retained_in_memory_book_projection', lambda: adopter.unchanged_projection(
                            baseline_book, adopter.protected_book(book, retained), unit + '/book')),
                    ]
                    for label, check in checks:
                        try:
                            check()
                            batch_result[label] = 'PASS'
                        except Exception as error:
                            batch_result[label] = str(error)
                            batch_result['status'] = 'FAIL'
                    current_untouched = untouched_source_sheets(target)
                    differences = [name for name in sorted(set(baseline_untouched) | set(current_untouched))
                                   if baseline_untouched.get(name) != current_untouched.get(name)]
                    batch_result['untouched_sheets_exact_typed_values'] = 'PASS' if not differences else differences
                    if differences:
                        batch_result['status'] = 'FAIL'
                    if not coverage._source_matches(target_dir, book, keys):
                        batch_result['source_matches_current_methods'] = 'FAIL'
                        batch_result['status'] = 'FAIL'
                    else:
                        batch_result['source_matches_current_methods'] = 'PASS'
                    print(unit + ': batch ' + str(number) + ' ' + batch_result['status'], flush=True)
                result['status'] = 'PASS' if all(b['status'] == 'PASS' for b in result['batches']) else 'FAIL'
            except Exception as error:
                result.update(status='FAIL', error=str(error), traceback=traceback.format_exc())
                print(unit + ': FAIL ' + str(error), flush=True)
            result['seconds'] = round(time.monotonic() - began, 3)
    report['consumed_input_sha256'] = {relative(p): digest for p, digest in consumed.items()}
    report['changed_consumed_files'] = [relative(p) for p, digest in consumed.items() if sha(p) != digest]
    report['status'] = 'PASS' if not report['changed_consumed_files'] and all(p['status'] == 'PASS' for p in results) else 'FAIL'
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    output = WORK / 'qa/all_source_projection_preflight.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'pairs': len(results),
                      'batches': sum(len(p['batches']) for p in results),
                      'failures': [p['unit_id'] for p in results if p['status'] != 'PASS'],
                      'report': relative(output), 'sha256': sha(output)}, ensure_ascii=False), flush=True)
    raise SystemExit(0 if report['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
