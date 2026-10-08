"""Regression for precise reviewed metadata surviving Excel serialization."""
import json
from pathlib import Path
import tempfile
import unittest

import apply_reviewed_metadata as subject


class MetadataRoundTrip(unittest.TestCase):
    def test_precise_fraction_and_unrelated_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_root, old_here = subject.ROOT, subject.HERE
            subject.ROOT = subject.HERE = root
            try:
                book = {
                    "Papers": {"Papers": (["article_id", "target_coverage_ratio"], [["source", None]])},
                    "Models & coverage": {"Models": (["model_id", "note"], [["accepted", "Keep this unchanged"]])},
                    "Unrelated": {"Values": (["name", "value"], [["scientific", 1.412971356337523]])},
                }
                project = root / "Project.xlsx"
                subject.write_book(project, book)
                plan = {
                    "regional_inputs": [],
                    "patches": [{"sheet": "Papers", "table": "Papers", "key": {"article_id": "source"},
                                 "field": "target_coverage_ratio", "expected_old": None,
                                 "proposed": 0.46879416652121647}],
                }
                plan_path = root / "plan.json"
                plan_path.write_text(json.dumps(plan), encoding="utf-8")
                subject.apply(plan_path, True)
                actual = subject.read_book(project)
                self.assertEqual(actual["Papers"]["Papers"][1][0][1], 0.4687941665212165)
                self.assertEqual(actual["Unrelated"], book["Unrelated"])
                self.assertEqual(actual["Models & coverage"], book["Models & coverage"])
                receipt = json.loads((root / "plan_applied.json").read_text(encoding="utf-8"))
                self.assertTrue(receipt["preserved_unrelated_content"])
                self.assertEqual(receipt["patches"][0]["proposed"], plan["patches"][0]["proposed"])
            finally:
                subject.ROOT, subject.HERE = old_root, old_here


if __name__ == "__main__":
    unittest.main()
