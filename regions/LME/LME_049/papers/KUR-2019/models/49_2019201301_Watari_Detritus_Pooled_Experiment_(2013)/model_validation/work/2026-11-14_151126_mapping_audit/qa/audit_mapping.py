"""Read-only verification of reused LME049 mapping and reference arithmetic."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import math
import sys
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records, overview, digest_tables
import openpyxl

MODEL_ID = '49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
MODEL = ROOT / 'regions/LME/LME_049/papers/KUR-2019/models' / MODEL_ID
REGION = ROOT / 'regions/LME/LME_049'
EVIDENCE = MODEL / 'model_validation/evidence/source_review'
OUT = Path(__file__).parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def relative(path):
    return path.relative_to(ROOT).as_posix()

def finite(v):
    return isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v)

def same_number(a, b):
    return a == b or (finite(a) and finite(b) and math.isclose(a, b, rel_tol=2e-15, abs_tol=1e-12))

paths = [REGION/'LME_049.xlsx', MODEL/'model.json', MODEL/'model_validation/taxon_mapping.xlsx',
         EVIDENCE/'taxon_audit.json', EVIDENCE/'candidate_and_allocation_evidence.json',
         EVIDENCE/'authoritative_taxonomy_api.json', EVIDENCE/'publisher_supplement_web_reader.json',
         MODEL.parent.parent/'sources/Watari-Ecosystemmodelingwestern-2019.pdf']
before = {relative(p): sha(p) for p in paths}
book = read_book(paths[0], sheets=['Overview','Catch','Classic PPR','Selected model groups','PPR'])
settings = overview(book)
assert settings['selected_model_id'] == MODEL_ID
year, basis = int(settings['taxon_detail_year']), settings['catch_basis']
audits = load(EVIDENCE/'taxon_audit.json')
candidates = load(EVIDENCE/'candidate_and_allocation_evidence.json')
oldverify = load(EVIDENCE/'independent_source_review/verification.json')
source_model = load(MODEL/'model.json')
groups = {int(x['group_seq']):x for x in source_model['group']}
audit_by = {x['taxon']:x for x in audits}
candidate_by = {x['taxon']:x for x in candidates}
catch = [x for x in records(book,'Catch','Catch') if x['catch_basis'] == basis]
classic = records(book,'Classic PPR','Taxa')
match = [x for x in records(book,'PPR','Matching') if x['model_id'] == MODEL_ID]
membership = [x for x in records(book,'PPR','Mapping review') if x.get('model_id',MODEL_ID) == MODEL_ID]
allocations = [x for x in records(book,'PPR','Allocation assumptions') if x.get('model_id') == MODEL_ID]
issues = []
checks = {}
def check(name, condition, detail=None):
    checks[name] = bool(condition)
    if not condition:
        issues.append({'check':name,'detail':detail})

check('unique_catch_labels',len({x['taxon'] for x in catch})==len(catch))
check('unique_classic_labels',len({x['taxon'] for x in classic})==len(classic))
check('unique_mapping_pairs',len({(x['taxon'],x['group']) for x in match})==len(match))
check('all_253_exact_catch_labels',len(catch)==253 and set(audit_by)=={x['taxon'] for x in catch})
check('all_253_candidate_records',len(candidates)==253 and set(candidate_by)==set(audit_by))
classic_by = {x['taxon']:x for x in classic}
match_by = collections.defaultdict(list)
for x in match: match_by[x['taxon']].append(x)
check('stored_mapping_taxon_set_exact',set(match_by)==set(audit_by))
membership_by = {x['taxon']:x for x in membership}
check('stored_component_review_taxon_set_exact',len(membership)==253 and set(membership_by)==set(audit_by))
allocation_by = {(x['taxon'],int(x['seq'])):x for x in allocations}
check('stored_allocation_keys_unique',len(allocation_by)==len(allocations))

reuse_hashes = []
for original,expected in oldverify['input_sha256'].items():
    name = Path(original).name
    path = EVIDENCE/name
    if path.exists():
        reuse_hashes.append({'historical_path':original,'current_path':relative(path),'expected':expected,'actual':sha(path),'matches':sha(path)==expected})
    elif name=='model.json':
        actual_path = MODEL/'model.json' if MODEL_ID in original else MODEL.parent/'49_20192013_Western_North_Pacific_Watari_(2013)'/'model.json'
        reuse_hashes.append({'historical_path':original,'current_path':relative(actual_path),'expected':expected,'actual':sha(actual_path),'matches':sha(actual_path)==expected})
check('reused_review_hashes_match',all(r['matches'] for r in reuse_hashes),reuse_hashes)

levels = ['High','Medium','Low','Very low','Unresolved']
rows = []
max_weight_difference = 0.0
for c in catch:
    taxon = c['taxon']; a = audit_by[taxon]; cl = classic_by.get(taxon,{})
    ct, coeff, tl = c.get(year), cl.get('sppr'), cl.get('tl')
    ppr = 0.0 if finite(ct) and ct==0 else ct*coeff/9 if finite(ct) and finite(coeff) else None
    keyed_current = {x['group']:x for x in match_by[taxon]}
    keyed_reviewed = {n:w for n,w in zip(a['group_names'],a['weights'])}
    differences = []
    if set(keyed_current)!=set(keyed_reviewed): differences.append('group set')
    for name,weight in keyed_reviewed.items():
        current = keyed_current.get(name,{})
        if not same_number(current.get('weight'),weight): differences.append('weight: '+name)
        if finite(current.get('weight')): max_weight_difference=max(max_weight_difference,abs(current['weight']-weight))
        if (current.get('confidence') or '').lower().replace('_',' ') != a['overall_confidence'].lower(): differences.append('confidence: '+name)
        if current.get('explanation') != a['reason']: differences.append('reason: '+name)
    if differences: issues.append({'taxon':taxon,'mapping_discrepancy':differences})
    for field in ('membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence','reason'):
        if membership_by.get(taxon,{}).get(field) != a[field]: issues.append({'taxon':taxon,'stored_component_review_mismatch':field})
    for gid,weight in zip(a['group_ids'],a['weights']):
        al=allocation_by.get((taxon,gid),{})
        if not same_number(al.get('weight'),weight) or al.get('rule')!=a['allocation_rule']:
            issues.append({'taxon':taxon,'stored_allocation_mismatch':gid})
    if not all(same_number(v,w) for v,w in [(ct,a['catch_tonnes']),(coeff,a['classic_sppr']),(tl,a['tl']),(ppr,a['simple_chain_ppr_tC'])]):
        issues.append({'taxon':taxon,'reference_arithmetic_mismatch':True})
    if levels[max(levels.index(a['membership_confidence']),levels.index(a['allocation_confidence']))] != a['overall_confidence']:
        issues.append({'taxon':taxon,'weakest_component_mismatch':True})
    if any(groups[gid]['group_name'] != name for gid,name in zip(a['group_ids'],a['group_names'])):
        issues.append({'taxon':taxon,'canonical_group_identity_mismatch':True})
    cand = candidate_by[taxon]
    inc = cand['included']
    if set(x['seq'] for x in inc)!=set(a['group_ids']): issues.append({'taxon':taxon,'candidate_set_mismatch':True})
    if set(x['seq'] for x in inc) | set(x['seq'] for x in cand['excluded']) != set(groups): issues.append({'taxon':taxon,'incomplete_candidate_partition':True})
    if a['allocation_rule'] in ('W4','W9'):
        field='source_catch' if a['allocation_rule']=='W4' else 'source_biomass'
        values=[x[field] for x in inc]
        if not all(finite(v) and v>=0 for v in values) or sum(values)<=0:
            issues.append({'taxon':taxon,'unusable_allocation_source_vector':True})
        else:
            expected={x['seq']:x[field]/sum(values) for x in inc}
            if any(not same_number(expected[gid],w) for gid,w in zip(a['group_ids'],a['weights'])):
                issues.append({'taxon':taxon,'reused_allocation_vector_mismatch':True})
        if a['allocation_rule']=='W9' and cand['catch_vector_complete']:
            issues.append({'taxon':taxon,'biomass_fallback_without_rejected_catch':True})
    row={k:v for k,v in a.items() if k not in ('prior_mapping','taxonomy_identity')}
    row.update(reference_year=year,catch_basis=basis,catch_tonnes=ct,classic_sppr=coeff,tl=tl,simple_chain_ppr_tC=ppr,
               stored_confidence=sorted({x.get('confidence') for x in match_by[taxon]}),
               review_reused_with_identical_input_hash=True,mapping_discrepancies=differences)
    rows.append(row)

tot_catch=sum(r['catch_tonnes'] for r in rows if finite(r['catch_tonnes']))
tot_ppr=sum(r['simple_chain_ppr_tC'] for r in rows if finite(r['simple_chain_ppr_tC']))
def partition(fields):
    result=[]
    keys=sorted({tuple(r[k] for k in fields) for r in rows})
    for key in keys:
        selected=[r for r in rows if tuple(r[k] for k in fields)==key]
        ct=sum(r['catch_tonnes'] for r in selected if finite(r['catch_tonnes']))
        pp=sum(r['simple_chain_ppr_tC'] for r in selected if finite(r['simple_chain_ppr_tC']))
        result.append(dict(zip(fields,key))|{'taxa':len(selected),'catch_tonnes':ct,'ppr_tC':pp,'catch_percentage':100*ct/tot_catch,'ppr_percentage':100*pp/tot_ppr})
    return result

summary=partition(['overall_confidence'])
for level in levels:
    if not any(r['overall_confidence']==level for r in summary): summary.append({'overall_confidence':level,'taxa':0,'catch_tonnes':0.0,'ppr_tC':0.0,'catch_percentage':0.0,'ppr_percentage':0.0})
summary.sort(key=lambda r:levels.index(r['overall_confidence']))
mem_summary=partition(['membership_rule','membership_confidence'])
weight_summary=partition(['allocation_rule','allocation_confidence'])
check('confidence_membership_allocation_each_partition_100',all(math.isclose(sum(x['ppr_percentage'] for x in t),100,abs_tol=1e-10) for t in [summary,mem_summary,weight_summary]))
annual=[x for x in records(book,'Classic PPR','Annual') if x.get('scope')=='all' and x.get('method')=='simple trophic chain' and x.get('catch_basis')==basis and x.get('unidentified')=='method' and x.get('metric')=='ppr']
check('one_reference_classic_annual_row',len(annual)==1)
check('carbon_conversion_exactly_once_matches_saved_annual',len(annual)==1 and same_number(annual[0][year]/9,tot_ppr))

appendix_path=MODEL/'model_validation/taxon_mapping.xlsx'
wb=openpyxl.load_workbook(appendix_path,read_only=True,data_only=False)
appendix_data=list(wb['Taxon mapping'].values)
header_index=next(i for i,r in enumerate(appendix_data) if r[0]=='Taxon name')
appendix=[r[:7] for r in appendix_data[header_index+1:] if r[0] is not None]
wb.close()
check('appendix_has_exact_taxon_set',len(appendix)==253 and {r[0] for r in appendix}==set(audit_by))
appendix_differences=[]
for values in appendix:
    taxon=values[0]; a=audit_by[taxon]
    # Existing appendix adds separate component labels and descriptive source IDs.
    prefix=f"Membership {a['membership_confidence']}; allocation {a['allocation_confidence']}. "
    reason_ok=isinstance(values[6],str) and values[6].startswith(prefix+a['reason']) and all(s in values[6] for s in a['sources'])
    expected_reason=values[6] if reason_ok else prefix+a['reason']
    expected=[a['taxon'],a['tl'] if a['tl'] is not None else '?',a['catch_tonnes'],a['simple_chain_ppr_tC'],a['mapping_display'],a['overall_confidence'],expected_reason]
    diffs=[i+1 for i,(x,y) in enumerate(zip(values,expected)) if not same_number(x,y)]
    if diffs: appendix_differences.append({'taxon':taxon,'differing_columns':diffs,'current_values':values,'audit_values':expected})
check('appendix_values_match_audit',not appendix_differences,appendix_differences)
expected_order=[r['taxon'] for r in sorted(rows,key=lambda r:(r['simple_chain_ppr_tC'] is None,-r['simple_chain_ppr_tC'] if finite(r['simple_chain_ppr_tC']) else 0,r['taxon']))]
check('appendix_sorted_by_unrounded_ppr_then_taxon',[r[0] for r in appendix]==expected_order)

geo=load(EVIDENCE/'geography/geography_trace_assessment.json')
geo_delivery=load(EVIDENCE/'independent_source_review/delivery_hashes.json')['files']
geo_hashes=[]
for name in ('Figure1_native.png','Figure1_colored_study_trace_draft.geojson','target_LME049.geojson','target_trace_controls.png','geography_trace_assessment.json'):
    p=EVIDENCE/'geography'/name
    geo_hashes.append({'path':relative(p),'actual':sha(p),'expected':geo_delivery[name]['sha256'],'matches':sha(p)==geo_delivery[name]['sha256']})
check('geographic_retained_evidence_hashes_match',all(x['matches'] for x in geo_hashes),geo_hashes)
check('main_article_bytes_match_geography',sha(paths[-1])==geo['source_main_pdf_sha256'])
for s in geo['scenarios']:
    check('geography_'+s['name']+'_arithmetic',same_number(100*s['overlap_km2']/geo['target_area_km2'],s['A_overlap_over_target_percent']) and same_number(100*s['overlap_km2']/s['study_area_km2'],s['B_overlap_over_traced_study_percent']))

verylow=collections.defaultdict(list)
for r in rows:
    if r['overall_confidence']=='Very low': verylow[r['reason']].append(r['taxon'])
verylow_groups=[{'taxa':sorted(taxa),'reason':reason} for reason,taxa in verylow.items()]
verylow_groups.sort(key=lambda r:r['taxa'][0])
after={relative(p):sha(p) for p in paths}
check('all_consumed_mutable_inputs_unchanged_during_audit',before==after)
review={
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'Read-only verification and report arithmetic. Reused hash-matching prior all-taxon source/candidate review; no independent re-extraction, mapping changes, source taxonomy refresh, scientific execution, workbook/map/project write or approval.',
 'unit_id':'LME_049','model_id':MODEL_ID,'reference_controls':{'year':year,'catch_basis':basis,'source_scope':'all','unidentified':'method','taxon_filter':'all','group_filter':'none'},
 'input_hashes':before,'reused_review_input_hashes':reuse_hashes,
 'dependency_hashes':{f'{s}/{t}':digest_tables([book[s][t]]) for s,t in [('Catch','Catch'),('Classic PPR','Taxa'),('PPR','Matching'),('PPR','Mapping review'),('PPR','Allocation assumptions')]},
 'checks':checks,'issues':issues,'source_group_count':len(groups),'historical_synthetic_group':'diet_import40 (outside source ecological count)',
 'taxa':len(rows),'positive_reference_catch_taxa':sum(finite(r['catch_tonnes']) and r['catch_tonnes']>0 for r in rows),'zero_reference_catch_taxa':sum(r['catch_tonnes']==0 for r in rows),
 'total_catch_tonnes':tot_catch,'total_simple_chain_ppr_tC':tot_ppr,'stored_classic_annual_wet':annual[0][year],
 'missing_coefficients':[r['taxon'] for r in rows if not finite(r['classic_sppr'])],
 'missing_tl':[r['taxon'] for r in rows if not finite(r['tl'])],
 'unknown_annual_ppr':[r['taxon'] for r in rows if r['simple_chain_ppr_tC'] is None],
 'unresolved_taxa':[r['taxon'] for r in rows if r['overall_confidence']=='Unresolved'],
 'confidence_summary':summary,'membership_summary':mem_summary,'allocation_summary':weight_summary,
 'very_low_decisions':verylow_groups,'very_low_taxon_count':sum(len(r['taxa']) for r in verylow_groups),
 'mapping_max_weight_serialization_difference':max_weight_difference,'appendix_discrepancies':appendix_differences,
 'mapping_review_table_schema':book['PPR']['Mapping review'][0], 'allocation_table_schema':book['PPR']['Allocation assumptions'][0],
 'geography':{'evidence_hashes':geo_hashes,'source_locator':geo['calibration']['source_locator'],'target_area_km2':geo['target_area_km2'],'reported_source_areas_km2':geo['reported_source_areas_km2'],'scenarios':geo['scenarios'],'confidence':'Low','proposal_only':True,'limits':geo['limits']},
 'temporal_fit':'Static 2013 linked OYC/KC/OF model and fixed 2013 source catch/biomass allocations transferred to the 1950–2019 whole-LME series; report reference is 2019, six years after baseline. Fixed proxies are composition assumptions, not measured 2019 regional splits.',
 'material_limits':['Partial Supplement 1 retained indexed text only (pages 1–11 of reported 46); exact supplemental PDF bytes and later membership/time-series not recovered in reused review.','94 Very low taxa retain disclosed broad-composition or analogue uncertainty; zero Unresolved is not independent proof of ecological validity.','24 missing classic TL/coefficient labels have zero 2019 landings, so no unknown annual PPR; do not fill the missing inputs.','Historical source_review diagnostics and source assumptions must not be relabeled as outcomes of the new accounting run.','Geographic overlap is approximate retained digitization with Low confidence, no catch/PPR multiplier and no newly adopted geographic estimate.'],
 'rows':rows,
}
(OUT/'mapping_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({k:review[k] for k in ['taxa','positive_reference_catch_taxa','zero_reference_catch_taxa','total_catch_tonnes','total_simple_chain_ppr_tC','confidence_summary','membership_summary','allocation_summary','checks']},ensure_ascii=False,indent=2))
print('ISSUE COUNT '+str(len(issues)))
print(json.dumps(issues[:2],ensure_ascii=False)[:2000])
print('OUTPUT '+str(OUT/'mapping_review.json'))
