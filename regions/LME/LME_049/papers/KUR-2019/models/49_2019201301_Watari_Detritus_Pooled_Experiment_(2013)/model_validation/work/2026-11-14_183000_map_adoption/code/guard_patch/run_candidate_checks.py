"""Check a proposed adapter in memory; never replace the production file."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest

sys.stdout.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
PRODUCTION = ROOT/'tools/scientific_helpers/sppr/method_coverage.py'
before = hashlib.sha256(PRODUCTION.read_bytes()).hexdigest()

# Use the production location for dependency resolution but execute only the
# staged source bytes in this process. Subsequent test imports see this module.
name = 'tools.scientific_helpers.sppr.method_coverage'
candidate = types.ModuleType(name)
candidate.__file__ = str(PRODUCTION)
candidate.__package__ = 'tools.scientific_helpers.sppr'
sys.modules[name] = candidate
exec(compile((HERE/'method_coverage.py').read_bytes(), str(PRODUCTION), 'exec'), candidate.__dict__)

spec = importlib.util.spec_from_file_location('_guard_tests', HERE/'test_runtime_initialization_guard.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
loader = unittest.TestLoader()
suite = unittest.TestSuite([
    loader.loadTestsFromModule(tests),
    loader.loadTestsFromName('tools.workflow_checks.calculations.test_audited_configuration'),
    loader.loadTestsFromName('tools.workflow_checks.calculations.test_validated_method_coverage'),
    loader.loadTestsFromName('tools.workflow_checks.calculations.test_coverage_preservation'),
])
log = io.StringIO()
result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
after = hashlib.sha256(PRODUCTION.read_bytes()).hexdigest()
assert before == after, 'Production adapter changed while draft checks ran'
(HERE/'candidate_checks.txt').write_text(log.getvalue(), encoding='utf-8')
report = {'passed':result.wasSuccessful(), 'tests':result.testsRun,
          'failures':len(result.failures), 'errors':len(result.errors),
          'failure_names':[str(t) for t,_ in result.failures], 'error_names':[str(t) for t,_ in result.errors],
          'production_sha256_before':before, 'production_sha256_after':after,
          'production_unchanged':True,
          'candidate_sha256':hashlib.sha256((HERE/'method_coverage.py').read_bytes()).hexdigest(),
          'test_scope':'Guard tests plus adjacent configuration/coverage/preservation suites; candidate source loaded only in this process.',
          'production_patch_applied':False}
(HERE/'candidate_checks.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report, indent=2), flush=True)
if not result.wasSuccessful():
    print(log.getvalue(), flush=True)
sys.exit(0 if result.wasSuccessful() else 1)
