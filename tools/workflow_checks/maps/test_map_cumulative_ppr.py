"""Exercise cumulative coverage in the generated map and future layout builds."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.project_core.maps.build_html import linked_layout


@unittest.skipUnless(shutil.which('node'), 'Node required for map behavior')
class CumulativePprTests(unittest.TestCase):
    def check_page(self, page):
        result = subprocess.run(
            [shutil.which('node'), str(Path(__file__).with_name('check_map_cumulative_ppr.js')), str(page)],
            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generated_map_uses_entire_set_after_display_filters(self):
        self.check_page(Path(__file__).resolve().parents[3] / 'interactive_map/index.html')

    def test_future_layout_builds_keep_dynamic_cumulative_coverage(self):
        template = Path(__file__).resolve().parents[2] / 'project_core/maps/original_html_layout/index.html'
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / 'index.html'
            page.write_text(linked_layout(template.read_text(encoding='utf-8')), encoding='utf-8')
            self.check_page(page)


if __name__ == '__main__':
    unittest.main()
