from pathlib import Path
import sys,json
sys.path.insert(0,r'C:/Users/idoca/.agents/skills/ecopath-extraction/scripts')
from pdfgrid import get_words
root=Path(r'C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/קוד/PPR_Ecopath_Atlas/archive/regions/LME_036/SCS-2007')
work=root/'extracted/work'
pages=(work/'thesis.txt').read_text(encoding='utf-8').split('\f')
for a,b,name in [(183,218,'chapter6'),(337,356,'appendix61')]:
 (work/f'{name}.txt').write_text('\n'.join(f'\nPDF PAGE {i} (printed {i-15})\n'+pages[i-1] for i in range(a,b+1)),encoding='utf-8')
for n in [190,191,193,194,357,358,359,360,361,362,363]:
 lines=get_words(str(root/'ubc_2007-317501-87ea9ea0.pdf'),n,merge_gap=0.4)
 (work/f'grid-{n}.json').write_text(json.dumps([[vars(c) for c in l.cells] for l in lines]),encoding='utf-8')
 (work/f'raw-{n}.txt').write_text('\n'.join(f'[{i}] y={l.cells[0].yc:.1f} '+ ' | '.join(c.text for c in l.cells) for i,l in enumerate(lines)),encoding='utf-8')
 print(n,flush=True)
