from pathlib import Path
import json,zipfile,hashlib,sys,copy
from lxml import etree as E
R=Path.cwd();O=R/'outputs/validation_revision_20260930';sys.path[:0]=[str(O),str(R/'tools')]
from read_fast import read_fast
from workbooks import records,input_hash
from regional import result_hash
D=R/'regions/LME_036/validation_reports/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)/adopted_revision_20260930'
N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};S='{'+N['s']+'}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(c):
 if c.get('t')=='inlineStr':return ''.join(c.xpath('.//s:t/text()',namespaces=N))
 v=c.find(S+'v');return v.text if v is not None else None
def edit(path,sheetfile,table,select,updates):
 with zipfile.ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
 root=E.fromstring(parts[sheetfile]);active=False;headers=None;changed=0
 for row in root.findall('.//s:sheetData/s:row',N):
  cells=row.findall(S+'c');vals=[text(c) for c in cells]
  if vals and vals[0]=='@table':active=vals[1]==table;headers=None;continue
  if not active:continue
  if headers is None:headers=vals;continue
  rec=dict(zip(headers,vals))
  if select(rec):
   bycol={''.join(filter(str.isalpha,c.get('r'))):c for c in cells}
   for key,value in updates.items():
    index=headers.index(key);col=''
    while index>=0:col=chr(65+index%26)+col;index=index//26-1
    c=bycol[col]
    for child in list(c):c.remove(child)
    c.set('t','inlineStr');E.SubElement(E.SubElement(c,S+'is'),S+'t').text=value
   changed+=1
 parts[sheetfile]=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for name,value in parts.items():z.writestr(name,value)
 return changed
region=R/'regions/LME_036/LME_036.xlsx';before=read_fast(region);oldhash=sha(region)
fix=dict(rule='single_group_analogue',rule_details='W1 no split: weight 1 in the selected ecological analogue',source_catch_basis='Not applicable: no allocation split')
assert edit(region,'xl/worksheets/sheet5.xml','Allocation assumptions',lambda r:r.get('taxon') in ['Ruvettus pretiosus','Gadiformes'],fix)==2
after=read_fast(region);expected=copy.deepcopy(before);h,rows=expected['PPR']['Allocation assumptions']
for row in rows:
 if row[h.index('taxon')] in ['Ruvettus pretiosus','Gadiformes']:
  for k,v in fix.items():row[h.index(k)]=v
assert after==expected and input_hash(after)==input_hash(before) and result_hash(after)==result_hash(before)
newhash=sha(region)
project=R/'Project.xlsx';pb=read_fast(project)
with zipfile.ZipFile(project) as z:
 workbook=E.fromstring(z.read('xl/workbook.xml'))
 titles=[x.get('name') for x in workbook.findall('s:sheets/s:sheet',N)]
sheetfile=f"xl/worksheets/sheet{titles.index('Regions & status')+1}.xml"
assert edit(project,sheetfile,'Regions',lambda r:r.get('unit_id')=='LME_036',{'sha256':newhash})==1
pa=read_fast(project);pe=copy.deepcopy(pb);h,rows=pe['Regions & status']['Regions']
for row in rows:
 if row[h.index('unit_id')]=='LME_036':assert row[h.index('sha256')]==oldhash;row[h.index('sha256')]=newhash
assert pa==pe
html={}
for name in ['interactive_map/index.html','interactive_map/trends.html','interactive_map/archive/index.html']:
 p=R/name;raw=p.read_bytes();count=raw.count(oldhash.encode());html[name]=count
 assert b'model_none_proxy' not in raw
 if count:p.write_bytes(raw.replace(oldhash.encode(),newhash.encode()))
cached=json.loads((O/'adopted_book.json').read_text(encoding='utf-8'));h,rows=cached['PPR']['Allocation assumptions']
for row in rows:
 if row[h.index('taxon')] in ['Ruvettus pretiosus','Gadiformes']:
  for k,v in fix.items():row[h.index(k)]=v
(O/'adopted_book.json').write_text(json.dumps(cached,ensure_ascii=False),encoding='utf-8')
p=D/'input_identity.json';ident=json.loads(p.read_text());assert ident['last_adopted_sha256']==oldhash;ident['last_adopted_sha256']=newhash;p.write_text(json.dumps(ident,indent=2),encoding='utf-8')
p=O/'integration_complete.json';q=json.loads(p.read_text());q['project_sha256']=sha(project);p.write_text(json.dumps(q,indent=2),encoding='utf-8')
checks=dict(two_single_group_metadata_rows_corrected=True,all_other_regional_tables_and_values_exact=True,regional_scientific_input_and_result_hashes_unchanged=True,only_project_regional_fingerprint_changed=True,html_fingerprint_replacements=html)
(D/'ledger_metadata_correction.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2))
