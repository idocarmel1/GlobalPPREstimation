# Consumer mean TE: catch and consumption variants

Both the map and annual graphs expose four model methods. The original IDs
`SPPR_1995_TEmean` and `Ulanowicz_globalTEmean` now use consumption weights;
`SPPR_1995_TEmean_catch` and `Ulanowicz_globalTEmean_catch` use catch weights.
The selectors spell out the weighting. The exported method registry contains
22 methods, including these four.

## Definition

For Regular consumers, the calculator retains its group-level definition
`TE_i = (P_i / Q_i) * (1 - M0_i / P_i)` and computes
`mean_TE = sum(w_i * TE_i) / sum(w_i)` over positive weights. Zero-TE consumers
remain included. Producers, detritus and import groups do not enter the mean.
Consumption weights are total consumption `Q`, not `Q/B`. Catch weights use
the model's catch vector, with consumer biomass as the fallback when total
consumer catch is zero. These model weights remain fixed across catch years
and across the landings, all-catch and discard display choices.

`get_TE(..., weights='consumption')` is the default. Explicit alternatives are
`catch`, `biomass` and `equal`. `SPPR_1995`, `SPPR_1995_TL_fix` and
`SPPR_EwE_Ulanowicz` forward the flag. Literal global TE and group-specific
TE/GE modes retain their existing behavior. Both exported Ulanowicz mean
variants retain `use_EE=False`.

## Recalculated means

All numbers below are arithmetic means, in percent. An asterisk means the catch
column uses consumer biomass because the saved model contains no consumer catch.

| Model | Consumption | Catch |
|---|---:|---:|
| Eastern tropical Pacific, 1993–1997 | 22.49 | 5.25 |
| Chilean Patagonia, 1980 | 25.68 | 12.52 |
| Northern Humboldt, 1995–1998 | 24.15 | 10.29 |
| Guinea, 1998 | 10.17 | 12.18 |
| Arabian Sea, 2000 | 16.07 | 20.48 |
| Bay of Bengal, 1978 | 11.83 | 19.29 |
| Gulf of Thailand, saved file labelled 1963 | 15.34 | 22.57 |
| Northern South China Sea, 2000s | 6.69 | 18.59 |
| Northern South China Sea, 1970s | 1.80 | 13.44 |
| East China Sea, 1997 | 9.51 | 12.02* |
| East China Sea, 2018 | 8.36 | 13.24* |
| Sea of Okhotsk NE, 1980 | 21.73 | 21.29* |
| Sea of Okhotsk SD, 1980 | 19.42 | 19.13* |

The Arabian Sea difference is therefore reproducible under two explicitly
different weightings. Comparing the fixed-10% method against either mean also
depends on the full distribution of model trophic levels and catch allocations;
using TL=3 for every taxon is only an approximation. Changing the selected
baseline changes normalized curves even when their absolute numerator is unchanged.

## Cycle removal

The existing `remove_cycles(..., new=False)` implementation finds a directed
cycle by depth-first search, finds its smallest positive edge, and subtracts
that amount from every edge in the cycle. Values below `1e-20` become zero.
It repeats until no directed cycles remain; self-loops are removed as well.
The traversal follows matrix order, so this is an order-dependent decomposition.

The two method families apply this procedure differently:

- `SPPR_1995` obtains TL with `get_TL(break_cycles=True, DET_as_PP=True)`.
  Cycle subtraction acts on the flow matrix `Z`; the residual rows are normalized
  into diets before solving `TL = (I - DC)^(-1) * 1`. Detritus is basal.
- `SPPR_EwE_Ulanowicz` applies cycle subtraction to a copy of the diet matrix.
  It then uses only the resulting zero-edge mask on the original diet matrix:
  surviving original diet proportions are retained, without renormalization.
  The pruned diet matrix divided by TE enters its nullspace calculation.

This refresh changes neither cycle-removal behavior nor the model parameters.
These pruned calculations are not the full sum of repeated recycling paths.

## Refresh scope and evidence

Thirteen balanced source workbooks were refreshed using their saved solved
parameters. The reconstructed models passed `is_model_balanced`, and their
fixed-10% SPPR reproduced the saved coefficients. No balancing, Monte Carlo
sampling or unrelated method calculations were rerun. The three unbalanced
source models were excluded: Northwest Africa 1987, Banc d'Arguin / Mauritanian
Shelf 1991, and Guinea 1985. Ten mapped workbooks supply verified atlas results;
other balanced source models remain available in source downloads only.

The refresh checks every non-mean cell against the immutable pre-refresh source
workbook, and the graph verification compares all non-mean numerical outputs
against the pre-refresh map and time-series payloads. Catch, NPP, group metadata
and unaffected discard responses must remain exactly equal.

The frozen discard study remains unchanged. `data/discard_responses.current.json`
derives a live package from it, verifies the original study hashes, and updates
workbook hashes only after proving non-mean cells unchanged. Changed mean methods
are removed from that package; no new discard sensitivity is claimed for them.

Machine-readable evidence:

- `data/mean_te_refresh_2026_09_11.json`: per-model means, exclusions, hashes and cell checks.
- `data/mean_te_graph_verification_2026_09_11.json`: before/after graph comparisons.
- `data/time_series_validation.json`: annual arithmetic and source verification.

The targeted calculator/exporter/discard tests passed (82 tests), the additional
workbook/scope/time-series export tests passed (28 tests), and the targeted
JavaScript graph/map/group/discard tests passed (57 tests).

Independent review identified a mixed-sign catch validation edge case. The
fallback now requires every consumer catch weight to be zero; negative weights
cannot cancel positive weights and bypass validation. The added regression and
calculator/registry checks passed (27 tests). No refreshed model has negative
consumer catch, so this guard changes none of the generated results.

The dated refresh and graph verification helpers require the immutable snapshots
under `tmp/mean_te_refresh_2026_09_11`. Those local backups are intentionally not
versioned. For a fresh checkout, recover the pre-refresh inputs from the parent
commit into that directory before running this historical comparison. The
committed audits preserve the original and regenerated hashes.

Both graph comparisons passed: all protected values are exactly unchanged and
all ten verified models contain all four mean variants. The annual build checked
50,308 simple source values, 36,680 model annual values and 26 source hashes.
Browser checks confirmed the map selectors and the four-curve Arabian Sea graph,
including baseline normalization and readable weighting labels.
