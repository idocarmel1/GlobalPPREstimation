# Ultra successor: finish ICES, then graph and Git

Checkpoint: 14 November 2026, approximately 21:30 Asia/Jerusalem. This is an execution handoff, not scientific evidence or new researcher approval.

## Ownership and current user instructions

This successor becomes the sole shared-resource coordinator. Predecessor chat is `01a1db4c-e3e4-7612-86d5-79904e81be94`. All three internal subagents have completed and stopped. No publication, scientific run, rendering helper or writer lock remains active. Do not contact other user-owned model chats: the user expressly chose no cross-chat messages. Internal bounded subagents remain authorized, but minimize credits and reuse completed audits.

The user explicitly said: “make this run as short as you can as long as produces reliable results.” They then instructed that if repeated mistakes appear, stop and continue in a new chat with **Ultra** thinking effort. This transition follows a second ICES driver orchestration error (details below); it does not imply a scientific package failure. The new chat should use Ultra and avoid importing the entire previous chats.

New authorized scope, in order: finish all remaining current updates (only ICES LME022 publication remains), then update the canonical knowledge graph, then **commit and push all changes**. User explicitly clarified graph/Git must happen **after all current updates are finished**. Neither graph refresh nor Git mutations have begun. A read-only status check found branch `main`, remote `origin https://github.com/idocarmel1/GlobalPPREstimation.git`, and many existing tracked/untracked project changes. Preserve them; no worktree or new branch was requested. Inspect final Git/LFS state before staging, and respect existing LFS policy.

Read current README.md and explainers/agents/project_contract.md before edits. Preserve signed reports, researcher edits, canonical inputs, selections, missingness, warnings and actual executed provenance. No new scientific solves or Monte Carlo draws. The project graph is only `tools/knowledge_graph/graph.json`; its existing scope controls coverage. Do not create graphify-out or a second graph location.

## Live checkpoint (verified after failed ICES isolated preflight)

Current Project matches the completed disqualification transaction exactly:

| File | SHA256 |
|---|---|
| Project.xlsx | fda4722cdaa4ce0890da37caf4c7a0170cae576a4c84192851ba8802a49febfa |
| interactive_map/index.html | 627ca97476dca12641bdfc376edae1b968f54a148f90b67994018d4e0c7f5e28 |
| interactive_map/trends.html | f5dbccb2682118f48288e6b2e49b3f6fcd14f9b8d4d28e31e703e0cd6edc2d76 |
| interactive_map/sources.html | 55cf203b8d466d52560ddf8febc852ba9d3991be45be84f463533c37c45460f4 |
| tools/project_core/maps/build_html.py | e266898cc73a74948ed6f82f3c7e216e1b48263c3879045ef7119f2ca5db390b |
| tools/project_core/maps/original_atlas_data.py | ee1786f811ad15112a64d98007d7329aa622e74ebac6a788b88551ae2a41c8c8 |
| tools/project_core/registry/review_candidates.py | 47ccd7bd7790431e7f6a86b8695ec1b8e9c015346917eaa8248f8d04fcd990ae |

Map/trends fingerprints match current Project. Sources.html was last rebuilt with the three-model batch, before the metadata-only disqualifications; the final ICES scoped `_build` should refresh it normally. Do not run a separate full build to compensate.

## Completed work — DO NOT REPEAT

Original batch HS071/EEZ598/EEZ941/LME038/LME049 and LME050 disqualification, removal of mandatory global scientific inventory, associated rules/tests and original browser checks were already completed in the first coordinator chat.

This predecessor completed:

1. **LME003, LME014, LME037 retained publication**. All 19 promotions, exact signed reviews/exclusions, coefficient/missingness matrices, floor settings, default selections, protected inputs and prior six decisions passed final verification. LME003 has 31 exclusions, LME014 none, LME037 Seabirds [1]. LME037 workbook/snapshot bytes stayed exact and actual floor remains 1.0/threshold .1.
2. **LME024 and BOTH LME026 disqualifications**. Exact sources/reasons registered and published, including exact known-source metadata insertion for previously absent pooled026 candidate. Original026 remains selected. Pooled candidate is review-only, verified false, scopes empty, source-only review with no borrowed calculation identity. All three fresh report→Project→both-page checks passed and receipts saved. Call this the **disqualification batch** to the user; they asked why it was called “negative.”
3. **ICES retained package v2 prepared and independently reviewed**. It is ready but NOT adopted or published. No shared/numerical ICES mutation occurred.

Abbreviations:

`RUN2 = regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native/model_validation/work/2026-11-14_193033_coordinator_batch_2`

`NEG = regions/LME/LME_026/papers/MED-2022/models/Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114/model_validation/work/2026-11-14_230000_bounded_registration`

Important completed evidence:

- RUN2 `qa/combined_preflight.json` passed, no live changes.
- RUN2 `qa/combined_publication.json` passed, final three-model Project hash `bb7272d0b0cac1eb72987fc9abc0a4666f2cd82dac65fed01a383d207431feb2` (now superseded by disqualification Project, legitimately).
- RUN2 `qa/published_controls.json`: 127 available cases; all nine prior/current models, exclusion defaults/manual overrides, exact validated-only filtering and generated JS syntax passed.
- Three model-local `model_validation/evidence/source_review/coordinator_publication_20261114.json` receipts saved by RUN2 `code/finalize_evidence.py`.
- NEG `outputs/20261114_212130/registration_receipt.json` and adjacent pre-registration Project snapshot retain exact disqualification transaction.
- Each of LME024, original026 and pooled026 has `model_validation/work/2026-11-14_235500_publication_acceptance/outputs/coordinator_acceptance_2026-11-14_192651.json`. These passed fresh source/page/default/preservation checks; browser UI was not checked.
- NEG `code/verify_negative_acceptance.py` is the completed acceptance implementation. Do not rerun unless changed input or integration regression requires it; ICES final checks preserve these decisions.

## One genuine publication failure already resolved

The first RUN2 publication reached final `os.replace(tmp, trends.html)` and failed with Windows WinError5. Rollback was proven by 23 checks: Project, both pages, all19 original promotion targets and lock removal. Evidence: RUN2 `qa/combined_publication_attempt1.json`, `qa/rollback_attempt1.json`. A current DELETE-access probe succeeded. A byte-identical live trends replacement probe then passed (`qa/atomic_replacement_probe.json`).

Installed a narrow `atomic_bytes` retry in build_html: only Windows PermissionError5/32/33, maximum6 attempts, total6.2seconds sleep; target original fingerprint checked each attempt, publication journal guard each attempt, never retry post-success guard failure, abort on author mutation, clean temp. Five focused tests and15 related publication/combined gate regressions passed. Retried RUN2 successfully; its final page write and all final checks passed. Do not redo this transaction.

Other installed shared changes:

- `calculation_provenance` reads explicit flat flags ONLY when constructor key is absent. Nested precedence, OFF, unknown and malformed enable handling preserved.12 focused floor tests passed; independent review passed. No workbook changes for the display fix.
- `review_candidates.py` exact known-source/unselected metadata insertion changes only Models worksheet/native table extent, rejects guessed readiness/scientific fields, verifies canonical/path/paper identity. `_refresh_reviews` now supports exact `model_pairs` and `candidate_rows`, replaying insertion BEFORE signed reviews against true prior Project, preserving full ZIP equality and true page baseline. New candidates require source-only disqualification.
- Installed `test_atomic_replace_retry.py` and `test_review_candidate_gate.py`. Together12 installed tests passed after installation; 21 original candidate/boundary/insertion tests plus related rollback regressions had passed during preparation. Reuse evidence.

## Remaining ICES package and authorization

Model directory `regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991` (abbrev MODEL).

User-authorized signed MODEL VALIDATED, Ido Carmel,2026-11-14, exclusions [1,2,3,4,65] = BaleenWhales, ToothedWhales, Seals, SurfaceFeedingSeabirds, DivingSeabirds. Original authenticated human message `01a1db3d-bf6c-7601-acc0-f0a36871b95d`, source chat `01a1dabb-4107-7d32-bc28-80f6a22b66a5`. The older detailed handoff in RUN2 `outputs/coordinator_handoff_20261114.md` contains original authorizations if needed; avoid rereading it wholesale.

- Canonical SHA `450e0f43822a34a02d4d26ad71358aeef32af8daaff7fcf07cd95ef2131cf97a`.
- Signed DOCX SHA `aa5516a7d20ddd25ac803b026ea96627a8fd51897b02c675d6aedbb2f1643b90`.
- Package run `MODEL/model_validation/work/2026-11-14_230000_retained_adoption` (STAGE).
- Read STAGE `outputs/coordinator_handoff.json` first; SHA `0b5c4159b6a0557b1db51d24118ed3a88d1152d6847de85e8464f10fd826480e`.
- ONLY use STAGE `outputs/retained_package_v2`.
- Wrapper `code/adopt_retained.py`, SHA `fb7e602603bb4ea892d0e029a8ac8731259192add5ca774e1113ab527bfe0882`.
- Preparation SHA `b185578c27f803c9600bff4d919e99edcd1772c4395e0b61e6ab1728c3e9fdcc`.
- APIs `verify_package(package_path=None, *, check_consumed=True)` / `apply(publication, package_path=None)`. After install use check_consumed=False for original-target guards.
- Eight promotions,114 guarded inputs.70groups,630coefficients,384taxa,715 assignments including88zero weights.
- Regional/snapshot SHA `1e16996d8ee0ca84e2a0fc8f0d958a44e6e6d10ef828f4af433f6dfcd0b04f15`; source `70441684c67705f41ddc28b1ccbdb51b370e00b8b22a7e4769ecebdcefc2796b`; manifest `ab835d525f02b9a2cfdc8e80b4e01b88da9e1bc38cdf6626ba2a26a14f15f7fd`.
- QA already passed5670annual cells exact,37800ratio cells/missingness,1890historical exclusion cases. Independent Catch/Classic/NPP sheet XML exact. Maximum display-vs-regional difference1.0290646553wet tonnes is within verified six-decimal taxon-coefficient rounding bound. Do not re-audit all arithmetic.
- Actual executed engines pinned from Git38cb75d. Model-local historical input engine copies were NOT executed; do not use them. Preserve STAGE inputs/executed_engine and inputs/pre_adoption (manifest references them).
- Retained annual scope statuses are `ok`, detailed diagnoses all WARN, and production_eligible=False remains separately truthful. Do not invent provisional restrictions or reinterpret signature as new scientific approval.
- Keep historical Cetorhinus maximus→BaleenWhales weight1/Very low mapping. Catch positive62years1950–2012,total50893.6574923636t; zero2019 is not no trend impact. Exclusions only control displayed PPR; all groups/weights remain.
- v1 scratch remains: automatic approval review rejected its deletion as irreversible project-artifact deletion outside perceived authorization. Agent did not bypass/retry. v1 is explicitly rejected, invalid against wrapper guard, and must not be used. Disclose any remaining cleanup limit; do not blindly remove it.

## Immediate next action: fix isolated ICES preflight dependency copying

Coordinator driver run `MODEL/model_validation/work/2026-11-14_235000_coordinator_publication` (ICESRUN).

`code/publish_ices.py` has explicit `--preflight` (default) and `--publish`. No publish has occurred. It pins the v2 package in `inputs/package_pin.json`, serializes central writes, has a scientific-inventory tripwire, journals all8targets, applies package BEFORE registration because live usable Groups/mapping tables are empty, registers exclusions, exact replay gate, one `_update` only022, one `_build` only_units={LME_022}, and final source/review/numeric/default checks. Mutable Project is intentionally authenticated at execution, not frozen to an earlier batch.

First driver review caught overbroad `_preserved_inputs` comparison including authorized Groups/Matching additions. This is already fixed: `independent_inputs()` digests whole Catch/Classic PPR/NPP; selection/rationale preserved separately; exact installed/staged package bytes bind all adopted tables. Focused read-only preservation test passed, independent review confirmed fix. Actual populated live Groups/Matching/Allocation assumptions/Mapping review are all0 rows; XML scanner earlier counted blank styled rows, which was corrected in QA. Staged counts70/715/715/384. Do NOT restore the faulty comparison.

At19:27UTC the isolated preflight authenticated package and baseline successfully, then failed in `_register_review`→`read_report`:

`ValueError: Review hyperlink is missing or outside the repository: ../../../../../raw/catch/LME_022-catch.zip`

`isolated_preflight()` copies Project, pages, staged promotions, canonical JSON/report/notes/mapping appendix, but omits other local targets linked by signed DOCX. `researcher_review.py` lines149–154 resolves each non-URL link against report.parent, requires inside fixture root and exists. This is a fixture construction omission, NOT absent live source evidence or a scientific gap. Audit and copy the actual needed local link targets into the isolated root with exact relative paths/bytes, including fragment/URL decoding handling, instead of one-by-one missing-file fixes. Do not edit signed DOCX or weaken hyperlink/review gates. Existing live `read_report` passed repeatedly. Use its verified section links or inspect DOCX relationships to enumerate fixture dependencies. Then run isolated preflight again. Its TemporaryDirectory cleaned up, writer lock removed; live Project still exactly fda4722... after failure.

Progress is in ICESRUN `qa/progress.json`; static/preservation evidence nearby. No `qa/preflight.json` success exists yet. Keep only current relevant fixture evidence. Once preflight passes, run `--publish`, monitor timestamped stage logs, and verify rollback on any failure. No full-build fallback or fresh science.

After successful ICES publication run prepared Node checker `ICESRUN/code/check_published_controls.js` (inputs/display_exclusions.json + negative_reviews.json). It preserves original9checks, adds ICES5default exclusions/manual overrides, exact validated-only trend filtering, and all3new disqualifications including pooled review-only restrictions. Syntax check passed; not executed on unpublished data. Save final ICES receipt linked to publication/controls evidence with actual browser limitation. Ensure source-index signed-report provenance promotion is present (one of8promotions).

## Browser limitation

Actual browser verification could not be completed in predecessor. CUA getState timed out300seconds; Windows fallback initialized but `get_window_state` stopped Computer Use because it could not reliably determine current browser URL for policy enforcement. No further UI calls were made. RUN2 `qa/ui_verification.json` and receipts explicitly say browser acceptance false/blocked; embedded Node control checks passed. Do not claim visible browser checks occurred. A new chat may assess available supported browser tooling normally, but must respect any stop/policy restriction and not bypass it. Existing local read-only servers8877/8881 must not be stopped. Last known local map URL http://127.0.0.1:8877/interactive_map/trends.html; Chrome was displaying an unrelated Google Slides tab during fallback. Preserve user tabs/preferences. Do not waste repeated5-minute initialization timeouts.

## Runtime and finish order

- Python `C:/Users/idoca/miniconda3/python.exe` (Python3.13 runtime despite initial old descriptions).
- Node `C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe`.
- Use own writable TEMP/TMP; predecessor used `C:/Users/idoca/.codex/visualizations/2026/11/14/01a1db4c-e3e4-7612-86d5-79904e81be94/test-temp`. Successor may need its own visualization root.
- Current code/work uses Windows CRLF; `git -c core.whitespace=cr-at-eol diff --check` avoids false whole-file warnings.
- Complete ICES/preflight/publication/final controls/receipts first. Then refresh existing knowledge graph using installed skill/current scope, verify it, then commit/push all authorized project changes. No graph/Git mutation yet.
- Real timings: successful RUN2 retry took about20minutes including ~9minute consolidation and~2.3minute page build; prior failed transaction23minutes. Disqualification batch~5minutes. ICES likely~15–25minutes after fixture fix, then graph/Git~15–30minutes provisionally (upload size unmeasured). Last user-facing estimate before this fixture failure was22:05–22:40Israel; update from actual progress rather than promise it.
- No outgoing messages to other user-owned chats. This predecessor will cease all writes once successor is created.
