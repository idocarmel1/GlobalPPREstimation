# Adopted LME036 mapping revision — 29 September 2026

This revision adopts the authorized taxon-mapping decisions for the selected 2000s Northern South China Sea model. It recalculates only dependent taxon coefficients, annual results and ratios, then updates the isolated project workbook and generated pages. The source model, saved group SPPR, diagnostics, catch, independent classic PPR and NPP are preserved. It does not establish model validity or resolve the missing per-source matrix evidence.

## Scope and evidence

- Selected model: `36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)`.
- Reference view: 2019 landings, all sources, method-specific unidentified treatment, all taxa and groups; independent simple trophic chain at TE 0.1, wet-weight PPR divided by nine once.
- Canonical records: [regional workbook](../../../../../../../../LME_036.xlsx), PPR / Matching, Mapping review and Allocation assumptions. Machine-readable audit: [adopted taxon audit](taxon_audit_adopted.json). The [input identity](input_identity.json) records the baseline and protected-source identities.
- 374 taxa; 10,308,126.303982593 t landings; known simple-chain PPR 837,452,937.7894479 t C. The 34 taxa lacking coefficients have zero landings; unknown coefficients remain unknown.
- 22 reviewed candidate sets use the approved model-catch fallback; no biomass fallback was needed. Fifteen have Medium membership and seven flatfish have Low membership due to conflicting life-stage boundaries. Every fallback has Medium allocation confidence. Including earlier stage allocations, 157 taxa retain explicit assumption flags.
- Maximum lengths exclude the small-species pools for Psettodes erumei (64 cm TL), Paralichthys olivaceus (103 cm TL) and Larimichthys polyactis (40 cm SL, already exceeding 30 cm). URLs, units and retrieval dates are retained in the audit and Excel Sources sheet.
- Whole-pool source-model catches are composition proxies, transferred across years and catch bases; they are not measured composition of the regional catches. Twenty taxa remain unresolved. See the audit for included candidates, raw catch/biomass, denominators, exact weights and prior decisions.

## Confidence and regional results

| Overall confidence | Taxa | Known simple-chain PPR share |
|---|---:|---:|
| High | 126 | 31.0269% |
| Medium | 120 | 33.4649% |
| Low | 108 | 30.6822% |
| Unresolved | 20 | 4.8260% |

The group-assignment and allocation tables each partition the entire known-PPR universe; their percentages must not be added together. Component confidence and weakest-component overall confidence are separate. Internal historical rule identifiers remain only in audit records.

| Provisional 2019 landings result | Before (t C) | After (t C) |
|---|---:|---:|
| GE | 49,595,054.5446873 | 43,800,120.28175317 |
| TE | 412,990,776.0229069 | 382,696,433.4805596 |

Both methods cover 9,012,796.927105889 t landings after revision, compared with 10,270,718.05495921 t before. Removing unsupported broad-category mappings lowers numerical coverage. See [all recorded changes](dependent_result_changes.json) for other catch bases. The classic-PPR denominator is unchanged. Saved diagnostic warnings and provisional method restrictions remain in force.

## Report and instructions

The new Word derivative preserves the entire researcher SPPR row, selection rationale, open-issues and review rows as canonical OOXML, all other package parts and original link targets. The researcher original is unchanged. The full taxon appendix is a separate seven-column Excel file, with Coverage, Allocation evidence and Sources sheets. The reusable Word template, filling guide and ecopath-model-validation skill reflect this structure and the approved allocation policy.

The coordinated task completed the two additional model tests and confirmed the revised user condition. Its reviewed skill-only commit `bd4f5e5997ab3116553d349e0b272eed14e3680b` has been synchronized, preserving this task’s validation changes. The original paper-to-PPR instructions now also include the approved catch-first/biomass fallback and consistent Word/Excel/browser reporting requirements. [Skill handoff evidence](skill_handoff.json) records the gate, models, numerical scales and changes. No calculator, balanced-state or model-selection changes were introduced.

## Verification

Final verification results are recorded separately in artifact_checks.json, saved_data_checks.json and map_checks.json. Temporary render PDFs, page images, browser screenshots and authoring scripts are internal QA materials, not required deliverables. Browser checks use a fresh local Edge profile against this isolated generated map; they do not claim to inspect the user's already-open browser or its remembered selections.


Final data/artifact checks passed:

- Protected source identities, every saved group table, catch/classic/NPP tables and saved method diagnostics compare exactly with the pre-adoption baseline.
- All 150,041 unrelated unit-keyed Project.xlsx records are unchanged.
- All 2,280,180 generated annual map/time-series cells and NPP match Project.xlsx; page layouts, source files, selected models and the archive page pass the project verifier.
- The actual browser view gives simple-chain 837,500,000 t C, GE 43,800,000 t C and TE 382,700,000 t C after display rounding. The unrounded simple-chain value is 837,452,937.7894479 t C. All 374 map mappings and 24,684 taxon coefficients match adopted data; no browser script errors occurred.
- The Excel appendix contains all 374 ordered records, frozen/filterable headers and 16 working native source hyperlinks. Formulas cover 157 assumption-dependent taxa and contain no error cells. The largest cached-weight difference from canonical data is 1.11 × 10⁻¹⁶, within floating-point representation precision. Both rule-table partitions are exactly 100% before display rounding.
- Every page of the six-page report and four-page template was rendered and inspected, alongside all four spreadsheet-sheet previews. No clipping, extra blank pages or broken local Word links were found. The researcher manual rows and original link targets are preserved.
- Five allocation-helper tests passed; the validation skill structure and whitespace checks passed.

See [combined verification record](reconciliation_checks.json) for output hashes and machine-readable results. The simple-chain payload retains its historical source snapshot identity because those inputs are unchanged; the generated page itself is stamped with the newly updated Project.xlsx identity.


A final prose correction removed a contradictory three-pool statement from Larimichthys polyactis while retaining the correct two-group allocation. Canonical text, Excel and source/build identities were refreshed; all numerical result hashes remained unchanged. Data, artifact and browser checks passed again after that correction.

The revised original skill is synchronized with reviewed commit `bd4f5e5997ab3116553d349e0b272eed14e3680b`, plus this task’s authorized mapping/reporting additions. Its 17 evidence-checker tests and both skill validators passed. The retained original proposal is historical; the applied instructions and gate are recorded in skill_handoff.json.
