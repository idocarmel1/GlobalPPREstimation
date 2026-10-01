from pathlib import Path
import json,re,csv,hashlib,datetime,collections
O=Path(__file__).resolve().parent
R=O.parents[2]
catch=json.loads((O/'catch_label_universe.json').read_text(encoding='utf-8'))
groups=json.loads((O/'source_group_definitions.json').read_text(encoding='utf-8'))
G={g['group_seq']:g for g in groups}
worms=json.loads((O/'worms_name_lookup.json').read_text(encoding='utf-8'))
sw=json.loads((O/'worms_source_name_lookup.json').read_text(encoding='utf-8'))
def authority(name,lookup=worms):
    found=[r for r in lookup.get(name,[]) if r.get('scientificname','').lower()==name.lower()]
    return next((r for r in found if r.get('status')=='accepted'),found[0] if found else None)
raw={};valid={};families=collections.defaultdict(set);genera=collections.defaultdict(set);orders=collections.defaultdict(set);explicit_genus=collections.defaultdict(set)
source_members=[]
for g in groups:
    d=g['description'].split(':',1)[-1]
    terms=re.findall(r'\b[A-Z][a-z]+\s+[a-z][a-z-]+(?:\s+[a-z]+)?',d)
    for t in terms:
        t=t.strip();raw.setdefault(t,set()).add(g['group_seq']);a=authority(t,sw)
        if a:
            valid.setdefault(a['valid_AphiaID'],set()).add(g['group_seq'])
            if a.get('family'):families[a['family']].add(g['group_seq'])
            if a.get('genus'):genera[a['genus']].add(g['group_seq'])
            if a.get('order'):orders[a['order']].add(g['group_seq'])
        source_members.append({'source_name':t,'group_id':g['group_seq'],'authority':a})
    for genus in re.findall(r'\b([A-Z][a-z]+)\s+spp\.?',d):explicit_genus[genus].add(g['group_seq'])
    if g['group_seq']==57:explicit_genus['Crangon'].add(57)

overrides={}
def set_rule(names,ids,rule,confidence,rationale,assumption=True):
    for n in names.split('|'):overrides[n]=(ids,rule,confidence,rationale,assumption)

# Coherent documented taxa with one represented generic compartment.
set_rule('Bivalvia|Cardiidae|Bothidae|Pectinidae|Mytilidae|Mytilus|Ostreidae|Veneridae|Mactridae|Pteriomorphia',[51],'M3','High','Authoritative bivalve identity fits the explicit Bivalves compartment; no ecological or stage boundary separates these catch labels.',False)
# Bothidae is a fish family, corrected below.
set_rule('Gastropoda',[52],'M3','High','Authoritative Gastropoda identity matches the explicit Gastropods compartment.',False)
set_rule('Pleuronectiformes|Pleuronectoidei|Bothidae|Pleuronectidae|Scophthalmidae|Soleidae|Lepidorhombus|Microchirus',[35],'M3','High','Verified flatfish lineage fits the documented Flatfish compartment; no competing flatfish stage or habitat pool is defined.',False)
set_rule('Holothuroidea|Echinoidea',[61],'M3','High','Verified echinoderm class and provider benthic reporting fit Mobile benthos, whose composition includes sea cucumbers and sea urchins.',False)
set_rule('Ascidiacea|Spongia',[62],'M3','High','Verified ascidian or sponge identity fits Sessile benthos, which explicitly enumerates these sessile benthic lineages.',False)
set_rule('Gadidae',[32],'M3','High','The source explicitly names Gadidae and lists regional gadids; authority confirms the family. Phycis and Molva are currently separate families, preventing a false family-wide cross-boundary conflict.',False)
set_rule('Xiphiidae',[16],'M3','High','Swordfish is the family representative and source Xiphias gladius has a dedicated pool; the catch reporting family fits that compartment.',False)
set_rule('Torpedinidae',[47],'M3','High','The source defines Torpedos and explicitly includes Torpedo spp.; verified electric-ray family identity fits this compartment.',False)
set_rule('Mugilidae',[34],'M9','Medium','Regional mullets are represented together in group34, including Mugil, Chelon and historical Liza. Extending the listed regional members to the entire reporting family remains an assumption.')
set_rule('Sparidae',[25,33],'M9','Medium','Modern Sparidae includes source Spicara in25 as well as seabreams in33; do not force the entire reporting family into the source pool named Sparidae. Provider constituent composition is unavailable.')
set_rule('Labridae',[34,40,41],'M9','Medium','Source Labrus/Symphodus occupy34 and40, and Pteragogus occupies41. All three pools are eligible; treating the regional family mixture as their union is assumed.')
set_rule('Gobiidae',[40,41],'M9','Medium','Aphia minuta is explicitly source40 while Gobius and multiple other gobies are41; reporting-family composition is not observed.')
set_rule('Serranidae',[31,34,40],'M9','Medium','Groupers occur in31, Serranus in34 and Anthias anthias in40. Broad bass/groupers reporting must retain all compatible named and residual groups.')
set_rule('Scyliorhinidae',[43,44,45],'M9','Medium','Source catshark members occur in dedicated43/44 and residual45; family composition is unknown, but all three source pools are eligible.')
set_rule('Scyliorhinus',[43,45],'M9','Medium','Source explicitly places S. canicula in43 and S. stellaris in45; genus composition is unknown.')
set_rule('Galeus',[44,45],'M9','Medium','Source explicitly places G. melastomus in44 and G. atlanticus in45; genus composition is unknown.')
set_rule('Mullus',[37,38,39],'M9','Medium','Source Mullus barbatus has stages37/38 and M. surmuletus has39. Both species and both red-mullet stages remain eligible.')
set_rule('Mullidae',[37,38,39,41],'M9','Medium','Mullus occupies37/38/39 while explicitly listed Upeneus occupies41. Regional family reporting can span these pools.')
set_rule('Carangidae',[17,19,20],'M9','Medium','Source carangids include large Lichia/Seriola in17, Trachurus in19 and Caranx/Naucrates in20; generic reporting composition is inferred.')
set_rule('Sciaenidae',[26,34],'M9','Medium','Argyrosomus regius is source26 while Sciaena/Umbrina are34; both pools are eligible for drums/croakers reporting.')
set_rule('Triglidae|Scorpaeniformes',[34,40],'M9','Medium','Regional gurnards/scorpionfish representatives occupy34, and Lepidotrigla occupies40; source definitions take precedence over coarse provider size categories.')
set_rule('Trachinidae|Trachinus',[34,36],'M9','Medium','Source Trachinus radiatus is34 while T. draco/araneus are36; broad weevers span both pools.')
set_rule('Centrolophidae',[20,26,27],'M9','Medium','Source Schedophilus medusophagus is20, S. ovalis26 and Centrolophus niger27; preserve all these eligible pools.')
set_rule('Macrouridae',[26,42],'M9','Medium','Source Coelorinchus/Nezumia rattails occur in26 and Coelorinchus occa/Trachyrincus in42; reporting mixture is inferred.')
set_rule('Moridae',[26,27],'M9','Medium','Source morids Gadella/Physiculus occur in26 and Mora/Lepidion in27; retain both despite the coarse provider benthopelagic label.')
set_rule('Congridae',[31,34,40],'M9','Medium','Source Conger is31, Gnathophis34 and Ariosoma40; family reporting spans all three.')
set_rule('Anguilliformes',[27,31,34,36,40],'M10','Very low','Eel/moray reporting spans commercial and residual benthic/bathypelagic pools; source Nemichthys/Nettastoma/Notacanthus entries and unlisted eels make composition uncertain. This is a broad mixture approximation.')
set_rule('Clupeidae',[20,21,22,25],'M9','Medium','Source Alosa is20, Sardina stages21/22 and Sardinella/Sprattus25. Provider family reporting composition is unknown and historical clupeid concepts are transferred.')
set_rule('Clupeiformes',[20,21,22,23,24,25],'M9','Medium','Shads, sardines and anchovies have eligible pools20-25, including both represented stage pairs; no catch composition is measured.')
set_rule('Engraulidae',[23,24],'M9','Medium','The Mediterranean anchovy family reporting is inferred to the source European anchovy pair; provider family constituents are not retained.')
set_rule('Batoidea',[14,46,47],'M10','Very low','Broad batoid reporting may include source Mobula14, rays/skates46 and electric rays47, plus unlisted guitarfishes. Approximate the full plausible set rather than residual46 only.')
set_rule('Myliobatidae',[14,46],'M9','Medium','Historical eagle/manta-ray reporting can include source Mobula14 and eagle rays46; family concepts and reporting composition are transferred.')
set_rule('Chondrichthyes', [13,14,43,44,45,46,47],'M10','Very low','Broad cartilaginous-fish reporting spans pelagic sharks13, basking/devil rays14, dedicated/residual demersal sharks43-45 and rays46/47. Chimaera is explicitly source45. Composition remains uncertain.')
set_rule('Elasmobranchii', [13,14,43,44,45,46,47],'M10','Very low','Elasmobranchii reports sharks, rays and skates, excluding chimaeras (FAO 3.1.1). Groups13/14/43-47 form a weak pooled proxy. Source45 is eligible through listed sharks (e.g. Centrophorus and Mustelus); its Chimaera monstrosa is outside target scope. Pooled source composition and target proportions remain uncertain.')
set_rule('Lamniformes',[13,14],'M9','Medium','Source mackerel-shark order includes source pelagic sharks13 and basking shark14; generic catch composition is inferred.')
set_rule('Triakidae',[13,45],'M9','Medium','Galeorhinus is explicitly source13 while Mustelus is45; houndshark reporting spans both pools.')
set_rule('Chimaeriformes',[45],'M9','Medium','Source Chimaera monstrosa is explicitly45; treating the regional order as that represented chimaera pool is inferred, despite the provider Large rays label.')
set_rule('Cephalopoda',[48,49,50],'M9','Medium','Source defines benthic, benthopelagic and mesopelagic cephalopod compartments; all three are eligible and composition is assumed.')
set_rule('Teuthida',[48,49,50],'M10','Very low','Provider Squids does not retain its constituent species or distinguish bobtail/benthic from benthopelagic/mesopelagic squid. Source squid-like taxa occur in48/49/50, so retain all plausible compartments.')
set_rule('Octopoda',[48,49,50],'M9','Medium','Source octopods include benthic octopus48, Opisthoteuthis/Ocythoe49 and Argonauta50; order reporting spans the three ecological pools.')
set_rule('Sepiida',[48,50],'M9','Medium','The provider calls this Cuttlefishes, bobtail squids. Source cuttlefish and most bobtails are48, while Heteroteuthis/Stoloteuthis are50; include the latter under the reporting interpretation.')
set_rule('Sepiidae|Octopodidae',[48],'M9','Medium','The listed regional cuttlefish/true octopus representatives occur in the benthic cephalopod pool; extension of the reporting family beyond listed species is assumed.')
set_rule('Loliginidae|Ommastrephidae',[49],'M9','Medium','Source listed loliginid/ommastrephid squids occupy benthopelagic cephalopods49; regional family reporting extension is inferred.')
set_rule('Decapoda',[53,54,55,56,57,58,59,60],'M9','Medium','Verified decapod reporting spans all shrimp53-57 and lobster/crab58-60 compartments; source commercial/non-commercial labels do not exclude caught members.')
set_rule('Dendrobranchiata',[53,54,55,56,57],'M9','Medium','Penaeoid/sergestoid shrimp reporting spans dedicated shrimp53-55, commercial56 and residual57; reporting composition is inferred.')
set_rule('Malacostraca|Miscellaneous marine crustaceans',[53,54,55,56,57,58,59,60,61,65],'M10','Very low','Broad crustacean reporting may include shrimp, crab/lobster, benthic peracarids61 and krill/plankton65; all compatible named and residual compartments are retained. Composition is unobserved.')
set_rule('Anomura',[60],'M9','Medium','Source squat lobsters/hermit crabs are explicitly residual60; extension to the broad regional anomuran label is inferred.')
set_rule('Nephropidae',[58,59],'M9','Medium','Nephrops has dedicated58 while Homarus is59; both clawed-lobster source pools remain eligible.')
set_rule('Aristeidae',[54,55,57],'M9','Medium','Dedicated Aristeus54 and Aristaeomorpha55 plus residual deep-water shrimps57 are retained under historical aristeid reporting uncertainty.')
set_rule('Penaeidae',[53,56,57],'M9','Medium','Source Parapenaeus occupies53, Penaeus56 and residual penaeids Funchalia/Penaeopsis57; commercial reporting does not prove confinement to56.')
set_rule('Squillidae',[59,60],'M9','Medium','Source Squilla mantis occupies59 while Erugosquilla and other mantis shrimps occupy60; provider Shrimp classification is broader than true decapod shrimps.')
set_rule('Portunidae|Portunus',[59,60],'M9','Medium','Source Necora puber is59 while Liocarcinus/Portunus and other swimming crabs are60; commercial/non-commercial names do not establish catch composition.')
set_rule('Scombridae',[15,17,18,20],'M9','Medium','Tunas, mackerels and bonitos span source bluefin15, albacore/large pelagics17, mackerel18 and bonito20; broad family composition is inferred.')
set_rule('Scombroidei',[15,16,17,18,20,26],'M10','Very low','Historical broad tunas/bonitos/billfish reporting has uncertain scope, possibly including cutlassfish26. Approximate with compatible dedicated and residual source pools, not large-pelagic17 alone.')
set_rule('Thunnus',[15,17],'M9','Medium','Source bluefin Thunnus thynnus is15 and albacore T. alalunga17; unlisted tuna species require extension to the large-pelagic pool.')
set_rule('Marine fishes not identified|Marine finfishes not identified',list(range(13,48)),'M10','Very low','Unidentified marine finfish can span all represented bony/cartilaginous fish compartments13-47. Provider Medium demersals is a coarse tag and does not establish species containment. Use an explicitly assumed broad mixture.')
set_rule('Osteichthyes',[14]+list(range(15,43)),'M10','Very low','Unidentified bony fish span dedicated/residual teleost compartments15-42 plus Mola-containing14. Group14 also contains cartilaginous fish, so that pool is a coarse approximation; exclude shark/ray-only pools.')
set_rule('Marine groundfishes not identified',[13]+list(range(26,48)),'M10','Very low','Groundfish reporting can span benthic/benthopelagic/deep demersal teleost and shark/ray pools, including dedicated groups; source13 contains some bottom-associated sharks and27 includes deep benthic-associated fishes. Provider composition is absent.')
set_rule('Marine pelagic fishes not identified',list(range(13,28))+[46],'M10','Very low','Pelagic reporting can span all dedicated/residual pelagic pools13-27 and the pelagic stingray component in46. The mixed ray pool is a coarse analogue and unobserved composition is assumed.')
set_rule('Miscellaneous diadromous fishes',[17,20,34],'M10','Very low','Represented Alosa20 and Anguilla/mullets34 provide direct diadromous connections; unrepresented sea-run fishes require a large-pelagic17 analogue. Mixture and habitat transfer remain uncertain.')
set_rule('Miscellaneous aquatic invertebrates',list(range(48,66)),'M10','Very low','Unidentified aquatic invertebrate reporting may include molluscs, crustaceans, mobile/sessile benthos, jellyfish, corals and zooplankton. Retain compatible named and residual invertebrate pools48-65; composition is unknown.')
set_rule('Mollusca',[48,49,50,51,52],'M9','Medium','Provider clams/snails/squids/octopuses and authoritative mollusc identity support cephalopod48-50, bivalve51 and gastropod52 pools; extension to unlisted minor mollusc classes remains assumed.')
set_rule('Echinodermata',[61],'M9','Medium','Source mobile benthos61 explicitly enumerates echinoderm classes. Extending to the broad reporting phylum is inferred; unusual source placements and any stalked forms remain a limitation.')
set_rule('Acipenser sturio|Acipenseridae|Esox lucius',[31],'M11','Very low','No explicit sturgeon/pike compartment exists. Large demersal fish31 is the closest represented size/feeding analogue; freshwater/diadromous habitat and species composition mismatch remain explicit.')
set_rule('Salmo trutta',[17],'M11','Very low','No salmonid compartment exists; large pelagic fish17 is the closest represented marine-stage analogue. Cold-water and diadromous/freshwater life-history mismatch remains explicit.')
set_rule('Istiophoridae|Istiophorus albicans|Kajikia albida|Makaira nigricans|Tetrapturus belone',[16,17],'M6','Low','Unlisted billfish share ecology with dedicated Swordfish16 and Other large pelagic17; both are meaningful but competing represented pools, so membership is a partial/conflicting fit.')
set_rule('Magallana gigas',[51],'M3','High','WoRMS verifies a bivalve and Crassostrea gigas synonym. Source group51 is explicitly Bivalves, but its printed CrassOweniidaea gigas is corrupt; use generic documented containment instead of claiming exact species spelling.',False)
set_rule('Carcharias taurus',[13],'M4','Medium','Source13 prints Carcharia taurus. Accepted Carcharias taurus is a strongly supported spelling interpretation, but no formal authority record for that printed misspelling was found; retain the normalization assumption.')
set_rule('Naucrates ductor',[20],'M4','Medium','Source20 prints Naucrates doctor. Authority accepts N. ductor and the same unique genus/ecology supports this spelling interpretation; the printed form has no verified synonym entry.')
set_rule('Scomberesocidae',[18],'M9','Medium','Source18 explicitly includes Scomberesox saurus saurus. Extending to the regional saury reporting family is supported, but species composition is inferred.')

# Targeted review of broad historical ranks and unrepresented habitats.
set_rule('Gadiformes',[26,27,29,30,31,32,34,42],'M9','Medium','Authority-confirmed source gadiforms occur in benthopelagic26, mesopelagic27, hake29/30, lings31, gadids32, forkbeards34 and bathydemersal42. Broad order reporting retains the complete represented set.')
set_rule('Perciformes',[17,19,20,25,26,27,31,33,34,36,39,40,41,42],'M10','Very low','Provider Perch-likes reflects a broad historical fisheries category whose boundaries differ from current orders. Approximate with compatible large/medium/small pelagic, benthopelagic, grouper, seabream, demersal, mullet and deep-water pools; composition is unknown.')
set_rule('Scaridae',[34],'M9','Medium','Historical parrotfish reporting is supported by explicit source Sparisoma cretense in34. FishBase now treats parrotfishes in Labridae/Scarinae; extend the source representative to the reporting family without moving it to small wrasse pools.')
set_rule('Squaliformes',[45],'M9','Medium','Explicit source dogfish/deep-water shark representatives Centrophorus, Dalatias, Etmopterus, Oxynotus and Squalus are45; provider Large sharks does not move them into Pelagic shark13.')
set_rule('Centroscymnus coelolepis|Somniosus rostratus|Echinorhinus brucus',[45],'M5','Medium','Unlisted deep-water bottom-associated sharks fit residual demersal shark45 by ecology and source deep-shark representatives; the misleading source small label also contains large Hexanchus/Heptranchias. This remains an ecological extension.')
set_rule('Scyris alexandrina',[17,20],'M6','Low','Authority accepts this historical name as Alectis alexandrina; provider medium-pelagic identity and source large/medium carangids leave competing17/20 candidates. Horse mackerel19 is genus-specific and is excluded.')
set_rule('Thysanoteuthis rhombus',[49,50],'M6','Low','FAO/SeaLifeBase describe epipelagic to mesopelagic oceanic squid. Benthopelagic49 versus Mesopelagic50 remain competing fits; Benthic48 is excluded. This is not exact source membership.')
set_rule('Pelates quadrilineatus|Terapontidae',[36,41],'M6','Low','Unlisted coastal terapon reporting lacks a matching named compartment. Residual medium36 versus small41 demersal/reef fish are meaningful but competing analogues; coarse provider small-pelagic classification does not establish source25 containment.')

# Ecological and taxonomic extensions for species omitted from the composition table.
set_rule('Acanthocybium solandri|Euthynnus alletteratus|Katsuwonus pelamis|Orcynopsis unicolor|Scomberomorus|Scomberomorus commerson',[17],'M5','Medium','Provider large-pelagic identity supports extension to Other large pelagic17, which lists albacore/dolphinfish/amberjack. The unlisted species/genus assignment remains an ecological assumption.')
set_rule('Auxis|Auxis rochei|Auxis thazard|Belone belone|Belonidae|Cheilopogon heterurus|Hemiramphidae|Hemiramphus|Hirundichthys rondeletii|Trachinotus|Trachinotus ovatus|Scomberomorus tritor',[20],'M5','Medium','Provider medium-pelagic identity supports extension to Other medium pelagic20, which includes bonito/jacks/barracuda. The source does not explicitly list this catch taxon.')
set_rule('Caranx|Caranx crysos',[20],'M4','Medium','Source20 lists Caranx rhonchus and related medium pelagic jacks; extension to the unlisted related catch taxon is assumed.')
set_rule('Caranx hippos',[17,20],'M6','Low','Provider large reef-associated jack and related source jacks in medium20/large17 leave competing size/ecological fits; both pools are provisional candidates.')
set_rule('Campogramma glaycos',[20,26],'M6','Low','Provider calls this medium benthopelagic, while closely related source carangids are pelagic20. Both medium-pelagic20 and benthopelagic26 are plausible; containment is uncertain.')
set_rule('Beryx|Ruvettus pretiosus|Gempylidae',[26,42],'M6','Low','Provider benthopelagic/deep-water identity overlaps Benthopelagic26 and Bathydemersal42; source has no explicit corresponding species and pool boundaries are incompletely specified.')
set_rule('Lampris guttatus',[17,27],'M6','Low','Provider large bathypelagic identity conflicts with size-based large pelagic17 versus meso/bathypelagic27 source compartments; both meaningful candidates remain.')
set_rule('Echeneidae',[17],'M5','Medium','Provider large-pelagic remoras support the broad Other large pelagic17 analogue; the family is not listed and host-associated ecology is transferred.')
set_rule('Ammodytes tobianus',[40],'M4','Medium','Source40 lists related small sandeel Gymnammodytes cicerelus; authority and provider small-demeral identity support a taxonomic/ecological extension.')
set_rule('Arbacia lixula',[61],'M3','High','Authority verifies a sea urchin; explicit Mobile benthos61 includes sea-urchin lineages and no competing sea-urchin compartment is defined.',False)
set_rule('Thalassoma pavo',[40],'M4','Medium','Provider small reef-associated wrasse and source small wrasses40 support extension; this species is not named in Table S2.')
set_rule('Pseudaphya ferreri',[40,41],'M6','Low','Provider small benthopelagic goby could resemble commercial pelagic goby Aphia40 or residual gobies41; source composition does not resolve the competing pools.')
set_rule('Cancer pagurus|Carcinus aestuarii',[59,60],'M6','Low','Unlisted commercially caught crab has a commercial59 analogue, while taxonomically related crabs are residual60. Commercial status alone does not resolve source containment.')
set_rule('Portunus pelagicus|Ixa monodi',[60],'M4','Medium','Source60 lists related non-commercial crab taxa, including Portunus and diverse brachyurans; extend to the unlisted catch species while retaining the reporting/source mismatch.')
set_rule('Palaemon elegans|Palaemon serratus|Palaemonidae',[57],'M4','Medium','Source57 lists related caridean/palaemonid shrimps; unlisted Palaemon reporting is extended to residual shrimp57 rather than Penaeus-specific56.')
set_rule('Metapenaeus monoceros|Penaeus semisulcatus|Trachysalambria curvirostris',[56],'M4','Medium','Source56 lists commercial penaeid prawns. Provider shrimp reporting and verified related penaeid identity support an extension to56; it is not exact source membership.')

results=[]
for r in catch:
    n=r['taxon'];a=authority(n);ids=set();rule=None;conf=None;reason=None;assumed=True
    if n in raw:
        ids=raw[n];rule='M1';conf='High';reason='Exact catch taxon is explicitly named in Table S2 species composition for the selected 1990s model.';assumed=False
    elif a and a['valid_AphiaID'] in valid:
        ids=valid[a['valid_AphiaID']];rule='M2';conf='High';reason='WoRMS accepted identity matches a named source taxon despite a synonym or nomenclatural spelling change.';assumed=False
    elif n in explicit_genus:
        ids=explicit_genus[n];rule='M1';conf='High';reason='Source explicitly includes this genus (spp. or an unqualified genus), supporting the exact genus catch label.';assumed=False
    elif a and a.get('genus') in explicit_genus:
        ids=explicit_genus[a['genus']];rule='M3';conf='High';reason='Verified species belongs to a genus explicitly included without species restriction in source composition.';assumed=False
    if n in overrides:ids,rule,conf,reason,assumed=overrides[n]
    if rule is None and a:
        rank=a['rank'];f=a.get('family');gen=a.get('genus')
        if a.get('class')=='Bivalvia':ids=[51];rule='M3';conf='High';reason='Verified bivalve identity unambiguously fits the documented Bivalves compartment; species listing is not needed for this generic criterion.';assumed=False
        elif a.get('class')=='Gastropoda':ids=[52];rule='M3';conf='High';reason='Verified gastropod identity unambiguously fits the documented Gastropods compartment.';assumed=False
        elif rank=='Species' and a.get('order')=='Pleuronectiformes':ids=[35];rule='M3';conf='High';reason='Verified flatfish identity unambiguously fits the generic Flatfish compartment.';assumed=False
        elif rank=='Genus' and n in genera:
            ids=genera[n];rule='M9';conf='Medium';reason='Verified genus and its listed source members support this eligible set; extending their placements to an unenumerated genus catch mixture is assumed.'
        elif rank=='Family' and (f or n) in families:
            ids=families[f or n];rule='M9';conf='Medium';reason='Authority confirms the reporting family and source representatives establish the candidate set; transferring listed members to the whole family composition is assumed.'
        elif rank=='Species' and gen in genera:
            ids=genera[gen];rule='M4';conf='Medium';reason='Verified congeneric source representatives support this pool or union; the unlisted species extension remains an assumption.'
        elif rank=='Species' and f in families:
            ids=families[f];rule='M4' if len(ids)==1 else 'M6';conf='Medium' if len(ids)==1 else 'Low';reason='Verified family contains listed source representatives. Extension is assumed; multiple source pools remain competing when the species itself is unlisted.'
    if rule is None:
        fg=r['functional_group']
        if 'flatfish' in fg:ids=[35]
        elif 'shark' in fg:ids=[13] if 'Large' in fg else [45]
        elif 'rays' in fg:ids=[46]
        elif fg=='Shrimps':ids=[56,57]
        elif fg=='Lobsters, crabs':ids=[59,60]
        elif fg=='Cephalopods':ids=[48,49,50]
        elif 'Large pelagics' in fg:ids=[17]
        elif 'Medium pelagics' in fg:ids=[20]
        elif 'Small pelagics' in fg:ids=[25]
        elif 'bathy' in fg:ids=[42]
        elif 'benthopelagic' in fg:ids=[26]
        elif 'Small' in fg and ('demersal' in fg or 'reef' in fg):ids=[40,41]
        elif 'Large' in fg and ('demersal' in fg or 'reef' in fg):ids=[31]
        elif 'demersal' in fg or 'reef' in fg:ids=[34,36]
        else:ids=[61,62]
        rule='M5' if len(ids)==1 else 'M6';conf='Medium' if len(ids)==1 else 'Low';reason='Provider functional reporting and the exact source guild representatives support an ecological extension. Constituent identity/source boundaries remain unverified; this is not documented membership.'
    ids=sorted(set(int(i) for i in ids))
    if n=='Trisopterus minutus':rule='M4';conf='Medium';reason='Authority treats Trisopterus minutus and source T. capelanus as distinct accepted species. Use an explicit congeneric extension to Gadidae32, not a verified synonym.';assumed=True
    if n=='Aristeidae':ids=sorted(set(ids))
    locs=[{'group_id':i,'group_name':G[i]['group_name'],'source_table':'S2','docx_table_one_based':G[i].get('docx_table_one_based'),'row_one_based':G[i].get('row_one_based'),'source_text':G[i]['header'],'source_path':'../../../papers/MED-2022/41598_2022_18017_MOESM2_ESM-7d26163a.docx'} for i in ids]
    stage=[i for i in ids if i in [21,22,23,24,29,30,37,38]]
    results.append({'taxon':n,'model_id':'Piroddi_2022_Mediterranean_1995','year':2019,'catch_basis':'landings','catch_tonnes_2019':r['2019'],'common_name':r['common_name'],'functional_group':r['functional_group'],'commercial_group':r['commercial_group'],'candidate_group_ids':ids,'candidate_group_names':[G[i]['group_name'] for i in ids],'membership_rule':rule,'membership_confidence':conf,'assumed_membership':assumed,'assumption_type':None if not assumed else ('broad_composition' if rule=='M10' else 'analogue' if rule=='M11' else 'taxonomic_or_ecological_extension'),'rationale':reason,'source_locators':locs,'authority_record':a,'authority_evidence_path':'worms_name_lookup.json','source_authority_evidence_path':'worms_source_name_lookup.json','provider_locator':'../../../LME_026.xlsx / Catch / Catch / exact taxon '+n+' / landings / 2019','source_membership_documented':rule in ['M1','M2','M3'],'prior_membership':None,'prior_membership_reason':'PPR / Matching was empty at capture; no adopted membership exists to retain or regrade.','allocation_owned_by_parent':True,'allocation_weights':None,'stage_pair_eligibility_note':('Source supports eligibility in the listed stage pair(s); unverified adult/recruit cutoffs affect allocation, not supported union membership.' if stage else None),'adoption_state':'proposal_only'})

for row in results:
    row['membership_evidence']=row['source_locators']
    row['reason']=row['rationale']
    row['assumptions']=[] if not row['assumed_membership'] else [row['rationale']]
    row['accepted_name']=(row['authority_record'] or {}).get('valid_name')
    row['authority_family']=(row['authority_record'] or {}).get('family')
out={'schema_version':1,'audit_id':'LME_026_Mediterranean_2019_taxonomy_review_20260930','model_id':'Piroddi_2022_Mediterranean_1995','year':2019,'basis':'landings','taxon_count':len(results),'membership_only':True,'allocation_owner':'parent regional auditor','records':results,'limitations':['No workbook mappings existed at capture; prior membership confidence is unavailable.','Source S2 is a composition table for the 1990s model, not a contemporary observed caught-mass mixture.','Source stage cutoffs are not asserted; stage proportions belong to parent review.','Numerical model parameters, routing, SPPR and calculators were neither changed nor run.','Broad reporting composition and any source spelling without authoritative synonym require the disclosed assumptions.']}
(O/'taxonomy_mapping_proposals.json').write_text(json.dumps(out,indent=2,ensure_ascii=True),encoding='utf-8')
fields=['taxon','catch_tonnes_2019','candidate_group_ids','candidate_group_names','membership_rule','membership_confidence','assumed_membership','rationale','authority_AphiaID','authority_valid_name','source_rows','stage_pair_eligibility_note','adoption_state']
with (O/'taxonomy_mapping_proposals.csv').open('w',newline='',encoding='utf-8') as fh:
    w=csv.DictWriter(fh,fieldnames=fields);w.writeheader()
    for r in results:
        v={k:r.get(k) for k in fields};v['candidate_group_ids']=';'.join(map(str,r['candidate_group_ids']));v['candidate_group_names']=';'.join(r['candidate_group_names']);v['authority_AphiaID']=(r['authority_record'] or {}).get('AphiaID');v['authority_valid_name']=(r['authority_record'] or {}).get('valid_name');v['source_rows']=';'.join(str(l['row_one_based']) for l in r['source_locators']);w.writerow(v)
(O/'source_member_authority_crosswalk.json').write_text(json.dumps(source_members,indent=2,ensure_ascii=True),encoding='utf-8')
counts=collections.Counter(r['membership_confidence'] for r in results)
validation={'taxon_count':len(results),'unique_keys':len(set(r['taxon'] for r in results)),'zero_catch_labels':sum(r['catch_tonnes_2019']==0 for r in results),'confidence_counts':dict(counts),'empty_candidate_sets':[r['taxon'] for r in results if not r['candidate_group_ids']],'invalid_ids':[r['taxon'] for r in results if any(i not in G or i>=70 for i in r['candidate_group_ids'])],'immutable_model_json_sha256':hashlib.sha256((R/'models/Piroddi_2022_Mediterranean_1995/model.json').read_bytes()).hexdigest(),'source_docx_sha256':hashlib.sha256((R/'papers/MED-2022/41598_2022_18017_MOESM2_ESM-7d26163a.docx').read_bytes()).hexdigest(),'weights_assigned':False,'calculation_performed':False}
(O/'audit_verification.json').write_text(json.dumps(validation,indent=2,ensure_ascii=True),encoding='utf-8')
print(json.dumps(validation,ensure_ascii=True))
for r in results:
    if r['membership_rule'] not in ['M1','M2','M3']:print(r['taxon']+'|'+str(r['candidate_group_ids'])+'|'+r['membership_rule']+'|'+r['membership_confidence'])
