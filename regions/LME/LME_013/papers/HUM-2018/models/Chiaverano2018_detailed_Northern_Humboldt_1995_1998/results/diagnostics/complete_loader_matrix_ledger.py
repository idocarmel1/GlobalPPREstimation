"""Complete source-input to loader/runtime matrix ledger from retained files."""
from pathlib import Path
import csv,json,math
HERE=Path(__file__).resolve().parent
model=json.loads((HERE/'computational_input_exact.json').read_text(encoding='utf-8'))
groups={int(g['group_seq']):g for g in model['group']}
def read_matrix(path):
    with path.open(encoding='utf-8',newline='') as f:
        reader=csv.DictReader(f);index_field=reader.fieldnames[0];rs=list(reader)
    return {int(r[index_field]):{int(k):float(v) for k,v in r.items() if k!=index_field} for r in rs}
raw_dc=read_matrix(HERE/'raw_loader_diet.csv')
runtime_dc=read_matrix(HERE/'runtime_diet.csv')
fate=read_matrix(HERE/'loader_detritus_fate.csv')
names={i:g['group_name'] for i,g in groups.items()};names[40]='diet_import'
rows=[]
for i,cols in raw_dc.items():
    diet={int(float(d['prey_seq'])):d for d in groups.get(i,{}).get('diet_descr',{}).get('diet',[])}
    for j,loaded in cols.items():
        source=groups.get(i,{}).get('diet_imp') if j==40 and i in groups else diet.get(j,{}).get('proportion')
        raw=float(source) if source is not None and source!='-9999' else None
        runtime=runtime_dc[i][j]
        rows.append({'matrix':'diet','row_consumer_id':i,'row_name':names[i],'column_prey_id':j,'column_name':names[j],
           'input_literal':source,'input_numeric':raw,'loader_value':loaded,'runtime_value':runtime,
           'input_to_loader_changed':raw!=loaded,'loader_to_runtime_changed':loaded!=runtime,
           'reason':'Synthetic import row structural zero' if i==40 else ('Synthetic import prey column from source diet_imp' if j==40 else 'Exact source diet literal; runtime normalization changes separately recorded')})
for i,cols in fate.items():
    diet={int(float(d['prey_seq'])):d for d in groups.get(i,{}).get('diet_descr',{}).get('diet',[])}
    for j,loaded in cols.items():
        source=diet.get(j,{}).get('detritus_fate')
        raw=float(source) if source is not None and source!='-9999' else None
        rows.append({'matrix':'detritus_fate','row_consumer_id':i,'row_name':names[i],'column_prey_id':j,'column_name':names[j],
           'input_literal':source,'input_numeric':raw,'loader_value':loaded,'runtime_value':loaded,
           'input_to_loader_changed':raw!=loaded,'loader_to_runtime_changed':False,
           'reason':'ModelData._finalize_det_fate forces the detritus self-identity block' if i in (36,37,38,39) else
                    ('Synthetic import row routes no natural detrital flow' if i==40 else 'Exact native natural mortality/egestion routing')})
out={'schema_version':1,'orientation':{'diet':'row consumer, column prey','detritus_fate':'row donor, column detritus pool'},
     'entries':rows,'input_to_loader_changed_cells':sum(r['input_to_loader_changed'] for r in rows),
     'loader_to_runtime_changed_cells':sum(r['loader_to_runtime_changed'] for r in rows),
     'native_fleet_nodes':{'40':'Artisanal fisheries','41':'Commercial fisheries'},
     'runtime_synthetic_nodes':{'40':'diet_import'},
     'identity_namespace_note':'Native fleet IDs40/41 are not stock IDs. Runtime synthetic40 does not represent native fleet40.',
     'physical_limitation':'Source fleet discard routing and donor ancestry retained separately; not implemented in calculator recycling matrix.'}
(HERE/'loader_matrix_field_ledger.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k.endswith('_cells')}))
