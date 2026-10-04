from pathlib import Path
from PIL import Image
base=Path(r'C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\GlobalPPREstimation\regions\LME_052\models\52_GM2019_Fig9_Pelagic_(2000-2014)')
out=base/'research_20261003'/'arrow_audit';im=Image.open(base/'audit'/'figure9_original.png')
for name,box in {'F41_F42_origins':(90,750,340,1165),'F52_F57_origins':(380,880,960,1165),'F62_label':(190,1255,310,1330),'F67_label':(1140,1160,1280,1240),'F24_endpoint':(910,780,1020,930)}.items():
 im.crop(box).resize(((box[2]-box[0])*4,(box[3]-box[1])*4)).save(out/(name+'_source_x4.png'))
