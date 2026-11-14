# Native Rpath balance and PPR diagnostic interpretation

This interpretation uses only saved native R outputs, saved diagnostic returns and saved runtime states. It performs arithmetic reconciliation; it does not rerun the scientific engine, change model inputs, or calculate annual LME PPR. The native Rpath reproduction succeeded. All three maintained PPR formulations returned and reproduced after persisted-input reload, but all three diagnostics remain **FAIL**.

## Native balance versus effective PPR runtime

The native Rpath result reconciles its living equations and its detritus equations. The PPR initializer then forces detritus EE to 1 and M0 to 0, reconstructs p=q from routed natural input plus internal fleet-discard returns, and retains the known native biomass accumulation of zero. It does not represent the native unused detritus input as an explicit sink. Both retained detritus stock residuals are positive; they are not negative-stock warnings. No missing-flow repair was made.

| Pool | Native input | Native consumption | Native EE | Native unused input | Runtime EE | Runtime stock residual |
|---|---:|---:|---:|---:|---:|---:|
| Pelagic detritus | 1989.927196990858 | 383.423551536085 | 0.1926822006935194 | 1606.503645454774 | 1 | 1606.503645454773 |
| Benthic detritus | 2067.650082583794 | 1067.841140090477 | 0.516451574221917 | 999.8089424933171 | 1 | 999.8089424933166 |

Flows are t/km²/year in the native Ecopath model mass basis. Native unused input is input minus consumption. It has not been relabeled as biomass accumulation or migration. Native zero residual in its detritus audit refers to reproduction of its own balance equations, not to unused input being zero.

The retained 47 living/PP groups close to floating precision in the effective PPR runtime. Maximum absolute production and consumption residuals are each 9.094947017729282e-13 (Primary production). Maximum relative production residual is 4.364680104024699e-16 (Walleye pollock); maximum relative consumption residual is 2.076298991748194e-16 (Eelpouts). Detritus alone supplies the runtime maximum relative residual of 0.8073177993064805. The effective EE-range checks pass, but these checks see the forced DET EE=1 and do not establish detritus accounting closure.

The source parent has all 49 EE entries unknown. The adapter preserves that missingness for the project-default floor (ON, threshold=0.1, floor=0.1). All 47 living groups are ineligible because their original EE is unknown; no floor is applied and no physical flows change. Native-solved EE values are preserved separately from original source EE provenance.

## Actual PP budgets and exact decomposition

The actual diagnostic call checks the original effective runtime object. It does not check or adopt the constructor’s internally prepared balanced copy. No forced-copy diagnostic was executed or saved.

```text
I = sum(p for PP and Import groups)
O = sum((external catch + growth + net migration + floor sink) * total SPPR)
    + formulation-specific unrouted export
signed residual = O - I
relative gap = abs(O - I) / abs(I)
U_d = native total detritus input_d - native consumption_d
I - O = sum_d(SPPR_d * U_d) + numerical remainder
```

Unrouted exports are evaluated using the actual formulation: GE counts unrouted mortality at group SPPR; TE counts basal PP/Import mortality without double-counting consumer mortality; With Egestion also counts egestion at diet-weighted SPPR. The arithmetic decomposition below retains the actual reported totals, including negative GE and With Egestion outflows. It does not reinterpret those negative budgets as valid estimates.

| Method | Actual inflow I | Actual outflow O | Signed O−I | Relative gap |
|---|---:|---:|---:|---:|
| GE | 4451.953547222999 | -26.22603946696475 | -4478.179586689964 | 100.5890905911029% |
| TE | 4451.953547222999 | 1083.206401978454 | -3368.747145244545 | 75.66896441104767% |
| WithEgestion | 4451.953547222999 | -19.42768410430258 | -4471.381231327302 | 100.4363855978781% |

| Method | Pelagic SPPR | Benthic SPPR | SPPR-weighted unused native detritus | (I−O) minus that sum |
|---|---:|---:|---:|---:|
| GE | 1.644011930486874 | 1.837419479976238 | 4478.179586689967 | -2.728484105318785e-12 |
| TE | 1.216719179866512 | 1.414353570161024 | 3368.747145244634 | -8.913048077374697e-11 |
| WithEgestion | 1.59780366129689 | 1.904867764018421 | 4471.381231327305 | -2.728484105318785e-12 |

The weighted unused-detritus totals account for each actual PP-budget gap to floating precision. Adding them arithmetically to the reported outflow recovers the PP inflow of 4451.953547222999; this is a decomposition, **not a forced-balance diagnostic or an approved repair**. It identifies the common accounting mismatch in these runs. It does not remove the method-specific warnings below or establish that another formulation/translation would pass without being tested.

## Grades, strict flags and numerical behavior

| Method | Overall | Model input | Divergence | PP balance | Strict model balance | Strict PP balance | b | Living spectral radius |
|---|---|---|---|---|---|---|---:|---:|
| GE | FAIL | FAIL | WARN | FAIL | False | False | 0.4090673647283584 | 0.26659952990268 |
| TE | FAIL | FAIL | WARN | FAIL | False | False | 0.2672886407947974 | 0.9766894020612613 |
| WithEgestion | FAIL | FAIL | OK | FAIL | False | False | 0.4406459221547789 | 0.213279623922144 |

Here b is the spectral radius of diag(theta)·B, the method-specific detritus recycling matrix, with theta=1. Living spectral radius is rho(A_LL), with A=DC/TE and Regular groups forming the living block. Both are below 1 for all three methods; those convergence conditions are necessary but do not prove PP budget closure. TE has nonzero b here because the complete native fleet-discard return matrix creates a coupled recycling system. The engine’s TE b=0 convention applies only when no discard returns exist.

Near-zero effective transfer efficiencies are defined by the diagnostic as 0 < |TE| < 0.001. These warnings concern the formulation’s efficiency matrix, not source-EE floor eligibility:

- GE: 9 Other seabirds, 5 Procellarids.
- TE: 39 Sponge, 35 Anemones, 10 Cormorants, 9 Other seabirds, 8 Alcids planktivorous, 7 Larids, 6 Alcids piscivorous, 5 Procellarids, 4 Other pinnipeds, 3 Other baleen, 2 Gray whale, 1 Toothed whales.
- WithEgestion: none.

TE is especially sensitive: its living spectral radius is 0.9766894020612613 and its largest group coefficient is 852777853.9355636 for Toothed whales. GE also has near-zero-efficiency warnings. With Egestion has divergence grade OK and no near-zero-efficiency warning, while retaining both accounting FAILs. No method returned a solver error or negative SPPR source contribution. Expected negative equation-matrix coefficients are recorded separately from negative SPPR values in the full receipts.

## Failed native-catch footprint snapshots

The following values were returned by the failed diagnostics using native model catch density (total catch 1.4381429207 t/km²/year). They are reproducible diagnostic snapshots, **not accepted annual LME_002 PPR estimates**, and should not be ranked as policy-ready estimates. No regional area multiplication, catch mapping, carbon conversion or map update was performed.

| Method | PPR all | PPR inner | PPR PP-only | NPP | PPR all/NPP | PPR PP-only/NPP |
|---|---:|---:|---:|---:|---:|---:|
| GE | 450.3074747660822 | 450.3074747660822 | 151.2423365726364 | 4451.953547222999 | 0.1011482869238317 | 0.03397212818336278 |
| TE | 3828.811631806325 | 3828.811631806326 | 1599.366848906957 | 4451.953547222999 | 0.8600295558327711 | 0.3592505698772611 |
| WithEgestion | 159.2095989436187 | 159.2095989436187 | 59.21197512596122 | 4451.953547222999 | 0.03576173858393673 | 0.01330022303644564 |

The aggregate Primary production includes Outside production, and Pelagic detritus mixes internal and external source pools. The engine’s inner scope drops Import columns; PP-only drops detrital source contributions. Neither operation reconstructs the lost geographic partition. The explicit diet-import group contributes zero, explaining why all and inner agree to floating precision. This is not proof that all modeled support is local to the Gulf of Alaska. The source shelf domain is 291,840 km² for 1990–1994; it has not been established as a complete LME_002 boundary.

## Reproducibility and next limitation

All three initial and reload calls returned, all lossless four-part returns match at atol=rtol=1e-12, and the constructor state also reproduced. No method mutated its input state. Source/variant hashes and executed-code copies are retained by the run. Full matrices, missing-value masks, source contributions, coefficients, transformation ledgers and diagnostic reports remain in the model’s retained results/diagnostics directory.

The next scientific issue is a documented, reviewed representation of the native unused detritus flow in the PPR translation. Automatically changing EE, biomass accumulation or migration would change the calculation and requires a distinct explicit treatment, not a silent repair. GE/TE efficiency sensitivity remains an independent concern even if that translation is resolved. This run supplies evidence for that decision and does not approve any formulation for annual LME estimation.

Evidence: diagnostic_budget_decomposition.json contains the saved-output hashes, all per-group residuals, exact native/runtime detritus quantities, method warnings, component grades, strict flags and numerical decomposition. The executed PPRCalculator.py snapshot documents initializer DET defaults (around lines 827–828, 928–945), balance identities (1180–1201), PP budget (1272–1340), convergence definitions (1433–1446), TE discard behavior (1710–1728, 3252–3257), and the actual diagnostic balance call (1855–1869).
