# Project Reorganization Implementation Plan

> **For agentic workers:** Read this entire file before implementation. Use `superpowers:executing-plans` for sequential execution, or `superpowers:subagent-driven-development` when the user authorizes that execution method. Track steps with the checkboxes. This document is self-contained: the agreed specification is included below; do not reconstruct requirements from older plans or archived instructions.

**Goal:** Reorganize GlobalPPREstimation into a stable, human-readable region/paper/model structure, remove superseded extractions and obsolete content, and reduce regional model selection to one workbook choice plus one refresh command.

**Architecture:** Regional workbooks own active selection and calculations. Each model owns its single canonical JSON, extraction, saved regional workbook, diagnostics, and validation package. Shared workflow code and scientific engines have fixed homes; Project.xlsx and HTML receive derived updates without becoming additional selection authorities.

**Tech stack:** Windows/PowerShell, Python 3.11+, existing openpyxl/numpy and scientific dependencies, existing HTML/JavaScript map code, Git/Git LFS. Preserve the existing scientific calculation implementations and workbook table contract.

**Specification:** Sections 1–9 of this document record the final agreements. Tasks 1–12 implement the structural migration. Task 13 is the later legacy/documentation audit after the structure is stable. Task 14 refreshes and verifies the knowledge graph against the final state. Task 15 commits and pushes the verified changes. The subsequent skill-efficiency ideas document is `explainers/plans/skill_efficiency_ideas.md` and should be turned into a concrete implementation plan only after this reorganization handoff.

**Plan status:** Reorganization implemented; the verified first release is committed and pushed. The final publication record and fresh skill-work handoff are recorded in section 14. Original planning-time statements and earlier execution checkpoints are historical. Reorganization does not certify scientific results or authorize parameter repairs; skill-efficiency implementation belongs to the fresh follow-up conversation.

## 1. Agreement register and precedence

The user's later corrections override both the original proposal and the independent review. In particular, do not implement the rejected suggestions listed below.

| Topic | Final agreement |
|---|---|
| Overall layout | Keep the original proposed layout, with the specific amendments recorded here. |
| Region grouping | `regions/LME/<region_id>/`, `regions/EEZ/<region_id>/`, `regions/HS/<region_id>/`. Preserve region IDs and workbook names. |
| Paper ownership | Each paper has its own sources and `models/<model_id>/` collection. |
| EcoBase candidates | Regional JSON-only candidates use `ecobase/<model_id>/`, with the same model layout. |
| Structure contract | Add `explainers/structure.md`; it is an AI must-read under `project_contract` in root AGENTS.md and both active skills. |
| Duplicate extractions | Keep **only the most updated extraction of each distinct model**. Delete superseded extraction packages. Do not preserve their contents as a legacy extraction archive or merge their old contents into the latest package as a retention workaround. |
| Canonical JSON | Keep one `model.json`, shaped like a supported Ecopath export and loadable by ModelData and PPRCalculator. |
| Rejected JSON files | Do **not** introduce `source_model.json`, `computational_input.json`, or `computation_input.json`. |
| Departures from publication | Put concise, explicit `model_notes.md` beside `model.json`; summarize departures in the model extraction row of the validation DOCX and link to these notes. |
| Loading behavior | Record actual loading flags and calculator/code identity in result provenance; do not retain a redundant loaded-model JSON. |
| Regional snapshot | `model/results/regional_snapshot.xlsx` is a **full copy of the regional workbook**, readable like the active workbook. A reduced model-only workbook was explicitly rejected. |
| Restoration | Automated restoration imports only compatible model-dependent tables, preserving current independent regional inputs and settings. |
| Results location | Store restoration outputs and diagnostics under the model directory. |
| Minimal selection work | Choose `selected_model_id` and rationale in the regional workbook; one refresh command performs dependent administrative and ready calculation updates. No manual path, shortcut, Project.xlsx selection, or HTML editing. |
| Work cleanup | Promote necessary current outputs/evidence to permanent locations and delete redundant temporary material; work folders must not become replacement archives. |
| Legacy/consistency audit | Include a later scan of skills, project files, regional content, README files and explainers for legacy material and disagreements with code. |
| Scientific validity | Loadability, selection, diagnostic health, readiness and researcher approval remain separate concepts. Moving files must not change scientific conclusions. |

The user explicitly retained both `results/regional_snapshot.xlsx` and `results/result_manifest.json`, all five `project_core/` directories, and the `scientific_helpers/sppr`, `catch`, and `npp` subdivisions. Do not substitute the later suggested simplified layout.

This plan is saved inside the existing explainers directory to keep planning material within the agreed project organization. It is an execution reference, not a second normative structure contract.

## 2. Global constraints

- Never invent model/paper identity or geographic coverage to make relocation easier.
- Preserve model IDs, region IDs, modeled periods, source identities and distinct scientific variants. Shorten descriptive filenames where needed for Windows path limits; update references through the relocation map.
- Do not mutate scientific JSON values, matching weights, NPP or PPR coefficients merely to pass migration checks. Deduplication that replaces a scientifically different extraction must explicitly invalidate affected results and record the difference.
- Selection does not establish scientific validity. Preserve FAIL, NOT_RUN, provisional, reviewed, disqualified and unavailable semantics as implemented, unless separately authorized scientific work changes them.
- All repository-local hyperlinks must remain portable and relative to their containing document. Preserve legitimate external URLs and Word anchors.
- Preserve researcher-authored content and formatting in current validation documents. Reorganization permits rebasing links, not rewriting human decisions.
- No additional authoritative selection database, editable manifest status, or hand-maintained path field.
- Keep original scientific engine package layouts internally where needed for imports; organize the integration layer without gratuitously rewriting engine internals.
- Large source bytes remain under Git LFS according to existing policy. Detect LFS pointers before claiming source-byte verification.
- Use native PowerShell file operations with literal, resolved paths. Before recursive moves/deletions, verify every target is within the intended workspace and does not traverse a junction/symlink unexpectedly.
- Do not add historical aliases, compatibility folder trees, legacy extraction backups, or another archive to the finished layout. Git history can provide recovery without keeping obsolete content in the working project.
- Empty approved directories may be created by initialization; do not add dozens of placeholder files just to track empty skeletons.
- The original plan-authoring task did not itself authorize implementation. The subsequent reorganization execution is explicitly authorized by the user and follows the session's filesystem permissions and repository instructions.

## 3. Final directory tree

`<...>` denotes a collection item, not a literal filename. Optional evidence and source files are created only when applicable. Scientific collections can grow; fixed organizational containers should not proliferate.

```text
GlobalPPREstimation/
├── Project.xlsx
├── README.md
├── AGENTS.md
├── .gitignore
├── .gitattributes
├── .graphifyignore
├── regions/
│   ├── LME/
│   │   └── <region_id>/
│   │       ├── <region_id>.xlsx
│   │       ├── selected_model.lnk                 generated; Windows convenience only
│   │       ├── raw/
│   │       │   ├── catch/<original catch files>
│   │       │   ├── npp/<region-specific inputs>
│   │       │   └── geography/<region-specific inputs>
│   │       ├── papers/
│   │       │   └── <paper_id>/
│   │       │       ├── sources/
│   │       │       │   ├── <paper.pdf>
│   │       │       │   ├── supplements/
│   │       │       │   └── context/
│   │       │       ├── source_manifest.json
│   │       │       └── models/
│   │       │           └── <model_id>/
│   │       │               ├── model.json
│   │       │               ├── model_notes.md
│   │       │               ├── sppr_source.xlsx
│   │       │               ├── inputs/
│   │       │               │   ├── native/
│   │       │               │   └── provenance.json
│   │       │               ├── extracted_tables/
│   │       │               │   ├── <EwE import tables>
│   │       │               │   ├── <published companion tables>
│   │       │               │   ├── Taxonomy.xlsx
│   │       │               │   └── evidence/
│   │       │               ├── results/
│   │       │               │   ├── regional_snapshot.xlsx
│   │       │               │   ├── result_manifest.json
│   │       │               │   └── diagnostics/
│   │       │               └── model_validation/
│   │       │                   ├── validation.docx
│   │       │                   ├── taxon_mapping.xlsx
│   │       │                   ├── evidence/
│   │       │                   │   ├── evidence_index.json
│   │       │                   │   ├── source_review/
│   │       │                   │   ├── geography/
│   │       │                   │   └── mapping/
│   │       │                   └── work/<run_id>/
│   │       │                       ├── inputs/
│   │       │                       ├── outputs/
│   │       │                       ├── code/
│   │       │                       └── qa/
│   │       ├── ecobase/
│   │       │   └── <model_id>/                    identical model layout above
│   │       └── work/<run_id>/
│   │           ├── inputs/
│   │           ├── outputs/
│   │           ├── code/
│   │           └── qa/
│   ├── EEZ/<region_id>/                          identical region layout
│   └── HS/<region_id>/                           identical region layout
├── explainers/
│   ├── structure.md                             authoritative directory contract
│   ├── workflow.md
│   ├── model_selection.md
│   ├── model_loading.md
│   ├── sppr_methods.md
│   ├── sppr_parameters.md
│   ├── validation.md
│   └── plans/
│       ├── project_reorganization_plan.md        this execution plan
│       └── skill_efficiency_ideas.md              post-reorganization ideas
├── tools/
│   ├── cli/
│   │   ├── project.py
│   │   ├── region.py
│   │   ├── map.py
│   │   └── npp.py
│   ├── project_core/
│   │   ├── workbooks/
│   │   ├── registry/
│   │   ├── calculations/
│   │   ├── maps/
│   │   └── validation/
│   ├── skills/
│   │   ├── paper-to-ppr/
│   │   │   ├── SKILL.md
│   │   │   ├── agents/
│   │   │   ├── references/
│   │   │   ├── scripts/
│   │   │   └── resources/
│   │   │       ├── extraction/
│   │   │       └── mapping/
│   │   └── ecopath-model-validation/
│   │       ├── SKILL.md
│   │       ├── agents/
│   │       ├── references/
│   │       └── scripts/
│   ├── scientific_code/
│   │   ├── PPREstimation/
│   │   ├── SeaAroundUsExtraction/
│   │   └── NPPExtraction/
│   ├── scientific_helpers/
│   │   ├── sppr/
│   │   ├── catch/
│   │   └── npp/
│   ├── workflow_checks/
│   │   ├── structure/
│   │   ├── calculations/
│   │   ├── selection/
│   │   ├── maps/
│   │   └── validation/
│   ├── knowledge_graph/
│   │   ├── graph.json
│   │   ├── graph.html
│   │   ├── GRAPH_REPORT.md
│   │   ├── REFRESH_SCOPE.md
│   │   └── provenance/
│   └── templates/
│       ├── validation.docx
│       ├── taxon_mapping.xlsx
│       ├── instructions.md
│       └── builders/
├── common_reference_data/
│   ├── geography/
│   │   ├── boundaries/
│   │   ├── basemaps/
│   │   └── metadata/
│   ├── taxonomy/
│   │   ├── references/
│   │   └── provenance/
│   ├── ecobase/
│   │   ├── source_data/
│   │   ├── models/
│   │   └── provenance/
│   ├── npp/
│   │   ├── raw/<product>/<year>/<monthly files>
│   │   └── source_manifest.json
│   ├── atlas_source_context/
│   │   ├── <required compressed payloads>
│   │   └── provenance.json
│   └── provenance/
│       ├── source_paths.csv
│       └── paper_file_roles.json
├── interactive_map/
│   ├── index.html
│   ├── trends.html
│   ├── sources.html
│   ├── Open map.cmd
│   ├── data/
│   └── sources/
└── research/
    └── <study_id>/
        ├── README.md
        ├── inputs/
        ├── code/
        ├── results/
        ├── evidence/
        └── work/<run_id>/
```

Do not create arbitrary extra layers, `legacy/`, `previous_results/`, `reorganization_history/`, or new project-root output directories. A run ID is `YYYY-MM-DD_HHMMSS_<purpose>` with a collision suffix if necessary; date alone is insufficient for multiple daily runs. Original scientific file basenames may be retained inside their designated containers.

## 4. Ownership and meaning of files

### 4.1 Authoritative information

- **Project.xlsx:** central human-edited publication/model metadata and explicit researcher review records. Generated regional summaries, selected flags, derived paths and map fields are written by tools. Adding a publication requires metadata once; selecting an already registered model must not require central edits.
- **Regional workbook:** editable `selected_model_id` and `selection_rationale`, active matching/assumptions and independent regional inputs; generated regional results and freshness fields. `model_path` may remain for schema compatibility, but becomes derived and must never be manually maintained.
- **model.json:** the sole canonical JSON for that model. Preserve the supported Ecopath-export-compatible schema, group IDs and field semantics; do not add project administration data inside scientific model fields.
- **model_notes.md:** central, short scientific description and departure record. Minimum sections: Source identity; Modeled period and area; Departures from the publication; Evidence links. If no departures are known, explicitly state that. For each departure identify group/field, published and retained values (including missingness), rationale, scientific limitation, decision provenance when available, and exact supporting source locator.
- **source_manifest.json / inputs/provenance.json:** evidence provenance and roles, not competing editable paper/model registries.
- **result_manifest.json:** a generated description of the saved result package, loading flags and dependencies, not selection or approval authority.
- **regional_snapshot.xlsx:** a generated, complete regional workbook copy. Humans can browse all its sheets; it is inactive evidence until compatible model-dependent content is restored.
- **selected_model.lnk:** a generated Windows navigation convenience. Never use it for computation or model discovery; do not traverse it during inventory. Ignore it in Git and regenerate after clone/move. Its machine-specific target is not a portable authority.
- **HTML pages:** generated views. No manual selection updates in page source.

### 4.2 Model classification

Use a single canonical folder per distinct model within a region. Paper-reconstructed models belong under their paper; JSON-only EcoBase candidates belong under regional ecobase. Supporting EcoBase/native exports for a paper model belong in its `inputs/native/`, not a second active regional model folder. Shared EcoBase originals are reference inputs, not duplicate extraction outputs.

Different modeled periods, spatial scopes, explicit scenarios or scientifically distinct variants remain different models. Multiple regional applications can have separate regional result packages. Do not introduce a cross-region single-results folder: catch and matching differ by region. Link/register additional sources centrally rather than duplicating one model under several paper folders in the same region.

### 4.3 Tool responsibilities

| Directory | Responsibility and existing modules to route here |
|---|---|
| project_core/workbooks | Workbook table I/O, schema, formatting and shared workbook operations; currently workbooks.py and format_workbooks.py. |
| project_core/registry | Region/model discovery, candidate indexing, path resolution, Project.xlsx consolidation and ranking; currently update_project.py, index_candidates.py, atlas_ranks.py and source-path resolution logic. |
| project_core/calculations | Regional aggregation, taxon views, comparison support and allocation integration; currently regional.py, size_allocations.py and the regional orchestration pieces of run_region.py. |
| project_core/maps | HTML/data generation, source-context adaptation, map serving/launcher logic, map layouts and JavaScript; currently build_html.py, original_atlas_data.py, open_map.py, map_cumulative_ppr.py, original_html_layout/, map_basemap.js, provisional_display.py and map-facing review code. |
| project_core/validation | Validation artifact assembly, result/evidence consistency, review-record processing, runtime-equivalence verification and output formatting; currently researcher_review.py, runtime_equivalence.py, validation_percentage_format.py and validation builders scattered in regions. Split mixed modules by responsibility only when necessary. |
| scientific_helpers/sppr | Shared SPPR export/health/scope functions; currently scientific_helpers/ppr_scopes.py. |
| scientific_helpers/catch | Shared scientific catch interpretation/integration functions actually used across workflows. |
| scientific_helpers/npp | Shared NPP integration functions actually used across workflows. |
| scientific_code | Preserve the three existing engine packages. Do not duplicate helpers already supplied by an engine. |
| workflow_checks | Group current tests by the five proposed categories; preserve meaningful coverage and update imports. |

Every moved module must have one implementation home. Package `__init__.py` files are allowed. CLI files should expose project operations without copying business logic. Do not manufacture unused scientific modules merely to fill the approved subdivisions.

## 5. Latest-extraction cleanup rules

The user specifically rejected preservation of older extraction packages. The finished working tree contains only the latest extraction of each distinct model, even when old extraction material contains information absent from the latest package. Report such missing information; do not quietly keep or merge an older package.

Determine the extraction lineage using model/paper identity, modeled period/scope/variant, recorded extraction runs, corrections and provenance. Modification times alone are unreliable after copies. Quality and completeness describe the latest extraction; they do not grant permission to retain an older extraction instead. If the newest candidate is an explicitly separate experiment, classify it as a distinct variant rather than mistaking it for an extraction revision.

The migration inventory must record each duplicate group, selected latest package, superseded paths, evidence establishing ordering, and any affected active result/report references. If ordering is genuinely ambiguous, isolate that model's cleanup decision for a precise user clarification; continue independent migration work. Never choose arbitrarily or fabricate a chronological claim.

For a latest extraction that changes scientific model values: retain that latest canonical JSON, remove superseded extraction copies, invalidate results tied to the old JSON, and record pending status. Do not rewrite the old result hash as though a recalculation occurred. Fresh scientific reruns or repairs are separate work with the authorization appropriate to the execution session.

The rule applies to superseded JSONs, extraction tables, extraction-specific audits/renders/builders and obsolete extraction copies in region roots, models, archives and work folders. It does not mean deleting the original publication, the current validation record, shared source archives, or a genuine cross-model research study solely because its inputs contain a cited scientific model. Distinguish a study's frozen scientific input from an obsolete extraction package used to keep legacy content indirectly.

Record removals and dispositions in `common_reference_data/provenance/source_paths.csv`; retain metadata, not legacy extraction payloads. No automatic transfer of unique legacy extraction evidence into the latest package.

## 6. Snapshot and result-manifest contract

### 6.1 Saving

1. Resolve the outgoing model using `results_model_id`, not the newly edited `selected_model_id`.
2. Before clearing or replacing results, copy the entire active regional workbook byte-for-byte to the outgoing model's `results/regional_snapshot.xlsx` using an atomic staged replacement. Preserve all worksheets, formatting, hyperlinks and workbook features in the snapshot.
3. A user may have already changed Overview to the incoming model. The snapshot remains an exact copy; record both requested selection and actual results identity in the manifest. Do not alter the snapshot to pretend its outgoing rationale is known. Document this distinction for human readers.
4. Never overwrite a useful snapshot with a pending workbook lacking model-dependent results. Never save a workbook under the wrong model folder.
5. On successful refresh, save the current complete active workbook into the selected model's result package so switching back later has a recent snapshot.
6. Keep one current snapshot per model. Temporary transaction backups are removed after verification and are not a permanent historical snapshot collection.

### 6.2 Manifest

Use a small versioned generated schema. Capture `schema_version`, `unit_id`, `model_id` (actual results identity), `snapshot_selected_model_id`, timestamp with timezone, snapshot SHA-256, canonical model SHA-256, coefficient-source SHA-256, effective calculator/loader flags, executed code identity/hashes, relevant catch/matching/NPP/settings table hashes, and relative artifact paths. Unknown historical provenance must be explicitly unknown; do not insert current defaults and claim they describe an old run.

Use separate hashes for independent inputs so a changed NPP series does not unnecessarily force an SPPR rerun. Settings include scopes/methods/catch basis/unidentified treatment where relevant. Do not mix source JSON hash, full workbook bytes and scientific dependency hash as if they were interchangeable.

### 6.3 Restoration

Read the snapshot through the supported workbook API. Restore selected-model groups, model-specific matching/allocation records, available coefficients and applicable diagnostic content through an explicit table allowlist. Keep current Overview selection/rationale and independent settings, Catch, Classic PPR and NPP. Preserve unrelated human Diagnostics entries; do not replace a whole Diagnostics sheet indiscriminately.

Recompute dependent taxon/annual PPR, ratios and comparisons when their inputs changed and the necessary coefficients/matching are available. If model hash, loading flags or calculator identity are incompatible, reject numerical reuse with an exact reason. Preserve usable matching only when taxon/group identities and assumptions remain applicable; never guess mappings for new taxa.

Do not restore old researcher approval onto a changed model/input identity. Review records and validation links must retain existing freshness rules. A cached FAIL remains FAIL; a selected uncalculated model remains pending. A snapshot is not a shortcut around scientific review.

## 7. One-action model-selection workflow

The human edits only `selected_model_id` and `selection_rationale` in the regional Overview. Generate its available-model list from discovered, registered regional models. Preserve the existing Settings/@table schema; Excel data validation may provide a dropdown, but must not break programmatic editing or add another editable selection field.

Proposed human command, to be implemented (not available merely because this document exists):

```powershell
python tools/cli/region.py refresh --region regions/LME/LME_028
```

The command must:

1. Validate unique region/model identity, requested rationale, canonical JSON existence and supported schema before any destructive changes.
2. Resolve the selected model through the inventory; derive `model_path` relative to the regional folder. Update generated central paths and selected flags while preserving human metadata.
3. Save outgoing usable results under the outgoing results identity.
4. Load compatible saved material and coefficients; restore applicable matching or identify missing stages.
5. Recalculate ready regional arithmetic without automatically launching broad SPPR/Monte Carlo or inventing taxon assignments. Fresh diagnostics must obey the active scientific execution contract and recorded flags.
6. Write the regional workbook, regenerate its shortcut, update affected Project.xlsx rows, and regenerate dependent map/trend/source views through one orchestrated operation.
7. Preserve unrelated regional data and central edits. Serialize Project.xlsx writes; do not permit multiple agents to write it concurrently.
8. On missing prerequisites, record the incoming selection and a precise pending status. Clear/invalidate outgoing model-dependent display values so the map cannot borrow A's results for B.
9. On technical failure, leave coherent authoritative files and an actionable error; do not report success with mixed model identities. Stage outputs and restore temporary transaction copies if publication fails. Clean transaction work after successful verification.
10. Treat a repeated refresh of an unchanged, ready selection as a safe refresh, not a reason to create more snapshots/directories or fail with the current prepare-selection error.

This one command applies to an existing regional model. Adding a paper/model still requires its scientific metadata once. Filesystem paths and model candidates can be indexed automatically, but citation, interpretation and coverage must not be fabricated by discovery.

## 8. Contract, documentation and work lifecycle

Root AGENTS.md must contain a `project_contract` section requiring AI to read README.md, explainers/structure.md and explainers/workflow.md before modifying project content. Both active skills reference this section and the structure guide. The guide defines permitted placements, naming, ownership, generated files, run folders, canonical JSON, snapshots, duplicate cleanup and selection updates. README summarizes and links; do not maintain a second full normative directory tree that can drift.

Revise the validation instructions that currently place DOCX/XLSX beside the regional workbook. Final outputs belong under the exact model's `model_validation/`; they use fixed names because their directory already identifies the model. Preserve manual content and existing template semantics, and rebase every local hyperlink from its new containing location.

Write model preparation/extraction/calculation and cross-paper comparison work under regional `work/<run_id>/`. Write validation work under the model's `model_validation/work/<run_id>/`. Promote necessary extraction evidence, diagnostics and current validation evidence into the canonical destinations. Remove redundant outputs, vendored dependency trees, temporary builders and renders after verification. A work directory must not retain a whole superseded extraction under another label.

The later full audit is explicitly requested but not performed during plan creation. Migration-critical documentation updates are immediate implementation work; broader semantic audit/removal is Task 13.

## 9. Existing project facts and investigation entry points

These observations orient the executor; re-inventory before acting because the workspace can change:

- Earlier read-only inspection counted 366 regional directories (282 EEZ, 66 LME, 18 HS), currently flat under regions/. Of them, 23 had additional root-level content beyond workbook/raw/papers patterns.
- README currently describes `original_research_archive/`, manually entered model_path, region-root models and old skill locations.
- `tools/run_region.py:prepare_selection` currently snapshots into `models/previous_results` and clears model-dependent sheets. Replace that behavior; do not preserve that directory contract.
- `tools/workbooks.py` provides read_book, write_book, rows, records, overview, input_hash, sha and validate_region. Its table dictionaries use `(headers, rows)` and authoritative tables do not support formulas. Preserve the @table contract.
- `tools/update_project.py:update` preserves central metadata and expects selected models to be registered. Retain that principle while generating paths/selection updates automatically.
- `tools/original_atlas_data.py` resolves historical source paths via migration/relocation ledgers and serves model/source context. Move necessary path metadata before deleting archive directories.
- Active combined skill is currently `tools/skills/original_skill_resources/combined-src/SKILL.md`; needed resources exist among historical claude/codex distributions. Keep required current scientific procedures/helpers, remove redundant distributions and old builders after all references are rewired.
- Validation paths are currently specified in `tools/skills/ecopath-model-validation/references/document-production.md`; template instructions and researcher-review references also contain current paths requiring updates.
- Current scientific classes are in `tools/scientific_code/PPREstimation/ModelData.py` and `PPRCalculator.py`. PPRCalculator accepts model path plus flags including underdetermined, zero_catch, zero_biomass_accum, default_gs, weight_flow, weight_guess, normalize_DC, DC_tol and balance_BA_after_DC_normalization. Discover actual installed signatures before building provenance; do not assume these are the only relevant settings forever.
- The current graph is `tools/knowledge_graph/graph.json`; use its documented query path rather than creating graphify-out. It is an index with bounded coverage, not current scientific authority.
- `structure.txt` contains the initial user proposal; remove it after the authoritative structure guide incorporates the final agreements.
- Tool runtimes may not be on PATH. Resolve the bundled runtime using the Codex dependency tool or the environment's existing interpreter; do not install an unrelated Python just to execute the plan.

## 10. Review focus

The following failure modes require explicit checks in the owning tasks:

1. Selection already changed to B while current results still belong to A: snapshot A correctly, never label A values as B.
2. Latest extraction changes scientific values or lacks old evidence: remove old extractions as requested, invalidate incompatible results, report gaps, do not fabricate provenance or preserve a hidden legacy copy.
3. Catch/NPP changed since a snapshot: retain current inputs, selectively reuse compatible artifacts and recalculate only ready dependencies.
4. Moved Word/Excel/source links and machine-specific shortcuts: portable scientific links resolve under another repository root; shortcuts are regenerated convenience files.
5. Partial publication failure or simultaneous central writers: no mixed model identities, lost researcher edits or stale map success claims.

## 11. Implementation tasks

### Task 1: Inventory, baseline and concrete migration manifest

**Read:** README, current skills/references, workbook APIs, current graph scope, current template guide and this plan. Inspect all region subdirectories, including nested JSONs and work copies; avoid following reparse points.

**Working artifacts:** Use one execution-specific temporary directory for the inventory/baseline and staging. Final portable relocation/removal metadata belongs in `common_reference_data/provenance/source_paths.csv`, not a new archive. Suggested CSV columns: `original_path,retained_path,sha256,action,reason,unit_id,model_id,extraction_run_id`. Blank retained_path means explicitly removed; actions distinguish relocated, duplicate_removed, superseded_extraction_removed and obsolete_removed.

- [x] Record Git state, user changes, region counts, canonical workbook paths, models, papers, nested source variants, validation documents and all old-path consumers.
- [x] Read central/regional metadata to associate each model with region, source and distinct period/scope/variant. Locate current result identities separately from selected IDs.
- [x] Capture semantic baselines for regional inputs/results and generated payloads, plus byte hashes for scientific inputs, native sources and human validation documents. Do not depend solely on XLSX byte hashes for later numerical equality.
- [x] Produce a concrete source-to-destination/removal manifest with explicit collision decisions. Reject path escapes and unexpected reparse points. Resolve Windows long paths before moving anything.
- [x] Identify still-used archived bytes and ledgers, scientific research studies to retain, obsolete extraction groups, and dependencies that must be moved before archive deletion.
- [x] Verify every planned deletion has a disposition reason and that no destination collides with unrelated bytes. Ambiguous newest extractions require a narrow decision rather than blanket retention.

**Acceptance:** Inventory covers all current region directories and known source locations; counts reconcile; every planned move/removal has a reason and destination where applicable. The saved baseline contains enough information to prove unchanged science or explicit invalidation later.

### Task 2: Write the project contract and update output rules

**Create:** root AGENTS.md if absent; explainers/structure.md, workflow.md, model_selection.md, validation.md. **Modify:** README and active pipeline/validation references. Carry model_loading/sppr_methods/sppr_parameters content into their final filenames without losing current scientific explanations.

- [x] Write the authoritative structure guide from Sections 1–8, including examples for one paper with multiple models and a JSON-only EcoBase candidate.
- [x] Add the AGENTS.md project_contract must-read requirement and point both skills to it.
- [x] Replace region-root report and previous_results rules with model-local final deliverables and per-model full snapshots.
- [x] Replace manual model_path instructions with derived paths and one refresh command. Clearly mark commands as unavailable until their implementation task passes.
- [x] Define allowed work locations and promotion/cleanup rules in both active skills. Remove instructions that would recreate historical folders.
- [x] Verify both skills link the guide and approved output rules, resolving links from their containing files. Implementation deviation: the independent semantic/local-link audit replaces the proposed mirrored `test_project_contract.py`; evidence and rationale are recorded below.

**Acceptance:** One normative directory contract; no contradiction in immediately active path/selection instructions. Broad documentation truth audit is still separate.

### Task 3: Create the code package boundaries and grouped discovery

**Move/refactor:** Modules listed in Section 4.3 into tools/project_core; ppr_scopes.py into scientific_helpers/sppr. **Create:** tools/cli/{project,region,map,npp}.py and package initializers. **Tests:** workflow_checks/structure/test_region_discovery.py and test_model_inventory.py.

Proposed internal interfaces to implement consistently (these are planning decisions, not existing APIs):

```python
def discover_regions(root: Path) -> dict[str, Path]:
    # Map unit_id to only its canonical workbook under regions/{LME,EEZ,HS}.
    ...

def discover_models(region_dir: Path) -> dict[str, Path]:
    # Map model_id to only papers/*/models/*/model.json and ecobase/*/model.json.
    ...

def resolve_model(region_dir: Path, model_id: str) -> Path:
    # Require a unique discovered canonical model inside this region.
    ...
```

The ellipses above document signatures, not implementation to copy. Duplicate IDs and unexpected model.json locations must raise a descriptive error; do not pick the first glob result. Do not discover work copies, snapshots or shortcut targets as canonical models.

- [x] Add meaningful fixture tests for all three region types, extra appendices, nested work JSONs, a paper containing multiple models, EcoBase candidates and duplicate model IDs.
- [x] Move modules, update imports, __file__/parents-based root resolution and CLI execution bootstrap so direct root commands work. Resolve root from Project.xlsx and explicit CLI paths, not an assumed number of parents.
- [x] Route grouped region/model discovery through one implementation used by updater, NPP planning, map generation, selection and structure checks.
- [x] Update affected existing test fixtures/imports, including test_model_source_paths.py and selection tests in test_workflow.py.
- [x] Smoke-test all four CLIs and the package imports. Do not keep duplicate old modules as compatibility implementations.

**Acceptance:** One discovery mechanism; canonical identities survive extra grouping and deeper paper/model paths; core packages import and CLIs run.

### Task 4: Consolidate skills, templates and shared reference locations

**Move:** combined-src into tools/skills/paper-to-ppr; needed extraction/mapping resources into its resources subdivisions. Preserve the separate validation skill. Move current templates/builders to final locations; create a reusable taxon-mapping workbook template from the established appendix contract if no maintained template exists.

- [x] Build an explicit active-resource dependency list from references/imports before deleting distributions.
- [x] Consolidate equivalent procedures/scripts once and rebase relative resources, schema links and helper imports. Keep scientific instructions needed by the current workflow; remove historical packaging copies, .skill archives and unused compatibility builders.
- [x] Move geography, taxonomy, EcoBase and NPP sources according to the final tree. Update source manifests, paths, LFS patterns, NPP extraction code and tests together.
- [x] Move shared source-path resolution into registry; consolidate the old ledgers into source_paths.csv while preserving deliberate removals and resolvable historical provenance strings.
- [x] Keep archive-derived compressed context only where the current adapter still needs it; update its provenance and references without silently altering embedded scientific values.
- [x] Verify active skill/resource links, template availability, source membership and raw input bytes. Do not assert source hashes verified when only an LFS pointer is present.

**Acceptance:** Exactly two active project skill homes; no required resource relies on a deleted distribution or archive path. Reference moves preserve source bytes.

### Task 5: Relocate every region, latest extraction and current validation package

**Modify/move:** regions/*, central model/source paths, validation packages and linked evidence. **Add:** model_notes.md for each retained model. **Tests:** structure/test_latest_extractions.py and validation/test_relocated_links.py.

- [x] Group regions by type without renaming IDs/workbooks; place raw inputs into catch/npp/geography destinations and update consumers.
- [x] Resolve each duplicate extraction group and move only its latest package into its canonical paper/model or EcoBase home. Delete explicitly superseded packages; do not consolidate their unique old contents into the latest extraction.
- [x] Check each retained model against the supported export schema and loader path. ModelData loading and PPRCalculator construction should be tested with the relevant actual flags; diagnostic/numerical health is reported separately. If construction fails, report the exact limitation and keep the migration of unrelated models moving. A failure does not authorize numerical repair.
- [x] Write model_notes.md with supported source identity and departures; never claim exact source fidelity solely because a JSON loads. Remove redundant model representations according to the final single-JSON rule, preserving necessary configuration records and original native source inputs.
- [x] Move current validation.docx, taxon_mapping.xlsx and supporting evidence into each model's fixed validation location. Rebase links and preserve human-authored cells, decisions and formatting. Use the document/PDF skills when rendering these artifacts for visual verification.
- [x] Update the validation model extraction row to summarize/link model_notes.md while preserving researcher additions. Update central validation_report_path and review artifact hashes with a record that path/link edits were administrative, not renewed approval.
- [x] Move dated work by task/model identity; distinguish valid distinct candidates/studies from discarded old extraction runs. Remove region-root builders/reports and forbidden containers after consumers are rewired.

**Acceptance:** All regional roots follow the contract; one latest extraction per distinct regional model; no rejected JSON companions. Every changed-value extraction has incompatible results marked pending rather than silently reused.

### Task 6: Implement full-workbook snapshot saving and selective restoration

**Create:** project_core/calculations/snapshots.py and selection/test_snapshots.py. Use the workbook package and atomic temporary paths; do not regenerate a snapshot through write_book when an exact copy is required.

```python
def save_snapshot(workbook_path: Path, model_dir: Path, *, result_identity: dict) -> Path:
    # Validate results_model_id against destination, copy the full XLSX, write manifest.
    ...

def inspect_snapshot(model_dir: Path, current_book: dict) -> dict:
    # Return role-specific compatibility and reasons; never adopt files.
    ...

def restore_model_tables(current_book: dict, snapshot_book: dict, compatibility: dict) -> dict:
    # Apply explicit allowlist and retain independent inputs/settings/manual entries.
    ...
```

- [x] Test outgoing A results with Overview already edited to B; destination identity must be A and the copied XLSX must be byte-identical.
- [x] Test preservation of every worksheet, manual sheet, formatting and hyperlink in the saved snapshot, including content outside @table blocks.
- [x] Test that a pending empty workbook cannot overwrite A's useful snapshot and that manifest mismatch/corruption prevents reuse.
- [x] Implement the generated manifest contract with actual flags, unknown provenance handling and artifact paths relative to the manifest.
- [x] Define the restoration allowlist from actual regional schemas; preserve current Catch, Classic PPR, NPP, Overview and unrelated Diagnostics/manual content. Test new catch taxa and changed NPP against a stale snapshot.
- [x] Test model/code/flag mismatch, incompatible group membership, failed diagnostic status and stale human review identity. Provide exact missing/recalculation reasons.

**Acceptance:** Snapshots are complete workbook copies in model/results; selective restoration cannot roll back current independent data. Manifests do not become another editable authority.

### Task 7: Implement one-command regional selection refresh

**Create/refactor:** project_core/calculations/selection.py, CLI region.py; registry consolidation and generated dropdown/path integration. **Tests:** selection/test_selection_refresh.py and test_selection_transactions.py.

```python
def refresh_region(root: Path, region_workbook: Path) -> dict:
    # Orchestrate preflight, snapshots, restore/recalculate/pending and publication.
    # Return unit_id, selected_model_id, calculation_status, missing_stages, changed_paths.
    ...
```

- [x] Test A-to-B-to-A using existing coefficients/matching, and prove only selected_model_id/rationale are human edits.
- [x] Test B with no saved results or mapping: B is selected/pending in regional and central records; map shows no stale A values.
- [x] Test a normal unchanged-model refresh, missing rationale, unknown/duplicate model ID and an invalid path before mutation.
- [x] Implement automatic path/selected-field derivation and preserve centrally edited paper/model metadata. Do not silently fabricate a missing source registration; provide an actionable registration error for a genuinely new unregistered model.
- [x] Save/restore snapshots, recalculate ready arithmetic, update Project.xlsx once, and publish generated pages coherently. Retain exact current scientific scope; no implicit broad engine reruns.
- [x] Inject a failure before publication and during central/page writes; verify rollback/coherence and no lost researcher edits. Serialize central writes and reject stale-write baselines.
- [x] Generate selected_model.lnk safely on Windows; on other environments calculations still work, with shortcut unavailable rather than a fabricated functioning link.

**Acceptance:** One human command refreshes selection and its dependent views; unchanged/pending/failed states behave explicitly, with no additional manual files to update.

### Task 8: Finish map/source pages and validation integration

**Move/refactor:** project_core/maps and validation; templates and JavaScript. **Tests:** maps/test_source_links.py, test_selection_payloads.py and validation/test_model_notes_links.py.

- [x] Replace generated archive naming with sources.html and sources/ as proposed; distinguish source-detail pages from obsolete archives. Update map controls/download links and launcher server allowlist.
- [x] Derive model.json, sppr_source.xlsx, validation and source links from the inventory rather than model-ID string concatenation.
- [x] Rebase Word/Excel links, check their anchors and local targets, and render changed current deliverables to verify they remain readable.
- [x] Compare selected identities, scopes/methods, catch basis, uncertainty labels, annual totals, coverage and carbon conversion with baselines. Keep missing results missing.
- [x] Verify source pages and generated map/trends through the supported local launcher; check remembered browser selections cannot expose A values as B.

**Acceptance:** Current scientific views and delivered document links work after relocation; required scientific/manual content is preserved.

### Task 9: Retain current scientific research and remove obsolete archive content

**Move:** retained cross-model/cross-region studies into research/<study_id> with inputs/code/results/evidence/work subdivisions. Examples of likely scientific studies: discard sensitivity (both study scopes), TE mean comparisons and substantive NPP investigations. Historical workflow releases/coordination snapshots are removal candidates, not automatically research studies worth preserving.

- [x] Classify every archive subtree by current source dependency, genuine scientific study, superseded extraction or obsolete workflow output using the manifest.
- [x] Move necessary inputs/evidence before removing their old containers; preserve frozen study semantics and required code/data dependencies. Do not copy entire obsolete packages to research merely to avoid cleanup.
- [x] Remove superseded extraction payloads from every location per Task 5. For unrelated legacy candidates discovered during the broad audit, use the later Task 13 classification before deletion rather than a filename-only rule.
- [x] Remove obsolete distributions/builds, previous_results, redundant snapshots, temporary dependency trees and caches after their replacement checks pass.
- [x] Consolidate portable relocation/removal metadata; delete original_research_archive once no retained active or research dependency needs that tree.
- [x] Remove structure.txt, obsolete migration executables and historical preservation-only checks after replacing checks still protecting current source integrity.

**Acceptance:** No original_research_archive or disguised extraction archive in the finished tree; retained scientific studies and current source links still resolve.

### Task 10: Clean work folders and prepare graph/ignore rules

**Modify:** graph corpus paths, graph provenance locations, .gitignore, .gitattributes, .graphifyignore. **Tests:** structure/test_work_cleanup.py and test_allowed_layout.py.

- [x] Promote current numerical diagnostics, extraction evidence, validation evidence and reusable builders into their permanent destinations.
- [x] Delete redundant temporary outputs after successful checks, preserving evidence still referenced by current scientific documents. Work cleanup must never delete canonical results just because they were produced in a run.
- [x] Add ignore rules for generated shortcuts, caches, local graph settings, decoded NPP work and installed dependencies; keep canonical model/result/validation artifacts versioned as appropriate.
- [x] Prepare the final graph corpus paths and provenance locations, and remove obsolete graph cache/intermediate locations. Defer the actual refresh to Task 14 after migration and audit edits so it indexes the final state once rather than repeatedly rebuilding during moves.
- [x] Enforce approved region/model root entries and reject new ad hoc dated roots. Make initialization create optional fixed containers without generating placeholder clutter.

**Acceptance:** New AI tasks have predetermined output homes; ignored local work does not hide required evidence; final graph corpus paths and ignore rules are ready for Task 14. Do not claim the graph is current until Task 14 passes.

### Task 11: End-to-end migration verification

- [x] Re-inventory all regions and models; reconcile original counts with deliberate dedup/removal decisions and verify no IDs disappeared without a recorded reason.
- [x] Compare baseline and final authoritative scientific table values/units/missingness, selected IDs and review states. Separate unchanged relocations from latest-extraction changes requiring pending results.
- [x] Verify current source hashes, model loadability/configuration, snapshots, manifests, current local navigation and allowed directory shapes. Frozen unavailable references are explicitly historical; the checked-document/link coverage is recorded below rather than claiming every arbitrary evidence string resolves.
- [x] Exercise complete A-to-B-to-A selection in a temporary fixture/copy; do not switch the real project's scientific selection merely for a test.
- [x] Run the relevant existing and new workflow suites once stable. Fix administrative regressions without loosening tolerances or dropping meaningful tests; the unchanged scientific sentinel defect remains a disclosed failure outside this reorganization scope.
- [x] Verify generated payloads and visible map/trends/source pages; render edited validation deliverables. Report unavailable input bytes or unrun checks truthfully.
- [x] Publish a concise completion record distinguishing moves/removals, unchanged science, explicit invalidations, pending scientific work and the later audit. Keep the record as an execution section of this plan, not another status database.

Suggested suite command once packages/tests are migrated and a Python runtime is resolved:

```powershell
python -m unittest discover -s tools/workflow_checks -p 'test_*.py'
```

Make the five test subdivisions discoverable packages or provide a runner that executes each and preserves failures. Run existing JavaScript/scientific-engine tests separately where their own runners require it. The command above is a target interface, not proof that all current tests already fit one runner.

**Acceptance:** No success claim without fresh check output. Scientific differences and unresolved checks are explicitly listed.

### Task 12: Final human-facing handoff

- [x] Ensure README opens with Project.xlsx, grouped regional paths, the map launcher and the single refresh command.
- [x] Demonstrate opening a region, finding its selected model through the shortcut, reading model_notes.md, opening its validation package and inspecting its full workbook snapshot.
- [x] Explain adding a paper/model separately from selecting an existing model. List only required human inputs.
- [x] Confirm the final directory tree matches explainers/structure.md and that old instructions cannot recreate removed paths.
- [x] Report the resulting layout, verification performed, scientific pending states and location of the later audit task.

**Acceptance:** A human can browse the project and select an existing model without maintaining paths or editing multiple selection records.

### Task 13: Later comprehensive legacy and documentation/code consistency audit

**Timing:** The user explicitly described this as a task for later. Do not claim it completed during planning or substitute a migration path-string search for the full audit. Run it after the structural migration is stable unless the user separately requests another order.

**Scope:** README, all explainers, both skills and their resources/references, all region roots/subdirectories, templates, project scripts, shared data guides, research guides and graph documentation.

- [x] Search for old path contracts, superseded commands, old model copies, archived distributions, outdated preservation claims, legacy schema/source labels and unused utilities. A match is an audit candidate, not automatic proof of obsolescence.
- [x] Trace every candidate to current code, file consumers, scientific provenance and genuine study dependencies. Distinguish current runtime compatibility requirements from obsolete historical instructions.
- [x] Compare each documented command/path, selection workflow, calculator flag description, output rule and calculation/update claim with actual implementation and meaningful checks.
- [x] Produce a compact audit table in this plan's execution/audit section: path/location, finding, code/evidence reference, proposed correction/removal, dependency impact and disposition. Avoid creating another archive or index hierarchy.
- [x] Correct misleading active documentation and remove proven obsolete content within the future session's authorized scope. Preserve intentional historical scientific statements in genuine studies, clearly scoped as historical.
- [x] Repeat relevant link, command, structural and numerical checks after corrections. Remove dead graph endpoints and update the authoritative structure guide only for intentional agreed changes.

**Acceptance:** Active skills/documentation describe actual code behavior; retained historical research is clearly scoped; identified removals have evidence-based dispositions, not just renamed folders.

### Task 14: Refresh and verify the final knowledge graph

**Depends on:** Tasks 1–13. If the user explicitly defers Task 13, record that deferral and graph coverage limits; do not claim the broad audit completed. The graph must reflect all changes actually included in the reorganization release.

**Modify:** `tools/knowledge_graph/graph.json`, `graph.html`, `GRAPH_REPORT.md`, `REFRESH_SCOPE.md` and its `provenance/` records. Update `.graphifyignore` to the final canonical corpus where needed.

- [x] Read the installed graphify skill and resolve the documented existing graph at `tools/knowledge_graph/graph.json`. This is an explicit update task, not a read-only query. Do not create a second default graphify-out directory.
- [x] Inventory changed/deleted source paths from the migration manifest. Include current project contract, explainers, both active skills, core/CLI/scientific helper code and retained reviewed scientific evidence; exclude superseded extractions, local caches, dependency trees and raw binary data that the graph is not designed to parse.
- [x] Re-extract changed sources and remove deleted-source evidence, including obsolete extraction nodes/edges. Preserve unchanged valid scientific evidence and distinguish historical retained research from current workflow authority. Follow the graphify skill's agent/dependency requirements when an update needs semantic extraction.
- [x] Regenerate JSON, HTML, report, scope and portable source-hash/provenance records in their canonical locations. Do not merely rewrite source paths without checking whether the indexed content changed.
- [x] Verify graph schema, node/edge endpoint integrity, source-file existence, actual content freshness, evidence locations and coverage. Run three retrieval probes: current region/paper/model layout; one-command model selection with snapshots; current two-skill responsibilities. Check that answers cite current source locations and no removed extraction packages.
- [x] Open the generated graph HTML for a functional check. Record verified corpus counts, update limitations and actual check results in the plan's execution record. Avoid inventing unavailable token/runtime measurements.

**Acceptance:** The one canonical graph describes the reorganized project, contains no dangling references to deleted extraction packages, and retrieves the current ownership/selection contracts accurately. Scope explicitly states omitted or deferred work.

### Task 15: Commit, push and hand off the reorganization release

**Depends on:** Migration verification and Task 14. This is future implementation work explicitly requested as part of this plan. Do not commit or push merely while authoring these plans.

- [x] Inspect current Git status, branch, remotes and upstream. Preserve unrelated user work and existing branch choices. If a new branch is needed, use the repository's agreed policy/default `codex/` prefix; never guess a remote URL, overwrite a remote branch or force-push.
- [x] Review the exact final diff and deletion manifest, verify `.gitignore`/LFS behavior, and run the affected tests and graph checks against the actual final files. Confirm model notes, manifests, this plan and the skill-efficiency ideas document are included; exclude caches, temporary copies, secrets and machine-specific shortcuts.
- [x] Update this plan's execution record with completed tasks, real verification results, pending scientific states and any explicit audit deferral. Stage only authorized reorganization/plan changes using explicit path lists from the manifest; do not blindly include unrelated modified files.
- [x] Run `git diff --cached --check` and inspect the staged file summary/content. Create a descriptive commit, such as `Reorganize regional model workflow and project contract`, after the staged release passes checks. Checkpoint commits are acceptable, but the final commit must contain the verified graph and documentation. The retained-baseline whitespace exception is documented below; it is not a passing full-tree check.
- [x] Push the implementation branch to its verified configured remote/upstream using ordinary `git push`; use `git push --set-upstream <verified-remote> <implementation-branch>` only when no upstream exists. Include required Git LFS objects. No force push, history rewrite or automatic merge.
- [x] Verify push success and that the remote branch tip matches the local release commit. If credentials, networking, filesystem approval or the remote block publication, retain the local commit and report the exact limitation; do not mark push complete.
- [x] Report branch, commit ID, remote destination, graph verification, checks performed and remaining issues. The next planning/implementation agent reads `explainers/plans/skill_efficiency_ideas.md` only after the reorganized state is established; a failed push must be explicitly resolved or accepted as deferred by the user before claiming the requested handoff complete.

**Acceptance:** Verified reorganization changes and the current graph are committed and pushed to the intended remote branch; unrelated work is preserved; the next agent has a concrete committed baseline. No PR/merge is required unless separately requested.

## 12. Verification examples for high-risk behavior

Implement these as meaningful tests using existing fixture schemas; do not write tautological tests that merely assert hard-coded directory strings.

```python
def test_outgoing_results_identity_wins_over_edited_selection(self):
    # Build workbook: selected_model_id=B, results_model_id=A, nonempty A results.
    before = self.workbook.read_bytes()
    package = self.save_outgoing_snapshot()
    self.assertEqual(package.parent.parent.name, 'A')
    self.assertEqual(package.read_bytes(), before)
    self.assertEqual(self.read_manifest(package)['model_id'], 'A')

def test_restore_keeps_current_independent_data(self):
    # Snapshot A contains old Catch/NPP; active workbook contains revised inputs.
    before = self.independent_tables(self.active_book)
    restored = self.restore_A()
    self.assertEqual(self.independent_tables(restored), before)
    self.assertEqual(self.selected_id(restored), 'A')
    self.assertEqual(self.restored_matching_identity(restored), 'A')

def test_latest_extraction_invalidates_old_coefficients(self):
    # Same distinct model, newer extraction changes diet; old coefficient hash differs.
    self.apply_latest_extraction_cleanup()
    self.assertFalse(self.superseded_package.exists())
    self.assertTrue(self.latest_model.exists())
    self.assertEqual(self.refresh_selected_model()['calculation_status'], 'pending')
    self.assertFalse(self.map_has_outgoing_results())

def test_pending_workbook_does_not_replace_useful_snapshot(self):
    saved = self.snapshot.read_bytes()
    self.clear_model_results_and_refresh()
    self.assertEqual(self.snapshot.read_bytes(), saved)
```

The fixture helpers above belong to the indicated snapshot/selection/dedup test classes and must use actual workbook schemas. They express required behavior; they are not ready-to-run tests or fabricated current APIs. Add numerical assertions for recalculation where appropriate and failure injection for staged writes.

## 13. Completion checklist

- [x] Original proposed layout retained with final amendments only.
- [x] Structure guide is authoritative and an AI must-read through project_contract.
- [x] Only latest extractions remain; no hidden legacy extraction retention/merging.
- [x] One loadable Ecopath-compatible model.json per canonical regional model; no rejected JSON companions.
- [x] model_notes.md sits beside model.json and current validation extraction rows link/summarize departures.
- [x] Model-local snapshots are complete regional workbook copies, with generated manifests and selective compatible restoration.
- [x] One regional refresh command derives all selection paths/shortcuts/central fields/views.
- [x] Existing current scientific inputs, result semantics and researcher edits survive relocation, or documented extraction changes explicitly invalidate their affected outputs.
- [x] Both active skills, all migration-critical documentation and code agree about destinations and selection behavior.
- [x] Obsolete archives, redundant extraction copies and temporary clutter removed with verified dispositions.
- [x] Source hyperlinks, graph endpoints, LFS sources and meaningful workflow checks verified or explicitly reported unavailable.
- [x] Later comprehensive legacy/consistency audit was performed after structural migration; findings and dispositions are recorded below.
- [x] Canonical knowledge graph refreshed and verified against the final reorganized state.
- [x] Verified reorganization release committed and pushed; local/remote commit identity recorded.
- [x] Subsequent skill-efficiency planning receives the committed post-reorganization baseline, with any explicitly deferred items identified.

## 14. Execution record

At plan creation: implementation not started; no project directories relocated; no scientific files or legacy extractions deleted; no model selections changed. A future executor should record task completion, evidence and outstanding issues here without changing the agreement register to fit an implementation shortcut.

### 2026-10-04 authorized execution

Initial execution status: in progress at this entry; later checkpoints below supersede it. Skill-efficiency implementation remains reserved for a fresh follow-up chat.

Pre-flight shared interfaces: discovery feeds selection, updater, maps and NPP; one canonical grouped discovery implementation. Canonical model identity feeds snapshots/review/source links; the retained actual results identity wins over an edited selection. Workbook restoration feeds calculations/publication; current independent inputs and manual content remain protected. Path ledger feeds Office/Markdown/source-context references; explicit removal wins over guessed aliases. Final corpus feeds graph refresh; defer refresh until final files are stable.

Ruling: preserve both agreed documents in explainers/plans/ and reconcile references, as the current user instruction explicitly overrides their former paths.

Ruling: execute in the user-named current checkout on main, preserving the existing branch choice and uncommitted working scientific state. A new worktree would omit those edits. No force push or automatic merge.

Task 1 baseline: starting Git status/head and complete readable file inventory recorded in regional work/2026-10-04_000002_reorganization/qa. Scientific/source/report files hashed as full bytes; shared raw NPP verification deferred to its dedicated manifest verifier and explicitly distinguished. Workbook semantic baseline is being captured. Vendored dependencies and reparse points excluded.

Baseline checks: existing unittest suite ran 116 tests, with 6 failures and 15 errors. Converter import errors concern source_fidelity resolution; other pre-existing failures concern map expectations and historical researcher-report fixtures. Full log retained temporarily for differential verification.

Independent pre-migration review: model identities, latest lineage, source/computational variants, 57 validation associations and duplicate comparisons reviewed; findings recorded as metadata. LME_026 missing detritus routing blocks construction and is not authorization to repair. LME_038 retains a historical result hash linked by runtime_equivalence evidence; it must be verified after relocation, never relabeled.

Task 2: authoritative structure guide, root project_contract and workflow/selection/validation explainers drafted. Active skill references and their output rules will be rebased with resource consolidation.

Task 3 focused RED/GREEN: new grouped discovery and full-workbook/selective snapshot tests failed on missing package APIs, then passed 6/6 after implementation. Additional selection/transaction tests remain pending.


### Release verification checkpoint after recovery

Structural implementation is complete; final source-page correction, final inventory review, graph refresh and publication are in progress. No efficiency implementation has been performed. Earlier task notes above describe their execution-time state, not the current completion state.

The actual checkout now contains 366 grouped regions (282 EEZ, 66 LME, 18 HS), 61 current distinct models and 61 adjacent model notes. Counts reconcile as 60 registered models minus eight duplicate identities and one unavailable candidate, plus four already-present unregistered distinct models and six scientific source/computational variants. Model identity, area, period and scenario determined these decisions, rather than dates in filenames. The independent lineage dispositions are in `regions/LME/LME_028/work/2026-10-04_000001_reorganization_review/qa/`.

The old flat region containers and `original_research_archive` have been removed. Native PowerShell removed 1,787 reviewed obsolete leaves, followed by 102 specifically recorded cache/leaf items and 3,182 physically empty directories. A proposed broader container deletion was rejected by automatic approval review and did not run. Read-only inspection and a narrower approved script then removed only inventoried cache trees and named leaves; the region containers were removed only when empty. Scientific payload baseline patches and compressed table dumps were removed after independent preservation verification. Hash-only audit metadata was promoted into canonical regional work.

Preservation proof is in `work/2026-10-04_000007_preservation/qa/`: all 61 canonical model hashes match the agreed retained working-state bytes or the already-existing supported export, 366 selected IDs are unchanged, 17,656 retained originals match exactly, and 34 late moves were reconciled individually. There are no unexplained scientific byte changes. All shared raw NPP bytes were verified once against the manifest: 1,110 files, 32,055,853,324 bytes. The final path ledger records historical and current hashes separately; 100 stale historical links were already absent from the initial baseline and are explicitly marked unavailable, while six were reconciled to identical retained bytes. This does not fabricate recovery of the absent historical material.

There are 26 complete model-local workbook snapshots: 23 current/matching-bearing copies and three useful distinct-model outgoing copies recovered from the old snapshot collection. Their original bytes are retained, including manual content and formatting. Unknown historical flags/code identity remain unknown and block numerical restoration. Current inputs, independent Classic PPR/NPP, matching evidence, authored allocation assumptions and mapping review stay separate from cached numerical compatibility and human signoff.

LME_038 is an explicit scientific freshness limitation. Its latest accepted extraction differs from the input underlying historical coefficients. Removing the superseded package invalidated that runtime-equivalence bridge. Current model coefficients, model PPR and model comparisons are pending/unavailable in the regional and central workbooks and generated views. Its historical full snapshot and report remain labeled as historical; matching, authored allocation/mapping evidence, independent catch/Classic PPR/NPP and researcher edits are preserved. No coefficients were regenerated or relabeled current.

#### Checks actually run

| Check | Observed result and interpretation |
| --- | --- |
| Broad workflow suite | 138 methods, 137 passed, one method failed in four scientific missing-sentinel subcases, zero errors; 311.952 seconds. The unchanged converter treats decimal `-9999.0` / `-9999.000` as known in its diet-sum receipt. Source literals and failing assertions remain intact. This release does not claim an entirely passing scientific suite. |
| Snapshot/refresh review | Twelve independent refresh regressions passed; eight subsequent focused snapshot, authored-evidence, A–B–A and unknown-group checks passed. They exercise actual workbook schemas and rollback, rather than string-only layout assertions. |
| NPP I/O | Thirty distinct focused checks passed in the existing scientific environment, including native missing masks, day weighting, source-change guards and outside-cwd launcher planning. No real NPP extraction or broad scientific recomputation was run. Native fixture creation used an ASCII temporary root before the tests' own Unicode moves; no assertions were weakened. |
| Current model JSON loading | The real engine's current model-loading test file passed 80 tests, including all 61 current regional JSONs; paths/discovery fixtures were corrected. Strict and production-convention constructor probes are recorded separately from JSON loadability and numerical health. |
| Additional structure and actual generated map | Three retention/grouped-discovery tests passed; actual generated map selection check passed with ranks, missingness, set changes, carbon conversion and metric independence preserved. |
| Word reports | Thirty current reports rendered in Word, 221 initial pages, with zero text spans outside page bounds. All pages were visually inspected, including a separate final seven-page LME_038 freshness-note render. Two harmless existing pagination splits remain readable. Original Word XML was not independently saved: preservation of original text/style relies on operation assertions and changed-part records, while current readability was independently inspected. |
| Documentation | Forty-six current Markdown documents and 191 local links checked, zero broken local links. Both active skills read the same project contract. The comprehensive semantic audit was performed, not deferred. Final live source-page inspection found a remaining old role-ledger path/manifest-label problem; its focused correction is being verified before the graph capture. |
| Browser | Supported localhost launcher served the rebuilt map, populated time-series controls/chart and filtered source page. LME_038 displayed unavailable Ecopath PPR. Pointer activation was ineffective once; keyboard activation opened its region panel. No scientific workbook selection was changed for a browser test. |

#### Comprehensive audit dispositions

| Location/finding | Evidence/consumer trace | Disposition and impact |
| --- | --- | --- |
| Older plan locations and flat discovery | Current user ruling; canonical registry feeds selection, updater, maps and NPP | Plans preserved in `explainers/plans/`, consumers and references rebased to grouped discovery. |
| Nested/distributed skills and old mapping helpers | Active resource dependency trace; old helper imports were mutual only and used retired selection/output paths | Exactly two active repository skills; redundant distributions and three unused mapper helpers removed. Scientific extraction and mapping procedures retained. |
| `previous_results` and old preparation command | Actual full snapshot and refresh transaction tests | Replaced by complete model-local snapshots and the one refresh command; unsupported old command removed. |
| Legacy source-path fallbacks and duplicate ledgers | Explicit unified relocation/removal ledger | Guessed archive fallback removed; one portable ledger preserves actual chain dispositions and unavailable historical references. |
| Latest extraction versus old output claims | Independent lineage/source hash review and LME_038 workbook baseline | Superseded packages removed without merging unique older evidence; affected numerical outputs explicitly pending. Scientific variants kept distinct. |
| Active/frozen scientific statements | Actual engine/calculator contracts, current resources and genuine study dependency review | Current instructions corrected; frozen studies remain explicitly historical. No parameters repaired, approval inferred or missing values replaced. |
| Paper-role ledger and source-manifest label | Final live source-page inspection; current adapter/test fixtures still used old location | Focused canonical source discovery and role-label correction under verification, with exact-byte identity guards retained. |
| Sentinel receipt and apostrophe validator defects | Existing converter byte hashes plus retained failing assertions; writer permits genuine apostrophes but historical validator rejects them | Separately scoped scientific fixes remain unresolved. Source labels must not be renamed and checks must not be bypassed. |

Material implementation decisions: the agreed outcomes govern the API, so full snapshots and one transaction-owning refresh replace the speculative split task APIs; contract coverage is verified by the independent semantic/link audit instead of an extra test that only mirrors documentation. Administrative worksheet XML updates preserve unrelated cells and parts. Two migration bugs were caught and corrected before release: initially unpersisted derived regional paths, and out-of-order central registry XML rows. Word namespace declarations stripped by an administrative XML serializer were restored before rendering. The initially cleared LME_038 authored mapping tables were restored exactly from its full historical snapshot, and restoration tests now protect them.

Pending at this checkpoint: final independent navigation/snapshot/constructor results, focused source-page correction, final cleanup of reproducible renders/builders, canonical graph freshness/endpoint/retrieval/browser checks, explicit staged diff review, commit, ordinary push verification and the authorized fresh skill-work chat. No stale graph or saved scientific answer is being represented as independently replicated current work.


Independent final inventory: 366 grouped workbooks, 61/61 exact registered models, 23/23 correct selected paths/model lists/Windows shortcut targets, and 26 exact snapshot manifests, whole bytes, identities and dependencies. Twenty-five snapshots have unknown execution provenance and cannot restore numerical results; one has known exact execution. Only LME_038 has a historical snapshot input hash different from the latest canonical model. Three promoted outgoing copies were compared independently with the original baseline bytes; remaining copies are supported by manifest/save-copy evidence, not represented as an independent second baseline.

Construction is separate from JSON compatibility. All 61 JSONs load through ModelData. An explicitly nonnormalized strict probe constructs 21/61; the existing runtime diet-normalization convention with recorded public constructor defaults constructs 53/61. Eight unchanged multi-detritus routing restrictions remain: the original detailed Humboldt model, the published Falkland tables, Hernvann Celtic Sea, Piroddi Mediterranean, native Watari 2013, and the native 2005 Warm Pool model in EEZ_598, EEZ_941 and HS_071. The exact options/errors are in `work/2026-10-04_000005_final_checks/qa/normalized_constructor_probe.json`. Runtime BA closure occurred in memory for 26 models as documented; it was not written into any model or treated as newly observed biomass. No LIM, SPPR, diagnostic or Monte Carlo run was performed. No JSON or engine bytes changed during these probes.

Current report readability and render metadata are retained; reproducible PDFs, contact sheets and failed render staging have now been deleted after inspection. The graph will omit binary document content and raw data parsing; separate artifact/hash proofs supply their verification.


Final scoped source-page correction passed 17 affected tests after a realistic canonical fixture failed before the fix. The adapter now reads the reviewed role registry under `common_reference_data/provenance/`, enumerates original source files under canonical `sources/`, and discovers current model JSON/notes through canonical discovery. Source manifests are labeled metadata. Exact-byte identity guards, scores, missingness and prior-assessment downgrades remain intact. Generated pages will receive only this metadata correction, with all numerical/model/uncertainty payloads required to stay exactly identical.

One necessary existing Java Sea `runtime_equivalence.json` certificate remains adjacent to the model at the actual loader's supported configuration location. This is a documented directory-detail deviation, avoiding a gratuitous second certificate migration; it is neither a second model export nor selection authority, and its historical bridge remains invalid. The authoritative structure guide documents this exception. Seven blocked-source notes already described the construction limits; the eighth (original detailed Humboldt) now includes a narrowly recorded current constructor check.

Source capture is ready for Task 14. Graph completion hashes/counts belong to its non-corpus provenance report; final plan status changes require bounded content re-extraction of this plan, not a hash-only freshness update. At this point final graph verification, exact staged diff review, commit, push and fresh chat creation remain pending.

### Final administrative closure before publication

Tasks 1–13 are complete with the recorded task-detail substitutions and scientific limits. Generated source metadata has been refreshed with numerical/model/uncertainty payloads exactly unchanged. The independent final inventory and Word/browser checks above are complete. Fifty-two temporary-save snapshot/manifest files had protected sandbox-only ACLs; normal inherited directory access was restored using DACL-only native operations, with all full-byte hashes unchanged. This makes the reviewed files readable to the normal user and Git.

Graph semantic reading extended navigation verification to its 164-document corpus: 78 invalid Markdown links in 33 files were reconciled, plus one plain Bay of Bengal evidence locator. Sixty-two use exact ledger relocations, five use unique exact descendant-directory maps, three accepted Warm Pool JSONs independently match their historical SHA, and two reference the exact retained study/input. Six removed/unavailable historical targets are explicit nonlinks; newer model variants are never substituted. Detailed dispositions are in `work/2026-10-04_000002_reorganization/qa/final_graph_navigation_reconciliation.json`. This extends the earlier 46-current-document/191-link audit; it does not claim all frozen machine evidence or arbitrary plaintext strings have been interpreted as live navigation.

Three pre-existing descriptive contradictions were resolved against unchanged actual method bodies: net migration is emigration minus immigration (with calculator detritus-import subtraction), fractional exponent lies below integer interpolation for positive TE, and EwE simple-path/cycle-pruned formulations agree only under compatible acyclic/complete-path conditions. The authoritative API explainer was corrected; its stale engine-directory duplicate became a verified pointer, preserving the complete current method body in one location. Code locators and the harmless interpolation example are in `work/2026-10-04_000006_contract_audit/qa/scientific_documentation_consistency.json`. No source parameter, constructor default, solver or diagnostic check changed.

Remaining release steps: verified canonical graph, exact staged review, commit/push and the authorized fresh skill-work chat. Neither the known sentinel/apostrophe defects nor the eight source construction restrictions authorize scientific repairs in this session.

Final staged payload verification passed: all61canonicalJSONs and26full snapshots equal their actual staged bytes; all1110shared raw NPP staged LFS pointers match the full-byte-verified manifest SHA/size, with correctly sized full objects present locally. Git author/upstream configuration is available. Remote main `fcc624a6` is the parent of the existing local baseline `7cce584e`; publishing includes that previously unpushed baseline commit, without conflicting remote integration.

The full-tree Git whitespace check ran with native CRLF recognized and remained nonzero for retained content. Of270affected existing files,246match original baseline bytes exactly;24others were individually reviewed as existing EOF/Markdown formatting, preserved human source-metadata fields or unedited actual test logs. Two newly authored EOF blanks were removed from README and one discovery test, with Python AST identical. Scientific source/evidence bytes were not normalized to manufacture a passing check. See `work/2026-10-04_000002_reorganization/qa/staged_diff_check.json`, `staged_whitespace_dispositions.json` and `staged_nonbaseline_whitespace_review.json`. This is an explicit preservation exception; no fully passing full-tree whitespace claim is made.

A focused native snapshot access test passed repeated promotion, inherited permanent-parent access, exact workbook bytes and manifest identity in bundledPython3.12.14(9.993seconds) and defaultCondaPython3.13.9(6.111seconds). The suspected current-saver regression was disproved; production snapshots.py was left unchanged. The52 migrated copies were repaired, not evidence of a current saving defect. The native checks are in `work/2026-10-04_000005_final_checks/qa/native_snapshot_access_verification.json`.

A fourth active-guide description was corrected against the unchanged mass-balance helper: at fixed positive production/catch/predation, negative BA lowers calculated EE relative to BA0 and positive BA raises it. Unknown BA remains blank; resolving one mismatch is not full extraction fidelity. No helper or source input changed. Eleven additional exact provenance locators in eight of61notes were made local evidence links and checked; these extend the165-document/1637-link navigation check. Details are in `work/2026-10-04_000002_reorganization/qa/notes_plaintext_navigation.json`.


### Verified graph and publication checkpoint

Task14 passed the installed-skill source extraction, merge, integrity, retrieval and actual browser checks. Its curated corpus contains353current files:189code and164documents. Fresh AST extraction and all eight fresh semantic chunks were used; no stale semantic fragment was silently reused. Initial export had2550nodes,5539topology pairs and5694separately attributed edge evidence records. The final counts and hashes are authoritative in `tools/knowledge_graph/provenance/completion_verification.json`, outside this indexed plan. Schema/endpoints, every current source full hash, locations and scope coverage passed. Generic initial query ranking/budget missed the structure contract; the three required probe suites subsequently passed with five supported narrowed concept-anchor queries. The initial limitation is retained in provenance.

Parent browser verification actually searched and selected the layout contract, navigated its neighbor, toggled a community, inspected explicit historical evidence and a current model-review source/currency warning, and observed no console errors or warnings. The graph indexes recorded architecture/evidence sources; it does not parse omitted scientific binaries, replicate new scientific results or establish researcher approval. Actual host semantic token/cost telemetry is unavailable, rather than estimated. Closing statements in this plan are re-extracted as actual changed content before publication; a hash-only freshness update is prohibited.

Final source navigation verification covered165documents and1637current local links with zero broken links, plus eleven individually verified exact evidence links subsequently added to eight model notes. A stale workflow sentence describing the refresh command as under implementation was corrected to cite its completed checks and scientific freshness limits. No operation scope or behavior changed. The final empty root `diet_reextraction_20261002` container was removed only after native containment, reparse and emptiness checks; all of its scientific material had already been relocated.

Publication will use ordinary push to the verified `origin/main`. No efficiency implementation has been performed here. The prepared follow-up context is `regions/LME/LME_028/work/2026-10-04_000002_reorganization/qa/skill_work_handoff.md`; it requires a concrete plan against this actual code, independent scientific replication distinguished from saved-output reuse, matched overhead measurements, retained scientific limitations and isolated benchmarks. Commit/push identity and the new conversation remain pending until actually observed.

### Published release and fresh skill-work handoff

Observed on 2026-10-04: commit `7b2989fa2afce05130a198f67901d94c48cf7eec`, `Reorganize regional model workflow and project contract`, was created on `main` and pushed to the verified configured remote `https://github.com/idocarmel1/GlobalPPREstimation.git`. Both push and subsequent `git ls-remote origin refs/heads/main` succeeded; remote and local tips matched exactly, with a clean working tree. This includes the previously unpushed baseline commit `7cce584e` and does not rewrite history. The successful push uploaded the required Git LFS objects.

Initial ordinary push attempts received HTTP 500 while an overinclusive default sparse pack crossed the remote's 2 GiB push limit. A negotiation attempt also failed without advancing the branch. The successful ordinary fast-forward push used command-local `pack.useSparse=false` and `http.version=HTTP/1.1`, traversing the actual 6,513 required objects instead of the redundant 21,490-object stream. No persistent configuration, source data, security checks or history changed. GitHub accepted the release with nonblocking warnings for four current/evidence HTML files over its recommended 50 MB threshold. Exact push output, remote proof and the handoff identity are in `work/2026-10-04_000002_reorganization/qa/publication_record.json`.

The requested fresh local conversation was created in this same saved project: [Plan and implement scoped skill efficiency](codex://threads/01a104ef-49cc-7df1-9ed8-236969ab61b0). Its initial message supplies the published baseline, both document paths, project contract, detailed handoff record, real verification results and unresolved limitations. It requires a concrete plan against the actual code followed by implementation, independently replicated retained work distinguished from reuse/regeneration, and measured overhead reductions for simple routes. A read-only initial planning barrier prevents competing writes while this session commits the small publication-record and graph delta; the final authorized message supplies the closing published SHA and lifts that barrier. No efficiency changes are implemented in this session.

Reorganization Tasks 1–15 and the substantive preservation/cleanup/consistency/graph requirements are complete for the published release. Scientific limitations remain exactly as recorded: the decimal sentinel receipt defect, apostrophe validator disagreement, eight source construction restrictions, unknown historical snapshot execution provenance, unavailable historical references and LME_038 pending numerical freshness. The final administrative closeout commit will contain this actual publication evidence and a content-re-extracted graph; its SHA is supplied after successful push rather than fabricated inside its own commit. No broad scientific tests are repeated solely for this metadata closure.
