from pathlib import Path
from decimal import Decimal
import json, hashlib
OUT=Path(__file__).resolve().parent
CAND=OUT.parents[1]
source=json.loads((OUT/'extraction.json').read_text(encoding='utf-8'))
nativepath=CAND/'evidence/identity/ecobase118_official_native.json'
native=json.loads(nativepath.read_text(encoding='utf-8'))['group_descr']['group']
byname={g['group_name'].lower().replace(' ',''):g for g in native}
byid={g['group_seq']:g for g in native}
crosswalk={}
for g in source['groups']:
    name=g['name'].lower().replace(' ','')
    if name=='baleenwhales' and name not in byname: name='bluewhales'
    if name=='bathydeersalpredators' and name not in byname: name='bathydemersalpredators'
    if name not in byname:
        candidates=[x for x in native if int(x['group_seq'])==g['n'] and g['n']>10]
        assert len(candidates)==1,(name,list(byname))
        target=candidates[0]
    else:target=byname[name]
    crosswalk[str(g['n'])]=target['group_seq']
assert len(set(crosswalk.values()))==27
rows=[]
for s_id,d in source['diet'].items():
    if s_id=='25':continue
    ng=byid[crosswalk[s_id]]
    entries=(ng.get('diet_descr') or {}).get('diet') or []
    if isinstance(entries,dict):entries=[entries]
    nd={e['prey_seq']:Decimal(e['proportion']) for e in entries}
    for prey in [str(i) for i in range(1,28)]+['import']:
        source_literal=d.get(prey)
        actual=Decimal(ng['diet_imp']) if prey=='import' else nd.get(crosswalk[prey],Decimal(0))
        expected=Decimal(source_literal) if source_literal is not None else Decimal(0)
        printed_zero=source_literal=='0.000'
        tolerance=Decimal('0.0005') if source_literal is not None and prey!='import' or source_literal and '.' in source_literal else Decimal(0)
        same=abs(actual-expected)<=tolerance
        rows.append({'source_predator_id':int(s_id),'source_prey_id':prey,'native_predator_id':crosswalk[s_id],'native_prey_id':crosswalk[prey] if prey!='import' else 'import','source_literal':source_literal,'native_literal':str(actual),'difference_native_minus_paper':str(actual-expected),'printed_precision_tolerance':str(tolerance),'consistent_at_printed_precision':same,'source_cell_status':'printed_zero' if printed_zero else 'printed_value' if source_literal is not None else 'blank_structural_zero'})
report={'native_sha256':hashlib.sha256(nativepath.read_bytes()).hexdigest(),'source_to_native_group_id':crosswalk,'comparison_count':len(rows),'inconsistent_count':sum(not r['consistent_at_printed_precision'] for r in rows),'inconsistencies':[r for r in rows if not r['consistent_at_printed_precision']],'rows':rows,'missing_source_zooplankton_diet':{'native_group_id':crosswalk['25'],'native_diet':byid[crosswalk['25']]['diet_descr'],'adopted_to_paper_canonical':False},'restriction':'Matching rounded signatures establishes strong same-lineage evidence, not author-confirmed identity or permission to fill source unknowns.'}
(OUT/'paper_native_diet_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['rows']},ensure_ascii=False,indent=2))
