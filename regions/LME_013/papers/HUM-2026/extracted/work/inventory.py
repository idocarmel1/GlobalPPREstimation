from pathlib import Path
import sys, json, zipfile, xml.etree.ElementTree as ET
sys.path.insert(0,r'C:\Users\idoca\.agents\skills\ecopath-extraction\scripts')
from pdf_backend import page_count, page_text
root=Path(__file__).parents[3]
for aid in ['HUM-2026','HUM-2018']:
    folder=root/aid
    work=folder/'extracted'/'work'
    work.mkdir(parents=True,exist_ok=True)
    pdf=next(folder.glob('*.pdf'))
    n=page_count(pdf)
    print(aid,n,'pages')
    for i in range(1,n+1):
        txt=page_text(pdf,i)
        (work/f'page-{i:02}.txt').write_text(txt,encoding='utf-8')
    for d in folder.glob('*.docx'):
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        with zipfile.ZipFile(d) as z:
            rt=ET.fromstring(z.read('word/document.xml'))
            out=[]
            for el in rt.find('w:body',ns):
                if el.tag.endswith('}p'):
                    s=''.join(el.itertext()) if False else ''.join(el.iterfind('.//w:t',ns).__str__()) if False else ''.join(t.text or '' for t in el.findall('.//w:t',ns))
                    if s: out.append(s)
                elif el.tag.endswith('}tbl'):
                    rows=[[''.join(t.text or '' for t in cell.findall('.//w:t',ns)) for cell in row.findall('w:tc',ns)] for row in el.findall('w:tr',ns)]
                    out.append(rows)
            (work/'docx_content.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
            print(d.name,'tables',sum(isinstance(x,list) for x in out))
