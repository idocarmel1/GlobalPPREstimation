from pathlib import Path
import pdfplumber,csv,json,re,hashlib
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'evidence/identity/Villanueva2004_thesis_29305.pdf'
OUT=ROOT/'extracted_tables/thesis'
OUT.mkdir(parents=True,exist_ok=True)
pdf=pdfplumber.open(SRC)
def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def csvwrite(name,rows):
 with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def chars_text(page,xl,xr,cy,tol=4):
 cs=sorted([c for c in page.chars if xl<=(c['x0']+c['x1'])/2<xr and abs((c['top']+c['bottom'])/2-cy)<tol],key=lambda c:c['x0'])
 return ''.join(c['text'] for c in cs).strip(),cs
page=pdf.pages[137]; words=page.extract_words()
ids=sorted([w for w in words if 79<w['x0']<90 and 188<w['top']<600 and w['text'].isdigit()],key=lambda w:w['top'])
assert len(ids)==37
fields=['TL','B','PB','QB','EE','PQ','Y']
xregs=[(230,261),(268,307),(318,359),(370,406),(413,455),(459,503),(511,554)]
groups=[];cells=[]
for idx,idword in enumerate(ids,1):
 assert int(idword['text'])==idx
 cy=(idword['top']+idword['bottom'])/2
 ns=sorted([w for w in words if 103<=w['x0']<228 and abs((w['top']+w['bottom'])/2-cy)<4],key=lambda w:w['x0'])
 name=' '.join(w['text'] for w in ns)
 g={'group_id':idx,'group_name_source':name,'group_name':name.rstrip('*').strip(),'pooled_asterisk':name.endswith('*'),'type':'detritus' if idx==37 else 'producer' if idx>=35 else 'consumer'}
 for field,(xl,xr) in zip(fields,xregs):
  literal,chars=chars_text(page,xl,xr,cy)
  # Retain complete source cell incl. comma decimals, parentheses and source letters.
  m=re.search(r'[-+]?[0-9]+(?:,[0-9]+)?',literal)
  value=m.group(0).replace(',','.') if m else None
  estimated='(' in literal
  c={'group_id':idx,'group_name_source':name,'field':field,'literal':literal,'value':value,'estimated_parentheses':estimated,'source_footnote':literal[-1] if literal and literal[-1] in 'abcdefghijklmnop' else None,'missingness':'printed_dash' if literal=='-' else 'printed_number' if value is not None else 'blank','pdf_page':138,'printed_page':114,'table':'6.5','cell_id':f'6.5/r{idx}/{field}','bbox_pt':[xl,round(cy-4,3),xr,round(cy+4,3)]}
  cells.append(c);g[field]=value;g[field+'_literal']=literal;g[field+'_estimated']=estimated
 groups.append(g)
csvwrite('table_6_5_literal.csv',groups);save('table_6_5_cells.json',cells)
diet_cells=[];rows=[];crosswalk=[]
for pnum,start,end in [(235,1,17),(236,18,34)]:
 p=pdf.pages[pnum-1];ws=p.extract_words()
 header_top=138.57 if pnum==235 else 128.97
 headers=sorted([w for w in ws if w['text'].isdigit() and w['x0']>190 and abs(w['top']-header_top)<1],key=lambda w:w['x0'])
 assert [int(w['text']) for w in headers]==list(range(start,end+1)),headers
 anchors=[(w['x0']+w['x1'])/2 for w in headers]
 rowids=sorted([w for w in ws if 65<w['x0']<78 and header_top+5<w['top']<500 and w['text'].isdigit()],key=lambda w:w['top'])
 assert len(rowids)==37,(pnum,len(rowids))
 for idx,w in enumerate(rowids,1):
  assert int(w['text'])==idx
  cy=(w['top']+w['bottom'])/2
  ns=sorted([v for v in ws if 80<v['x0']<190 and abs((v['top']+v['bottom'])/2-cy)<3],key=lambda v:v['x0'])
  name=' '.join(v['text'] for v in ns)
  if pnum==235:crosswalk.append({'group_id':idx,'basic_name':groups[idx-1]['group_name_source'],'annex_name':name,'name_agreement':'same_literal' if name==groups[idx-1]['group_name'] else 'source_spelling_or_identity_conflict','pdf_page_basic':138,'pdf_page_diet':235})
  for col,ax in zip(range(start,end+1),anchors):
   literal,chars=chars_text(p,ax-12.5,ax+12.5,cy,tol=3)
   assert not literal or re.fullmatch(r'[0-9]+,[0-9]+',literal),(pnum,idx,col,literal)
   diet_cells.append({'prey_id':idx,'prey_name_source':name,'consumer_id_source_number':col,'consumer_name_Table6_5':groups[col-1]['group_name_source'],'literal':literal,'value':literal.replace(',','.') if literal else None,'missingness':'source_blank_structural_diet_cell' if not literal else 'printed_number','pdf_page':pnum,'printed_page':pnum-24,'table':'Annex II.A','cell_id':f'II.A/prey{idx}/consumer{col}','bbox_pt':[round(ax-12.5,3),round(cy-3,3),round(ax+12.5,3),round(cy+3,3)],'orientation':'prey rows, numbered consumer columns, caption Proie/Predateur'})
save('diet_cells.json',diet_cells);csvwrite('diet_identity_crosswalk.csv',crosswalk)
for g in groups:
 row={'prey_id':g['group_id'],'Table6_5_name':g['group_name_source'],'annex_name':crosswalk[g['group_id']-1]['annex_name']}
 for cid in range(1,35):row['consumer_'+str(cid)]=next(c['value'] or '' for c in diet_cells if c['prey_id']==g['group_id'] and c['consumer_id_source_number']==cid)
 rows.append(row)
csvwrite('diet_literal_prey_by_consumer.csv',rows)
sums=[]
for cid in range(1,35):
 cs=[c for c in diet_cells if c['consumer_id_source_number']==cid]
 total=sum(Decimal(c['value']) for c in cs if c['value'] is not None)
 sums.append({'consumer_id':cid,'source_Table6_5_name':groups[cid-1]['group_name_source'],'sum_source_literals':str(total),'deviation_from_one':str(total-1),'nonblank_cells':sum(c['value'] is not None for c in cs),'runtime_normalized':False,'header_units':'caption says percent, numeric cells sum to approx1; retain literal fractions pending audit'})
csvwrite('diet_column_sums.csv',sums)
save('literal_source_extraction.json',{'schema':'thesis_literal_source_v1','source_pdf':'evidence/identity/Villanueva2004_thesis_29305.pdf','path_basis':'candidate_directory','sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'model_name':'Sine-Saloum','period':'1991-1992','groups':groups,'diet_cells':diet_cells,'diet_column_sums':sums,'identity_crosswalk':crosswalk,'unassimilated_fraction':None,'BA':None,'detritus_routing':None,'migration':None,'discards':None,'group_20_identity_conflict':'Table6.5 Epinephelus aeneus* versus AnnexIIA Hemichromis fasciatus','group_27_identity_conflict':'Table6.5 Liza grandisquamis* versus AnnexIIA Liza falcipinnis','admission':'pending source identity and runtime audit, no implicit repair'})
imports={'metadata':{'LME':'27 Canary Current','model_number':'Villanueva2004Thesis','model_name':'Sine Saloum','model_year':'1991-1992','biomass_basis':'whole_model_area','source_admission':'BLOCKED','model_identifier_scope':'local candidate identity, not verified native accession','source':'../../../../papers/LME027-Villanueva-2004-Thesis/Villanueva2004_thesis_29305.pdf','source_locator':'Table6.5 printed114/PDF138 and AnnexIIA printed211-212/PDF235-236','export_basis':'reported_landings','export_scope':'Published Y catch only; discards not separated; total removals unknown'},'groups':[],'consumers':list(range(1,35)),'fleets':['Reported total catch'],'landings':{},'discards':{},'detritus_groups':['Détritus'],'detritus_fate':{},'diet':{},'diet_rows':37,'landings_rows':37,'discards_rows':37,'source_admission':'BLOCKED: unresolved group20 identity; missingGS/BA/routing/discards. Eight files are partial evidentiary schemas, not admitted calculator input.'}
lossmask=[]
for g in groups:
 role={dest:('model_estimated' if g[src+'_estimated'] else 'source_input') for src,dest in {'B':'biomass','PB':'pb','QB':'qb','EE':'ee','PQ':'pq','TL':'tl'}.items()}
 imports['groups'].append({'n':g['group_id'],'name':g['group_name'],'biomass':g['B'],'pb':g['PB'],'qb':g['QB'],'ee':g['EE'],'pq':g['PQ'],'tl':g['TL'],'hab_area':None,'z':None,'unassim':None,'ba':None,'ba_rate':None,'other_mort':None,'detritus_import':None,'parameter_roles':role,'source_name':g['group_name_source'],'source_group_pooled':g['pooled_asterisk']})
 imports['landings'][str(g['group_id'])]={'Reported total catch':g['Y']}
for cid in range(1,35):
 col={'import':None}
 for c in [c for c in diet_cells if c['consumer_id_source_number']==cid]:
  pid=c['prey_id']
  if cid==20 or pid==20:
   col[str(pid)]=None
   lossmask.append({'prey_id':pid,'consumer_id':cid,'source_literal':c['literal'],'source_value':c['value'],'canonical_value':None,'reason':'Annex group20 Hemichromis fasciatus incompatible with Table6.5 Epinephelus aeneus; identity unresolved','cell_id':c['cell_id']})
  elif c['value'] is not None:col[str(pid)]=c['value']
 imports['diet'][str(cid)]=col
imports['companions']={'Literal_source_parameters.csv':{'description':'All exact Table6.5 cells including source footnotes and parentheses','rows':[list(cells[0])]+[[json.dumps(c[k],ensure_ascii=False) if isinstance(c[k],list) else c[k] for k in cells[0]] for c in cells]},'Literal_source_diet.csv':{'description':'Complete numbered AnnexIIA cells before any identity mapping; blank masks preserved','rows':[list(diet_cells[0])]+[[json.dumps(c[k],ensure_ascii=False) if isinstance(c[k],list) else c[k] for k in diet_cells[0]] for c in diet_cells]},'Unresolved_diet_cells.csv':{'description':'Cells withheld from canonical identity matrix, with source originals retained','rows':[list(lossmask[0])]+[[c[k] for k in lossmask[0]] for c in lossmask]},'Identity_crosswalk.csv':{'description':'Source names retained; source-group20 conflict remains unresolved','rows':[list(crosswalk[0])]+[[c[k] for k in crosswalk[0]] for c in crosswalk]}}
save('partial_import_source.json',imports);save('canonical_diet_missingness.json',lossmask)
print('Thesis37groups '+str(len(diet_cells))+' dietcells; sums '+','.join(s['sum_source_literals'] for s in sums))
