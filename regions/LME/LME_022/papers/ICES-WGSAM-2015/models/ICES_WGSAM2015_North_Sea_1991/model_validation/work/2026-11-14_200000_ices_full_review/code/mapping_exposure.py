"""Report-only exposure of proposed mapping uncertainty to saved coefficients."""
from pathlib import Path
import json,gzip,math,hashlib
RUN=Path(__file__).resolve().parents[1];BASE=RUN.parents[1]
src=BASE/'evidence/mapping/mapping_decisions.json'
d=json.loads(src.read_text(encoding='utf8'));rows=d['rows']
result={'scope':'Report-only arithmetic on proposed mapping and retained all-source coefficients; not adopted regional PPR and not a fresh SPPR run','year':2019,'basis':'catch','mapping_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'methods':[]}
for method in ['new_GE','new_TE_EEfix','new_WithEgestion']:
    file=BASE.parent/'results/diagnostics/2026-11-14_loader_repair'/f'{method}.json.gz'
    run=json.loads(gzip.decompress(file.read_bytes()));coefs=run['scopes']['all']
    taxon=[]
    for r in rows:
        if r['catch_tonnes']==0:value=0.0
        elif r['overall_confidence']=='Unresolved':value=None
        else:
            coefficient=math.fsum(g['weight']*coefs[g['group_name']] for g in r['groups'] if g['weight'])
            value=r['catch_tonnes']*coefficient/9
        taxon.append({'taxon':r['taxon'],'confidence':r['overall_confidence'],'proposed_ppr_tC':value,'allocation_assumed':r['assumptions']['allocation_assumed']})
    total=math.fsum(t['proposed_ppr_tC'] for t in taxon if t['proposed_ppr_tC'] is not None)
    shares={level:100*math.fsum(t['proposed_ppr_tC'] or 0 for t in taxon if t['confidence']==level)/total for level in ['High','Medium','Low','Very low','Unresolved']}
    result['methods'].append({'method':method,'status':run['status'],'saved_source_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'proposed_total_tC':total,'confidence_ppr_shares':shares,'top_very_low_contributions':sorted([dict(t,method_ppr_share=100*(t['proposed_ppr_tC'] or 0)/total) for t in taxon if t['confidence']=='Very low'],key=lambda t:-(t['proposed_ppr_tC'] or 0))[:10]})
(RUN/'qa/proposed_mapping_method_exposure.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'mapping_sha256':result['mapping_sha256'],'method_confidence_shares':[{m['method']:m['confidence_ppr_shares']} for m in result['methods']]},indent=2))
