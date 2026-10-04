from pathlib import Path
import sys,json
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).parent;REG=OUT.parents[2]
for p in (REG/'models/regional_ge_integration_20260928').glob('direct_new_*.json'):
    d=json.loads(p.read_text(encoding='utf-8'));print(p.name,type(d),list(d) if isinstance(d,dict) else len(d))
    if isinstance(d,dict):
        for i,v in enumerate(d.get('values',[])):
            print(i,str(v)[:2000])
for name in ['matrix_inspection.json','residual_fish_method_exposure.json','invertebrate_reporting_scope_retention.json']:
    p=OUT.parent/name
    d=json.loads(p.read_text(encoding='utf-8'));print(name,str(d)[:1600])
