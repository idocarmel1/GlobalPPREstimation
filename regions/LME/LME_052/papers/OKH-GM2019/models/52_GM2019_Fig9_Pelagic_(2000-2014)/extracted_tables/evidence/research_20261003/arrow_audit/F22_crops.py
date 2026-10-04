from pathlib import Path
from PIL import Image
import numpy as np
base=Path(r'C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\GlobalPPREstimation\regions\LME_052\models\52_GM2019_Fig9_Pelagic_(2000-2014)');out=base/'research_20261003'/'arrow_audit';im=Image.open(base/'audit'/'figure9_original.png').convert('RGB');a=np.asarray(im)
blue=(a[:,:,2]>170)&(a[:,:,0]<120)&(a[:,:,1]>80)&(a[:,:,1]<210);black=a.max(axis=2)<130
b=np.ones(a.shape,dtype=np.uint8)*255;b[blue|black]=a[blue|black]
bi=Image.fromarray(b)
for name,box in {'F22_entire_route':(540,400,1318,1340),'jellyfish_blue_incoming_check':(800,740,1318,1020),'F22_whale_endpoint':(710,1200,960,1340)}.items():
 im.crop(box).save(out/(name+'_source_native.png'));im.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2),Image.Resampling.NEAREST).save(out/(name+'_source_x2.png'))
 bi.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2),Image.Resampling.NEAREST).save(out/(name+'_blue_reading_aid_x2.png'))
