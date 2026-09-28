## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 22_20071991_North_Sea_report_Table_3.3_(1991), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 1 error(s), 19 indeterminate, 4 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 68 of 68 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 3.351, group 54 (Large crabs).

Groups with recomputed EE > 1: 23 (Norway pout, 1.145), 24 (Other gadoids (large), 2.534), 25 (Other gadoids (small), 3.865), 26 (Monkfish, 1.394), 43 (Halibut, 1.767), 50 (Fish larvae, 2.983), 54 (Large crabs, 4.283), 59 (Small mobile epifauna (swarming crustaceans), 1.014).

P/Q outside 0.02-0.5: 1 (Baleen whales, 0.002), 2 (Toothed whales, 0.001), 3 (Seals, 0.003), 4 (Seabirds, 0.001), 53 (Gelatinous zooplankton, 15.878).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 53 (Gelatinous zooplankton): P/Q = 15.878 with GS = 0.2 implies non-positive respiration (needs P/Q < 0.80)

### Indeterminate (BA unknown)

- group 6 (Spurdog): printed EE 0.95 vs recomputed 0.884 (diff 0.066) with BA unknown - a BA of +0.0006633 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Norway pout): recomputed EE = 1.145 > 1 without BA, and BA is unknown - a BA of -1.209 t/km^2/year (-0.39 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 24 (Other gadoids (large)): recomputed EE = 2.534 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 25 (Other gadoids (small)): recomputed EE = 3.865 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 26 (Monkfish): recomputed EE = 1.394 > 1 without BA, and BA is unknown - a BA of -0.01605 t/km^2/year (-0.55 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 36 (Long-rough dab): printed EE 0.6055 vs recomputed 0.708 (diff 0.103) with BA unknown - a BA of -0.0252 t/km^2/year (-0.10 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 41 (Turbot and brill): printed EE 0.1387 vs recomputed 0.310 (diff 0.172) with BA unknown - a BA of -0.007975 t/km^2/year (-0.17 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 42 (Megrim): printed EE 0.2425 vs recomputed 0.566 (diff 0.324) with BA unknown - a BA of -0.007928 t/km^2/year (-0.32 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 43 (Halibut): recomputed EE = 1.767 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 46 (Large demersal fish): printed EE 0.9 vs recomputed 0.798 (diff 0.102) with BA unknown - a BA of +0.0009574 t/km^2/year (+0.10 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 48 (Miscellaneous filterfeeding pelagic fish): printed EE 0.98 vs recomputed 0.705 (diff 0.275) with BA unknown - a BA of +0.03275 t/km^2/year (+0.27 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 49 (Squid & cuttlefish): printed EE 0.8876 vs recomputed 0.682 (diff 0.205) with BA unknown - a BA of +0.07394 t/km^2/year (+0.21 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 50 (Fish larvae): recomputed EE = 2.983 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 51 (Carnivorous zooplankton): printed EE 0.99 vs recomputed 0.542 (diff 0.448) with BA unknown - a BA of +5.994 t/km^2/year (+0.45 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 53 (Gelatinous zooplankton): printed EE 0.7604 vs recomputed 0.706 (diff 0.055) with BA unknown - a BA of +0.01028 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 54 (Large crabs): recomputed EE = 4.283 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 56 (Epifaunal macrobenthos (mobile grazers)): printed EE 0.4315 vs recomputed 0.485 (diff 0.054) with BA unknown - a BA of -1.621 t/km^2/year (-0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 58 (Shrimp): printed EE 0.4486 vs recomputed 0.869 (diff 0.420) with BA unknown - a BA of -0.6305 t/km^2/year (-0.42 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 59 (Small mobile epifauna (swarming crustaceans)): recomputed EE = 1.014 > 1 without BA, and BA is unknown - a BA of -5.102 t/km^2/year (-0.09 of production) would close it - undecidable until the source is checked for biomass accumulation

### Warnings

- group 1 (Baleen whales): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Toothed whales): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Seals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 64 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Baleen whales), 2 (Toothed whales), 3 (Seals), 4 (Seabirds), 5 (Juvenile sharks), 6 (Spurdog), 7 (Large piscivorous sharks), 8 (Small sharks) ...
- detritus pools (3): inflow ~3865, consumption ~3649 t/km^2/year, implied EE ~0.944 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Baleen whales | 0.067 | 0.02 | 9.9 | 0 | 0 | 0.00202 | 0 | unknown |
| 2 | Toothed whales | 0.017 | 0.02 | 17.63 | 0 | 0 | 0.00113 | 0 | unknown |
| 3 | Seals | 0.008 | 0.09 | 26.84 | 0 | 0 | 0.00335 | 0 | unknown |
| 4 | Seabirds | 0.003 | 0.28 | 216.6 | 0 | 0 | 0.00129 | 0 | unknown |
| 5 | Juvenile sharks | 0.001 | 0.5 | 2.5 | 0.3847 | 0.384 | 0.2 | 0 | unknown |
| 6 | Spurdog | 0.0167 | 0.6 | 2 | 0.95 | 0.884 | 0.3 | 0.008774 | unknown |
| 7 | Large piscivorous sharks | 0.002 | 0.48 | 1.6 | 0.2833 | 0.283 | 0.3 | 0.0002719 | unknown |
| 8 | Small sharks | 0.002 | 0.51 | 2.96 | 0.4152 | 0.417 | 0.172 | 0.0002649 | unknown |
| 9 | Juvenile rays | 0.268 | 0.66 | 1.7 | 0.0047 | 0.00379 | 0.388 | 0 | unknown |
| 10 | Starry ray + others | 0.109 | 0.66 | 1.7 | 0.0945 | 0.0944 | 0.388 | 0.006789 | unknown |
| 11 | Thornback & Spotted ray | 0.066 | 0.78 | 2.3 | 0.1086 | 0.109 | 0.339 | 0.005588 | unknown |
| 12 | Skate + cuckoo ray | 0.05 | 0.35 | 1.8 | 0.0039 | 0.00391 | 0.194 | 6.842e-05 | unknown |
| 13 | Juvenile Cod(0-2; 0-40cm) | 0.079 | 1.79 | 5.96 | 0.9359 | 0.96 | 0.3 | 0.05203 | unknown |
| 14 | Cod (adult) | 0.161 | 1.19 | 3.5 | 0.7498 | 0.749 | 0.34 | 0.1242 | unknown |
| 15 | Juvenile Whiting (0-1; 0-20cm) | 0.222 | 2.36 | 6.58 | 0.8603 | 0.882 | 0.359 | 0.02436 | unknown |
| 16 | Whiting (adult) | 0.352 | 0.89 | 5.46 | 0.9322 | 0.936 | 0.163 | 0.1815 | unknown |
| 17 | Juvenile Haddock (0-1; 0-20cm) | 0.284 | 2 | 5.39 | 0.4532 | 0.464 | 0.371 | 0.06314 | unknown |
| 18 | Haddock (adult) | 0.104 | 1.14 | 4.4 | 0.9717 | 0.971 | 0.259 | 0.09524 | unknown |
| 19 | Juvenile Saithe (0-3; 0-40cm) | 0.281 | 1 | 4.94 | 0.3149 | 0.317 | 0.202 | 0.05527 | unknown |
| 20 | Saithe (adult) | 0.22 | 0.95 | 3.6 | 0.621 | 0.621 | 0.264 | 0.1173 | unknown |
| 21 | Hake | 0.014 | 0.82 | 2.2 | 0.6422 | 0.633 | 0.373 | 0.005288 | unknown |
| 22 | Blue whiting | 0.08 | 2.5 | 9.06 | 0.8484 | 0.871 | 0.276 | 0.06099 | unknown |
| 23 | Norway pout | 1.394 | 2.2 | 5.05 | 0.7505 | 1.14 | 0.436 | 0.2735 | unknown |
| 24 | Other gadoids (large) | 0.0486 | 1.27 | 3.2 | 0.95 | 2.53 | 0.397 | 0.03632 | unknown |
| 25 | Other gadoids (small) | 0.1909 | 2.3 | 6 | 0.95 | 3.87 | 0.383 | 0.02829 | unknown |
| 26 | Monkfish | 0.042 | 0.7 | 1.9 | 0.848 | 1.39 | 0.368 | 0.02251 | unknown |
| 27 | Gurnards | 0.077 | 0.82 | 3.2 | 0.5772 | 0.575 | 0.256 | 0.008042 | unknown |
| 28 | Herring (juvenile 0; 1) | 0.63 | 1.31 | 5.63 | 0.6718 | 0.664 | 0.233 | 0.1513 | unknown |
| 29 | Herring (adult) | 1.966 | 0.8 | 4.34 | 0.6911 | 0.691 | 0.184 | 0.8593 | unknown |
| 30 | Sprat | 0.579 | 2.28 | 6 | 0.8059 | 0.794 | 0.38 | 0.1821 | unknown |
| 31 | Mackerel | 1.72 | 0.6 | 1.73 | 0.6317 | 0.649 | 0.347 | 0.5528 | unknown |
| 32 | Horse mackerel | 0.579 | 1.2 | 3.51 | 0.356 | 0.333 | 0.342 | 0.1724 | unknown |
| 33 | Sandeels | 3.122 | 2.28 | 10.1 | 0.7851 | 0.78 | 0.226 | 1.478 | unknown |
| 34 | Plaice | 0.703 | 0.85 | 3.42 | 0.6948 | 0.681 | 0.249 | 0.381 | unknown |
| 35 | Dab | 3 | 0.672 | 3.36 | 0.2086 | 0.23 | 0.2 | 0.1376 | unknown |
| 36 | Long-rough dab | 0.35 | 0.7 | 3.4 | 0.6055 | 0.708 | 0.206 | 5.263e-06 | unknown |
| 37 | Flounder | 0.25 | 1.1 | 3.2 | 0.2783 | 0.277 | 0.344 | 0.06401 | unknown |
| 38 | Sole | 0.158 | 0.8 | 3.1 | 0.894 | 0.905 | 0.258 | 0.0673 | unknown |
| 39 | Lemon sole | 0.305 | 0.864 | 4.32 | 0.2422 | 0.241 | 0.2 | 0.01469 | unknown |
| 40 | Witch | 0.082 | 0.9 | 3 | 0.4206 | 0.415 | 0.3 | 0.01632 | unknown |
| 41 | Turbot and brill | 0.054 | 0.86 | 2.3 | 0.1387 | 0.31 | 0.374 | 0.004268 | unknown |
| 42 | Megrim | 0.034 | 0.72 | 3.1 | 0.2425 | 0.566 | 0.232 | 0.003477 | unknown |
| 43 | Halibut | 0.033 | 0.16 | 3.14 | 0.2582 | 1.77 | 0.051 | 0.00133 | unknown |
| 44 | Dragonets | 0.045 | 1.5 | 6 | 0.7545 | 0.737 | 0.25 | 0 | unknown |
| 45 | Catfish (Wolf-fish) | 0.014 | 0.48 | 1.7 | 0.7923 | 0.793 | 0.282 | 0.005326 | unknown |
| 46 | Large demersal fish | 0.017 | 0.55 | 2.54 | 0.9 | 0.798 | 0.217 | 0.007191 | unknown |
| 47 | Small demersal fish | 0.3431 | 1.42 | 3.7 | 0.98 | 0.967 | 0.384 | 0.1693 | unknown |
| 48 | Miscellaneous filterfeeding pelagic fish | 0.0298 | 4 | 10.19 | 0.98 | 0.705 | 0.393 | 0.01022 | unknown |
| 49 | Squid & cuttlefish | 0.08 | 4.5 | 20 | 0.8876 | 0.682 | 0.225 | 0.002156 | unknown |
| 50 | Fish larvae | 0.3192 | 4 | 20 | 0.99 | 2.98 | 0.2 | 0 | unknown |
| 51 | Carnivorous zooplankton | 3.345 | 4 | 12.5 | 0.99 | 0.542 | 0.32 | 0 | unknown |
| 52 | Herbivorous & Omnivorous zooplankton (copepods) | 16 | 9.2 | 30 | 0.4852 | 0.46 | 0.307 | 0 | unknown |
| 53 | Gelatinous zooplankton | 0.066 | 2.858 | 0.18 | 0.7604 | 0.706 | 15.9 | 0 | unknown |
| 54 | Large crabs | 1.354 | 0.5541 | 2.77 | 0.9322 | 4.28 | 0.2 | 0.01246 | unknown |
| 55 | Nephrops | 1.1 | 0.37 | 1.85 | 0.9937 | 0.949 | 0.2 | 0.01807 | unknown |
| 56 | Epifaunal macrobenthos (mobile grazers) | 78 | 0.3884 | 1.942 | 0.4315 | 0.485 | 0.2 | 0.006628 | unknown |
| 57 | Infaunal macrobenthos | 136 | 1 | 3.333 | 0.2791 | 0.266 | 0.3 | 0.1407 | unknown |
| 58 | Shrimp | 0.5 | 3 | 10 | 0.4486 | 0.869 | 0.3 | 0.0434 | unknown |
| 59 | Small mobile epifauna (swarming crustaceans) | 30 | 1.9 | 5.429 | 0.9249 | 1.01 | 0.35 | 0 | unknown |
| 60 | Small infauna (polychaetes) | 150 | 0.9 | 3 | 0.9079 | 0.875 | 0.3 | 0 | unknown |
| 61 | Sessile epifauna | 105 | 0.26 | 1.3 | 0.039 | 0.0394 | 0.2 | 0.211 | unknown |
| 62 | Meiofauna | 4.107 | 35 | 125 | 0.99 | 0.992 | 0.28 | 0 | unknown |
| 63 | Benthic microflora (incl. Bacteria; protozoa)) | 0.105 | 9470 | 1.894e+04 | 0.9873 | 0.988 | 0.5 | 0 | unknown |
| 64 | Planktonic microflora (incl. Bacteria; protozoa) | 1.46 | 571 | 1142 | 0.7196 | 0.72 | 0.5 | 0 | unknown |
| 65 | Phytoplankton | 7.5 | 286 | - | 0.212 | 0.213 | - | 0 | unknown |
| 66 | Detritus - DOM -water column | 25 | - | - | 0.9316 | - | - | 0 | unknown |
| 67 | Detritus - POM - sediment | 25 | - | - | 0.9529 | - | - | 0 | unknown |
| 68 | Discards | 50 | - | - | 0.7473 | - | - | 0 | unknown |
