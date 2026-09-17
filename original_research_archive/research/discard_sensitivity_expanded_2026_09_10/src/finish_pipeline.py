"""Resume final validation after the two owned, bounded calculation queues finish."""
from pathlib import Path
import json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def ready():
    a=(ROOT/'verification/run_all.log').read_text(encoding='utf-8',errors='replace')
    b=(ROOT/'verification/run_replacements.log').read_text(encoding='utf-8',errors='replace')
    return 'FINISHED 52_1_Sea_of_Okhotsk_NE_(1980)' in a and "'model_id': '462_462_Northern_Gulf_of_St_Lawrence_(1990)', 'exit_code': 0" in b
def run():
    while not ready():time.sleep(10)
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    stages=['audit_saved_differences','summarize','audit_inputs','verify_outputs','findings','static_checks','render_report']
    for stage in stages:
        print('STAGE',stage,flush=True);start=time.time()
        with (ROOT/'verification'/f'final_{stage}.log').open('w',encoding='utf-8') as log:
            result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'src'/f'{stage}.py')],env=env,stdout=log,stderr=subprocess.STDOUT)
        print('FINISHED',stage,'exit',result.returncode,'seconds',round(time.time()-start,1),flush=True)
        if result.returncode:raise SystemExit(result.returncode)
    print('NUMERICAL AND RENDER PIPELINE COMPLETE; browser verification remains',flush=True)
if __name__=='__main__':run()
