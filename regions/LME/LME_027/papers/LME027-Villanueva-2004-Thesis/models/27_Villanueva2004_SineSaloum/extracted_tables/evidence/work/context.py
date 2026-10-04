from pathlib import Path
import sys,json,hashlib,os
ROOT=Path(__file__).resolve().parents[5]
C=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book, records,overview
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
targets=[ROOT/'Project.xlsx',*list((ROOT/'regions/LME_027').glob('*.*')),*list((ROOT/'interactive_map').glob('*.*')),ROOT/'tools/templates/Model_validation_template.docx']
for folder in [ROOT/'regions/LME_027/models/27_118_Northwest_Africa_(1987)',ROOT/'regions/LME_027/models/27_Morissette2009_Northwest_Africa_Table17',ROOT/'regions/LME_027/validation_reports/27_118_Northwest_Africa_(1987)',ROOT/'regions/LME_027/papers/LME027-Villanueva-2004']:
 for current,dirs,files in os.walk(folder,followlinks=False):
  dirs[:]=[d for d in dirs if d not in ['_deps','node_modules','__pycache__'] and Path(current)/d!=C]
  targets.extend(Path(current)/f for f in files)
baseline={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in set(targets)}
dump(C/'qa/protected_baseline.json',baseline)
b=read_book(ROOT/'regions/LME_027/LME_027.xlsx')
o=overview(b)
ctx={'overview':o,'catch':records(b,'Catch','Catch'),'classic':records(b,'Classic PPR','Taxa'),'classic_annual':records(b,'Classic PPR','Annual'),'npp':records(b,'NPP','NPP')}
dump(C/'work/regional_context.json',ctx)
print(json.dumps({'overview':o,'blocks':{s:{t:len(v[1]) for t,v in tables.items()} for s,tables in b.items()}},ensure_ascii=False,indent=2))
p=read_book(ROOT/'Project.xlsx')
relevant={s:{t:[dict(zip(h,r)) for r in rows if 'LME_027' in r] for t,(h,rows) in ts.items()} for s,ts in p.items() if s in ['Papers','Models & coverage']}
dump(C/'work/project_context.json',relevant)
print('Protected files:',len(baseline))
