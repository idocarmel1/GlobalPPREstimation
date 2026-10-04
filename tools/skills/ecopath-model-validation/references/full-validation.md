# Full model validation workflow

For a composed pipeline, apply the shared [single mapping handoff](../../paper-to-ppr/references/operation-contract.md#one-mapping-stage-per-pipeline-run). The complete mapping checks below inspect the same evidence and keyed decisions produced by the one mapping stage; they do not require a second research/assignment pass. Missing or conflicting evidence returns affected decisions to that stage and leaves dependent report alignment pending.

Read this for a complete model-validation request after the entry skill and shared operation contract. The entry skill retains authorization, exclusions and ownership boundaries. This workflow is required in full for full validation; bounded routes use their named relevant sections/references. Relative links below resolve from this reference.

## Workflow

### 1. Establish the exact target

Resolve the supplied region folder or workbook. Read `Overview / Settings` for the selected model, path, reference year and catch basis. Explicit user choices override the report's default year/basis; record the choice without changing Overview.

If a different candidate is explicitly named, label the report as a candidate review and preserve the actual selection. If the target or required year/basis cannot be determined, inspect the available context and ask only for the unresolved choice. A missing model selection does not authorize choosing one.

Identify any authorized researcher-edited record. Capture its text, table cells and complete hyperlink targets, including anchors. Compare it with the template and existing report only as needed to preserve edits. Do not restore deleted prose or links automatically.

### 2. Establish evidence identity

Read the regional workbook once where practical, the relevant central paper/model records, and exact-model source and diagnostic files. Keep source tables, the exact canonical JSON of the reviewed model/variant, ephemeral loaded state, and saved diagnostic outputs distinguishable. Each distinct computational variant has its own single canonical model.json and departure notes; no redundant computational-input JSON is retained.

Check model IDs, group IDs, periods, source scope, method, runtime settings and available provenance. Reuse an existing validation bundle only when its identity matches the current inputs; its presence is not proof of freshness. Use targeted hashes or recorded identities for permitted inputs, not an indiscriminate repository scan.

Build a compact supporting evidence record with source locations, model/configuration identity, review findings and unavailable items. It is report provenance, never an authoritative selection/status/configuration sidecar.

### 3. Review model context and diagnostics

Populate article/model fields and known alternatives. Keep Article and Model selection rationales separate; preserve a recorded reason or show `?`. Review material source conflicts and transformations without repeating a full extraction unless explicitly requested.

For **each of GE and TE**, inspect the corresponding saved per-source SPPR matrix. List every column containing negative SPPR and the affected group names/IDs under that column. A positive row total can conceal a negative contribution. Check all retained groups, including unfished groups, and do not silently apply researcher exclusion notes to saved matrices. Use the detailed identity and missing-data rules in the evidence reference.

Report rho_living, GE recycling parameter b, and named detritus-pool SPPR from matching saved diagnostics. Use compact verdict, sign and metric paragraphs, with readable rounded display values and relevant balance findings. Preserve researcher rounding and manual breaks. Keep the cells to material scientific findings and numerical diagnostics. Record exact status, unavailable matrices and verification details in supporting evidence; place a material timing/configuration note once in Other when needed. Do not imply new verification or conceal a material failure. Recommend a confirmed fresh run when a material gap cannot be resolved from existing evidence; use the approval rules above. Preserve the manual SPPR calculation, open-issues and review cells.

### 4. Review all taxon mappings

Create one audit row for every catch taxon in the chosen year/basis universe. Join by exact taxon and model/group identifiers; validate duplicates before aggregating. Read source membership evidence and existing allocation assumptions, checking online primary/authoritative sources when needed to establish or verify a claim. Record what each reference supports.

Apply the guide's membership and weight rules separately; the weaker necessary confidence determines the taxon's overall category. Preserve supported assignments and known partial weights. Show unresolved weights as `?`; do not invent equal weights or use a numerical placeholder as evidence of resolution.

A report may assign a higher or lower **review confidence** when a documented reassessment supports it. Do not preserve an unsupported old rating or aim for upgrades. Preserve the stored label in supporting evidence and leave the workbook untouched unless confidence adoption is authorized. Review existing High/Medium and zero-catch records as carefully as Low/Very low. Follow the guide's distinctions between operative size/habitat criteria, reporting scope, historical taxonomy, pair membership and internal stage weights. Proposed new mappings/weights remain proposals, excluded from the adopted mapping summary until authorized; uncertainties in existing decisions can still be documented now.

For an explicitly approved fallback, apply the guide’s eligible-group catch-first then biomass hierarchy, with Medium allocation confidence for both. Record exact candidate decisions, fields/values/proportions and assumptions in adopted records. Prefer a meaningful M10/M11 Very low placement over leaving an uncertain taxon unresolved. Applicable direct geographic source quantities support High allocation confidence; otherwise retain the catch/biomass hierarchy and consider a justified W11 last resort. Only genuinely undecidable placements/allocations remain unresolved. Approval already given for the stated adoption/dependent arithmetic does not require a second permission request and does not authorize fresh extraction or group-SPPR regeneration.

### 5. Calculate the summary and appendix

Use the same audit rows for both outputs. Calculate catch and independent simple-chain PPR totals, the five confidence categories (High, Medium, Low, Very low, Unresolved) and their shares. The simple-chain coefficient comes from the classic-PPR data, not GE/TE SPPR or an Ecopath group's TL. Apply the documented carbon conversion exactly once.

Include unresolved taxa in the catch denominator and, whenever their simple-chain PPR is known, in that PPR denominator. Distinguish missing coefficients from annual contributions: zero recorded catch gives zero PPR even if TL/coefficient is unavailable; positive catch with a missing coefficient gives unknown PPR. Label an incomplete subtotal known PPR only when unknown contributions remain. Count a split taxon once. Distinguish source ecological groups from synthetic computational imports.

Create the linked Excel workbook with a separate descriptive Sources sheet and the seven-column appendix: **Taxon name; TL; Catch (t); Simple-chain PPR (t C); Mapped group names and weights; Confidence level; Reason.** Sort by unrounded simple-chain PPR numerically descending, with unavailable values last and taxon name breaking ties. State year, basis, method and units once above it; put full descriptive sources on the Sources sheet. Freeze headers, enable filtering and verify widths/wrapping.

Move mapping and coverage outside the main validation table. After the confidence/rule summaries, include the separate **Very low decisions** table (**Affected taxa | Why confidence is very low**) from the exact current appendix, covering every Very low taxon once; do not replace the rule tables or borrow another model's reasons. Include the five-category summary and separate group-assignment/allocation tables with exact columns **Plain-language rule | Confidence | PPR percentage**. Describe actual rules in words, split component confidence levels, and account for the full known-PPR universe once per table. Check internally that these are two views of the same taxa and cannot be added; do not repeat this explanation in the report. For authorized adoption or a requested map comparison, trace and reconcile the actual map controls/payload/display with this denominator; an annual-workbook check alone is insufficient. Reuse adequate saved matching evidence for ordinary drafting and preserve its scope.

### 6. Assess geography and time

Define R as the target region and S as the selected model's study area. Report A = 100 × overlap/R and B = 100 × overlap/S. Prefer appropriate area measurements; use documented tracing, georeferencing or visual estimates when exact polygons are absent. Identify approximation/range and evidence. Different image scales must not become a raw pixel-area comparison. Missing coordinates alone are not grounds to report no estimate.

Use the figure matching this particular model, not another study within the same article. Attach readable region and study-area figures with source and page information. Explain material model-period/catch-year differences and fixed-weight extrapolation concisely.

### 7. Produce and verify the report

Apply the [evidence handoff contract](../../paper-to-ppr/references/evidence-handoff.md) and the [approved adoption and denominator checks](document-production.md#approved-adoption-and-denominator-checks). Final report classifications, mappings and figures must agree with adopted regional data and the map. If review differs from adoption, keep a keyed discrepancy ledger and label the report a pending-alignment draft; report-only reclassification is not completed validation. Changing data or publishing requires explicit adoption authorization. The evidence index is provenance, not configuration authority.

Follow the document-production reference. Fill a copy of the current template, or minimally update the explicitly authorized edited report. Copy needed evidence without moving originals; retain useful relative links and source IDs. Keep extended method/rule instructions out of the filled report.

Verify count/share arithmetic, mapping completeness, exact source-to-group negative pairings, appendix ordering, units, evidence links and preservation of manual entries. Render and inspect every page, including the separate coverage section; also inspect the Excel appendix. Fix layout defects before delivery.

After an explicitly authorized researcher signoff adoption, use the [bounded Project/map handoff](researcher-signoff-and-map.md); any later Word edit requires fresh registration and source-to-map equality checks. Do not start new scientific validations or a full rebuild for a notes-only sync.

Keep the report scientific and concise: name unresolved taxa and their specific reasons (or state none), flag Very low assignments and their coverage share, and omit skill/integration/test narratives. Deliver the Word file, linked Excel appendix and a short statement of material evidence gaps and checks actually performed. Do not claim fresh extraction, recalculation, approval or a successful regional test unless it happened within the authorized scope. Stop at any user-requested review point.

