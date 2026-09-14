from pathlib import Path
import json,re,sys,subprocess
sys.path.insert(0,r'C:\Users\idoca\.agents\skills\ecopath-extraction\scripts')
from pdfgrid import get_words,build_grid
from decimal import Decimal
folder=Path(__file__).parents[2];work=folder/'extracted'/'work';pdf=next(folder.glob('*.pdf'))
groups=[];landings={}; names={}
for line in get_words(str(pdf),6,merge_gap=2):
 if not 600<line.y<734: continue
 cells=line.cells
 m=re.match(r'^(\d+)\. (.*)$',cells[0].text)
 if not m: continue
 assert len(cells)==8,[(c.text,c.x0) for c in cells]
 n=int(m[1]); name=m[2];names[n]=name
 row={'n':n,'name':name}
 for field,cell in zip(['tl','biomass','pb','qb','ee','pq','catch'],cells[1:]):
  txt=cell.text.replace('\u200b','').strip()
  if txt:
   Decimal(txt)
   if field=='catch': landings[str(n)]={'Landings (all fleets)':txt}
   else: row[field]=txt
 groups.append(row)
assert len(groups)==15
lines=get_words(str(pdf),7,merge_gap=0.4)
grid=build_grid(lines,anchor_line=4);diet={str(i):{} for i in range(2,15)}
for row in grid[5:21]:
 label=row[0]
 if label=='Import':prey='import'
 else:
  m=re.match(r'^(\d+)\. (.*)$',label); assert m
  prey=m[1];assert names[int(prey)]==m[2]
 for pred,val in zip(range(2,15),row[1:]):
  txt=val.replace('\u200b','').strip()
  if txt:Decimal(txt);diet[str(pred)][prey]=txt
data={'metadata':{'LME':'13 Humboldt Current','model_number':'13_1','model_name':'Chilean Patagonia','model_year':1980},
 'groups':groups,'consumers':list(range(2,15)),'fleets':['Landings (all fleets)'],'landings':landings,'discards':{},
 'detritus_groups':['Detritus'],'detritus_fate':{},'diet':diet,'diet_rows':15}
(work/'model-input.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
for pred,vals in diet.items():print(pred,'sum',sum(Decimal(v) for v in vals.values()))
r=subprocess.run([sys.executable,'-X','utf8',r'C:\Users\idoca\.agents\skills\ecopath-extraction\scripts\write_outputs.py',str(work/'model-input.json'),'--outdir',str(folder/'extracted')],capture_output=True,text=True,encoding='utf-8')
print(r.stdout);print(r.stderr);r.check_returncode()

