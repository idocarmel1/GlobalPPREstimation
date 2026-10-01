from pathlib import Path
import json,re
O=Path(__file__).resolve().parent
s=json.loads((O/'workbook_review_snapshot.json').read_text(encoding='utf-8'))
h=s['Catch']['Catch']['header'];rows=[dict(zip(h,r)) for r in s['Catch']['Catch']['rows']]
labels=sorted([r for r in rows if r['catch_basis']=='landings'],key=lambda r:r['taxon'])
tax=json.loads((O/'source_group_definitions.json').read_text(encoding='utf-8'))
members={}
for g in tax:
    d=g['description'].split(':',1)[-1]
    terms=re.findall(r'\b[A-Z][a-z]+\s+[a-z][a-z-]+(?:\s+[a-z]+)?',d)
    for t in terms: members.setdefault(t.strip(),[]).append(g['group_seq'])
unmatched=[]
for r in labels:
    key=r['taxon'];direct=members.get(key,[])
    if not direct:unmatched.append(r)
    r['direct_groups']=direct
(O/'catch_label_universe.json').write_text(json.dumps(labels,indent=2,ensure_ascii=True),encoding='utf-8')
print(json.dumps({'labels':len(labels),'direct':len(labels)-len(unmatched),'unmatched':len(unmatched)}))
for r in unmatched:
    print(json.dumps({'taxon':r['taxon'],'common':r['common_name'],'functional':r['functional_group'],'commercial':r['commercial_group'],'catch_2019':r['2019'] if '2019' in r else r[2019]},ensure_ascii=True))
print('GROUPS40-45')
for g in tax:
    if 40<=g['group_seq']<=45:print(json.dumps(g,ensure_ascii=True))
