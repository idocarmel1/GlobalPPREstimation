from pathlib import Path
from decimal import Decimal as D
import json,csv,hashlib,subprocess,sys,shutil,openpyxl
w=Path(r'C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/קוד/PPR_Ecopath_Atlas/archive/regions/LME_036/SCS-2007/extracted/work');out=w.parent
results=[]
for year in ['1970s','2000s']:
 d=out/f'SCS-2007_Northern_South_China_Sea_{year}'
 m=json.loads((d/'model.json').read_text(encoding='utf-8'))
 dbpath=d/f'36_South_China_Sea_SCS-2007_Northern_South_China_Sea_({year}).json'
 db=json.loads(dbpath.read_text(encoding='utf-8'));assert len(db['group'])==38
 basic=list(csv.reader((d/'Basic_input.csv').open(encoding='utf-8',newline='')))
 diet=list(csv.reader((d/'Diet_composition.csv').open(encoding='utf-8',newline='')))
 fieldcols={'biomass':3,'z':4,'pb':5,'qb':6,'ee':7,'other_mort':8,'pq':9,'unassim':10}
 checked=0
 for g,rec in zip(m['groups'],basic[1:]):
  assert int(rec[0])==g['n'] and rec[1]==g['name']
  for key,col in fieldcols.items(): assert rec[col]==str(g.get(key) or ''),(year,g['n'],key,rec[col],g.get(key))
 for g in db['group']:
  n=int(g['group_seq']);src=m['groups'][n-1]
  assert g['group_name']==src['name']
  for key in ['pb','qb','ee','other_mort']:
   assert D(g[key])==D(src.get(key,'-9999')),(year,n,key)
  assert D(g['biomass_habitat_area'])==D(src['biomass'])
  assert D(g['biomass'])==D(src['biomass'])
  assert g['habitat_area']=='-9999' and g['gs']=='-9999' and g['biomass_accum']=='-9999' and g['biomass_accum_rate']=='-9999'
  assert D(g['ge'])==D(src.get('pq','-9999'))
  items=(g.get('diet_descr') or {}).get('diet') or []
  if isinstance(items,dict):items=[items]
  actual={str(i['prey_seq']):D(i['proportion']) for i in items if D(i['proportion'])>0}
  expected={k:D(v) for k,v in m['diet'].get(str(n),{}).items()}
  assert actual==expected,(year,n,'diet changed',actual,expected)
  for i in items:assert i['detritus_fate']=='-9999'
  for prey,v in expected.items():
   col=diet[0].index(str(n));assert diet[int(prey)][col]==m['diet'][str(n)][prey]
   checked+=1
  assert abs(D(g['export'])-sum(D(v) for v in m['landings'][str(n)].values()))<D('1e-12')
 for file in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Biomass_accumulation.csv','Detritus_fate.csv']:
  b=(d/file).read_bytes();assert b'"' not in b and b.endswith(b'\r\n') and b'\n' not in b.replace(b'\r\n',b'')
 md=openpyxl.load_workbook(d/'Metadata.xlsx',data_only=True).active
 assert dict(md.iter_rows(min_row=1,max_row=4,max_col=2,values_only=True))==m['metadata']
 tl=openpyxl.load_workbook(d/'TL.xlsx',data_only=True).active
 assert tl['C1'].value=='TL'
 for g in m['groups']:assert tl.cell(g['n']+1,2).value==g['name'] and tl.cell(g['n']+1,3).value is None
 rw=openpyxl.load_workbook(dbpath.with_name(dbpath.stem+'_reconstructed.xlsx'),data_only=True)
 assert all(row[0] in (None, "") for row in rw['Detritus fate'].iter_rows(min_row=2,max_row=39,min_col=3,max_col=3,values_only=True))
 bi=list(rw['Basic input'].values);headers=bi[0]
 for row,g in zip(bi[1:],m['groups']):
  assert row[1]==g['name']
  for key,label in [('biomass','Biomass in habitat area (t/km^2)'),('pb','Production / biomass (/year)'),('qb','Consumption / biomass (/year)'),('ee','Ecotrophic Efficiency'),('pq','Production / consumption'),('other_mort','Other mortality')]:
   val=row[headers.index(label)]
   if g.get(key) is None:assert val in (None, "")
   else:assert D(str(val))==D(g[key]),(year,g['n'],key,val,g[key])
 for sheet in rw:
  for row in sheet:
   for cell in row:assert cell.data_type!='e',(year,sheet.title,cell.coordinate,cell.value)
 validation=subprocess.run([sys.executable,r'C:/Users/idoca/.agents/skills/ecopath-extraction/scripts/validate.py',str(d)],text=True,capture_output=True,encoding='utf-8')
 (d/'VALIDATION.txt').write_text(validation.stdout,encoding='utf-8')
 assert validation.returncode==0 and '0 error(s), 41 warning(s)' in validation.stdout
 for p in d.glob('*.inspect.ndjson'):shutil.move(str(p),str(w/f'{year}-{p.name}'))
 results.append({'period':year,'groups':38,'consumer_diets':35,'exact_diet_values_verified_across_csv_json':checked,'structure_errors':0,'structure_warnings':41,'unknown_BA_GS_habitat_preserved':True,'workbook_values_checked':True,'balance':'INDETERMINATE'})
# Reference bundle remains unchanged from inventory.
for item in json.loads((out/'SOURCE_INVENTORY.json').read_text()):
 assert hashlib.sha256((out.parent/item['file']).read_bytes()).hexdigest()==item['sha256']
print(json.dumps(results,indent=2))
(out/'FINAL_VERIFICATION.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('Printed 2000s group-total sum:',sum(D(r['2000s_printed_total']) for r in json.loads((w/'catch_source_totals.json').read_text())))

