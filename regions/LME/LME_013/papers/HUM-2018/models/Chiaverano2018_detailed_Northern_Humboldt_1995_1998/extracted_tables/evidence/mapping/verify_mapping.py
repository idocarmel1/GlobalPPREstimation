from pathlib import Path
import csv, hashlib, json, math
from collections import Counter

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
SOURCE=OUT.parent/'source'/'resolved_native'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def close(a,b):return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-9)
m=read(OUT/'mapping_review.json');u=read(OUT/'catch_universe.json');s=read(OUT/'regional_arithmetic_snapshot.json')
rows=m['taxa'];checks={}
def check(name,test):
    checks[name]=bool(test)
    if not test:raise AssertionError(name)
labels=[r['taxon'] for r in rows]
check('all_218_exact_labels_unique',len(labels)==218 and len(set(labels))==218 and set(labels)=={r['taxon'] for r in u['taxa']})
check('all_42_zero_catch_labels_in_review',sum(r['catch_t']==0 for r in rows)==42 and all(r['simple_chain_ppr_tC']==0 for r in rows if r['catch_t']==0))
rank={'High':4,'Medium':3,'Low':2,'Very low':1,'Unresolved':0}
ident={int(g['seq']):g for g in read(SOURCE/'GROUP_IDENTITY.json')}
with (SOURCE/'GROUP_CATCH_BIOMASS.csv').open(encoding='utf-8-sig',newline='') as f:proxy={int(r['seq']):r for r in csv.DictReader(f)}
check('fresh_source_39_stock_group_ids',set(ident)==set(range(1,40)))
search=read(OUT/'search_records.json');searchids={r['id']:r for r in search['records']}
refs={r['id']:r for r in m['sources']}
weight_errors=[];proxy_errors=[];names_errors=[];decision_errors=[];search_errors=[];confidence_errors=[]
zero_candidates=[]
for r in rows:
    cs=r['candidates'];ids=[c['group_id'] for c in cs]
    if len(ids)!=len(set(ids)) or not close(math.fsum(c['weight'] for c in cs),1):weight_errors.append(r['taxon'])
    if r['overall_confidence']!=min(r['membership_confidence'],r['allocation_confidence'],key=rank.get):confidence_errors.append(r['taxon'])
    decisions=r['candidate_decisions']
    if {c['group_id'] for c in decisions}!=set(ident) or len(decisions)!=39 or {c['group_id'] for c in decisions if c['decision']=='included'}!=set(ids):decision_errors.append(r['taxon'])
    if r['allocation_rule']!='W1' and not r['composition_search_record_ids']:search_errors.append(r['taxon'])
    for sid in r['composition_search_record_ids']:
        if sid not in searchids or r['taxon'] not in searchids[sid]['taxa']:search_errors.append(r['taxon'])
    for c in cs:
        g=ident[c['group_id']];p=proxy[c['group_id']]
        if c['group_name']!=g['group_name'] or c['source_definition']!=g['taxon_descr']:names_errors.append(r['taxon'])
        pairs={'source_landings':'landings_total_t_km2_y','source_discards':'discards_total_t_km2_y','source_catch':'catch_total_t_km2_y','source_biomass':'biomass_t_km2','source_landings_artisanal':'landings_artisanal_t_km2_y','source_landings_commercial':'landings_commercial_t_km2_y'}
        if any(not close(c[k],float(p[v])) for k,v in pairs.items()):proxy_errors.append(r['taxon'])
        if c['catch_value_missing'] or c['loaded_catch_used'] or c['zero_is_source_explicit']!=(float(p['landings_total_t_km2_y'])==0):proxy_errors.append(r['taxon'])
        if c['weight']==0:zero_candidates.append({'taxon':r['taxon'],'group_id':c['group_id'],'native_landings':c['source_landings'],'native_discards':c['source_discards']})
    if r['allocation_rule']=='W1':
        if len(cs)!=1 or cs[0]['weight']!=1 or r['allocation_denominator'] is not None:weight_errors.append(r['taxon'])
    else:
        field='source_biomass' if r['allocation_rule']=='W9' else 'source_landings'
        total=math.fsum(c[field] for c in cs)
        if not close(total,r['allocation_denominator']) or any(not close(c['weight'],c[field]/total) for c in cs):weight_errors.append(r['taxon'])
        if r['allocation_rule']=='W9' and (not all(c['source_landings']==0 for c in cs) or not r['rejected_proxy_attempt']):proxy_errors.append(r['taxon'])
    if not all(x in refs for x in r['sources']):search_errors.append(r['taxon'])
check('complete_candidate_decisions_218_times_39',not decision_errors)
check('weaker_required_component_confidence',not confidence_errors)
check('all_weights_finite_sum_one_recomputed',not weight_errors)
check('native_quantities_missingness_zero_and_basis_match_fresh_source',not proxy_errors)
check('native_group_strings_and_definitions_preserved',not names_errors)
check('all_38_split_rows_have_applicable_primary_search_ledger',not search_errors)
check('large_hake_zero_weight_retained_for_all_hake_stage_rows',all(any(c['group_id']==20 and c['weight']==0 and c['source_discards']>0 for c in r['candidates']) for r in rows if any(c['group_id']==18 for c in r['candidates'])))

classic={r['taxon']:r for r in s['classic_taxa']}
catch={(r['taxon'],r['catch_basis']):r for r in s['catch']}
check('catch_snapshot_all_bases_labels_years',len(catch)==654 and all(set(str(y) for y in range(1950,2020)).issubset(r) for r in catch.values()))
independent=[];missing_positive=[];tl_checks=[]
for r in rows:
    base=catch[r['taxon'],'landings']['2019'];cl=classic.get(r['taxon'],{})
    coefficient=cl.get('sppr')
    if coefficient is None and cl.get('tl') is not None:coefficient=0.1**(1-cl['tl'])
    if coefficient is not None and cl.get('tl') is not None:tl_checks.append(close(coefficient,0.1**(1-cl['tl'])))
    expected=0.0 if base==0 else None if base is None or coefficient is None else base*coefficient/9
    if expected is None and base and base>0:missing_positive.append(r['taxon'])
    check('classic_row_'+r['taxon'],expected==r['simple_chain_ppr_tC'] if expected is None else close(expected,r['simple_chain_ppr_tC']))
    if expected is not None:independent.append(expected)
check('saved_TL_coefficients_match_TE_one_tenth',all(tl_checks))
check('no_positive_reference_catch_missing_classic_ppr',not missing_positive)
independent_total=math.fsum(independent);catch_total=math.fsum(r['catch_t'] for r in rows)
savedannual=[r for r in s['classic_annual'] if r['catch_basis']=='landings' and r['metric']=='ppr' and r['scope']=='all' and r['method']=='simple trophic chain' and r['unidentified']=='method']
check('independent_carbon_denominator_divide_nine_once',len(savedannual)==1 and close(independent_total,savedannual[0]['2019']/9) and close(independent_total,u['metadata']['known_ppr_denominator_tC']))
summary=m['summary']
for key in ['confidence_rows','membership_rule_rows','allocation_rule_rows']:
    counts=Counter(t for rr in summary[key] for t in rr['taxa'])
    check(key+'_all_labels_partition_once',set(counts)==set(labels) and all(v==1 for v in counts.values()))
    check(key+'_catch_and_ppr_reconcile',close(math.fsum(x['catch_t'] for x in summary[key]),catch_total) and close(math.fsum(x['simple_chain_ppr_tC'] for x in summary[key]),independent_total) and close(math.fsum(x['ppr_percentage'] for x in summary[key]),100))
vl=Counter(t for r in summary['very_low_decision_groups'] for t in r['taxa'])
check('all_27_very_low_labels_grouped_exactly_once',set(vl)=={r['taxon'] for r in rows if r['overall_confidence']=='Very low'} and len(vl)==27 and all(v==1 for v in vl.values()))
local_links=[]
for ref in m['sources']:
    t=ref['target']
    if not t.startswith('http'):
        p=(OUT/t.split('#')[0]).resolve();local_links.append({'id':ref['id'],'path':t,'exists':p.is_file()})
check('all_local_source_links_resolve',all(x['exists'] for x in local_links))
check('all_raw_search_ledger_files_resolve',all((OUT/p).is_file() for r in search['records'] for p in r['raw_search_evidence']))
book=ROOT/'regions/LME_013/LME_013.xlsx'
check('active_regional_workbook_sha_unchanged',sha(book)==u['metadata']['workbook_sha256'])
check('mapping_fresh_source_hashes_match',all(sha(SOURCE/name)==value for name,value in m['metadata']['source_hashes'].items()))
check('search_ledger_hash_matches_mapping',sha(OUT/'search_records.json')==m['metadata']['search_ledger_sha256'])
nonrowchecks={k:v for k,v in checks.items() if not k.startswith('classic_row_')}
verification={'status':'PASS','verified_utc_date':'2026-10-03','mapping_sha256':sha(OUT/'mapping_review.json'),'checks':nonrowchecks,'individual_classic_rows_checked':218,'source_groups_reviewed_per_label':39,'candidate_decisions_count':218*39,'catch_denominator_t':catch_total,'independent_simple_chain_ppr_tC':independent_total,'missing_positive_reference_ppr':missing_positive,'zero_weight_candidates':zero_candidates,'local_links':local_links,'limitations':'Verification checks numerical reconciliation, completeness, provenance and confidence combination. Ecological interpretations remain proposals; no validation of wider-LME applicability or scientifically failed candidate engine is inferred.'}
(OUT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
artifacts=[]
roles={'catch_universe':'catch_universe.json','regional_arithmetic_snapshot':'regional_arithmetic_snapshot.json','mapping_review':'mapping_review.json','allocation_ledger':'allocation_ledger.json','mapping_summary':'summary.json','primary_search_ledger':'search_records.json','taxonomy_authority':'taxonomy_authority_records.json','mapping_verification':'verification.json','mapping_csv':'mapping_flat.csv','catch_universe_csv':'catch_universe.csv','mapping_builder':'build_mapping.py','search_ledger_builder':'build_search_ledger.py','verification_code':'verify_mapping.py','fresh_source_identity':'../source/resolved_native/GROUP_IDENTITY.json','fresh_source_quantities':'../source/resolved_native/GROUP_CATCH_BIOMASS.csv'}
for role,name in roles.items():artifacts.append({'role':role,'availability':'present','path':name,'sha256':sha(OUT/name)})
for path in sorted(OUT.glob('search_*_*.json')):
    if path.name=='search_records.json':continue
    artifacts.append({'role':'primary_raw_search','availability':'present','path':path.name,'sha256':sha(path)})
index={'schema_version':1,'run_id':'HUM2018_20261003','region_id':'LME_013','model_id':'HUM2018_20261003_detailed','variant_id':'native_supplement_unadopted_mapping','source_identity':m['metadata']['source_hashes'],'computational_input_identity':{'mapping_sha256':sha(OUT/'mapping_review.json'),'regional_workbook_sha256':u['metadata']['workbook_sha256']},'methods':['independent simple trophic chain','catch-label membership and allocation audit'],'required_roles':list(roles),'artifacts':artifacts,'reconciliation':nonrowchecks}
(OUT/'evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','mapping_sha256':verification['mapping_sha256'],'checks':len(checks),'catch_t':catch_total,'independent_ppr_tC':independent_total,'zero_weight_candidates':len(zero_candidates)},indent=2))
