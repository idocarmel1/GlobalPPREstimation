import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import hashlib

HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('check_evidence',HERE/'check_evidence.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.file=self.root/'return.json';self.file.write_text('{}')
        self.index={'schema_version':1,'run_id':'test','region_id':'R','model_id':'M','variant_id':'source',
                    'source_identity':'source1','computational_input_identity':'input1','methods':['GE'],
                    'required_roles':['full_return','source_matrix'],
                    'artifacts':[{'role':'full_return','path':'return.json','sha256':hashlib.sha256(b'{}').hexdigest(),'availability':'present'}]}
    def tearDown(self):self.temp.cleanup()
    def run_check(self):
        path=self.root/'index.json';path.write_text(json.dumps(self.index));return module.check(path)
    def test_aggregate_only_is_incomplete(self):
        result=self.run_check();self.assertFalse(result['complete']);self.assertIn('source_matrix',result['missing_roles'])
    def test_tamper_rejected(self):
        self.index['required_roles']=['full_return'];self.file.write_text('{"changed":true}')
        self.assertFalse(self.run_check()['complete'])
    def test_missing_record_needs_reason(self):
        self.index['artifacts'].append({'role':'source_matrix','availability':'missing'})
        self.assertTrue(any('reason' in x for x in self.run_check()['errors']))
    def test_declared_missing_stays_incomplete(self):
        self.index['artifacts'].append({'role':'source_matrix','availability':'missing','reason':'old export omitted','acquisition_status':'pending authorized run'})
        self.assertFalse(self.run_check()['complete'])
    def test_present_complete(self):
        self.index['required_roles']=['full_return'];self.assertTrue(self.run_check()['complete'])
    def test_forbidden_basename_never_read(self):
        self.index['artifacts'][0]['path']='notes for AI.txt'
        self.assertTrue(any('excluded basename' in x for x in self.run_check()['errors']))
    def test_absolute_link_rejected(self):
        self.index['artifacts'][0]['path']=str(self.file.resolve())
        self.assertFalse(self.run_check()['complete'])
    def test_failed_reconciliation_prevents_completion(self):
        self.index['required_roles']=['full_return'];self.index['reconciliation']={'scope_sums':False}
        self.assertFalse(self.run_check()['complete'])
    def test_null_roles_returns_incomplete(self):
        self.index['required_roles']=None;self.assertFalse(self.run_check()['complete'])
    def test_nonstring_roles_returns_incomplete(self):
        self.index['required_roles']=[{}];self.assertFalse(self.run_check()['complete'])
    def test_null_reconciliation_returns_incomplete(self):
        self.index['reconciliation']=None;self.assertFalse(self.run_check()['complete'])
    def test_empty_model_identity_is_incomplete(self):
        self.index['required_roles']=['full_return'];self.index['model_id']=''
        self.assertFalse(self.run_check()['complete'])
    def test_null_source_identity_is_incomplete(self):
        self.index['required_roles']=['full_return'];self.index['source_identity']=None
        self.assertFalse(self.run_check()['complete'])
    def test_invalid_methods_is_incomplete(self):
        self.index['required_roles']=['full_return'];self.index['methods']=None
        self.assertFalse(self.run_check()['complete'])
    def test_nonobject_index_is_incomplete(self):
        self.index=None;self.assertFalse(self.run_check()['complete'])
    def test_drive_relative_path_rejected(self):
        self.index['required_roles']=['full_return'];self.index['artifacts'][0]['path']='C:return.json'
        self.assertTrue(any('nonportable' in e for e in self.run_check()['errors']))
    def test_rooted_windows_path_rejected(self):
        self.index['required_roles']=['full_return'];self.index['artifacts'][0]['path']='\\return.json'
        self.assertTrue(any('nonportable' in e for e in self.run_check()['errors']))

if __name__=='__main__':unittest.main()
