"""Preserve provisional exclusions, then solve only the new source-valid replacements."""
from pathlib import Path
import json,os,subprocess,sys,time,shutil
ROOT=Path(__file__).resolve().parents[1]
def run():
    selected=json.loads((ROOT/'results/selected_models.json').read_text(encoding='utf-8'))
    provisional=json.loads((ROOT/'results/selected_models.provisional.v1.json').read_text(encoding='utf-8'))
    final_ids={r['model_id'] for r in selected};old_ids={r['model_id'] for r in provisional}
    excluded=old_ids-final_ids
    for mid in sorted(excluded):
        src=(ROOT/'results/models'/mid).resolve();dst=(ROOT/'results/excluded_provisional_models'/mid).resolve()
        assert src.is_relative_to(ROOT.resolve()) and dst.is_relative_to(ROOT.resolve())
        dst.parent.mkdir(exist_ok=True)
        if src.exists():
            assert not dst.exists()
            shutil.move(str(src),str(dst))
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    outcomes=[]
    for row in selected:
        mid=row['model_id']
        if mid in old_ids:continue
        print('RUN REPLACEMENT',mid,flush=True);start=time.time()
        with (ROOT/'verification'/f'run_{mid}.log').open('w',encoding='utf-8') as log:
            proc=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'src/run_study.py'),'--model',mid],env=env,stdout=log,stderr=subprocess.STDOUT)
        outcomes.append(dict(model_id=mid,exit_code=proc.returncode,elapsed_seconds=time.time()-start))
        (ROOT/'verification/replacement_timings.json').write_text(json.dumps(outcomes,indent=2),encoding='utf-8')
        print('FINISHED',outcomes[-1],flush=True)
        if proc.returncode:raise SystemExit(proc.returncode)
if __name__=='__main__':run()
