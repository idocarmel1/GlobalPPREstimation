"""Persist narrow red/green proof without reverting the shared adapter file."""
from pathlib import Path
import contextlib
import hashlib
import json
import os
import re
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'tools/workflow_checks')]
NEW = """                    declared=o.get('model_path') if refresh else None
                    registered=model_metadata.get((unit,selected),{}).get('model_path')
                    native=(path.parent/str(declared) if declared else root/str(registered or f'regions/{unit}/models/{selected}/model.json')).resolve()
                    sourcefile=native.with_name('sppr_source.xlsx')
                    if not sourcefile.is_file():sourcefile=native
                    sourcefile=sourcefile.relative_to(root.resolve()).as_posix()"""
OLD = """                    sourcefile=f'regions/{unit}/models/{selected}/sppr_source.xlsx'
                    if not (root/sourcefile).exists():sourcefile=f'regions/{unit}/models/{selected}/model.json'"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if len(sys.argv) > 1:
    import test_model_source_paths
    if sys.argv[1] == 'baseline':
        source = (ROOT / 'tools/original_atlas_data.py').read_text(encoding='utf-8')
        assert source.count(NEW) == 1, 'Expected exact narrow source resolver block'
        namespace = {'__name__': 'isolated_original_atlas_data_baseline'}
        exec(compile(source.replace(NEW, OLD), '<isolated old source resolver>', 'exec'), namespace)
        test_model_source_paths.datasets = namespace['datasets']
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_model_source_paths)
    sys.exit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())

protected = [ROOT / 'regions/LME_052/LME_052.xlsx',
             ROOT / 'regions/LME_052/models/52_GM2019_Fig9_Pelagic_(2000-2014)/assumption_variants/adopted_balanced_20261003/model.json']
before = {p.relative_to(ROOT).as_posix(): digest(p) for p in protected}
checks = {}
for label, args in [('source_link_regression_red', [str(Path(__file__).resolve()), 'baseline']),
                    ('source_link_regression_green', [str(Path(__file__).resolve()), 'current']),
                    ('full_workflow_suite_20261003', ['-m', 'unittest', 'discover', '-s', 'tools/workflow_checks', '-v'])]:
    command = [sys.executable, *args]
    log = HERE / (label + '.log')
    with log.open('w', encoding='utf-8') as output:
        result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT, env=os.environ.copy())
    text = log.read_text(encoding='utf-8')
    failures = []
    for block in re.split(r'={20,}\n', text):
        if block.startswith(('FAIL:', 'ERROR:')):
            lines = block.splitlines()
            reason = next((s for s in lines if s.startswith(('ModuleNotFoundError:', 'ReferenceError:', 'AssertionError:'))), None)
            failures.append({'name': lines[0], 'cause': reason})
    checks[label] = {'command': command, 'exit_code': result.returncode, 'log': log.name,
                     'summary': re.findall(r'Ran \d+ tests.*|FAILED \(.*\)|^OK$', text, re.MULTILINE),
                     'failures': failures}
    print(label, result.returncode, flush=True)
after = {p.relative_to(ROOT).as_posix(): digest(p) for p in protected}
evidence = {'source_resolver_change': {'before': OLD, 'after': NEW},
            'baseline_method': 'Only the resolver block is restored in a compiled in-memory copy; shared production file is never reverted.',
            'adapter_sha256': digest(ROOT / 'tools/original_atlas_data.py'),
            'regression_fixture_sha256': digest(ROOT / 'tools/workflow_checks/test_model_source_paths.py'),
            'checks': checks, 'protected_before': before, 'protected_after': after, 'protected_unchanged': before == after,
            'failure_scope': 'Full-suite failures are reported as observed; their prior existence is not established by this run. No broader fixes are included.'}
(HERE / 'source_link_fix_verification.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
print('Structured evidence saved', flush=True)
