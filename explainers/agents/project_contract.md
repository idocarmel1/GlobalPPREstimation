# Project operating contract for agents

Read the root [project guide](../../README.md) and this contract before modifying project content. Both active skills follow root [AGENTS.md project_contract](../../AGENTS.md#project_contract). Reuse an unchanged contract already read in this execution context; read it in a new context or after it changes. Choose the requested operation through the [shared operation contract](../../tools/skills/paper-to-ppr/references/operation-contract.md) and read its additional scientific references only as needed.

This document contains the current directory, ownership, preservation and execution rules. It supersedes the operating rules formerly embedded in the reorganization and skill-efficiency plans. Human explanations live in the parent directory; completed plans are recovered from Git rather than retained as current authority.

Current user instructions take precedence. Preserve scientific inputs, researcher edits, missingness, diagnostic restrictions and source identity. Selection, schema loading, construction, numerical readiness and researcher approval are separate. Administrative work must not repair parameters, normalize diets, invent provenance or adopt a scientific result.

## Regions, papers and models

Regions live at `regions/{LME,EEZ,HS}/<unit_id>/`. Preserve IDs and `<unit_id>.xlsx` names. The regional root contains its workbook, generated `selected_model.lnk`, optional `raw/`, `papers/`, `ecobase/`, and `work/`. Region raw inputs use `raw/catch/`, `raw/npp/`, and `raw/geography/`.

A paper owns `papers/<paper_id>/sources/` (with optional `supplements/` and `context/`), `source_manifest.json`, and `models/<model_id>/`. One paper can own several periods/scenarios, for example `papers/P/models/period_A/` and `papers/P/models/period_B/`. JSON-only EcoBase candidates use `ecobase/<model_id>/` with the identical model layout. Identity and provenance determine ownership; discovery must never guess citations, chronology or coverage.

Every distinct regional model has exactly one canonical `model.json` and adjacent `model_notes.md`. Notes contain Source identity; Modeled period and area; Departures from the publication; Evidence links. Departures identify fields/groups, published and retained values including missingness, rationale, limitations, actual decision provenance and source locators when available. Unknown provenance remains unknown. Notes may state that departures have not been assessed; absence of evidence is not proof of source fidelity. Canonical JSON remains a supported Ecopath export. Administrative fields belong outside scientific JSON. Do not create `source_model.json`, `computational_input.json`, or a loaded-model JSON.

Supporting EcoBase/native exports for a paper model belong in that model's `inputs/native/`, not a second active regional model folder. Register additional sources centrally instead of duplicating the model under another paper in the same region. Multiple regional applications retain regional result packages because catch and matching differ; do not create a single cross-region results folder.

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

In the map, selection sets the model opened by default for each region. It must not filter out other models or prevent switching, reviewing or disqualifying an exact candidate. Reviews belong to `(unit_id, model_id)`. A review-only candidate without calculated results remains selectable with its scientific values unavailable; it never inherits the default model's calculation identity or results.

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
- `research/{human,agents}/<study_id>/{README.md,inputs,code,results,evidence,work/}`: retained studies organized by purpose and ownership. `human/` holds researcher-owned experiments and method comparisons; `agents/` holds supporting audits, baselines, reviews and integration evidence. Agent assistance does not determine ownership, and placement never confers approval. Keep each study package intact and list it in `research/README.md`. Frozen statements and execution records remain explicitly historical; resolve their original paths through the source ledger.

## Work, portability and cleanup

Regional preparation/comparison work uses `work/<run_id>/{inputs,outputs,code,qa}/`; a run ID is `YYYY-MM-DD_HHMMSS_<purpose>` with a collision suffix when necessary. Promote necessary current evidence/results, then delete redundant temporary outputs, renders, builders, dependency trees and transaction backups. Work folders must not become extraction archives. Do not create `legacy/`, `previous_results/`, `reorganization_history/`, an `original_research_archive/`, or root output folders. Optional empty approved directories need no placeholder clutter.

Repository-local hyperlinks are relative to their containing document. Preserve external URLs and Word anchors. Record path-only link changes separately from renewed human approval. Source bytes use existing Git LFS policy; verify full bytes and disclose pointers. Before recursive moves/deletions, verify resolved paths stay inside this workspace and do not traverse unexpected reparse points. Every relocation/removal has a reason in the provenance ledger.


## Snapshot identity and publication details

Save outgoing full-workbook bytes atomically before replacing usable results, and save the successful current workbook under the selected model afterward. A snapshot may contain the incoming Overview selection and the outgoing results; retain both identities honestly. Never overwrite a useful snapshot with an empty pending state.

Result manifests distinguish schema version, region and actual model identity, snapshot selection, timezone-aware timestamp, snapshot/model/coefficient-source hashes, effective loader/calculator flags, executed code identity, separate catch/matching/NPP/settings dependency hashes and relative artifact paths. Unknown historical flags or code remain unknown. Source JSON, workbook-byte and dependency hashes have distinct meanings. A changed independent input need not force an unrelated SPPR run.

Restoration uses an explicit allowlist of compatible model-dependent tables. Matching may be reused only while taxon/group identities and assumptions still apply. Current inputs, human Diagnostics entries, review freshness and failure/provisional states remain protected. On technical publication failure roll back coherently; on missing scientific prerequisites retain the requested selection and an exact pending reason. Serialize Project.xlsx writes.

## Scientific and human-review boundaries

The two active skills are the scientific procedures, not this directory contract. Direct diagnostics ordinarily retain GE, TE and With Egestion; full validation report rows retain GE/TE. Broad inventories, global methods and Monte Carlo require their own authorized scope. Reuse the audited input and actual configuration rather than substituting defaults. Record unsuccessful construction, exceptions, timeouts and unavailable matrices truthfully.

A composed pipeline resolves taxon-to-group mapping once, using the union of pipeline and validation requirements. Hand off the same keyed group/weight/confidence/evidence decision set; validation checks and reports it. Changed inputs or missing evidence return only affected gaps to that stage. Full validation still covers all catch taxa, including zero rows, and separate membership/allocation confidence.

Preserve current researcher-authored Word text, manual appendix cells, deletions, signatures, breaks and links. Render and inspect every output page after a Word edit. If an edit touches parser-consumed headings/labels, compare the existing signoff summary before/after; unexpected identity/date/sections/reference changes block adoption. Signed-source registration and bounded map refresh follow the existing handoff, preserve the exact human verdict, and do not authorize recalculation or reselection.

Read-only saved-table inspection and content-checked in-memory ReadSession reuse establish only their stated evidence scope. Recheck consumed input bytes before publication and retain the existing mutation guards. A session that observed any input change cannot publish a mixture of versions.

## Evidence and navigation

Use the one canonical [knowledge graph](../../tools/knowledge_graph/graph.json) and its [scope](../../tools/knowledge_graph/REFRESH_SCOPE.md). Query `graphify query "question" --graph tools/knowledge_graph/graph.json` before architecture exploration. Hash-eligible unchanged evidence may be reused; changed sources and relocated concepts require current verification. An outdated graph indexes its recorded snapshot and does not prove current scientific validity.

[Current limitations](../limitations.md) explain unresolved project restrictions to human readers. Model-local notes, diagnostics and review evidence establish actual scientific state. Work QA records what was checked; do not turn a partial trial, historical execution record or graph into approval.
