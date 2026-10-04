from pathlib import Path
from collections import defaultdict,Counter
import sys,json,hashlib,math
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).parent;ROOT=OUT.parents[4];REG=ROOT/'regions/LME_013'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import records,overview,input_hash,digest_tables
from regional import result_hash
b=json.loads((OUT/'baseline_tables.json').read_text(encoding='utf-8'))
o=overview(b);model=o['selected_model_id']
catch=records(b,'Catch','Catch');classic={r['taxon']:r for r in records(b,'Classic PPR','Taxa')}
matching=defaultdict(list)
for r in records(b,'PPR','Matching'):matching[r['taxon']].append(r)
review={r['taxon']:r for r in records(b,'Diagnostics','Taxon mapping validation')}
coeff=defaultdict(dict)
for r in records(b,'PPR','Taxon SPPR'):coeff[r['taxon']][r['scope']+'|'+r['method']]=r['sppr']
taxa=[]
for r in catch:
    if r['catch_basis']!='landings':continue
    c=r[2019];cl=classic.get(r['taxon'],{});sp=cl.get('sppr')
    p=0. if c==0 else c*sp/9 if isinstance(sp,(int,float)) and c is not None else None
    taxa.append({'taxon':r['taxon'],'provider':{k:r[k] for k in ['common_name','functional_group','commercial_group','unidentified']},'catch_tonnes':c,'tl':cl.get('tl'),'classic_sppr_wet':sp,'simple_chain_ppr_tC':p,'matching':matching[r['taxon']],'old_review':review.get(r['taxon']), 'method_exposure_tC':{k:(c*v/9 if isinstance(v,(int,float)) and c is not None else None) for k,v in coeff[r['taxon']].items()}})
assert len(taxa)==len(set(r['taxon'] for r in taxa))==218
(OUT/'review_inputs.json').write_text(json.dumps(taxa,ensure_ascii=False,indent=2),encoding='utf-8')
paths=[REG/o['model_path'],REG/'models/13_1_Chilean_Patagonia_(1980)/sppr_source.xlsx']
paths+=list((REG/'models/regional_ge_integration_20260928').glob('direct_new_*.json'))
paths+=list((REG/'models/regional_ge_integration_20260928').glob('diagnostic_new_*.json'))
paths+=list((REG/'models/13_1_Chilean_Patagonia_(1980)/diet_reextraction_20261002').glob('*'))
paths+=[ROOT/'tools/templates/Model_validation_template.docx',ROOT/'tools/templates/Model_validation_template_instructions.md',ROOT/'tools/knowledge_graph/graph.json',ROOT/'Project.xlsx',ROOT/'interactive_map/index.html',ROOT/'interactive_map/trends.html',ROOT/'interactive_map/archive/index.html']
hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
protected={s:{n:digest_tables([h,r]) for n,(h,r) in b[s].items()} for s in ['Catch','Classic PPR','Selected model groups','NPP','Diagnostics']}
identity={'settings':o,'current_selected_model_sha256':hashes[(REG/o['model_path']).relative_to(ROOT).as_posix()],'saved_result_input_identity':o['results_model_sha256'],'calculation_input_hash_matches':input_hash(b)==o['calculation_input_sha256'],'calculation_result_hash_matches':result_hash(b)==o['calculation_result_sha256'],'protected_table_hashes':protected,'protected_file_hashes':hashes,'independent_simple_ppr_tC':math.fsum(r['simple_chain_ppr_tC'] for r in taxa if r['simple_chain_ppr_tC'] is not None),'total_catch_tonnes':math.fsum(r['catch_tonnes'] for r in taxa),'coefficient_missing':sum(r['classic_sppr_wet'] is None for r in taxa),'positive_catch_unknown_contributions':[r['taxon'] for r in taxa if r['simple_chain_ppr_tC'] is None]}
(OUT/'baseline_identity.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in identity.items() if k not in ['settings','protected_table_hashes','protected_file_hashes']},indent=2))
print('CONFIDENCE',dict(Counter(r['old_review']['overall_confidence'] for r in taxa)))
for k in ['all|new_GE','all|new_TE_EEfix','all|new_WithEgestion']:
    print('EXPOSURE',k)
    for r in sorted(taxa,key=lambda r:abs(r['method_exposure_tC'].get(k) or 0),reverse=True)[:8]:print(r['taxon'],r['method_exposure_tC'].get(k))
