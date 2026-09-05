from pathlib import Path
import sys,json,re,subprocess
sys.path.insert(0,r'C:\Users\idoca\.agents\skills\ecopath-extraction\scripts')
from pdfgrid import get_words,build_grid
folder=Path(__file__).parents[2]; work=folder/'extracted'/'work'; pdf=next(folder.glob('*.pdf'))
basic=get_words(str(pdf),6,merge_gap=2.0)
diet=get_words(str(pdf),7,merge_gap=0.4)
for line in basic:
 if 593<line.y<731: print([(c.text,round(c.x0,1),round(c.x1,1)) for c in line.cells])
grid=build_grid(diet,anchor_line=4)
(work/'diet-grid.json').write_text(json.dumps(grid,indent=2,ensure_ascii=False),encoding='utf-8')
print('DIET GRID',json.dumps(grid[4:22],ensure_ascii=False))
