"""EEZ_598 review/adoption builder. Scientific input blocks are immutable."""
import sys,json,math,shutil,csv,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];REG=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from workbooks import *
from regional import set_setting,recalculate,set_result_hash
MID='941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)'
OUT=REG/'validation_reports'/MID;QA=OUT/'qa';QA.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'original_research_archive/research/selected_regions_validation_20260930/baseline/EEZ_598'
b=read_book(BASE/'EEZ_598.xlsx');o=overview(b);model=REG/o['model_path'];m=json.loads(model.read_text(encoding='utf-8'))
assert sha(model)==sha(BASE/'accepted_model.json')
groups={int(r['seq']):r for r in records(b,'Selected model groups','Groups')}
raw={int(g['group_seq']):g for g in m['group']}
catch={r['taxon']:r for r in records(b,'Catch','Catch') if r['catch_basis']=='landings'}
classic={r['taxon']:r for r in records(b,'Classic PPR','Taxa')}
old=records(b,'PPR','Matching');old_by={t:[r for r in old if r['taxon']==t] for t in catch}
levels=['High','Medium','Low','Very low','Unresolved'];dec={}
def add(names,ids,rule,conf,reason,sources=('source definitions','catch classification')):
 for t in names.split('|'):
  assert t in catch and t not in dec,t
  dec[t]={'candidate_ids':ids,'membership_rule':rule,'membership_confidence':conf,'membership_reason':reason,'sources':list(sources)}
add('Acanthocybium solandri|Coryphaena hippurus',[8],'Explicit source assignment','High','Final Table 1 explicitly names wahoo and includes Coryphaenidae. No source stage split is required.')
add('Alopias|Carcharhinus falciformis|Carcharhinus longimanus|Isurus|Isurus oxyrinchus|Sphyrna',[4,10],'Unambiguous documented group fit','High','Source Other Sharks includes Alopiidae, Carcharhinidae, Lamnidae and Sphyrnidae; Small Sharks contains the same species. Provider shark categories fit this complete union; regional caught sizes are unknown.')
add('Galeocerdo cuvier',[4,10],'Unambiguous documented group fit','High','Tiger shark belongs to the historical Carcharhinidae source concept; source Other Sharks and Small Sharks cover that union. The historical taxonomic bridge does not establish regional caught-stage composition.',('source definitions','FAO shark taxonomy','catch classification'))
add('Carcharhinidae',[3,4,10],'Assumed eligible group set','Medium','Source Other Sharks explicitly names Carcharhinidae; historically this family also includes separately represented Prionace in Blue Shark. Retain Blue Shark, Other Sharks and Small Sharks as the complete compatible family union, with unknown residual reporting composition and coastal applicability. Separately identified catches do not measure this family label composition.',('source definitions','FAO shark taxonomy','catch classification'))
add('Prionace glauca',[3,10],'Explicit source assignment','High','Explicit Blue Shark member and matching Small Sharks stage union; pooled juvenile catch is a proxy for this species.')
add('Xiphias gladius',[1,9],'Explicit source assignment','High','Explicit swordfish and its small-stage union; source pooled small billfish ratio is assumed transferable.')
add('Istiompax indica|Kajikia audax',[2,9],'Verified synonym','High','NCBI entries connect Istiompax indica to source Makaira indica and Kajikia audax to Tetrapturus audax; both occupy Other Billfish and the small-stage union.',('source definitions','billfish synonyms','catch classification'))
add('Istiophoridae',[2,9],'Assumed eligible group set','Medium','Source locally relevant marlin/sailfish/spearfish members support Other Billfish plus Small Billfish. Residual family composition and historical scope are unknown; separately reported swordfish is excluded.')
add('Katsuwonus pelamis',[7,13,14],'Explicit source assignment','High','Explicit adult, small and infant skipjack compartments. Source Table 1/PDF15 infant cutoff conflict concerns allocation inside this verified species union.')
add('Thunnus albacares',[6,12],'Explicit source assignment','High','Explicit adult/small yellowfin, 120 cm maturity boundary; PNG caught-mass stage shares are unknown.')
add('Thunnus obesus',[5,11],'Explicit source assignment','High','Explicit adult/small bigeye, 124 cm maturity boundary; PNG caught-mass stage shares are unknown.')
add('Carangidae|Decapterus|Elagatis bipinnulata|Scomberoides',[8,16,17],'Assumed eligible group set','Medium','Source Carangidae overlaps Piscivorous fish and Epi fish plus its larval/juvenile stage. Provider pelagic categories support this candidate union, with unknown trophic/size boundaries and within-label composition.')
add('Alepes|Caranx|Seriola',[8,16,17],'Partial or conflicting ecological fit','Low','These carangid genera fit overlapping source fish pools, but PNG provider reef/benthopelagic categories can represent adults outside the pelagic forage inventory. Retain all three meaningful candidates, with this partial habitat/stage fit.')
add('Engraulidae|Stolephorus',[16,17],'Explicit source assignment','High','Final source explicitly includes Engraulidae in Epi fish and corresponding larvae/juveniles in Epi small fish. Stolephorus is an anchovy genus; provider identifies anchovies.')
add('Acanthuridae|Balistidae|Lethrinidae|Serranidae|Tetraodontidae|Scaridae|Epinephelus',[16,17],'Partial or conflicting ecological fit','Low','Final Epi fish explicitly lists these reef-fish lineages and Epi small fish their larvae/juveniles. Provider reef catches may be benthic adults with feeding/habitat mismatch to the pelagic forage compartment; Epinephelus is within source Serranidae.')
add('Clupeidae|Clupeiformes|Pellona ditchela|Anodontostoma chacunda|Hilsa kelee',[16,17],'Extension from listed representatives','Medium','Provider small-pelagic herring/shad categories support extension from final Engraulidae and other small pelagic fish. Clupeidae is explicitly in the removed initial forage definition, not the final named list; final eligibility is an assumed ecological/lineage extension.')
add('Auxis|Scomber|Scomberomorus|Rastrelliger',[8,16,17],'Assumed eligible group set','Medium','FAO Scombridae identification includes these genera. Source residual small scombrids in Piscivorous fish overlap Epi fish and its small stage; exact regional caught-size/guild composition is unknown.',('source definitions','FAO family identification','catch classification'))
add('Scombridae',[5,6,7,8,11,12,13,14,16,17],'Broad-category approximation','Very low','Residual provider mackerel/tuna/bonito category can span named tuna stages and residual scombrid pools. All compatible named and residual groups are retained as a weak composition proxy; unidentified family composition is not measured by the separately identified catches.')
add('Thunnus alalunga|Thunnus orientalis|Thunnus maccoyii',[5,11],'Closest represented analogue','Very low','Unlisted albacore/bluefins have a weak deep-using Thunnus analogue in the bigeye pair. Species, temperature and maturation differ; this is not source membership or observed caught-stage composition.',('source definitions','FAO tuna ecology','catch classification'))
add('Chirocentrus|Rachycentridae',[8],'Supported ecological assignment','Medium','Provider large pelagics and FAO coastal/offshore carnivory support a non-enumerated Piscivorous fish extension. Inclusion is an ecological assumption; cobia also consumes crustaceans and source membership is not explicit.',('source definitions','FAO piscivore ecology','catch classification'))
add('Trichiurus|Trichiuridae|Scorpaenidae',[22],'Partial or conflicting ecological fit','Low','Final Meso fish + other explicitly includes juvenile Trichiuridae/Scorpaenidae. Provider large benthopelagic or reef catches may be adults/shallower members; this is a partial lineage and habitat/stage fit.')
add('Lates calcarifer',[8],'Closest represented analogue','Very low','Barramundi is a large estuarine/demersal fish according to the provider and lacks a source compartment. Piscivorous fish is the closest represented predator analogue, with substantial coastal/estuarine habitat and taxonomic mismatch.')
add('Labridae|Lactarius lactarius|Leiognathidae|Leiognathus|Lutjanidae|Lutjanus|Lutjanus argentimaculatus|Mugilidae|Mullidae|Upeneus|Nemipterus|Drepane|Plotosidae|Plotosus|Pristipomoides|Sparidae|Cynoglossus|Bothidae|Pleuronectiformes|Congridae|Sciaenidae|Sillago|Terapontidae',[16,17],'Closest represented analogue','Very low','Provider coastal, reef, demersal or benthopelagic fish lack explicit final source membership. Epi fish and its small stage are the closest usable mixed-fish analogues; real depth/feeding/adult-stage and taxonomic mismatches remain. No basal or synthetic import pool is treated as a catch guild.')
add('Marine fishes not identified|Perciformes',[16,17],'Broad-category approximation','Very low','Provider broad demersal category lacks regional species composition. Epi fish and its small stage provide a weak represented mixed-fish composition, with demersal habitat and omitted taxa disclosed.')
add('Marine pelagic fishes not identified',[8,16,17,20,22,24,26],'Broad-category approximation','Very low','Unidentified medium pelagic reporting can include residual piscivorous, epipelagic, mesopelagic and fish-bearing bathypelagic pools. All compatible residual fish pools are retained; dedicated tuna/billfish categories are separately reported, and crustacean/mollusc-only M Bathy forage is excluded. Composition across depths is a weak assumption.')
add('Chondrichthyes',[3,4,10],'Broad-category approximation','Very low','Provider sharks/rays/skates/chimaeras crosses source shark-only boundaries. Blue Shark/Other Sharks/small-stage pools form a weak represented-shark proxy; unrepresented rays/chimaeras remain a genuine unknown component.')
add('Elasmobranchii',[3,4,10],'Broad-category approximation','Very low','Elasmobranchii reports sharks, rays and skates; chimaeras are outside this target scope (FAO 3.1.1). Blue Shark, Other Sharks and Small Sharks supply a weak represented-shark proxy; unrepresented rays/skates remain an unknown component.')
add('Dendrobranchiata|Malacostraca',[15,24,25],'Broad-category approximation','Very low','Source Epi crust, HM Bathy forage and M Bathy forage contain pelagic crustaceans, Caridae/Sergestidae/Penaeoidea. Broad reported shrimp/crab/lobster/krill categories also contain benthic adults; these complete compatible crustacean pools are a weak composition proxy.')
add('Miscellaneous marine crustaceans',[15,24,25],'Broad-category approximation','Very low','SAU reports crabs, shrimps and lobsters nei. Groups 15/24/25 contain lobster taxa and crab stages, Caridae/Sergestidae and Penaeoidea/Acanthephyra. These mixed pelagic/deep-water pools provide a Very low proxy; benthic-adult, stage and nondecapod/fish/mollusc mismatches remain.')
add('Metapenaeus|Penaeus merguiensis|Penaeus monodon',[25],'Closest represented analogue','Very low','Penaeoidea is named in M Bathy forage, making it the closest taxonomic shrimp analogue. FAO identifies these coastal/benthic penaeids; bathypelagic mixed-forage depth and feeding differ substantially. Other crustacean pools have no explicit penaeid lineage.',('source definitions','FAO penaeid ecology','catch classification'))
add('Panulirus',[15],'Partial or conflicting ecological fit','Low','Source Epi crust names historical Palinura; FAO places Panulirus in Palinuridae. Provider lobster catch may be benthic adults rather than pelagic larval forage, giving a partial lineage/stage fit.',('source definitions','FAO lobster taxonomy','catch classification'))
add('Scylla serrata',[15],'Closest represented analogue','Very low','Benthic mud crab has no source adult-crab compartment. Epi crust includes megalopa-stage crustaceans and is the closest larval crustacean analogue; this substantial habitat/stage mismatch is explicit.')
add('Mollusca',[18,19,21,23,24,25,26],'Broad-category approximation','Very low','Provider clams/snails/squid/octopuses spans unrepresented benthic molluscs and represented pelagic molluscs. All dedicated and mollusc-bearing bathypelagic forage pools, including Liocranchia in HM Bathy forage, form a weak composite; complete taxonomic coverage is not claimed.')
add('Gastropoda|Trochus',[18,19],'Closest represented analogue','Very low','Source Epi mollusc includes pelagic Carinariidae/Cavoliniidae gastropods and its small stage. Provider sea-snail and FAO reef-grazing Trochus ecology differs substantially in habitat/feeding; this is the closest usable lineage analogue.',('source definitions','FAO gastropod ecology','catch classification'))
add('Loliginidae',[18,19],'Partial or conflicting ecological fit','Low','Loliginidae is explicitly listed in Epi mollusc and its small stage, but provider common pencil-squid catch can involve neritic/bottom-associated adults outside pelagic forage use.')
add('Octopoda',[18,19,23,26],'Broad-category approximation','Very low','Reported octopuses/argonauts includes surface Argonautidae, mesopelagic Amphitretidae and bathypelagic Bolitaenidae source pools, with many unrepresented benthic octopuses. Preserve all four compatible pools as a weak order-level composition proxy.')
add('Teuthida',[18,19,21,23,24,25],'Broad-category approximation','Very low','Broad squid label spans dedicated epi/migrant-meso/meso molluscs and bathypelagic Liocranchia/Histioteuthidae forage. Bathy forage Bolitaenidae is octopod-only and excluded. This is an assumed depth/species composition.')
add('Sepia|Sepiidae',[18,19],'Closest represented analogue','Very low','Benthic/neritic cuttlefish lacks a final source compartment. Epi mollusc and its small stage are the closest muscular cephalopod analogues, with substantial taxonomic/habitat mismatch; source Sepiolidae is not Sepiidae.')
add('Bivalvia|Pinctada|Tridacna gigas|Echinodermata|Holothuriidae',[],'No meaningful assignment','Unresolved','Benthic bivalve/filter-feeder and echinoderm guilds have no meaningful taxonomic/feeding analogue in the source pelagic fish/squid/gastropod/crustacean pools. No arbitrary basal or import assignment is adopted.')
assert set(dec)==set(catch),(set(catch)-set(dec))
SRC=[{'label': 'source definitions',
  'title': 'Allain et al. (2007), final Table 1, PDF9; stage prose PDF15; geography PDF7 and Figure 1 PDF3',
  'target': 'papers/WCP-2007/download-0adcf55e.pdf#page=9',
  'supports': 'Final-model memberships, overlap, stages and study area; initial blue groups are excluded; '
              'infant cutoff conflict retained.'},
 {'label': 'source catch and biomass',
  'title': 'Allain et al. (2007), Tables 3/5/6, PDF11/14/19; accepted option1 raw JSON',
  'target': 'models/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods).json',
  'supports': 'Raw landings density and biomass. Source missing export (-9999) differs from genuine zero and '
              'runtime default. Biomass fallback assumes catch composition/catchability follows model '
              'biomass.'},
 {'label': 'catch classification',
  'title': 'EEZ_598 workbook Catch/Catch, 2019 landings; Sea Around Us labels and ecological categories',
  'target': 'EEZ_598.xlsx',
  'supports': 'Exact regional reporting labels and provider common/functional/commercial groups; category '
              'size is not an observed individual measurement.'},
 {'label': 'classic coefficient',
  'title': 'EEZ_598 workbook Classic PPR/Taxa: saved independent TL/coefficient and recorded provenance',
  'target': 'EEZ_598.xlsx',
  'supports': 'Independent simple-chain coefficient, TL and source fields are unchanged. Annual tonnes C = '
              'catch × saved wet-weight coefficient / 9 once.'},
 {'label': 'billfish synonyms',
  'title': 'NCBI Taxonomy: Istiompax indica (13603), Kajikia audax (13721); WoRMS corroborating entries',
  'target': 'https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=13603',
  'supports': 'Full NCBI entries independently read 2026-09-30: Makaira indica and Tetrapturus audax '
              'synonyms. Kajikia entry13721 is separately linked. WoRMS corroboration was previously '
              'indexed/read in EEZ_941 review with direct timeout/403; not claimed as a fresh full retrieval '
              'here.'},
 {'label': 'FAO tuna ecology',
  'title': 'FAO: introduction to tuna and billfish biology (Y0490E), vertical habitat and life histories',
  'target': 'https://www.fao.org/4/y0490e/y0490e04.htm',
  'supports': 'Full relevant text read 2026-09-30: bigeye/bluefin deep diving, albacore intermediate '
              'habitat; supports weak analogue only, not caught-size shares.'},
 {'label': 'FAO family identification',
  'title': 'FAO historical Scombridae identification sheet; retained Chirocentridae evidence',
  'target': 'https://www.fao.org/docrep/pdf/009/e9163e/e9163e4c.pdf#page=5',
  'supports': 'Scombridae PDF5 independently read 2026-09-30, including '
              'Scomber/Scomberomorus/Thunnus/Katsuwonus/Acanthocybium. Chirocentrus coastal-pelagic ecology '
              'is retained EEZ_941 source evidence, independently compared with PNG provider categories; no '
              'claim of regional composition.'},
 {'label': 'FAO octopod ecology',
  'title': 'FAO identification guide Y4160E, printed pp.217–219 (PDF2–4), '
           'Argonautidae/Bolitaenidae/Octopodidae',
  'target': 'https://www.fao.org/4/y4160e/y4160e13.pdf#page=4',
  'supports': 'Relevant PDF2–4 independently read 2026-09-30: surface pelagic Argonautidae, '
              'meso/bathypelagic Bolitaenidae and benthic Octopodidae. Supports full order-level candidate '
              'review and actual habitat mismatch; no composition shares.'},
 {'label': 'diagnostics',
  'title': 'Exact accepted option1 retained full direct diagnostic returns and group × source matrices',
  'target': '../EEZ_941/evidence/2026-09-28_integration/direct_diagnostics.json',
  'supports': 'GE/TE/With Egestion WARN, strict mass balance false, PP budget OK. Full source matrix checked '
              'independently in this review; no fresh solver executed.'},
 {'label': 'reconstruction provenance',
  'title': 'Original final source reconstruction audit and selected option1 provenance',
  'target': '../EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)/extracted_tables/REPORT.md',
  'supports': '31 source groups plus synthetic import; loader conventions, source initial/final '
              'distinctions, native multistanza and author-confirmation limits; original final '
              'reconstruction FAIL differs from accepted variant.'},
 {'label': 'stage data search',
  'title': 'Retained 2026-09-29 WCPFC/SPC public size-data search and Papua New Guinea 2020 annual report',
  'target': 'validation_reports/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)/source_review.md#stage-allocation',
  'supports': 'No relevant all-fleet PNG-EEZ 2019 caught-mass shares at exact source stage thresholds '
              'recovered. This is not evidence such data do not exist.'},
 {'label': 'FAO penaeid ecology',
  'title': 'FAO penaeid shrimp manual, Section2; Penaeus monodon profile',
  'target': 'https://www.fao.org/4/ac006e/AC006E02.htm',
  'supports': '2026-09-30 full relevant text: coastal/benthic penaeid habitat; taxonomy/ecology only, no '
              'regional stage shares.'},
 {'label': 'FAO gastropod ecology',
  'title': 'FAO marine-snail restocking manual Section2.2',
  'target': 'https://www.fao.org/4/ag150e/ag150e03.htm',
  'supports': '2026-09-30 full relevant text: reef-flat/subtidal Trochus grazing; real mismatch to pelagic '
              'gastropod forage.'},
 {'label': 'FAO piscivore ecology',
  'title': 'FAO cobia profile; family identification Chirocentrus',
  'target': 'https://www.fao.org/fishery/docs/DOCUMENT/aquaculture/CulturedSpecies/file/en/en_cobia.htm',
  'supports': '2026-09-30 cobia profile read: offshore/coastal carnivory, fish/crab/shrimp/squid feeding. '
              'Chirocentrus FAO source reused with independent provider comparison.'},
 {'label': 'FAO lobster taxonomy',
  'title': 'FAO Marine Lobsters of the World Vol13 (1991), Palinuridae/Panulirus',
  'target': 'https://www.fao.org/4/t0411e/t0411e00.htm',
  'supports': '2026-09-30 catalogue family/genera reviewed; provider benthic lobster reporting differs from '
              'source epipelagic forage.'},
 {'label': 'FAO shark taxonomy',
  'title': 'FAO Field Identification Guide to Sharks and Rays (2005), printed45/PDF22, '
           'Carcharhinidae/Galeocerdo/Prionace',
  'target': 'https://www.fao.org/4/y5945e/y5945e03.pdf#page=22',
  'supports': '2026-09-30 relevant full page read: historical Carcharhinidae includes Galeocerdo and '
              'Prionace, bridging tiger shark and complete reported family to source pools. No regional '
              'composition measurement.'}]
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
   ar={'unit_id':'EEZ_598','model_id':MID,'taxon':t,'rule':wr,'confidence':wc.lower(),'weight_evidence':'assumed','definition':groups[i]['taxon_descr'],'evidence':'Allain et al. 2007 Table 1 PDF9; Table 3 PDF11; Table 5 PDF14; accepted raw JSON','limitations':reason,'source_period':'mixed 1993–2007 source periods, fixed historical surrogate','online_search':'Retained 2026-09-29 primary stage-data search; 2026-09-30 regional synonym/ecology review','previous_mapping':json.dumps(old_by[t],ensure_ascii=False),'years_applied':'1950-2019','catch_bases_applied':'landings;catch;discards','rule_details':json.dumps({'candidate_ids':ids,'raw_catch':raw_c,'biomass':bio,'basis':wr,'weights':weights}),'source_catch_basis':'Table 5 fisheries landings density, t/km2/year','temporal_and_basis_assumption':why,'group':groups[i]['group_name'],'seq':i,'source_catch':v,'canonical_export_raw':raw[i]['export'],'loaded_catch':groups[i]['catch'],'catch_state':d['candidates'][ids.index(i)]['catch_state'],'weight':w,'effective_source_catch':0 if t=='Katsuwonus pelamis' and v is None else v,'catch_assumption':'existing infant uncaught assumption retained' if t=='Katsuwonus pelamis' and v is None else None}
   alloc.append([ar.get(k) for k in ah])
 if not ids:mappings.append([MID,t,None,None,'unresolved','; '.join(d['sources']),reason])
 deltas.append({'key':{'unit_id':'EEZ_598','model_id':MID,'taxon':t},'old':old_by[t],'adopted':d['candidates'],'membership_rule':d['membership_rule'],'membership_confidence':d['membership_confidence'],'allocation_rule':wr,'allocation_confidence':wc,'overall_confidence':conf,'evidence':d['sources'],'reason':reason})
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
audit={'unit_id':'EEZ_598','model_id':MID,'model_sha256':sha(model),'baseline_workbook_sha256':sha(BASE/'EEZ_598.xlsx'),'year':2019,'catch_basis':'landings','n_taxa':len(out),'source_groups':31,'synthetic_groups':1,'total_catch_tonnes':ct,'simple_chain_ppr_tC':pt,'missing_tl_taxa':[d['taxon'] for d in out if d['tl'] is None],'unknown_annual_ppr_taxa':[d['taxon'] for d in out if d['simple_chain_ppr_tC'] is None],'confidence_summary':summary('confidence'),'membership_summary':summary('membership_rule'),'allocation_summary':summary('allocation_rule'),'rows':out,'sources':SRC,'decisions':deltas}
(OUT/'taxon_audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
print('AUDIT',len(out),'catch',ct,'simple PPRtC',pt,'confidence',audit['confidence_summary'])
if '--adopt' in sys.argv:
 live_path=REG/'EEZ_598.xlsx';live_sha=sha(live_path)
 # Admit only the frozen baseline or recorded previous reviewed final output.
 admitted={sha(BASE/'EEZ_598.xlsx')}
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
 b['Diagnostics']['Validation mapping review']=(['unit_id','model_id','date','reviewed_taxa','resolved_taxa','evidence'],[['EEZ_598',MID,'2026-09-30',len(out),sum(bool(d['candidate_ids']) for d in out),'validation_reports/'+MID+'/taxon_audit.json']])
 recalculate(b,REG/'EEZ_598.xlsx')
 b['Classic PPR']['Annual']=protected_annual
 b['PPR–NPP']['Ratios']=(b['PPR–NPP']['Ratios'][0],classic_ratios+[r for r in rows(b,'PPR–NPP','Ratios') if r[0]])
 set_setting(b,'source_note','PROVISIONAL: reviewed 102 labels; 97 resolved including explicit Very low analogues; historical stage/catch/biomass composition assumptions and exact option1 WARN/strict balance false retained. See validation report/appendix.')
 set_setting(b,'calculation_status','provisional: adopted evidence-reviewed mapping and model-proportion assumptions; exact accepted option1 diagnostics retained; historical sensitivity bounds superseded')
 # Historical impact tables must not masquerade as the newly reviewed set.
 b['Diagnostics']['Size allocation impact historical 20260929']=b['Diagnostics'].pop('Size allocation impact')
 set_result_hash(b)
 assert sha(live_path)==live_sha,'Intervening regional edit detected immediately before save.'
 write_book(live_path,b)
 final=read_book(REG/'EEZ_598.xlsx');checks=[]
 for f in json.loads((BASE/'protected_table_fingerprints.json').read_text(encoding='utf-8'))['tables']:
  key=(f['sheet'],f['table']);before=b if False else read_book(BASE/'EEZ_598.xlsx')
  h,r=final[key[0]][key[1]];same=digest_tables([h,r])==digest_tables(list(before[key[0]][key[1]]));checks.append({'sheet':key[0],'table':key[1],'unchanged':same})
 assert all(x['unchanged'] for x in checks),checks
 assert sha(model)==sha(BASE/'accepted_model.json')
 audit['final_workbook_sha256']=sha(REG/'EEZ_598.xlsx');audit['final_input_sha256']=overview(final)['calculation_input_sha256'];audit['protected_checks']=checks
 previous.write_text(json.dumps({'baseline_workbook_sha256':sha(BASE/'EEZ_598.xlsx'),'reviewed_live_sha256':live_sha,'final_workbook_sha256':audit['final_workbook_sha256'],'scientific_input_preservation':checks,'date':'2026-09-30'},indent=2),encoding='utf-8')
 (OUT/'taxon_audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
 print('ADOPTED',audit['final_workbook_sha256'],checks)
