# LME_014 physical Discards–Detritus merge

The isolated physical-merge scenario is complete with **EE floor ON at 0.1**. Discards35 and Detritus36 were replaced by one physical pool, retained as group36 and named **Detritus including Discards**. The canonical model was not changed.

## GE/TE comparison

| Method | Separate physical pools | Physically merged pool | Change | Diagnostic status |
|---|---:|---:|---:|---|
| GE | 35.6114670127 | 35.6180417016 | +0.018462% | WARN → OK |
| TE | 89.4135556062 | 89.4197374676 | +0.006914% | WARN → OK |

Values are source-model total-catch, all-source PPR, not regional LME annual totals. Source units are tonnes per km² for 2020; wet versus dry mass is not explicitly established. No carbon conversion was made. PP-only PPR remains GE **20.8858634579** and TE **60.4869998045**.

The physical merge reproduces the prior attribution-pooling result within numerical tolerance. Maximum absolute SPPR difference after the correct source-column crosswalk is **1.14e-13**. For retained recipients, merged source36 equals the previous pooled columns35+36. The two detritus recipient rows are not added together, because each represented a coefficient per unit material.

- GE: merged-pool SPPR **1.091817694021**, recycling b **0.039086893262**, strict weighted relative gap **1.17e-16**, overall **OK**.
- TE: merged-pool SPPR **0.941071225662**, recycling b **0.001469625816**, strict weighted relative gap **1.17e-16**, overall **OK**.

All returned SPPR values are finite and nonnegative at the recorded tolerance. Both strict weighted balance checks pass. Full matrices retain every recipient, including unfished groups. The matrix has 36 runtime recipients and four basal-source columns; only one detritus group remains.

For Seabirds25, the coefficients change more than the fishery total:

| Method | Separate-pool SPPR | Physical-merge SPPR | Change |
|---|---:|---:|---:|
| GE | 576.498641 | 584.621925 | +1.4091% |
| TE | 15827.119078 | 15900.621563 | +0.4644% |

## What was physically merged

The run restored the audited, source-reconciled **pre-floor** state. It summed the two inherited stocks and extensive flows, summed their prey fractions for every consumer, and combined both natural-detritus-fate and fleet-return recipient columns. The two detritus consumer rows were both zero. After recipient aggregation, both original detritus fate rows were exactly one into the merged pool, so there was no undefined donor-weighting choice. All living biological quantities and total diet consumption were preserved.

Merged runtime biomass is **1.005859524943** in the inherited model's stock units. This is the sum of retained runtime values, not a newly observed stock. PB/QB and GE/GS were derived from the summed flows; source EE was not averaged. Original component source values and missingness remain in the [merge specification](inputs/merge_specification.json).

The floor was then applied exactly once. The affected living groups and hypothetical external mortality sink (**65.521187843373 t/km²/year**) match the separate-pool reference. Recorded fisheries returns (**0.005859524956463 t/km²/year**) enter the merged pool once; total fishery catch and external-removal accounting are preserved. No additional offal or import was introduced.

## Why the negative-stock warning disappears

The merged physical budget after the floor is:

| Term | t/km²/year |
|---|---:|
| Incoming material | 839.524102782152 |
| Consumption | 43.505115897365 |
| Calculated stock residual | +796.018986884787 |

The source model's two reported BA inputs sum to zero; the positive runtime residual remains the reconstruction's calculated closure. It is not a measured accumulation. The former Discards deficit of **−0.20750363203745528** is absorbed into the larger Detritus surplus when their physical budgets are combined. There is no separately represented Discards stock left for the diagnostic to flag.

This is a numerical outcome under the **complete-mixing assumption**. It does not establish that ordinary detritus and fishery heads/guts are interchangeable food or identify the missing source-specific offal supply. The [original Discards reconciliation](../discards_reconciliation_20261114/discards_reconciliation.md) and its source warning remain unchanged. An improved scenario diagnostic does not validate or approve the original model.

## Execution and preservation

Only two fresh diagnostics were run: GE and TE on the physically merged state, using `det_collapse_mode=never` and `det_open_mode=none`. There was no additional attribution-pooling operation. This is a PPR-calculator scenario based on the audited reconstruction; no merged native EwE database run was performed. The separate-pool and [attribution-pooled](../pooled_detritus_20261114/pooled_detritus.md) baselines were reused with their exact code/input identities. The merged pre-floor and effective states were retained; the effective state was reopened and authenticated before the calls.

[GE full return](outputs/GE_physical_merge_full_return.json) · [TE full return](outputs/TE_physical_merge_full_return.json) · [Merge and floor states](outputs/merge_and_floor.json) · [Independent verification](qa/independent_physical_merge_verification.json) · [Comparison data](outputs/comparison.json) · [Execution provenance](outputs/provenance.json) · [Evidence index](evidence_index.json)

No canonical model, source input, researcher DOCX, appendix, regional workbook, Project.xlsx, map, trends or shared code was changed by this task. No scenario was adopted, decision registered, or findings sent to the coordinator.
