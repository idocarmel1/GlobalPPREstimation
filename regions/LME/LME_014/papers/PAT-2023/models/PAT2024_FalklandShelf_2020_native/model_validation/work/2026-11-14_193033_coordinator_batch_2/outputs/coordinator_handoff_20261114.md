# Shared publication coordinator handoff

Checkpoint: 14 November 2026, approximately 20:20 Asia/Jerusalem. This file is an execution handoff, not scientific evidence or a new approval. Read the final checkpoint section at the end for updates made before the successor chat started.

## User request and ownership

The user explicitly requested a detailed handoff file and a new chat to finish all remaining tasks because the old context is too large. They request subagents where useful and minimal credit use. Start from this handoff, not the old chat's entire history. Reuse authenticated prepared artifacts and completed tests; investigate only changed inputs or identified gaps. Do not redo the completed first batch.

Old coordinator chat: `01a1daa4-cbff-7830-8cb0-b8342b49ec5d`. The successor becomes the sole shared-resource coordinator: Project.xlsx, generated pages, shared implementation and instructions. Other model chats have been holding central writes. Do not open a concurrent write window. No publication transaction or central lock is active at this checkpoint. Old-chat subagents are being brought to a clean stop before transfer.

The user previously explicitly answered **Continue this work without cross-chat messages**. Do not send coordination messages to other user-owned chats. Incoming authorized handoffs and read-only inspection are allowed. Internal bounded subagents are allowed and requested. This new-chat creation is explicitly authorized. No commit, push, merge, new worktree or fresh scientific run is requested.

Workspace: `C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation`.

Read `README.md` and `explainers/agents/project_contract.md` in the new context before edits. Use the current project validation/pipeline skills for the exact operation. Preserve scientific inputs, researcher edits, signed report bytes, missingness, warnings and selections. Use canonical discovery and model-local work/output locations. An inaccessible PID in the sandbox does not prove a writer lock is stale.

## Current state that must be preserved

- Current `Project.xlsx` SHA256: `c9fb86a34119987348e7a4e89536cd154209ee8d7fc8769a8e1791c3db48ef9c`.
- Both published pages still embed the completed first-batch Project SHA: `9a3951c5e4342c3b8cc0ab2c0feccff9962aac3f91daf600e7a18a38e4c2e06b`.
- The difference is intentional: LME_003's signed decision and 31 display exclusions were subsequently registered, but its numerical package and the second batch have NOT been applied/published.
- LME_014 and LME_037 decisions are not yet centrally registered. Their packages are prepared, not installed.
- LME_024 disqualification, both LME_026 disqualifications and LME_022 ICES adoption/review are authorized but not centrally registered/published.
- Many unrelated dirty files exist. Preserve them; do not reset the tree or broadly normalize files.

This handoff's run directory, abbreviated **RUN2** below:

`regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native/model_validation/work/2026-11-14_193033_coordinator_batch_2`

Important RUN2 files:

- `inputs/authorized_scope.json`: authenticated user authorization for exact 003/014/037 batch, source hashes/configurations/exclusions.
- `inputs/display_exclusions.json`: expected exclusions for the original six plus these three.
- `inputs/Project_before_batch_2_registration.xlsx`: exact pre-003 Project, SHA `9a3951...e06b` above. Essential bounded replay baseline; retain it.
- `qa/LME_003_registration.json`: successful metadata-only registration receipt.
- `qa/LME_003_exclusion_audit.json`: independent root audit of all 94 groups and the 31 exclusions.
- `code/register_lme003.py`: already executed successfully; DO NOT register again unnecessarily.
- `code/combined_publication.py`: prepared next-batch driver, NOT EXECUTED.
- `qa/driver_handoff.json`: syntax/static review and known prerequisite; SHA `f2259d1536e7f80d1d8c0248424c6c4072ca4bf96a53f7de96eedc6923368e6d`.
- `code/check_published_controls.js`: ready for after publication, copied/adapted from the tested first-batch checker. Reads RUN2 exclusions JSON and writes RUN2 `qa/published_controls.json`.

## Completed first batch — do not repeat

The original requested publication and global-inventory work is COMPLETE:

- HS_071, EEZ_598, EEZ_941, LME_038, LME_049: authenticated retained packages adopted, reviews published to Project/map/trends.
- LME_050: signed disqualification registered and published; excluded by validated-only filters.
- Default selections and scientific inputs preserved. Original historical execution identities retained; no claims of equivalence to today's engine. No scientific solves or new MC draws.
- Both pages verified by embedded-data/JavaScript checks and real browser controls. Five positive models appear under the validated filter, LME_050 does not. LME_038 Marine mammals and LME_049 Toothed whales (all) unchecked by default, manual overrides work.
- Six model-local publication receipts saved. Twelve redundant scratch files (1,037,413 bytes) removed with evidence; recovery/provenance material retained.

First-batch run directory, **RUN1**:

`regions/EEZ/EEZ_598/papers/WCP-2007/models/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)/model_validation/work/2026-11-14_190000_coordinator`

Evidence: `qa/combined_publication.json`, `qa/published_controls.json`, `qa/ui_verification.json`, `qa/cleanup.json`. Reusable examples: `code/combined_publication.py`, `code/finalize_evidence.py`. The successful transaction took **3,784.549 seconds (~63 minutes)**. An earlier verification failure rolled back coherently; do not reuse obsolete failed QA as current state.

Shared implementation already changed: coverage filtered to explicit unit/model scope before discovery; empty/default scope performs no scientific work; saved-data rendering and bounded reviews do not launch scientific inventory; full inventory requires explicit audit/migration. Updates/selection/publication backups respect scope. Fifteen active instruction files updated. Seventy scoped checks plus fifteen guard/prose checks passed. No historical scientific record was rewritten.

## Immediate next step — publish ready 003/014/037 batch

### One known prerequisite remains

LME_037 stores its actual `effective_loader_flags` as a **flat** object, with explicit `use_ee_floor=true`, `ee_floor=1.0`, `ee_threshold=0.1`; no nested `constructor` key, standalone floor settings, or Diagnostics/EE floor table.

`tools/project_core/maps/original_atlas_data.py::calculation_provenance` currently reads only `flags['constructor']` and standalone/table settings. Thus it omits LME_037's authenticated floor display. The driver correctly detects this before adoption. Smallest fix: support explicitly recorded flat constructor flags when the nested constructor is absent, without inferring defaults or changing workbook bytes. Preserve nested-constructor precedence, OFF, absent/unknown and malformed-value handling. Add focused regression coverage in `tools/workflow_checks/maps/test_ee_floor_views.py`, run that relevant suite. Check package consumed-input pins before making the shared change; do not unpin provenance or rerun arithmetic merely because a display helper changed.

Current unchanged `original_atlas_data.py` SHA: `9513547d9ca5b9cec46805232a7aa197a4c7f3211b8b31418cf22243e570ffc0`.

### Driver and execution order

RUN2 driver SHA: `aec8e65baa17d0c6a593aa536c6e6746b58bf2ed7d4ff7f1c9657ec3319be868`. AST syntax and independent static review passed. No preflight or production run has occurred. The driver pins 3 wrappers, 3 plans and 19 total promotions; uses actual package semantics, not a fictitious full 22-method inventory requirement.

1. Resolve the LME_037 display issue above.
2. Run `code/combined_publication.py --preflight` with the scientific Python below. It holds the central lock but registers only on an isolated temporary Project copy, authenticates all packages, replays the exact bounded review gate, and checks candidate reviews/diagnoses/floor/missingness using staged books. No page build, adoption or science.
3. Inspect `qa/combined_preflight.json` and address any concrete mismatch before starting the expensive transaction. Do not weaken assertions to conceal missing data.
4. Run the same script with `--publish`. It journals each registration, uses one rollback-protected transaction, registers only LME_014 [] and LME_037 [1], then exact replay order **003 → 014 → 037** against the pre-003 9a baseline. It then adopts each verified package, performs **one** `_update` for these three, and **one** scoped `_build`.
5. Driver progress/failure stages go to `qa/combined_publication.json` with UTC/elapsed timings. A tripwire rejects `ensure_validated_coverage` calls. It verifies every installed promotion byte, source/review agreement, protected inputs, unchanged LME_037 workbook, and original six decisions/exclusions/defaults.
6. Run RUN2 Node controls checker, then actual browser checks for new three models. Confirm LME_003's 31 defaults and LME_037 Seabirds default, positive filters, source review and floor labels.
7. Save model-local publication receipts and cleanup only proven redundant work. Adapt RUN1 finalizer to RUN2 schema (`page_hashes` etc.), do not blindly run its hardcoded six-model cleanup.

If a technical failure occurs, verify rollback. Do not clear an active lock or bypass a failed bounded gate with an unscoped build. Rollback should restore current c9 Project (including successful 003 metadata registration), not the pre-003 9a baseline. Preserve both baseline roles.

The driver deliberately excludes later 022/024/026 requests. Keep this batch stable. Driver `Progress.excluded_pending_units` currently lists only 026; that's a historical bookkeeping limitation, not the complete remaining queue. No numerical assumptions may be inferred from this field.

## Frozen package facts

### LME_003 California Current

Model: `regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014`.

- Canonical SHA `18ed0ba93eb9c95ce305fc03fc36cc189b4cd365d9482fd8be30f398c2508925`.
- Signed DOCX SHA `64d7df9a743268bf9808c988144c8e5a7d0005b4297b8f017b2710e5b0062c3c`.
- Source chat `01a1dac2-d77f-7690-808f-d3e65e801235`; actual human message `01a1db16-0e8f-74b0-b45d-0ecf3e269f58` verified. GE < .01 display exclusions; preserve missingness and all trophic nodes.
- Excluded seq: 60–79 and 82–92 (31 groups). Exact names/order in RUN2 exclusions JSON and signed packet. Root independently recomputed against all 94 raw groups; missing/-9999/nonfinite values are not classified below threshold. Seq80 GE .021028116531165313;81 .015419438279132792; detritus93 missing; producer/import1/94 GE1.
- Metadata registration already done; receipt also at `model_validation/evidence/source_review/researcher_registration_20261114.json`.
- Package run: `model_validation/work/2026-11-14_193900_retained_adoption`.
- **USE `code/retained_package.py`**, NOT original `stage_lme003_adoption.py::apply` (original has a source-buffer race; reviewed wrapper fixes it).
- Wrapper SHA `50065e2390839f282070bf99248db9691234b4b01b3f141bdc6f3a70b823f597`.
- Plan `outputs/current_adoption_final/preparation.json` SHA `9e59e6a4a9977219d569adcdc6af5963ab735b05b6fe4e15ed10cacb00545840`.
- Wrapper API `verify_package(package_path=None, check_inputs=True)` / `apply(publication, package_path=None)`.
- 9 promotions, 69 consumed-input guards; sources package-relative, targets root-relative.
- Final regional/snapshot SHA `57d07971d8789543326c3bdc537bac3e7bb766eff079f9423e4ff9da1ab9e2ef`.
- Source SHA `0f84c08f0f1ed53df924a54aeb7712f45167e387489e352523ef5b677c8af011`; manifest SHA `c53f600b3bb9f13377008de807c80b891c6bed7cd3c18a00654a236d842bd72c`.
- 564 exact approved GE/TE coefficients; 226 GE and 233 TE cells changed exactly (not tolerance-based counts). 282 old With Egestion cells cleared; original bytes archived. GE/TE WARN; current With Egestion NOT_RUN/unavailable.
- 133,917 protected cells exact, mapping/Catch/NPP/Classic/manual cells preserved. Valid independent catch/coverage remains, not blanked indiscriminately.
- Final metadata step changed ONLY Diagnostics XML relative to numeric v2; every previous row and other ZIP member exact. Supported map helper shows ON .1 and all 94 actual effective EE values.
- Actual executed floor recorded in `effective_flags.runtime_initialization.floor_configuration`; original pre-floor constructor kwargs remain truthful. No invented floor kwargs.
- Five safety tests and independent code/ZIP review passed. Previous `sppr_source.xlsx` genuinely absent; preserve that absence honestly in archival evidence.

### LME_014 Falkland Shelf

Model: `regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native`.

- Canonical SHA `9880e521a406974367530ffb06f13392714dba57b9645c38a1b1448926d83d17`.
- Signed DOCX `2854655b494fc8d9220c86962da02f043d9f1180a86dc9bb77d310787af072be`; appendix `427570e31f01224fc162c8df667c4dde7b9eeb5be45d1fdf1ca2e7053cec7a8c`.
- Source chat `01a1da3d-f487-7a82-93aa-29befa678187`, human message `01a1daf9-eaf8-7732-86db-29a78ef1dbde` verified.
- Approved primary `source_exact_returns_to_36`, floor ON .1, threshold .1, detritus open none / collapse never. Fishery returns .005859524956463247 to Detritus36 exactly once; Discards35 remains separate. Physical merging is sensitivity ONLY.
- No display exclusions. GE/TE WARN retained; strict balances pass; source footprint GE35.611467012724624 / TE89.4135556062374.
- Package run `model_validation/work/2026-11-14_193100_retained_adoption`.
- `code/adopt_retained.py` SHA `a645be60166bf5d04194593f3631c9e3f866050ab5e7bb84d4859e2e4f87b740`.
- `outputs/retained_package_v2/preparation.json` SHA `8784349c0283464f2eee5d5997e024491c1342e31871e85d7cc050720dae1569`.
- APIs `verify_package(package_path=None, check_consumed=True)` / `apply(publication, package_path=None)`. After install use `check_consumed=False` for its original-target guards.
- 7 promotions,39 consumed guards. 222 exact approved coefficients; 111 historical WithE values archived and current outputs unavailable. 420 independently checked annual sums exact;37 effective groups,8 floor affected.
- Regional/snapshot SHA `b61e6984454d449f133198ee530c3f2e8543a4ab5b08ccfc27cff50676c21719`; source `c0bc897066e1ffb918b66d6938f1fcb0facc7372bfda700ac9e544dafc5f277f`; manifest `e3ff40b11744bf08ec243618e46aefce3b6162fb1347ca5c37508609dd6721e4`.
- Preserve `production_eligible=False`, mapping/geography/warnings. v1 was rejected for XML/blank-row preservation; use only v2. Keep `inputs/pre_adoption` and original-source provenance.

### LME_037 Visayan Sea

Model: `regions/LME/LME_037/papers/LME037-Bacalso-2026/models/Bacalso2026_Visayan_Sea_1997_baseline`.

- Canonical `a361c3dbf6abef5cedb0d0d480492e55907efde57b573278c5a7db2b7dbaf270`; DOCX `d28f170b249548a4520000affbe6fc68ff2e3ce1c97220f714c857eed88d6c2e`.
- Source chat `01a1da77-23d7-77e2-a5e0-50cbe868d501`, human message `01a1dae2-108d-7c72-aaae-2e8a8a0668de` verified.
- Already locally adopted numbers: 32 living production-BA closures,30 normalized feeding diets, Seabirds seq1 external M0 .000784, egestion to detritus. Actual retained floor **1.0**, eligibility threshold .1. Do not replace with .1 just because other models use it.
- GE/TE/WithE all OK;306 coefficients and9 method-scope annual statuses; all strict balances pass. Exclude Seabirds display only, seq[1].
- Regional AND snapshot SHA must stay exactly `f8b78a3ca0bc1303f3b3a41cf1944c704df1a635a7c709246ec3a83057c94965`.
- Metadata-only package: `model_validation/work/2026-11-14_220000_configuration_compatibility`.
- `code/retained_metadata.py` SHA `1d0f97bf329b4f6b268fd2d117ed755c262bc93848ce2731ee7d11900caac999`.
- `outputs/preparation.json` SHA `bd72bf0d56bce05d27dae293a4c4214ee294cceb3d4fbfb27844d1b657523d54`.
- APIs `verify_package()` / `apply(publication)`;3 promotions,95 consumed guards; both source/target plan paths ROOT-relative.
- Old manifest `c422ba7826f17b1785bc50d8f9b60b88da8f5608e30a6908a824b7794c7baf2b`; normalized manifest `189e13bcecfd24555dd6964d92dccca675e28ca7f39e6921448079c8ea4b0784`; ledger `d14a57459880f26f58d1a536dcd4c48fbcdfcdfd1699a04d6a6393c1133c229d`.
- All45 raw hashes and306 coefficients verified. Four safety tests passed. Normalized manifest retains original runtime marker, historical code identities and explicit stock_adapter_reconstructible=False. Canonical full-inventory cache validity intentionally FALSE because historical arithmetic context is absent; do not invent it or require22filler methods.

## Later authorized requests — not in RUN2 driver

### LME_024 negative review ready

Exact model: `regions/LME/LME_024/papers/LME024-Hernvann-2020/models/Hernvann_2020_Celtic_Sea_1985`.

- Source chat `01a1dac3-ce79-78d2-b97e-a861b79c4c94`; actual human message `01a1db43-0d93-73b3-8382-f3249e3f7166` independently read: disqualified in DOCX, updateProject, coordinator handles map/trends.
- Ready packet: `model_validation/work/2026-11-14_181408_disqualification/outputs/signed_review_packet.json`.
- DOCX SHA `cf2c5d6e37ae4747a7fea9ef098ab3f036081965bb4d574667779823dd7af782`; canonical `b4ba75b14c47a23b2b97aaacdc4b392f2183679e201942c35f36b910c92b63cf`.
- Ido Carmel,2026-11-14,MODEL DISQUALIFIED, exact reason **Reason – unrealistic detritus SPPR**. Exclusions[]. Existing exact row is registered; no new model row needed.
- Do bounded metadata-only registration/publication after RUN2, preserving the pre-registration Project for replay. No regional numerical adoption, new science, selection change or report edit. Source chat holds writes and will read the coordinator's receipt.
- Previously completed local import-completion diagnostics GE/TE FAIL are NOT an instruction to adopt them; source blanks remain canonical. Their separate report history is irrelevant to this exact signed rejection.

### LME_026 all canonical models disqualified

User's direct clarification in old root chat, message `01a1db40-1b39-7aa2-aaad-562fd6b1dc4e`: **all models for this region are disqualified for the reason I mentioned**. This answered a question explicitly about whether the existing Ido Carmel14/11/2026 signature/reason applied to pooled despite original-model report identity. The source gap is RESOLVED by that instruction; do not ask again.

Canonical discovery found exactly TWO models under `regions/LME/LME_026/papers/MED-2022/models`:

1. `Piroddi_2022_Mediterranean_1995`: canonical `f038707bf7837962933eec3e6daeae53eb0b9a7f48837763b0ce621edcdc3a9e`; current selected/results model; Project Models row40 unreviewed. Existing `model_validation/validation.docx` SHA `092dafe37aa0125198f63b61da8d41f88e30fe9a87d675f0109327f886fef0a5`, signedIdoCarmel14/11/2026, disqualified. Preserve these bytes.
2. `Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114`: canonical `281d8543a165bf67652168cbc47f09db224e51bddb6768e9365f8c52d03ac956`. No Project model row yet; a model-specific negative-review DOCX is being finalized (final checkpoint below).

Exact reason for BOTH, unchanged from signed Word:

> Reason - The pooled model is proposed for disqualification because unresolved production-budget inconsistencies in six groups cause all three SPPR methods to fail with EE floor ON at 0.1.

Retain that exact wording, even though it says proposed; the human's final verdict is MODEL DISQUALIFIED. Exclusions[] for both. Preserve default original selection, all source/results, the six-group primary evidence, and stopped hypothetical discards-div10 sensitivity. Do not resume/adopt that sensitivity or substitute its five residual failures as the signed reason.

Paper row189 exists: article_id `MED-2022__LME_026`, DOI `10.1038/s41598-022-18017-x`, publication2022, baseline1995. Add only an exact known-source pooled metadata row, selectedfalse, no fabricated coverage/readiness. `index_candidates` refuses missing scientific registrations and is NOT a suitable row-adder. `_register_review` also refuses an absent row, so solve the metadata insertion explicitly under the central lock with preservation proof.

Candidate binding work:

`.../Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114/model_validation/work/2026-11-14_201300_disqualification_binding`

Agent is making a short candidate-specific negative decision record using existing template styles and **exact copied Review/reproducibility cell XML**, not regenerating original scientific analysis. Candidate identity exact; external provenance paragraph records the user's all-model instruction; no transferred positive sections or appendix. Files include `outputs/authorization.json`, `outputs/proposed_central_metadata.json`, `outputs/validation.docx`, code and structural/render QA. Final canonical installation/hash stated at end. Original DOCX remains exact.

Existing `_refresh_reviews` accepts one model_id per unit mapping and replays only review changes, not a new metadata row. Publishing BOTH026 model decisions and the new candidate row needs carefully bounded sequencing or a narrowly tested extension; do not falsely pass the old baseline hash or bypass the gate with a full build. Prefer a small exact metadata/review path over rerunning science. Candidate must be selectable with verifiedfalse/empty scientific scopes if it lacks regional results; never copy original-model calculations into it. This is a real remaining implementation/sequencing task, not yet solved.

### LME_022 ICES adoption and review

Model: `regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991`.

- Source chat `01a1dabb-4107-7d32-bc28-80f6a22b66a5`, actual human message `01a1db3d-bf6c-7601-acc0-f0a36871b95d` independently read in root and subagent: signedMODEL VALIDATED, exclude BaleenWhales1,ToothedWhales2,Seals3,SurfaceFeedingSeabirds4,DivingSeabirds65; coordinator expressly authorized Project/map/trends.
- SignedDOCX SHA `aa5516a7d20ddd25ac803b026ea96627a8fd51897b02c675d6aedbb2f1643b90`; canonical `450e0f43822a34a02d4d26ad71358aeef32af8daaff7fcf07cd95ef2131cf97a`.
- IdoCarmel,14/11/2026. Exact signed SPPR text is a single `Near-zero TE:` list under `Groups removed from calculation:`. Preserve signed bytes.
- Canonical `model.json['group']` confirms all five exact names/IDs. Keep trophic nodes, original allocation weights and SPPR; exclusions affect displayed PPR under the existing contract.
- Current local selection alreadyICES; `results_model_id` null usesselectedfallback. Regional Groups,GroupSPPR,Matching,TaxonSPPR,Annual empty; no ICES regional_snapshot or result_manifest yet. Therefore **substantial retained-data integration remains**, not just metadata refresh.
- Authenticated primary package: `results/diagnostics/2026-11-14_loader_repair`, separate DOM67/sedimentPOM68/Discards69, floorON.1. GE/TE/WithE allWARN, finite nonnegative outputs; preserve restrictions and executed engine identity. No new scientific run or fullinventory.
- PooledICES at `results/diagnostics/2026-11-14_193500_pooled_detritus`, Scotland correctedOFF/ON are sensitivity/comparison only, not primary replacements.
- Mapping `model_validation/evidence/mapping/mapping_decisions.json` SHA `b0be4c37e3f5b1827f2c0e64f08f5cb84a5f963368f71f1fc63e20fe32fe3c81`:384taxa,715candidate assignments including88zero-weight candidates. Preserve reviewed weights/confidence and unresolvedness.
- Only excluded-group allocation is Cetorhinus maximus→BaleenWhales1 weight1,Very low documented filter-feeder analogue. Zero2019catch but positive62years1950–2012, total50,893.6574923636t, max1965 5,366.6666209834t. Do not remap or claim exclusions have no historical trend impact.
- Comparison handoff `model_validation/work/2026-11-14_200000_ices_full_review/qa/report_comparison_handoff.json`, SHA `e43d2e90dd89ffcb7976ebd6113dd46457bd3c7bb727c20e4c2bd0509abcbb28`.
- Model-local evidence_index still binds pre-signatureDOCX `8f14433a...`; update that provenance explicitly after accepting current signature, preserving other evidence.
- Need stage sourceGroups/coefficient source/actual flags and engine provenance, adopt reviewed mapping, calculate only dependent annual arithmetic, write honest manifest/snapshot, then exact signed registration and bounded publication. Empty current groups mean exclusions cannot currently register using the unmodified regional lookup; plan the bounded source/registration/adoption order explicitly rather than fabricating groups or bypassing gates.
- Subagent's read-only audit/checkpoint added at end. No ICES adoption code/package created in the old root turn.

## Shared fixes completed during the final status turn

`tools/project_core/validation/researcher_review.py` current SHA `169e6d95c5e714112e9392ae67b774e0fb77f6a6771e5c9981f9d532c78f971d`.

1. Earlier group-ID compatibility fix: `review_group_sequences` supports canonical group_seq or legacyseq, requires equal if both, integerlike1.0 accepted, missing/bool/nonfinite/nonintegral/conflicting/duplicateIDs or names fail closed. Empty exclusions skip sequence resolution. Registration and bounded replay use same helper.20 focused tests passed. Two guide references updated.
2. Newly fixed signature label case: `[Rr]eview date:` accepts existing template's `Review date:` without altering signed sources or exact verdict/model gates. Regression reproduced failure beforefix;12 boundary/disqualification tests passed.
3. Newly fixed exact single-line numbered `Near-zero GE/TE:` list under `Groups removed...`: splits only fully matched numbered entries, preserving legacy heading behavior and taxonomic parentheses. Regression reproduced beforefix;11 exclusion-heading/model-boundary tests passed. This makesICES default note name all5groups. It does NOT remove scientific groups.

Changed tests: `tools/workflow_checks/validation/test_researcher_review_model_boundary.py`, `test_researcher_review_exclusion_heading.py`. Run `git -c core.whitespace=cr-at-eol diff --check ...`; plain diffcheck falsely marks existing Windows CRLF as trailing whitespace. The CR-aware check passed. No need to rerun these unchanged checks.

Frozen shared scientific code (do not change while integrating retained outputs):

- PPRCalculator `5bd249eb73d61c1db77279a8a527465e4673944f377c40ca9e6100a2da0cc877`.
- ModelData `64c7769ed1494ccadf71dea333765989964ce8c4be9575143b6bc4cbbc6cc680`.
- method_coverage adapter `f855b88eebeb52d8814b0eb1dc8e9ed37e943fe62ed77d5bec88522b1cf19905`.
- exporter `5f94a4d885643e706a57a9e8faa1bf9fa5338e8626831d74dfe59f2d833158a1`.
- coverage.py `3c8fab7a6613ce6c5c2ec5b4e104aee8ef166615e0a5350792af609fa766a2c2`.

## Runtime, browser and verification

Scientific Python: `C:/Users/idoca/miniconda3/python.exe`.

Node: `C:/Users/idoca/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe`.

For tests use a writable task TEMP/TMP. Old working test directory: `C:/Users/idoca/.codex/visualizations/2026/11/14/01a1daa4-cbff-7830-8cb0-b8342b49ec5d/test-temp`. A new chat may need its own writable visualization/temp root. Avoid Windows temp permission failures. Use bundled dependency loader for new document/spreadsheet authoring, per relevant skill.

Existing read-only local servers8877/8881 left alive; do not stop them. Browser lastused `http://127.0.0.1:8877/interactive_map/trends.html`. Prior CUA part was finalized with completion_summary. A new browser verification needs normal tool initialization and its own final completion_summary. FullAX snapshots can be huge/hang; prefer cheap DOMlocators/read-onlyevaluate. Preserve existing browser selections/preferences.

Map IDs: `#rankFilter` valuevalidated, `#regionList`, `#openGroupFilter`, `#groupEcosystem`, `#groupModel`. Groupcheck accessible names `Include <exact group>`. Close button `Close group selection`. Trends `#regionReviewFilter` valuevalidated. Page fingerprint meta `ppr-project-sha256`. Prior trend selectedNorthSea wasunreviewed, correctly noselectedregionsmatched; don't mistake storeduserselection forfilterbug.

Final acceptance for each new decision: freshread_report→exactProjectrow→bothpagepayload equality; source/canonicalhashes; exactstatus/signature/date/verdict/reason/exclusions; signedtext and sourceScientificbytes unchanged; selection/rationale preserved; no pendingreview; correctpositivefilter/rednegativecase; unavailable/provisional/WARNstates truthful. Browser groupdefaults are overridable userpreferences, not deletionfromnetwork.

## Recommended division and time estimates

Use small-context subagents with exactpaths/deliverables, avoid fullhistoryforks when unnecessary, and stop them afterboundedcompletion. Reuse preparedQA. Parent owns all centralwrites. Good parallel work: one subagent stagesICES integration while parentfixes037andpublishesreadybatch; one bounded subagent prepares026metadata/replay implementation. Avoid duplicate independentfullaudits or concurrent centralwriters.

Estimates are elapsed walltime, not guarantees or token estimates:

| Remaining work | Estimate | Dependency |
|---|---:|---|
|037explicitflatflagsdisplayfix+focusedcheck|10–20min|BeforeRUN2preflight|
|RUN2isolatedpreflightandanysmallmismatch|5–15min|Packagesalreadyready|
|RUN2publicationtransaction|45–70min|Prioractualbatch63min; sourceunchanged|
|RUN2controls/browser/receipts/cleanup|10–20min|Afterpublication|
|024boundednegative-reviewregistration+pages|5–15min|SerializeafterRUN2; nonewscience|
|026pooledDOCXbinding|Almostfinishedinoldchat; seefinalcheckpoint|NoProjectwrite|
|026exactnewrow+two-decisionsboundedpublication|20–40min|Needsmetadata/replaysequencing; noresultadoption|
|022retainedintegrationpackage+meaningfularithmeticQA|30–60mininitialestimate|Read-onlyauditfinalcheckpoint; canoverlapRUN2|
|022central/pagepublication+finalcontrols|35–65min|Packageapproval/integrityfirst; maycombinecompatiblelatermetadatawork|

Do not add all rows mechanically; much preparation can overlap. The earlier 75–120 minute estimate was ONLY for 003/014/037, before the later 022/024/026 scope arrived. The complete queue plausibly requires 2.5–4 hours, depending on ICES prerequisites and publication runtime. Re-estimate from observed stages and communicate changes. A late failed transaction could add about an hour; address known semantic checks before expensive publication.

## Final checkpoint before successor creation

All three old-chat subagents finished their assigned work and reported that they have stopped. No central writer or publication transaction was launched. Do not treat prepared packages as published.

**LME_026 candidate record complete:** canonical pooled `model_validation/validation.docx` SHA `337ef70efe2a1f904505728208e2041eb8ab9457c16e3784c4c08e64ba16c64d`. One-page render and visual QA passed, exact signed Review cell XML preserved, original report hash unchanged. Parser returns Ido Carmel,2026-11-14,MODEL DISQUALIFIED, exact reason, sections[]. Canonical `model_validation/evidence/source_review/researcher_review_20261114/authorization.json` SHA `0997eb57422bd7716f2b65aec3bb9a84c8c59085c0f29e0696c3e7443f152d66`. Work `outputs/proposed_central_metadata.json` SHA `2f2ef664114ce0025eade85e168fdf115e78e44bf0a1515e0832fb621e64ad67`. Read work `qa/coordinator_handoff.json`, `qa/completion.json` and `qa/visual_qa.json` as needed. All owned hidden Word rendering helpers exited. No Project/pages/selection/scientific files changed.

**LME_022 audit complete:** `model_validation/work/2026-11-14_200000_ices_full_review/qa/coordinator_retained_adoption_audit_20261114.json`, SHA `1c47e1a9293a7a500003c8a797043cffcd214208c84bbfa98a76225bd62b08ec`. Ready for retained staging:70 groups,630 coefficients,3 WARN methods,384 taxa,715 assignments. Primary8 + summary7 artifact hashes passed;91 validation-index entries passed, with only signed-report provenance still needing explicit update. The current parser passes. **Pin actual executed engine bytes from Git commit38cb75d; model-local input ModelData/PPR copies are not the executed bytes.** Read the audit before staging. Preserve the stale Scotland source_note as historical, not current ICES provenance. No result source/snapshot/manifest exists. The auditor's own integration estimate was30–45minutes; the parent estimates above allow additional time for the observed large central workbook/page runtime.

**Final shared checks:** current Project hash remains `c9fb86a34119987348e7a4e89536cd154209ee8d7fc8769a8e1791c3db48ef9c`; no new numerical packages applied. New chat must verify this and absence/liveness of central lock before mutations. Use an initial fresh, bounded source/hash check; do not reread all old chats or repeat completed scientific audits.
