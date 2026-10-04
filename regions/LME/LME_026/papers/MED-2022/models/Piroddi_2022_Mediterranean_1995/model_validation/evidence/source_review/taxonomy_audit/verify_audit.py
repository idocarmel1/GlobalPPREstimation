from pathlib import Path
import json,csv,hashlib,collections
O=Path(__file__).resolve().parent
p=json.loads((O/'taxonomy_mapping_proposals.json').read_text(encoding='utf-8'))
r=p['records'];c=list(csv.DictReader((O/'taxonomy_mapping_proposals.csv').open(encoding='utf-8')))
u=json.loads((O/'catch_label_universe.json').read_text(encoding='utf-8'))
g=json.loads((O/'source_group_definitions.json').read_text(encoding='utf-8'))
t=json.loads((O/'source_docx_tables.json').read_text(encoding='utf-8'))
source_row_conflicts=[]
for x in g:
    ti=x.get('docx_table_one_based');ri=x.get('row_one_based')
    if ti is not None and ri is not None and x['header'] not in t[ti-1]['rows'][ri-1]['cells']:source_row_conflicts.append(x['group_seq'])
checks={'522_exact_unique_keys':len(r)==len(set(x['taxon'] for x in r))==522,'universe_keys_equal':set(x['taxon'] for x in r)==set(x['taxon'] for x in u),'json_csv_keys_equal':set(x['taxon'] for x in r)==set(x['taxon'] for x in c),'all_candidates_valid':all(x['candidate_group_ids'] and all(i in range(1,70) for i in x['candidate_group_ids']) for x in r),'all_source_headers_agree_with_docx':not source_row_conflicts,'all_weights_unassigned':all(x['allocation_weights'] is None for x in r),'four_explicit_stage_unions_high':all(next(x for x in r if x['taxon']==n)['membership_confidence']=='High' for n in ['Sardina pilchardus','Engraulis encrasicolus','Merluccius merluccius','Mullus barbatus'])}
for x in r:
    for l in x['source_locators']:
        assert (O/l['source_path']).is_file()
with (O/'taxonomy_mapping_proposals.json').open(encoding='utf-8') as f:json.load(f)
index={'schema_version':1,'run_id':p['audit_id'],'region_id':'LME_026','model_id':p['model_id'],'stage':'independent_membership_review_only','required_roles':['membership_proposals','flat_membership_proposals','source_group_definitions','catch_universe','source_docx_tables','catch_taxonomy_authority','source_taxonomy_authority','ecology_evidence'],'reconciliation':checks,'artifacts':[]}
identities=json.loads((O/'audit_verification.json').read_text(encoding='utf-8'))
index['variant_id']='accepted source 1995 / 71 groups / no computational transformations'
index['source_identity']={'path':'../../../papers/MED-2022/41598_2022_18017_MOESM2_ESM-7d26163a.docx','sha256':identities['source_docx_sha256'],'table':'S2','purpose':'1990s species composition'}
index['computational_input_identity']={'model_path':'../../../models/Piroddi_2022_Mediterranean_1995/model.json','model_sha256':identities['immutable_model_json_sha256'],'catch_snapshot_path':'catch_label_universe.json','catch_snapshot_sha256':hashlib.sha256((O/'catch_label_universe.json').read_bytes()).hexdigest(),'calculation':'not performed; membership evidence only'}
index['methods']=[]
files={'membership_proposals':'taxonomy_mapping_proposals.json','flat_membership_proposals':'taxonomy_mapping_proposals.csv','source_group_definitions':'source_group_definitions.json','catch_universe':'catch_label_universe.json','source_docx_tables':'source_docx_tables.json','catch_taxonomy_authority':'worms_api_evidence.json','source_taxonomy_authority':'worms_source_api_evidence.json','ecology_evidence':'ecology_web_evidence.json'}
for role,fn in files.items():
    q=O/fn;index['artifacts'].append({'role':role,'path':fn,'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'availability':'present'})
(O/'evidence_index.json').write_text(json.dumps(index,indent=2,ensure_ascii=True),encoding='utf-8')
(O/'completion_checks.json').write_text(json.dumps({'checks':checks,'source_row_conflicts':source_row_conflicts,'confidence_counts':dict(collections.Counter(x['membership_confidence'] for x in r)),'zero_catch_labels':sum(x['catch_tonnes_2019']==0 for x in r)},indent=2,ensure_ascii=True),encoding='utf-8')
print(json.dumps({'checks':checks,'source_row_conflicts':source_row_conflicts},ensure_ascii=True))
assert all(checks.values())
