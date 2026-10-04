"""Analysis views only; the original PDF and raster are preserved separately."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
im=Image.open(HERE/'audit/figure9_original.png')
arr=np.array(im).astype(int)
r,g,b=arr[:,:,0],arr[:,:,1],arr[:,:,2]
black=(r<120)&(g<120)&(b<120)
masks=dict(red=(r>180)&(g<130)&(b<140),blue=(b>150)&(b-r>80)&(g-r>40),green=(g>100)&(g-r>65)&(g-b>60))
for name,mask in masks.items():
 out=np.full_like(arr,255)
 out[mask|black]=arr[mask|black]
 Image.fromarray(out.astype('uint8')).save(HERE/f'audit/figure9_{name}_analysis.png')
for name,box in [('upper',(0,0,1318,490)),('middle',(0,490,1318,1150)),('lower',(0,1080,1318,1627))]:
 im.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2)).save(HERE/f'audit/figure9_{name}_crop.png')
grid=im.copy();d=ImageDraw.Draw(grid)
for x in range(100,1318,100):
 d.line([(x,0),(x,1627)],fill=(120,120,120),width=1)
 for y in range(500,1627,100):d.text((x+2,y+2),f'{x},{y}',fill='black',stroke_width=1,stroke_fill='white')
for y in range(500,1627,100):d.line([(0,y),(1318,y)],fill=(120,120,120),width=1)
for name,box in [('left',(70,680,670,1445)),('right',(550,600,1318,1540))]:
 grid.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2)).save(HERE/f'audit/figure9_grid_{name}.png')
thesis=HERE.parents[1]/'papers/OKH-GM2019/gorbatenko_2018_dissertation.pdf'
rd=PdfReader(thesis)
for p in [321]:
 for k,image in enumerate(rd.pages[p].images):
  image.image.convert('RGB').save(HERE/f'audit/dissertation_p{p+1}_image{k}.png')
  print(p+1,image.name,image.image.size)
