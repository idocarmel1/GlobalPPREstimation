from pathlib import Path
import json,re,sys
from decimal import Decimal
W=Path(r'C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/קוד/PPR_Ecopath_Atlas/archive/regions/LME_036/SCS-2007/extracted/work')
def grid(p): return json.loads((W/f'grid-{p}.json').read_text())
models={}; provenance=[]
for year,p,start in [('1970s',190,5),('2000s',191,2)]:
 groups=[]
 for row in grid(p)[start:start+38]:
  n=int(row[0]['text']); name=' '.join(c['text'] for c in row[1:] if c['x1']<340)
  name=re.sub(r'>\s*30', '> 30', name)
  if n in [21,24,29]: name=name.replace('<','≤')
  g={'n':n,'name':name}
  for c in row:
   if c['x1']<340 or c['text'] in ['.','-']: continue
   if not re.fullmatch(r'\(?\d+(?:\.\d+)?\)?',c['text']): raise ValueError(c)
   k=min(range(4),key=lambda k:abs(c['x1']-[365,410,456,501][k]))
   key=['biomass','pb','qb','ee'][k]
   assert key not in g
   g[key]=c['text'].strip('()')
   provenance.append({'period':year,'group':n,'field':key,'value':g[key],'printed':c['text'],'category':'model-estimated' if '(' in c['text'] else 'tabulated','pdf_page':p,'printed_page':p-15,'bbox':[c['x0'],c['y0'],c['x1'],c['y1']]})
  groups.append(g)
 assert [g['n'] for g in groups]==list(range(1,39))
 models[year]={'metadata':{'LME':'36 South China Sea','model_number':'SCS-2007','model_name':'Northern South China Sea','model_year':year},'groups':groups,'consumers':list(range(3,38)),'detritus_groups':['Detritus'],'detritus_fate':{},'diet_rows':38,'landings_rows':38,'discards_rows':38,'discards':{}}
assert [g['name'] for g in models['1970s']['groups']]==[g['name'] for g in models['2000s']['groups']], [(a['name'],b['name']) for a,b in zip(models['1970s']['groups'],models['2000s']['groups']) if a['name']!=b['name']]
def norm(s):
 s=s.lower().replace('≤','<').replace('threadfm','threadfin').replace('juv.','juvenile').replace('juv ','juvenile ').replace('ad.','adult').replace('dem.','demersal').replace('demesral','demersal').replace('inverts','invertebrates')
 s=re.sub(r'\((nemipterids|priacanthids|synodontids|trichiurids|stromateids)\)','',s)
 s=s.replace('phytoplanktons','phytoplankton').replace('zooplanktons','zooplankton').replace('benthic producers','benthic producer')
 return re.sub(r'\s+','',s)
lookup={norm(g['name']):g['n'] for g in models['1970s']['groups']}
# Each block: page, first/last body line (inclusive), named predator identities from header.
blocks=[(357,3,8,[3,4]),(357,13,23,[5,6,7,8,9]),(357,27,37,[10,11]),(358,2,19,[12]),(358,23,43,[13,14,15]),(359,3,26,[16,17,18]),(360,3,27,[19,20,21,22,23]),(361,3,29,[24,25,26,27]),(362,3,24,[28,29,30,31]),(363,4,46,[32,33,34,35,36,37])]
diet={str(n):{} for n in range(3,38)}; block_info=[]
for p,a,b,preds in blocks:
 rows=grid(p)[a:b+1]
 xs=sorted(c['x1'] for row in rows for c in row if re.fullmatch(r'\d+\.\d+',c['text']))
 clusters=[]
 for x in xs:
  if not clusters or x-clusters[-1][-1]>8: clusters.append([x])
  else: clusters[-1].append(x)
 anchors=[sum(c)/len(c) for c in clusters]
 assert len(anchors)==len(preds),(p,anchors,preds)
 pending=''
 for ri,row in enumerate(rows,a):
  nums=[c for c in row if re.fullmatch(r'\d+\.\d+',c['text'])]
  label=' '.join(c['text'] for c in row if c not in nums and c['text'] not in ['.','-'])
  label=(pending+' '+label).strip()
  if not nums and p==363 and ri in [14,17,20,29,31,36,39]:
   pending=label;continue
  if norm(label) not in lookup:
   assert not nums,(p,ri,label)
   pending=label;continue
  prey=lookup[norm(label)];pending=''
  for c in nums:
   col=min(range(len(anchors)),key=lambda j:abs(c['x1']-anchors[j]))
   assert abs(c['x1']-anchors[col])<8
   pred=preds[col]
   assert str(prey) not in diet[str(pred)]
   diet[str(pred)][str(prey)]=c['text']
   provenance.append({'period':'both','group':pred,'field':'diet','prey':prey,'source_label':label,'value':c['text'],'category':'tabulated','pdf_page':p,'printed_page':p-15,'bbox':[c['x0'],c['y0'],c['x1'],c['y1']]})
 assert not pending
 block_info.append({'pdf_page':p,'body_lines':[a,b],'predators':preds,'numeric_right_anchors':anchors})
for m in models.values(): m['diet']=diet
fleets=['Pair and stern trawl','Shrimp trawl','Purse seine','Hook and line','Gillnet','Other fishing gears']
models['1970s']['fleets']=['Total fishery'];models['2000s']['fleets']=fleets
for m in models.values(): m['landings']={}
catch_records=[]
for p,a,b in [(193,22,36),(194,5,27)]:
 for row in grid(p)[a:b+1]:
  label=' '.join(c['text'] for c in row if c['x0']<198)
  n=lookup[norm(label)]
  nums=sorted([c for c in row if c['x0']>=198 and re.fullmatch(r'\d+\.\d+',c['text'])],key=lambda c:c['x0'])
  assert len(nums)==8,(label,nums)
  vals=[c['text'] for c in nums]
  models['1970s']['landings'][str(n)]={'Total fishery':vals[0]}
  models['2000s']['landings'][str(n)]=dict(zip(fleets,vals[1:7]))
  catch_records.append({'group':n,'name':label,'1970s_total':vals[0],'2000s_fleets':dict(zip(fleets,vals[1:7])),'2000s_printed_total':vals[7],'2000s_fleet_sum':str(sum(Decimal(v) for v in vals[1:7])),'pdf_page':p})
  for k,c in enumerate(nums): provenance.append({'period':'1970s' if k==0 else '2000s','group':n,'field':'catch','fleet':'Total' if k in [0,7] else fleets[k-1],'value':c['text'],'category':'tabulated','pdf_page':p,'printed_page':p-15,'bbox':[c['x0'],c['y0'],c['x1'],c['y1']]})
# Table 6.5: M0 is a mortality RATE, retained exactly as published.
mortality=[]
for row in grid(205)[5:42]:
 nums=[c for c in row if re.fullmatch(r'\d+\.\d+',c['text'])]
 assert len(nums)==6
 label=' '.join(c['text'] for c in row if c not in nums)
 n=lookup[norm(label)]
 for year,offset in [('1970s',0),('2000s',3)]:
  c=nums[offset+2]
  models[year]['groups'][n-1]['other_mort']=c['text']
  mortality.append({'period':year,'group':n,'F':nums[offset]['text'],'M_as_labelled':nums[offset+1]['text'],'M0':c['text'],'pdf_page':205,'printed_page':190})
  provenance.append({'period':year,'group':n,'field':'other_mort','value':c['text'],'category':'tabulated model output mortality rate','pdf_page':205,'printed_page':190,'bbox':[c['x0'],c['y0'],c['x1'],c['y1']]})
(W/'mortality_source.json').write_text(json.dumps(mortality,indent=2),encoding='utf-8')
# Explicit prose P/Q assumptions; do not calculate these from rounded B/PB/QB.
for year,m in models.items():
 for n in [5,18,27,32,33]:
  val='0.3' if n==5 else '0.2'
  if year=='1970s' and n==5: continue # P/Q prose specifically scoped to 2000s.
  m['groups'][n-1]['pq']=val
  p={5:339,18:346,27:352,32:355,33:355}[n]
  provenance.append({'period':year,'group':n,'field':'pq','value':val,'category':'prose-stated assumption','pdf_page':p,'printed_page':p-15})
 # Table 6.1 lists final PB; only exact explicit same-period Z statements are copied separately below.
 for n in ([7,10,13,14,21,23,24,25,26,27,28,29] if year=='2000s' else [10,13,14,21,23,24,31,32,33]):
  # These are source-stated equivalences PB = total mortality, with the same numeric rate as final table.
  g=m['groups'][n-1]
  g['z']=g['pb']
 for n,g in enumerate(m['groups'],1):
  if g.get('z') is not None: provenance.append({'period':year,'group':n,'field':'z','value':g['z'],'category':'prose-stated PB=Z; matching final table','pdf_page':{7:339,10:341,13:342,14:342 if year=='2000s' else 343,21:348,23:349,24:350,25:351,26:351,27:352,28:347,29:353,31:354,32:355,33:355}[n]})
 (W/f'model-{year}.json').write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding='utf-8')
(W/'cell_provenance.json').write_text(json.dumps(provenance,indent=2,ensure_ascii=False),encoding='utf-8')
(W/'table_layouts.json').write_text(json.dumps(block_info,indent=2),encoding='utf-8')
(W/'catch_source_totals.json').write_text(json.dumps(catch_records,indent=2,ensure_ascii=False),encoding='utf-8')
print('Groups',len(models['1970s']['groups']),'Diet nonblank',sum(len(v) for v in diet.values()))
for k,v in diet.items():
 s=sum(Decimal(x) for x in v.values())
 print(k,models['1970s']['groups'][int(k)-1]['name'],s)
print('Catch totals:',{y:str(sum(Decimal(v) for row in m['landings'].values() for v in row.values())) for y,m in models.items()})




