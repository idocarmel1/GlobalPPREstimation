"""Extract published cells by PDF coordinates and DOCX XML table coordinates."""
from pathlib import Path
import json,re,sys,csv,hashlib,subprocess,shutil
from decimal import Decimal
import pymupdf as fitz
import openpyxl
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
REG=ROOT/'regions/LME_050'; SRC=REG/'papers/SOJ-2023'; REVIEW=Path(__file__).parent
SKILL=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf8')
def clean(s):return ' '.join(s.split())
def spans(p):return [s for b in p.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
pdf=fitz.open(next(SRC.glob('*.pdf')))
tables=json.loads((SRC/'evidence/supplement_tables.json').read_text(encoding='utf8'))
groups={1985:[],2013:[]}; cells={1985:[],2013:[]}
for pi in [4,5]:
 ss=spans(pdf[pi]); anchors=[s for s in ss if s['bbox'][0]<60 and s['text'].isdigit() and 85<s['bbox'][1]<(720 if pi==4 else 490)]
 for k,a in enumerate(anchors):
  n=int(a['text']); year=1985 if pi==4 and k<40 else 2013;y=a['bbox'][1]
  row=[s for s in ss if abs(s['bbox'][1]-y)<1]
  name=' '.join(s['text'] for s in row if 100<s['bbox'][0]<190)
  g={'n':n,'name':name}
  for field,x in [('tl',209),('biomass',280),('pb',338),('qb',400),('pq',467),('ee',525)]:
   vals=[s for s in row if abs(s['bbox'][0]-x)<20]
   assert len(vals)<=1,(year,n,field,vals)
   val=vals[0]['text'].strip() if vals else None
   if val is not None:Decimal(val)
   g[field]=val
   cells[year].append({'seq':n,'group_name':name,'field':field,'source_text':val,'pdf_page':pi+1,'printed_page':pi+573,'table':'1','bbox':vals[0]['bbox'] if vals else None,'source_status':('author_input' if 'Bold' in vals[0]['font'] else 'Ecopath_estimated') if vals else 'not_tabulated'})
  groups[year].append(g)
for year in groups:assert [g['n'] for g in groups[year]]==list(range(1,41)),(year,groups[year])
assert [g['name'] for g in groups[1985]]==[g['name'] for g in groups[2013]]
# Recover individual whitespace-delimited tokens from raw characters: normal word
# extraction fuses adjacent narrow columns. Coordinates map LEFT edges to headers.
def tokens(page):
 out=[]
 for b in page.get_text('rawdict')['blocks']:
  for line in b.get('lines',[]):
   for span in line['spans']:
    buf=[]
    for c in span['chars']+[{'c':' '}]:
     if c['c'].isspace():
      if buf:
       rect=fitz.Rect(buf[0]['bbox'])
       for z in buf[1:]:rect|=fitz.Rect(z['bbox'])
       rect=rect*page.rotation_matrix
       out.append([*rect,''.join(z['c'] for z in buf)])
       buf=[]
     else:buf.append(c)
 return out
diet={str(c):{} for c in range(1,39)};dcells=[]
for pi in [6,7]:
 pg=pdf[pi];pg.set_rotation(90);tt=tokens(pg)
 headers={int(t[4]):t[0] for t in tt if 64<t[1]<68 and t[4].isdigit()}
 assert list(sorted(headers))==list(range(1,39)),headers
 anchors={int(t[4]):t[1] for t in tt if 73<t[0]<80 and t[4].isdigit() and 90<t[1]<545}
 if pi==7:
  anchors.update({t[4]:t[1] for t in tt if 86<t[0]<90 and t[4] in ['Import','Sum']})
 for prey,y in anchors.items():
  for t in tt:
   if t[0]<119 or t[0]>730 or abs(t[1]-y)>1:continue
   pred=min(headers,key=lambda c:abs(headers[c]-t[0]))
   assert abs(headers[pred]-t[0])<.3,(pi,prey,pred,t)
   Decimal(t[4])
   dcells.append({'prey_seq':prey,'predator_seq':pred,'source_text':t[4],'pdf_page':pi+1,'printed_page':pi+573,'table':'2','rotated_bbox':t[:4]})
   if prey!='Sum':diet[str(pred)][str(prey).lower()]=t[4]
dump(SRC/'evidence/table2_cells.json',dcells)
dump(SRC/'evidence/table2_diet.json',diet)
print('diet sums',[(k,str(sum(Decimal(v) for v in d.values()))) for k,d in diet.items()])
taxonomy={}
for rowi,r in enumerate(tables[2],1):
 if r[0].strip().isdigit():
  source_n=int(r[0]); n={29:30,30:29}.get(source_n,source_n)
  expected={6:'Amberjack',30:'Sole'}.get(n,groups[1985][n-1]['name'])
  assert clean(r[1]).lower()==expected.lower(),(n,r)
  tx=clean(r[2]) or 'not documented: Table S3 representative-taxa cell is blank'
  if n==8:tx+='; conflict: main article p.585 identifies Thunnus orientalis, whereas S3 gives Thunnus thynnus; unresolved source identity'
  taxonomy[n]={'text':tx,'source_seq':source_n,'source_group_name':clean(r[1]),'table':'S3','docx_table':3,'docx_row':rowi,'scope':'Representative taxa; not an exhaustive membership list.'}
assert len(taxonomy)==40
for year in [1985,2013]:
 mid=f'50_50{year}_Coastal_Kyoto_Inoue_({year})';dest=REG/'models'/mid;et=dest/'extracted_tables';et.mkdir(parents=True,exist_ok=True)
 table=tables[3 if year==1985 else 4]; header=table[1 if year==1985 else 0]; fleets=header[2:-1]
 catches={}; ccells=[];totals={}
 for rowi,row in enumerate(table,1):
  if not row[0].strip().isdigit():continue
  n=int(row[0]);assert clean(row[1]).lower()==groups[year][n-1]['name'].lower(),(year,n,row[1])
  catches[str(n)]={f:clean(v) for f,v in zip(fleets,row[2:-1]) if clean(v)}
  totals[str(n)]=clean(row[-1])
  for coli,v in enumerate(row[2:],3):ccells.append({'seq':n,'field':header[coli-1],'source_text':v,'docx_table':4 if year==1985 else 5,'docx_row':rowi,'docx_column':coli,'units':'t/km2/year'})
 model={'metadata':{'LME':'50 Sea of Japan','model_number':int('50'+str(year)),'model_name':'Coastal Kyoto Inoue','model_year':year},'groups':groups[year],'consumers':list(range(1,39)),'fleets':fleets,'landings':catches,'discards':{},'detritus_groups':['Detritus'],'detritus_fate':{},'diet':diet,'diet_rows':40,'landings_rows':40,'discards_rows':40}
 dump(et/'model.json',model);dump(et/'source_cells.json',cells[year]);dump(et/'catch_source_cells.json',ccells);dump(et/'source_reported_catch_totals.json',totals);dump(et/'diet_source_cells.json',dcells);dump(et/'taxonomy_evidence.json',taxonomy)
 subprocess.run([sys.executable,'-X','utf8',str(SKILL/'write_outputs.py'),str(et/'model.json'),'--outdir',str(dest),'--dir-name','extracted_tables'],check=True)
 wb=openpyxl.Workbook();ws=wb.active;ws.title='Taxonomy';ws.append(['seq','group_name','taxon_descr'])
 for g in groups[year]:ws.append([g['n'],g['name'],taxonomy[g['n']]['text']+'; representative taxa (not exhaustive), Supplement Table S3; source spelling preserved.'])
 wb.save(et/'Taxonomy.xlsx')
 with (et/'taxonomy.csv').open('w',newline='',encoding='utf8') as f:
  writer=csv.writer(f);writer.writerows(ws.values)
 (et/'REPORT.md').write_text(f'# Coastal Kyoto {year}\n\nSource-faithful tabulated reconstruction, exact original model diet version unresolved. See ../REPORT.md.\n',encoding='utf8')
 for script,args in [('validate.py',[str(et)]),('massbalance_check.py',[str(et)]),('database_json.py',['-d',str(et),'--update-report'])]:
  proc=subprocess.run([sys.executable,'-X','utf8',str(SKILL/script),*args],capture_output=True,text=True,encoding='utf8');(et/(script.replace('.py','')+'.log')).write_text(proc.stdout+'\n'+proc.stderr,encoding='utf8')
  print(year,script,proc.returncode)
 # Converter supplies defaults and normalizes. Keep its output, then rebuild the
 # canonical source fields from the retained import tables without either action.
 generated=next(et.glob('50_*.json')); obj=json.loads(generated.read_text(encoding='utf8'));changes=[]
 for g,source in zip(obj['group'],groups[year]):
  n=g['group_seq']; before=json.loads(json.dumps(g));g['biomass']=source['biomass'];g['biomass_habitat_area']=source['biomass'];g['habitat_area']='-9999'
  for key in ['pb','qb','ee']:g[key]=source.get(key) or '-9999'
  g['ge']=source.get('pq') or '-9999';g['ge_input']='true' if next(c for c in cells[year] if c['seq']==int(n) and c['field']=='pq')['source_status']=='author_input' else 'false'
  g['tl']=source['tl']
  for key in ['vbk','shadow_price','detritus_import','respiration','immigration','emigration','emigration_rate','gs','other_mort','biomass_accum','biomass_accum_rate']:g[key]='-9999'
  g['export']=str(sum(Decimal(v) for v in catches.get(n,{}).values())) if catches.get(n) else '-9999'
  g['diet_imp']=diet.get(n,{}).get('import','-9999')
  g['diet_descr']={'diet':[{'prey_seq':str(prey),'proportion':diet.get(n,{}).get(str(prey),'-9999'),'detritus_fate':'-9999'} for prey in range(1,41)]}
  for key in ['b_hab_area_input','pb_input','qb_input','ee_input']:
   field={'b_hab_area_input':'biomass','pb_input':'pb','qb_input':'qb','ee_input':'ee'}[key]
   evidence=next(c for c in cells[year] if c['seq']==int(n) and c['field']==field)
   g[key]='true' if evidence['source_status']=='author_input' else 'false'
  for key in g:
   if g[key]!=before.get(key):changes.append({'seq':n,'field':key,'converter':before.get(key),'source_canonical':g[key]})
 dump(dest/'model.json',obj);dump(et/'converter_transformations_reversed.json',changes)
 subprocess.run([sys.executable,'-X','utf8',str(SKILL/'database_json.py'),'-j',str(dest/'model.json')],capture_output=True)
 dump(dest/'source_manifest.json',[{'path':str(p.relative_to(ROOT)),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in SRC.iterdir() if p.suffix in ['.pdf','.docx']])
 print(mid,len(groups[year]),'groups')
