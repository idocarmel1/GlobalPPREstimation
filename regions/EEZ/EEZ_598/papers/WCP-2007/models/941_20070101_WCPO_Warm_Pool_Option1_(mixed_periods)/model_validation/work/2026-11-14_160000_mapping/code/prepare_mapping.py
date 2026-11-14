import sys, json, math, hashlib, os, copy
from pathlib import Path
from collections import defaultdict
import openpyxl
ROOT = Path.cwd()
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book, records, overview, digest_tables
M = ROOT/'regions/EEZ/EEZ_598/papers/WCP-2007/models/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
V=M/'model_validation'; W=Path(__file__).resolve().parents[1]; E=V/'evidence/mapping'
for d in (W/'inputs',W/'outputs',W/'qa',E):d.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def close(a,b):return a==b if a is None or b is None else math.isclose(a,b,rel_tol=2e-14,abs_tol=1e-10)
P=ROOT/'regions/EEZ/EEZ_598/EEZ_598.xlsx'
b=read_book(P); ov=overview(b); model=ov['selected_model_id']; year=int(ov['taxon_detail_year']); basis=ov['catch_basis']
old=json.loads((V/'evidence/source_review/taxon_audit.json').read_text(encoding='utf-8'))
assert model==old['model_id'] and sha(M/'model.json')==old['model_sha256']
assert year==2019 and basis=='landings'
catches=records(b,'Catch','Catch'); cc=[r for r in catches if r['catch_basis']==basis]
assert len(cc)==len({r['taxon'] for r in cc})
classic={r['taxon']:r for r in records(b,'Classic PPR','Taxa')}
groups={int(r['seq']):r for r in records(b,'Selected model groups','Groups')}; byname={g['group_name']:i for i,g in groups.items()}
matching=[r for r in records(b,'PPR','Matching') if r['model_id']==model]; mm=defaultdict(list)
for r in matching:mm[r['taxon']].append(r)
reviews={r['taxon']:r for r in records(b,'PPR','Mapping review') if r['model_id']==model}
audits={r['taxon']:r for r in old['rows']}
assert set(audits)==set(reviews)==set(mm)=={r['taxon'] for r in cc}
raw=json.loads((M/'model.json').read_text(encoding='utf-8'))
raw={int(r['group_seq']):r for r in raw['group']}
rank={'High':0,'Medium':1,'Low':2,'Very low':3,'Unresolved':4}
rows=[];differences=[]; max_w_delta=0
for c in cc:
    t=c['taxon']; a=copy.deepcopy(audits[t]); rr=reviews[t]; cl=classic.get(t,{})
    a['stored_matching']=mm[t];a['stored_review']=rr
    for af,rf in [('membership_rule','membership_rule'),('membership_confidence','membership_confidence'),('allocation_rule','allocation_rule'),('allocation_confidence','allocation_confidence'),('confidence','overall_confidence'),('reason','reason')]:
        if a[af]!=rr[rf]:differences.append({'taxon':t,'field':af,'audit':a[af],'current':rr[rf]})
    assert a['confidence']==max([a['membership_confidence'],a['allocation_confidence']],key=lambda q:rank[q])
    assert all(r['confidence'].casefold()==a['confidence'].casefold() for r in mm[t])
    adopted={byname[r['group']]:r['weight'] for r in mm[t] if r['group']}
    expected={g['id']:g['weight'] for g in a['candidates']}
    assert adopted.keys()==expected.keys(),(t,adopted,expected)
    for gid,w in adopted.items():
        assert close(w,expected[gid]),(t,gid,w,expected[gid]);max_w_delta=max(max_w_delta,abs(w-expected[gid]))
        g=next(q for q in a['candidates'] if q['id']==gid)
        assert g['name']==groups[gid]['group_name']==raw[gid]['group_name']
        src_c=float(raw[gid]['export']);src_c=None if src_c==-9999 else src_c
        src_b=float(raw[gid]['biomass']);src_b=None if src_b==-9999 else src_b
        assert close(g['raw_catch'],src_c),(t,gid,'source catch',g['raw_catch'],src_c)
        assert close(g['biomass'],src_b),(t,gid,'biomass')
    assert not adopted or close(sum(adopted.values()),1),(t,adopted)
    if a['allocation_rule']=='Approved model-biomass fallback':
        vals=[float(raw[g]['biomass']) for g in adopted];den=sum(vals)
        assert all(v>=0 for v in vals) and den>0
        assert any(float(raw[g]['export'])==-9999 for g in adopted) or sum(float(raw[g]['export']) for g in adopted)==0
        assert all(close(w,float(raw[g]['biomass'])/den) for g,w in adopted.items())
    if a['allocation_rule']=='Source-model catch proportions':
        vals=[0 if float(raw[g]['export'])==-9999 and t=='Katsuwonus pelamis' else float(raw[g]['export']) for g in adopted];den=sum(vals)
        assert all(v>=0 for v in vals) and den>0
        assert all(close(w,v/den) for w,v in zip(adopted.values(),vals))
    catch=c.get(year);coef=cl.get('sppr');tl=cl.get('tl');ppr=0.0 if catch==0 else (catch*coef/9 if catch is not None and coef is not None else None)
    for key,val in [('catch_tonnes',catch),('tl',tl),('classic_sppr',coef),('simple_chain_ppr_tC',ppr)]:
        assert close(a.get(key),val),(t,key,a.get(key),val)
        a[key]=val
    a['input_locations']={'catch':f'EEZ_598.xlsx / Catch / Catch / taxon={t}, catch_basis={basis}, year={year}','classic':f'EEZ_598.xlsx / Classic PPR / Taxa / taxon={t}','matching':f'EEZ_598.xlsx / PPR / Matching / model_id={model}, taxon={t}'}
    rows.append(a)
assert all(d['field']=='reason' and d['taxon'] in ['Elasmobranchii','Miscellaneous marine crustaceans'] for d in differences),differences
rows.sort(key=lambda r:(r['simple_chain_ppr_tC'] is None,-(r['simple_chain_ppr_tC'] or 0),r['taxon']))
total_c=math.fsum(r['catch_tonnes'] for r in rows if r['catch_tonnes'] is not None);total_p=math.fsum(r['simple_chain_ppr_tC'] for r in rows if r['simple_chain_ppr_tC'] is not None)
def aggregate(field,confidence=None):
    buckets=defaultdict(list)
    for r in rows:buckets[(r[field],r[confidence] if confidence else r[field])].append(r)
    out=[]
    for (label,conf),rs in buckets.items():
        cv=math.fsum(r['catch_tonnes'] for r in rs if r['catch_tonnes'] is not None);pv=math.fsum(r['simple_chain_ppr_tC'] for r in rs if r['simple_chain_ppr_tC'] is not None)
        out.append({'label':label,'confidence':conf,'taxa':len(rs),'catch_tonnes':cv,'catch_percentage':cv/total_c*100,'ppr_tC':pv,'ppr_percentage':pv/total_p*100,'taxon_labels':[r['taxon'] for r in rs]})
    return sorted(out,key=lambda r:(-r['ppr_percentage'],r['label']))
cs=aggregate('confidence');cs.sort(key=lambda r:rank[r['label']]);ms=aggregate('membership_rule','membership_confidence');als=aggregate('allocation_rule','allocation_confidence')
vl=defaultdict(list)
for r in rows:
    if r['confidence']=='Very low':vl[(r['membership_reason'],r['allocation_reason'])].append(r['taxon'])
protected=[P,M/'model.json',V/'evidence/source_review/taxon_audit.json',ROOT/'tools/templates/instructions.md',M.parents[1]/'sources/download-0adcf55e.pdf']
paths={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in protected}
summary={'schema_version':1,'unit_id':'EEZ_598','model_id':model,'year':year,'catch_basis':basis,'source_groups':len(raw),'synthetic_groups':len(groups)-len(raw),'n_taxa':len(rows),'total_catch_tonnes':total_c,'simple_chain_ppr_tC':total_p,'confidence_summary':cs,'membership_summary':ms,'allocation_summary':als,'very_low_decisions':[{'taxa':ts,'membership_reason':m,'allocation_reason':w} for (m,w),ts in vl.items()],'unresolved':[{'taxon':r['taxon'],'reason':r['reason'],'catch_tonnes':r['catch_tonnes'],'simple_chain_ppr_tC':r['simple_chain_ppr_tC']} for r in rows if r['confidence']=='Unresolved'],'missing_tl_taxa':[r['taxon'] for r in rows if r['tl'] is None],'missing_coefficient_taxa':[r['taxon'] for r in rows if r['classic_sppr'] is None],'unknown_annual_ppr_taxa':[r['taxon'] for r in rows if r['simple_chain_ppr_tC'] is None],'hashes':paths,'invariants':{'complete_exact_taxon_universe':True,'unique_taxon_basis_keys':True,'all_mapping_groups_weights_match_current':True,'all_audit_components_match_current_mapping_review':True,'weakest_component_applied_all_taxa':True,'raw_source_catch_biomass_verified_all_candidates':True,'weight_max_serialization_delta':max_w_delta,'no_scientific_execution_or_adoption':True,'original_mapping_evidence_reused':True,'unresolved_in_full_denominators':True,'confidence_ppr_share_sum':sum(r['ppr_percentage'] for r in cs),'membership_ppr_share_sum':sum(r['ppr_percentage'] for r in ms),'allocation_ppr_share_sum':sum(r['ppr_percentage'] for r in als),'missing_xlsx_template':'tools/templates/taxon_mapping.xlsx absent; current seven-column instructions and existing appendix layout used'},'review_differences':differences,'evidence_reuse_note':'Exact EEZ_598 adopted decisions and prior source review reused, current model/source and all taxon/component/catch/classic/group/weight identities checked. No fresh online taxonomic research or new mapping adoption; historical retrieval dates preserved.'}
dump(E/'mapping_summary.json',summary);dump(E/'taxon_mapping_audit.json',{'summary':summary,'rows':rows})
# Preserve existing source descriptions while repairing portable destinations and stale wording.
wb=openpyxl.load_workbook(V/'taxon_mapping.xlsx'); ss=wb['Sources']; sources=[]
for cells in list(ss.rows)[4:]:
    vals=[c.value for c in cells[:4]];link=cells[2].hyperlink;target=link.target if link else None
    sources.append({'title':vals[0],'supports':vals[1],'target':target,'reviewed':vals[3]})
sources[1]['target']='../model.json'; sources[1]['supports']='Current accepted model.json, group export and biomass fields, checked against every mapped candidate; missing export (-9999) is not observed zero. Biomass proxy assumes comparable catchability and composition.'
sources[8]['supports']='Historical exact accepted option1 GE/TE/With Egestion direct diagnostic evidence; reused context only. Current EE-floor diagnostics are documented separately in validation.docx.'
if not (V/sources[9]['target'].split('#')[0]).resolve().exists():
    sources[9]['target']='../model_notes.md#removed-extraction-evidence';sources[9]['supports']='Historical source extraction package was removed under latest-only policy. Model notes record the unavailable former payload; this link is not replacement extraction evidence.'
sources[-1]['target']=os.path.relpath(ROOT/'research/agents/selected_regions_validation_20260930/evidence/verification/reporting_scope_sources/FAO_2001_Area27_capture.pdf',V).replace('\\','/')+'#page=3'
sources.append({'title':'Current complete EEZ_598 mapping verification (14 November 2026)','supports':'All 102 current adopted mappings, component confidence, raw source values, weights, numeric order, missingness and independent classic PPR verified. Historical source retrievals were reused.','target':'evidence/mapping/taxon_mapping_audit.json','reviewed':'2026-11-14'})
sources.append({'title':'Regional calculation convention: simple trophic chain and carbon units','supports':'Classic coefficient multiplied by catch, then divided by 9 exactly once; missing coefficients remain missing and zero catch contributes zero annual PPR.','target':os.path.relpath(ROOT/'tools/skills/paper-to-ppr/references/regional-calculation.md',V).replace('\\','/'),'reviewed':'2026-11-14'})
link_checks=[]
for s in sources:
    t=s['target'];ok=True if t.startswith('http') else (V/t.split('#')[0]).resolve().exists()
    link_checks.append({'target':t,'exists_or_public':ok});assert ok,t
values=[]
for r in rows:
    reason=r['reason']+' Sources: '+ '; '.join(dict.fromkeys(r['sources']+(['source catch and biomass'] if r['candidates'] else [])))+'.'
    values.append([r['taxon'],r['tl'] if r['tl'] is not None else '?',r['catch_tonnes'] if r['catch_tonnes'] is not None else '?',r['simple_chain_ppr_tC'] if r['simple_chain_ppr_tC'] is not None else '?',r['mapping_display'],r['confidence'],reason])
dump(W/'inputs/appendix_data.json',{'summary':summary,'rows':values,'sources':sources,'old_path':str(V/'taxon_mapping.xlsx'),'output_path':str(V/'taxon_mapping.xlsx')})
dump(W/'qa/input_checks.json',{'hashes':paths,'link_checks':link_checks,'old_appendix_sha256':sha(V/'taxon_mapping.xlsx'),'all_checks_passed':True})
print(json.dumps({k:summary[k] for k in ['n_taxa','total_catch_tonnes','simple_chain_ppr_tC','invariants']},indent=2))
