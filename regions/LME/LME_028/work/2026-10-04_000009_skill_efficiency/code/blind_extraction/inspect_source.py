from pathlib import Path
import json, sys, subprocess, datetime, re
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[7]
RUN=ROOT/'regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency'
OUT=RUN/'outputs/blind_extraction'
PDF=RUN/'inputs/blind_extraction/original_publication.pdf'
SCRIPTS=ROOT/'tools/skills/paper-to-ppr/resources/extraction/scripts'
sys.path.insert(0,str(SCRIPTS))
from pdfgrid import get_words
doc=fitz.open(PDF)
pages=[185,193,194,197,199,205,345,*range(357,364)]
for n in pages:
    pix=doc[n-1].get_pixmap(matrix=fitz.Matrix(200/72,200/72))
    pix.save(OUT/'evidence/source_pages'/f'original_publication_page_{n}_200dpi.png')
for n in [191,193,194,197,199,205,345,*range(357,364)]:
    lines=get_words(str(PDF),n,merge_gap=.4)
    payload=[{'line':i,'y':l.y,'cells':[{'text':w.text,'bbox':[w.x0,w.y0,w.x1,w.y1]} for w in l.cells]} for i,l in enumerate(lines)]
    (OUT/'evidence'/f'page_{n}_coordinates.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PAGE',n)
    for i,l in enumerate(lines):
        if n in [191,193,194,197,199,205] and i>5:continue
        print(i,round(l.y,1),' | '.join(f'{w.text} [{w.x0:.1f},{w.x1:.1f}]' for w in l.cells))
for label,args in [('chapter_pointers',['--pages','185-225','--family','pointers']),('chapter_numeric',['--pages','185-225','--numbers-only']),('appendix_numeric',['--pages','337-363','--numbers-only']),('blank_field_sweep',['--pages','1-369','--family','assimilation,accumulation,detritus','--context','1'])]:
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    p=subprocess.run([sys.executable,str(SCRIPTS/'prose_sweep.py'),str(PDF),*args],capture_output=True)
    (OUT/'evidence'/f'{label}.txt').write_bytes(p.stdout+p.stderr)
    print('sweep',label,'return',p.returncode,'start',start,'bytes',len(p.stdout+p.stderr))
