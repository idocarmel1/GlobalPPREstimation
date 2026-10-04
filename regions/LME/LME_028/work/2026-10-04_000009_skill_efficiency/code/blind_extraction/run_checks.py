"""Bounded reconstruction from isolated PDF-derived coordinates, with actual logs."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[7]
RUN=ROOT/'regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency'
OUT=RUN/'outputs/blind_extraction'; E=OUT/'evidence'; MODEL=OUT/'model_2000s'
HELPERS=ROOT/'tools/skills/paper-to-ppr/resources/extraction/scripts'
trace=[]
def execute(stage,script,args):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat(); clock=time.perf_counter()
    cmd=[sys.executable,'-X','utf8',str(script),*map(str,args)]
    process=subprocess.run(cmd,cwd=ROOT,capture_output=True,encoding='utf-8',timeout=120,env={**os.environ,'PYTHONUTF8':'1'})
    log=E/(stage+'.log');log.write_text(process.stdout+'\nSTDERR:\n'+process.stderr,encoding='utf-8')
    trace.append({'stage':stage,'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.perf_counter()-clock,'returncode':process.returncode,'command':[str(Path(x).relative_to(ROOT)) if Path(x).is_absolute() and Path(x).is_relative_to(ROOT) else x for x in cmd],'log':log.relative_to(OUT).as_posix()})
    (E/'stage_trace.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2),encoding='utf-8')
    print(stage,process.returncode,round(trace[-1]['seconds'],3),flush=True)
    return process
assert execute('extract',Path(__file__).with_name('extract_model.py'),[]).returncode==0
assert execute('write_imports',HELPERS/'write_outputs.py',[OUT/'extraction.json','--outdir',OUT,'--dir-name','model_2000s']).returncode==0
assert execute('validate_imports',HELPERS/'validate.py',[MODEL]).returncode==0
execute('indicative_mass_balance',HELPERS/'massbalance_check.py',[MODEL])
assert execute('convert_roundtrip',HELPERS/'database_json.py',['-d',MODEL]).returncode==0
converted=MODEL/'28_South_China_Sea_NSCS_2000s_blind_Northern_South_China_Sea_(2000s).json'
fidelity=json.loads((MODEL/'SOURCE_FIDELITY_CHECK.json').read_text(encoding='utf-8'))
assert fidelity['exact_value_and_missing_mask_match'] and not fidelity['errors']
data=json.loads(converted.read_text(encoding='utf-8'));assert len(data['group'])==38
converted.replace(MODEL/'model.json')
# The writer input is reproducible from our source coordinates. Only one Ecopath
# model JSON remains; source literals and companion rows are in the canonical JSON.
(OUT/'extraction.json').unlink()
(E/'canonical_identity.json').write_text(json.dumps({'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canonical_model':(MODEL/'model.json').relative_to(OUT).as_posix(),'sha256':hashlib.sha256((MODEL/'model.json').read_bytes()).hexdigest(),'groups':38,'preservation':'No repair/normalization; source-table/missing-mask round trip exact','previous_exception':'Earlier massbalance_check run hit cp1255 UnicodeEncodeError at ≤; this UTF-8 run supersedes incomplete stdout; no scientific changes made for that exception'},ensure_ascii=False,indent=2),encoding='utf-8')
