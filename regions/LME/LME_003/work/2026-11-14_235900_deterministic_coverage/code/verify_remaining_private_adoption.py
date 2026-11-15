"""Run one remaining unit's complete cached adopter on bounded owned copies."""
import argparse
from contextlib import ExitStack
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import time
import traceback
from unittest.mock import patch

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
import adopt_completion as adopter
from tools.project_core.calculations import coverage
from tools.scientific_helpers.sppr import method_coverage as adapter
from verify_lme014_private_adoption import bounded_files, CopyBoundary, no_solver


def allowed_node_junctions(model_dir):
    """Allow only non-scientific validation-work code/node_modules links."""
    work = model_dir / 'model_validation/work'
    if not work.is_dir():
        return set()
    if work.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        raise ValueError('Validation work directory is a reparse point')
    allowed = set()
    with os.scandir(work) as entries:
        for entry in entries:
            info = entry.stat(follow_symlinks=False)
            if info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ValueError('Validation work child is a reparse point')
            if not stat.S_ISDIR(info.st_mode):
                continue
            code = Path(entry.path) / 'code'
            if not code.exists():
                continue
            if code.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ValueError('Validation code directory is a reparse point')
            node = code / 'node_modules'
            if node.exists() and node.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                allowed.add(node)
    return allowed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', required=True, choices=['LME_037', 'LME_013', 'LME_022'])
    parser.add_argument('--coverage-sha', required=True)
    args = parser.parse_args()
    began = time.monotonic()
    print(args.unit + ': starting bounded private full-adopter verification', flush=True)
    coverage_path = Path(coverage.__file__).resolve()
    assert adopter.sha(coverage_path) == args.coverage_sha
    inventory = adopter.read(WORK / 'inputs/validated_inventory.json')
    item = next(item for item in inventory['pairs'] if item['unit_id'] == args.unit)
    model_dir = ROOT / item['model_dir']
    region = next(parent for parent in model_dir.parents if parent.name == args.unit)
    regional = region / (args.unit + '.xlsx')
    metadata = next(row for row in coverage._metadata(ROOT)
                    if (row['unit_id'], row['model_id']) == (args.unit, item['model_id']))
    model_files, _, skipped = bounded_files(model_dir, allowed_reparse=allowed_node_junctions(model_dir))
    originals = list(dict.fromkeys([ROOT / 'Project.xlsx', regional,
                                   ROOT / metadata['validation_report_path'], *model_files]))
    hashes = {path: adopter.sha(path) for path in originals}
    hashes.update({coverage_path: args.coverage_sha, Path(adopter.__file__): adopter.sha(adopter.__file__)})
    copied = Path(tempfile.mkdtemp(prefix='remaining-' + args.unit.lower() + '-', dir=WORK / 'tmp')).resolve()
    assert copied.parent == (WORK / 'tmp').resolve()
    print(args.unit + ': copying ' + str(len(model_files)) + ' bounded model files; skipped ' + str(len(skipped)) + ' junctions', flush=True)
    for source in originals:
        destination = copied / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        assert adopter.sha(destination) == hashes[source]
    report = {'status': 'RUNNING', 'unit_id': args.unit, 'model_id': item['model_id'],
        'started_at': datetime.now(timezone.utc).isoformat(), 'coverage_sha256': args.coverage_sha,
        'adopter_sha256': hashes[Path(adopter.__file__)], 'helper_sha256': adopter.sha(__file__),
        'bounded_helper_sha256': adopter.sha(WORK / 'code/verify_lme014_private_adoption.py'),
        'copy_root': copied.relative_to(ROOT).as_posix(), 'model_file_count': len(model_files),
        'skipped_reparse_points': skipped, 'canonical_writes': False,
        'scientific_solver_called': False, 'batches': []}
    try:
        with ExitStack() as stack:
            stack.enter_context(patch.object(adopter, 'ROOT', copied))
            for name in ('compute_methods', '_run', '_load'):
                stack.enter_context(patch.object(adapter, name, no_solver))
            plans, consumed, immutable, central = adopter.prepare(units={args.unit})
            assert len(plans) == 1 and plans[0]['batches']
            plan = plans[0]
            original_execution = copy.deepcopy(adopter.read(plan['manifest']).get('method_coverage', {}).get('execution_evidence', {}))
            report['original_execution_evidence'] = original_execution
            boundary = CopyBoundary(copied)
            for key in ('model', 'source', 'manifest', 'workbook', 'regional'):
                boundary.before_write(plan[key])
            adopter.check_hashes(consumed)
            adopter.check_hashes(immutable)
            for number, batch in enumerate(plan['batches'], 1):
                print(args.unit + ': complete private batch ' + str(number) + ': ' + ', '.join(batch.verified), flush=True)
                changed, result = coverage._complete_model(copied, plan['metadata'], tuple(batch.verified),
                    progress=lambda message: print(message, flush=True), compute=batch,
                    retry_unavailable=True, execution_flags=batch.identity['flags'])
                boundary.checkpoint(result.get('written_paths', ()), fingerprints=result.get('written_hashes'))
                if changed:
                    adopter.stamp_actual_execution(plan, batch, boundary)
                adopter.check_hashes(immutable)
                adopter.assert_retained(plan)
                current = adopter.read(plan['manifest'])['method_coverage']
                adopter.unchanged_projection(original_execution, current.get('execution_evidence', {}),
                                             'original execution evidence')
                for reference in coverage._execution_evidence_references(current):
                    adopter.reference(plan['model'].parent / 'results/diagnostics', reference)
                report['batches'].append({'number': number, 'methods': list(batch.verified),
                    'changed': changed, 'entire_assert_retained': 'PASS', 'immutable_hashes': 'PASS',
                    'original_execution_evidence_retained_and_all_references_authenticated': 'PASS',
                    'source_sha256': adopter.sha(plan['source']), 'workbook_sha256': adopter.sha(plan['workbook'])})
                print(args.unit + ': full assert_retained and execution evidence PASS for batch ' + str(number), flush=True)
            adopter.assert_retained(plan)
            adopter.unchanged_projection(central, adopter.central_state(), 'Project private copy')
            report['status'] = 'PASS'
    except Exception as error:
        report.update(status='FAIL', error=str(error), traceback=traceback.format_exc())
        print(report['traceback'], flush=True)
    report['changed_canonical_inputs'] = [path.relative_to(ROOT).as_posix()
        for path, digest in hashes.items() if adopter.sha(path) != digest]
    if report['changed_canonical_inputs']:
        report['status'] = 'FAIL'
    report['canonical_input_sha256'] = {path.relative_to(ROOT).as_posix(): digest for path, digest in hashes.items()}
    report['seconds'] = round(time.monotonic() - began, 3)
    output = WORK / ('qa/' + args.unit.lower() + '_private_full_adoption.json')
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'unit_id': args.unit, 'batches': len(report['batches']),
                      'report': output.relative_to(ROOT).as_posix(), 'sha256': adopter.sha(output)}, ensure_ascii=False), flush=True)
    raise SystemExit(0 if report['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
