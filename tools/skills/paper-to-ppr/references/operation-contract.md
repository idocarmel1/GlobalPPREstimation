# Scoped operations and shared dependencies

This is the shared execution contract for the two active project skills. It is guidance, not an editable selection/status registry. Read the entry skill and root project_contract first. An unchanged contract already read in the same execution context need not be reread; a new context or changed contract does require reading it. Record the requested operation, exact target and existing authorization/exclusions before choosing detailed references. Composed requests use the union of applicable routes.

## Route and finish the requested operation

| Operation | Additional references and inputs | Work and verification | Permitted claim / escalation |
|---|---|---|---|
| Explain a field or saved result | Relevant README definition; named saved table/evidence. Overview only to resolve target/year/basis. | Read-only answer; check applicable identity, missingness and status. No new evidence package. | Explain the saved meaning. A scoped read is not readiness, fresh science or full review. Conflicts stay explicit. |
| Edit named report wording/layout | Exact authorized document/notes; relevant field definition; [document production](../../ecopath-model-validation/references/document-production.md) preservation, links and rendering sections. | Change named content, preserve unaffected science/manual cells/deletions/signatures/breaks/links; compare parts and render/inspect every output page when Word is edited. | Bounded edit only. A changed scientific assertion needs its affected evidence route; no unrelated taxon/diagnostic/geography reassessment. A changed signed source needs fresh authorized registration before display. |
| Synchronize researcher review/signoff | Latest actual signed Word; [signoff handoff](../../ecopath-model-validation/references/researcher-signoff-and-map.md); exact Settings/Groups, central Models, pre-registration Project and page fingerprints. | Existing `read_report`, `register_review`, `refresh_reviews`; serialize central writes, preserve snapshot until source/page equality passes. Validate percentage format only when validated confidence tables transfer. | Actual source decision registered; no new science/reselection. Ambiguous signature/verdict/date/exclusions or stale page stops dependent work; do not fall back to a full build. |
| Select an existing registered model | Overview choice/rationale; [project integration](project-integration.md) selection section, canonical discovery, model and snapshot identities. | `python tools/cli/region.py refresh --region regions/<type>/<unit>`; inspect actual ready/pending state and saved identity. Preserve independent inputs, diagnostic restrictions and full snapshots. | Saved selection plus actual readiness. Missing/unknown historical code/flags block numerical restoration; do not invent provenance or mapping. Selection does not authorize extraction or parameter repair. |
| Recalculate regional arithmetic | [Regional calculation](regional-calculation.md); exact current Catch/Classic/Groups/coefficients/Matching/NPP and applicable model/settings identity. | Existing `--stage calculate`, then only authorized affected publication. Reconcile taxon/annual totals, denominators, masks, ratios and comparisons. | Arithmetic on compatible retained coefficients; no fresh extraction/SPPR. Missing coefficients or new taxa stay unavailable or need the affected scientific route. |
| Review named mapping or confidence | Named taxa and their source/group definitions; relevant M/W/C rules in [template guide](../../../templates/instructions.md); regional-calculation. Read [size/stage allocations](size-stage-allocations.md) only when applicable. | Review named decisions; proposals remain unadopted by default. For authorized adoption, preserve unrelated rows and group coefficients; confidence-only work proves groups/weights unchanged. Reconcile affected totals and views. | Targeted review/adoption, not complete validation. Membership and weight confidence remain separate; scientific repairs require their authorization. |
| Full model validation | Complete [template guide](../../../templates/instructions.md), [full validation workflow](../../ecopath-model-validation/references/full-validation.md), [evidence/calculations](../../ecopath-model-validation/references/evidence-and-calculations.md), document-production and [acceptance checks](../../ecopath-model-validation/references/acceptance-checks.md); applicable pipeline references. | Complete required catch-taxon universe (including zero rows), exact GE/TE negative source/group pairings and matrices, source/flags, geography/time, confidence/assumptions, denominators, appendix and all-page render. | Full applicable review only with unavailable evidence/unaligned proposals explicit. Saved evidence reuse is not independently regenerated science. Fresh runs need existing explicit scoped authorization. |
| Extract/convert a model | [Model preparation](model-preparation.md), [reconstruction audit](reconstruction-audit.md), extraction procedure and applicable resource references. [Recovery](missing-data-recovery.md) only for missing sources; [taxonomy](group-taxonomy.md) when requested. | Original paper/native bytes, requested period/area only; exact source-cell/missing masks, imports, round trips, loader, departures and applicable taxonomy. Apply [evidence handoff](evidence-handoff.md) to this stage. | Only completed extraction stages. Missing original bytes or unrepresented native equations remain gaps; canonical schema loadability is separate from construction/results. |
| Direct model diagnostics | [Direct diagnostics](direct-diagnostics.md), reconstruction-audit, source departures and exact effective settings/code evidence; evidence-handoff for this stage. | Authorized GE/TE/With Egestion by default; each full return, lossless matrix/axes/masks/status, before/after runtime state and saved coefficient reconciliation. Handle options independently. | Exact methods/configurations actually run. Constructor/exception/timeout records are not successful diagnostics. Global/inventory/Monte Carlo require a broader request. |
| Full paper-to-PPR pipeline | Union of all applicable extraction/taxonomy/diagnostic/selection/mapping/arithmetic/integration/report routes. | Finish every applicable authorized stage; keep independent stages moving while dependent gaps remain explicit. | Full pipeline replication only if all required stages were independently completed from appropriate inputs. Otherwise name completed, reused/regenerated and incomplete stages separately. |

Full-route scientific procedures remain mandatory within their scope. A router cannot waive diagnostic matrices, evidence, rendering, uncertainty, denominator or authorization requirements. Read the relevant reference completely when its stage needs the whole procedure; bounded definitions/edits may read the named sections only.

For a Word edit that touches parser-consumed headings or field labels, compare the existing signoff parser's identity/date/sections/source-reference summary before and after. Exact DOCX part/link preservation and identical rendering alone do not prove registration compatibility. An unexpected summary change remains a keyed gap and blocks adoption of that edited report; do not repair the parser or rewrite the source decision as part of a wording task. An authorized semantic review change follows its affected evidence and registration route.

## One mapping stage per pipeline run

The pipeline and validation skills share one taxon-to-model-group decision set for the exact model-region pair. At the start of a composed run, combine their mapping requirements: complete catch-taxon universe (including zero rows), exact source group membership, group identifiers, weights, separate membership/allocation confidence, assumptions and source evidence. Resolve or reuse each taxon's decisions once in the mapping stage. Do not dispatch separate pipeline and validation agents to independently map the same taxa.

Hand off the existing regional `PPR / Matching` rows and their keyed evidence/audit rows, or the authorized proposal when adoption is pending. Record in the existing stage trace/evidence the model/region identity; current content hashes for group/source definitions, taxon universe, matching rows, relevant allocation inputs and rules; and the exact groups/weights/confidence/reasons plus unresolved or proposed status. Use the existing model-local evidence locations; this handoff is provenance, not a new configuration or approval sidecar. Current researcher edits and source departures remain inputs.

Validation verifies identities, complete taxon coverage, evidence support, weights and confidence against that same decision set; it uses those rows for the appendix, confidence/rule summaries and denominators. Verification and report arithmetic are separate from resolving mappings: they do not repeat taxonomy lookups, group selection or allocation calculations already established in the stage. Full validation still checks all High/Medium/weak/zero-catch records and all required component criteria. Unadopted proposals stay outside adopted summaries and leave alignment pending.

If a dependency changed, a required decision/evidence is absent, or verification finds a conflict, record the keyed gap and revisit only affected taxa/decisions in the same mapping stage within existing authorization. New interpretation or adoption still follows the applicable approval boundary. An explicitly requested independent mapping audit is a separately labeled audit; never claim that it is reuse or silently merge its proposals. Otherwise an unchanged completed mapping stage is consumed by both skills once, including across retained years/bases with its extrapolation documented. Recheck mutable inputs before publication.

## Dependency checks and safe reuse

| Changed input | Affected work | Reusable only after applicable identity checks |
|---|---|---|
| Descriptive notes | Named notes/report and authorized review display | Unchanged scientific inputs/numerical outputs; no new full evidence inventory |
| Selection | Model-dependent regional tables, shortcut, central summary and views | Current Catch/Classic/NPP; explicitly compatible target results/matching |
| Confidence only | Confidence/coverage/review summaries | Coefficients/arithmetic if exact mapping groups/weights and numerical dependencies remain unchanged |
| Mapping groups/weights | Taxon/annual PPR, ratios/comparisons/coverage and affected report/views | Unchanged group coefficients; unrelated authored decisions |
| Model values or effective flags/code | Coefficient/diagnostic/results and review freshness | Independent regional inputs; matching only where groups/taxa/assumptions remain applicable |
| Catch/taxon universe | Arithmetic/coverage; new taxa require mapping review | Current compatible coefficients and unchanged mapping rows |
| NPP | Dependent ratios/views | PPR numerator and model coefficients |
| Relocation | Paths/links and provenance | Unchanged scientific values; source identity alone does not renew approval |

Use actual content/dependency hashes, never modification times alone. A cached manifest does not prove present source bytes. Check current model/configuration and the dependencies relevant to the route; recheck mutable permitted inputs before adoption/publication. Preserve missing evidence, FAIL/NOT_RUN/provisional restrictions, uncertainty and researcher review identity. Do not rewrite fingerprints to bypass a gate.

Read/parse each workbook once per coherent operation where practical. Existing workbook commands remain the authority for writes. For narrow saved-table inspection:

```powershell
python tools/cli/region.py inspect --region regions/LME/LME_038 --sheet Overview --table Settings
```

This emits one saved table and its input hash, with no readiness assessment or write. The complete `read_book(path)` default still reads all tables and rejects unsupported authoritative formulas. `read_book(path, sheets=[...])` is scoped evidence and checks formulas in the selected sheets only.

For repeated reads in one Python operation use the [read session](../../../project_core/workbooks/read_session.py):

```python
from tools.project_core.workbooks.read_session import ReadSession
reads = ReadSession()
book = reads.read(path, sheets=['Overview'])
# Further unchanged reads with the same scope reuse parsed tables, returning copies.
reads.assert_unchanged()  # Supplement existing mutation/publication guards.
```

The session is temporary in memory, validates full input hashes on reuse, and reparses changed bytes. If an input changed during the operation, its publication guard rejects the mixed-version session even after a reread; start a new coherent session. It is not a persistent registry, approval, full-workbook validator or replacement for selection/review transaction guards. New contexts/changed files reacquire applicable evidence. Keep exclusions before reading/hashing/copying/rendering; never touch an excluded file merely to prove preservation.

Serialize Project.xlsx writes. Use canonical discovery and model-local outputs under the structure contract. Preserve rollback snapshots until affected acceptance checks pass. A bounded refresh failure does not authorize bypassing it with a broad build. No numerical repair, guessed scientific provenance or new selection follows from an administrative request.

## Evidence and truthful completion

Reuse compatible saved outputs when appropriate; regenerate tools only when requested/authorized and needed. Independent extraction receives original inputs with retained answers hidden until comparison. State which evidence was independently extracted/reviewed, which was reused, which was regenerated and which required stage is incomplete. A partial-stage trial cannot be called a full pipeline replication. Preserve latest-only model extractions; temporary benchmarks must not become another extraction archive.

Measure actual matched traces to claim efficiency: required/unique/repeated reads, workbook parses, engine/render invocations, writes/checks and elapsed time. Label cold/reused contexts and unavailable token telemetry. Instruction length and routing assertions alone prove no performance improvement.
