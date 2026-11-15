"""Bind the legacy fix proofs and remove only the LME037 agent-owned copy."""
import ast
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import shutil
import sys

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
import adopt_completion as adopter
from verify_lme014_private_adoption import bounded_files


def main():
    report_paths = {unit: WORK / ('qa/' + unit.lower() + '_private_full_adoption.json')
                    for unit in ('LME_037', 'LME_013', 'LME_022')}
    reports = {unit: adopter.read(path) for unit, path in report_paths.items()}
    source = ROOT / 'tools/project_core/calculations/coverage.py'
    digest = adopter.sha(source)
    for unit, report in reports.items():
        assert report['status'] == 'PASS' and report['unit_id'] == unit and report['batches']
        assert report['coverage_sha256'] == digest and not report['changed_canonical_inputs']
        assert report['helper_sha256'] == adopter.sha(WORK / 'code/verify_remaining_private_adoption.py')
        assert report['bounded_helper_sha256'] == adopter.sha(WORK / 'code/verify_lme014_private_adoption.py')
        assert report['adopter_sha256'] == adopter.sha(adopter.__file__)
        assert all(batch['entire_assert_retained'] == 'PASS' and
                   batch['original_execution_evidence_retained_and_all_references_authenticated'] == 'PASS'
                   for batch in report['batches'])
    focused = WORK / 'qa/legacy_execution_references_focused35.log'
    log = focused.read_text(encoding='utf-8-sig')
    assert 'Ran 35 tests' in log and log.rstrip().endswith('OK')
    baseline = WORK / 'inputs/coverage_before_legacy_evidence_guard.py'
    before, after = ast.parse(baseline.read_text(encoding='utf-8-sig')), ast.parse(source.read_text(encoding='utf-8-sig'))
    left = {node.name: ast.dump(node) for node in before.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    right = {node.name: ast.dump(node) for node in after.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    changed = sorted(key for key in left.keys() | right.keys() if left.get(key) != right.get(key))
    assert changed == ['_cached_methods', '_execution_evidence_references', '_package_cache_valid']
    before.body = [node for node in before.body if not isinstance(node, (ast.FunctionDef, ast.ClassDef))]
    after.body = [node for node in after.body if not isinstance(node, (ast.FunctionDef, ast.ClassDef))]
    assert ast.dump(before) == ast.dump(after)
    diff = WORK / 'qa/legacy_execution_evidence_coverage.diff'
    diff.write_text(''.join(difflib.unified_diff(baseline.read_text().splitlines(True),
        source.read_text().splitlines(True), fromfile=str(baseline.relative_to(ROOT)),
        tofile=str(source.relative_to(ROOT)))), encoding='utf-8')
    own = reports['LME_037']
    copied = (ROOT / own['copy_root']).resolve()
    assert copied.parent == (WORK / 'tmp').resolve() and copied.name.startswith('remaining-lme_037-')
    item = next(item for item in adopter.read(WORK / 'inputs/validated_inventory.json')['pairs']
                if item['unit_id'] == 'LME_037')
    final_execution = adopter.read(copied / item['model_dir'] / 'results/result_manifest.json')['method_coverage']['execution_evidence']
    adopter.unchanged_projection(own['original_execution_evidence'], final_execution, 'original execution reference')
    for path, expected in own['canonical_input_sha256'].items():
        assert adopter.sha(ROOT / path) == expected, path
    files, directories, skipped = bounded_files(copied)
    assert not skipped
    cleanup = {'status': 'HASHED_BEFORE_REMOVAL', 'unit_id': 'LME_037',
        'owned_root': copied.relative_to(ROOT).as_posix(),
        'files': [{'path': path.relative_to(ROOT).as_posix(), 'sha256': adopter.sha(path),
                   'bytes': path.stat().st_size} for path in files],
        'directories': [path.relative_to(ROOT).as_posix() for path in directories]}
    cleanup['total_files'] = len(files)
    cleanup['total_bytes'] = sum(item['bytes'] for item in cleanup['files'])
    cleanup_path = WORK / 'qa/lme037_private_copy_cleanup.json'
    cleanup_path.write_text(json.dumps(cleanup, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # The exact resolved target was checked above; the bounded inventory refuses
    # reparse points. No peer fixture or canonical model path can qualify.
    shutil.rmtree(copied)
    assert not copied.exists()
    cleanup.update(status='REMOVED_OWNED_COPY', removed_at=datetime.now(timezone.utc).isoformat())
    cleanup_path.write_text(json.dumps(cleanup, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    artifacts = [*report_paths.values(), focused, diff, cleanup_path,
        WORK / 'qa/lme037_private_full_adoption.log',
        WORK / 'qa/legacy_execution_references_red.log', WORK / 'qa/legacy_execution_references_green.log',
        WORK / 'qa/legacy_execution_reference_reproduction.json', WORK / 'qa/legacy_execution_reference_reproduction.log',
        WORK / 'code/verify_remaining_private_adoption.py', WORK / 'code/verify_lme014_private_adoption.py',
        Path(__file__), ROOT / 'tools/workflow_checks/calculations/test_execution_evidence_references.py']
    summary = {'status': 'PASS_SOURCE_FROZEN', 'coverage_sha256': digest,
        'baseline_coverage_sha256': adopter.sha(baseline), 'adopter_sha256': adopter.sha(adopter.__file__),
        'changed_production_definitions': changed, 'red_tests': 5, 'red_errors': 15,
        'green_focused_tests': 35, 'full_private_unit_batches': {unit: len(report['batches']) for unit, report in reports.items()},
        'all_full_assert_retained_checks': 'PASS', 'all_original_execution_evidence_checks': 'PASS',
        'original_legacy_execution_evidence': own['original_execution_evidence'],
        'final_mixed_execution_evidence': final_execution, 'canonical_writes': False,
        'scientific_solver_called': False, 'canonical_inputs_unchanged': True,
        'owned_copy_cleanup': {'path': cleanup_path.relative_to(ROOT).as_posix(),
                              'status': cleanup['status'], 'files': cleanup['total_files'], 'bytes': cleanup['total_bytes']},
        'artifact_hashes': {path.relative_to(ROOT).as_posix(): adopter.sha(path) for path in artifacts}}
    output = WORK / 'qa/legacy_execution_reference_regression_summary.json'
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': summary['status'], 'summary': output.relative_to(ROOT).as_posix(),
                      'sha256': adopter.sha(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
