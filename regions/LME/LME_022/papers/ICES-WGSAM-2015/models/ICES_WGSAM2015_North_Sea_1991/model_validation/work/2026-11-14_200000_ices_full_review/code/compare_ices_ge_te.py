"""Read-only source inputs; arithmetic comparison of retained ICES GE/TE coefficients."""
from pathlib import Path
import json, gzip, hashlib, math

RUN = Path(__file__).resolve().parents[1]
BASE = RUN.parents[1]
ROOT = next(p for p in RUN.parents if (p / 'Project.xlsx').exists())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
mapping_path = BASE / 'evidence/mapping/mapping_decisions.json'
mapping = json.loads(mapping_path.read_text(encoding='utf8'))
rows = mapping['rows']
assert len(rows) == len({r['taxon'] for r in rows}) == 384
for rel, expected in mapping['input_sha256'].items():
    assert sha(ROOT / rel) == expected, rel
inputs = {str(mapping_path.relative_to(ROOT)).replace('\\','/'):sha(mapping_path)}
result = {'purpose':'Requested recommendation and GE/TE PPR comparison; report arithmetic only',
    'year':2019,'catch_basis':'catch (landings plus discards)', 'unidentified_treatment':'method',
    'units':'tonnes carbon per year','conversion':'catch tonnes times weighted saved SPPR divided by 9 once',
    'adoption':'Proposed mappings remain unadopted; no selection, workbook or scientific-engine changes',
    'catch_tonnes':math.fsum(r['catch_tonnes'] for r in rows),'methods':{},'input_sha256':inputs}
for method in ['new_GE','new_TE_EEfix']:
    p = BASE.parent / 'results/diagnostics/2026-11-14_loader_repair' / (method+'.json.gz')
    inputs[p.relative_to(ROOT).as_posix()] = sha(p)
    saved = json.loads(gzip.decompress(p.read_bytes()))
    record = {'status':saved['status'],'scopes':{}}
    for scope, coefficients in saved['scopes'].items():
        taxa=[]; contributions={}
        for row in rows:
            assert math.isclose(math.fsum(g['weight'] for g in row['groups']),1,abs_tol=1e-9)
            pairs=[]
            for g in row['groups']:
                if not g['weight'] or not row['catch_tonnes']:
                    value=0.0
                else:
                    coefficient=coefficients[g['group_name']]
                    assert isinstance(coefficient,(int,float)) and math.isfinite(coefficient) and coefficient>=0
                    value=row['catch_tonnes']*g['weight']*coefficient/9
                pairs.append(value)
                contributions.setdefault(g['group_name'],[]).append(value)
            taxa.append({'taxon':row['taxon'],'catch_tonnes':row['catch_tonnes'],
                         'ppr_tC':math.fsum(pairs),'confidence':row['overall_confidence']})
        total=math.fsum(t['ppr_tC'] for t in taxa)
        groups=[{'group':g,'ppr_tC':math.fsum(v)} for g,v in contributions.items()]
        assert math.isclose(math.fsum(g['ppr_tC'] for g in groups),total,rel_tol=1e-12)
        record['scopes'][scope]={'total_tC':total,'taxa':taxa,
           'top_taxa':sorted(taxa,key=lambda t:-t['ppr_tC'])[:12],
           'top_groups':sorted(groups,key=lambda g:-g['ppr_tC'])[:12],
           'confidence_share_pct':{c:100*math.fsum(t['ppr_tC'] for t in taxa if t['confidence']==c)/total
              for c in ['High','Medium','Low','Very low','Unresolved']}}
    result['methods'][method]=record
for rel, expected in inputs.items(): assert sha(ROOT/rel)==expected
out=RUN/'qa/ices_ge_te_comparison.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'catch_tonnes':result['catch_tonnes'],'totals_tC':{m:{s:v['total_tC'] for s,v in d['scopes'].items()} for m,d in result['methods'].items()}},indent=2))
