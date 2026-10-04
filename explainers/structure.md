# Authoritative project structure

This document is the directory and ownership contract required by root [AGENTS.md](../AGENTS.md#project_contract) and both active project skills. The agreements in [the reorganization plan](plans/project_reorganization_plan.md) govern this migration. Plans stay in `explainers/plans/`; implementation and verification are recorded there. Scientific behavior is governed by the retained scientific methods and evidence, never by a folder name.

## Regions, papers and models

Regions live at `regions/{LME,EEZ,HS}/<unit_id>/`. Preserve IDs and `<unit_id>.xlsx` names. The regional root contains its workbook, generated `selected_model.lnk`, optional `raw/`, `papers/`, `ecobase/`, and `work/`. Region raw inputs use `raw/catch/`, `raw/npp/`, and `raw/geography/`.

A paper owns `papers/<paper_id>/sources/` (with optional `supplements/` and `context/`), `source_manifest.json`, and `models/<model_id>/`. One paper can own several periods/scenarios, for example `papers/P/models/period_A/` and `papers/P/models/period_B/`. JSON-only EcoBase candidates use `ecobase/<model_id>/` with the identical model layout. Identity and provenance determine ownership; discovery must never guess citations, chronology or coverage.

Every distinct regional model has exactly one canonical `model.json` and adjacent `model_notes.md`. Notes contain Source identity; Modeled period and area; Departures from the publication; Evidence links. Departures identify fields/groups, published and retained values including missingness, rationale, limitations, actual decision provenance and source locators when available. Unknown provenance remains unknown. Notes may state that departures have not been assessed; absence of evidence is not proof of source fidelity. Canonical JSON remains a supported Ecopath export. Administrative fields belong outside scientific JSON. Do not create `source_model.json`, `computational_input.json`, or a loaded-model JSON.

The model owns these optional fixed destinations:

- `sppr_source.xlsx`: exact coefficient source.
- `inputs/native/` and `inputs/provenance.json`: original native inputs and their roles.
- `extracted_tables/`: latest EwE import tables, published companions, `Taxonomy.xlsx`, and `evidence/`.
- `results/regional_snapshot.xlsx`, `results/result_manifest.json`, and `results/diagnostics/`.
- `model_validation/validation.docx`, `taxon_mapping.xlsx`, and `evidence/` containing `evidence_index.json`, `source_review/`, `geography/`, and `mapping/` when applicable.
- `model_validation/work/<run_id>/{inputs,outputs,code,qa}/` for validation work.

The existing `runtime_equivalence.json` beside the Java Sea model is a compatibility certificate, not another model representation or selection authority. It stays at the loader's current certificate location; its historical bridge is unavailable after the superseded extraction was removed, so it cannot make the current numerical results ready.

Keep only the most updated extraction of each distinct model. Determine lineage from identity, period, area, scenario and recorded corrections; modification time is insufficient. Remove older extraction packages, audits, renders and builders without merging their unique evidence into the latest package. Record losses and affected results. Original publications/native source inputs and genuinely frozen cross-model study inputs are different roles. Scientifically distinct variants remain distinct models.

## Selection and results

The regional Overview owns editable `selected_model_id` and `selection_rationale`. `model_path` is generated. Project.xlsx owns human paper/model metadata and explicit review records; its selected flags, paths and regional summaries are derived. HTML is generated. No sidecar, shortcut or manifest is an editable selection authority.

The single command is `python tools/cli/region.py refresh --region regions/LME/LME_028`. Adding a publication/model requires its scientific registration once; choosing an existing registered model requires only the Overview choice/rationale and refresh. Available model IDs come from canonical discovery. Discovery ignores work copies, snapshots and shortcuts and rejects duplicate identities.

Snapshots are complete byte-for-byte regional workbook copies, including all sheets, manual content, formatting and links. Save outgoing results using `results_model_id` even if Overview already requests another model. Record both identities honestly. Keep one useful snapshot per model; a pending empty workbook cannot replace it. Manifests record actual or explicitly unknown historical flags/code identity, model/source/workbook hashes and separate dependency hashes. They do not confer approval.

Restore only explicitly compatible model-dependent groups, coefficients, matching and diagnostics. Preserve current Overview, independent settings, Catch, Classic PPR, NPP and unrelated human Diagnostics entries. Reject numerical reuse for incompatible/unknown model, code or flags. Recalculate ready arithmetic using retained coefficients without fresh broad SPPR/Monte Carlo or invented mappings. Preserve FAIL, NOT_RUN, provisional and missing-result semantics. Technical publication failures must roll back coherently; central writes are serialized. `selected_model.lnk` is ignored, machine-local navigation only and regenerated after relocation.

## Shared implementation and data

- `tools/cli/{project,region,map,npp}.py`: human command entry points.
- `tools/project_core/{workbooks,registry,calculations,maps,validation}/`: one implementation home per responsibility.
- `tools/skills/paper-to-ppr/` and `tools/skills/ecopath-model-validation/`: the two active project skills. Pipeline domain resources live in `paper-to-ppr/resources/{extraction,mapping}/`.
- `tools/scientific_code/{PPREstimation,SeaAroundUsExtraction,NPPExtraction}/`: preserve engine internals and numerical behavior.
- `tools/scientific_helpers/{sppr,catch,npp}/`: shared integration helpers as needed; no unused filler modules.
- `tools/workflow_checks/{structure,calculations,selection,maps,validation}/`: focused checks.
- `tools/templates/{validation.docx,taxon_mapping.xlsx,instructions.md,builders/}`: reusable current templates.
- `tools/knowledge_graph/{graph.json,graph.html,GRAPH_REPORT.md,REFRESH_SCOPE.md,provenance/}`: one bounded, verified index. Local caches and runtime settings are ignored.
- `common_reference_data/geography/{boundaries,basemaps,metadata}/`, `taxonomy/{references,provenance}/`, `ecobase/{source_data,models,provenance}/`, `npp/raw/<product>/<year>/`, `npp/source_manifest.json`, and `atlas_source_context/`: shared reference inputs, with provenance.
- `common_reference_data/provenance/source_paths.csv` and `paper_file_roles.json`: portable path/disposition and source-role evidence.
- `interactive_map/{index.html,trends.html,sources.html,Open map.cmd,data/,sources/}`: generated human views.
- `research/<study_id>/{README.md,inputs,code,results,evidence,work/}`: substantive retained scientific studies. Frozen statements are explicitly historical.

## Work, portability and cleanup

Regional preparation/comparison work uses `work/<run_id>/{inputs,outputs,code,qa}/`; a run ID is `YYYY-MM-DD_HHMMSS_<purpose>` with a collision suffix when necessary. Promote necessary current evidence/results, then delete redundant temporary outputs, renders, builders, dependency trees and transaction backups. Work folders must not become extraction archives. Do not create `legacy/`, `previous_results/`, `reorganization_history/`, an `original_research_archive/`, or root output folders. Optional empty approved directories need no placeholder clutter.

Repository-local hyperlinks are relative to their containing document. Preserve external URLs and Word anchors. Record path-only link changes separately from renewed human approval. Source bytes use existing Git LFS policy; verify full bytes and disclose pointers. Before recursive moves/deletions, verify resolved paths stay inside this workspace and do not traverse unexpected reparse points. Every relocation/removal has a reason in the provenance ledger.
