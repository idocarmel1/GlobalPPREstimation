from pathlib import Path
import sys,json
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'_deps'))
import fitz
qa=root.parent/'qa/reports'
results=[]
for variant in ['Base','M30','P30']:
    doc=fitz.open(qa/(variant+'.pdf'))
    pages=[]
    for i,page in enumerate(doc):
        dest=qa/f'{variant}_page_{i+1:02d}.png'
        page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(dest)
        pages.append({'page':i+1,'image':str(dest),'text':page.get_text(),'bounds':list(page.rect)})
    results.append({'variant':variant,'page_count':len(doc),'pages':pages})
(qa/'render_manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{'variant':x['variant'],'pages':x['page_count']} for x in results]))
