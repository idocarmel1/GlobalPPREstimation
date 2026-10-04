"""Reviewed catch mapping and portable appendix for the GM2019 adopted variant.

Source membership, ecological analogues, allocation proxies, and carbon-unit
transfer are deliberately distinguished. Does not change the regional selection.
"""
import csv, importlib.util, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
REGION = ROOT / "regions/LME_052"
CANDIDATE = HERE.parents[1]
MODEL_ID = "52_GM2019_Fig9_Pelagic_balanced_(2000-2014)"
MODEL_PATH = "models/52_GM2019_Fig9_Pelagic_(2000-2014)/assumption_variants/adopted_balanced_20261003/model.json"
spec = importlib.util.spec_from_file_location("assumed_allocation", ROOT / "tools/skills/original_skill_resources/combined-src/scripts/assumed_allocation.py")
allocation_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(allocation_module)
baseline = json.loads((HERE / "baseline_inventory.json").read_text(encoding="utf-8"))
source_groups = {int(g["group_seq"]): g for g in baseline["candidate_groups"]}
names = {i: g["group_name"] for i, g in source_groups.items()}
biomass = {i: float(g["biomass"]) * 1.544 for i, g in source_groups.items() if float(g["biomass"]) != -9999}
catch = {r["taxon"]: r for r in baseline["catch"] if r["catch_basis"] == "landings"}
classic = {r["taxon"]: r for r in baseline["classic_taxa"]}
old = defaultdict(list)
for r in baseline["old_matching"]:
    old[r["taxon"]].append({k: r.get(k) for k in ("group", "weight", "confidence")})

source_taxonomy = {
    1: "Phytoplankton; primary-producer pool (2019 Table 3 and Figure 9); exhaustive species membership not documented.",
    2: "Bacteria; Figure 9 bacterial compartment separated from Table 3 microheterotroph aggregate; source species list not documented.",
    3: "Protozoa; Figure 9 protozoan compartment separated from Table 3 microheterotroph aggregate; species list not documented.",
    4: "Copepods; source taxonomic plankton pool; species membership is not exhaustively enumerated (2019 Table 3, Figures 5 and 9).",
    5: "Euphausiids; source taxonomic plankton pool; species membership is not exhaustively enumerated (2019 Table 3, Figures 5 and 9).",
    6: "Hyperiids; source hyperiid amphipod pool; species membership is not exhaustively enumerated (2019 Table 3 and Figure 9).",
    7: "Chaetognaths, source sagittas; species membership is not exhaustively enumerated (2019 Table 3 and Figure 9).",
    8: "Pink salmon Oncorhynchus gorbuscha; chum salmon Oncorhynchus keta; sockeye salmon Oncorhynchus nerka. These three species underpin the tier III production calculation (2019 p.155; supporting dissertation Table 4.52 p.169).",
    9: "Squid at trophic level III; source examples Onychoteuthis borealijaponica; Berrytheuthis magister [source spelling]; Gonatopsis borealis (2019 p.155). Examples are not an exhaustive membership list or an exact age cutoff.",
    10: "Okhotsk Sea herring stock; source p.155 (Clupea pallasii crosswalk from retained regional taxonomy evidence).",
    11: "Deep-sea smelt (source serebryanka); dominant mesopelagic fish of eight species detected in the epipelagic (2019 p.155). Bathylagidae crosswalk is inherited from reviewed whole-sea regional taxonomy and is distinguished from coastal Osmeridae.",
    12: "Pollock less than 30 cm; source Figure 9 and Table 3. Source p.156 identifies juvenile planktivorous pollock; length convention and exact 30 cm boundary treatment not specified.",
    13: "Capelin Mallotus villosus; 2019 Figure 6, Table 3 and pp.155–156.",
    14: "Jellyfish; source Figure 9 and Table 3. Supporting dissertation Tables 4.13–4.16 include Aglantha digitale, Sarsia princeps, Aequorea spp., Obelia longissima, Cyanea capillata, Chrysaora melanaster, Aurelia aurita; examples support feeding reconstruction, not exhaustive composition.",
    15: "Pollock 30–60 cm; source Figure 9, Table 3 and p.156; source length convention and exact endpoints not specified.",
    16: "Squid at trophic level IV, mainly nekton-feeding; source examples Gonatus madokai; Gonatus onyx and others (2019 p.155–156). It is a trophic guild, not a documented universal adult size class.",
    17: "Predatory salmon; supporting dissertation p.162 identifies Chinook Oncorhynchus tshawytscha, coho Oncorhynchus kisutch, and masu Oncorhynchus masou. Tier IV source production and 2.4% total salmon biomass discussed in 2019 p.156.",
    18: "Baleen whales; source Table 3 and p.156; no exhaustive species list.",
    19: "Pollock greater than 60 cm; near-bottom very large pollock (2019 pp.152,156; Table 3 and Figure 9).",
    20: "Predatory fish; 2019 Table 3 footnote ****: sharks, daggertooth, lancetfish and other predatory fish, including halibuts with pelagic feeding. Source pool contains cartilaginous and bony fishes and does not cover every demersal fish.",
    21: "Predatory mammals; toothed whales and pinnipeds (2019 Table 3 footnote ***, pp.156–157).",
    22: "Detritus; nonliving source compartment, not a catch taxon.",
}
with (HERE / "taxonomy.csv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["seq", "group_name", "taxon_descr"])
    writer.writerows((i, names[i], source_taxonomy[i]) for i in sorted(names))

search = [
    {"date": "2026-10-03", "query": "Sea Okhotsk pollock catch length composition 30 60 cm 2014 TINRO", "url": "https://russianpollock.com/upload/iblock/6a6/soo-pollock-2018-kamchatniro.pdf", "retrieval": "Search preview recovered; full primary PDF request timed out", "adopted": False, "reason": "Subzone/month length percentages are not whole-sea caught mass below30/between30and60/above60 cm. 2018 is outside modeled 2000–2014."},
    {"date": "2026-10-03", "query": "Sea Okhotsk pollock catch length composition 30 60 cm 2014 TINRO", "url": "https://russianpollock.com/upload/iblock/b38/summary-tinro-soo-observers-2019.pdf", "retrieval": "Search preview recovered; full primary PDF request timed out", "adopted": False, "reason": "Number-based commercial/juvenile limits 35/37cm are incompatible with exact model cutoffs; no caught-mass conversion available."},
    {"date": "2026-10-03", "query": "Sea Okhotsk pollock catch length composition 30 60 cm 2014 TINRO", "url": "https://vniro.ru/en/news-archive/pollock-fishery-and-its-scientific-support-in-the-far-eastern-fishery-basin-202502251459", "retrieval": "Primary VNIRO page read", "adopted": False, "reason": "2025 short observer summary establishes commercial size ranges and subzone differences, not source-period whole-sea caught-mass shares at30/60cm."},
    {"date": "2026-10-03", "query": "Gorbatenko 2019 Okhotsk predatory salmon coho Chinook trophic III IV", "url": "https://agris.fao.org/search/en/providers/122436/records/67599d0cc7a957febdfe6888", "retrieval": "Article abstract indexed by AGRIS; source is Kuznetsova et al2021", "adopted": False, "reason": "Consistent dietary context; modeled-period source dissertationp162/Table4.52 has direct salmon membership and is preferred. No caught-mass split is established by a diet study."},
]
(HERE / "allocation_search.json").write_text(json.dumps(search, ensure_ascii=False, indent=2), encoding="utf-8")

fish_set = [8, 10, 11, 12, 13, 15, 17, 19, 20]
direct = {
    "Gadus chalcogrammus": ([12, 15, 19], "M3", "High", "The three source pollock length compartments together cover the stock; observed catch-at-length mass at30/60cm is unavailable. Source Table3 complete wet biomass supplies the approved composition/catchability proxy."),
    "Clupea pallasii": ([10], "M3", "High", "Pacific herring fits the named whole-sea source herring stock. One group; source size-independent prey composition supports no stage split."),
    "Mallotus villosus": ([13], "M1", "High", "Explicit M.villosus source identification in Figure6/Table3; single capelin compartment."),
    "Berryteuthis magister": ([9], "M1", "High", "Sourcep155 names Berrytheuthis magister [spelling variation] among tierIII squid; exact source example overrides a generic squid mixture."),
    "Bathylagidae": ([11], "M12", "Medium", "Previous evidenced whole-sea model assigns deep-sea smelts to Bathylagidae. Sourcep155 describes serebryanka as the dominant mesopelagic fish. This family-to-stock extension is inherited taxonomy, not a new exhaustive source species list."),
    "Oncorhynchus gorbuscha": ([8], "M1", "High", "Sourcep155 explicitly places pink salmon in the tierIII production calculation."),
    "Oncorhynchus keta": ([8], "M1", "High", "Sourcep155 explicitly places chum salmon in the tierIII production calculation."),
    "Oncorhynchus nerka": ([8], "M1", "High", "Sourcep155 explicitly places sockeye salmon in the tierIII production calculation."),
    "Oncorhynchus kisutch": ([17], "M1", "High", "Supporting dissertationp162 explicitly defines coho among predatory salmon; source2019 tierIV guild matches this inherited definition."),
    "Oncorhynchus tshawytscha": ([17], "M1", "High", "Supporting dissertationp162 explicitly defines Chinook among predatory salmon; source2019 tierIV guild matches this inherited definition."),
    "Oncorhynchus masou": ([17], "M1", "High", "Supporting dissertationp162 explicitly defines masu among predatory salmon; source2019 tierIV guild matches this inherited definition."),
    "Oncorhynchus": ([8, 17], "M9", "Medium", "The regional salmon genus category is extended to the two source salmon guilds. Source Table3 wet biomasses0.80/0.02million t give fixed assumed composition; unlisted trout constituents and fishery/residence differences remain."),
    "Salmonidae": ([8, 17], "M6", "Low", "The salmonid family includes non-Pacific-salmon components; two cold-water salmon guilds are usable but freshwater/coastal constituents require a substantive ecological transfer. Source salmon biomass mixture is assumed."),
    "Salvelinus": ([17], "M6", "Low", "Anadromous char is a related cold-water predatory salmonid analogue; coastal/freshwater residence differs from the source pelagic salmon pool. No literal char membership is claimed."),
    "Salvelinus malma": ([17], "M6", "Low", "Dolly Varden uses a related cold-water predatory salmonid pool with acknowledged coastal/freshwater residence mismatch; this is an ecological extension, not author membership."),
    "Coregonus": ([8], "M11", "Very low", "Whitefish can include anadromous planktivorous salmonids. The plankton-fed salmon compartment is the closest family/trophic analogue; unknown freshwater components and different life history remain."),
    "Teuthida": ([9, 16], "M3", "High", "The squid reporting category fits the source squid guild pair. III/IV are trophic pools, not a universal age cutoff. Source Table3 wet biomasses0.5/0.5million t are an assumed composition proxy."),
    "Ommastrephidae": ([9, 16], "M4", "Medium", "Pelagic squids fit the source squid guild pair by supported extension beyond listed examples; species/ontogenetic composition of the catch is unavailable."),
    "Ommastrephes bartramii": ([9, 16], "M6", "Low", "Pelagic migratory squid can use both source feeding guilds, but source isotope figure distinguishes Pacific migrants. Source biomass split is a transfer assumption, not species-specific caught composition."),
    "Todarodes pacificus": ([9, 16], "M6", "Low", "Pelagic squid has a meaningful source guild pair, with coastal/Pacific migration and size-dependent feeding differences. No exact caught-guild shares recovered; source biomass mixture is assumed."),
    "Loliginidae": ([9, 16], "M11", "Very low", "Coastal pencil squids use the represented squid trophic guilds as a cephalopod predator analogue; source gonatid/open-water species and habitat differ substantially."),
    "Cephalopoda": ([9, 16], "M10", "Very low", "Broad cephalopod category spans squid and unrepresented cuttlefish/octopus; the two squid guilds approximate that mixture. Benthic/nectonic feeding mismatch is explicit; source biomass weights are assumed."),
    "Octopoda": ([16], "M11", "Very low", "Carnivorous cephalopod analogue uses the nekton-feeding squid guild. Benthic octopus is not represented source membership; benthic food pathways and body composition differ."),
    "Octopodidae": ([16], "M11", "Very low", "Benthic carnivorous octopods use nekton-feeding squid as the closest represented cephalopod predator analogue; habitat and prey-source mismatch is substantial."),
    "Octopus": ([16], "M11", "Very low", "Benthic carnivorous octopus uses the closest represented cephalopod predator, SquidIV. No source octopus membership or matched benthic food supply is implied."),
    "Osmeridae": ([13], "M11", "Very low", "Coastal smelts are closer taxonomically/ecologically to the capelin forage-fish compartment than to the source mesopelagic deep-sea smelt stock. Estuarine/freshwater constituents and species composition remain uncertain."),
    "Clupeidae": ([10], "M11", "Very low", "Clupeid zooplanktivores use the source herring stock as a family/trophic analogue; sardines/menhadens are not explicit herring membership."),
    "Clupeiformes": ([10], "M11", "Very low", "The closest represented clupeiform/plankton-feeding fish is herring; anchovies/shads and other constituent species have no exact source stock."),
    "Sardinops sagax": ([10], "M11", "Very low", "The provider historical Pacific-sardine label uses herring as the closest represented small pelagic clupeid analogue. Source herring stock is not sardine; historical synonym/geographic transfer is disclosed."),
    "Engraulis japonicus": ([10], "M11", "Very low", "Anchovy is a small schooling clupeiform planktivore; source herring is the closest represented ecological/taxonomic analogue, with size/carbon-fraction and stock differences."),
    "Ammodytes personatus": ([13], "M11", "Very low", "Sandlance and capelin are forage fishes feeding on plankton. Sand-burrowing/coastal ecology differs; the source capelin group is a feeding analogue, not source membership."),
    "Arctoscopus japonicus": ([13], "M11", "Very low", "Japanese sandfish uses the small plankton-feeding capelin as a forage-fish analogue. Benthic/slope habitat and reproductive ecology differ; no literal stock membership is claimed."),
    "Scomber": ([10,20], "M11", "Very low", "Mackerels feed on plankton and small nekton; herring and predatory fish provide the closest represented feeding analogue set. Source stock/species, trophic intensity and body-carbon mixture differ. Source biomass weighting is an explicit coarse proxy."),
    "Scomber japonicus": ([10,20], "M11", "Very low", "Chub mackerel plankton/small-nekton feeding is approximated using the source herring and predatory-fish pools. Source herring/shark-dominated body-carbon factors and source guild biomass proportions transfer weakly."),
    "Scombridae": ([10,20], "M10", "Very low", "Mackerel/tuna/bonito reporting union spans plankton/nekton feeding; the herring and predatory-fish mixture is a broad trophic approximation. Pool-specific source biomass is not measured scombrid catch composition."),
    "Cololabis saira": ([10], "M11", "Very low", "Saury is an epipelagic plankton feeder with no source stock. Herring is the closest abundant represented plankton-feeding fish, with migration/taxonomic differences."),
    "Chanos chanos": ([10], "M11", "Very low", "Milkfish uses the plankton-feeding herring compartment only as a weak trophic analogue; tropical/estuarine range, diet details and body composition differ."),
    "Mugil cephalus": ([10], "M11", "Very low", "Mullet feeds on fine particulate/plant material and uses the low-trophic plankton-feeding herring as a weak consumer analogue; coastal benthic-detrital pathways are unrepresented."),
    "Mugilidae": ([10], "M11", "Very low", "Mullet family receives the same weak low-trophic fish analogue, with unrepresented benthic/estuarine detrital feeding explicitly retained as uncertainty."),
    "Actinopterygii": (fish_set, "M10", "Very low", "Broad ray-finned category is approximated across all represented named bony stocks and the mixed predatory-fish pool. Source20 includes sharks as well as eligible bony fishes; its whole-pool biomass is a coarse proxy. Nonfish/groups and mammals are excluded."),
    "Marine fishes not identified": (fish_set, "M10", "Very low", "Verified provider ISSCAAP39 residual is bony fishes. All represented bony stocks plus eligible bony members of the mixed predatory-fish pool are retained; benthic/bathyal/unlisted fish receive this coarse pelagic mixture. Sharks are not asserted as catch members; source20 pooled biomass contaminates the composition proxy."),
    "Marine pelagic fishes not identified": ([8,10,11,12,13,15,17,20], "M10", "Very low", "Broad pelagic bony-fish reporting mixture covers represented pelagic stocks and bony members of source20. Very large near-bottom pollock19 is excluded by its explicit source habitat. Source20 mixes shark/bony biomass; uncertain composition is disclosed."),
    "Gadidae": ([12,15,19,20], "M10", "Very low", "Pollock occupies three exact compartments; other gadids lack a named group and use the predatory-fish analogue. Whole source20 biomass is not measured gadid biomass. The assumed mixture combines stock and trophic proxies."),
    "Gadiformes": ([12,15,19,20], "M10", "Very low", "The broad gadiform category spans pollock stages and unrepresented codlings; source20 is a weak predatory-fish analogue for those residual constituents. Complete source biomass is the explicit composition proxy."),
    "Mollusca": ([4,9,16], "M10", "Very low", "Broad mollusc catch spans suspension/plant-feeding and carnivorous cephalopods; copepod grazer and the two squid guilds are weak represented trophic analogues. Source pool biomasses are not a plausible mollusc composition measure; explicit equal-thirds W11 is used."),
    "Gastropoda": ([4,6], "M10", "Very low", "The generic snail label spans grazing and predatory taxa. Copepod grazer/omnivore and hyperiid predator are weak trophic analogues; shell/benthic food pathways are absent. An explicit equal-half W11 mixture is used; no observed composition is claimed."),
    "Miscellaneous aquatic invertebrates": ([4,5,6,9,14,16], "M10", "Very low", "Broad unidentified invertebrates use represented grazer/omnivore, crustacean predator, gelatinous predator and cephalopod pools as a weak mixture; benthic composition is unknown. Equal-sixth W11 avoids treating unrelated model pool biomass as observed catch composition."),
    "Decapoda": ([5,6], "M11", "Very low", "Omnivorous/predatory crustacean analogue pair uses euphausiids and hyperiids. Decapod size, benthic habitat and prey-source mismatch is substantial. Source crustacean wet biomass mixture transfers as an explicit assumption."),
    "Miscellaneous marine crustaceans": ([5,6], "M11", "Very low", "Provider shrimp/crab residual is approximated with represented omnivorous and predatory crustacean pools; benthic adult structure is absent. Source biomass allocation is assumed."),
}
unresolved = {
    "Cyprinidae": "Freshwater cyprinids have no source freshwater/marine guild correspondence; no meaningful marine predatory/plankton-stock transfer is established.",
    "Apostichopus japonicus": "Benthic deposit-feeding sea cucumber requires a sediment/detritivore pathway absent from the biological compartments. Detritus is not an animal catch group.",
    "Holothuroidea": "Benthic deposit-feeding holothurians have no represented consumer compartment with comparable source pathway; detritus/bacteria are not usable taxon mappings.",
    "Echinoidea": "Macroalgal/benthic-grazing sea urchins lack a phytobenthos consumer pathway; assigning them to pelagic microbes or a crustacean solely for coverage is not defensible.",
    "Echinozoa": "Urchin/sea-cucumber reporting union spans missing macroalgal-grazing and sediment deposit-feeding benthic consumers; no meaningful represented group set.",
    "Haliotidae": "Benthic macroalgal-grazing abalones lack a modeled phytobenthos/consumer pathway. Pelagic copepod grazing is too weak a transfer to adopt here.",
    "Haliotis": "Benthic macroalgal-grazing abalones lack a modeled phytobenthos/consumer pathway; no source comparable consumer.",
    "Scaridae": "Reef algal-grazing parrotfishes have no represented source reef or macroalgal consumer pathway; the extremely small catch is retained unresolved.",
}
filter_feeders = {"Bivalvia","Corbicula japonica","Crassostrea","Mactridae","Magallana gigas","Mizuhopecten yessoensis","Mytilidae","Pectinidae","Pinctada"}
jellyfish = {"Cephea","Rhopilema hispidum","Scyphozoa"}
shrimp = {"Dendrobranchiata","Metapenaeus","Pandalopsis japonica","Pandalus","Pandalus borealis","Pandalus goniurus","Pandalus hypsinotus","Pandalus kessleri","Penaeus chinensis","Sclerocrangon","Squillidae"}
crab = {"Brachyura","Chionoecetes","Chionoecetes japonicus","Chionoecetes opilio","Erimacrus isenbeckii","Panulirus","Paralithodes","Paralithodes brevipes","Paralithodes camtschaticus","Paralithodes platypus"}
equal = {"Mollusca","Gastropoda","Miscellaneous aquatic invertebrates"}
reviews, matching, candidates = [], [], []
level_order = ["High","Medium","Low","Very low","Unresolved"]
for taxon, c in sorted(catch.items()):
    if taxon in unresolved:
        ids, rule, membership, reason = [], "M8", "Unresolved", unresolved[taxon]
    elif taxon in direct:
        ids, rule, membership, reason = direct[taxon]
    elif taxon in filter_feeders:
        ids, rule, membership = [4], "M11", "Very low"
        reason = "Bivalve suspension feeding has a weak particulate/plankton-consumer analogue in copepods. Benthic filtration, shell/body carbon and detrital feeding differ; no literal copepod taxonomic membership is claimed."
    elif taxon in jellyfish:
        ids, rule, membership = [14], "M4", "Medium"
        reason = "The jellyfish taxon fits the source gelatinous predator group by extension beyond supporting-source species. Tropical/stock-specific composition can differ; one compartment removes split uncertainty."
        if taxon == "Scyphozoa":
            rule, membership = "M3", "High"
            reason = "Scyphozoan jellyfish are represented in the source jellyfish pool and supporting diet tables; no competing gelatinous group exists."
    elif taxon in shrimp:
        ids, rule, membership = [5], "M11", "Very low"
        reason = "Decapod/mantis shrimp uses euphausiids as the closest represented omnivorous crustacean feeding analogue. Taxonomic, size, benthic habitat and body-carbon differences are explicit; source membership is not asserted."
    elif taxon in crab:
        ids, rule, membership = [6], "M11", "Very low"
        reason = "Crab/lobster uses hyperiids as the closest represented omnivorous/carnivorous crustacean analogue. Adult benthic feeding, size and body-carbon differences are substantial; no literal source membership is claimed."
    else:
        ids, rule, membership = [20], "M11", "Very low"
        reason = "Unlisted marine fish uses the source predatory-fish guild as the closest represented fish-feeding/animal-feeding analogue; source pool is pelagic and includes sharks, whereas this catch label may be benthic/bathyal/reef-associated and have different prey/body carbon."
        if taxon in {"Isurus","Isurus oxyrinchus","Prionace glauca"}:
            rule, membership = "M3", "High"
            reason = "The source predatory-fish pool explicitly includes sharks; this pelagic shark fits the named generic taxon and feeding habitat. One group receives the catch."
        elif taxon in {"Hippoglossus stenolepis","Reinhardtius hippoglossoides","Atheresthes evermanni"}:
            rule, membership = "M6", "Low"
            reason = "Source Table3 explicitly includes halibuts with pelagic feeding. This halibut/flounder can use that pool with a partial/conflicting benthic habitat and variable pelagic-feeding fit; no total stock membership is proved."
        elif taxon in {"Chondrichthyes","Elasmobranchii","Batoidea"}:
            reason += " Rays/chimaeras are not automatically the source shark stock; source pool mixes eligible bony predators with sharks."
    if not ids:
        weights, w_rule, w_conf, attempts = [], "W8", "Unresolved", []
    elif len(ids) == 1:
        weights, w_rule, w_conf, attempts = [1.0], "W1", "High", []
    elif taxon in equal:
        weights, w_rule, w_conf = [1/len(ids)]*len(ids), "W11", "Very low"
        attempts = [{"field":"catch","values":[None]*len(ids),"usable":False,"reason":"Source catches are absent; researcher runtime zeros are not observed catch."},{"field":"biomass","values":[biomass[i] for i in ids],"usable":False,"reason":"Model biomasses across unrelated broad trophic analogues do not establish catch composition; rejected before equal-share judgment."}]
    else:
        allocation = allocation_module.allocate([{"group_id":i,"eligibility":True,"catch":None,"biomass":biomass[i]} for i in ids])
        weights, w_rule, w_conf, attempts = allocation["weights"], "W9", allocation["confidence"], allocation["attempts"]
    confidence = max((membership, w_conf), key=level_order.index)
    tl = classic.get(taxon, {}).get("tl")
    simple_sppr = classic.get(taxon, {}).get("sppr")
    mass = c["catch_2019"]
    simple_ppr = 0.0 if mass == 0 else mass*simple_sppr/9 if isinstance(mass,(float,int)) and isinstance(simple_sppr,(float,int)) else None
    source_ids = ["S1","S2","S3","S4"]
    transfer = "Fixed 2000–2014 pool proportions/coefficients are applied across1950–2019 landings, totalcatch and discards; annual ecosystem/stage composition is not reconstructed. For carbon native SPPR, source group wet/C factors transfer with the group assignment; this is an additional weak assumption for ecological analogues."
    review = dict(taxon=taxon, common_name=c["common_name"], functional_group=c["functional_group"], catch_tonnes=mass, total_catch_1950_2019=c["total_1950_2019"], tl=tl, simple_sppr=simple_sppr, simple_ppr_tC=simple_ppr, membership_rule=rule, membership_confidence=membership, allocation_rule=w_rule, allocation_confidence=w_conf, overall_confidence=confidence, assumed=rule not in {"M1","M2","M3"} or w_rule!="W1", included_groups=[names[i] for i in ids], excluded_groups=[names[i] for i in names if i not in ids], reason=reason, applicability=transfer, source_ids=source_ids, previous_mapping=old[taxon], allocation_attempts=attempts, groups=[dict(seq=i,group=names[i],weight=w,source_biomass_million_wet_tonnes=biomass.get(i)) for i,w in zip(ids,weights)])
    reviews.append(review)
    if ids:
        for i,w in zip(ids,weights):
            matching.append(dict(model_id=MODEL_ID,taxon=taxon,group=names[i],weight=w,confidence=confidence.lower().replace(" ","_"),evidence="models/52_GM2019_Fig9_Pelagic_(2000-2014)/research_20261003/integration/taxon_audit.json",explanation=reason+" "+transfer))
            candidates.append(dict(unit_id="LME_052",model_id=MODEL_ID,taxon=taxon,seq=i,group=names[i],weight=w,membership_rule=rule,membership_confidence=membership,allocation_rule=w_rule,allocation_confidence=w_conf,confidence=confidence,source_catch=None,source_catch_raw="not reported",loaded_catch=0.0,source_biomass=biomass.get(i),source_biomass_units="million wet tonnes",source_biomass_provenance="2019 Table3 printedp154/PDFp12",source_period="2000–2014",years_applied="1950–2019",catch_bases_applied="landings;catch;discards",assumed=review["assumed"],reason=reason,limitations=transfer))
    else:
        matching.append(dict(model_id=MODEL_ID,taxon=taxon,group=None,weight=None,confidence="unresolved",evidence="models/52_GM2019_Fig9_Pelagic_(2000-2014)/research_20261003/integration/taxon_audit.json",explanation=reason))

total = math.fsum(r["catch_tonnes"] for r in reviews)
mapped = math.fsum(r["catch_tonnes"] for r in reviews if r["groups"])
known_simple = math.fsum(r["catch_tonnes"] for r in reviews if r["simple_ppr_tC"] is not None)
verylow = math.fsum(r["catch_tonnes"] for r in reviews if r["overall_confidence"]=="Very low")
total_simple = math.fsum(r["simple_ppr_tC"] for r in reviews if r["simple_ppr_tC"] is not None)
summary = dict(schema_version=1,unit_id="LME_052",model_id=MODEL_ID,model_path=MODEL_PATH,year=2019,catch_basis="landings",catch_units="wet tonnes",simple_ppr_units="tonnesC; wet-equivalentPPR/9 once",retained_catch_range="1950–2019",taxa_count=len(reviews),total_catch_tonnes=total,mapped_catch_tonnes=mapped,mapping_coverage_percent=100*mapped/total,very_low_catch_tonnes=verylow,very_low_catch_percent=100*verylow/total,known_classic_catch_tonnes=known_simple,known_classic_catch_percent=100*known_simple/total,total_known_simple_ppr_tC=total_simple,unresolved=[dict(taxon=r["taxon"],catch_tonnes=r["catch_tonnes"],reason=r["reason"]) for r in reviews if not r["groups"]],missing_classic=[dict(taxon=r["taxon"],catch_tonnes=r["catch_tonnes"],tl=r["tl"],simple_sppr=r["simple_sppr"]) for r in reviews if r["simple_ppr_tC"] is None],confidence=[],rule_shares=[])
for confidence in level_order:
    rr=[r for r in reviews if r["overall_confidence"]==confidence]
    mass=math.fsum(r["catch_tonnes"] for r in rr)
    ppr=math.fsum(r["simple_ppr_tC"] for r in rr if r["simple_ppr_tC"] is not None)
    summary["confidence"].append(dict(confidence=confidence,taxa=len(rr),catch_tonnes=mass,catch_percent=100*mass/total,simple_ppr_tC=ppr,simple_ppr_percent=100*ppr/total_simple))
for (m,w), rr in sorted(((key,[r for r in reviews if (r["membership_rule"],r["allocation_rule"])==key]) for key in {(r["membership_rule"],r["allocation_rule"]) for r in reviews}),key=lambda pair:-math.fsum(r["simple_ppr_tC"] or 0 for r in pair[1])):
    mass=math.fsum(r["catch_tonnes"] for r in rr)
    ppr=math.fsum(r["simple_ppr_tC"] or 0 for r in rr)
    summary["rule_shares"].append(dict(membership_rule=m,allocation_rule=w,taxa=len(rr),catch_tonnes=mass,catch_percent=100*mass/total,simple_ppr_tC=ppr,simple_ppr_percent=100*ppr/total_simple))
(HERE / "taxon_audit.json").write_text(json.dumps(reviews,ensure_ascii=False,indent=2),encoding="utf-8")
(HERE / "mapping_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
(HERE / "matching_rows.json").write_text(json.dumps(matching,ensure_ascii=False,indent=2),encoding="utf-8")
(HERE / "allocation_ledger.json").write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))

if "--appendix" in sys.argv:
    # Artifact Tool and its dependency loader are unavailable in this subagent;
    # cache node_modules was verified empty. Use the documented fallback.
    import openpyxl
    from openpyxl.styles import Alignment,Font,PatternFill
    from openpyxl.worksheet.table import Table,TableStyleInfo
    from openpyxl.utils import get_column_letter
    w=openpyxl.Workbook()
    s=w.active;s.title="Taxon mappings"
    s.append(["2019 landings; sorted by unrounded independent simple-chain PPR descending; wet catch t and PPR tC. Coefficients/proxies fixed across1950–2019. Missing TL/PPR stays unknown; zero catch produces zero PPR."])
    s.merge_cells("A1:G1");s.row_dimensions[1].height=45
    s.append(["Taxon name","TL","Catch (t)","Simple-chain PPR (t C)","Mapped group names and weights","Confidence level","Reason"])
    for r in sorted(reviews,key=lambda r:(r["simple_ppr_tC"] is None,-(r["simple_ppr_tC"] or 0),r["taxon"])):
        groups="; ".join(f'{g["group"]} ({100*g["weight"]:.6f}%)' for g in r["groups"]) or "Unresolved"
        s.append([r["taxon"],r["tl"] if r["tl"] is not None else "?",r["catch_tonnes"],r["simple_ppr_tC"] if r["simple_ppr_tC"] is not None else "?",groups,r["overall_confidence"],r["reason"]+" [S1–S4; allocation ledger]. "+r["applicability"]])
    s.freeze_panes="C3";s.auto_filter.ref=f"A2:G{s.max_row}";s.sheet_view.showGridLines=False
    for col,width in zip("ABCDEFG",[32,9,17,25,58,17,110]):s.column_dimensions[col].width=width
    for row in s.iter_rows():
        for cell in row:cell.alignment=Alignment(vertical="top",wrap_text=True);cell.font=Font(name="Calibri",size=11)
    for cell in s[2]:cell.font=Font(name="Calibri",size=11,bold=True,color="FFFFFF");cell.fill=PatternFill("solid",fgColor="174C58")
    for i in range(3,s.max_row+1):
        s.row_dimensions[i].height=max(72,14*math.ceil(len(s.cell(i,7).value or "")/100))
        for j in [3,4]:s.cell(i,j).number_format='#,##0.000000'
    tab=Table(displayName="GM2019_Mappings",ref=f"A2:G{s.max_row}");tab.tableStyleInfo=TableStyleInfo(name="TableStyleMedium2",showRowStripes=True);s.add_table(tab)
    ss=w.create_sheet("Sources");ss.append(["Source ID","Description and use","Link"])
    sources=[
        ("S1","Gorbatenko & Melnikov2019, DOI10.26428/1606-9919-2019-198-143-163. Whole Okhotsk epipelagic2000–2014; Table3p154 biomass/body wet:C; pp155–157 source guilds; Figure9 generalized carbon flows.","papers/OKH-GM2019/gorbatenko_melnikov_2019.pdf#page=12"),
        ("S2","Gorbatenko2018 dissertation; p162 predatory-salmon membership; Table4.52p169 diet/biomass; source recovery ledger preserves scope and source conflicts.","papers/OKH-GM2019/gorbatenko_2018_dissertation.pdf#page=162"),
        ("S3","LME_052 regional Catch and ClassicPPR/Taxa. Catch is wet tonnes; original TL/method/source fields are unchanged. Classic PPR is catch×10^(TL−1)/9 where a saved coefficient exists; no new TL gaps filled.","LME_052.xlsx"),
        ("S4","Complete mapping audit: source vs assumed membership, candidate group sets, prior mapping, source wet biomass, rejected catch vectors, fixed transfers and confidence components.","models/52_GM2019_Fig9_Pelagic_(2000-2014)/research_20261003/integration/taxon_audit.json"),
        ("S5","2026-10-03 online primary fishery retrieval log. No compatible whole-sea caught-mass split recovered; commercial length reports are not number-to-mass conversions.","models/52_GM2019_Fig9_Pelagic_(2000-2014)/research_20261003/integration/allocation_search.json"),
        ("S6","Allocation ledger: every candidate, weight, raw/source/runtime catch distinction, source wet biomass, W9 or W11 assumption and applicability.","models/52_GM2019_Fig9_Pelagic_(2000-2014)/research_20261003/integration/allocation_ledger.json"),
        ("S7","Previous whole-sea1980 model taxonomy confidence audit, used only as reviewed crosswalk/context. Its group IDs, weights and SPPR are not copied into this selected reconstruction.","validation_reports/52_1_Sea_of_Okhotsk_NE_(1980)/taxon_audit.json"),
        ("S8","VNIRO primary observer update25Feb2025: commercial length ranges/subzone differences; rejected as outside source period and without compatible whole-sea caught mass.","https://vniro.ru/en/news-archive/pollock-fishery-and-its-scientific-support-in-the-far-eastern-fishery-basin-202502251459"),
    ]
    for row in sources:ss.append(row);ss.cell(ss.max_row,3).hyperlink=row[2];ss.cell(ss.max_row,3).font=Font(name="Calibri",size=11,color="0563C1",underline="single")
    for col,width in zip("ABC",[12,120,80]):ss.column_dimensions[col].width=width
    for row in ss.iter_rows():
        for cell in row:cell.alignment=Alignment(vertical="top",wrap_text=True)
    for i in range(2,ss.max_row+1):ss.row_dimensions[i].height=60
    ss.freeze_panes="B2";ss.auto_filter.ref=f"A1:C{ss.max_row}";ss.sheet_view.showGridLines=False
    path=REGION/f"{MODEL_ID}_taxon_mapping_appendix.xlsx"
    w.save(path)
    print("APPENDIX",path)
