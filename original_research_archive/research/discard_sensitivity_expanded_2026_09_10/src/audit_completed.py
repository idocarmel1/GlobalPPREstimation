"""Early independent numerical audit of completed models while later models run."""
from pathlib import Path
import json,numpy as np
from baseline import ROOT,METHODS,SCOPES,FRACTIONS
from summarize import finalize_model
from run_study import write_json
out=[]
timings=json.loads((ROOT/'verification/run_timings.json').read_text(encoding='utf-8'))
for timing in timings:
    mid=timing['model_id'];p=ROOT/'results/models'/mid/'study.json';s=finalize_model(json.loads(p.read_text(encoding='utf-8')))
    rr=s['records'];gg=s['groups'];lookup={(r['method'],r['scope'],r['route'],r['fraction']):r for r in rr};failures=[];n=0
    def arr(r):return np.array([g['sppr'] if g['sppr'] is not None else np.nan for g in gg.get(r['scenario_id'],[])])
    for method in METHODS:
        for scope in SCOPES:
            b=lookup[method,scope,'S0',0.];a=arr(b)
            for f in FRACTIONS:
                sc=lookup[method,scope,'SC',f];se=lookup[method,scope,'SE',f];x=arr(sc);y=arr(se);n+=1
                if a.shape!=x.shape or not np.allclose(a,x,rtol=2e-7,atol=1e-7,equal_nan=True):failures.append(sc['scenario_id']+' SC changed')
                if f<1 and (x.shape!=y.shape or not np.allclose(x,y,rtol=2e-7,atol=1e-7,equal_nan=True)):failures.append(se['scenario_id']+' SE differs')
            for route in ['SC','SM','SE']:
                r=lookup[method,scope,route,0.];x=arr(r)
                if a.shape!=x.shape or not np.allclose(a,x,rtol=2e-7,atol=1e-7,equal_nan=True):failures.append(r['scenario_id']+' zero fraction changed')
    for r in rr:
        if r['valid']:
            g=gg[r['scenario_id']];ppr=sum(v['sppr']*v['H']/9 for v in g if v['H']>0)
            if not np.isclose(ppr,r['ppr_fixed_H_tC'],rtol=1e-12,atol=1e-8):failures.append(r['scenario_id']+' fixed support total mismatch')
            if not np.isclose(r['ppr_retained_L_tC'],(1-r['fraction'])*ppr,rtol=1e-12,atol=1e-8):failures.append(r['scenario_id']+' retained total mismatch')
    out.append(dict(model_id=mid,passed=not failures,curve_checks=n,failures=failures));print(mid,'passed' if not failures else failures,flush=True)
write_json(ROOT/'verification/completed_model_early_checks.json',out)
if any(not r['passed'] for r in out):raise SystemExit(1)
