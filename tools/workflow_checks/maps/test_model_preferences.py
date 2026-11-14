import json
from pathlib import Path
import shutil
import subprocess
import unittest


class ModelPreferenceTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node required')
    def test_shared_preferences_and_both_page_integrations(self):
        from tools.project_core.maps.build_html import linked_layout
        root = Path(__file__).resolve().parents[3]
        layouts = {name: linked_layout((root / 'tools/project_core/maps/original_html_layout' / file).read_text('utf-8'))
                   for name, file in [('map', 'index.html'), ('trends', 'trends.html')]}
        result = subprocess.run([shutil.which('node'), str(Path(__file__).with_name('check_model_preferences.js'))],
                                input=json.dumps(layouts), capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_changed_preference_anchor_stops_publication(self):
        from tools.project_core.maps.build_html import linked_layout
        root = Path(__file__).resolve().parents[3]
        template = (root / 'tools/project_core/maps/original_html_layout/index.html').read_text('utf-8')
        with self.assertRaisesRegex(ValueError, 'Model preferences layout anchor'):
            linked_layout(template.replace("PPRGroupSettings.create({view:'map'})", "PPRGroupSettings.create({view:'renamed'})"))
