"""Reload the previously authorized adapter state; retain fresh direct reports only."""
from pathlib import Path
import sys,json,pickle,hashlib,math,warnings
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'Project.xlsx').exists())
SOURCE=ROOT/'regions/LME_024/models/extraction_review_20260928/authorized_routing_experiment'
sys.path.insert(0,str(SOURCE))
from routing_adapter import PPRCalculator
def clean(v):
    if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [clean(x) for x in v]
    if isinstance(v,np.ndarray):return clean(v.tolist())
    if isinstance(v,np.generic):return clean(v.item())
    if isinstance(v,float) and not math.isfinite(v):return str(v)
    return v
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,v):(HERE/name).write_text(json.dumps(clean(v),indent=2,ensure_ascii=False),encoding='utf-8')
hashes=json.loads((SOURCE/'verification_final.json').read_text(encoding='utf-8'))['after_hashes']
for path,h in hashes.items():assert sha(ROOT/path)==h,path
artifact=json.loads((SOURCE/'artifact_hashes.json').read_text(encoding='utf-8'))
for name,h in artifact.items():assert sha(SOURCE/name)==h,name
reports={};rows=[];checks={}
for opt in ['GE','TE','With Egestion']:
    tag=opt.replace(' ','_')
    c=pickle.loads((SOURCE/'faithful_printed_BA_state.pkl').read_bytes())
    with warnings.catch_warnings(record=True) as w:
        r=PPRCalculator.diagnose_sppr(c,TE_option=opt,short=False,flat=False)
    old=json.loads((SOURCE/f'diagnose_{tag}_raw.json').read_text(encoding='utf-8'))
    assert clean(r)==old, opt+' retained direct return changed'
    reports[opt]=r
    if hasattr(c,'last_solve'):
        s,a,l=c.last_solve
        retained=pd.read_csv(SOURCE/f'{tag}_SPPR.csv',index_col=0);retained.columns=retained.columns.astype(int)
        np.testing.assert_allclose(s,retained.reindex(index=s.index,columns=s.columns),rtol=1e-12,atol=1e-9)
        s.to_csv(HERE/f'{tag}_SPPR.csv');checks[opt]='exact report and identity-aligned coefficients reproduced'
        for scope in ['all','inner','PP']:
            cols=[i for i in s.columns if scope=='all' or (i not in c.get_Import_seq() and (scope!='PP' or i not in c.get_DET_seq()))]
            for seq,val in s[cols].sum(axis=1,min_count=1).items():
                rows.append(dict(seq=int(seq),group=c.seq2name[seq],scope=scope,method={'GE':'new_GE','With Egestion':'new_WithEgestion'}[opt],sppr=float(val)))
    else:checks[opt]='unsupported return equation; no numerical coefficient invented'
dump('direct_reports.json',reports)
dump('execution_evidence.json',dict(retained_hashes_verified=True,checks=checks,retained_input_sha256=sha(SOURCE/'faithful_printed_BA_state.pkl'),input_provenance=str(SOURCE.relative_to(ROOT)),engine_hashes={k:v for k,v in hashes.items() if k.startswith('tools/')},adapter_sha256=sha(SOURCE/'routing_adapter.py')))
(HERE/'DIRECT_DIAGNOSTICS.md').write_text('# Full direct SPPR diagnostic returns\n\n'+'\n\n'.join('## '+k+'\n\n```json\n'+json.dumps(clean(v),indent=2,ensure_ascii=False)+'\n```' for k,v in reports.items()),encoding='utf-8')
pd.DataFrame(rows).to_csv(HERE/'direct_group_sppr.csv',index=False,encoding='utf-8')
groups=pd.read_csv(SOURCE/'faithful_printed_BA_groups.csv').rename(columns={'group_seq':'seq'})
groups.to_csv(HERE/'runtime_groups.csv',index=False,encoding='utf-8')
print({k:v['status'] for k,v in reports.items()})
