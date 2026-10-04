# Consumer means excluding TE = 0

Read-only sensitivity: consumer groups with TE > 0 only, with weights renormalized after exclusion. Canary Current remains excluded for failed mass balance. Existing source-diet caveats apply. Values below are percentages.

| Model | Equal geometric | Catch geometric | Biomass geometric | Excluded consumer groups | Excluded biomass (%) | Excluded catch (%) |
|---|---:|---:|---:|---:|---:|---:|
| 077HS_1_Eastern_tropical_Pacific_(1993-1997) | 2.98 | 4.53 | 18.58 | 1/36 | 0.42 | 0.00 |
| 13_2_Northern_Humboldt_Current_(1995-1998) | 6.51 | 9.68 | 9.05 | 5/33 | 0.07 | 0.00 |
| 28_646_Guinea_(1998) | 7.02 | 11.20 | 7.09 | 0/42 | 0.00 | 0.00 |
| 32_1_Arabian_Sea_off_Karnataka_(2000) | 13.75 | 18.85 | 6.72 | 0/22 | 0.00 | 0.00 |
| 34_1_Bay_of_Bengal_(1978) | 15.34 | 18.77 | 12.03 | 0/44 | 0.00 | 0.00 |
| 35_412_Gulf_of_Thailande_(1963) | 20.06 | 22.45 | 12.86 | 2/27 | 1.44 | 0.00 |
| 36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s) | 8.43 | 17.82 | 10.48 | 0/35 | 0.00 | 0.00 |
| 47_2_East_China_Sea_(2018) | 17.55 | Unavailable | 11.13 | 2/22 | 0.03 | Unavailable |
| 52_1_Sea_of_Okhotsk_NE_(1980) | 5.23 | Unavailable | 19.74 | 2/26 | 0.00 | Unavailable |

Formula: G = exp(sum_{TE_i>0}(w_i ln TE_i) / sum_{TE_i>0}(w_i)). If no positive weight remains, the mean is unavailable. Positive efficiencies arbitrarily close to zero are retained; no positive cutoff is imposed.

The single ETP toothed-whale TE of approximately -3.92e-18 is treated as zero under the same -1e-15 to 0 signed-roundoff rule as the preceding sensitivity. Other negative values cause an error. This rule does not modify production code.

These are means conditional on positive transfer efficiency, not means over the entire consumer community. TE=0 can reflect EE=0 rather than missing data, so dropping such consumers changes the scientific quantity. Exact excluded names, weight fractions, corresponding arithmetic means and previous inclusive means are in positive_te_results.json.

No production code, workbook or atlas output was changed. Verified renormalization on a known example, zero remaining weight, geometric <= arithmetic, and unchanged values whenever excluded groups carry zero weight.
