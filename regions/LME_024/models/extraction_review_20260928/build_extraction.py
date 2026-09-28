from pathlib import Path
import json,sys,csv,subprocess,hashlib
from decimal import Decimal
from docx import Document
from openpyxl import Workbook
ROOT=Path(__file__).resolve().parents[4]; REVIEW=Path(__file__).resolve().parent
SRC=ROOT/'regions/LME_024/papers/LME024-Hernvann-2020'
MID='Hernvann_2020_Celtic_Sea_1985'; MD=ROOT/'regions/LME_024/models'/MID
MD.mkdir(exist_ok=True)
SCRIPTS=Path('C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
tables=json.loads((REVIEW/'docx_tables.json').read_text(encoding='utf8'))
doc=Document(next(SRC.glob('*.docx')))
def clean(x): return ' '.join(x.split())
def num(x): return clean(x).replace(',','.') or None
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
groups=[]; evidence=[]
fields=['n','name','tl','biomass','pb','qb','ee','pq','ba_rate','unassim']
for r,row in enumerate(tables[4][1:],2):
 g={k:num(v) for k,v in zip(fields,row)};g['n']=int(g['n']);g['name']=clean(row[1]);groups.append(g)
 for c,(k,v) in enumerate(zip(fields,row),1):
  runs=[run for p in doc.tables[4].rows[r-1].cells[c-1].paragraphs for run in p.runs]
  evidence.append({'table':'B4','docx_table':5,'row':r,'column':c,'group_seq':g['n'],'field':k,'source_text':v,'value':g[k],'bold_runs':[run.text for run in runs if run.bold],'meaning':'bold denotes model estimate per caption'})
diet={};dietnames={}
for ti in (1,2):
 t=tables[ti]
 for c,pred in enumerate(t[0][2:],2):
  diet[pred]={}
  for r,row in enumerate(t[1:],2):
   prey=clean(row[0]) or 'import'; value=num(row[c]); diet[pred][prey]=value
   if prey!='import':dietnames[int(prey)]=clean(row[1])
   evidence.append({'table':'B2','docx_table':ti+1,'row':r,'column':c+1,'predator_seq':int(pred),'prey_seq':prey,'source_text':row[c],'value':value})
assert sorted(dietnames)==list(range(1,55))
# Names vary between source tables; retain exact B4 names and explicit reviewed aliases.
catch_alias={'Carnivorous dem. elasmobranchs':'Piscivorous dem. elasmobranchs'}
for g in groups:
 catch_alias[g['name'].replace(' dem. fish',' demersal fish')]=g['name']
landings={};discards={}; name2id={g['name']:g['n'] for g in groups}
for r,row in enumerate(tables[3][1:],2):
 name=clean(row[0]);canonical=catch_alias.get(name,name)
 if name in ['Anglerfish','Hake','Cod','Sum']:continue
 seq=name2id[canonical]
 for c,dest,field in [(1,landings,'landings'),(2,discards,'discards')]:
  dest[str(seq)]={'Total fishery':num(row[c])}
  evidence.append({'table':'B3','docx_table':4,'row':r,'column':c+1,'group_seq':seq,'source_group_name':name,'canonical_group_name':canonical,'field':field,'source_text':row[c],'value':num(row[c])})
assert len(landings)==54
model={'metadata':{'LME':'24','model_number':2402020,'model_name':'Celtic Sea Hernvann','model_year':1985},'groups':groups,'consumers':list(range(1,51)),'fleets':['Total fishery'],'landings':landings,'discards':discards,'detritus_groups':['Discards','Detritus'],'detritus_fate':{},'diet':diet,'diet_rows':54,'landings_rows':54,'discards_rows':54}
save(REVIEW/'extraction_input.json',model)
save(REVIEW/'cell_evidence.json',evidence)
save(REVIEW/'group_name_crosswalk.json',{'diet':dietnames,'catch_aliases':catch_alias})
run=subprocess.run([sys.executable,str(SCRIPTS/'write_outputs.py'),str(REVIEW/'extraction_input.json'),'--outdir',str(MD),'--dir-name','extracted_tables'],capture_output=True,text=True,encoding='utf8')
(REVIEW/'writer.log').write_text(run.stdout+run.stderr,encoding='utf8');assert run.returncode==0,run.stderr
ED=MD/'extracted_tables'
aliases={1:'Plunge and pursuit divers seabirds',2:'Surface feeders seabirds',4:'Toothed whales and Seals',6:'Piscivorous demersal elasmobranchs',7:'Benthivorous demersal elasmobrancs',9:'Anglerfish',10:'Anglerfish',11:'Hake',12:'Hake',13:'Cod',14:'Cod',21:'Piscivorous demersal fish',22:'Epibenthivorous demersal fish',23:'Endobenthivorous demersal fish',24:'Suprabenthivorous demersal fish',25:'Small benthivorous demersal fish',31:'Sardine',33:'Large Pelagic fish',34:'Medium pelagic fish',37:'Commercial large crustaceans',38:'Norway lobster',39:'Commercial bivalves (ComBiv)',40:'Shrimps (Sh)',41:'Carnivores and necrophages (CarnNec)',42:'Suspension and surface deposit feeders (SSDF)',43:'Subsurface deposit feeders (SubSDF)',44:'Suprabenthos (Supra)',45:'Benthic meiofauna (Meio)',46:'Macrozooplankton (MacroZ)',47:'Mesozooplankton - Large (MesoL)',48:'Mesozooplankton - Small (MesoS)',49:'Microzooplankton (MicroZ)',51:'Phytoplankton - Large (PhL)',52:'Phytoplankton - Small (PhS)'}
tax=[];member_evidence=[]
for g in groups:
 key=aliases.get(g['n'],g['name']); matches=[(i+2,r) for i,r in enumerate(tables[0][1:]) if clean(r[2])==key]
 members=[];comments=[]
 for ri,r in matches:
  # Source B1 accidentally exchanges common/Latin columns for its two seals.
  latin=clean(r[0] if ri in (27,28) else r[1]);comment=clean(r[3])
  if latin:members.append(latin)
  if comment and comment not in comments:comments.append(comment)
  member_evidence.append({'group_seq':g['n'],'group_name':g['name'],'table':'B1','docx_table':1,'row':ri,'source_group':key,'source_common_name':r[0],'source_latin_name':r[1],'member':latin,'comment':comment,'column_swap_corrected':ri in (27,28)})
 desc='; '.join(dict.fromkeys(members))
 if comments:desc+=(' — ' if desc else '')+'; '.join(comments)
 if not desc:desc='not documented — B1 has no member row; B4 group label: '+g['name']
 if g['n'] in (9,10,11,12,13,14):desc+='; '+('adult' if g['n']%2 else 'juvenile')+' life stage per B4; no numerical age boundary supplied'
 tax.append([g['n'],g['name'],desc])
w=Workbook();ws=w.active;ws.title='Taxonomy';ws.append(['seq','group_name','taxon_descr'])
for row in tax:ws.append(row)
w.save(ED/'Taxonomy.xlsx');save(REVIEW/'taxonomy_evidence.json',member_evidence)
with (ED/'taxonomy.csv').open('w',encoding='utf8',newline='') as f:
 cw=csv.writer(f);cw.writerow(['seq','group_name','taxon_descr']);cw.writerows(tax)
for script,args,name in [('validate.py',[str(ED)],'validate'),('massbalance_check.py',[str(ED)],'source_massbalance'),('database_json.py',['-d',str(ED)],'converter')]:
 p=subprocess.run([sys.executable,str(SCRIPTS/script),*args],capture_output=True,text=True,encoding='utf8',errors='replace')
 (REVIEW/f'{name}.log').write_text(p.stdout+p.stderr,encoding='utf8');print(name,p.returncode)
# Preserve converter output as evidence; reconstruct source-faithful database fields.
converted=next(ED.glob('24_2402020*.json'));raw=json.loads(converted.read_text())
save(REVIEW/'converter_raw.json',raw)
source=json.loads(json.dumps(raw));changes=[]
for sg,g,tr in zip(source['group'],groups,tax):
 n=g['n']; old=json.loads(json.dumps(sg))
 sg.update({'biomass':g['biomass'] or '-9999','habitat_area':'-9999','ge':g['pq'] or '-9999','ge_input':'true' if g['pq'] is not None else 'false','tl':g['tl'] or '-9999','diet_imp':diet.get(str(n),{}).get('import') or '-9999','taxon_descr':tr[2]})
 for source_field,target_field in [('biomass','biomass_habitat_area'),('pb','pb'),('qb','qb'),('ee','ee'),('unassim','gs'),('ba_rate','biomass_accum_rate')]:
  sg[target_field]=g[source_field] if g[source_field] is not None else '-9999'
 sg['export']=str(sum((Decimal(x[str(n)]['Total fishery']) for x in (landings,discards)),Decimal(0)))
 # Retain explicit zeros and absent cells in source JSON, including both unknown routing pools.
 entries=[]
 for prey in range(1,55):
  value=diet.get(str(n),{}).get(str(prey))
  if value is not None or prey in (53,54):entries.append({'prey_seq':str(prey),'proportion':value if value is not None else '-9999','detritus_fate':'-9999'})
 sg['diet_descr']={'diet':entries}
 for k in sg:
  if sg[k]!=old.get(k):changes.append({'group_seq':n,'field':k,'converter_value':old.get(k),'source_value':sg[k]})
save(MD/'model.json',source);save(REVIEW/'converter_source_restoration.json',changes)
save(REVIEW/'model_identity.json',{'model_id':MID,'year':1985,'serialization_number':2402020,'serialization_number_is_ecobase_accession':False,'groups':54,'consumers':50,'primary_producers':2,'detritus':2,'source_table':'B4','source_unknown_biomass_count':0})
print(MD)
