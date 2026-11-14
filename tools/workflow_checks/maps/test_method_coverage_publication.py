"""Scientific preparation is scoped and saved-data publishing never executes it."""
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.project_core.maps import build_html, open_map
from tools.project_core.registry import update_project
from tools.project_core.workbooks.workbooks import sha, write_book


class CoveragePublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        write_book(self.root / 'Project.xlsx', {'Models & coverage': {'Models': (['unit_id','model_id'],[])}})
        self.events = []
        from tools.project_core.calculations import coverage
        self.coverage = coverage
        def ensure(root, **kwargs):
            self.events.append(('coverage', kwargs.get('lock_held'), kwargs.get('units'), kwargs.get('model_pairs')))
            return {'changed_units': ['LME_002'], 'models': {}}
        self.addCleanup(patch.stopall)
        patch.object(self.coverage, 'ensure_validated_coverage', side_effect=ensure).start()
        self.region = self.root / 'regions/LME/LME_002/LME_002.xlsx'
        patch.object(update_project, 'region_directory', return_value=self.region.parent).start()
        patch.object(build_html, 'region_directory', return_value=self.region.parent).start()

    def test_central_update_includes_changed_candidate_region_under_same_lock(self):
        requested = self.root / 'regions/LME/LME_001/LME_001.xlsx'
        with patch.object(update_project, '_update', side_effect=lambda root, paths, all_regions: self.events.append(('update', list(paths)))):
            update_project.update(self.root, [requested])
        self.assertEqual(self.events, [('coverage', True, {'LME_001'}, None), ('update', [requested, self.region])])
        self.assertFalse((self.root / '.project-write.lock').exists())

    def test_build_renders_only_requested_saved_units_without_inventory(self):
        with patch.object(update_project, '_update', side_effect=lambda *args: self.events.append(('update',))), \
             patch.object(build_html, '_build', create=True, side_effect=lambda workbook, output, only_units: self.events.append(('build', only_units))):
            build_html.build(self.root / 'Project.xlsx', only_units={'LME_001'})
        self.assertEqual(self.events, [('build', {'LME_001'})])

    def test_all_saved_consolidation_does_not_request_global_science(self):
        with patch.object(update_project, '_update'):
            update_project.update(self.root, [], all_regions=True)
        self.assertEqual(self.events, [])

    def test_fresh_launch_does_not_rebuild_pages(self):
        directory = self.root / 'interactive_map'
        directory.mkdir()
        for name in ['index.html', 'trends.html']:
            (directory / name).write_text('<meta name="ppr-project-sha256" content="' + sha(self.root / 'Project.xlsx') + '">')
        (directory / 'sources.html').write_text('sources')
        with patch.object(build_html, '_build', create=True) as build:
            build_html.ensure_map_publication(self.root)
        build.assert_not_called()

    def test_layout_refresh_skips_scientific_inventory(self):
        with patch.object(build_html,'_relayout',create=True,side_effect=lambda *args,**kwargs:self.events.append(('validate-layout',kwargs.get('publish',True)))), \
             patch.object(update_project,'_update',side_effect=lambda *args:self.events.append(('update',))), \
             patch.object(build_html,'_build',side_effect=lambda workbook,output,only_units:self.events.append(('build',only_units))):
            build_html.relayout(self.root/'Project.xlsx')
        self.assertEqual(self.events,[('validate-layout',False),('validate-layout',True)])

    def test_review_handoff_keeps_bounded_gate_and_skips_scientific_inventory(self):
        with patch.object(build_html,'_refresh_reviews',side_effect=lambda *args,**kwargs:self.events.append(('verify-review',kwargs.get('publish',True)))), \
             patch.object(update_project,'_update',side_effect=lambda *args:self.events.append(('update',))), \
             patch.object(build_html,'_build',side_effect=lambda workbook,output,only_units:self.events.append(('build',only_units))):
            build_html.refresh_reviews(self.root/'Project.xlsx',self.root/'previous.xlsx',['LME_001'])
        self.assertEqual(self.events,[('verify-review',False),('verify-review',True)])

    def test_invalid_review_handoff_does_not_start_scientific_completion(self):
        with patch.object(build_html,'_refresh_reviews',side_effect=ValueError('unrelated central edits')):
            with self.assertRaisesRegex(ValueError,'unrelated central edits'):
                build_html.refresh_reviews(self.root/'Project.xlsx',self.root/'previous.xlsx',['LME_001'])
        self.assertEqual(self.events,[])


class OpenMapTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'Project.xlsx').write_bytes(b'not a workbook: serving must not read it')
        self.events = []

    def test_launcher_reuses_server_without_publication_even_with_project_lock(self):
        lock = self.root / '.project-write.lock'
        lock.write_bytes(b'another project writer')
        directory = self.root / 'interactive_map'
        directory.mkdir()
        page = directory / 'index.html'
        page.write_bytes(b'existing saved map')
        before = {path: path.read_bytes() for path in [lock, page, self.root / 'Project.xlsx']}
        with patch.object(open_map, 'ROOT', self.root), \
             patch.object(build_html, 'ensure_map_publication', create=True, side_effect=lambda root: self.events.append(('publication',))), \
             patch.object(open_map, 'find_or_start', side_effect=lambda *args: (self.events.append(('server',)) or (None, 8877))), \
             patch.object(open_map.webbrowser, 'open') as browser, \
             patch.object(sys, 'argv', ['map.py']):
            open_map.main()
        self.assertEqual(self.events, [('server',)])
        browser.assert_called_once_with('http://127.0.0.1:8877/interactive_map/index.html')
        self.assertEqual({path: path.read_bytes() for path in before}, before)

    def test_missing_html_stops_without_generating_files_or_starting_server(self):
        with patch.object(open_map, 'ROOT', self.root), \
             patch.object(build_html, 'ensure_map_publication', side_effect=AssertionError('must not publish')), \
             patch.object(open_map, 'find_or_start') as start, \
             patch.object(sys, 'argv', ['map.py', '--no-browser']):
            with self.assertRaises(SystemExit) as error:
                open_map.main()
        self.assertEqual(error.exception.code, 2)
        start.assert_not_called()
        self.assertFalse((self.root / 'interactive_map').exists())

if __name__ == '__main__':
    unittest.main()
