from pathlib import Path
import json, hashlib
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'gorbatenko_melnikov_2019.pdf'
doc=pdfium.PdfDocument(str(SOURCE))
reader=PdfReader(SOURCE)
inventory=[]
for n,page in enumerate(doc):
    im=page.render(scale=1.5).to_pil().convert('RGB')
    im.save(HERE/f'source_{n+143}.png')
    inventory.append({'pdf_page':n+1,'printed_page':n+143,'size':page.get_size(),'images':[{'name':p.name,'size':p.image.size} for p in reader.pages[n].images]})
    txt=reader.pages[n].extract_text()
    (HERE/f'source_{n+143}.txt').write_text(txt,encoding='utf8')
for start in range(0,21,7):
    out=Image.new('RGB',(1000,600),'#dddddd')
    draw=ImageDraw.Draw(out)
    for idx in range(start,min(start+7,21)):
        im=Image.open(HERE/f'source_{idx+143}.png');im.thumbnail((240,270))
        col=(idx-start)%4;row=(idx-start)//4
        out.paste(im,(col*250,row*300+20));draw.text((col*250+10,row*300+4),str(idx+143),fill='black')
    out.save(HERE/f'contact_source_{start+143}.png')
(HERE/'source_inventory.json').write_text(json.dumps({'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'pages':inventory},indent=2),encoding='utf8')
print(json.dumps(inventory,indent=2))
