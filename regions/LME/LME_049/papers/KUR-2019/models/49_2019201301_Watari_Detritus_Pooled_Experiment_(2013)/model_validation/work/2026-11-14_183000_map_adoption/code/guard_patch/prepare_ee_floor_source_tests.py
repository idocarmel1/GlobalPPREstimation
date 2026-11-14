"""Stage source-page prose regression tests; preserve production tests."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd()
OUT=Path(__file__).resolve().parent
source=(ROOT/'tools/workflow_checks/maps/test_ee_floor_views.py').read_text('utf-8')
anchor="    @unittest.skipUnless(shutil.which('node'), 'Node required for display/export checks')"
assert source.count(anchor)==1
addition='''    def test_source_view_distinguishes_floor_and_review_states_without_mutation(self):
        approved = {'id': 'approved', 'label': 'Reviewed ON', 'calculation_provenance': {'use_ee_floor': True, 'ee_floor': .1},
                    'researcher_review': {'status': 'Validated by researcher', 'report_path': 'report.docx'}}
        pending = {'id': 'pending', 'label': 'Pending ON', 'calculation_provenance': {'use_ee_floor': True, 'ee_floor': .1},
                   'recorded_review_pending': {'recorded_status': 'Validated by researcher', 'reason': 'Source changed'}}
        unsigned = {'id': 'unsigned', 'label': 'Unreviewed OFF', 'calculation_provenance': {'use_ee_floor': False, 'ee_floor': .1}}
        for model, expected, forbidden in [
            (approved, 'The signed researcher review applies to the model, diagnostics and calculation conditions recorded in its report. Other method results retain their own diagnostic status.',
             ['does not approve this changed', 'awaiting current verification', 'No verified researcher review']),
            (pending, 'The recorded researcher review is awaiting current verification.',
             ['The signed researcher review applies', 'No verified researcher review']),
            (unsigned, 'No verified researcher review is recorded for this model.',
             ['The signed researcher review applies', 'awaiting current verification'])]:
            with self.subTest(model=model['id']):
                catalog = {'regions': [{'unit_id': 'LME_001'}],
                           'network': {'units': {'LME_001': {'models': [model]}}}}
                before = copy.deepcopy(catalog)
                page = '<details><summary>Region <small>LME_001 · 0 studies</small></summary><p>Retained source prose</p></details>'
                updated = source_provenance_layout(page, catalog)
                self.assertIn(expected, updated)
                for text in forbidden: self.assertNotIn(text, updated)
                if model['calculation_provenance']['use_ee_floor']:
                    self.assertIn('Hypothetical external nonfishery mortality sink; excluded from catch and fishery PPR.', updated)
                    self.assertNotIn('No EE floor is applied', updated)
                else:
                    self.assertIn('No EE floor is applied in this saved calculation.', updated)
                    self.assertNotIn('Hypothetical external nonfishery mortality sink', updated)
                self.assertEqual(catalog, before, 'Prose rendering cannot mutate approval or calculation payloads')
                self.assertIn('<p>Retained source prose</p>', updated)

'''
(OUT/'test_ee_floor_views_candidate.py').write_text(source.replace(anchor,addition+anchor),encoding='utf-8',newline='\n')
print('Staged source-page state checks.')

