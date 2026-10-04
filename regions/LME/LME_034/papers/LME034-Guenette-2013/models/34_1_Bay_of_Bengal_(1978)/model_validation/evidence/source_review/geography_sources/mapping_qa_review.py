from pathlib import Path
import json, collections, math, hashlib

root=Path.cwd()
out=root/'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/geography_sources'
path=root/'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/mapping_review/audit_decisions.json'
bundle=json.loads(path.read_text(encoding='utf8'))
d=bundle['decisions']
print('RULES',collections.Counter((r['membership_rule'],r['membership_confidence'],r['allocation_rule'],r['overall_confidence']) for r in d))
print('ALL DECISIONS')
for i,r in enumerate(d):
    print(f"{i:03d} {r['taxon']} | {r['membership_rule']}/{r['membership_confidence']} + {r['allocation_rule']}/{r['allocation_confidence']} => {r['overall_confidence']} | {', '.join(g['group'] for g in r['proposed_groups'])}")
print('CHANGED')
changed=[]
for r in d:
    if {g['group'] for g in r['proposed_groups']} != {g['group'] for g in r['old_groups']}:
        changed.append(r['taxon'])
        print(json.dumps({k:r.get(k) for k in ['taxon','common_name','functional_group','membership_rule','membership_confidence','allocation_rule','overall_confidence','candidate_inclusion_rationale']},ensure_ascii=False)+' NEW '+str([g['group'] for g in r['proposed_groups']])+' OLD '+str([g['group'] for g in r['old_groups']]))

rank={'Unresolved':0,'Very low':1,'Low':2,'Medium':3,'High':4}
checks={'taxon_count':len(d),'taxon_unique':len({r['taxon'] for r in d}), 'changed_group_sets':len(changed)}
concerns=[]
snapshot=json.loads((root/'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/mapping_review/workbook_extract.json').read_text(encoding='utf8'))
provider={r['taxon']:r for r in snapshot['Catch']['Catch'] if r['catch_basis']=='landings'}
checks['provider_landings_taxa']=len(provider)
checks['provider_universe_matches']=set(provider)=={r['taxon'] for r in d}
for r in d:
    p=provider[r['taxon']]
    for field in ['common_name','functional_group','commercial_group']:
        if p[field]!=r[field]:concerns.append({'taxon':r['taxon'],'check':'provider_category','finding':field+' does not match Catch provider.'})
    if abs(p['2019']-r['catch_tonnes'])>1e-8:concerns.append({'taxon':r['taxon'],'check':'catch_year','finding':'Annual catch does not match2019landings.'})

synonym_pairs={
 'Penaeus merguiensis':'Fenneropenaeus merguiensis','Penaeus latisulcatus':'Melicertus latisulcatus',
 'Deveximentum insidiator':'Secutor insidiator','Mierspenaeopsis hardwickii':'Parapenaeopsis hardwickii',
 'Penaeus indicus':'Fenneropenaeus indicus','Penaeus japonicus':'Marsupenaeus japonicus',
 'Mierspenaeopsis sculptilis':'Parapenaeopsis sculptilis','Scyris indica':'Alectis indica',
 'Platycaranx malabaricus':'Carangoides malabaricus'}
authority=json.loads((root/'regions/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/mapping_review/taxonomy_authority_records.json').read_text(encoding='utf8'))
by_name={r['name']:r['records'] for r in authority}
checks['M2_same_taxon_bridge_checks']=[]
for r in d:
    if r['membership_rule']!='M2':continue
    n=r['taxon']; old=synonym_pairs[n]
    catch_ids={v['valid_AphiaID'] for v in by_name[n]}
    source_ids={v['valid_AphiaID'] for v in by_name[old]}
    valid=bool(catch_ids&source_ids)
    checks['M2_same_taxon_bridge_checks'].append({'catch_taxon':n,'source_name':old,'matching_valid_AphiaIDs':sorted(catch_ids&source_ids),'same_taxon_bridge':valid})
    if not valid:concerns.append({'taxon':n,'check':'M2_synonym','finding':'No identical accepted WoRMS taxon ID bridges source and catch name.'})

for r in d:
    if rank[r['overall_confidence']] != min(rank[r['membership_confidence']],rank[r['allocation_confidence']]): concerns.append({'taxon':r['taxon'],'check':'weakest_component','finding':'Overall confidence disagrees with necessary components.'})
    groups=r['proposed_groups']
    if len(groups)!=len({g['seq'] for g in groups}): concerns.append({'taxon':r['taxon'],'check':'candidate_unique','finding':'Duplicate group IDs.'})
    if any(not isinstance(g['weight'],(int,float)) or not math.isfinite(g['weight']) or g['weight']<0 for g in groups): concerns.append({'taxon':r['taxon'],'check':'weight_value','finding':'Invalid/missing weight.'})
    if abs(sum(g['weight'] for g in groups)-1)>1e-9: concerns.append({'taxon':r['taxon'],'check':'weight_sum','finding':'Weights do not sum to one.'})
    if r['allocation_rule']=='W4':
        vals=[g['native_model_catch_density'] for g in groups]
        if any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in vals) or sum(vals)<=0: concerns.append({'taxon':r['taxon'],'check':'catch_usable','finding':'W4 uses incomplete/nonpositive catch values.'})
        else:
            for g,v in zip(groups,vals):
                if abs(g['weight']-v/sum(vals))>1e-9: concerns.append({'taxon':r['taxon'],'check':'catch_weights','finding':'Weight does not match native catch density ratio.'})
                if v==0 and g['weight']!=0:concerns.append({'taxon':r['taxon'],'check':'zero_weight','finding':'Genuine zero catch candidate has nonzero weight.'})
                if g['common_area_km2']!=6205051:concerns.append({'taxon':r['taxon'],'check':'area_denominator','finding':'Common catch area is not whole-study-area6205051km².'})
                if abs(g['source_caught_mass_t']-v*6205051)>max(1e-6,abs(v*6205051)*1e-12):concerns.append({'taxon':r['taxon'],'check':'area_conversion','finding':'Source mass does not match native density times common area.'})

checks['mechanical_concerns']=concerns
(out/'independent_mapping_qa_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
print('MECHANICAL',json.dumps(checks,ensure_ascii=False))
