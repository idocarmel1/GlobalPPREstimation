from pathlib import Path
import sys,json
from pdf2image import convert_from_path
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')
p=Path(sys.argv[1]); doc=PdfReader(p)
pages=convert_from_path(p,dpi=120,poppler_path='C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin')
for i,page in enumerate(pages): page.save(p.parent/f'page-{i+1}.png')
(p.parent/'page_text.json').write_text(json.dumps([p.extract_text() for p in doc.pages],indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'pages':len(pages),'directory':str(p.parent)},ensure_ascii=False))
