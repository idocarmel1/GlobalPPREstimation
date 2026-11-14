from pathlib import Path
from lxml import etree as ET
from openpyxl import load_workbook
import zipfile,json,copy,hashlib,os
RUN=Path(__file__).resolve().parents[1]; DEST=RUN.parents[1]/'taxon_mapping.xlsx'
ORIG=RUN/'inputs/taxon_mapping_before.xlsx'; GENERATED=RUN/'outputs/taxon_mapping_candidate.xlsx'
assert DEST.exists()
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'; q=lambda n:'{'+NS+'}'+n
generated=load_workbook(GENERATED)
changes={'xl/worksheets/sheet1.xml':('Taxon mapping',['A2']),'xl/worksheets/sheet2.xml':('Sources',['B11','B13','B20'])}
parts={}; before={}
with zipfile.ZipFile(ORIG) as z:
 for i in z.infolist(): parts[i.filename]=z.read(i.filename); before[i.filename]=parts[i.filename]
for part,(sheet,cells) in changes.items():
 tree=ET.fromstring(parts[part])
 for address in cells:
  c=tree.find('.//'+q('c')+'[@r="'+address+'"]'); assert c is not None
  for child in list(c):
   if child.tag in {q('is'),q('v'),q('f')}: c.remove(child)
  c.set('t','inlineStr'); inline=ET.SubElement(c,q('is')); text=ET.SubElement(inline,q('t')); text.text=generated[sheet][address].value
 parts[part]=ET.tostring(tree,encoding='utf-8',xml_declaration=False)
with zipfile.ZipFile(GENERATED) as z:
 for name in [n for n in parts if n.startswith('xl/tables/') and n.endswith('.xml')]:
  old=ET.fromstring(parts[name]); new=ET.fromstring(z.read(name))
  found=old.find(q('autoFilter'))
  if found is not None: old.remove(found)
  nf=new.find(q('autoFilter')); assert nf is not None
  old.insert(0,copy.deepcopy(nf)); parts[name]=ET.tostring(old,encoding='utf-8',xml_declaration=False)
temp=RUN/'outputs/taxon_mapping_preserved.xlsx'
with zipfile.ZipFile(ORIG) as oz,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as out:
 for i in oz.infolist(): out.writestr(i,parts[i.filename])
a=load_workbook(ORIG); b=load_workbook(temp)
allowed={('Taxon mapping','A2'),('Sources','B11'),('Sources','B13'),('Sources','B20')}; value_changes=[]; errors=[]
for s in a:
 for row in s:
  for c in row:
   d=b[s.title][c.coordinate]
   if c.value!=d.value:
    value_changes.append([s.title,c.coordinate]); assert (s.title,c.coordinate) in allowed
   assert copy.copy(c.font)==copy.copy(d.font) and copy.copy(c.alignment)==copy.copy(d.alignment) and copy.copy(c.fill)==copy.copy(d.fill) and c.number_format==d.number_format
assert set(map(tuple,value_changes))==allowed
assert all(t.autoFilter is not None for s in b for t in s.tables.values())
assert hashlib.sha256(DEST.read_bytes()).digest()==hashlib.sha256(ORIG.read_bytes()).digest(),'Appendix changed concurrently'
os.replace(temp,DEST)
qa={'method':'Artifact Tool authored updated text and table filters; bounded OOXML transfer preserved original package outside exact affected cells and table-filter elements.','changed_cells':value_changes,'changed_parts':[n for n in parts if parts[n]!=before[n]],'all_cell_styles_preserved':True,'native_filters_present':True,'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest()}
(RUN/'qa/final_appendix_preservation.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
print(json.dumps(qa,indent=2))
