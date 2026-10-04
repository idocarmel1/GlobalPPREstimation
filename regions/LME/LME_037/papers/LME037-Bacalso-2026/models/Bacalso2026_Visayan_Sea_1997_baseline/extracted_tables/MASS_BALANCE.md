## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 37_3702026_Visayan_Sea_Bacalso_baseline_(1997), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 1 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 33 of 33 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.009, group 21 (Jellyfish).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Seabirds, 0.006).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 1 (Seabirds): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 30 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Seabirds), 2 (Sharks (juveniles/young adults)), 3 (Rays), 4 (Pel-pred fish (i)), 5 (Pel-pred fish (a)), 6 (Anchovies), 7 (Sardines (i)), 8 (Sardines (a)) ...
- detritus pools (1): inflow ~1208, consumption ~525.4 t/km^2/year, implied EE ~0.435 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Seabirds | 0.002 | 0.4 | 64 | 0.02 | 0.0241 | 0.00625 | 0 | unknown |
| 2 | Sharks (juveniles/young adults) | 0.028 | 0.92 | 6.87 | 0.46 | 0.464 | 0.134 | 0.011 | unknown |
| 3 | Rays | 0.053 | 1.61 | 7.62 | 0.54 | 0.535 | 0.211 | 0.036 | unknown |
| 4 | Pel-pred fish (i) | 0.076 | 1.66 | 19.88 | 0.55 | 0.549 | 0.0835 | 0.048 | unknown |
| 5 | Pel-pred fish (a) | 0.029 | 1.96 | 11.56 | 0.64 | 0.644 | 0.17 | 0.035 | unknown |
| 6 | Anchovies | 1.747 | 3.26 | 22.4 | 0.9 | 0.9 | 0.146 | 0.576 | unknown |
| 7 | Sardines (i) | 0.978 | 3.15 | 33.83 | 0.96 | 0.955 | 0.0931 | 0.925 | unknown |
| 8 | Sardines (a) | 0.73 | 4.72 | 19.07 | 0.63 | 0.633 | 0.248 | 2.048 | unknown |
| 9 | Mackerels (i) | 0.755 | 3.1 | 34.32 | 0.9 | 0.898 | 0.0903 | 0.858 | unknown |
| 10 | Mackerels (a) | 0.411 | 4.2 | 19.03 | 0.7 | 0.699 | 0.221 | 1.167 | unknown |
| 11 | Scads (i) | 0.805 | 2.75 | 31.31 | 0.67 | 0.668 | 0.0878 | 0.826 | unknown |
| 12 | Scads (a) | 0.63 | 3.25 | 17.6 | 0.64 | 0.638 | 0.185 | 1.241 | unknown |
| 13 | Demersal fish (>30 cm) | 0.296 | 2.14 | 10.44 | 0.67 | 0.676 | 0.205 | 0.292 | unknown |
| 14 | Demersal fish (<30 cm) | 1.665 | 3.92 | 16.04 | 0.86 | 0.861 | 0.244 | 3.342 | unknown |
| 15 | Jacks - barracudas | 0.286 | 2.24 | 13.6 | 0.46 | 0.458 | 0.165 | 0.27 | unknown |
| 16 | Reef-associated carnivorous - piscivorous fish (>30 cm) | 0.331 | 2.08 | 9.82 | 0.61 | 0.609 | 0.212 | 0.324 | unknown |
| 17 | Reef-associated zoobenthos-feeding fish (<30 cm) | 1.326 | 2.64 | 16.92 | 0.79 | 0.788 | 0.156 | 1.195 | unknown |
| 18 | Reef-associated herbivorous fish | 0.258 | 1.83 | 34 | 0.59 | 0.586 | 0.0538 | 0.067 | unknown |
| 19 | Rabbitfish | 0.066 | 2.9 | 37.06 | 0.79 | 0.782 | 0.0783 | 0.074 | unknown |
| 20 | Reef-associated planktivorous fish | 0.377 | 2.14 | 18.04 | 0.67 | 0.667 | 0.119 | 0.176 | unknown |
| 21 | Jellyfish | 0.013 | 6.5 | 26 | 0.9 | 0.909 | 0.25 | 0 | unknown |
| 22 | Octopus | 0.121 | 2.32 | 13.2 | 0.85 | 0.851 | 0.176 | 0.024 | unknown |
| 23 | Squids | 0.471 | 2.72 | 14.79 | 0.9 | 0.9 | 0.184 | 0.555 | unknown |
| 24 | Marine crabs | 2.089 | 3.5 | 16.2 | 0.9 | 0.9 | 0.216 | 0.337 | unknown |
| 25 | Shrimps | 6.69 | 3.26 | 19 | 0.9 | 0.9 | 0.172 | 0.363 | unknown |
| 26 | Mollusks | 5.279 | 3.92 | 15.75 | 0.9 | 0.9 | 0.249 | 0.268 | unknown |
| 27 | Other epibenthos | 4.896 | 2.28 | 12.25 | 0.9 | 0.9 | 0.186 | 0.061 | unknown |
| 28 | Worms - infauna | 15.99 | 6.5 | 25 | 0.9 | 0.9 | 0.26 | 0 | unknown |
| 29 | Sessile benthos | 11.22 | 1.75 | 15 | 0.5 | 0.5 | 0.117 | 0.041 | unknown |
| 30 | Zooplankton | 14.57 | 33 | 145 | 0.95 | 0.95 | 0.228 | 0 | unknown |
| 31 | Phytoplankton | 16.07 | 135 | - | 0.86 | 0.864 | - | 0 | unknown |
| 32 | Benthic primary producers | 26.75 | 15 | - | 0.5 | 0.5 | - | 0 | unknown |
| 33 | Detritus | 86.28 | - | - | 0.44 | - | - | 0 | unknown |
