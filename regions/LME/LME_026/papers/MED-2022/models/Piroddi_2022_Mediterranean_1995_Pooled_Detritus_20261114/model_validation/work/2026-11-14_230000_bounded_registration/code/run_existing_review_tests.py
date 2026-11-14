"""Reuse existing review regressions against proposed gate, in isolated fixtures."""
import tempfile
import unittest
from pathlib import Path
import test_review_candidate_gate as proposal
from tools.workflow_checks.validation import test_researcher_disqualification as negative
from tools.workflow_checks.validation import test_researcher_review_model_boundary as boundary
# Filesystem changes stay in this model-local QA directory.
tempfile.tempdir=str(proposal.RUN/'qa')
negative.refresh_reviews=proposal.build._refresh_reviews
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(negative),unittest.defaultTestLoader.loadTestsFromModule(boundary)])
result=unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(not result.wasSuccessful())
