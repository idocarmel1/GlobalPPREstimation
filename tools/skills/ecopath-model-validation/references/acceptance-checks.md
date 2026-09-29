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
- **Missing data:** unknown catch/PPR is not zero; missing coefficient counts and catch shares are visible; unresolved model mappings with known PPR still contribute to PPR totals.
- **Units:** catch tonnes and PPR tonnes C are labeled; the configured conversion occurs once; classic/simple-chain values are independent of GE/TE mapping.
- **Order:** appendix rows sort by full-precision numeric simple-chain PPR descending; unavailable values are last; taxon name breaks ties.
- **Geography:** A and B use the correct denominators; approximation is labeled and grounded in the correct figures; missing coordinates alone did not prevent a defensible estimate.
- **Document:** manual cells and edited hyperlinks/deletions are preserved; all seven linked Excel appendix columns and a separate Sources sheet are present; every rendered page was inspected.
- **Delivery:** remaining evidence gaps and unperformed checks are reported honestly; regional workbooks, model inputs, selections and generated maps remain unchanged during a report-only run.

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
