# Retrospective evidence review: LME050, LME003 and LME014

Reviewed 2026-09-28. This is a review of other agents' retained reports and transformation records, not firsthand extraction work on these three regions. No source extraction, scientific calculation, web taxonomy query or diagnostic was rerun. Only this retrospective was written. Numerical findings below describe the retained evidence; they are not new independent validations.

The comparison to existing instructions uses the already-read ecopath-extraction workflow, source-bundle, parameter-conventions, output-formats, mortality-and-discards and group-taxonomy references, plus the project's prepare-ecopath-model, calculate-regional-ppr and update-ppr-project workflows. Existing rules should be made executable where possible rather than duplicated as more prose.

## 1. Establish source identity before assigning a model year

**Evidence.** LME050 retains two parameter tables, 1985 and 2013, but only one published diet matrix. Its caption covers both years while the article explicitly describes different diets. Embedded supplement images also conflict with final basic inputs. LME014's PAT-2023 folder contains a 2024 publication and a 2020 native model. Its 35-group published diet, 36-group native model and 45-row initial-parameter table do not describe interchangeable final inputs. Ocampo Reinaldo's 1970 Ecopath baseline is distinct from the 1970–2009 dynamic simulation.

**Existing rule:** inventory distinct models, periods and source authority; retain conflicts. **Gap:** a completed extraction can still be described too confidently as recovery of an original model when its period-specific identity is unresolved.

**Proposed clause:** “Maintain a source-to-variant crosswalk containing group roster, period, input/output status and diet version. When a shared table conflicts with period-specific prose, label each result a tabulated reconstruction with unresolved identity; do not silently swap prey, merge group structures, or promote initial parameters into another final model.”

Evidence: [LME050 source report](../../../regions/LME_050/models/50_502013_Coastal_Kyoto_Inoue_(2013)/REPORT.md); [native PAT source report](../../../regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native__source/extracted_tables/evidence/source_report.md); [Ocampo source report](../../../regions/LME/LME_014/papers/LME014-OcampoReinaldo-2016/models/OcampoReinaldo2016_SanMatiasGulf_1970/extracted_tables/evidence/source_report.md).

## 2. Cross-check identifiers, names and parameter signatures

**Evidence.** LME003's parameters CSV reverses Shelf/Slope rockfish names relative to groupinfo and the manuscript; the retained extraction reconciled identities through parameter signatures, groupinfo and the printed table. LME050's supplementary Sole/Dragonet numbering differs from the main table, and Amberjack/Yellowtail requires an explicit alias. Native PAT uses Sequence for order, not Access GroupID.

**Existing rule:** establish group identities and table layout first. **Operational improvement:** one identity key alone cannot settle contradictory source labels.

**Proposed clause:** “Retain native IDs, ordering fields, source names and a crosswalk. Where they conflict, verify identity against at least one independent parameter or membership source. Never resolve a name/number discrepancy by positional alignment alone.”

Evidence: [LME003 extraction report](../../../regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014__source/extracted_tables/REPORT.md); LME050 and PAT source reports above.

## 3. Interpret sentinels and placeholders using author definitions or code

**Evidence.** LME003's source -1 values indicate unknown B/EE inputs to solve. Its GCE=0 field is an unused placeholder; author code calculates PB/QB. Treating these as negative observed biomass or zero gross efficiency would misrepresent the model. The publisher and author diets matched in 8,742 cells, repeated parameters in 372 cells, and 837 printed parameter/CV cells agreed at printed precision.

**Existing rule:** preserve missing versus zero; inspect author scripts as evidence. **Gap:** sentinel meanings need an explicit field-level audit before generic import.

**Proposed clause:** “Record sentinel and placeholder semantics separately for every source field. Confirm whether zero or a negative value is an observation, unresolved input or unused code placeholder. Cross-check duplicate tables by group identity and printed precision; disagreement triggers review rather than averaging.”

Evidence: [LME003 extraction report](../../../regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014__source/extracted_tables/REPORT.md).

## 4. Solve coupled unknowns before interpreting a default-loader failure

**Evidence.** LME003 independently solved 26 unknown B and 66 unknown living EEs, checking an equivalent reduced system; retained production residual was 2.84e-14. Native PAT solved 13 unknown living/producer biomasses with habitat basis and Kingclip immigration preserved; the retained matrix residual was 1.13e-14 and solved B reproduced printed outputs. An earlier PAT loader run replaced unresolved B with 1 and returned FAIL; that run does not diagnose the same state as the audited coupled reconstruction.

**Existing rule:** canonical unknowns remain unknown; defaults/completion must be documented. **Gap:** the workflow needs a decision gate against silently feeding missing biological biomass into a placeholder default.

**Proposed clause:** “Before calculator initialization, enumerate missing biological B/PB/QB/EE. If the source equations determine them, solve the coupled system in a separate computational input, verify residuals and admissibility, and cross-check published outputs. Never treat a loader's B=1 placeholder as a biological reconstruction. Preserve unresolved systems as blocked.”

This clause must distinguish the algebraically determined source model from a free balancing adjustment; a small residual alone does not justify choosing unspecified biological inputs.

Evidence: [LME003 staging transformations](../../../regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014__source/results/diagnostics/staging_transformations.json); [PAT selection provenance](../../../regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native__source/extracted_tables/evidence/selection_20260928/selection_provenance.json); [PAT selection report](../../../regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native__source/extracted_tables/evidence/selection_report.md).

## 5. Validate equation scope and units before trusting a helper verdict

**Evidence.** The PAT reports identify habitat-area versus model-area biomass and omitted immigration as reasons the standalone eight-table checker can disagree with the independent native audit. Ocampo's juvenile-hake conditional EE is approximately 43.539, but the flattened workflow omits multistanza maturation transfers. Its report appropriately does not diagnose the discrepancy uniquely as a source typo. The incipient-fishing effort statement is not a group catch table or a valid automatic catch multiplier.

**Existing rule:** units, mortality rates/flows, unknown BA and source limitations must be explicit. **Gap:** helper applicability is insufficiently visible before its verdict is presented.

**Proposed clause:** “For each balance checker, declare supported biomass basis, migration, fisheries returns and multistanza transfers. Treat omitted terms as limitations of the check. Use exact source cells and conditional residuals to locate concerns, not to manufacture corrections or equate effort with catch.”

Evidence: PAT and Ocampo source reports linked above.

## 6. Distinguish source detritus accounting from completed calculator accounting

**Evidence.** LME003's author code routes unused production to one pool but omits egestion. The calculator adds GS=0.2 egestion, changes detritus inflow from approximately 2534.09145 to 3090.05775, and forces detritus EE to 1. Native PAT has separate natural-mortality fate and fleet-discard fate tables. Both fleets route discards to Detritus, while consumers eat the separate Discards pool; the loader omits explicit fleet supply and derives negative Discards accumulation despite source BA=0.

**Existing rule:** mortality-and-discards already requires these distinctions. **Operational gap:** a blanket “defaults applied” note is inadequate to explain a balanced result.

**Proposed clause:** “Retain before/after tables for every routing, egestion, detritus EE, import and BA transformation. Preserve native fleet-return tables even when the interchange format cannot encode them. State which physical flows entered the completed budget and which were omitted; successful balance does not certify the original routing.”

Evidence: [LME003 transformation ledger](../../../regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014__source/results/diagnostics/staging_transformations.json); [PAT selection report](../../../regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native__source/extracted_tables/evidence/selection_report.md).

## 7. Promote the exact audited computational state, not merely its model name

**Evidence.** PAT selection provenance records identical hashes for the diagnostic input and selected computational input. Its selected groups reproduced 777 previously audited numeric cells. LME003's selected calculations reproduced the prior full diagnostic reports at 1e-12 tolerance. LME050's diagnostic record uses materially different choices—underdetermined completion, normalization and nonzero-completed BA—so a default rerun could produce another state.

**Existing rule:** provenance, freshness and supported regional stages are required. **Gap:** selected execution needs a stable configuration contract alongside the canonical source ID.

**Proposed clause:** “A selection records canonical source hash, computational-input hash, exact loader settings, code version and an executable bounded entry point. Before publishing coefficients, compare the loaded group state and requested direct diagnostic returns to the reviewed state. A changed setting constitutes a new computation, not automatic reproduction.”

Evidence: PAT provenance and selection report above; [LME003 selected report](../../../regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014/extracted_tables/evidence/SELECTED_REGIONAL_REPORT.md); [LME050 diagnostic provenance](../../../regions/LME_050/models/50_502013_Coastal_Kyoto_Inoue_(2013)/evidence/diagnostic_provenance.json).

## 8. Treat format validation and roundtrip checks as distinct from source admission

**Evidence.** LME003's validator rejects authentic apostrophes in group labels as quote characters. PAT and LME050 reconstruction audits expose lost fleet detail, missing P/Q/metadata, or unknown diets/routing displayed as zeros. LME050's converter normalization/defaults were reversed with a field-level ledger; the canonical source matrix remains unchanged.

**Existing rule:** exact labels, roundtrip validation and missing-value fidelity. **Implementation gap:** blanket quote rejection and a successful converter exit do not establish fidelity.

**Proposed clause:** “Classify each validator finding as source issue, serialization defect or checker limitation. Do not rename authentic taxa to satisfy a false-positive quote check. Compare every scientifically relevant field and blank/zero state across conversion; label a lossy reconstructed workbook as a view, not a source replacement.”

Evidence: [LME003 extraction report](../../../regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014__source/extracted_tables/REPORT.md); PAT source report; [LME050 roundtrip audit](../../../regions/LME_050/models/50_502013_Coastal_Kyoto_Inoue_(2013)/evidence/ROUNDTRIP_VERIFICATION.json).

## 9. Keep direct diagnostics concise while retaining complete scientific provenance

**Evidence.** These projects retain only the requested GE, TE and With Egestion direct reports, separate from extraction/source caveats. A common WARN outcome does not mean identical qualifications: zero EE, near-zero TE and loader-completed balance need method-specific interpretation. Ocampo's zero loaded source catch does not establish zero historical catch or a usable coefficient.

**Existing rule:** retain full diagnostics and explicit unavailable outcomes. **Gap/conflict:** broad default report/Monte Carlo inventories should not override the user's narrow diagnostic request.

**Proposed clause:** “The diagnostic report contains requested `diagnose_sppr(short=False, flat=False)` returns or exact not-run/exception records only. Store source caveats and transformation analysis separately. Preserve method-specific WARN/FAIL outcomes, all biological groups including unfished groups, and computational settings. Do not infer one method's validity from another's warning.”

No global option or Monte Carlo should be added merely because an older general workflow lists them.

## 10. Explain high PPR using coefficients, catch and feedback separately

**Evidence.** LME050's saved-result comparison found finite, nonnegative GE coefficients in both years. Stingray's all-source coefficients of 80.82/88.47 follow from low GE and prey costs, not unstable feedback. Changes in an unfished Goby group affect predator coefficients. The larger 1985 catch-weighted footprint is mainly a catch difference; it does not establish inferior coefficients. PP-only and all-source extrema also differ.

**Existing rule:** inspect negative coefficients/convergence. **New analysis clause:** “When comparing PPR magnitudes, separate coefficient changes, catch quantities/composition, source scope and feedback amplification. Review all groups, not only caught groups. A high positive coefficient or lower inter-year value is not by itself an accuracy criterion; do not impose an unsupported universal cutoff.”

Evidence: [LME050 GE comparison](../../../common_reference_data/provenance/source_paths.csv).

## 11. Improve mappings through source-supported aggregation, not exact-name restriction alone

**Evidence.** LME050's 19/253 resolved labels initially covered 25.05% of 2019 catch. The retrospective mapping review identifies a missed opportunity: Scomber members share one modeled Mackerel group, so unknown proportions within that supported pool do not require between-group weights. Auxis has the same pattern. By contrast, Teuthida spans groups with different coefficients and needs supported allocation. Source S3 gives representative taxa, not an exhaustive roster; however, broad guild labels do not automatically validate every related taxon's rates or geographic fit.

**Existing rule:** taxonomy workflow already recognizes group definitions, containment, synonyms and evidence-based weights. **Compliance improvement:** exact-only matching should be labeled a first pass, not a final ecological coverage limit.

**Proposed clause:** “After exact/synonym matching, review high-tonnage unresolved labels for supported aliases and containment. If all supported constituent taxa map to the same model group, within-pool proportions are unnecessary. If they map to different groups, require a supported candidate set and weights. Preserve uncertainty in representative-versus-exhaustive membership.”

The same review found no additional unambiguous accepted-name matches among unresolved labels after checking 70 representative binomials. This argues for targeted ecological review rather than promising that more synonym queries will solve structural gaps.

Evidence: [LME050 matching improvement review](../../../common_reference_data/provenance/source_paths.csv).

## 12. Report catch coverage, spatial applicability and selection as separate dimensions

**Evidence.** LME050's 253 records include higher taxa and unidentified labels, not 253 species. A 2,230-km² Kyoto model lacks documented counterparts for major whole-LME stocks. LME014's selected Falkland model covers 29/250 labels but 65.31% of 2019 catch; LME003 covers 147/349 and 76.51%. Neither a model's selection nor its computed WARN status implies full regional catch support. Historical calculations hold selected model coefficients fixed; they are not annual reconstructed food webs.

**Existing rule:** explicit tonnage coverage, unresolved mappings, spatial limitations and source ownership. **Operational improvement:** make these dimensions mandatory in the selection handoff.

**Proposed clause:** “Report resolved labels and covered tonnes by catch basis and period, list the largest unsupported catches, and label partial PPR totals accordingly. Distinguish geographic overlap from taxonomic catch coverage. State when fixed-period coefficients are applied across historical catches. Never meet a numerical coverage target by silently broadening membership.”

Evidence: LME050 matching review, LME003 selected report and PAT selected report above.

## 13. Keep historical reports readable without confusing current status

**Evidence.** Extraction snapshots say 'not selected'; later selected reports explicitly identify the user's choice and current computational input. Some provenance records correctly retain the status at creation rather than being current project dashboards.

**Existing rule:** regional Overview owns selection; source evidence is preserved. **Small documentation gap:** readers need an obvious current-state pointer.

**Proposed clause:** “Timestamp stage reports and link the current selection/calculation report from earlier extraction summaries without rewriting source results. Treat regional Overview as current selection authority; frozen provenance describes its recorded event.”

## Priorities for an actual skill revision

1. Add a pre-loader missing-biological-input gate and a coupled-equation completion checklist.
2. Add semantic conversion/roundtrip checks that include unknowns, P/Q, habitat basis, migration and fleet returns.
3. Require exact diagnostic-to-selected-state reproduction through input hashes and loader configuration.
4. Make high-tonnage alias/containment review a required second matching pass, with explicit same-group versus multi-group logic.
5. Add a PPR comparison checklist separating catch, coefficient, scope and feedback effects.

Many remaining lessons reinforce existing rules. They should become targeted checks or concrete examples rather than an additional broad approval process. These proposals do not authorize changes to any source model, scientific engine, selected mapping or skill file.
