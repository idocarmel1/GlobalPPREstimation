## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 50_Sea_of_Japan_502013_Coastal_Kyoto_Inoue_(2013), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 6 indeterminate, 0 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 40 of 40 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.179, group 26 (Crab).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: none.

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 12 (Flounder): printed EE 0.76 vs recomputed 0.687 (diff 0.073) with BA unknown - a BA of +0.001624 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 13 (Black porgy): printed EE 0.47 vs recomputed 0.524 (diff 0.054) with BA unknown - a BA of -0.00113 t/km^2/year (-0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Ivory shell): printed EE 0.16 vs recomputed 0.333 (diff 0.173) with BA unknown - a BA of -5.2e-06 t/km^2/year (-0.17 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 26 (Crab): printed EE 0.68 vs recomputed 0.501 (diff 0.179) with BA unknown - a BA of +0.00537 t/km^2/year (+0.18 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 27 (Prawn): printed EE 0.63 vs recomputed 0.485 (diff 0.145) with BA unknown - a BA of +0.00872 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 37 (Mysid): printed EE 0.44 vs recomputed 0.610 (diff 0.170) with BA unknown - a BA of -0.07671 t/km^2/year (-0.17 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Notes

- 38 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Sardine), 2 (Round herring), 3 (Anchovy), 4 (Mackerel), 5 (Jack mackerel), 6 (Yellowtail), 7 (Frigate tuna), 8 (Tuna) ...
- detritus pools (1): inflow ~1339, consumption ~43.99 t/km^2/year, implied EE ~0.033 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Sardine | 0.85 | 0.69 | 5.8 | 0.86 | 0.867 | 0.119 | 0.286 | unknown |
| 2 | Round herring | 0.004 | 3.6 | 12.75 | 0.85 | 0.807 | 0.282 | 0.002 | unknown |
| 3 | Anchovy | 1.95 | 2.96 | 11.39 | 0.83 | 0.829 | 0.26 | 1.016 | unknown |
| 4 | Mackerel | 0.13 | 1.08 | 6.14 | 0.82 | 0.795 | 0.176 | 0.0544 | unknown |
| 5 | Jack mackerel | 0.82 | 2 | 5.97 | 0.87 | 0.863 | 0.335 | 0.3191 | unknown |
| 6 | Yellowtail | 1.41 | 0.93 | 4.87 | 0.42 | 0.416 | 0.191 | 0.546 | unknown |
| 7 | Frigate tuna | 0.15 | 1.08 | 5.61 | 0.33 | 0.324 | 0.193 | 0.043 | unknown |
| 8 | Tuna | 0.08 | 1.08 | 8.79 | 0.27 | 0.255 | 0.123 | 0.022 | unknown |
| 9 | Sailfish | 0.03 | 1.08 | 8.44 | 0.27 | 0.247 | 0.128 | 0.008 | unknown |
| 10 | Spanish mackerel | 1.99 | 0.93 | 6.22 | 0.84 | 0.837 | 0.15 | 0.767 | unknown |
| 11 | Stingray | 2e-05 | 0.39 | 5.01 | 0.63 | 0.641 | 0.0778 | 5e-06 | unknown |
| 12 | Flounder | 0.04 | 0.56 | 2.26 | 0.76 | 0.687 | 0.248 | 0.0154 | unknown |
| 13 | Black porgy | 0.03 | 0.7 | 3.55 | 0.47 | 0.524 | 0.197 | 0.011 | unknown |
| 14 | Red seabream | 0.1 | 0.41 | 2.38 | 0.81 | 0.805 | 0.172 | 0.033 | unknown |
| 15 | Tilefish | 0.03 | 0.7 | 3.88 | 0.47 | 0.501 | 0.18 | 0.01052 | unknown |
| 16 | Seabass | 0.14 | 0.7 | 4.43 | 0.68 | 0.669 | 0.158 | 0.0532 | unknown |
| 17 | Flying fish | 0.25 | 0.69 | 4.49 | 0.57 | 0.57 | 0.154 | 0.0984 | unknown |
| 18 | Rockfish | 0.05 | 0.7 | 3.81 | 0.69 | 0.731 | 0.184 | 0.02 | unknown |
| 19 | Barracuda | 0.49 | 0.69 | 4.49 | 0.69 | 0.696 | 0.154 | 0.1922 | unknown |
| 20 | Flying squid | 0.51 | 4 | 25 | 0.57 | 0.571 | 0.16 | 0.065 | unknown |
| 21 | Other squids | 1.73 | 4 | 25 | 0.27 | 0.27 | 0.16 | 0.219 | unknown |
| 22 | Octopus | 0.26 | 4 | 25 | 0.04 | 0.0411 | 0.16 | 0.0331 | unknown |
| 23 | Ivory shell | 2e-05 | 1.5 | 5 | 0.16 | 0.333 | 0.3 | 1e-05 | unknown |
| 24 | Sea cucumber | 0.2 | 0.64 | 2.13 | 0.38 | 0.391 | 0.3 | 0.05 | unknown |
| 25 | Other conch | 0.1 | 1.5 | 5 | 0.68 | 0.684 | 0.3 | 0.025 | unknown |
| 26 | Crab | 0.01 | 3 | 10 | 0.68 | 0.501 | 0.3 | 0.00207 | unknown |
| 27 | Prawn | 0.02 | 3 | 10 | 0.63 | 0.485 | 0.3 | 0.0042 | unknown |
| 28 | Bivalve | 0.42 | 3 | 10 | 0.64 | 0.64 | 0.3 | 0.104 | unknown |
| 29 | Dragonet | 0.01 | 2.96 | 14.73 | 0.14 | 0.105 | 0.201 | 0 | unknown |
| 30 | Tongue sole | 0.02 | 2.96 | 14.08 | 0 | 0.00105 | 0.21 | 0 | unknown |
| 31 | Goby | 0.01 | 2.96 | 24.46 | 0.18 | 0.21 | 0.121 | 0 | unknown |
| 32 | Shrimp | 0.14 | 3 | 10 | 0.71 | 0.702 | 0.3 | 0 | unknown |
| 33 | Starfish | 0.07 | 0.17 | 0.57 | 0.1 | 0.0895 | 0.298 | 0 | unknown |
| 34 | Brittle star | 10.9 | 0.2 | 0.67 | 0.01 | 0.00717 | 0.299 | 0 | unknown |
| 35 | Polychaeta | 8.74 | 1 | 3.33 | 0.1 | 0.0999 | 0.3 | 0 | unknown |
| 36 | Hermit crab | 0.02 | 3 | 10 | 0.15 | 0.141 | 0.3 | 0 | unknown |
| 37 | Mysid | 0.01 | 45 | 150 | 0.44 | 0.61 | 0.3 | 0 | unknown |
| 38 | Zooplankton | 5.82 | 46.21 | 154 | 0.24 | 0.242 | 0.3 | 0 | unknown |
| 39 | Phytoplankton | 28.06 | 64.21 | - | 0.5 | 0.5 | - | 0 | unknown |
| 40 | Detritus | 43 | - | - | 0.03 | - | - | 0 | unknown |
