# LME_014 pooled-detritus sensitivity

Pooling changes source-model total-catch PPR by only **+0.01846% (GE)** and **+0.00691% (TE)** relative to the source-reconciled separate-pool calculation. Both results remain **WARN**. EE floor is **ON at 0.1** in both configurations.

## Matched comparison

Discards (35) is already classified as DET, alongside Detritus (36). This experiment changes the existing calculator option from `det_collapse_mode=never` to `always`, retaining `det_open_mode=none`. It uses the exact prior effective state, including independently verified fishery returns to Detritus36, and the same pinned engine. The floor was not applied again. The two separate-pool results are reused; only the pooled GE and TE calls are new.

| Method | Separate pools | Pooled attribution | Change | Overall status |
|---|---:|---:|---:|---|
| GE | 35.6114670127 | 35.6180417016 | +0.018462% | WARN |
| TE | 89.4135556062 | 89.4197374676 | +0.006914% | WARN |

These are source-model catch-weighted, all-source PPR values, not regional LME annual totals. Source mass is reported as tonnes per km² for 2020; wet versus dry mass is not explicit. No carbon conversion was made. PP-only PPR is unchanged: GE 20.8858634579 and TE 60.4869998045. [Full comparison](outputs/comparison.json)

## What pooling changes

The calculator sums the two detritus basis contributions, solves one scalar `a/(1-b)`, and applies it to both original source columns. It preserves group identities, consumer diets, physical flows and the A/L operators. This is pooled SPPR attribution, not a physical rewrite of the source Ecopath model.

| Method | Separate Discards SPPR | Separate Detritus SPPR | Shared pooled SPPR |
|---|---:|---:|---:|
| GE | 0 | 1.091558565747 | 1.091817694021 |
| TE | 0 | 0.941069101163 | 0.941071225662 |

Pooling therefore assigns a positive PPR origin to consumption through the Discards pathway. The effect is larger for some consumers than for total fishery PPR. For Seabirds:

| Method | Separate-pool SPPR | Pooled SPPR | Change |
|---|---:|---:|---:|
| GE | 576.498641 | 584.621925 | +1.4091% |
| TE | 15827.119078 | 15900.621563 | +0.4644% |

The actual pooled recycling coefficients are GE `collapse_b=0.0390868932624` and TE `collapse_b=0.00146962581595`. Diagnostic `divergence.b` deliberately retains the pre-pooling spectral radius; it should not be substituted for those pooled coefficients. Complete values and identities are retained in each full return.

## The stock residual remains a source question

The unchanged physical budgets sum to inflow **839.524102782**, consumption **43.505115897**, and net residual **+796.018986885 t/km²/year**. Aggregating those budgets would hide the individual Discards deficit inside the large Detritus surplus. It would not identify new fishery-discard or processing-offal supply.

The actual pooling option keeps Discards35's **−0.20750363203745528 t/km²/year** stock residual visible. Both methods retain this warning, pass strict weighted PPR balance with zero reported relative gap, and return finite SPPR matrices without negative entries. Their physical runtime state is unchanged. All non-detritus source columns, including PP and imports, are unchanged.

The original paper's heads-and-guts feeding mechanism does not establish that ordinary detritus is a substitute for fishery offal. Pooling is useful as a sensitivity assumption, showing that the total model-catch PPR is insensitive here. It does not resolve the missing source attribution or justify removing the warning. The earlier [Discards reconciliation](../discards_reconciliation_20261114/discards_reconciliation.md) retains the native model and paper evidence.

## Evidence and preservation

[GE full return](outputs/GE_pooled_full_return.json) · [TE full return](outputs/TE_pooled_full_return.json) · [Independent verification](qa/independent_pooling_verification.json) · [Execution provenance](outputs/provenance.json) · [Evidence index](evidence_index.json)

The model, source inputs, researcher DOCX, appendix, regional workbooks and retained baseline results were preserved. No Project.xlsx, map, trends or shared code writes were made. No decision was registered and no findings were sent to the coordinator. A summary-only group-name alignment issue was corrected by verified IDs before handoff; all numeric outputs and direct diagnostics were unchanged, with the correction and exact executed runner retained.
