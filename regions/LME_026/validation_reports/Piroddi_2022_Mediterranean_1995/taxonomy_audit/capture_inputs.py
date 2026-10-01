from pathlib import Path
import sys, json, hashlib
from docx import Document

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / 'tools'))
import workbooks
OUT = Path(__file__).resolve().parent
REGION = ROOT / 'regions/LME_026'
book = workbooks.read_book(REGION / 'LME_026.xlsx')
snapshot = {s:{t:{'header':h,'rows':r} for t,(h,r) in ts.items()} for s,ts in book.items() if s in ['Overview','Catch','Classic PPR','Selected model groups','PPR']}
(OUT/'workbook_review_snapshot.json').write_text(json.dumps(snapshot,indent=2,ensure_ascii=True),encoding='utf-8')
source = REGION / 'papers/MED-2022/41598_2022_18017_MOESM2_ESM-7d26163a.docx'
doc = Document(source)
tables=[{'table_one_based':ti+1,'rows':[{'row_one_based':ri+1,'cells':[c.text for c in row.cells]} for ri,row in enumerate(t.rows)]} for ti,t in enumerate(doc.tables)]
(OUT/'source_docx_tables.json').write_text(json.dumps(tables,indent=2,ensure_ascii=True),encoding='utf-8')
tax=json.loads((REGION/'extraction_review_20260928/taxonomy_evidence.json').read_text(encoding='utf-8'))
(OUT/'source_group_definitions.json').write_text(json.dumps(tax,indent=2,ensure_ascii=True),encoding='utf-8')
print(json.dumps({'tables':{s:{t:{'rows':len(r),'header':h[:12]} for t,(h,r) in ts.items()} for s,ts in book.items()},'docx_tables':len(tables)},ensure_ascii=True))
for g in tax:
    if 10 <= int(g['group_seq']) <= 60: print(json.dumps(g,ensure_ascii=True))
