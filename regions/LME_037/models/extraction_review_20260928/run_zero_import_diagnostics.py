"""Replay only the documented zero-import diagnostic staging; no source edits."""
from pathlib import Path
import json,sys,pickle
ROOT=Path(__file__).resolve().parents[4]
M=ROOT/'regions/LME_037/models/Bacalso2026_Visayan_Sea_1997_baseline'
D=M/'diagnostics/zero_import_default'
sys.path.insert(0,str(ROOT/'tools/scientific_code/PPREstimation'))
from ModelData import ModelData
from PPRCalculator import PPRCalculator
source=json.loads((M/'model.json').read_text(encoding='utf8'))
for g in source['group']:g['diet_imp']='0'
p=D/'37_3702026_Visayan_Sea_Bacalso_baseline_(1997).json'
p.write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding='utf8')
c=PPRCalculator.from_modeldata(ModelData(str(p)),zero_catch=True,zero_biomass_accum=True,default_gs=True,DC_tol=.0021,normalize_DC=False)
c.get_groups_df().to_csv(D/'groups_after_defaults.csv');c._DC.to_csv(D/'diet_after_defaults.csv')
results=[]
for method in ['GE','TE','With Egestion']:
    raw=c.diagnose_sppr(TE_option=method,short=False,flat=False);n=method.replace(' ','_')
    (D/f'{n}_raw.pkl').write_bytes(pickle.dumps(raw))
    (D/f'{n}_raw.json').write_text(json.dumps(raw,indent=2,default=str),encoding='utf8')
    results.append({'method':method,'returned':True,'result':raw})
    print(method,raw['status'])
(D/'results.json').write_text(json.dumps(results,indent=2,default=str),encoding='utf8')
