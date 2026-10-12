"""A validated nondefault model publishes its own saved coefficients and years."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.project_core.calculations.regional import set_result_hash
from tools.project_core.maps.original_atlas_data import add_source_reviews
from tools.project_core.workbooks.workbooks import YEARS, input_hash, sha, write_book


class CandidatePublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.model = self.root / 'regions/LME/LME_001/papers/p/models/candidate'
        (self.model / 'results').mkdir(parents=True)
        (self.model / 'model.json').write_text('{}')
        self.snapshot = self.model / 'results/regional_snapshot.xlsx'
        self.book = {
            'Overview': {'Settings': (['field', 'value'], [
                ['unit_id', 'LME_001'], ['selected_model_id', 'other'],
                ['results_model_id', 'candidate'], ['results_model_sha256', sha(self.model / 'model.json')]])},
            'Catch': {'Catch': (['taxon', 'catch_basis', 'unidentified', *YEARS],
                                [['fish', basis, False, *([5.] * 70)] for basis in ['landings', 'catch', 'discards']])},
            'Classic PPR': {'Taxa': (['taxon', 'tl', 'sppr'], [['fish', 2., 10.]])},
            'Selected model groups': {
                'Groups': (['group_name', 'tl', 'ge', 'ee'], [['fish group', 2., .2, .8]]),
                'Group SPPR': (['model_id', 'group', 'scope', 'method', 'sppr'], [['candidate', 'fish group', 'all', 'new_GE', 3.]])},
            'PPR': {
                'Matching': (['model_id', 'taxon', 'group', 'weight'], [['candidate', 'fish', 'fish group', 1.]]),
                'Taxon SPPR': (['taxon', 'scope', 'method', 'sppr'], [['fish', 'all', 'new_GE', 3.]]),
                'Annual': (['model_id', 'scope', 'method', 'catch_basis', 'unidentified', 'metric', 'status', *YEARS],
                           [['candidate', 'all', 'new_GE', 'landings', 'method', 'ppr', 'provisional: WARN', *([15.] * 70)]])},
            'NPP': {'NPP': (['method', 'units', *YEARS], [['npp', 'tC/year', *([100.] * 70)]])}}
        self.book['Overview']['Settings'][1].append(['calculation_input_sha256', input_hash(self.book)])
        set_result_hash(self.book)
        write_book(self.snapshot, self.book)
        (self.model / 'results/result_manifest.json').write_text(json.dumps({
            'model_id': 'candidate', 'unit_id': 'LME_001', 'snapshot_sha256': sha(self.snapshot),
            'canonical_model_sha256': sha(self.model / 'model.json')}))
        self.metadata = {('LME_001', 'candidate'): {'unit_id': 'LME_001', 'model_id': 'candidate',
            'model_path': (self.model / 'model.json').relative_to(self.root).as_posix(),
            'researcher_review_status': 'Validated by researcher', 'researcher_review_summary': '{}'}}
        self.review = {'status': 'Validated by researcher', 'excluded_group_ids': []}

    def launcher_review(self):
        from tools.project_core.validation.researcher_review import approved_review,read_report
        from tools.workflow_checks.validation.test_researcher_review_model_boundary import ModelBoundaryTests
        report=ModelBoundaryTests().report(self.root,'candidate')
        name,date,summary=read_report(self.root,report,'candidate')
        summary['excluded_group_ids']=[]
        metadata=list(self.metadata.values())[0]
        metadata.update(researcher_name=name,researcher_review_date=date,
                        researcher_review_summary=json.dumps(summary),
                        validation_report_path=report.relative_to(self.root).as_posix(),
                        validation_report_sha256=sha(report),reviewed_model_sha256=sha(self.model/'model.json'))
        return report,metadata,approved_review(self.root,metadata,self.book)

    def test_candidate_values_and_snapshot_identity_are_published_without_changing_default(self):
        series = {'default_model': 'other', 'models': [{'id': 'other', 'scopes': {'unchanged': 1}}]}
        network = {'default_model': 0, 'models': [{'id': 'other', 'scopes': {'unchanged': 2}}]}
        before = copy.deepcopy((series['models'][0], network['models'][0]))
        with patch('tools.project_core.maps.original_atlas_data.review_display', return_value=(self.review, None)):
            add_source_reviews(self.root, 'LME_001', self.metadata, (series, network))
        candidate = series['models'][1]
        self.assertEqual(candidate['scopes']['all']['methods']['new_GE']['ppr'], [15.] * 70)
        self.assertEqual(candidate['scopes']['all']['methods']['new_GE']['status'], 'provisional: WARN')
        self.assertEqual(candidate['workbook'], self.snapshot.relative_to(self.root).as_posix())
        self.assertEqual(candidate['workbook_sha256'], sha(self.snapshot))
        self.assertEqual(network['models'][1]['scopes']['all']['values'], [[3., 10.]])
        self.assertEqual(before, (series['models'][0], network['models'][0]))
        self.assertEqual((series['default_model'], network['default_model']), ('other', 0))

    def test_changed_snapshot_is_rejected_before_any_candidate_payload_is_added(self):
        self.snapshot.write_bytes(self.snapshot.read_bytes() + b'changed')
        payloads = ({'models': []}, {'models': []})
        with patch('tools.project_core.maps.original_atlas_data.review_display', return_value=(self.review, None)):
            with self.assertRaisesRegex(ValueError, 'snapshot'):
                add_source_reviews(self.root, 'LME_001', self.metadata, payloads)
        self.assertEqual(payloads, ({'models': []}, {'models': []}))

    def test_launcher_detects_candidate_change_without_project_change(self):
        from tools.project_core.maps.build_html import _stale_reviewed_payload_units
        regional=self.root/'regions/LME/LME_001/LME_001.xlsx';regional.write_bytes(self.snapshot.read_bytes())
        saved={'id':'candidate','workbook_sha256':sha(self.snapshot)}
        catalog={'network':{'units':{'LME_001':{'models':[saved]}}}}
        series={'units':{'LME_001':{'models':[saved]}}}
        self.snapshot.write_bytes(self.snapshot.read_bytes()+b'new calculation package')
        with patch('tools.project_core.maps.original_atlas_data.embedded',side_effect=[(catalog,None),(series,None)]):
            changed=_stale_reviewed_payload_units(self.root,self.root/'interactive_map',list(self.metadata.values()))
        self.assertEqual(changed,{'LME_001'})

    def test_launcher_rechecks_signed_report_even_when_project_and_snapshot_are_unchanged(self):
        from tools.project_core.maps.build_html import _stale_reviewed_payload_units
        regional=self.root/'regions/LME/LME_001/LME_001.xlsx';regional.write_bytes(self.snapshot.read_bytes())
        from tools.project_core.validation.researcher_review import review_display
        report,metadata,review=self.launcher_review();original=report.read_bytes()
        saved={'id':'candidate','workbook_sha256':sha(self.snapshot),'researcher_review':review}
        catalog={'network':{'units':{'LME_001':{'models':[saved]}}}}
        series={'units':{'LME_001':{'models':[saved]}}}
        def check():
            with patch('tools.project_core.maps.original_atlas_data.embedded',side_effect=[(catalog,None),(series,None)]):
                return _stale_reviewed_payload_units(self.root,self.root/'interactive_map',[metadata])
        self.assertEqual(check(),set())
        report.write_bytes(b'new researcher corrections, not registered')
        self.assertEqual(check(),{'LME_001'})
        saved.pop('researcher_review')
        saved['recorded_review_pending']=review_display(self.root,metadata,self.book)[1]
        self.assertEqual(check(),set())
        report.write_bytes(original)
        self.assertEqual(check(),{'LME_001'})

    def test_changed_independent_inputs_publish_coefficients_without_stale_annual_results(self):
        current=copy.deepcopy(self.book);current['NPP']['NPP'][1][0][-1]=200.
        series={'default_model':'other','models':[{'id':'other','scopes':{'untouched':1}}]}
        network={'default_model':0,'models':[{'id':'other','scopes':{'untouched':2}}]}
        with patch('tools.project_core.maps.original_atlas_data.review_display',return_value=(self.review,None)):
            add_source_reviews(self.root,'LME_001',self.metadata,(series,network),current)
        candidate=series['models'][1]
        self.assertEqual(candidate['scopes'],{})
        self.assertFalse(candidate['verified'])
        self.assertIn('independent regional inputs changed',candidate['arithmetic_unavailable_reason'])
        self.assertEqual(candidate['group_data']['scopes']['all'],[[3.]])
        self.assertEqual(network['models'][1]['scopes'],{})
        self.assertEqual((series['default_model'],network['default_model']),('other',0))

    def test_launcher_ignores_calculation_manifest_for_validation_and_recovers_old_pending(self):
        from tools.project_core.maps.build_html import _stale_reviewed_payload_units
        regional=self.root/'regions/LME/LME_001/LME_001.xlsx';regional.write_bytes(self.snapshot.read_bytes())
        _,metadata,review=self.launcher_review()
        manifest=self.model/'results/result_manifest.json'
        saved={'id':'candidate','workbook_sha256':sha(self.snapshot),
               'researcher_review':review}
        catalog={'network':{'units':{'LME_001':{'models':[saved]}}}}
        series={'units':{'LME_001':{'models':[saved]}}}
        def check():
            with patch('tools.project_core.maps.original_atlas_data.embedded',side_effect=[(catalog,None),(series,None)]):
                return _stale_reviewed_payload_units(self.root,self.root/'interactive_map',list(self.metadata.values()))
        self.assertEqual(check(),set())
        manifest.write_text('{}')
        self.assertEqual(check(),set())
        manifest.unlink()
        self.assertEqual(check(),set())
        saved.pop('researcher_review')
        saved['recorded_review_pending']={'reason':'Researcher review calculation inputs changed; missing method extension evidence'}
        self.assertEqual(check(),{'LME_001'})

    def test_saved_pending_allocation_state_remains_coefficient_only_after_current_inputs_copy(self):
        from tools.project_core.calculations.coverage_candidates import prepare_candidate_book,suppress_candidate_arithmetic
        current=copy.deepcopy(self.book)
        for row in current['Catch']['Catch'][1]:row[0]='new fish'
        prepared=prepare_candidate_book(self.book,current)
        book=prepared['book'];suppress_candidate_arithmetic(book,prepared['pending_reason'])
        write_book(self.snapshot,book)
        manifest_path=self.model/'results/result_manifest.json'
        manifest=json.loads(manifest_path.read_text());manifest['snapshot_sha256']=sha(self.snapshot)
        manifest_path.write_text(json.dumps(manifest))
        payloads=({'models':[]},{'models':[]})
        with patch('tools.project_core.maps.original_atlas_data.review_display',return_value=(None,None)):
            add_source_reviews(self.root,'LME_001',self.metadata,payloads,current)
        candidate=payloads[0]['models'][0]
        self.assertEqual(candidate['scopes'],{})
        self.assertEqual(candidate['group_data']['scopes']['all'],[[3.]])
        self.assertIn('taxon set changed',candidate['arithmetic_unavailable_reason'])


if __name__ == '__main__':
    unittest.main()
