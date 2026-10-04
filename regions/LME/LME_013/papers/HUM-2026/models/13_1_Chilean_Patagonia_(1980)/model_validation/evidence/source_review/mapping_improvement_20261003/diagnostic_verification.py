from pathlib import Path
import json,sys,math,hashlib
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).parent;REG=OUT.parents[2]
def decode(v):
    if isinstance(v,list):return [decode(x) for x in v]
    if not isinstance(v,dict):return v
    if v.get('type')=='dict':return {decode(k):decode(x) for k,x in v['items']}
    if v.get('type')=='tuple':return tuple(decode(x) for x in v['values'])
    return v
b=json.loads((OUT/'baseline_tables.json').read_text(encoding='utf-8'))
h,rr=b['Selected model groups']['Groups'];groups={r[h.index('seq')]:r[h.index('group_name')] for r in rr}
sp_h,sp_rows=b['Selected model groups']['Group SPPR'];sp={(r[sp_h.index('group')],r[sp_h.index('scope')],r[sp_h.index('method')]):r[sp_h.index('sppr')] for r in sp_rows}
result=[]
for suffix,method in [('GE','new_GE'),('TE_EEfix','new_TE_EEfix'),('WithEgestion','new_WithEgestion')]:
    p=REG/'models/regional_ge_integration_20260928'/('direct_new_'+suffix+'.json')
    raw=json.loads(p.read_text(encoding='utf-8'));diag=decode(raw['values'][0]);m=raw['values'][1]
    assert m['type']=='DataFrame' and len(m['index'])==len(set(m['index']))==16
    assert len(m['columns'])==len(set(m['columns']))==3
    assert all(len(row)==3 for row in m['values'])
    negative=[];nonfinite=[];comparisons=[]
    for rid,vs in zip(m['index'],m['values']):
        for cid,v in zip(m['columns'],vs):
            if not isinstance(v,(int,float)) or not math.isfinite(v):nonfinite.append([rid,cid,v])
            elif v<0:negative.append({'group_id':rid,'group_name':groups[rid],'source_id':cid,'source_name':groups[cid],'value':v})
        scopes={'all':math.fsum(vs),'PP':vs[m['columns'].index(1)],'inner':math.fsum(v for cid,v in zip(m['columns'],vs) if cid!=16)}
        for scope,v in scopes.items():
            saved=sp.get((groups[rid],scope,method))
            if saved is not None:comparisons.append({'group':groups[rid],'scope':scope,'saved':saved,'matrix_sum':v,'absolute_difference':abs(saved-v),'matches':math.isclose(saved,v,rel_tol=1e-12,abs_tol=1e-9)})
    assert not nonfinite
    assert all(r['matches'] for r in comparisons)
    result.append({'method':method,'retained_return':p.relative_to(OUT).as_posix() if p.is_relative_to(OUT) else '../../../models/regional_ge_integration_20260928/'+p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actual_status':diag['status'],'configuration':diag['config'],'diagnosis':diag,'row_ids':m['index'],'row_names':[groups[i] for i in m['index']],'source_ids':m['columns'],'source_names':[groups[i] for i in m['columns']],'negative_entries':negative,'nonfinite_entries':nonfinite,'scope_coefficients_reconciled':comparisons,'fresh_solver':False})
(OUT/'diagnostic_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'method':r['method'],'status':r['actual_status'],'negative_entries':len(r['negative_entries']),'nonfinite_entries':len(r['nonfinite_entries']),'scope_comparisons':len(r['scope_coefficients_reconciled'])} for r in result],indent=2))
