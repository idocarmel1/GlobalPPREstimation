"""Recover exact archived dependency locations without changing scientific options."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from tools.project_core.calculations import coverage


class ExecutionDependencyRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.model=Path(self.tmp.name)
        (self.model/'model.json').write_text('{}',encoding='utf-8')
        self.hash=hashlib.sha256(b'{}').hexdigest()
        self.original={'constructor':{'underdetermined':False,'zero_catch':False},
                       'diagnostics':{'det_collapse_mode':'never'},'engine_source_hashes':{}}
        self.supplied=copy.deepcopy(self.original)
        self.supplied['engine_sources']={}
        for name in ('PPRCalculator.py','ModelData.py','utils.py'):
            target=self.model/name;target.write_text('# exact recorded '+name,encoding='utf-8')
            digest=hashlib.sha256(target.read_bytes()).hexdigest()
            self.original['engine_source_hashes'][name]=digest
            self.supplied['engine_source_hashes'][name]=digest
            self.supplied['engine_sources'][name]=name
        self.manifest={'canonical_model_sha256':self.hash,'effective_flags':self.original}
        self.book={'Overview':{'Settings':(['field','value'],[
            ['results_model_id',self.model.name],['results_model_sha256',self.hash],
            ['effective_loader_flags',json.dumps(self.original)]])}}

    def recover(self):
        return coverage._recover_execution_configuration(self.model,self.book,self.manifest,self.supplied)

    def test_exact_new_dependency_paths_preserve_recorded_options(self):
        result=self.recover()
        self.assertEqual(result['constructor'],self.original['constructor'])
        self.assertEqual(result['diagnostics'],self.original['diagnostics'])
        self.assertEqual(set(result['engine_sources']),{'PPRCalculator.py','ModelData.py','utils.py'})

    def test_changed_constructor_cannot_use_dependency_recovery(self):
        self.supplied['constructor']['zero_catch']=True
        with self.assertRaisesRegex(ValueError,'contradicts'):self.recover()

    def test_changed_archived_bytes_are_rejected(self):
        (self.model/'ModelData.py').write_text('# changed',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):self.recover()

    def test_unknown_source_identity_is_not_repaired(self):
        self.manifest['canonical_model_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'model identity'):self.recover()

    def test_conflicting_saved_overview_is_not_overridden(self):
        original=copy.deepcopy(self.original);original['diagnostics']['det_collapse_mode']='auto'
        self.book['Overview']['Settings'][1][-1][1]=json.dumps(original)
        with self.assertRaisesRegex(ValueError,'contradicts'):self.recover()


if __name__=='__main__':unittest.main()
