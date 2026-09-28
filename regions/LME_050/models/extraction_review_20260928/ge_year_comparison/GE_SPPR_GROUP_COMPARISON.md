# GE SPPR reliability: 1985 versus 2013

**Recommendation: do not prefer either year on GE numerical reliability alone.** Both produce entirely finite, nonnegative coefficients and stable living and detritus calculations. The 1985 all-source maximum is slightly lower, while the 2013 PP-only maximum is slightly lower. These differences do not establish which reconstructed ecosystem is ecologically more accurate. Exact year selection remains pending.

This independently checked comparison uses the saved GE results, without calculator reruns. It covers all 40 source groups—including groups with no loaded catch—and the added diet-import group. SPPR is a coefficient per unit production; this report does not compare catch-weighted PPR totals.

## Nonnegative and stable in both years

| Check | 1985 | 2013 |
|---|---:|---:|
| Negative group totals, all 41 groups | 0 | 0 |
| Negative source cells, all 123 cells | 0 | 0 |
| Nonfinite source cells | 0 | 0 |
| Living feedback spectral radius | 0.106045 | 0.106045 |
| Detritus recycling gain | 0.019185 | 0.031294 |
| Minimum consumer GE | 0.077844 | 0.077844 |
| Near-singular efficiency flags | none | none |
| PP-budget relative residual | 2.03×10⁻¹⁶ | 1.23×10⁻¹⁶ |
| Direct diagnostic status | WARN | WARN |

Both feedback measures are well below the divergence boundary of 1. The saved linear equations also close to a maximum absolute coefficient residual of 7.11×10⁻¹⁵. There is no detected sign, divergence, or numerical singularity problem favoring one year.

The WARN messages concern source EE=0 groups: Ivory shell and Brittle star in 1985; Tongue sole in 2013. The text describes what happens under the separate TE option. **EE=0 does not make GE zero**, because GE uses P/Q rather than EE×P/Q. It therefore does not automatically invalidate these GE coefficients. The EE values still matter to mortality and detritus calculations and remain ecological evidence to review.

## “Larger” depends on the source columns

All-source SPPR sums phytoplankton, scaled detritus, and diet-import columns. PP-only retains just the phytoplankton column. A zero PP-only value can mean that the model allocates the group's coefficient entirely to detritus, rather than that the group requires no basal production.

| Statistic, 38 consumers | 1985 all-source | 2013 all-source | 1985 PP-only | 2013 PP-only |
|---|---:|---:|---:|---:|
| Minimum | 3.33326 | 3.33261 | 0 | 0 |
| Median | 16.63918 | 16.99553 | 12.50331 | 12.38103 |
| Unweighted mean | 21.12172 | 21.37358 | 14.32343 | 13.99206 |
| Maximum | 80.82391 | 88.47169 | 52.04609 | 50.85299 |
| Group with maximum | Stingray | Stingray | Tuna | Tuna |

For all-source coefficients, 2013 is lower for **16** consumers and higher for **22**. For PP-only coefficients, it is lower for **31**, higher for **2** (Stingray and Goby), and exactly equal for **5** (the five zero-PP consumers). These are descriptive counts, not scores of accuracy. Many decreases are very small.

## Are the high values excessive?

There is no defensible universal GE SPPR cutoff for this comparison. A coefficient should be assessed against the group's efficiency, prey requirements, and feedback—not rejected just because it is larger than another group's coefficient.

For a living group, the saved equations give `SPPRᵢ = (1/GEᵢ) × Σ dietᵢⱼ × SPPRⱼ`. Stingray is the largest all-source coefficient in both years because its GE is only **0.077844**, giving an inverse multiplier of **12.846**. Its diet-weighted prey cost is approximately **6.292** in 1985 and **6.888** in 2013, producing **80.824** and **88.472**. These values are high within this food web but are explained by its stated efficiency and diet, without near-divergent feedback. They are review priorities, not established numerical failures.

Stingray's source components are:

| Component | 1985 | 2013 |
|---|---:|---:|
| PP | 42.03980 | 43.70966 |
| Scaled detritus | 35.66767 | 41.70486 |
| Import | 3.11644 | 3.05717 |
| Total | 80.82391 | 88.47169 |

Its own GE and extracted diet are unchanged. Of its +7.64778 increase, the Goby prey route contributes **+3.54315** and the Polychaeta route **+2.94765**, together about 85%. Other routes supply the remainder, including some offsets. Its diet is one of the published columns summing to 1.01 and is normalized by the loader in both years. Thus the finite result is traceable, but depends on that documented transformation and the unresolved source diets.

Other notable changes have identifiable causes:

- **Mackerel: 29.16684 → 17.82137 (−38.90%).** P/B increases from 0.66 to 1.08 at the same Q/B=6.14, increasing GE and reducing its coefficient.
- **Jack mackerel: 11.74412 → 8.92411 (−24.01%).** P/B increases from 1.52 to 2.00 at the same Q/B=5.97.
- **Goby: 23.90545 → 29.47689 (+23.31%).** P/B decreases from 3.50 to 2.96 at Q/B=24.46; the higher 2013 detritus multiplier further increases its coefficient. Goby has zero loaded catch in both years but still affects predators such as Stingray.
- **Tuna: 68.06679 → 66.63995; Sailfish: 53.43658 → 52.24930.** Their high coefficients also follow from approximately eightfold inverse GE multiplying animal-prey costs. Their own GE is unchanged; changes arrive through prey pathways. Tuna is the largest PP-only coefficient in both years.
- **Detritus-dependent benthos** commonly increase by 14.25%, following the detritus multiplier's increase from 1.19135 to 1.36109. This is not a convergence failure.

## Source reliability still limits both years

Both candidates use the same single available published diet matrix. The paper explicitly describes different year-specific diets, especially sardine prey in 1985 versus anchovy in 2013 ([printed p.585](../../../papers/SOJ-2023/evidence/page_13.txt)). Consequently, this analysis verifies the extracted candidates' mathematics, not recovery of both original author networks.

Both loads normalize diets, default missing consumer GS to 0.2, complete missing catch/migration and single-pool detritus routing, and solve missing biomass accumulation. For example, loaded phytoplankton BA is −231.4096 in 1985 and +0.6163 in 2013; these are solved quantities, not reported measurements. The extremely small balance residuals therefore cannot independently validate the source inputs. Full transformations remain in each model's loader audit.

**Neither year earns a clear overall GE reliability preference from positivity, magnitude, or stability.** There is no GE-based reason to discard 1985 because its catch-weighted PPR is larger, nor to certify 2013 because some coefficients are smaller. Choose the intended historical reference period only with the source limitations explicit; resolving the year-specific diets would strengthen the scientific basis for choosing between them. This report adopts neither model.

## Every group

The table includes all source groups in their source numbering. The extra import group is separately identified. Full precision, each source component, and zero-loaded-catch indicators are retained in [GE_GROUP_RELIABILITY_FULL.csv](GE_GROUP_RELIABILITY_FULL.csv). “Zero loaded catch” includes missing catches defaulted to zero; it is not always an explicit published zero.

| ID | Group | All 1985 | All 2013 | All change | PP-only 1985 | PP-only 2013 |
|---|---|---:|---:|---:|---:|---:|
| 1 | Sardine | 20.17355 | 20.17027 | -0.02% | 16.81123 | 16.80796 |
| 2 | Round herring | 8.49985 | 8.49847 | -0.02% | 7.08318 | 7.08180 |
| 3 | Anchovy | 9.23497 | 9.23347 | -0.02% | 7.69578 | 7.69428 |
| 4 | Mackerel | 29.16684 | 17.82137 | -38.90% | 23.60789 | 14.42423 |
| 5 | Jack mackerel | 11.74412 | 8.92411 | -24.01% | 9.56853 | 7.27067 |
| 6 | Yellowtail | 35.63237 | 34.94988 | -1.92% | 27.04640 | 26.47913 |
| 7 | Frigate tuna | 30.27507 | 30.08670 | -0.62% | 23.60781 | 23.44182 |
| 8 | Tuna | 68.06679 | 66.63995 | -2.10% | 52.04609 | 50.85299 |
| 9 | Sailfish | 53.43658 | 52.24930 | -2.22% | 39.06081 | 38.07585 |
| 10 | Spanish mackerel | 27.18685 | 26.09617 | -4.01% | 20.63223 | 19.73118 |
| 11 | Stingray | 80.82391 | 88.47169 | +9.46% | 42.03980 | 43.70966 |
| 12 | Flounder | 24.10701 | 23.89734 | -0.87% | 16.09797 | 15.26966 |
| 13 | Black porgy | 30.92424 | 32.34104 | +4.58% | 18.65721 | 18.54997 |
| 14 | Red seabream | 36.93524 | 38.38684 | +3.93% | 23.28715 | 23.16458 |
| 15 | Tilefish | 28.41968 | 29.96478 | +5.44% | 15.31110 | 15.19567 |
| 16 | Seabass | 38.14885 | 39.38514 | +3.24% | 26.45715 | 26.37740 |
| 17 | Flying fish | 21.69035 | 21.68613 | -0.02% | 21.69035 | 21.68613 |
| 18 | Rockfish | 32.85168 | 33.17060 | +0.97% | 24.26876 | 23.90019 |
| 19 | Barracuda | 41.96673 | 42.02101 | +0.13% | 35.79506 | 35.64770 |
| 20 | Flying squid | 17.80467 | 17.78757 | -0.10% | 14.66707 | 14.65131 |
| 21 | Other squids | 18.40367 | 18.16943 | -1.27% | 15.97884 | 15.77289 |
| 22 | Octopus | 14.10745 | 14.89851 | +5.61% | 8.53096 | 8.52903 |
| 23 | Ivory shell | 6.22974 | 6.92699 | +11.19% | 1.32745 | 1.32705 |
| 24 | Sea cucumber | 3.96495 | 4.52988 | +14.25% | 0.00000 | 0.00000 |
| 25 | Other conch | 3.97116 | 4.53697 | +14.25% | 0.00000 | 0.00000 |
| 26 | Crab | 6.74700 | 7.70832 | +14.25% | 0.00000 | 0.00000 |
| 27 | Prawn | 6.99453 | 7.48409 | +7.00% | 3.55551 | 3.55507 |
| 28 | Bivalve | 5.08120 | 5.24950 | +3.31% | 3.88962 | 3.88841 |
| 29 | Dragonet | 15.47370 | 16.20349 | +4.72% | 10.33956 | 10.33784 |
| 30 | Tongue sole | 14.37511 | 15.69212 | +9.16% | 5.12665 | 5.12593 |
| 31 | Goby | 23.90545 | 29.47689 | +23.31% | 16.69513 | 19.73664 |
| 32 | Shrimp | 5.41906 | 5.89017 | +8.69% | 2.11109 | 2.11087 |
| 33 | Starfish | 6.42389 | 7.15285 | +11.35% | 1.30417 | 1.30376 |
| 34 | Brittle star | 3.99101 | 4.55966 | +14.25% | 0.00000 | 0.00000 |
| 35 | Polychaeta | 3.96719 | 4.53244 | +14.25% | 0.00000 | 0.00000 |
| 36 | Hermit crab | 9.03644 | 9.95942 | +10.21% | 2.55551 | 2.55507 |
| 37 | Mysid | 4.11109 | 4.11087 | -0.01% | 4.11109 | 4.11087 |
| 38 | Zooplankton | 3.33326 | 3.33261 | -0.02% | 3.33326 | 3.33261 |
| 39 | Phytoplankton | 1.00000 | 1.00000 | +0.00% | 1.00000 | 1.00000 |
| 40 | Detritus | 1.19135 | 1.36109 | +14.25% | 0.00000 | 0.00000 |
| 41 | diet_import | 1.00000 | 1.00000 | +0.00% | 0.00000 | 0.00000 |

## Retained checks

[GE_RELIABILITY_VERIFICATION.json](GE_RELIABILITY_VERIFICATION.json) records independent sign, finiteness, statistics, equation-residual, hash, and saved-return checks. [GE_HIGH_GROUP_PREY_CONTRIBUTIONS.csv](GE_HIGH_GROUP_PREY_CONTRIBUTIONS.csv) lists every nonzero direct prey contribution for the six highlighted consumers. The complete [1985](1985/direct_diagnose_sppr_GE.json) and [2013](2013/direct_diagnose_sppr_GE.json) direct returns are unchanged. Canonical source hashes and loaded group tables match the original evidence. No calculator reruns, source edits, model selection, or workbook changes were made.
