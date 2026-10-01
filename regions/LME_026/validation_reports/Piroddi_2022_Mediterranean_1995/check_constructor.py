from pathlib import Path
import json,sys,hashlib,traceback,warnings
OUT=Path(__file__).parent;ROOT=OUT.parents[3];REGION=OUT.parents[1];ENGINE=ROOT/'tools/scientific_code/PPREstimation';D=REGION/'models/Piroddi_2022_Mediterranean_1995/diagnostics'
sys.path.insert(0,str(ENGINE));from ModelData import ModelData
from PPRCalculator import PPRCalculator
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
model=REGION/'models/Piroddi_2022_Mediterranean_1995/model.json';before=sha(model);src=json.loads(model.read_text(encoding='utf-8'))
strict=D/'26_2602022_Mediterranean_Piroddi_Source_(1995).json';staged=D/'26_2602022_Mediterranean_Piroddi_(1995).json'
assert json.loads(strict.read_text(encoding='utf-8'))==src
original=json.loads((D/'loader_audit.json').read_text(encoding='utf-8'));results={}
for label,path,settings in [('strict_source',strict,{'zero_catch':False,'zero_biomass_accum':False,'default_gs':False}),('documented_loader_defaults',staged,{'zero_catch':False,'zero_biomass_accum':True,'default_gs':True})]:
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always');data=ModelData(str(path));data.lme=26
            calc=PPRCalculator.from_modeldata(data,underdetermined=False,normalize_DC=False,**settings)
        results[label]={'status':'LOADED','settings':settings,'input_sha256':sha(path),'warnings':[str(w.message) for w in caught]}
    except Exception as exc:
        results[label]={'status':'EXCEPTION','exception_type':type(exc).__name__,'exception':str(exc),'settings':settings,'input_sha256':sha(path),'traceback':traceback.format_exc().replace(str(ROOT),'[repository]'),'matches_retained_exception':str(exc)==original[label]['exception']}
    assert results[label]['status']=='EXCEPTION' and results[label]['matches_retained_exception'],results[label]
assert sha(model)==before
result={'date':'2026-09-30','scope':'Bounded constructor admission only; diagnose_sppr not called; no parameter writes, Monte Carlo or coefficient generation','canonical_model_sha256':before,'canonical_unchanged':True,'engine_sha256':{p.name:sha(p) for p in [ENGINE/'ModelData.py',ENGINE/'PPRCalculator.py']},'normalize_DC':False,'underdetermined':False,'admission':results,'methods':[{'method':m,'status':'NOT_RUN','direct_return':None,'basal_source_matrix':None,'rho_living':None,'b':None,'pool_70_sppr':None,'pool_71_sppr':None} for m in ['GE','TE','With Egestion']]}
(OUT/'current_constructor_check.json').write_text(json.dumps(result,indent=2,ensure_ascii=True),encoding='utf-8')
print(json.dumps({'strict_source':results['strict_source']['status'],'documented_defaults':results['documented_loader_defaults']['status'],'both_match_retained_exception':True,'canonical_unchanged':True},ensure_ascii=True))
