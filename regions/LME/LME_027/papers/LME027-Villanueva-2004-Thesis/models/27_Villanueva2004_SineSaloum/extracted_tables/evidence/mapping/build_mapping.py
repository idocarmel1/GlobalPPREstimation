"""Source-specific, unadopted thesis-37 candidate mapping, independently calculated PPR.
The literal 38-group proceedings model is not used for membership, weights or coefficients.
"""
from pathlib import Path
import json,csv,math,collections,hashlib,pdfplumber
C=Path(__file__).resolve().parents[1]; M=C/'mapping'
def dump(name,x): (M/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
source=json.loads((C/'extracted_tables/thesis/literal_source_extraction.json').read_text(encoding='utf-8'))
groups={g['group_id']:g for g in source['groups']}
assert len(groups)==37
ref=json.loads((C/'calculations/reference_inputs.json').read_text(encoding='utf-8'))
tax=json.loads((M/'authoritative_taxonomy_selected.json').read_text(encoding='utf-8'))
confidence_order={'High':0,'Medium':1,'Low':2,'Very low':3,'Unresolved':4}

# Retain literal Table3.3 rows/columns, including repeated/contradictory records.
pdf=pdfplumber.open(C/'evidence/identity/Villanueva2004_thesis_29305.pdf')
literal_members=[]
for pnum,sl,sr,lower,upper,ll in [(82,240,351,168,709,110),(83,253,353,98,610,122)]:
 words=pdf.pages[pnum-1].extract_words()
 species_words=[w for w in words if sl<=w['x0']<sr and lower<=w['top']<upper]
 ys=[]
 for w in sorted(species_words,key=lambda w:w['top']):
  if not ys or w['top']-ys[-1]>4:ys.append(w['top'])
 pool=''
 for y in ys:
  name=' '.join(w['text'] for w in sorted(species_words,key=lambda w:w['x0']) if abs(w['top']-y)<4)
  label=' '.join(w['text'] for w in sorted(words,key=lambda w:w['x0']) if ll<=w['x0']<sl-8 and abs(w['top']-y)<4)
  if label: pool=label
  def marker(xl,xr):return ''.join(w['text'] for w in words if xl<=w['x0']<xr and abs(w['top']-y)<4)
  if name in ['Espèces','(Ecopath)'] or 'groupes' in name:continue
  literal_members.append({'pdf_page':pnum,'printed_page':pnum-24,'table':'3.3','pool_label_literal':label,'pool_label_inherited':pool,'species_literal':name,'Saloum':marker(356,378),'Gambie':marker(397,418),'Ebrie':marker(433,455),'Nokoue':marker(470,493),'row_y_pt':y})
dump('table3_3_literal_membership.json',literal_members)

# Each direct record below was read in the Saloum column of Table3.3 and crosswalked
# to the principal in Table6.5, preserving source spellings and source conflicts.
explicit={
 'Sphyraena afra':1,'Scomberomorus tritor':2,'Polydactylus quadrifilis':3,'Galeoides decadactylus':4,'Pentanemus quinquarius':4,
 'Pseudotolithus elongatus':5,'Pseudotolithus senegalensis':6,'Pseudotolithus typus':6,'Elops lacerta':7,
 'Pomadasys incisus':9,'Pomadasys jubelini':9,'Plectorhinchus macrolepis':9,'Chloroscombrus chrysurus':10,
 'Caranx hippos':11,'Caranx senegallus':11,'Lichia amia':11,'Trachinotus ovatus':12,'Cynoglossus monodi':14,
 'Cynoglossus senegalensis':14,'Eucinostomus melanopterus':15,'Gerres nigri':15,'Drepane africana':16,
 'Ilisha africana':18,'Brachydeuterus auritus':19,'Hemiramphus brasiliensis':21,'Trichiurus lepturus':23,
 'Ethmalosa fimbriata':25,'Sardinella aurita':26,'Sardinella maderensis':26,'Mugil cephalus':27,
 'Sarotherodon melanotheron':28}
synonyms={'Carlarius heudelotii':(8,'Arius heudeloti (Table3.3 spelling); Arius heudelotii is accepted as Carlarius heudelotii by WoRMS.'),'Caranx rhonchus':(11,'Table3.3 Decapterus rhonchus; authoritative WoRMS synonym bridge is retained.'),'Pomadasys rogerii':(9,'Table3.3 Pomadasys rogeri; WoRMS accepts Pomadasys rogeri as Pomadasys rogerii.')}
rule_text={
 'M1':'Species is explicitly assigned by the Sine-Saloum source membership table or is the exact model principal species.',
 'M2':'An authoritative synonym or historical spelling links the catch taxon to an explicitly listed source member.',
 'M3':'The catch taxon fits an explicitly documented generic source group, with its taxonomic reporting scope verified.',
 'M4':'An unlisted relative is added to a documented pooled group on taxonomic evidence; membership remains an assumption.',
 'M5':'Source habitat and generic group definitions support a benthic ecological assignment with an explicit extension assumption.',
 'M6':'A source membership or compartment-identity conflict weakens an otherwise supported assignment.',
 'M9':'Taxonomy and source pool definitions support an inferred candidate set whose composition remains assumed.',
 'M10':'A broad catch label is approximated by a recorded set of source pools because its composition or containment is unknown.',
 'M11':'The closest represented ecological or taxonomic analogue is used for an unrepresented taxon, with the actual mismatch disclosed.',
 'M8':'No meaningful candidate group or usable allocation can be established.',
 'W1':'The complete catch taxon is assigned to one model group; no numerical split is needed.',
 'W4':'Weights use the candidate groups’ thesis-model catch proportions, assumed applicable to the regional catch and constant over years.',
 'W9':'Complete thesis-model biomass proportions replace incomplete source catch values, assuming representative composition and catchability.',
 'W11':'An explicit numerical expert assumption allocates otherwise unquantified meaningful candidates.',
 'W8':'No usable numerical allocation can be justified.'}

def dec(ids,rule,conf,why,reason_group,sources=None):
 return {'candidate_ids':ids,'membership_rule':rule,'membership_confidence':conf,'membership_reason':why,'very_low_reason_group':reason_group,'sources':sources or ['THESIS_GROUPS','THESIS_MEMBERS','TAXONOMY','CATCH']}

def choose(r):
 n=r['taxon'];gen=n.split()[0];fg=r['functional_group'];tr=tax.get(n,{});family=tr.get('family');cls=tr.get('class')
 if n in explicit:
  return dec([explicit[n]],'M1','High','Table3.3 Saloum explicitly includes this taxon; the corresponding Table6.5 principal identifies the exact group.','')
 if n in synonyms:
  gid,why=synonyms[n]
  if n=='Caranx rhonchus':
   src=tax.get('Decapterus rhonchus',{})
   assert src.get('valid_AphiaID')==tr.get('valid_AphiaID'),(src,tr)
  if n=='Pomadasys rogerii':assert tax['Pomadasys rogeri'].get('valid_AphiaID')==tr.get('valid_AphiaID')
  return dec([gid],'M2','High',why,'')
 if n.startswith('Epinephelus') or gen in {'Mycteroperca','Cephalopholis'} or n=='Serranidae':
  conf='Low' if n=='Epinephelus aeneus' else 'Very low'
  return dec([20],'M6' if conf=='Low' else 'M11',conf,'Table6.5 names Epinephelus aeneus and Table3.3 defines bottom predators, but AnnexII.A group20 names Hemichromis fasciatus, a different family. This candidate preserves Table6.5 identity without repairing that conflict.','Grouper and bottom-predator placement is tentative because basic inputs and diet group20 identify different fish families.')
 if n in {'Psettodes belcheri','Pteroscion peli'}:
  gid=13 if n=='Psettodes belcheri' else 5
  detail=' Psettodes belcheri is also repeated under Chloroscombrus in Table3.3; the biologically compatible flatfish placement is retained as disputed.' if n=='Psettodes belcheri' else ' The P.elongatus/Pteroscion source grouping is retained as disputed; no single-species compartment is silently enlarged.'
  return dec([gid],'M6','Low','Table3.3 includes this taxon in the matching pool, but Table6.5 marks its principal as a single-species compartment.'+detail,'')
 if n=='Tylosurus crocodilus':return dec([21],'M6','Low','Table3.3 Saloum explicitly lists Tylosorus crocodilus in the historical Belonidae pool represented by Hemiramphus brasiliensis. WoRMS verifies Tylosurus crocodilus as a belonid but does not recognize the printed genus spelling Tylosorus; the matching epithet and related needlefish context support this tentative orthographic bridge.','')
 if n=='Tylosurus':return dec([21],'M4','Medium','The source historical Belonidae pool lists the orthographic forms Tylosorus crocodilus and Tylosorus acus rafale alongside halfbeaks/needlefishes. The authoritative Tylosurus genus is an assumed extension of that represented needlefish set; the source spelling and complete genus membership remain uncertain.','')
 if n in {'Sphyraena','Sphyraenidae'} or family=='Sphyraenidae':
  return dec([1],'M3','High','Table3.3 explicitly defines Sphyraenidae; taxonomic identity matches the sole barracuda pool. Different principal spellings in Tables3.3/6.1/6.5 remain source evidence.','')
 if gen=='Scomberomorus':return dec([2],'M11','Very low','Only Scomberomorus tritor is represented as a single-species compartment. The unidentified genus is transferred to its represented Spanish-mackerel species; catch composition is unknown.','An unrepresented taxon or unresolved reported genus uses a named single-species relative; the source does not document its inclusion.')
 if family=='Mugilidae' or n=='Mugilidae':
  return dec([27],'M3','High','Table3.3 defines the Mugilidés pool and includes both Liza grandisquamis and Liza falcipinnis; WoRMS verifies this catch label’s Mugilidae scope. The basic/diet representative differs but belongs to the documented pool.','')
 if family=='Gerreidae':return dec([15],'M3','High','Table3.3 defines Gerreidae for this pool, listing Eucinostomus and Gerres; authoritative family membership matches with no competing mojarra pool.','')
 if family=='Dasyatidae' or n=='Dasyatidae':return dec([17],'M3','High','Table3.3 defines Dasyatidae, with Dasyatis margarita/margaritella; WoRMS verifies the catch taxon’s family. Model-area transfer is separate from family membership.','')
 if gen in {'Pomadasys','Plectorhinchus'}:
  return dec([9],'M4','Medium','The source Haemulidae pool explicitly lists multiple Pomadasys and Plectorhinchus species; this broader genus or unlisted congener is an assumed extension of those members.','')
 if n in {'Haemulidae','Inermiidae'}:return dec([9,19],'M10','Very low','Source Table3.3 includes a mixed grunt pool and a dedicated Brachydeuterus compartment; the family/reporting label may include other grunts and bonnetmouths whose source membership is not established.','Broad fish-family composition is unknown across represented pools; unlisted members may have different ecological affinities.')
 if family=='Sciaenidae' or n=='Sciaenidae':
  if n in {'Pseudotolithus','Sciaenidae'}:return dec([5,6],'M9','Medium','Table3.3 separates Pseudotolithus elongatus/Pteroscion from other sciaenids. This broad label is inferred to span both source sciaenid pools; the within-label composition is unknown.','')
  return dec([6],'M4','Medium','The source defines an other-sciaenid pool represented by Pseudotolithus species; authoritative family membership supports an explicit extension to this unlisted sciaenid. Group5 is reserved for the separately documented P.elongatus/Pteroscion set.','')
 if gen=='Elops':return dec([7],'M3','High','Table3.3 defines Elopidae and lists Elops lacerta and Elops senegalensis; the genus reporting label falls within this single source pool.','')
 if gen=='Cynoglossus':return dec([14],'M3','High','The source Cynoglossidae pool contains tonguesoles; source-listed monodi/senegalensis and authoritative genus membership support the reporting label or congener.','')
 if family=='Carangidae' or n=='Carangidae':
  if n=='Carangidae':return dec([10,11,12],'M9','Medium','Source Table3.3 separates the dedicated Chloroscombrus compartment, a multi-species Carangidae pool, and other Carangidae (Trachinotus). The family catch is inferred to span these pools, excluding neither named nor residual members.','')
  if gen=='Trachinotus':return dec([12],'M4','Medium','Table3.3 explicitly places T.ovatus and T.teraia in the other-Carangidae pool. The genus catch label is an assumed extension beyond those named members; absence of a competing pompano compartment does not establish exhaustive genus membership.','')
  if gen=='Caranx':return dec([11],'M4','Medium','Table3.3 lists multiple Caranx species in the Carangidae pool. This unlisted congener or genus label is an assumed extension, excluding dedicated Chloroscombrus and Trachinotus pools.','')
  return dec([11],'M11','Very low','The catch label is a carangid, but its inclusion is not documented in the listed Caranx/Decapterus/Hemicaranx/Lichia pool. That pool is the closest represented jack/scad analogue; the dedicated Chloroscombrus and Trachinotus pools are less directly related.','Unlisted jack/scad taxa use the source Carangidae pool as a taxonomic analogue; their ecology and actual source membership remain uncertain.')
 if n=='Sardinella':return dec([26],'M3','High','Table3.3 explicitly includes both regionally caught Sardinella aurita and S.maderensis in the other-clupeid pool; the reported genus is the union of those regional species (FAO small-pelagics source).','',sources=['THESIS_GROUPS','THESIS_MEMBERS','FAO_SARDINELLA','CATCH'])
 if n in {'Clupeidae','Clupeiformes'}:return dec([18,22,25,26],'M10','Very low','The broad label can include ilisha, Pellonula, Ethmalosa and Sardinella as well as unrepresented clupeiform taxa. Use all meaningful source clupeiform pools; retain the source’s real zero catch for Pellonula group22.','Broad clupeid or clupeiform composition is unknown across dedicated and pooled source compartments.')
 if gen in {'Sardina','Alosa','Engraulis'} or n in {'Engraulidae','Atherinidae','Myctophidae','Inermiidae'} or (fg.startswith('Small pelagics') and n!='Diplodus bellottii'):
  return dec([26],'M11','Very low','This small pelagic is not listed in the source other-clupeid pool. Sardinella is the closest schooling small-pelagic analogue; different taxonomy and, for deep-water taxa, habitat are explicitly transferred.','Unrepresented small pelagics use the source Sardinella pool as a schooling-fish analogue; taxonomy and sometimes habitat differ.',sources=['THESIS_GROUPS','THESIS_MEMBERS','CATCH','FAO_PILCHARD'])
 if fg=='Cephalopods':return dec([32],'M11','Very low','The thesis has no cephalopod compartment. Macrobenthos is the closest represented molluscan/benthic-invertebrate pool, dominated by bivalves/gastropods rather than predatory cephalopods. Pelagic squid and argonaut components add a pelagic-to-benthic mismatch.','Cephalopods are unrepresented; a bivalve/gastropod-dominated macrobenthos analogue transfers trophic function and, for pelagic forms, habitat.')
 if cls in {'Bivalvia','Gastropoda'} or n in {'Bivalvia','Gastropoda','Pteriomorphia','Mytilidae','Veneridae'}:
  return dec([32],'M3','High','Thesis section4.2.2.2.b explicitly places bivalves and gastropods in macrobenthos; WoRMS verifies the catch label’s class. No within-pool species split is required.','',sources=['THESIS_MACROBENTHOS','THESIS_GROUPS','TAXONOMY','CATCH'])
 if n in {'Echinoidea','Paracentrotus lividus'}:return dec([32],'M3','High','Thesis section4.2.2.2.b explicitly includes echinoids in macrobenthos; authoritative taxonomy confirms the catch taxon.','',sources=['THESIS_MACROBENTHOS','THESIS_GROUPS','TAXONOMY','CATCH'])
 if n=='Mollusca':return dec([32],'M10','Very low','Source macrobenthos explicitly includes bivalves/gastropods, but the broad Mollusca catch label also includes unrepresented cephalopods and other molluscs. Entire composition is unknown.','Broad mollusc composition is unknown and includes unrepresented cephalopods; all catch is approximated by the source macrobenthos pool.')
 if fg=='Shrimps' and n not in {'Malacostraca','Miscellaneous marine crustaceans'}:
  if n=='Penaeus notialis':return dec([30],'M4','Medium','Thesis section3.3.4.1.a explicitly discusses P.notialis occurrence in Sine-Saloum, but Table3.3 marks only Penaeus duorarum as the Saloum shrimp principal and does not mark P.notialis in the Saloum column. Its inclusion in generic Crevettes remains an evidence-supported contextual extension.','',sources=['THESIS_CRUSTACEANS','THESIS_MEMBERS','THESIS_GROUPS','CATCH'])
  if n=='Dendrobranchiata':return dec([30],'M10','Very low','The reported order can include coastal penaeids and unrepresented deep-water/pelagic shrimp families; the source shrimp pool is based on estuarine Penaeus/Macrobrachium. Entire unidentified within-order composition is approximated by this closest shrimp pool.','Broad shrimp reporting composition is unknown and can include offshore/deep-water families absent from the estuarine source pool.',sources=['THESIS_CRUSTACEANS','THESIS_GROUPS','CATCH'])
  if n in {'Penaeidae','Penaeus kerathurus','Parapenaeopsis atlantica','Palaemonidae','Crangon'}:return dec([30],'M4','Medium','The source shrimp pool explicitly discusses Penaeus and Macrobrachium; this unlisted relative or broader shrimp category is a taxonomic extension, with coastal/benthic composition transferred.','',sources=['THESIS_CRUSTACEANS','THESIS_GROUPS','CATCH'])
  return dec([30],'M11','Very low','The source shrimp pool is based on estuarine Penaeus/Macrobrachium. This reported shrimp is unlisted and may represent deep-water offshore taxa; taxonomy remains related but habitat and fishery differ.','Unrepresented offshore/deep-water shrimps use the estuarine shrimp pool; source taxonomic and habitat containment is unverified.',sources=['THESIS_CRUSTACEANS','THESIS_GROUPS','CATCH'])
 if n=='Portunidae':return dec([31],'M3','High','Thesis section3.3.4.1.b explicitly restricts the model crab group to Portunidae, including Callinectes. This exact family catch fits that definition.','',sources=['THESIS_CRUSTACEANS','THESIS_GROUPS','TAXONOMY','CATCH'])
 if n in {'Decapoda','Malacostraca','Miscellaneous marine crustaceans'}:return dec([30,31],'M10','Very low','This broad crustacean label includes represented shrimp/portunid crabs and unrepresented lobsters or other crustaceans. Both meaningful source macrocrustacean pools are retained; neither its shrimp/crab nor unsupported composition is observed.','Broad crustacean composition is unknown and can include unrepresented lobsters/krill; a shrimp-and-portunid-crab mixture is assumed.',sources=['THESIS_CRUSTACEANS','THESIS_GROUPS','CATCH'])
 if fg=='Lobsters, crabs':return dec([31],'M11','Very low','The source crab pool is restricted to portunids. This non-portunid crab or lobster is an unrepresented decapod; the closest benthic macrocrustacean analogue is the crab pool rather than shrimps or microfauna. Deep-water/rocky lobster habitat and feeding may differ.','Non-portunid crabs and lobsters use the source portunid crab pool as a benthic decapod analogue; taxonomy, habitat and fishery differ.',sources=['THESIS_CRUSTACEANS','THESIS_GROUPS','CATCH'])
 if n=='Miscellaneous aquatic invertebrates':return dec([30,31,32,33,34],'M10','Very low','Unknown invertebrate catch composition may span shrimp, crabs, macrobenthos, meiobenthos and zooplankton. These consumer pools are meaningful candidates; producers and detritus are excluded. No observed mixture is available.','Unidentified aquatic invertebrates use a biomass-weighted mixture of represented consumer pools; unrepresented components and reporting composition remain unknown.')
 if fg=='Other demersal invertebrates':return dec([32],'M11','Very low','The source macrobenthos includes molluscs, worms and echinoids. This unlisted benthic invertebrate is assigned as an ecological bottom-fauna analogue, without claiming explicit source inclusion.','Unlisted benthic invertebrates use macrobenthos as a bottom-fauna analogue; the exact taxonomic/source composition is unverified.')
 if n in {'Chondrichthyes','Elasmobranchii','Batoidea','Rajiformes'}:return dec([1,17],'M10','Very low','Broad cartilaginous composition is unknown. The represented dasyatid pool is a benthic ray analogue; the barracuda pool is a predatory pelagic-fish analogue for unrepresented sharks. Chimaeras, sawfish and planktivorous rays are not represented.','Broad cartilaginous-fish composition mixes ray and predatory-fish analogues; unrepresented sharks, chimaeras and specialized rays remain a major biological mismatch.')
 if 'sharks' in fg:
  benthic=gen in {'Mustelus','Scyliorhinus','Squalus','Etmopterus','Galeus','Squatina','Leptocharias','Centrophorus','Centroscymnus','Centroscyllium','Centroselachus','Deania','Dalatias','Echinorhinus','Oxynotus','Scymnodon','Somniosus'} or n in {'Scyliorhinidae','Triakidae','Squalidae','Squaliformes','Squatinidae'}
  return dec([17 if benthic else 1],'M11','Very low','No shark compartment exists. '+('The dasyatid pool supplies a weak benthic-cartilaginous-feeder analogue; shark form, trophic ecology and often depth differ.' if benthic else 'The Sphyraenidae pool supplies a weak predatory pelagic-fish analogue; shark taxonomy, physiology and offshore/deep habitat differ. Filter-feeding forms are especially poorly represented.'),'Sharks have no source compartment; benthic cartilaginous or pelagic predatory-fish analogues transfer body form, trophic ecology and often depth.',sources=['THESIS_GROUPS','THESIS_MEMBERS','CATCH','FAO_SHARKS','FAO_BARRACUDA','FAO_DASYATIS'])
 if 'rays' in fg or n=='Chimaeriformes':return dec([17],'M11','Very low','The source Dasyatidae pool is the closest represented cartilaginous/bottom-feeding fish analogue. This ray/chimaera lies outside the documented family; pelagic manta and deep-water forms have additional habitat and feeding mismatches.','Non-dasyatid rays and chimaeras use the source dasyatid pool; specialized morphology, feeding and sometimes pelagic/deep habitat differ.',sources=['THESIS_GROUPS','THESIS_MEMBERS','CATCH','FAO_DASYATIS'])
 if n in {'Actinopterygii','Marine finfishes not identified','Marine fishes not identified','Perciformes'}:
  ids=[g for g in range(1,30) if g!=17]
  return dec(ids,'M10','Very low','The reported broad bony-fish assemblage may span named and pooled source fish compartments, including both pelagic and bottom-associated taxa. Use all represented bony-fish pools; exclude the dasyatid, invertebrate, producer and detrital pools. Source composition is a proxy, not regional unidentified-catch composition.','Broad bony-fish composition is unknown across named and residual estuarine fish pools; whole-LME unidentified catch is approximated by the source assemblage.',sources=['THESIS_GROUPS','THESIS_MEMBERS','CATCH','FAO_REPORTING'])
 if n=='Marine groundfishes not identified':return dec([3,4,5,6,8,9,13,14,15,16,19,20,23,27,28,29],'M10','Very low','Groundfish reporting narrows the bony-fish label to plausible bottom-associated source fish; dedicated pelagic and cartilaginous pools are excluded. Actual species, depth and capture composition are unknown.','Groundfish composition is unknown among source bottom-associated pools; the estuarine assemblage is transferred to whole-LME reported groundfish.',sources=['THESIS_GROUPS','THESIS_MEMBERS','CATCH','FAO_REPORTING'])
 if n=='Marine pelagic fishes not identified':return dec([1,2,7,10,11,12,18,21,22,23,24,25,26,27],'M10','Very low','Pelagic reporting leaves composition among plausible source water-column fish unknown, including named and pooled taxa and flexible benthopelagic members. Whole-LME offshore components are unrepresented.','Unidentified pelagic-fish composition is unknown; a mixture of source pelagic/benthopelagic pools transfers the estuarine assemblage to offshore regional catch.',sources=['THESIS_GROUPS','THESIS_MEMBERS','CATCH','FAO_REPORTING'])
 if 'flatfishes' in fg:return dec([13,14],'M11','Very low','The model represents a Citarichthys/Psettodes pool and a Cynoglossidae pool; this other flatfish is unlisted. Both closest flattened-bottom-fish analogues are retained, with family and habitat/depth mismatches.','Unrepresented flatfish families use the Citarichthys/Psettodes and Cynoglossus pools; source taxonomic containment and their target split are unknown.')
 if gen in {'Acanthurus','Sarpa','Sparisoma','Kyphosus'} or n in {'Acanthuridae','Scaridae'}:
  return dec([27],'M11','Very low','The source Mugilidés pool provides a detritus/algae-feeding coastal-fish analogue for this unrepresented herbivorous reef/coastal taxon. Reef browsing, body form and actual group membership differ.','Unrepresented reef/coastal herbivores use the mullet pool as a feeding analogue; taxonomy and habitat differ.',sources=['THESIS_GROUPS','THESIS_MEMBERS','CATCH','FAO_MULLET'])
 if gen in {'Aphanopus','Lepidopus','Promethichthys','Ruvettus','Lepidocybium'} or n in {'Trichiuridae','Trichiurus','Gempylidae'}:return dec([23],'M11','Very low','The dedicated Trichiurus lepturus compartment is the closest represented elongate predatory/benthopelagic fish analogue. This broader label or other scabbard/snake-mackerel taxon is not source membership; deep habitat and taxonomy may differ.','Unrepresented elongate benthopelagic predators use single-species Trichiurus lepturus; broader taxonomy and often deep-water habitat differ.')
 if 'pelagics' in fg and 'benthopelagics' not in fg or 'bathypelagics' in fg:
  return dec([1],'M11','Very low','The source barracuda pool is a represented predatory water-column fish assemblage. This unlisted pelagic/deep-water fish has no matching source compartment; body form, offshore/deep habitat and trophic function may differ.','Unrepresented pelagic and bathypelagic fishes use the predatory barracuda pool; habitat, taxonomy and trophic specialization differ.',sources=['THESIS_GROUPS','THESIS_MEMBERS','CATCH','FAO_BARRACUDA'])
 return dec([9],'M11','Very low','The source Pomadasys/Plectorhinchus pool represents coastal bottom-associated fishes. Provider classification identifies this taxon as '+fg+'; it is unlisted and transferred only as a weak coastal demersal/reef fish analogue. Deep-water, reef and body-form/trophic differences remain.','Unrepresented demersal, reef and benthopelagic fishes use the coastal grunt pool; family, depth, habitat and feeding specialization can differ.',sources=['THESIS_GROUPS','THESIS_MEMBERS','CATCH','FAO_DEMERSAL'])

rows=[]
for r in ref:
 d=choose(r); ids=d['candidate_ids']; assert len(set(ids))==len(ids) and all(i in groups and i<35 for i in ids)
 vals=[float(groups[i]['Y']) if groups[i]['Y'] is not None else None for i in ids]
 biomass=[float(groups[i]['B']) if groups[i]['B'] is not None else None for i in ids]
 if len(ids)==1:weights=[1.0];wrule='W1';wconf='High';weight_reason='One supported or disclosed analogue group; 100% by definition, not an observed composition estimate.';basis='none';total=1.0
 elif all(v is not None and math.isfinite(v) and v>=0 for v in vals) and math.fsum(vals)>0:
  total=math.fsum(vals);weights=[v/total for v in vals];wrule='W4';wconf='Medium';basis='Y';weight_reason='Thesis Table6.5 source-model Y proportions are a candidate composition proxy for regional landings; these are estimates Y=B×F, not measured regional taxon catch shares. Fixed source-period and study-area transfer is assumed.'
 elif all(v is not None and math.isfinite(v) and v>=0 for v in biomass) and math.fsum(biomass)>0:
  total=math.fsum(biomass);weights=[v/total for v in biomass];wrule='W9';wconf='Medium';basis='B';weight_reason='Source catch allocation rejected because at least one candidate Y is a printed dash (unknown), not zero. Complete Table6.5 biomass proportions are used under a source assemblage/catchability proxy and fixed time/area transfer assumption; model-estimated parenthesized biomass remains labelled estimated.'
 else:weights=[None]*len(ids);wrule='W8';wconf='Unresolved';basis=None;total=None;weight_reason='Neither source catch nor biomass supplies complete positive usable proportions; no defensible assumed split.'
 conf=max([d['membership_confidence'],wconf],key=confidence_order.get)
 assignments=[{'group_id':i,'group_name':groups[i]['group_name'],'weight':w,'Y_literal':groups[i]['Y_literal'],'Y_source_value':y,'B_literal':groups[i]['B_literal'],'B_source_value':b,'B_model_estimated':groups[i]['B_estimated'],'Y_model_estimated':groups[i]['Y_estimated'],'inclusion_reason':d['membership_reason']} for i,w,y,b in zip(ids,weights,vals,biomass)]
 reason=d['membership_reason']+' '+weight_reason+' Sources: '+', '.join(d['sources'])+'.'
 display='; '.join(a['group_name']+' ('+('?' if a['weight'] is None else f"{100*a['weight']:.6g}%")+')' for a in assignments)
 rows.append({**r,**d,'allocation_rule':wrule,'allocation_confidence':wconf,'allocation_reason':weight_reason,'allocation_basis':basis,'allocation_total_source':total,'catch_attempt_complete':all(v is not None for v in vals),'assignments':assignments,'overall_confidence':conf,'reason':reason,'mapped_display':display,'model_id':'27_Villanueva2004_SineSaloum_thesis_1991-1992','adopted':False,'model_sppr':None,'model_status':'BLOCKED: unresolved thesis compartment identity; no computational loading performed','exclusions':'Eligible sets established from source biological definitions; unrelated fish/invertebrate/producer pools excluded. Dedicated named compartments remain candidates for broad reporting labels; missing source values never remove candidates.'})
rows.sort(key=lambda r:(r['simple_ppr_tC'] is None,-r['simple_ppr_tC'] if r['simple_ppr_tC'] is not None else 0,r['taxon']))
for r in rows:
 r['model_id']='27_Villanueva2004_SineSaloum'
 r['variant_id']='thesis_1991-1992_Table6_5_AnnexIIA'
dump('taxon_mapping_audit.json',rows)
lookup={r['taxon']:r for r in rows}
saloum_audit=[]
for entry in literal_members:
 if entry['Saloum'] not in ['+','*']:continue
 source_name=entry['species_literal']
 matches=[source_name] if source_name in lookup else []
 authority=tax.get(source_name,{})
 if not matches and authority.get('valid_AphiaID'):
  matches=[n for n in lookup if tax.get(n,{}).get('valid_AphiaID')==authority['valid_AphiaID']]
 if source_name=='Tylosorus crocodilus':matches=['Tylosurus crocodilus']
 if source_name=='Arius heudeloti':matches=['Carlarius heudelotii']
 saloum_audit.append({**entry,'matched_catch_labels':matches,'match_type':'exact literal' if source_name in lookup else 'verified authoritative accepted taxon' if authority.get('valid_AphiaID') and matches else 'tentative orthographic bridge; retained Low' if matches else 'no exact or verified synonym catch label in the512taxon universe','mapping_findings':[{'taxon':n,'membership_rule':lookup[n]['membership_rule'],'membership_confidence':lookup[n]['membership_confidence'],'group_ids':lookup[n]['candidate_ids'],'reason':lookup[n]['membership_reason']} for n in matches],'source_conflict_retained':source_name in {'Pteroscion peli','Psettodes belcheri','Epinephelus aeneus','Tylosorus crocodilus'}})
assert all(a['mapping_findings'][0]['membership_confidence']!='Very low' for a in saloum_audit if a['species_literal'] in lookup)
dump('explicit_saloum_membership_coverage_audit.json',{'scope':'Every literal Table3.3 Saloum+/* row, with exact catch and verified synonym matches; source-listed species absent from catch are preserved, not fabricated. Generic ranks require separate membership evidence.','source_rows':saloum_audit,'exact_catch_member_omissions_remaining':[],'orthographic_bridge_unresolved':'Tylosorus crocodilus is tentatively identified with Tylosurus crocodilus, retained Low; no authoritative record for source misspelling.','source_internal_conflicts':'Pteroscion and Psettodes source grouping versus Table6.5 single-species caption; duplicate Psettodes placement; Epinephelus/Hemichromis diet identity remain explicit.'})
dump('allocation_evidence.json',[{'taxon':r['taxon'],'candidate_ids':r['candidate_ids'],'allocation_rule':r['allocation_rule'],'allocation_confidence':r['allocation_confidence'],'allocation_basis':r['allocation_basis'],'allocation_total_source':r['allocation_total_source'],'catch_attempt_complete':r['catch_attempt_complete'],'source_period':'1991-1992','source_quantities_unit':'t wet weight/km2/year for Y; t wet weight/km2 for B','allocation_reason':r['allocation_reason'],'all_candidates':r['assignments'],'regional_transfer':'Source estuary composition is provisionally applied to whole-LME taxa and fixed across all1950-2019 regional years/bases; no measured geographic/temporal allocation is claimed.','adopted':False} for r in rows])
cols=['Taxon name','TL','Catch (t)','Simple-chain PPR (t C)','Mapped group names and weights','Confidence level','Reason']
appendix=[dict(zip(cols,[r['taxon'],r['tl'] if r['tl'] is not None else '?',r['catch_t'] if r['catch_t'] is not None else '?',r['simple_ppr_tC'] if r['simple_ppr_tC'] is not None else '?',r['mapped_display'],r['overall_confidence'],r['reason']])) for r in rows]
dump('appendix_rows.json',appendix)
with (M/'appendix_rows.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,cols);w.writeheader();w.writerows(appendix)
catch=math.fsum(r['catch_t'] for r in rows if r['catch_t'] is not None); ppr=math.fsum(r['simple_ppr_tC'] for r in rows if r['simple_ppr_tC'] is not None)
summary={'taxa':len(rows),'source_groups':37,'year':2019,'basis':'landings','basis_definition':'Recorded regional Sea Around Us landings, excluding discards; annual wet-weight tonnes.','method':'Independent simple trophic chain; saved Classic PPR / Taxa coefficient, TE 0.1, catch × coefficient / 9 once.','total_catch_tonnes':catch,'total_simple_chain_ppr_tC':ppr,'known_total_complete':all(r['simple_ppr_tC'] is not None for r in rows),'missing_classic_coefficients':sum(r['missing_classic_coefficient'] for r in rows),'missing_classic_coefficients_positive_catch':sum(r['missing_classic_coefficient'] and r['catch_t']>0 for r in rows),'missing_catch':sum(r['missing_catch'] for r in rows),'confidence_summary':[]}
summary.update({'mapped_taxa':sum(r['overall_confidence']!='Unresolved' for r in rows),'candidate_mapping_catch_percentage':100.0,'model_SPPR_coefficient_catch_coverage_percentage':0.0,'model_annual_PPR_available':False,'candidate_mapping_adopted':False,'source_identity_blocker':'Table6.5 grouper Epinephelus aeneus versus AnnexII.A cichlid Hemichromis fasciatus at group20; no source-supported reconciliation.'})
summary.update({'model_id':'27_Villanueva2004_SineSaloum','variant_id':'thesis_1991-1992_Table6_5_AnnexIIA'})
for conf in confidence_order:
 subset=[r for r in rows if r['overall_confidence']==conf]
 summary['confidence_summary'].append({'label':conf,'taxa':len(subset),'catch_percentage':100*math.fsum(r['catch_t'] for r in subset)/catch,'ppr_percentage':100*math.fsum(r['simple_ppr_tC'] or 0 for r in subset)/ppr})
for key,field in [('membership_summary','membership'),('allocation_summary','allocation')]:
 counts=collections.defaultdict(list)
 for r in rows:counts[(r[field+'_rule'],r[field+'_confidence'])].append(r)
 summary[key]=sorted([{'rule_id':rid,'plain_language_rule':rule_text[rid],'confidence':conf,'ppr_percentage':100*math.fsum(r['simple_ppr_tC'] or 0 for r in subset)/ppr,'taxa':len(subset)} for (rid,conf),subset in counts.items()],key=lambda x:-x['ppr_percentage'])
dump('coverage_summary.json',summary)
reasons=collections.defaultdict(list)
for r in rows:
 if r['overall_confidence']=='Very low':reasons[r['very_low_reason_group']].append(r['taxon'])
dump('very_low_decisions.json',[{'taxa':sorted(v),'reason':k} for k,v in reasons.items()])
sources=[
 ('THESIS_GROUPS','Villanueva (2004) thesis Table6.5, PDF138 / printed114','Exact source37 group identities, pooled principal flags, literal B and Y, estimates and dashes. Y is estimated from B and F; no direct geographic caught-mass allocation.','../evidence/identity/Villanueva2004_thesis_29305.pdf#page=138'),
 ('THESIS_MEMBERS','Villanueva thesis Table3.3, PDF82–83 / printed58–59','Actual Sine-Saloum pool membership and representative/other marks. Repeated Psettodes and single-species-caption conflicts remain disclosed. Table3.3 is group composition, distinct from the multi-ecosystem species list.','../evidence/identity/Villanueva2004_thesis_29305.pdf#page=82'),
 ('THESIS_CRUSTACEANS','Villanueva thesis section3.3.4.1, PDF77 / printed53','Shrimp principal taxa and Sine-Saloum P.notialis context; model crabs explicitly Portunidae. Other crabs/lobsters require analogues.','../evidence/identity/Villanueva2004_thesis_29305.pdf#page=77'),
 ('THESIS_MACROBENTHOS','Villanueva thesis sections3.3.4.2.a and4.2.2.2.b, PDF78 and87','Macrobenthos explicitly contains bivalves/gastropods, annelids/polychaetes and echinoids; representative Corbula trigona. No cephalopod compartment is documented.','../evidence/identity/Villanueva2004_thesis_29305.pdf#page=87'),
 ('TAXONOMY','WoRMS authoritative exact-name records, retrieved3 October2026','Raw responses are retained for125 taxon/source names, with123 uniquely resolved records. The exact source spellings Sphyraena guanchancho and Tylosorus crocodilus are unresolved; historical source spellings are not silently replaced.','authoritative_taxonomy_raw.json'),
 ('CATCH','LME_027.xlsx Catch / Catch and Overview / Settings','Exact512 taxon reporting labels, common/functional classifications and2019 landings; classifications support weak habitat analogues, not exhaustive source membership.','../../../LME_027.xlsx'),
 ('CLASSIC','LME_027.xlsx Classic PPR / Taxa and Annual','Stored412 independent TL/coefficient records and annual arithmetic. No candidate group TL or SPPR generates these coefficients; 100 missing coefficients have zero2019catch.','../../../LME_027.xlsx'),
 ('CLASSIC_METHOD','Independent candidate calculation verification','Annual catch × saved simple-chain coefficient /9 carbon conversion once; all210 basis/year records independently reproduce saved totals.','../calculations/independent_arithmetic_verification.json'),
 ('FAO_SARDINELLA','FAO Northwest Africa sardinella stock identity','Regional Sardinella catch comprises S.aurita and S.maderensis; supports generic regional genus reporting scope, not model proportions.','https://www.fao.org/4/Y2668B/y2668b05.htm'),
 ('FAO_PILCHARD','FAO species identification: Sardina pilchardus','Coastal schooling pelagic pilchard, planktonic prey and range; supports small-pelagic analogy, not source membership.','https://www.fao.org/fishery/docs/CDrom/ARTFIMED/ArtFiWeb/descript/Species/CLUSAPIL.HTML'),
 ('FAO_REPORTING','FAO marine resources statistical tables','Marine fishes nei is Osteichthyes, separated from sharks/rays/chimaeras; reporting scope supports excluding group17 from broad bony-fish candidate sets.','https://www.fao.org/4/y5852e/Y5852E11.htm'),
 ('FAO_SHARKS','FAO Sharks of the World species catalogue, Part2','Primary taxonomy and habitat context for unrepresented shark analogues; no shark source membership or observed allocation is implied.','https://www.fao.org/4/ad123e/ad123e00.htm'),
 ('FAO_BARRACUDA','FAO Sphyraena sphyraena species identification','Barracuda as a predatory pelagic/coastal fish analogue; source pool transfer still includes different species/body forms and offshore/deep habitats.','https://www.fao.org/fishery/docs/CDrom/ARTFIMED/ArtFiWeb/descript/Species/SPHSPSPH.HTML'),
 ('FAO_DASYATIS','FAO living marine resources guide: Dasyatis pastinaca','Demersal soft-bottom stingray feeding on benthic fishes/crustaceans/molluscs; supports only the disclosed benthic analogue.','https://www.fao.org/4/i1276b/i1276b12.pdf'),
 ('FAO_MULLET','FAO Mugil cephalus species profile','Detritus, microalgae and shallow/estuarine feeding context supports the explicitly weak herbivore analogue.','https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_flatheadgreymullet.htm'),
 ('FAO_DEMERSAL','FAO CECAF central Gulf of Guinea demersal/shrimp resources','Source-represented croaker/grunt/threadfin/sole assemblage occurs in estuarine and coastal bottom communities; supports an ecological analogue only, with whole-LME transfer uncertainty.','https://www.fao.org/4/r9762e/R9762E04.htm')]
dump('appendix_sources.json',[{'id':i,'title':t,'supports':s,'target':p,'date':'2026-10-03' if p.startswith('https:') or i=='TAXONOMY' else None,'target_basis':'mapping_directory' if not p.startswith('https:') else 'external'} for i,t,s,p in sources])
assert len(rows)==len(set(r['taxon'] for r in rows))==512
assert {r['taxon'] for r in rows}=={r['taxon'] for r in ref}
assert all(all(a['weight'] is not None and a['weight']>=0 for a in r['assignments']) and abs(math.fsum(a['weight'] for a in r['assignments'])-1)<1e-12 for r in rows)
assert abs(sum(x['catch_percentage'] for x in summary['confidence_summary'])-100)<1e-8
assert abs(sum(x['ppr_percentage'] for x in summary['confidence_summary'])-100)<1e-8
assert all(abs(sum(x['ppr_percentage'] for x in summary[key])-100)<1e-8 for key in ['membership_summary','allocation_summary'])
assert sum(len(v) for v in reasons.values())==sum(r['overall_confidence']=='Very low' for r in rows)
qa={'taxa':512,'groups':37,'model_identity':'thesis Sine-Saloum1991–1992; Table6.5 group identities retained','unique_taxa':True,'complete_universe':True,'zero_catch_taxa':sum(r['catch_t']==0 for r in rows),'weights_max_error':max(abs(math.fsum(a['weight'] for a in r['assignments'])-1) for r in rows),'zero_source_catch_candidates_retained':[(r['taxon'],a['group_id']) for r in rows for a in r['assignments'] if a['Y_source_value']==0],'source_dashes_kept_unknown':True,'no_model_sppr_fabricated':True,'appendix_full_precision_descending':True,'unresolved_taxa':[r['taxon'] for r in rows if r['overall_confidence']=='Unresolved'],'source_membership_conflicts':'Group20 grouper/cichlid; Table3.3 repeated Psettodes; Table6.5 single-species caption versus Table3.3 groups5/13 retained explicitly. Group27 representatives are both members of the documented mullet pool.','only_candidate_outputs_written':True,'classic_PPR_independent_of_mapping':True,'parent_verification_required':'Reconcile exact37 group canonical identity, independently review all membership claims and arithmetic, render Word/Excel and verify source links.'}
dump('mapping_verification.json',qa)
print(json.dumps(summary,ensure_ascii=False,indent=2))
