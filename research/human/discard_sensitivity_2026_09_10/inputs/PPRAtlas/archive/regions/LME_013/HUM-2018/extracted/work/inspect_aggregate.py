import sys,json
from pathlib import Path
sys.path.insert(0,r'C:\Users\idoca\.agents\skills\ecopath-extraction\scripts')
from pdfgrid import get_words
p=next(Path(__file__).parents[2].glob('*.pdf'))
for line in get_words(str(p),4,merge_gap=2):
 if 80<line.y<138:print(line.y,[(c.text,round(c.x0,1),round(c.x1,1)) for c in line.cells])

