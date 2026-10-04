"""Preserve source bytes and expose the original Fig. 9 raster for auditing."""
from pathlib import Path
import hashlib, json, shutil
from datetime import datetime, timezone
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[4]
REGION = ROOT / 'regions/LME_052'
MODEL = Path(__file__).resolve().parent
SOURCES = REGION / 'papers/OKH-GM2019'
SEARCH = REGION / 'papers/alternative_model_search_20261002'
SOURCES.mkdir(parents=True, exist_ok=True)
(MODEL / 'audit').mkdir(exist_ok=True)
(MODEL / 'extracted_tables').mkdir(exist_ok=True)

items = [
 ('gorbatenko_melnikov_2019.pdf', SEARCH, 'primary article', 'https://izvestiya.tinro-center.ru/jour/article/download/497/467', '2000-2014 epipelagic network; Table 3 and Figure 9'),
 ('gorbatenko_levitskaya_2016_pollock.pdf', SEARCH, 'supporting feeding study', 'https://izvestiya.tinro-center.ru/jour/article/download/112/113', 'Pollock diets, rations and annual prey consumption'),
 ('gorbatenko_melnikov_2016_herring.pdf', SEARCH, 'supporting feeding study', 'https://izvestiya.tinro-center.ru/jour/article/download/111/112', 'Herring diets and annual prey consumption'),
 ('gorbatenko_2016_euphausiids.pdf', SEARCH, 'supporting feeding study', 'https://izvestiya.tinro-center.ru/jour/article/download/113/114', 'Euphausiid diets and annual prey consumption'),
 ('gorbatenko_2016_sagitta.pdf', SEARCH, 'supporting feeding study', 'https://izvestiya.tinro-center.ru/jour/article/download/86/87', 'Sagitta diets and annual prey consumption'),
 ('gorbatenko_2018_dissertation.pdf', REGION / 'papers/OKH-2015/online_recovery_20261002', 'supporting dissertation', 'http://www.imb.dvo.ru/misc/dissertations/images/dissertations/files/gorbatenko/Dissertation_Gorbatenko.pdf', 'Chapter 4 feeding; Chapter 8 epipelagic network and separate shelf-bottom network'),
]
manifest=[]
for filename, origin, role, url, contents in items:
 src=origin/filename; dst=SOURCES/filename
 shutil.copy2(src,dst)
 digest=hashlib.sha256(src.read_bytes()).hexdigest()
 assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
 txt=src.with_suffix('.pdf.txt')
 if txt.exists(): shutil.copy2(txt,SOURCES/txt.name)
 manifest.append(dict(file=filename,role=role,url=url,sha256=digest,bytes=dst.stat().st_size,pages=len(PdfReader(dst).pages),original_local_path=src.relative_to(ROOT).as_posix(),contents=contents))
for name in ['feeding_sources_manifest.json','gorbatenko2019_routes.json','alternative_model_assessment.txt','verification.json']:
 shutil.copy2(SEARCH/name,SOURCES/('discovery_'+name))
r=PdfReader(SOURCES/'gorbatenko_melnikov_2019.pdf')
im=list(r.pages[14].images)[0]
(MODEL/'audit/figure9_original.tif').write_bytes(im.data)
im.image.convert('RGB').save(MODEL/'audit/figure9_original.png')
manifest_data=dict(organized_utc=datetime.now(timezone.utc).isoformat(),note='Exact-byte copies of earlier recovered originals; source acquisition timestamps remain in discovery manifests. No content changes to original PDFs.',sources=manifest)
(SOURCES/'source_manifest.json').write_text(json.dumps(manifest_data,ensure_ascii=False,indent=2),encoding='utf-8')
(MODEL/'audit/source_inventory.json').write_text(json.dumps(manifest_data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(source_directory=str(SOURCES),model_directory=str(MODEL),source_count=len(manifest),figure_size=im.image.size),ensure_ascii=False))
