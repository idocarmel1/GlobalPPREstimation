# Default SPPR parameters

SPPR is the production required from basal sources per unit of a group's production. This note distinguishes **function API defaults**, **exporter settings**, and **the project's ordinary direct-validation scope**. It describes the current shared engine; regional departures belong in the relevant region's own explainer.

Sources: [calculator implementation](../tools/scientific_code/PPREstimation/PPRCalculator.py), [exporter implementation](../tools/scientific_code/PPREstimation/create_PPRS_excel.py), [User Guide](PPREstimation/USER_GUIDE.md), and [SPPR Methods](PPREstimation/SPPR_Methods.md). The implementations govern exact defaults.

## Direct validation and the primary solver

The [direct-diagnostics contract](../tools/skills/original_skill_resources/combined-src/references/direct-diagnostics.md) defaults to full `diagnose_sppr()` returns for **GE, TE and With Egestion**. Global, broad method inventories and Monte Carlo require a broader request. Use the already-audited computational input and constructor/settings; stock defaults are not permission to alter a regional reconstruction.

| `SPPR_new` parameter | API default | Meaning |
|---|---|---|
| `TE` | `None` | Build the efficiency matrix from `TE_option`; an explicit matrix replaces that step. |
| `TE_option` | `'GE'` | GE: `p/q`; TE: `(p/q)·(1−M0/p)`; With Egestion: `p/(q−egestion)`. This also selects detritus equations. |
| `DET_TE_vals` | `1` | Efficiency assigned to detritus rows when building the matrix. |
| `det_collapse_mode` | `'never'` | Solve separate coupled detritus pools; no automatic pooling. Alternatives: `'auto'`, `'always'`. |
| `det_open_mode` | `'none'` | Closed recycling. Alternatives: `'recycling_loss'`, `'source_dilution'`. |
| `det_theta` | `1.0` | Detritus retention/availability; scalar or dictionary by pool sequence/name. It does not damp recycling gain under `'none'`; TE uses it as a scaling factor. |
| `det_external_sppr` | `0.0` | External source coefficient for `'source_dilution'`. |
| `fix_EE_0_cases` | `True` | Re-credit consumed source burden to detritus for zero-TE/EE=0 dead ends, **only in single-detritus TE models**. |

The EE-zero flag changes SPPR accounting; it does **not** repair input EE, fix small positive EE, or extend that correction to multiple detritus pools. GE/With Egestion use coupled recycling equations; TE uses direct PP/import ancestry. Diet fractions are not renormalized by `SPPR_new`.

`diagnose_sppr` defaults to `TE_option='GE'`, `short=False`, `flat=False`, `thresholds=None`, `return_sppr=False`; solver keywords pass through to `SPPR_new`. `short=True` drops configuration, footprint and warnings; `flat=True` flattens sections and replaces lists with counts. `return_sppr=True` returns `(report, SPPR, A, L)` from the internal solve, avoiding another calculation.

```python
# calculator has already been constructed with the audited regional settings.
for option in ("GE", "TE", "With Egestion"):
    report, sppr, A, L = calculator.diagnose_sppr(
        TE_option=option, short=False, flat=False, return_sppr=True,
        det_collapse_mode="never", det_open_mode="none",
        det_theta=1.0, det_external_sppr=0.0,
    )
    # Retain the full return and configuration; handle each option independently.
```

Default diagnostic thresholds (override individual keys with `thresholds={...}`):

| Quantity | Default keys and values |
|---|---|
| Detritus recycling gain | `b_warn=0.7`, `b_fail=1.0` |
| Living-network gain | `rho_living_warn=0.7`, `rho_living_fail=1.0` |
| Detritus SPPR | `sppr_det_warn=10.0` |
| Relative PP-budget gap | `balance_warn=0.01`, `balance_fail=0.05` |
| Relative input mass-balance residual | `model_balance_warn=1e-4`, `model_balance_fail=0.1` |
| Diet-row deviation / marginal EE | `dc_row_tol=1e-6`, `ee_marginal=1e-3` |

A diagnostic grades the **configuration**. Overall status is the worst component grade; input balance, SPPR budget closure and convergence are distinct. Returned grades are also distinct from execution exceptions, timeouts and NOT_RUN.

## Other methods and exporter choices

The broad exporter uses the following variants. Its health rows retain the three direct options and explicitly pin the closed, separate-pool detritus settings above.

| Method | API defaults | Exporter choices |
|---|---|---|
| `SPPR_1986()` | No arguments; fixed TE `0.1`, one catch-weighted TL; same coefficient for every group. | Same. |
| `SPPR_1995` / `SPPR_1995_TL_fix` | `global_TE=0.1`, `weights='consumption'`. TL-fix interpolates between integer TL coefficients. Both calculate TL with cycles broken and detritus at TL 1. | 1995 at `0.1`, plus `'mean'` with consumption and catch weights; TL-fix is not registered. |
| `SPPR_EwE` | Required `TE_option`; `use_EE=True`, `return_paths=True`, `silent=True`, `max_paths=1_000_000`. | TE with/without EE row weighting; both cap paths at `100_000`; no-EE uses `return_paths=False`. |
| `SPPR_EwE_Ulanowicz` | Required `TE_option`; `global_TE='mean'`, `use_EE=True`, `weights='consumption'`. | `use_EE=False`; group TE plus global consumption/catch means. |
| `SPPR_2015()` | No arguments; production/EE-based matrix inversion with detritus reassignment. | Bare call; no `only_pp_det` argument. |
| `SPPR_new` | Defaults above. | GE, With Egestion, and TE with EE-zero re-credit both disabled/enabled. |
| `SPPR_symbolic` | Same efficiency/detritus defaults; `diet_import_option='as_DC'`, `sppr_det_value=None`, `fix_EE_0_cases=True`. | All three direct options with both `as_PP` and `as_DC`. |

Symbolic `as_DC` keeps imported diet as a source with its own diet-derived SPPR; `as_PP` treats it as an extra primary-production source. `sppr_det_value` fixes detritus scaling instead of solving it. The symbolic EE-zero correction applies only to the single-pool `as_PP` TE branch. Matching parameter names do not guarantee matching equations or configurations across methods or audited regional adapters.

Global `'mean'` is an arithmetic consumer-only TE mean, defaulting to total-consumption weights. Catch weights fall back to consumer biomass if consumer catch totals zero; `'equal'` and `'biomass'` are also supported. These are model weights, not annually changing catch weights. `get_TE` defaults to `global_TE='mean'`. Although its docstring advertises `'global'`, **`SPPR_new` currently rejects it in the executable detritus branch**; use the supported global methods above. It exposes no `global_TE`/`weights` keyword.

## Monte Carlo and output scopes

`monte_carlo_SPPR` defaults to **1,000 draws**, gamma TE uncertainty with **10% relative standard deviation**, clipped at **±20%**, `kind='new'`, `TE_option='GE'`, `exclude_diverged=False`, `return_diagnostics=False`, `method_kwargs=None`, `diet_import_option='as_DC'`, and `silent=True`; detritus knobs retain the defaults above. Negative-SPPR draws are rejected. The exporter uses **100 draws**, GE and TE-with-re-credit, and overrides `exclude_diverged=True`, `return_diagnostics=True`. Divergence FAIL draws are screened as well; screening does not require every diagnostic component to pass.

`method_kwargs` passes solver-specific flags, e.g. `{'fix_EE_0_cases': False}` or `{'fix_EE_0_cases': True}`. Wrapper-controlled efficiency, import and detritus options use their dedicated arguments; duplicate wrapper-owned keys or unknown solver keys raise errors.

The exporter allows 180 seconds per method/health row by default. A timeout leaves unavailable values, not zeros.

`all`, `inner` and `PP` are **post-solve source-column sums**, not separate solver runs: all sources; all except Import; all except Import and Detritus. Unattributed classic coefficients cannot be split into PP-only values (exporter: NaN). `SPPR_2015` resolves no detritus source column, so its inner and PP sums coincide.
