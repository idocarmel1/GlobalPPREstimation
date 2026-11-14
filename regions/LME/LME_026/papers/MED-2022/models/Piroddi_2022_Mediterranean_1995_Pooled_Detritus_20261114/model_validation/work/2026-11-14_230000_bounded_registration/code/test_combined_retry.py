from pathlib import Path
import importlib.util,sys,tempfile,unittest
run=Path(__file__).resolve().parents[1];sys.path.insert(0,str(run/'code'))
import test_review_candidate_gate as gate
spec=importlib.util.spec_from_file_location('combined_review_retry',run/'outputs/build_html.combined.proposed.py');build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build);build.__file__=str(gate.ROOT/'tools/project_core/maps/build_html.py');gate.build=build
from tools.workflow_checks.maps import test_publication_transactions as existing
existing.atomic_text=build.atomic_text;tempfile.tempdir=str(run/'qa')
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(gate),unittest.defaultTestLoader.loadTestsFromModule(existing)])
result=unittest.TextTestRunner(verbosity=1).run(suite);raise SystemExit(not result.wasSuccessful())
