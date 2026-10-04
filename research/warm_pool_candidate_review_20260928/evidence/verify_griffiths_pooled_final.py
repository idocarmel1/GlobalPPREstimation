from pathlib import Path
import json,hashlib,csv,openpyxl
from decimal import Decimal as D
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
SRC=ROOT/'regions/EEZ_941/models/941_201901_Warm_Pool_(2005)';OUT=SRC.parent/'941_20190101_Warm_Pool_Detritus_Pooled_Experiment_(2005)'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC/'model.json')=='523cefaa423538f0609b96b75064594f426d87c8dca997a7973515792c1bafc3'
a=read(SRC/'model.json')['group'];b=read(OUT/'model.json')['group'];assert len(a)==46 and len(b)==45
assert a[42:44]==b[42:44]
for x,y in zip(a[:42],b[:42]):
    assert {k:v for k,v in x.items() if k!='diet_descr'}=={k:v for k,v in y.items() if k!='diet_descr'}
    dx=x['diet_descr']['diet'];dy=y['diet_descr']['diet']
    assert sum(D(i['proportion']) for i in dx)==sum(D(i['proportion']) for i in dy)
    assert [i for i in dx if int(i['prey_seq'])<45]==[i for i in dy if int(i['prey_seq'])<45]
assert D(b[44]['biomass'])==sum(D(x['biomass']) for x in a[44:])
files=['Metadata.xlsx','Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Biomass_accumulation.csv','TL.xlsx','Detritus_fate.csv']
assert all((OUT/'extracted_tables'/n).exists() for n in files)
wb=openpyxl.load_workbook(OUT/'extracted_tables/CANONICAL_reconstructed.xlsx',data_only=True)
shapes={s:[ws.max_row,ws.max_column] for s,ws in [(s,wb[s]) for s in wb.sheetnames]}
assert wb['Basic input'].max_row==46
assert wb['Taxonomy'].max_row==46
returns=read(OUT/'diagnostics/DIRECT_DIAGNOSTICS.json');assert set(returns)=={'GE','TE','With Egestion'}
for o,r in returns.items():
    assert r==read(OUT/'diagnostics'/('diagnose_'+o.replace(' ','_')+'.json'))
    assert r['status']=='FAIL' and r['config']['TE_option']==o
    assert r['model_input']['total_catch']==0.033458867
    assert r['divergence']['solve_error'] is None and r['divergence']['n_negative_sources']==0
prov=read(OUT/'diagnostics/RUN_PROVENANCE.json');assert prov['experiment_sha256']==sha(OUT/'model.json')
for n,h in prov['code_sha256'].items():assert sha(OUT/'diagnostics/executed_code'/n)==h
manifest=read(OUT/'evidence/ARTIFACT_MANIFEST.json')
for f in manifest['files']:assert sha(OUT/f['path'])==f['sha256']
bench=ROOT/'regions/EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)/balance_investigation/correction_scenarios/D_fixed_M0'
w=read(BASE/'WCP_OPTION1_SAVED_DIRECT_DIAGNOSTICS.json')
for o in returns:assert w[o]==read(bench/('diagnose_'+o.replace(' ','_')+'.json'))
v={'verification':'PASS','original_source_hash_unchanged':True,'all_living_scalar_inputs_exactly_preserved':True,'diet_pool_conservation_exact':True,'imports':files,'canonical_reconstruction_shapes':shapes,'full_direct_returns':{o:r['status'] for o,r in returns.items()},'frozen_code_hashes_verified':True,'experiment_manifest_files_verified':len(manifest['files']),'saved_WCP_returns_equal_original':True,'no_selection':True,'no_global':True,'scientific_model_status':'FAIL'}
(BASE/'POOLED_FINAL_VERIFICATION.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');print(json.dumps(v,indent=2))
