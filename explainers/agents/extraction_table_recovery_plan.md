# Extraction table recovery implementation plan

Status: proposed work, not executed. Prepared 8 October 2026 after the research-directory relocation and its bounded knowledge-graph refresh. This plan does not authorize scientific parameter repair, new model selection, runtime calculations or researcher signoff.

**Goal:** Restore each applicable model's import tables under `extracted_tables/` using the article/native source values plus explicit researcher-authorized changes, before automatic loader/calculator transformations.

**Specification:** The researcher's instruction is: “the tables need to be exact values as are shown in the article, after researcher-authorized changes only (and before automatic runtime changes).” Apply the [project contract](project_contract.md), [extraction procedure](../../tools/skills/paper-to-ppr/resources/extraction/procedure.md), [output formats](../../tools/skills/paper-to-ppr/resources/extraction/references/output-formats.md), [diet source/runtime separation](../../tools/skills/paper-to-ppr/resources/extraction/references/diet-source-runtime.md), [published companions](../../tools/skills/paper-to-ppr/resources/extraction/references/published-companions.md) and [reconstruction audit](../../tools/skills/paper-to-ppr/references/reconstruction-audit.md).

**Architecture:** Prefer byte-preserving relocation of verified existing tables. For absent tables, use a verified embedded source-table snapshot or a field-by-field, provenance-backed translation of source-faithful JSON into the writer's temporary input schema. Where JSON does not retain the required source values, literals, missing masks, units or identity, recover those particular fields from the original sources. A valid schema or successful runtime is insufficient proof.

**Execution:** Implement inline, one model package at a time. Scientific reconstruction and tooling changes remain proposed until this plan is authorized for execution. Temporary staging uses `regions/<type>/<unit_id>/work/<run_id>/{inputs,outputs,code,qa}/`. Current tables and permanent supporting evidence remain with their exact model. Serialize any separately authorized central workbook writes; this recovery should not need them.

## Verified starting inventory

The [full inventory](../../common_reference_data/provenance/extraction_package_inventory_20261008.csv) covers 61 canonical regional model directories discovered by the maintained discovery APIs. The [gap list](../../common_reference_data/provenance/extraction_package_gaps_20261008.csv) supplies every affected paper-model directory and filename. Counts describe filename/layout availability, not extraction fidelity or scientific approval.

| Case | Count | Action |
|---|---:|---|
| Paper-model directories with all eight standard tables directly under `extracted_tables/` | 32 | Preserve; separately check the three taxonomy-only gaps below. |
| Paper-model directories with all eight tables nested below `extracted_tables/evidence/` | 3 | Review their exact model/version and cell fidelity, then relocate as intact tables. |
| Paper-model directories with no matching standard table files anywhere under `extracted_tables/` | 23 | Search the exact model's native/source evidence and verified retained provenance; reconstruct only with sufficient source evidence. |
| Additional paper models with all eight standard tables but no root `Taxonomy.xlsx` | 3 | Recover taxonomy only if the applicable requested pipeline stage requires it. |
| JSON-only EcoBase candidate directories | 3 | Retain their distinct source role; do not assert article-extraction completeness or invent article provenance. |

The nested packages are:

| Model | Existing tables |
|---|---|
| LME_013 / `Chiaverano2018_detailed_Northern_Humboldt_1995_1998__source` | `extracted_tables/evidence/` |
| LME_027 / `27_Villanueva2004_SineSaloum` | `extracted_tables/evidence/` |
| LME_052 / `52_GM2019_Fig9_Pelagic_balanced_(2000-2014)` | `extracted_tables/evidence/ewe_imports/` |

The taxonomy-only gaps are LME_013 / `13_Humboldt_Current_13_3_Northern_Humboldt_Current_(1995-1998)`, LME_035 / `35_Gulf_of_Thailand_35_1_Gulf_of_Thailand_(1973)` and LME_052 / `52_GM2019_Fig9_Pelagic_(2000-2014)`.

The [JSON recovery inventory](../../common_reference_data/provenance/extraction_json_recovery_inventory_20261008.json) inspected the 23 packages with no standard table files. Only LME_027 / `Guenette2014_BancArguin_Base_1991__approximation` presently contains an `extraction_source_tables` snapshot of all eight files. The other 22 do not. Presence of that snapshot does not establish fidelity or authorize the approximation's departures. This requires a source/authorization check before recovery.

## Constraints and review focus

- The accepted table value is the printed/native source literal unless a specific researcher decision changes that cell. Record both the source and accepted value. Preserve established authorized variants and their identities; never replace a variant with its parent model's tables merely because names are similar.
- Do not load `ModelData` or `PPRCalculator` to generate these tables. Runtime diet normalization, coupled completion, default B/GS/habitat values, complementary BA, predation calculations and other automatic transformations are excluded.
- A canonical `model.json` can itself contain historical processing or accepted changes. Establish its actual provenance before calling it source-faithful. Sums equal to one, healthy diagnostics and an adjacent narrative are not proof of authorization.
- Distinguish printed zero, source blank, unknown sentinel, source-reported model estimate, accepted correction and exporter-derived summary. Unknown biological values remain unknown. Keep unpublished and unknown cells distinct in the evidence even when both export blank.
- Exactness has two layers: CSV source/adopted decimal text and missing masks must match exactly; Excel cells must preserve numeric values and source-compatible display precision. A numeric float round trip alone does not prove printed decimal fidelity.
- Metadata, group numbering, fleet identities, stage definitions, units, spatial basis, diet orientation/imports and table version must agree. JSON aggregate catch cannot establish missing fleet-specific landings/discards. Published TL cannot be replaced by calculated runtime TL.
- Store unrepresented published fields in purpose-specific `companions/*.csv`. Derived representation summaries such as `Sum` or `Total` are explicitly derived from evidenced operands; they are never represented as article-stated observations.
- Keep model JSONs, regional workbooks, current SPPR/results, signed Word reports and researcher-owned notebooks unchanged. Restoring a table package does not grant scientific approval or require automatic recalculation.

## Task 1 — freeze identities and select the recovery route

Files: read the two inventory CSVs, canonical `model.json`, `model_notes.md`, source manifests, current tables and exact paper/native originals. Write `qa/baseline_hashes.json`, `outputs/recovery_manifest.csv` and `qa/protected_hashes.json` in the regional work run.

- [ ] Rerun `discover_regions(root)` and `discover_models(region_dir)`; reconcile the saved inventory against current bytes rather than relying on the date of this plan.
- [ ] For each affected model, identify whether it is a published baseline, deposited native version or explicitly authorized variant. Record exact period/scenario and group/fleet crosswalk. Never merge distinct identities or reuse a donor model's parameters.
- [ ] Record SHA-256 for canonical JSON, existing extracted files, source inputs, regional workbook, model results/review artifacts and Project.xlsx before mutation. Resolve retained historical paths with `SourcePaths`; Git is a provenance lead, not automatic authority to restore a superseded extraction.
- [ ] Assign each table/field one route: verified existing table; verified embedded source snapshot; verified JSON field plus source-literal evidence; primary-source recovery required; unsupported/conflicting. Record a reason and source locator for each unresolved item.
- [ ] Verify the manifest covers all 29 paper-model layout/taxonomy gaps and explicitly distinguishes the three JSON-only candidates. An individual model can use different routes for different fields.

## Task 2 — establish an accepted pre-runtime cell ledger

Files: write `outputs/cell_ledger.csv`, `outputs/authorized_changes.csv` and `qa/source_review.json`; permanent accepted evidence goes to that model's `extracted_tables/evidence/table_recovery/` after verification.

- [ ] Read the original article/supplement/native cells and the existing extraction/conversion history. Retain source bytes and their exact locators. Prefer genuine source literals over values reformatted by later Excel exports.
- [ ] Use ledger columns: `model_id`, `table`, `group_id`, `consumer_id`, `prey_id`, `fleet_id`, `field`, `source_literal`, `accepted_literal`, `units`, `spatial_basis`, `cell_status`, `source_path`, `source_sha256`, `source_locator`, `canonical_json_pointer`, `authorization_reference`, `decision_date`, `decision_identity`, `excluded_runtime_transformation`.
- [ ] Allowed adopted statuses are source-stated, source-reported estimate, researcher-authorized change or documented source unknown. Keep derived exporter summaries separate. A missing authorization reference blocks adopting a discrepancy; do not interpret an automatic transformation log as a researcher decision.
- [ ] For diet/import, retain each printed proportion, unknown mask and column sum, including non-unit sums. Never reverse a normalization using an approximate sum, invent an omitted prey or normalize restored data.
- [ ] For BA, retain only the source/authorized absolute or rate form; do not manufacture the other using rounded B. Keep runtime-balanced BA and predation out of the source tables.
- [ ] For a JSON-only numeric value such as `0.1`, establish the source literal and units before claiming it reproduces printed `0.10`. If the evidence cannot recover the literal or the value, mark the item unresolved and use the primary-source route.
- [ ] An independent field-by-field review verifies every nonblank adopted value and every missingness decision. A converter receipt proves its input, not the article's values or researcher acceptance.

## Task 3 — relocate the three verified nested packages

Files: the three model-local nested locations listed above; their root `extracted_tables/`; the relocation ledger `common_reference_data/provenance/source_paths.csv`.

- [ ] Verify existing tables against Task 2 before treating this as relocation-only. A nested package for a different source/variant must remain evidence, not become the active package.
- [ ] Stage the eight files intact and check group order, exact model/version and original hashes. Check whether companions, report and source-cell evidence belong to the same latest extraction.
- [ ] Move verified files to `extracted_tables/<filename>`. Preserve all table bytes and researcher edits. Keep necessary supporting evidence in its existing model-local owner; do not indiscriminately flatten the whole evidence directory.
- [ ] If a destination already exists, compare hashes and evidence first. Identical redundant copies can be removed after reconciliation; a conflicting or manually edited file requires a recorded disposition, never silent overwrite.
- [ ] Update actual navigation links and append each move's old/new path and hashes to the source ledger. Preserve historical execution records and their original paths. Verify old references resolve to the new retained files.
- [ ] Pass criterion: all eight correct files exist at the root, all relocated table hashes match their verified starting hashes, and every moved-file reference resolves. A source mismatch switches that table to Task 4 instead.

## Task 4 — recover genuinely absent standard tables

Proposed implementation files: `tools/skills/paper-to-ppr/resources/extraction/scripts/recover_tables.py` for a strictly offline exporter, and `tools/workflow_checks/structure/test_extraction_table_recovery.py` for meaningful source/missingness/authorization tests. Reuse the maintained writer and `source_fidelity.py`; do not add a second converter with different scientific rules.

- [ ] First test the verified embedded-snapshot route. For an exact `extraction_source_tables` table, export its actual header, rows, literals and masks, including TL/metadata when retained. Cross-check snapshot and adopted ledger values; stale snapshots do not override authorized corrections.
- [ ] The existing `database_json.py -j` produces a reconstructed workbook, not the required six CSVs plus two separate XLSX files. Its generic fallback is not a source-fidelity proof. Do not label its generated workbook a complete recovered import package.
- [ ] For JSON without exact source tables, implement an explicit source-schema-to-writer crosswalk gated by the verified ledger. Read numeric literals with `Decimal`/decimal strings. Retain original group/fleet IDs, orientation, units and unknowns. Do not infer missing fleet partitions, defaults or source TL.
- [ ] Exporter interface: accept an immutable source JSON path, verified ledger path and empty work output directory; return generated files plus a field provenance receipt. Refuse conflicting sources, missing authorization, undocumented unit conversion and missing required identity. Never write to the input JSON or invoke the runtime loader.
- [ ] If a required source field is not represented in JSON, read the corresponding source table/prose/native field. Populate only source-supported/authorized cells. A fully blank table is acceptable only where source review establishes that its values are unknown/unreported; an unread source cannot be relabeled “not reported”.
- [ ] Keep the writer-input JSON temporary. It has `groups` and writer-specific fields, whereas the canonical export has its supported model schema; never pass the latter directly to `write_outputs.py` or promote the temporary representation as `model.json`.
- [ ] Use the maintained writer in staging after the field ledger passes. Concrete invocation pattern, with model-specific paths supplied by the manifest:

```powershell
$extractionScripts = Join-Path $repoRoot 'tools/skills/paper-to-ppr/resources/extraction/scripts'
python (Join-Path $extractionScripts 'write_outputs.py') $verifiedWriterInput --outdir $stagedOutputs
python (Join-Path $extractionScripts 'validate.py') $generatedModelDirectory
```

The generated directory is the writer's returned path, not a guessed name. `$verifiedWriterInput`, `$stagedOutputs` and `$generatedModelDirectory` are actual paths in the model's work run, recorded in `recovery_manifest.csv`.

- [ ] CSV output preserves exact literals, standard headers/order, UTF-8 without BOM and CRLF. XLSX TL/metadata retain the required shapes. Do not use rounding, normalization or equal-share allocation to satisfy a checker.
- [ ] Retain format limitations as explicit blockers. The existing apostrophe-check inconsistency must not be bypassed by renaming scientific groups. Any separately authorized tooling fix requires a focused test using the actual source name.

## Task 5 — recover taxonomy and companions only where supported

Files: model-local `Taxonomy.xlsx`, `MODEL_PROFILE.md` and applicable `companions/*.csv`, following the separate taxonomy and published-companion contracts.

- [ ] Review the three taxonomy-only gaps and missing taxonomy in other packages against actual stage authorization. Extraction-only work does not automatically require a new taxonomic interpretation.
- [ ] Recover group membership from the source definitions or verified existing source-faithful descriptions. Keep the three columns `seq`, `group_name`, `taxon_descr` in that order. Missing exact membership stays explicitly unknown; do not use assumed catch mappings as source taxonomy.
- [ ] Preserve every additional published field: stanza links/ages/growth, migration, fleet routing, constraints, parameter roles and source-cell precision/provenance, where present. Use purpose-specific companion filenames and source locators; these are evidence, not claimed EwE import tables.
- [ ] Model metadata comes from actual source/identity records. Do not guess publication year, model period, LME identity or source area to fill Metadata.xlsx.

## Task 6 — prove fidelity before promoting files

Files: model work `qa/table_fidelity.json`, `qa/authorization_review.json`, `qa/missing_mask_comparison.json`, `qa/protected_hashes_after.json`; permanent concise receipts under `extracted_tables/evidence/table_recovery/`.

- [ ] Write failing exporter tests before implementing it. Required cases: preserved `0.10` versus `0.1` display text; zero versus blank versus `-9999`; non-unit diet/import sums; explicitly unknown import; exact accepted correction with and without authorization; group-order/fleet mismatch; source TL absent while runtime TL exists; BA rate supplied without absolute BA; missing landings with known discards; habitat/whole-area units; immutable input JSON.
- [ ] Reopen all generated CSV/XLSX files and compare every scientific cell with the adopted ledger and its source locator. For CSV literals and masks require exact equality. For numeric XLSX storage use documented absolute `1e-12`/relative `1e-14` comparisons, separately verifying source display formats/literals; do not call tolerant storage equivalence “exact printed text”.
- [ ] Validate table structure with maintained `validate.py`. Investigate sum warnings against the source. A scientifically faithful non-unit diet sum must be reported as such, not normalized or hidden to obtain a passing numerical check.
- [ ] Perform conversion/round-trip checks only on a work copy using `database_json.py` and the source-fidelity path. Compare results to the immutable canonical JSON as appropriate, keeping author-reported estimated/output roles separate from importer flags. Do not promote the converter's temporary JSON or its automatic-derived fields.
- [ ] Where a generic reconstructed workbook lacks source snapshots, its round trip cannot establish article fidelity. Keep that limitation explicit even when numeric values agree.
- [ ] Recheck every protected hash before promotion: canonical JSON, source originals, regional workbook, Project.xlsx, existing results, signed reports and notebooks must be unchanged. An unexpected difference stops that package's promotion.
- [ ] Pass criterion: every adopted nonblank value and missing mask has supported source/authorization evidence, no runtime-generated scientific value entered the imports, source identity and schema match, and no protected file changed. Unresolved fields/models remain reported gaps rather than guessed completion.

## Task 7 — promote latest tables, document dispositions and close

- [ ] Promote only the verified eight imports, applicable taxonomy/companions and necessary extraction reports/evidence to the exact model's `extracted_tables/`. Keep one current package per distinct identity and preserve manually edited evidence.
- [ ] Record source JSON hash, source/authorization references, tool version, routes by field, exact output hashes and remaining gaps in a concise recovery receipt. Clarify source literal versus authorized accepted literal versus derived summary.
- [ ] Keep superseded package recovery in Git rather than new archive/source-model folders. Remove only reconciled redundant work artifacts; retain evidence needed to justify the current accepted cells.
- [ ] Re-run the inventory. Each original gap has a recorded outcome: byte-preserving relocation, verified reconstruction, documented source-required blocker or explicit inapplicability. Do not turn an unresolved package into a “complete extraction” claim merely by creating filenames.
- [ ] Update human/agent navigation and relevant skill references only if their rules or paths changed. Refresh the canonical knowledge graph for changed indexed guides/evidence and record its bounded scope.
- [ ] Do not launch SPPR, change model selection, rebuild numerical results, edit signed reviews or refresh Project.xlsx/map by default. If source conflicts imply a canonical scientific correction, keep it as a separate proposal with its required authorization and dependency review.

## Completion evidence to deliver

Deliver the before/after inventory, exact model paths, table hashes and cell-fidelity receipts; a list of preserved researcher-authorized changes; unresolved fields and missing source evidence; and protected-file hash equality. Distinguish fully faithful packages, structurally present but unverified packages and blocked recoveries. The plan is complete when the proposed steps and decision gates are documented; recovery itself is not complete until those checks pass during a later authorized execution.
