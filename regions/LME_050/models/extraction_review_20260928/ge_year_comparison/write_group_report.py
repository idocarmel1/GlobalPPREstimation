from pathlib import Path
import pandas as pd,json
P=Path(__file__).resolve().parent
f=pd.read_csv(P/'GE_GROUP_RELIABILITY_FULL.csv',index_col=0)
intro='''# GE SPPR reliability: 1985 versus 2013

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
'''
rows=[]
for i,r in f.iterrows():rows.append(f'| {i} | {r["name"]} | {r.all_1985:.5f} | {r.all_2013:.5f} | {r.all_change_pct:+.2f}% | {r.PP_1985:.5f} | {r.PP_2013:.5f} |')
end='''

## Retained checks

[GE_RELIABILITY_VERIFICATION.json](GE_RELIABILITY_VERIFICATION.json) records independent sign, finiteness, statistics, equation-residual, hash, and saved-return checks. [GE_HIGH_GROUP_PREY_CONTRIBUTIONS.csv](GE_HIGH_GROUP_PREY_CONTRIBUTIONS.csv) lists every nonzero direct prey contribution for the six highlighted consumers. The complete [1985](1985/direct_diagnose_sppr_GE.json) and [2013](2013/direct_diagnose_sppr_GE.json) direct returns are unchanged. Canonical source hashes and loaded group tables match the original evidence. No calculator reruns, source edits, model selection, or workbook changes were made.
'''
(P/'GE_SPPR_GROUP_COMPARISON.md').write_text(intro+'\n'.join(rows)+end,encoding='utf8')
(P/'GE_SPPR_MAIN_FINDINGS.md').write_text('''# GE coefficient comparison: main findings

Neither 1985 nor 2013 has a clear GE numerical reliability advantage. Both have zero negative or nonfinite source coefficients and stable feedback calculations.

- All-source maximum: Stingray, **80.82 in 1985; 88.47 in 2013**. Its high values are explained by low GE and prey costs, rather than divergent feedback.
- PP-only maximum: Tuna, **52.05 in 1985; 50.85 in 2013**.
- 2013 all-source coefficients are lower for 16 consumers and higher for 22. PP-only coefficients are lower for 31, higher for 2, and equal for 5.
- Lower positive values do not prove greater accuracy. EE=0 warnings do not automatically invalidate GE.
- Both reconstructions share the unresolved year-specific diet problem and rely on documented loader completions. No year is selected.

The larger 1985 catch-weighted footprint is mainly a catch difference, not generally inflated coefficients. [Full comparison and reliability assessment](GE_SPPR_GROUP_COMPARISON.md).
''',encoding='utf8')
print('Wrote independently verified comparison and short findings.')
