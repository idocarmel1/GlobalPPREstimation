"""Candidate arithmetic uses current independent inputs and retained mappings."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.project_core.calculations.coverage_candidates import (
    independent_dependencies, prepare_candidate_book, suppress_candidate_arithmetic)
from tools.project_core.workbooks.workbooks import overview, records, input_hash, sha, read_book, write_book
from tools.project_core.calculations.regional import result_hash
from tools.workflow_checks.selection.test_snapshots import fixture


class CandidateInputsTests(unittest.TestCase):
    def setUp(self):
        self.saved=fixture();self.current=copy.deepcopy(self.saved)
        self.saved['PPR']['Allocation assumptions']=(['note'],[['researcher weights']])
        self.saved['PPR']['Mapping review']=(['note'],[['researcher matching review']])
        self.current['Overview']['Settings'][1].append(['selection_rationale','default remains selected'])

    def test_compatible_current_inputs_are_copied_without_changing_authored_model_tables(self):
        self.current['Catch']['Catch'][1][0][-1]=30
        self.current['Classic PPR']['Taxa'][1][0][-1]=15
        self.current['NPP']['NPP'][1][0][-1]=200
        saved=copy.deepcopy(self.saved);current=copy.deepcopy(self.current)
        result=prepare_candidate_book(self.saved,self.current);prepared=result['book']
        self.assertTrue(result['changed']);self.assertIsNone(result['pending_reason'])
        for sheet in ['Catch','Classic PPR','NPP']:
            self.assertEqual(prepared[sheet],self.current[sheet])
        for name in ['Matching','Allocation assumptions','Mapping review']:
            self.assertEqual(prepared['PPR'][name],self.saved['PPR'][name])
        self.assertEqual(prepared['Selected model groups'],self.saved['Selected model groups'])
        self.assertEqual(self.saved,saved);self.assertEqual(self.current,current)
        self.assertEqual(overview(prepared)['selected_model_id'],overview(saved)['selected_model_id'])
        self.assertEqual(result['state']['current_dependencies'],independent_dependencies(current))

    def test_changed_catch_with_split_weights_stays_pending_until_matching_changes(self):
        header=self.saved['PPR']['Matching'][0]
        weight=header.index('weight')
        self.saved['PPR']['Matching'][1][0][weight]=.5
        extra=copy.deepcopy(self.saved['PPR']['Matching'][1][0]);extra[header.index('group')]='Other'
        self.saved['PPR']['Matching'][1].append(extra)
        groups=self.saved['Selected model groups']['Groups'];other=copy.deepcopy(groups[1][0])
        other[groups[0].index('group_name')]='Other';groups[1].append(other)
        self.current['Catch']['Catch'][1][0][-1]=30
        result=prepare_candidate_book(self.saved,self.current)
        self.assertIn('split allocation',result['pending_reason'])
        prepared=result['book'];suppress_candidate_arithmetic(prepared,result['pending_reason'])
        self.assertFalse(records(prepared,'PPR','Annual'))
        self.assertFalse(records(prepared,'PPR','Taxon SPPR'))
        self.assertEqual(prepared['PPR']['Matching'],self.saved['PPR']['Matching'])
        self.assertEqual(overview(prepared)['calculation_input_sha256'],input_hash(prepared))
        self.assertEqual(overview(prepared)['calculation_result_sha256'],result_hash(prepared))
        repeated=prepare_candidate_book(prepared,self.current)
        self.assertEqual(repeated['pending_reason'],result['pending_reason'])
        self.assertFalse(repeated['changed'])

    def test_removed_or_added_taxon_retains_matching_but_suppresses_candidate_arithmetic(self):
        self.current['Catch']['Catch'][1][0][0]='new taxon'
        result=prepare_candidate_book(self.saved,self.current)
        self.assertIn('taxon set changed',result['pending_reason'])
        self.assertEqual(result['book']['PPR']['Matching'],self.saved['PPR']['Matching'])
        self.assertEqual(result['book']['Catch'],self.current['Catch'])

    def test_npp_change_alone_does_not_invalidate_retained_split_weights(self):
        self.current['NPP']['NPP'][1][0][-1]=200
        result=prepare_candidate_book(self.saved,self.current)
        self.assertIsNone(result['pending_reason'])
        self.assertEqual(result['book']['PPR']['Matching'],self.saved['PPR']['Matching'])

    def test_compatible_candidate_arithmetic_uses_current_catch_and_npp_with_own_coefficients(self):
        from tools.project_core.calculations.coverage import _arithmetic
        from tools.project_core.calculations.regional import set_setting
        self.saved['PPR']['Annual'][1][0][6]='provisional: retained warning'
        self.current['Catch']['Catch'][1][0][-1]=30
        self.current['NPP']['NPP'][1][0][-1]=200
        original=copy.deepcopy(self.saved)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);model=root/'papers/p/models/A/model.json'
            model.parent.mkdir(parents=True);model.write_text('{}')
            set_setting(self.saved,'results_model_sha256',sha(model))
            prepared=prepare_candidate_book(self.saved,self.current)['book']
            _arithmetic(prepared,root/'LME_001.xlsx',model,{},self.saved)
        annual=next(row for row in records(prepared,'PPR','Annual')
                    if row['scope']=='all' and row['method']=='GE' and row['catch_basis']=='landings'
                    and row['unidentified']=='method' and row['metric']=='ppr')
        self.assertEqual(annual[2019],150)
        self.assertEqual(annual['status'],'provisional: retained warning')
        ratio=next(row for row in records(prepared,'PPR–NPP','Ratios')
                   if row['model_id']=='A' and row['catch_basis']=='landings' and row['unidentified']=='method')
        self.assertAlmostEqual(ratio[2019],100*150/9/200)
        self.assertEqual(overview(prepared)['selected_model_id'],overview(original)['selected_model_id'])
        self.assertEqual(prepared['PPR']['Matching'],original['PPR']['Matching'])
        self.assertEqual(prepared['Diagnostics'],original['Diagnostics'])


class CandidateCoverageIntegrationTests(unittest.TestCase):
    def test_candidate_refresh_reuses_coefficients_and_caches_explicit_split_pending(self):
        from tools.project_core.calculations import coverage
        from tools.project_core.calculations.regional import set_setting,set_result_hash,recalculate
        from tools.project_core.maps.original_atlas_data import candidate_result_models
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);region=root/'regions/LME/LME_001'
            model=region/'papers/P/models/A';default=region/'papers/P/models/B'
            for directory in (model,default):
                directory.mkdir(parents=True)
                (directory/'model.json').write_text('{"group":[{"group_seq":"1","group_name":"Fish"},{"group_seq":"2","group_name":"Other"}]}')
            project=root/'Project.xlsx';project.write_bytes(b'central unchanged')
            regional=region/'LME_001.xlsx';snapshot=model/'results/regional_snapshot.xlsx'
            candidate=fixture();candidate['PPR']['Annual'][1][0][6]='provisional: retained warning'
            candidate['Selected model groups']['Groups'][1].append([2,'Other'])
            candidate['Selected model groups']['Group SPPR'][1][:] = [
                ['A',group,scope,'GE',value] for scope in ('all','inner','PP')
                for group,value in (('Fish',5.),('Other',7.))]
            original_annual = candidate['PPR']['Annual'][1][0]
            candidate['PPR']['Annual'][1][:] = [
                [original_annual[0],scope,*original_annual[2:]] for scope in ('all','inner','PP')]
            candidate['PPR']['Allocation assumptions']=(['note'],[['researcher allocation']])
            candidate['PPR']['Mapping review']=(['note'],[['researcher matching']])
            set_setting(candidate,'results_model_sha256',sha(model/'model.json'))
            set_setting(candidate,'calculation_input_sha256',input_hash(candidate));set_result_hash(candidate)
            write_book(snapshot,candidate)
            current=copy.deepcopy(candidate)
            for sheet,table in [('Selected model groups','Group SPPR'),('PPR','Matching'),('PPR','Annual')]:
                for row in current[sheet][table][1]:row[0]='B'
            set_setting(current,'results_model_id','B');set_setting(current,'results_model_sha256',sha(default/'model.json'))
            set_setting(current,'model_path',(default/'model.json').relative_to(region).as_posix())
            current['Selected model groups']['Group SPPR'][1][0][4]=99
            recalculate(current,regional);write_book(regional,current)
            metadata={'unit_id':'LME_001','model_id':'A','model_path':(model/'model.json').relative_to(root).as_posix(),
                      'reviewed_calculation_input_sha256':input_hash(read_book(snapshot)),
                      'reviewed_model_sha256':sha(model/'model.json')}
            calls=[]
            def compute(model_path,flags,methods,directory,progress):
                calls.append(list(methods));outcomes={}
                for method in methods:
                    evidence=directory/(method+'.json');evidence.write_text(json.dumps({'method':method}))
                    outcomes[method]={'status':'ok','reason':'',
                        'scopes':{scope:{'Fish':5 if method=='GE' else 9,'Other':7} for scope in ('all','inner','PP')},
                        'annual_status':{scope:'ok' for scope in ('all','inner','PP')},
                        'evidence':{'path':evidence.name,'sha256':sha(evidence)}}
                return {'methods':outcomes}
            def complete():
                before=regional.read_bytes()
                result=coverage._complete_model(root,metadata,('GE','extra'),progress=lambda _:None,compute=compute)
                self.assertEqual(regional.read_bytes(),before)
                self.assertEqual(project.read_bytes(),b'central unchanged')
                return result
            with patch('tools.scientific_helpers.sppr.configuration.resolve_audited_configuration',return_value={'constructor':{}}), \
                 patch.object(coverage,'_context',return_value={'code_identity':{},'flags':{'constructor':{}},
                                                              'model_sha256':sha(model/'model.json')}):
                modified,_=complete();self.assertTrue(modified);self.assertEqual(calls,[['extra']])
                original=read_book(snapshot);current=read_book(regional)
                current['Catch']['Catch'][1][0][-1]=30;current['NPP']['NPP'][1][0][-1]=200
                recalculate(current,regional);write_book(regional,current)
                modified,_=complete();self.assertTrue(modified);self.assertEqual(len(calls),1)
                saved=read_book(snapshot)
                annual=next(row for row in records(saved,'PPR','Annual') if row['method']=='GE' and row['scope']=='all'
                            and row['metric']=='ppr' and row['catch_basis']=='landings' and row['unidentified']=='method')
                self.assertEqual(annual[2019],150)
                for name in ('Matching','Allocation assumptions','Mapping review'):
                    self.assertEqual(saved['PPR'][name],original['PPR'][name])
                self.assertEqual(overview(saved)['selected_model_id'],'B')
                # Authored split mapping is retained, then current catch changes.
                saved['PPR']['Matching'][1][:]=[['A','fish','Fish',.5],['A','fish','Other',.5]]
                write_book(snapshot,saved);complete()
                current=read_book(regional);current['Catch']['Catch'][1][0][-1]=40
                recalculate(current,regional);write_book(regional,current)
                modified,_=complete();self.assertTrue(modified)
                pending=read_book(snapshot);before=snapshot.read_bytes()
                self.assertFalse(records(pending,'PPR','Annual'))
                self.assertIn('split allocation',overview(pending)['calculation_status'])
                self.assertEqual(pending['PPR']['Matching'][1],[['A','fish','Fish',.5],['A','fish','Other',.5]])
                modified,_=complete();self.assertFalse(modified)
                self.assertEqual(snapshot.read_bytes(),before);self.assertEqual(len(calls),1)
                payload=candidate_result_models(root,metadata,read_book(regional))
                self.assertEqual(payload[0]['scopes'],{});self.assertFalse(payload[1]['verified'])
                self.assertEqual(payload[1]['group_data']['methods'],['GE','extra'])
                self.assertEqual(payload[1]['group_data']['scopes']['all'],[[5,9],[7,7]])


if __name__=='__main__':unittest.main()
