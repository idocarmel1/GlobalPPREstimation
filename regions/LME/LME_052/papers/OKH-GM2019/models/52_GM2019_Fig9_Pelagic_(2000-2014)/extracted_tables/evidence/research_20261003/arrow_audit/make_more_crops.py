from pathlib import Path
from PIL import Image
base=Path(r'C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\GlobalPPREstimation\regions\LME_052\models\52_GM2019_Fig9_Pelagic_(2000-2014)')
out=base/'research_20261003'/'arrow_audit'
im=Image.open(base/'audit'/'figure9_red_analysis.png')
for name,box in {'upper_left':(100,600,800,900),'upper_right':(650,600,1318,960),'middle_left':(90,820,760,1200),'middle_right':(640,820,1318,1220),'lower_left':(85,1080,750,1520),'lower_right':(670,1000,1318,1550)}.items():
 im.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2)).save(out/(name+'_red_x2.png'))
