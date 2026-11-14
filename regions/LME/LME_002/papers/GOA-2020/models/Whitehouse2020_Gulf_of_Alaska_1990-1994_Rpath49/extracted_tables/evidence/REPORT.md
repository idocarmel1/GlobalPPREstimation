# Gulf of Alaska (1990–1994), official Rpath49 aggregate

**Source:** Whitehouse, G.A. and Aydin, K.Y. (2020). Assessing the sensitivity of three Alaska marine food webs to perturbations: an example of Ecosim simulations using Rpath. Ecological Modelling 429, 109074. https://doi.org/10.1016/j.ecolmodel.2020.109074
**LME:**2 Gulf of Alaska. **Model ID:**Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49. **Extracted:**2026-11-14.
**Groups:**49 (47living including primary producer,2detritus). **Fleet:**Fishery/Subsistence.

## Source tables

The numerical source is the official NOAA-EDAB/Rpath repository commit `fe63f6d370d942ff1786f4d649e432fbfb85f81b`. Original CSV literals are read with Python's CSV parser; no PDF OCR, image digitization or manual numerical transcription was used. `Ecosense_GOA_base.csv` contains50 rows and14 columns: Group,Type,Biomass,PB,QB,EE,ProdCons,BioAcc,Unassim,DetInput,PelDetFate,BenthDetFate,F_Fishery,D_Fishery. The fleet row has Type3 and remains in companions, not as a biological group. Biomass is t/km²; PB/QB are year⁻¹; BA, detritus import and catch flows are t/km²/year; efficiencies, diets and fates are dimensionless.

`Ecosense_GOA_diet.csv` contains49 prey rows and an Import row, with47 biological columns (46consumers and nonfeeding primary production). Standard Diet_composition.csv has49prey×46consumer cells plusImport/Sum/(1−Sum). The complete47-column source table remains in `Rpath_diet_native.csv`. The native source is sparse: blank diet cells are NA, not literal zeros. Native Rpath runtime explicitly replaces diet NA with0; this action has not been written back into the extraction.

`Ecosense_GOA_pedigree.csv` is retained in full. Its numeric input values have not been mislabeled as original1–8 pedigree grades. The exact builder `Rpath_unbalanced_data.R` names these three CSVs as inputs to Ecosense.GOA. The RDA object and source/reader code are retained for provenance; no RDA decode or native balance execution was performed.

## Biomass accumulation

Native BioAcc explicitly supplies all49biological values. Walleye pollock(group12)−1.35, Pelagic forage fish(group14)−0.11 and Other demersals(group18)−0.002 t/km²/year are negative; other biological groups are0. No steady-state assumption overrides these source values. Pelagic forage fish includes Pacific herring; Other demersals includes greenlings, per2020Table1. BA rate is not computed or supplied.

## Values from prose

Area291,840km² and140°W–170°W (§2.2.3,p4); official documentation identifies the model as1990s and aggregated from Aydin2007; exact1990–1994 period is inherited from that base model. Publication available online25May2020. §2.2.4(pp4–7) describes sum of biomass/catch and biomass-weighted PB,QB,DC; no reconstruction of these aggregate values was used as an input. Table1 crosswalk was transcribed from indexed PDF text and awaits visual review because download/screenshot access failed.

## Conventions applied

No biological parameter convention, zero completion, normalization, EE/B solve or source repair. Whole-model-area biomass/BA metadata is supported by the native area-standardized model and source units. The one import-only label alias for group31 is reversible; canonical scientific identity is original. The complete native parameter companion adds exact duplicate destination-name routing columns solely for the supported fleet-return loader schema. Native original columns and separate verbatim companion remain present. `--dir-name aggregated_stage` was used for collision-free temporary staging in this shared regional run.

## Deliberate blanks

All49 EE values; all ProdCons values; detritus B(group48/49); nonconsumer QB; habitat fractions; TL; Z; other mortality; source-unspecified detritus export; BA rate; and raw diet NA cells remain unknown. All three native CSVs, the native object documentation, builder, parameter reader and balance-code field semantics were inspected. Rpath would solve missing EE/DET B when balanced; no such solve is part of this extraction. Do not interpret canonical−9999 or import blanks as measured zeros.

## Unresolved and flagged

This is an official aggregated source, not recovery of the exact133group native source. The138original-group count in2020 does not match133published biological rows, and no full version equivalence is asserted. Group names in Table1 are coarser than west/central Steller source labels. The illustrative B/PB/QB comparisons use rounded original published values and cannot prove exact native equivalence. Full original native recovery search and rejected CGOA/EBS/ECOTRAN candidates are recorded separately in the regional recovery evidence.

## Validation

Maintained validate.py returned two errors (native detritus fate0+0 rows48/49) and one warning (49missing TL). These source states were retained. Consumer known-entry diet sums range 0.999999780 to 1.000000221; all46columns include raw blank cells, so complete canonical source sums remain unknown. No diet normalization occurred. Fleet routing sums1; biological source DET routing rows sum0, with unknown export.

All 746 native-to-canonical checks passed, including group labels, type codes, parameter literal/missing masks, catches, fates, every represented consumer diet cell, source native table companions and original source hashes. Standard/companion workbook reconstruction checked9190cells; numeric and missing-mask match=True, exact match=True, max numeric difference=0. Exact group31 import name differs intentionally via explicit crosswalk; the standard reconstruction retains the literal alias.

## Mass balance

The maintained converter's source checker ran unchanged. It reported **0errors,46indeterminate,11warnings,1note**; full outcomes are inMASS_BALANCE.md. This is not evidence of a balanced model: unknown EE and sparse diet inputs prevent complete source checking. Its producer input-count warning and ten marine-mammal/seabird P/Q warnings are retained, without repairs. No PPRCalculator or native Rpath balance was run, and no SPPR/regional arithmetic was computed.

## Source-to-loader check

ModelData schema admission=True. It appends a synthetic diet_import group and performs supported runtime accounting. Native unknown EE and DET biomass remain source unknowns. The full source-facing fields, loader parameter view, unavailable counts and fleet-routing metadata are retained in loader_schema_check.json and loader_parameter_view.csv. Admission does not establish numerical readiness or researcher approval. No source/default replacement was promoted from the loaded view.

The source_to_loader_ledger.json audit compares 490 scalar fields and 2,254 diet cells. All source diet values and missing masks match the loaded matrix. The 47 scalar differences are source-blank DetInput values represented as runtime 0, consistent with explicit native Rpath runtime behavior. All 49 unknown EE values and both unknown detritus biomasses remain unknown. Runtime diet and fate matrices are separate evidence CSVs. The generated mass-balance check's generic “BA unknown” heading does not describe this model's BA: all 49 BA values are known, and its listed indeterminate reasons concern unknown diet cells.


## Candidate taxonomy handoff

MODEL_PROFILE.md is retained beside the extracted_tables directory. Candidate Taxonomy.xlsx has one sheet and exactly the columns seq, group_name, taxon_descr, with all 49 native biological groups. It preserves the group 31 native comma punctuation. Descriptions are source functional-group constituents from the retained 2020 Table 1 evidence, not newly resolved species taxonomy. Visual verification and taxonomic authority are pending. The canonical JSON retains null taxon_descr and its previous hash. The candidate workbook is independently checked and has not changed the eight-import/seven-companion reconstruction.
