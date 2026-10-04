from pathlib import Path
from PIL import Image
import pymupdf
import hashlib
import json

OUT=Path(__file__).resolve().parent
MODEL=OUT.parents[2]
PAPERS=MODEL.parents[1]/'papers'/'OKH-GM2019'
sources=[]
for name,pages in [('gorbatenko_melnikov_2019.pdf',[12,15]),('gorbatenko_2018_dissertation.pdf',[123,124,125,298])]:
    path=PAPERS/name
    doc=pymupdf.open(path)
    for pn in pages:
        stem=('primary2019' if 'melnikov' in name else 'dissertation2018')+f'_p{pn}'
        page=doc[pn-1]
        page.get_pixmap(matrix=pymupdf.Matrix(2,2)).save(OUT/(stem+'_source.png'))
        (OUT/(stem+'_text.txt')).write_text(page.get_text(),encoding='utf-8')
    sources.append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':pages})
article=pymupdf.open(PAPERS/'gorbatenko_melnikov_2019.pdf')
page=article[11]
words=page.get_text('words')
word=next(w for w in words if w[4]=='Медузы')
clip=pymupdf.Rect(50,word[1]-6,page.rect.width-35,word[3]+6)
page.get_pixmap(matrix=pymupdf.Matrix(4,4),clip=clip).save(OUT/'primary2019_table3_jelly_row_source.png')
sources[0]['table3_jelly_row_pdf_bounds']=list(clip)
figure=Image.open(MODEL/'audit'/'figure9_original.png').convert('RGB')
for name,bounds in [('jellyfish_figure9_local',(800,740,1318,1180)),('jellyfish_figure9_production',(960,890,1170,965)),('jellyfish_figure9_F24_label',(720,580,890,700)),('jellyfish_figure9_F48_label',(690,980,840,1070)),('jellyfish_figure9_F50_label',(560,1020,690,1100)),('jellyfish_figure9_outgoing_labels',(995,840,1170,1000))]:
    crop=figure.crop(bounds)
    crop.save(OUT/(name+'_source_native.png'))
    crop.resize((crop.width*3,crop.height*3),Image.Resampling.NEAREST).save(OUT/(name+'_source_x3.png'))
    sources.append({'crop':name+'_source_native.png','bounds_original_pixels':list(bounds),'source':str(MODEL/'audit'/'figure9_original.png'),'unmodified_native_pixels':True})
(OUT/'source_evidence.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(OUT)
