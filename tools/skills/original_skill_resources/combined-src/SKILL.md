---
name: ecopath-paper-to-ppr
description: Use when working on the Global PPR pipeline, from Ecopath papers, supplements or existing models through taxonomy, SPPR diagnostics, catch matching, regional PPR/NPP, model selection, registry and atlas updates, or any requested subset.
---

# From an Ecopath paper to regional PPR

This is the project's single active workflow skill. Use it for a complete pipeline or a requested stage; extraction-only, diagnostics-only, matching-only and registry-only requests retain their boundaries. Independent classic PPR or NPP does not require an Ecopath model.

Resolve `<skill-root>` as the directory containing this file and `<repo-root>` as the ancestor containing `Project.xlsx`. Read the [project guide and workbook contract](../../../../README.md#workbook-reference) and the named regional workbook's Overview. This entry point lives in the original `combined-src` directory; its updated instructions supersede archived Claude/Codex copies. Repository commands run from `<repo-root>`. Relative links resolve from the document containing them.

Read the [evidence, execution and adoption contract](references/evidence-handoff.md) for each requested stage. Its inventory and reconciliation checks are required for a complete handoff; incomplete evidence and unadopted review proposals must remain explicit. Existing explicit run authorization is respected without redundant confirmation.

For catch mapping, prefer approaching 100% catch coverage with openly stated assumptions over leaving taxa unresolved merely to preserve certainty. Apply this skill’s [broader mapping definitions and confidence rules](references/regional-calculation.md#broader-mapping-definitions-and-confidence): Very low broad-category and closest-analogue placements, including meaningful taxonomic, geographic and habitat approximations. Reserve Unresolved for cases with no meaningful assignment or usable allocation. Prefer applicable direct geographic source data for High-confidence allocation, then model catch proportions and biomass proportions for Medium allocation confidence; consider a justified Very low numerical rule if these fail. Keep the weaker membership/weight confidence overall. Preserve saved group SPPR and record candidates, values, proportions, source limits and assumptions. Report unresolved taxa/reasons and flag Very low decisions briefly; keep process and integration details in supporting evidence. For validation outputs follow the [single report contract](../../../../templates/Model_validation_template_instructions.md): concise findings, separate supporting verification, preserved researcher edits, and correct zero-catch versus missing-TL treatment. Do not regenerate deleted explanatory prose.

## Choose the requested stages

| Input or request | Read and perform |
|---|---|
| Paper, supplements, native export, EcoBase candidate, or model selection | [Model preparation](references/model-preparation.md); use [online recovery](references/missing-data-recovery.md) when inputs are missing and the [reconstruction audit](references/reconstruction-audit.md) for every extraction/conversion/load review |
| Group membership or full paper-to-PPR chain | [Taxonomy](references/group-taxonomy.md); capture membership during the same source reading as parameters |
| Model diagnostics | [Direct diagnostics](references/direct-diagnostics.md): full direct GE, TE and With Egestion returns by default; global and Monte Carlo require a broader request |
| Catch preparation, matching, coefficients, PPR, NPP or model comparison | [Regional calculation](references/regional-calculation.md) |
| Catch taxon split between size, age, life-stage or cohort groups; assumed allocation or coverage improvement | [Size/stage allocations](references/size-stage-allocations.md), then regional calculation; search online before a model-catch proxy |
| Registry consolidation, map refresh or knowledge graph update | [Project integration](references/project-integration.md) |

For a full regional pipeline, carry source recovery → extraction → taxonomy → diagnostics → authorized selection → catch matching → eligible PPR/NPP → requested project integration through to completion. Record blockers and finish independent authorized stages. Do not infer permission to select a model or introduce a numerical repair from a request to extract it.

## Scientific and project contract

- Keep source evidence, canonical JSON, explicit computational input and loaded calculator state distinguishable. Unknowns are not zero; loader defaults, solved parameters and authorized adjustments need evidence and a transformation ledger.
- Preserve exact group IDs, names and model structure. Group membership links extraction to catch mapping; source table purpose and geographic applicability matter. Retain eight EwE imports, round-trip checks, source balance evidence and taxonomy when applicable.
- Regional Overview owns selection and rationale. Project.xlsx owns central paper/model metadata. A selected FAIL or NOT_RUN model remains selected with restrictions; it does not acquire validated annual estimates. Explicitly authorized provisional display may use existing numeric coefficients with all diagnosis flags retained; never fabricate missing coefficients or promote a diagnosis. Archive/clear stale model results with `prepare-selection`; preserve catch, classic PPR and NPP.
- Every saved model-selection change includes updating Project.xlsx, rebuilding the map, time-series and archive pages, and verifying the displayed selection under [Project integration](references/project-integration.md). No separate refresh request is needed unless the user explicitly defers it. Check remembered browser model choices as well as generated defaults.
- Keep diagnostic returns separate from source interpretation and proposed repairs. Apply the explicit coverage preference above, reporting the catch share dependent on Very low assumptions. Do not fabricate observed weights or hide weak placements to meet a target.
- For a careful confidence reassessment, inspect all requested taxa, including existing High/Medium and zero-catch labels. Use exact group definitions, reporting scope and historical taxonomy; separate candidate eligibility from stage/weight uncertainty and model applicability. Record evidence-backed upgrades and downgrades, preserve numerical assignments during confidence-only review, and integrate reusable lessons in the existing references.
- When no better focal-model mapping can be supported, use mappings from geographically nearby models as a documented fallback. Verify the donor evidence and crosswalk compatible group definitions to the selected model; record geographic/ecological transfer and its confidence. Nearby location alone does not justify copying group IDs, allocation weights or SPPR coefficients.
- When the user authorizes assumed size/stage allocations, work on selected model-region pairs only, keep one mapping per pair, search online first, and record every adopted assumption, zero candidate and unresolved case using the allocation reference. Higher coverage is not validation.
- Serialize central writes, preserve unrelated records, and verify exact saved input/configuration before using coefficients. Never rewrite freshness hashes to bypass checks.

Detailed scientific procedures, scripts, templates and examples remain in the retained domain resources explicitly linked by the stage references. Their historical output paths and broad exporter commands are not the current execution contract. Read only the relevant references; no separate preparation, calculation or integration skill is required.
