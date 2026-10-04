from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image,ImageOps,ImageDraw
import json
C=Path(__file__).resolve().parents[1]
counts={}
for name in ['review','appendix_preview']:
 d=pdfium.PdfDocument(C/f'qa/{name}.pdf');out=C/'qa'/f'{name}_pages';out.mkdir(exist_ok=True);counts[name]=len(d);thumbs=[]
 for i in range(len(d)):
  im=d[i].render(scale=1.45).to_pil().convert('RGB');im.save(out/f'page-{i+1}.png');im.thumbnail((397,565));tile=Image.new('RGB',(417,590),'#ddd');tile.paste(im,((417-im.width)//2,20));ImageDraw.Draw(tile).text((8,4),f'Page {i+1}',fill='black');thumbs.append(tile)
 for start in range(0,len(thumbs),6):
  subset=thumbs[start:start+6];canvas=Image.new('RGB',(417*3,590*((len(subset)+2)//3)),'white')
  for i,im in enumerate(subset):canvas.paste(im,(417*(i%3),590*(i//3)))
  canvas.save(out/f'contact-{start//6+1}.png')
(C/'qa/render_page_counts.json').write_text(json.dumps(counts,indent=2),encoding='utf8');print(counts)
