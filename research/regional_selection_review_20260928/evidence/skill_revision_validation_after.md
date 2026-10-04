# Validation after research-skill revision

Date: 2026-09-28. This assessment replays the four baseline scenarios against the revised instructions. Only this report was written. No scientific execution, workbook update, source modification, or archived skill modification was performed.

## Scope and validation evidence

Read all three active `tools/skills/*/SKILL.md` entry points, the new preparation references `missing-data-recovery.md` and `reconstruction-audit.md`, the new calculation reference `direct-diagnostics.md`, and relevant README workflow/schema/ownership/research-agent sections. Archived original references were not read or changed. Their existence was checked where referenced.

All 11 local Markdown-link occurrences in these seven inspected documents resolved to existing files. These include every new cross-skill/reference link and README links to all three new references. The `README.md#workbook-reference` destination heading exists. Sixteen additional core script/resource paths named in code-style text were checked and exist, including the original extraction, mapping, paper-to-PPR, taxonomy, source-bundle, integration and mortality/discards references. No remote source download was attempted because these are scenario tests rather than an actual article-recovery task. No claim is made that engine code executes the displayed call or that workbook publication enforces every stated rule; implementation was outside this review.

## Scenario 1: no diet, failed publisher link, possible predecessor baseline reuse

The revised instructions now direct a concrete bounded recovery sequence:

1. Establish exact article identity and distinguish publication, baseline, survey and simulation dates. Inventory local files and their contents to identify the exact missing field/table and model version.
2. Search publisher article/supporting-information pages, accessible XML and attachment metadata; search exact DOI/title with the missing item.
3. Search official repository/API records and linked deposits using the parent DOI. Check the returned article/attachment relationship rather than guessing download identities.
4. Search author/institutional repositories, theses and model reports. Follow explicitly cited predecessors. Check EcoBase/native deposits where relevant while preserving them as distinct numerical variants until compared.
5. Validate retrieved bytes, file type, completeness and attachment identity; retain URL, repository record, access date, filename and hashes. Verify original table geometry before transcription.
6. Reuse predecessor inputs only with explicit lineage, a group/parameter crosswalk, checks of period, area basis, diets, catches and stages, and demonstrated area conversions. A matching region or group count is insufficient. Baseline diets must not silently stand in for a dynamic endpoint with changed trophic levels or structure.
7. After the named search routes have been checked, record queries/outcomes and exact gaps without repeated failed retries. Continue source-faithful extraction; issue NOT_RUN for blocked calculations. Distinguish not found, inaccessible, incomplete, and downloaded/verified.

**Result:** The baseline gap is resolved at the instruction level. A failed publisher link no longer ends discovery; official repositories/APIs and predecessor lineage are explicit. Possible reuse alone still does not authorize filling the diet. Search bounds are route-based rather than a fixed request/time budget, which is a reasonable research judgment boundary rather than an internal conflict.

## Scenario 2: unknown B loaded as 1; blank BA solved; diagnose OK; direct GE/TE/Egestion only

The revised instructions distinguish source evidence, canonical model, computational input, and loaded state. The directed audit is substantially more specific:

1. Compare source, eight import tables, canonical JSON and reconstructed tables field by field, preserving source unknown markers, names and numerical semantics. Archive raw converter output and every restoration of altered source values.
2. Enumerate unknown biological B/PB/QB/EE before loading. Do not call an imputed B=1 biological reconstruction. If source equations determine the unknowns, solve the coupled system separately and verify rank/uniqueness, residuals, admissibility, precision limits and published outputs or an independent formulation. This permits valid source-derived completion; it does not categorically reject every originally unknown parameter.
3. Retain a machine-readable post-loader transformation ledger, including imputation, changed known rates, solved/replaced BA, normalization and synthetic groups. Keep source balance distinct from loaded balance. Solved BA can close the equations but is neither observed accumulation nor proof of source steady state.
4. Reuse sufficient retained results only when exact input/configuration and engine identity meet the request. Otherwise use the audited candidate-specific constructor/settings or a bounded regional script. Do not silently introduce new normalization, BA solving, pooling, tolerance changes or repairs.
5. For a successfully constructed audited calculator, call `diagnose_sppr(TE_option=option, short=False, flat=False)` for exactly `GE`, `TE`, and `With Egestion`. Handle each option independently. If coefficients are requested, `return_sppr=True` provides the diagnostic/coefficient tuple and avoids solving twice.
6. Preserve each full return or exact NOT_RUN/exception/timeout/unsupported record. Save settings, source/runtime hashes, engine identity and before/after state. Keep scientific interpretation in a separate investigation report. Global and Monte Carlo work require a broader request; the generic `--stage sppr` is explicitly excluded as a direct-only shortcut.
7. Treat overall grade, component grades and strict flags separately. Returned OK means that configuration met thresholds, not that its original source fidelity or ecological suitability is proven. Check negative/nonfinite values across biological groups, including unfished groups. Before coefficient integration, reload the persisted input and compare state, flows and returns.

**Result:** The earlier generic-wrapper/direct-only conflict is resolved in the active skills, reference and README diagnostic section. The exact direct-call contract is present, and it clearly protects the user's requested scope. The comprehension is expressly labeled illustrative rather than an exception handler; the following independent-option requirement prevents treating it as a complete resilient runner.

**Remaining limits:** No time limit or ready-to-run universal constructor is supplied. The instructions intentionally require a candidate-specific audited constructor/bounded script and independent timeout handling; the numerical execution of that contract has not been validated here. An OK obtained using imputed B and solved BA may be retained as evidence of that runtime state, but cannot be promoted to source reconstruction merely because it is OK. The text supplies no automatic universal admission formula for every such candidate, which is appropriate where source equations differ.

## Scenario 3: unresolved Scomber label; all documented constituents share one group; fivefold 2019 PPR

The revised matching instructions direct exact/synonym matching first, then high-tonnage unresolved-label review for supported aliases/containment. When the supported constituents all map to one exact group, within-pool proportions are explicitly unnecessary: record that group with weight 1, evidence, explanation and confidence. When constituents span groups, supported membership and allocation weights are necessary. Distinguish representative lists from exhaustive definitions; the same-group rule cannot turn a partial list into proof about every constituent.

Validate membership, exact identifiers and weights; report label and catch-tonnage coverage by year/basis and largest unsupported catches. If matching inputs change and downstream calculation is authorized, calculate and refresh dependent results; matching-only scope still stops before downstream calculation.

For the fivefold difference, the current skill explicitly requires separating catch quantity/composition, coefficients, scope, mapping support and feedback. Fixed-period coefficients applied to annual historical catches do not reconstruct annual ecosystem states. Compare compatible bases/scopes and inspect the taxon-by-year contribution view; do not infer model accuracy from large positive SPPR or prefer lower PPR merely because it is lower.

**Result:** Both baseline gaps are addressed as research instructions: same-group alias/containment resolution is explicit, and the catch-versus-coefficient/source-support decomposition is now mandatory. The text does not give a numerical attribution formula, change threshold, or allocation convention for interaction terms. That remains an implementation/reporting choice rather than evidence of an error in this hypothetical fivefold ratio. No causal attribution can be accepted without actual calculation and source evidence.

## Scenario 4: explicit FAIL selection and registry update; older reports say unselected

The revised instructions expressly permit authorized FAIL/NOT_RUN selection while keeping numerical eligibility independent:

1. Record model ID/path/rationale in regional Overview and exact restrictions. Register known source identity centrally without fabricated metadata.
2. Use `prepare-selection` to archive/clear obsolete model-dependent results and leave the choice pending. Do not borrow earlier-model annual results. Catch, classic PPR and NPP remain independent.
3. Keep failed/unavailable model annual estimates empty/unavailable, never zero or relabeled valid. Retain per-configuration grades/restrictions; selecting a model does not authorize repairing it.
4. Preserve older unselected reports as dated history and point to current selection evidence. The current selected model is governed by Overview, not the older report.
5. Complete the requested registration through serialized central writes. Validate patches against live headers/keys, recheck the current workbook hash, retain backups, preserve unrelated records and compare keys/content rather than sorted row positions.
6. Use the regional updater and, when visualization is within scope, the HTML builder. Verify selection IDs/paths/rationales, restrictions, missing states, unrelated values and native tables/filters. A pending choice does not require unsupported SPPR merely to update the registry.

**Result:** The principal selection-versus-eligibility and historical-status gaps are explicitly resolved. The selected FAIL candidate can be recorded while its failed annual model results remain unavailable. This does not erase independent classic PPR/NPP results.

**Remaining scope ambiguity:** The update skill still presents updater-plus-HTML as its normal unconditional two-command workflow; it does not separately document a registry-only command path. README's requested-stage rule provides a basis for limiting a narrowly requested registry update, but the text could state that distinction more directly. This is a small remaining operational ambiguity, not permission to rerun science or publish failed estimates.

## Rechecked conflict and overall assessment

The first review found that README's **Freshness and ownership** section still said changing the selected JSON required a new SPPR stage, which could incorrectly imply the broader exporter. The coordinator corrected that sentence during review. I re-read the current sentence: it now requires regenerating/verifying affected SPPR with reviewed input/settings before annual publication, explicitly follows requested direct methods, and excludes automatically launching the broader SPPR stage. That resolves the identified textual conflict without requiring a numerical run for a pending selection.

The four scenarios now have materially stronger decision rules, and no remaining material textual conflict was found in the final inspected version. Remaining limitations are primarily candidate-specific execution and publication mechanics, plus the minor registry-only scope wording described above. Link validation passed for all inspected local Markdown links and the additional checked resource paths. No implementation/runtime test, remote retrieval test, or verification of archived byte-for-byte preservation was performed by this reviewer.
