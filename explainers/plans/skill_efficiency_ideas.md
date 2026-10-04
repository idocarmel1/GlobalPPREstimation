# Ideas for Faster, Scoped Skills with Reliable Replication

**Status:** Ideas and acceptance requirements, not an implementation plan. Develop the detailed plan **after project reorganization**, against the actual reorganized code, tools, skills and retained current evidence.

**Predecessor:** [Project reorganization plan](project_reorganization_plan.md).

**Objective:** Reduce unnecessary work for simple actions while preserving the ability to reproduce existing scientific work correctly. Keep the two agreed project skills; improve their routing, references, tools and verification rather than adding many overlapping skills.

No skills have been changed and no replication or performance tests have been performed by creating this file. Do not start implementation or dispatch an agent merely because the ideas are recorded.

## 1. Constraints inherited from the agreed reorganization

- Respect root AGENTS.md's `project_contract`, including the must-read `explainers/structure.md`.
- Use the reorganized region/paper/model layout and the two active skills under `tools/skills/paper-to-ppr/` and `tools/skills/ecopath-model-validation/`.
- Retain only the latest extraction of each distinct model. Do not recreate a legacy extraction archive for testing or caching.
- Keep one Ecopath-compatible, loadable `model.json`; put scientific source departures in adjacent `model_notes.md` and the validation document's model extraction row. Do not add source_model.json or computational_input.json.
- Preserve model-local results, generated loading/configuration provenance and full regional workbook snapshots. Automated restoration still preserves current independent catch, classic PPR and NPP.
- Preserve scientific rules, model identities, missingness, units, method/scope restrictions, diagnostic failures, assumptions, review states and researcher edits.
- Respect existing authorization and exclusions. A report wording edit is not permission to recalculate, repair model parameters, adopt mapping proposals or publish a new scientific selection.

## 2. Highest-priority improvement: route before reading everything

Put an operation router at the start of both skills, before unconditional detailed template/evidence/reference reading. A matched skill should not automatically start its complete scientific workflow.

| Requested action | Intended scope |
|---|---|
| Explain a field or saved result | Read the relevant definition/evidence and answer; no generated scientific artifacts. |
| Edit report wording/formatting | Preserve scientific content, change the named material and verify document/layout/links. |
| Synchronize review notes/signoff | Register the actual authorized source and update only relevant review metadata/page sections. |
| Select an existing model | Use the one-refresh workflow, restore compatible material and show readiness/pending status. |
| Recalculate regional arithmetic | Use existing compatible coefficients/matching and update affected results. |
| Review one mapping | Investigate named taxa and their dependencies, leaving unrelated mappings unchanged. |
| Fully validate a model | Perform the complete applicable scientific review and report workflow. |
| Extract a new model | Independently execute the requested extraction and its scientific checks. |
| Run a complete pipeline | Perform all applicable authorized stages and verify the integrated outcome. |

For each route, the eventual plan should define exact required references, files read/written, applicable checks, completion claims and escalation triggers. Composed requests use the union of their required stages, not all references. Ask only for missing choices that materially change the work.

The current skills already contain scoped language and a bounded researcher-signoff route. Strengthen and surface these rather than creating a conflicting replacement policy.

## 3. Distinguish bounded edits from fresh scientific reviews

A request to change an extraction-note paragraph should not trigger reassessment of every taxon, all diagnostics and geography. A bounded edit preserves unaffected scientific findings and reuses their current evidence; it must not claim fresh full validation.

Full validation still reviews the complete required taxon universe, source/group negative pairings, applicable diagnostic matrices, geography, confidence/assumptions and report arithmetic.

Keep artifact QA where necessary. Word edits that may change pagination require the applicable full render/inspection workflow; saving time must come from avoiding irrelevant scientific work, not skipping required visual verification. Preserve manual cells, deleted prose, signatures, rounding, links and anchors.

## 4. Define shared dependencies and route-specific evidence

Use one shared dependency contract referenced by both skills, with stage detail elsewhere. Do not create another authoritative selection/status file.

| Change | Affected work | Generally reusable material, subject to identity checks |
|---|---|---|
| Descriptive notes | Changed report/notes and applicable bounded review display | Scientific inputs and numerical results |
| Selection | Model-dependent regional state, shortcut, central summary and views | Independent catch/Classic PPR/NPP and compatible target results |
| Confidence only | Confidence/coverage/review summaries; prove groups/weights unchanged | Numerical coefficients/results when their inputs are unchanged |
| Mapping groups/weights | Taxon/annual PPR, ratios/comparisons/coverage and affected report/view figures | Unchanged group coefficients |
| Model values/loading flags | Invalidate incompatible coefficients/diagnostics/results/review freshness | Independent regional data and demonstrably applicable matching |
| Catch or taxon universe | Affected arithmetic and coverage; new taxa require mapping review | Unchanged model coefficients and compatible matching rows |
| NPP | Dependent ratios and views | PPR numerator and model coefficients |
| Relocation | Paths, links and provenance | Scientific values with unchanged dependencies |

Do not reconstruct the entire extraction/diagnostic evidence bundle for a notes-only task. Reuse a compatible current index and verify identities applicable to the operation. Fresh scientific stages still retain all required matrices, axes, masks, flags, source locators and numerical reconciliations. Missing evidence remains missing.

## 5. Move mechanical work into reusable tools

Inspect the post-reorganization helpers first. Reuse or extend existing tools for model/result identity, snapshot compatibility, mapping weights, denominator reconciliation, link checks and bounded Project/map publication. Avoid repeatedly constructing one-off Python scripts for the same checks.

Read/parse each workbook once per coherent operation where possible; reuse the parsed data until it changes. Read detailed references only for the selected route after reading the mandatory project contract. A contract already read in the same unchanged execution context need not be redundantly reread; new agents/contexts and changed files must read it.

Use dependency/content hashes for reuse, not modification times alone. Recheck relevant mutable inputs before publication. Cached manifests do not prove present bytes or scientific correctness. Prefer current evidence/result packages and temporary in-memory reuse; no new extraction archive or competing cache registry.

Keep concurrent central-write and stale-page guards. A failed bounded refresh must not silently fall back to a broad build that bypasses those guards.

## 6. Essential requirement: correctly replicate existing work

The later implementation plan must demonstrate scientific fidelity, not merely shorter instructions. Distinguish these proofs:

1. **Reuse:** correctly consume compatible saved outputs. This proves reuse, not regeneration.
2. **Tool regeneration:** rerun tools on identical inputs/settings and compare outputs. This does not prove the agent independently performed extraction or interpretation.
3. **Independent skill replication:** the revised skill performs each claimed applicable stage from its appropriate inputs in isolation, then compares against retained current work.

An extraction-only or diagnostic-only trial must not be called a full pipeline replication.

### Representative cases

After reorganization, choose concrete retained models covering:

- A complete paper extraction with multiple periods/models, extracting only the requested one.
- A JSON-only EcoBase route with genuine missing fields.
- Documented source departures and nondefault loader flags.
- Diagnostic failure, negative contribution or unavailable matrices.
- Split-group/assumed mapping, confidence rules, and zero-catch versus missing-coefficient cases.
- A human-edited validation document with manual rows, deletions and portable links.
- Signed disqualification/review-date synchronization and pending selection without results.

One real model may cover several cases. Use labeled synthetic fixtures for absent behaviors and disclose that they do not prove real-model replication. Use only latest retained extractions; baseline old skill instructions can be read from a committed version or temporary checkpoint without installing a third skill.

### Independent inputs and isolation

For extraction replication, provide the original paper/native inputs but hide completed extraction tables, reconstructed model answers and previous validation findings from the extracting agent until comparison. For report-only replication, saved scientific evidence is intentionally supplied and must be reused correctly.

Use isolated temporary projects or approved fixed work folders. Do not alter live regional selections, Project.xlsx, current human reports or maps during benchmarks. Explain concrete expensive run scope and obey the future execution session's scientific authorization/exclusions. If required fresh stages cannot run, label their replication incomplete instead of copying old answers.

### What to compare

Compare model/group IDs, periods/scopes, fields/diets, missingness, import schemas, taxonomy, mapping groups/weights/confidence/assumptions, effective flags, coefficients, applicable full diagnostic matrices/masks/axes/statuses, taxon/annual outputs, denominators and carbon conversion.

Compare reports semantically: scientific statements/numbers, human edits/deletions, signature state, appendix ordering, links/anchors and rendered layout. Packaging/timestamps may differ in regenerated DOCX/XLSX; an exact full-workbook snapshot copy must remain byte-identical.

Freeze scientific tolerances before changes, using existing domain tests where available. Report exact equality separately from approximate equality, with maximum differences and changed keys. Do not loosen tolerances after failure or erase null/nonfinite-mask differences.

Keep diagnostic and reporting scopes distinct: the pipeline's ordinary direct route includes GE/TE/With Egestion under its contract; the validation report's agreed rows are GE/TE. Do not add broad Monte Carlo runs to a speed trial. If stochastic behavior is explicitly tested, use an established seeded/statistical validation contract or disclose it was not replicated.

## 7. Measure actual overhead and correctness together

Record route choice, references read, unique/repeated reads, workbook parses, scientific engine invocations, outputs written, checks performed, total time, engine/rendering time and task tokens when available. Compare matched old/new instructions with the same inputs/model/runtime as far as possible; distinguish cold and reused-context runs.

Mandatory scope checks:

- Explanation performs no project write, full scientific run or new evidence package.
- Bounded report edit does not reassess all mappings/diagnostics/geography or change scientific workbooks.
- Review sync does not reselect, recalculate coefficients or force a full rebuild.
- Ready selection/arithmetic does not trigger new extraction, guessed mapping or unrequested broad SPPR.
- Targeted mapping preserves unrelated decisions while reconciling affected totals.

Accept efficiency only alongside correct outputs and preserved scientific behavior. Report measured reductions and limitations; do not promise arbitrary seconds/percentages. Static wording tests cannot replace observed agent traces and replication results.

## 8. Questions the later planning agent must resolve from actual code

- Which post-reorganization commands already provide the required bounded checks and updates?
- Which broad resource/evidence requirements should become conditional, and which are scientifically mandatory for full routes?
- Where can parsed workbook/reference reuse happen safely without weakening freshness checks?
- Which actual retained models provide the representative cases, and which source bytes are available through Git LFS?
- What existing comparison tolerances and rendering/test runners apply?
- What can be measured reliably from agent/task traces, and how much benchmarking is justified?
- Which concrete files/APIs need changes, and what independently testable task order should implement them?

Resolve these after migration; do not freeze speculative new APIs/file layouts in advance. The detailed plan must include executable checks, scoped replication runs, required outputs and evidence-based completion criteria.

## 9. Proposed subsequent workflow

1. Finish the reorganization plan, its knowledge-graph refresh and verified commit/push handoff.
2. Have the next planning agent read the actual project_contract, current code/skills, this file and the reorganization execution record.
3. Turn these ideas into a concrete skill-update implementation plan, with selected real cases and frozen replication criteria.
4. Implement scope routing, shared dependencies and needed helpers; test simple actions and independently replicate claimed full workflows.
5. Record correctness/efficiency evidence; update documentation and the current knowledge graph; commit and push verified changes within the authorized implementation scope.

The future final report must state which work was independently replicated, which was only reused/regenerated, what remained incomplete, and which simple actions became narrower/faster.
