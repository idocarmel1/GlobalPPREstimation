from pathlib import Path
import sys,json,hashlib,math,collections,urllib.parse,shutil
from openpyxl import load_workbook
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
from tools.project_core.workbooks.workbooks import read_book,records
MODEL=Path(__file__).resolve().parents[4]; RUN=Path(__file__).resolve().parents[1]
EVID=MODEL/'model_validation/evidence/source_review'; APP=MODEL/'model_validation/taxon_mapping.xlsx'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (RUN/'outputs'/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
audit=read(EVID/'taxon_audit.json'); summary=read(EVID/'coverage_summary.json'); alloc=read(EVID/'allocation_evidence.json')
book=read_book(ROOT/'regions/LME/LME_022/LME_022.xlsx',sheets=['Overview','Catch','Classic PPR','PPR'])
catch=records(book,'Catch','Catch'); catch=[r for r in catch if r['catch_basis']=='catch']; classic=records(book,'Classic PPR','Taxa')
ct={r['taxon']:r for r in catch}; cl={r['taxon']:r for r in classic}; au={r['taxon']:r for r in audit}
assert len(ct)==len(catch) and len(au)==len(audit) and len(cl)==len(classic)
qa={'current_region_sha256':sha(ROOT/'regions/LME/LME_022/LME_022.xlsx'),'canonical_sha256':sha(MODEL/'model.json'),'appendix_before_sha256':sha(APP),'universe_new':sorted(set(ct)-set(au)),'universe_removed':sorted(set(au)-set(ct)),'current_matching_rows':len(records(book,'PPR','Matching')),'numeric_differences':[],'appendix_differences':[],'weight_issues':[],'candidate_issues':[],'links':[]}
def equal(a,b): return a==b or (isinstance(a,(int,float)) and isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10))
for tax,r in au.items():
 c=ct.get(tax,{}).get(2019); coeff=cl.get(tax,{}).get('sppr'); tl=cl.get(tax,{}).get('tl')
 p=0 if c==0 else c*coeff/9 if c is not None and coeff is not None else None
 for k,x,y in [('catch_tonnes',c,r['catch_tonnes']),('tl',tl,r['tl']),('classic_coefficient_wet',coeff,r['classic_coefficient_wet']),('simple_chain_ppr_tC',p,r['simple_chain_ppr_tC'])]:
  if not equal(x,y): qa['numeric_differences'].append([tax,k,x,y])
 if r['groups'] and not math.isclose(sum(g['weight'] for g in r['groups']),1,abs_tol=1e-12): qa['weight_issues'].append(tax)
 if len(r['candidate_decisions'])!=26 or {x['seq'] for x in r['candidate_decisions']}!=set(range(1,27)): qa['candidate_issues'].append(tax)
w=load_workbook(APP,data_only=False); s=w['Taxon mapping']
ar=list(s.values)[7:]; assert len(ar)==len(audit)
for row in ar:
 r=au[row[0]]; expected=[r['taxon'],r['tl'] if r['tl'] is not None else '?',r['catch_tonnes'],r['simple_chain_ppr_tC'],r['mapping_display'],r['overall_confidence'],r['reason']+' Sources: '+'; '.join(r['sources'])+'.']
 for i,(x,y) in enumerate(zip(row,expected)):
  if not equal(x,y): qa['appendix_differences'].append([row[0],i,x,y])
qa['order_ok']=[r[0] for r in ar]==[r['taxon'] for r in sorted(audit,key=lambda r:(r['simple_chain_ppr_tC'] is None,-(r['simple_chain_ppr_tC'] or 0),r['taxon']))]
for sheet in w:
 for row in sheet:
  for c in row:
   if c.hyperlink:
    t=c.hyperlink.target
    exists=True if not t or t.startswith(('http:','https:')) else (APP.parent/urllib.parse.unquote(t.split('#')[0])).exists()
    qa['links'].append({'sheet':sheet.title,'cell':c.coordinate,'target':t,'location':c.hyperlink.location,'exists':exists,'blue':str(c.font.color),'underline':c.font.underline})
qa['tables']={sh.title:[{'name':t.name,'ref':t.ref,'filter':t.autoFilter.ref if t.autoFilter else None} for t in sh.tables.values()] for sh in w}
qa['all_catch_taxa_present']=set(ct)==set(au)
qa['retained_audit_sha256']=sha(EVID/'taxon_audit.json')
qa['retained_source_definitions_sha256']=sha(EVID/'source_group_definitions.json')
snapshot=MODEL/'results/regional_snapshot.xlsx'
if snapshot.exists():
 sb=read_book(snapshot,sheets=['Overview','PPR']); sr=records(sb,'PPR','Matching')
 qa['snapshot_sha256']=sha(snapshot); qa['snapshot_matching_rows']=len(sr)
 qa['snapshot_model_ids']=sorted(set(r['model_id'] for r in sr))
 keyed={}
 for r in sr: keyed.setdefault(r['taxon'],[]).append((r['group'],r['weight']))
 qa['snapshot_matching_differences']=[]
 for tax,r in au.items():
  got=sorted((str(x),y) for x,y in keyed.get(tax,[]) if x is not None)
  expected=sorted((g['group_name'],g['weight']) for g in r['groups'])
  if len(got)!=len(expected) or any(x[0]!=y[0] or not equal(x[1],y[1]) for x,y in zip(got,expected)): qa['snapshot_matching_differences'].append({'taxon':tax,'got':got,'expected':expected})
groups=collections.defaultdict(list)
for r in audit:
 if r['overall_confidence']=='Very low': groups[(r['membership_reason'],r['allocation_reason'])].append(r['taxon'])
low=[{'taxa':sorted(t),'reason':m+' '+a} for (m,a),t in groups.items()]
low.sort(key=lambda x:(-len(x['taxa']),x['taxa'][0]))
member_names={'M1':'Explicit source assignment','M2':'Verified synonym','M3':'Unambiguous documented group fit','M4':'Extension from listed representatives','M5':'Supported ecological assignment','M6':'Partial or conflicting ecological fit','M8':'No meaningful marine-group assignment','M9':'Assumed eligible group set','M10':'Broad-category approximation','M11':'Closest represented analogue'}
weight_names={'W1':'No split required','W4':'Source-model catch proportions, assumed transferable','W9':'Model-biomass proportions after incomplete source catch','W10':'No usable allocation for unresolved freshwater taxa'}
handoff={'scope':'Scotland candidate review; retained exact-model mapping, not current ICES mapping. No mapping adoption or regional refresh.','summary':summary,'confidence_rows':summary['confidence_summary'],'membership_rows':[dict(r,plain_language=member_names[r['rule']]) for r in summary['membership_summary']],'allocation_rows':[dict(r,plain_language=weight_names[r['rule']]) for r in summary['allocation_summary']],'very_low_decisions':low,'very_low_taxa_count':sum(len(x['taxa']) for x in low),'geography':read(EVID/'geography/geographic_assessment.json'),'limitations':['Current regional PPR/Matching is empty following ICES selection; this appendix reuses retained Scotland candidate decisions, not adopted current regional matching.','Historical source landings and biomass weights are assumptions transferred from Scotland 1991–1995 to North Sea 1950–2019 and total catch including discards.','Twelve freshwater taxa remain unresolved because no meaningful represented marine membership was established.','72 missing classic coefficients/TLs affect only zero-catch 2019 labels; all annual contributions are zero.','Source Main Species lists are representative, not exhaustive; source species and ecological category conflicts remain documented.'],'rule_code_note':'Retained audit uses W10 for unresolved weights, an older code; current template W10 means measured geographic allocation. The readable report must say unresolved/no usable allocation and must not imply direct geographic evidence.'}
save('mapping_verification.json',qa); save('report_handoff.json',handoff)
compact=collections.defaultdict(list)
for r in audit:
 if r['overall_confidence']!='Very low': continue
 m=r['membership_reason']; a=r['allocation_reason']
 if m.startswith('Unlisted marine/coastal'): reason='Large Dem. fish is a weak bottom-associated analogue. Taxonomy, reef or bathyal habitat, size and diadromous stages differ from source representatives; dedicated species groups are narrower. No split is required.'
 elif m.startswith('Mobile marine pelagic'): reason='Large Pelagics is a weak open-water analogue. Body size, feeding, taxonomy or offshore habitat differs from the source mackerel and horse-mackerel representatives. No split is required.'
 elif m.startswith('Unlisted small/deep'): reason='Small pelagics is a weak forage-fish analogue based on source pearlside/Argentina. Taxonomy or bathypelagic depth differs. No split is required.'
 elif m.startswith('Marine migratory salmonids'): reason='Large Pelagics approximates the marine predatory phase of migratory salmonids. Freshwater stages, migration and taxonomy are not represented. No split is required.'
 elif m.startswith('Chimaera shares'): reason='Sharks & rays is a weak cartilaginous, benthic-feeding analogue for chimaeras. Holocephalan body form and bathyal habitat differ. No split is required.'
 elif m.startswith('Bottom-surface echinoderm'): reason='Epifauna is a weak epibenthic analogue for echinoderms. Shellfish taxonomy, feeding and body form differ. No split is required.'
 elif m.startswith('Exact SAU taxon key100139') or m.startswith('Exact SAU taxon key100039'): reason='The provider-code bridge supports bony-fish scope, but residual composition across dedicated and pooled bony groups is unknown. Historical model-landings proportions proxy composition across the wider region, years and total catch including discards.'
 elif m.startswith('Exact SAU taxon key100239'): reason='Groundfish composition is unknown across dedicated and pooled bony groups, including benthic members of pelagic-named pools. Historical model-landings proportions add geographic, temporal and discard-transfer assumptions.'
 elif m.startswith('Exact SAU taxon key100339'): reason='Pelagic bony-fish composition among Herring, Small pelagics and Large Pelagics is unknown; mixed pools also contain demersal members. Historical model-landings proportions add geographic, temporal and discard-transfer assumptions.'
 elif m.startswith('Basking shark'): reason='Sharks & rays preserves a taxonomic connection, but basking-shark filter feeding and size differ sharply from the predatory source sharks. No split is required.'
 elif m.startswith('Cartilaginous-fish reporting'): reason='The broad category mixes represented sharks/rays with chimaeras requiring a weak body-form and depth analogue. Composition is unknown; a single pooled group adds no split uncertainty.'
 elif m.startswith('Provider Other demersal invertebrates'): reason='The broad demersal-invertebrate label has unknown composition across infauna, epifauna, crustaceans and benthic cephalopods in a mixed pool. Incomplete source catches trigger model-biomass weights with geographic, temporal and catch-basis transfer assumptions.'
 elif m.startswith('Unknown marine fish/finfish'): reason='The broad marine-fish category has unknown composition across dedicated and pooled fish groups. Model-landings proportions proxy composition across the wider region, years and total catch including discards.'
 elif m.startswith('Historical order-level'): reason='Historical order boundaries are heterogeneous and do not establish source-pool composition. '+('Source landings proxy the split between Large Dem. fish and Small pelagics, transferred across region, years and catch bases.' if r['allocation_rule']!='W1' else 'Large Dem. fish is an assumed pooled placement; no split is required.')
 elif m.startswith('Tunas/billfish'): reason='Large Pelagics is a weak open-water analogue for tunas/billfish. Large body size, oceanic habitat and feeding differ from mackerel/horse-mackerel representatives. No split is required.'
 else: raise ValueError(m)
 compact[reason].append(r['taxon'])
handoff['very_low_decisions_compact']=[{'taxa':sorted(t),'reason':reason} for reason,t in sorted(compact.items(),key=lambda x:(-len(x[1]),x[1][0]))]
save('report_handoff.json',handoff)
shutil.copy2(APP,RUN/'inputs/taxon_mapping_before.xlsx')
print(json.dumps({'numeric_diff_count':len(qa['numeric_differences']),'appendix_diff_count':len(qa['appendix_differences']),'snapshot_diff_count':len(qa.get('snapshot_matching_differences',[])),'broken_links':[r for r in qa['links'] if not r['exists']],'very_low_groups':len(low)},ensure_ascii=False,indent=2))
