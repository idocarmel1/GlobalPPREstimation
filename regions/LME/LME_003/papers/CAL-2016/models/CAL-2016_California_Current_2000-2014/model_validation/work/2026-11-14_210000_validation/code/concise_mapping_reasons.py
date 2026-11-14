from pathlib import Path
import json
p=Path('regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014/model_validation/evidence/mapping/coverage_2019_landings_20261114.json')
d=json.loads(p.read_text(encoding='utf-8'))
reasons=[
'Forty bony-fish-bearing pools approximate unknown reporting-category composition, including named stocks and juvenile stages. Unrepresented taxa and the mixed ratfish/bony Benthic fish pool limit membership; source Yield proportions assume the same composition across 1950–2019 and catch bases.',
'Albacore supplies the closest represented mobile pelagic predator analogue. These unlisted taxa can differ substantially in size, feeding and offshore or deep-water habitat; the assignment does not establish albacore-group membership.',
'Dogfish, Skates and Sharks approximate the broad elasmobranch label; unlisted sharks and non-skate rays remain imperfect members. Source Yield proportions assume fixed composition across years and catch bases.',
'Pacific Mackerel and Albacore approximate the family, but other tunas, bonitos and Spanish mackerels lack corresponding pools. Source Yield proportions assume fixed composition across years and catch bases.',
'Pacific Mackerel is the nearest represented mobile coastal-pelagic analogue. Its documented Scomber identity does not include these taxa, which can differ in feeding, size and habitat.',
'Herring is the closest represented taxonomic and coastal-forage analogue for these unlisted herring or shad taxa. Species identity and warm-water ranges differ from the source pool.',
'Other cephal. supplies a taxonomic analogue, but Appendix B explicitly limits it to smaller prey cephalopods and excludes jumbo squid. This predatory species therefore contradicts the operative source definition.',
'Named sardine, anchovy and herring pools approximate this broad order, but tropical members are unrepresented. Source Yield proportions assume a constant mixture across years and catch bases.',
'Residual Benthic fish is the closest represented habitat or taxonomic analogue for these unlisted taxa. Source examples and provider categories do not establish membership, and transferring the pool’s feeding and habitat composition remains weak.',
'Documented shallow-bay benthic habitat and crab, clam and fish feeding support Benthic fish as an analogue. The provider’s small-pelagic classification conflicts with adult ecology; species and warm-estuarine transfer remain uncertain.',
'Sharks supplies the closest represented large-shark analogue. Source representatives do not establish these members, and taxonomic, feeding and depth differences remain unresolved.',
'Anchovy supplies the closest represented anchovy and forage-fish analogue. Pacific anchoveta is absent from the source definition and differs in species identity and southern geographic range.',
'Benthic shrimp is the closest represented benthic crustacean analogue, but its source examples chiefly describe Crangon and other carideans. The penaeid and mantis-shrimp labels are therefore weak ecological extensions.',
'Skates is the closest represented flattened-elasmobranch analogue for non-skate rays. Their benthic or pelagic habitats and feeding can differ substantially, and the source does not establish membership.',
'Mixed Benthic fish, Hake and Grenadiers approximate this order, but cod and pollock members are absent and Benthic fish includes unrelated families. Source Yield proportions transfer a fixed mixed-pool composition across years and catch bases.',
'Skates supplies a flattened-elasmobranch analogue for this broad reporting category. Non-skate rays remain included only by approximation because their feeding and habitats can differ substantially.',
'Epibenthic crustaceans are the closest represented motile benthic analogue for spiny and slipper lobsters. The source’s brachyuran and anomuran examples do not establish lobster membership.',
'Dogfish, Skates, Sharks and the Hydrolagus-bearing Benthic fish pool approximate cartilaginous fishes. The mixed bony/cartilaginous pool weakens membership; source Yield proportions transfer its composition across years and catch bases.',
'Coastal bottom-feeding habitat supports Benthic fish as an analogue. Milkfish feeding on microbial mats, detritus and epiphytes is poorly represented by the source’s animal-prey diet, with no producer diet and little detritus.',
'Shallow coastal sediment-feeding habitat connects mullet to Benthic fish. Its detritus and microalgal energy pathway is poorly represented by the source’s animal-prey diet, with no producer diet and little detritus.',
'Demersal model pools approximate the historical perch-like reporting category, whose modern taxonomic limits are uncertain. This provider-guild proxy is not exhaustive order membership; source Yield proportions assume fixed composition across years and catch bases.',
'Juvenile rockfish and residual Nearshore, Shelf and Slope pools are the closest represented rockfish analogue set. Unlisted species do not belong to named single-species stocks; unknown adult habitat composition is approximated with fixed source Yield proportions.',
'Buried, epibenthic, pelagic-shrimp and dedicated crab/shrimp pools approximate the provider’s broad crustacean category. Its actual mixture is unknown; source Yield proportions assume fixed composition across years and catch bases.',
'Mixed infaunal, epibenthic and pelagic-shrimp pools plus named shrimp and crab groups approximate Decapoda. Actual within-label composition is unknown; source Yield proportions transfer a fixed mixture across years and catch bases.',
'Coastal bottom-feeding ecology connects the mullet family to Benthic fish. Whole-family composition is unknown, and its detritivore or microalgal pathways are poorly represented by the source’s mainly animal-prey diet.',
'Market squid and Other cephal. approximate a label with unknown size and species composition. Identified-catch proportions transfer across 1950–2019 without evidence that donor catches represent the unidentified reporting population.',
'Dogfish supplies the closest represented demersal dogfish or catshark analogue. Its source representatives do not establish these members, and taxonomic, feeding and depth differences remain unresolved.',
'Juvenile and residual Nearshore, Shelf and Slope rockfish pools approximate a reporting category with historical family ambiguity. Named stocks and thornyheads are not asserted members; fixed source Yield proportions approximate its unknown composition.',
'Named forage and large pelagic fish, mesopelagics, salmon and compatible water-column or juvenile stocks approximate unknown pelagic reporting composition. Strictly benthic adults, including adult Sablefish, are excluded; source Yield proportions assume a fixed mixture across years and catch bases.',
'The provider’s demersal-invertebrate scope restricts this broad mollusc label to benthic bivalve and gastropod pools. Actual composition remains unknown, and identified-catch proportions transfer across years without an established donor/target reporting match.',
'Nearshore rock. and Widow rock. partly match sunfish gelatinous feeding, but differ in body size, physiology, habitat and non-gelatinous diet. Source Yield proportions impose a fixed mixture across years and catch bases; neither pool establishes source membership.',
'Coastal bottom-feeding habitat connects white mullet to Benthic fish. Its detritivore and microalgal feeding is poorly represented by the source’s mainly animal-prey diet, and species-specific composition is unknown.',
'Benthic fish contains tomcod and thus offers a cod-family connection. It is dominated by other fish families, however, so transferring the entire mixed pool is only a weak analogue.',
'Nearshore bottom-dwelling habitat and body form connect prickleback to the eelpout/sculpin-bearing Benthic fish pool. Macroalgal herbivory is absent from the source’s producer diet and model compartments, creating a serious energy-pathway mismatch.',
'Other smelt offers the closest represented small coastal-forage analogue for silversides and flyingfishes. The ecological resemblance does not establish family identity or membership in the source pool.',
'Sand lance partly matches blacksmith’s zooplankton feeding. Reef-dwelling damselfish and sand-burying forage fish differ substantially in habitat, so this feeding-role analogue does not establish membership.',
'Coastal reef and bottom-associated habitat connects opaleye to Benthic fish. Its predominantly algal and seagrass diet lacks a corresponding herbivorous group or macroalgal producer, so the model misrepresents its main energy pathway.',
'Coastal reef habitat connects sea-chubs to Benthic fish. Unknown family composition and macroalgal grazers conflict with the source’s animal-prey diet and absent macroalgal pathway.',
'Demersal stocks, residual Benthic fish, surfperch, grenadiers and compatible juveniles approximate the unidentified groundfish label. Unknown composition and ratfish in the mixed Benthic fish pool limit membership; source Yield proportions transfer a fixed mixture across years and catch bases.',
'Benthic and demersal-caught shrimp, crabs, mixed bottom fauna, gelatinous organisms and cephalopods approximate a taxonomically uncertain label. Plankton-only pools are excluded; source Yield proportions assume fixed composition across years and catch bases.',
'Salmon is the closest represented family analogue, but the source contains only marine Chinook and coho. Ecologically different trout and char prevent treating the whole family as documented members.',
'Pacific Mackerel and Albacore approximate the provider’s tuna, bonito and billfish category, which includes absent billfish stocks. Source Yield proportions assume the same broad pelagic composition across years and catch bases.',
'Sculpin-bearing Benthic fish, rockfish, thornyheads and juvenile pools approximate the historical scorpionfish/flathead category. Unlisted taxa and mixed-pool contents remain uncertain; source Yield proportions assume fixed composition across years and catch bases.',
'Market squid and Other cephal. approximate a broad squid label whose large predatory members are unresolved. Identified-catch proportions transfer across 1950–2019 without evidence that donor catches represent the target reporting population.'
]
assert len(reasons)==len(d['very_low_decisions'])==44
for r,s in zip(d['very_low_decisions'],reasons):r['report_reason']=s
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Added 44 concise report reasons; maximum word count',max(len(s.split()) for s in reasons))
