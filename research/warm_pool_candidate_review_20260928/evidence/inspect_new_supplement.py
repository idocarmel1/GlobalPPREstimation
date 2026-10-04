from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import hashlib,json,shutil

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
source=BASE/'Griffiths2019/fog12389-sup-0001-appendixs1-s4.docx'
review=ROOT/'regions/EEZ_941/models/941_201901_Warm_Pool_(2005)/source_review'
archive=ROOT/'regions/EEZ_941/papers/Griffiths-2019'/source.name
shutil.copy2(source,archive)
history=review/'history_before_supplement';history.mkdir(exist_ok=True)
for name in ['ADMISSION_STATUS.json','SOURCE_ADMISSION.md','SOURCE_VALIDATION.json']:
    if not (history/name).exists():shutil.copy2(review/name,history/name)
for name in ['PACIFIC_PAPER_COMPARISON.md','PROGRESS_STATUS.json','REGISTRATION_PROPOSAL.json']:
    if not (history/name).exists():shutil.copy2(BASE/name,history/name)
w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
raw=source.read_bytes()
with ZipFile(source) as z:
    xml=z.read('word/document.xml');doc=ET.fromstring(xml)
def txt(e):return ''.join(x.text or '' for x in e.iter(w+'t'))
tables=[];paras=[];body=[]
for e in doc.find(w+'body'):
    if e.tag==w+'p':
        s=txt(e);paras.append(s);body.append({'paragraph':len(paras),'text':s})
    elif e.tag==w+'tbl':
        rows=[]
        for r in e.findall(w+'tr'):
            cells=[];col=0
            before=r.find(w+'trPr/'+w+'gridBefore')
            if before is not None:col=int(before.get(w+'val'))
            for c in r.findall(w+'tc'):
                span=c.find(w+'tcPr/'+w+'gridSpan'); span=int(span.get(w+'val')) if span is not None else 1
                cells.append({'grid_start':col,'grid_span':span,'text':txt(c)})
                col+=span
            rows.append(cells)
        tables.append(rows);body.append({'table':len(tables),'rows':rows})
data={'source_sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw),'tables':tables,'body':body}
(review/'SUPPLEMENT_XML_EVIDENCE.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(review/'SUPPLEMENT_PROSE.txt').write_text('\n'.join(f'{i}: {s}' for i,s in enumerate(paras,1)),encoding='utf-8')
manifest={'source':str(source.relative_to(ROOT)),'archive':str(archive.relative_to(ROOT)),'sha256':data['source_sha256'],'size_bytes':len(raw),'provenance':'User supplied the original Word supplement on 2026-09-28; exact bytes archived. Filename agrees with publisher supporting-information listing.','xml_tables':len(tables)}
(review/'SUPPLEMENT_SOURCE.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
for i,t in enumerate(tables,1):
    print('TABLE',i,'rows',len(t),'widths',sorted({sum(c['grid_span'] for c in r) for r in t}))
    for r in t[:4]:print([(c['grid_start'],c['grid_span'],c['text'][:160]) for c in r])
