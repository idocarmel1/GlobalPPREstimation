# Baseline validation of current research skill instructions

Date: 2026-09-28. This is a read-only scenario assessment of the instructions that existed before revision. The only output created is this assessment. No model, workbook, code, or skill was changed and no scientific calculation was run.

## Evidence boundary

Read only:

- `tools/skills/prepare-ecopath-model/SKILL.md`
- `tools/skills/calculate-regional-ppr/SKILL.md`
- `tools/skills/update-ppr-project/SKILL.md`
- The current `README.md`, particularly Research stages and locations, Change a region, Workbook reference, Freshness and ownership, Instructions for research agents, and Validation and scientific limits.

No new lessons, parent task history, models, source papers, preserved original skill references, or implementation files were consulted. Where a current skill delegates a decision to an original reference, that referral is reported; the unseen reference's contents are not assumed. The scenarios are hypothetical inputs, not findings about particular regional models.

## Scenario 1: missing diet, failed publisher supplement link, possible predecessor baseline reuse

### Steps directed by the current instructions

1. Resolve the project from the ancestor containing `Project.xlsx`; resolve the regional workbook and read Overview and the workbook contract.
2. Archive discovered papers and supplements in `papers/<paper_id>/`. Record citation, year, modeled periods, distinct model identities, geographic coverage, and the basis of that coverage centrally. Missing evidence remains missing; candidate availability, applicability, model health, and adoption are separate matters.
3. Read the preserved extraction skill as instructed. The current entry point expressly requires exact groups/table layouts, coordinate-based extraction inspection, prose/footnote and biomass-accumulation review, import validation, mass balance, and a JSON round trip. Write source-faithful tables, page/cell evidence, and source JSON under the model directory, preserving unknown source values separately from loader defaults/corrections.
4. If taxonomy or the full paper-to-PPR chain is requested, read the preserved paper-to-PPR workflow and its taxonomy and source-bundle references. The entry point expressly says to distinguish a source's archived presence from verified numerical use.
5. Record structural profile, exclusions, limitations, and review findings in Diagnostics and central source/model records. Do not silently adopt a validation experiment or remove historical identity caveats.
6. Under README's LME-candidate rule, retain a model-specific diagnostic report and compact results record. If missing evidence makes the candidate scientifically blocked, produce an explicit not-run report with reasons and missing evidence, rather than an unsupported numerical run.
7. Recommend a model unless selection is already authorized. If selection is authorized, record identity, path, and rationale in regional Overview and keep incomplete processing explicit.

### Baseline decision and limitations

The failed link is not numerical evidence. Possible predecessor reuse is not established reuse. These documents require source fidelity and explicit missing evidence, so they do not authorize silently filling the missing diet from the predecessor. They allow a blocked/not-run outcome with retained reasons.

The three entry points and README do not themselves give an ordered recovery process for failed supplements, stopping conditions for searching, required provenance for inherited diets, or an exact test distinguishing legitimate predecessor reuse from an unsupported reconstruction. They refer to preserved scientific/source-bundle instructions for further detail, which were outside this assessment's permitted reading. No particular recovery channel or reuse criterion can therefore be attributed to the inspected instructions.

## Scenario 2: unknown biological B loaded as 1; blank BA solved; diagnose says OK; only direct GE/TE/Egestion requested

### Steps directed by the current instructions

1. Resolve/read the regional workbook and relevant blocks and keep the work within the requested research stage.
2. Preserve unknown source B separately from loader defaults/corrections in the source extraction record. The current preparation workflow also calls for biomass-accumulation review, import validation, balance checking, and JSON round-trip verification.
3. Inspect Diagnostics before accepting configurations. Any negative source group matters, including an unfished group. Preserve distinctions between source support, numerical validity, and ecological interpretation.
4. For every processed LME candidate, README requires a full model-specific diagnostic report and compact results record. Report strict source admission separately from canonical and loader-completed balance, including transformations; exact configuration health, convergence, residuals; negative contributions/coefficients across all biological groups; method outcomes and unavailable/timed-out results; Monte Carlo settings and accepted/rejected draws; source/taxonomy/spatial/provenance limits; and production eligibility. Existing sufficient diagnostics can be reused. Scientifically blocked candidates get an explicit not-run report.
5. The entry points name `python tools/run_region.py --region <workbook> --stage sppr` as the selected-model SPPR command, prohibit the broad historical batch exporter, and warn that Monte Carlo reruns are new realizations. They do not show a direct GE/TE/Egestion-only command.
6. If calculation inputs are changed, the calculation skill directs a regional calculate stage to validate assignments/remap coefficients/rebuild annual results and invalidate prior sensitivity bounds. It also says to stop at a requested matching-only stage and report downstream refresh needs; README more generally requires staying within the requested research stage.

### Baseline decision and limitations

An `OK` diagnosis alone cannot establish strict source admission: README explicitly separates source admission from canonical and loader-completed balance, while preparation explicitly preserves unknown values separately from defaults. The unknown B and solved BA must remain visible as source/default/completion distinctions. The inspected documents do not establish whether the stated model qualifies for any specific direct method or for production.

They do not specify a strict-admission decision rule for biological B=1 that originated as an unknown, nor an exact rule for blank BA that is solved by a loader. They do not define what this particular diagnostic `OK` certifies. They refer to original integration semantics and exact configuration gates without spelling out those gates here.

There is operational tension between a direct-method-only request and a generic SPPR command plus the all-method/Monte Carlo diagnostic-report requirement. The inspected text does not explain how to request only direct GE/TE/Egestion, represent intentionally unrequested methods, or meet that report requirement without launching unrequested calculations. It does not itself authorize expanding the user's scope to fresh Monte Carlo runs. No direct-only execution route is inferred.

## Scenario 3: unresolved Scomber label, documented constituents all in one group, 2019 PPR five times an earlier year

### Steps directed by the current instructions

1. Read the model, current Catch, Selected model groups, and source papers. Read the preserved mapper workflow and its model-structure, coarse-taxon, and output-format references.
2. Capture explicit species-to-group evidence and resolve synonyms. Explicit source membership takes precedence over a broad ecological analogue. Preserve exact group identifiers; do not let one supported member hide unsupported constituents.
3. For the stated case, if the documented constituents exhaust the taxon's supported interpretation and every constituent maps to the same exact group, the current membership-precedence and weight rules support one matching row with weight 1, evidence, explanation, and confidence. If that premise is not established, unresolved rows retain blank group/weight. An unresolved label alone does not explicitly override complete constituent evidence in these instructions.
4. Validate exact identifiers, complete taxon coverage, membership contradictions, weight sums, and inappropriate basal-group assignments. Report tonnage and taxon coverage; the 95% tonnage target is a review target, not permission to invent membership.
5. After changing matching/calculation inputs, run the calculate stage. It validates assignments, remaps coefficients, rebuilds annual outputs by scope/basis/unidentified treatment, and records freshness. Use inspect-year for a requested year's taxon view; all annual years remain in outputs. For a matching-only request, stop at matching and disclose downstream refresh needs.
6. Preserve catch bases, source scopes, missing coefficients/years, wet-weight totals, and the single division by nine for carbon display or PPR/NPP. Validate and report model/source limitations for a complete regional request.

### Baseline decision and limitations

The inspected instructions provide a defensible conditional route from complete constituent membership to a weight-1 assignment. They do not specify a Scomber/genus-label adjudication checklist, required documentation of constituent exhaustiveness, or a numerical confidence threshold. Such detail may be delegated to the unread original mapper references.

A fivefold annual difference is not labeled an error or a valid ecological change by these instructions. They provide annual and taxon inspection capabilities and comparable scope/basis conventions, but no explicit trigger, tolerance, or required attribution procedure for investigating a large PPR jump. They do not explicitly require decomposing the change into catch, coefficient, taxonomy/mapping, coverage, or composition contributions. No causal conclusion or correction can be made from the ratio alone.

## Scenario 4: user selects a FAIL model and requests registry update; older reports say unselected

### Steps directed by the current instructions

1. Treat the user's selection as authorization to record selection. Regional Overview owns selected_model_id, model_path, and selection_rationale; generated project selection is not edited independently.
2. Register the selected model in `Project.xlsx / Models & coverage` if absent, using known source identity, and maintain known paper metadata in Papers without inventing metadata.
3. Preserve previous model-specific outputs when changing selection. README gives `python tools/run_region.py --region <region-folder> --stage prepare-selection` to archive the preceding workbook, clear model-dependent results, and mark the new selection pending. A selection can be recorded without numerical results and must not borrow the previous model's values.
4. Keep the failed diagnostic state and limitations visible. Selection, candidate preference, successful computation, source support, and production eligibility are distinct. The workbook contract requires `status=ok` to publish PPR, and the update skill says to preserve exact method health and missing states.
5. Run the regional project updater for the requested region; the update workflow also supplies the HTML build command. Neither updater nor HTML generation runs SPPR or performs matching. Verify regional totals, source links, and missing states, and check generated HTML when it is built.
6. If prior-model results or changed hashes remain, refresh the affected processing through the regional workflow when requested; do not rewrite hashes to bypass stale-result checks. A pending selection can be consolidated immediately without SPPR/matching.
7. Treat older reports as historical evidence. README says current regional Overview owns selection and historical instructions are not new requests. Preserve original research evidence unless the user requests modification.

### Baseline decision and limitations

The user's selected FAIL model can be represented as the current selection with pending/unavailable numerical results. The current text does not require a model to pass before it can be selected, and a failure does not authorize borrowing prior-model results or publishing failed PPR as `ok`. Older reports saying unselected do not supersede the current authorized Overview selection; preservation rules do not direct rewriting those historical reports.

The inspected entry points do not precisely define propagation of an aggregate `FAIL` into each direct method/configuration's eligibility; exact gates are delegated to original references. They also do not spell out a metadata-only registry-update variant separate from the update skill's standard updater-plus-HTML sequence. README's stage-scoping rule constrains expansion of a narrowly requested registry update. There is no explicit conflict-resolution protocol for reconciling historical unselected statements in current-facing contextual material, beyond clear ownership and preservation rules.

## Baseline conclusion

The current documents establish strong ownership, source-fidelity, missing-state, selection-versus-adoption, and provenance boundaries. README already demands distinct source-admission and loader-completion reporting and full candidate diagnostics. The main scenario gaps in the inspected entry points are explicit source-recovery/inheritance criteria, strict admission and direct-only execution rules, anomaly attribution requirements, and precise failed-model method-gate/status propagation. Those omissions cannot be filled by assuming the content of unread historical references.
