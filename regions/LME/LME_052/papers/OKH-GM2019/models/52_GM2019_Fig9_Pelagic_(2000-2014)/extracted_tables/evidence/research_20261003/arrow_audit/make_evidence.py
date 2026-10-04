from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, runpy, json, hashlib
base=Path(r'C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\GlobalPPREstimation\regions\LME_052\models\52_GM2019_Fig9_Pelagic_(2000-2014)')
out=base/'research_20261003'/'arrow_audit'
im=Image.open(base/'audit'/'figure9_original.png').convert('RGB')
box=(140,1080,820,1525)
im.crop(box).save(out/'F77_unannotated_source_crop.png')
im.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.Resampling.NEAREST).save(out/'F77_unannotated_source_crop_x3.png')
a=np.asarray(im); green=(a[:,:,1]>120)&(a[:,:,0]<140)&(a[:,:,2]<160); black=(a.max(axis=2)<130)
g=np.ones(a.shape,dtype=np.uint8)*255;g[green|black]=a[green|black]
Image.fromarray(g).crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.Resampling.NEAREST).save(out/'F77_green_reading_aid_x3.png')
pts=[(295,1163),(284,1235),(300,1320),(327,1384),(390,1449),(450,1474),(513,1485),(559,1484)]
anno=im.copy();d=ImageDraw.Draw(anno)
# Small numbered checkpoints preserve visibility of the actual curve between them.
for idx,(x,y) in enumerate(pts,1):
 d.ellipse((x-5,y-5,x+5,y+5),outline=(200,0,200),width=2)
 d.text((x+8,y-10),str(idx),fill=(150,0,150),stroke_width=1,stroke_fill=(255,255,255))
# Dashed magenta trace is a diagnostic overlay, not a new source curve.
for p,q in zip(pts,pts[1:]):
 dx=q[0]-p[0];dy=q[1]-p[1];n=max(1,int((dx*dx+dy*dy)**.5/5))
 for j in range(n):
  if j%3==0:
   t0=j/n;t1=min(1,(j+.7)/n)
   d.line([(p[0]+dx*t0,p[1]+dy*t0),(p[0]+dx*t1,p[1]+dy*t1)],fill=(200,0,200),width=1)
anno.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.Resampling.NEAREST).save(out/'F77_annotated_path_x3.png')
# Direct box crops, kept independent of table values.
groups=runpy.run_path(str(base/'figure9_data.py'))['GROUPS']
thumbs=[]
for gid,en,ru,val,b,tier in groups:
 c=im.crop(b);sheet=Image.new('RGB',(600,175),'white');
 c.thumbnail((570,125));sheet.paste(c,((600-c.width)//2,35))
 ImageDraw.Draw(sheet).text((10,10),f'{gid:02d} {en}',fill='black');thumbs.append(sheet)
mont=Image.new('RGB',(1200,175*11),'white')
for i,t in enumerate(thumbs): mont.paste(t,((i%2)*600,(i//2)*175))
mont.save(out/'production_node_source_montage.png')
print('F77 evidence crops and 22-node montage saved.')
