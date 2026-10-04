"""Source-faithful taxonomy and explicitly reviewed candidate memberships.

No catch amount, coefficient or existing mapping is used to select candidates.
Every extension is explicit below; unmatched labels stop the build.
"""
from pathlib import Path
import json,csv,re
P=Path(__file__).resolve().parent
tables=json.loads((P/'source_supplement_tables.json').read_text(encoding='utf8'))
catch=json.loads((P/'catch_labels.json').read_text(encoding='utf8'))
labels={r['taxon']:r for r in catch}
xls=json.loads((P.parent/'extraction/Table_1-f0424c0e.xls.cells.json').read_text(encoding='utf8'))
cells={(c['row'],c['column']):c for c in xls['sheets'][0]['cells']}
groups={int(c['value']):{'seq':int(c['value']),'group_name':re.sub('<[^>]*>','',str(cells[(c['row'],2)]['value'])).strip()} for c in xls['sheets'][0]['cells'] if c['column']==1 and str(c['value']).isdigit() and 1<=int(c['value'])<=51}
assert len(groups)==51
members={};taxa={};decisions={}
stage_pairs={3:[3,4],14:[14,15],16:[16,17],18:[18,19],23:[23,24],25:[25,26]}
for row in tables[0]['rows'][1:]:
 srcids,name,membertext=row
 if name=='Hake':continue
 ids=stage_pairs.get(int(srcids.split('-')[0]),[int(srcids.split('-')[0])])
 for i in ids:
  taxa[i]={'members_source_spelling':[x.strip() for x in membertext.split(';') if x.strip()], 'membership_scope':'Source Table S1 states composition of fish functional groups; list retained verbatim, including repetitions and apparent errors. Completeness outside the source study area is not asserted.','source_locator':'Supplement Table S1, DOCX table 1 body element 72, row '+str(tables[0]['rows'].index(row)+1),'source_group_id':srcids,'source_group_name':name,'life_stage':'juvenile, age 0–1 year' if i in [4,15,17,19,24,26] else 'adult, following juvenile age 0–1 year' if i in [3,14,16,18,23,25] else 'no separate stage group','stage_boundary_source':'Article PDF p2, Model structure' if len(ids)>1 else None,'habitat_definition':'coastal and migratory' if i in [3,4,5] else 'coastal, including Banc, near shelf and coast south of Banc' if i<=19 else 'shelf, more offshore including shelf break','size_cutoff':None,'size_cutoff_reason':'S/M/L are qualitative classes; no numeric size boundary or length type documented.'}
 for species in membertext.split(';'):
  species=species.strip()
  if species:members.setdefault(species,set()).update(ids)
for i in [6,7,8,9,10]:taxa[i]['habitat_definition']='Pelagic species migrate between Morocco and Senegal and occur on the whole shelf; Horse mackerels are benthopelagic but grouped as pelagic by source.'
other={
1:('Marine mammals mostly feeding in the study area; oceanic species feeding only marginally excluded. '+ '; '.join(row[1] for row in tables[5]['rows'][1:6]),'Text S1 P41; Table S4, DOCX table6'),
2:('Coastal breeding or migratory birds feeding in coastal waters or on Banc mudflats. '+ '; '.join(row[0] for row in tables[6]['rows'][1:] if len(row)>2 and row[0] and row[0] not in ['Breeders','Waders','total breeders','total waders','coastal birds'] and not row[0].startswith('a Campredon')),'Text S1 P43; Table S5, DOCX table7'),
30:('Octopus vulgaris; separately represented from other cephalopods.','Article Table1 ID30; Text S1 Cephalopods P45'),
31:('Other cephalopods, excluding the separately modeled Octopus vulgaris group. Loligo forbesi, L. vulgaris and Illex illecebrosus are named diet-study taxa, not an exhaustive composition list.','Text S1 Cephalopods P45'),
32:('Banc large crustaceans: Uca tangeri and shrimps. Table S6 names Hippolyte inermis, Palaemon spp. and Penaeus spp.; individuals <10 mm and Penaeus may be undersampled. No model L/S threshold stated.','Text S1 P51; Table S6 Crustaceans L and footnote t'),
33:('Banc molluscs: Gastropoda, Bivalvia, and Senilia senilis (as printed; source prose calls the latter a gastropod although it is a bivalve). Table S6 biomass calculation composition.','Text S1 P51; Table S6 Molluscs'),
34:('Banc worms: Nemertinea, Oligocheta, Planaria, Polychaeta (source spellings). Table S6 biomass calculation composition.','Table S6 Worms'),
35:('Banc small crustaceans: Amphipoda, Crustacea, Isopoda, Sipunculida and Tanaidacea as placed in Table S6. Sipunculida placement is a source inconsistency, retained without taxonomic repair.','Text S1 P51; Table S6 Crustaceans'),
36:('Banc other invertebrates: Coelenterata, Echinodermata (including Holothuroidea and Ophiuroidea) and Insecta. Table S6 biomass calculation categories.','Table S6 Other inverts'),
37:('Banc meiobenthos, biomass inferred from macrobenthos rather than an exhaustive taxon census.','Text S1 P51; Table S6 Meiobenthos'),
38:('Shelf large crustaceans; separate from smaller shelf crustaceans. Species composition not enumerated; source fisheries include shrimps and the group has reported demersal catch.','Article p2 fisheries; Table1; Table S6 Crustaceans L'),
39:('Shelf molluscs; separate from cephalopods. Species composition not enumerated in Table S6; molluscan biomass estimated from shelf transects.','Text S1 P49; Table S6 Molluscs'),
40:('Shelf worms: mainly Polychaeta and Oligochaeta; other worm categories inferred using Banc densities.','Table S6 Worms and footnote l'),
41:('Shelf small crustaceans: Isopoda, Cumacea, Gammaridae and Tanaidacea.','Table S6 Crustaceans, footnote k'),
42:('Shelf other invertebrates: principally Ophiuroidea and miscellaneous invertebrates.','Table S6 Other inverts and footnote s'),
43:('Shelf meiobenthos: nematodes, copepods and foraminiferans.','Table S6 Meiobenthos'),
44:('Shelf mesozooplankton: copepods, cladocerans, gastropod and lamellibranch larvae, dinoflagellates, etc.','Text S1 Plankton P47'),
45:('Shelf macrozooplankton: euphausiids, mysids, chaetognaths, salps, hydrozoa, fish larvae, etc.','Text S1 Plankton P47'),
46:('Banc mesozooplankton; no local biomass observations, corresponding shelf composition described as copepods, cladocerans, molluscan larvae, dinoflagellates, etc.','Text S1 Plankton P47'),
47:('Banc macrozooplankton; no local biomass observations, corresponding shelf composition includes euphausiids, mysids, chaetognaths, salps, hydrozoa and fish larvae.','Text S1 Plankton P47'),
48:('Banc phytoplankton, distinct composition from the upwelling area. Species not enumerated.','Text S1 Primary production P53'),
49:('Shelf phytoplankton; diatoms abundant in the upwelling area. Species not enumerated.','Text S1 Primary production P53'),
50:('Algae and eelgrass; seagrass biomass derived from tidal and subtidal beds, with extrapolation outside Banc. Source does not enumerate group species here.','Text S1 Primary production P55'),
51:('Detritus pool; dead organic matter, not a catch taxon.','Article Table1; Table S2')}
for i,(descr,loc) in other.items():taxa[i]={'members_source_spelling':[], 'membership_scope':'Source functional definition and/or biomass-estimation categories; exhaustive species list unavailable.','source_locator':loc,'source_group_id':str(i),'source_group_name':groups[i]['group_name'],'life_stage':'not stage-separated','stage_boundary_source':None,'habitat_definition':'Banc d’Arguin' if groups[i]['group_name'].startswith('BA ') else 'shelf / whole modeled area as defined in source','size_cutoff':None,'size_cutoff_reason':'No numeric model threshold documented.','taxon_descr':descr}
for i,g in groups.items():
 t=taxa[i];t.update(g)
 if 'taxon_descr' not in t:t['taxon_descr']='; '.join(t['members_source_spelling'])+('. Life stage: '+t['life_stage']+'.' if i in sum(stage_pairs.values(),[]) else '')
 t['variants']=['Base','M30','P30'];t['variant_membership_basis']='Article compares perturbations of the same group structure and diets/biomasses; Table S8 preserves group identities. No new variant member list reported.'
 t['authority_id']=None;t['source_taxonomic_spelling_policy']='Verbatim source. Verified catch synonyms live in mapping evidence, not silent source edits.'
 t['conflicts']=[]
 if i==20:t['conflicts'].append('S1 lists the wrasse Symphodus bailloni under Shelf selacians. Do not generalize that isolated conflict to wrasses.')
 if i==30:t['conflicts'].append('S1 ID30 is Hake, while final Table1 and S2 ID30 are Octopus vulgaris. The orphan Hake row is retained separately and not attached to ID30.')
 if i==33:t['conflicts'].append('Source prose calls Senilia senilis a gastropod; Table S6 taxon and group retained without correcting numeric input.')
 if i==35:t['conflicts'].append('Sipunculida appears among small crustaceans in S6; this does not redefine Sipuncula as Crustacea.')
(P/'taxonomy_evidence.json').write_text(json.dumps({'groups':[taxa[i] for i in sorted(taxa)],'orphan_source_rows':[{'table':'S1','source_id':30,'name':'Hake','members':['Merluccius senegalensis','Merluccius polli'],'decision':'No corresponding final-model Hake group. Do not attach to final ID30 Octopus vulgaris.'}]},ensure_ascii=False,indent=2),encoding='utf8')
with (P/'taxonomy.csv').open('w',encoding='utf8',newline='') as f:
 w=csv.writer(f);w.writerow(['seq','group_name','taxon_descr']);w.writerows([i,groups[i]['group_name'],taxa[i]['taxon_descr']] for i in sorted(groups))
def put(names,ids,rule,confidence,reason,refs=None):
 for name in names.split(';'):
  name=name.strip()
  if not name:continue
  assert name in labels, name
  assert name not in decisions, 'Duplicate '+name
  decisions[name]={'taxon':name,'candidate_ids':ids,'membership_rule':rule,'membership_confidence':confidence,'membership_reason':reason,'membership_references':refs or ['SRC_S1','SRC_P2','CATCH'],'membership_assumed':confidence!='High','review_status':'individually reviewed against source composition and habitat; zero catches included'}
# Only an exact explicitly enumerated binomial is initially eligible for High.
for name in labels:
 if name in members:put(name,sorted(members[name]),'M1','High',f'Table S1 explicitly includes {name} in the stated group composition; stage union is preserved where applicable.',['SRC_S1','SRC_P2'])
put('Octopus vulgaris',[30],'M1','High','Dedicated final-model Octopus vulgaris compartment; S1 Hake row30 is not the final group.',['SRC_T1','SRC_S1','SRC_S1_TEXT'])
# Exact subspecies spelling is broader than catch species: supported containment, not an automatic synonym claim.
put('Auxis rochei;Auxis thazard',[6],'M4','Medium','S1 lists the nominotypical subspecies in Pelagic L. Species-level catch is extended to that pool; no other source Auxis compartment exists.')
put('Diplodus sargus',[16,17],'M4','Medium','S1 lists D. sargus sargus and D. sargus cadenati within Seabreams; the species-level catch is interpreted within that historical source concept.')
put('Pagellus bellottii',[25,26],'M4','Medium','S1 lists Pagellus bellottii bellottii in Sparids; the species-level catch is extended to this stage pair.')
put('Sarotherodon melanotheron',[12],'M4','Medium','S1 names S. melanotheron melanotheron in Coastal M; regional species-level catch is extended to that pool.')
put('Helicolenus dactylopterus',[22],'M4','Medium','S1 lists Helicolenus dactylopterus dactylopterus in Shelf M; regional species-level catch is extended to that pool.')
aliases={
'Carlarius heudelotii':([18,19],'Arius heudelotii','TAX_ARIUS'),
'Chelon auratus':([5],'Liza aurata','TAX_CHELON'),
'Balistes capriscus':([12],'Balistes carolinensis','TAX_BALISTES'),
'Bathytoshia centroura':([11],'Dasyatis centroura','TAX_DASYATIS'),
'Glaucostegus cemiculus':([11],'Rhinobatos cemiculus','TAX_RHINOBATOS'),
'Chelidonichthys lastoviza':([29],'Trigloporus lastoviza','TAX_TRIGLOPORUS')}
for name,(ids,old,ref) in aliases.items():put(name,ids,'M2','High',f'Authority record links catch name {name} to source name {old}, explicitly listed in S1.',['SRC_S1',ref])
put('Aetomylaeus bovinus',[11],'M2','High','The taxonomic revision synonymizes Pteromylaeus with Aetomylaeus; S1 Pteromylaeus bovinus is the bull ray.',['SRC_S1','TAX_AETOMYLAEUS'])
put('Scyris alexandrina',[22],'M2','High','IMROP national nomenclature lists Scyris alexandrina as the name corresponding to source Alectis alexandrinus.',['SRC_S1','IMROP_GUIDE'])
put('Stephanolepis hispida',[12],'M4','Medium','Catch spelling differs from S1 Stephanolepis hispidus; probable spelling/gender correspondence used as supported extension, without verified synonym High.')
put('Sphoeroides marmoratus',[12],'M4','Medium','S1 prints Spaeroides marmoratus in Coastal M; probable typographic correspondence is retained as an explicit interpretation.')
put('Scomber colias',[7],'M4','Medium','Atlantic chub mackerel is interpreted as the Atlantic component of S1 historical Scomber japonicus. WoRMS recognizes S. japonicus colias as S. colias, but source lacks subspecies; historical concept transfer remains an assumption.',['SRC_S1','TAX_SCOMBER'])
# Coherent extensions to represented relatives, reviewed independently of catch values.
ext={
(5,):'Chelon labrosus;Liza;Mugil;Mugilidae',
(6,):'Auxis;Coryphaena;Sarda;Scomberomorus;Sphyraena;Sphyraena afra;Sphyraena barracuda;Sphyraena viridensis;Sphyraenidae;Trichiurus;Trichiuridae',
(7,):'Scomber;Scomber scombrus',
(9,):'Sardinella;Engraulidae',
(10,):'Trachurus;Trachurus mediterraneus;Trachurus picturatus;Decapterus;Decapterus macarellus',
(11,):'Dasyatis;Gymnura micrura;Mustelus;Mustelus asterias;Rhinobatidae;Rhinobatos',
(12,):'Aluterus;Aluterus monoceros;Balistes;Balistidae;Cynoglossus;Solea;Psettodidae;Gerres nigri;Monacanthidae;Polydactylus quadrifilis;Polynemidae',
(13,):'Atherina presbyter;Atherinidae',
(14,15):'Pseudotolithus;Pseudotolithus elongatus',
(16,17):'Diplodus;Diplodus annularis;Diplodus cervinus;Dentex dentex;Pagrus;Pagrus africanus;Plectorhinchus;Plectorhinchus macrolepis',
(20,):'Galeus melastomus;Squalidae;Squalus;Squalus acanthias;Squatina squatina;Squatinidae;Sphyrna;Sphyrna mokarran;Sphyrnidae;Scyliorhinidae;Scyliorhinus;Scyliorhinus canicula;Scyliorhinus stellaris;Raja brachyura;Raja microocellata;Hexanchus griseus',
(21,):'Congridae;Brotula;Fistulariidae;Gymnothorax;Gymnothorax maderensis;Gymnothorax polygonius;Gymnothorax unicolor;Muraena augusti;Muraenidae;Lophiidae;Lophius;Lophius vaillanti;Echelus myrus',
(22,):'Acanthuridae;Acanthurus;Alectis ciliaris;Branchiostegus;Caranx hippos;Caranx lugubris;Seriola dumerili;Seriola rivoliana;Trachinotus;Pseudocaranx dentex;Pomadasys;Uranoscopus;Uranoscopus scaber;Stromateidae;Sebastidae',
(23,24):'Cephalopholis taeniops;Epinephelus;Mycteroperca fusca',
(25,26):'Pagellus erythrinus',
(27,):'Umbrina cirrosa;Umbrina ronchus;Pteroscion peli',
(28,):'Bothidae;Dicologlossa hexophthalma;Microchirus;Microchirus variegatus;Lepidorhombus;Lepidorhombus boscii;Lepidorhombus whiffiagonis;Synapturichthys kleinii',
(29,):'Chromis limbata;Pomacentridae;Similiparma lurida;Scorpaena porcus;Synodus saurus'}
for ids,names in ext.items():
 put(names,list(ids),'M9' if len(ids)>1 else 'M4','Medium','Extension from S1 regional members with shared taxonomic and ecological characteristics. Candidate pool(s) chosen explicitly; unlisted species or broader reporting population are assumed to share this source placement. Habitat/size boundaries are qualitative, not a measured cutoff.')
# Cephalopod divisions and large crustacean/mollusc/other-invertebrate habitat pools.
put('Loliginidae;Loligo;Loligo forbesii;Illex coindetii;Ommastrephes;Ommastrephes bartramii;Ommastrephidae;Sepia;Sepia officinalis;Sepiida;Sepiidae;Teuthida;Todarodes sagittatus;Todaropsis eblanae',[31],'M3','High','Text S1 defines other cephalopods separately from Octopus; source gives squid diet examples and article identifies squid/cuttlefish fisheries. These identified squid/cuttlefish labels fit that explicit residual compartment.',['SRC_S1_TEXT','SRC_P2'])
put('Octopus;Octopodidae',[30],'M4','Medium','The final group is explicitly Octopus vulgaris, while the reported genus/family may contain other octopuses. Its use as a benthic octopus extension is an assumption; do not claim every reported individual is O. vulgaris.',['SRC_S1_TEXT','SRC_T1'])
put('Octopoda',[30,31],'M10','Very low','Broad order includes benthic octopuses represented by Octopus vulgaris and potentially pelagic argonaut/octopod forms in other cephalopods; unobserved composition is approximated across both.',['SRC_S1_TEXT','CATCH'])
put('Cephalopoda',[30,31],'M9','Medium','Reported cephalopods span the explicitly separated Octopus and other-cephalopod compartments; both are retained, with composition unobserved.',['SRC_S1_TEXT'])
put('Acanthocardia aculeata;Acanthocardia tuberculata;Bivalvia;Callista chione;Cerastoderma edule;Chamelea gallina;Crassostrea;Cymbium;Donax;Gastropoda;Haliotis;Murex;Mytilidae;Patella;Pteriomorphia;Veneridae',[33,39],'M9','Medium','Benthos molluscan label is compatible with the Banc and shelf mollusc pools. Catch does not identify geographic stratum; both are eligible. Geographic composition is assumed, including transfer of model pools to the wider LME.',['SRC_S6','SRC_P2','CATCH'])
put('Mollusca',[30,31,33,39],'M10','Very low','The taxonomic label can include cephalopods and benthic molluscs. Provider demersal-invertebrate tag does not prove cephalopods absent. Retain both named cephalopod groups and Banc/shelf mollusc pools in a broad composition approximation.',['SRC_S1_TEXT','SRC_S6','CATCH'])
put('Calappa granulata;Eriphia verrucosa;Maja squinado;Portunidae;Crangon;Palaemonidae;Parapenaeopsis atlantica;Penaeidae;Penaeus kerathurus;Penaeus notialis;Dendrobranchiata',[32,38],'M9','Medium','Shrimp/large decapod catch is assigned to Banc and shelf large-crustacean pools; source specifically represents Uca and shrimp in Banc. Regional shrimp study supports nursery/offshore movement but supplies no matching regional caught-mass fractions. Other decapods are explicit taxonomic/ecological extensions.',['SRC_S6','SHRIMP_HABITAT','CATCH'])
put('Homarus gammarus;Nephropidae;Nephrops norvegicus;Palinuridae;Palinurus;Palinurus mauritanicus;Panulirus;Panulirus regius;Scyllaridae;Scyllarus arctus;Solenocera africana;Solenocera membranacea;Solenoceridae;Parapenaeus longirostris',[38],'M5','Medium','Large benthic crustaceans from shelf habitats are a supported extension of the shelf large-crustacean group. The shallow Banc shrimp/Uca pool is not used for adult offshore lobster/shrimp labels. Exact species composition of shelf group is not enumerated.',['SRC_S6','WB_HABITAT','CATCH'])
put('Aristaeomorpha foliacea;Aristaeopsis edwardsiana;Aristeidae;Aristeus antennatus;Aristeus varidens;Chaceon affinis;Chaceon maritae;Geryon;Paromola cuvieri',[38],'M11','Very low','Deep/slope large crustaceans extend beyond the modeled <200 m shelf and lack a deep-water pool; shelf large crustaceans are the closest represented benthic decapod analogue. This habitat mismatch is retained.',['SRC_P2','SRC_S6','WB_HABITAT','CATCH'])
put('Echinoidea;Paracentrotus lividus;Holothuroidea',[36,42],'M9','Medium','Echinoderms are explicitly represented in S6 other-invertebrate biomass categories; geographic pool and transfer to target harvested assemblage require an assumption.',['SRC_S6'])
put('Lepas',[35,41],'M11','Very low','Pelagic/rafting goose barnacles are crustaceans without a matching sessile-epifaunal compartment. Small benthic crustacean pools are the closest size/taxonomic analogue, with habitat and feeding mismatch.',['SRC_S6','CATCH'])
put('Decapoda',[32,35,38,41],'M10','Very low','Broad decapod reporting can include large harvested shrimps/crabs/lobsters and smaller benthic forms. Use large and small Banc/shelf crustacean pools; cannot infer strict large-only containment from provider commercial tag. Exclude pelagic macrozooplankton because source macro examples are euphausiids/mysids rather than harvested adult Decapoda.',['SRC_S6','CATCH'])
put('Malacostraca;Miscellaneous marine crustaceans',[32,35,38,41,45,47],'M10','Very low','Composition unspecified across large and small benthic crustaceans and macrozooplankton (euphausiids/mysids). Retain those compatible compartments; source catch labels do not establish a complete size/habitat boundary. Meio/larval pools excluded as not a plausible adult fishery reporting population.',['SRC_S6','SRC_S1_TEXT','CATCH'])
put('Miscellaneous aquatic invertebrates',[30,31,32,33,34,35,36,38,39,40,41,42,45,47],'M10','Very low','Unidentified invertebrate reporting can include cephalopods, large/small crustaceans, molluscs, worms, echinoderms and other macro-invertebrates. The provider tag is not exhaustive; named and residual compatible macrofaunal pools retained. Meio/mesoplankton and primary producers excluded as unsupported harvested reporting components.',['SRC_S6','SRC_S1_TEXT','CATCH'])
# Family/genus labels demonstrably spanning source compartments.
split={
(6,10,22):'Carangidae',
(10,22):'Caranx',
(8,9,12):'Clupeidae;Clupeiformes',
(16,17,25,26):'Dentex;Pagellus;Sparidae',
(12,21):'Dicentrarchus;Moronidae',
(12,16,17,22):'Haemulidae',
(12,22):'Mullidae;Mullus',
(11,20):'Batoidea;Dasyatidae;Elasmobranchii;Myliobatidae;Raja;Rajiformes;Torpedo;Triakidae',
(12,28):'Pleuronectiformes;Soleidae',
(3,4,14,15,27):'Sciaenidae',
(6,7):'Scombridae;Scombroidei',
(12,22,29):'Scorpaena;Scorpaenidae;Scorpaeniformes;Tetraodontidae',
(22,23,24,29):'Serranidae',
(22,29):'Serranus;Trachinus;Triglidae',
(21,22,29):'Gadiformes'}
for ids,names in split.items():put(names,list(ids),'M9','Medium','S1 regional members of this reported lineage occur in multiple exact source pools. Retain the listed candidate set; absence of a named member from the residual reporting category is not assumed. Composition and extension to unlisted regional members remain assumptions.')
put('Chondrichthyes',[11,20],'M10','Very low','Broad cartilaginous-fish label includes sharks/rays in both source pools and potentially unrepresented chimaeras. Approximate with both meaningful selacian pools; disclose unrepresented component.')
put('Chimaeriformes',[20],'M11','Very low','Chimaeras have no source group and differ taxonomically from selacians; shelf selacians are the closest cartilaginous demersal-fish analogue, with deep-water and feeding mismatch.')
put('Marine finfishes not identified;Marine fishes not identified;Actinopterygii',list(range(3,30)),'M10','Very low','Unidentified finfish can span named fish, pelagic, coastal and shelf pools. No composition observations support a narrower exclusion; use all source fish pools (3–29). Actinopterygii excludes selacians, so those are removed for that label below.')
decisions['Actinopterygii']['candidate_ids']=[i for i in range(3,30) if i not in [11,20]]
for name in ['Marine finfishes not identified','Marine fishes not identified']:
 decisions[name]['membership_reason']='Unidentified finfish can span named fish, pelagic, coastal and shelf pools. No observed composition supports a narrower exclusion; approximate with all source fish pools (3–29), including selacians.'
decisions['Actinopterygii']['membership_reason']='Broad ray-finned-fish reporting spans named fish, pelagic, coastal and shelf pools. Approximate with source fish pools3–29 except11/20 (selacians), which are taxonomically excluded. Constituent composition is unobserved.'
put('Perciformes',[3,4,6,7,10,12,13,14,15,16,17,21,22,23,24,25,26,27,29],'M10','Very low','Historical broad perch-like reporting spans many source fish pools. Approximate using compatible named/guild compartments, excluding clupeiforms, selacians, catfish and flatfish-only groups; no observed constituent mix is available.')
put('Marine groundfishes not identified',[3,4,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29],'M10','Very low','Groundfish reporting establishes demersal tendency but no species mix. Include compatible named and generic coastal/shelf fish groups, including demersal elasmobranchs; exclude strictly pelagic/mullet pools.')
put('Marine pelagic fishes not identified',[5,6,7,8,9,10],'M10','Very low','Pelagic reporting supports the migratory mullet and pelagic groups, but source Coastal M includes pelagic Ethmalosa. Coastal M is additionally retained for that known exception; composition is assumed.')
decisions['Marine pelagic fishes not identified']['candidate_ids'] += [12,20,22]
decisions['Marine pelagic fishes not identified']['membership_reason']='Pelagic reporting spans migratory mullets, the five named pelagic pools, Coastal M (Ethmalosa), Shelf M (explicit pelagic/benthopelagic jacks) and offshore selacian analogue (potential pelagic sharks/rays). Pool names do not exclude these known exceptions. Unobserved composition is a broad approximation; strictly benthic fish pools are excluded.'
# Remaining documented ecological extensions; no universal size-to-guild matching rule.
put('Ablennes hians;Acanthocybium solandri;Belone belone;Belonidae;Echeneidae;Elagatis bipinnulata;Hemiramphus brasiliensis;Istiophoridae;Istiophorus albicans;Kajikia albida;Katsuwonus pelamis;Makaira nigricans;Megalops atlanticus;Rachycentridae;Rachycentron canadum;Scomberesox saurus;Tetrapturus belone;Tetrapturus pfluegeri;Thunnus;Thunnus alalunga;Thunnus albacares;Thunnus obesus;Thunnus thynnus;Tylosurus;Tylosurus crocodilus;Xiphias gladius',[6],'M5','Medium','Pelagic fish ecology supports extension of Pelagic L, whose S1 membership already includes scombrids, barracudas, dolphinfish and ribbonfish. Offshore distribution limits model applicability but does not contradict its explicit migratory pelagic guild. No measured numeric size boundary is imposed.',['SRC_S1','SRC_P2','CATCH'])
put('Alosa;Ilisha africana;Inermiidae;Argentina sphyraena',[9],'M6','Low','Small/medium schooling pelagic fish are extended to the Sardinelles/anchovy pool, with partial habitat/feeding fit and no direct focal-source membership. Coastal M (Ethmalosa) is a competing ecological analogue; source distinctions are not fully specified.')
put('Alepisaurus ferox;Lampris guttatus;Brama brama;Bramidae',[6],'M11','Very low','Bathypelagic or oceanic midwater fish lack their own depth/feeding compartment. Pelagic L is the closest mobile pelagic-fish analogue, with deep-water/feeding differences retained.',['SRC_P2','SRC_S1','CATCH'])
put('Myctophidae',[9],'M11','Very low','Mesopelagic lanternfish are not a represented source fish pool. Sardinelles/anchovy supplies the closest small schooling zooplanktivorous-fish analogue, despite depth and diel-migration mismatch.',['SRC_P2','SRC_S1','CATCH'])
put('Aphanopus carbo;Aphanopus intermedius;Lepidocybium flavobrunneum;Promethichthys prometheus;Gempylidae',[21],'M6','Low','Deep benthopelagic predators partly resemble source Shelf L (including Ruvettus), while source ribbonfish occur in Pelagic L. Choose Shelf L under explicit feeding/habitat extension; competing pelagic fit remains unresolved scientifically but numerical placement is supported.')
put('Antimora rostrata;Mora moro;Trachyrincus scabrus',[21],'M11','Very low','Deep slope fish exceed the modeled shelf domain. Shelf L includes a deep-associated macrourid and provides a meaningful predatory demersal-fish analogue, with depth/composition mismatch retained.')
put('Berycidae;Beryx;Beryx decadactylus;Beryx splendens;Epigonus telescopus;Hoplostethus atlanticus;Trachichthyidae;Polymixia nobilis;Peristediidae',[22],'M6','Low','Deeper shelf/slope mid-sized fishes are partly compatible with Shelf M (e.g. Gephyroberyx and Helicolenus), but group size/depth limits and species inclusion are not fully stated. Extension is partial rather than direct source membership.')
put('Ophidiidae;Polyprion americanus',[21],'M6','Low','Large demersal/deep-associated fish extend source Shelf L (including Brotula and other large predators); depth and lineage composition are incompletely matched.')
put('Merlucciidae;Merluccius;Merluccius merluccius;Merluccius polli;Merluccius senegalensis',[21],'M6','Low','S1 names a Hake group absent from final Table1/S2 (final ID30 is Octopus). Use Shelf L predatory demersal-fish pool as a documented partial-fit replacement; never attach hake taxonomy to octopus. Source does not document a final Hake-to-Shelf-L merge.',['SRC_S1','SRC_T1','SRC_P2'])
put('Anguilla anguilla;Anguilliformes',[21],'M6','Low','Elongate demersal fishes resemble source Shelf L eels (Conger/Muraena); freshwater/estuarine adult eel habitat and broad order composition differ. A partial ecological extension is recorded.')
put('Gadidae;Micromesistius poutassou;Phycis;Phycis blennoides;Phycis phycis;Trisopterus luscus',[21,22],'M6','Low','Cod-like benthopelagic fishes lack a dedicated final group. Large/medium shelf fish pools are meaningful predatory demersal analogues; size/habitat and juvenile composition do not establish one exclusive group. Both retained under partial-fit assumption.')
put('Apsilus fuscus;Lutjanidae;Lutjanus;Lutjanus agennes;Heteropriacanthus cruentatus;Priacanthidae;Priacanthus;Priacanthus arenatus',[22],'M5','Medium','Reef/coastal demersal predators extend Shelf M, which includes mixed reef/demersal percoids in S1. No listed member establishes exact membership; this is an ecological extension with a qualitative boundary.')
put('Centracanthus cirrus;Oblada melanurus;Spicara',[25,26],'M4','Medium','Small zooplanktivorous/omnivorous seabream relatives are extended to Sparids (S1 Boops/Sarpa/Spondyliosoma), rather than assuming the broader family maps to Seabreams. Source lacks these exact taxa.')
put('Centrolophidae;Schedophilus ovalis;Schedophilus pemarco',[22],'M6','Low','Benthopelagic medusafish resemble source Shelf M Stromateus and other mixed fish, but feeding/habitat fit is partial and Pelagic L is a plausible competing analogue.')
put('Bodianus scrofa;Coris julis;Kyphosus sectatrix;Labridae;Labrus;Scaridae;Sparisoma cretense;Symphodus;Thalassoma pavo',[22,29],'M6','Low','Reef wrasses/parrotfishes/herbivores span sizes and feeding roles imperfectly represented by Shelf M (Scarus hoefleri) and Shelf S (Xyrichtys). Both meaningful guilds retained. S1 Symphodus bailloni under selacians is an apparent source error, not evidence to put wrasses into sharks.',['SRC_S1','SRC_P2','CATCH'])
put('Trachinus radiatus',[22,29],'M9','Medium','S1 places Trachinus armatus in Shelf S while middle-sized demersal weevers plausibly extend Shelf M. Qualitative size definitions do not establish one exclusive pool.')
# Unlisted selacians reviewed for coastal, shelf/deep or oceanic mismatch.
put('Carcharhinus brachyurus;Carcharhinus brevipinna;Carcharhinus leucas;Carcharhinus limbatus;Carcharhinus obscurus;Carcharhinus plumbeus;Carcharias taurus;Ginglymostoma cirratum;Galeocerdo cuvier;Pristidae',[11],'M5','Medium','Coastal shark/sawfish habitat supports an extension of Coastal selacians (source coastal rays and sharks); taxonomic and feeding differences from named members remain assumed.')
put('Carcharhinidae;Carcharhiniformes;Carcharhinus;Squaliformes',[11,20],'M10','Very low','Broad shark reporting spans source coastal/shelf habitats and potentially oceanic/deep species. Both selacian pools are a meaningful approximation; no observed species/habitat composition supports stronger containment.')
put('Alopias;Alopias superciliosus;Alopias vulpinus;Carcharhinus falciformis;Carcharhinus galapagensis;Carcharhinus longimanus;Carcharhinus signatus;Carcharodon carcharias;Cetorhinus maximus;Isurus;Isurus oxyrinchus;Isurus paucus;Lamna nasus;Lamnidae;Lamniformes;Mobula birostris;Prionace glauca;Odontaspis ferox',[20],'M11','Very low','Oceanic, highly migratory or large filter-feeding elasmobranch lacks a matching pool. Shelf selacians is the closest offshore cartilaginous-fish analogue; oceanic/depth or feeding differences (especially basking shark/mobula) are material. Coastal selacians would not resolve those differences.',['SRC_S1','SRC_P2','CATCH'])
put('Centrophorus;Centrophorus granulosus;Centrophorus lusitanicus;Centrophorus squamosus;Centroscyllium fabricii;Centroscymnus coelolepis;Centroselachus crepidater;Dalatias licha;Deania calceus;Echinorhinus brucus;Etmopterus;Etmopterus princeps;Scymnodon ringens;Somniosus rostratus',[20],'M11','Very low','Deep-water dogfish/shark assemblage extends beyond the modeled shelf. Shelf selacians (including Squalus/Oxynotus/Galeus) is the closest taxonomic/demersal analogue, with depth and unlisted-species mismatch.',['SRC_S1','SRC_P2','CATCH'])
unmatched=sorted(set(labels)-set(decisions))
if unmatched:
 print('UNMATCHED',len(unmatched),';'.join(unmatched));raise SystemExit(1)
assert len(decisions)==512
for d in decisions.values():
 d['candidate_names']=[groups[i]['group_name'] for i in d['candidate_ids']]
 d['excluded_candidates_reason']='All groups outside the reviewed set are excluded by the source taxon/guild scope or the explicit extension/analogue rationale; basal producers, detritus, mammals and birds are never fish-catch candidates.'
 d['provider_context']={k:labels[d['taxon']].get(k) for k in ['common_name','functional_group','commercial_group','unidentified']}
 d['decision_state']='candidate-only; not adopted into regional workbook'
(P/'membership_decisions.json').write_text(json.dumps([decisions[n] for n in sorted(decisions)],ensure_ascii=False,indent=2),encoding='utf8')
print('Taxonomy',len(groups),'decisions',len(decisions))
from collections import Counter
print(Counter(x['membership_confidence'] for x in decisions.values()))
