## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 14_Patagonian_Shelf_OcampoReinaldo2016_San_Matias_Gulf_(1970), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 2 indeterminate, 1 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 26 of 26 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 42.559, group 16 (Juvenile hake).

Groups with recomputed EE > 1: 12 (Benthic-demersal fish I, 1.006), 16 (Juvenile hake, 43.558).

P/Q outside 0.02-0.5: 14 (Large hake, 0.507).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 12 (Benthic-demersal fish I): recomputed EE = 1.006 > 1 without BA, and BA is unknown - a BA of -0.01202 t/km^2/year (-0.01 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 16 (Juvenile hake): recomputed EE = 43.558 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation

### Warnings

- group 14 (Large hake): P/Q = 0.507 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 24 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Dolphins), 2 (Sea Lions), 3 (Other rays), 4 (Large rays), 5 (Small rays), 6 (Large sharks), 7 (Medium-sized sharks), 8 (Juvenile sharks) ...
- detritus pools (1): inflow ~214.7, consumption ~119.2 t/km^2/year, implied EE ~0.555 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Dolphins | 0.008 | 0.85 | 10 | 4.509e-05 | 0 | 0.085 | 0 | unknown |
| 2 | Sea Lions | 0.021 | 1.014 | 14 | 0.0001 | 0 | 0.0724 | 0 | unknown |
| 3 | Other rays | 0.306 | 0.27 | 4.09 | 0 | 0 | 0.066 | 0 | unknown |
| 4 | Large rays | 0.553 | 0.45 | 3.233 | 2.135e-06 | 0 | 0.139 | 0 | unknown |
| 5 | Small rays | 0.447 | 0.55 | 4.753 | 0.7495 | 0.754 | 0.116 | 0 | unknown |
| 6 | Large sharks | 0.018 | 0.28 | 2.263 | 1.511e-10 | 0 | 0.124 | 0 | unknown |
| 7 | Medium-sized sharks | 0.762 | 0.615 | 3.632 | 0.0062 | 0.00591 | 0.169 | 0 | unknown |
| 8 | Juvenile sharks | 0.118 | 0.4 | 3.485 | 0.999 | 0.997 | 0.115 | 0 | unknown |
| 9 | Narrownose smooth-hound | 0.153 | 0.6 | 4 | 8.471e-07 | 0 | 0.15 | 0 | unknown |
| 10 | Benthic-demersal fish II | 1.304 | 0.435 | 3.14 | 0.0147 | 0.0144 | 0.139 | 0 | unknown |
| 11 | Flounders | 0.339 | 0.97 | 3.7 | 0.9 | 0.904 | 0.262 | 0 | unknown |
| 12 | Benthic-demersal fish I | 1.327 | 1.29 | 6.95 | 0.999 | 1.01 | 0.186 | 0 | unknown |
| 13 | Plownose chimaera | 0.464 | 0.4 | 3.485 | 0.02611 | 0.0247 | 0.115 | 0 | unknown |
| 14 | Large hake | 3.227 | 0.688 | 1.358 | 0.0018 | 0.00159 | 0.507 | 0 | unknown |
| 15 | Medium-sized hake | 6.237 | 0.77 | 2.889 | 0.9485 | 0.947 | 0.267 | 0 | unknown |
| 16 | Juvenile hake | 0.098 | 0.88 | 11.57 | 0.999 | 43.6 | 0.0761 | 0 | unknown |
| 17 | Pink cusk-eel | 0.947 | 0.99 | 3.076 | 0.2209 | 0.221 | 0.322 | 0 | unknown |
| 18 | Patagonian hoki | 3.861 | 0.69 | 3.892 | 0.2579 | 0.257 | 0.177 | 0 | unknown |
| 19 | Medium-sized pelagic fishes | 8.953 | 1.25 | 6.49 | 0.451 | 0.452 | 0.193 | 0 | unknown |
| 20 | Small pelagic fishes | 10.34 | 1.943 | 12 | 0.99 | 0.991 | 0.162 | 0 | unknown |
| 21 | Squids | 1.898 | 2.977 | 6.1 | 0.9 | 0.899 | 0.488 | 0 | unknown |
| 22 | Benthic organisms | 9.78 | 4.12 | 12 | 0.5856 | 0.586 | 0.343 | 0 | unknown |
| 23 | Jellyfishes | 2.765 | 9.56 | 21.9 | 0.9 | 0.9 | 0.437 | 0 | unknown |
| 24 | Zooplankton | 9.059 | 19.92 | 41.58 | 0.9 | 0.9 | 0.479 | 0 | unknown |
| 25 | Phytoplankton | 3.577 | 105 | - | 0.999 | 0.999 | - | 0 | unknown |
| 26 | Detritus | 1 | - | - | 0.5552 | - | - | 0 | unknown |
