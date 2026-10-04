from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, json, runpy
base=Path(r'C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\GlobalPPREstimation\regions\LME_052\models\52_GM2019_Fig9_Pelagic_(2000-2014)')
out=base/'research_20261003'/'arrow_audit'
im=Image.open(base/'audit'/'figure9_original.png').convert('RGB')
boxes={'upper_arcs':(100,590,1300,960),'left_lower':(85,890,700,1460),'right_lower':(670,770,1318,1627),'F62_literal':(170,1230,340,1325),'F67_literal':(1130,1140,1290,1250),'large_pollock_node':(100,1360,400,1450)}
a=np.asarray(im)
red=(a[:,:,0]>170)&(a[:,:,1]<120)&(a[:,:,2]<150)
redim=np.ones(a.shape,dtype=np.uint8)*255
redim[red]=a[red]
# Retain black label pixels and node text as source context in red-only aid.
black=(a.max(axis=2)<130)
redim[black]=a[black]
rim=Image.fromarray(redim)
for name,box in boxes.items():
 im.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3)).save(out/(name+'_source_x3.png'))
 rim.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3)).save(out/(name+'_red_x3.png'))
# Coordinates only; this is a reading aid, not source reconstruction.
over=im.copy(); d=ImageDraw.Draw(over)
for x in range(0,1318,100): d.line([(x,0),(x,1627)],fill=(140,140,140),width=1); d.text((x+2,220),str(x),fill=(80,80,80))
for y in range(500,1627,100): d.line([(0,y),(1318,y)],fill=(140,140,140),width=1); d.text((5,y+2),str(y),fill=(80,80,80))
over.save(out/'coordinate_grid.png')
print(out)
