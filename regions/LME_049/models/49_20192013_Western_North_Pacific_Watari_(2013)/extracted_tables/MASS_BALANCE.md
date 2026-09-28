## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 49_Kuroshio_Current_20192013_Western_North_Pacific_Watari_(2013), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 5 indeterminate, 3 warning(s), 3 note(s).

Biomass accumulation is unknown (-9999) for 41 of 41 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.450, group 21 (Seabreams (KC)).

Groups with recomputed EE > 1: 16 (Righteye flounders (OYC), 1.001).

P/Q outside 0.02-0.5: 1 (Baleen whales (OYC & OF), 0.014), 2 (Toothed whales (all), 0.010), 3 (Seabirds (all), 0.003).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 1 (Baleen whales (OYC & OF)): printed EE 0.08 vs recomputed 0.000 (diff 0.080) with BA unknown - a BA of +0.0007168 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 5 (Tunas (all)): printed EE 0.75 vs recomputed 0.888 (diff 0.138) with BA unknown - a BA of -0.001825 t/km^2/year (-0.14 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 16 (Righteye flounders (OYC)): recomputed EE = 1.001 > 1 without BA, and BA is unknown - a BA of -0.002116 t/km^2/year (-0.03 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 20 (Flatfishes (KC)): printed EE 0.95 vs recomputed 0.652 (diff 0.298) with BA unknown - a BA of +0.002004 t/km^2/year (+0.30 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 21 (Seabreams (KC)): printed EE 0.45 vs recomputed 0.000 (diff 0.450) with BA unknown - a BA of +0.002952 t/km^2/year (+0.45 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 1 (Baleen whales (OYC & OF)): P/Q = 0.014 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Toothed whales (all)): P/Q = 0.010 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Seabirds (all)): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 1 consumer(s) lack B or Q/B, so predation on their prey is under-counted and every recomputed EE below is a lower bound: 3 (Seabirds (all))
- 34 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Baleen whales (OYC & OF)), 2 (Toothed whales (all)), 4 (Sharks (all)), 5 (Tunas (all)), 6 (Skipjack (all)), 7 (Miscellaneous piscivores (all)), 8 (Yellowtail (OYC & KC)), 9 (Japanese sardine (all)) ...
- detritus pools (3): inflow ~1076, consumption ~53.92 t/km^2/year, implied EE ~0.050 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Baleen whales (OYC & OF) | 0.128 | 0.07 | 5.1 | 0.08 | 0 | 0.0137 | 0 | unknown |
| 2 | Toothed whales (all) | 0.25 | 0.08 | 8.16 | 0.01 | 0 | 0.0098 | 0 | unknown |
| 3 | Seabirds (all) | - | 0.12 | 36.67 | 0 | - | 0.00327 | 0 | unknown |
| 4 | Sharks (all) | 0.2 | 0.39 | 2.19 | 0.09 | 0.128 | 0.178 | 0.01 | unknown |
| 5 | Tunas (all) | 0.04 | 0.33 | 6.75 | 0.75 | 0.888 | 0.0489 | 0.01 | unknown |
| 6 | Skipjack (all) | 0.09 | 0.46 | 16.2 | 0.77 | 0.766 | 0.0284 | 0.03 | unknown |
| 7 | Miscellaneous piscivores (all) | 0.53 | 0.52 | 5 | 0.62 | 0.645 | 0.104 | 0.02 | unknown |
| 8 | Yellowtail (OYC & KC) | 0.108 | 0.93 | 3.1 | 0.56 | 0.597 | 0.3 | 0.06 | unknown |
| 9 | Japanese sardine (all) | 0.78 | 0.69 | 2.3 | 0.98 | 0.975 | 0.3 | 0.14 | unknown |
| 10 | Japanese anchovy (all) | 0.68 | 2.96 | 9.87 | 0.96 | 0.967 | 0.3 | 0.2 | unknown |
| 11 | Pacific saury (all) | 0.94 | 1.25 | 4.17 | 0.79 | 0.791 | 0.3 | 0.46 | unknown |
| 12 | Chub mackerel (all) | 1.49 | 0.66 | 2.2 | 0.74 | 0.733 | 0.3 | 0.25 | unknown |
| 13 | Spotted mackerel (all) | 0.86 | 0.64 | 2.13 | 0.97 | 0.959 | 0.3 | 0.11 | unknown |
| 14 | Round herring (KC) | 0.07 | 3.6 | 12 | 0.45 | 0.46 | 0.3 | 0.04 | unknown |
| 15 | Jack mackerel (OYC & KC) | 0.064 | 1.52 | 5.07 | 0.96 | 0.955 | 0.3 | 0.04 | unknown |
| 16 | Righteye flounders (OYC) | 0.164 | 0.42 | 1.4 | 0.97 | 1 | 0.3 | 0.02 | unknown |
| 17 | Walleye pollock (OYC) | 0.978 | 0.44 | 1.47 | 0.26 | 0.247 | 0.299 | 0.08 | unknown |
| 18 | Pacific cod (OYC) | 0.3 | 0.45 | 1.51 | 0.79 | 0.788 | 0.298 | 0.03 | unknown |
| 19 | Miscellaneous bottom fishes (OYC) | 0.606 | 0.45 | 1.51 | 0.87 | 0.874 | 0.298 | 0.03 | unknown |
| 20 | Flatfishes (KC) | 0.012 | 0.56 | 1.87 | 0.95 | 0.652 | 0.299 | 0 | unknown |
| 21 | Seabreams (KC) | 0.016 | 0.41 | 1.36 | 0.45 | 0 | 0.301 | 0 | unknown |
| 22 | Demersal piscivores (KC) | 0.056 | 0.7 | 2.32 | 0.95 | 0.953 | 0.302 | 0.01 | unknown |
| 23 | Miscellaneous bottom fishes (KC) | 0.416 | 0.7 | 2.32 | 0.97 | 0.958 | 0.302 | 0.02 | unknown |
| 24 | Mesopelagic fishes (OYC) | 1.188 | 1.5 | 6 | 0.9 | 0.897 | 0.25 | 0 | unknown |
| 25 | Mesopelagic fishes (KC) | 0.998 | 1.5 | 6 | 0.9 | 0.895 | 0.25 | 0 | unknown |
| 26 | Mesopelagic fishes (OF) | 0.864 | 1.5 | 6 | 0.9 | 0.903 | 0.25 | 0 | unknown |
| 27 | Epipelagic cephalopods (all) | 0.68 | 2.56 | 7.3 | 0.95 | 0.952 | 0.351 | 0.11 | unknown |
| 28 | Mesopelagic cephalopods (all) | 0.52 | 3.5 | 13.64 | 0.95 | 0.951 | 0.257 | 0 | unknown |
| 29 | Benthos (OYC) | 1.544 | 3.44 | 11.47 | 0.9 | 0.901 | 0.3 | 0.01 | unknown |
| 30 | Benthos (KC) | 2.74 | 3.22 | 10.73 | 0.61 | 0.609 | 0.3 | 0.01 | unknown |
| 31 | Krill (OYC) | 3.862 | 2.56 | 12.05 | 0.88 | 0.879 | 0.212 | 0.03 | unknown |
| 32 | Krill (OF) | 4.83 | 2.56 | 12.05 | 0.5 | 0.499 | 0.212 | 0 | unknown |
| 33 | Zooplankton (OYC) | 7.13 | 5.8 | 19.33 | 0.31 | 0.314 | 0.3 | 0 | unknown |
| 34 | Zooplankton (KC) | 5.804 | 5.8 | 19.33 | 0.36 | 0.358 | 0.3 | 0 | unknown |
| 35 | Zooplankton (OF) | 25.13 | 5.8 | 19.33 | 0.13 | 0.13 | 0.3 | 0 | unknown |
| 36 | Phytoplankton (OYC) | 2.712 | 153.8 | - | 0.41 | 0.413 | - | 0 | unknown |
| 37 | Phytoplankton (KC) | 2.002 | 128.3 | - | 0.45 | 0.449 | - | 0 | unknown |
| 38 | Phytoplankton (OF) | 5.424 | 153.8 | - | 0.63 | 0.631 | - | 0 | unknown |
| 39 | Detritus (OYC) | 9.582 | - | - | - | - | - | 0 | unknown |
| 40 | Detritus (KC) | 6.036 | - | - | - | - | - | 0 | unknown |
| 41 | Detritus (OF) | 28.5 | - | - | - | - | - | 0 | unknown |
