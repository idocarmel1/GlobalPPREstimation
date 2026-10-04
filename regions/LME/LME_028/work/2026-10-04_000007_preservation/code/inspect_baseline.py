import json, gzip, csv, sys
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
q=root/'regions/LME_028/work/2026-10-04_000002_reorganization/qa'
with gzip.open(q/'workbooks.json.gz','rt',encoding='utf8') as f: books=json.load(f)
print('books',len(books),list(books)[:3],flush=True)
b=next(iter(books.values()))
print('book keys',list(b),flush=True)
for k,v in b.items():
 print(k,type(v).__name__,len(v) if hasattr(v,'__len__') else None,flush=True)
 if isinstance(v,dict): print('first',next(iter(v.items())),flush=True)
print('central',list(books['Project.xlsx']),flush=True)
