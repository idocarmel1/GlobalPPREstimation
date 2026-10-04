import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,records,overview,sha,digest_tables
book=read_book(Path(__file__).with_name('EEZ_941.xlsx'))
print('OVERVIEW',json.dumps(overview(book),ensure_ascii=False))
print('TABLES',json.dumps({s:{t:[len(h),len(r),h[:20]] for t,(h,r) in b.items()} for s,b in book.items()},ensure_ascii=False))
catch=records(book,'Catch','Catch'); classic={r['taxon']:r for r in records(book,'Classic PPR','Taxa')}
matching=records(book,'PPR','Matching')
for r in catch:
 if r['catch_basis']=='landings':
  print('TAXON',json.dumps({k:r.get(k) for k in ['taxon','common_name','functional_group','commercial_group','unidentified',2019]},ensure_ascii=False),json.dumps(classic.get(r['taxon']),ensure_ascii=False),json.dumps([x for x in matching if x['taxon']==r['taxon']],ensure_ascii=False))
for r in records(book,'Selected model groups','Groups'):print('GROUP',json.dumps(r,ensure_ascii=False))
for r in records(book,'PPR','Allocation assumptions'): print('ALLOC',json.dumps(r,ensure_ascii=False))
for name,(header,rows) in book.get('Diagnostics',{}).items():
 if name not in ['Size allocation impact']:print('DIAG',name,json.dumps(header),json.dumps(rows))
