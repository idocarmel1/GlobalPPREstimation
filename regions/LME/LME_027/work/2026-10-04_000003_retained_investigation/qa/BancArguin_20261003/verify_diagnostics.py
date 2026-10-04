"""Independent reopened-array, scope, state, and flow reconciliation; no new solves."""
from pathlib import Path
import csv,hashlib,json,math
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
results=[]
for folder in ('Base_runtime_PQ_approximation','EcoBase689_native_companion'):
    out=HERE/'runtime'/folder;solutions=load(out/'direct_solutions.json');coeff=load(out/'group_coefficients.json');reports=load(out/'direct_reports.json');state=load(out/'loaded_state_before.json');after=load(out/'loaded_state_after.json')
    assert {k:v for k,v in state.items() if k!='detritus_resolution_info'}=={k:v for k,v in after.items() if k!='detritus_resolution_info'}
    checked=[]
    for method,bundle in solutions.items():
        for matrix,frame in bundle.items():
            assert frame['type']=='DataFrame';rows=frame['index'];cols=frame['columns'];data=frame['data']
            assert len(rows)==len(set(rows)) and len(cols)==len(set(cols))
            assert frame['shape']==[len(rows),len(cols)] and len(data)==len(rows)
            assert all(len(r)==len(cols) for r in data)
            assert all(isinstance(x,(int,float)) and math.isfinite(x) for r in data for x in r)
            for mask in ('null_mask','nan_mask','positive_infinity_mask','negative_infinity_mask'):assert frame[mask]==[[False]*len(cols) for _ in rows]
            checked.append({'method':method,'matrix':matrix,'shape':frame['shape'],'nonfinite':0,'negative':sum(x<0 for r in data for x in r)})
            if matrix=='SPPR':
                assert cols==[48,49,50,51,52] or set(cols)=={48,49,50,51,52}
                for r in [x for x in coeff if x['method']==method]:
                    ids=cols if r['scope']=='all' else [x for x in cols if x!=52 and (r['scope']!='PP' or x!=51)]
                    total=math.fsum(data[rows.index(r['group_seq'])][cols.index(j)] for j in ids)
                    assert math.isclose(total,r['sppr'],rel_tol=1e-12,abs_tol=1e-12)
                assert reports[method]['divergence']['n_negative_sources']==sum(any(row[j]<0 for row in data) for j in range(len(cols)))
    # Reconstruct diagnostic production/consumption identities independently from retained vectors.
    vector=lambda k:dict(zip(state[k]['index'],state[k]['data']))
    fields={k:vector(k) for k in ('p','q','catch','predation','growth','net_migration','M0','egestion','respiration')}
    flows=[]
    for i in fields['p']:
        p=math.fsum(fields[k][i] for k in ('catch','predation','growth','net_migration','M0'))
        q=math.fsum((p,fields['egestion'][i],fields['respiration'][i]))
        flows.append({'group_seq':i,**{k:v[i] for k,v in fields.items()},'production_identity':p,'consumption_identity':q,'production_residual':p-fields['p'][i],'consumption_residual':q-fields['q'][i],'production_relative_residual':abs(p-fields['p'][i])/max(abs(fields['p'][i]),1e-12),'consumption_relative_residual':abs(q-fields['q'][i])/max(abs(fields['q'][i]),1e-12)})
    for kind,field in [('p','production'),('q','consumption')]:
        mx=max(r[field+'_relative_residual'] for r in flows)
        for method,report in reports.items():assert math.isclose(mx,report['model_input'][kind+'_max_rel_residual'],rel_tol=1e-10,abs_tol=1e-10)
    with (out/'flow_residuals.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(flows[0]));w.writeheader();w.writerows(flows)
    result={'configuration':folder,'checked_matrices':checked,'coefficient_rows_reconciled':len(coeff),'all_scientific_state_unchanged':True,'source_sha256':load(out/'execution_evidence.json')['source_sha256'],'input_sha256':sha(out/'computational_input.json'),'solutions_sha256':sha(out/'direct_solutions.json'),'worst_production':max(flows,key=lambda r:r['production_relative_residual']),'worst_consumption':max(flows,key=lambda r:r['consumption_relative_residual']),'passed':True}
    results.append(result)
save(HERE/'qa/diagnostic_reconciliation.json',results)
print(json.dumps([{'configuration':r['configuration'],'matrices':len(r['checked_matrices']),'passed':r['passed']} for r in results]))
