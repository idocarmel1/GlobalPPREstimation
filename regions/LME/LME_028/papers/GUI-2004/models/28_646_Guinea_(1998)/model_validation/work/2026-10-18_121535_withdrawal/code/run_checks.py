"""Focused existing workflow tests using a workspace-local temporary root."""
import sys, tempfile, unittest
from pathlib import Path

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
RUN=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
scratch=ROOT/'regions/LME/LME_028/work/2026-10-18_121535_withdrawal_tests'
scratch.mkdir(exist_ok=True)
tempfile.tempdir=str(scratch)
names=[
 'tools.workflow_checks.validation.test_researcher_disqualification',
 'tools.workflow_checks.validation.test_researcher_review',
 'tools.workflow_checks.validation.test_review_scope',
 'tools.workflow_checks.maps.test_method_coverage_publication',
 'tools.workflow_checks.maps.test_publication_transactions',
]
print('Loading five focused workflow test modules',flush=True)
suite=unittest.defaultTestLoader.loadTestsFromNames(names)
with (RUN/'qa/focused_tests.txt').open('w',encoding='utf-8') as log:
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
print(f'Focused tests: {result.testsRun}; failures={len(result.failures)} errors={len(result.errors)} skipped={len(result.skipped)}',flush=True)
sys.exit(not result.wasSuccessful())
