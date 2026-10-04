from pathlib import Path
import json, csv, math, sys
import fitz
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
R=Path(__file__).resolve().parent.parent
pdf=next((ROOT/'regions/LME_032/papers/ARAB-2005').glob('*.pdf'))
d=fitz.open(pdf)
def words(n,rot=0):
 p=d[n-1];p.set_rotation(rot)
 return [(fitz.Rect(w[:4])*p.rotation_matrix,w[4]) for w in p.get_text('words')]
def number(s):
 try:return float(s)
 except ValueError:return None
def write_csv(name,head,rows):
 with (R/'source'/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(head);w.writerows(rows)
model=json.loads((R/'source/baseline_model.json').read_text(encoding='utf-8'))
by={int(g['group_seq']):g for g in model['group']}
w=words(31);basic=[];diff=[]
fields=[('tl',241),('habitat_area',284),('biomass',331),('pb',383),('qb',430),('ee',480),('pq',527)]
ids=[(int(t),rect.y0) for rect,t in w if rect.x0<80 and rect.y0>440 and t.isdigit() and 1<=int(t)<=24]
for seq,y in ids:
 row=[seq,by[seq]['group_name']]
 for key,x in fields:
  cells=[(rect,t) for rect,t in w if abs(rect.y0-y)<2 and abs((rect.x0+rect.x1)/2-x)<17 and number(t) is not None]
  val=number(cells[0][1]) if cells else None;row.append(val)
  if key in ['biomass','pb','qb','ee'] and val is not None:
   stored=float(by[seq][key]);diff.append({'table':'balanced basic','group_id':seq,'field':key,'source':val,'canonical':stored,'equal':abs(val-stored)<1e-9})
 basic.append(row)
assert len(basic)==24
write_csv('published_balanced_basic.csv',['group_id','name']+[x[0] for x in fields],basic)
w=words(23);ys={int(t):rect.y0 for rect,t in w if rect.x0<80 and 155<rect.y0<445 and t.isdigit() and 1<=int(t)<=24}
catch=[]
for seq,y in sorted(ys.items()):
 vals=[]
 for x in [225,273,323,377,432,480,527]:
  cells=[t for rect,t in w if abs(rect.y0-y)<2 and abs((rect.x0+rect.x1)/2-x)<17 and number(t) is not None]
  assert len(cells)==1,(seq,x,cells)
  vals.append(float(cells[0]))
 catch.append([seq,by[seq]['group_name'],*vals])
 stored=float(by[seq]['export']);diff.append({'table':'landings 1999-2001','group_id':seq,'field':'catch','source':vals[-1],'canonical':stored,'equal':abs(stored-vals[-1])<1e-9})
assert len(catch)==24
write_csv('published_landings.csv',['group_id','name','MDF','SDF','PS','GN','H&L','AS','TOTAL'],catch)
w=words(63,90)
xs={int(t):(rect.x0+rect.x1)/2 for rect,t in w if abs(rect.y0-132.73)<2 and t.isdigit() and 1<=int(t)<=22}
ys={int(t):rect.y0 for rect,t in w if rect.x0<95 and 145<rect.y0<470 and t.isdigit() and 1<=int(t)<=24}
assert len(xs)==22 and len(ys)==24,(xs,ys)
diet={seq:[0.]*24 for seq in xs}; nonzero=0
for rect,t in w:
 val=number(t)
 if val is None or (rect.x0+rect.x1)/2<180 or not 145<rect.y0<460:continue
 prey=min(ys,key=lambda k:abs(ys[k]-rect.y0)); pred=min(xs,key=lambda k:abs(xs[k]-(rect.x0+rect.x1)/2))
 if abs(ys[prey]-rect.y0)>3:continue
 assert diet[pred][prey-1]==0,(pred,prey,t)
 diet[pred][prey-1]=val;nonzero+=val>0
diet_rows=[];sums={}
for pred,vals in sorted(diet.items()):
 total=math.fsum(vals);sums[pred]=total
 canonical=[0.]*24
 for cell in by[pred]['diet_descr']['diet']:canonical[int(cell['prey_seq'])-1]=float(cell['proportion'])
 for prey,v in enumerate(vals,1):
  cv=canonical[prey-1]; normalized=v/total if total else v
  diet_rows.append([prey,by[prey]['group_name'],pred,by[pred]['group_name'],v,total,normalized,cv,cv-normalized])
  diff.append({'table':'modified balanced diet','group_id':pred,'prey_id':prey,'source':v,'canonical':cv,'source_sum':total,'normalized_source':normalized,'equal':abs(cv-normalized)<1e-9})
write_csv('published_modified_diet_cells.csv',['prey_id','prey_name','predator_id','predator_name','printed_value','printed_column_sum','normalized_source','canonical','difference'],diet_rows)
report={'basic_cells':len([x for x in diff if x['table']=='balanced basic']),'catch_cells':24,'diet_cells':528,'diet_nonzero':nonzero,'printed_diet_sums':sums,'differences':[x for x in diff if not x['equal']], 'locator':{'basic':'printed p.21/PDF31','landings':'printed p.13/PDF23','diet':'printed p.53/PDF63'},'zero_BA':'All group biomass accumulation assumed zero: printed p.21/PDF31. Canonical -9999 is missing, not zero.','diet_policy':'Blank published diet cells are structural zero; normalize each printed predator column by its actual sum. Compare normalized source with canonical.'}
(R/'source/source_table_reconciliation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
