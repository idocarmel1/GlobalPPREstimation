# TE comparison: definitions and limitations

This read-only analysis uses the ten default model identities in `data/atlas_selection.json`, the saved `groups_df` and underlying model health in `PPREstimation/output/top10`, and normalized source diets from `PPREstimation/real_models/global_cover_jsons`. No model coefficients, source records, atlas outputs, or production algorithms were changed. Each input file's SHA-256 is recorded in results.json.

## Eligibility

Canary Current's Banc d'Arguin/Mauritanian Shelf 1991 model fails the underlying Ecopath production/consumption balance and is excluded from every mean. The other nine pass the saved check and an independent reconstruction of the same mass-balance identities. Predation reconstructed from normalized source diets and saved consumption agrees with saved predation. No new balancing was performed.

This gate concerns the underlying Ecopath model, not the separate SPPR balance/divergence diagnostics. Passing this gate does not endorse every SPPR configuration. The saved parameters can include inferred biomass accumulation; the calculation does not impose stationarity. Eastern Tropical Pacific, Humboldt and South China Sea source diets were normalized by the production loader. ETP corrections are substantial (one source row sums to 0.425, another to 1.575); its numerical balance after normalization does not validate the source diet scientifically. Exact warnings are preserved in results.json.

## Consumer means

Consumers are exactly groups classified `Regular`. Primary producers, detritus and the synthetic imported-diet group are excluded from both numerator and denominator. Genuine consumer TE=0 entries are retained.

For group i, the project definition is `TE_i = (P_i/Q_i) * EE_i`, reproduced with the existing `get_TE` NaN rules and checked against saved GE times EE. The three means are:

- Equal weights: `sum(TE_i) / number_of_consumers`.
- Catch weights: `sum(C_i * TE_i) / sum(C_i)`.
- Biomass weights: `sum(B_i * TE_i) / sum(B_i)`.

Catch means use the original model catch, not a chosen year of Sea Around Us catches. East China Sea and Okhotsk contain no model catch in the saved inputs, so their catch-weighted means are undefined. Zero here describes the available input, not a claim that these ecosystems were unfished. No biomass fallback is silently substituted.

The Gulf of Thailand model is the 1980 payload despite its inherited 1963 filename. Geography follows the selected model: e.g. Karnataka is not the entire Arabian Sea, and the Guinea model is not the whole Guinea Current LME.

## Trophic aggregation

This is a reconstruction, not an output exported by an installed EwE executable. The reference is the [official EwE network-analysis implementation](https://github.com/Official-EwE/Eii.Ecopath/blob/master/Sources/EwECustomPlugins/EwENetworkAnalysis/NetworkAnalysis/cEcoNetwork.vb), read on 11 September 2026, especially `Lindeman`, together with `TotTransferEfficiency` in [cNetworkManager](https://github.com/Official-EwE/Eii.Ecopath/blob/master/Sources/EwECustomPlugins/EwENetworkAnalysis/NetworkAnalysis/cNetworkManager.vb) and `UpdateExportCatch` in [cEcoPathModel](https://github.com/Official-EwE/Eii.Ecopath/blob/master/Sources/EwECore/EcoPath/Model/cEcoPathModel.vb).

Groups are distributed fractionally among integer trophic levels by powers of the predator-by-prey diet matrix. Producers and detritus are level-I sources, not consumer observations. The primary-producer and detrital pathways are combined. Imported food follows the reference implementation's renormalization over internally traced source fractions; it is not treated as another consumer or assigned a fabricated TE. The reference small-path cutoff and stopping criterion are reproduced, in double precision. An independent full-series calculation verifies that this truncation changes level efficiencies by less than 0.000014 percentage points in this dataset.

For level l the reconstructed reference formula is:

`TE_l = sum_i a_li * (predation_i + catch_i) / sum_i a_li * H_i`

where `H_i = predation_i + catch_i + net_migration_i + flow_to_detritus_i + respiration_i`.

This precise code formula uses catches in the numerator. The manual describes it more generally as exports plus onward transfer divided by throughput. Net migration is zero in the selected consumer data, so that wording difference does not alter these results. Biomass accumulation is not an export in this reference calculation. Consequently, even in a balanced model, `H_i` need not equal `Q_i`: it equals `Q_i - biomass_accumulation_i`. Nor is the group-level `P_i*EE_i` necessarily equal to predation plus catch.

The reported geometric summary is `(TE_II * TE_III * TE_IV)^(1/3)`, as used by EwE for its II–IV summary. Arithmetic summaries `(TE_II + TE_III + TE_IV)/3` and the individual level values are also retained. The [Pauly and Christensen 1995 paper](https://www.seaaroundus.org/wp-content/uploads/2015/04/PrimaryProductionRequiredToSustainGlobalFisheries.pdf) reports an arithmetic mean of 140 level-II–IV estimates from 48 models, 10.13%; that is a different sample-level statistic, not a requirement that these nine ecosystems average 10%. This analysis does not claim to reproduce the historical Ecopath executable.

Two cycle conventions are shown because the choice materially affects results:

1. **Cycles retained:** reproduces the official EwE source setting `CalcPathsAndCycles=False`, whose default is false in the plugin's [Settings.settings](https://github.com/Official-EwE/Eii.Ecopath/blob/master/Sources/EwECustomPlugins/EwENetworkAnalysis/My%20Project/Settings.settings). Consumption around a feeding cycle contributes to the level flows.
2. **Cycles removed, project convention:** applies the existing PPRCalculator helper `remove_cycles(..., new=False)` to the consumption-flow matrix before rebuilding diets, matching the cycle-removal convention used for the project's 1995 SPPR trophic levels. Predation and throughput are recalculated from the remaining flows. This is a sensitivity variant; the project's deterministic minimum-flow removal is not asserted to be identical to EwE's optional cycle-removal routine. It preserves external balance by removing equal incoming and outgoing circulation at each affected group. Source group TE values used in the first three columns remain unchanged.

Thus a trophic result should always state its cycle convention and whether the II–IV summary is arithmetic or geometric. Neither averaging convention should be selected solely because it produces a value near 10%.

### Exact project cycle-removal procedure

1. Build the consumption-flow matrix `Z[i,j] = Q_i * DC[i,j]`, where i is the consumer and j is its prey. These are amounts of food per area per time, not bare diet percentages. Rows for primary producers, detritus and imported diet have no feeding flows.
2. Search positive links by depth-first traversal and take the first directed cycle found, including a group's self-feeding link when present. The project's matrix order is retained (descending group sequence).
3. For that cycle, compute `m = min(Z[i,j])` over its links.
4. Subtract m from every link in the cycle. At least one link becomes zero, breaking that cycle. The implementation sets residual entries below 1e-20 to zero.
5. Repeat the search and subtraction until no directed cycles remain.
6. Normalize each remaining consumer row to obtain its new diet proportions. Use the remaining consumption and predation flows to rebuild throughput and the trophic-level decomposition. Catch, respiration and flow to detritus stay at their original values for this circulation-removal calculation.

For example, a three-link loop with flows 5, 3 and 4 becomes 2, 0 and 1 after subtracting 3 from every link. Each participating group loses the same amount of incoming and outgoing circulation, preserving its net external flow balance. The study verifies this conservation and checks that the final graph is acyclic.

With overlapping cycles, selecting a different cycle first can leave a different acyclic network. The method is deterministic for the stored group order, but is not order-independent, and is not the alternative probability-weighted nexus algorithm also present in utils.py. Cycle removal here separates circulation for network accounting; it is not a biological simulation of eliminating cannibalism or interactions from the ecosystem. It does not rebalance or overwrite the saved model.

## Verification

`compare.py` checks a hand-solvable three-transfer 10% food chain, an omnivore with 40/60% level-II/III contributions, zero-catch handling, saved production and consumption identities, source-to-saved predation agreement, GE-times-EE equivalence, and small-path truncation against an independent matrix solution. It also checks that project cycle removal leaves a nonnegative acyclic network and removes equal inflow and outflow per group.

Run: `python research/te_mean_comparison_2026_09_11/compare.py` using a runtime with numpy, pandas, openpyxl, sympy and networkx. It writes only this study's results.json and results.md.
