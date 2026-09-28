## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 941_EEZ_Kiribati_Gilbert_Islands_proxy_200702_WCPO_Warm_Pool_Initial_(mixed_periods), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 11 indeterminate, 2 warning(s), 0 note(s).

Biomass accumulation is unknown (-9999) for 23 of 23 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: no group has both a printed EE and enough inputs to recompute one.

Groups with recomputed EE > 1: 8 (Piscivorous fish, 1.043), 11 (Small BET, 2.312), 12 (Small YFT, 4.634), 13 (Small SKJ, 30.762), 14 (Epi forage, 2.957), 15 (M Meso forage, 4.385), 16 (Meso forage, 9.162), 17 (HM Bathy forage, 6.976), 18 (M Bathy forage, 10.650), 19 (Bathy forage, 4.192), 21 (Microzpk, 3.026).

P/Q outside 0.02-0.5: none.

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 8 (Piscivorous fish): recomputed EE = 1.043 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 11 (Small BET): recomputed EE = 2.312 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 12 (Small YFT): recomputed EE = 4.634 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 13 (Small SKJ): recomputed EE = 30.762 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 14 (Epi forage): recomputed EE = 2.957 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 15 (M Meso forage): recomputed EE = 4.385 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 16 (Meso forage): recomputed EE = 9.162 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 17 (HM Bathy forage): recomputed EE = 6.976 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 18 (M Bathy forage): recomputed EE = 10.650 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 19 (Bathy forage): recomputed EE = 4.192 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 21 (Microzpk): recomputed EE = 3.026 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation

### Warnings

- group 22 (Large phyto): only 2 of B/P-B/Q-B/EE given (B, P/B) - Ecopath needs three
- group 23 (Small phyto): only 2 of B/P-B/Q-B/EE given (B, P/B) - Ecopath needs three

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Swordfish | 0.0036 | 0.4 | 5 | - | 0.0496 | 0.08 | 7.14e-05 | unknown |
| 2 | Other Billfish | 0.0052 | 0.6 | 5 | - | 0.0747 | 0.12 | 0.0002331 | unknown |
| 3 | Blue Shark | 0.016 | 0.3 | 5 | - | 0.198 | 0.06 | 0.000144 | unknown |
| 4 | Other Sharks | 0.0012 | 0.3 | 5 | - | 0.421 | 0.06 | 9.23e-05 | unknown |
| 5 | BET | 0.00162 | 0.95 | 24.73 | - | 0.823 | 0.0384 | 0.000819 | unknown |
| 6 | YFT | 0.00799 | 1.537 | 16.14 | - | 0.631 | 0.0952 | 0.0065 | unknown |
| 7 | SKJ | 0.0842 | 2.046 | 33.48 | - | 0.406 | 0.0611 | 0.03569 | unknown |
| 8 | Piscivorous fish | 0.05 | 1.5 | 10 | - | 1.04 | 0.15 | 0.00038 | unknown |
| 9 | Small Billfish | 0.0106 | 1 | 10 | - | 0.131 | 0.1 | 0 | unknown |
| 10 | Small Sharks | 0.0118 | 0.5 | 10 | - | 0.317 | 0.05 | 0 | unknown |
| 11 | Small BET | 0.00356 | 0.834 | 22.39 | - | 2.31 | 0.0373 | 0.001398 | unknown |
| 12 | Small YFT | 0.0157 | 1.983 | 18.01 | - | 4.63 | 0.11 | 0.006973 | unknown |
| 13 | Small SKJ | 0.0275 | 2.539 | 69.29 | - | 30.8 | 0.0366 | 0.00172 | unknown |
| 14 | Epi forage | 0.339 | 3.691 | 15 | - | 2.96 | 0.246 | 0 | unknown |
| 15 | M Meso forage | 0.417 | 2.132 | 15 | - | 4.39 | 0.142 | 0 | unknown |
| 16 | Meso forage | 0.164 | 2.435 | 15 | - | 9.16 | 0.162 | 0 | unknown |
| 17 | HM Bathy forage | 0.629 | 1.189 | 15 | - | 6.98 | 0.0793 | 0 | unknown |
| 18 | M Bathy forage | 0.343 | 1.338 | 15 | - | 10.6 | 0.0892 | 0 | unknown |
| 19 | Bathy forage | 0.759 | 0.845 | 15 | - | 4.19 | 0.0563 | 0 | unknown |
| 20 | Mesozpk | 4.358 | 38 | 230 | - | 0.699 | 0.165 | 0 | unknown |
| 21 | Microzpk | 1.461 | 120 | 382 | - | 3.03 | 0.314 | 0 | unknown |
| 22 | Large phyto | 1.849 | 120.3 | - | - | 0.577 | - | 0 | unknown |
| 23 | Small phyto | 10.48 | 109.4 | - | - | 0.433 | - | 0 | unknown |
