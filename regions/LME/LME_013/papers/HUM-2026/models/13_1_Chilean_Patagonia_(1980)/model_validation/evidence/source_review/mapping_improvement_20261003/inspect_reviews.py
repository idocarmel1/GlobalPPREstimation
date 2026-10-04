from pathlib import Path
import json,sys
sys.stdout.reconfigure(encoding='utf-8');OUT=Path(__file__).parent
baseline={r['taxon']:r for r in json.loads((OUT/'review_inputs.json').read_text(encoding='utf-8'))}
for p in OUT.glob('*_review.json'):
    d=json.loads(p.read_text(encoding='utf-8'));a=d.get('decisions',d.get('reviews',d.get('taxa',d.get('taxon_records',[])))) if isinstance(d,dict) else d
    rows=list(a.values()) if isinstance(a,dict) else a
    print(p.name,'top keys',list(d)[:25] if isinstance(d,dict) else 'list','rows',len(rows))
    if rows:print('row keys',list(rows[0]))
    for r in rows:
        t=r['taxon'];m=r.get('new_mappings',r.get('proposed_mappings',[]));old=baseline[t]['matching'];prior=baseline[t]['old_review']
        sig=lambda v:sorted((x.get('group',x.get('group_name')),round(x['weight'],12)) for x in v if x['weight']>0)
        nc=sig(m)!=sig(old);cc=any(r.get(k)!=prior[k] for k in ['membership_confidence','allocation_confidence','overall_confidence'])
        if nc or cc:print(json.dumps({'taxon':t,'numerical':nc,'components':[r.get(k) for k in ['membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence']],'prior':[prior[k] for k in ['membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence']],'new':[(v.get('group',v.get('group_name')),v['weight']) for v in m]},ensure_ascii=False))
