# Extraction pipeline lessons — 28 September 2026

This is a proposed skill revision brief, not an applied skill change. LME024, LME026 and LME037 agents provided fresh retrospectives of their actual work. At the user's request, they then reviewed retained extraction and diagnostic evidence for Griffiths2019, EEZ941/WCP2007, LME050, LME003, LME029, LME014, LME049, LME022 and LME038. Those additional nine reviews are explicitly evidence reviews, not claims of firsthand execution. No model was recalculated for this review.

## Highest-priority changes

1. **Verify every conversion, then audit the loaded model separately.** Compare extraction input → eight import tables → canonical JSON → reconstructed tables, field by field. Include missing-value sentinels, diet import, P/Q, TL, habitat area, BA, routing, fleet identities, landings, discards, group names and taxonomy. Archive raw converter output and record restorations. Then capture all initializer changes in a second before/after ledger with options and engine hashes. Neither a round trip nor successful loading proves source fidelity.
   - LME026 conversion omitted P/Q and represented missing routing as zeros; a reconstructed view omitted BA and fleet/discard detail.
   - LME037 conversion normalized diets and altered precision; the runtime initializer changed detritus EE from 0.44 to 1 and derived BA 682.68614643.
   - LME024 initialization replaced printed detritus accumulation. Source-correct extraction still failed ecological budgets despite 3,628 successful reconstruction checks.

2. **Use distinct completion states.** Report source extraction, constructor admission, diagnostic execution, returned diagnostic status, matching coverage, geographic suitability, selection and annual PPR readiness separately. A selected model can remain blocked or failing. A constructor error means NOT_RUN, not a returned FAIL. Unsupported equations and execution exceptions require their own reasons. Preserve full `diagnose_sppr()` returns, component statuses and strict Boolean balance flags.
   - LME026: constructor blocked; all three methods NOT_RUN.
   - LME024: GE/Egestion converge but FAIL; TE returns FAIL with an unsupported-return equation, without numerical coefficients.
   - LME037: overall WARN and component balance OK coexist with strict balance false.
   - In this project, run only GE, TE and With Egestion, with `short=False, flat=False`; omit global and broad Monte Carlo inventories unless separately requested. This is a project preference, not a universal extraction rule.

3. **Recover missing supplements through verified model lineage.** Search official publisher XML and official repository/API records by exact parent DOI before declaring data unavailable. Verify attachment metadata and any supplied checksum. A predecessor's diet requires explicit model lineage plus a group/parameter crosswalk, not merely equal group counts.
   - LME037 recovered the 2023 supplement through the official Figshare API. Explicit baseline reuse and 191 matching parameter cells supported the 1997 model after the stated habitat conversion.
   - Record publication year, Ecopath baseline, survey period, supplement label and simulation period separately. A dynamic endpoint needs its own realized diet/flow, BA and state data; LME037's 2018 endpoint remains blocked.

4. **Preserve partially known values and their bases.** Read stored spreadsheet numbers rather than displayed rounding, retain formats as evidence, and distinguish blanks, exact zeros and censored values. Keep known discards even where landings are missing; label total removals incomplete. Record whether BA is a rate or flow and whether biomass is per habitat area or whole model area.
   - LME026 fin-whale EE displays 0.00 but is stored as 0.00001; 22 groups lack listed landings although discard information exists.
   - LME037 fleet `0.000*` cells are censored, not exact zero. Published group catch totals can support a documented aggregate representation without claiming exact fleet reconstruction.
   - The LME037 reef-area correction must not be applied twice. LME024's explicitly printed 0.00 bird biomasses must not be replaced by generic positive defaults.

5. **Make detritus and discard experiments explicit.** For any authorized routing experiment, check donor fishery removal, recipient inflow, recycling ancestry and external-export accounting independently. Do not add a returned discard twice. Residual flow needed to close a budget is not recovered source routing. Pooling is a separate derived model with provenance and conservation checks; it is not an automatic response to missing routing.
   - LME024's source-informed routing still left natural-detritus and discard deficits; it did not establish the missing published fate matrix.
   - User-authorized pooling made Watari GE/Egestion calculable, but TE failed. Griffiths pooling still failed all three methods. Pooling alone is no guarantee of validity.

## Targeted practical additions

- **Diet changes and dependencies:** preserve original diets and exact normalization factors; recompute dependent predation and derived parameters from the selected runtime diet. A constructor tolerance change is distinct from normalization. Neither is an unreported source correction.
- **Basal-row troubleshooting:** before assigning a solver exception to biology, inspect nonfeeding basal rows, NaNs and expected basis dimension. Four missing import cells caused LME024's misleading missing-column exception. Any structural-zero convention must identify the exact cells and preserve the original error.
- **Early feasibility screening:** compare known removals with production even when catch is incomplete. Cite exact cells, units and missing-flow assumptions. LME026 fin-whale discards exceeded production under the stated missing-flow assumptions.
- **Group identity and taxonomy:** audit unnumbered aggregate columns before excluding them; retain life-stage identity when species membership is shared. Never fill a missing taxonomy heading from adjacent groups. Separate taxon-count coverage from catch-weighted coverage and from geographic overlap.
- **Windows reliability:** specify UTF-8 for every text/JSON read and write and compare labels after conversion. If LibreOffice is unavailable, installed Word can export a separate PDF hidden and read-only, with guaranteed closure, for visual verification.
- **Report consistency:** regenerate or label reports after canonical source values are restored. A report describing a normalized converter intermediate must not be presented as a report on the restored source matrix.
- **Coordination and registration:** read regional Overview first. Agents deliver metadata patches validated against the current central schema; one coordinator writes Project.xlsx. Preserve candidate preferences and provenance. Regional Overview owns selection, and changing selection archives and clears old model-dependent results before consolidation.

## Lessons added from the nine requested extractions

| Case | Concrete lesson | Proposed workflow addition |
|---|---|---|
| Griffiths2019 | New original Word data enabled a faithful final-table extraction. Pooling solved the routing admission obstacle, but not the Pomfret production contradiction or 22 catch-total conflicts. | Reopen source-blocked work when new evidence arrives; verify final versus initial tables visually and reconcile fleet sums. Never describe pooling as a biological repair. |
| EEZ941 / WCP2007 | Diet normalization hardly changed the roughly 69.42% worst production residual. Option1 changed juvenile PB/EE while preserving other-mortality flows; it remains an explicit scenario, not an author-confirmed correction. | Decompose budget failures into group residuals and rule out transcription, units and rounding before proposing parameter changes. Record exactly which quantities a proposed correction preserves. |
| LME049 | Watari's GE/Egestion OK depends on extensive runtime completion: censored seabird biomass becomes 1 and unknown BA is solved, including detritus BA about +1021.63. Griffiths constrains living BA to zero and still fails. | Display consequential defaults beside the outcome. Do not rank original source models by diagnostic grade when their completion freedoms differ. Add conservation checks and explicit assumptions for pooled variants. |
| LME050 | Higher catch-weighted PPR in 1985 mainly reflects higher catch. Exact-name matching missed Scomber/Auxis labels whose supported members share one model group; many other unmatched stocks have no supported group. | Separate coefficient, catch, scope and feedback effects. Add a second matching pass for high-tonnage aliases/containment; same-group aliases need no within-pool proportions, whereas multi-group assignments need supported weights. |
| LME003 | Author-defined -1 inputs and unused GCE=0 placeholders must not be interpreted literally. Coupled source equations determined unknown B/EE; a generic loader default would represent a different model. | Add a pre-loader missing-biological-input gate. Solve only determined source equations in separate runtime input; check an independent formulation, admissibility and published output precision. |
| LME014 | Native .eweaccdb Sequence, habitat basis, migration and separate fleet-return tables matter. Missing B was solved with those terms; the source's 35/36/45-row representations are not interchangeable. | Audit native schema and solver equation coverage before flattening. Require exact diagnostic-input-to-selected-input reproduction, including loaded state and hashes. |
| LME029 | Stock-level BA, stanza transfers and Z-versus-P/B cannot be translated by treating every stanza as an ordinary independent group. A small total PP gap coexists with a 23.96% production residual. | Add a native multistanza compatibility check. Record unsupported equations and distinguish translation limitations from confirmed errors in the authors' model. |
| LME022 | Printed North Sea tables and EcoBase457 differ in 205 numeric fields. Independent source balance and loaded diagnostics disagree for the latter. Negative SPPR in an unfished seabird group causes a real TE failure in the preferred Scotland model. | Compare repository variants numerically; trace discrepancies across source/converter/loader/equation layers before assigning cause. Screen all groups, including those with zero catch. |
| LME038 | A folder year was not the publication year. Authorized normalization filled a material diet deficit, and 28 signed BA completions were frozen in a derived model and successfully reloaded. | Confirm identity from source title pages. Give authorized derived variants distinct identities and verify complete state/flow equivalence on reload. Residual BA is not automatically evidence of ecological stock trends. |

The strongest extra lesson is that **a model can return OK after the loader supplies balancing quantities that were never measured**. Watari illustrates this; the selected model remains selected, and its limitations remain recorded. This review did not repair its biomass, BA or TE behavior.

Detailed reviews with source links:

- [Griffiths, EEZ941/WCP and LME049](LESSONS_PACIFIC_LME049.md)
- [LME050, LME003 and LME014](LESSONS_LME050_LME003_LME014.md)
- [LME029, LME022 and LME038](LESSONS_LME029_LME022_LME038.md)

For an actual revision, prioritize executable checks for converter/loader fidelity, coupled unknowns, native equation compatibility and exact selected-state reproduction. Add matching and PPR-comparison checklists to the downstream skill rather than expanding extraction-only instructions into every downstream task.

## Existing instructions versus proposed additions

Source inventories, exact group identities, visual checks, unknown-versus-zero handling, source precision, taxonomy evidence, round trips, mortality/discard accounting and selection ownership already exist in the skills. Their presence was helpful. The main gaps are enforceable converter and initializer audits, clear stage/status terminology, predecessor-lineage verification, partial-catch handling and concrete troubleshooting examples. Reading Overview late was an execution lapse, not a missing rule.

Suggested destinations are the current `prepare-ecopath-model` and `calculate-regional-ppr` entry points plus maintained domain references for conversion, source bundles and mortality/discards. Put the three-option/no-global reporting preference in the project workflow. Preserve the frozen original skill resources as historical evidence; do not edit all archived copies.

## Evidence

- [LME024 authorized experiment](../../../common_reference_data/provenance/source_paths.csv)
- [LME026 extraction](../../../regions/LME/LME_026/papers/MED-2022/models/Piroddi_2022_Mediterranean_1995/extracted_tables/REPORT.md)
- [LME037 source search](../../../common_reference_data/provenance/source_paths.csv)
- [LME037 direct diagnostics](../../../regions/LME/LME_037/papers/LME037-Bacalso-2026/models/Bacalso2026_Visayan_Sea_1997_baseline/results/diagnostics/DIRECT_SPPR_REPORT.md)
- [Griffiths versus WCP option 1](../../warm_pool_candidate_review_20260928/evidence/GRIFFITHS_VS_WCP_OPTION1.md)
