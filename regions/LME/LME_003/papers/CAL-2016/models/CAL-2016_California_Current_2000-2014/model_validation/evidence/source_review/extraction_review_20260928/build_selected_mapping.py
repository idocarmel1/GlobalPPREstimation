from pathlib import Path
import sys,json,csv,math,collections
ROOT=Path(__file__).resolve().parents[3];REG=ROOT/'regions/LME_003';MODEL=REG/'models/CAL-2016_California_Current_2000-2014';OUT=MODEL/'selected_pipeline'
sys.path.insert(0,str(ROOT/'tools'));from workbooks import *
from regional import set_setting,recalculate
book=read_book(REG/'LME_003.xlsx');taxa=json.loads((REG/'extraction_review_20260928/catch_work_order.json').read_text(encoding='utf-8'))
taxonomy=json.loads((MODEL/'extracted_tables/taxonomy_source_evidence.json').read_text(encoding='utf-8'));names={t['seq']:t['group_name'] for t in taxonomy}
decisions={};members=[]
def assign(taxon,seq,confidence='high',evidence='explicit_member',note=''):
 if taxon not in {x['taxon'] for x in taxa}:return
 text=f"Appendix B '{taxonomy[seq-1]['appendix_heading']}', paragraph {taxonomy[seq-1]['heading_paragraph_zero_based']} (zero-based) and following group definition. "+note
 decisions[taxon]={'taxon':taxon,'assignments':[(seq,1.0)],'confidence':confidence,'evidence':evidence,'explanation':text}
 if evidence=='explicit_member':members.append([taxon,names[seq],text])
exact={19:'Doryteuthis opalescens',20:'Sardinops sagax',21:'Engraulis mordax',22:'Clupea pallasii',23:'Scomber japonicus',25:'Allosmerus elongatus',27:'Cololabis saira',13:'Metacarcinus magister',33:'Sebastes flavidus',34:'Sebastes melanops',36:'Sebastes ruberrimus',37:'Sebastes elongatus',39:'Sebastes jordani',40:'Eopsetta jordani',42:'Merluccius productus',43:'Ophiodon elongatus',44:'Atheresthes stomias',45:'Anoplopoma fimbria',46:'Thunnus alalunga',50:'Sebastes pinniger',51:'Sebastes alutus',52:'Sebastes entomelas',53:'Sebastes diploproa',55:'Sebastolobus alascanus',56:'Sebastolobus altivelis'}
for seq,t in exact.items():
 note=''
 if seq in [33,34,35,36,37,38,39,50,51,52,53,54,42,40,41,43,44,45,55,56,57]:note='Life-stage allocation uses author model catch: relevant juvenile group catch is explicitly zero, so the full weight falls on this caught adult group; this does not claim all regional discards are adults.'
 if seq==23:note+=' Source spelling japonicas is a spelling variant of Scomber japonicus; NOAA Fisheries Pacific Mackerel species profile confirms identity: https://www.fisheries.noaa.gov/species/pacific-mackerel'
 assign(t,seq,note=note)
multi={26:['Hypomesus pretiosus','Thaleichthys pacificus'],35:['Sebastes auriculatus','Sebastes chlorostictus','Sebastes levis'],38:['Sebastes paucispinis','Sebastes goodei','Sebastes saxicola','Sebastes carnatus'],41:['Hippoglossus stenolepis','Paralichthys californicus'],47:['Oncorhynchus tshawytscha','Oncorhynchus kisutch'],54:['Sebastes crameri','Sebastes aurora','Sebastes aleutianus','Sebastes zacentrus'],16:['Microgadus proximus','Hydrolagus colliei'],49:['Apristurus brunneus'],59:['Alopias vulpinus','Alopias superciliosus','Prionace glauca','Galeorhinus galeus','Isurus oxyrinchus','Carcharodon carcharias']}
for seq,ts in multi.items():
 for t in ts:assign(t,seq,note='For explicit juvenile/adult counterparts, source model zero juvenile catch supports adult weight1 where applicable. Original source misspellings remain preserved in taxonomy evidence.')
assign('Squalus suckleyi',49,evidence='synonym_match',note='Pacific S. suckleyi was formerly called S. acanthias in regional sources, matching the paper dogfish identity: NOAA https://www.fisheries.noaa.gov/inport/item/24030. This is a regional taxonomic revision, not an Atlantic-stock substitution.')
assign('Pandalus jordani',11,evidence='taxonomic_containment',note='Pandalus genus is explicitly included; author species spelling is jordanii.')
assign('Pandalus',11,evidence='taxonomic_containment',note='Pandalus species form this group.')
assign('Crangon franciscorum',12,evidence='taxonomic_containment',note='Author explicitly includes Crangon species.')

# Taxonomic containment follows the source definitions, with dedicated exceptions first.
bivalve={'Magallana','Crassostrea','Ostrea','Veneridae','Panopea','Siliqua','Mytilus','Tivela','Leukoma','Bivalvia','Saxidomus','Tresus','Mya','Anadara','Clinocardium','Donax','Tellinidae'}
gastropod={'Haliotis','Megastraea','Gastropoda'}
epicrab={'Portunus','Portunidae','Callinectes','Diogenidae','Cancer','Lithodidae'}
flat={'Microstomus','Parophrys','Glyptocephalus','Achirus','Syacium','Citharichthys','Psettichthys','Reinhardtius','Atheresthes','Platichthys','Limanda','Pleuronichthys','Hippoglossoides','Lepidopsetta','Xystreurys','Bothidae'}
surf={'Amphistichus','Embiotoca','Hyperprosopon','Rhacochilus','Phanerodon','Hypsurus'}
sculp={'Cottidae','Scorpaenichthys','Hemilepidotus','Enophrys','Myoxocephalus'}
for t in taxa:
 name=t['taxon'];g=name.split()[0]
 if name in decisions:continue
 if g in bivalve:assign(name,2,evidence='taxonomic_containment',note='Source group explicitly includes bivalves. Magallana gigas oyster classification corroborated by WoRMS https://www.marinespecies.org/aphia.php?p=taxdetails&id=836033 where relevant. Reef-attached oysters/mussels use the documented bivalve pool, despite the infauna label.')
 elif g in gastropod:assign(name,4,evidence='taxonomic_containment',note='Source epibenthic group explicitly includes primarily gastropod molluscs.')
 elif g in epicrab:assign(name,4,evidence='taxonomic_containment',note='Source explicitly includes brachyurans except Dungeness/Tanner and anomurans.')
 elif g in flat:assign(name,57,evidence='taxonomic_containment',note='Source Flatfish defines all pleuronectiforms except dedicated halibut/petrale and arrowtooth groups. Dedicated species assigned first. Juvenile-flat catch zero supports adult weight1; this is model selectivity, not an observed regional stage split.')
 elif g in surf:assign(name,17,evidence='taxonomic_containment',note='Source group is explicitly Embiotocidae; this taxon is a surfperch.')
 elif g in sculp:assign(name,16,evidence='taxonomic_containment',note='Source benthic fish group explicitly includes sculpins (Cottidae).')
 elif name in ['Stomolophus','Stomolophus meleagris']:assign(name,10,evidence='taxonomic_containment',note='Scyphozoan cnidarians are explicitly included in the gelatinous-carnivore group; not the small-jelly herbivore pool.')
 elif name in ['Octopodidae','Octopoda']:assign(name,18,evidence='taxonomic_containment',note='Source explicitly includes octopods and cephalopods other than market squid; large predatory jumbo squid caveat does not apply to these labels.')
 elif name in ['Echinoidea','Strongylocentrotus']:assign(name,2,'medium','taxonomic_containment','Source infauna includes echinoderms; epibenthic list separately names other echinoderm classes but not echinoids. This pool assignment is inferred from that partition.')
 elif name in ['Alopias','Isurus']:assign(name,59,'medium','taxonomic_containment','Named genus represented in the source shark group; coarse genus identity rather than species-specific observation.')

# Composite candidates are explicitly recorded; weights derive only from direct identified catch.
composites={
 'Sebastes':([33,34,35,36,37,38,39,50,51,52,53,54],'all modeled adult Sebastes groups; juvenile-rockfish catch zero'),
 'Sebastidae':([33,34,35,36,37,38,39,50,51,52,53,54,55,56],'adult rockfish and thornyhead groups; source juvenile catches zero'),
 'Pleuronectiformes':([40,41,44,57],'modeled adult flatfish pools; juvenile-flatfish catch zero'),
 'Pleuronectoidei':([40,41,44,57],'modeled adult flatfish pools; juvenile-flatfish catch zero'),
 'Pleuronectidae':([40,41,44,57],'right-eye flatfish intersect these groups; only identified right-eye taxa seed the weights'),
 'Paralichthyidae':([41,57],'California halibut versus other left-eye flatfish; excludes right-eye halibut composition within pooled Halibut'),
 'Osmeridae':([25,26],'whitebait smelt and the other-osmerid pool'),
 'Teuthida':([18,19],'non-market versus market squid; no evidence to resolve large predatory squids within coarse label'),
 'Loliginidae':([18,19],'market squid and remaining loliginids in other cephalopods'),
 'Cephalopoda':([18,19],'market squid and other cephalopods; unknown coarse-size composition'),
 'Brachyura':([4,13,14],'other brachyurans, Dungeness, Tanner'),
 'Mollusca':([2,4],'SAU other-demersal-invertebrate class restricts to benthic bivalve/gastropod pools; excludes pelagic cephalopods'),
 'Echinodermata':([2,4],'echinoids and other source-listed epibenthic echinoderms'),
 'Marine fishes not identified':([16,35,38,48,54,57],'SAU medium-demersal class: pooled demersal-fish groups, excluding dedicated commercial single-species groups, pelagic fish, sharks and invertebrates'),
 'Marine finfishes not identified':([16,35,38,48,54,57],'same constrained medium-demersal pooled groups; catches of absent species cannot be identified within this record'),
 'Marine groundfishes not identified':([16,35,38,48,54,57],'constrained demersal pooled groups'),
 'Actinopterygii':([16,35,38,48,54,57],'ray-finned fishes restricted by SAU medium-demersal class to modeled demersal pools'),
 'Osteichthyes':([16,35,38,48,54,57],'bony fishes restricted by SAU medium-demersal class to modeled demersal pools'),
}
def in_composite(parent,taxon):
 genus=taxon.split()[0]
 if parent=='Pleuronectidae':return genus in {'Eopsetta','Hippoglossus','Atheresthes','Microstomus','Parophrys','Glyptocephalus','Psettichthys','Reinhardtius','Platichthys','Limanda','Pleuronichthys','Hippoglossoides','Lepidopsetta'}
 if parent=='Paralichthyidae':return genus in {'Paralichthys','Citharichthys','Syacium','Xystreurys'}
 if parent in {'Mollusca'}:return genus in bivalve|gastropod
 if parent=='Echinodermata':return genus in {'Echinoidea','Strongylocentrotus','Echinodermata'}
 if parent in {'Sebastes','Sebastidae'}:return genus in ({'Sebastes'} if parent=='Sebastes' else {'Sebastes','Sebastolobus'})
 if parent in {'Actinopterygii','Osteichthyes'}:return taxon!='Hydrolagus colliei'
 return True
author=json.loads((MODEL/'extracted_tables/author_equation_solution.json').read_text(encoding='utf-8'))['groups'];raw=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))['group']
for name,(seqs,description) in composites.items():
 if name not in {t['taxon'] for t in taxa}:continue
 direct_mass=collections.defaultdict(float)
 for t in taxa:
  if t['taxon'] in decisions and decisions[t['taxon']]['evidence']!='composite_split' and in_composite(name,t['taxon']):
   for seq,w in decisions[t['taxon']]['assignments']:direct_mass[seq]+=t['total']*w
 masses=[direct_mass[s] for s in seqs];basis='1950–2019 identified regional catch assigned directly to candidate groups, filtered to the composite taxon where a pool spans different higher taxa'
 if not sum(masses):masses=[float(raw[s-1]['export']) for s in seqs];basis='author total model catch'
 if not sum(masses):masses=[author[s-1]['biomass'] for s in seqs];basis='author-equation solved biomass'
 assert sum(masses)>0
 assignments=[(s,x/sum(masses)) for s,x in zip(seqs,masses) if x>0]
 decisions[name]={'taxon':name,'assignments':assignments,'confidence':'low' if name.startswith('Marine') or name in ['Actinopterygii','Osteichthyes'] else 'medium','evidence':'composite_split','explanation':f'Candidate set: {description}. Constant weights from {basis}; only direct identified assignments seed weights, so no circular composite weighting. This is a modeled catch-composition projection, not observed composition of unidentified catches. Full candidate set including zero-weight groups: '+', '.join(names[s] for s in seqs)}
unresolved=[]
for t in taxa:
 n=t['taxon']
 if n in decisions:continue
 reason='No source-supported adult group or complete composite candidate set for this taxon in Appendix B; source group labels are not expanded solely to raise coverage.'
 if n in ['Thunnus albacares','Katsuwonus pelamis','Thunnus orientalis','Thunnus obesus','Thunnus','Scombridae','Scombroidei']:reason='Albacore group is specifically Thunnus alalunga; other tunas/bonitos are not documented members. Coarse scombrid labels include these unsupported taxa.'
 if n=='Trachurus symmetricus':reason='Pacific Mackerel group is Scomber japonicus, not Trachurus; no jack-mackerel group.'
 if n in ['Gadus chalcogrammus','Gadus macrocephalus','Gadidae','Gadiformes']:reason='Hake group is Merluccius productus; pollock and cod are not documented there or in the source benthic-fish pool.'
 if n in ['Opisthonema libertate','Cetengraulis mysticetus','Clupeiformes','Clupeidae','Engraulidae']:reason='Dedicated Sardine/Anchovy/Herring groups describe named species; thread herring/anchoveta are absent. Coarse labels span these unsupported species, so a full-support split cannot be established.'
 if n in ['Oncorhynchus keta','Oncorhynchus gorbuscha','Oncorhynchus nerka','Oncorhynchus mykiss','Oncorhynchus','Salmonidae']:reason='Appendix B Salmon explicitly contains Chinook and coho; other salmon/trout species are not documented members, and coarse labels include them.'
 if n=='Dosidicus gigas':reason='Appendix B cephalopod discussion says this pool represents smaller cephalopods, not large predatory jumbo/Humboldt squid; retain the conflicting broad class definition and do not assign this species.'
 if n in ['Batoidea','Rajiformes','Elasmobranchii','Chondrichthyes']:reason='Coarse label includes non-skate rays/chimaeras beyond the documented Skates pool; complete supported partition unavailable.'
 if n.startswith('Penaeus') or n in ['Penaeidae','Dendrobranchiata']:reason='Pandalid and benthic-shrimp definitions name Pandalus and Crangon/caridean groups; penaeid shrimp are not documented and were not forced into them.'
 decisions[n]={'taxon':n,'assignments':[],'confidence':'unresolved','evidence':'unresolved','explanation':reason};unresolved.append(t|{'reason':reason})
mapping=[]
for t in taxa:
 d=decisions[t['taxon']]
 if d['assignments']:
  assert math.isclose(sum(w for s,w in d['assignments']),1,rel_tol=0,abs_tol=1e-12)
  for s,w in d['assignments']:
   assert 2<=s<=92
   mapping.append([MODEL.name,d['taxon'],names[s],w,d['confidence'],d['evidence'],d['explanation']])
 else:mapping.append([MODEL.name,d['taxon'],None,None,d['confidence'],d['evidence'],d['explanation']])
header=['model_id','taxon','group','weight','confidence','evidence','explanation'];book['PPR']['Matching']=(header,mapping)
with (OUT/'catch_mapping.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(header);w.writerows(mapping)
with (OUT/'explicit_members_used.csv').open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['taxon','group','source']);w.writerows(members)
(OUT/'mapping_decisions.json').write_text(json.dumps(list(decisions.values()),indent=2,ensure_ascii=False),encoding='utf-8')
(OUT/'unresolved_taxa.json').write_text(json.dumps(unresolved,indent=2,ensure_ascii=False),encoding='utf-8')
coverage={'taxa_total':len(taxa),'taxa_mapped':sum(bool(d['assignments']) for d in decisions.values()),'taxa_unresolved':len(unresolved),'1950_2019_total_catch_tonnes':sum(t['total'] for t in taxa),'1950_2019_mapped_catch_tonnes':sum(t['total'] for t in taxa if decisions[t['taxon']]['assignments']),'2019_total_catch_tonnes':sum(t['2019'] or 0 for t in taxa),'2019_mapped_catch_tonnes':sum(t['2019'] or 0 for t in taxa if decisions[t['taxon']]['assignments']),'confidence_counts':dict(collections.Counter(d['confidence'] for d in decisions.values()))}
coverage['historical_tonnage_coverage']=coverage['1950_2019_mapped_catch_tonnes']/coverage['1950_2019_total_catch_tonnes'];coverage['2019_tonnage_coverage']=coverage['2019_mapped_catch_tonnes']/coverage['2019_total_catch_tonnes']
book['Diagnostics']['Mapping coverage']=(list(coverage),[[json.dumps(v) if isinstance(v,dict) else v for v in coverage.values()]])
book['Diagnostics']['Mapping review']=(['finding','detail'],[['coverage_limit','Mapped-catch PPR is partial; uncovered taxon catches remain explicit. The 95% review target is not achieved because named tropical/pelagic taxa lack documented groups.'],['coarse_weights','Constant 1950–2019 direct identified catch weights; source/model fallback only where no direct composition exists; all candidates and exact weights retained.'],['life_stages','Source juvenile catches zero supports adult model catch weighting; unobserved regional stage distributions and juvenile discards remain uncertain.'],['source_geometry','302000 km² source domain does not prove all SAU LME catch lies in source area.'],['uncertainty','No Monte Carlo or new NPP extraction. Existing annual NPP and source provenance preserved.']])
set_setting(book,'production_eligible',True)
set_setting(book,'source_note',f'PARTIAL mapped-catch PPR: {coverage["historical_tonnage_coverage"]:.2%} of 1950–2019 catch and {coverage["2019_tonnage_coverage"]:.2%} of 2019 catch; {coverage["taxa_unresolved"]} taxa unresolved. Source model: 93 groups, 302000 km²; no established geographic LME coverage fraction. Runtime solves 26 B and 67 EE from author equations, adds GS=0.2 and egestion-to-detritus; source canonical unchanged. Total model catch includes discards without a split. Fixed 2000–2014 coefficients applied to historical catch; NPP uses retained same-year support. Three configuration diagnostics WARN. Eligibility means supported mapped-catch calculations only.')
recalculate(book,REG/'LME_003.xlsx')
set_setting(book,'calculation_status',f'Complete for supported mapped catch; {coverage["2019_tonnage_coverage"]:.2%} catch coverage in 2019; three direct diagnostics WARN; historical sensitivity unavailable')
write_book(REG/'LME_003.xlsx',book)
(OUT/'mapping_coverage.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
print(json.dumps(coverage,indent=2))
