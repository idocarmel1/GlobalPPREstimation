from pathlib import Path
from PIL import Image
base=Path(r'C:\Users\idoca\Desktop\אישי\אקדמיה\תואר שני\מחקר\BTN\GlobalPPREstimation\regions\LME_052\models\52_GM2019_Fig9_Pelagic_(2000-2014)')
out=base/'research_20261003'/'arrow_audit';im=Image.open(base/'audit'/'figure9_original.png')
im.crop((110,930,230,1110)).resize((960,1440),resample=Image.Resampling.NEAREST).save(out/'F41_F42_pixel_nearest.png')
