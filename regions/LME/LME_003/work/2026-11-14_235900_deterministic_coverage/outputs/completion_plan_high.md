# Cached PPR completion and publication implementation plan

> For agentic workers: execute this plan natively in the new chat at high thinking effort, using superpowers:executing-plans where helpful. The user has already instructed execution; do not ask for another plan approval. Use one narrowly scoped reviewer for the checkpoint/atomic-write change, not a new audit team. No intermediate commits: the final commit is the final tool action.

**Goal:** Finish the already authorized 16-ecosystem deterministic-result adoption, Humboldt review amendment, requested map/trend defaults, final verification, cleanup and local commit without repeating verified science or losing completed workbook work on a late failure.

**Architecture:** Preserve the current coordinator and whole-publication rollback. Add a small cache of complete, already verified model packages, captured after all model batches and provenance stamping. A failed later step may roll back canonical files but must retain sealed packages for fast guarded restoration. Central publication remains serialized and uses saved data only.

**Tech stack:** Existing Python 3.11/openpyxl pipeline; Node verification/Playwright; Windows filesystem; Git. No new service or framework.

**Spec:** continuation_high_handoff.json and the user's instruction to continue in a new high-effort chat, reuse cached results, prevent late integration failures and handle failures without restarting the whole workload. Earlier continuation_handoff.json supplies original scientific requirements; its pending-work status is superseded by this plan and the latest handoff.

## Constraints

- Read README.md and explainers/agents/project_contract.md in the new context. Work in the existing checkout; no new worktree or branch was requested.
- Preserve canonical scientific inputs, selections, researcher edits, exact exclusions, missingness, finite-result restrictions and existing MC evidence. No scientific solver or Monte Carlo rerun is needed.
- All 148 new deterministic outcomes are cached and authenticated. Reuse the current immutable audits and tests when their consumed bytes match. Do not rerun the previous full private-copy or 24 source-batch suites merely to rebuild confidence.
- Only one writer for Project.xlsx, canonical model outputs, source_paths.csv and published pages. Delegate only independent read-only review/final QA.
- Preserve the original guarded adoption and review transaction. Do not bypass bounded review refresh with a full build to hide a failed guard.
- stamp_actual_execution() is NOT idempotent. A cached package already contains the stamped manifest; never stamp it again or relabel historical execution with current software.
- No guarantee of zero errors is possible. Every failure must either be detected before expensive writes or leave reusable, independently verifiable completed packages.
- Preserve CRLF/scientific bytes. Windows path containment and reparse checks apply to every copy/delete. Do not recurse through node_modules junctions.
- One final commit of all authorized changes, after all checks and cleanup. No push. Commit must be the final tool action in the new chat.

## Review focus and required tests

1. A destination changes after preflight: reject replacement and preserve the concurrent human edit.
2. Windows denies an atomic replacement: bounded retry only for a diagnosed transient condition, rechecking original target SHA before every retry; persistent failure stops that write.
3. Exception or termination between replacement and checkpoint: durable intended before/after hashes and tested ownership reconciliation must support correct rollback without claiming arbitrary external bytes.
4. A checkpoint is incomplete, corrupt, wrong-model or stale: reject only that package; leave all other valid checkpoints reusable.
5. Restoring a completed package: exact manifest/evidence bytes survive, provenance is not stamped twice, no solver/batch executor is invoked, and full retained-data assertions still pass.

## Task 1: Establish a clean, known baseline and diagnose WinError 5

Files: existing qa/adoption_application_attempt6.log; outputs/background_adoption_status.json; outputs/final_cohort_audit.json; tmp/adoption_recovery_attempt3/manifest.json; outputs/rollback_verification_after_attempt5.json. New evidence belongs in qa/ and outputs/ under this same WORK folder.

- [ ] Confirm old supervisor 18564/child20656 and peer writers are absent using actual OS process evidence, not sandbox invisibility. Archive the attempt6 status before reusing the current status filename.
- [ ] Compare the union of the 980 audit hashes and 1052 durable manifest entries (1152 unique paths) to the current filesystem. Attempt6 rollback has NOT been verified. Do not claim the workspace is restored until this passes.
- [ ] If any complete post-adoption package survived, authenticate it against the original baseline and full assertions before considering salvage. Otherwise restore only verified task-owned partial outputs from matching durable backup objects. Never overwrite an unexplained changed input or human edit.
- [ ] Diagnose access denied for California results/regional_snapshot.xlsx: open handles, attributes/ACL, own unclosed readers and filesystem constraints. Do not guess the cause. Do not close user applications or kill unrelated processes.
- [ ] Exercise atomic write/replace on an owned throwaway sibling under the same destination directory, without replacing scientific files. Remove that fixture with a ledger disposition. Resolve permission/handle ownership first.
- [ ] If a code fix is needed, modify only the actual writer/reader responsible. For retry behavior, write a small failing fault-injection test: first transient denial then success; persistent denial; changed target between retries. No unbounded retry, permission broadening, or guard removal.

Gate: verified baseline, reproducible/understood write behavior, and focused regression evidence. Do not start another long cohort attempt before this gate.

## Task 2: Add sealed complete-model checkpoints

Create WORK/code/completion_checkpoints.py and a focused unittest module under WORK/code/ or tools/workflow_checks/calculations/. Modify WORK/code/adopt_completion.py only at its model-loop boundary. Modify tools/project_core/calculations/coverage.py or registry/publication.py only if Task1 or a proven ownership gap requires it. Preserve the current source versions in WORK/inputs before modification and record new hashes.

Interfaces (keep the helper independent of scientific computation):
- capture_model_checkpoint(root, plan, cache_root, bindings, batch_reports, written_paths) -> checkpoint_manifest_path
- load_model_checkpoint(root, plan, cache_root, bindings) -> verified checkpoint or None
- restore_model_checkpoint(root, plan, checkpoint, publication) -> original batch-report records plus explicit cache-restoration metadata

Use WORK/outputs/completion_checkpoints/<unit>/<model>/<binding-id>/ for sealed packages. This folder is outside BOTH PublicationBackup.generated_directories and the durable rollback allowlist. Confirm that property before the first capture. It is temporary recovery/output cache, not a new canonical results location.

- [ ] Cache key/bindings cover exact unit/model identity; original source/regional/snapshot/manifest SHA or absence; selection/review/mapping/independent input identities; cached scientific outcome and evidence hashes; and compatible producer implementation identities. Record producer code honestly. An unrelated software change alone must not cause scientific recomputation; any reuse across changed producer code requires explicit narrow compatibility evidence, not a forged new hash.
- [ ] Capture only after every batch for that model, actual-execution stamping, immutable checks and unchanged assert_retained(plan). Include final regional/source/snapshot/manifest bytes and EVERY newly referenced evidence file. Bind existing immutable referenced evidence separately. Collect exact touched files from guarded reports plus manifest references; never copy a whole model tree blindly.
- [ ] Write content objects first and validate them. Publish a COMPLETE manifest atomically LAST. An incomplete directory has no reusable state. Include final produced hashes and original destination preconditions/absence for an exact destination allowlist.
- [ ] Restore inside the existing publication transaction only after rechecking bindings, all package bytes and destination preconditions. Journal intended before/after hashes BEFORE replacement. Use a tested guarded wrapper that reconciles exact post-write ownership even if an exception occurs between replace and checkpoint; never claim an arbitrary observed hash. Do not overwrite concurrent changes.
- [ ] Restore the already stamped manifest unchanged; authenticate all referenced evidence, run immutable checks and full assert_retained(plan), and append truthful cache-restoration metadata to the current report. Never call stamp_actual_execution or _complete_model for a restored checkpoint.
- [ ] Test complete reuse with a callback that fails if scientific/batch execution is invoked; wrong identity/input/SHA/absent-path mismatch; incomplete manifest; corrupt blob; failure during copy and immediately after replacement; preserved concurrent edit; exact no-double-stamping; checkpoint survival through whole-cohort rollback.
- [ ] Review the narrow diff once. Freeze the writer/coordinator/checkpoint code before the expensive run. Reuse unchanged 35-test and full-copy evidence; run only tests affected by these new edits.

Gate: a later model/publication failure can roll back canonical outputs while earlier sealed model packages remain reusable. The next attempt cannot silently rebuild a valid package.

## Task 3: Finish model adoption with reuse

- [ ] Refresh preflight once and keep its hash-bound parsed protection records in the same process. Reuse authenticated science caches through CachedBatch only.
- [ ] For each model, restore a valid checkpoint or execute only its missing uncheckpointed workbook batches. Seal each newly complete model immediately. The five models with no missing methods require no rebuild.
- [ ] Use the durable hidden supervisor pattern with unique attempt logs and explicit current code pins. Do not blindly rerun old run_adoption_background.py: it is pinned to the pre-checkpoint adopter and must be updated/reviewed before use.
- [ ] On model failure, stop dependent work, preserve successful checkpoints, verify canonical rollback, diagnose only the failing component and resume from valid packages. Revalidate rather than rerun unaffected science or tests.
- [ ] Emit progress at completed-model/phase boundaries. Do not flood the chat with unchanged polling updates or spawn agents just to poll the same process.

## Task 4: Publish saved data and the approved Humboldt amendment

Keep the existing apply() tail: update(..., coverage_units=set()), build(), central metadata assertions, all immutable/retained checks, then publish_review() using the approved staged handoff. Keep one outer lock/transaction. A publication/review failure rolls back canonical publication, retains model checkpoints, and retries only the corrected phase after guarded restoration. Do not rerun numerical work.

- [ ] Publish only after all exact model packages pass; then promote the staged Humboldt DOCX through the existing helper. Do not edit/re-render its unchanged accepted bytes.
- [ ] Preserve validated status, signer/date and four exclusions; pooled GE WARN, raw aggregate/unpooled FAIL and TE WARN remain distinct.
- [ ] Require outputs/adoption_publication.json, matching final Project.xlsx hash, exact review amendment and all existing preservation checks. A stopped process or exit0 alone is not completion evidence.

## Task 5: Final verification, cleanup and commit

Run these independent final checks concurrently where safe, with no canonical writers:
- Node WORK/code/verify_table.cjs (already binds Project/trends hashes): exact16, fixed-1995 all16, landings+catch annual coverage, retained GE/TE comparison.
- Python -m tools.workflow_checks.maps.verify_html --workbook Project.xlsx --html interactive_map/index.html.
- tools/workflow_checks/maps/check_trend_defaults.js on the ACTUAL trends.html (input is JSON string containing HTML).
- WORK/code/verify_final_publication.py --published: approved DOCX/review/MC/inputs and exact16/57-exclusion checks.
- WORK/code/verify_browser.cjs --publication-ready using bundled Node, Playwright and isolated headless Chrome, TEMP/TMP=WORK/tmp. Inspect actual screenshots and errors.

- [ ] If a verifier fails, determine whether production or the verifier is wrong; fix the specific cause and rerun affected checks. Do not waive a scientific or review restriction.
- [ ] After all checks pass, use the prepared cleanup_after_acceptance.cjs --prepare/--apply for the existing exact allowlist. Review the prepared plan first. It retains an exact recovery manifest copy before retiring backup objects. Extend separate bounded cleanup ONLY for the new checkpoint cache, owned write-test fixtures and task-owned temp files. Keep immutable source/cached scientific evidence and historical signed review.
- [ ] Record every removal in source_paths.csv. Recheck current accepted file hashes after cleanup. Preserve compact reports rather than duplicate huge workbooks.
- [ ] Write a compact final completion report binding actual final hashes, checks, limitations, cache reuse counts and old/current comparisons. No extra human document needed.
- [ ] Freeze all writers, inspect/stage ALL authorized changes, verify git-lfs/hook/config and staged diff (CRLF-aware whitespace check). No temporary backups, node_modules, locks or partial cache directories staged.
- [ ] Make git commit the FINAL tool action. No push and no tool calls after successful commit. Final answer includes commit hash, all16 outcome, publication/review status, verification and material Humboldt change.

## Error policy

| Error | Response | Reuse |
|---|---|---|
| Input SHA changed / researcher edit | Fail closed; preserve external change; assess affected model | Unaffected model caches remain |
| Bad/incomplete checkpoint | Reject that package; keep evidence; rebuild only affected workbook package | Scientific outputs remain cached |
| Transient atomic-replace denial | Small bounded retry with target SHA rechecked each time | Same staged bytes |
| Persistent access denial | Stop that write; identify handle/ACL cause; no automatic permission expansion | Completed packages survive |
| Shape/schema/provenance error | Reproduce on small fixture, targeted fix/tests, then affected real package | All compatible prior evidence |
| Retained-data mismatch | Do not relax assertion; isolate exact changed fields; rollback canonical writes | Unaffected sealed packages |
| Build/review/browser failure | Repair the failed publication/test layer, preserve signed-review boundaries | All completed model packages |
| Process interrupted | Check real PID/liveness, inspect durable journal/status, reconcile before/after hashes | Sealed complete packages only |

## Time discipline

The earlier full canonical run spent about49 minutes before a late-model failure; another spent25 minutes before the access-denied error. Do not promise a short deadline without evidence. Spend the initial phase diagnosing the blocker and adding the small checkpoint layer, then report an estimate based on measured uncached work. If one diagnostic approach makes no progress after roughly10–15 minutes, change approach and explain the concrete blocker rather than repeating it. No broad refactor, new graph, new science audit, duplicated document render or repeated whole-cohort trial. One successful run remains necessary for packages whose final workbook bytes were rolled back/deleted; repeated full rebuilds after later errors are not acceptable.
