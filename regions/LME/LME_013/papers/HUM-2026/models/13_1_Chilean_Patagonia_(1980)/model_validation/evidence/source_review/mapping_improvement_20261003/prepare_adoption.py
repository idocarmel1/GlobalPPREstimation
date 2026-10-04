from pathlib import Path
from collections import defaultdict,Counter
from copy import deepcopy
import json,sys,math,hashlib
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).parent;ROOT=OUT.parents[4];REG=ROOT/'regions/LME_013'
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import records,overview,table_dict,digest_tables,input_hash,validate_region
from regional import recalculate,result_hash,set_setting,set_result_hash
def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
base=load('baseline_tables.json');b=deepcopy(base);inputs=load('review_inputs.json')
rank={'High':4,'Medium':3,'Low':2,'Very low':1,'Unresolved':0}
group_rows=records(base,'Selected model groups','Groups');group_by_name={r['group_name']:r for r in group_rows};group_by_id={r['seq']:r for r in group_rows}
model=overview(base)['selected_model_id'];decisions=load('reconciled_decisions.json')
assert set(decisions)=={r['taxon'] for r in inputs} and len(decisions)==218
old={r['taxon']:r for r in inputs};ledger=[];newmatching=[];newreview=[]
evidence='validation_reports/13_1_Chilean_Patagonia_(1980)/mapping_improvement_20261003/decision_ledger.json'
def signature(m):return sorted((r['group'],float(r['weight'])) for r in m if r.get('group'))
for taxon in sorted(decisions):
    r=deepcopy(decisions[taxon]);prev=old[taxon];m=r['new_mappings']
    assert all(v['group'] in group_by_name and v.get('seq',group_by_name[v['group']]['seq'])==group_by_name[v['group']]['seq'] for v in m)
    assert len({v['group'] for v in m})==len(m)
    assert all(isinstance(v['weight'],(int,float)) and v['weight']>=0 and math.isfinite(v['weight']) for v in m)
    assert math.isclose(math.fsum(v['weight'] for v in m),1,abs_tol=1e-9,rel_tol=0)
    overall=min([r['membership_confidence'],r['allocation_confidence']],key=rank.get)
    assert r['overall_confidence']==overall
    numerical=signature(m)!=signature(prev['matching'])
    prior=prev['old_review'];confidence_changed=any(prior[k]!=r[k] for k in ['membership_confidence','allocation_confidence','overall_confidence'])
    rules_changed=any(prior[k]!=r[k] for k in ['membership_rule','allocation_rule'])
    r.update({'model_id':model,'year':2019,'catch_basis':'landings','old_mappings':prev['matching'],'old_components':prior,'provider':prev['provider'],'catch_tonnes':prev['catch_tonnes'],'tl':prev['tl'],'classic_sppr_wet':prev['classic_sppr_wet'],'simple_chain_ppr_tC':prev['simple_chain_ppr_tC'],'baseline_method_exposure_tC':prev['method_exposure_tC'],'numerical_mapping_changed':numerical,'confidence_changed':confidence_changed,'rules_changed':rules_changed,'decision_type':'numerical mapping change' if numerical else 'confidence-only change' if confidence_changed else 'rule/evidence reassessment' if rules_changed else 'retained decision','adoption_state':'adopted in regional workbook; researcher review and shared update deferred','assumed_membership':r['membership_rule'] not in ['M1','M2','M3'],'assumed_allocation':r['allocation_rule']!='W1'})
    ledger.append(r)
    for v in sorted(m,key=lambda v:group_by_name[v['group']]['seq']):
        if v['weight']>0:newmatching.append({'model_id':model,'taxon':taxon,'group':v['group'],'weight':v['weight'],'confidence':overall,'evidence':evidence,'explanation':r['reason']})
    newreview.append({k:r[k] for k in ['model_id','taxon','membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence','assumed_membership','assumed_allocation']}|{'evidence':evidence})
b['PPR']['Matching']=table_dict(newmatching)
b['Diagnostics']['Taxon mapping validation']=table_dict(newreview)
b['PPR']['Mapping review']=table_dict([r|{'reason':decisions[r['taxon']]['reason']} for r in newreview])
# Reconcile assumption rows; retain excluded historical candidates at weight zero,
# explicitly distinct from observed source zeros.
alloc=records(base,'PPR','Allocation assumptions');alloc_by_taxon=defaultdict(list)
source_values={}
for source in json.loads((OUT.parent/'allocation_evidence.json').read_text(encoding='utf-8')):
    for candidate in source.get('candidates',[]):source_values[candidate['group_name']]=candidate
for r in alloc:alloc_by_taxon[r['taxon']].append(r)
new_alloc=[]
for r in ledger:
    taxon=r['taxon'];m=r['new_mappings'];prior=alloc_by_taxon.get(taxon,[])
    if len(m)==1 and not prior:continue
    names={v['group'] for v in m}|{v['group'] for v in prior}
    weights={v['group']:v['weight'] for v in m}
    for name in sorted(names,key=lambda n:group_by_name[n]['seq']):
        row=deepcopy(next((v for v in prior if v['group']==name),{}));g=group_by_name[name]
        row.update({'model_id':model,'taxon':taxon,'group':name,'seq':g['seq'],'weight':weights.get(name,0),'rule':r['allocation_rule'],'confidence':r['allocation_confidence'],'source_biomass':g['biomass'],'years_applied':'1950–2019','catch_bases_applied':'landings; catch; discards','evidence':evidence,'limitations':r.get('allocation_reason',r['reason'])+(' Former candidate excluded by reviewed reporting/group scope; weight zero is an allocation exclusion, not an observed catch zero.' if name not in weights else ''),'eligibility':'included' if name in weights else 'excluded','prior_mapping':json.dumps(r['old_mappings'],ensure_ascii=False,separators=(',',':'))})
        if not prior:
            candidates=r.get('allocation_candidates',[])
            c=next((v for v in candidates if v.get('group',v.get('group_name'))==name),source_values.get(name,{}))
            row['source_catch']=c.get('source_catch_value',c.get('source_catch'))
            row['source_catch_raw']=c.get('source_landings_raw',c.get('source_catch_raw'))
            row['loaded_catch']=g['catch'];row['source_biomass_raw']=str(g['biomass'])
        new_alloc.append(row)
b['PPR']['Allocation assumptions']=table_dict(new_alloc)
changed_numerical=[r['taxon'] for r in ledger if r['numerical_mapping_changed']]
assert changed_numerical
# Only saved coefficients enter this arithmetic; this never calls a SPPR engine.
recalculate(b,REG/'LME_013.xlsx')
# Retain independent classic outputs byte-for-value; mapping changes cannot affect them.
b['Classic PPR']=deepcopy(base['Classic PPR'])
for blocks in b.values():
    for name,(header,rows) in list(blocks.items()):
        blocks[name]=[header,[[None if v=='' else v for v in row] for row in rows]]
set_result_hash(b)
set_setting(b,'source_note','PROVISIONAL: all 218 catch labels reassessed against exact source definitions and regional reporting evidence. See '+evidence+'. Fixed Chilean Patagonia 1980 coefficients remain a geographic/temporal transfer; retained direct configurations WARN and production eligibility false.')
set_setting(b,'calculation_input_sha256',input_hash(b))
validate_region(b,REG/'LME_013.xlsx')
for s in ['Catch','Classic PPR','Selected model groups','NPP']:assert b[s]==base[s],s
for name,block in base['Diagnostics'].items():
    if name!='Taxon mapping validation':assert b['Diagnostics'][name]==block,name
o0,o1=overview(base),overview(b)
for k in ['selected_model_id','model_path','results_model_sha256','results_model_id','catch_basis','taxon_detail_year','transfer_efficiency','npp_policy','selection_rationale','computational_runtime_evidence','computational_state_sha256','production_eligible']:assert o0[k]==o1[k],k
taxon_sppr={(r['taxon'],r['scope']+'|'+r['method']):r['sppr'] for r in records(b,'PPR','Taxon SPPR')}
for r in ledger:r['revised_method_exposure_tC']={k:r['catch_tonnes']*taxon_sppr[r['taxon'],k]/9 if isinstance(taxon_sppr[r['taxon'],k],(int,float)) else None for k in r['baseline_method_exposure_tC']}
save('decision_ledger.json',ledger);save('adopted_tables.json',b)
changed={s:{n:block for n,block in blocks.items() if base.get(s,{}).get(n)!=block} for s,blocks in b.items()};changed={s:t for s,t in changed.items() if t}
save('regional_changed_blocks.json',changed)
den=math.fsum(r['simple_chain_ppr_tC'] for r in ledger if r['simple_chain_ppr_tC'] is not None);catchden=math.fsum(r['catch_tonnes'] for r in ledger)
def summaries(key_rows):
    out=[]
    for q in rank:
        selected=[r for r,c in key_rows if c==q];catch=math.fsum(r['catch_tonnes'] for r in selected);p=math.fsum(r['simple_chain_ppr_tC'] for r in selected if r['simple_chain_ppr_tC'] is not None)
        out.append({'label':q,'taxa':len(selected),'catch_tonnes':catch,'ppr_tC':p,'catch_percentage':100*catch/catchden,'ppr_percentage':100*p/den})
    return out
components={}
for component in ['membership','allocation']:
    pools=defaultdict(list)
    for r in ledger:pools[r[component+'_rule'],r[component+'_confidence']].append(r)
    components[component]=sorted([{'rule':k[0],'confidence':k[1],'taxa':len(v),'ppr_percentage':100*math.fsum(r['simple_chain_ppr_tC'] or 0 for r in v)/den} for k,v in pools.items()],key=lambda r:-r['ppr_percentage'])
annual=[]
def annual_key(r):return tuple(r[k] for k in ['scope','method','catch_basis','unidentified','metric'])
a0={annual_key(r):r for r in records(base,'PPR','Annual')};a1={annual_key(r):r for r in records(b,'PPR','Annual')}
for key,v in a1.items():
    oldv=a0[key];year=2019
    annual.append({'scope':key[0],'method':key[1],'basis':key[2],'unidentified':key[3],'metric':key[4],'baseline':oldv.get(year),'revised':v.get(year),'baseline_status':oldv['status'],'revised_status':v['status'],'units':'wet tonnes'})
summary={'year':2019,'catch_basis':'landings','taxa':218,'source_ecological_groups':15,'synthetic_import_groups':1,'total_catch_tonnes':catchden,'total_simple_chain_ppr_tC':den,'baseline_confidence':summaries([(r,r['old_components']['overall_confidence']) for r in ledger]),'revised_confidence':summaries([(r,r['overall_confidence']) for r in ledger]),'membership_summary':components['membership'],'allocation_summary':components['allocation'],'numerical_mapping_changes':changed_numerical,'confidence_only_changes':[r['taxon'] for r in ledger if r['confidence_changed'] and not r['numerical_mapping_changed']],'very_low_taxa':sorted(r['taxon'] for r in ledger if r['overall_confidence']=='Very low'),'missing_classic_coefficients':[r['taxon'] for r in ledger if r['classic_sppr_wet'] is None],'positive_catch_unknown_ppr':[r['taxon'] for r in ledger if r['simple_chain_ppr_tC'] is None],'regional_2019_comparison':annual,'changed_tables':{s:list(t) for s,t in changed.items()},'shared_update':'deferred by explicit user review gate; Project/map/trends/archive/knowledge graph untouched; no researcher approval registered','solver_execution':False}
save('comparison_summary.json',summary)
print(json.dumps({'numerical_changes':changed_numerical,'confidence_only':summary['confidence_only_changes'],'final_confidence_counts':dict(Counter(r['overall_confidence'] for r in ledger)),'changed_tables':summary['changed_tables']},ensure_ascii=False,indent=2))
