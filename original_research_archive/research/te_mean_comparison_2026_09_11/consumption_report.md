# Original comparison with consumption weights

Consumer-only arithmetic means, including zero-TE consumers. Q is total consumption (biomass × Q/B), not Q/B alone. Consumption-weighted TE = sum(Q_i TE_i)/sum(Q_i) = sum(P_i EE_i)/sum(Q_i). Input hashes and the original three means were verified against the saved workbooks.

| Model | Equal | Catch | Biomass | Consumption | Trophic: cycles removed | Trophic: cycles retained |
|---|---:|---:|---:|---:|---:|---:|
| 077HS_1_Eastern_tropical_Pacific_(1993-1997) | 7.67 | 5.25 | 19.38 | 22.49 | 18.76 | 20.37 |
| 13_2_Northern_Humboldt_Current_(1995-1998) | 10.87 | 10.29 | 16.70 | 24.15 | 12.11 | 21.32 |
| 27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991) | Excluded | Excluded | Excluded | Excluded | Excluded | Excluded |
| 28_646_Guinea_(1998) | 9.85 | 12.18 | 8.02 | 10.17 | 10.29 | 11.42 |
| 32_1_Arabian_Sea_off_Karnataka_(2000) | 19.81 | 20.48 | 9.32 | 16.07 | 13.37 | 13.94 |
| 34_1_Bay_of_Bengal_(1978) | 16.84 | 19.29 | 13.54 | 11.83 | 13.39 | 16.68 |
| 35_412_Gulf_of_Thailande_(1963) | 18.95 | 22.57 | 14.00 | 15.34 | 11.68 | 14.10 |
| 36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s) | 15.21 | 18.59 | 12.78 | 6.69 | 9.96 | 11.01 |
| 47_2_East_China_Sea_(2018) | 18.99 | Unavailable | 13.24 | 8.36 | 8.30 | 11.25 |
| 52_1_Sea_of_Okhotsk_NE_(1980) | 9.58 | Unavailable | 21.29 | 21.73 | 11.53 | 20.97 |

All table entries are percentages. The trophic columns are unchanged geometric summaries of level-II–IV flow efficiencies, with the cycle conventions documented in methodology.md. They are different statistics from consumer-weighted means.

Canary Current remains excluded for failed underlying model mass balance. All original source/model caveats apply, especially substantial source-diet normalization in Eastern tropical Pacific. Missing catch means no catch in the available model input. Thailand is the 1980 payload despite its inherited 1963 filename.

This is a read-only analysis. No production code, model workbook, or atlas output was changed.
