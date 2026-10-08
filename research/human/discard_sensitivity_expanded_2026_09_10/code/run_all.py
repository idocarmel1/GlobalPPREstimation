"""Sequential bounded-memory orchestration; never runs a production exporter."""
from pathlib import Path
import json,subprocess,sys,os,time,hashlib
from provenance import fingerprint
ROOT=Path(__file__).resolve().parents[1]
def run():
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    selected=json.loads((ROOT/'results/selected_models.json').read_text(encoding='utf-8'))
    names=[r['model_id'] for r in selected]+[p.stem for p in sorted((ROOT/'inputs/references').glob('*.json'))]
    paths={r['model_id']:ROOT/r['snapshot_path'] for r in selected}
    paths.update({p.stem:p for p in (ROOT/'inputs/references').glob('*.json')})
    outcomes=[]
    engine_hash={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'src/experimental_engine').glob('*.py')}
    for name in names:
        target=ROOT/'results/models'/name/'study.json'
        identity=fingerprint(paths[name]);stamp=target.parent/'calculation_provenance.json'
        if target.exists():
            saved=json.loads(target.read_text(encoding='utf-8'))
            matches=stamp.exists() and json.loads(stamp.read_text(encoding='utf-8')).get('calculation_sha256')==identity['calculation_sha256']
            if matches and len(saved['records'])==2616 and len(saved['fraction_grid'])==27:
                print('REUSE completed',name,flush=True);continue
        start=time.time();print('RUN',name,flush=True)
        with (ROOT/'verification'/f'run_{name}.log').open('w',encoding='utf-8') as log:
            result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'src/run_study.py'),'--model',name],env=env,stdout=log,stderr=subprocess.STDOUT)
        row=dict(model_id=name,exit_code=result.returncode,elapsed_seconds=time.time()-start,engine_hashes=engine_hash)
        outcomes.append(row)
        (ROOT/'verification/run_timings.json').write_text(json.dumps(outcomes,indent=2),encoding='utf-8')
        print('FINISHED',name,row,flush=True)
        if result.returncode:raise SystemExit('Private runner failed; inspect log for '+name)
        stamp.write_text(json.dumps(identity,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':run()
