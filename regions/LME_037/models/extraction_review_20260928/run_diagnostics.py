from pathlib import Path
import sys,json,pickle,traceback,warnings,shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[4];R=Path(__file__).resolve().parent
MD=ROOT/'regions/LME_037/models/Bacalso2026_Visayan_Sea_1997_baseline'
D=MD/'diagnostics';D.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
def serial(o):
    if hasattr(o,'to_dict'):return o.to_dict()
    if isinstance(o,np.ndarray):return o.tolist()
    if isinstance(o,np.generic):return o.item()
    return str(o)
def save(p,obj):p.write_text(json.dumps(obj,indent=2,default=serial),encoding='utf8')
source=next(MD.glob('37_3702026_*.json'));data=ModelData(str(source));audit={};calc=None
data.groups_data.to_csv(D/'groups_before_defaults.csv');data.DC.to_csv(D/'diet_before_defaults.csv');data.det_fate.to_csv(D/'routing_completed_by_loader.csv')
for name,kwargs in [('strict_source',dict(zero_catch=False,zero_biomass_accum=False,default_gs=False)),('standard_loader',dict(zero_catch=True,zero_biomass_accum=True,default_gs=True)),('unchanged_diet_rounding_tolerance',dict(zero_catch=True,zero_biomass_accum=True,default_gs=True,DC_tol=.0021,normalize_DC=False))]:
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always'); candidate=PPRCalculator.from_modeldata(data,**kwargs)
        audit[name]={'status':'LOADED','configuration':kwargs,'warnings':[str(w.message) for w in caught]};calc=candidate;active=name
    except Exception as e:
        audit[name]={'status':'EXCEPTION','configuration':kwargs,'exception':str(e),'type':type(e).__name__,'traceback':traceback.format_exc()}
save(D/'loader_audit.json',audit)
results=[]
for option in ['GE','TE','With Egestion']:
    if calc is None:
        results.append({'TE_option':option,'status':'NOT_RUN','reason':'Calculator construction failed. No diagnose_sppr return exists. See loader_audit.json.'});continue
    try:
        raw=calc.diagnose_sppr(TE_option=option,short=False,flat=False)
        file=option.replace(' ','_');(D/f'{file}_raw.pkl').write_bytes(pickle.dumps(raw));save(D/f'{file}_raw.json',raw)
        results.append({'TE_option':option,'status':'RETURNED','configuration':active,'raw_file':f'{file}_raw.json','raw_return':raw})
    except Exception as e:results.append({'TE_option':option,'status':'EXCEPTION','exception':str(e),'traceback':traceback.format_exc()})
save(D/'results.json',results)
if calc is not None:
    calc.get_groups_df().to_csv(D/'groups_after_defaults.csv')
    calc._DC.to_csv(D/'diet_after_defaults.csv')
print(json.dumps(audit,indent=2,default=serial));print([(x['TE_option'],x['status']) for x in results])
