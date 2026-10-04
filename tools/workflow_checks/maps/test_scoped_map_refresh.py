import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from tools.project_core.maps.original_atlas_data import verify_retained_unit
from tools.project_core.workbooks.workbooks import YEARS

class ScopedMapRefreshTests(unittest.TestCase):
    def setUp(self):
        self.region={'unit_id':'U','selected_model_id':'m','sha256':'saved'}
        self.record={'ppr':[2.,None]+[0.]*68,'status':'provisional: FAIL'}
        self.unit={'default_model':'m','models':[{'id':'m','workbook_sha256':'saved','scopes':{'all':{'methods':{'GE':self.record}}}}], 'npp':{'annual':[None]*70}}
        self.network={'models':[{'id':'m','workbook_sha256':'saved'}]}
        self.annual=[{'model_id':'m','scope':'all','method':'GE','unidentified':'method','catch_basis':'landings','metric':'ppr',**dict(zip(YEARS,self.record['ppr']))}]
    def check(self):verify_retained_unit(self.region,self.unit,self.network,self.annual,{'annual':[None]*70})
    def test_identical_registered_results_preserve_missingness_and_fail(self):
        before=copy.deepcopy((self.unit,self.network,self.annual));self.check()
        self.assertEqual(before,(self.unit,self.network,self.annual))
    def test_changed_annual_and_missingness_are_rejected(self):
        self.annual[0][1951]=0.
        with self.assertRaisesRegex(ValueError,'annual values changed'):self.check()
    def test_different_registered_workbook_is_rejected(self):
        self.region['sha256']='new'
        with self.assertRaisesRegex(ValueError,'selection or workbook'):self.check()
    def test_different_registered_selection_is_rejected(self):
        self.region['selected_model_id']='other'
        with self.assertRaisesRegex(ValueError,'selection or workbook'):self.check()
    def test_npp_changes_are_rejected(self):
        self.unit['npp']['annual'][0]=1.
        with self.assertRaisesRegex(ValueError,'NPP changed'):self.check()
