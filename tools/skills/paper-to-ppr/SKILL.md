---
name: ecopath-paper-to-ppr
description: Use when working on the Global PPR pipeline, from Ecopath papers, supplements or existing models through taxonomy, SPPR diagnostics, catch matching, regional PPR/NPP, model selection, registry and atlas updates, or any requested subset.
---

# From an Ecopath paper to regional PPR

Use this active pipeline skill for a complete chain or a requested operation. Resolve this directory as `skill_root` and the ancestor containing Project.xlsx as `repo_root`; commands run from that root and links resolve from their containing file.

## Route before detailed reading

Choose the requested operation using the shared [operation and dependency contract](references/operation-contract.md). Read root [AGENTS.md project_contract](../../../AGENTS.md#project_contract), [README](../../../README.md), [agent project contract](../../../explainers/agents/project_contract.md) before modifying project content. An unchanged contract already read in this context need not be repeated; new contexts read it. Read only the route's additional references and relevant saved inputs.

| Request | Route |
|---|---|
| Explain a field/saved result | Explain; relevant definition/table only, no new evidence package |
| Existing registered model selection | Selection; one regional refresh, no extraction or broad diagnostics |
| Regional arithmetic/PPR/NPP | Arithmetic; compatible retained coefficients/inputs |
| Named mapping or confidence | Targeted mapping; only affected decisions/dependencies |
| Paper/native/JSON extraction | Extraction; requested model/period and applicable taxonomy |
| Model diagnostics | Direct diagnostics; GE/TE/With Egestion default, full returns |
| Registry/map publication | Applicable integration scope and existing freshness/serialization guards |
| Complete paper-to-PPR | Union of applicable scientific stages; finish all authorized stages |
| Word/report/review task | [Validation skill](../ecopath-model-validation/SKILL.md), its applicable bounded or full route |

For extraction, taxonomy, diagnostics, mapping or scientific pipeline work, read the [scientific contract](references/scientific-contract.md) and the route's named stage references. Its exact source/missingness, mapping-confidence, uncertainty and adoption rules remain mandatory for those stages. Apply [evidence handoff](references/evidence-handoff.md) to the actual scientific stages performed; a definition, wording edit or review metadata sync does not create a full extraction/diagnostic inventory.

For a composed pipeline and validation run, perform taxon-to-group mapping once under the shared [single mapping handoff](references/operation-contract.md#one-mapping-stage-per-pipeline-run). Gather both routes' membership, weight and confidence requirements before that stage; validation consumes and checks its same keyed decisions rather than starting another mapping pass.

For authorized registry/map changes read [project integration](references/project-integration.md) for that operation. Existing selection uses `python tools/cli/region.py refresh --region regions/<type>/<unit>` and automatically publishes its dependent saved selection; it does not confer numerical readiness or approval. Do not guess a new publication's citation/coverage or rewrite freshness hashes.

## Boundaries that apply to every route

Preserve scientific input values, exact model/group/taxon identities, missingness, diagnostic FAIL/NOT_RUN/provisional restrictions, uncertainty and researcher edits. Model JSON, documented departures and ephemeral loaded state have distinct roles. Root structure defines one canonical model.json with adjacent model_notes.md and latest-only extractions; canonical discovery and model-local outputs own navigation.

Selection, loadability, construction, readiness and researcher approval are separate. Independent Catch/Classic PPR/NPP survive model switches. Existing explicit scientific execution/adoption authorization is respected without asking again; an extraction request does not authorize selection or numerical repairs. Apply continuing exclusions before any read/hash/copy/render. Proposals remain proposals until authorized adoption.

Use content/dependency identity checks and recheck mutable inputs before publication. Serialize central writes and preserve rollback/stale-page guards. Reuse compatible saved material honestly; report only stages actually independently completed or regenerated and name incomplete stages. No broad Monte Carlo follows from a simple action.

The detailed scientific resources remain conditional linked references. Their historical paths/exporter commands do not override the current structure and operation contract.
