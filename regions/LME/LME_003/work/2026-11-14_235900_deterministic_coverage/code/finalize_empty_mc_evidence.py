"""Bind verified regression evidence and remove only this test's owned copy."""
import ast
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import shutil
import sys
import zipfile

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p / 'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
import adopt_completion as adopter
from tools.project_core.validation.researcher_review import S, sheet_xml
from verify_lme014_private_adoption import bounded_files


def mc_state(path):
    import openpyxl
    workbook = openpyxl.load_workbook(path, read_only=True)
    try:
        values = [[(type(value).__name__, repr(value)) for value in row]
                  for row in workbook['mc_diagnostics'].values]
    finally:
        workbook.close()
    with zipfile.ZipFile(path) as archive:
        _, sheet = sheet_xml(archive, 'mc_diagnostics')
    return {'typed_values': values, 'dimension': sheet.find(f'{{{S}}}dimension').get('ref'),
            'explicit_empty_rows': [row.get('r') for row in
                sheet.findall(f'{{{S}}}sheetData/{{{S}}}row') if not len(row)]}


def main():
    report_path = WORK / 'qa/lme014_private_full_adoption.json'
    report = adopter.read(report_path)
    assert report['status'] == 'PASS' and len(report['batches']) == 2
    assert all(batch['entire_assert_retained'] == 'PASS' for batch in report['batches'])
    assert not report['changed_canonical_inputs']
    all_source_path = WORK / 'qa/all_source_projection_preflight.json'
    all_source = adopter.read(all_source_path)
    assert all_source['status'] == 'PASS' and len(all_source['pairs']) == 11
    assert sum(len(pair['batches']) for pair in all_source['pairs']) == 24
    assert all_source['coverage_sha256'] == report['coverage_sha256']
    focused = WORK / 'qa/empty_mc_regressions_focused30.log'
    log = focused.read_text(encoding='utf-8-sig')
    assert 'Ran 30 tests' in log and log.rstrip().endswith('OK')
    source = ROOT / 'tools/project_core/calculations/coverage.py'
    assert adopter.sha(source) == report['coverage_sha256']
    baseline = WORK / 'inputs/coverage_before_empty_mc_preservation.py'
    before, after = ast.parse(baseline.read_text(encoding='utf-8-sig')), ast.parse(source.read_text(encoding='utf-8-sig'))
    left = {node.name: ast.dump(node) for node in before.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    right = {node.name: ast.dump(node) for node in after.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    changed = sorted(key for key in left.keys() | right.keys() if left.get(key) != right.get(key))
    assert changed == ['_update_source']
    before.body = [node for node in before.body if not isinstance(node, (ast.FunctionDef, ast.ClassDef))]
    after.body = [node for node in after.body if not isinstance(node, (ast.FunctionDef, ast.ClassDef))]
    assert ast.dump(before) == ast.dump(after)
    diff = WORK / 'qa/empty_mc_coverage.diff'
    diff.write_text(''.join(difflib.unified_diff(baseline.read_text().splitlines(True),
        source.read_text().splitlines(True), fromfile=str(baseline.relative_to(ROOT)),
        tofile=str(source.relative_to(ROOT)))), encoding='utf-8')
    copied = (ROOT / report['copy_root']).resolve()
    assert copied.parent == (WORK / 'tmp').resolve() and copied.name.startswith('full-lme014-adoption-')
    original_source = ROOT / 'regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native/sppr_source.xlsx'
    assert original_source.relative_to(ROOT).as_posix() in report['canonical_input_sha256']
    old_mc, new_mc = mc_state(original_source), mc_state(copied / original_source.relative_to(ROOT))
    assert old_mc == new_mc
    for path, digest in report['canonical_input_sha256'].items():
        assert adopter.sha(ROOT / path) == digest, path
    aborted = (WORK / 'tmp/full-lme014-adoption-08y78gij').resolve()
    roots = [copied, aborted]
    cleanup = {'status': 'HASHED_BEFORE_REMOVAL', 'runs': []}
    for owned_root in roots:
        assert owned_root.parent == (WORK / 'tmp').resolve()
        assert owned_root.name.startswith('full-lme014-adoption-')
        files, directories, skipped = bounded_files(owned_root)
        assert not skipped
        cleanup['runs'].append({'owned_root': owned_root.relative_to(ROOT).as_posix(),
            'scope': 'completed verified fixture' if owned_root == copied else 'interrupted setup; no adoption executed',
            'files': [{'path': path.relative_to(ROOT).as_posix(), 'sha256': adopter.sha(path),
                       'bytes': path.stat().st_size} for path in files],
            'directories': [path.relative_to(ROOT).as_posix() for path in directories]})
    cleanup['total_files'] = sum(len(run['files']) for run in cleanup['runs'])
    cleanup['total_bytes'] = sum(row['bytes'] for run in cleanup['runs'] for row in run['files'])
    cleanup_path = WORK / 'qa/lme014_private_copy_cleanup.json'
    cleanup_path.write_text(json.dumps(cleanup, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # The absolute target is verified above to be this harness's unique child
    # of WORK/tmp. No original or another agent's directory can qualify.
    for owned_root in roots:
        shutil.rmtree(owned_root)
        assert not owned_root.exists()
    cleanup.update(status='REMOVED_OWNED_COPY', removed_at=datetime.now(timezone.utc).isoformat())
    cleanup_path.write_text(json.dumps(cleanup, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    artifacts = [report_path, all_source_path, WORK / 'qa/lme014_private_full_adoption.log', focused, diff, cleanup_path,
        WORK / 'qa/empty_mc_regressions_red.log', WORK / 'qa/empty_mc_regressions_green.log',
        WORK / 'qa/mc_source_roundtrip_reproduction.json', WORK / 'qa/mc_source_roundtrip_reproduction.log',
        WORK / 'qa/lme014_private_full_adoption_attempt1.log',
        WORK / 'code/verify_lme014_private_adoption.py', Path(__file__),
        ROOT / 'tools/workflow_checks/calculations/test_source_mc_preservation.py',
        ROOT / 'tools/workflow_checks/calculations/test_retained_diagnostic_numbers.py']
    summary = {'status': 'PASS_SOURCE_FROZEN', 'coverage_sha256': adopter.sha(source),
        'baseline_coverage_sha256': adopter.sha(baseline), 'adopter_sha256': adopter.sha(adopter.__file__),
        'changed_production_definitions': changed,
        'red_tests': 5, 'red_failing_cases': 4, 'green_focused_tests': 30,
        'full_lme014_batches': len(report['batches']), 'entire_assert_retained_after_each_batch': 'PASS',
        'all_source_copy_models': 11, 'all_source_copy_batches': 24,
        'interrupted_setup': {'status': 'STOPPED_BEFORE_ADOPTION',
            'reason': 'Initial rglob traversed a non-scientific node_modules junction; bounded no-reparse inventory replaced it',
            'partial_copy': aborted.relative_to(ROOT).as_posix(),
            'corrected_model_file_count': report['model_file_count'],
            'skipped_reparse_points': report['skipped_reparse_points']},
        'actual_original_mc_state': old_mc, 'actual_final_mc_state': new_mc,
        'canonical_inputs_unchanged': True, 'canonical_writes': False, 'scientific_solver_called': False,
        'owned_copy_cleanup': {'path': cleanup_path.relative_to(ROOT).as_posix(), 'status': cleanup['status'],
                              'files': cleanup['total_files'], 'bytes': cleanup['total_bytes']},
        'artifact_hashes': {path.relative_to(ROOT).as_posix(): adopter.sha(path) for path in artifacts}}
    output = WORK / 'qa/empty_mc_regression_summary.json'
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': summary['status'], 'summary': output.relative_to(ROOT).as_posix(),
                      'sha256': adopter.sha(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
