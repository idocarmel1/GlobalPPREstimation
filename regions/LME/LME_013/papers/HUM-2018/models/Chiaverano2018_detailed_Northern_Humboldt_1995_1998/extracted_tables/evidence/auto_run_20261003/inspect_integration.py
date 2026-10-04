from pathlib import Path
import sys,json,csv
OUT=Path(__file__).resolve().parent; BASE=OUT.parent; ROOT=BASE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
b=read_book(ROOT/'regions/LME_013/LME_013.xlsx')
p=read_book(ROOT/'Project.xlsx')
m=json.loads((BASE/'mapping/mapping_review.json').read_text(encoding='utf-8'))
snapshot=json.loads((BASE/'mapping/regional_arithmetic_snapshot.json').read_text(encoding='utf-8'))
print('OVERVIEW',json.dumps(overview(b),ensure_ascii=False))
print('HEADERS',json.dumps({s:{t:[h,len(r)] for t,(h,r) in blocks.items()} for s,blocks in b.items()},ensure_ascii=False))
print('MAPPING',json.dumps(m['taxa'][:1],ensure_ascii=False))
print('SUMMARY',json.dumps(m['summary'],ensure_ascii=False))
print('SNAPSHOT KEYS',snapshot.keys())
print('SNAPSHOT CATCH',snapshot['catch'][0])
print('PROJECT MODELS HEADER',p['Models & coverage']['Models'][0] if 'Models' in p['Models & coverage'] else list(p['Models & coverage'].items())[0][0:1])
print('PROJECT LME ROWS',json.dumps({s:{t:[dict(zip(h,r)) for r in rr if 'LME_013' in r] for t,(h,rr) in blocks.items()} for s,blocks in p.items() if s in ['Models & coverage','Papers','Regions & status']},ensure_ascii=False))
print('HEALTH SAMPLE',records(b,'Diagnostics','model_health')[:1])
