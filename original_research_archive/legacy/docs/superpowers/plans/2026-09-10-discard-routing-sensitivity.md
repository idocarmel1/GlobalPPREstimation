# Discard-routing sensitivity and standalone results HTML — implementation plan

> **For the receiving agent:** Use the executing-plans workflow to carry this research task through implementation, numerical verification and delivery. The user has explicitly authorized this study and its HTML output. Resolve ordinary implementation choices autonomously. Work sequentially by default while the existing NPP extraction agent continues. This document is both the scientific specification and execution plan.

**Goal:** Quantify how source-model treatment of discards changes SPPR and ecosystem PPR across methods, deliver a standalone interactive HTML with reproducible sensitivity results, and apply the user's landings-only central estimate plus discard-related sensitivity envelope to the existing map without disrupting annual NPP work.

**Architecture:** Run experiments against private copies of frozen calculator code and model/catch inputs. Use a common, explicit flow ledger to transform discard routing, then recompute each supported method. Generate the standalone HTML from verified results. After coordinating file ownership with the NPP agent, integrate only landings-based evaluation and versioned sensitivity-response data into the production map; keep experimental calculator changes private.

**Tech stack:** Existing Python scientific stack, pytest, CSV/JSON, and standalone HTML/CSS/JavaScript; use locally available plotting libraries when useful. Prefer embedded assets and data so the final HTML opens offline without a server. Reuse the user's installed runtime rather than modifying shared environments.

**Requested executor:** Existing task “Explore GlobalPPREstimation project,” id `01a08b83-fe92-7453-af04-51d267b3dd16`, using `gpt-6-astra` and `ultra` reasoning effort. The user changed the handoff destination from a new chat to this now-finished chat. Do not create another user-facing task.

## Latest user clarification — controlling experimental design

The user explicitly wants **different percentages of the catch already present in each source model allocated to discards**, not a new source model for every historical year. This clarification controls the interpretation of the tasks below.

- Freeze each original model and its modeled catch vector H. For a uniform fraction f, designate D_i(f)=f*H_i and retained L_i(f)=(1-f)*H_i for each caught living group. The designated discard amount is a subset of the existing modeled catch, never an addition to it.
- Primary fraction grid: **0%, 1%, 5%, 10%, 20%, 30%, 40%, 50%, 75%, 100%**. Show 75–100% as stress-test endpoints; preserve infeasible cases with reasons. A smoother slider/curve can use additional computed points after this grid is verified. Never interpolate across invalid cases as if a model was solved there.
- Use a uniform fraction initially so the effect is interpretable. A secondary group-specific allocation may use documented discard patterns while holding the same aggregate designated discard amount, but is optional and must be labeled separately.
- Recompute SPPR once per **model × fraction × routing scenario × method/settings**. There is no year loop for fitting or reconstructing models. Cache identical configurations.
- Evaluate the primary coefficient effect using the **same original H vector in every scenario**. Separately show the retained-catch-only footprint using L(f). This prevents dropping designated discards from the evaluated numerator from being mistaken for a coefficient effect.
- Report native-model PPR first, with its native area/time units. A native PPR/PP or PPR/NPP comparison must use the same model boundary and an explicitly identified, compatible production denominator. The optional 2019 LME application uses the perturbed coefficients with a frozen external catch/mapping/NPP snapshot and is a distinct panel, not a new model fit.
- Published discard fractions are **reference markers/validation information**, not required amounts for the main hypothetical percentage experiment. Unknown original discard fractions do not block that experiment when the source model itself is usable. Still audit pre-existing return flows: replace/reclassify the designated flow coherently rather than adding a second copy of a return already present.
- Add invariance tests: SC should be independent of f when all H remains the same catch sink and no new return is credited. Uniformly scaling catch weights usually leaves a normalized catch-weighted mean unchanged for f<1; at f=1 some methods switch to a biomass-weighted fallback or become undefined. Expose that endpoint behavior rather than presenting it as a smooth ecological effect.

For the primary native-model “standard method” benchmark, use fixed baseline group TL and TE=0.1 with the same H. Show recomputed model-TL SPPR_1995 separately when the perturbation changes its TL. External taxon-TL simple-chain results belong to the secondary 2019 application. These controls avoid conflating changes in the benchmark itself with excess/deficit relative to recycling scenarios.

## Latest map instruction — landings central estimate and sensitivity band

The user subsequently instructed: **“for the map itself, calculate PPR from landings only, and add the uncertainty band according to the relative size of discards and the results of the sensitivity analysis.”** This authorizes the focused map integration in Task G after the isolated study and coordination. The earlier total-catch-headline recommendation is superseded.

- Central map estimate: `PPR_landings = sum(L_i * SPPR_i) / 9`, using the selected method, scope, year and unidentified-taxon setting. L includes reported and unreported retained landings. PPR/NPP map colors use this numerator and the currently selected annual NPP method. Retain total catch/discard data for explanation and sensitivity, not as the central numerator.
- Region/year discard exposure: `f = D / (L + D)` from actual regional catch data, with mapped/covered equivalents and group composition available where relevant. Do not confuse this with D/L. Handle no catch and missing classification explicitly.
- Use the fraction-dependent **coefficient/recycling** responses from the study to evaluate possible PPR on the **same landed catch vector**. Do not simply add the PPR of discarded catch to the upper endpoint; that would mix a different catch boundary with the requested uncertainty.
- For a tested compatible model/method, prefer taxon/group-level perturbed coefficients applied to actual landings, preserving fixed mapping weights and units. A scalar response curve is acceptable only with its weighting and transfer assumptions stated. Interpolate only over verified valid intervals, or compute an additional exact-fraction scenario without any annual source-model refitting.
- Report a min/max range across valid, identified scenarios as a **discard-routing sensitivity envelope**. It is not a confidence interval. The central landings estimate need not be the midpoint or lie between all alternate scenario estimates; show its relation honestly. Do not force uncertainty to be symmetric or upward-only.
- Differentiate tested model-specific envelopes from explicitly labeled transfer/proxy envelopes. A small sample of food webs does not validate global uncertainty bounds. Default to “not assessed” for unsupported model/method/scope combinations; do not substitute zero uncertainty. Any optional pooled proxy must be visibly labeled, identify donor models and have a documented applicability rule.
- The external fixed-TL standard method is insensitive to routing by construction. Do not interpret this invariance as proof of no recycling uncertainty. Use the study's standard-versus-recycling comparison to explain and, where defensible, expose a separately labeled recycling-reference discrepancy envelope. Distinguish ordinary between-method differences from the incremental effect associated with f. Never relabel a cross-method proxy as measured within-method uncertainty.
- On the map, color regions by the central estimate and show the numerical range, a compact interval graphic, discard fraction, method/source and validity in the region detail/tooltip. If updating linked time-series displays, use landings consistently and shade only supported bands with matching settings; do not silently leave a linked graph representing total catch while the map represents landings.
- The NPP denominator stays fixed within each discard-sensitivity comparison. Divide the PPR interval endpoints by the same selected NPP to obtain PPR/NPP bounds; NPP uncertainty remains separate.

## 1. Authorization, isolation and current work

- Project: `C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation`.
- The receiving task's previous atlas/workbook integration is finished. Its NPP child `01a08bce-faaa-71a0-b413-9422a846fe4c` remains active and owns annual NPP extraction, refreshes and related live outputs.
- **During Tasks A–F own only the new directory `research/discard_sensitivity_2026_09_10/`.** Put all new research code, private calculator copies, tests, model variants, logs, data, HTML and figures there. A separate experimental directory with private code and frozen data avoids modifying either the shared checkout's calculator or the NPP agent's outputs. If using a worktree as additional isolation, do not hand off or move the existing shared checkout and its uncommitted state. Task G has the additional narrowly authorized integration scope below.
- Frozen handoff inputs are in `tmp/discard-sensitivity-handoff-2026-09-10/inputs/`, with a hash manifest in its parent. Copy the needed frozen material into your owned directory before experimentation. Preserve the frozen input tree itself unchanged.
- During research, do not modify `PPREstimation/`, `tools/`, `tests/`, `data/`, `NPPExtraction/`, `PPRAtlas/`, existing shared documentation, project settings, or this plan in place. Do not regenerate production workbooks or maps until Task G's ownership coordination is resolved. Keep production `PPREstimation/` calculator code unchanged throughout; integrate response data and evaluation policy rather than experimental engine changes.
- Do not run broad exporters. In particular, do not execute `PPREstimation/create_PPRS_excel.py` directly: its main block can overwrite the entire live `output/top10` set irrespective of supplied arguments.
- Do not reset, stash, clean, checkout or stage the other task's changes. Do not stop other processes or reuse their servers (8765/8766). If a local server is needed for browser verification, allocate an unused port and stop only the server you launched.
- No further all-year NPP downloading is part of this study. Freeze available 2019 NPP and record its snapshot. Missing NPP must not prevent reporting PPR or coefficient sensitivity.
- Do not merge or copy experimental calculator changes into production. Final delivery includes the new HTML, result tables, reporting protocol and the user's focused map update from Task G. Report any real calculator defects independently from the experiment's assumptions.

## 2. Scientific question and terminology

The preceding audit held SPPR fixed and split annual catches into landings/discards. That answered how much current PPR is attributed to discarded catch, **not** how much different discard recycling changes the coefficients. This task must recompute SPPR after the routing changes.

Use two separate catch concepts:

1. **Source-model catches and discard flows:** in the original model's own period, units, area and functional groups. These define the experimental food-web perturbation.
2. **External evaluation catch:** an optional secondary fixed annual vector used to multiply the perturbed SPPR coefficients. Use 2019 SAU catch for comparability with the atlas. Keep group mapping, mapping weights, carbon conversion, taxon inclusion and NPP fixed in this comparison. The primary evaluation instead uses the frozen native-model catch H as specified above.

Never insert regional 2019 tonnes directly into a historical model expressed in t/km²/year. Native model-period PPR is the primary panel; the external 2019 application is optional and clearly separate. Do not call a modeled scenario ground truth.

The standard trophic method is a useful benchmark. Report its **signed relative excess/deficit** against every valid recycling scenario. Call it “overestimation relative to scenario X” only when the sign is positive. Distinguish the external taxon-TL simple chain from model-derived `SPPR_1995_TE0.1`; they are not interchangeable. Do not assume either must exceed a recycling-aware method.

## 3. Explicit routing ledger and required scenarios

**Resolve the catch/export alias first.** The current loader renames JSON `export` to `catch`. Assigning the same discard amount to those two field names would not create distinct physical experiments. Explain this in the report and test it. If two routes are mathematically equivalent for a method, equal results are an informative outcome, not a reason to fabricate a distinction.

For each group, build an auditable ledger with production, consumption, predation, baseline non-predation mortality M0, egestion, retained landings L, dead discards D, other external loss E, biomass accumulation, migration and detritus destinations. Keep offal distinguishable from whole discarded fish where the source does so. Do not add processing offal twice to catches already recorded as landed biomass.

The production budget must close with each discard removal counted once. Track the return flow separately from the removal. Separate retained catch, discarded fishery mortality and non-fishery external loss even if a private calculator adapter must map their sum to a legacy sink variable. Preserve the distinct ledger and document what each method actually consumes.

Required comparisons, where supported:

- **S0 — Published/imported baseline:** untouched source and the current calculator behavior; record known conversion limitations. Reproduce its saved results before applying any perturbation.
- **SC — Discards counted as catch:** D remains a fishery catch/removal with no separately credited internal discard return, corresponding to the current combined-catch convention where applicable. L remains retained landings; do not relabel D as landed fish in the report.
- **SM — Discards routed through M0:** remove the specified D from the catch sink and add it to the group's M0 route, carrying that flow through the selected detritus-fate fractions. This is an **accounting sensitivity proxy**, not a biological claim that fishing deaths are natural mortality. Recompute the dependent EE/flows coherently rather than editing a derived M0 field that initialization will overwrite.
- **SE — Discards treated as external loss/export:** remove D from fishery catch and route it to a distinct external sink, with no internal return. Do not silently use net migration as a substitute. A private experimental adapter can represent the sink explicitly. Catch-weighted methods may differ from SC because their weights change; flow methods that see only the combined sink may be invariant. Diagnose and label that distinction.
- **SR — Explicit discard return reference, when documented:** keep D as fishery mortality and route its returned biomass to the source's documented detritus/scavenger destination. This separates a faithful discard representation from the M0 proxy. Do not invent a return destination or a full-return assumption as a source fact. If unsupported, keep SR hypothetical or unavailable.

Use the original source fate as the preferred destination. If unknown, test clearly labeled plausible destination alternatives only when the model supports them, and record the assumption. Do not normalize undocumented fate fractions silently. A portion leaving the modeled region is external loss; returned detritus is not new primary production or an external detritus subsidy.

For the simplified fixed-production/fixed-predation reclassification, verify the necessary EE change analytically. Example bookkeeping fixture: P=100, predation=20, M0=30, L=40, D=10, other export=0, and zero accumulation/migration. SC has catch=50 and EE=0.70; SM has catch=40, M0=40 and EE=0.60; SE has catch=40, M0=30, external export=10 and EE=0.70. Each totals 100. SM must add exactly 10 units to the routed return if the fate fraction is one. A full food-web run must also satisfy detritus and consumption balances; this group example does not by itself establish full ecosystem balance.

Keep source parameter changes minimal and explicit. If fixed production, predation, detritus use and all other requested constraints cannot simultaneously hold, document the closure rule and which parameters were solved. Do not hide rebalancing adjustments or silently repair inputs. Preserve invalid scenarios with diagnostic reasons.

## 4. Model selection and evidence

Aim for **four real models plus a small analytic/toy control**, starting with:

| Candidate | Why include it | Specific caution |
|---|---|---|
| Northern Humboldt Current, `13_2_Northern_Humboldt_Current_(1995-1998)` | Separate source discard metadata and an offal compartment; strongest starting candidate | Check how source routing survives conversion and the ecological role of the offal compartment |
| Bay of Bengal, `34_1_Bay_of_Bengal_(1978)` | User's focal system and low direct discard contribution | Original model combines catch; its discard split is not automatically known |
| Sea of Okhotsk NE, `52_1_Sea_of_Okhotsk_NE_(1980)` | High annual discard contribution | Model period/area differ from LME-wide 2019 evaluation; verify original discard evidence |
| Guinea, `28_646_Guinea_(1998)` | Another high-contribution case with different food-web structure | Source represents a subregion; preserve domain caveat and distinguish model vs LME catch |

Prefer evidence quality over completing a nominal model count. If a candidate's food web cannot support a valid scenario, show its limitation and choose a source-rich substitute if readily available. Complete at least a few usable real-model comparisons where feasible. The designated fractions in the primary experiment are explicit hypothetical inputs, not made-up claims about source discard observations.

The primary experiment deliberately designates the same percentage grid of each model's existing harvest, whether or not published D is known. Distinguish these **hypothetical** scenarios from observed reference points. A source-period SAU discard fraction mapped to groups may be an optional reference proxy, with explicit temporal/domain/mapping limitations; it is not a recovered published parameter. Do not replace a missing value with a global discard percentage and describe it as observed.

Use primary publications, supplements and EwE guidance to resolve definitions. Internet access is available. Earlier user preference was Perplexity: use it if accessible for discovery, then verify claims against original sources. A search summary is not extraction evidence. No broad new literature/model coverage project is required.

## 5. Method matrix and paired evaluation

Read the frozen `PPREstimation/information/SPPR_Methods.md` and the implementation before choosing flags. Include:

- External simple trophic chain, TE=0.1, fixed external TL: an invariance control under routing-only perturbation.
- `SPPR_1995_TE0.1`: recompute model TL and show whether/why it changes.
- `SPPR_1995_TEmean` and at least one catch-weighted formulation where available, to expose weighting changes.
- Representative recycling-aware methods: `new_GE`, `new_TE_EEfix`, `new_WithEgestion`, plus valid EwE/Ulanowicz alternatives supported by the selected models. Expand to other deterministic available methods when inexpensive and interpretable.
- Monte Carlo variants only where useful after deterministic comparisons pass. Use matched random draws across paired scenarios and record seeds/configuration. Do not let random run-to-run variation masquerade as a routing effect.

Keep flags, basal-source scope and solver settings identical within a paired comparison. “All basal sources,” “internal” and “primary producers only” are different estimands. Provide scope as a separate comparison if supported; never pool scopes into one uncertainty envelope.

For the main external comparison, freeze mapping weights. A weight based on source-model catch must not be silently recomputed when the catch/export label changes. A later optional mapping-sensitivity panel may recompute it, but must distinguish mapping effects from coefficient effects.

For each model/scenario/method/scope, report group SPPR, fixed-catch PPR in t C, absolute and percent changes from S0, PPR/NPP with a fixed denominator, source-model group balances, solver status, recycling diagnostics, changed parameters and catch coverage. Use consistent taxa/common support for paired differences; a newly failed coefficient must not silently disappear from one scenario's total.

## 6. Integrate uncertainty into the reporting plan

Apply the user's revised recommendation: consistent **landings-only central PPR**, with total-catch/discard components retained as explicitly labeled context. Add a **distinct structural sensitivity component** for source-model discard routing, evaluated on the same landed-catch numerator.

Perform the experiment in stages:

1. Hold the native evaluation catch H and compatible denominator fixed; compare S0/SC/SM/SE/SR across the discard-percentage grid. This isolates source-model coefficient sensitivity. Optionally repeat the evaluation, without refitting models, against a fixed 2019 external catch vector.
2. At fixed baseline coefficients, compare retained L(f) versus total H. This isolates the direct catch-boundary effect under the designated percentage. The previous actual-2019 landings/discards split is a separate secondary application.
3. Cross the two factors to show their interaction. For evaluation catch vectors H0 and H1 and coefficient scenarios s0 and s:

       coefficient effect = PPR(s,H0) - PPR(s0,H0)
       catch effect = PPR(s0,H1) - PPR(s0,H0)
       interaction = PPR(s,H1) - PPR(s,H0) - PPR(s0,H1) + PPR(s0,H0)
       total change = coefficient effect + catch effect + interaction

4. The required primary gradient is the designated discard percentage f from the latest clarification. For feasible cases, optionally evaluate a separate partial-return gradient (0, .25, .5, .75, 1 of D(f)); do not confuse percent of catch designated discarded with percent of those discards returned. Avoid an unnecessary full Cartesian sweep over all unrelated assumptions. Each mixture must conserve the same designated amount and have a stated catch/sink weighting convention.
5. Report an envelope across **valid, explicitly defined routing scenarios** within each model/method/scope, with absolute range, relative spread and changes in method rankings. Keep known-input and hypothetical-input envelopes separate. This is a sensitivity/scenario envelope, not a 95% confidence interval or a probability distribution. Do not assign equal probabilities to alternative routes without evidence.
6. Keep NPP, TE, unidentified-taxon treatment and biological parameter uncertainty separate. Optional source-supported Monte Carlo propagation must state distributions and dependencies, use paired draws, and distinguish within-scenario statistical uncertainty from between-scenario structural spread. Do not add unrelated uncertainties in quadrature automatically.

For the standard-method benchmark report `100 * (PPR_standard / PPR_scenario - 1)` with the reference named explicitly. Show absolute differences as well. A zero or invalid denominator is unavailable, not infinity. Provide the range of this excess/deficit across scenarios; do not label it proven bias against the real ecosystem.

Do not apply a percentage correction inferred from these few models to all 366 ecosystems as if validated. Propose a future reporting scheme with model-specific uncertainty bands where tested and “discard-routing uncertainty not assessed” elsewhere. Explain whether a screening relationship with direct discard share or recycling diagnostics is suggested, and its small-sample limitations.

## 7. Deliverable structure and execution tasks

All paths below are inside `research/discard_sensitivity_2026_09_10/`.

### Task A — Freeze, inventory and reproduce baseline

**Create:** `README.md`, `inputs/`, `input_manifest.json`, `src/baseline.py`, `results/model_inventory.csv`, `results/baseline_checks.json`.

- [x] Verify the supplied handoff hashes; copy the required inputs and private engine files. Record source paths, SHA-256 hashes, baseline Git revision and all model/method settings. Do not follow future live-file changes during the experiment.
- [x] Record model discard evidence and missing information with source page/table references. Check numerical units and model domain before choosing D.
- [x] Instantiate private copies of the unchanged calculator and reproduce selected deterministic coefficients and totals against saved outputs within an explicitly documented numerical tolerance. Separate existing source failures from experiment failures.
- [x] Reproduce the 2019 fixed-coefficient direct-discard audit for the selected candidates. The expected current default SPPR_1995 direct shares are about Bay 3.32%, Guinea 18.14%, Okhotsk 27.67%, Humboldt 4.77%; these are sanity checks, not target results to force.

### Task B — Build an explicit ledger and verify routing

**Create:** `src/ledger.py`, `src/scenarios.py`, `src/experimental_engine/`, `tests/test_routing.py`, `tests/test_analytic_controls.py`, `results/scenario_definitions.json`.

- [x] Write meaningful numerical tests before adapter changes: the P=100 example above, zero-discard identity, fraction endpoints, amount conservation, missing-data preservation, and no double-counted return.
- [x] Trace precisely which engine fields each method consumes, including EE repair, catch-weighted TE/TL, detritus fate and export balancing. Document catches/exports that are aliases.
- [x] Implement transformations through the explicit ledger, using private engine adapters only. Retain the raw and solved values for each changed parameter.
- [x] Add an analytic food-web control with no return path (expected routing invariance for flow-only methods), and a convergent recycling loop that can be checked independently by linear algebra. Verify expected mathematical equivalence of SC and SE where their only difference is a label.
- [x] Demonstrate that each adapter change is reached by the calculator rather than overwritten by initialization/default filling. Fail clearly when a method cannot represent a route faithfully.

### Task C — Run paired real-model scenarios and diagnostics

**Create:** `src/run_study.py`, `src/metrics.py`, `tests/test_paired_metrics.py`, `results/group_sppr.csv`, `results/ecosystem_ppr.csv`, `results/diagnostics.csv`, `results/parameter_changes.csv`.

- [x] Execute the pure routing scenarios over the required designated-discard percentage grid on the selected real models, with the source-faithful/hypothetical distinction visible for each. Do not rebuild source models for separate catch years.
- [x] Recompute SPPR and native PPR for every valid method/fraction/scenario pairing. Optionally evaluate fixed 2019 external PPR, preserving fixed mappings and common comparison coverage.
- [x] Check living-group production, consumption, detritus inflow/outflow and whole-system budgets. Record residuals before and after any repair. Check non-negativity, finite results, valid EE where applicable, recycling spectral radii/convergence and solver failures. Do not interpret balance/convergence alone as ecological validation.
- [x] Retain unavailable/divergent scenarios with reasons instead of plotting them as zeros. Do not trim outliers merely because PPR/NPP exceeds 100%.

### Task D — Decompose effects and characterize uncertainty

**Create:** `src/uncertainty.py`, `tests/test_decomposition.py`, `results/effect_decomposition.csv`, `results/scenario_envelopes.csv`, `results/standard_method_comparison.csv`.

- [x] Verify that coefficient effect + catch effect + interaction exactly reconstructs the total change within tolerance.
- [x] Run the designated-discard percentage sensitivity, and optional partial-return or group-allocation sensitivities for feasible models, retaining all shared controls.
- [x] Calculate scenario envelopes and signed standard-method excess/deficit; show rank changes and identify which mechanisms drive large effects.
- [x] Explain whether low direct discard share can coexist with large coefficient sensitivity, and whether catch weighting explains SC/SE differences. Report observed answers, including null effects.

### Task E — Build and verify the standalone HTML

**Create:** `src/render_report.py`, `report.html`, `figures/`, `results/study.json`, `tests/test_report_data.py`, `verification/browser_checks.json`.

- [x] Build a readable, nontechnical report with controls for model, method, scope, routing scenario, **percent of existing modeled catch designated as discards**, evaluation catch boundary and metric. If partial return is implemented, give it a separate clearly labeled control. Include input assumptions and uncertainty type next to results; do not expose technical switches without an explanation.
- [x] Include: a routing diagram; baseline-versus-scenario coefficient/PPR comparisons; a group contribution view; a sensitivity curve; standard-method excess/deficit; direct versus coefficient versus interaction effects; and a sortable ecosystem summary. Use shared scales where comparison requires them and visible units everywhere.
- [x] Provide clearly labeled statuses for source-supported, hypothetical, unavailable and invalid cases. A hidden or excluded failed scenario must not make the uncertainty range look narrower without disclosure.
- [x] Embed the verified data and required assets, support CSV/JSON downloads and printable summaries. Default to the Bay of Bengal comparison where available; retain other models clearly accessible. Output must work by opening `report.html` directly. No production atlas modifications or external hosting are required.
- [ ] Open the actual HTML in the browser and exercise the selectors, chart/table synchronization, unavailable states and downloads. Check browser-visible numbers against the result tables and confirm labels use percentage vs percentage points correctly. Capture verification evidence.

### Task F — Deliver the revised scientific reporting plan

**Create:** `METHODS_AND_FINDINGS.md`, `INTEGRATION_PROPOSAL.md`, `verification/summary.json`.

- [x] State findings with primary-source citations, model identities, quantitative changes, evidence limits and scenario definitions.
- [x] Update the prior reporting protocol: landings-only central PPR + standardized annual catch/discard accounting + per-model discard provenance + tested source-routing sensitivity evaluated on landings + separate NPP/parameter uncertainties. Recommend which models should receive additional source auditing and why.
- [x] Define the minimal versioned integration interface for Task G, keyed by model, method, scope, source hash, designated fraction, scenario and evaluation convention; include uncertainty type, validity and coverage. Document any deferred extensions as proposals.
- [x] Run the focused numerical tests and final production browser checks (standalone-report browser check blocked, as recorded below). Check the experiment has written only its owned files. Deliver links to the HTML, methods/findings, downloadable results and integration proposal. Clearly identify anything that could not be estimated without new source evidence.

### Task G — Integrate landings-only map PPR and discard sensitivity without NPP conflicts

**Additional authorized production scope after coordination:** narrowly necessary changes in catch/evaluation exporters (`tools/build_network_atlas.py`, `tools/build_time_series.py` and a dedicated discard-response reader if useful), relevant map/time-series metric and display files under `PPRAtlas/atlas/`, focused tests, and the corresponding generated atlas files. Reuse the current integration architecture rather than creating a parallel production pipeline. Do not change NPP extraction logic or the main PPRCalculator methods.

- [x] Coordinate directly with the still-running NPP child before touching shared export code or generated files. Determine whether it is currently writing those files, agree which agent owns the final rebuild, and preserve all newly collected years and metadata. Extraction may continue while the sensitivity study runs; do not terminate or restart it. Do not let either final exporter overwrite the other's changes.
- [x] Snapshot the actual current integration code at this stage, which may be newer than the research snapshot. Make the production adapter consume the latest annual NPP schema. Reuse the already implemented unidentified-taxon and PPR/PPR:NPP controls; do not revert them or apply NPP coverage scaling twice.
- [x] Preserve landings and discards separately in exported per-taxon/year inputs or the minimum sufficient evaluation structure. Recompute central PPR from landings at taxon resolution; do not multiply old PPR by an ecosystem-wide retained-catch fraction, because landed and discarded taxonomic composition differs.
- [x] Add versioned sensitivity-response metadata with model/method/scope compatibility and source hashes. Evaluate bands against regional discard fractions and actual landings, using the protocol above. Keep missing, unassessed, proxy and invalid cases distinct in both data and UI.
- [x] Implement the central map colors, legends, tooltips, detail interval, downloadable results and any linked graph updates needed for consistent catch definitions. Retain reported plus unreported landings. Clearly label the central measure “PPR from landings” and the range “Discard-routing sensitivity.”
- [x] Add tests for different landing/discard TL composition; D=0; L=0; missing NPP; unsupported methods/scopes; selected unidentified treatment; an observed fraction outside the solved range; invalid intermediate cases; source-hash mismatch; and response invariance that must not become a false claim of zero ecological uncertainty.
- [x] Check a known Bay of Bengal reference: before changing coefficients, the prior frozen 2019 ensemble denominator gives model landings-only PPR/NPP about **42.26%**, rather than total-catch **43.71%**. Recompute from the current verified snapshot and explain any legitimate differences rather than forcing these numbers. Do not use this one regional adjustment as a global scaling factor.
- [x] Complete the coordinated final rebuild once, then check the live map and linked graph in a browser. Verify the central estimate and band update coherently with year, PPR method, NPP method, scope and unidentified treatment. Confirm all NPP years from the child remain present and no earlier UI features regressed.
- [x] Deliver the new standalone sensitivity HTML and the updated live map links, with exact supported-band coverage and remaining scientific limitations. No additional permission is needed for this requested map integration.

## 8. Starting references and available prior results

- `docs/discard-audit-2026-09-10/README.md`: preceding direct-discard audit and proposed accounting protocol.
- `docs/discard-audit-2026-09-10/model_methods_2019.csv`: direct contributions across available methods.
- `docs/discard-audit-2026-09-10/input_model_discard_fields.csv`: source-field inventory; not a completed paper audit.
- `docs/LME034_PPR_NPP_diagnostic_2026-09-10.md`: Bay of Bengal hypotheses and controls.
- `PPREstimation/PPRCalculator.py`, `ModelData.py`, `utils.py`, and `information/SPPR_Methods.md`: calculator mechanics.
- `PPRAtlas/data/network_ppr.json`: saved mappings/coefficient arrays, model status and source hashes.
- `PPRAtlas/data/time_series.json`: evaluation catch/NPP context; freeze its version because the NPP agent is refreshing live data.
- `SeaAroundUsExtraction/data/catch_by_taxon_year/`: historical taxon catch with landed/discarded split.
- [Pauly and Christensen 1995](https://api.seaaroundus.org/wp-content/uploads/2015/04/PrimaryProductionRequiredToSustainGlobalFisheries.pdf).
- [Sea Around Us catch reconstruction definitions](https://www.seaaroundus.org/doc/Methods/CatchReconstructionMethod/Methods-Catch-tab-May-02-2016.pdf).
- [EwE fisheries discard quantities, mortality and fate](https://pressbooks.bccampus.ca/ewemodel/chapter/spatial-fishery-dynamics/).

**Completion criterion:** A reproducible study that allocates different percentages of each model's existing catch to discards, recomputes SPPR under the user's three routes without constructing yearly source models, explains any mathematical equivalence or unsupported route, quantifies direct and structural effects separately for several usable models, and delivers a verified standalone HTML plus a reporting plan incorporating the resulting sensitivity uncertainty. The live map must use landings-only central PPR and show supported discard-related sensitivity bands with clear coverage/proxy labels, integrated without disrupting NPP work. A plan alone, a fixed-SPPR numerator toggle, or a mock HTML with invented results does not complete this task.

## Completion record — 2026-09-10

Tasks A–D and F–G are implemented and verified. Task E's report is delivered with
embedded verified data and 384 DOM-stub views; its actual browser check is the
single outstanding verification limitation. Direct local-file navigation was
blocked by browser policy and was not retried through an indirect route.

The latest catch-basis instruction is implemented: landings default with optional
supported routing sensitivity, plus all catch and discards-only with no envelope.
All 22 supported NPP years survived the coordinated final workbook/map/graph
refresh. There are 31 supported model/method/scope combinations across Humboldt,
Guinea and Bay; Okhotsk has no transferable response from zero native harvest.

Final evidence is in `research/discard_sensitivity_2026_09_10/verification/summary.json`:
56 private study tests, 107 root Python tests plus two subtests, 49 JavaScript
tests, 59 baseline comparisons, 16,200 production map/graph cases, full annual
NPP/workbook audits, unchanged frozen/production engine hashes and actual
production browser checks. No additional source model, global uncertainty proxy,
carbon-conversion change or production experimental-engine change was introduced.
