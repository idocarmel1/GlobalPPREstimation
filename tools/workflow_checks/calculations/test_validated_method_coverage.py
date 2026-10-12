import copy
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from tools.project_core.calculations import coverage


class CoveragePlanTests(unittest.TestCase):
    def setUp(self):
        self.keys = ('new_GE', 'new_TE_EEfix', 'new_WithEgestion', 'EwE_TE_EE', 'MC_new_GE')
        self.context = {'model_sha256': 'original', 'flags': {'det_collapse_mode': 'auto'}}
        self.saved = {'context': self.context, 'methods': {
            key: {'status': 'ok', 'group_rows_sha256': key} for key in self.keys}}
        self.hashes = {k:k for k in self.keys}

    def test_three_method_package_triggers_completion(self):
        del self.saved['methods']['EwE_TE_EE']; del self.saved['methods']['MC_new_GE']
        self.assertEqual(coverage.plan_methods(self.keys, self.context, self.saved, self.hashes), list(self.keys[3:]))

    def test_complete_fresh_package_reused(self):
        self.assertEqual(coverage.plan_methods(self.keys, self.context, self.saved, self.hashes), [])

    def test_corrected_input_invalidates_all_methods(self):
        current = copy.deepcopy(self.context); current['model_sha256'] = 'corrected'
        self.assertEqual(coverage.plan_methods(self.keys, current, self.saved, self.hashes), list(self.keys))

    def test_explicit_failure_is_cached_but_missing_reason_is_not(self):
        self.saved['methods']['MC_new_GE'].update(status='failed', reason='all draws rejected')
        self.assertEqual(coverage.plan_methods(self.keys, self.context, self.saved, self.hashes), [])
        self.saved['methods']['MC_new_GE']['reason'] = ''
        self.assertEqual(coverage.plan_methods(self.keys, self.context, self.saved, self.hashes), ['MC_new_GE'])

    def test_partial_overwrite_invalidates_missing_columns(self):
        self.assertEqual(coverage.plan_methods(self.keys, self.context, self.saved,
                                              {k:k for k in self.keys[:3]}), list(self.keys[3:]))

    def test_candidate_identity_not_filtered_by_selection(self):
        entries = [{'unit_id':'LME_001', 'model_id':m, 'selected':m=='default',
                    'researcher_review_status':s} for m,s in [
                        ('default','Validated by researcher'), ('candidate','Validated by researcher'),
                        ('rejected','Disqualified by researcher')]]
        self.assertEqual(coverage.validated_identities(entries), [('LME_001','candidate'),('LME_001','default')])

    def test_extension_preserves_reviewed_group_row_order_and_failure(self):
        book = {'Selected model groups': {
            'Groups': (['group_name'], [['fish'], ['algae']]),
            'Group SPPR': (['model_id','group','scope','method','sppr'],
                           [['model','fish','all','new_GE',2.], ['model','algae','all','new_GE',1.]])}}
        original = copy.deepcopy(book['Selected model groups']['Group SPPR'][1])
        outcome = {'EwE_TE_EE': {'status':'failed','reason':'worker failed',
                               'annual_status': {s:'unavailable: worker failed' for s in ('all','inner','PP')}}}
        coverage._apply_outcomes(book, 'model', outcome, ['EwE_TE_EE'])
        self.assertEqual(book['Selected model groups']['Group SPPR'][1][:2], original)
        self.assertTrue(all(r[4] is None for r in book['Selected model groups']['Group SPPR'][1][2:]))
        self.assertTrue(all(r[6]=='unavailable: worker failed' for r in book['PPR']['Annual'][1]))

    def test_finite_execution_does_not_promote_prior_failure_or_erase_unchanged_preview(self):
        from tools.workflow_checks.selection.test_snapshots import fixture
        from tools.project_core.workbooks.workbooks import rows
        for prior in ('FAIL: retained scientific restriction','provisional: authorized diagnostic preview'):
            book=fixture(); book['PPR']['Annual'][1][0][6]=prior
            outcome={'GE':{'status':'ok','scopes':{'all':{'Fish':5.}},
                           'annual_status':{'all':'ok'}}}
            coverage._apply_outcomes(book,'A',outcome,['GE'])
            status=next(row[6] for row in rows(book,'PPR','Annual') if row[1]=='all')
            self.assertEqual(status,prior)


class CoverageIntegrationTests(unittest.TestCase):
    def test_persisted_result_hash_survives_excel_signed_zero_normalization(self):
        from tools.project_core.workbooks.workbooks import input_hash, overview, rows
        from tools.project_core.calculations.regional import set_setting, set_result_hash, result_hash
        book = {'Overview': {'Settings': (['field','value'], [])},
                'PPR': {'Taxon SPPR': (['model_id','taxon','scope','method','sppr'],
                                      [['A','fish','all','GE',round(-1e-12,6)]])}}
        set_setting(book,'calculation_input_sha256',input_hash(book)); set_result_hash(book)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'region.xlsx'
            saved = coverage._save_calculation(path,book,Path(temporary)/'model.json',{},None)
            self.assertEqual(rows(saved,'PPR','Taxon SPPR')[0][-1],0)
            self.assertEqual(overview(saved)['calculation_result_sha256'],result_hash(saved))
            self.assertEqual(overview(saved)['calculation_input_sha256'],input_hash(saved))

    def test_full_package_reuse_missing_method_completion_and_input_change_rejection(self):
        from tools.workflow_checks.selection.test_snapshots import fixture
        from tools.project_core.workbooks.workbooks import write_book, read_book, sha, input_hash, overview, rows
        from tools.project_core.calculations.regional import set_setting, recalculate
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); region = root/'regions/LME/LME_001'
            model = region/'papers/P/models/A'; model.mkdir(parents=True)
            (root/'Project.xlsx').write_bytes(b'central remains untouched')
            source = model/'model.json'; source.write_text('{"group":[{"group_seq":"1","group_name":"Fish"}]}')
            original_model = source.read_bytes()
            path = region/'LME_001.xlsx'; book = fixture()
            book['Selected model groups']['Group SPPR'][1][:] = [
                ['A','Fish',scope,'GE',5.] for scope in ('all','inner','PP')]
            original_annual = book['PPR']['Annual'][1][0]
            book['PPR']['Annual'][1][:] = [
                [original_annual[0],scope,*original_annual[2:]] for scope in ('all','inner','PP')]
            set_setting(book,'selected_model_id','A'); set_setting(book,'results_model_sha256',sha(source))
            set_setting(book,'model_path',source.relative_to(region).as_posix())
            book['PPR–NPP'] = {}
            recalculate(book,path); write_book(path,book)
            original = read_book(path)
            metadata = {'unit_id':'LME_001','model_id':'A','reviewed_calculation_input_sha256':input_hash(original),
                        'reviewed_model_sha256':sha(source)}
            calls=[]
            def compute(model_path,flags,keys,directory,progress):
                calls.append(list(keys)); directory.mkdir(parents=True,exist_ok=True)
                outcomes={}
                for key in keys:
                    evidence=directory/(key+'.json'); evidence.write_text(json.dumps({'method':key,'input':sha(model_path)}))
                    outcomes[key]={'status':'ok' if key=='GE' else 'failed',
                        'reason':'' if key=='GE' else 'numeric failure retained',
                        'scopes':{s:{'Fish':5. if key=='GE' else None} for s in ('all','inner','PP')},
                        'annual_status':{s:'ok' if key=='GE' else 'unavailable: numeric failure retained' for s in ('all','inner','PP')},
                        'evidence':{'path':evidence.name,'sha256':sha(evidence)}}
                auxiliary={}
                for key in ('constructor_evidence','evidence_index'):
                    evidence=directory/(key+'.json'); evidence.write_text(key)
                    auxiliary[key]={'path':evidence.name,'sha256':sha(evidence)}
                return {'methods':outcomes,**auxiliary}
            flags={'constructor':{'normalize_DC':True}}
            context = coverage._context
            repository = Path(__file__).resolve().parents[3]
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration',return_value=flags), \
                 patch.object(coverage, '_context', side_effect=lambda root,model,flags: context(repository,model,flags)):
                modified,report=coverage._complete_model(root,metadata,('GE','extra'),progress=lambda x:None,compute=compute)
                self.assertTrue(modified); self.assertEqual(calls,[['extra']])
                saved=read_book(path)
                self.assertEqual([r for r in rows(saved,'Selected model groups','Group SPPR') if r[3]=='GE'],
                                 rows(original,'Selected model groups','Group SPPR'))
                self.assertEqual([r for r in rows(saved,'PPR','Annual') if r[2]=='GE'],
                                 [r for r in rows(original,'PPR','Annual') if r[2]=='GE'])
                manifest=json.loads((model/'results/result_manifest.json').read_text())
                for evidence in manifest['method_coverage']['execution_evidence'].values():
                    self.assertEqual(sha(model/'results/diagnostics'/evidence['path']),evidence['sha256'])
                for sheet in ('Catch','Classic PPR','NPP'):
                    self.assertEqual(saved[sheet],original[sheet])
                self.assertEqual(saved['PPR']['Matching'],original['PPR']['Matching'])
                self.assertEqual(overview(saved)['selected_model_id'],'A')
                self.assertEqual(saved['Diagnostics']['manual'],original['Diagnostics']['manual'])
                self.assertTrue(all(r[6].startswith('unavailable:') and all(v is None for v in r[7:])
                    for r in rows(saved,'PPR','Annual') if r[2]=='extra' and r[5]=='ppr' and r[4]=='method'))
                before=path.read_bytes()
                modified,_=coverage._complete_model(root,metadata,('GE','extra'),progress=lambda x:None,compute=compute)
                self.assertFalse(modified); self.assertEqual(len(calls),1); self.assertEqual(path.read_bytes(),before)
                # A corrupt local snapshot is repaired from current regional
                # results without rerunning any otherwise fresh method.
                (model/'results/regional_snapshot.xlsx').write_bytes(b'corrupt snapshot')
                modified,_=coverage._complete_model(root,metadata,('GE','extra'),progress=lambda x:None,compute=compute)
                self.assertTrue(modified); self.assertEqual(len(calls),1)
                self.assertEqual((model/'results/regional_snapshot.xlsx').read_bytes(),path.read_bytes())
                # A diagnostic-only overwrite deletes the extra coefficient column.
                saved['Selected model groups']['Group SPPR'][1][:]=[r for r in rows(saved,'Selected model groups','Group SPPR') if r[3]=='GE']
                write_book(path,saved)
                coverage._complete_model(root,metadata,('GE','extra'),progress=lambda x:None,compute=compute)
                self.assertEqual(calls[-1],['extra'])
                outputs = [path, model/'sppr_source.xlsx', model/'results/regional_snapshot.xlsx',
                           model/'results/result_manifest.json']
                prior = {p:p.read_bytes() for p in outputs}
                prior_calls = copy.deepcopy(calls)
                source.write_text('{"group":[{"group_seq":"1","group_name":"Fish","b":2}]}')
                with self.assertRaisesRegex(ValueError,'explicit scientific refresh'):
                    coverage._complete_model(root,metadata,('GE','extra'),progress=lambda x:None,compute=compute)
                self.assertEqual(calls,prior_calls)
                self.assertEqual({p:p.read_bytes() for p in outputs},prior)
                source.write_bytes(original_model)
                # A worker error owns only its staged evidence; a researcher's
                # simultaneous new file in the result directory must survive.
                author_file = model/'results/diagnostics/method_coverage/researcher-note.txt'
                def fail(model_path,flags,keys,directory,progress):
                    self.assertEqual(list(keys),['third'])
                    (directory/'unfinished.json').write_text('partial worker return')
                    author_file.write_text('concurrent researcher note')
                    raise RuntimeError('worker infrastructure failed')
                with self.assertRaisesRegex(RuntimeError,'worker infrastructure failed'):
                    coverage._complete_model(root,metadata,('GE','extra','third'),progress=lambda x:None,compute=fail)
                self.assertEqual(author_file.read_text(),'concurrent researcher note')
                self.assertEqual({p:p.read_bytes() for p in outputs},prior)
                self.assertFalse(list((model/'results/diagnostics').glob('.method-coverage-*')))

    def test_unchanged_sensitivity_preserved_changed_scope_invalidated(self):
        from tools.workflow_checks.selection.test_snapshots import fixture
        from tools.project_core.workbooks.workbooks import sha, rows, YEARS
        from tools.project_core.calculations.regional import set_setting, recalculate
        with tempfile.TemporaryDirectory() as temporary:
            region=Path(temporary); model=region/'A/model.json'; model.parent.mkdir()
            model.write_text('{}'); path=region/'LME_001.xlsx'; original=fixture()
            set_setting(original,'selected_model_id','A'); set_setting(original,'model_path','A/model.json')
            set_setting(original,'results_model_sha256',sha(model))
            original['PPR']['Annual'][1][0][6]='ok'
            recalculate(original,path)
            bound=['A','all','GE','landings','method','min_tC','ok',*([.4]*len(YEARS))]
            original['PPR']['Annual'][1].append(bound)
            unchanged=copy.deepcopy(original)
            coverage._arithmetic(unchanged,path,model,{},original)
            self.assertIn(bound,rows(unchanged,'PPR','Annual'))
            self.assertEqual(unchanged['Classic PPR'],original['Classic PPR'])
            changed=copy.deepcopy(original)
            changed['Selected model groups']['Group SPPR'][1][0][4]=6
            coverage._arithmetic(changed,path,model,{},original)
            self.assertFalse(any(row[5]=='min_tC' for row in rows(changed,'PPR','Annual')))


if __name__ == '__main__': unittest.main()
