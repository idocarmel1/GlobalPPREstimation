# Evidence and report calculations

Read with the [template guide](../../../templates/Model_validation_template_instructions.md). The guide defines confidence categories and report fields; this reference explains how to obtain and check their inputs.

## Locate evidence without changing scientific state

From the repository root, use the read-only `read_book`, `records` and `overview` functions in `tools/workbooks.py`. Workbook sheets contain `@table` blocks, not a single rectangular table per sheet. The reader rejects authoritative formula cells rather than using stale cached values. If reading fails, report the issue and use an explicit, documented read-only investigation; do not save/recalculate the workbook to make it readable.

| Evidence | Location and use |
|---|---|
| Selected model and report defaults | Regional `Overview / Settings`: selected_model_id, model_path, taxon_detail_year, catch_basis, selection_rationale; check results_model_id and available provenance separately. |
| Catch | Regional `Catch / Catch`: exact taxon labels, catch_basis, annual tonnes; retain source unidentified classification. |
| Independent TL and simple-chain coefficient | Regional `Classic PPR / Taxa`: taxon, tl, sppr, tl_source, match_method, confidence. The stored sppr is the coefficient actually used; a changed TL alone does not establish a changed coefficient. |
| Source ecological groups | Exact model JSON and regional `Selected model groups / Groups`; verify model identity, IDs, names and source versus synthetic status. |
| Adopted mapping | Regional `PPR / Matching`: model_id, taxon, group, weight, confidence, evidence, explanation. Filter by the exact model. |
| Weight assumptions | Allocation-assumption tables when present, exact-model mapping/allocation reports, group definitions and source caught-mass evidence. Discover actual table headers; do not assume every workbook contains an identical optional ledger. |
| Diagnostic fields | Regional Diagnostics blocks and exact-model retained direct returns with their input/settings provenance. |
| Negative SPPR entries | The corresponding saved **group × basal-source SPPR matrix**, including its row/column identifiers. An aggregated Group SPPR table or a negative-column count cannot identify all pairings. |
| Article/model alternatives | Relevant `Project.xlsx` paper/model blocks, paper folder, source text and tables. Inspect source period/area; do not merge models from one article. |
| Geography | Region boundary provenance and the source figure/domain for the selected model; inspect images before estimating. |

Discover actual files by listing the specified model/paper/report directories and following recorded paths. Do not assume that a generic `sppr_source.xlsx` contains the full contribution matrix merely from its name. Do not execute archived builders or calculators as a way to inspect their outputs.

The [pipeline reconstruction reference](../../original_skill_resources/combined-src/references/reconstruction-audit.md) distinguishes source, loader and computational state. Use it for source-fidelity interpretation, without running its extraction/conversion stages. The [direct-diagnostics reference](../../original_skill_resources/combined-src/references/direct-diagnostics.md) explains returned outcomes and configuration identity; validation alone does not call the solver.

## Exact identity and freshness

For each result used, record the available model ID, canonical/computational input identity, group-ID mapping, method and source scope, and configuration/engine evidence. Hash permitted exact inputs when useful. Match saved results to those identities; similar filenames and matching group counts are insufficient.

If a report and current workbook disagree, establish which is current from explicit provenance. Do not silently select whichever result looks better. If identity cannot be reconciled, keep the discrepancy in supporting evidence and mark the affected finding unavailable or historical. Independent source context, catch data and other verifiable sections can still be completed.

Reuse existing source conflict, mapping and allocation reports when still applicable. Read cited tables/figures when needed to check consequential claims. Distinguish an independently checked finding from a summary of an existing audit. A validation report does not claim a new cell-by-cell extraction audit by default.

## When to recommend a fresh scientific run

Actively assess whether the validation can be completed reliably from saved evidence. Recommend a fresh paper-to-PPR run when a consequential gap cannot be resolved through source inspection, identity checks or report arithmetic. Match the scope to the reason:

| Condition | Appropriate recommendation |
|---|---|
| Required per-source matrices or direct diagnostic returns were never retained, and the full finding is needed. | Fresh diagnostics for the exact audited input/configuration and required methods, retaining full matrices and labels. Explain that existing column counts cannot identify affected source/group pairs. |
| Saved results belong to an earlier/different model input or incompatible settings. | Recompute the affected diagnostic/calculation stages from the verified input, preserving the historical result separately. |
| Extraction fidelity is materially uncertain, source conflicts affect parameters/structure, or required source-to-runtime transformations cannot be reconstructed. | Fresh extraction/reconstruction audit plus the dependent paper-to-PPR stages needed for a defensible comparison. Recommend the full current workflow when the uncertainty spans the whole chain. |
| A confirmed correction to membership/weights or model parameters would change downstream results. | Explain the proposed correction and affected stages; ask for approval of both the change and its run/adoption scope. Discovery of an issue alone does not adopt the correction. |
| The user needs independent reproduction that existing files cannot establish. | Propose the precise stages and settings to reproduce, and the old/new comparison to retain. |

A change in skill version or file age alone does not prove that the science needs rerunning. Explain the particular missing stage, required evidence or suspected effect. Do not recommend a full rerun just to fill a missing hyperlink, reformat a report, recalculate confidence shares, sort the appendix or estimate geography from available figures.

Before each fresh scientific run:

1. Complete available read-only investigation and independent report sections. Identify the exact model/input and unresolved finding.
2. Present a concrete recommendation: why the run is necessary; why saved evidence is insufficient; stages/methods/settings; expected outputs and comparison; proposed input changes, if any; and whether results would only be retained for review or adopted into workbook/project/map outputs.
3. Ask explicitly, for example: `The saved TE diagnostic reports two negative source columns, but its contribution matrix was not retained, so I cannot identify the affected groups. I recommend rerunning TE diagnostics on the verified saved input and retaining the labeled matrix for review. This proposal does not include changing inputs or adopting new regional results. Shall I proceed with this run?` Adapt the wording and scope to the actual evidence.
4. Wait for explicit confirmation for that proposal. Broad interest in validation, skill approval and silence are not confirmation. If confirmed, invoke the current paper-to-PPR workflow for exactly the approved scope and preserve both old and fresh identities. If the required scope expands, explain and ask again before the additional run.
5. If declined/deferred, keep the unsupported finding explicit and retain the recommendation in the handoff/supporting review. Do not put a new decision in a manual researcher field.

The same approval rule applies to a fresh scientific substage as to a full paper-to-PPR run. A regional **validation test** may use saved evidence and report arithmetic, but permission for that test does not by itself authorize fresh extraction, SPPR execution or changes to scientific results.

## Negative SPPR source columns

1. Obtain GE and TE matrices separately for the recorded configurations. If retained serialized arrays have labels elsewhere, verify their association before use. Reject duplicated/missing row or column IDs and ambiguous array orientation.
2. Resolve **row labels to recipient model groups** and **column labels to basal sources**. Resolve names from the exact same model/runtime inventory, including synthetic source IDs when applicable. Do not assign sorted names positionally to an array with a different order.
3. Inspect each finite matrix entry for a strict negative value before display rounding. The current engine counts negative source columns using `(SPPR < 0).any(axis=0)`. Preserve tiny negatives in the finding; any numerical-tolerance interpretation is a separate note with its actual basis.
4. Collect `method, source_id, source_name, group_id, group_name, sppr_value` for every negative entry. Retain the full-precision values in supporting evidence. The concise report lists each source followed by its affected group names/IDs; magnitudes can be included when useful.
5. Include unfished groups. A researcher's stated exclusions do not change the matrix being reviewed. If a distinct retained matrix actually implements exclusions, identify that configuration and its scope.
6. Check the derived number of affected columns against the saved `divergence.n_negative_sources`, when present. A mismatch can indicate different inputs, sign conventions, filtering or misaligned labels; investigate before describing the findings as equivalent.
7. Inspect nonfinite/missing entries separately. Zero negative entries in an incomplete matrix is not evidence of a completely negative-free matrix.

If the matrix is absent but a matching saved diagnostic reports a count, preserve that limited finding, for example `Saved diagnostic reports two affected source columns; matrix unavailable to identify columns/groups.` For a complete matrix with no negative entries, use the preferred report wording `No negative SPPR entries across the basal-source columns`. If only the matching saved diagnostic reports zero, use the concise sign finding in Word and retain the diagnostic attribution, configuration and missing-matrix limitation here in supporting evidence. Do not describe that as a new independent matrix check. Avoid the shorthand `0 negative source columns`. This sign check alone does not establish an overall diagnostic pass. Recommend a fresh diagnostic run when needed to obtain the required detail, explain the reason, and always ask for confirmation before running the solver.

Example using fictional IDs, deliberately out of order:

| Group row | Source 2 | Source 1 |
|---|---:|---:|
| Group 30 | -1 | 2 |
| Group 10 | 3 | -4 |
| Group 20 | 5 | 6 |

Required finding: Source 2 → Group 30; Source 1 → Group 10. Group 30 has a positive total but still has negative source SPPR. Sorting group IDs and then applying matrix values by position would produce the wrong identities.

For rho_living, b and detritus SPPR use matching saved diagnostic fields, not recomputed surrogate formulas. TE's conventionally zero recycling parameter is not evidence that detritus recycling is absent. Unknown/unsupported values remain unavailable.

## Build the taxon audit rows

Start from all catch labels for the selected catch basis, including zero-catch labels. Select the requested year column. Missing year values are missing, not zero. Keep exact catch labels for display and keys; taxonomic normalization helps assess membership but must not silently merge catch records.

Check duplicate taxon/basis keys. Only sum genuinely disjoint, documented catch components; duplicate copies are an error to resolve. For total catch, use the recorded total-catch basis when available. Do not add landings and discards again to an existing total-catch row. If deriving total catch from components is necessary, document the derivation and missing-component behavior.

Join the classic coefficient and model mapping by exact keys with explicit unmatched lists. Join groups by ID, not spreadsheet row order. Validate every referenced group belongs to the model under review. Read allocation ledgers for stage definitions, source catch proportions, zero candidates, transfer periods and catch-basis assumptions.

The supporting row record needs these semantic fields; an equivalent table structure is acceptable:

- Exact taxon label, reference year/basis, catch tonnes, TL, classic SPPR coefficient, simple-chain PPR tonnes C, missing-value flags and input locations.
- Adopted group IDs/names and weights, known partial weights and unresolved candidates where supported.
- Membership rule, confidence and evidence; allocation rule, confidence and evidence; transfer assumptions; stored confidence and review confidence.
- Overall confidence, a concise reason, source IDs and any difference from the stored decision.

Apply the [guide's rules](../../../templates/Model_validation_template_instructions.md#confidence-rules-and-examples) rather than copying historic labels uncritically. A single-group weight of 1 adds no allocation uncertainty, but cannot improve weak membership evidence. Complete resolved weights are nonnegative and sum to 1 within documented numerical tolerance. A clearly erroneous weight total is not repaired by automatic normalization.

Search source definitions and authoritative online evidence where needed. Record queries/references and outcomes proportionately; online searching alone does not increase confidence. For stage composition, verify taxon, caught-mass basis, region/fishery, period, stage threshold and catch basis. Unsupported geographic or temporal transfers can lower confidence. Do not infer catch proportions directly from biomass without assessing the assumption.

If a defensible replacement mapping is found, retain it as a proposed correction and explain the current uncertainty. A report-only task does not adopt it in the workbook or use it to inflate the adopted summary. The report's review confidence can change while the stored scientific inputs stay unchanged.

## Arithmetic and sorting

Let C_i be catch tonnes for taxon i, s_i its saved classic/simple-chain SPPR coefficient, and k the verified wet-weight-to-carbon divisor. Under the repository's current convention, raw simple-chain PPR is C_i × s_i and P_i = C_i × s_i / 9 tonnes C. Confirm the stored coefficient's units before applying this conversion. An already-carbon result must not be divided again.

Do not recompute s_i from a generic TL formula merely because the saved coefficient is absent. Use the existing configured simple-chain method only if its derivation is explicitly part of the authorized report arithmetic and fully evidenced; otherwise retain `?`. If TL is absent but a legitimate coefficient exists, retain the distinction and document its provenance. A genuine zero catch gives zero annual PPR even when its coefficient is unavailable; this does not establish a known TL/coefficient. Positive catch with an unavailable coefficient remains unknown. Label the total known PPR only when unknown annual contributions remain.

For each overall confidence category q:

- n_q = number of taxon rows assigned to q.
- Catch_q = sum of their known C_i; catch share = 100 × Catch_q / sum(C_i), provided the full catch denominator is available and positive.
- PPR_q = sum of their available P_i; PPR share = 100 × PPR_q / sum(available P_i), provided the known-PPR denominator is positive.

If catch itself is missing, mark totals as known subtotals and make the denominator limitation explicit. Do not show unqualified total-catch shares. If simple-chain PPR is missing, the guide permits shares of **known simple-chain PPR**, with the missing taxon count and associated known catch share disclosed. Unknown PPR is not a zero-valued observation even when its category has no contribution to the known subtotal.

Keep all unresolved mappings in these denominators whenever their catch/PPR is known. The mapping summary describes confidence in assignments, not the fraction with finite GE/TE coefficients. Do not substitute an old GE/TE supported-catch statistic for these measures.

Use full-precision values for calculations and descending appendix sorting; round only displayed values. Missing PPR sorts after every known numeric value, including zero; use taxon name for ties. Derive summary totals from these same rows and verify they reconcile. Do not filter low-PPR or unresolved records out of the appendix.

## Geographic evidence

Keep a short record of boundary definitions, figure/page, map orientation/scale and the interpretation of the study-area line. Use appropriate geographic area calculations for compatible polygons. If digitizing an image, retain landmarks/control points and the estimated boundary; exclude land consistently with the study definition.

A visual estimate is acceptable when the figure supports it. Record approximate percentages or a defensible range, how it was judged, and the main boundary uncertainty. Never compare the raw areas of screenshots at different scales or treat a bounding rectangle as the actual shelf/study polygon. Reserve Not determined for evidence too ambiguous to support an estimate.

Do not insert the earlier LME036 visual estimates into another model or region. Even for LME036, establish that the same figure and target boundary are being reviewed, and distinguish the researcher's estimate from a fresh independent area measurement.

## Approved fallback and readable coverage

Apply the template guide’s Medium catch-first then biomass fallback only after establishing eligible groups. Retain the rejected catch attempt, actual source fields/values/units and normalized proportions, membership uncertainty and transfer assumptions. Canonical PPR / Matching and the companion Mapping review/Allocation assumptions retain adopted classifications and separate assumption flags. A report-only task still cannot adopt proposals; an explicitly authorized adoption must propagate dependent calculations and map outputs before completion.

For each of membership and allocation, aggregate known simple-chain PPR by actual rule and component confidence. Each taxon contributes once to each separate table, not once per group. Include unresolved/not applicable and all used rules. Tables must reconcile independently to the same full known-PPR denominator. Capture actual map controls, filters, payload calculation, visible display rounding and exact value; diagnose differences rather than copying a displayed number.


## Coverage preference and concise uncertainty

Apply the template guide’s Very low broad-category and closest-analogue rules before leaving a meaningful placement unresolved. Prefer near-complete coverage with visible assumptions; retain Unresolved only when no meaningful group or numerical allocation can be justified. Direct applicable source geographic catch quantities can support High allocation confidence; geographic overlap alone cannot. Include all five confidence categories and the Very low coverage share. Name every unresolved taxon with a short reason, or state none; group and flag Very low cases compactly. Keep skill, approval, integration, hashes and test details in supporting evidence rather than validation prose.
