## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 941_EEZ_Kiribati_Gilbert_Islands_proxy_200701_WCPO_Warm_Pool_Final_(mixed_periods), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 2 error(s), 0 indeterminate, 2 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 24 of 31 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.694, group 11 (Small BET).

Groups with recomputed EE > 1: 11 (Small BET, 1.338), 12 (Small YFT, 1.125).

P/Q outside 0.02-0.5: none.

BA: carried for 7 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 5 (BET, +0), 6 (YFT, +0), 7 (SKJ, +0), 11 (Small BET, +0), 12 (Small YFT, +0), 13 (Small SKJ, +0), 14 (baby SKJ, +0). The remaining 24 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 11 (Small BET): recomputed EE = 1.338 > 1 - catch+BA+predation (0.00269) exceeds production (0.00201)
- group 12 (Small YFT): recomputed EE = 1.125 > 1 - catch+BA+predation (0.02856) exceeds production (0.02538)

### Warnings

- group 11 (Small BET): printed EE 0.644 vs recomputed 1.338 (diff 0.694), BA 0 carried
- group 12 (Small YFT): printed EE 0.849 vs recomputed 1.125 (diff 0.276), BA 0 carried

### Notes

- 28 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Swordfish), 2 (Other Billfish), 3 (Blue Shark), 4 (Other Sharks), 5 (BET), 6 (YFT), 7 (SKJ), 8 (Piscivorous fish) ...
- detritus pools (1): inflow ~996.7, consumption ~788.6 t/km^2/year, implied EE ~0.791 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Swordfish | 0.0036 | 0.4 | 5 | 0.05 | 0.0496 | 0.08 | 7.14e-05 | unknown |
| 2 | Other Billfish | 0.0052 | 0.6 | 5 | 0.075 | 0.0747 | 0.12 | 0.0002331 | unknown |
| 3 | Blue Shark | 0.016 | 0.3 | 3 | 0.031 | 0.0308 | 0.1 | 0.000144 | unknown |
| 4 | Other Sharks | 0.0012 | 0.3 | 3 | 0.356 | 0.356 | 0.1 | 9.23e-05 | unknown |
| 5 | BET | 0.00162 | 0.95 | 15 | 0.777 | 0.77 | 0.0633 | 0.000819 | 0 |
| 6 | YFT | 0.00799 | 1.537 | 16.14 | 0.56 | 0.559 | 0.0952 | 0.0065 | 0 |
| 7 | SKJ | 0.0842 | 2.046 | 25 | 0.347 | 0.347 | 0.0818 | 0.03569 | 0 |
| 8 | Piscivorous fish | 0.025 | 1.5 | 10 | 0.946 | 0.947 | 0.15 | 0.00038 | unknown |
| 9 | Small Billfish | 0.0106 | 1 | 10 | 0.114 | 0.111 | 0.1 | 0 | unknown |
| 10 | Small Sharks | 0.0118 | 0.5 | 5 | 0.043 | 0.042 | 0.1 | 0 | unknown |
| 11 | Small BET | 0.00241 | 0.834 | 26.16 | 0.644 | 1.34 | 0.0319 | 0.001398 | 0 |
| 12 | Small YFT | 0.0128 | 1.983 | 33.96 | 0.849 | 1.13 | 0.0584 | 0.006973 | 0 |
| 13 | Small SKJ | 0.0194 | 2.539 | 50.7 | 0.927 | 0.927 | 0.0501 | 0.00172 | 0 |
| 14 | baby SKJ | 0.00659 | 25 | 191.8 | 0.776 | 0.776 | 0.13 | 0 | 0 |
| 15 | Epi crust | 4.515 | 8 | 30 | 0.98 | 0.98 | 0.267 | 0 | unknown |
| 16 | Epi fish | 2.127 | 3 | 15 | 0.95 | 0.952 | 0.2 | 0 | unknown |
| 17 | Epi small fish | 0.785 | 10 | 60 | 0.98 | 0.978 | 0.167 | 0 | unknown |
| 18 | Epi mollusc | 0.384 | 7 | 20 | 0.95 | 0.95 | 0.35 | 0 | unknown |
| 19 | Epi small mollusc | 0.955 | 15 | 100 | 0.98 | 0.979 | 0.15 | 0 | unknown |
| 20 | M Meso fish+other | 3.404 | 2.2 | 10 | 0.95 | 0.95 | 0.22 | 0 | unknown |
| 21 | M meso mollusc | 1.484 | 3 | 10 | 0.95 | 0.951 | 0.3 | 0 | unknown |
| 22 | Meso fish + other | 0.634 | 2.5 | 10 | 0.95 | 0.952 | 0.25 | 0 | unknown |
| 23 | Meso mollusc | 0.201 | 3 | 10 | 0.95 | 0.95 | 0.3 | 0 | unknown |
| 24 | HM Bathy forage | 1.803 | 1.189 | 8 | 0.95 | 0.95 | 0.149 | 0 | unknown |
| 25 | M Bathy forage | 0.282 | 1.338 | 8 | 0.95 | 0.949 | 0.167 | 0 | unknown |
| 26 | Bathy forage | 0.0698 | 0.845 | 8 | 0.95 | 0.95 | 0.106 | 0 | unknown |
| 27 | Mesozpk | 4.4 | 50 | 230 | 0.995 | 0.995 | 0.217 | 0 | unknown |
| 28 | Microzpk | 2 | 120 | 382 | 0.992 | 0.992 | 0.314 | 0 | unknown |
| 29 | Large phyto | 1.849 | 120.3 | - | 0.829 | 0.829 | - | 0 | unknown |
| 30 | Small phyto | 8 | 109.4 | - | 0.756 | 0.756 | - | 0 | unknown |
| 31 | Detritus | 100 | - | - | 0.791 | - | - | 0 | unknown |
