"""Independent comparison of every consolidated annual cell to the pre-migration export."""
import argparse,csv,json,math
from pathlib import Path
from workbooks import *

def verify(source,root):
    t=json.loads((source/'PPRAtlas/data/time_series.json').read_text());sel=json.loads((source/'data/atlas_selection.json').read_text())['units']
    p=read_book(root/'Project.xlsx');actual={tuple(r[:7]):r[8:] for r in rows(p,'Regional PPR','Annual')};checks=0
    def same(a,b,context):
        nonlocal checks
        if len(a)!=len(b):raise AssertionError((context,'length',len(a),len(b)))
        for x,y in zip(a,b):
            if x is None or y is None:
                if x!=y:raise AssertionError((context,x,y))
            elif not math.isclose(x,y,rel_tol=1e-14,abs_tol=1e-8):raise AssertionError((context,x,y))
            checks+=1
    for unit,u in t['units'].items():
        models=[('', 'all', SIMPLE,u['simple'])]
        chosen=sel.get(unit,{}).get('default_model')
        for m in u['models']:
            if m['id']==chosen:
                for scope,s in m.get('scopes',{}).items():
                    models.extend((chosen,scope,method,r) for method,r in s['methods'].items())
        for model,scope,method,r in models:
            for treatment in ['method','zero','simple']:
                v=r if treatment=='method' else r.get('unidentified_'+treatment)
                if v is None:continue
                for basis in ['landings','catch','discards']:
                    b=v if basis=='landings' else v.get('catch_bases',{}).get(basis,{})
                    for metric in ['ppr','catch','covered_catch']:
                        k=(unit,model or None,scope,method,basis,treatment,metric)
                        same(actual[k],b.get(metric,[None]*70),k)
    actualn={(r[0],r[1]):r[3:] for r in rows(p,'Regional NPP','NPP')}
    for unit,u in t['units'].items():
        for method,v in u.get('npp',{}).items():same(actualn[unit,method],v,(unit,method))
    kept=0
    ledger=root/'original_research_archive/migration.csv'
    if ledger.exists():
        for r in csv.DictReader(ledger.open()):
            path=root/r['retained_path']
            if not path.is_file() or sha(path)!=r['sha256']:raise AssertionError(f'Retention mismatch: {r["original_path"]}')
            kept+=1
    report={'annual_cells_compared':checks,'source_files_verified':kept,'regions':len(t['units']),'differences':0}
    print(json.dumps(report));return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--root',type=Path,required=True);a=ap.parse_args();report=verify(a.source,a.root)
    (a.root/'original_research_archive/numerical_verification.txt').write_text(json.dumps(report,indent=2))
