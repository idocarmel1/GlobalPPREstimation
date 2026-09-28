---
name: ecopath-paper-to-ppr
description: Use when working on the Global PPR pipeline, from Ecopath papers, supplements or existing models through taxonomy, SPPR diagnostics, catch matching, regional PPR/NPP, model selection, registry and atlas updates, or any requested subset.
---

# From an Ecopath paper to regional PPR

This is the project's single active workflow skill. Use it for a complete pipeline or a requested stage; extraction-only, diagnostics-only, matching-only and registry-only requests retain their boundaries. Independent classic PPR or NPP does not require an Ecopath model.

Resolve `<skill-root>` as the directory containing this file and `<repo-root>` as the ancestor containing `Project.xlsx`. Read the [project guide and workbook contract](../../../../README.md#workbook-reference) and the named regional workbook's Overview. This entry point lives in the original `combined-src` directory; its updated instructions supersede archived Claude/Codex copies. Repository commands run from `<repo-root>`. Relative links resolve from the document containing them.

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
- Keep diagnostic returns separate from source interpretation and proposed repairs. Match supported taxa and report catch-tonnage coverage without inventing weights to meet a coverage target.
- When the user authorizes assumed size/stage allocations, work on selected model-region pairs only, keep one mapping per pair, search online first, and record every adopted assumption, zero candidate and unresolved case using the allocation reference. Higher coverage is not validation.
- Serialize central writes, preserve unrelated records, and verify exact saved input/configuration before using coefficients. Never rewrite freshness hashes to bypass checks.

Detailed scientific procedures, scripts, templates and examples remain in the retained domain resources explicitly linked by the stage references. Their historical output paths and broad exporter commands are not the current execution contract. Read only the relevant references; no separate preparation, calculation or integration skill is required.
