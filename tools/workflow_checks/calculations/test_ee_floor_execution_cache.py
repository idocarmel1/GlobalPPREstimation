"""Publication retries reuse executed draws, never infer execution from metadata."""
import base64
import copy
import gzip
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


class EEFloorExecutionCacheTests(unittest.TestCase):
    def helper(self):
        name='tools.project_core.calculations.ee_floor_execution'
        self.assertIsNotNone(importlib.util.find_spec(name),'Durable EE-floor execution cache is missing')
        return __import__(name,fromlist=['cache'])

    def test_retry_reuses_identical_execution_but_rejects_changed_inputs_or_evidence(self):
        helper=self.helper()
        from tools.project_core.workbooks.workbooks import sha
        with tempfile.TemporaryDirectory() as temporary:
            model=Path(temporary)/'model';model.mkdir();(model/'model.json').write_text('{}')
            staged=Path(temporary)/'staged';staged.mkdir();evidence=staged/'MC_new_GE.json.gz'
            evidence.write_bytes(b'exact individual random draws and full return')
            context={'model_sha256':sha(model/'model.json'),'flags':{'constructor':{'ee_floor':.1}},
                     'code_identity':{'PPRCalculator.py':'old','calculation/PPRCalculator.py':'new'},
                     'adapter_sha256':'same','dependencies':{'numpy':'same'}}
            settings={'MC_new_GE':{'method':'MC_new_GE','kwargs':{'n_samples':75},'seed':None}}
            calculated={'model_sha256':context['model_sha256'],'methods':{'MC_new_GE':{'status':'ok',
                'settings':settings['MC_new_GE'],'evidence':{'path':evidence.name,'sha256':sha(evidence)}}}}
            reference=helper.save_execution(model,context,['MC_new_GE'],settings,calculated,staged)
            evidence.unlink();reuse=Path(temporary)/'reuse';reuse.mkdir()
            restored=helper.load_execution(model,context,['MC_new_GE'],settings,reuse)
            self.assertEqual(restored['calculated'],calculated)
            self.assertEqual((reuse/evidence.name).read_bytes(),b'exact individual random draws and full return')
            for changed in ({**context,'flags':{}},{**context,'dependencies':{}},{**context,'code_identity':{}}):
                self.assertIsNone(helper.load_execution(model,changed,['MC_new_GE'],settings,reuse))
            self.assertIsNone(helper.load_execution(model,context,['MC_new_GE'],{'MC_new_GE':{'seed':4}},reuse))
            path=model/reference['path']
            with gzip.open(path,'rt',encoding='utf-8') as stream:package=json.load(stream)
            package['files'][evidence.name]['base64']=base64.b64encode(b'tampered draws').decode('ascii')
            path.write_bytes(gzip.compress(json.dumps(package).encode('utf-8'),mtime=0))
            with self.assertRaisesRegex(ValueError,'evidence'):
                helper.load_execution(model,context,['MC_new_GE'],settings,reuse)

    def test_complete_constructor_and_index_evidence_and_bounded_cleanup(self):
        helper=self.helper()
        from tools.project_core.workbooks.workbooks import sha
        with tempfile.TemporaryDirectory() as temporary:
            model=Path(temporary)/'model';model.mkdir();(model/'model.json').write_text('{}')
            staged=Path(temporary)/'staged';staged.mkdir()
            context={'model_sha256':sha(model/'model.json'),'flags':{},'code_identity':{},'adapter_sha256':'same'}
            settings={'MC_new_GE':{'kwargs':{'n_samples':75}}}
            def evidence(name):
                path=staged/name;path.write_bytes(name.encode())
                return {'path':name,'sha256':sha(path)}
            calculated={'methods':{'MC_new_GE':{'settings':settings['MC_new_GE'],'evidence':evidence('method.json.gz')}},
                        'constructor_evidence':evidence('constructor.json.gz'),'evidence_index':evidence('index.json.gz')}
            reference=helper.save_execution(model,context,['MC_new_GE'],settings,calculated,staged)
            reuse=Path(temporary)/'reuse';reuse.mkdir()
            restored=helper.load_execution(model,context,['MC_new_GE'],settings,reuse)
            self.assertEqual(restored['calculated'],calculated)
            self.assertEqual({p.name:p.read_bytes() for p in reuse.iterdir()},
                             {p.name:p.read_bytes() for p in staged.iterdir()})
            path=model/reference['path'];author=path.parent.parent/'qa/author-note.txt'
            author.parent.mkdir();author.write_text('preserved author work')
            helper.discard_execution(model,reference)
            self.assertFalse(path.exists());self.assertEqual(author.read_text(),'preserved author work')
            with self.assertRaisesRegex(ValueError,'bounded'):
                helper.discard_execution(model,{'path':'model.json','sha256':sha(model/'model.json')})

    def test_compact_outcome_tampering_does_not_restore_evidence(self):
        helper=self.helper()
        from tools.project_core.workbooks.workbooks import sha
        with tempfile.TemporaryDirectory() as temporary:
            model=Path(temporary)/'model';model.mkdir();(model/'model.json').write_text('{}')
            staged=Path(temporary)/'staged';staged.mkdir();evidence=staged/'MC_new_GE.json.gz';evidence.write_bytes(b'draws')
            context={'model_sha256':sha(model/'model.json')};settings={'MC_new_GE':{'kwargs':{'n_samples':100}}}
            calculated={'methods':{'MC_new_GE':{'status':'ok','evidence':{'path':evidence.name,'sha256':sha(evidence)}}}}
            reference=helper.save_execution(model,context,['MC_new_GE'],settings,calculated,staged)
            path=model/reference['path'];package=json.loads(gzip.decompress(path.read_bytes()))
            package['calculated']['methods']['MC_new_GE']['status']='failed'
            path.write_bytes(gzip.compress(json.dumps(package).encode(),mtime=0))
            reuse=Path(temporary)/'reuse';reuse.mkdir()
            with self.assertRaisesRegex(ValueError,'package changed'):
                helper.load_execution(model,context,['MC_new_GE'],settings,reuse)
            self.assertEqual(list(reuse.iterdir()),[])

    def test_pending_draws_survive_publication_rollback_without_changing_adopted_artifacts(self):
        helper=self.helper()
        from tools.project_core.registry.publication import publication_transaction
        from tools.project_core.workbooks.workbooks import write_book,sha
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);model=root/'model';model.mkdir();(model/'model.json').write_text('{}')
            write_book(root/'Project.xlsx',{'Models & coverage':{'Models':(['unit_id','model_id'],[])}})
            source=model/'sppr_source.xlsx';source.write_bytes(b'original adopted source')
            staged=root/'staged';staged.mkdir();evidence=staged/'MC_new_GE.json';evidence.write_bytes(b'fresh draws')
            context={'model_sha256':sha(model/'model.json')}; settings={'MC_new_GE':{'kwargs':{'n_samples':100}}}
            calculated={'methods':{'MC_new_GE':{'evidence':{'path':evidence.name,'sha256':sha(evidence)}}}}
            with self.assertRaisesRegex(RuntimeError,'metadata publication failed'):
                with publication_transaction(root,extra_model_dirs=[model]) as publication:
                    reference=helper.save_execution(model,context,['MC_new_GE'],settings,calculated,staged)
                    source.write_bytes(b'generated adopted source');publication.checkpoint([source])
                    raise RuntimeError('metadata publication failed')
            self.assertEqual(source.read_bytes(),b'original adopted source')
            self.assertTrue((model/reference['path']).is_file())

    def test_metadata_failure_retry_reuses_exact_completed_execution(self):
        import pandas as pd
        from unittest.mock import patch
        from tools.project_core.calculations import coverage
        from tools.project_core.calculations.ee_floor_migration import target_flags
        from tools.project_core.workbooks.workbooks import sha
        from tools.workflow_checks.calculations.test_coverage_preservation import CoveragePreservationTests
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);model,path,_,metadata=CoveragePreservationTests().package(root)
            flags={'constructor':{},'mc':{'n_samples':75}}
            settings={'method':'MC_new_GE','kwargs':{'n_samples':75},'seed':None}
            migration={'flags':target_flags(flags,True,.1,'a'*64),'compatible':{},
                'effective_groups':pd.DataFrame({'group_name':['Fish'],'ee':[.1]},index=[1]),
                'before_runtime':{},'after_runtime':{},'old_warnings':[],'new_warnings':[],
                'info':{'use_ee_floor':True,'ee_floor':.1},'ledger':pd.DataFrame(),
                'calculation_code':b'current calculator'}
            def context(root,model_path,resolved):
                return {'model_sha256':sha(model_path),'flags':resolved,'code_identity':{},'adapter_sha256':'same'}
            calls=[]
            def executor(model_path,resolved,keys,directory,progress):
                calls.append(keys)
                evidence=directory/'MC_new_GE.json';evidence.write_bytes(b'exact completed random draw evidence')
                return {'methods':{'MC_new_GE':{'status':'ok','settings':copy.deepcopy(settings),
                    'scopes':{scope:{'Fish':7.} for scope in ('all','inner','PP')},
                    'annual_status':{scope:'ok' for scope in ('all','inner','PP')},
                    'evidence':{'path':evidence.name,'sha256':sha(evidence)}}}}
            original={p:p.read_bytes() for p in [path,model/'sppr_source.xlsx',
                       model/'results/regional_snapshot.xlsx',model/'results/result_manifest.json'] if p.exists()}
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration',return_value=flags), \
                 patch.object(coverage,'_context',side_effect=context), \
                 patch('tools.project_core.calculations.ee_floor_migration.prepare',return_value=migration), \
                 patch('tools.scientific_helpers.sppr.method_coverage.method_settings',return_value=settings):
                with patch.object(coverage,'_update_source',side_effect=ValueError('metadata publication failed')), \
                     self.assertRaisesRegex(ValueError,'metadata publication failed'):
                    coverage._complete_model(root,metadata,('MC_new_GE',),progress=lambda value:None,
                        compute=executor,ee_floor={'use_ee_floor':True,'ee_floor':.1})
                self.assertEqual({p:p.read_bytes() for p in original},original)
                changed,report=coverage._complete_model(root,metadata,('MC_new_GE',),progress=lambda value:None,
                    compute=executor,ee_floor={'use_ee_floor':True,'ee_floor':.1})
            self.assertTrue(changed)
            self.assertEqual(calls,[['MC_new_GE']],'Publication retry must not redraw completed Monte Carlo')
            self.assertTrue((model/report['execution_cache']['path']).is_file())
            evidence=model/'results/diagnostics'/report['methods']['MC_new_GE']['evidence']['path']
            self.assertEqual(evidence.read_bytes(),b'exact completed random draw evidence')


if __name__=='__main__':unittest.main()
