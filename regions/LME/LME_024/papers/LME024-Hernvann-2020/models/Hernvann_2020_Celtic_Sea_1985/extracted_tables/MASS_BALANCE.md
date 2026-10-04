## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 24_2402020_Celtic_Sea_Hernvann_(1985), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 2 error(s), 0 indeterminate, 15 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 2 of 54 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.247, group 41 (Carnivores/Necrophages).

Groups with recomputed EE > 1: 16 (Haddock, 1.012), 20 (Plaice, 1.027).

P/Q outside 0.02-0.5: 1 (Seabirds - Divers, 0.001), 2 (Seabirds - Surface feeders, 0.002), 3 (Baleen whales, 0.008), 4 (Toothed cetaceans / Seals, 0.012).

BA: carried for 52 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 3 (Baleen whales, +0), 4 (Toothed cetaceans / Seals, +0), 5 (Pelagic sharks, +0), 6 (Piscivorous dem. elasmobranchs, +0), 7 (Benthivorous dem. elasmobranchs, +0), 8 (Sea bass, +0), 9 (Anglerfish adult, +0), 10 (Anglerfish juvenile, +0), 11 (Hake adult, +0), 12 (Hake juvenile, +0), 13 (Cod adult, +0), 14 (Cod juvenile, +0), 15 (Whiting, +0), 16 (Haddock, +0), 17 (Pouts, +0), 18 (Megrim, +0), 19 (Sole, +0), 20 (Plaice, -0.0004), 21 (Piscivorous dem. fish, +0), 22 (Epibenthivorous dem. fish, +0), 23 (Endobenthivorous dem. fish, +0), 24 (Suprabenthivorous dem. fish, +0), 25 (Small benthivorous dem. fish, +0), 26 (Mackerel, +0), 27 (Horse mackerel, +0), 28 (Boarfish, +0), 29 (Sprat, +0), 30 (Blue whiting, +0), 31 (Pilchard, +0), 32 (Herring, +0), 33 (Pelagic - Large, +0), 34 (Pelagic - Medium, +0), 35 (Squids, +0), 36 (Benthic cephalopods, +0), 37 (Commercial crustaceans, +0), 38 (Nephrops, +0), 39 (Commercial bivalves, +0), 40 (Shrimps, +0), 41 (Carnivores/Necrophages, +0), 42 (Suspension/Surface detritus Feeders, +0), 43 (Subsurface deposit feeders, +0), 44 (Suprabenthos, +0), 45 (Benthic meiofauna, +0), 46 (Macrozooplankton, +0), 47 (Mesozooplankton - Large, +0), 48 (Mesozooplankton - Small, +0), 49 (Microzooplankton, +0), 50 (Bacteria, +0), 51 (Phytoplankton - Large, +0), 52 (Phytoplankton - Small, +0), 53 (Discards, +0.1), 54 (Detritus, +481.1). The remaining 2 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 16 (Haddock): recomputed EE = 1.012 > 1 - catch+BA+predation (0.05224) exceeds production (0.0516)
- group 20 (Plaice): recomputed EE = 1.027 > 1 - catch+BA+predation (0.03326) exceeds production (0.0324)

### Warnings

- group 1 (Seabirds - Divers): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Seabirds - Surface feeders): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Baleen whales): P/Q = 0.008 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Toothed cetaceans / Seals): P/Q = 0.012 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 19 (Sole): printed EE 0.96 vs recomputed 0.839 (diff 0.121), BA 0 carried
- group 20 (Plaice): printed EE 0.97 vs recomputed 1.027 (diff 0.057), BA -0.0004 carried
- group 26 (Mackerel): printed EE 0.97 vs recomputed 0.908 (diff 0.062), BA 0 carried
- group 27 (Horse mackerel): printed EE 0.79 vs recomputed 0.689 (diff 0.101), BA 0 carried
- group 31 (Pilchard): printed EE 0.62 vs recomputed 0.414 (diff 0.206), BA 0 carried
- group 32 (Herring): printed EE 0.97 vs recomputed 0.886 (diff 0.084), BA 0 carried
- group 34 (Pelagic - Medium): printed EE 0.95 vs recomputed 0.893 (diff 0.057), BA 0 carried
- group 41 (Carnivores/Necrophages): printed EE 0.95 vs recomputed 0.703 (diff 0.247), BA 0 carried
- group 42 (Suspension/Surface detritus Feeders): printed EE 0.95 vs recomputed 0.799 (diff 0.151), BA 0 carried
- group 43 (Subsurface deposit feeders): printed EE 0.9 vs recomputed 0.700 (diff 0.200), BA 0 carried
- group 44 (Suprabenthos): printed EE 0.95 vs recomputed 0.897 (diff 0.053), BA 0 carried

### Notes

- 43 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Seabirds - Divers), 2 (Seabirds - Surface feeders), 3 (Baleen whales), 4 (Toothed cetaceans / Seals), 5 (Pelagic sharks), 6 (Piscivorous dem. elasmobranchs), 7 (Benthivorous dem. elasmobranchs), 8 (Sea bass) ...
- detritus pools (2): inflow ~2028, consumption ~1854 t/km^2/year, implied EE ~0.914 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Seabirds - Divers | 0 | 0.15 | 135.3 | 0 | - | 0.00111 | 0 | unknown |
| 2 | Seabirds - Surface feeders | 0 | 0.25 | 114.5 | 0 | - | 0.00218 | 0 | unknown |
| 3 | Baleen whales | 0.07 | 0.04 | 4.77 | 0 | 0 | 0.00839 | 0 | 0 |
| 4 | Toothed cetaceans / Seals | 0.03 | 0.14 | 12 | 0 | 0 | 0.0117 | 0 | 0 |
| 5 | Pelagic sharks | 0.12 | 0.2 | 1.96 | 0.6 | 0.598 | 0.102 | 0.004031 | 0 |
| 6 | Piscivorous dem. elasmobranchs | 0.15 | 0.47 | 3.13 | 0.65 | 0.644 | 0.15 | 0.04301 | 0 |
| 7 | Benthivorous dem. elasmobranchs | 0.22 | 0.52 | 3.48 | 0.65 | 0.646 | 0.149 | 0.07231 | 0 |
| 8 | Sea bass | 0.05 | 0.28 | 1.52 | 0.58 | 0.564 | 0.184 | 0.006221 | 0 |
| 9 | Anglerfish adult | 0.26 | - | 2.38 | 0.57 | - | - | 0.08727 | 0 |
| 10 | Anglerfish juvenile | 0.04 | - | 6.89 | 0.38 | - | - | 0.01892 | 0 |
| 11 | Hake adult | 0.1 | - | 2.52 | 0.96 | - | - | 0.07503 | 0 |
| 12 | Hake juvenile | 0.05 | - | 5.56 | 0.22 | - | - | 0.00287 | 0 |
| 13 | Cod adult | 0.08 | - | 2.58 | 0.85 | - | - | 0.03144 | 0 |
| 14 | Cod juvenile | 0.02 | - | 5.04 | 0.9 | - | - | 0.007782 | 0 |
| 15 | Whiting | 0.17 | 0.92 | 3.7 | 0.97 | 0.988 | 0.249 | 0.06395 | 0 |
| 16 | Haddock | 0.06 | 0.86 | 3.33 | 0.98 | 1.01 | 0.258 | 0.02361 | 0 |
| 17 | Pouts | 0.94 | 1.35 | 5.4 | 0.95 | 0.952 | 0.25 | 0.007717 | 0 |
| 18 | Megrim | 0.3 | 0.45 | 2.24 | - | 0.761 | 0.201 | 0.07391 | 0 |
| 19 | Sole | 0.05 | 0.47 | 2.58 | 0.96 | 0.839 | 0.182 | 0.01438 | 0 |
| 20 | Plaice | 0.04 | 0.81 | 4.5 | 0.97 | 1.03 | 0.18 | 0.02882 | -0.0004 |
| 21 | Piscivorous dem. fish | 0.33 | 0.64 | 3.21 | 0.85 | 0.847 | 0.199 | 0.1088 | 0 |
| 22 | Epibenthivorous dem. fish | 0.5 | 0.86 | 4.3 | 0.95 | 0.925 | 0.2 | 0.02143 | 0 |
| 23 | Endobenthivorous dem. fish | 0.15 | 1.09 | 5.45 | 0.95 | 0.95 | 0.2 | 0.02701 | 0 |
| 24 | Suprabenthivorous dem. fish | 0.49 | 1.88 | 7.52 | 0.95 | 0.957 | 0.25 | 0.000594 | 0 |
| 25 | Small benthivorous dem. fish | 0.95 | 1.83 | 7.34 | 0.95 | 0.942 | 0.249 | 0.004634 | 0 |
| 26 | Mackerel | 0.95 | 0.26 | 1.04 | 0.97 | 0.908 | 0.25 | 0.1191 | 0 |
| 27 | Horse mackerel | 6.4 | 0.25 | 1 | 0.79 | 0.689 | 0.25 | 0.1762 | 0 |
| 28 | Boarfish | 0.15 | 1.2 | 4.8 | 0.07 | 0.0668 | 0.25 | 1.463e-08 | 0 |
| 29 | Sprat | 0.26 | 0.85 | 7 | 0.95 | 0.932 | 0.121 | 0.02947 | 0 |
| 30 | Blue whiting | 0.48 | 1.43 | 5.7 | 0.94 | 0.925 | 0.251 | 0.03743 | 0 |
| 31 | Pilchard | 0.31 | 0.68 | 6.8 | 0.62 | 0.414 | 0.1 | 0.02707 | 0 |
| 32 | Herring | 0.81 | 0.51 | 4.59 | 0.97 | 0.886 | 0.111 | 0.08454 | 0 |
| 33 | Pelagic - Large | 0.2 | 0.42 | 2.8 | 0.9 | 0.898 | 0.15 | 0.05478 | 0 |
| 34 | Pelagic - Medium | 0.16 | 0.88 | 5.93 | 0.95 | 0.893 | 0.148 | 0.001255 | 0 |
| 35 | Squids | 0.09 | 3.9 | 13 | 0.9 | 0.915 | 0.3 | 0.006797 | 0 |
| 36 | Benthic cephalopods | 0.23 | 3.9 | 13 | 0.9 | 0.943 | 0.3 | 0.01728 | 0 |
| 37 | Commercial crustaceans | 0.78 | 0.55 | 3.67 | 0.8 | 0.798 | 0.15 | 0.09817 | 0 |
| 38 | Nephrops | 0.22 | 0.6 | 4 | 0.77 | 0.789 | 0.15 | 0.02357 | 0 |
| 39 | Commercial bivalves | 0.3 | 3.5 | 17.5 | 0.73 | 0.729 | 0.2 | 0.06309 | 0 |
| 40 | Shrimps | 1.2 | 3 | 20 | 0.95 | 0.945 | 0.15 | 0.0006579 | 0 |
| 41 | Carnivores/Necrophages | 5.02 | 6.11 | 40.73 | 0.95 | 0.703 | 0.15 | 0.03318 | 0 |
| 42 | Suspension/Surface detritus Feeders | 15.55 | 6.35 | 31.75 | 0.95 | 0.799 | 0.2 | 0.01262 | 0 |
| 43 | Subsurface deposit feeders | 21.69 | 2.88 | 14.4 | 0.9 | 0.7 | 0.2 | 0 | 0 |
| 44 | Suprabenthos | 1.53 | 7.7 | 38.5 | 0.95 | 0.897 | 0.2 | 0 | 0 |
| 45 | Benthic meiofauna | 11.41 | 10 | 50 | 0.95 | 0.901 | 0.2 | 0 | 0 |
| 46 | Macrozooplankton | 2.25 | 7.5 | 25 | 0.74 | 0.738 | 0.3 | 0 | 0 |
| 47 | Mesozooplankton - Large | 1.98 | 8.01 | 26.69 | 0.9 | 0.896 | 0.3 | 0 | 0 |
| 48 | Mesozooplankton - Small | 9.61 | 25.35 | 84.5 | 0.12 | 0.119 | 0.3 | 0 | 0 |
| 49 | Microzooplankton | 2.52 | 63.9 | 213 | 0.7 | 0.696 | 0.3 | 0 | 0 |
| 50 | Bacteria | 1.75 | 157.4 | 393.6 | 0.65 | 0.648 | 0.4 | 0 | 0 |
| 51 | Phytoplankton - Large | 14.19 | 76.45 | - | 0.57 | 0.566 | - | 0 | 0 |
| 52 | Phytoplankton - Small | 10.49 | 76.45 | - | 0.98 | 0.978 | - | 0 | 0 |
| 53 | Discards | 0.25 | - | - | 0.62 | - | - | 0 | 0.1 |
| 54 | Detritus | 124 | - | - | 0.79 | - | - | 0 | 481.1 |
