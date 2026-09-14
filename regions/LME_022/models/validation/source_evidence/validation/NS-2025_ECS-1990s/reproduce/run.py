"""One-pass reproduction of the isolated Saygu 2025 extraction-to-PPR test.

Run from any directory with Python's existing project dependencies. Default
recomputes the named SPPR model through the safe API wrapper. --skip-sppr uses
the archived validation SPPR workbook and avoids new Monte Carlo draws.
"""
from pathlib import Path
import argparse,subprocess,sys,json,os
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
ROOT=next(p for p in HERE.parents if (p/'tools/run_sppr.py').is_file() and (p/'PPRAtlas/archive').is_dir())
MODEL=BASE/'extraction/20251990_East_Coast_of_Scotland_1991-1995'
STEM='22_20251990_East_Coast_of_Scotland_(1991-1995)'
SKILL=ROOT/'skills/codex/ecopath-paper-to-ppr/scripts';EVAL=BASE/'evaluation'
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--skip-sppr',action='store_true');args=ap.parse_args()
LOGS=BASE/'logs';LOGS.mkdir(exist_ok=True);results=[]
def run(name,script,*arguments,allowed=(0,)):
    command=[sys.executable,'-X','utf8',str(script),*map(str,arguments)]
    env=dict(os.environ);env['PYTHONUTF8']='1';env['GLOBALPPR_ROOT']=str(EVAL)
    proc=subprocess.run(command,cwd=ROOT,env=env,text=True,encoding='utf-8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (LOGS/(name+'.log')).write_text(proc.stdout,encoding='utf-8')
    results.append({'stage':name,'returncode':proc.returncode,'command':command})
    if proc.returncode not in allowed:raise RuntimeError(f'{name} returned {proc.returncode}; see {LOGS/(name+".log")}')
    if name=='massbalance' and proc.returncode:
        errors=[line for line in proc.stdout.splitlines() if line.startswith('ERROR ')]
        assert len(errors)==1 and 'group 11 (Ling)' in errors[0],errors
    print(name,proc.returncode,flush=True)
run('environment',SKILL/'check_environment.py')
run('extract',HERE/'extract_north_sea.py')
run('extraction_validate',SKILL/'validate.py',MODEL)
run('massbalance',SKILL/'massbalance_check.py',MODEL,allowed=(0,1))
run('database',SKILL/'database_json.py','--dir',MODEL)
if not args.skip_sppr:
    run('sppr',ROOT/'tools/run_sppr.py','--models',STEM,'--json-dir',MODEL,'--out',BASE/'sppr','--timeout','30')
else:assert (BASE/'sppr'/f'{STEM}.xlsx').is_file()
run('prepare_eval',HERE/'prepare_eval.py')
run('mapping',HERE/'map_north_sea.py')
run('mapping_validate',EVAL/'skills/claude/ewe-species-to-group-mapper/scripts/validate_mapping.py','LME_022','--root',EVAL)
run('ppr_build',EVAL/'tools/build_model_workbook.py','--units','LME_022')
run('ppr_verify',EVAL/'tools/verify_model_workbook.py','--units','LME_022')
run('source_audit',HERE/'audit_north_sea.py')
run('scope_audit',HERE/'verify_scopes_independently.py')
(LOGS/'commands.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('All pipeline stages completed; the documented raw-source Ling mass-balance warning remains. No production selection or atlas data were changed.')
