# Why the 1985 GE footprint is higher

The reported GE footprint is **433.7915 in 1985 versus 83.0978 in 2013: 5.220× higher**. This is principally the effect of much larger reported catches, especially sardine. It is not a general fivefold increase in per-group GE coefficients. An exact symmetric decomposition assigns **97.45% of the difference to catches and 2.55% to coefficients**.

These are model-area catch-weighted diagnostic footprints for coastal Kyoto (2,230 km²), in the source catch-density/time units, t/km²/year. They are not total LME annual PPR. Both fresh GE calls exactly reproduce the original complete direct `diagnose_sppr()` returns; their status remains WARN. No model has been selected or changed.

| Quantity | 1985 | 2013 | 1985 / 2013 |
|---|---:|---:|---:|
| Total model catch | 21.46681 | 3.999627 | 5.367× |
| GE PPR, all basal columns | 433.7915 | 83.0978 | 5.220× |
| GE PPR, inner-system columns | 362.4740 | 67.8619 | 5.341× |
| GE PPR, PP column only | 360.0269 | 65.1053 | 5.530× |
| Catch-weighted mean GE SPPR | 20.2075 | 20.7764 | 0.973× |
| Model phytoplankton production | 4162.7343 | 1801.7326 | 2.310× |
| Inner GE PPR / model production | 8.7076% | 3.7665% | 2.312× |

The mean coefficient actually goes slightly **down** when weighted by each year's own catch mix. This differs from the small positive coefficient effect obtained when holding the catch weights fixed; both statements are compatible.

## Where the extra footprint comes from

| Group | Catch 1985 → 2013 | GE SPPR 1985 → 2013 | PPR 1985 → 2013 | Contribution to 1985−2013 gap |
|---|---:|---:|---:|---:|
| Sardine | 15.764222 → 0.286000 | 20.17355 → 20.17027 | 318.02031 → 5.76870 | +312.25161 |
| Mackerel | 1.217440 → 0.054400 | 29.16684 → 17.82137 | 35.50888 → 0.96948 | +34.53939 |
| Anchovy | 1.963010 → 1.016000 | 9.23497 → 9.23347 | 18.12834 → 9.38121 | +8.74713 |
| Flying fish | 0.495020 → 0.098400 | 21.69035 → 21.68613 | 10.73716 → 2.13391 | +8.60324 |
| Barracuda | 0.359201 → 0.192210 | 41.96673 → 42.02101 | 15.07449 → 8.07686 | +6.99763 |
| All groups combined | 21.466810 → 3.999627 | — | 433.79150 → 83.09784 | +350.69366 |

Sardine alone accounts for **89.04% of the net gap**. Its catch is 55.12× higher, whereas its coefficient differs by only 0.0162%. The table's leading positive contributions can exceed the net difference because other groups offset them. All 40 source groups, plus the loader's explicit diet-import group, are retained in [the complete comparison](all_groups_comparison.csv), including unfished groups.

This large catch contrast is directly supported by the paper: Results, printed p.585 / PDF p.13, reports total catch falling from approximately 21.5 to 4.0 t/km²/year and sardine from 15.8 to 0.3. Exact values here are sums of the individual fleet cells in Supplement Table S4, rather than its rounded printed totals. Source evidence: [page 585 text](../../../papers/SOJ-2023/evidence/page_13.txt), Table 1 on printed pp.577–578, and [original supplement](../../../papers/SOJ-2023/12562_2023_1691_MOESM1_ESM-8d668bb0.docx).

## Exact attribution and parameter explanation

The calculator uses `PPR = Σ catchᵢ × SPPRᵢ`. Swapping only these already-computed arrays, without loading or adopting a hybrid model, gives:

| Catch vector | 1985 coefficients | 2013 coefficients |
|---|---:|---:|
| 1985 catches | 433.79150 | 418.48741 |
| 2013 catches | 85.67913 | 83.09784 |

Thus 1985 catches still produce a footprint of 418.49 even with 2013 coefficients. The order-independent, symmetric attribution is:

`catch effect = Σ(C85−C13)(S85+S13)/2 = 341.75097`

`coefficient effect = Σ(S85−S13)(C85+C13)/2 = 8.94269`

For living groups GE is `P/Q = (P/B)/(Q/B)`. Biomass cancels from this ratio. Diet and GE determine the living transfer matrix; changing B or EE alone does not directly rescale those living coefficients. The engine recomputes GE from P and Q, rather than using the rounded source P/Q column. Although 37 source B values and 36 EE values differ, only five living GE rows differ:

| Group | P/B, 1985 → 2013 | Q/B, 1985 → 2013 | Effect of this GE-row change on the coefficient component |
|---|---:|---:|---:|
| Mackerel | 0.66 → 1.08 | 6.14 → 6.14 | +7.34249 |
| Jack mackerel | 1.52 → 2.00 | 5.97 → 5.97 | +1.92162 |
| Bivalve | 5.00 → 3.00 | 16.67 → 10.00 | +0.00010 |
| Goby | 3.50 → 2.96 | 24.46 → 24.46 | −0.01612 |
| Zooplankton | 46.21 → 46.21 | 154.03 → 154.00 | +0.04080 |

These effects include propagation to predators. They are exact Shapley attributions across all 32 combinations of the five matrix rows, evaluated at mean catches and the mean detritus multiplier. They sum to **+9.28889**; the detritus multiplier contributes **−0.34621**, giving the total coefficient effect **+8.94269**. These are labeled algebraic explanatory checks, not balanced alternative source models.

## Basal production, detritus, and imports

Phytoplankton B falls from 64.83 to 28.06 while P/B remains 64.21/year. Consequently model production falls 2.310×. This changes the PPR/production denominator, but does not itself multiply GE SPPR by 2.310: the direct phytoplankton basal coefficient is anchored at 1 in both years.

The all-column PPR difference comprises **+294.92162 from the PP column, +56.08165 from the import column, and −0.30962 from the scaled detritus column**. These are the calculator's column conventions: “PP only” excludes both import and detritus; “inner” excludes import. They should not be interpreted as a separate tracing of the ultimate primary-production origin of every recycled unit.

For the single detritus pool, GE solves `x = c/(1−b)`. The loaded pool consumption/inflow is 2878.35138 in 1985 and 1338.79131 in 2013. Respectively, `c = 1.16849, 1.31850`, `b = 0.019185, 0.031294`, and the multiplier `x = 1.19135, 1.36109`. Detritus scaling is therefore **higher in 2013**, and does not explain the high 1985 total. Its unscaled source term is dominated by phytoplankton, sardine, and zooplankton in 1985; in 2013 zooplankton replaces sardine as the large animal contribution. [All group contributions to this calculation](detritus_flow_comparison.csv) are retained.

## Limits on choosing a year

The extracted candidates contain exactly the same published diet and import cells. However, p.585 says the authors changed diets between years, with sardine as the main prey in 1985 and anchovy in 2013. Only one complete published matrix was available. The comparison therefore rigorously explains **these extracted candidates**, but cannot establish the true difference between the authors' separate original diet networks. No year-specific diets were invented.

Both loads apply the same diet normalization, consumer GS=0.2 default, missing-catch/migration defaults, and closure of the single detritus fate. B, EE, and defaults influence mortality, egestion, and hence detritus scaling. Biomass accumulation is solved separately for each year, so a balanced loaded state does not validate the incomplete source reconstruction. These transformations are documented in each candidate's original loader audit. The common loading settings are not the main numerical reason for this GE footprint gap; the observed published catches are.

Selecting 2013 simply because its footprint is lower would confuse a historical catch change with model suitability. Year selection remains pending; the intended reference period and unresolved source-diet uncertainty remain material considerations.

## Reproducibility

[COMPARISON.json](COMPARISON.json) retains all catch/coefficient and basal-factor counterfactual values; [DECOMPOSITION.json](DECOMPOSITION.json) retains the attribution and checks. [All changed source parameters](all_changed_source_parameters.csv) preserve the exact source strings. The `1985/` and `2013/` folders retain direct GE returns, SPPR/A/L, complete loaded group tables, unscaled bases, detritus flow contributions, source-identical canonical copies, and hashes. Both numeric basal solves reproduce the direct method outputs to 1e−11. Canonical models, production selection, and central workbooks were not changed.
