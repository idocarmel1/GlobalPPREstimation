import json
import shutil
import subprocess
import unittest
from pathlib import Path


class GroupContributionsTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node required')
    def test_group_stack_preserves_totals_and_reselects_top_five(self):
        from tools.project_core.maps.build_html import linked_layout
        root = Path(__file__).resolve().parents[3]
        page = linked_layout((root / 'tools/project_core/maps/original_html_layout/trends.html').read_text('utf-8'))
        result = subprocess.run(
            [shutil.which('node'), str(Path(__file__).with_name('check_group_contributions.js'))],
            input=json.dumps(page), capture_output=True, text=True, encoding='utf-8',
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
