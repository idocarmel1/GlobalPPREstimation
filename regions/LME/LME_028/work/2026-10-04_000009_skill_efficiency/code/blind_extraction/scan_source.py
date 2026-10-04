from pathlib import Path
import datetime, hashlib, json, re, sys
import fitz

ROOT = Path(__file__).resolve().parents[7]
RUN = ROOT / 'regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency'
PDF = RUN / 'inputs/blind_extraction/original_publication.pdf'
OUT = RUN / 'outputs/blind_extraction'
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'evidence').mkdir(exist_ok=True)
doc = fitz.open(PDF)
pages = [{ 'pdf_page': i+1, 'text': p.get_text()} for i,p in enumerate(doc)]
(OUT / 'evidence/source_text.json').write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf-8')
receipt = {'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source': str(PDF.relative_to(ROOT)), 'sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(), 'bytes': PDF.stat().st_size, 'pages': len(doc), 'metadata': doc.metadata, 'exclusions': 'No retained model JSON, extracted tables, native model answers, SPPR sources, model notes, review findings, other trial output or regional/Project workbook read, hashed or copied. No graph retrieval.'}
(OUT / 'evidence/source_identity.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
for p in pages:
    if re.search(r'appendix\s*6\.[12]|1970s|2000s|Northern South China', p['text'], re.I):
        hits = [line for line in p['text'].splitlines() if re.search(r'appendix\s*6\.[12]|1970s|2000s|Northern South China', line, re.I)]
        print(p['pdf_page'], ' | '.join(hits))
print(json.dumps(receipt, ensure_ascii=False))
