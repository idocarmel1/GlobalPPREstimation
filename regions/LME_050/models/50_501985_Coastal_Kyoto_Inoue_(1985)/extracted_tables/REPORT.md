# Coastal Kyoto 1985

Source-faithful tabulated reconstruction, exact original model diet version unresolved. See ../REPORT.md.

## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 50_Sea_of_Japan_501985_Coastal_Kyoto_Inoue_(1985), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 22 indeterminate, 0 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 40 of 40 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 6.296, group 20 (Flying squid).

Groups with recomputed EE > 1: 10 (Spanish mackerel, 6.076), 20 (Flying squid, 6.596), 28 (Bivalve, 1.302), 29 (Dragonet, 1.212), 31 (Goby, 1.670).

P/Q outside 0.02-0.5: none.

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 1 (Sardine): printed EE 0.51 vs recomputed 0.203 (diff 0.307) with BA unknown - a BA of +24.35 t/km^2/year (+0.31 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 2 (Round herring): printed EE 0.77 vs recomputed 0.135 (diff 0.635) with BA unknown - a BA of +0.5483 t/km^2/year (+0.63 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 3 (Anchovy): printed EE 0.46 vs recomputed 0.533 (diff 0.073) with BA unknown - a BA of -0.9457 t/km^2/year (-0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 4 (Mackerel): printed EE 0.78 vs recomputed 0.439 (diff 0.341) with BA unknown - a BA of +0.9618 t/km^2/year (+0.34 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 5 (Jack mackerel): printed EE 0.56 vs recomputed 0.306 (diff 0.254) with BA unknown - a BA of +0.5595 t/km^2/year (+0.25 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 6 (Yellowtail): printed EE 0.6 vs recomputed 0.451 (diff 0.149) with BA unknown - a BA of +0.09443 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 9 (Sailfish): printed EE 0.46 vs recomputed 0.401 (diff 0.059) with BA unknown - a BA of +0.001904 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 10 (Spanish mackerel): recomputed EE = 6.076 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 11 (Stingray): printed EE 0.63 vs recomputed 0.564 (diff 0.066) with BA unknown - a BA of +0.000514 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 13 (Black porgy): printed EE 0.5 vs recomputed 0.631 (diff 0.131) with BA unknown - a BA of -0.00092 t/km^2/year (-0.13 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 15 (Tilefish): printed EE 0.5 vs recomputed 0.576 (diff 0.076) with BA unknown - a BA of -0.00016 t/km^2/year (-0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 18 (Rockfish): printed EE 0.53 vs recomputed 0.590 (diff 0.060) with BA unknown - a BA of -0.002517 t/km^2/year (-0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 19 (Barracuda): printed EE 0.8 vs recomputed 0.462 (diff 0.338) with BA unknown - a BA of +0.2754 t/km^2/year (+0.34 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 20 (Flying squid): recomputed EE = 6.596 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 21 (Other squids): printed EE 0.41 vs recomputed 0.554 (diff 0.144) with BA unknown - a BA of -0.3857 t/km^2/year (-0.14 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 22 (Octopus): printed EE 0.46 vs recomputed 0.092 (diff 0.368) with BA unknown - a BA of +0.1618 t/km^2/year (+0.37 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 27 (Prawn): printed EE 0.28 vs recomputed 0.123 (diff 0.157) with BA unknown - a BA of +0.03297 t/km^2/year (+0.16 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 28 (Bivalve): recomputed EE = 1.302 > 1 without BA, and BA is unknown - a BA of -0.1506 t/km^2/year (-0.60 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 29 (Dragonet): recomputed EE = 1.212 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 31 (Goby): recomputed EE = 1.670 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 38 (Zooplankton): printed EE 0.86 vs recomputed 0.682 (diff 0.178) with BA unknown - a BA of +123.3 t/km^2/year (+0.18 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 39 (Phytoplankton): printed EE 0.5 vs recomputed 0.556 (diff 0.056) with BA unknown - a BA of -231.4 t/km^2/year (-0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Notes

- 38 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Sardine), 2 (Round herring), 3 (Anchovy), 4 (Mackerel), 5 (Jack mackerel), 6 (Yellowtail), 7 (Frigate tuna), 8 (Tuna) ...
- detritus pools (1): inflow ~2878, consumption ~58.1 t/km^2/year, implied EE ~0.020 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Sardine | 114.9 | 0.69 | 5.8 | 0.51 | 0.203 | 0.119 | 15.76 | unknown |
| 2 | Round herring | 0.24 | 3.6 | 12.75 | 0.77 | 0.135 | 0.282 | 0.115 | unknown |
| 3 | Anchovy | 4.36 | 2.96 | 11.39 | 0.46 | 0.533 | 0.26 | 1.963 | unknown |
| 4 | Mackerel | 4.27 | 0.66 | 6.14 | 0.78 | 0.439 | 0.107 | 1.217 | unknown |
| 5 | Jack mackerel | 1.45 | 1.52 | 5.97 | 0.56 | 0.306 | 0.255 | 0.442 | unknown |
| 6 | Yellowtail | 0.68 | 0.93 | 4.87 | 0.6 | 0.451 | 0.191 | 0.285 | unknown |
| 7 | Frigate tuna | 0.34 | 1.08 | 5.61 | 0.5 | 0.499 | 0.193 | 0.1693 | unknown |
| 8 | Tuna | 0.13 | 1.08 | 8.79 | 0.46 | 0.463 | 0.123 | 0.065 | unknown |
| 9 | Sailfish | 0.03 | 1.08 | 8.44 | 0.46 | 0.401 | 0.128 | 0.013 | unknown |
| 10 | Spanish mackerel | 0.09 | 0.93 | 6.22 | 0.45 | 6.08 | 0.15 | 0.038 | unknown |
| 11 | Stingray | 0.02 | 0.39 | 5.01 | 0.63 | 0.564 | 0.0778 | 0.0044 | unknown |
| 12 | Flounder | 0.07 | 0.56 | 2.26 | 0.7 | 0.667 | 0.248 | 0.02614 | unknown |
| 13 | Black porgy | 0.01 | 0.7 | 3.55 | 0.5 | 0.631 | 0.197 | 0.00442 | unknown |
| 14 | Red seabream | 0.05 | 0.41 | 2.38 | 0.86 | 0.833 | 0.172 | 0.01708 | unknown |
| 15 | Tilefish | 0.003 | 0.7 | 3.88 | 0.5 | 0.576 | 0.18 | 0.00121 | unknown |
| 16 | Seabass | 0.02 | 0.7 | 4.43 | 0.64 | 0.614 | 0.158 | 0.00804 | unknown |
| 17 | Flying fish | 1.63 | 0.69 | 4.49 | 0.45 | 0.44 | 0.154 | 0.495 | unknown |
| 18 | Rockfish | 0.06 | 0.7 | 3.81 | 0.53 | 0.59 | 0.184 | 0.023 | unknown |
| 19 | Barracuda | 1.18 | 0.69 | 4.49 | 0.8 | 0.462 | 0.154 | 0.3592 | unknown |
| 20 | Flying squid | 0.04 | 4 | 25 | 0.3 | 6.6 | 0.16 | 0.0142 | unknown |
| 21 | Other squids | 0.67 | 4 | 25 | 0.41 | 0.554 | 0.16 | 0.2272 | unknown |
| 22 | Octopus | 0.11 | 4 | 25 | 0.46 | 0.0923 | 0.16 | 0.0382 | unknown |
| 23 | Ivory shell | 0.02 | 1.5 | 5 | 0 | 0 | 0.3 | 0 | unknown |
| 24 | Sea cucumber | 0.35 | 0.64 | 2.13 | 0.38 | 0.385 | 0.3 | 0.0863 | unknown |
| 25 | Other conch | 0.06 | 1.5 | 5 | 0.68 | 0.64 | 0.3 | 0.01403 | unknown |
| 26 | Crab | 0.2 | 3 | 10 | 0.12 | 0.0875 | 0.3 | 0.04832 | unknown |
| 27 | Prawn | 0.07 | 3 | 10 | 0.28 | 0.123 | 0.3 | 0.01603 | unknown |
| 28 | Bivalve | 0.05 | 5 | 16.67 | 0.7 | 1.3 | 0.3 | 0.012 | unknown |
| 29 | Dragonet | 0.0004 | 2.96 | 14.73 | 0.16 | 1.21 | 0.201 | 0 | unknown |
| 30 | Tongue sole | 0.001 | 2.96 | 14.08 | 0.01 | 0.00299 | 0.21 | 0 | unknown |
| 31 | Goby | 0.001 | 3.5 | 24.46 | 0.01 | 1.67 | 0.143 | 0 | unknown |
| 32 | Shrimp | 0.08 | 3 | 10 | 0.51 | 0.539 | 0.3 | 0 | unknown |
| 33 | Starfish | 0.14 | 0.17 | 0.57 | 0.02 | 0.0149 | 0.298 | 0 | unknown |
| 34 | Brittle star | 29.99 | 0.2 | 0.67 | 0 | 0.00152 | 0.299 | 0 | unknown |
| 35 | Polychaeta | 9.53 | 1 | 3.33 | 0.12 | 0.127 | 0.3 | 0 | unknown |
| 36 | Hermit crab | 0.04 | 3 | 10 | 0.02 | 0.0196 | 0.3 | 0 | unknown |
| 37 | Mysid | 0.01 | 45 | 150 | 0.1 | 0.116 | 0.3 | 0 | unknown |
| 38 | Zooplankton | 15 | 46.21 | 154 | 0.86 | 0.682 | 0.3 | 0 | unknown |
| 39 | Phytoplankton | 64.83 | 64.21 | - | 0.5 | 0.556 | - | 0 | unknown |
| 40 | Detritus | 43 | - | - | 0.1 | - | - | 0 | unknown |
