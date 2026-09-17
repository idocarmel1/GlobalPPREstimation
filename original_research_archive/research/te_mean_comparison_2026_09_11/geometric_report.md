# Geometric mean sensitivity

Each cell shows arithmetic mean → geometric mean, in percent. All three weighting schemes use consumer groups only. Canary Current remains excluded for failed mass balance.

| Model | Equal weights | Catch weights | Biomass weights |
|---|---:|---:|---:|
| 077HS_1_Eastern_tropical_Pacific_(1993-1997) | 7.67 → 0.00 | 5.25 → 0.00 | 19.38 → 0.00 |
| 13_2_Northern_Humboldt_Current_(1995-1998) | 10.87 → 0.00 | 10.29 → 9.68 | 16.70 → 0.00 |
| 28_646_Guinea_(1998) | 9.85 → 7.02 | 12.18 → 11.20 | 8.02 → 7.09 |
| 32_1_Arabian_Sea_off_Karnataka_(2000) | 19.81 → 13.75 | 20.48 → 18.85 | 9.32 → 6.72 |
| 34_1_Bay_of_Bengal_(1978) | 16.84 → 15.34 | 19.29 → 18.77 | 13.54 → 12.03 |
| 35_412_Gulf_of_Thailande_(1963) | 18.95 → 0.00 | 22.57 → 22.45 | 14.00 → 0.00 |
| 36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s) | 15.21 → 8.43 | 18.59 → 17.82 | 12.78 → 10.48 |
| 47_2_East_China_Sea_(2018) | 18.99 → 0.00 | Unavailable | 13.24 → 0.00 |
| 52_1_Sea_of_Okhotsk_NE_(1980) | 9.58 → 0.00 | Unavailable | 21.29 → 0.00 |

For positive efficiencies: G = exp(sum(w_i ln(TE_i)) / sum(w_i)). Zero-weight groups are omitted; a zero efficiency with positive weight makes the geometric mean zero (its continuous extension). No zero-efficiency consumers were discarded.

Eastern tropical Pacific has one numerical-roundoff negative TE (toothed whales, approximately -3.92e-18). This sensitivity treats values between -1e-15 and 0 as zero and records every such group; other negative values would stop the calculation. No clipping was added to production code.

The requested production fix retains arithmetic averaging and changes only the zero-catch biomass fallback to consumer groups. Catch-weighted production calculations retain their previous cohort. Geometric weighting was not added to production. The catch sensitivity above, like the previous comparison, is consumer-only.

For Arabian Sea the biomass mean changes from 9.32% to 6.72%. If used as the common TE in SPPR_1995 at TL=3, this alone would raise SPPR by about 1.92 times; at heterogeneous trophic levels the aggregate effect differs. The actual Arabian Sea production method uses catch weights because its model has catch, so this hypothetical biomass substitution is not triggered by the code fix.

For East China Sea and Okhotsk the geometric biomass mean is zero because positive-biomass consumers have EE=0. Using a zero global TE gives no finite classic SPPR for TL>1. A geometric consumer mean therefore cannot serve as a general replacement without an explicit, scientifically justified treatment of those zeros.

Exact values, zero-TE group names and results from the actual production get_TE method are recorded in geometric_results.json. All nine saved balanced models were checked against the patched method. Existing exported workbooks and atlas data were not regenerated.
