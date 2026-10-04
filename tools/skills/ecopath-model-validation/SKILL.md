---
name: ecopath-model-validation
description: Use when creating, updating, or reviewing a regional Ecopath model validation record in GlobalPPREstimation, including GE/TE diagnostics, taxon mapping confidence and catch/PPR coverage, geographic fit, the linked Excel mapping appendix, and an explicitly authorized signed-review handoff to Project/map. Full extraction or scientific recalculation belongs to the paper-to-PPR workflow.
---

# Ecopath model validation

Create or update the requested review artifact or review information for one exact regional model. A report supports researcher review; it does not approve a model or authorize scientific recalculation.

## Route before detailed reading

Use the shared [operation and dependency contract](../paper-to-ppr/references/operation-contract.md). Read root [AGENTS.md project_contract](../../../AGENTS.md#project_contract), [README](../../../README.md), [agent project contract](../../../explainers/agents/project_contract.md) before edits. Reuse an unchanged contract already read in this context; new contexts read it. Resolve this directory as `skill_root`, root as the ancestor containing Project.xlsx, and links from their containing file.

| Request | Additional reading and work |
|---|---|
| Explain a definition/saved result | Relevant definition and named saved evidence only; no generated artifacts or full review |
| Edit named wording/formatting | [Document production](references/document-production.md) preservation/link/render sections and relevant field definition; preserve unaffected scientific/manual content and inspect every output page |
| Synchronize actual signed review/notes | [Signoff handoff](references/researcher-signoff-and-map.md); latest source and exact current review identities; bounded metadata/page checks only |
| Review one mapping/confidence | Shared targeted-mapping route; named taxa, applicable membership/weight rules and affected denominators; do not reassess unrelated taxa |
| Full model validation | Complete [template guide](../../templates/instructions.md), [full workflow](references/full-validation.md), [evidence/calculations](references/evidence-and-calculations.md), document-production and [acceptance checks](references/acceptance-checks.md) |
| Fresh extraction/diagnostics/arithmetic or selection | [Pipeline skill](../paper-to-ppr/SKILL.md), only the authorized scientific/selection stages |

The shared router scopes detailed reads; it does not reduce the mandatory scientific universe or QA for a full validation. Full review retains GE/TE full negative source/group pairings, all catch taxa including zero rows, mapping assumptions/confidence, geography/time, complete denominator checks and the rendered report/appendix. Direct pipeline diagnostics retain their separate GE/TE/With Egestion contract.

When validation follows mapping in the same pipeline run, use the shared [single mapping handoff](../paper-to-ppr/references/operation-contract.md#one-mapping-stage-per-pipeline-run). Check and report that stage's exact decisions; do not repeat taxon research, group assignment or weight/confidence resolution. If a required input changed or the handoff lacks evidence, record the gap and return only affected decisions to the same mapping stage within existing authorization.

Use the existing [validation.docx](../../templates/validation.docx) layout and relevant [template field/rule definitions](../../templates/instructions.md); do not fork a second template or duplicate the guide. Word operations use the available documents skill and applicable full rendering workflow; spreadsheet operations use the available spreadsheets skill and bundled runtimes. Definition-only tasks do not require artifact runtimes or a new evidence package.

Keep repository-local links relative to the containing document; preserve public URLs, internal anchors, manual cells/breaks, rounding, signatures, researcher edits and deleted prose. Current user instructions/edit scope govern the task. Accepted manual scientific inputs remain protected: mapping authorization does not authorize restoring publication parameters, normalizing canonical diets or rebalancing. Keep source departures and remaining concerns explicit.

## Scope and review boundaries

For an explicitly authorized adoption of a researcher-signed final report, follow [researcher signoff and map](references/researcher-signoff-and-map.md): register the actual source and refresh only its review metadata. Support both `MODEL VALIDATED` and `MODEL DISQUALIFIED`. A disqualification is a completed negative review: preserve its exact reason and latest signed date, display the Ecopath model heading/name in red, and exclude it from the validated-only filter. It does not authorize scientific recalculation, reselection or adoption of draft group-removal notes. Signoff and this adoption are distinct from drafting a report.

An ordinary validation request authorizes reading relevant permitted evidence, checking sources, performing report arithmetic, preparing supporting review records, and generating the Word report. It does **not** authorize running extraction or SPPR again, changing catch/mappings/weights/TLs, selecting another model, updating workbook results, or refreshing the project/map.

Reuse adequate saved outputs. When they are insufficient, **recommend a fresh scientific paper-to-PPR run if necessary**. Explain the specific gap or conflict, why further read-only review cannot resolve it, the smallest sufficient stages, the expected result and which files/results would be created or affected. Use the [rerun decision and approval rules](references/evidence-and-calculations.md#when-to-recommend-a-fresh-scientific-run).

**Ask the user before a fresh scientific run that is not already covered by explicit session authorization, and wait for confirmation.** An ordinary validation request, a recommendation to rerun, or approval of this skill does not authorize execution. When the user explicitly authorizes necessary runs within a defined regional validation/integration scope, explain the concrete gap and setup and proceed within that scope without requesting the same authorization again. Further execution outside the authorized scope requires a new explanation and confirmation. Keep numerical repairs and adoption into workbooks/maps distinct: approval to recompute is not blanket approval to change accepted model parameters or publish results.

Finish independent validation work from existing evidence before the approval request, and keep only dependent findings pending. If the user declines or defers the run, deliver the available report with those limitations and the recommendation recorded.

Respect file exclusions from the conversation before reading, hashing, copying or rendering any file. A later explicit instruction can authorize a named file without lifting unrelated exclusions. Never read an excluded file merely to verify it was unchanged. Preserve user-edited originals and active application sessions.

A request to draft or revise this skill/template ends with that artifact for review. Run a regional test only after the user has reviewed it and authorized proceeding. Do not treat elapsed time, a tool returning no answer, or creation of this skill as that authorization.

## Authoritative output ownership

Read [the agent project contract](../../../explainers/agents/project_contract.md) under root project_contract before editing. Each exact model owns model_validation/validation.docx, taxon_mapping.xlsx and evidence/. Canonical model.json and model_notes.md are adjacent in that model. Keep departures and their evidence in model_notes.md and link them from the extraction row. Use the regional workbook and `python tools/cli/region.py refresh --region regions/<type>/<unit>` for an authorized selection change. Preserve complete model-local snapshots, researcher edits, uncertainty and current independent tables; no legacy extraction payloads or authority sidecars.
