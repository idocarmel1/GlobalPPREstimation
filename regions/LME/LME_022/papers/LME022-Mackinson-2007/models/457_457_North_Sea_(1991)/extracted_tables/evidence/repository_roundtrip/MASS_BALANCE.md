## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 457_457_North_Sea_(1991), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 4 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 0 of 68 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.000, group 23 (Norway pout).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Baleen whales, 0.002), 4 (Seabirds, 0.001), 3 (Seals, 0.003), 2 (Toothed whales, 0.001).

BA: carried for 68 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Baleen whales, +0), 63 (Benthic microflora (incl. Bacteria, protozoa)), +0), 22 (Blue whiting, +0), 51 (Carnivorous zooplankton, +0), 45 (Catfish (Wolf-fish), +0), 14 (Cod (adult), +0), 35 (Dab, +0), 66 (Detritus - DOM -water column, +454.4), 67 (Detritus - POM - sediment, +507.4), 68 (Discards, +0), 44 (Dragonets, +0), 56 (Epifaunal macrobenthos (mobile grazers), +0), 50 (Fish larvae, +0), 37 (Flounder, +0), 53 (Gelatinous zooplankton, +0), 27 (Gurnards, +0), 18 (Haddock (adult), +0), 21 (Hake, +0), 43 (Halibut, +0), 52 (Herbivorous &amp; Omnivorous zooplankton (copepods), +0), 29 (Herring (adult), +0), 28 (Herring (juvenile 0, 1), +0), 32 (Horse mackerel, +0), 57 (Infaunal macrobenthos, +0), 13 (Juvenile Cod(0-2, 0-40cm), +0), 17 (Juvenile Haddock (0-1, 0-20cm), +0), 9 (Juvenile rays, +0), 19 (Juvenile Saithe (0-3, 0-40cm), +0), 5 (Juvenile sharks, +0), 15 (Juvenile Whiting (0-1, 0-20cm), +0), 54 (Large crabs, +0), 46 (Large demersal fish, +0), 7 (Large piscivorous sharks, +0), 39 (Lemon sole, +0), 36 (Long-rough dab, +0), 31 (Mackerel, +0), 42 (Megrim, +0), 62 (Meiofauna, +0), 48 (Miscellaneous filterfeeding pelagic fish, +0), 26 (Monkfish, +0), 55 (Nephrops, +0), 23 (Norway pout, +0), 24 (Other gadoids (large), +0), 25 (Other gadoids (small), +0), 65 (Phytoplankton, +0), 34 (Plaice, +0), 64 (Planktonic microflora (incl. Bacteria, protozoa), +0), 20 (Saithe (adult), +0), 33 (Sandeels, +0), 4 (Seabirds, +0), 3 (Seals, +0), 61 (Sessile epifauna, +0), 58 (Shrimp, +0), 12 (Skate + cuckoo ray, +0), 47 (Small demersal fish, +0), 60 (Small infauna (polychaetes), +0), 59 (Small mobile epifauna (swarming crustaceans), +0), 8 (Small sharks, +0), 38 (Sole, +0), 30 (Sprat, +0), 6 (Spurdog, +0), 49 (Squid &amp; cuttlefish, +0), 10 (Starry ray + others, +0), 11 (Thornback &amp; Spotted ray, +0), 2 (Toothed whales, +0), 41 (Turbot and brill, +0), 16 (Whiting (adult), +0), 40 (Witch, +0). The remaining 0 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 1 (Baleen whales): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Seals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Toothed whales): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 65 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Baleen whales), 63 (Benthic microflora (incl. Bacteria, protozoa))), 22 (Blue whiting), 51 (Carnivorous zooplankton), 45 (Catfish (Wolf-fish)), 14 (Cod (adult)), 35 (Dab), 44 (Dragonets) ...
- detritus pools (3): inflow ~3969, consumption ~3649 t/km^2/year, implied EE ~0.919 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Baleen whales | 0.067 | 0.02 | 9.9 | 0 | 0 | 0.00202 | 0 | 0 |
| 63 | Benthic microflora (incl. Bacteria, protozoa)) | 0.105 | 9470 | 1.894e+04 | 0.9885 | 0.988 | 0.5 | 0 | 0 |
| 22 | Blue whiting | 0.08 | 2.5 | 9.06 | 0.8938 | 0.894 | 0.276 | 0.06097 | 0 |
| 51 | Carnivorous zooplankton | 3.141 | 4 | 12.5 | 0.99 | 0.99 | 0.32 | 0 | 0 |
| 45 | Catfish (Wolf-fish) | 0.014 | 0.48 | 1.7 | 0.7923 | 0.792 | 0.282 | 0.005325 | 0 |
| 14 | Cod (adult) | 0.161 | 1.19 | 3.5 | 0.7485 | 0.749 | 0.34 | 0.1243 | 0 |
| 35 | Dab | 3 | 0.672 | 3.36 | 0.2178 | 0.218 | 0.2 | 0.1376 | 0 |
| 66 | Detritus - DOM -water column | 25 | - | - | 0.9155 | - | - | 0 | 454.4 |
| 67 | Detritus - POM - sediment | 25 | - | - | 0.9222 | - | - | 0 | 507.4 |
| 68 | Discards | 50 | - | - | 0 | - | - | 0 | 0 |
| 44 | Dragonets | 0.045 | 1.5 | 6 | 0.8607 | 0.861 | 0.25 | 0 | 0 |
| 56 | Epifaunal macrobenthos (mobile grazers) | 78 | 0.3884 | 1.942 | 0.4283 | 0.428 | 0.2 | 0.006652 | 0 |
| 50 | Fish larvae | 0.3319 | 4 | 20 | 0.99 | 0.99 | 0.2 | 0 | 0 |
| 37 | Flounder | 0.25 | 1.1 | 3.2 | 0.2805 | 0.28 | 0.344 | 0.06402 | 0 |
| 53 | Gelatinous zooplankton | 0.066 | 2.858 | 6.351 | 0.7723 | 0.772 | 0.45 | 0 | 0 |
| 27 | Gurnards | 0.077 | 0.82 | 3.2 | 0.6252 | 0.625 | 0.256 | 0.008042 | 0 |
| 18 | Haddock (adult) | 0.104 | 1.14 | 4.4 | 0.9941 | 0.994 | 0.259 | 0.09517 | 0 |
| 21 | Hake | 0.014 | 0.82 | 2.2 | 0.6875 | 0.687 | 0.373 | 0.005296 | 0 |
| 43 | Halibut | 0.033 | 0.16 | 3.14 | 0.2582 | 0.258 | 0.051 | 0.001326 | 0 |
| 52 | Herbivorous &amp; Omnivorous zooplankton (copepods) | 16 | 9.2 | 30 | 0.4641 | 0.464 | 0.307 | 0 | 0 |
| 29 | Herring (adult) | 1.966 | 0.8 | 4.34 | 0.7071 | 0.707 | 0.184 | 0.8593 | 0 |
| 28 | Herring (juvenile 0, 1) | 0.08541 | 1.31 | 12.51 | 0.9797 | 0.98 | 0.105 | 0.02161 | 0 |
| 32 | Horse mackerel | 0.579 | 1.2 | 3.51 | 0.3608 | 0.361 | 0.342 | 0.1723 | 0 |
| 57 | Infaunal macrobenthos | 136 | 1 | 3.333 | 0.2766 | 0.277 | 0.3 | 0.0908 | 0 |
| 13 | Juvenile Cod(0-2, 0-40cm) | 0.1241 | 1.79 | 8.012 | 0.7527 | 0.753 | 0.223 | 0.07805 | 0 |
| 17 | Juvenile Haddock (0-1, 0-20cm) | 0.006677 | 2 | 14.39 | 0.8164 | 0.816 | 0.139 | 0.002105 | 0 |
| 9 | Juvenile rays | 0.268 | 0.66 | 1.7 | 0.005473 | 0.00547 | 0.388 | 0 | 0 |
| 19 | Juvenile Saithe (0-3, 0-40cm) | 0.1395 | 1 | 8.289 | 0.4664 | 0.466 | 0.121 | 0.02763 | 0 |
| 5 | Juvenile sharks | 0.001 | 0.5 | 2.5 | 0.3886 | 0.389 | 0.2 | 0 | 0 |
| 15 | Juvenile Whiting (0-1, 0-20cm) | 0.02183 | 2.36 | 17.4 | 0.782 | 0.782 | 0.136 | 0.002436 | 0 |
| 54 | Large crabs | 1.354 | 0.5541 | 2.77 | 0.8429 | 0.843 | 0.2 | 0.01147 | 0 |
| 46 | Large demersal fish | 0.01698 | 0.55 | 2.54 | 0.9 | 0.9 | 0.217 | 0.007193 | 0 |
| 7 | Large piscivorous sharks | 0.002 | 0.48 | 1.6 | 0.2833 | 0.283 | 0.3 | 0.0002719 | 0 |
| 39 | Lemon sole | 0.305 | 0.864 | 4.32 | 0.2451 | 0.245 | 0.2 | 0.01469 | 0 |
| 36 | Long-rough dab | 0.35 | 0.7 | 3.4 | 0.5446 | 0.545 | 0.206 | 5.263e-06 | 0 |
| 31 | Mackerel | 1.72 | 0.6 | 1.73 | 0.6376 | 0.638 | 0.347 | 0.5528 | 0 |
| 42 | Megrim | 0.034 | 0.72 | 3.1 | 0.2504 | 0.25 | 0.232 | 0.003472 | 0 |
| 62 | Meiofauna | 4.115 | 35 | 125 | 0.99 | 0.99 | 0.28 | 0 | 0 |
| 48 | Miscellaneous filterfeeding pelagic fish | 0.02968 | 4 | 10.19 | 0.98 | 0.98 | 0.393 | 0.01024 | 0 |
| 26 | Monkfish | 0.042 | 0.7 | 1.9 | 0.8542 | 0.854 | 0.368 | 0.0225 | 0 |
| 55 | Nephrops | 1.1 | 0.37 | 1.85 | 0.9354 | 0.935 | 0.2 | 0.0191 | 0 |
| 23 | Norway pout | 1.394 | 2.2 | 5.05 | 0.7505 | 0.75 | 0.436 | 0.2735 | 0 |
| 24 | Other gadoids (large) | 0.05117 | 1.27 | 3.2 | 0.95 | 0.95 | 0.397 | 0.03635 | 0 |
| 25 | Other gadoids (small) | 0.2022 | 2.3 | 6 | 0.95 | 0.95 | 0.383 | 0.02833 | 0 |
| 65 | Phytoplankton | 7.5 | 286.7 | 0 | 0.2121 | 0.212 | - | 0 | 0 |
| 34 | Plaice | 0.703 | 0.85 | 3.42 | 0.6984 | 0.698 | 0.249 | 0.3811 | 0 |
| 64 | Planktonic microflora (incl. Bacteria, protozoa) | 1.46 | 571 | 1142 | 0.7197 | 0.72 | 0.5 | 0 | 0 |
| 20 | Saithe (adult) | 0.22 | 0.95 | 3.6 | 0.6332 | 0.633 | 0.264 | 0.1174 | 0 |
| 33 | Sandeels | 3.122 | 2.28 | 10.1 | 0.7583 | 0.758 | 0.226 | 1.478 | 0 |
| 4 | Seabirds | 0.003 | 0.28 | 216 | 0 | 0 | 0.0013 | 0 | 0 |
| 3 | Seals | 0.008 | 0.09 | 26.84 | 0 | 0 | 0.00335 | 0 | 0 |
| 61 | Sessile epifauna | 105 | 0.26 | 1.3 | 0.04173 | 0.0417 | 0.2 | 0.211 | 0 |
| 58 | Shrimp | 0.5 | 3 | 10 | 0.4314 | 0.431 | 0.3 | 0.09336 | 0 |
| 12 | Skate + cuckoo ray | 0.05 | 0.35 | 1.8 | 0.00391 | 0.00391 | 0.194 | 6.842e-05 | 0 |
| 47 | Small demersal fish | 0.3662 | 1.42 | 3.7 | 0.98 | 0.98 | 0.384 | 0.1694 | 0 |
| 60 | Small infauna (polychaetes) | 150 | 0.9 | 3 | 0.9076 | 0.908 | 0.3 | 0 | 0 |
| 59 | Small mobile epifauna (swarming crustaceans) | 30 | 1.9 | 5.429 | 0.92 | 0.92 | 0.35 | 0 | 0 |
| 8 | Small sharks | 0.002 | 0.51 | 2.96 | 0.4168 | 0.417 | 0.172 | 0.0002632 | 0 |
| 38 | Sole | 0.158 | 0.8 | 3.1 | 0.9148 | 0.915 | 0.258 | 0.06727 | 0 |
| 30 | Sprat | 0.579 | 2.28 | 6 | 0.8398 | 0.84 | 0.38 | 0.182 | 0 |
| 6 | Spurdog | 0.01678 | 0.6 | 2 | 0.95 | 0.95 | 0.3 | 0.008772 | 0 |
| 49 | Squid &amp; cuttlefish | 0.08 | 4.5 | 20 | 0.899 | 0.899 | 0.225 | 0.002151 | 0 |
| 10 | Starry ray + others | 0.109 | 0.66 | 1.7 | 0.09445 | 0.0945 | 0.388 | 0.006795 | 0 |
| 11 | Thornback &amp; Spotted ray | 0.066 | 0.78 | 2.3 | 0.1086 | 0.109 | 0.339 | 0.00559 | 0 |
| 2 | Toothed whales | 0.017 | 0.02 | 17.63 | 0 | 0 | 0.00113 | 0 | 0 |
| 41 | Turbot and brill | 0.054 | 0.86 | 2.3 | 0.141 | 0.141 | 0.374 | 0.004272 | 0 |
| 16 | Whiting (adult) | 0.352 | 0.89 | 5.46 | 0.9747 | 0.975 | 0.163 | 0.1814 | 0 |
| 40 | Witch | 0.082 | 0.9 | 3 | 0.4312 | 0.431 | 0.3 | 0.01634 | 0 |
