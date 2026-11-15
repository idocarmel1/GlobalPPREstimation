"""Durable supervisor for the authorized cached-adoption coordinator.

No scientific calculations or automatic recovery writes occur here. Backups are
local recovery material and are removed only after final acceptance.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, traceback
from datetime import datetime, timezone
from contextlib import contextmanager

WORK = Path(__file__).resolve().parents[1]
ROOT = next(p for p in WORK.parents if (p/'Project.xlsx').is_file())
sys.path.insert(0, str(ROOT))
ORIGINAL_ADOPTER_SHA = '8f5dc02329a3d3381022c2ae344cd17431f31df4026538b512ecabb3dd873cbc'
PINS = json.loads((WORK/'outputs/checkpoint_implementation_delta.json').read_text(encoding='utf-8'))['current_source_hashes']
ADOPTER_SHA = PINS[(WORK/'code/adopt_completion.py').relative_to(ROOT).as_posix()]
COVERAGE_SHA = PINS['tools/project_core/calculations/coverage.py']
STATUS = WORK/'outputs/background_adoption_status.json'
RECOVERY = WORK/'tmp/adoption_recovery_attempt3'
LOG = None
SUPERVISOR_LOCK = WORK/'tmp/adoption_supervisor.lock'

def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def record(phase, **details):
    data={'phase':phase,'timestamp':datetime.now(timezone.utc).isoformat(),'supervisor_pid':os.getpid(),'coverage_sha256':COVERAGE_SHA,**details}
    temporary=STATUS.with_suffix('.tmp');temporary.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');os.replace(temporary,STATUS)

@contextmanager
def supervisor_lock():
    fd=os.open(SUPERVISOR_LOCK,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    marker=str(os.getpid()).encode()
    try:
        os.write(fd,marker);os.close(fd)
        yield
    finally:
        if SUPERVISOR_LOCK.is_file() and SUPERVISOR_LOCK.read_bytes()==marker:
            SUPERVISOR_LOCK.unlink()

def main():
    global LOG
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--attempt', required=True, type=int)
    args=parser.parse_args()
    LOG = WORK/'qa'/('adoption_application_attempt'+str(args.attempt)+'.log')
    for name, expected in PINS.items():
        if sha((ROOT/name).read_bytes()) != expected: raise ValueError('Frozen checkpoint implementation changed: '+name)
    adopter=WORK/'code/adopt_completion.py'
    if sha(adopter.read_bytes()) != ADOPTER_SHA: raise ValueError('Coordinator changed')
    if sha((ROOT/'tools/project_core/calculations/coverage.py').read_bytes()) != COVERAGE_SHA: raise ValueError('Coverage implementation changed')
    if (ROOT/'.project-write.lock').exists(): raise ValueError('A central writer lock exists')
    inventory=read(WORK/'inputs/validated_inventory.json')
    audit=read(WORK/'outputs/final_cohort_audit.json')
    if sha((ROOT/'Project.xlsx').read_bytes()) != inventory['project_sha256']: raise ValueError('Original Project differs')
    manifest_path=RECOVERY/'manifest.json'
    if not manifest_path.exists():
        from tools.project_core.registry.publication import PublicationBackup
        backup=PublicationBackup(ROOT,model_pairs={(p['unit_id'],p['model_id']) for p in inventory['pairs']})
        handoff=read(ROOT/read(WORK/'outputs/continuation_handoff.json')['humboldt']['handoff'])
        for value in [handoff['canonical_report'],handoff['retained_historical_original'],str((WORK/'inputs/Project_before_humboldt_review.xlsx').relative_to(ROOT))]:
            path=ROOT/value
            backup.before[path]=path.read_bytes() if path.is_file() else None
        entries=[]
        for path,data in sorted(backup.before.items(),key=lambda v:str(v[0])):
            relative=path.relative_to(ROOT).as_posix()
            digest=sha(data) if data is not None else None
            if relative in audit['protected_files'] and digest != audit['protected_files'][relative]:
                raise ValueError('Recovery preimage differs from scientific audit: '+relative)
            entries.append({'path':relative,'before_sha256':digest})
        RECOVERY.mkdir(parents=True,exist_ok=True)
        objects=RECOVERY/'objects';objects.mkdir(exist_ok=True)
        for path,data in backup.before.items():
            if data is not None:
                target=objects/sha(data)
                if not target.exists(): target.write_bytes(data)
                if sha(target.read_bytes())!=target.name:raise ValueError('Recovery object mismatch')
        payload={'schema_version':1,'purpose':'Exact pre-adoption bytes for interruption recovery; no automatic restore',
                 'created':datetime.now(timezone.utc).isoformat(),'coordinator_sha256':ADOPTER_SHA,'entries':entries}
        manifest_path.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
        del backup
    manifest=read(manifest_path)
    if manifest['coordinator_sha256']!=ORIGINAL_ADOPTER_SHA:raise ValueError('Original recovery coordinator differs')
    for entry in manifest['entries']:
        current=ROOT/entry['path'];data=current.read_bytes() if current.is_file() else None
        if (sha(data) if data is not None else None)!=entry['before_sha256']:raise ValueError('Input changed after durable snapshot: '+entry['path'])
        if data is not None and sha((RECOVERY/'objects'/entry['before_sha256']).read_bytes())!=entry['before_sha256']:raise ValueError('Recovery object changed')
    snapshot_hash=sha(manifest_path.read_bytes())
    if not args.run:
        record('PREPARED',recovery_manifest=manifest_path.relative_to(ROOT).as_posix(),recovery_sha256=snapshot_hash,files=len(manifest['entries']))
        return
    handoff=ROOT/read(WORK/'outputs/continuation_handoff.json')['humboldt']['handoff']
    env=dict(os.environ,PYTHONUTF8='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',TEMP=str(WORK/'tmp'),TMP=str(WORK/'tmp'))
    with LOG.open('x',encoding='utf-8') as output:
        child=subprocess.Popen([sys.executable,'-B','-u',str(adopter),'--apply','--review-handoff',str(handoff)],cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        record('RUNNING',child_pid=child.pid,recovery_manifest=manifest_path.relative_to(ROOT).as_posix(),recovery_sha256=snapshot_hash,log=LOG.relative_to(ROOT).as_posix())
        code=child.wait()
    record('COMPLETED' if code==0 else 'FAILED',child_pid=child.pid,exit_code=code,recovery_manifest=manifest_path.relative_to(ROOT).as_posix(),recovery_sha256=snapshot_hash,log=LOG.relative_to(ROOT).as_posix())
    raise SystemExit(code)

if __name__=='__main__':
    with supervisor_lock():
        try:main()
        except Exception as error:
            record('SUPERVISOR_FAILED',error=str(error),traceback=traceback.format_exc())
            raise
