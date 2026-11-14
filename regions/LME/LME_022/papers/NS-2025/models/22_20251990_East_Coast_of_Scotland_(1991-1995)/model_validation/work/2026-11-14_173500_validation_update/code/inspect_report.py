from pathlib import Path
from docx import Document
import json, sys, zipfile
sys.stdout.reconfigure(encoding='utf-8')
model = Path(__file__).resolve().parents[4]
report = model / 'model_validation/validation.docx'
doc = Document(report)
print('MODEL',model)
print('PARAGRAPHS')
for i,p in enumerate(doc.paragraphs): print(i,repr(p.text))
print('TABLES')
for i,t in enumerate(doc.tables):
    print('TABLE',i)
    for j,r in enumerate(t.rows): print(j,[c.text for c in r.cells])
print('FILES')
for p in (model/'model_validation').iterdir(): print(p.name)
print('LINKS')
with zipfile.ZipFile(report) as z: print(z.read('word/_rels/document.xml.rels').decode())
