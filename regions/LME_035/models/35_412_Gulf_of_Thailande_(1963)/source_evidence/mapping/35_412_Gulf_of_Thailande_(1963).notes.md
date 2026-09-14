# 35_412_Gulf_of_Thailande_(1963)

**The file contains the 1980 model, despite its 1963 filename and model_year.** The local Ecobase metadata description explicitly identifies the overexploited Gulf of Thailand 1980. Christensen (1998) Table II p.136 supplies 11 biomass entries: all 11 match the imported JSON's 1980 column at printed precision, while 10 disagree with 1963; Benthos is unchanged at 33 in both periods. See source-check.json for every value. No numerical parameter or filename was changed. This identity warning must travel with downstream outputs.

Christensen, V. (1998), Fishery-induced changes in a marine ecosystem: insight from models of the Gulf of Thailand, Journal of Fish Biology 53(Suppl.A):128–142. [Original publication full text, linked from the author profile](https://www.academia.edu/1483062/Fishery_induced_changes_in_a_marine_ecosystem_insight_from_models_of_the_Gulf_of_Thailand); [DOI](https://doi.org/10.1111/j.1095-8649.1998.tb01023.x); [author profile](https://ubc.academia.edu/VillyChristensen).

The web reader retrieved the article's full HTML text. The publisher page/PDF and direct author-page/PDF requests returned 403. Archived retrieval records and extracted source facts are in PPRAtlas/archive/regions/LME_035/Christensen-1998; no original PDF is falsely claimed. The p.130 ecological-grouping prose, pp.130–132 model methods, Tables I/II and the article's discussion were read. Table II was checked numerically. The paper says the full models were distributed through ecopath.org; it does not print a complete B/PB/QB/EE/diet table. Therefore full numerical source re-extraction remains unavailable, while identity, habitat and documented membership verification are substantially resolved.

The source covers the 10–50 m Gulf of Thailand shelf. Applying it to all LME_035 catch is a geographic/habitat transfer. Pauly & Chuenpagdee (2003), Development of fisheries in the Gulf of Thailand Large Marine Ecosystem, Fig.14-3 was retrieved as supporting lineage evidence. [Author-hosted PDF](https://www.seaaroundus.org/doc/Researcher%2BPublications/dpauly/PDF/2003/Books%26Chapters/DevelopmentFisheriesGulfThailandLargeMarineEcosystem.pdf). The accessible Vibunpant (2003) model was excluded as direct evidence because it has 40 groups and describes 1973.

## Membership decisions

The recovered p.130 list supplies 38 member rows, including duplicated juvenile memberships and the source's common-name sardine/anchovy components. It names important fishery components, not an exhaustive inventory. Printed Ephinephelus and Plectorhynchus were explicitly normalized to Epinephelus and Plectorhinchus using WoRMS; Tachysuridea remains an unresolved source spelling and was not silently converted to a family. Exact/containing-genus/source-family decisions override SAU habitat classes; WoRMS responses are archived in taxonomy-sources.json. [WoRMS taxonomy service](https://www.marinespecies.org/rest/AphiaRecordsByNames), queried 2026-09-07.

The source changes Sciaenidae/Pennahia, Lethrinus and Psettodes to medium demersal piscivores; Priacanthus to small demersal piscivores; and Scolopsis/Upeneus to medium demersal benthivores. Nemipteridae therefore includes both medium Scolopsis and small Nemipterus. Flatfish order catch includes the source's medium-piscivore Psettodes plus Bothidae/Cynoglossidae. Clupeiformes includes the large-piscivore Chirocentrus stages and the source's sardine/anchovy small-pelagic pool. All documented candidates are retained. The candidate-audit records 66 source-constrained cases and the changed decisions; standard member validation alone only checks intersection.

The original paper explicitly splits juvenile grouper AND snapper, correcting the shortened Juv. groupers JSON name. Shark, large-piscivore and grouper/snapper stages use model_catch weights; juvenile reported catches are zero. Scombridae, elasmobranchs, Mollusca and Decapoda retain their multiple represented compartments.

O.fish corresponds to the source's trash-fish residual, superseding the earlier inference that its label meant a dedicated omnivore group. Its imported diet remains 25% each phytoplankton, detritus, zooplankton and benthos. Unidentified demersal landings span explicit guilds and this residual; the label does not justify assigning every unidentified fish solely to trash fish. Herbivores/omnivores without source membership remain low-confidence residual analogues. Billfish remain unresolved because this shelf model has no documented oceanic billfish compartment. Other illustrative-list extensions are marked as inference.

## Mapping result

247 catch rows preserved in original order; 151,940,825.586 of 151,964,195.481 tonnes mapped over 1950-2019 (**99.9846%**). 63 composite decisions. high: 105 taxa, 48.077% of catch; medium: 117 taxa, 45.733% of catch; low: 16 taxa, 6.175% of catch; unresolved: 9 taxa, 0.015% of catch. Confidence is conditional on the model being applicable.

Composite weights are left blank for identified-catch composition unless explicitly marked model_catch or model_biomass. The downstream builder records the actual fallback basis in resolved.csv. Validation success does not establish every candidate's ecological correctness: documented direct/genus candidates were checked as full sets, and family unions were reviewed against the member table with WoRMS lineage.

Largest unresolved records:

- Istiophorus: 11,854.2 t. Sailfish genus (Istiophoridae), not Scombridae; the 1963 shallow Gulf of Thailand shelf model has no billfish compartment and oceanic epipelagic billfish are outside its likely original scope.
- Istiophoridae: 6,152.4 t. Billfish family, taxonomically distinct from Scombridae Tuna; no billfish compartment in this model.
- Xiphias gladius: 2,801.2 t. Swordfish (Xiphiidae), an oceanic epipelagic species outside the demersal/coastal-pelagic scope of the 1963 Gulf of Thailand shelf model; no billfish compartment exists.
- Makaira mazara: 1,283.1 t. Blue marlin (Istiophoridae); no billfish compartment in this model.
- Istiompax indica: 851.1 t. Black marlin (Istiophoridae); no billfish compartment in this model.
- Makaira: 263.4 t. Marlin genus (Istiophoridae); no billfish compartment in this model.
- Istiophorus platypterus: 164.3 t. Sailfish (Istiophoridae), not Scombridae; no billfish compartment exists in this 1963 coastal-shelf model.
- Tetrapturus angustirostris: 0.1 t. Shortbill spearfish (Istiophoridae), an oceanic species with no counterpart compartment in this shallow-shelf 1963 model.
- Kajikia audax: 0.1 t. Striped marlin (Istiophoridae), an oceanic species with no counterpart compartment in this shallow-shelf 1963 model.

## Regeneration and checks

Taxonomy was applied only through tools/apply_taxonomy.py. Exact group-name and seq coverage was independently asserted. Named SPPR regeneration uses tools/run_sppr.py --in-place; the result, numeric comparison, health and final validator output are recorded in validation.txt and regeneration.json. The global builder and index were left to the coordinating task.

The named UTF-8 regeneration wrote the workbook successfully. Every comparable deterministic value in all three SPPR sheets equals the original workbook within 1e-9 relative tolerance, with no deterministic numeric missingness changes. Monte Carlo differences reflect resampling; every missing or negative value remains explicit. Current non-OK method statuses: sym_TE_asPP: failed; sym_TE_asDC: failed; sym_GE_asPP: failed; sym_GE_asDC: failed; sym_WithEgestion_asPP: failed; sym_WithEgestion_asDC: failed. Per-configuration health, finite-cell counts and any changed missingness are recorded in regeneration.json.

Late source corrections were synchronized only into groups_df taxon_descr after export (29 Thailand descriptions,1 Guinea bird description); every other cell in every worksheet was asserted identical before and after that metadata edit. JSON non-taxonomy fields match the original backups exactly. All other units and algorithm/Jensen calculations were preserved.
