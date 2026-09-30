---
name: ecopath-model-validation
description: Use when creating, updating, or reviewing a regional Ecopath model validation record in GlobalPPREstimation, including GE/TE diagnostics, taxon mapping confidence and catch/PPR coverage, geographic fit, and the linked Excel mapping appendix. Full extraction or scientific recalculation belongs to the paper-to-PPR workflow.
---

# Ecopath model validation

Produce a concise, evidence-based Word validation record for one region and one exact model version, using the agreed template. The record supports researcher review; it does not approve the model. Explicitly authorized mapping adoption and dependent recalculation follow the adoption gate below; an ordinary report request remains read-only scientifically.

## Resources and precedence

Resolve this directory as `skill_root`; its third parent is the repository root containing `Project.xlsx`, `regions` and `tools`. Resolve relative links from the file containing them, not the current working directory.

- Read the [project workbook contract](../../../README.md#workbook-reference).
- Read the complete [template filling guide](../../templates/Model_validation_template_instructions.md). It owns field definitions, confidence rules M1–M12/W1–W11/C1–C6, examples, denominator conventions, appendix ordering and geographic approximation rules.
- Use [Model_validation_template.docx](../../templates/Model_validation_template.docx) as the report layout. Do not fork a second template or duplicate the full guide inside this skill.
- Apply the guide's [portable-link rules](../../templates/Model_validation_template_instructions.md#links-output-and-verification) to reports, appendices and current supporting documents: repository-local links are relative to their containing file so another user can download or clone the repository and retain navigation. Preserve public URLs and internal anchors, and verify relocation.
- Read [evidence and calculations](references/evidence-and-calculations.md) before collecting or aggregating evidence, then [document production](references/document-production.md) before authoring. Apply [acceptance checks](references/acceptance-checks.md) before delivery.
- Consult the [paper-to-PPR entry point](../original_skill_resources/combined-src/SKILL.md) and only the relevant scientific references for interpretation. Its execution commands are not automatically authorized by a validation request.
- Use the available documents skill for Word work and the spreadsheets skill for workbook analysis. Load the bundled workspace runtimes before artifact work. If a required capability is absent, use an appropriate available equivalent and disclose the limitation.

Current user instructions and edits govern the task. If an older document or pipeline reference conflicts with this report's agreed format, apply the current template guide. In particular, geographic approximation is allowed and the report has GE and TE rows only.

## Scope and review boundaries

An ordinary validation request authorizes reading relevant permitted evidence, checking sources, performing report arithmetic, preparing supporting review records, and generating the Word report. It does **not** authorize running extraction or SPPR again, changing catch/mappings/weights/TLs, selecting another model, updating workbook results, or refreshing the project/map.

Reuse adequate saved outputs. When they are insufficient, **recommend a fresh scientific paper-to-PPR run if necessary**. Explain the specific gap or conflict, why further read-only review cannot resolve it, the smallest sufficient stages, the expected result and which files/results would be created or affected. Use the [rerun decision and approval rules](references/evidence-and-calculations.md#when-to-recommend-a-fresh-scientific-run).

**Always ask the user before each proposed fresh scientific run and wait for explicit confirmation of that run.** A validation request, a recommendation to rerun, or approval of this skill does not authorize execution. Once the user confirms the concrete proposal, execute only that approved scope through the current paper-to-PPR workflow; do not ask again for the same approved run. A further or expanded run requires a new explanation and confirmation. Keep proposed numerical repairs and adoption into workbooks/maps explicit in the proposal; approval to recompute is not blanket approval to change the model or publish results.

Finish independent validation work from existing evidence before the approval request, and keep only dependent findings pending. If the user declines or defers the run, deliver the available report with those limitations and the recommendation recorded.

Respect file exclusions from the conversation before reading, hashing, copying or rendering any file. A later explicit instruction can authorize a named file without lifting unrelated exclusions. Never read an excluded file merely to verify it was unchanged. Preserve user-edited originals and active application sessions.

A request to draft or revise this skill/template ends with that artifact for review. Run a regional test only after the user has reviewed it and authorized proceeding. Do not treat elapsed time, a tool returning no answer, or creation of this skill as that authorization.

## Workflow

### 1. Establish the exact target

Resolve the supplied region folder or workbook. Read `Overview / Settings` for the selected model, path, reference year and catch basis. Explicit user choices override the report's default year/basis; record the choice without changing Overview.

If a different candidate is explicitly named, label the report as a candidate review and preserve the actual selection. If the target or required year/basis cannot be determined, inspect the available context and ask only for the unresolved choice. A missing model selection does not authorize choosing one.

Identify any authorized researcher-edited record. Capture its text, table cells and complete hyperlink targets, including anchors. Compare it with the template and existing report only as needed to preserve edits. Do not restore deleted prose or links automatically.

### 2. Establish evidence identity

Read the regional workbook once where practical, the relevant central paper/model records, and exact-model source and diagnostic files. Keep source tables, canonical JSON, computational input, loaded state, and saved diagnostic outputs distinguishable.

Check model IDs, group IDs, periods, source scope, method, runtime settings and available provenance. Reuse an existing validation bundle only when its identity matches the current inputs; its presence is not proof of freshness. Use targeted hashes or recorded identities for permitted inputs, not an indiscriminate repository scan.

Build a compact supporting evidence record with source locations, model/configuration identity, review findings and unavailable items. It is report provenance, never an authoritative selection/status/configuration sidecar.

### 3. Review model context and diagnostics

Populate article/model fields and known alternatives. Keep Article and Model selection rationales separate; preserve a recorded reason or show `?`. Review material source conflicts and transformations without repeating a full extraction unless explicitly requested.

For **each of GE and TE**, inspect the corresponding saved per-source SPPR matrix. List every column containing negative SPPR and the affected group names/IDs under that column. A positive row total can conceal a negative contribution. Check all retained groups, including unfished groups, and do not silently apply researcher exclusion notes to saved matrices. Use the detailed identity and missing-data rules in the evidence reference.

Report rho_living, GE recycling parameter b, and named detritus-pool SPPR from matching saved diagnostics. Keep the cells to sign findings and numerical diagnostics. Record exact status, unavailable matrices and verification details in supporting evidence; place a material timing/configuration note once in Other when needed. Do not imply new verification or conceal a material failure. Recommend a confirmed fresh run when a material gap cannot be resolved from existing evidence; use the approval rules above. Preserve the manual SPPR calculation, open-issues and review cells.

### 4. Review all taxon mappings

Create one audit row for every catch taxon in the chosen year/basis universe. Join by exact taxon and model/group identifiers; validate duplicates before aggregating. Read source membership evidence and existing allocation assumptions, checking online primary/authoritative sources when needed to establish or verify a claim. Record what each reference supports.

Apply the guide's membership and weight rules separately; the weaker necessary confidence determines the taxon's overall category. Preserve supported assignments and known partial weights. Show unresolved weights as `?`; do not invent equal weights or use a numerical placeholder as evidence of resolution.

A report may assign a higher or lower **review confidence** when a documented reassessment supports it. Do not preserve an unsupported old rating or aim for upgrades. Preserve the stored label in supporting evidence and leave the workbook untouched unless confidence adoption is authorized. Review existing High/Medium and zero-catch records as carefully as Low/Very low. Follow the guide's distinctions between operative size/habitat criteria, reporting scope, historical taxonomy, pair membership and internal stage weights. Proposed new mappings/weights remain proposals, excluded from the adopted mapping summary until authorized; uncertainties in existing decisions can still be documented now.

For an explicitly approved fallback, apply the guide’s eligible-group catch-first then biomass hierarchy, with Medium allocation confidence for both. Record exact candidate decisions, fields/values/proportions and assumptions in adopted records. Prefer a meaningful M10/M11 Very low placement over leaving an uncertain taxon unresolved. Applicable direct geographic source quantities support High allocation confidence; otherwise retain the catch/biomass hierarchy and consider a justified W11 last resort. Only genuinely undecidable placements/allocations remain unresolved. Approval already given for the stated adoption/dependent arithmetic does not require a second permission request and does not authorize fresh extraction or group-SPPR regeneration.

### 5. Calculate the summary and appendix

Use the same audit rows for both outputs. Calculate catch and independent simple-chain PPR totals, the five confidence categories (High, Medium, Low, Very low, Unresolved) and their shares. The simple-chain coefficient comes from the classic-PPR data, not GE/TE SPPR or an Ecopath group's TL. Apply the documented carbon conversion exactly once.

Include unresolved taxa in the catch denominator and, whenever their simple-chain PPR is known, in that PPR denominator. Distinguish missing coefficients from annual contributions: zero recorded catch gives zero PPR even if TL/coefficient is unavailable; positive catch with a missing coefficient gives unknown PPR. Label an incomplete subtotal known PPR only when unknown contributions remain. Count a split taxon once. Distinguish source ecological groups from synthetic computational imports.

Create the linked Excel workbook with a separate descriptive Sources sheet and the seven-column appendix: **Taxon name; TL; Catch (t); Simple-chain PPR (t C); Mapped group names and weights; Confidence level; Reason.** Sort by unrounded simple-chain PPR numerically descending, with unavailable values last and taxon name breaking ties. State year, basis, method and units once above it; put full descriptive sources on the Sources sheet. Freeze headers, enable filtering and verify widths/wrapping.

Move mapping and coverage outside the main validation table. Include the five-category summary and separate group-assignment/allocation tables with exact columns **Plain-language rule | Confidence | PPR percentage**. Describe actual rules in words, split component confidence levels, and account for the full known-PPR universe once per table. Check internally that these are two views of the same taxa and cannot be added; do not repeat this explanation in the report. Trace and reconcile the actual map controls/payload/display with this denominator; an annual-workbook check alone is insufficient.

### 6. Assess geography and time

Define R as the target region and S as the selected model's study area. Report A = 100 × overlap/R and B = 100 × overlap/S. Prefer appropriate area measurements; use documented tracing, georeferencing or visual estimates when exact polygons are absent. Identify approximation/range and evidence. Different image scales must not become a raw pixel-area comparison. Missing coordinates alone are not grounds to report no estimate.

Use the figure matching this particular model, not another study within the same article. Attach readable region and study-area figures with source and page information. Explain material model-period/catch-year differences and fixed-weight extrapolation concisely.

### 7. Produce and verify the report

Apply the [evidence handoff contract](../original_skill_resources/combined-src/references/evidence-handoff.md) and the [approved adoption and denominator checks](references/document-production.md#approved-adoption-and-denominator-checks). Final report classifications, mappings and figures must agree with adopted regional data and the map. If review differs from adoption, keep a keyed discrepancy ledger and label the report a pending-alignment draft; report-only reclassification is not completed validation. Changing data or publishing requires explicit adoption authorization. The evidence index is provenance, not configuration authority.

Follow the document-production reference. Fill a copy of the current template, or minimally update the explicitly authorized edited report. Copy needed evidence without moving originals; retain useful relative links and source IDs. Keep extended method/rule instructions out of the filled report.

Verify count/share arithmetic, mapping completeness, exact source-to-group negative pairings, appendix ordering, units, evidence links and preservation of manual entries. Render and inspect every page, including the separate coverage section; also inspect the Excel appendix. Fix layout defects before delivery.

Keep the report scientific and concise: name unresolved taxa and their specific reasons (or state none), flag Very low assignments and their coverage share, and omit skill/integration/test narratives. Deliver the Word file, linked Excel appendix and a short statement of material evidence gaps and checks actually performed. Do not claim fresh extraction, recalculation, approval or a successful regional test unless it happened within the authorized scope. Stop at any user-requested review point.
