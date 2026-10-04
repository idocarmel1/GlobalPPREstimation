from pathlib import Path
import csv, hashlib, json, math
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / 'source' / 'resolved_native'
universe = json.loads((OUT / 'catch_universe.json').read_text(encoding='utf-8'))
identity = json.loads((SOURCE / 'GROUP_IDENTITY.json').read_text(encoding='utf-8'))
groups = {int(x['seq']): x for x in identity}
with (SOURCE / 'GROUP_CATCH_BIOMASS.csv').open(encoding='utf-8-sig',newline='') as f:
    proxy = {int(r['seq']): r for r in csv.DictReader(f)}
for r in proxy.values():
    for k in list(r):
        if k.endswith('t_km2_y') or k=='biomass_t_km2': r[k]=float(r[k])
tax = json.loads((ROOT / 'regions/LME_013/validation_reports/13_1_Chilean_Patagonia_(1980)/taxonomy_crosswalk.json').read_text(encoding='utf-8-sig'))
fissurella = json.loads((ROOT / 'regions/LME_013/validation_reports/13_1_Chilean_Patagonia_(1980)/taxonomy_fissurella_spelling.json').read_text(encoding='utf-8-sig'))
tax['Fissurella cumingi'] = [fissurella['current_record']]
search_ledger = json.loads((OUT/'search_records.json').read_text(encoding='utf-8'))
search_ids = defaultdict(list)
for record in search_ledger['records']:
    for label in record['taxa']: search_ids[label].append(record['id'])
source_aliases = {
 'Doryteuthis gahi': {'reported_source_name':'Loligo gahi','accepted_name':'Doryteuthis gahi','relationship':'accepted synonym','authority':'OBIS / MolluscaBase via WoRMS','url':'https://obis.org/taxon/341880'},
 'Merluccius peruanus': {'reported_source_name':'Merluccius gayi peruanus','accepted_name':'Merluccius peruanus','relationship':'accepted synonym; other modern hake species remain distinct','authority':'WoRMS','url':'https://www.marinespecies.org/aphia.php?p=taxlist&pid=125473&rComp=%3E%3D&tRank=220'},
 'Odontesthes regia': {'reported_source_name':'Odonthestes regia','accepted_name':'Odontesthes regia','relationship':'source orthographic correction, catch label preserved','authority':'retained WoRMS / source identity audit'},
 'Labrisomus philippii': {'reported_source_name':'Labrisomus philippi','accepted_name':'Labrisomus philippii','relationship':'source orthographic correction, catch label preserved','authority':'retained WoRMS / source identity audit'},
 'Fissurella cumingi': {'reported_catch_name':'Fissurella cumingi','accepted_name':'Fissurella cumingii','relationship':'reported catch spelling retained; accepted-name authority linked without changing membership grade','authority':'MolluscaBase via WoRMS','aphia_id':570478}
}

M = {
'M1': 'Explicit inclusion of the taxon in the source model',
'M2': 'Source membership connected through a verified synonym or documented spelling correction',
'M3': 'Unambiguous fit to a documented taxonomic or ecological group',
'M4': 'Supported extension from the source’s listed representative taxa',
'M5': 'Supported ecological assignment requiring a group-boundary interpretation',
'M6': 'Partial or competing ecological fit',
'M9': 'Assumed eligible group set supported by taxonomy and ecology',
'M10': 'Approximation of a broad reporting category across plausible model pools',
'M11': 'Closest represented ecological or taxonomic analogue',
'M8': 'No meaningful assignment established'
}
W = {'W1':'One group; no allocation split required',
     'W4':'Allocation proportional to native source-model landings',
     'W9':'Complete source-model biomass fallback after unusable landings',
     'W8':'No usable allocation established'}
rank = {'High':4,'Medium':3,'Low':2,'Very low':1,'Unresolved':0}
spec = {}
def add(names, ids, rule, level, reason, refs=None, vl=None):
    for t in names.split('|'):
        assert t not in spec,t
        spec[t]={'ids':ids,'membership_rule':rule,'membership_confidence':level,
                 'membership_reason':reason,'extra_sources':refs or [],'very_low_group':vl}

add('Dosidicus gigas',[12],'M1','High','Jumbo squid explicitly represents Dosidicus gigas in the inherited source definition; other cephalopods exclude this named compartment.')
add('Engraulis ringens',[10],'M1','High','Anchovy explicitly represents Engraulis ringens; anchovy eggs are a separate nonfeeding pool and are excluded from landed fish.')
add('Sardinops sagax',[9],'M1','High','Sardine explicitly represents Sardinops sagax. The source’s landings-version conflict affects a composition proxy and model applicability, not species identity.')
add('Trachurus murphyi',[15],'M1','High','Horse mackerel explicitly represents Trachurus murphyi; the dedicated group takes precedence over generic pelagic pools.')
add('Scomber japonicus',[16],'M1','High','The source explicitly names Scomber japonicus for Chub mackerel; the dedicated group takes precedence over other pelagic fishes.')
add('Sarda chiliensis|Coryphaena hippurus|Thunnus albacares',[17],'M1','High','The inherited definition explicitly lists this species among Other large pelagic fish; the list is not treated as exhaustive.')
add('Anchoa nasus',[14],'M1','High','The inherited definition explicitly lists Anchoa nasus in Other small pelagic fish. Named anchovy and sardine pools are different taxa.')
add('Mugil cephalus|Paralabrax humeralis',[26],'M1','High','The inherited definition explicitly lists this species in Medium demersal fish. Its provider habitat tag does not override explicit source placement.')
add('Stromateus stellatus',[24],'M1','High','The inherited Butter fishes definition explicitly includes Stromateus stellatus; this takes precedence over a broad benthopelagic provider category.')
add('Prionotus stephanophrys',[28],'M1','High','Sea robin explicitly represents Prionotus stephanophrys.')
add('Chrysaora plocamia',[7],'M1','High','The focal model adds Chrysaora plocamia as a separate species group; small gelatinous zooplankton is explicitly a different pool. This zero-landings label was retained and audited.')
add('Doryteuthis gahi',[13],'M2','High','Other cephalopods explicitly lists historical Loligo gahi; OBIS and retained MolluscaBase/WoRMS authority identify it as Doryteuthis gahi. Jumbo squid is excluded.',['OBIS_Loligo'])
add('Odontesthes regia',[22],'M2','High','The inherited source prints Odonthestes regia. The documented orthographic correction to the accepted Odontesthes regia identifies the same species in Small demersal fish; source placement takes precedence over its small-pelagic provider tag.')
add('Labrisomus philippii',[22],'M2','High','The inherited source prints Labrisomus philippi; the documented orthographic correction to accepted Labrisomus philippii preserves its explicit Small demersal fish placement.')
add('Merluccius peruanus',[18,19,20],'M2','High','The source’s Merluccius gayi peruanus is accepted as Merluccius peruanus by WoRMS. The union of all three hake size groups is eligible; printed boundary gaps and the unspecified length convention affect allocation, not this species identity.',['WoRMS_hake','IMARPE_hake2019'])

add('Enteroctopus megalocyathus',[13],'M4','Medium','A regional octopus extends the source’s listed Octopus representative in Other cephalopods. This is a supported taxonomic extension, not an explicit source member.')
add('Teuthida',[12,13],'M9','Medium','The reporting label explicitly means squids, spanning named Jumbo squid and squid members of Other cephalopods. The latter pool also contains octopus: its whole-pool landings are an assumed squid-composition proxy, not observed squid-only mass.')
add('Katsuwonus pelamis|Thunnus obesus|Thunnus alalunga|Thunnus maccoyii|Thunnus orientalis|Auxis|Auxis rochei|Euthynnus lineatus|Acanthocybium solandri|Scomberomorus sierra|Allothunnus fallai',[17],'M4','Medium','This tuna, bonito or mackerel lineage extends the source’s named Sarda/Thunnus representatives in Other large pelagic fish. Scomber japonicus has a species-specific compartment; it does not contain these different taxa. No source numerical size cutoff is assumed.')
add('Coryphaena',[17],'M4','Medium','The dolphinfish genus is extended from source-listed Coryphaena hippurus to the regional reported genus. The generic large-pelagic pool supports the extension; unidentified congener composition is assumed.')
add('Xiphias gladius|Kajikia audax|Istiophoridae|Istiophorus platypterus|Istiompax indica|Tetrapturus|Tetrapturus angustirostris',[17],'M5','Medium','Large mobile billfishes fit Other large pelagic fish on documented taxonomy and the provider’s pelagic fisheries category. The source does not enumerate billfishes, so this remains an ecological extension; offshore distribution alone does not create a separate membership mismatch.')
add('Brama australis|Brama brama|Lampris guttatus|Lepidocybium flavobrunneum|Ruvettus pretiosus|Elagatis bipinnulata|Caranx|Caranx lugubris|Seriola|Seriola lalandi|Seriola rivoliana',[17],'M5','Medium','A mobile pelagic or benthopelagic fish is assigned to the source’s generic Other large pelagic fish. The source supplies no numerical maximum-length or depth boundary; its listed bonito/dolphinfish/tuna are representatives. The extension and regional coefficient transfer remain assumptions, with no claim of an explicit species member.')
add('Fistularia corneta|Thyrsites atun|Trichiurus lepturus|Trichiuridae',[17],'M6','Low','A coastal benthopelagic predator has both water-column and near-bottom affinities. Other large pelagic fish is the closest broad predator pool; Medium demersal fish is a competing interpretation with a smaller, incompletely bounded source guild. Selecting the pelagic pool is a disclosed ecological judgment.')
add('Selene peruviana|Sprattus fuegensis|Strangomera bentincki|Ethmidium maculatum|Decapterus macrosoma|Cetengraulis mysticetus|Emmelichthys nitidus',[14],'M5','Medium','A schooling smaller pelagic fish extends Other small pelagic fish from its named Anchoa representative. Dedicated Anchovy/Sardine/Horse mackerel/Chub mackerel pools are species-specific and are excluded. Provider maximum-size categories are ecological context, not observed caught-size proportions.')
add('Normanichthys crockeri',[14],'M6','Low','The coastal schooling mote has a meaningful small-pelagic affinity, while the provider classifies it as small demersal. Other small pelagic fish is selected over Small demersal fish with that conflict retained. Predecessor parameter analogues described as pelagic goby do not establish explicit source membership.')
add('Seriolella|Seriolella violacea|Seriolella punctata',[24],'M4','Medium','The reported butterfish/warehou lineage is extended to Butter fishes from the listed stromateoid representatives Stromateus/Peprilus. Modern Centrolophidae identity does not establish explicit source membership; the extension is assumed.')
add('Seriolella caerulea',[24],'M6','Low','The warehou lineage supplies a supported Butter fishes connection, but its bathypelagic provider category conflicts with the source pool’s pelagic-planktivorous aggregation. This remains a partial ecological fit.')
add('Paralabrax|Epinephelus',[26],'M4','Medium','The bass/grouper taxon extends Medium demersal fish from its listed Paralabrax and Hemanthias representatives; unidentified congeners and source size limits remain assumptions.')
add('Caulolatilus|Caulolatilus princeps|Malacanthidae|Isacia conceptionis|Chirodactylus variegatus|Prolatilus jugularis|Pinguipes chilensis|Polydactylus approximans|Graus nigra|Aplodactylus punctatus|Nemadactylus|Salilota australis|Monacanthidae',[26],'M5','Medium','A medium coastal demersal, reef or benthopelagic fish fits the generic Medium demersal fish guild using its reporting ecology and taxonomy. Inclusion extends an incompletely enumerated source pool; the source supplies no numerical size boundary.')
add('Diplectrum pacificum|Diapterus peruvianus|Parapsettus panamensis|Heteropriacanthus cruentatus|Scorpaena histrio|Hippocampus',[22],'M5','Medium','A smaller reef/near-bottom fish fits Small demersal fish by ecological extension from the source’s blenny/coastal representatives. No numerical size threshold or exhaustive species list is supplied; for higher-rank labels regional caught constituents are assumed.')
add('Cynoscion analis|Cilus gilberti|Paralonchurus peruanus',[27],'M5','Medium','WoRMS and regional IMARPE records place the taxon among sciaenids, compatible with Medium sciaenids. The source does not name these species or give numerical size bounds. Source-listed Ctenosciaena in Small demersal fish is excluded as a different species.',['IMARPE_sciaenids'])
add('Larimus pacificus|Stellifer minor',[22,27],'M6','Low','Regional IMARPE coastal catches include these small sciaenids, so Small demersal fish and Medium sciaenids remain competing source guilds without a numerical boundary. Both are retained as an explicitly assumed ecological mixture; source pool landings do not observe this species’s actual split.',['IMARPE_sciaenids'])
add('Genypterus maculatus|Genypterus',[25],'M5','Medium','Regional IMARPE commercial nomenclature identifies Genypterus maculatus as congrio/conger in the model-period fishery. This supports interpretation of the unnamed Conger pool, with extension to the reported genus assumed. The source itself does not enumerate a species.',['IMARPE_congrio'])
add('Genypterus blacodes',[25],'M6','Low','The cusk-eel shares the regional congrio interpretation of Conger, but its southern bathydemersal ecology and the source’s unnamed species composition leave a material partial fit.',['IMARPE_congrio'])
add('Ophichthus',[25],'M11','Very low','Snake eels provide the closest eel-bodied, bottom-associated piscivorous analogue to the source’s unnamed Conger pool. IMARPE distinguishes anguila Ophichthus from congrio Genypterus: this is not a verified conger synonym or explicit membership.',['IMARPE_congrio'],'eel_analogue')
add('Beryx splendens|Coelorinchus chilensis|Macrouridae|Sebastidae',[26],'M6','Low','The demersal/benthopelagic reporting ecology supports Medium demersal fish, but deeper-water or broad-family constituents are only partially represented by its listed coastal species. Source size/depth bounds are not complete; this is a partial guild fit.')
add('Merluccius gayi|Merluccius australis|Macruronus magellanicus|Micromesistius australis',[18,19,20],'M11','Very low','The species is not the source’s Peruvian hake: modern authority keeps it distinct. The three Peruvian hake groups provide a meaningful cod-like/hake demersal-predator analogue, but species identity, southern ecology and size thresholds differ. All stages are retained; source stage landings are a transferred proxy, not these species’ size composition.',['WoRMS_hake'],'hake_analogue')
add('Dissostichus eleginoides|Hoplostethus atlanticus',[26],'M11','Very low','A deep-water, colder-water fish lacks a corresponding source population. Medium demersal fish is the closest represented bottom-associated fish analogue, with depth/size and taxonomic mismatch explicit. Source mesopelagic examples are small forage taxa and do not establish membership of this large deep-water assemblage.',['FishBase_roughy'],'deep_analogue')
add('Galaxias maculatus',[22],'M11','Very low','The amphidromous galaxiid has marine larvae and freshwater adult habitat. Small demersal fish is a weak coastal small-fish analogue; the source has no diadromous galaxiid compartment. The provider’s large-reef tag is set aside as inconsistent with authoritative life-history evidence.',['NIWA_galaxias'],'diadromous_analogue')

flat='Pleuronectiformes|Cynoglossidae|Paralichthys|Paralichthys microps|Bothidae|Hippoglossina macrops|Paralichthyidae'
add(flat,[21],'M3','High','Taxonomy and the provider’s flatfish category fit the source’s taxonomic Flatfish pool, with named Paralichthys/Hippoglossina examples and no competing flatfish group. The list is not assumed exhaustive.')
add('Prionace glauca|Sphyrna zygaena|Isurus oxyrinchus|Isurus|Alopias vulpinus|Alopias|Lamna nasus|Carcharhinus falciformis|Carcharhinus longimanus',[30],'M5','Medium','Pelagic/mobile sharks fit the source Chondrichthyans pool after excluding the separate Benthic elasmobranchs guild. The source has no species list, so taxonomic and habitat interpretation is assumed; mere source-group name is not treated as explicit membership.',['FAO_sharks'])
add('Mustelus|Mustelus whitneyi|Mustelus mento',[23],'M5','Medium','FAO regional evidence and taxonomy support a bottom-associated smoothhound connection to Benthic elasmobranchs. The source does not list species and the generic genus catch remains an assumed regional extension.',['FAO_sharks'])
add('Galeorhinus galeus|Squalus acanthias|Deania calceus|Hexanchus griseus',[23,30],'M6','Low','Demersal/benthopelagic sharks can occupy bottom and water-column predator habitats. Both Benthic elasmobranchs and Chondrichthyans are retained because the source does not provide an exhaustive partition; model landings assume their regional mixture.',['FAO_sharks'])
add('Zearaja chilensis|Dipturus trachyderma|Rajidae|Rajiformes|Pseudobatos planiceps|Rhinoptera steindachneri',[23],'M5','Medium','Bottom-associated skate/ray/guitarfish ecology supports Benthic elasmobranchs. The source does not enumerate species; family/order reporting meaning and bottom association remain interpreted rather than explicit species membership.',['FAO_sharks'])
add('Batoidea|Elasmobranchii',[23,30],'M10','Very low','The source separately represents benthic elasmobranchs and other chondrichthyans. Both pools are plausible for the reported ray/shark lineage, but the broad label can include pelagic filter-feeding rays absent from the source’s apex-predatory correspondence. The two-pool approximation does not let a supported benthic component conceal that unsupported constituent.',['FAO_sharks'],'cartilaginous_broad')
add('Myliobatidae',[23,30],'M10','Very low','The provider’s historical eagle/manta-ray category crosses benthic eagle rays and pelagic mobulids. Both source cartilaginous pools are retained; the modern family name alone does not reconstruct historical reporting composition. The source has no pelagic filter-feeding ray compartment.',['FAO_sharks'],'cartilaginous_broad')
add('Chondrichthyes',[23,30],'M10','Very low','The reported class includes sharks, rays and chimaeras. Both cartilaginous pools are plausible, but Benthic elasmobranchs excludes true chimaeras taxonomically and the other pool is not a documented chimaera population. This broad approximation retains that unrepresented component.',['FAO_sharks'],'cartilaginous_broad')
add('Callorhinchus callorynchus',[23],'M11','Very low','The chimaera is not an elasmobranch. Benthic elasmobranchs supplies the closest bottom-feeding cartilaginous analogue; Chondrichthyans has a poorer apex-predator ecological correspondence. The taxonomic mismatch is explicit.',['FAO_sharks'],'chimaera_analogue')
add('Mobula birostris',[30],'M11','Very low','The oceanic manta is a pelagic cartilaginous filter feeder. Chondrichthyans is the closest water-column cartilaginous pool, but its apex-predatory aggregation and the absence of a filter-feeding ray population make this a weak analogue. Benthic elasmobranchs has a stronger habitat mismatch.',['FAO_sharks'],'manta_analogue')

add('Scombridae|Scombroidei',[16,17],'M9','Medium','Taxonomy/reporting meaning spans the source’s Scomber-specific Chub mackerel and Other large pelagic fish with tuna/bonito representatives. Historical Scombroidei includes billfish-like members as well. Horse mackerel is Carangidae, not this lineage, and is excluded.')
add('Clupeidae',[9,14],'M9','Medium','The herring/sardine reporting lineage includes named Sardinops and other smaller clupeid pelagics. Engraulis belongs to Engraulidae and is excluded; absence of a Sardinops share is a weighting uncertainty, not absence of an eligible set.')
add('Clupeiformes',[9,10,14],'M9','Medium','The herring/shad/anchovy reporting order spans named Sardine, Anchovy and other small clupeiform pelagics. All are retained, including the named pools; relative composition is unobserved.')
add('Carangidae',[14,15,17,24],'M9','Medium','Regional carangids span smaller pelagics, named Trachurus, larger jacks and source-listed Trachinotus in Butter fishes. The full supported set includes named and residual groups. Species/size composition is assumed; Scomber is not Carangidae.')
add('Sciaenidae',[22,27],'M9','Medium','The source explicitly puts Ctenosciaena in Small demersal fish and separately has Medium sciaenids. Both are eligible for the family catch; no exclusion is inferred from separately reported named croakers.',['IMARPE_sciaenids'])
add('Serranidae|Haemulidae',[22,26],'M9','Medium','Regional smaller and medium demersal/reef taxa support Small demersal fish and Medium demersal fish. Exact source size boundaries and regional family composition are not supplied, so the two-pool set is an explicit interpretation.')
add('Scorpaeniformes',[22,26,28],'M10','Very low','Historical scorpionfish/flathead reporting can span small and medium demersal guilds and source-named Prionotus sea robin. Modern order reshuffling cannot reconstruct the recorded category’s constituents. All three plausible pools are retained.','', 'fish_broad')
add('Gadiformes',[18,19,20,26],'M10','Very low','The cod-like reporting order can include the named hake stages and other demersal cod-like fishes. Medium demersal fish is a provisional remainder analogue; Southern/deep constituents have no explicit population. Source hake stages are retained even at zero landings.','', 'fish_broad')
add('Perciformes',[14,15,16,17,22,24,26,27,28],'M10','Very low','A historically broad perch-like catch label can cross carangids/scombrids, small and medium demersals, butterfishes, sciaenids and modern perciform sea robins. Current taxonomy and provider size tags do not establish its historical catch composition. Named and residual plausible pools are retained.','', 'fish_broad')
bony=[9,10,11,14,15,16,17,18,19,20,21,22,24,25,26,27,28,29]
fish=bony+[23,30]
add('Actinopterygii|Marine finfishes not identified',bony,'M10','Very low','The broad ray-finned/finfish label can cross named and residual pelagic, mesopelagic and demersal bony-fish compartments. A demersal provider tag is not an exhaustive constituent boundary. Cartilaginous fish, cephalopods and nonfish pools are excluded. Source proxies approximate unknown regional composition.','', 'fish_broad')
add('Marine fishes not identified',fish,'M10','Very low','The generic marine-fish reporting label supplies no constituent species restriction. All named/residual bony-fish and cartilaginous fish pools are retained, including genuine zero source catches; its demersal functional tag is not exhaustive. Cephalopods and nonfish pools are excluded.','', 'fish_broad')
add('Marine groundfishes not identified',[18,19,20,21,22,23,25,26,27,28,29],'M10','Very low','Groundfish reporting supports demersal hake, flatfish, smaller/medium demersals, benthic elasmobranchs, conger, sciaenids, sea robin and catfish. The label does not reveal species or deep-water composition. Explicitly water-column pelagic pools and cephalopods are excluded.','', 'fish_broad')
add('Marine pelagic fishes not identified',[9,10,11,14,15,16,17,24,30],'M10','Very low','The generic pelagic-fish label can span named forage/mackerels, smaller/larger residual pelagics, mesopelagic fishes, butterfishes and mobile chondrichthyans. The label does not identify depth or taxonomic composition. Cephalopods and explicitly benthic guilds are excluded.','', 'fish_broad')

add('Mollusca',[8,12,13],'M9','Medium','The provider explicitly describes clams, sea snails, squids and octopuses: compatible caught macro-molluscs span Macrobenthos, Jumbo squid and Other cephalopods. The functional demersal tag does not exclude cephalopods. Microscopic/planktonic life stages are not inferred as commercially recorded catch members.',['IMARPE_inverts'])
add('Decapoda|Malacostraca|Miscellaneous marine crustaceans',[5,8],'M10','Very low','The broad crustacean reporting categories may include benthic crabs/shrimps and pelagic krill/squat-lobster components. Macrobenthos and Macrozooplankton are retained. The latter’s 2–20 mm boundary does not fully represent larger pelagic crustaceans; the proxy is a disclosed broad approximation.',['IMARPE_munida'],'crustacean_broad')
add('Galatheidae|Grimothea monodon',[5,8],'M11','Very low','The source lacks a distinct squat-lobster population. Regional IMARPE surveys document substantial pelagic Grimothea/Pleuroncodes, while other life/history/fishery components are benthic. Macrozooplankton and Macrobenthos are meaningful analogues, but the macrozooplankton 2–20 mm boundary mismatches larger caught animals and historical Galatheidae has changed scope.',['IMARPE_munida'],'squatlobster_analogue')

# Every other recorded non-cephalopod invertebrate was individually checked against its
# authority rank, provider ecology and the fresh source's macro-benthic pool.
remaining=[r for r in universe['taxa'] if r['taxon'] not in spec]
for r in remaining:
    t=r['taxon']; a=(tax.get(t) or [{}])[0]
    assert a.get('phylum') in ['Mollusca','Arthropoda','Echinodermata','Chordata'],t
    assert r['functional_group'] in ['Other demersal invertebrates','Lobsters, crabs','Shrimps'],(t,r['functional_group'])
    level='High' if a.get('rank')=='Species' else 'Medium'
    rule='M3' if level=='High' else 'M9'
    desc=('The named caught macroinvertebrate has a documented benthic provider category and authoritative taxonomic identity; it fits the source Macrobenthos concept with no competing named source population. The source does not enumerate species, so no explicit species-list inclusion is claimed.' if level=='High' else 'The provider’s coherent commercial shellfish/benthic-invertebrate meaning and authoritative rank support the Macrobenthos pool; regional constituent species and harvested life stages remain interpreted. No named cephalopod pool fits this more restricted label.')
    add(t,[8],rule,level,desc,['IMARPE_inverts'])

sources=[
 {'id':'CompositionSearch','title':'Primary composition searches, decisions and bounded access failures','target':'search_records.json','supports':'Actual final query strings and provider outputs; applicable observed composition not established, so modeled proxy allocations remain explicitly assumed.'},
 {'id':'Focal','title':'Chiaverano et al. (2018), Northern Humboldt ecological network','target':'../../../papers/HUM-2018/1-s2.0-S0079661117303312-main.pdf#page=3','supports':'Focal inheritance, domain/period, added jellyfish/turtles/eggs, source-version qualifications; DOI 10.1016/j.pocean.2018.04.009.'},
 {'id':'Native','title':'Original revised/final supplement, Table A: resolved stock parameters and fleet removals','target':'../../../papers/HUM-2018/Supplementary material revised and final.xls','supports':'Exact stock IDs/names, stored biomass C and fleet landings I/J and discards K/L; all zeros are explicit. Native supplement landings are used as composition proxies.'},
 {'id':'FreshTaxonomy','title':'Independent fresh group definitions and evidence scopes','target':'../source/resolved_native/GROUP_IDENTITY.json','supports':'Exact stock definitions; inherited enumerated examples distinguished from parameter analogues and unsupported exhaustive lists.'},
 {'id':'FreshProxy','title':'Independent source catch and biomass vector with exact cell locators','target':'../source/resolved_native/GROUP_CATCH_BIOMASS.csv','supports':'Every candidate raw value and genuine zero, source basis and fallback inputs.'},
 {'id':'Tam2008','title':'Tam et al. (2008), inherited Northern Humboldt model methods, pp.353–354','target':'https://epic.awi.de/id/eprint/22464/1/Tam2008a.pdf','supports':'Explicit species examples, three Peruvian hake intervals, plankton size classes; parameter analogues are not source-membership observations.'},
 {'id':'Regional','title':'LME 013 regional Catch, Classic PPR and NPP tables, read-only snapshot','target':'../../../LME_013.xlsx','supports':'All exact reporting labels and functional/common names, all bases/years, saved independent classic TL/SPPR and NPP. Active selection was not changed.'},
 {'id':'SAU_methods','title':'Sea Around Us, catch reconstruction and allocation methods','target':'https://api.seaaroundus.org/catch-reconstruction-and-allocation-methods/','supports':'Commercial/functional reporting groups differ from taxa and maximum size is not caught-size mass composition; page opened 2026-10-03.'},
 {'id':'WoRMS','title':'WoRMS/FishBase/MolluscaBase authority records retained from 30 September 2026','target':'taxonomy_authority_records.json','supports':'Taxonomic identity, accepted name, family/order, marine/freshwater status and authority IDs for all available exact catch names. These records are reused taxonomy evidence, not prior mapping assignments.'},
 {'id':'WoRMS_hake','title':'WoRMS Merlucciidae taxonomic list and accepted Peruvian hake identity','target':'https://www.marinespecies.org/aphia.php?p=taxlist&pid=125473&rComp=%3E%3D&tRank=220','supports':'Merluccius gayi peruanus accepted as M. peruanus; M. gayi and M. australis retained distinct. Search result read; full endpoint fetch failed 2026-10-03.'},
 {'id':'OBIS_Loligo','title':'OBIS, Loligo gahi taxon entry','target':'https://obis.org/taxon/341880','supports':'Accepted Doryteuthis gahi identity for source Loligo gahi; full entry opened 2026-10-03.'},
 {'id':'IMARPE_hake2019','title':'IMARPE 2019 Scientific and Technical Yearbook, p.38, hake fishery size structure','target':'https://repositorio.imarpe.gob.pe/server/api/core/bitstreams/efeadc99-888b-41fb-aba1-5e0396136e06/content','supports':'Primary indexed passage describes industrial catch lengths, not matching all-region caught-mass bins for exact model intervals. Full PDF retrieval failed; no fractions adopted.'},
 {'id':'IMARPE_sciaenids','title':'IMARPE 2016 Vol.43 No.2, p.158, coastal fishery species and caught lengths','target':'https://repositorio.imarpe.gob.pe/server/api/core/bitstreams/9b6206d2-e2e7-4f2b-b69f-dcdaf3658eae/content','supports':'Regional small sciaenids and historical family nomenclature; primary indexed table only. A single coastal fishery does not supply whole-LME residual-label proportions.'},
 {'id':'IMARPE_congrio','title':'IMARPE 1995–1996 commercial species list and later demersal records','target':'https://repositorio.imarpe.gob.pe/bitstreams/0bc833fc-9c71-4826-8b79-cc8d421c8fff/download','supports':'Primary indexed commercial list names Congrio = Genypterus maculatus; later records distinguish Ophichthus anguila. Supports generic-pool interpretation, not focal explicit membership.'},
 {'id':'IMARPE_munida','title':'IMARPE 2025 pelagic survey, p.34, Grimothea monodon in midwater catch','target':'https://www.imarpe.gob.pe/wp-content/uploads/2025/09/20250424_1200-Informe_Crucero_2502_04_de_Evaluacion_Hidroacustica_de_Anchoveta_y_otros_Recursos_Pelagicos-Pesca_Artesanal-1.pdf','supports':'Primary indexed pelagic occurrence and meaningful squat-lobster analogue; survey catches do not determine broad regional commercial residual composition.'},
 {'id':'IMARPE_inverts','title':'IMARPE public fishery activity reporting service and 2013 marine invertebrate landings','target':'https://www.gob.pe/12280','supports':'Regional fisheries report scallop/snail/octopus/squid/crab resources separately; national totals do not establish catch composition of unidentified SAU labels.'},
 {'id':'FAO_sharks','title':'FAO shark habitat/species catalogue and Galeorhinus fishery review','target':'https://www.fao.org/4/X2098E/X2098E11.htm','supports':'Mixed demersal/pelagic Galeorhinus ecology; primary FAO catalogue and regional records inform elasmobranch guilds. No compatible regional observed habitat-pool catch fractions were adopted.'},
 {'id':'FishBase_roughy','title':'FishBase orange roughy species summary','target':'https://www.fishbase.se/summary/334','supports':'Deep bathypelagic habitat (typically 400–900m) differs from the represented coastal guild; indexed primary authority page read 2026-10-03.'},
 {'id':'NIWA_galaxias','title':'NIWA, new science on inanga','target':'https://niwa.co.nz/lakes/freshwater-update/freshwater-update-75-november-2017/new-science-inanga','supports':'Marine larvae and freshwater adult life establish a true life-history mismatch, rather than following the inconsistent provider large-reef tag.'}
]

def excluded_reason(t,g,eligible):
    i=g['seq']
    if i in eligible:return 'Included: '+spec[t]['membership_reason']
    if i in [1,2]:return 'Excluded: primary producer, not the reported animal catch.'
    if i in [3,4]:return 'Excluded: micro/mesoplankton size class; no evidence that this catch reporting label is harvested microscopic plankton or fish larvae.'
    if i in [31,32,33,34,35]:return 'Excluded: bird, mammal or sea-turtle population, not this catch taxon.'
    if i in [36,37,38,39]:return 'Excluded: eggs, offal or detrital/nonfeeding pool, not landed whole animals.'
    if i in [6,7]:return 'Excluded: gelatinous zooplankton/jellyfish taxon; only the named Chrysaora record fits its dedicated group.'
    if i in [12,13]:return 'Excluded: cephalopod species/pool, incompatible with this taxon; broad Mollusca and squid exceptions were explicitly retained.'
    if i in [5,8]:return 'Excluded: planktonic or benthic invertebrate pool; incompatible taxonomic/habitat criteria, with broad crustacean and mollusc exceptions explicitly reviewed.'
    if i in [9,10,15,16,18,19,20,28,29]:return 'Excluded: species-specific source population; the named taxon differs, or this broad label does not include that lineage. Explicit hake analogues and broad-reporting exceptions are retained separately.'
    if i in [23,30]:return 'Excluded: cartilaginous-fish habitat pool, incompatible taxon or poorer habitat/feeding correspondence than retained candidates.'
    return 'Excluded: taxonomic/ecological correspondence is weaker or contradicted relative to the retained guild set; incomplete source size bounds are not invented to expand eligibility.'

rows=[]
for u in universe['taxa']:
    t=u['taxon']; s=spec[t]; ids=s['ids']
    assert all(i in groups for i in ids)
    vals=[proxy[i]['landings_total_t_km2_y'] for i in ids]
    total=math.fsum(vals)
    fallback=None
    if len(ids)==1:
        weights=[1.0];wrule='W1';wc='High';formula='weight = 1; no numerical split';qtytotal=None
    elif all(math.isfinite(x) and x>=0 for x in vals) and total>0:
        weights=[x/total for x in vals];wrule='W4';wc='Medium';formula='weight_g = native_landings_g / sum(native_landings_candidates)';qtytotal=total
    else:
        fallback={'field':'landings_total_t_km2_y','values':vals,'total':total,'reason':'All native candidate landings are explicit zeros; no positive normalizing total.'}
        vals=[proxy[i]['biomass_t_km2'] for i in ids];qtytotal=math.fsum(vals)
        assert all(math.isfinite(x) and x>=0 for x in vals) and qtytotal>0,t
        weights=[x/qtytotal for x in vals];wrule='W9';wc='Medium';formula='weight_g = native_biomass_g / sum(native_biomass_candidates)'
    assert abs(math.fsum(weights)-1)<1e-12,t
    candidates=[]
    for i,weight in zip(ids,weights):
        p=proxy[i];g=groups[i]
        candidates.append({'group_id':i,'seq':i,'group_name':g['group_name'],'display_group_name':g['group_name'].strip(),'weight':weight,
          'source_definition':g['taxon_descr'],'definition_locator':g['taxonomy_evidence'],'source_membership_scope':g['membership_scope'],
          'source_landings':p['landings_total_t_km2_y'],'source_discards':p['discards_total_t_km2_y'],'source_catch':p['catch_total_t_km2_y'],'source_biomass':p['biomass_t_km2'],
          'source_landings_artisanal':p['landings_artisanal_t_km2_y'],'source_landings_commercial':p['landings_commercial_t_km2_y'],
          'raw_source_status':p['status'],'catch_value_missing':False,'zero_is_source_explicit':p['landings_total_t_km2_y']==0,
          'loaded_catch_used':False,'source_locator':p['source'],'proxy_quantity':p['biomass_t_km2'] if wrule=='W9' else p['landings_total_t_km2_y'],
          'proxy_field':('biomass_t_km2' if wrule=='W9' else 'landings_total_t_km2_y') if wrule!='W1' else 'not required',
          'proxy_units':'t wet weight/km2' if wrule=='W9' else 't wet weight/km2/year','proxy_total':qtytotal,'weight_formula':formula,'inclusion_reason':s['membership_reason']})
    overall=min(s['membership_confidence'],wc,key=lambda x:rank[x])
    assumed_m=s['membership_rule'] not in ['M1','M2','M3']
    if wrule=='W1': allocation_reason='One reviewed group receives 100%; no empirical within-group allocation is asserted.'
    elif wrule=='W4': allocation_reason='Complete native Table A artisanal + commercial landings supply an assumed historical composition proxy; genuine zero candidates remain. Fixed ratios transfer beyond 1995–1998 and to the wider LME/other bases. The supplement branch is retained despite the sardine prose conflict.'
    else: allocation_reason='All native candidate landings are genuine zeros, so catch proportions are undefined. Complete native biomasses give an assumed composition/catchability proxy; the rejected zero-landings vector is retained. Ratios are fixed across years, the wider LME and other bases.'
    authority=(tax.get(t) or [None])[0]
    assumptions=[]
    if assumed_m:assumptions.append({'type':'membership','text':s['membership_reason']})
    if wrule!='W1':assumptions.append({'type':'allocation','text':allocation_reason})
    if any(i in [18,19,20] for i in ids):
        assumptions.append({'type':'size_definition','text':'Source prints <29, 30–49, >50 cm; length convention and boundary gaps at 29/50 are unknown. Model proportions bypass observed bin assignment and do not silently repair endpoints. Large hake has zero native landings but positive native discards.'})
    refs=list(dict.fromkeys(['Focal','FreshTaxonomy','Tam2008','Regional','SAU_methods','WoRMS']+s['extra_sources']+(['Native','FreshProxy'] if wrule!='W1' else [])+(['CompositionSearch'] if search_ids[t] else [])))
    concise_allocation = {'W1':'One group receives 100%.','W4':'Allocation assumes fixed native group-landings proportions; zero candidates remain.','W9':'Native landings are all zero; complete biomasses supply assumed proportions.'}[wrule]
    alias = source_aliases.get(t)
    if alias and authority and 'url' not in alias: alias={**alias,'url':authority.get('url')}
    rows.append({**{k:v for k,v in u.items() if k!='saved_landings_t_by_year'},
       'catch_tonnes':u['catch_t'],'classic_coefficient_wet':u['sppr_wet'],'candidates':candidates,'groups':[{'seq':c['seq'],'group_name':c['group_name'],'weight':c['weight']} for c in candidates],
       'mapping_display':'; '.join(f"{c['display_group_name']} ({c['weight']*100:.8g}%)" for c in candidates),
       'membership_rule':s['membership_rule'],'membership_rule_text':M[s['membership_rule']],
       'membership_confidence':s['membership_confidence'],'membership_reason':s['membership_reason'],
       'allocation_rule':wrule,'allocation_rule_text':W[wrule],'allocation_confidence':wc,'allocation_reason':allocation_reason,
       'overall_confidence':overall,'assumed_membership':assumed_m,'assumed_allocation':wrule!='W1','assumed':assumed_m or wrule!='W1',
       'reason':s['membership_reason']+' '+concise_allocation,'sources':refs,'assumptions':assumptions,
       'composition_search_record_ids':search_ids[t], 'taxonomic_alias_evidence':alias,
       'allocation_formula':formula,'allocation_numerator_values':vals if wrule!='W1' else None,'allocation_denominator':qtytotal,
       'rejected_proxy_attempt':fallback,'authority_record':authority,'authority_url':authority.get('url') if authority else None,
       'authority_evidence_date':'2026-09-30' if authority else None,
       'ecological_model_applicability':{'area':'Northern Humboldt Peru model applied to the full Humboldt LME; membership fit does not validate this spatial transfer.','period':'Native reference 1995–1998 (some added biology later); fixed coefficients and weights applied to 1950–2019, with 2019 reference 21–24 years later.','source_version':'Native supplement branch; paper prose’s revised sardine landings conflict is unresolved.'},
       'candidate_decisions':[{'group_id':i,'group_name':g['group_name'],'source_definition':g['taxon_descr'],'decision':'included' if i in ids else 'excluded','reason':excluded_reason(t,g,ids)} for i,g in groups.items()],
       'prior_decision':'New independent isolated candidate mapping; no regional adopted mapping copied or changed.',
       'very_low_group':s['very_low_group']})

assert len(rows)==218
assert {r['taxon'] for r in rows}=={r['taxon'] for r in universe['taxa']}
catchden=universe['metadata']['catch_denominator_t'];pprden=universe['metadata']['known_ppr_denominator_tC']
def summarized(rs):
    cv=math.fsum(r['catch_t'] for r in rs);pv=math.fsum(r['simple_chain_ppr_tC'] for r in rs if r['simple_chain_ppr_tC'] is not None)
    return {'taxa_n':len(rs),'catch_t':cv,'catch_percentage':cv/catchden*100,'simple_chain_ppr_tC':pv,'ppr_percentage':pv/pprden*100,'taxa':[r['taxon'] for r in rs]}
conf=[{'confidence':c,**summarized([r for r in rows if r['overall_confidence']==c])} for c in rank]
def rule_rows(component,names):
    d=defaultdict(list)
    for r in rows:d[(r[component+'_rule'],r[component+'_confidence'])].append(r)
    return sorted([{'rule':code,'plain_language_rule':names[code],'confidence':confidence,**summarized(rs)} for (code,confidence),rs in d.items()],key=lambda r:-r['ppr_percentage'])
vl=defaultdict(list)
for r in rows:
    if r['overall_confidence']=='Very low':vl[r['very_low_group']].append(r)
vlreasons={
 'eel_analogue':'Snake eel mapped to unnamed conger pool despite taxonomic identity differing from the regional congrio interpretation.',
 'hake_analogue':'Non-Peruvian hake/cod-like fishes use Peruvian hake groups; species, southern ecology and size boundaries differ, and native stage landings are transferred.',
 'deep_analogue':'Large deep-water colder-water fishes use the closest medium-demersal analogue; source population, depth and size mismatch remain.',
 'diadromous_analogue':'Amphidromous galaxiid lacks a corresponding source population; a coastal small-fish analogue is assumed.',
 'cartilaginous_broad':'Broad/historical cartilaginous labels cross benthic and water-column pools with unrepresented chimaera or filter-feeding ray components.',
 'chimaera_analogue':'Benthic chimaera assigned to a benthic elasmobranch analogue despite belonging to Holocephali rather than Elasmobranchii.',
 'manta_analogue':'Pelagic filter-feeding manta uses the closest chondrichthyan pool despite the source apex-predator correspondence.',
 'fish_broad':'Broad fish reporting labels have unknown composition across named and residual pools, historical taxonomic scope, and potentially unrepresented deep-water members; native landings approximate their mixtures.',
 'crustacean_broad':'Broad crustacean reporting mixes benthic and pelagic components; a macrozooplankton/benthos approximation uses biomass because both native landings are zero, with a 2–20 mm size mismatch.',
 'squatlobster_analogue':'Pelagic/benthic squat-lobster catch lacks a separate source population; macrozooplankton/benthos analogues and biomass weights retain the 2–20 mm mismatch.'}
assert None not in vl
summary={'reference_year':2019,'catch_basis':'landings','taxa_count':218,'source_stock_group_count':39,'source_original_network_nodes':41,'known_simple_chain_ppr_tC':pprden,'total_catch_t':catchden,
 'ppr_total_complete':True,'missing_classic_coefficient_taxa':[r['taxon'] for r in rows if not r['coefficient_available']],
 'missing_classic_positive_catch_taxa':[],'zero_catch_taxa_count':42,
 'confidence_rows':conf,'membership_rule_rows':rule_rows('membership',M),'allocation_rule_rows':rule_rows('allocation',W),
 'very_low_decision_groups':[{'group_key':k,'taxa':[r['taxon'] for r in rs],'reason':vlreasons[k],**{f:v for f,v in summarized(rs).items() if f!='taxa'}} for k,rs in vl.items()],
 'unresolved_taxa':[], 'mapping_coverage_taxa_percentage':100.0,'mapped_catch_percentage':100.0,
 'very_low_exposure':summarized([r for r in rows if r['overall_confidence']=='Very low']),
 'assumption_dependent_exposure':summarized([r for r in rows if r['assumed']]),
 'rule_sum_policy':'Each component table separately partitions the complete known independent classic-PPR denominator. Rows sorted by unrounded PPR share; no Sum row when total is 100% within 1e-8 percentage points.',
 'coefficient_availability_note':'34 missing classic coefficients all belong to recorded zero-landings taxa. Their annual contributions are genuine zero; no positive catch has unknown classic PPR.',
 'model_numeric_coverage':'Not inferred from mapping; depends on fresh candidate GE/TE/With Egestion coefficient availability and diagnostic restrictions.'}
for key in ['confidence_rows','membership_rule_rows','allocation_rule_rows']:
    assert sum(r['taxa_n'] for r in summary[key])==218,key
    assert abs(math.fsum(r['ppr_percentage'] for r in summary[key])-100)<1e-8,key
meta={**{k:v for k,v in universe['metadata'].items() if k not in ['npp_snapshot','settings_snapshot']},
 'run_id':'HUM2018_20261003','status':'isolated candidate proposal; unadopted','group_name_policy':'Exact native strings and source seq IDs; display labels strip only trailing whitespace.',
 'source_branch':'Native detailed supplement Table A, 39 stock nodes; 2 fishery nodes omitted from Ecopath stock calculation. Source prose/supplement Sardine landings conflict preserved.',
 'allocation_basis':'Source native artisanal+commercial LANDINGS first to match reference2019 landings, then complete BIOMASS when all candidate landings total zero; fixed map reused all years/bases as stated assumption.',
 'membership_allocation_combination':'Weaker required component; High > Medium > Low > Very low > Unresolved.',
 'authorization_boundary':'Candidate mapping/calculations only; no active workbook selection, adoption, Project/atlas or researcher signoff changes.',
 'search_coverage':'Bounded primary/authoritative searches retained in search_records.json and raw search batches. Failed full texts are identified; no snippet or gear/legal/mean-size summary is treated as measured caught-mass allocation.',
 'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'GROUP_IDENTITY.json',SOURCE/'GROUP_CATCH_BIOMASS.csv',SOURCE/'model.json']},
 'search_ledger_sha256':hashlib.sha256((OUT/'search_records.json').read_bytes()).hexdigest()}
(OUT/'mapping_review.json').write_text(json.dumps({'metadata':meta,'sources':sources,'taxa':rows,'summary':summary},ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'taxonomy_authority_records.json').write_text(json.dumps({'evidence_date':'2026-09-30','source':'../../../validation_reports/13_1_Chilean_Patagonia_(1980)/taxonomy_api_evidence.json','purpose':'Reused primary taxonomic identity only; independent focal membership decisions above.','records':{r['taxon']:tax.get(r['taxon']) for r in rows}},ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'mapping_flat.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['taxon','tl','catch_t','simple_chain_ppr_tC','mapping_display','membership_rule','membership_confidence','allocation_rule','allocation_confidence','overall_confidence','reason']
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:r[k] for k in fields} for r in rows)
(OUT/'allocation_ledger.json').write_text(json.dumps({'basis':meta['allocation_basis'],'records':[{k:r[k] for k in ['taxon','candidates','allocation_rule','allocation_confidence','allocation_formula','allocation_numerator_values','allocation_denominator','rejected_proxy_attempt','assumptions','sources','composition_search_record_ids']} for r in rows]},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'taxa':len(rows),'confidence':[{k:r[k] for k in ['confidence','taxa_n','catch_percentage','ppr_percentage']} for r in conf],'allocation_rules':[(r['rule'],r['taxa_n']) for r in summary['allocation_rule_rows']],'very_low_count':sum(len(x['taxa']) for x in summary['very_low_decision_groups'])},indent=2))
