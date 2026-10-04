from pathlib import Path
from PIL import Image
base=Path(r'C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\GlobalPPREstimation\regions\LME_052\models\52_GM2019_Fig9_Pelagic_(2000-2014)');out=base/'research_20261003'/'arrow_audit';im=Image.open(base/'audit'/'figure9_original.png')
for name,box in {'F78_label_and_heads':(470,1370,650,1495),'F78_continuation':(510,1400,1045,1580)}.items():
 im.crop(box).save(out/(name+'_source_native.png'));im.crop(box).resize(((box[2]-box[0])*4,(box[3]-box[1])*4),Image.Resampling.NEAREST).save(out/(name+'_source_x4.png'))
