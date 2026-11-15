"""Run the real two-batch adopter on owned copies; never run a science solver."""
from contextlib import ExitStack
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

COVERAGE_SHA = '5e01c14c65d4cbb0cff01f058559f0c840579ad164698e413ae0e31d027bd775'


def no_solver(*args, **kwargs):
    raise AssertionError('Scientific computation was requested during private cached adoption')


def bounded_files(directory, *, allowed_reparse=()):
    """Inspect lstat attributes before descent; never follow a Windows junction."""
    directory = Path(directory).absolute()
    allowed = {Path(path).absolute() for path in allowed_reparse}
    pending, files, directories, skipped = [directory], [], [directory], []
    while pending:
        current = pending.pop()
        with os.scandir(current) as entries:
            for entry in entries:
                path = current / entry.name
                info = entry.stat(follow_symlinks=False)
                attributes = getattr(info, 'st_file_attributes', 0)
                if entry.is_symlink() or attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                    if path not in allowed or not attributes & stat.FILE_ATTRIBUTE_DIRECTORY:
                        raise ValueError('Unapproved reparse point in private fixture input: ' + str(path))
                    skipped.append({'path': path.relative_to(directory).as_posix(),
                                    'resolved_target': str(path.resolve()), 'attributes': attributes,
                                    'reason': 'Non-scientific Node dependencies; junction not traversed or copied'})
                elif stat.S_ISDIR(info.st_mode):
                    directories.append(path)
                    pending.append(path)
                elif stat.S_ISREG(info.st_mode):
                    files.append(path)
                else:
                    raise ValueError('Unsupported private fixture file type: ' + str(path))
    return sorted(files), sorted(directories), skipped


class CopyBoundary:
    def __init__(self, root):
        self.root = root

    def before_write(self, path):
        if not Path(path).resolve().is_relative_to(self.root):
            raise ValueError('Private adoption attempted a write outside its owned copy')

    def checkpoint(self, paths, *, fingerprints=None):
        for path in paths:
            self.before_write(path)
            if fingerprints and adopter.sha(path) != fingerprints[str(path)]:
                raise ValueError('Private checkpoint hash differs')


def main():
    began = time.monotonic()
    print('Starting bounded LME014 fixture setup (no junction traversal)', flush=True)
    coverage_path = ROOT / 'tools/project_core/calculations/coverage.py'
    assert adopter.sha(coverage_path) == COVERAGE_SHA
    inventory = adopter.read(WORK / 'inputs/validated_inventory.json')
    item = next(item for item in inventory['pairs'] if item['unit_id'] == 'LME_014')
    model_dir = ROOT / item['model_dir']
    regional = ROOT / 'regions/LME/LME_014/LME_014.xlsx'
    metadata = next(row for row in coverage._metadata(ROOT)
                    if (row['unit_id'], row['model_id']) == (item['unit_id'], item['model_id']))
    node_junction = model_dir / 'model_validation/work/2026-11-14_120000_validation_ee_on/code/node_modules'
    model_files, _, skipped = bounded_files(model_dir, allowed_reparse={node_junction})
    assert len(model_files) == 468 and len(skipped) == 1
    print('Bounded inventory: 468 model files; known node_modules junction skipped', flush=True)
    originals = list(dict.fromkeys([ROOT / 'Project.xlsx', regional,
                                   ROOT / metadata['validation_report_path'], *model_files]))
    hashes = {p: adopter.sha(p) for p in originals}
    hashes[coverage_path] = COVERAGE_SHA
    hashes[Path(adopter.__file__)] = adopter.sha(adopter.__file__)
    copied = Path(tempfile.mkdtemp(prefix='full-lme014-adoption-', dir=WORK / 'tmp')).resolve()
    assert copied.is_relative_to((WORK / 'tmp').resolve())
    print('Copying exact LME014 inputs to ' + str(copied), flush=True)
    for source in originals:
        destination = copied / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        assert adopter.sha(destination) == hashes[source]
    report = {'started_at': datetime.now(timezone.utc).isoformat(), 'coverage_sha256': COVERAGE_SHA,
              'adopter_sha256': hashes[Path(adopter.__file__)], 'helper_sha256': adopter.sha(__file__),
              'copy_root': copied.relative_to(ROOT).as_posix(), 'canonical_writes': False,
              'scientific_solver_called': False, 'batches': [], 'status': 'RUNNING',
              'model_file_count': len(model_files), 'skipped_reparse_points': skipped}
    try:
        with ExitStack() as stack:
            stack.enter_context(patch.object(adopter, 'ROOT', copied))
            for name in ('compute_methods', '_run', '_load'):
                stack.enter_context(patch.object(adapter, name, no_solver))
            plans, consumed, immutable, central = adopter.prepare(units={'LME_014'})
            assert len(plans) == 1 and len(plans[0]['batches']) == 2
            plan = plans[0]
            boundary = CopyBoundary(copied)
            for key in ('model', 'source', 'manifest', 'workbook', 'regional'):
                boundary.before_write(plan[key])
            adopter.check_hashes(consumed)
            adopter.check_hashes(immutable)
            for number, batch in enumerate(plan['batches'], 1):
                print('Starting complete private batch ' + str(number) + ': ' + ', '.join(batch.verified), flush=True)
                changed, result = coverage._complete_model(copied, plan['metadata'], tuple(batch.verified),
                    progress=lambda message: print(message, flush=True), compute=batch,
                    retry_unavailable=True, execution_flags=batch.identity['flags'])
                boundary.checkpoint(result.get('written_paths', ()), fingerprints=result.get('written_hashes'))
                if changed:
                    adopter.stamp_actual_execution(plan, batch, boundary)
                adopter.check_hashes(immutable)
                # This is the complete, unmodified production coordinator guard.
                adopter.assert_retained(plan)
                report['batches'].append({'number': number, 'methods': list(batch.verified),
                    'changed': changed, 'entire_assert_retained': 'PASS',
                    'immutable_hashes': 'PASS', 'source_sha256': adopter.sha(plan['source']),
                    'workbook_sha256': adopter.sha(plan['workbook'])})
                print('Complete private batch ' + str(number) + ': full assert_retained PASS', flush=True)
            adopter.assert_retained(plan)
            adopter.unchanged_projection(central, adopter.central_state(), 'Project private copy')
            report['status'] = 'PASS'
    except Exception as error:
        report.update(status='FAIL', error=str(error), traceback=traceback.format_exc())
        print(report['traceback'], flush=True)
    changed_originals = [str(p.relative_to(ROOT)) for p, digest in hashes.items() if adopter.sha(p) != digest]
    if changed_originals:
        report['status'] = 'FAIL'
    report['changed_canonical_inputs'] = changed_originals
    report['canonical_input_sha256'] = {p.relative_to(ROOT).as_posix(): digest for p, digest in hashes.items()}
    report['seconds'] = round(time.monotonic() - began, 3)
    output = WORK / 'qa/lme014_private_full_adoption.json'
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'batches': len(report['batches']),
                      'report': output.relative_to(ROOT).as_posix(), 'sha256': adopter.sha(output)},
                     ensure_ascii=False), flush=True)
    raise SystemExit(0 if report['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
