## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 22_20251890_East_Coast_of_Scotland_(1890-1895), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 25 of 25 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.041, group 16 (Monkfish).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 22 (Seabirds, 0.006), 23 (Seals, 0.004), 24 (Cetaceans, 0.002).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 22 (Seabirds): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 23 (Seals): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 24 (Cetaceans): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 23 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 2 (Small zooplankton), 3 (Large zooplankton), 4 (Infauna), 5 (Epifauna), 6 (Crustacea), 7 (Squid & Octopus), 8 (Flatfishes), 9 (Turbot) ...
- detritus pools (1): inflow ~1392, consumption ~461.6 t/km^2/year, implied EE ~0.332 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 7.5 | 286 | - | 0.61 | 0.61 | - | 0 | unknown |
| 2 | Small zooplankton | 34.02 | 9.17 | 29.96 | 0.84 | 0.84 | 0.306 | 0 | unknown |
| 3 | Large zooplankton | 31.07 | 4 | 12.5 | 0.9 | 0.9 | 0.32 | 0 | unknown |
| 4 | Infauna | 5.28 | 20 | 80 | 0.9 | 0.902 | 0.25 | 0 | unknown |
| 5 | Epifauna | 2.82 | 18.09 | 72.65 | 0.88 | 0.878 | 0.249 | 0.03145 | unknown |
| 6 | Crustacea | 4.99 | 2.26 | 13.44 | 0.81 | 0.81 | 0.168 | 0.03626 | unknown |
| 7 | Squid & Octopus | 0.21 | 2 | 15.04 | 0.95 | 0.937 | 0.133 | 0.0005629 | unknown |
| 8 | Flatfishes | 4.09 | 0.39 | 2.35 | 0.89 | 0.887 | 0.166 | 0.05092 | unknown |
| 9 | Turbot | 1.09 | 0.45 | 2.2 | 0.08 | 0.0824 | 0.205 | 0.02187 | unknown |
| 10 | Cod | 2.1 | 1.03 | 4.41 | 0.2 | 0.199 | 0.234 | 0.1107 | unknown |
| 11 | Ling | 0.37 | 0.46 | 1.53 | 0.65 | 0.639 | 0.301 | 0.09397 | unknown |
| 12 | Haddock | 1.2 | 1.11 | 6.48 | 0.96 | 0.963 | 0.171 | 0.2726 | unknown |
| 13 | Whiting | 0.95 | 1 | 6.31 | 0.51 | 0.507 | 0.158 | 0.01114 | unknown |
| 14 | Hake | 0.59 | 0.5 | 1.68 | 0.59 | 0.583 | 0.298 | 0.1491 | unknown |
| 15 | Saithe | 1.21 | 0.6 | 2.88 | 0.98 | 0.96 | 0.208 | 0.2165 | unknown |
| 16 | Monkfish | 0.03 | 0.2 | 0.93 | 0.92 | 0.879 | 0.215 | 0.003293 | unknown |
| 17 | Large Dem. fish | 0.48 | 0.65 | 5.2 | 0.95 | 0.95 | 0.125 | 0.1225 | unknown |
| 18 | Herring | 9.8 | 0.85 | 4.25 | 0.69 | 0.693 | 0.2 | 2.156 | unknown |
| 19 | Small pelagics | 12.38 | 1.89 | 8.48 | 0.88 | 0.879 | 0.223 | 0.04193 | unknown |
| 20 | Large Pelagics | 4.53 | 0.54 | 4.82 | 0.9 | 0.901 | 0.112 | 5.023e-05 | unknown |
| 21 | Sharks & rays | 2.15 | 0.22 | 1.84 | 0.34 | 0.344 | 0.12 | 0.01466 | unknown |
| 22 | Seabirds | 0.01 | 0.4 | 66.67 | 0.03 | 0.0333 | 0.006 | 0 | unknown |
| 23 | Seals | 0 | 0.06 | 15 | 0.83 | - | 0.004 | 0.0001 | unknown |
| 24 | Cetaceans | 0.29 | 0.02 | 10 | 0.02 | 0.0166 | 0.002 | 9.65e-05 | unknown |
| 25 | Detritus | 100 | - | - | 0.33 | - | - | 0 | unknown |
