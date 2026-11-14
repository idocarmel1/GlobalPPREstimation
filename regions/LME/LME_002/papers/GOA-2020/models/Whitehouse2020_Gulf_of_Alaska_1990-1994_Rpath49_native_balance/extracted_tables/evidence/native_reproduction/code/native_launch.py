"""Run the authenticated native R balance and record execution identities."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')
RUN=Path(__file__).resolve().parents[1]
ROOT=next(p for p in RUN.parents if (p/'Project.xlsx').exists())
MODEL=ROOT/'regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49'
SOURCE=MODEL/'inputs/native'
OUT=RUN/'outputs/native_balance';OUT.mkdir(parents=True,exist_ok=True)
QA=RUN/'qa';QA.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
rscripts=list((RUN/'inputs/native_R_runtime').rglob('Rscript.exe'))
rscript=next(p for p in rscripts if p.parent.name=='x64')
env={**os.environ,'R_LIBS_USER':str(RUN/'inputs/native_R_library'),
     'LC_ALL':'English_United States.utf8','LANG':'en_US.UTF-8'}
version=subprocess.run([str(rscript),'--version'],capture_output=True,text=True,encoding='utf-8',errors='replace',env=env)
print(version.stdout+version.stderr,flush=True)
files=list(SOURCE.glob('*'))+[MODEL/'model.json']
before={rel(p):sha(p) for p in files if p.is_file()}
assert before[rel(MODEL/'model.json')]=='10dfbf57dcc9c1ca2e57460637709a061c9264a7e29bf17e0028fadf4c919125'
script=RUN/'code/native_balance.R'
record={'stage':'native_Rpath_balance','run_id':RUN.name,'source_model_id':MODEL.name,
 'official_Rpath_commit':'fe63f6d370d942ff1786f4d649e432fbfb85f81b',
 'source_hashes_before':before,'Rscript_version':(version.stdout+version.stderr).strip(),
 'Rscript_sha256':sha(rscript),'driver_sha256':sha(script),
 'driver':rel(script),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'process_environment':{'LC_ALL':env['LC_ALL'],'LANG':env['LANG'],'R_LIBS_USER':'run-local inputs/native_R_library'},
 'setup_correction':'Inherited Linux LC_ALL=C.UTF-8 is unavailable in Windows R and hid Hebrew paths under fallback C locale; child-process UTF-8 Windows locale verified library namespace visibility. No R code or global settings changed.',
 'calculation_scope':'Pinned Rpath read.rpath.params + rpath, unmodified source; no normalization, fitting, parameter repairs, PPR, map, selection, or registry writes',
 'runtime_acquisition':json.loads((RUN/'inputs/native_runtime_downloads/runtime_acquisition.json').read_text(encoding='utf-8'))}
if (QA/'native_execution.json').exists() and not (QA/'native_startup_failure.json').exists():
 shutil.copy2(QA/'native_execution.json',QA/'native_startup_failure.json')
 shutil.copy2(QA/'native_execution.log',QA/'native_startup_failure.log')
with (QA/'native_execution.log').open('w',encoding='utf-8') as log:
 proc=subprocess.run([str(rscript),'--vanilla',str(script),str(SOURCE),str(OUT),str(RUN/'inputs/native_R_library')],
                      cwd=RUN,stdout=log,stderr=subprocess.STDOUT,env=env)
record.update({'returncode':proc.returncode,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'source_hashes_after':{rel(p):sha(p) for p in files if p.is_file()}})
record['all_source_bytes_unchanged']=record['source_hashes_before']==record['source_hashes_after']
record['outputs']=[{'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.iterdir()) if p.is_file()]
(QA/'native_execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'returncode':proc.returncode,'all_source_bytes_unchanged':record['all_source_bytes_unchanged'],'outputs':len(record['outputs']),'log':rel(QA/'native_execution.log')},indent=2))
if proc.returncode:print((QA/'native_execution.log').read_text(encoding='utf-8')[-6000:])
raise SystemExit(proc.returncode)
