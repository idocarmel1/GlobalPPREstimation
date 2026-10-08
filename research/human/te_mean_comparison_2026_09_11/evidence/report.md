# Consumer transfer-efficiency comparison

11 September 2026

Nine of the ten default pilot models pass the underlying Ecopath mass-balance checks. Canary Current's Banc d'Arguin/Mauritanian Shelf model fails and is excluded. No models were rebalanced or production outputs changed for this analysis.

All values below are percentages. The first three columns average consumer-group TE, excluding primary producers, detritus and the imported-diet pseudo-group. The last two columns aggregate food flows by integer trophic level and take the geometric mean of the level-II, III and IV efficiencies.

| Ecosystem and selected model period | Equal weights | Catch weights | Biomass weights | Trophic: cycles removed | Trophic: cycles retained |
|---|---:|---:|---:|---:|---:|
| Eastern tropical Pacific, 1993–1997* | 7.67 | 5.25 | 19.38 | 18.76 | 20.37 |
| Northern Humboldt, 1995–1998 | 10.87 | 10.29 | 16.70 | 12.11 | 21.32 |
| Canary Current, 1991 | Excluded | Excluded | Excluded | Excluded | Excluded |
| Guinea, 1998 | 9.85 | 12.18 | 8.02 | 10.29 | 11.42 |
| Arabian Sea / Karnataka, 2000 | 19.81 | 20.48 | 9.32 | 13.37 | 13.94 |
| Bay of Bengal, 1978 | 16.84 | 19.29 | 13.54 | 13.39 | 16.68 |
| Gulf of Thailand, 1980 payload | 18.95 | 22.57 | 14.00 | 11.68 | 14.10 |
| Northern South China Sea, 2000s | 15.21 | 18.59 | 12.78 | 9.96 | 11.01 |
| East China Sea, 2018 | 18.99 | Unavailable | 13.24 | 8.30 | 11.25 |
| Sea of Okhotsk, 1980 detailed model | 9.58 | Unavailable | 21.29 | 11.53 | 20.97 |

Catch weights are the original Ecopath model catches, not a selected year of global catches. East China Sea and Okhotsk have zero catch in the available saved inputs, so their catch means are undefined; no biomass fallback was substituted.

*Eastern tropical Pacific is balanced in the saved calculation after substantial diet normalization. Its raw source diet has unresolved consistency concerns. Passing numerical balance is not independent scientific validation of that source. Humboldt and South China Sea also have diet-normalization warnings; see the detailed audit.

## What is being averaged?

For a consumer group, `TE_i = (P_i / Q_i) × EE_i`. Equal weighting averages these values directly; catch and biomass weighting use `sum(weight_i × TE_i) / sum(weight_i)` over the same consumer set.

For trophic aggregation, a consumer can contribute to more than one integer trophic level according to its diet. Flows from primary producers and detritus provide the basal sources. At each level, the calculation divides onward predation plus catch by the corresponding throughput; the ecosystem summary is `(TE_II × TE_III × TE_IV)^(1/3)`. This follows the [EwE network-analysis framework](https://pressbooks.bccampus.ca/ewemodel/chapter/network-analysis/), with exact implementation choices documented in methodology.md.

The cycles-retained column reconstructs the current official EwE code with its default cycle/pathway calculation disabled. The cycles-removed column uses the project's existing cycle-removal helper, as used in its SPPR trophic-level calculation. This helper is not claimed to reproduce EwE's optional cycle algorithm exactly. Both columns are reconstructions from the saved model parameters, not results exported from an EwE executable.

The historical 10.13% reported by [Pauly and Christensen (1995)](https://www.seaaroundus.org/wp-content/uploads/2015/04/PrimaryProductionRequiredToSustainGlobalFisheries.pdf) is an arithmetic mean of 140 trophic-level estimates from 48 models. For comparison, the arithmetic mean of our 27 level-II–IV estimates is 12.71% with project cycle removal, versus 15.93% with cycles retained. These are a different sample and implementation; the historical value is not a calibration target. Individual arithmetic summaries are provided in results.md and results.json.

## How cycles were removed

The calculation uses the existing `remove_cycles(..., new=False)` implementation in PPREstimation/utils.py:

1. Convert diets to actual consumption flows: `Z[i,j] = Q_i × DC[i,j]` for consumer i eating prey j.
2. Find the first directed feeding loop using depth-first search in the stored group order. Self-feeding links are included.
3. Find the smallest flow along that loop and subtract that amount from every link in it. At least one link becomes zero and breaks the loop.
4. Repeat until no loops remain, then normalize remaining consumer flows into diets and recalculate predation, throughput and trophic-level fractions.

For example, loop flows of 5, 3 and 4 become 2, 0 and 1. Removing the same circulating amount from each link removes equal inflow and outflow from every participating group, preserving net external flow balance. The calculation verified this conservation and that the remaining network is acyclic.

When loops overlap, removal order can affect the result. The calculation preserves the project's current group order, so it is reproducible, but not order-independent. This is an accounting decomposition of circulation, not a simulation of an ecosystem after removing biological interactions. The original model and the first three TE means remain unchanged.

## Interpretation

For Arabian Sea, consumer-only equal and catch weighting remain close to 20%, whereas biomass weighting gives 9.32%. Thus excluding basal groups does not by itself bring the catch-weighted value toward 10%; the choice of weights matters. Trophic aggregation gives 13.37–13.94% under the two cycle conventions.

There is no universal direction to the weighting effect: Okhotsk's biomass mean is 21.29%, but its equal-weight mean is 9.58%. Cycle handling is particularly consequential for Humboldt and Okhotsk, where retaining recycled feeding raises the aggregated estimate substantially. A TE comparison therefore needs to specify both the quantity averaged and how circulation is treated.

For full definitions, model caveats and verification, see methodology.md. Exact values, level-specific flows, input hashes and normalization warnings are in results.json. The reproducible analysis is compare.py.
