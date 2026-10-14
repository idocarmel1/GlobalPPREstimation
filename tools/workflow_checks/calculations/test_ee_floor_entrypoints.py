"""EE-floor command wiring and honest standalone resume on isolated model copies."""
import copy
import json
import sys
import tempfile
import unittest
import io
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / 'tools/scientific_code/PPREstimation'
sys.path.insert(0, str(ENGINE))
import create_PPRS_excel as cpe
from tools.project_core.calculations import run_region, coverage
from tools.project_core.workbooks.workbooks import read_book, write_book, overview, records, sha


class StandaloneFloorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.models = self.root / 'models'; self.models.mkdir()
        self.output = self.root / 'output'
        source = ROOT / 'common_reference_data/ecobase/source_data/ToyModels/900_900_Multi_DET_Toy_(2026).json'
        self.model = self.models / source.name
        self.model.write_bytes(source.read_bytes())

    def tearDown(self):
        self.temporary.cleanup()

    def test_load_and_export_honor_explicit_floor_and_record_identity(self):
        off, _ = cpe.load_model(str(self.model), use_ee_floor=False, ee_floor=.3)
        self.assertFalse(off.use_ee_floor)
        self.assertEqual(off.ee_floor, .3)
        result = cpe.write_model_excel(str(self.model), str(self.output),
            method_keys=('SPPR_1986',), method_timeout=None, use_ee_floor=True, ee_floor=.3)
        notes = cpe.read_pprs_excel(result)['run_notes']
        identity = json.loads(notes.loc['execution_identity', 'note'])
        self.assertTrue(identity['use_ee_floor'])
        self.assertEqual(identity['ee_floor'], .3)
        self.assertEqual(identity['method_keys'], ['SPPR_1986'])
        self.assertEqual(identity['canonical_model_sha256'], cpe._file_sha256(self.model))
        self.assertEqual(set(identity['code_identity']), {'PPRCalculator.py', 'ModelData.py', 'utils.py', 'create_PPRS_excel.py'})

    def test_resume_requires_same_source_flags_inventory_and_sampling(self):
        options = dict(method_keys=('SPPR_1986',), method_timeout=None, silent=True,
                       use_ee_floor=False, ee_floor=.1, mc_samples=7)
        initial = cpe.run_directory(str(self.models), str(self.output), **options)
        self.assertEqual(initial['n_written'], 1)
        same = cpe.run_directory(str(self.models), str(self.output), resume=True, **options)
        self.assertEqual(same['n_skipped'], 1)
        changed = cpe.run_directory(str(self.models), str(self.output), resume=True,
                                   **{**options, 'use_ee_floor':True})
        self.assertEqual(changed['n_written'], 1)
        sampling = cpe.run_directory(str(self.models), str(self.output), resume=True,
                                    **{**options, 'use_ee_floor':True, 'mc_samples':8})
        self.assertEqual(sampling['n_written'], 1)
        self.model.write_bytes(self.model.read_bytes() + b'\n')
        source = cpe.run_directory(str(self.models), str(self.output), resume=True,
                                  **{**options, 'use_ee_floor':True, 'mc_samples':8})
        self.assertEqual(source['n_written'], 1)
        inventory = cpe.run_directory(str(self.models), str(self.output), resume=True,
            **{**options, 'use_ee_floor':True, 'mc_samples':8, 'method_keys':('SPPR_1986','SPPR_1995_TE0.1')})
        self.assertEqual(inventory['n_written'], 1)

    def test_historical_missing_identity_and_changed_code_are_not_resumable(self):
        options = dict(method_keys=('SPPR_1986',), method_timeout=None, silent=True)
        cpe.run_directory(str(self.models), str(self.output), **options)
        result = self.output / (self.model.stem + '.xlsx')
        workbook = openpyxl.load_workbook(result)
        notes = workbook['run_notes']
        for row in list(notes):
            if row[0].value == 'execution_identity':
                notes.delete_rows(row[0].row)
                break
        workbook.save(result); workbook.close()
        legacy = cpe.run_directory(str(self.models), str(self.output), resume=True, **options)
        self.assertEqual(legacy['n_written'], 1)
        original = cpe._export_identity
        def changed(*args, **kwargs):
            identity = original(*args, **kwargs)
            identity['code_identity']['PPRCalculator.py'] = 'changed'
            return identity
        with patch.object(cpe, '_export_identity', side_effect=changed):
            code = cpe.run_directory(str(self.models), str(self.output), resume=True, **options)
        self.assertEqual(code['n_written'], 1)

    def test_invalid_threshold_is_rejected_even_when_off(self):
        for value in (-.1, 1.1, float('nan'), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                cpe.run_directory(str(self.models), str(self.output), use_ee_floor=False, ee_floor=value)

    def test_cli_floor_flags_reach_directory_runner(self):
        answer = {'n_written':0,'n_models':0,'n_skipped':0,'n_timeout':0,'n_failed':0,'report':'run.txt'}
        with patch.object(cpe,'run_directory',return_value=answer) as run:
            self.assertEqual(cpe.main(['input','output','--no-ee-floor','--ee-floor','.25','--timeout','none']),0)
            self.assertFalse(run.call_args.kwargs['use_ee_floor'])
            self.assertEqual(run.call_args.kwargs['ee_floor'], .25)
        with patch.object(cpe,'run_directory',return_value=answer) as run:
            cpe.main(['input','output','--use-ee-floor','--ee-floor=.4'])
            self.assertTrue(run.call_args.kwargs['use_ee_floor'])
            self.assertEqual(run.call_args.kwargs['ee_floor'], .4)


class RegionalFloorTests(unittest.TestCase):
    def package(self, root):
        from tools.workflow_checks.calculations.test_coverage_preservation import CoveragePreservationTests
        model, path, book, _ = CoveragePreservationTests().package(root)
        write_book(root/'Project.xlsx', {'Models & coverage':{'Models':(['unit_id','model_id','researcher_review_status'],[])}})
        return model, path, book

    def flags(self):
        return {'constructor':{'normalize_DC':True,'balance_BA_after_DC_normalization':False,
                              'use_ee_floor':False,'ee_floor':.1},
                'diagnostics':{'det_collapse_mode':'auto'},'mc':{'n_samples':75}}

    def executor(self, called):
        def run(model, flags, keys, directory, progress=print, *, method_timeout=None):
            called.append((copy.deepcopy(flags),list(keys),method_timeout))
            outcomes={}
            for key in keys:
                evidence=directory/(key+'.json'); evidence.write_text('isolated result',encoding='utf-8')
                outcomes[key]={'status':'ok','scopes':{scope:{'Fish':9.} for scope in ('all','inner','PP')},
                    'annual_status':{scope:'ok' for scope in ('all','inner','PP')},
                    'evidence':{'path':evidence.name,'sha256':sha(evidence)}}
            return {'methods':outcomes,'engine_hashes':{},'constructor':flags['constructor']}
        return run

    def test_regional_sppr_retains_audited_settings_and_source_tables(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); model,path,book=self.package(root); original=copy.deepcopy(book); called=[]
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration',return_value=self.flags()), \
                 patch('tools.scientific_helpers.sppr.method_coverage.compute_methods',side_effect=self.executor(called)), \
                 patch.object(coverage,'_context',return_value={'code_identity':{},'flags':self.flags()}), \
                 patch.object(cpe,'ALL_METHOD_KEYS',('new_GE','MC_new_GE')), \
                 patch.object(cpe,'load_model',side_effect=AssertionError('Stock loading is forbidden')):
                run_region.sppr(book,path,0)
            self.assertEqual(called[0][0],self.flags())
            self.assertEqual(called[0][2],0)
            saved=read_book(path)
            self.assertEqual(saved['Selected model groups']['Groups'],original['Selected model groups']['Groups'])
            for sheet,table in [('PPR','Matching'),('Catch','Catch'),('NPP','NPP')]:
                self.assertEqual(saved[sheet][table],original[sheet][table])
            self.assertEqual(json.loads(overview(saved)['effective_loader_flags']),self.flags())

    def test_unknown_audited_config_records_not_run_without_relabeling(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); model,path,book=self.package(root); original=copy.deepcopy(book)
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration',side_effect=ValueError('missing historical code')), \
                 patch('tools.scientific_helpers.sppr.method_coverage.compute_methods') as run, \
                 patch.object(cpe,'ALL_METHOD_KEYS',('new_GE','MC_new_GE')):
                run_region.sppr(book,path,0,use_ee_floor=True,ee_floor=.1)
            run.assert_not_called()
            saved=read_book(path)
            self.assertEqual(saved['Overview'],original['Overview'])
            self.assertEqual(saved['Selected model groups'],original['Selected model groups'])
            self.assertEqual(saved['PPR'],original['PPR'])
            attempted=records(saved,'Diagnostics','SPPR execution')
            self.assertEqual({row['status'] for row in attempted},{'NOT_RUN'})
            self.assertTrue(all('missing historical code' in row['reason'] for row in attempted))
            self.assertFalse((model/'sppr_source.xlsx').exists())

    def test_explicit_floor_keeps_unaffected_draw_and_existing_restrictions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); model,path,book=self.package(root); original=copy.deepcopy(book); called=[]
            for row in book['PPR']['Annual'][1]:
                if row[2]=='new_GE': row[6]='FAIL: historical diagnostic'
            write_book(path,book); original=read_book(path)
            migration={'flags':{**self.flags(),'constructor':{**self.flags()['constructor'],'use_ee_floor':True}},
                'compatible':{'MC_new_GE':{'reason':'unchanged runtime'}},'before_runtime':{},'after_runtime':{},
                'old_warnings':[],'new_warnings':[],
                'effective_groups':pd.DataFrame({'group_name':['Fish'],'ee':[.1],'source_EE':[.01]},index=[1]),
                'info':{'use_ee_floor':True,'ee_floor':.1,'affected_groups':[1]},
                'ledger':pd.DataFrame({'group_name':['Fish'],'EE_before_floor':[.01],'EE_effective':[.1]},index=[1]),
                'calculation_code':b'isolated calculator source'}
            retained={'MC_new_GE':{'status':'reused','preserve_saved':True,'reason':'unchanged dependencies'}}
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration',return_value=self.flags()), \
                 patch('tools.project_core.calculations.ee_floor_migration.prepare',return_value=migration), \
                 patch('tools.project_core.calculations.ee_floor_migration.retained_outcomes',return_value=retained), \
                 patch('tools.scientific_helpers.sppr.method_coverage.compute_methods',side_effect=self.executor(called)), \
                 patch.object(coverage,'_context',return_value={'code_identity':{},'flags':migration['flags']}), \
                 patch.object(cpe,'ALL_METHOD_KEYS',('new_GE','MC_new_GE')):
                run_region.sppr(book,path,0,use_ee_floor=True,ee_floor=.1)
            self.assertEqual(called[0][1],['new_GE'])
            saved=read_book(path)
            old_mc=[row for row in original['Selected model groups']['Group SPPR'][1] if row[3]=='MC_new_GE']
            new_mc=[row for row in saved['Selected model groups']['Group SPPR'][1] if row[3]=='MC_new_GE']
            self.assertEqual(new_mc,old_mc)
            self.assertEqual(saved['Diagnostics']['mc_diagnostics'],original['Diagnostics']['mc_diagnostics'])
            self.assertTrue(all(str(row['status']).startswith('FAIL: historical') for row in records(saved,'PPR','Annual') if row['method']=='new_GE'))

    def test_missing_pinned_engine_after_resolution_records_not_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); model,path,book=self.package(root); original=copy.deepcopy(book)
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration',return_value=self.flags()), \
                 patch.object(coverage,'_context',side_effect=ValueError('pinned engine source missing')), \
                 patch('tools.scientific_helpers.sppr.method_coverage.compute_methods') as run, \
                 patch.object(cpe,'ALL_METHOD_KEYS',('new_GE','MC_new_GE')):
                run_region.sppr(book,path,0,use_ee_floor=True,ee_floor=.1)
            run.assert_not_called()
            saved=read_book(path)
            self.assertEqual(saved['Overview'],original['Overview'])
            self.assertEqual(saved['Selected model groups'],original['Selected model groups'])
            self.assertEqual({row['status'] for row in records(saved,'Diagnostics','SPPR execution')},{'NOT_RUN'})

    def test_first_floor_run_without_saved_methods_does_not_authenticate_history(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); model,path,book=self.package(root);called=[]
            book['Selected model groups']['Group SPPR'][1].clear()
            book['PPR']['Annual'][1].clear()
            write_book(path,book)
            migration={'flags':{**self.flags(),'constructor':{**self.flags()['constructor'],'use_ee_floor':True}},
                'compatible':{'MC_new_GE':{'reason':'unchanged runtime'}},'before_runtime':{},'after_runtime':{},
                'old_warnings':[],'new_warnings':[],
                'effective_groups':pd.DataFrame({'group_name':['Fish'],'ee':[.1],'source_EE':[.01]},index=[1]),
                'info':{'use_ee_floor':True,'ee_floor':.1,'affected_groups':[1]},
                'ledger':pd.DataFrame({'group_name':['Fish'],'EE_before_floor':[.01],'EE_effective':[.1]},index=[1]),
                'calculation_code':b'isolated calculator source'}
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration',return_value=self.flags()), \
                 patch('tools.project_core.calculations.ee_floor_migration.prepare',return_value=migration), \
                 patch('tools.project_core.calculations.ee_floor_migration.retained_outcomes',side_effect=AssertionError('There is no historical result to authenticate')) as retain, \
                 patch('tools.scientific_helpers.sppr.method_coverage.compute_methods',side_effect=self.executor(called)), \
                 patch.object(coverage,'_context',return_value={'code_identity':{},'flags':migration['flags']}), \
                 patch.object(cpe,'ALL_METHOD_KEYS',('new_GE','MC_new_GE')):
                run_region.sppr(book,path,0,use_ee_floor=True,ee_floor=.1)
            retain.assert_not_called()
            self.assertEqual(called[0][1],['new_GE','MC_new_GE'])
            manifest=json.loads((model/'results/result_manifest.json').read_text(encoding='utf-8'))
            self.assertTrue(all(not outcome.get('preserve_saved') for outcome in manifest['method_coverage']['methods'].values()))

    def test_regional_cli_omission_and_explicit_flags(self):
        base=['--region','regions/LME/LME_001','--stage','sppr']
        args=run_region.parse_arguments(base)
        self.assertIsNone(args.use_ee_floor); self.assertIsNone(args.ee_floor)
        args=run_region.parse_arguments(base+['--no-ee-floor','--ee-floor','.2'])
        self.assertFalse(args.use_ee_floor); self.assertEqual(args.ee_floor,.2)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            run_region.parse_arguments(base+['--no-ee-floor','--ee-floor','nan'])

    def test_regional_failure_rolls_back_owned_workbook_source_and_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); model,path,book=self.package(root); original=path.read_bytes();called=[]
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration',return_value=self.flags()), \
                 patch('tools.scientific_helpers.sppr.method_coverage.compute_methods',side_effect=self.executor(called)), \
                 patch.object(coverage,'_context',return_value={'code_identity':{},'flags':self.flags()}), \
                 patch.object(coverage,'_write_json',side_effect=RuntimeError('isolated downstream failure')), \
                 patch.object(cpe,'ALL_METHOD_KEYS',('new_GE','MC_new_GE')):
                with self.assertRaisesRegex(RuntimeError,'isolated downstream failure'):
                    run_region.sppr(book,path,0)
            self.assertEqual(path.read_bytes(),original)
            self.assertFalse((model/'sppr_source.xlsx').exists())
            self.assertFalse((model/'results/result_manifest.json').exists())
            self.assertFalse(any(file.is_file() for file in (model/'results/diagnostics').rglob('*')))


if __name__ == '__main__':
    unittest.main()
