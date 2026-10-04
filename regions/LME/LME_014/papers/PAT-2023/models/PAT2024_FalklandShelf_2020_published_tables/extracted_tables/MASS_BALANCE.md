## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 14_Patagonian_Shelf_PAT2024-tables_Falkland_Shelf_(2020), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 12 indeterminate, 2 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 36 of 36 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.519, group 6 (Grenadier).

Groups with recomputed EE > 1: 3 (Blue whiting (Micromesistius australis), 1.108), 9 (Hoki, 1.021), 13 (Kingclip (Genypterus blacodes), 1.420), 18 (Myctophidae, 1.001), 23 (Red cod (Salilota australis), 1.080), 24 (Rock cod (Patagonotothen ramsayi), 1.000).

P/Q outside 0.02-0.5: 25 (Seabirds, 0.017), 33 (Toothfish juv (Dissostichus eleginoides), 0.590).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 3 (Blue whiting (Micromesistius australis)): recomputed EE = 1.108 > 1 without BA, and BA is unknown - a BA of -0.0008718 t/km^2/year (-0.18 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 6 (Grenadier): printed EE 0.8 vs recomputed 0.281 (diff 0.519) with BA unknown - a BA of +0.00166 t/km^2/year (+0.52 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 9 (Hoki): recomputed EE = 1.021 > 1 without BA, and BA is unknown - a BA of -0.003799 t/km^2/year (-0.04 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 13 (Kingclip (Genypterus blacodes)): recomputed EE = 1.420 > 1 without BA, and BA is unknown - a BA of -0.002578 t/km^2/year (-0.43 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 17 (Doryteuthis gahi SSC): printed EE 0.91 vs recomputed 0.786 (diff 0.124) with BA unknown - a BA of +0.1492 t/km^2/year (+0.12 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 18 (Myctophidae): recomputed EE = 1.001 > 1 without BA, and BA is unknown - a BA of -0.02771 t/km^2/year (-0.02 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 19 (Octopods): printed EE 0.95 vs recomputed 0.871 (diff 0.079) with BA unknown - a BA of +0.006341 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 21 (Penguins): printed EE 0.53 vs recomputed 0.470 (diff 0.060) with BA unknown - a BA of +0.0006712 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Red cod (Salilota australis)): recomputed EE = 1.080 > 1 without BA, and BA is unknown - a BA of -0.002849 t/km^2/year (-0.10 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 24 (Rock cod (Patagonotothen ramsayi)): recomputed EE = 1.000 > 1 without BA, and BA is unknown - a BA of -0.001237 t/km^2/year (-0.03 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 31 (Squid): printed EE 0.9 vs recomputed 0.840 (diff 0.060) with BA unknown - a BA of +0.0148 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 33 (Toothfish juv (Dissostichus eleginoides)): printed EE 0.85 vs recomputed 0.785 (diff 0.065) with BA unknown - a BA of +0.0001917 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 25 (Seabirds): P/Q = 0.017 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 33 (Toothfish juv (Dissostichus eleginoides)): P/Q = 0.590 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 32 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Baleen whales), 2 (Benthic crustaceans), 3 (Blue whiting (Micromesistius australis)), 4 (Dogfish), 5 (Flounder), 6 (Grenadier), 7 (Hake Austral (Merluccius australis)), 8 (Hake common (Merluccius hubbsi)) ...
- detritus pools (2): inflow ~902.7, consumption ~43.45 t/km^2/year, implied EE ~0.048 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Baleen whales | 0.002 | 0.8 | 10 | 0 | 0 | 0.08 | 0 | unknown |
| 2 | Benthic crustaceans | 1.37 | 2.5 | 11 | 0.9 | 0.907 | 0.227 | 0.0002 | unknown |
| 3 | Blue whiting (Micromesistius australis) | 0.01 | 0.49 | 2.7 | 0.93 | 1.11 | 0.181 | 0.0003 | unknown |
| 4 | Dogfish | 0.05 | 0.32 | 3.7 | 0.03 | 0.025 | 0.0865 | 0.0004 | unknown |
| 5 | Flounder | 0 | 0.65 | 3.1 | 0.09 | - | 0.21 | 0 | unknown |
| 6 | Grenadier | 0.02 | 0.16 | 2.8 | 0.8 | 0.281 | 0.0571 | 0.0009 | unknown |
| 7 | Hake Austral (Merluccius australis) | 0 | 0.34 | 1.8 | 0.27 | - | 0.189 | 0.0003 | unknown |
| 8 | Hake common (Merluccius hubbsi) | 1.18 | 0.25 | 2.3 | 0.98 | 0.956 | 0.109 | 0.2176 | unknown |
| 9 | Hoki | 0.31 | 0.3 | 2.3 | 0.98 | 1.02 | 0.13 | 0.0386 | unknown |
| 10 | Illex argentinus | 0.66 | 6.5 | 16 | 0.31 | 0.309 | 0.406 | 0.3451 | unknown |
| 11 | Jellyfish | 0.01 | 6 | 15 | 0.95 | 0.974 | 0.4 | 0 | unknown |
| 12 | Kelp (Macrocystis pyrifera) | 100 | 7 | - | 0.01 | 0.0064 | - | 0 | unknown |
| 13 | Kingclip (Genypterus blacodes) | 0.05 | 0.12 | 1.6 | 0.99 | 1.42 | 0.075 | 0.0083 | unknown |
| 14 | Large Demersal fish | 0.14 | 0.35 | 2.7 | 0.8 | 0.84 | 0.13 | 0.0003 | unknown |
| 15 | Large Zoobenthos | 0.66 | 1.1 | 10 | 0.65 | 0.649 | 0.11 | 0 | unknown |
| 16 | Doryteuthis gahi ASC | 0.1782 | 3.5 | 11 | 0.91 | 0.915 | 0.318 | 0.1501 | unknown |
| 17 | Doryteuthis gahi SSC | 0.3432 | 3.5 | 11 | 0.91 | 0.786 | 0.318 | 0.1548 | unknown |
| 18 | Myctophidae | 2.21 | 0.6 | 5 | 0.98 | 1 | 0.12 | 0 | unknown |
| 19 | Octopods | 0.04 | 2 | 5 | 0.95 | 0.871 | 0.4 | 0 | unknown |
| 20 | Pelagic fish | 0.66 | 0.37 | 5.6 | 0.95 | 0.943 | 0.0661 | 0.0039 | unknown |
| 21 | Penguins | 0.0075 | 1.5 | 65 | 0.53 | 0.47 | 0.0231 | 0 | unknown |
| 22 | Phytoplankton | 3.26 | 80 | - | 0.4 | 0.399 | - | 0 | unknown |
| 23 | Red cod (Salilota australis) | 0.11 | 0.26 | 2.9 | 0.98 | 1.08 | 0.0897 | 0.0072 | unknown |
| 24 | Rock cod (Patagonotothen ramsayi) | 0.11 | 0.37 | 3.2 | 0.97 | 1 | 0.116 | 0.004 | unknown |
| 25 | Seabirds | 0.02 | 1.22 | 70 | 0.04 | 0.0349 | 0.0174 | 0 | unknown |
| 26 | Seals and Sea Lion | 0.02 | 0.4 | 17.44 | 0 | 0 | 0.0229 | 0 | unknown |
| 27 | Sharks | 0 | 0.08 | 0.85 | 0.04 | - | 0.0941 | 0 | unknown |
| 28 | Skates | 0.07 | 0.22 | 2.1 | 0.77 | 0.74 | 0.105 | 0.0071 | unknown |
| 29 | Small Demersal fish | 0.39 | 0.37 | 6.5 | 0.95 | 0.994 | 0.0569 | 0 | unknown |
| 30 | Small Zoobenthos | 2.14 | 3 | 11 | 0.85 | 0.853 | 0.273 | 0.0001 | unknown |
| 31 | Squid | 0.07 | 3.5 | 10 | 0.9 | 0.84 | 0.35 | 0 | unknown |
| 32 | Toothed Whales and dolphins | 0.002 | 0.42 | 10.46 | 0.01 | 0 | 0.0402 | 0 | unknown |
| 33 | Toothfish juv (Dissostichus eleginoides) | 0.005 | 0.59 | 1 | 0.85 | 0.785 | 0.59 | 0.0014 | unknown |
| 34 | Zooplankton | 1.18 | 25 | 93.5 | 0.7 | 0.705 | 0.267 | 0.0001 | unknown |
| 35 | Discards | 0.01 | - | - | - | - | - | 0 | unknown |
| 36 | Detritus | - | - | - | 0.05 | - | - | 0 | unknown |
