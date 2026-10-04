from pathlib import Path
import sys,json,hashlib,zipfile
from xml.etree import ElementTree as E
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,overview
book=read_book(ROOT/'regions/LME_027/LME_027.xlsx')
frozen={s:book[s] for s in ['Overview','Catch','Classic PPR','NPP']}
(OUT/'frozen_workbook_evidence.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2),encoding='utf-8')
print('SETTINGS',json.dumps(overview(book),ensure_ascii=False))
for s in frozen:
 print(s,{n:(len(h),len(r)) for n,(h,r) in frozen[s].items()})
catch=records(book,'Catch','Catch')
cl={r['taxon']:r for r in records(book,'Classic PPR','Taxa')}
rows=[]
for r in catch:
 if r['catch_basis']=='catch':rows.append({**{k:v for k,v in r.items() if not isinstance(k,int)},'catch2019':r.get(2019),'classic':cl.get(r['taxon'])})
(OUT/'catch_labels.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows:print(r['taxon'], '|',r['common_name'],'|',r['functional_group'],'|',r['commercial_group'],'|',r['catch2019'])
p=ROOT/'regions/LME_027/papers/CAN-2014/pone.0094742.s001-eb18ca66.docx'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(p) as z:root=E.fromstring(z.read('word/document.xml'))
parts=[];tables=[]
for i,ch in enumerate(root.find('w:body',ns)):
 if ch.tag.endswith('}p'):
  t=''.join(ch.itertext()) if False else ''.join(x.text or '' for x in ch.findall('.//w:t',ns))
  if t:parts.append(f'P{i}: {t}')
 elif ch.tag.endswith('}tbl'):
  tab=[]
  for row in ch.findall('w:tr',ns):
   tab.append([' | '.join(''.join(x.text or '' for x in p.findall('.//w:t',ns)) for p in cell.findall('w:p',ns)) for cell in row.findall('w:tc',ns)])
  tables.append({'body_index':i,'rows':tab});parts.append(f'TABLE {len(tables)} BODY {i}\n'+'\n'.join('\t'.join(row) for row in tab))
(OUT/'source_supplement.txt').write_text('\n\n'.join(parts),encoding='utf-8')
(OUT/'source_supplement_tables.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2),encoding='utf-8')
try:
 import pypdf
 pdf=pypdf.PdfReader(ROOT/'regions/LME_027/papers/CAN-2014/file-e30dfe50.pdf')
 (OUT/'source_article.txt').write_text('\n\n'.join(f'PDF PAGE {i+1}\n'+p.extract_text() for i,p in enumerate(pdf.pages)),encoding='utf-8')
except Exception as e:print(type(e).__name__,str(e))
