from pathlib import Path
import json
import pdfplumber

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
PDF = ROOT / 'regions/LME_027/papers/FCRR_2009_17-2.pdf.pdf'
OUT.mkdir(parents=True, exist_ok=True)
with pdfplumber.open(PDF) as doc:
    for i in range(10, 56):
        p = doc.pages[i-1]
        (OUT / f'pdf_{i:03d}.txt').write_text(p.extract_text(x_tolerance=1) or '', encoding='utf-8')
        if i in [18, 19, 20, 38, 39, 40, 41, 42, 43]:
            words = p.extract_words(x_tolerance=0.4)
            (OUT / f'pdf_{i:03d}_words.json').write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding='utf-8')
    for i in [38, 39, 40, 41, 42, 43]:
        print(f'\nPDF PAGE {i}\n' + (OUT / f'pdf_{i:03d}.txt').read_text(encoding='utf-8'))
