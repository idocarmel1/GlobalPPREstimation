import copy,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_workflow import fixture
from workbooks import records,overview
from regional import recalculate
from size_allocations import apply_allocations

class SizeAllocationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'LME_001.xlsx'
        model=self.path.parent/'models/m/model.json';model.parent.mkdir(parents=True);model.write_text('{}')
        self.book=fixture()
        self.book['Selected model groups']['Groups']=(['seq','group_name'],[[1,'A'],[2,'B'],[3,'C']])
        self.book['Selected model groups']['Group SPPR'][1][1][-1]=20.
        self.book['Selected model groups']['Group SPPR'][1].extend([['m','C','all','one',10.],['m','C','all','two',10.]])
        self.book['PPR']['Matching'][1][1][2:4]=[None,None]
        recalculate(self.book,self.path)
        self.plan={'unit_id':'LME_001','model_id':'m','proposals':[{'taxon':'b','rule':'model_catch_proxy','evidence':'Source table 2','definition':'Same species: small C, large B','limitations':'Source-period proxy; no regional size observations','source_period':'1980','candidates':[{'group':'B','seq':2,'source_catch':3.,'weight':.75},{'group':'C','seq':3,'source_catch':1.,'weight':.25}]}]}
        self.plan['proposals'][0]['online_search']=[{'query':'fixture catch at size','url':'https://example.org/fixture','outcome':'Test fixture: no applicable size composition'}]
    def tearDown(self):self.temp.cleanup()
    def test_proxy_mass_balance_provenance_and_provisional_result(self):
        classic=copy.deepcopy(self.book['Classic PPR']);groups=copy.deepcopy(self.book['Selected model groups'])
        apply_allocations(self.book,self.path,self.plan)
        a=next(r for r in records(self.book,'PPR','Annual') if r['method']=='one' and r['catch_basis']=='catch' and r['metric']=='ppr' and r['unidentified']=='method')
        self.assertEqual(a[2019],62.5);self.assertTrue(a['status'].startswith('provisional:'))
        self.assertEqual(self.book['Classic PPR'],classic);self.assertEqual(self.book['Selected model groups'],groups)
        impact=next(r for r in records(self.book,'Diagnostics','Size allocation impact') if r['method']=='one' and r['catch_basis']=='catch' and r['year']==2019)
        self.assertEqual(impact['baseline_covered_catch'],2.);self.assertEqual(impact['covered_catch'],5.)
        self.assertEqual(impact['assumed_covered_catch'],3.);self.assertEqual(impact['covered_without_size_assumptions'],2.)
        ledger=records(self.book,'PPR','Allocation assumptions')
        self.assertEqual(len(ledger),2);self.assertEqual(sum(r['weight'] for r in ledger),1)
        self.assertIn('assumed',overview(self.book)['source_note'].lower())
    def test_wrong_pair_or_weights_rejected_before_mutation(self):
        for mutate in [lambda p:p.update(model_id='other'),lambda p:p['proposals'][0]['candidates'][0].update(weight=.9),lambda p:p['proposals'][0]['candidates'][0].update(group='unknown'),lambda p:p['proposals'][0].pop('online_search')]:
            p=copy.deepcopy(self.plan);mutate(p);before=copy.deepcopy(self.book)
            with self.assertRaises(ValueError):apply_allocations(self.book,self.path,p)
            self.assertEqual(self.book,before)
    def test_zero_weight_candidate_does_not_require_missing_coefficient(self):
        self.plan['proposals'][0]['candidates'][0]['weight']=1
        self.plan['proposals'][0]['candidates'][1]['weight']=0
        self.plan['proposals'][0]['rule']='adult_only_assumption'
        self.book['Selected model groups']['Group SPPR'][1][-2][-1]=None
        apply_allocations(self.book,self.path,self.plan)
        sppr=next(r for r in records(self.book,'PPR','Taxon SPPR') if r['taxon']=='b' and r['method']=='one')
        self.assertEqual(sppr['sppr'],20)
        self.assertEqual(len([r for r in records(self.book,'PPR','Matching') if r['taxon']=='b']),1)
        self.assertEqual(len(records(self.book,'PPR','Allocation assumptions')),2)

    def test_source_scope_numeric_results_survive_unavailable_simple_treatment(self):
        for r in list(self.book['Selected model groups']['Group SPPR'][1]):
            self.book['Selected model groups']['Group SPPR'][1].append([r[0],r[1],'PP',r[3],r[4]])
        for r in list(self.book['PPR']['Annual'][1]):
            self.book['PPR']['Annual'][1].append([r[0],'PP',*r[2:6],
                'unavailable: simple reference has no source decomposition' if r[4]=='simple' else r[6],*r[7:]])
        apply_allocations(self.book,self.path,self.plan)
        rr=[r for r in records(self.book,'PPR','Annual') if r['scope']=='PP' and r['method']=='one' and r['catch_basis']=='catch' and r['metric']=='ppr']
        self.assertEqual(next(r for r in rr if r['unidentified']=='method')[2019],62.5)
        self.assertIsNone(next(r for r in rr if r['unidentified']=='simple')[2019])

if __name__=='__main__':unittest.main()
