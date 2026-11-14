from pathlib import Path
import json, hashlib, re
from pypdf import PdfReader

out = Path(__file__).parent
root = next(p for p in out.parents if (p/'README.md').exists() and (p/'Project.xlsx').exists())
source = root/'regions/LME/LME_022/papers/LME022-Mackinson-2007/sources/tech142-ead77c0e.pdf'
reader = PdfReader(source)
groups = {
 'Other gadoids (large)':'OtherLargeGadoids', 'Other gadoids (small)':'OtherSmallGadoids',
 'Miscellaneous filter feeding pelagic fish':'MiscellaneousFilterfeedingPelagicFish',
 'Epifaunal macrobenthos (mobile grazers)':'EpifaunalMacrobenthosMobileGrazers',
 'Infaunal macrobenthos':'InfaunalMacrobenthos','Sessile epifauna':'SessileEpifauna',
 'Large demersal fish':'LargeDemersalFish','Small demersal fish':'SmallDemersalFish',
 'Large piscivorous sharks':'LargePiscivorousSharks','Small sharks':'SmallSharks',
 'Baleen whales':'BaleenWhales','Starry ray + others':'StarryRayOthers',
 'Thornback & Spotted ray':'ThornbackAndSpottedRay','Skate + Cuckoo ray':'SkateCuckooRay',
 'Catfish (Wolf-fish)':'CatfishWolfFish','Turbot and brill':'Turbot',
 'Cod (adult)':'AduCod','Haddock (adult)':'AduHaddock','Whiting (adult)':'AduWhiting',
 'Saithe (adult)':'AduSaithe','Herring (adult)':'AduHerring',
 'Horse mackerel':'HorseMackerel','Blue whiting':'BlueWhiting','Norway pout':'NorwayPout',
 'Long-rough dab':'LongRoughDab','Lemon sole':'LemonSole','Lemon Sole':'LemonSole',
 'Large crabs':'LargeCrabs','Cephalopods':'SquidAndCuttlefish',
 'Nephrops':'Nephrops','Shrimp':'Shrimp','Spurdog':'Spurdog','Sandeels':'Sandeels',
 'Gurnards':'Gurnards','Monkfish':'Monkfish','Megrim':'Megrim','Halibut':'Halibut',
 'Mackerel':'Mackerel','Sprat':'Sprat','Plaice':'Plaice','Flounder':'Flounder',
 'Dab':'Dab','Sole':'Sole','Witch':'Witch','Hake':'Hake','unclassified':None,
}
crosswalk=[]
for page in range(158,163):
    raw=reader.pages[page-1].extract_text()
    (out/f'table146_page{page}.txt').write_text(raw,encoding='utf8')
    for line in raw.splitlines():
        line=line.strip()
        if not line or line.startswith(('Table 14.6.','UK FAD','14.  FISHERIES')):continue
        matches=[(line.find(g),g) for g in groups if g in line]
        if not matches:continue
        # Longest group label prevents splitting a multiword group at a species alias.
        longest=max(len(g) for _,g in matches)
        candidates=[(i,g) for i,g in matches if len(g)==longest]
        i,g=max(candidates)
        # Repeated single-species words can occur across dataset columns; last is model group.
        i=line.rfind(g)
        crosswalk.append({'printed_name':line[i+len(g):].strip() or None,'common_name':line[:i].strip() or None,'group_name':g,'canonical_group_name':groups[g],'pdf_page':page,'printed_page':page-2,'table':'14.6','raw_row':line,'role':'Historical catch-database crosswalk; not exhaustive biological membership. Adult-only entries do not override juvenile groups.'})
(out/'catch_crosswalk.json').write_text(json.dumps(crosswalk,ensure_ascii=False,indent=2),encoding='utf8')
print(len(crosswalk),'crosswalk rows')

def row(group, section, pdf, members, definition, caveat=''):
    return {'group_name':group,'section':section,'pdf_page':pdf,'printed_page':pdf-2,'members_as_printed':members,'definition':definition,'caveat':caveat}
definitions=[
row('OtherLargeGadoids','13.22',142,['Pollachius pollachius','Brosme brosme','Molva molva','Phycis blennoides'],'Composite of the named large gadoids, distinguished from dedicated cod, whiting, haddock, saithe, hake, blue whiting and Norway pout groups.','Table 14.6 additionally places blue ling here. No numerical generic size boundary is stated.'),
row('OtherSmallGadoids','13.23',142,['Rhinonemus cimbrius','Ciliata mustela','Gaidropsarus vulgaris','Gaidropsarus mediterraneus','Trisopterus minutus','Trisopterus luscus','Gadiculus argenteus'],'Named small gadoid and rockling species.','Table14.6 also routes Argentina/Argentinidae here, while section13.44 lists Argentina spp. under SmallDemersalFish. Treat this as a real conflict.'),
row('LargeDemersalFish','13.43',147,['Chimaera monstrosa','Zeus faber','Salmo trutta','Sebastes viviparous','Helicolenus dactylopterus','Coryphaenoides rupestris'],'Residual larger demersal and benthopelagic fishes represented in surveys, excluding dedicated groups.','No numerical size cutoff given. Table14.6 adds commercial catch categories including eels, salmon, seabasses, some pelagic fishes and tunas. Source examples establish actual broad ecological coverage, not a ban on all deepwater taxa.'),
row('SmallDemersalFish','13.44',148,['Zoarces viviparous','Myoxocephalus scorpius','Lycodes vahlii','Taurulus bubalis','Agonus cataphractus','Liparis liparis','Trachinus draco','Echiichthys vipera','Lumpenus lampretaeformis','Mullus surmuletus','Buglossidium luteum','Microchirus variegatus','Arnoglossus laterna','Argentina sp.'],'Residual unspecified small demersal fishes in survey samples.','No numerical size cutoff. Table14.6 conflicts for Mullus surmuletus and Argentina. Generic marine-fish rows in Table14.6 are historical catch accounting and must not erase named-group eligibility for broad current catch labels.'),
row('MiscellaneousFilterfeedingPelagicFish','13.45',148,['Alosa sp.','Engraulis encrasicolus','Sardina pilchardus','Maurolicus muelleri'],'Residual planktivorous pelagic fishes, with herring/sprat separate.','Table14.6 also includes capelin, whitebait, Baltic herring, silver smelt and broad other-pelagic labels; whitefish appears in two different groups in the table.'),
row('JuvenileSharks','13.7',138,['Squalus acanthias','other shark species'],'Young spurdog and juveniles of other sharks smaller than 40 cm.','Length measure is not specified in this paragraph. Juvenile group is not spurdog-only; no measured 2019 caught-mass fraction supplied.'),
row('Spurdog','13.8',138,['Squalus acanthias'],'Adult spurdog larger than 40 cm.','Length measure unspecified in the paragraph.'),
row('LargePiscivorousSharks','13.9',139,['Galeorhinus galeus','Lamna nasus','Aloplas vulpinus'],'Primarily tope; porbeagle and thresher are explicitly intended members although absent from 1991 IBTS observations.','Aloplas is printed misspelling. Table14.6 adds Prionace glauca. JuvenileSharks remains eligible for juveniles.'),
row('SmallSharks','13.10',139,['Scyliorhinus canicua','Mustelus spp.','Etmopterus spinax'],'Named small shark and smoothhound guild.','Scyliorhinus spelling as printed. Table14.6 adds nursehound/greater-spotted dogfish. JuvenileSharks remains eligible for juveniles.'),
row('JuvenileRays','13.11',139,['all skates'],'Skates smaller than 30 cm, across adult skate group identities.','Length measure unspecified; this does not explicitly say stingrays or electric rays.'),
row('StarryRayOthers','13.12',139,['Amblyraja radiata','unidentified rajiid skates'],'Starry ray and unidentified rajid skates.','Table14.6 specifically assigns shagreen ray and broad Raja/skate labels. Dedicated thornback/spotted and skate/cuckoo groups remain eligible for generic current broad labels.'),
row('ThornbackAndSpottedRay','13.13',139,['Raja clavata','Raja montagui'],'Adult-group union of thornback and spotted rays based on similar diets.','JuvenileRays eligible for smaller individuals.'),
row('SkateCuckooRay','13.14',140,['Dipturus batis','Leucoraja naevus'],'Common skate and cuckoo ray combined.','Historical Dipturus batis species concept predates split; Table14.6 includes longnosed skate. JuvenileRays eligible for smaller individuals.'),
row('InfaunalMacrobenthos','Table 11.6 and Table 11.8',117,['cockles','Cardium','Buccinium','Arctica islandica','Amphiura filiformis','Aphrodita aculeata','Mysella bidentata','Spisula subtruncata','Thyasira spp.','Chamelea gallina','Echinocardium cordatum','Abra prismatica','Gari fervensis','Echinocardium flavescens','Dosinia lupinus','Antalis entalis','Nicomache spp.','Caudofoveata','Nuculoma tenuis','Phaxas pellucidus','Pelecypoda'],'Predominantly infaunal bivalves and gastropods greater than 2 mm, plus source-listed infaunal taxa.','Table11.8 members are PDF118. Do not discard source-listed polychaetes/echinoderms merely because short Table11.6 definition emphasizes molluscs. Buccinium example conflicts with whelk catch crosswalk to mobile epifauna.'),
row('EpifaunalMacrobenthosMobileGrazers','Table 11.6 and Table 14.6',117,['brittle stars','sea urchins','small crabs','gastropods','scallops'],'Mobile macrobenthos living freely on the sediment surface.','Table14.6 assigns queen/king/great Atlantic scallops, periwinkles and whelks. Name mobile grazers is narrower than actual source definition, which includes predatory/scavenging taxa.'),
row('SmallMobileEpifaunaSwarmingCrustaceans','Table 11.6',117,['crustaceans','molluscs','polychaetes','mysids','gammarids','amphipods'],'Small interface fauna, including crustaceans swarming above the bottom.','Not an indiscriminate all-crustacean pool; dedicated shrimp, Nephrops and large crabs remain separate.'),
row('SmallInfaunaPolychaetes','Table 11.6',117,['Sabella','Nereis','Sipunculus','Turbellaria','Arenicola','Sagitta','small sediment crustaceans'],'Mainly sediment-dwelling polychaetes and other small infauna.','Source genera as printed; some are taxonomically or ecologically unusual and are not corrections.'),
row('SessileEpifauna','Table 11.6 and Table 14.6',117,['anemones','sponges','corals','tunicates','gorgonians','hydroids','anthozoans','pelecypods','Balanus','bryozoans','mussels','crinoids','ascidians','oysters'],'Attached or sessile suspension/filter-feeding epifauna.','Table14.6 specifically assigns blue mussel, European flat oyster, Pacific cupped oyster. Table11.8 also has named worms; use actual members rather than taxonomy alone.'),
row('LargeCrabs','11.7',129,['Cancer pagurus','Maja brachydactyla','Necora puber','Liocarcinus holsatus','Hyas coarctatus','Homarus gammarus','squat lobsters'],'Modest/large brachyuran crabs recognizable in fish diets and fisheries plus other large decapods, including European lobster and squat lobsters.','This is not exclusively Brachyura. Small epifaunal crabs can instead belong to mobile macrobenthos.'),
row('Nephrops','11.5',122,['Nephrops norvegicus'],'Norway lobster inhabiting burrows in muddy sediment.'),
row('Shrimp','11.6',124,['Pandalus','Crangon','Eualus pusiolus'],'Prawns and shrimps, parameterized mainly using Pandalus borealis and Crangon.','Diet based entirely on Pandalus borealis; this does not exclude other listed shrimps. Table14.6 includes Aesop shrimp, English prawns and Pandalus spp.'),
]
(out/'group_definitions.json').write_text(json.dumps(definitions,ensure_ascii=False,indent=2),encoding='utf8')
print(len(definitions),'group definitions')

notes={
'source_id':'MD2007','source_url':'https://www.cefas.co.uk/publications/techrep/tech142.pdf','source_path':source.relative_to(root).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'retrieved_online':'2026-11-14','local_bytes_read':'2026-11-14',
'source_identity':'Mackinson and Daskalov 2007, Cefas Technical Report142; publication copyright2008; model1991 and1973 predecessor. PDF page=printed page+2 in relevant sections.',
'inheritance_evidence':'ICES WGSAM2015 Table2.1 printed106 states original technical report Mackinson and Daskalov2007 supplies parameter ranges; §2.1 and subsequent revisions update existing North Sea model. Exact Rpath port preserves most group structure but is not identical to accepted 2015 native configuration.',
'group_changes':['Original68 groups become69 when seabirds split into SurfaceFeedingSeabirds and DivingSeabirds.','Original Turbot and brill becomes Turbot in2015 Table2.1 and canonical port. Brill inheritance therefore requires explicit assumption, not unquestioned exact-source identity.','Table14.6 calls catches Cephalopods while ecological group is Squid & cuttlefish. Octopus rows have inherited catch accounting support but not a literal focal2015 group-name match.','Predecessor weights/biomass/catches must not replace focal canonical Rpath fields.'],
'conflicts':[{'taxon':'Mullus surmuletus','biological_definition':'SmallDemersalFish §13.44 PDF148','catch_crosswalk':'LargeDemersalFish Table14.6 PDF161','recommendation':'Record contradiction and lower membership confidence or explicitly select one source role.'},{'taxon':'Argentina / Argentina silus / Argentinidae','biological_definition':'SmallDemersalFish §13.44 PDF148','catch_crosswalk':'OtherSmallGadoids Table14.6 PDF158–159, with Silver Smelt to MiscellaneousFilterfeedingPelagicFish PDF162','recommendation':'Do not claim unique High membership. Record which source role governs proposed placement.'},{'taxon':'Coregonus / European whitefish','catch_crosswalk':'Both MiscellaneousFilterfeedingPelagicFish and OtherLargeGadoids Table14.6 PDF159','recommendation':'Ambiguous historical row; use justified ecology with downgraded confidence.'},{'taxon':'Buccinum / Buccinidae','biological_definition':'Buccinium example in InfaunalMacrobenthos Table11.6 PDF117','catch_crosswalk':'Whelks/Buccinidae to EpifaunalMacrobenthos Table14.6 PDF161','recommendation':'Recognize mobile whelk ecology and preserve conflict.'},{'taxon':'Cetorhinus maximus','catch_crosswalk':'BaleenWhales Table14.6 PDF158','recommendation':'Historical explicit feeding analogue; never call it whale taxonomic membership. Very low M11 is defensible.'}],
'limitations':['PDF text crosswalk rows preserve original misspellings; canonical-name crosswalk is analyst normalization.','Broad historical nei rows are accounting shortcuts and not exhaustive sets for present reporting labels.','Unclassified Esox/Rutilus/Sander rows document no predecessor placement; they do not forbid meaningful explicit low-confidence analogy.','Pypdf layout extraction excluded rotated table text; source_pages.json was regenerated with ordinary extraction; table146_page158 image visually inspected.']}
(out/'source_findings.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf8')
