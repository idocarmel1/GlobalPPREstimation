from pathlib import Path
import csv,gzip,hashlib,importlib.util,json,os,sys

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
BASE=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
spec=importlib.util.spec_from_file_location('evidence_checker',ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
summaries=[];verifications={}
for entry in read(BASE/'inputs/models.json'):
    w=ROOT/entry['work'];cfg=read(w/'inputs/configuration.json');qa=read(w/'qa/ee_floor_checks.json')
    rows=read(w/'outputs/ee_floor_summary.json')
    assert len(rows)==3 and all(r['status']=='computed_sensitivity' for r in rows)
    assert all(sha(ROOT/p)==h for p,h in cfg['protected_hashes'].items())
    index=w/'qa/evidence_index.json';data=read(index)
    def add(role,p):
        artifact={'role':role,'path':Path(os.path.relpath(p,index.parent)).as_posix(),'sha256':sha(p),'availability':'present'}
        data['artifacts']=[a for a in data['artifacts'] if a['role']!=role]+[artifact]
        if role not in data['required_roles']:data['required_roles'].append(role)
    for role,p in [('ee_floor_code',BASE/'code/test_ee_floor.py'),('ee_floor_summary',w/'outputs/ee_floor_summary.json'),
                   ('ee_floor_groups',w/'outputs/ee_floor_groups.csv'),('ee_floor_checks',w/'qa/ee_floor_checks.json')]:add(role,p)
    summary={'unit_id':entry['unit_id'],'affected_groups':len(qa['affected_group_ids'])}
    for row in rows:
        option=row['method'];out=w/'outputs/ee_floor_0p1'/option.replace(' ','_')
        summary[option+'_PPR_percent_change']=row['percent_change_from_baseline']
        summary[option+'_extended_PP_gap']=row['relative_pp_budget_gap_with_external_sink']
        summary[option+'_PPR_tC']=row['landings_2019_ppr_tC']
        summary[option+'_negative_source_entries']=row['negative_source_entries']
        summary[option+'_hypothetical_external_sink_flow']=row['hypothetical_external_sink_flow']
        for name in ['full_return.json.gz','runtime.json.gz','metrics.json']:add('ee_floor_'+option+'_'+name,out/name)
        with gzip.open(out/'full_return.json.gz','rt',encoding='utf-8') as f:ret=json.load(f)
        for mat in ret.values():
            assert mat['type']=='dataframe'
            assert mat['shape']==[len(mat['index']),len(mat['columns'])]
            assert len(set(mat['index']))==len(mat['index']) and len(set(mat['columns']))==len(mat['columns'])
            assert len(mat['data'])==mat['shape'][0] and all(len(r)==mat['shape'][1] for r in mat['data'])
            assert all(len(mask)==mat['shape'][0] and all(len(r)==mat['shape'][1] for r in mask) for mask in mat['masks'].values())
    save(index,data);complete=checker.check(index);save(w/'qa/completeness.json',complete)
    assert complete['complete'],complete
    verifications[entry['unit_id']]={'complete':True,'protected_inputs_unchanged':True,
        'baseline_runtime_exact':qa['baseline_runtime_exact'],'floor_methods':len(rows)}
    summaries.append(summary)
save(BASE/'outputs/eight_model_ee_floor.json',summaries)
with (BASE/'outputs/eight_model_ee_floor.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(summaries[0]));writer.writeheader();writer.writerows(summaries)
save(BASE/'qa/eight_model_ee_floor_verification.json',verifications)
for r in summaries:
    print(r['unit_id'],'affected',r['affected_groups'],'GE%',round(r['GE_PPR_percent_change'],5),
          'TE%',round(r['TE_PPR_percent_change'],5),'egestion%',round(r['With Egestion_PPR_percent_change'],5),
          'GEgap',round(r['GE_extended_PP_gap'],7),'TEgap',round(r['TE_extended_PP_gap'],7))
print('VERIFIED EE FLOOR',len(summaries),'models,',sum(v['floor_methods'] for v in verifications.values()),'method results')
