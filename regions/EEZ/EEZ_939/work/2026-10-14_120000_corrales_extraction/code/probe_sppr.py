from pathlib import Path
import sys,json,hashlib,traceback,platform
ROOT=Path(__file__).resolve().parents[6];WORK=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'tools/scientific_code/PPREstimation';sys.path.insert(0,str(ENGINE))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
settings=dict(underdetermined=False,zero_catch=True,zero_biomass_accum=True,default_gs=True,normalize_DC=True,DC_tol=.001,balance_BA_after_DC_normalization=False)
for period in ['1990_1994','2008_2012']:
 stage=Path(json.loads((WORK/f'outputs/stage_{period}.json').read_text(encoding='utf-8'))['path'])
 path=next(p for p in stage.glob('*.json') if isinstance(json.loads(p.read_text(encoding='utf-8')).get('group'),list))
 result={'schema_version':1,'period':period,'settings':settings,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'engine_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ENGINE/'ModelData.py',ENGINE/'PPRCalculator.py',ENGINE/'utils.py']},'python':sys.version,'executable':sys.executable,'methods':{}}
 md=ModelData(str(path));result['loader']='passed'
 try:
  calc=PPRCalculator.from_modeldata(md,**settings);result['constructor']='passed'
  for option in ['GE','TE','With Egestion']:
   try:
    diag,*returns=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True)
    result['methods'][option]={'status':'executed','diagnostics':diag}
   except Exception as e:result['methods'][option]={'status':'exception','exception':repr(e),'traceback':traceback.format_exc()}
 except Exception as e:
  result['constructor']='blocked';result['exception']=repr(e);result['traceback']=traceback.format_exc()
  for option in ['GE','TE','With Egestion']:result['methods'][option]={'status':'NOT_RUN','reason':repr(e)}
 (WORK/f'qa/{period}_admission.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
 print(period,result['constructor'],result.get('exception',''),flush=True)
