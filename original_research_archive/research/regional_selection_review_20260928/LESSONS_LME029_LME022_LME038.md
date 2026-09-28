# Retrospective lessons: LME029, LME022 and LME038

Review date: 28 September 2026. Reviewer: LME037 source/extraction agent.

This is a review of other agents' retained reports and transformation records, **not firsthand execution of these three regional pipelines**. No model, diagnostic, source extraction or scientific calculation was rerun. Reported numerical values below are attributed to saved evidence. Historical reports describe the state when written; this review does not certify the current central workbook or override later selection decisions.

Only this retrospective file was written. Central workbooks, regional artifacts, scientific code and skills were not edited.

## Scope of the existing-rule comparison

I checked the installed `ecopath-extraction` skill and its source-bundle, workflow, parameter-convention, table-layout, output-format, Ecopath-model and mortality/discard references. They already require preserving unknowns/source precision, explicit parameter mapping, source conflict records, independent model identities, no silent normalization, prose/footnote sweeps, round-trip artifacts and separation of experiments from source extraction. They also already distinguish Z from P/B unless the source states their equivalence.

“Gap” below means a missing operational detail or useful strengthening in that extraction contract. Downstream integration recommendations should also be checked against the combined paper-to-PPR skill before inserting duplicate instructions. Existing safeguards should be enforced, not presented as newly invented rules.

## LME029: source semantics before numerical repair

### 1. Multi-stanza mortality, production and accumulation need an explicit compatibility check

**Evidence reviewed.** BEN-2020 has one 1978 static baseline, not separate models for every year of the 1978–2015 Ecosim fitting period. Table 2 has Z and P/B as distinct fields. Supplement S1 supplies eight missing stanza P/B values, while deep-water hake P/B remains absent. S1 gives sardine stock BA/B = 0.3/year. Applying this stock rate to juvenile and adult groups as ordinary additive BA yields recomputed EE approximately 1.200 and 1.219, against printed 0.984 and 0.979. The report identifies a possible difference between native multi-stanza accounting and this calculator's equations; it does not establish that the authors' native model failed. See [extraction report][29-report].

**Existing rule:** do not silently copy Z to P/B; retain source BA in its published form; do not use balance-check suggestions as source values.

**Proposed clause:** “For multi-stanza models, inventory stanza links, transition ages, growth parameters and stock-level accumulation conventions. State which native equations the target calculator implements. Do not treat a stock-level BA/B statement as independent measured BA for every stanza without an explicit representation note. Diagnose translation incompatibility before proposing biological corrections.”

### 2. Algebraic completion must retain both its equation and source precision limits

**Evidence reviewed.** Separate diagnostic staging fills only two unknown P/B cells: small M. paradoxus, 0.125 × 16.030 = 2.00375; large M. paradoxus, 0.170 × 4.700 = 0.799. Canonical P/B remains unknown. These are derived from rounded P/Q and Q/B, not published P/B cells or tuned repairs. The staging also declares GS, BA, migration and single-detritus defaults. See [staging transformations][29-staging].

**Existing rule:** distinguish source data, derived values and defaults; preserve missing canonical values.

**Proposed clause:** “Every diagnostic completion must include group, field, old value, new value, equation, source operands and precision caveat in a machine-readable transformation ledger. Reject accidental source-file replacement. Compare the resulting staging file against canonical input and allow only the recorded differences.”

### 3. Conditional prose must not become an undocumented classification algorithm

**Evidence reviewed.** The supplement specifies GS 0.35 for zooplanktivorous fish, 0.30 for mixed zooplankton/fish diets and 0.20 for heavily predatory groups, without a complete membership list or mixed-diet thresholds. The extraction assigns 0.35 only to five fish groups with entirely zooplankton diets; other GS values remain unknown in canonical input. It also preserves a genuine taxonomy conflict: Panulirus homarus in one source location versus Palinurus gilchristi in another. See [extraction report][29-report].

**Existing rule:** sweep prose and preserve source conflicts.

**Proposed clause:** “For conditional parameter statements, record the stated condition, group assignment evidence and any unstated threshold. Label classification-derived assignments distinctly from explicit per-group values. Do not invent a mixed-diet cutoff or merge conflicting taxa as presumed synonyms.”

### 4. Join tables by verified identities, not convenient row numbers

**Evidence reviewed.** Main Table 1 has a different group order from Table 2/S4. Canonical numbering follows S4. The two catch-table blocks were joined by group identity, with 48 fleet sums checked against printed totals. Diet asterisks mean 0.0001. Rotated fleet headers required rendered-page inspection. See [extraction report][29-report].

**Existing rule:** fix group numbering, map headers and visually verify unfamiliar layouts.

**Proposed clause:** “Create a source-table-to-canonical group crosswalk whenever ordering differs. Validate continued-table joins using both identities and published totals. Capture each table's symbol legend before converting asterisks, dashes or inequalities.” This is chiefly an enforcement improvement.

### 5. A small total budget gap can coexist with material input failure

**Evidence reviewed.** All three direct methods return FAIL. GE's PP-budget relative gap is about 0.0004853 and With Egestion's about 0.0004255, but the maximum production residual is approximately 0.23961. TE additionally has a PP-budget gap around 0.09618. See [saved results][29-results] and [full direct returns][29-direct].

**Proposed downstream clause:** “Keep overall diagnostic status, model-input residuals, divergence and total-flow budget results separate. Never promote a candidate because one balance component says OK, and never erase a scientific FAIL because extraction/serialization verification passed.”

## LME022: model identity and calculation-layer attribution

### 6. A repository record citing a paper is a separate numerical variant until compared

**Evidence reviewed.** Printed North Sea Table 3.3 and EcoBase457 have 68 groups, but the retained comparison finds 205 unequal numerical fields. Gelatinous zooplankton Q/B is 0.18 in print versus 6.35111141 in the repository variant; BA, catches and precision also differ. Repository exports aggregate catch and do not retain the original 12-fleet ledger. The source record period is 1991–1992 although the local filename says 1991. See [regional report][22-report] and [repository variant report][22-repository].

**Existing rule:** distinguish model versions and preserve conflicting authoritative sources.

**Proposed clause:** “Treat article tables and repository/native exports as separate candidate versions until group identities, parameter fields, diets and fisheries have been compared. A matching citation is lineage evidence, not numerical equivalence. Preserve accession, source period, file naming and publication year separately. Do not label a repository replacement as a correction to the printed model.”

### 7. Check accounting layers before blaming source biology

**Evidence reviewed.** EcoBase457 passes the retained independent source mass-balance check but fails the engine diagnostics. At Discards group 68, stored production is 0.2981897135 and recomputed production is −99.7018102865; source detritus_import and immigration are both 100. The loader ledger also shows group 68 EE 0 → 1 and BA 0 → 99.53394068567071. Cause remains unresolved. This review has not run a causal experiment. See [repository report][22-repository], [extraction audit][22-audit] and [loader transformations][22-loader].

**Existing rule:** distinguish source facts, importer omissions and experimental assumptions.

**Proposed clause:** “When an independent source check and loaded-model diagnosis disagree, trace the worst residual through raw fields, converter output, loaded state and diagnostic equations. Check detritus import, migration, export and accumulation conventions explicitly. Report the discrepancy as evidence; do not call an apparent duplicate field the cause until an isolated test establishes it.”

### 8. Preserve severe table defects; normalization is not recovery of missing data

**Evidence reviewed.** The printed North Sea diet matrix has 19 consumer sums more than 0.01 from unity, including juvenile cod 0.562, adult saithe 1.530 and blue whiting 0.387. Some continuation values appear repeated. Printed gelatinous P/B 2.858 and Q/B 0.18 imply P/Q 15.8778, conflicting with prose P/Q 0.45. Coordinates and page images were retained. Loader normalization produced numbers but did not repair the source. See [regional report][22-report].

**Existing rule:** never normalize source data merely to pass validation; retain conflicting evidence.

**Proposed clause:** “Report the size and location of diet deficits/excesses before describing them as rounding. Inspect continuation blocks, import rows and source images first. A normalized computational variant must not be described as recovered published diet, especially for material deficits or duplicated cells.”

### 9. Test unfished groups and distinguish preference from method validity

**Evidence reviewed.** The preferred 1991–1995 Scotland model has GE/With Egestion OK in the saved completed run but TE FAIL, living spectral radius approximately 1.11278 and negative seabird SPPR despite zero seabird catch. The user's recorded reason is ‘least SPPR failures’. The historical report records preference without claiming production adoption or universal method validity. See [regional report][22-report].

**Proposed downstream clause:** “Screen all modeled biological groups, including zero-catch groups. Preserve method-specific restrictions alongside a chosen/preferred model and the user's exact rationale. A catch-weighted total can hide an invalid unfished coefficient.”

The same report records timeouts as unavailable, not zero and not a scientific pass. A zero-group EcoBase628 record is evidence that its retrieved payload is unusable, not an extractable 1973 model. These are useful explicit availability-state examples.

## LME038: authorized variants, reload equivalence and mapping limits

### 10. Resolve paper identity from the document, not its directory label

**Evidence reviewed.** The folder BUCHARY-1991 contains an April 1999 thesis; 1991 is the earlier degree year. Its association with the INDO-1999 placeholder was documented as an inference, while equivalence to EcoBase410 remained unverified. The earlier 36% geographic estimate was not treated as measured overlap. See [preselection report][38-before].

**Existing rule:** confirm source identity and distinguish verified evidence from inherited references.

**Proposed clause:** “Validate title, degree/publication year, author and study against the actual title page. Retain folder aliases and legacy catalogue claims as history. Do not infer repository-model equivalence or spatial coverage from a bibliographic reconciliation.”

### 11. Freeze a user-authorized computed variant and verify its reload

**Evidence reviewed.** Buchary's Macrozoobenthos diet sums 0.660; the source detritus dash is not evidence of the missing 0.340. The selected derived model scales existing fractions by 1/0.660 and stores all 28 signed loader-completed BA values. Seventeen BA values are negative, including both rounding-scale and material residuals; detritus BA is 1761.423470522 t/km²/year. These are computed accounting completions, not demonstrated stock trends. The source remains unchanged. Reload comparison found no differences across 29 rows and 18 state/flow fields at relative 1e-10 and absolute 1e-9 tolerance. See [selection report][38-selected], [exact changes][38-changes] and [reload validation][38-reload].

**Existing rule:** preserve source canonical data and separate explicit experimental assumptions.

**Proposed clause:** “When the user authorizes normalization or completed BA, create a distinctly identified derived model with source/derived hashes and every changed field. Preserve signs and small residuals. Reload the saved derived file and compare its full state and flows to the intended reference; matching filenames or successful loading is insufficient. Do not infer ecological trends from residual BA or attribute all changes to normalization without an isolating experiment.”

This is not permission to normalize other models. The authorization is specific to the selected variant. Generic statements that negative BA signifies decline should be qualified: that ecological interpretation applies to source-supported accumulation, not automatically to a solver's residual.

### 12. Preserve bounds and stop instead of guessing a decimal point

**Evidence reviewed.** Nurhakim Table 3 prints 217 in one diet cell, giving a 217.78 subtotal. Other diets cannot close within their reported censored bounds; 29 diet entries and producer EE are censored. The retained report does not replace 217 with 0.217 or borrow predecessor fractions. Downstream diagnostics are NOT RUN, with no invented zero counts or Monte Carlo outcomes. See [preselection report][38-before].

**Existing rule:** retain source precision, unknowns and conflicts.

**Proposed clause:** “Retain inequality bounds and compute feasibility only within those bounds when reviewing completeness. Do not impute a likely decimal correction or replace censored input without authority. For unsupported inputs, emit a blocked/NOT_RUN record that names the required corrected data; a complete extraction report does not require an unsupported calculation.”

### 13. Direct diagnostic retention should be independent of the broad production wrapper

**Evidence reviewed.** The selected model's retained direct report contains GE, TE and With Egestion only. A bounded three-option retention verified all saved flattened fields without rerunning the 22-method inventory or Monte Carlo. TE has two distinct warnings: absent detritus recycling matrix and group 27 near-zero TE. Its TE is about 0.00084696 while the living spectral radius is below one; this is not network divergence. See [direct retention record][38-direct] and [selection report][38-selected].

**Proposed downstream clause:** “Provide a bounded direct-diagnostics stage that retains complete method returns, options, warnings and code/input identity independently of annual production and Monte Carlo. Separate local near-zero efficiency from network divergence. A report-formatting task should reuse authoritative retained outputs when adequate; if full fields must be recovered, run only the bounded diagnostic calls and verify common fields.”

For this user/project, the requested set is GE, TE and With Egestion, without global. Do not turn that preference into a universal scientific requirement. Historical 22-method records remain valid evidence of past scope, not the default recipe for every future diagnostic request.

### 14. Taxonomy coverage needs both counts and catch-weighted denominators

**Evidence reviewed.** The selected workflow reports 153/181 resolved taxa, with 2019 landings coverage 96.759% and total-catch coverage 96.671%. It retains 28 unresolved taxa, including Lates calcarifer at roughly 82,097 tonnes of 2019 catch. Source-specific membership can override a broad guild label; stage and coarse-pool allocations have explicit, noncircular proxy bases. See [selection report][38-selected] and [mapping coverage][38-coverage].

**Proposed downstream clause:** “Report resolved/unresolved taxon counts plus catch-tonnage coverage by year and catch basis. Rank unresolved taxa by contribution. Preserve explicit source membership, synonym evidence and allocation weights; distinguish complete taxonomic extraction from complete regional catch matching. Covered-catch PPR must not be labelled all-catch PPR.”

This is a downstream integration recommendation; its novelty should be checked against the combined mapping skill, not inferred solely from the extraction-only skill.

## Cross-region priorities

1. Enforce a source → converter → diagnostic input → loaded state audit, including defaults and overwritten published detritus fields.
2. Add an explicit multi-stanza compatibility checkpoint and classify equation-translation uncertainty separately from source error.
3. Require exact variant identity and a reload comparison when adopting a computed model.
4. Keep transcription success, admission, diagnostic status, user preference/selection and production eligibility as separate states.
5. Preserve direct diagnostics independently of expensive wrappers; distinguish FAIL, WARN, exception, timeout and NOT_RUN.
6. Keep model area, display bounding box, measured region overlap and catch-mapping coverage distinct. LME029's inherited 50%, LME022's inherited 10% and LME038's former 36% were not established polygon intersections in these reports.

The review supports skill clarifications and verification gates, not new numerical repairs. No causal resolution of EcoBase457, native multi-stanza equivalence for BEN-2020, or corrected Nurhakim diet is claimed.

## Evidence index

[29-report]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_029/models/BEN2020_Southern_Benguela_1978/extracted_tables/REPORT.md>
[29-staging]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_029/models/BEN2020_Southern_Benguela_1978/diagnostics/staging_transformations.json>
[29-results]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_029/extraction_review_20260928/results_record.json>
[29-direct]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_029/models/BEN2020_Southern_Benguela_1978/diagnostics/DIRECT_SPPR_REPORT.md>
[22-report]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_022/models/extraction_review_20260928/EXTRACTION_AND_SPPR_REPORT.md>
[22-repository]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_022/models/457_457_North_Sea_(1991)/REPORT.md>
[22-loader]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_022/models/457_457_North_Sea_(1991)/LOADER_TRANSFORMATIONS.csv>
[22-audit]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_022/models/457_457_North_Sea_(1991)/EXTRACTION_AUDIT.json>
[38-before]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_038/models/extraction_review_20260928/EXTRACTION_PRESELECTION_REPORT.md>
[38-selected]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_038/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/SELECTED_MODEL_REPORT.md>
[38-changes]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_038/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/evidence/SOURCE_TO_DERIVED.json>
[38-reload]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_038/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/evidence/DERIVED_RELOAD_VALIDATION.json>
[38-direct]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_038/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/evidence/DIRECT_DIAGNOSTIC_RETENTION.json>
[38-coverage]: <C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/regions/LME_038/models/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/evidence/MAPPING_COVERAGE.json>
