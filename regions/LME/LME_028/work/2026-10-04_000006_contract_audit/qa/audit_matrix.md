# Reorganization contract audit, 2026-10-04

This is an administrative semantic review of the agreed plans, current code, two active skills, supporting resources, documentation and templates. It does not certify new extraction/scientific results, graph freshness or efficiency gains.

| Requirement | Disposition and evidence |
| --- | --- |
| Region → paper → model ownership | Current guides consistently use grouped canonical discovery, paper-owned sources, model-owned evidence and reports. Frozen study guides carry an explicit historical preface. |
| Latest extraction and one supported JSON | Canonical model.json belongs to one exact variant; writer-input JSON is temporary staging. Notes describe departures, preserving missingness, uncertainty and diagnostic restrictions. |
| Workbook selection and one refresh command | ID plus researcher rationale are editable; path is derived; selection/loadability/readiness/signoff remain separate. Removed prepare-selection and unsupported refresh --all guidance. |
| Snapshot/approval semantics | Guides use full local workbook copies and selective compatible restore, preserve manual tables and require reviewed exact-model signoff. No administrative approval inference. |
| Scientific method scope | Reviewed actual model loader, PPRCalculator/BA normalization, SPPR restrictions, catch/discard/NPP contracts and namespaced APIs; corrected claims without editing scientific code. |
| Two active skills follow one contract | Exactly paper-to-ppr and ecopath-model-validation; both explicitly read root project_contract, README, structure and workflow. Nested SKILL.md and redundant distribution removed with containment checks. |
| Lost-resource dependency | Original pipeline integration-contract was text-identical after newline normalization to the retained contract. Retained scientific equations/distinctions are preserved; current ownership and commands reconciled. |
| Obsolete mapper helpers | prepare_mapping.py, validate_mapping.py and mapping_io.py have no maintained consumer beyond mutual internal imports. They depend on retired layout and are approved for removal by the parent. Historical copies are evidence. |
| Documentation consistency | Fresh verification: 46 current Markdown documents, 191 local links, zero broken links; both skills contain all contract must-reads. Map module help commands pass. Full dependency/hash records are adjacent JSON. |
| Known validator limitation | The writer permits apostrophes but the historical validator rejects them. Deferred to a separately scoped fix; source groups must not be renamed or checks bypassed/loosened during reorganization. |
| Runtime limitations | Bundled Python lacks NPP yaml; existing Conda Python passes NPP help. Module invocation resolves imports for map/size tools. No fresh NPP or broad scientific rerun here. |
| Scope boundary | No efficiency changes, parameter repair, invented provenance, graph-current assertion or replication claim. Follow-up must demonstrate independent replication and overhead reduction. |

Material deviations and their reasons are detailed in disposition_record.json. Earlier change logs may omit edits already completed before an interrupted helper rerun; the reorganization baseline/move ledger remains authoritative for original file bytes.

Late live-page check exposed a paper-file metadata migration miss in production discovery. It is corrected in reconcile_paper_files: authoritative provenance registry, canonical sources/model discovery, explicit administrative manifest and current model/notes labels. The new realistic fixture failed first, then all 17 paper-files tests passed; exact-byte role guards and scientific assessment preservation remain enforced. Evidence is paper_file_metadata_fix.json. Generated page metadata refresh is parent-owned and must preserve scientific payload exactly; this subagent did not write pages.
