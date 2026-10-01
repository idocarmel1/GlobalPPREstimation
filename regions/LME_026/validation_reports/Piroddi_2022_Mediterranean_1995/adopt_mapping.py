from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import json,sys,math,hashlib
OUT=Path(__file__).parent; ROOT=OUT.parents[3]; REGION=OUT.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import read_book,write_book,records,table_dict,sha,finite,overview,digest_tables
MODEL='Piroddi_2022_Mediterranean_1995'; bookpath=REGION/'LME_026.xlsx'
EXPECTED=sys.argv[1] if len(sys.argv)>1 else '71ca4f707f9fbff61c29cda2c2a0c6fd8320f681a477c1cec5b29557a035758b'
assert sha(bookpath)==EXPECTED,'Regional workbook changed since reviewed snapshot'
book=read_book(bookpath); before=read_book(bookpath)
baseline=ROOT/'original_research_archive/research/selected_regions_validation_20260930/baseline/LME_026'
modelpath=REGION/'models'/MODEL/'model.json'; model=json.loads(modelpath.read_text(encoding='utf-8'))
assert modelpath.read_bytes()==(baseline/'accepted_model.json').read_bytes()
groups={int(g['group_seq']):g for g in model['group']}
proposals=json.loads((OUT/'taxonomy_audit/taxonomy_mapping_proposals.json').read_text(encoding='utf-8'))['records']
catch={r['taxon']:r for r in records(book,'Catch','Catch') if r['catch_basis']=='landings'}
classic={r['taxon']:r for r in records(book,'Classic PPR','Taxa')}
assert len(proposals)==len(catch)==522 and {r['taxon'] for r in proposals}==set(catch)
stage={r['taxon']:json.loads(r['candidates']) for r in records(book,'Diagnostics','Blocked size allocation proposals')}
rank={'High':0,'Medium':1,'Low':2,'Very low':3,'Unresolved':4}
audit=[];matching=[];alloc=[];changes=[]
for p in proposals:
    t=p['taxon'];ids=p['candidate_group_ids'];assert ids and len(ids)==len(set(ids)) and all(i in groups for i in ids)
    quantities=[];landings=[]; biomass=[]
    for i in ids:
        g=groups[i]; raw=model['source_fisheries']['landings'].get(str(i))
        lv=sum((Decimal(v) for v in raw.values()),Decimal(0)) if raw is not None else None
        bv=Decimal(g['biomass']) if g.get('biomass') not in [None,'-9999'] else None
        landings.append(lv);biomass.append(bv)
        quantities.append({'seq':i,'group_name':g['group_name'],'source_landings_fleets_raw':raw,'source_landings_sum':str(lv) if lv is not None else None,'accepted_biomass_raw':g.get('biomass'),'source_total_removals_raw':g.get('export'),'source_discards_raw':g.get('source_discards')})
    trigger=None
    if len(ids)==1:
        weights=[1.];wr='W1';wc='High';reason='Complete allocation to the sole eligible group; no numerical split.';basis='one eligible group'
    elif t in stage:
        candidates=stage[t];assert set(ids)=={r['seq'] for r in candidates}
        weights=[next(r['weight'] for r in candidates if r['seq']==i) for i in ids]
        wr='W4';wc='Medium';basis='retained selected-model total removals (landings plus reported discards)'
        reason='Retain the four previously evidenced source Adult/Recruit total-removal proportions. Qualitative stage labels have no recovered quantitative cutoff; this fixed 1995 caught-mass proxy is transferred to unsized 1950–2019 regional catch and all catch bases.'
    elif all(v is not None and v>=0 for v in landings) and sum(landings)>0:
        total=sum(landings);weights=[float(v/total) for v in landings];wr='W4';wc='Medium';basis='37 source fleet landings per candidate, summed without loader-default zeros'
        reason='Complete selected-model source-landings proportions are a fixed composition proxy, not an observed 2019 taxon-specific caught-mass mixture. Applied across 1950–2019 years and all catch bases; source zeros remain candidates with zero weight.'
    else:
        trigger='Incomplete source landings' if any(v is None for v in landings) else 'All eligible source landings are zero'
        assert all(v is not None and v>=0 for v in biomass) and sum(biomass)>0, (t,ids,'Unusable biomass')
        total=sum(biomass);weights=[float(v/total) for v in biomass];wr='W9';wc='Medium';basis='complete accepted 1995 model biomass across all eligible candidates'
        reason=trigger+'. Complete accepted model biomass provides an explicitly assumed composition proxy, not observed caught mass. Fixed proportions are transferred across 1950–2019 years and all catch bases; no missing candidate is discarded.'
    assert math.isclose(math.fsum(weights),1,abs_tol=1e-12,rel_tol=0)
    overall=max([p['membership_confidence'],wc],key=rank.get)
    c=catch[t][2019];co=classic.get(t,{}).get('sppr');tl=classic.get(t,{}).get('tl')
    ppr=0. if c==0 else c*co/9 if finite(c) and finite(co) else None
    gs=[{'seq':i,'group_name':groups[i]['group_name'],'weight':w} for i,w in zip(ids,weights)]
    for q,w in zip(quantities,weights):q['weight']=w
    ar={'taxon':t,'model_id':MODEL,'allocation_rule':wr,'allocation_confidence':wc,'assumed_allocation':len(ids)>1,'basis':basis,'fallback_trigger':trigger,'candidates':quantities,'source_period':'1995 (supplement: 1990s)','source_units':model['source_fisheries']['units'],'applicable_catch_years':'1950–2019','applicable_catch_bases':['landings','catch','discards'],'reason':reason,'observed_taxon_specific_fractions_recovered':False,'retained_prior_stage_weights':t in stage}
    alloc.append(ar)
    reason_full=p['reason']+' Membership '+p['membership_confidence']+' ('+p['membership_rule']+'). '+reason+' Allocation '+wc+' ('+wr+'); overall '+overall+'.'
    if p['assumptions']:reason_full+=' Membership assumptions: '+'; '.join(p['assumptions'])+'.'
    r={'taxon':t,'model_id':MODEL,'year':2019,'catch_basis':'landings','catch_tonnes':c,'tl':tl,'classic_coefficient_wet':co,'simple_chain_ppr_tC':ppr,'groups':gs,'membership_rule':p['membership_rule'],'membership_confidence':p['membership_confidence'],'membership_reason':p['reason'],'membership_evidence':p['membership_evidence'],'membership_assumptions':p['assumptions'],'assumed_membership':p['assumed_membership'],'allocation_rule':wr,'allocation_confidence':wc,'allocation_reason':reason,'assumed_allocation':len(ids)>1,'overall_confidence':overall,'appendix_reason':reason_full,'authority_url':(p.get('authority_record') or {}).get('url'),'previous_mapping':[],'adoption':'adopted; source inventory only; model SPPR unavailable'}
    audit.append(r)
    for g in gs:
        if g['weight']>0:matching.append({'model_id':MODEL,'taxon':t,'group':g['group_name'],'weight':g['weight'],'confidence':overall,'evidence':'validation_reports/'+MODEL+'/adopted_taxon_audit.json; taxonomy_audit/taxonomy_mapping_proposals.json; allocation_evidence.json','explanation':reason_full})
    changes.append({'key':{'unit_id':'LME_026','model_id':MODEL,'taxon':t},'old':{'Matching':[],'membership_confidence':None,'allocation_confidence':None,'overall_confidence':None},'adopted':{'groups':gs,'membership_rule':p['membership_rule'],'membership_confidence':p['membership_confidence'],'allocation_rule':wr,'allocation_confidence':wc,'overall_confidence':overall,'assumed_membership':p['assumed_membership'],'assumed_allocation':len(ids)>1}})
inventory=[{'seq':i,**g,'inventory_provenance':'Exact accepted canonical JSON; initialized source inventory without runnable coefficients'} for i,g in groups.items()]
book['Selected model groups']['Groups']=table_dict(inventory)
book['PPR']['Matching']=table_dict(matching)
book['Diagnostics']['Taxon mapping review']=table_dict([{k:r[k] for k in ['model_id','taxon','membership_rule','membership_confidence','assumed_membership','allocation_rule','allocation_confidence','assumed_allocation','overall_confidence']} for r in audit])
book['Diagnostics']['Allocation assumptions']=table_dict([{'model_id':MODEL,'taxon':r['taxon'],'rule':r['allocation_rule'],'confidence':r['allocation_confidence'],'assumed':r['assumed_allocation'],'basis':r['basis'],'fallback_trigger':r['fallback_trigger'],'reason':r['reason'],'evidence':'validation_reports/'+MODEL+'/allocation_evidence.json'} for r in alloc])
book['Diagnostics']['Validation current review']=table_dict([{'model_id':MODEL,'review_date':'2026-09-30','taxa':522,'adopted_taxa':522,'source_groups_initialized':71,'source_model_sha256':sha(modelpath),'methods':'GE, TE, With Egestion NOT_RUN; existing strict/source and documented-default constructor evidence reused','historical_records':'September 28/29 source/no-selection and blocked-size records retained as dated history; Overview and this review govern current adoption','model_approval':False,'production_eligible':False}])
for s,n in [('Catch','Catch'),('Classic PPR','Taxa'),('NPP','NPP'),('NPP','Provenance')]:assert before.get(s,{}).get(n)==book.get(s,{}).get(n)
assert sha(bookpath)==EXPECTED,'Regional workbook changed immediately before save'
write_book(bookpath,book)
after=read_book(bookpath)
for s,n in [('Catch','Catch'),('Classic PPR','Taxa'),('NPP','NPP'),('NPP','Provenance')]:assert digest_tables(before.get(s,{}).get(n))==digest_tables(after.get(s,{}).get(n))
def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=True,allow_nan=False),encoding='utf-8')
save('adopted_taxon_audit.json',audit);save('allocation_evidence.json',{'schema_version':1,'model_sha256':sha(modelpath),'records':alloc});save('mapping_changes.json',changes)
tc=math.fsum(r['catch_tonnes'] for r in audit);pp=math.fsum(r['simple_chain_ppr_tC'] for r in audit if r['simple_chain_ppr_tC'] is not None)
summary={'taxa_count':len(audit),'total_catch_tonnes':tc,'total_simple_chain_ppr_tC':pp,'year':2019,'basis':'landings','conversion':'catch tonnes * preserved classic wet coefficient / 9 once','missing_classic_coefficients':[r['taxon'] for r in audit if r['classic_coefficient_wet'] is None],'positive_catch_unknown_ppr':[r['taxon'] for r in audit if r['catch_tonnes']>0 and r['simple_chain_ppr_tC'] is None],'categories':{},'membership_rules':[],'allocation_rules':[]}
for level in rank:
    rows=[r for r in audit if r['overall_confidence']==level];cs=math.fsum(r['catch_tonnes'] for r in rows);ps=math.fsum(r['simple_chain_ppr_tC'] for r in rows if r['simple_chain_ppr_tC'] is not None)
    summary['categories'][level]={'taxa_count':len(rows),'catch_tonnes':cs,'ppr_tC':ps,'catch_percent':100*cs/tc,'ppr_percent':100*ps/pp}
for key,ck,dest in [('membership_rule','membership_confidence','membership_rules'),('allocation_rule','allocation_confidence','allocation_rules')]:
    for rule,conf in sorted(set((r[key],r[ck]) for r in audit)):
        rr=[r for r in audit if r[key]==rule and r[ck]==conf];ps=math.fsum(r['simple_chain_ppr_tC'] for r in rr if r['simple_chain_ppr_tC'] is not None)
        summary[dest].append({'rule':rule,'confidence':conf,'taxa_count':len(rr),'ppr_tC':ps,'ppr_percent':100*ps/pp})
save('coverage_summary.json',summary)
save('qa/adoption_freshness.json',{'expected_reviewed_sha256':EXPECTED,'checked_on_read':True,'checked_immediately_before_save':True,'adopted_workbook_sha256':sha(bookpath),'canonical_model_sha256':sha(modelpath),'canonical_model_bytes_equal_baseline':True,'protected_tables_preserved':True,'matching_rows':len(matching),'source_groups':71,'adopted_taxa':522,'parameter_corrections':[]})
print(json.dumps({'taxa':522,'matching_rows':len(matching),'categories':summary['categories'],'allocation_rules':summary['allocation_rules'],'expected_calculate_workbook_sha256':sha(bookpath)},ensure_ascii=True))
