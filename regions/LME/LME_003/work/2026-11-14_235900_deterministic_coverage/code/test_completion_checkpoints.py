import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0, str(ROOT))
import completion_checkpoints as cp
from tools.project_core.registry.publication import PublicationBackup, publication_transaction, guarded_replace

class Checkpoints(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.model = self.root/'regions/LME/X/papers/P/models/M'
        self.model.mkdir(parents=True)
        self.plan = {'pair': ('X', 'M'), 'model': self.model/'model.json',
                     'source': self.model/'sppr_source.xlsx',
                     'manifest': self.model/'results/result_manifest.json',
                     'regional': self.root/'regions/LME/X/X.xlsx'}
        self.paths = [self.plan['source'], self.plan['manifest'], self.plan['regional'], self.model/'results/regional_snapshot.xlsx']
        for p in self.paths:
            p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b'original')
        self.plan['model'].write_bytes(b'input')
        self.cache = self.root/'work/cache'
        self.bindings = {'identity': ['X', 'M'], 'inputs': {self.plan['model'].relative_to(self.root).as_posix(): cp.digest(self.plan['model'])},
                         'destinations': {p.relative_to(self.root).as_posix(): cp.digest(p) for p in self.paths}}
        self.reports = [{'methods': ['new'], 'execution_context': 'already stamped'}]

    def capture(self):
        for p in self.paths: p.write_bytes(b'complete')
        self.plan['manifest'].write_text(json.dumps({'already_stamped': True}))
        return cp.capture_model_checkpoint(self.root, self.plan, self.cache, self.bindings, self.reports, {p:cp.digest(p) for p in self.paths})

    def reset(self):
        for p in self.paths: p.write_bytes(b'original')

    def transaction(self):
        return publication_transaction(self.root, extra_region_paths=[self.plan['regional']], extra_model_dirs=[self.model])

    def test_restore_no_execution_and_exact_manifest(self):
        self.capture(); expected=self.plan['manifest'].read_bytes(); self.reset()
        checkpoint=cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings)
        with self.transaction() as pub:
            pub.journal_path=self.root/'journal.jsonl'
            with patch('tools.project_core.calculations.coverage._complete_model',side_effect=AssertionError('must not execute')):
                reports=cp.restore_model_checkpoint(self.root,self.plan,checkpoint,pub)
        self.assertEqual(expected,self.plan['manifest'].read_bytes())
        self.assertEqual(self.reports,reports['batch_reports'])
        self.assertTrue(reports['cache_restoration']['no_execution'])

    def test_missing_and_partial_seal_rejected(self):
        self.assertIsNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings))
        seal=self.capture(); seal.unlink(); self.reset()
        self.assertIsNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings))

    def test_corrupt_blob_rejected(self):
        seal=self.capture(); data=json.loads(seal.read_text()); self.reset()
        (seal.parent/'objects'/data['files'][0]['after_sha256']).write_bytes(b'bad')
        self.assertIsNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings))

    def test_changed_input_rejected(self):
        self.capture();self.reset();self.plan['model'].write_bytes(b'human')
        self.assertIsNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings))

    def test_wrong_identity_and_binding_rejected(self):
        self.capture();self.reset()
        for key,value in [('identity',['Y','M'])]:
            bindings={**self.bindings,key:value}
            self.assertIsNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,bindings))
        with self.assertRaisesRegex(RuntimeError,'explicit narrow compatibility'):
            cp.load_model_checkpoint(self.root,self.plan,self.cache,{**self.bindings,'producer':{'different':'hash'}})

    def test_concurrent_destination_preserved(self):
        self.capture(); self.reset(); checkpoint=cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings)
        self.plan['source'].write_bytes(b'human')
        with self.assertRaises(ValueError), self.transaction() as pub:
            cp.restore_model_checkpoint(self.root,self.plan,checkpoint,pub)
        self.assertEqual(b'human',self.plan['source'].read_bytes())

    def test_exception_after_replace_claims_only_exact_bytes_and_rolls_back(self):
        self.capture();self.reset();checkpoint=cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings)
        original=__import__('os').replace
        def interrupted(source,destination):
            original(source,destination)
            raise RuntimeError('interrupted immediately after replace')
        with self.assertRaisesRegex(RuntimeError,'interrupted'), self.transaction() as pub:
            pub.journal_path=self.root/'journal.jsonl'
            with patch('tools.project_core.registry.publication.os.replace',side_effect=interrupted):
                cp.restore_model_checkpoint(self.root,self.plan,checkpoint,pub)
        self.assertTrue(all(p.read_bytes()==b'original' for p in self.paths))
        self.assertIsNotNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings))
        self.assertIn('intent',(self.root/'journal.jsonl').read_text())

    def test_external_edit_after_replace_preserved(self):
        dest=self.plan['source']; staged=dest.with_suffix('.tmp');staged.write_bytes(b'ours')
        original=__import__('os').replace
        def raced(source,destination):
            original(source,destination);Path(destination).write_bytes(b'human');raise RuntimeError('race')
        with self.assertRaises(Exception),self.transaction() as pub:
            with patch('tools.project_core.registry.publication.os.replace',side_effect=raced):
                guarded_replace(staged,dest,expected_sha256=cp.digest(dest))
        self.assertEqual(dest.read_bytes(),b'human')

    def test_persistent_denial_does_not_claim_write(self):
        dest=self.plan['source'];staged=dest.with_suffix('.tmp');staged.write_bytes(b'ours')
        with self.assertRaises(PermissionError),self.transaction():
            with patch('tools.project_core.registry.publication._replacement_access',return_value={'delete_access':False,'own_open_handles':[]}),patch('tools.project_core.registry.publication.os.replace',side_effect=PermissionError(5,'denied')) as replace:
                guarded_replace(staged,dest,expected_sha256=cp.digest(dest))
        self.assertEqual(1,replace.call_count)
        self.assertEqual(b'original',dest.read_bytes())

    def test_unexpected_new_destination_rejected(self):
        extra=self.model/'results/diagnostics/method_coverage/new.json';extra.parent.mkdir(parents=True);extra.write_bytes(b'new')
        self.paths.append(extra);self.capture();self.reset();extra.write_bytes(b'human')
        self.assertIsNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings))

    def test_late_failure_rolls_back_but_preserves_checkpoint(self):
        self.capture();self.reset();checkpoint=cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings)
        with self.assertRaises(RuntimeError),self.transaction() as pub:
            cp.restore_model_checkpoint(self.root,self.plan,checkpoint,pub)
            raise RuntimeError('late publication failure')
        self.assertTrue(all(p.read_bytes()==b'original' for p in self.paths))
        self.assertIsNotNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings))

    def test_durable_intent_recognizes_hard_interruption_and_preserves_other_bytes(self):
        dest=self.plan['source']; name=dest.relative_to(self.root).as_posix(); before=cp.digest(dest)
        journal=self.root/'journal.jsonl';after=hashlib.sha256(b'ours').hexdigest()
        journal.write_text(json.dumps({'event':'intent','path':name,'before_sha256':before,'after_sha256':after})+'\n')
        dest.write_bytes(b'ours')
        self.assertEqual('task_owned',cp.reconcile_ownership(self.root,journal,{name:before},{name})[0]['state'])
        dest.write_bytes(b'human')
        self.assertEqual('external_conflict',cp.reconcile_ownership(self.root,journal,{name:before},{name})[0]['state'])

    def test_new_evidence_is_packaged_and_immutable_reference_bound(self):
        evidence=self.model/'results/diagnostics/method_coverage/new.json'; evidence.parent.mkdir(parents=True);evidence.write_bytes(b'evidence')
        for p in self.paths:p.write_bytes(b'complete')
        self.plan['manifest'].write_text(json.dumps({'method_coverage':{'methods':{'new':{'evidence':{'path':'method_coverage/new.json','sha256':cp.digest(evidence),'availability':'present'}}}}}))
        seal=cp.capture_model_checkpoint(self.root,self.plan,self.cache,self.bindings,self.reports,{p:cp.digest(p) for p in [*self.paths,evidence]})
        data=json.loads(seal.read_text());self.assertIn(evidence.relative_to(self.root).as_posix(),{x['path'] for x in data['files']})

    def test_corrupt_seal_with_missing_file_rejected(self):
        seal=self.capture();data=json.loads(seal.read_text());data['files'].pop();seal.write_text(json.dumps(data));self.reset()
        self.assertIsNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings))

    def test_concurrent_edit_between_verification_and_capture_rejected(self):
        self.capture();expected={p:cp.digest(p) for p in self.paths};self.plan['source'].write_bytes(b'human')
        with self.assertRaisesRegex(ValueError,'after its verified write'):
            cp.capture_model_checkpoint(self.root,self.plan,self.cache,self.bindings,self.reports,expected)

    def test_malformed_seal_shapes_rejected(self):
        for malformed in (None, [], {'schema_version':1,'files':None}):
            seal=self.capture();seal.write_text(json.dumps(malformed));(seal.parent/'manifest.sha256').write_text(cp.digest(seal));self.reset()
            self.assertIsNone(cp.load_model_checkpoint(self.root,self.plan,self.cache,self.bindings))

    def test_journal_intent_before_second_replace_recognizes_first_write(self):
        dest=self.plan['source'];name=dest.relative_to(self.root).as_posix();before=cp.digest(dest)
        first=hashlib.sha256(b'first').hexdigest();second=hashlib.sha256(b'second').hexdigest()
        journal=self.root/'journal.jsonl'
        journal.write_text('\n'.join(json.dumps({'event':'intent','path':name,'before_sha256':a,'after_sha256':b}) for a,b in [(before,first),(first,second)])+'\n')
        dest.write_bytes(b'first')
        self.assertEqual('task_owned',cp.reconcile_ownership(self.root,journal,{name:before},{name})[0]['state'])

    def test_bind_existing_manifest_execution_evidence_before_capture(self):
        evidence=self.model/'results/diagnostics/ee_floor/runtime.json.gz';evidence.parent.mkdir(parents=True);evidence.write_bytes(b'original runtime')
        self.plan['manifest'].write_text(json.dumps({'method_coverage':{'execution_evidence':{'ee_floor_migration':{'path':'ee_floor/runtime.json.gz','sha256':cp.digest(evidence)}}}}))
        project=self.root/'Project.xlsx';project.write_bytes(b'project')
        plan={**self.plan,'metadata':{},'wanted':['new'],'batches':[]}
        consumed={p:cp.digest(p) for p in [*self.paths,self.plan['model'],project]}
        bindings=cp.make_bindings(self.root,plan,consumed,{}, {})
        self.assertEqual(cp.digest(evidence),bindings['inputs'].get(evidence.relative_to(self.root).as_posix()))

    def test_transient_denial_retries_only_after_native_access_confirmation(self):
        dest=self.plan['source'];staged=dest.with_suffix('.tmp');staged.write_bytes(b'ours');original=__import__('os').replace
        attempts=[]
        def transient(a,b):
            attempts.append(1)
            if len(attempts)==1:raise PermissionError(5,'transient')
            return original(a,b)
        with patch('tools.project_core.registry.publication._replacement_access',return_value={'delete_access':True,'own_open_handles':[]},create=True), patch('tools.project_core.registry.publication.os.replace',side_effect=transient):
            guarded_replace(staged,dest,expected_sha256=cp.digest(dest))
        self.assertEqual(2,len(attempts));self.assertEqual(b'ours',dest.read_bytes())

    def test_concurrent_change_during_denial_blocks_retry(self):
        dest=self.plan['source'];staged=dest.with_suffix('.tmp');staged.write_bytes(b'ours')
        def changed(path):path.write_bytes(b'human');return {'delete_access':True,'own_open_handles':[]}
        with self.assertRaises(ValueError),patch('tools.project_core.registry.publication._replacement_access',side_effect=changed,create=True),patch('tools.project_core.registry.publication.os.replace',side_effect=PermissionError(5,'denied')) as replace:
            guarded_replace(staged,dest,expected_sha256=cp.digest(dest))
        self.assertEqual(1,replace.call_count);self.assertEqual(b'human',dest.read_bytes())

    def test_persistent_denial_with_access_stops_after_three_calls(self):
        dest=self.plan['source'];staged=dest.with_suffix('.tmp');staged.write_bytes(b'ours')
        with self.assertRaises(PermissionError),patch('tools.project_core.registry.publication._replacement_access',return_value={'delete_access':True,'own_open_handles':[]}),patch('tools.project_core.registry.publication.os.replace',side_effect=PermissionError(5,'denied')) as replace:
            guarded_replace(staged,dest,expected_sha256=cp.digest(dest))
        self.assertEqual(3,replace.call_count);self.assertEqual(b'original',dest.read_bytes())

    def test_explicit_producer_compatibility_restores_original_stamped_bytes(self):
        producer=self.root/'producer.py';producer.write_bytes(b'old IO only');old_hash=cp.digest(producer)
        self.bindings['producer']={'producer.py':old_hash};self.bindings['inputs']['producer.py']=old_hash
        self.capture();expected=self.plan['manifest'].read_bytes();self.reset()
        archive=self.root/'original_producer.py';archive.write_bytes(producer.read_bytes());producer.write_bytes(b'new IO only')
        current={**self.bindings,'producer':{'producer.py':cp.digest(producer)},'inputs':{**self.bindings['inputs'],'producer.py':cp.digest(producer)}}
        certificate={'records':[{'original_producer':self.bindings['producer'],'current_producer':current['producer'],'reason':'IO only','verification':'focused tests','original_source_evidence':{'producer.py':{'path':'original_producer.py','sha256':old_hash}}}]}
        (self.cache.parent/'checkpoint_producer_compatibility.json').write_text(json.dumps(certificate))
        checkpoint=cp.load_model_checkpoint(self.root,self.plan,self.cache,current)
        self.assertIsNotNone(checkpoint)
        with self.transaction() as pub:cp.restore_model_checkpoint(self.root,self.plan,checkpoint,pub)
        self.assertEqual(expected,self.plan['manifest'].read_bytes())

if __name__ == '__main__': unittest.main()
