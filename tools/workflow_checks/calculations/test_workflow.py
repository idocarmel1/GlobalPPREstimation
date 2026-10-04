import sys,unittest,tempfile,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from tools.project_core.workbooks.workbooks import *
from tools.project_core.calculations.regional import *

def fixture():
 b={s:{} for s in REGION_SHEETS}
 b['Overview']['Settings']=(['field','value'],[['unit_id','LME_001'],['selected_model_id','m'],['model_path','papers/P/models/m/model.json'],['results_model_id','m'],['taxon_detail_year',2019],['catch_basis','landings']])
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
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.path=self.root/'regions/LME/LME_001/LME_001.xlsx';p=self.path.parent/'papers/P/models/m/model.json';p.parent.mkdir(parents=True);p.write_text('{}');self.b=fixture()
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
  recalculate(self.b,self.path);(self.path.parent/'papers/P/models/m/model.json').write_text('{"changed":true}')
  with self.assertRaisesRegex(ValueError,'model JSON changed'):validate_region(self.b,self.path)
 def test_source_inventory_mapping_without_coefficients_stays_unavailable(self):
  self.b['Selected model groups']['Groups']=(['seq','group_name','biomass'],[[1,'A',2.5],[2,'B',None]])
  self.b['Selected model groups']['Group SPPR'][1].clear()
  self.b['PPR']['Annual'][1].clear()
  self.b['Diagnostics']['review']=(['method','status'],[['GE','NOT_RUN'],['TE','NOT_RUN']])
  set_setting(self.b,'results_model_id',None)
  set_setting(self.b,'calculation_status','selected; constructor blocked; NOT_RUN')
  protected=copy.deepcopy(self.b['Selected model groups'])
  diagnosis=copy.deepcopy(self.b['Diagnostics'])
  recalculate(self.b,self.path)
  write_book(self.path,self.b);reopened=read_book(self.path);validate_region(reopened,self.path)
  self.assertEqual(len(rows(reopened,'PPR','Matching')),2)
  self.assertEqual(rows(reopened,'PPR','Taxon SPPR'),[])
  self.assertEqual(rows(reopened,'PPR','Annual'),[])
  self.assertEqual(rows(reopened,'PPR','Taxon PPR inspected year'),[])
  self.assertEqual(self.b['Selected model groups'],protected)
  self.assertEqual(self.b['Diagnostics'],diagnosis)
  self.assertIn('unavailable',overview(reopened)['calculation_status'].lower())
  classic=next(r for r in records(reopened,'Classic PPR','Annual') if r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric']=='ppr')
  self.assertEqual(classic[2019],320)
 def test_inventory_member_missing_coefficient_is_unknown_not_invalid_mapping(self):
  self.b['Selected model groups']['Groups']=(['seq','group_name'],[[1,'A'],[2,'B']])
  header,group_rows=self.b['Selected model groups']['Group SPPR']
  self.b['Selected model groups']['Group SPPR']=(header,[r for r in group_rows if r[1]=='A'])
  recalculate(self.b,self.path)
  coeff={(r['taxon'],r['method']):r['sppr'] for r in records(self.b,'PPR','Taxon SPPR')}
  self.assertIsNone(coeff['b','one']);self.assertIsNone(coeff['b','two'])
  annual=next(r for r in records(self.b,'PPR','Annual') if r['method']=='one' and r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric']=='ppr')
  self.assertEqual(annual[2019],10)
  self.b['PPR']['Matching'][1][0][2]='not a source group'
  with self.assertRaisesRegex(ValueError,'Unknown group'):recalculate(self.b,self.path)
 def test_carbon_once_and_missing_npp(self):
  recalculate(self.b,self.path)
  r=next(r for r in rows(self.b,'PPR–NPP','Ratios') if r[:5]==['m','all','one','landings','method'])
  self.assertAlmostEqual(r[6],100*10/9/100)
  self.b['NPP']['NPP'][1][0][2]=None;recalculate(self.b,self.path)
  r=next(r for r in rows(self.b,'PPR–NPP','Ratios') if r[:5]==['m','all','one','landings','method']);self.assertIsNone(r[6])
 def test_repeated_calculation_keeps_model_source_scopes_available(self):
  for scope in ['PP','inner']:
   self.b['Selected model groups']['Group SPPR'][1].extend([['m','A',scope,'one',5.],['m','B',scope,'one',None]])
   self.b['PPR']['Annual'][1].append(['m',scope,'one','landings','method','ppr','provisional: retained WARN',*([None]*70)])
  for _ in range(2):
   recalculate(self.b,self.path)
   for r in records(self.b,'PPR','Annual'):
    if r['scope'] not in ['PP','inner'] or r['method']!='one' or r['metric']!='ppr':continue
    if r['unidentified']=='simple':
     self.assertEqual(r['status'],'unavailable: simple reference has no source decomposition')
     self.assertIsNone(r[2019])
    else:
     self.assertEqual(r['status'],'provisional: retained WARN')
     self.assertEqual(r[2019],10.)
 def test_negative_unfished_group_invalidates(self):
  self.b['Selected model groups']['Group SPPR'][1].append(['m','unfished','all','one',-3])
  recalculate(self.b,self.path);r=next(r for r in rows(self.b,'PPR','Annual') if r[2:6]==['one','landings','method','ppr'])
  self.assertTrue(r[6].startswith('DIVERGED'));self.assertIsNone(r[7])
 def test_explicit_provisional_preserves_numeric_result_and_problem(self):
  self.b['PPR']['Annual'][1][0][6]='provisional: diagnostic FAIL; user requested review display'
  self.b['Selected model groups']['Group SPPR'][1][0][4]=-5.
  recalculate(self.b,self.path)
  r=next(r for r in records(self.b,'PPR','Annual') if r['method']=='one' and r['catch_basis']=='landings' and r['unidentified']=='method' and r['metric']=='ppr')
  self.assertTrue(r['status'].startswith('provisional:'))
  self.assertIn('negative source-group SPPR',r['status'])
  self.assertEqual(r[2019],-10.)
  pairs,_,_=comparison_tables(self.b)
  self.assertFalse(any('one' in p[4:6] for p in pairs))
 def test_obsolete_selection_stage_is_rejected_without_modifying_results(self):
  import subprocess
  recalculate(self.b,self.path);write_book(self.path,self.b)
  before=self.path.read_bytes()
  cli=Path(__file__).resolve().parents[2]/'cli/region.py'
  result=subprocess.run([sys.executable,str(cli),'--region',str(self.path.parent),'--stage','prepare-selection'],capture_output=True,text=True)
  self.assertNotEqual(result.returncode,0)
  self.assertIn('invalid choice',result.stderr)
  self.assertEqual(self.path.read_bytes(),before)
  self.assertFalse((self.path.parent/'models/previous_results').exists())
 def test_partial_update_preserves_metadata_and_other_regions(self):
  from tools.project_core.registry.update_project import update
  import gzip,json
  root=self.root
  context=root/'common_reference_data/atlas_source_context';context.mkdir(parents=True)
  with gzip.open(context/'catalog.json.gz','wt',encoding='utf-8') as f:json.dump({'curated_region_ids':['LME_001','LME_002']},f)
  set_setting(self.b,'region_name','Example');set_setting(self.b,'region_type','LME')
  recalculate(self.b,self.path);write_book(self.path,self.b)
  project={'Papers':{'Papers':(['unit_id','title'],[['LME_001','Manually reviewed title']])},'Models & coverage':{'Models':(['unit_id','model_id','coverage'],[['LME_001','m',73]])},'Regions & status':{'Regions':(['unit_id','name','type','selected_model_id','selection_rationale','status','workbook','sha256','production_eligible'],[['LME_002','Other','LME',None,None,'pending','other.xlsx','x',False]])},'Regional PPR':{'Annual':(['unit_id',*ANNUAL_HEADER],[['LME_002','', 'all',SIMPLE,'landings','method','ppr','ok',*([7]*70)]])},'Definitions & build':{}}
  mh,mr=project['Models & coverage']['Models'];mh.append('selection_rationale');mr[0].append(None)
  mr.append(['LME_001','alternative',42,'Retained for later failure investigation; not selected.'])
  write_book(root/'Project.xlsx',project);update(root,[self.path]);p=read_book(root/'Project.xlsx')
  self.assertEqual(next(r for r in records(p,'Models & coverage','Models') if r['model_id']=='alternative')['selection_rationale'],'Retained for later failure investigation; not selected.')
  self.assertEqual(records(p,'Papers','Papers')[0]['title'],'Manually reviewed title')
  self.assertEqual(records(p,'Papers','Papers')[0]['atlas_region_rank'],1)
  self.assertEqual(rows(p,'Models & coverage','Models')[0][2],73)
  self.assertEqual(next(r for r in rows(p,'Regional PPR','Annual') if r[0]=='LME_002')[8],7)
  update(root,[self.path]);p=read_book(root/'Project.xlsx')
  self.assertEqual(records(p,'Papers','Papers')[0]['atlas_region_rank'],1)
  other=next(r for r in records(p,'Regions & status','Regions') if r['unit_id']=='LME_002')
  self.assertEqual(other['name'],'Other');self.assertIsNone(other['atlas_region_rank'])
 def test_project_update_rejects_inputs_changed_during_integration(self):
  from tools.project_core.registry.update_project import update
  from unittest.mock import patch
  root=self.root;project_path=root/'Project.xlsx'
  for changed in ['project','region']:
   with self.subTest(changed=changed):
    b=fixture();set_setting(b,'region_name','Example');set_setting(b,'region_type','LME')
    recalculate(b,self.path);write_book(self.path,b)
    project={'Papers':{'Papers':(['unit_id','title'],[['LME_001','Reviewed title']])},'Models & coverage':{'Models':(['unit_id','model_id'],[['LME_001','m']])},'Definitions & build':{}}
    write_book(project_path,project);initial_project_sha=sha(project_path);modified=[]
    def concurrent_edit(*args):
     target=project_path if changed=='project' else self.path
     newer=read_book(target)
     if changed=='project':newer['Papers']['Papers'][1][0][1]='Newer researcher title'
     else:set_setting(newer,'researcher_note','Newer regional review')
     write_book(target,newer);modified.append((target,sha(target)))
    with patch('tools.project_core.registry.update_project.ensemble_ids',return_value=set()),patch('tools.project_core.registry.update_project.apply_atlas_ranks',side_effect=concurrent_edit):
     with self.assertRaisesRegex(ValueError,'changed during'):
      update(root,[self.path])
    self.assertEqual(len(modified),1)
    self.assertEqual(sha(modified[0][0]),modified[0][1])
    if changed=='region':self.assertEqual(sha(project_path),initial_project_sha)
 def test_all_region_update_ignores_adjacent_validation_appendices(self):
  import gzip,json,subprocess
  root=self.root
  context=root/'common_reference_data/atlas_source_context';context.mkdir(parents=True)
  with gzip.open(context/'catalog.json.gz','wt',encoding='utf-8') as f:json.dump({'curated_region_ids':['LME_001']},f)
  region=root/'regions/LME/LME_001/LME_001.xlsx';region.parent.mkdir(parents=True,exist_ok=True)
  model=region.parent/'papers/P/models/m/model.json';model.parent.mkdir(parents=True,exist_ok=True);model.write_text('{}',encoding='utf-8')
  set_setting(self.b,'region_name','Example');set_setting(self.b,'region_type','LME')
  recalculate(self.b,region);write_book(region,self.b)
  appendix=region.parent/'LME001_taxon_mapping_appendix.xlsx'
  write_book(appendix,{'Sources':{'Sources':(['description'],[['Review evidence; not a regional workbook']])}})
  project={'Papers':{'Papers':(['unit_id','title'],[['LME_001','Reviewed title']])},'Models & coverage':{'Models':(['unit_id','model_id'],[['LME_001','m']])},'Definitions & build':{}}
  write_book(root/'Project.xlsx',project)
  before=sha(appendix)
  result=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[2]/'cli/project.py'),'--all','--root',str(root)],capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stdout+result.stderr)
  self.assertEqual([r['unit_id'] for r in records(read_book(root/'Project.xlsx'),'Regions & status','Regions')],['LME_001'])
  self.assertEqual(sha(appendix),before)

if __name__=='__main__':unittest.main()
