# Coordinator handoff: bounded negative reviews

All work is model-local. No Project, page, regional workbook, report or scientific source was modified.

## Proposed shared change

1. Install `code/candidate_row.py` as `tools/project_core/registry/review_candidates.py` (same code, rename only).
2. Apply `outputs/build_html.patch` to the current `tools/project_core/maps/build_html.py`; review against concurrent edits. The full proposed file is reference only, not a wholesale replacement recommendation.
3. Keep the legacy API. New `_refresh_reviews(..., [], model_pairs=[(unit,model),...], candidate_rows=[{'row': exact_metadata, 'canonical_sha256': digest}])` supports multiple exact models for one unit. It rejects duplicate scope, mixed legacy/new scope, and candidate additions outside review scope.
4. Replay candidate-row insertion into the real prior workbook copy BEFORE replaying all reviews. The old all-ZIP-parts equality gate and real pre-registration page fingerprint remain intact. Newly inserted candidates must have verified source-only negative reviews. Candidate page creation already uses existing unavailable_review_model: verified=false, scopes={}, own canonical source and exact review. No numbers are copied.

The row helper writes only the Models XML and its existing native table extent; every other ZIP part stays byte-identical. It fails closed for existing keys, selected=true, scientific/readiness fields, absent schemas, ambiguous/missing source paper, DOI/year/unit mismatch, canonical hash/path mismatch and non-final Models blocks. Unknown fields remain absent. Caller holds the lock and checkpoints the real Project immediately after each insertion, exactly as for _register_review. The helper intentionally does not attach publication journaling to replay temp files: deleting a journaled temp before rollback would cause a false conflict.

## Driver and runtime sequencing

`code/register_negative_batch.py` defaults to read-only preflight. This passed for all three canonical/report hashes and Ido Carmel / 2026-11-14 disqualification identity. To publish, the coordinator runs with `--execute` ONLY after the shared patch checks below and after its current batch has finished.

It acquires central_lock, rechecks current sources, snapshots the THEN-current Project into this run's outputs timestamp folder, enters publication_transaction, inserts the one exact known-source candidate, registers 024 and both 026 decisions with [], and performs the extended bounded gate followed by publication. It checkpoints each owned central write for coherent rollback. Regional workbook/source/report hashes are rechecked before and after publication. No mutable Project baseline is pinned in this preparation. It does not alter sources.html because the existing bounded review API only publishes map/trends; this is unchanged behavior.

Preserve current original 026 selection. Do not run index_candidates, full build, coverage or arithmetic. Candidate proposal metadata remains the existing signed-binding output, not guessed from original model readiness. Expected immutable source hashes are in the driver and its preflight passed.

## Verification completed

Two focused tests passed on isolated copies of current Project (32.472 seconds initial green). Checks prove exactly two changed ZIP parts, selected boolean false, blank production eligibility, duplicate insertion rejection, and zero mutation for bad source hashes, selected=true and injected production eligibility. Tests were first run red before helper existed. A follow-up run after removing temporary-file publication journaling is recorded separately. Driver dry preflight passed; proposed build_html code compiles. No end-to-end shared gate or actual publication has been claimed.

## Required focused gate tests before installation/publication

Run existing researcher disqualification and model-boundary tests unchanged. Add fixtures covering: two exact reviews for one unit and one candidate insertion together; legacy API unchanged; duplicate/mixed scopes fail; candidate outside scope fails; positive/selected candidate rejected; missing candidate in previous workbook successfully replays; unrelated central XML change rejected; wrong page baseline fingerprint rejected; candidate verified=false/scopes={} and exact source; selected model/default/scientific payload identical; replay source changes rejected; rollback restores Project and both pages after induced second-page failure. Keep fixture writes inside a model-local temp root. Gate replays temp Project beside its ROOT, so do not run a live-root trial merely to call publish=False.

After successful actual publication, compare fresh read_report to exact Project rows and both payloads: verdict, exact reason, Ido Carmel/date, exclusions=[], no positive sections/pending review; source-only candidate reviewed input hash blank; candidate selectable and excluded from validated filter; red disqualification presentation. Preserve the actual pre-registration Project until these controls pass.

## Completed focused gate verification (supersedes pending-test paragraph above)

The coordinator-requested isolated gate suite is now implemented and passed against outputs/build_html.proposed.py imported via importlib, with candidate_row injected only in that Python process. Seven tests passed in 25.719 seconds: both exact reviews plus new candidate, legacy selected API, unrelated ZIP-part rejection, wrong page baseline rejection, mixed/duplicate/out-of-scope request rejection, source-only-negative restriction, exact science/default/payload preservation, and rollback after induced second-page failure (some tests contain several assertions).

Existing disqualification and model-boundary tests were reused against the proposed refresh function: 12 tests passed in 36.317 seconds. They exercise actual shared parser/registration logic and existing source-only model boundaries.

Fixture testing found trailing empty rows emitted by write_book; candidate_row now reuses an empty next row and still refuses any later populated content. This fix is model-local. Parent must install the latest candidate_row.py, not an earlier copy.

Install `outputs/test_review_candidate_gate.installable.py` as `tools/workflow_checks/validation/test_review_candidate_gate.py`. Its bootstrap imports the installed production modules; otherwise the seven tested fixture cases are unchanged. Configure the test TEMP/TMP to a writable directory. The runnable preparation version is code/test_review_candidate_gate.py. Existing-regression runner is code/run_existing_review_tests.py. No shared files or live-root test temporary files were written by this work.

Final negative data/control acceptance: code/verify_negative_acceptance.py (compiled, not executed). After negative publication, before ICES changes unrelated review rows, run with --publication-receipt <negative output timestamp>/registration_receipt.json --write-receipts. It checks fresh signed reports and approved_review against exact central rows and both payloads, exact reasons, sections/exclusions[], source-only pooled identity, verified=false/scopes={}, canonical/report hashes, current page Project fingerprints, preserved default selections, and red-style/validated-control source availability. It writes one receipt under EACH exact model's model_validation/work/2026-11-14_235500_publication_acceptance/outputs/. Omitting --write-receipts is read-only. It refuses an active central lock. Receipts explicitly state browser_UI_checked=false; data/control-source checks are not browser testing. The optional transaction receipt enables before/after preservation checks and should be used immediately following this batch, before another authorized review batch changes other rows.

## Transient Windows replacement retry

outputs/atomic_replace_retry.patch is the isolated atomic_bytes fix. It was installed by the coordinator, not this agent. The five focused tests passed after reproducing three pre-fix failures/errors: Windows access/sharing errors5/32/33 retry up to6attempts with0.2/0.4/0.8/1.6/3.2seconds waits; exhaustion preserves target and deletes temp; changed target stops retries without overwriting; transaction rollback restores a previously written first page; other PermissionErrors do not retry. Each attempt retains publication_write. Success followed by a guard failure is never retried.

Install outputs/test_atomic_replace_retry.installable.py as tools/workflow_checks/maps/test_atomic_replace_retry.py. Focused5 passed in0.674seconds. Combined exact-pair candidate gate plus existing publication regression tests15 passed in37.749seconds. qa/atomic_retry_verification.json records hashes/results. Original exact-pair build_html.patch and the atomic helper patch affect disjoint functions. outputs/build_html.combined.patch is a reference composition tested locally; do not overwrite subsequent shared changes from the full proposed source file. No additional tests are running.
