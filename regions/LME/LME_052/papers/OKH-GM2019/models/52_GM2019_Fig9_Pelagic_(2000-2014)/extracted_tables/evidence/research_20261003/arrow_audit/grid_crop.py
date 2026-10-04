from pathlib import Path
from PIL import Image, ImageDraw
base=Path(r'C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\GlobalPPREstimation\regions\LME_052\models\52_GM2019_Fig9_Pelagic_(2000-2014)');out=base/'research_20261003'/'arrow_audit';im=Image.open(base/'audit'/'figure9_red_analysis.png')
d=ImageDraw.Draw(im)
for x in range(600,1318,50): d.line([(x,600),(x,1550)],fill=(180,180,180),width=1);d.text((x+2,940),str(x),fill=(60,60,60))
for y in range(600,1550,50): d.line([(600,y),(1318,y)],fill=(180,180,180),width=1);d.text((1260,y+2),str(y),fill=(60,60,60))
im.crop((600,650,1318,1160)).resize((1436,1020)).save(out/'upper_right_red_grid_x2.png')
