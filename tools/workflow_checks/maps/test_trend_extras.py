import shutil
import json
import subprocess
import unittest
from pathlib import Path


class TrendExtrasTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node required')
    def test_selected_model_filter_and_regional_table(self):
        from tools.project_core.maps.build_html import linked_layout
        root = Path(__file__).resolve().parents[3]
        page = linked_layout((root / 'tools/project_core/maps/original_html_layout/trends.html').read_text('utf-8'))
        result = subprocess.run(
            [shutil.which('node'), str(Path(__file__).with_name('check_trend_extras.js'))],
            input=json.dumps(page), capture_output=True, text=True, encoding='utf-8',
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_changed_control_anchor_stops_publication(self):
        from tools.project_core.maps.build_html import linked_layout
        root = Path(__file__).resolve().parents[3]
        text = (root / 'tools/project_core/maps/original_html_layout/trends.html').read_text('utf-8')
        with self.assertRaisesRegex(ValueError, 'Trend controls anchor'):
            linked_layout(text.replace('id="openGroupFilter"', 'id="renamedFilter"'))
