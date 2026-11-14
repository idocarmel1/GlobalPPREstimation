"""Apply one committed fix while retaining the previously uncommitted BA feature."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path('C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation')
ISOLATED = Path('C:/Users/idoca/.codex/worktrees/lme022-loader-fix/GlobalPPREstimation')
QA = Path(__file__).resolve().parent
BACKUPS = QA.parent / 'inputs' / 'preintegration_scientific_files'
BASE = 'edc730c8832cd357e2cc174b411aa3a2aa21c675'
PPR = 'tools/scientific_code/PPREstimation/PPRCalculator.py'
EXPORTER = 'tools/scientific_code/PPREstimation/create_PPRS_excel.py'
EXISTING_TEST = 'tools/scientific_code/PPREstimation/tests/test_final_accounting.py'
EXPECTED = {
    PPR: 'b3286abb1749b7b760a8198c4c2d269eed88ca352f5858fa8499c76cf2756105',
    EXPORTER: '5f94a4d885643e706a57a9e8faa1bf9fa5338e8626831d74dfe59f2d833158a1',
    EXISTING_TEST: '128dd34b5b9495fd27e49389942a9d10bc33ec4e59017478c94f9a4ffdb652f3',
}
log = []


def git(*args, cwd=ROOT, input=None):
    result = subprocess.run(['git', *args], cwd=cwd, input=input, capture_output=True)
    log.append({'arguments': list(args), 'cwd': str(cwd), 'exit_code': result.returncode,
                'stdout': result.stdout.decode('utf-8', errors='replace'),
                'stderr': result.stderr.decode('utf-8', errors='replace')})
    if result.returncode:
        raise RuntimeError(f'git {args} failed: {log[-1]["stderr"]}')
    return result.stdout


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def paths(*args):
    return {p for p in git(*args).decode('utf-8').split('\0') if p}


def save(name, data):
    (QA / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def methods(blob):
    tree = ast.parse(blob.decode('utf-8-sig'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PPRCalculator')
    return {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}


def main():
    target = git('rev-parse', '38cb75d0^{commit}').decode().strip()
    assert git('rev-parse', 'HEAD').decode().strip() == BASE, 'Original HEAD changed'
    assert git('branch', '--show-current').decode().strip() == 'main', 'Original branch changed'
    assert not paths('diff', '--cached', '--name-only', '-z'), 'Original index is no longer empty'
    assert all(sha(ROOT / path) == expected for path, expected in EXPECTED.items()), 'Original critical bytes changed'
    git('merge-base', '--is-ancestor', BASE, target)
    changed = paths('diff', '--name-only', '-z', BASE, target)
    dirty = paths('diff', '--name-only', '-z')
    untracked = paths('ls-files', '--others', '--exclude-standard', '-z')
    assert changed & dirty == {PPR, EXPORTER}, 'New overlapping tracked changes'
    assert not changed & untracked, 'Untracked files collide with committed fixes'
    assert all(path.startswith(('tools/', 'explainers/')) for path in changed), 'Commit scope is broader than authorized'
    before_status = git('status', '--porcelain=v1', '-z', '--untracked-files=all').decode('utf-8').split('\0')
    before_hashes = {path: sha(ROOT / path) for path in sorted(dirty)}
    before_ppr = (ROOT / PPR).read_bytes()
    raw_patch = git('diff', '--', PPR)
    sections = re.split(rb'(?m)(?=^@@ )', raw_patch)
    selected = [p for p in sections[1:] if int(re.match(rb'@@ -(\d+)', p).group(1)) < 1102]
    starts = [int(re.match(rb'@@ -(\d+)', p).group(1)) for p in selected]
    assert starts == [40, 71, 87, 120, 129, 187, 197, 229, 243, 286, 544], 'Unexpected BA patch boundary'
    ba_patch = sections[0] + b''.join(selected)
    git('apply', '--check', '--whitespace=nowarn', '-', cwd=ISOLATED, input=ba_patch)
    assert git('rev-parse', 'HEAD', cwd=ISOLATED).decode().strip() == target, 'Isolated execution identity changed'

    BACKUPS.mkdir(parents=True, exist_ok=True)
    for path in EXPECTED:
        (BACKUPS / Path(path).name).write_bytes((ROOT / path).read_bytes())
    (BACKUPS / 'preserved_refresh_missing_biomass_accum.patch').write_bytes(ba_patch)
    save('integration_before_status.json', before_status)
    save('integration_before_hashes.json', before_hashes)
    manifest = {
        'started_utc': datetime.now(timezone.utc).isoformat(), 'original_branch': 'main',
        'original_head': BASE, 'target_commit': target, 'status': 'prepared',
        'commit_paths': sorted(changed), 'preexisting_critical_hashes': EXPECTED,
        'preserved_ba_hunk_base_starts': starts, 'index_was_empty': True,
        'backup_directory': '../inputs/preintegration_scientific_files',
        'official_diagnostics_engine': 'clean isolated commit; not the merged dirty calculator',
    }
    save('integration_manifest.json', manifest)
    # Recheck immediately before the first Git mutation.
    assert all(sha(ROOT / path) == expected for path, expected in EXPECTED.items())
    assert not paths('diff', '--cached', '--name-only', '-z')
    git('stash', 'push', '-m', 'Preserve preexisting BA feature before 38cb75d0', '--', PPR, EXPORTER)
    stash = git('rev-parse', 'refs/stash').decode().strip()
    assert paths('diff', '--name-only', '-z', stash + '^1', stash) == {PPR, EXPORTER}
    manifest.update(status='stashed', retained_stash=stash)
    save('integration_manifest.json', manifest)
    git('merge', '--ff-only', target)
    git('apply', '--check', '--whitespace=nowarn', '-', input=ba_patch)
    git('apply', '--whitespace=nowarn', '-', input=ba_patch)
    git('apply', '--reverse', '--check', '--whitespace=nowarn', '-', input=ba_patch)

    assert git('rev-parse', 'HEAD').decode().strip() == target
    assert not paths('diff', '--cached', '--name-only', '-z'), 'Integration must leave index empty'
    assert sha(ROOT / EXPORTER) == EXPECTED[EXPORTER], 'Exporter contents changed unexpectedly'
    assert sha(ROOT / EXISTING_TEST) == EXPECTED[EXISTING_TEST], 'Existing untracked tests changed'
    assert EXISTING_TEST in paths('ls-files', '--others', '--exclude-standard', '-z')
    after_ppr = (ROOT / PPR).read_bytes()
    compile(after_ppr, PPR, 'exec')
    before_methods, after_methods = methods(before_ppr), methods(after_ppr)
    feature = '_refresh_missing_biomass_accum'
    assert ast.dump(before_methods[feature], include_attributes=False) == ast.dump(after_methods[feature], include_attributes=False)
    for name in ('__init__', 'from_dict', 'from_modeldata'):
        assert ast.dump(before_methods[name].args) == ast.dump(after_methods[name].args)
    unrelated_changes = {path: {'before': value, 'after': sha(ROOT / path)}
                         for path, value in before_hashes.items()
                         if path not in {PPR, EXPORTER} and sha(ROOT / path) != value}
    after_status = git('status', '--porcelain=v1', '-z', '--untracked-files=all').decode('utf-8').split('\0')
    save('integration_after_status.json', after_status)
    save('integration_after_hashes.json', {path: sha(ROOT / path) for path in sorted(dirty)})
    save('integration_git_log.json', log)
    (QA / 'remaining_original_calculator.diff').write_bytes(git('diff', '--', PPR))
    manifest.update(status='integrated' if not unrelated_changes else 'integrated_with_concurrent_changes',
        finished_utc=datetime.now(timezone.utc).isoformat(), index_remains_empty=True,
        preexisting_untracked_test_preserved=True, preserved_ba_helper_ast_identical=True,
        preserved_constructor_signatures=True, reverse_ba_patch_check_passed=True,
        clean_committed_calculator_sha256=sha(ISOLATED / PPR),
        original_merged_calculator_sha256=sha(ROOT / PPR),
        unrelated_preexisting_tracked_files=len(before_hashes) - 2,
        unrelated_byte_changes=unrelated_changes,
        difference_note='Original main retains the preexisting opt-in refresh_missing_biomass_accum feature, default False. '
                        'Its calculator bytes differ from the clean committed engine used by the official diagnostics. '
                        'No byte-equivalence or automatic result-freshness claim is made.')
    save('integration_manifest.json', manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


try:
    main()
except Exception:
    save('integration_git_log.json', log)
    raise
