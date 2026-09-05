import pathlib,json,sys,re,html,decimal,copy,zipfile,hashlib
D=decimal.Decimal;p=pathlib.Path(sys.argv[1]);w=p/'extracted/work';s=json.loads((w/'Table_1-f0424c0e_cells.json').read_text(encoding='utf-8'))[0];tables=json.loads((w/'docx_tables.json').read_text(encoding='utf-8'))
def clean(v):return None if v is None else html.unescape(re.sub('<[^>]*>','',str(v))).strip()
fields={'C':'tl','D':'biomass','E':'z','F':'pb','G':'qb','H':'ee','I':'pq','J':'ba_rate'}
groups=[];land={};prov=[];rowmap={};original={}
for row in s['rows']:
 c={re.sub('[0-9]','',x['cell']):x for x in row};a=clean(c.get('A',{}).get('value'))
 if not a or not a.isdigit():continue
 n=int(a); rownum=int(re.sub('[A-Z]','',c['A']['cell']));rowmap[n]=rownum
 g={'n':n,'name':clean(c['B']['value'])};original[n]={k:clean(v['value']) for k,v in c.items()}
 for col,field in fields.items():
  val=clean(c.get(col,{}).get('value'));g[field]=val
  if val is not None:prov.append({'model':'Base','group':n,'field':field,'value':val,'file':'Table_1-f0424c0e.xls','sheet':'Table_1','cell':f'{col}{rownum}','pdf_page':4 if n<37 else 5,'category':'model-estimated' if '<b>' in str(c[col]['value']) else 'tabulated','raw':c[col]['value']})
 land[str(n)]={fleet:clean(c[col]['value']) for col,fleet in [('K','Artisanal'),('L','Industrial demersal'),('M','Industrial pelagic')]}
 groups.append(g)
assert len(groups)==51 and [g['n'] for g in groups]==list(range(1,52))
diet={str(n):{} for n in range(1,48)}
for ix in [1,2,3]:
 t=tables[ix];offset=2 if ix==1 else 1;heads=t[0][offset:]
 for ri,row in enumerate(t[1:],1):
  prey=int(row[0]);key='import' if prey==52 else str(prey)
  assert len(row)==len(t[0]),(ix,ri,row)
  for pred,v in zip(heads,row[offset:]):
   value=format(D(v)/D(100),'f') if v.strip() else None;diet[pred][key]=value
   prov.append({'model':'Base','group':int(pred),'field':'diet','prey':key,'value':value,'file':'pone.0094742.s001-eb18ca66.docx','table':'S2','block':ix,'physical_table':ix+1,'row':ri+1,'column':heads.index(pred)+offset+1,'rendered_page':ix+7,'raw_percent':v,'category':'unit-converted','arithmetic':f'{v}/100'})
for pred,d in diet.items():print('Diet',pred,sum(D(v) for v in d.values() if v is not None))
# Compare on group identity, not table position. Names are source aliases, retained for audit.
s8={int(r[0]):r for r in tables[9][3:] if r[0].strip().isdigit()};assert sorted(s8)==list(range(1,52))
conflicts=[]
for g in groups:
 n=g['n'];r=s8[n]
 for field,index in [('biomass',7),('ee',8)]:
  if g.get(field) is not None and D(g[field])!=D(r[index]):conflicts.append({'group':n,'name':g['name'],'field':field,'Table_1':g[field],'S8_base':r[index]})
base={'metadata':{'LME':'27 Canary Current','model_number':'27_1','model_name':'Banc d Arguin and Mauritanian Shelf','model_year':1991,'variant':'Base','model_area_km2':'33224','source_doi':'10.1371/journal.pone.0094742'},'groups':groups,'consumers':list(range(1,48)),'fleets':['Artisanal','Industrial demersal','Industrial pelagic'],'landings':land,'discards':{},'detritus_groups':['Detritus'],'detritus_fate':{},'diet':diet,'diet_rows':51,'landings_rows':51,'discards_rows':51}
(w/'base_input.json').write_text(json.dumps(base,ensure_ascii=False,indent=2),encoding='utf-8')
for variant,number,bi,ei,pi in [('M30','27_2',5,6,2),('P30','27_3',9,10,4)]:
 m=copy.deepcopy(base);m['metadata'].update(model_number=number,variant=variant)
 constraints=[];uncertain=[]
 for g in m['groups']:
  n=g['n'];r=s8[n];g['biomass']=r[bi].strip();g['ee']=r[ei].strip();g['tl']=None
  for field,index in [('biomass',bi),('ee',ei)]:prov.append({'model':variant,'group':n,'field':field,'value':g[field],'file':'pone.0094742.s001-eb18ca66.docx','table':'S8','physical_table':10,'column':index+1,'rendered_page':15 if n<=39 else 16,'category':'tabulated; bold provenance recorded separately','source_group_name':r[1]})
  if n<=47:
   constraints.append({'group':n,'name':g['name'],'base_pBA':r[3].strip(),'variant_pBA':r[pi].strip()})
   if r[pi].strip() and D(r[pi])!=D(r[3]):
    uncertain.append(n)
    # Aggregate Banc share does not specify the individual prey split. Preserve all other base components;
    # retain stated zero-zero pairs, leave potentially changing invertebrate components unknown.
    for ba,sh in [(32,38),(33,39),(34,40),(35,41),(36,42),(37,43),(46,44),(47,45)]:
     if D(diet[str(n)][str(ba)] or '0')!=0 or D(diet[str(n)][str(sh)] or '0')!=0:
      m['diet'][str(n)][str(ba)]=None;m['diet'][str(n)][str(sh)]=None
 m['extraction_notes']={'shared_parameters':'Base Table 1 parameters other than B, EE, TL retained as common model inputs; Table S8 defines differences. No numerical variant diet redistribution invented.','incomplete_diet_consumers':uncertain,'pBA_constraints':constraints}
 (w/(variant.lower()+'_input.json')).write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
(w/'cell_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2),encoding='utf-8');(w/'source_conflicts.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2),encoding='utf-8');(w/'group_row_map.json').write_text(json.dumps(rowmap,indent=2),encoding='utf-8')
print('CONFLICTS',conflicts)

