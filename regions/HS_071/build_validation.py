"""HS_071 review/adoption builder. Scientific input blocks are immutable."""
import sys,json,math,shutil,csv,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];REG=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import set_setting,recalculate,set_result_hash
MID='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
OUT=REG/'validation_reports'/MID;QA=OUT/'qa';QA.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'original_research_archive/research/selected_regions_validation_20260930/baseline/HS_071'
b=read_book(BASE/'HS_071.xlsx');o=overview(b);model=REG/o['model_path'];m=json.loads(model.read_text(encoding='utf-8'))
assert sha(model)==sha(BASE/'accepted_model.json')
groups={int(r['seq']):r for r in records(b,'Selected model groups','Groups')}
raw={int(g['group_seq']):g for g in m['group']}
catch={r['taxon']:r for r in records(b,'Catch','Catch') if r['catch_basis']=='landings'}
classic={r['taxon']:r for r in records(b,'Classic PPR','Taxa')}
old=records(b,'PPR','Matching');old_by={t:[r for r in old if r['taxon']==t] for t in catch}
levels=['High','Medium','Low','Very low','Unresolved'];dec={}
def add(names,ids,rule,conf,reason,sources=('source definitions','catch classification')):
 for t in names.split('|'):
  if t not in catch: continue
  assert t not in dec,t
  dec[t]={'candidate_ids':ids,'membership_rule':rule,'membership_confidence':conf,'membership_reason':reason,'sources':list(sources)}
add('Acanthocybium solandri|Coryphaena hippurus',[8],'Explicit source assignment','High','Table 1 explicitly names wahoo and includes Coryphaenidae; each catch label fits the piscivorous group without a required split.')
add('Alopias|Carcharhinus falciformis|Carcharhinus longimanus|Isurus|Isurus oxyrinchus|Lamnidae|Sphyrna',[4,10],'Unambiguous documented group fit','High','Source Other Sharks explicitly includes Alopiidae, Carcharhinidae, Lamnidae and Sphyrnidae; Small Sharks covers the same species. The provider reports sharks, not rays/chimaeras; size uncertainty concerns allocation within this union.')
add('Prionace glauca',[3,10],'Explicit source assignment','High','Prionace glauca is the explicit Blue Shark member; Small Sharks covers the same species. The pooled juvenile catch is a proxy for this taxon.')
add('Xiphias gladius',[1,9],'Explicit source assignment','High','Xiphias gladius is explicitly assigned to Swordfish and its small stage.')
add('Istiompax indica|Kajikia audax',[2,9],'Verified synonym','High','NCBI current entries connect Istiompax indica to source Makaira indica and Kajikia audax to source Tetrapturus audax. Both occur in Other Billfish and its small-stage union.',('source definitions','billfish synonyms','catch classification'))
add('Istiophoridae',[2,9],'Assumed eligible group set','Medium','Source lists the locally relevant marlin/sailfish/spearfish members; the family reporting category is approximated by Other Billfish plus Small Billfish, excluding separate Xiphias. Exact unidentified family composition and historical taxonomic scope are not measured.')
add('Katsuwonus pelamis',[7,13,14],'Explicit source assignment','High','Explicit skipjack adult, small and infant source compartments. Table 1 and PDF15 disagree on the infant boundary; this is an allocation limitation within the verified species union.')
add('Thunnus albacares',[6,12],'Explicit source assignment','High','Explicit yellowfin adult/small compartments, divided at 120 cm (50% maturity); regional caught-size shares are unobserved.')
add('Thunnus obesus',[5,11],'Explicit source assignment','High','Explicit bigeye adult/small compartments, divided at 124 cm (50% maturity); regional caught-size shares are unobserved.')
add('Carangidae|Decapterus|Elagatis bipinnulata',[8,16,17],'Assumed eligible group set','Medium','Carangidae occurs in both Piscivorous fish and Epi fish; Epi small fish is the latter larval/juvenile pool. Genus/species membership is consistent with the family, but unresolved trophic/size boundaries require this eligible-set inference.')
add('Caranx',[8,16,17],'Partial or conflicting ecological fit','Low','Caranx belongs to the explicitly overlapping Carangidae pools, but its provider reef-associated category is only partly represented by pelagic forage and piscivorous compartments.')
add('Exocoetidae',[16,17],'Explicit source assignment','High','Flyingfishes are an explicitly named Epi fish family; Epi small fish contains their larval/juvenile stages. The family union is supported; stage composition is assumed.')
add('Balistidae|Holocentridae|Lethrinidae|Serranidae',[16,17],'Partial or conflicting ecological fit','Low','Family is explicitly listed in Epi fish and its small stage, but provider reef-associated catches may be benthic adults outside the pelagic forage inventory; this partial ecological fit is retained.')
add('Clupeidae|Clupeiformes|Pellona ditchela',[16,17],'Extension from listed representatives','Medium','Final Epi fish includes Engraulidae and other small pelagic fishes. Clupeidae occurs in the removed initial Epipelagic forage definition, not the final explicit list. A small-pelagic lineage/ecology extension is assumed rather than treating initial membership as final evidence.',('source definitions','FAO family identification','catch classification'))
add('Scomber|Scomberomorus',[8,16,17],'Assumed eligible group set','Medium','FAO places these genera within source-listed Scombridae. Both residual piscivorous small scombrids and Epi fish/small fish are plausible; exact caught sizes and partition boundaries are not documented.',('source definitions','FAO family identification','catch classification'))
add('Scombridae',[5,6,7,8,11,12,13,14,16,17],'Broad-category approximation','Very low','Provider category includes mackerels, tunas and bonitos. Named tuna stages and residual scombrid pools are approximated together; unlisted taxa and exact composition remain unknown. Wahoo is represented in Piscivorous fish; source data do not identify this family catch mix.',('source definitions','FAO family identification','catch classification'))
add('Thunnus alalunga|Thunnus orientalis',[5,11],'Closest represented analogue','Very low','Neither species is a source member. Bigeye adult/small compartments are a weak Thunnus analogue: FAO records deeper use by albacore and bluefin/bigeye, but species, temperature and maturity thresholds differ. Yellowfin/skipjack and generic forage are excluded from this explicit closest-analogue assumption.',('source definitions','FAO tuna ecology','catch classification'))
add('Sphyraena|Chirocentrus',[8],'Supported ecological assignment','Medium','Provider large pelagic fish and FAO piscivorous coastal/pelagic ecology support a non-enumerated extension of Piscivorous fish. Source definition is non-exhaustive; inclusion is an ecological assumption.',('source definitions','FAO family identification','catch classification'))
add('Trichiurus',[22],'Partial or conflicting ecological fit','Low','Trichiuridae is explicitly listed in Meso fish + other, but that source compartment specifies juvenile mesopelagic members. Provider large benthopelagic hairtail catch may include adults or shallower species, so a partial source fit is assumed.')
add('Gerreidae|Labridae|Lutjanidae|Lutjanus|Lutjanus argentimaculatus|Mugilidae|Mullidae|Upeneus|Drepane|Plotosidae|Plotosus|Pristipomoides|Sparidae|Cynoglossus|Chanos chanos',[16,17],'Closest represented analogue','Very low','These coastal, reef, demersal or benthopelagic fish lack explicit final-model membership. Epi fish and its small stage are the closest usable fish pools, with real habitat/feeding and adult-stage mismatch. Provider ecological category and FAO family context support only this weak analogue.',('source definitions','FAO coastal fish ecology','catch classification'))
add('Marine fishes not identified|Perciformes',[16,17],'Broad-category approximation','Very low','Provider reports a broad demersal fish category; no local composition study assigns it to source species. Epi fish and its small stage provide a weak mixed-fish composition proxy, with demersal habitat and omitted-species mismatch.')
add('Marine pelagic fishes not identified',[8,16,17,20,22,24,26],'Broad-category approximation','Very low','Medium pelagic fish reporting lacks measured species/size composition. Approximate with every residual fish-bearing pool: piscivorous, epipelagic/small, mesopelagic and highly migratory/bathypelagic forage. Table 1 names fish in HM Bathy forage (24) and Bathy forage (26); their deep habitat and mixed invertebrates weaken the proxy but do not justify omitting them from this Very low composition assumption. Dedicated tuna, billfish and sharks are excluded under the explicit separate-reporting assumption, not inferred absence. M Bathy forage (25) has only mollusc/crustacean representatives; other invertebrate/basal pools are excluded. Provider size bins are not observations of caught sizes.')
add('Chondrichthyes',[3,4,10],'Broad-category approximation','Very low','Provider sharks/rays/skates/chimaeras category crosses model boundaries. Blue Shark, Other Sharks and Small Sharks supply a weak represented-shark proxy; rays and chimaeras have no corresponding compartment and their unknown contribution is a genuine limitation.')
add('Elasmobranchii',[3,4,10],'Broad-category approximation','Very low','Elasmobranchii reports sharks, rays and skates; chimaeras are outside this target scope (FAO 3.1.1). Blue Shark, Other Sharks and Small Sharks supply a weak represented-shark proxy; unrepresented rays/skates remain an unknown component.')
add('Dendrobranchiata|Miscellaneous marine crustaceans',[15,24,25],'Broad-category approximation','Very low','Source Epi crust and migratory forage explicitly contain pelagic crustaceans, Sergestidae and Penaeoidea. Reporting also includes benthic shrimps/crabs/lobsters; the three mixed pools provide a weak crustacean proxy with habitat and taxonomic mismatch.')
add('Mollusca',[18,19,21,23,24,25,26],'Broad-category approximation','Very low','Reported clams, snails, squid and octopuses span unrepresented benthic molluscs and represented pelagic molluscs. Use epipelagic/mesopelagic mollusc pools plus all three bathypelagic mollusc-bearing forage pools, including HM Bathy forage with Liocranchia squid, as a weak composite; no claim of complete taxonomic coverage.',('source definitions','FAO octopod ecology','catch classification'))
add('Octopodidae',[18,19],'Closest represented analogue','Very low','FAO defines Octopodidae as benthic octopuses. Surface pelagic Argonautidae in Epi mollusc and its small stage are the closest usable octopod analogue, with a substantial benthic/pelagic mismatch; deeper gelatinous octopod pools are excluded.',('source definitions','FAO octopod ecology','catch classification'))
add('Bivalvia|Echinodermata',[],'No meaningful assignment','Unresolved','Clams and echinoderms are demersal invertebrates with no corresponding taxonomic/feeding guild in this pelagic model. Available squid, gastropod, crustacean and zooplankton pools are not a defensible biological analogue; no arbitrary basal assignment is made.')
add('Thunnus maccoyii',[5,11],'Closest represented analogue','Very low','Southern bluefin is absent from the final source model. CCSBT describes temperate southern-hemisphere distribution and deep oceanic use; the bigeye adult/small pair is the closest represented deep-diving Thunnus analogue. Species, thermal range and maturity thresholds differ substantially; this is a weak taxonomic/functional assumption, not native warm-pool membership.',('source definitions','CCSBT southern bluefin','FAO tuna ecology','catch classification'))
assert set(dec)==set(catch),(set(catch)-set(dec))
SRC=[
 {'label':'source definitions','title':'Allain et al. 2007 final Table 1 PDF9, stage prose PDF15, Tables 3/5/6 PDF11/14/19','target':'papers/WCP-2007/download-0adcf55e.pdf#page=9','supports':'Final source membership and stages; blue removed initial groups are excluded; overlapping fish pools and infant cutoff conflict retained.'},
 {'label':'source catch and biomass','title':'Accepted Option1 raw JSON; Table 5 fisheries landings and Table 6 biomass','target':o['model_path'],'supports':'Catch/biomass source fields and exact retained variant. Unknown -9999 exports are not source zeros. Complete biomass proportions are assumed composition/catchability, not observed regional catch shares.'},
 {'label':'catch classification','title':'HS_071 Catch/Catch, Sea Around Us exact reporting labels and ecological categories','target':'HS_071.xlsx','supports':'2019 landings and regional reporting scope. Provider size bins do not establish caught-fish sizes.'},
 {'label':'classic coefficient','title':'HS_071 Classic PPR/Taxa saved TL/coefficient and recorded provenance','target':'HS_071.xlsx','supports':'Independent simple-chain PPR: unchanged saved wet-weight coefficient times regional catch /9 once. TL and coefficients remain unchanged.'},
 {'label':'billfish synonyms','title':'NCBI Istiompax indica 13603 and Kajikia audax 13721 taxonomy entries','target':'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=13603','supports':'Full entries read 2026-09-30 establish source Makaira indica and Tetrapturus audax synonyms. Kajikia: https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=13721. Synonyms establish membership, not stage mass shares.'},
 {'label':'FAO tuna ecology','title':'FAO Y0490E tuna and billfish biology, vertical habitat and life histories','target':'https://www.fao.org/4/y0490e/y0490e04.htm','supports':'Relevant full text read 2026-09-30 supports deep-diving Thunnus analogue for albacore and bluefins; species, thermal and maturity mismatch remains. No HS071 caught-mass weights.'},
 {'label':'CCSBT southern bluefin','title':'CCSBT About Southern Bluefin Tuna','target':'https://www.ccsbt.org/en/content/about-southern-bluefin-tuna','supports':'Read 2026-09-30: southern temperate distribution and deeper oceanic habitat. Supports only a weak bigeye-pair analogue for Thunnus maccoyii, which has zero 2019 landings.'},
 {'label':'diagnostics','title':'Exact accepted Option1 full direct returns and 32 by 4 source contribution matrices','target':'validation_reports/'+MID+'/reused_diagnostics/direct_diagnostics.json','supports':'GE, TE and With Egestion all WARN; strict mass balance false; no negative source entries. Independent full-array check retained separately; no new solver executed.'},
 {'label':'reconstruction provenance','title':'Original WCP-2007 final source extraction and reconstruction audit','target':'../EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)/extracted_tables/REPORT.md','supports':'Source tables/initial-final distinctions, eight imports, missing/default fields, multistanza limits and original source reconstruction FAIL. Distinct from accepted Option1 WARN.'},
 {'label':'stage data search','title':'Regional stage-composition review with retained 2026-09-29 WCPFC/SPC search and 2026-09-30 HS071 checks','target':'validation_reports/'+MID+'/source_review.md#stage-allocation','supports':'No matching HS071 all-fleet raised 2019 caught-mass shares recovered at exact source stage thresholds; primary annual geographic catches alone do not provide stage weights.'}
]
needed=set(x for d in dec.values() for x in d['sources'])|{'source catch and biomass','classic coefficient','diagnostics','reconstruction provenance','stage data search'}
SRC=[r for r in SRC if r['label'] in needed]
out=[];mappings=[];alloc=[];deltas=[]
ah=['unit_id','model_id','taxon','rule','confidence','weight_evidence','definition','evidence','limitations','source_period','online_search','previous_mapping','years_applied','catch_bases_applied','rule_details','source_catch_basis','temporal_and_basis_assumption','group','seq','source_catch','canonical_export_raw','loaded_catch','catch_state','weight','effective_source_catch','catch_assumption']
for t in sorted(catch):
 d=dec[t];ids=d['candidate_ids'];cs=catch[t];ci=classic.get(t,{})
 raw_c=[float(raw[i]['export']) if float(raw[i]['export'])>=0 else None for i in ids]
 bio=[float(raw[i]['biomass']) if float(raw[i]['biomass'])>=0 else None for i in ids]
 if not ids:weights=[];wr='No usable allocation';wc='Unresolved';why='No eligible compartment.'
 elif len(ids)==1:weights=[1.];wr='No split required';wc='High';why='Entire taxon assigned to the sole eligible group.'
 elif t=='Katsuwonus pelamis':
  # Preserve the previously accepted explicitly uncaught infant proxy, not a printed zero.
  total=math.fsum(v for v in raw_c if v is not None);weights=[(v or 0)/total for v in raw_c];wr='Source-model catch proportions';wc='Medium';why='Accepted historical landings proxy retained: infant catch is missing in source, explicitly assumed uncaught for this existing skipjack split. Not a measured zero. Stage cutoff conflict retained.'
 elif all(v is not None and math.isfinite(v) and v>=0 for v in raw_c) and math.fsum(raw_c)>0:
  total=math.fsum(raw_c);weights=[v/total for v in raw_c];wr='Source-model catch proportions';wc='Medium';why='Historical warm-pool model landings composition assumed transferable to this regional taxon and all years/bases. Genuine printed zero candidates retained.'
 else:
  assert all(v is not None and math.isfinite(v) and v>=0 for v in bio) and math.fsum(bio)>0
  total=math.fsum(bio);weights=[v/total for v in bio];wr='Approved model-biomass fallback';wc='Medium';why='Catch attempt rejected: one or more candidate raw catches missing (-9999), although runtime loads zero. Complete model biomass proportions assumed to represent caught composition/catchability across species, stages, region, years and bases.'
 conf=levels[max(levels.index(d['membership_confidence']),levels.index(wc))]
 c=cs[2019];s=ci.get('sppr');p=0. if c==0 else c*s/9 if finite(c) and finite(s) else None
 d.update(taxon=t,year=2019,catch_basis='landings',catch_tonnes=c,tl=ci.get('tl'),classic_sppr=s,simple_chain_ppr_tC=p,allocation_rule=wr,allocation_confidence=wc,allocation_reason=why,confidence=conf,raw_source_catch=raw_c,source_biomass=bio,weights=weights,previous_mapping=old_by[t],candidates=[{'id':i,'name':groups[i]['group_name'],'weight':w,'raw_catch':v,'biomass':bi,'loaded_catch':groups[i]['catch'],'catch_state':'missing sentinel; runtime default zero' if v is None else 'source numeric zero' if v==0 else 'source numeric positive'} for i,w,v,bi in zip(ids,weights,raw_c,bio)])
 reason=d['membership_reason']+' '+why
 d['reason']=reason;d['mapping_display']='; '.join(f"{groups[i]['group_name']} ({w*100:.8g}%)" for i,w in zip(ids,weights)) if ids else '?'
 for i,w,v,bi in zip(ids,weights,raw_c,bio):
  mappings.append([MID,t,groups[i]['group_name'],w,conf.lower(),'; '.join(d['sources']+['source catch and biomass']),reason])
  if len(ids)>1:
   ar={'unit_id':'HS_071','model_id':MID,'taxon':t,'rule':wr,'confidence':wc.lower(),'weight_evidence':'assumed','definition':groups[i]['taxon_descr'],'evidence':'Allain et al. 2007 Table 1 PDF9; Table 3 PDF11; Table 5 PDF14; accepted raw JSON','limitations':reason,'source_period':'mixed 1993–2007 source periods, fixed historical surrogate','online_search':'Retained 2026-09-29 primary stage-data search; 2026-09-30 regional synonym/ecology review','previous_mapping':json.dumps(old_by[t],ensure_ascii=False),'years_applied':'1950-2019','catch_bases_applied':'landings;catch;discards','rule_details':json.dumps({'candidate_ids':ids,'raw_catch':raw_c,'biomass':bio,'basis':wr,'weights':weights}),'source_catch_basis':'Table 5 fisheries landings density, t/km2/year','temporal_and_basis_assumption':why,'group':groups[i]['group_name'],'seq':i,'source_catch':v,'canonical_export_raw':raw[i]['export'],'loaded_catch':groups[i]['catch'],'catch_state':d['candidates'][ids.index(i)]['catch_state'],'weight':w,'effective_source_catch':0 if t=='Katsuwonus pelamis' and v is None else v,'catch_assumption':'existing infant uncaught assumption retained' if t=='Katsuwonus pelamis' and v is None else None}
   alloc.append([ar.get(k) for k in ah])
 if not ids:mappings.append([MID,t,None,None,'unresolved','; '.join(d['sources']),reason])
 deltas.append({'key':{'unit_id':'HS_071','model_id':MID,'taxon':t},'old':old_by[t],'adopted':d['candidates'],'membership_rule':d['membership_rule'],'membership_confidence':d['membership_confidence'],'allocation_rule':wr,'allocation_confidence':wc,'overall_confidence':conf,'evidence':d['sources'],'reason':reason})
 out.append(d)
out.sort(key=lambda d:(d['simple_chain_ppr_tC'] is None,-d['simple_chain_ppr_tC'] if d['simple_chain_ppr_tC'] is not None else 0,d['taxon']))
ct=math.fsum(d['catch_tonnes'] for d in out);pt=math.fsum(d['simple_chain_ppr_tC'] for d in out if d['simple_chain_ppr_tC'] is not None)
def summary(field):
 cats=levels if field=='confidence' else sorted(set((d[field],d[field.replace('rule','confidence')]) for d in out))
 res=[]
 for key in cats:
  rr=[d for d in out if d[field]==key] if field=='confidence' else [d for d in out if (d[field],d[field.replace('rule','confidence')])==key]
  res.append({'label':key if isinstance(key,str) else key[0],'confidence':key if isinstance(key,str) else key[1],'taxa':len(rr),'catch_tonnes':math.fsum(d['catch_tonnes'] for d in rr),'catch_percentage':100*math.fsum(d['catch_tonnes'] for d in rr)/ct,'ppr_tC':math.fsum(d['simple_chain_ppr_tC'] for d in rr if d['simple_chain_ppr_tC'] is not None),'ppr_percentage':100*math.fsum(d['simple_chain_ppr_tC'] for d in rr if d['simple_chain_ppr_tC'] is not None)/pt})
 if field!='confidence':res.sort(key=lambda d:-d['ppr_percentage'])
 assert math.isclose(math.fsum(r['ppr_percentage'] for r in res),100,abs_tol=1e-8)
 return res
audit={'unit_id':'HS_071','model_id':MID,'model_sha256':sha(model),'baseline_workbook_sha256':sha(BASE/'HS_071.xlsx'),'year':2019,'catch_basis':'landings','n_taxa':len(out),'source_groups':31,'synthetic_groups':1,'total_catch_tonnes':ct,'simple_chain_ppr_tC':pt,'missing_tl_taxa':[d['taxon'] for d in out if d['tl'] is None],'unknown_annual_ppr_taxa':[d['taxon'] for d in out if d['simple_chain_ppr_tC'] is None],'confidence_summary':summary('confidence'),'membership_summary':summary('membership_rule'),'allocation_summary':summary('allocation_rule'),'rows':out,'sources':SRC,'decisions':deltas}
(OUT/'taxon_audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('AUDIT',len(out),'catch',ct,'simple PPRtC',pt,'confidence',audit['confidence_summary'])
if '--adopt' in sys.argv:
 live_path=REG/'HS_071.xlsx';live_sha=sha(live_path)
 # This explicit hash is the first builder's own failed-verification output;
 # no other edit is admitted automatically. Future reruns require the recorded final hash.
 admitted={sha(BASE/'HS_071.xlsx')}
 previous=OUT/'adoption_receipt.json'
 if previous.exists():admitted.add(json.loads(previous.read_text(encoding='utf-8'))['final_workbook_sha256'])
 assert live_sha in admitted,'Live regional workbook changed since the reviewed state; reconcile before adoption.'
 protected_annual=b['Classic PPR']['Annual']
 classic_ratios=[r for r in rows(b,'PPR–NPP','Ratios') if not r[0]]
 b['PPR']['Matching']=(['model_id','taxon','group','weight','confidence','evidence','explanation'],mappings)
 b['PPR']['Allocation assumptions']=(ah,alloc)
 rh=['model_id','taxon','membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence','reason','evidence']
 b['PPR']['Mapping review']=(rh,[[MID,d['taxon'],d['membership_rule'],d['membership_confidence'],d['allocation_rule'],d['allocation_confidence'],d['confidence'],d['reason'],'; '.join(d['sources'])] for d in out])
 b['Diagnostics']['Size allocation unresolved']=(['taxon','existing_mapping','reason'],[[d['taxon'],json.dumps(d['previous_mapping']),d['reason']] for d in out if d['confidence']=='Unresolved'])
 b['Diagnostics']['Validation mapping review']=(['unit_id','model_id','date','reviewed_taxa','resolved_taxa','evidence'],[['HS_071',MID,'2026-09-30',len(out),sum(bool(d['candidate_ids']) for d in out),'validation_reports/'+MID+'/taxon_audit.json']])
 recalculate(b,REG/'HS_071.xlsx')
 b['Classic PPR']['Annual']=protected_annual
 b['PPR–NPP']['Ratios']=(b['PPR–NPP']['Ratios'][0],classic_ratios+[r for r in rows(b,'PPR–NPP','Ratios') if r[0]])
 set_setting(b,'source_note','PROVISIONAL: reviewed 23 labels; 23 resolved including explicit Very low analogues; historical stage/catch/biomass composition assumptions and exact option1 WARN/strict balance false retained. See validation report/appendix.')
 set_setting(b,'calculation_status','provisional: adopted evidence-reviewed mapping and model-proportion assumptions; exact accepted option1 diagnostics retained; historical sensitivity bounds superseded')
 # Historical impact tables must not masquerade as the newly reviewed set.
 b['Diagnostics']['Size allocation impact historical 20260929']=b['Diagnostics'].pop('Size allocation impact')
 set_result_hash(b)
 assert sha(live_path)==live_sha,'Intervening regional edit detected immediately before save.'
 write_book(live_path,b)
 final=read_book(REG/'HS_071.xlsx');checks=[]
 for f in json.loads((BASE/'protected_table_fingerprints.json').read_text(encoding='utf-8'))['tables']:
  key=(f['sheet'],f['table']);before=b if False else read_book(BASE/'HS_071.xlsx')
  h,r=final[key[0]][key[1]];same=digest_tables([h,r])==digest_tables(list(before[key[0]][key[1]]));checks.append({'sheet':key[0],'table':key[1],'unchanged':same})
 assert all(x['unchanged'] for x in checks),checks
 assert sha(model)==sha(BASE/'accepted_model.json')
 audit['final_workbook_sha256']=sha(REG/'HS_071.xlsx');audit['final_input_sha256']=overview(final)['calculation_input_sha256'];audit['protected_checks']=checks
 previous.write_text(json.dumps({'baseline_workbook_sha256':sha(BASE/'HS_071.xlsx'),'reviewed_live_sha256':live_sha,'final_workbook_sha256':audit['final_workbook_sha256'],'scientific_input_preservation':checks,'date':'2026-09-30'},indent=2),encoding='utf-8')
 (OUT/'taxon_audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
 print('ADOPTED',audit['final_workbook_sha256'],checks)
