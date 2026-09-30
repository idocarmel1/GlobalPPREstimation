# Acceptance checks

Use these checks on a produced report. They are also review scenarios for evaluating this skill; their presence is not evidence that a regional test has run. Do not execute the deferred LME036 test before the user's review and authorization.

## Before delivery

- **Scope:** region/model/year/basis match the request; exclusions were respected; no unrequested scientific execution or adoption occurred.
- **Fresh-run recommendation:** any necessary scientific rerun has a specific reason and proposed scope; the user was asked and explicitly confirmed that run before execution. Skill approval or a validation-test request was not substituted for this confirmation.
- **Identity:** each diagnostic and group lookup belongs to the same exact model/configuration, or its limitation is explicit. Source, canonical and loaded-state facts are distinguished.
- **Selection:** Article and Model reasons are separate and documented or `?`; known other models from the same article are described.
- **Negative SPPR:** each affected source column is paired with every affected group by names/IDs. GE and TE are separate. Positive row totals do not hide negative entries; missing matrices do not become a verified absence.
- **Diagnostics:** rho_living, GE b and detritus-pool SPPR come from matching retained fields; failures/unsupported results are not silently promoted.
- **Mapping:** all catch labels in the defined universe appear once; exact group IDs are valid; weights and stage assumptions are evidenced; unresolved weights remain `?`; review confidence follows the weakest required component.
- **Totals:** category counts sum to the appendix count; category catches/PPR reconcile to the same row data; percentages use the stated full-catch or known-PPR denominator and reconcile within rounding tolerance.
- **Missing data:** missing catch is unknown; genuine zero catch gives zero annual PPR even with a missing TL/coefficient; positive catch with a missing coefficient remains unknown; missing inputs are disclosed concisely; unresolved model mappings with known PPR still contribute to PPR totals.
- **Units:** catch tonnes and PPR tonnes C are labeled; the configured conversion occurs once; classic/simple-chain values are independent of GE/TE mapping.
- **Order:** appendix rows sort by full-precision numeric simple-chain PPR descending; unavailable values are last; taxon name breaks ties.
- **Geography:** A and B use the correct denominators; approximation is labeled and grounded in the correct figures; missing coordinates alone did not prevent a defensible estimate.
- **Document:** concise findings follow the edited template; no restored repeated status/provenance/method prose; manual cells and edited hyperlinks/deletions are preserved; all seven linked Excel appendix columns and a separate Sources sheet are present; every rendered page was inspected.
- **Delivery:** remaining evidence gaps and unperformed checks are reported honestly; regional workbooks, model inputs, selections and generated maps remain unchanged during a report-only run.
- **Portability:** all repository-local hyperlink targets in current deliverables are relative to their containing file, resolve to versioned files/directories, and work with the same directory structure under another repository root. Check Word relationships/fields and anchors, Excel relationships/formulas, and Hyperlink Base; reject machine-specific bases/paths. Preserve public URLs and internal anchors, document content, formulas and formatting. A resolved Office tooltip alone is not an absolute-path failure.

## Review scenarios

### Negative contributions concealed by totals

Use the fictional out-of-order matrix in [evidence and calculations](evidence-and-calculations.md#negative-sppr-source-columns). The finding must identify Source 2 → Group 30 and Source 1 → Group 10. Group 30's positive total must not exclude it. Row sorting must not change matrix identity.

### A count without a matrix

A saved diagnostic says two negative source columns, but no contribution matrix or group-pair list exists. Preserve the count as an attributed historical diagnostic; mark source/group detail unavailable. Recommend the necessary diagnostic rerun, explain why the full pairings cannot be recovered from the count, and ask for confirmation before running SPPR. Do not claim the pairs were checked from the existing evidence.

### Strong membership and assumed stage weights

A source explicitly identifies the species, but its juvenile/adult weights come from source-model catches and are transferred across all catch years. Membership can be High; W4 weights are Medium with the transfer assumption unless mismatch warrants lower confidence. Overall confidence is no higher than Medium. Count the taxon once.

### Unsupported equal split

Stored weights are 0.5/0.5 only because a prior process needed numbers, and no defensible rationale exists. Show the required weights as `?` and the reviewed mapping as Unresolved, explain the stored placeholder, and leave workbook numbers untouched. Numerical completeness does not establish confidence.

### Unresolved mapping with known independent PPR

A taxon has known catch and classic coefficient but no supported model-group assignment. Include its catch and simple-chain PPR in totals and in the Unresolved category. Never infer zero simple-chain PPR from the lack of an Ecopath mapping.

### Missing coefficient and weighted totals

Fictional four-row dataset under the repository's wet-weight coefficient /9 convention:

| Taxon | Catch t | Classic coefficient | Overall mapping confidence |
|---|---:|---:|---|
| Alpha | 60 | 9 | High |
| Beta | 30 | 90 | Medium |
| Gamma | 10 | unavailable | Unresolved |
| Delta | 0 | 9 | Low |

Expected known simple-chain PPR is 360 t C: Alpha 60, Beta 300, Delta 0; Gamma is unknown. Total catch is 100 t. Catch shares are High 60%, Medium 30%, Low 0%, Unresolved 10%. Known-PPR shares are High 16.666…%, Medium 83.333…%, Low 0%, Unresolved 0% of the **known** subtotal, with one missing-coefficient taxon representing 10% of catch explicitly disclosed. That last zero is not a claim that Gamma's true PPR is zero. Appendix order is Beta, Alpha, Delta, Gamma.

### Numeric sorting

Known PPR values 100, 20, 9 and 0 sort in that order, followed by unavailable values. Sorting their display strings would be wrong. Tied displayed numbers may have different unrounded values; retain the numeric ordering.

### Geographic evidence without coordinates

A readable study map has a coastline and an identifiable offshore boundary but no digital polygon. Estimate using documented visual comparison, tracing or georeferencing, label the approximation, and explain uncertainty. Do not default to Not determined solely because coordinates are absent, and do not compare raw pixels across mismatched map scales.

### Edited record and review gate

The researcher has deleted long diagnostics and links, written manual group-exclusion notes and requested review before a test. Preserve those edits; a note is not proof of applied exclusions. Deliver the requested draft artifact and stop. Do not create a regional report or invoke the scientific pipeline until the later test is authorized.

### Validation test approved but fresh science needed

The user approves testing this validation skill on a region. Its saved coefficients are stale relative to the selected JSON. Complete independent source/mapping/figure review, explain the mismatch and proposed affected-stage rerun, and ask for explicit confirmation. Do not treat the validation-test approval as permission to recompute. If the user declines, deliver an appropriately limited report.

## Revised report and adopted mapping gates

- Full taxon appendix is Excel: frozen/filterable headers, numeric unrounded PPR order, missing last, readable wrapping and explicit unresolved weights.
- Mapping/coverage is outside the main Word table. Each of the two rule tables has exactly Plain-language rule | Confidence | PPR percentage, full descriptions and descriptive source links. Each independently sums to 100% of the same known-PPR universe, with no double counting.
- Approved fallback uses established eligible groups, then complete model catch proportions, then complete model biomass proportions. Both carry Medium allocation confidence. Test incomplete catch, all-zero catch, valid zero candidates, unusable biomass and missing membership; never drop candidates to make weights sum.
- Record actual fields/values/totals/proportions and assumptions in canonical adopted records; preserve the separate assumed flag.
- Check the actual map controls and visible result as well as its payload and adopted data. A workbook match alone is not UI verification.
- Explicitly authorized adoption/dependent arithmetic is permitted; fresh extraction or group-SPPR runs still require their own scoped authorization.


## Coverage preference and concise uncertainty

Apply the template guide’s Very low broad-category and closest-analogue rules before leaving a meaningful placement unresolved. Prefer near-complete coverage with visible assumptions; retain Unresolved only when no meaningful group or numerical allocation can be justified. Direct applicable source geographic catch quantities can support High allocation confidence; geographic overlap alone cannot. Include all five confidence categories and the Very low coverage share. Name every unresolved taxon with a short reason, or state none; group and flag Very low cases compactly. Keep skill, approval, integration, hashes and test details in supporting evidence rather than validation prose.

## Zero catch without TL or coefficient

A row with recorded catch 0 and missing TL/coefficient contributes exactly 0 annual PPR; retain the missing TL/coefficient and sort with numeric zero rows. A row with positive catch and no coefficient has unknown PPR and sorts after numeric rows. A row with missing catch remains unknown. If all missing coefficients belong to zero-catch taxa, the annual total is complete and does not need the known-subtotal qualifier. Verify all three cases and the unchanged coefficient-availability mask.

## Careful confidence reassessment

- A source explicitly includes a taxon in a juvenile/adult pair, but two passages disagree about the cutoff. Retain supported membership in the union; record split uncertainty in allocation. Do not automatically downgrade both components.
- A small-species pool uses maximum TL at 30 cm. A regional member reaches 35 cm FL: it cannot qualify as a small species. A reported 28 cm FL alone does not prove maximum TL below 30 cm. Do not silently change groups during confidence-only review.
- A provider's broad scientific label denotes a documented fisheries reporting category. Resolve its common name and regional contents before importing unrelated global members as counterexamples; do not let provider metadata override a verified local conflict.
- A modern family name differs from the historical source, but an explicit source member and an authoritative taxonomic bridge establish continuity. Do not downgrade solely because nomenclature changed.
- A source says it assumed 90% juvenile catch. Reproducing 90% does not establish observed mass composition or High allocation confidence.
- Verify all old/new component decisions, including downgrades from High/Medium. Confirm the weakest-component rule, all taxon keys, unchanged groups/weights for confidence-only adoption, and reconciled category/rule totals. Distinguish proposed mapping corrections from adopted confidence changes.
- If no better focal-model mapping is available, an evidenced nearby-model mapping may be transferred through an explicit group-definition crosswalk. Verify donor identity, ecological/geographic compatibility, receiving group IDs and transfer confidence; identical names or proximity alone do not establish membership. Assess receiving weights independently and never copy donor SPPR as part of a mapping fallback.
