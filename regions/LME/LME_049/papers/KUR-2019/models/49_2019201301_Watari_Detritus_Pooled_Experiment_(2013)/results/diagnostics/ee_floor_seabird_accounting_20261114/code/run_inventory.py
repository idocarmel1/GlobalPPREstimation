"""Run canonical SPPR method inventory on an already audited scenario state."""
from pathlib import Path
import argparse,sys,json,gzip,hashlib,os,time,traceback,multiprocessing as mp,copy,warnings
sys.dont_write_bytecode=True
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def configure(engine):
 sys.path.insert(0,str(engine));sys.path.insert(1,str(ROOT/'research/agents/regional_ge_integration_20260928/evidence'))
def pack(value):
 from runtime_codec import encode
 import sympy
 if isinstance(value,sympy.Basic):return {'type':'sympy_expression','srepr':sympy.srepr(value),'display':str(value)}
 if isinstance(value,dict):return {'type':'dict','items':[[pack(k),pack(v)] for k,v in value.items()]}
 if isinstance(value,tuple):return {'type':'tuple','values':[pack(x) for x in value]}
 if isinstance(value,list):return [pack(x) for x in value]
 return encode(value)
def worker(conn,engine,state_path):
 configure(engine)
 import numpy as np
 from runtime_codec import decode,encode
 from PPRCalculator import PPRCalculator
 from create_PPRS_excel import SPEC_BY_KEY
 raw=Path(state_path).read_bytes()
 data=json.loads(gzip.decompress(raw) if str(state_path).endswith('.gz') else raw)
 state=decode(data)
 base=state if isinstance(state,PPRCalculator) else PPRCalculator.__new__(PPRCalculator)
 if not isinstance(state,PPRCalculator):base.__dict__.update(state)
 conn.send(('ready',None))
 while True:
  key=conn.recv()
  if key is None:return
  c=copy.deepcopy(base);start=time.monotonic()
  np.random.seed(20261114)
  with warnings.catch_warnings(record=True) as ws:
   try:
    if key.startswith('MC_'):
     option='GE' if key=='MC_new_GE' else 'TE'
     value=c.monte_carlo_SPPR(n_samples=100,TE_error_percent=10,TE_error_cut_percent=20,kind='new',TE_option=option,silent=True,method_kwargs=None if option=='GE' else {'fix_EE_0_cases':True},exclude_diverged=True,return_diagnostics=True)
     frame=value[0]; extras=value[-1]
    else:
     value=SPEC_BY_KEY[key].run(c,100);frame=value[0];extras=value[1]
    vals=np.asarray(frame,dtype=float)
    fields=['p','q','M0','egestion','growth','predation','catch','net_migration','EE','_DC','_det_fate','external_mortality_export','det_export']
    unchanged=all(encode(getattr(c,k))==encode(getattr(base,k)) for k in fields)
    result={'execution':'returned','elapsed_seconds':time.monotonic()-start,'full_return':pack(value),'shape':list(vals.shape),'negative_entries':int((vals<0).sum()),'nan_entries':int(np.isnan(vals).sum()),'infinite_entries':int(np.isinf(vals).sum()),'protected_runtime_unchanged':unchanged,'source_resolved':SPEC_BY_KEY[key].source_resolved,'mc':pack(extras) if key.startswith('MC_') else None}
   except Exception as e:result={'execution':'exception','elapsed_seconds':time.monotonic()-start,'exception_type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
  result['warnings']=[str(w.message) for w in ws]
  conn.send(result)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--engine',required=True,type=Path);ap.add_argument('--state',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
 engine=a.engine.resolve();state=a.state.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 configure(engine)
 from create_PPRS_excel import ALL_METHOD_KEYS
 ctx=mp.get_context('spawn');proc=conn=None
 statuses={}
 for key in ALL_METHOD_KEYS:
  if proc is None:
   conn,child=ctx.Pipe();proc=ctx.Process(target=worker,args=(child,str(engine),str(state)));proc.start();child.close()
   if not conn.poll(180):proc.terminate();proc.join();raise TimeoutError('Worker initialization exceeded 180 seconds')
   assert conn.recv()[0]=='ready'
  conn.send(key)
  if conn.poll(180):result=conn.recv()
  else:
   proc.terminate();proc.join();conn.close();proc=conn=None
   result={'execution':'timeout','seconds':180}
  raw=json.dumps(result,ensure_ascii=False,allow_nan=False).encode('utf-8')
  artifact=out/(key+'.json.gz');artifact.write_bytes(gzip.compress(raw,mtime=0));assert gzip.decompress(artifact.read_bytes())==raw
  statuses[key]={k:v for k,v in result.items() if k not in ['full_return','traceback','warnings']}
  print(key,json.dumps({k:v for k,v in statuses[key].items() if k!='mc'}),flush=True)
  (out/'summary.json').write_text(json.dumps({'methods':statuses,'all_method_keys':list(ALL_METHOD_KEYS),'state_sha256':sha(state),'engine_hashes':{p.name:sha(p) for p in engine.glob('*.py')},'mc_samples':100,'mc_seed':20261114,'time_budget_per_method_seconds':180,'fresh_draws':True,'publication':False},ensure_ascii=False,indent=2),encoding='utf-8')
 if proc is not None:
  conn.send(None);proc.join(10)
  if proc.is_alive():proc.terminate();proc.join()
  conn.close()
 assert set(statuses)==set(ALL_METHOD_KEYS)
 artifacts=[{'path':p.name,'sha256':sha(p)} for p in out.iterdir() if p.is_file() and p.name!='verification.json']
 (out/'verification.json').write_text(json.dumps({'inventory_complete':True,'count':len(statuses),'artifacts':artifacts,'actual_outcomes_preserved':True},indent=2),encoding='utf-8')
if __name__=='__main__':main()
