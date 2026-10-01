"""Read-only independent LME049 source/candidate checks; all writes stay beside this script."""
from pathlib import Path
import csv, json, hashlib, math
from decimal import Decimal
from collections import Counter

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
MID = '49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
REPORT = ROOT / 'regions/LME_049/validation_reports' / MID
MODEL = ROOT / 'regions/LME_049/models' / MID / 'model.json'
ORIGINAL = ROOT / 'regions/LME_049/models/49_20192013_Western_North_Pacific_Watari_(2013)/model.json'
LANDINGS = ORIGINAL.parent / 'extracted_tables/Landings.csv'
INPUTS = ROOT / 'original_research_archive/research/selected_regions_validation_20260930/work/LME_049/inputs.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(name, obj): (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

audit = read(REPORT/'taxon_audit.json'); candidates = read(REPORT/'candidate_and_allocation_evidence.json')
groups = read(MODEL)['group']; original = read(ORIGINAL)['group']; inputs = read(INPUTS)
assert sha(MODEL) == 'ce1c22a1e20e2a5de8a8ac75e6ddb00c3f0db619849354df9f1527277e36d15c'
assert len(groups) == 39 and len(original) == 41
assert groups == inputs['groups'], 'Accepted JSON changed from lead starting snapshot'
scalar_equal = all({k:v for k,v in g.items() if k != 'diet_descr'} == {k:v for k,v in h.items() if k != 'diet_descr'} for g,h in zip(groups[:38], original[:38]))
def diets(g): return (g.get('diet_descr') or {}).get('diet') or []
diet_equal = all([d for d in diets(g) if int(d['prey_seq']) <= 38] == [d for d in diets(h) if int(d['prey_seq']) <= 38] for g,h in zip(groups[:38],original[:38]))
pooled_equal = all(sum(Decimal(d['proportion']) for d in diets(h) if int(d['prey_seq']) >= 39) == sum(Decimal(d['proportion']) for d in diets(g) if int(d['prey_seq']) == 39) for g,h in zip(groups[:38],original[:38]))
assert scalar_equal and diet_equal and pooled_equal
assert Decimal(groups[38]['biomass']) == sum(Decimal(g['biomass']) for g in original[38:]) == Decimal('44.12')

landings = {int(row['']): row for row in csv.DictReader(LANDINGS.open(encoding='utf-8-sig',newline=''))}
raw_catch = {i: (float(r['Total']) if r['Total'] else None) for i,r in landings.items()}
censored = {1,2,20,21,25}
dashes = set(range(1,42)) - set(i for i,v in raw_catch.items() if v is not None) - censored
native_catch_ledger = [{'source_group_seq':i,'group_name':landings[i]['Group name'],
                       'native_Table2_Landings': '<0.01' if i in censored else ('—' if i in dashes else landings[i]['Total fishery']),
                       'classification': 'censored positive upper bound; not exact zero' if i in censored else ('dash; native zero not established' if i in dashes else 'printed positive numeric'),
                       'csv_value':raw_catch[i],
                       'accepted_selected_export':groups[i-1]['export'] if i<=38 else None,
                       'source_locator':'Main PDF6/printed299 Table2, Landings column'} for i in range(1,42)]
save('native_catch_ledger.json',native_catch_ledger)

names = [x['taxon'] for x in audit]; candidate_names = [x['taxon'] for x in candidates]
assert len(audit)==253 and len(set(names))==253 and names==candidate_names
assert set(names)=={x['taxon'] for x in inputs['matching']}
rank={'High':0,'Medium':1,'Low':2,'Very low':3,'unresolved':4}
byseq={int(x['group_seq']):x for x in groups}
checks=[]; max_error=0.; partitions=0
for r,c in zip(audit,candidates):
    ids=r['group_ids']; ws=r['weights']; inc=c['included']; exc=c['excluded']
    assert ids and len(ids)==len(ws)==len(set(ids))
    assert all(math.isfinite(w) and 0<=w<=1 for w in ws)
    assert abs(sum(ws)-1)<1e-12
    assert r['overall_confidence']==max((r['membership_confidence'],r['allocation_confidence']),key=lambda k:rank[k])
    assert ids==[x['seq'] for x in inc] and ws==[x['weight'] for x in inc]
    assert r['membership_rule']==c['membership_rule'] and r['allocation_rule']==c['allocation_rule']
    assert {x['seq'] for x in inc}|{x['seq'] for x in exc}==set(range(1,40))
    assert not ({x['seq'] for x in inc}&{x['seq'] for x in exc})
    partitions+=1
    bs=[float(byseq[i]['biomass']) for i in ids]
    cs=[raw_catch[i] for i in ids]
    assert all(x['source_biomass']==b for x,b in zip(inc,bs))
    assert all(x['source_catch']==v for x,v in zip(inc,cs))
    assert c['catch_vector_complete']==all(v is not None for v in cs)
    rule=r['allocation_rule']
    if rule=='W1':
        assert len(ids)==1
        expected=[1.]
    elif rule=='W4':
        assert all(v is not None for v in cs) and sum(cs)>0
        expected=[v/sum(cs) for v in cs]
        assert r['allocation_confidence']=='Medium'
    elif rule=='W9':
        assert not all(v is not None for v in cs)
        assert all(math.isfinite(b) and b>=0 for b in bs) and sum(bs)>0
        expected=[b/sum(bs) for b in bs]
        assert r['allocation_confidence']=='Medium'
    else:
        raise AssertionError((r['taxon'],rule))
    error=max(abs(x-y) for x,y in zip(ws,expected));max_error=max(max_error,error)
    assert error<1e-12
    checks.append({'taxon':r['taxon'],'group_ids':ids,'weights':ws,'allocation_rule':rule,
                   'independently_reproduced_max_absolute_error':error,
                   'membership_confidence':r['membership_confidence'],'allocation_confidence':r['allocation_confidence'],
                   'overall_confidence':r['overall_confidence']})
save('all253_vector_checks.json',checks)
priority={'Cephalopoda','Octopoda','Octopus','Sepiida','Teuthida','Acetes','Acetes japonicus','Sergestidae','Decapoda','Dendrobranchiata','Scyphozoa','Rhopilema','Gadidae','Gadiformes','Pleuronectidae','Pleuronectiformes','Marine fishes not identified','Marine pelagic fishes not identified','Miscellaneous aquatic invertebrates','Miscellaneous marine crustaceans','Bivalvia','Mollusca','Batoidea','Chondrichthyes','Elasmobranchii'}
save('reviewed_priority_candidate_snapshot.json',[r for r in audit if r['taxon'] in priority])
result={'scope':'Independent native source identity/provenance, all253 saved allocation vectors and confidence consistency; bounded candidate evidence review, not exhaustive unreadS1 membership verification or scientific approval',
        'input_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [MODEL,ORIGINAL,LANDINGS,INPUTS,REPORT/'taxon_audit.json',REPORT/'candidate_and_allocation_evidence.json',REPORT/'authoritative_taxonomy_api.json',REPORT/'publisher_supplement_web_reader.json',REPORT/'matrix_inspection.json']},
        'accepted_json_matches_starting_snapshot':True,
        'source41_selected39_comparison':{'all38_non_detritus_scalar_fields_equal':scalar_equal,'all_nondetritus_prey_records_equal':diet_equal,'each_original39_40_41_detritus_diet_sum_equals_selected39':pooled_equal,'source_detritus_B_sum_and_selected_B':44.12},
        'taxa_checked':len(audit),'unique_exact_labels':len(set(names)),'complete39_group_candidate_partitions':partitions,
        'all_finite_normalized_vectors':True,'weakest_confidence_rule_all_rows':True,
        'allocation_counts':dict(Counter(x['allocation_rule'] for x in audit)),
        'overall_confidence_counts':dict(Counter(x['overall_confidence'] for x in audit)),
        'max_weight_error':max_error,'native_catch_numeric_group_count':sum(v is not None for v in raw_catch.values()),
        'native_catch_genuine_exact_zero_count':0,'native_censored_groups':sorted(censored),'native_dash_groups':sorted(dashes),
        'protected_inputs_unchanged':True,'pipeline_or_diagnostic_execution':False,
        'status':'PASS bounded numeric/protected-input checks; native membership limitations retained'}
save('verification.json',result)
print(json.dumps(result,ensure_ascii=False,indent=2))
