## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for HS_077_Pacific_Eastern_Central_high_seas_HS_077_1_Eastern_tropical_Pacific_(1993-1997), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 5 indeterminate, 6 warning(s), 1 note(s).

Biomass accumulation is unknown (-9999) for 38 of 38 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.126, group 29 (Miscellaneous piscivores).

Groups with recomputed EE > 1: 26 (Small dorado, 1.012), 29 (Miscellaneous piscivores, 1.076).

P/Q outside 0.02-0.5: 1 (Pursuit birds, 0.001), 2 (Grazing birds, 0.002), 3 (Baleen whales, 0.002), 4 (Toothed whales, 0.003), 5 (Spotted dolphin, 0.002), 6 (Mesopelagic dolphins, 0.002).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 13 (Large dorado): printed EE 0.25 vs recomputed 0.159 (diff 0.091) with BA unknown - a BA of +2.391e-05 t/km^2/year (+0.09 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Small marlins): printed EE 0.75 vs recomputed 0.677 (diff 0.073) with BA unknown - a BA of +5.273e-06 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 24 (Small sailfish): printed EE 0.75 vs recomputed 0.677 (diff 0.073) with BA unknown - a BA of +5.301e-06 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 26 (Small dorado): recomputed EE = 1.012 > 1 without BA, and BA is unknown - a BA of -0.0001381 t/km^2/year (-0.02 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 29 (Miscellaneous piscivores): recomputed EE = 1.076 > 1 without BA, and BA is unknown - a BA of -0.004705 t/km^2/year (-0.13 of production) would close it - undecidable until the source is checked for biomass accumulation

### Warnings

- group 1 (Pursuit birds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Grazing birds): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Baleen whales): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Toothed whales): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 5 (Spotted dolphin): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 6 (Mesopelagic dolphins): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 34 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Pursuit birds), 2 (Grazing birds), 5 (Spotted dolphin), 6 (Mesopelagic dolphins), 7 (Sea turtles), 8 (Large yellowfin tuna), 9 (Large bigeye tuna), 10 (Large marlins) ...

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Pursuit birds | 0.0006 | 0.08 | 65.7 | 0.233 | 0.227 | 0.00122 | 0 | unknown |
| 2 | Grazing birds | 0.000123 | 0.15 | 65.7 | 0.134 | 0.126 | 0.00228 | 0 | unknown |
| 3 | Baleen whales | 0.0091 | 0.02 | 9.1 | - | 0 | 0.0022 | 0 | unknown |
| 4 | Toothed whales | 0.031 | 0.02 | 6.8 | - | 0.000274 | 0.00294 | 1.7e-07 | unknown |
| 5 | Spotted dolphin | 0.0035 | 0.04 | 16.5 | 0.219 | 0.217 | 0.00242 | 3e-06 | unknown |
| 6 | Mesopelagic dolphins | 0.017 | 0.04 | 16.5 | 0.19 | 0.188 | 0.00242 | 2.5e-06 | unknown |
| 7 | Sea turtles | 0.00026 | 0.15 | 3.5 | 0.5 | 0.5 | 0.0429 | 7.9e-07 | unknown |
| 8 | Large yellowfin tuna | 0.0065 | 2.35 | 15.6 | 0.36 | 0.359 | 0.151 | 0.00536 | unknown |
| 9 | Large bigeye tuna | 0.009 | 0.76 | 13 | 0.33 | 0.33 | 0.0585 | 0.002127 | unknown |
| 10 | Large marlins | 0.000573 | 1 | 7.8 | 0.5 | 0.5 | 0.128 | 0.0002865 | unknown |
| 11 | Large sailfish | 5.2e-05 | 1.15 | 7.8 | 0.25 | 0.251 | 0.147 | 1.501e-05 | unknown |
| 12 | Large swordfish | 3.3e-05 | 0.44 | 7.8 | 0.75 | 0.753 | 0.0564 | 1.094e-05 | unknown |
| 13 | Large dorado | 0.000218 | 1.2 | 21.9 | 0.25 | 0.159 | 0.0548 | 6e-08 | unknown |
| 14 | Large wahoo | 0.0011 | 1.2 | 9.8 | 0.068 | 0.0646 | 0.122 | 7.499e-05 | unknown |
| 15 | Large sharks | 0.0004 | 0.32 | 7.8 | 0.479 | 0.479 | 0.041 | 6.129e-05 | unknown |
| 16 | Rays | 0.00023 | 0.25 | 3.9 | 0.361 | 0.361 | 0.0641 | 2.076e-05 | unknown |
| 17 | Skipjack tuna | 0.02644 | 1.88 | 21.5 | 0.4 | 0.4 | 0.0874 | 0.004073 | unknown |
| 18 | Albacore | 0.003026 | 0.77 | 17 | 0.75 | 0.753 | 0.0453 | 0.0004419 | unknown |
| 19 | Auxis spp. | 0.1432 | 2.5 | 25 | 0.95 | 0.953 | 0.1 | 7.698e-05 | unknown |
| 20 | Bluefin tuna | 0.0014 | 0.65 | 12.8 | 0.794 | 0.809 | 0.0508 | 4.514e-05 | unknown |
| 21 | Small yellowfin tuna | 0.0082 | 1.75 | 18.3 | 0.905 | 0.919 | 0.0956 | 0.002812 | unknown |
| 22 | Small bigeye tuna | 0.01 | 0.72 | 15.3 | 0.689 | 0.69 | 0.0471 | 0.000575 | unknown |
| 23 | Small marlins | 0.000145 | 0.5 | 9 | 0.75 | 0.677 | 0.0556 | 1.6e-07 | unknown |
| 24 | Small sailfish | 0.000127 | 0.57 | 9.8 | 0.75 | 0.677 | 0.0582 | 5e-08 | unknown |
| 25 | Small swordfish | 9.8e-05 | 0.21 | 9 | 0.75 | 0.718 | 0.0233 | 3.64e-06 | unknown |
| 26 | Small dorado | 0.002 | 3.15 | 27.4 | 0.99 | 1.01 | 0.115 | 6.109e-05 | unknown |
| 27 | Small wahoo | 0.00273 | 1.75 | 11.4 | 0.75 | 0.749 | 0.154 | 1.16e-05 | unknown |
| 28 | Small sharks | 0.00027 | 0.58 | 9.2 | 0.583 | 0.568 | 0.063 | 8.473e-05 | unknown |
| 29 | Miscellaneous piscivores | 0.01654 | 2.25 | 7.7 | 0.95 | 1.08 | 0.292 | 0.0002368 | unknown |
| 30 | Flyingfishes | 0.1606 | 2.88 | 25.8 | 0.95 | 0.972 | 0.112 | 0 | unknown |
| 31 | Misc. epipelagic fishes | 2.249 | 2.07 | 10.8 | 0.95 | 0.961 | 0.192 | 1.073e-05 | unknown |
| 32 | Misc. mesopelagic fishes | 2 | 2 | 10.8 | 0.927 | 0.925 | 0.185 | 0 | unknown |
| 33 | Cephalopods | 1.105 | 2 | 7 | 0.85 | 0.863 | 0.286 | 0 | unknown |
| 34 | Crabs | 0.1197 | 3.5 | 10 | 0.95 | 0.965 | 0.35 | 0 | unknown |
| 35 | Mesozooplankton | 0.7067 | 64 | 200 | 0.68 | 0.681 | 0.32 | 0 | unknown |
| 36 | Microzooplankton | 0.8264 | 143 | 600 | 0.98 | 0.98 | 0.238 | 0 | unknown |
| 37 | Large phytoplankton | 0.4261 | 125 | - | 0.9 | 0.9 | - | 0 | unknown |
| 38 | Small producers | 2.999 | 167 | - | 0.99 | 0.99 | - | 0 | unknown |
