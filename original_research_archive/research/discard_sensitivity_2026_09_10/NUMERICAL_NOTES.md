# Numerical protocol and verified findings

The experiment designates fractions `0, .01, .05, .1, .2, .3, .4, .5, .75, 1` of each model's **existing living-group catch H**. It evaluates every perturbed coefficient vector on the same H, then separately on retained catch `L=(1-f)H`. It never fits a model for a catch year. Outputs have the native units **t C equivalent km⁻² yr⁻¹**, obtained from modeled wet-weight primary-production equivalents using the atlas convention `/9`. The model-period PP denominator is divided by the same factor. This assumed conversion is not a newly measured taxon-specific carbon ratio.

Native PP ratios are unavailable in all-source scope whenever the model has positive imported production: an imported-support numerator cannot be divided by internal PP as though their boundaries matched. PPR remains available. `native_denominator_compatible` and `native_ratio_reason` expose this guard; `native_import_production_tC` records the model import term. Compatible internal/PP-scope ratios remain constrained-model contextual ratios. This guard does not alter the separate regional satellite-NPP application.

## Baseline fidelity and source limitations

All **59 available deterministic saved-workbook method/scope comparisons pass** `atol=1e-7 + rtol=2e-7*abs(saved)`. The `standard_fixed_baseline_TL` control is newly defined and is checked against baseline `SPPR_1995_TE0.1`, so it does not add a saved-workbook comparison. The zero-harvest `SPPR_1986` calculation is unavailable rather than the legacy zero placeholder.

The saved exporter calls `PPRCalculator.from_modeldata(..., underdetermined=True, zero_biomass_accum=False, DC_tol=.001, normalize_DC=True)`. The exact reference source and hash are under `verification/baseline_invocation_source.json` and `baseline_runner_reference.py.txt`. The source JSONs and copied engine files are frozen. The three engine modules in `src/experimental_engine/` remain byte-for-byte copies; the new adapter lives separately in `src/scenarios.py`.

The initializer's diet normalization, missing-flow/default completion, and inferred living accumulation are logged separately from experimental changes in `results/parameter_changes.csv` (`stage=source_initializer` versus `routing_scenario`). Bay, Humboldt and Okhotsk require inferred living accumulation, including negative values. This is a constrained accounting experiment on the saved pipeline's completed models, not a new steady-state Ecopath calibration. Guinea retains small source rounding residuals: maximum living production residual about `7.3785e-5`, maximum consumption residual `4.8e-5`, and whole-system relative residual `3.4622e-8`.

The loader renames raw `export` to `catch`: these are aliases, not alternative routes. It then zeroes all detritus catches. Guinea's raw detritus export `1670.48071` is excluded from fishery H and catch weights; the importer instead carries its calculated detritus residual as accumulation. H is `0.86795216265` for Guinea, `1.025531307` for Bay, `35.5395489180725` for Humboldt, and **zero** for Okhotsk. Okhotsk's raw catches are explicit zeros, not values recovered from its contemporary regional fisheries. Its gradient is consequently a zero-harvest control and cannot support a regional sensitivity envelope.

## Physical ledger and dependent closure

For every living group the ledger checks

`P = predation + M0 + fishery_catch + external_loss + accumulation + net_migration`.

Consumption separately checks `Q = P + egestion + respiration`. The uniform transformation has `D=fH`, `L=(1-f)H`:

- SC: fishery catch remains H; M0 and EE remain baseline; no return is credited.
- SM: fishery catch becomes L; `M0'=M0+D`, `EE'=EE-D/P`. This is an accounting proxy, not natural mortality caused by nature.
- SE: fishery catch becomes L; a distinct external sink receives D; M0 and EE stay baseline. The adapter does not use migration as that sink. Mean-method weights see L.
- SR: fishery mortality stays H, with a separate internal return of D to a verified destination. Only Humboldt has a verified fleet-return destination. SR is explicitly unavailable for the other models.

Living production, consumption, predation, diet, accumulation and migration remain fixed after baseline completion. Detritus inflow is recomputed from mortality and egestion routed by biological fate, plus explicit SR returns. Detritus accumulation is solved as inflow minus fixed consumption/predation and external sinks. Consequently an additional return changes residual detritus accumulation; it does **not** assume all returned biomass is consumed. Fate remainders are external, and no undocumented normalization is performed.

For Humboldt, the original supplement routes both fleets 100% through Fishery offal, then offal 10% to pelagic and 90% to benthic detritus. There are no direct consumers of offal in the source diet. The loader overwrites detritus-to-detritus fate rows with identity, erasing this onward route. SR validates the raw JSON/source fate and algebraically collapses the unconsumed intermediate for solving, while `results/explicit_offal_transfers.csv` retains the donor→offal→pool ledger. No additional processing-offal quantity is invented. The designated amount is hypothetical; the source-supported original model reference is D/H `0.03996307735493703`.

`new_GE` and `new_WithEgestion` receive explicit SR donor ancestry through the private detritus equation. At positive f, SR is unavailable for `new_TE_EEfix`: its frozen direct-PP detritus scaling has no donor-return term, so pretending that a denominator change or M0 substitution represented SR would be misleading. Ulanowicz_TE is included with the exact frozen flags `TE_option='TE', global_TE=None, use_EE=False`; its detritus pools remain terminal basal sources and cycles are removed.

## Independent numerical checks and validity

Tests include the specified P=100 production fixture; a complete producer–fish–detritus web checked against independent two-equation linear algebra for SC/SM/SE/SR; a no-return-path control; conservation of each designated amount; source aliasing; source-field adapter synchronization; fixed-support failure handling; all grid/configuration identities; zero-fraction identity; SC invariance; SC/SE equivalence below the zero-catch weighting endpoint; decomposition; and invalid interpolation gaps.

Every result separates `numerical_valid`, `physical_valid`, `method_conservation_valid`, `source_validity` and `evidence_status`. Numerical convergence and biomass balance do not establish ecological correctness. The physical tolerance is `1e-4` relative per living production/consumer consumption and whole-system budget, preserving source precision, plus `1e-7` absolute for the constructed detritus budget. Original residuals and inferred accumulation remain visible.

The new solver family additionally documents the PP-equivalent export identity:

`sum(P_PP + P_Import) = sum[(catch + accumulation + net_migration) * SPPR_all]`.

The private check adds SE's external sink and subtracts internally returned SR biomass from donor external export. This is separate from the physical biomass equation (respiration is encoded in the coefficients, not added a second time). A relative discrepancy above the frozen diagnostic failure threshold of **5%** makes this method-identity check fail for new_GE/new_TE_EEfix/new_WithEgestion. Ulanowicz and trophic-chain references do not promise that same exact recycling identity, so their check is diagnostic only.

Humboldt GE and egestion already diverge in S0 and return negative source coefficients. Humboldt new_TE_EEfix is finite and its physical ledger closes, but its PP-equivalent identity fails by **14.21893%**. The frozen method's EE=0 recredit is limited to single-detritus models and does not repair Humboldt's multi-detritus dead ends. This source-pipeline failure is retained and excluded from production envelopes. Raw numeric diagnostics remain in the files; invalid totals are null, never zero.

## Findings

SC is invariant across all fractions, and SC/SE coefficients agree for all f<1 under uniform reclassification. The normalized catch weights stay identical. At f=1, SE switches TEmean to biomass weighting, creating a discontinuity; SPPR_1986 is undefined. These are weighting conventions, not smooth ecological effects.

At **50% designated discard**, fixed-H native results in all-source scope are:

| Model / method | Baseline | SM | Coefficient change |
|---|---:|---:|---:|
| Bay — new_GE | 132.9366 | 177.9501 | +33.8609% |
| Bay — new_TE_EEfix | 223.4857 | 447.5445 | +100.2564% |
| Bay — new_WithEgestion | 36.5676 | 39.2449 | +7.3215% |
| Guinea — new_GE | 127.1163 | 140.2508 | +10.3326% |
| Guinea — new_TE_EEfix | 378.2804 | 756.5413 | +99.9948% |
| Guinea — new_WithEgestion | 44.7622 | 46.4658 | +3.8058% |

Every number is t C equivalent km⁻² yr⁻¹. Retained-only PPR at f=.5 is half the SM number, and is shown separately; halving the numerator must not be confused with the coefficient response. The exact decomposition reconstructs total change with maximum residual `1.1369e-13` across reported valid cases.

The fixed baseline-TL 10% benchmark is **not always larger**. At f=.5 in Bay, its signed excess against SM new_GE is **−58.5672%**, against SM new_TE_EEfix **−83.5257%**, and against SM new_WithEgestion **+87.8706%**. Its value is 73.7297 native units and does not change with routing. No all-source standard comparison is emitted for PP-only or internal-source scopes, because the trophic-chain benchmark has no source attribution.

The separate frozen 2019 audit reproduces the earlier direct-discard PPR shares: Bay 3.31863%, Humboldt 4.77337%, Guinea 18.14469%, Okhotsk 27.67342%. Bay's frozen landings-only model1995 PPR/NPP is 42.257516%. Those external, taxon-composition-weighted shares are not source-model discard observations. They coexist with these model coefficient sensitivities but do not validate a causal screening law from four systems.

## Response interface and rerun

`results/discard_responses.v1.json` supplies group-level coefficients, exact model/source-workbook hashes, method/scope keys, fractions, routes, reasons, and permitted adjacent interpolation intervals. No interpolation crosses an invalid point or the TEmean biomass-weighting transition. Map evaluation must use the same actual landed taxon vector and frozen mapping weights for every scenario, followed by `/9`; annual NPP is fixed within each interval comparison. No pooled global proxy is provided. Zero-source-harvest Okhotsk is not assessed. Fixed-TL invariance is flagged as by construction and must not be advertised as proof of no ecological recycling uncertainty.

Run `python -X utf8 src/run_study.py`, then `python -X utf8 src/uncertainty.py`, using the existing project Python runtime; run the focused tests in this directory. The first script recomputes the numerical scenarios; the second applies method-identity validity, constructs envelopes/decomposition and publishes the versioned response file. Source and external evidence files are separate audited inputs to the report. The broad production workbook exporter is never imported or executed.

The original private run used the legacy loader's Windows text decoding, which corrupted 15 French group labels in Guinea. All numerical matrices and workbook comparisons use immutable group sequence identifiers, so numerical values were unaffected. Public group names now come from the hash-verified frozen workbook's sequence/name pairs; `engine_name_original` retains changed labels. This identity correction applies to study groups, response names and CSV name columns. `verification/group_identity_audit.json` records the unchanged numerical digest. Future numerical invocations require UTF-8 mode before loading the frozen engine.
