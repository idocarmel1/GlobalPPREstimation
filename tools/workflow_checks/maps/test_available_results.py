"""Exercise the generated calculation adapters, including strict anchor failures."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from tools.project_core.maps.provisional_display import provisional_layout
from tools.project_core.validation.researcher_review import reviewed_layout
from tools.project_core.maps.map_cumulative_ppr import cumulative_ppr_layout
from tools.project_core.maps.available_results_layout import available_results_layout

ROOT = Path(__file__).resolve().parents[3]
MAPS = ROOT / "tools/project_core/maps"


def current_layout(name):
    text = (MAPS / "original_html_layout" / name).read_text(encoding="utf-8")
    return cumulative_ppr_layout(reviewed_layout(provisional_layout(text)))


class AvailableResultsTests(unittest.TestCase):
    def test_independent_annual_results_and_reviewed_retained_arithmetic(self):
        from tools.project_core.maps.build_html import linked_layout
        payload = {name: linked_layout((MAPS / "original_html_layout" / name).read_text(encoding="utf-8"))
                   for name in ("index.html", "trends.html")}
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required for the browser calculation check")
        result = subprocess.run(
            [node, str(Path(__file__).with_name("check_available_results.js"))],
            input=json.dumps(payload), text=True, encoding="utf-8", capture_output=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_changed_calculation_anchor_stops_publication(self):
        text = current_layout("trends.html").replace("  function compare(db,state) {", "  function changedCompare(db,state) {")
        with self.assertRaisesRegex(ValueError, "compare"):
            available_results_layout(text)


if __name__ == "__main__":
    unittest.main()
