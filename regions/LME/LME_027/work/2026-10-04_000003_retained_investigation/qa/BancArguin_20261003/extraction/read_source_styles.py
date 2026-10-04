from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E
h=Path(__file__).resolve().parent;root=h.parents[4];p=root/'regions/LME_027/papers/CAN-2014/pone.0094742.s001-eb18ca66.docx';ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(p) as z:r=E.fromstring(z.read('word/document.xml'))
out=[]
for ti,t in enumerate(r.findall('w:body/w:tbl',ns),1):
 for ri,row in enumerate(t.findall('w:tr',ns),1):
  for ci,cell in enumerate(row.findall('w:tc',ns),1):
   runs=[]
   for run in cell.findall('.//w:r',ns):
    text=''.join(x.text or '' for x in run.findall('w:t',ns));b=run.find('w:rPr/w:b',ns);ital=run.find('w:rPr/w:i',ns)
    if text:runs.append({'text':text,'bold':b is not None and b.get('{'+ns['w']+'}val','1') not in ('0','false','off'),'italic':ital is not None and ital.get('{'+ns['w']+'}val','1') not in ('0','false','off')})
   out.append({'physical_table':ti,'row':ri,'column':ci,'text':''.join(x['text'] for x in runs),'explicit_bold':any(x['bold'] for x in runs),'runs':runs})
(h/'original_docx_styles.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('Read DOCX source formatting',len(out),'cells')
