# 52_1_Sea_of_Okhotsk_NE_(1980)

NE is a model identifier, not a northeastern spatial restriction. Chaikina (2020 p.24) compares the detailed NE Ecopath model with the SD model based on Shuntov and Dulepova. The study area is the Sea of Okhotsk, about 1,590,000 km². This corrects the older project handoff.

Chaikina, N. (2020), A Model of the Okhotsk Sea with a focus on marine mammals, pp.23-34 in Pauly & Ruiz-Leotaud (eds.), Marine and Freshwater Miscellanea II, FCRR28(2), based on her 2004 BSc thesis. [Source PDF](https://epic.awi.de/id/eprint/52730/1/Palomares20_FishCentResaRep28.pdf). The whole chapter was searched and Table 1 (p.26, PDF p.27) visually checked. Tables 1 and 3 support group definitions and diet constraints; the original 49-page thesis was searched online but no readable copy or separate supplement was obtained.

All 29 source group names/numbers match the imported model after obvious spelling/spacing normalization. The 26 consumer B/PB/QB/EE rows match Table 1 at printed precision; producer B/PB values also agree on manual inspection. Detritus biomass is absent from the table, so the imported value is not claimed to be source-verified. See source-check.json for the automated consumer comparison. The rounded published diet matrix was inspected for guild meaning, but was not independently re-extracted cell by cell.

The chapter does not supply a species inventory. Empty members.csv deliberately contains only the header; taxonomy.csv gives taxonomic labels, residual definitions and explicit membership gaps. WoRMS taxonomic lookups are archived beside the mapping; a common-name crosswalk, particularly Pacific Sardine, is labelled inference rather than asserted synonymy.

Walleye pollock and Juv. pollock are a single species at two stages. All model catches are zero, so species-level pollock uses model_biomass weights; Gadidae and Gadiformes retain the stage split as well. Shellfish and octopod residual placements are conservative feeding-guild analogues, with low confidence wherever no species list settles the split. Generic demersal catch uses the four broad bottom-fish groups; mackerels, saury, anchovies, sharks/rays and warm-water taxa with no source-compatible compartment remain unresolved. Char and whitefish are not asserted to be Pacific salmon.

The input model balances and diet sums are one, but TE is numerically unsafe: the living spectral radius exceeds one and negative sources occur. GE and With Egestion converge. Every method must retain its own health flag; the catch-mapping coverage cannot rehabilitate a diverged method. SPPR_1986 zero output is a pre-existing limitation. No algorithm or Jensen behavior was changed.

## Mapping result

151 catch rows preserved in original order; 235,876,742.751 of 242,338,606.426 tonnes mapped over 1950-2019 (**97.3335%**). 11 composite decisions. high: 50 taxa, 23.861% of catch; medium: 37 taxa, 72.676% of catch; low: 10 taxa, 0.796% of catch; unresolved: 54 taxa, 2.666% of catch. Confidence is conditional on the model being applicable.

Composite weights are left blank for identified-catch composition unless explicitly marked model_catch or model_biomass. The downstream builder records the actual fallback basis in resolved.csv. Validation success does not establish every candidate's ecological correctness: documented direct/genus candidates were checked as full sets, and family unions were reviewed against the member table with WoRMS lineage.

Largest unresolved records:

- Scomber: 1,716,358.1 t. Scombridae (mackerel genus), an epipelagic small pelagic; the Okhotsk model has no pelagic/mackerel group, only demersal/mesopelagic/benthic residual categories, so no defensible group exists. Reviewed: no documented compatible group for this catch label.
- Cololabis saira: 1,247,073.9 t. Scomberesocidae (Pacific saury), a small epipelagic fish; the Okhotsk model has no pelagic-fish group to place it in. Reviewed: no documented compatible group for this catch label.
- Scomber japonicus: 883,031.1 t. Scombridae (chub mackerel), epipelagic; same limitation as genus Scomber -- no pelagic-fish group in the Okhotsk model. Reviewed: no documented compatible group for this catch label.
- Engraulis japonicus: 546,075.0 t. Engraulidae (Japanese anchovy), small epipelagic; no anchovy or generic pelagic-fish group exists in the Okhotsk model. Reviewed: no documented compatible group for this catch label.
- Batoidea: 375,866.6 t. Skates/rays; the Okhotsk model contains no elasmobranch (shark/ray) group at all, only marine mammals, seabirds, fish and invertebrates. Reviewed: no documented compatible group for this catch label.
- Osmeridae: 340,195.1 t. Family Osmeridae (true smelts) includes several genera besides capelin (e.g. Hypomesus, Osmerus); the model's only Osmeridae-linked group, 'Capelin', is species-specific, so an unidentified smelt cannot be safely assigned to it. Reviewed: no documented compatible group for this catch label.
- Trichiurus lepturus: 195,817.1 t. Largehead hairtail (Trichiuridae) is a warm-temperate/tropical benthopelagic predator; no matching group in the Okhotsk model. Reviewed: no documented compatible group for this catch label.
- Trachurus japonicus: 160,436.4 t. Japanese jack mackerel, family Carangidae, epipelagic; no pelagic-fish group in the Okhotsk model. Reviewed: no documented compatible group for this catch label.
- Sciaenidae: 115,312.7 t. Drums/croakers, a warm-temperate demersal family; no matching group in the Okhotsk model. Reviewed: no documented compatible group for this catch label.
- Carangidae: 113,522.5 t. Jacks/pompanos, epipelagic; no pelagic-fish group in the Okhotsk model. Reviewed: no documented compatible group for this catch label.
- Seriola lalandi: 87,092.8 t. Yellowtail amberjack, Carangidae, warm-water epipelagic; no matching group. Reviewed: no documented compatible group for this catch label.
- Mugil cephalus: 85,819.3 t. Flathead grey mullet, Mugilidae, warm coastal species; no matching group in the Okhotsk model. Reviewed: no documented compatible group for this catch label.

## Regeneration and checks

Taxonomy was applied only through tools/apply_taxonomy.py. Exact group-name and seq coverage was independently asserted. Named SPPR regeneration uses tools/run_sppr.py --in-place; the result, numeric comparison, health and final validator output are recorded in validation.txt and regeneration.json. The global builder and index were left to the coordinating task.

The named UTF-8 regeneration wrote the workbook successfully. Every comparable deterministic value in all three SPPR sheets equals the original workbook within1e-9relative tolerance, with no deterministic numeric missingness changes. Monte Carlo differences reflect resampling; every missing or negative value remains explicit. Current non-OK method statuses: all method invocations completed. Per-configuration health, finite-cell counts and any changed missingness are recorded in regeneration.json.

Late source corrections were synchronized only into groups_df taxon_descr after export (29Thailand descriptions,1Guinea bird description); every other cell in every worksheet was asserted identical before and after that metadata edit. JSON non-taxonomy fields match the original backups exactly. All other units and algorithm/Jensen calculations were preserved.
