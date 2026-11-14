from pathlib import Path
from lxml import etree as E
import json, zipfile, hashlib, shutil, sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
RUN=Path(__file__).resolve().parents[1]
BASE=RUN.parents[1]
sys.path.insert(0,str(ROOT))
from tools.project_core.validation.researcher_review import read_report
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def text(el):
    return ''.join(n.text or '' if n.tag==W+'t' else '\n' if n.tag in {W+'br',W+'cr'} else '\t' if n.tag==W+'tab' else '' for n in el.iter())
for d in ['inputs','outputs','qa']: (RUN/d).mkdir(parents=True,exist_ok=True)
for src,name in [(BASE/'validation.docx','validation_before.docx'),(ROOT/'tools/templates/validation.docx','template_reference.docx')]:
    dst=RUN/'inputs'/name
    if not dst.exists(): shutil.copy2(src,dst)
def inventory(path):
    with zipfile.ZipFile(path) as z:
        doc=E.fromstring(z.read('word/document.xml'))
        parts={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
        rels=E.fromstring(z.read('word/_rels/document.xml.rels'))
    body=doc.find(W+'body')
    elements=[]
    for i,e in enumerate(body):
        if e.tag==W+'tbl': elements.append({'i':i,'table':[[text(c) for c in r.findall(W+'tc')] for r in e.findall(W+'tr')]})
        else: elements.append({'i':i,'tag':e.tag.split('}')[-1],'text':text(e)})
    try: parser={'result':read_report(ROOT,path,BASE.parent.name)}
    except ValueError as exc: parser={'expected_unsigned_error':str(exc)}
    return {'sha256':sha(path),'elements':elements,'parts':parts,'relationships':[dict(r.attrib) for r in rels], 'parser':parser}
data={'existing':inventory(BASE/'validation.docx'),'template':inventory(ROOT/'tools/templates/validation.docx')}
(RUN/'inputs/report_inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'existing':data['existing']['elements'],'parser':data['existing']['parser'],'template_elements':data['template']['elements']},ensure_ascii=False,indent=2))
