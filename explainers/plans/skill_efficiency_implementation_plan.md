# Scoped skill efficiency implementation plan

> **For agentic workers:** Execute sequentially with `superpowers:executing-plans`. Use fresh agents for observed skill trials, blind extraction and final review as required by `superpowers:writing-skills`. Check off tasks against observed evidence.

**Goal:** Make simple operations narrower while preserving the scientific procedures and demonstrate correctness with isolated, explicitly classified replication and observed old/new traces.

**Architecture:** Both existing skills route first through one shared operation/dependency reference. Detailed scientific/report instructions remain conditional references. The supported workbook reader gains optional sheet selection, with an operation-local content-checked read session and a read-only regional inspection command. Existing selection, snapshots, arithmetic, registration and page guards remain the mutation authorities.

**Tech stack:** Existing Python/openpyxl, scientific engine, DOCX OOXML and Word/packaged rendering, graphify, Git. No additional active skill or persistent cache registry.

**Spec:** [Efficiency requirements](skill_efficiency_ideas.md), [reorganization agreements](project_reorganization_plan.md), root project_contract. Published baseline `85ae543693887a5439fb13ebd84bcb91f8ecc360` on main.

## Constraints and rulings

- Read README, structure and workflow before edits. Reuse already read unchanged contract in this context; fresh agents read it independently.
- Preserve scientific JSON, parameters, missingness, exact IDs/names, diets, flags, statuses, authored mappings, human reports and live selections. Selection, readiness, diagnostics and approval remain separate.
- Trials use `regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency/{inputs,outputs,code,qa}/` and temporary isolated project copies. No live Project.xlsx, report, regional workbook or page writes.
- Use current latest model packages only; instruction checkpoints are not a third installed skill or an extraction archive.
- Keep central serialization, input rechecks, snapshot rollback and stale-page gates. Do not use broad SPPR/Monte Carlo as an efficiency benchmark.
- Existing decimal-sentinel/apostrophe defects, eight construction restrictions, unknown historical execution identity, LME_038 pending results and unavailable historical sources stay explicit.
- Ruling: execute in the named shared checkout on main after the publication barrier; the user explicitly authorized plan then implementation without another approval. Skill-default approval gates do not create a new gate.
- Ruling: implement routing and bounded read mechanics; do not refactor central mutation APIs without a demonstrated need. This keeps freshness/rollback dependencies unchanged.

## Review focus

1. A narrow read must not be represented as whole-workbook readiness or full scientific review.
2. Same-size/same-mtime changes must invalidate reuse; returned mutable dictionaries cannot corrupt cached originals.
3. Notes/signoff tasks must retain source breaks, deletions, signature/date, anchors and exact review decisions, and stop at stale-page failures.
4. Full routes must retain all required matrices/axes/masks and complete taxon universe; moved guidance cannot silently disappear.
5. Independent trials must not obtain retained extraction/review answers before producing their own results.

## Operation contract to implement

Read the entry skill, mandatory project contract and shared `paper-to-ppr/references/operation-contract.md`; then only the applicable route below. Composed requests use the union.

| Route | Exact additional reads | Allowed writes/checks | Completion claim and escalation |
|---|---|---|---|
| Explain field/saved result | Named README definition and named saved table/evidence; Overview only when resolving model/year/basis | No project artifacts; identity and scoped missing/status checks | Explain saved meaning. Conflicting identities remain a gap; no fresh science claim. |
| Wording/layout edit | Named DOCX/notes, document-production rendering/link/preservation sections, relevant template field only | Named isolated/final authorized artifact; package/manual/link comparison and all-page render | Bounded edit verified; changed scientific claims require their affected evidence route. |
| Review/signoff sync | Latest signed DOCX, signoff reference, regional Settings/Groups, central Models and page fingerprints | Existing register_review + refresh_reviews; exact Word/Project/page equality and rollback snapshot | Registered actual decision only. Ambiguous signer/verdict/exclusion or stale page stops dependent work. |
| Existing selection | Overview, discovery/registration, model and snapshot identities; project-integration selection contract | Existing single refresh; preservation/readiness/pending/rollback checks | Saved selection and its actual readiness; unknown provenance blocks numerical reuse. |
| Regional arithmetic | regional-calculation, applicable saved input/configuration/coefficient identities | Existing calculate stage and authorized scoped publication; masks, totals, ratios, comparisons | Dependent arithmetic regenerated; missing coefficient/new taxon triggers gap or targeted mapping. |
| One mapping/confidence | Named taxa, relevant template M/W/C rules and regional-calculation; size-stage reference only if applicable | Proposals by default; authorized exact rows and dependencies only; unrelated rows/group weights protected | Targeted review/adoption, not full validation. New numerical repair needs separate authorization. |
| Full validation | Entire template guide, full-validation, evidence/calculations, document-production, acceptance; relevant pipeline references | Complete saved-evidence review, Word/appendix/evidence; all required diagnostics, taxa, geography, arithmetic and render checks | Full applicable review, with unavailable/unaligned evidence explicit. Fresh science requires existing scoped authorization. |
| Extraction/taxonomy | model-preparation/reconstruction-audit and extraction procedure/resources; group-taxonomy if requested | Isolated latest imports/JSON/notes/evidence; source cells, missing masks, round trip and loader checks | Only independently performed stages. Unavailable original bytes or incompatible native equations remain incomplete. |
| Direct diagnostics | direct-diagnostics, reconstruction-audit and exact settings evidence | Authorized GE/TE/With Egestion full returns and lossless matrices, axes/masks/status checks | Exact methods/settings actually run; constructor/exception/timeout retained separately. |
| Complete pipeline | Union of applicable extraction/taxonomy/diagnostic/mapping/arithmetic/integration/report routes | All authorized stages and integrated checks | Full pipeline only when every required stage actually completed; otherwise list incomplete stages. |

## Frozen comparison criteria (before implementation)

- Exact: model/group/taxon IDs, requested period/area, field names/types and missing/null/nonfinite masks; source-extracted decimal inputs/diets, flags and status strings; mapping groups/weights/confidence/assumptions; manual text/deletions/signatures/breaks/hyperlink targets; full snapshot bytes.
- Spreadsheet numerical storage: compare typed values and masks, not ZIP timestamps. Input decimal numbers compare as decimals; Excel storage uses existing 16-significant-digit digest convention.
- Deterministic engine/regional numeric comparison: `rtol=0`, `atol=1e-12` (existing runtime-equivalence contract). Record maximum absolute differences and changed keys. No relaxation after failure; a failure can demonstrate a scientific or baseline mismatch and stays recorded.
- Required direct diagnostic matrices: unique axes and order, dimensions, null/nonfinite masks exact; finite values under the same tolerance; full status/component flags exact. GE/TE report scope remains distinct from the direct default GE/TE/With Egestion.
- Mapping totals and carbon conversion: unrounded catch and known-PPR denominators, zero catch contribution versus missing coefficient, original allocations and `/9` once. Report percentages retain two-significant-digit display; existing rule-table closure tolerance `1e-8` percentage points is display arithmetic only.
- DOCX: unchanged parts/manual cells exact except explicitly named edit; expected scientific statements, appendix ordering and links preserved; inspect every output page. Byte identity is required for copied snapshots, not regenerated DOCX/XLSX packaging.
- Efficiency: matched task/input/runtime/agent settings, cold versus reused-context labeled. Count observed requested/unique/repeated reads, workbook parses, engine/render calls, writes/checks, wall time; tokens unavailable unless actual tool telemetry supplies them. Static routing tests and instruction length are supplementary only.

## Task 1: Baselines and cases

**Files:** This plan; run `inputs/` old instruction checkpoints, `qa/` hashes and observed traces; `code/` trace reader and input preparation.

- [x] Record clean baseline SHA and permitted live artifact hashes. Preserve only instruction checkpoints and compact comparison metadata.
- [x] Instrument actual agent reads/parses/engine/render/writes/checks. Run old-skill explanation trials before changing either skill; retained task inputs remain identical.
- [x] Freeze representative real cases: SCS-2007 northern South China Sea 2000s (multi-period original publication, blind source extraction); LME_047 JSON-only 1997 candidate (missing fields); LME_036 current model (flags/full diagnostic matrices, split/assumed mappings and human edits); LME_027 signed disqualification; LME_038 pending selection and protected historical evidence. Trial preparation found that the initially named LME_034 is validated; LME_027 is the actual signed rejection in the current registry.
- [x] Verify required input bytes are actual files, not LFS pointers. If source does not supply a full extractable model, retain that finding and select another available paper case; never copy retained answers.

## Task 2: Bounded workbook reads

**Files:** Modify `tools/project_core/workbooks/workbooks.py`, `tools/cli/region.py`; create `tools/project_core/workbooks/read_session.py`, `tools/workflow_checks/structure/test_read_session.py`.

**Interfaces:** `read_book(path, *, sheets=None)` retains its current complete default and table/formula semantics. `ReadSession.read(path, *, sheets=None)` caches a deep-copy result by resolved path, selected sheets and actual SHA; `assert_unchanged()` verifies the hashes of all currently consumed inputs. `read_count`/`parse_count` expose observed operation counts. Regional `inspect --region ... --sheet ... --table ...` emits only a requested table and input SHA, with an explicit scoped-read label and no readiness claim.

- [x] RED: meaningful selected-sheet, formula rejection, same-mtime input mutation, return-mutation, missing-sheet and stale-before-publication tests fail on absent API.
- [x] GREEN: implement optional selection and operation-local session, plus read-only inspect CLI. Reuse input hashes; do not persist a cache or use timestamps as identity.
- [x] Verify legacy complete reader semantics, selective exact equality, one parse on unchanged repeated read and fresh parse on changed bytes. CLI must preserve workbook bytes and reject absent target tables.

## Task 3: Route the pipeline skill

**Files:** `tools/skills/paper-to-ppr/SKILL.md`, shared `references/operation-contract.md`; conditional affected references only where they conflict with the route.

- [x] Use the old actual trials as baseline; record whether excess reads occurred.
- [x] Add the operation table before detailed references; consolidate duplicate contract reads; make evidence-handoff stage-specific.
- [x] Keep extraction/taxonomy/direct-diagnostic/mapping and adoption contracts unchanged in their applicable routes. Run fresh matched revised trials and verify answer correctness/no writes.

## Task 4: Route validation and preserve full review

**Files:** `tools/skills/ecopath-model-validation/SKILL.md`, new `references/full-validation.md`; same shared contract.

- [x] Move the full scientific/report workflow intact into full-validation; leave authorization/exclusion and identity boundaries visible at the entry.
- [x] Route explanations, wording/layout, named mapping and signoff separately. A Word edit retains full render QA but does not reassess unrelated taxa/diagnostics/geography.
- [x] Run old/new bounded Word and review-sync trials on identical isolated real documents; compare edits/signatures/links and render every output page.

## Task 5: Replicate and classify evidence

**Files:** Run outputs/qa and reusable comparison code if needed; no live scientific output promotion.

- [x] A fresh extracting agent receives original paper/native bytes and instructions only, with explicit exclusion of retained tables/JSON/review answers until it finishes. Compare its independently completed stages against the latest retained model, recording departures and masks rather than overwriting either.
- [x] Independently consume a JSON-only candidate, retain genuine missing fields and perform its applicable conversion/load checks; classify this separately from paper extraction.
- [x] Regenerate the chosen real model's authorized direct diagnostics with its recorded configuration, preserving full returns and matrices. Compare with saved current evidence; do not label tool regeneration independent extraction.
- [x] Independently verify mapping summary/denominators and human report preservation from intentionally supplied saved evidence. Verify signed rejection sync and pending-selection behavior in isolated projects with existing APIs/tests. Report-only reuse is labeled reuse.
- [x] Compare matched overhead with correctness; record all unmet replication stages explicitly. No broad Monte Carlo or complete-pipeline claim from a partial trial.

## Task 6: Review, graph and publication

**Files:** Plan execution record, current graph/scope/provenance, affected docs and checks.

- [x] Run focused changed-dependency tests; leave unchanged broad-suite failure disposition intact. Check live protected hashes and exact diff for accidental scientific edits.
- [x] Fresh agent reviews the whole change against the spec and evidence; resolve material findings with focused regression checks.
- [ ] Refresh changed semantic sources/AST in the one canonical graph; reuse unchanged sources only after actual full hashes; validate endpoints, freshness, locations and retrieval/HTML.
- [ ] Inspect staged diff and focused whitespace check, commit and ordinary push to verified origin/main; independently verify remote SHA. Preserve publication proof outside graph corpus self-metadata.
- [ ] Final report states independently replicated stages, reused/regenerated stages, measured savings, known defects and incomplete work.

## Execution record

2026-10-04 resumed: The user authorized continuation. Mapping is now explicitly one shared decision stage across both skills; full validation verifies the same keyed membership/weights/confidence evidence without a second research pass, and returns only affected gaps to that stage. The fresh handoff trial and final evidence summary are closing in the run QA. Both edited Word trial documents have all 17 named package parts byte-identical; the completed six-page render/inspection is explicitly reused for the revised trial, with no successful new export claimed. The graph refresh will retain full-hash eligible semantic evidence and every independently attributed relationship; changed/new documents receive actual fresh extraction. Graph and publication closure are recorded outside the graph corpus in the run QA to avoid self-referential source hashes. The unchecked Task 6 graph/publication/report boxes describe this capture point; the final closure record supersedes their pending state.


2026-10-04 safe stop requested by the user. The implementation and trial artifacts remain uncommitted on baseline `85ae543693887a5439fb13ebd84bcb91f8ecc360`; no push or graph refresh was started. Resume from the run's `qa/resume_handoff.json`. All 461 protected live scientific/workbook/report/page hashes were checked at stopping and remain exact. Optional sheet reads, the read-only inspect CLI and the content-checked read session are implemented. The final 11 read-session tests pass; the earlier focused dependency run passed 52 methods. Fresh review resolved the observed parse/publication-change guard and parser-count findings. Both scientific workflows remain intact after relocation and the expressly added single-mapping handoff paragraph.

Completed evidence at stopping: old/new field explanation and zero/missing definition traces; the controlled workbook benchmark; independently extracted original SCS-2007 source values and round trip; JSON-only loader/missingness check; exact full diagnostic return/matrix regeneration using verified historical code and current compatibility settings; complete 374-taxon saved-mapping arithmetic; bounded LME_034 signed validation synchronization. Known mismatches remain: independent extraction role/missing-mask/name differences, strict source diet constructor failure, GE/TE aggregate coefficient differences above the frozen tolerance, and the inherited missing LME_027 source hyperlink blocking real rejection synchronization. Full pipeline equivalence is not established. Old Word all-page QA passed; new Word export is incomplete and its own renderer is being cleaned up. The new single-mapping handoff trial is saved as partial. Finish those bounded checks, compile the evidence report, prune temporary duplicate scientific copies with explicit dispositions, refresh/verify the canonical graph, then commit and publish when the user resumes.

2026-10-04 steering: The user required taxon-to-group mapping to occur once per pipeline run across both active skills. The shared operation contract now merges both routes' requirements before the one mapping stage and requires a keyed evidence/content-identity handoff. Validation verifies and reports the same rows; it revisits only affected decisions when dependencies or evidence change, preserving full-universe confidence checks and adoption boundaries. A fresh bounded handoff trial verifies this route separately from the old/new explanation benchmarks.

2026-10-04: Publication barrier lifted with observed baseline `85ae5436`. Read-only preflight found duplicate must-read instructions in both skills, unconditional full evidence/template pulls before validation routing, and existing narrow review/page APIs. Selection mutation remains the existing transaction-owning refresh. No efficiency implementation or replication claim is made by this plan.
