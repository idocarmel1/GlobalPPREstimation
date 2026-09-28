"""Only the requested direct diagnose_sppr call, with a bounded external caller."""
from pathlib import Path
import sys,json,math,time,hashlib,shutil,traceback
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());MID=sys.argv[1];OPTION=sys.argv[2];DEST=ROOT/'regions/LME_049/models'/MID;EV=DEST/'evidence';EV.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from create_PPRS_excel import load_model
p=EV/(MID+'.json')
if not p.exists():shutil.copy2(DEST/'model.json',p)
assert p.read_bytes()==(DEST/'model.json').read_bytes()
m,_=load_model(str(p));start=time.monotonic()
try:
    r=m.diagnose_sppr(TE_option=OPTION,short=False,flat=False,return_sppr=False,thresholds=None,det_collapse_mode='never',det_open_mode='none',det_theta=1.0,det_external_sppr=0.0)
    error=None
except Exception as exc:
    r=None;error={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,float) and not math.isfinite(x):return None
    if hasattr(x,'item'):return clean(x.item())
    return x
result={'model_id':MID,'TE_option':OPTION,'direct_diagnose_sppr_return':clean(r),'elapsed_seconds':time.monotonic()-start,'call_error':error}
(EV/('diagnose_sppr_'+OPTION.replace(' ','_')+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
print(OPTION,r['status'] if r is not None else 'RAISED EXCEPTION; NO RETURN')
