# Baltic Proper Rpath port snapshot (base-year lineage 2004)

Source: deposited BalticSeaModel.RData and BalticSeaModel_config.R; ICES WGSAM 2016 Annex 3 provides independently reviewed context, not an equivalent native input set. Extracted 14 October 2026. Region: LME_023. Groups: 22 (21 living, 1 detritus). Fleets: ACT0018, ACT1824, ACT2440, PAS0012, PAS1218, PAS1840, PEL0018, PEL1824, PEL2440, PEL40OO.

## Source tables

The native Rpath.parameters model has 32 rows and 31 fields: the first 22 biological/detritus rows form canonical groups, the remaining 10 gear rows define fleets. Biomass, PB, QB, EE, ProdCons, Unassim, DetInput and BioAcc map to their unchanged EwE import columns. Rpath diet has 23 prey/import rows and 21 living columns; the 20 consumer columns are imported, while producer nulls remain in a native companion. Source order and group names are unchanged. All cells have native-object row/column locators.

Only missing native parameter values were extracted from existing deposited Rpath.model outputs; explicit parameter roles identify those values as model_estimated. This is extraction of source outputs, not a new solve. Raw input masks, all static native output fields, the full parameter grid and stanza data remain separately retained. Five TL cells rounded through Excel were restored to the deposited native text, with before/after evidence in model.json source_fidelity.restorations.

Coordinate-based report evidence is in source_review/: PDF pages 48, 51–53, 55, 58–60, 63–64 and 85, with words/bounds and text. Renders of pages 55, 59 and 60 were inspected to confirm material sprat/herring/plankton version differences. Report and port values are compared in ICES_report_comparison.csv; report values were not substituted into the port. Exact port fitted calendar range is unverified; config simulation horizon 500 is not a fitted period. Bauer 2019 PDF p. 3 provides later-model lineage context only.

## Biomass accumulation

Native BioAcc is explicit: GreySeal 0.00036 t/km²/year, all remaining 21 groups zero. ICES report Table 1 PDF p. 52 gives GreySeal BA rate 0.06/year, equivalent for B=0.006. The rate column remains blank for every group; conversion arithmetic does not become an observed source parameter.

## Values from prose

No numerical biological import value was inferred from qualitative prose. Prices/costs described on ICES PDF p. 64 refer to unavailable detailed input data. Stanza published K, adult start months and Wmat/Winf on PDF p. 63 support the native stanza identities; precise deposited floating values remain in stanza companions. Contextual native period/footprint come from PDF p. 48.

## Conventions applied

Missing source cells are retained with blank import cells and canonical -9999. Known Rpath whole-model biomass density is retained without habitat conversion; habitat fraction remains unavailable. No new biological default, diet normalization, parameter tuning, geographical rescaling or catch substitution was applied. Gear rows are fleets, not functional groups. Native structural zeros remain source values.

## Deliberate blanks

Habitat fraction, migration, numeric off-vessel prices and costs, external detritus fate, BA rate and native diet producer nulls remain unavailable. Source stanza equations are retained as evidence, not claimed as implemented by the generic Ecopath checker. The native accepted EwE database and its detailed Ecopath workbook are missing. Canonical field roles separate extracted model estimates from supplied source inputs.

## Unresolved and flagged

Material published-native/port differences and precise port calendar identity are unresolved. The accepted EwE key-run designation applies to the native setup, not this port. ModelData loses producer routing and changes detritus self-routing; see LOADER_CHECK.json. Full static source tables are preserved despite these runtime limitations. Simulation objects stored in RData are pre-existing source contents; none were regenerated, used as observational data or run here. Exact source bytes remain the ultimate evidence for dynamics outside this static snapshot.

## Validation

All 460 diet/import cells, 440 fleet cells, 22 routing cells and 198 scalar parameter cells match source staging and canonical JSON exactly. Source sums are retained in DIET_SOURCE_SUMS.json without normalization. Maintained import validator: 1 error, 0 warnings, native detritus row fate sum zero against required one. This is preserved source structure, not a repaired model. Roundtrip: all 8 standard tables plus 17 companion tables, 30,122 cells; numeric/missing-mask match true; exact numeric bit-text match false due to spreadsheet floats; max difference 4e-16. No inference of research approval follows.

## Mass balance

Standalone physical checker: 0 errors, 3 warnings, 22 notes. Converter check: BALANCED within its stated equations, 0 errors, 0 indeterminate, 2 warnings. Largest EE recomputation difference is much less than 0.05. Low P/Q warnings concern GreySeal and FishFeedingBirds; standalone zero-Q/B phytoplankton warning is a basal-row applicability issue. Native BA is included; migration unavailable. Detritus inflow/consumption checks are indicative because export is not separated. Detailed retained outputs: MASS_BALANCE.md, physical_massbalance.txt. No ecological correction was made.

## Execution limits

ModelData source loading succeeded, 22 source groups plus synthetic import. No PPRCalculator construction, scientific diagnostics, R execution, Ecosim/SPPR calculation, Monte Carlo, selection refresh or publication occurred. This is a source snapshot and extraction handoff only. See ../MODEL_PROFILE.md, ../../model_notes.md and evidence_index.json.
