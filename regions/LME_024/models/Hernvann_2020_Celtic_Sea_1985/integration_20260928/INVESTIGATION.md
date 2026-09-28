# Provisional Celtic Sea SPPR-to-catch integration, 2026-09-28

The user requested numeric mapping and PPR display for the selected model before later scientific validation. This integration therefore retains **provisional** annual statuses and unchanged **FAIL** diagnostics. It does not establish an ecologically valid regional estimate.

2019, all sources, total catch (landings plus discards), unidentified treatment `method`:

| Numeric method | Supported-catch subtotal, tC |
|---|---:|
| GE | 17,635,031.275725935 |
| With Egestion | 9,069,352.592071421 |
| TE | unavailable: return equation unsupported |

Mapped catch is 852,488.2815712999 of 1,139,679.567089067 wet tonnes, **74.80069891475708%**. The mapping resolves 127 of 488 labels in the historical catch table. Unresolved taxa are omitted from the method subtotal rather than assigned zero coefficients. The coefficients are the fixed 1985 configuration applied to historical catches, not annually reconstructed ecosystems. Carbon is the wet-weight-equivalent result divided by nine exactly once.

## Numerical identity and restrictions

The canonical selected JSON remains unchanged. It cannot directly initialize the calculator because of rounded diet sums and absent two-pool detritus routing. Numeric results belong to the **previously authorized normalized-diet, explicit fishery-return adapter**, retained at `models/extraction_review_20260928/authorized_routing_experiment/`. The adapter, serialized state and donor-return table are necessary; the canonical JSON alone does not encode this configuration. No new parameter repair, pooling, routing, normalization or accumulation replacement was introduced here.

`reproduce_retained.py` verifies every original source/shared-engine hash in the experiment's verification record and every retained artifact hash. It reloads the saved `faithful_printed_BA_state.pkl` and calls the actual direct GE, TE and With Egestion diagnostics. All three complete returned objects exactly match their retained counterparts. Identity-aligned GE/Egestion source coefficients reproduce within 1e-12 relative tolerance. Full new reports and source coefficient matrices are retained beside this document; the preceding scientific evidence is not overwritten.

The prior authorized experiment supplies six P/B values through printed P/Q × Q/B and one Megrim EE from a source-constrained equation. It preserves the two source zero seabird biomasses. Its structural-zero convention is limited to four nonfeeding basal import cells. Printed detritus BA is retained, and discarded fish are counted once as donor removal and once as an internal return. The model's original experiment report and transformation ledgers document these assumptions distinctly from the canonical source.

GE and With Egestion both return FAIL, with maximum living-production relative residual **0.35377062030617057**. GE PP-balance relative gap is **0.30131275162479926**; With Egestion is **0.0517325869483851**. Both coefficient matrices are finite and nonnegative across all 54 source groups, including unfished groups, but convergence does not cure the failed budgets. TE returns `TE_RETURN_UNSUPPORTED`; no missing TE coefficient or annual result is represented as zero. No global option, broad exporter or Monte Carlo was run.

## Matching and geographic scope

Source taxonomy comes from supplement B1, crosswalked to B4's exact group IDs and retained in the selected model's `extracted_tables/taxonomy.csv` and canonical `taxon_descr`. The extraction report has already audited merged cells, life stages, source spelling and parameter identities. This integration uses exact named species and unambiguous explicitly documented genus-sp. membership. Commercial Pectinids support Pecten maximus, Aequipecten opercularis and Pectinidae in Commercial bivalves. All resolved weights are one within a single supported pool; no arbitrary split is used.

Cod, hake and anglerfish have adult/juvenile groups. Species-level catches for those groups remain unresolved because regional life-stage proportions are absent. Broad catch labels crossing other pools also remain unresolved. No biomass or native model catch ratio is substituted for the missing regional allocation. The full mapping evidence and unresolved explanations are in the workbook and `matching_review.csv`; yearly tonnage coverage is retained in Diagnostics.

The selected model covers the Celtic Sea shelf shallower than 200 m, approximately ICES 7.e/f/g/h/j.2, not the full Celtic–Biscay LME. No unsupported geographic fraction or full-LME biological representativeness is inferred. `production_eligible` remains false; provisional numeric display is separate from later validation.

## Preservation and reproduction

`LME_024_before_integration.xlsx` is the original workbook backup. Catch, all Classic PPR blocks, NPP, original classic PPR–NPP rows, selection and rationale are checked unchanged. The canonical hash is checked before and after. Model annual results, group coefficients, matching, coverage and direct-review evidence are added through the existing regional workbook/calculation tools; freshness hashes are generated normally for the saved result state.

Run `reproduce_retained.py`, then `integrate.py` in this directory from the project root. The first is bounded to the three direct diagnostics and reuses the precise persisted experimental state. `integration_verification.json` records result totals, coverage, original/final hashes, unresolved catches and successful regional validation. No shared tool, Project.xlsx or map is edited by these regional scripts.
