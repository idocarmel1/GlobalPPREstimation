from pathlib import Path
import sys, json
from pdf2image import convert_from_path
from pypdf import PdfReader
p=Path(sys.argv[1])
doc=PdfReader(p)
pages=convert_from_path(p,dpi=120,poppler_path='C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin')
for i,page in enumerate(pages,1): page.save(p.parent/f'page-{i}.png')
(p.parent/'page_text.json').write_text(json.dumps([q.extract_text() for q in doc.pages],ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'pages':len(doc.pages),'pdf':str(p)},ensure_ascii=False))
