import subprocess
from pathlib import Path
w=Path(r'C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/קוד/PPR_Ecopath_Atlas/archive/regions/LME_036/SCS-2007/extracted/work')
for p in [191,193,194,205,357,358,359,360,361,362,363]:
 subprocess.run(['python',r'C:/Users/idoca/.agents/skills/ecopath-extraction/scripts/render_pdf_page.py',str(w.parent.parent/'ubc_2007-317501-87ea9ea0.pdf'),str(p),'--dpi','200','--outdir',str(w)],capture_output=True,check=True)
 print(p,flush=True)
