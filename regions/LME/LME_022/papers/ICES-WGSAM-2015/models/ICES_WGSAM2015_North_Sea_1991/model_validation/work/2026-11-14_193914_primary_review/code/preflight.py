from pathlib import Path
import hashlib,json,zipfile,shutil
from lxml import etree as E
RUN=Path(__file__).resolve().parents[1]
BASE=RUN.parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def txt(n):return ''.join(n.xpath('.//w:t/text()',namespaces=NS))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['inputs','outputs','qa']:(RUN/name).mkdir(parents=True,exist_ok=True)
out={}
for name in ['validation.docx','validation_review.docx']:
 p=BASE/name
 with zipfile.ZipFile(p) as z:doc=E.fromstring(z.read('word/document.xml'))
 body=doc.find('w:body',NS)
 table=body.find('w:tbl',NS)
 fields={txt(r[0]):txt(r[1]) for r in table.findall('w:tr',NS) if len(r.findall('w:tc',NS))==2 for r in [r.findall('w:tc',NS)]}
 out[name]={'sha256':sha(p),'fields':fields,'body': [{'tag':E.QName(n).localname,'text':txt(n)[:500]} for n in body]}
 shutil.copyfile(p,RUN/'inputs'/name)
(RUN/'inputs/report_inventory.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
for name,item in out.items():
 print(name,item['sha256'])
 for key in ['Selection rationale','SPPR calculation','Open issues and next action','Review and reproducibility']:print(key,repr(item['fields'].get(key)))
 print('BODY',json.dumps(item['body'][:12],ensure_ascii=False))
(RUN/'artifact.md').write_text('Reference: inputs/validation_review.docx, the last delivered review copy. Preserve current report styling, mapping appendix, geography figures, diagnostic rows and researcher review cells. Authorized changes: selection rationale, SPPR calculation, candidate comparison replaced with four-case primary and sensitivity comparison. Primary ICES separate DOM/POM/Discards with EE floor ON at 0.1; no sign-off, mapping adoption, regional refresh or Project/map/trends publication. Render all pages and verify portable hyperlinks.\n',encoding='utf8')
