import sys,unittest,tempfile,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from workbooks import *
from regional import *

def fixture():
 b={s:{} for s in REGION_SHEETS}
 b['Overview']['Settings']=(['field','value'],[['unit_id','LME_001'],['selected_model_id','m'],['model_path','models/m/model.json'],['results_model_id','m'],['taxon_detail_year',2019],['catch_basis','landings']])
 b['Catch']['Catch']=(['taxon','common_name','functional_group','commercial_group','catch_basis','unidentified',*YEARS],[[t,t,'f','c',basis,False,*([v]*70)] for t,v in [('a',2.),('b',3.)] for basis in ['catch','landings','discards']])
 b['Classic PPR']['Taxa']=(['taxon','tl','sppr','tl_source','match_method','confidence'],[['a',2,10,'x','x','high'],['b',3,100,'x','x','high']])
 b['Classic PPR']['Annual']=(ANNUAL_HEADER,[])
 b['Selected model groups']['Group SPPR']=(['model_id','group','scope','method','sppr'],[['m','A','all','one',5.],['m','B','all','one',None],['m','A','all','two',10.],['m','B','all','two',20.]])
 b['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],[['m','a','A',1.,'high','explicit_member','source'],['m','b','B',1.,'high','explicit_member','source']])
 b['PPR']['Annual']=(ANNUAL_HEADER,[['m','all',m,'landings','method','ppr','ok',*([None]*70)] for m in ['one','two']])
 b['NPP']['NPP']=(['method','units',*YEARS],[['ens_median_tC_yr','tC/year',*([100.]*70)]])
 return b

class WorkflowTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'LME_001.xlsx';p=self.path.parent/'models/m/model.json';p.parent.mkdir(parents=True);p.write_text('{}');self.b=fixture()
 def tearDown(self):self.tmp.cleanup()
 def test_roundtrip_and_missing(self):
  recalculate(self.b,self.path);write_book(self.path,self.b);b=read_book(self.path);validate_region(b,self.path)
  coeff={(r['taxon'],r['method']):r['sppr'] for r in records(b,'PPR','Taxon SPPR')}
  self.assertIsNone(coeff['b','one']);self.assertEqual(coeff['a','one'],5)
 def test_common_catch_differs_from_ratio_of_totals(self):
  recalculate(self.b,self.path);pairs,ss,_=comparison_tables(self.b)
  p=next(r for r in pairs if r[2:6]==['all','method','one','two']);mid=p[6]
  vals={r[6]:r[8] for r in ss if r[2:6]==['all','method','landings',mid] and r[7]=='ppr'}
  self.assertAlmostEqual(vals['one']/vals['two'],.5)
  a={r[2]:r[7] for r in rows(self.b,'PPR','Annual') if r[3:6]==['landings','method','ppr']}
  self.assertAlmostEqual(a['one']/a['two'],.125)
 def test_changed_mapping_fails_freshness(self):
  recalculate(self.b,self.path);self.b['PPR']['Matching'][1][0][3]=.5
  with self.assertRaisesRegex(ValueError,'inputs changed'):validate_region(self.b,self.path)
  with self.assertRaisesRegex(ValueError,'sum to one'):recalculate(self.b,self.path)
 def test_changed_model_and_selection(self):
  recalculate(self.b,self.path);(self.path.parent/'models/m/model.json').write_text('{"changed":true}')
  with self.assertRaisesRegex(ValueError,'model JSON changed'):validate_region(self.b,self.path)
 def test_carbon_once_and_missing_npp(self):
  recalculate(self.b,self.path)
  r=next(r for r in rows(self.b,'PPR–NPP','Ratios') if r[:5]==['m','all','one','landings','method'])
  self.assertAlmostEqual(r[6],100*10/9/100)
  self.b['NPP']['NPP'][1][0][2]=None;recalculate(self.b,self.path)
  r=next(r for r in rows(self.b,'PPR–NPP','Ratios') if r[:5]==['m','all','one','landings','method']);self.assertIsNone(r[6])
 def test_negative_unfished_group_invalidates(self):
  self.b['Selected model groups']['Group SPPR'][1].append(['m','unfished','all','one',-3])
  recalculate(self.b,self.path);r=next(r for r in rows(self.b,'PPR','Annual') if r[2:6]==['one','landings','method','ppr'])
  self.assertTrue(r[6].startswith('DIVERGED'));self.assertIsNone(r[7])
 def test_selection_before_results_cannot_borrow_previous_model(self):
  from run_region import prepare_selection
  recalculate(self.b,self.path);write_book(self.path,self.b)
  p=self.path.parent/'models/new/model.json';p.parent.mkdir();p.write_text('{"new":true}')
  set_setting(self.b,'selected_model_id','new');set_setting(self.b,'model_path','models/new/model.json');set_setting(self.b,'selection_rationale','Newer model')
  prepare_selection(self.b,self.path);validate_region(self.b,self.path)
  self.assertEqual(rows(self.b,'PPR','Annual'),[])
  self.assertEqual(rows(self.b,'PPR','Matching'),[])
  self.assertTrue(rows(self.b,'Classic PPR','Annual'))
  self.assertEqual(len(list((self.path.parent/'models/previous_results').glob('*.xlsx'))),1)
 def test_partial_update_preserves_metadata_and_other_regions(self):
  from update_project import update
  root=self.path.parent
  set_setting(self.b,'region_name','Example');set_setting(self.b,'region_type','LME')
  recalculate(self.b,self.path);write_book(self.path,self.b)
  project={'Papers':{'Papers':(['unit_id','title'],[['LME_001','Manually reviewed title']])},'Models & coverage':{'Models':(['unit_id','model_id','coverage'],[['LME_001','m',73]])},'Regions & status':{'Regions':(['unit_id','name','type','selected_model_id','selection_rationale','status','workbook','sha256','production_eligible'],[['LME_002','Other','LME',None,None,'pending','other.xlsx','x',False]])},'Regional PPR':{'Annual':(['unit_id',*ANNUAL_HEADER],[['LME_002','', 'all',SIMPLE,'landings','method','ppr','ok',*([7]*70)]])},'Definitions & build':{}}
  write_book(root/'Project.xlsx',project);update(root,[self.path]);p=read_book(root/'Project.xlsx')
  self.assertEqual(rows(p,'Papers','Papers'),[['LME_001','Manually reviewed title']])
  self.assertEqual(rows(p,'Models & coverage','Models')[0][2],73)
  self.assertEqual(next(r for r in rows(p,'Regional PPR','Annual') if r[0]=='LME_002')[8],7)

if __name__=='__main__':unittest.main()
