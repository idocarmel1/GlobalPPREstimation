## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 14_Patagonian_Shelf_PAT2024-native_Falkland_Shelf_(2020), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 1 error(s), 0 indeterminate, 4 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 0 of 36 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: no group has both a printed EE and enough inputs to recompute one.

Groups with recomputed EE > 1: 13 (Kingclip, 1.524).

P/Q outside 0.02-0.5: 25 (Seabirds, 0.017), 33 (Toothfish juv, 0.585).

BA: carried for 36 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Baleen Whales, +0), 2 (Benthic Crustaceans, +0), 3 (Blue Whiting, +0), 4 (Dogfish, +0), 5 (Flounder, +0), 6 (Grenadier, +0), 7 (Hake Austral, +0), 8 (Hake Common, +0), 9 (Hoki, +0), 10 (I. argentinus, +0), 11 (Jellyfish, +0), 12 (Kelp, +0), 13 (Kingclip, +0), 14 (Large Demersal Fish, +0), 15 (Large Zoobenthos, +0), 16 (D. gahi ASC, +0), 17 (D. gahi SSC, +0), 18 (Myctophidae, +0), 19 (Octopods, +0), 20 (Pelagic Fish, +0), 21 (Penguins, +0), 22 (Phytoplankton, +0), 23 (Red Cod, +0), 24 (Rock Cod, +0), 25 (Seabirds, +0), 26 (Seals and Sea Lion, +0), 27 (Sharks, +0), 28 (Skates, +0), 29 (Small Demersal Fish, +0), 30 (Small Zoobenthos, +0), 31 (Squid, +0), 32 (Toothed Whales and Dolphins, +0), 33 (Toothfish juv, +0), 34 (Zooplankton, +0), 35 (Discards, +0), 36 (Detritus, +0). The remaining 0 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 13 (Kingclip): recomputed EE = 1.524 > 1 - catch+BA+predation (0.008516) exceeds production (0.005589)

### Warnings

- group 12 (Kelp): only 2 of B/P-B/Q-B/EE given (B, P/B) - Ecopath needs three
- group 22 (Phytoplankton): only 2 of B/P-B/Q-B/EE given (P/B, EE) - Ecopath needs three
- group 25 (Seabirds): P/Q = 0.017 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 33 (Toothfish juv): P/Q = 0.585 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 12 consumer(s) lack B or Q/B, so predation on their prey is under-counted and every recomputed EE below is a lower bound: 2 (Benthic Crustaceans), 6 (Grenadier), 11 (Jellyfish), 14 (Large Demersal Fish), 15 (Large Zoobenthos), 18 (Myctophidae)
- detritus pools (2): inflow ~708.7, consumption ~0.2298 t/km^2/year, implied EE ~0.000 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Baleen Whales | 0.0025 | 0.8 | 10 | - | 0 | 0.08 | 0 | 0 |
| 2 | Benthic Crustaceans | - | 2.5 | 11 | 0.9 | - | 0.227 | 0.0001592 | 0 |
| 3 | Blue Whiting | 0.01146 | 0.49 | 2.7 | - | 0.919 | 0.181 | 0.000344 | 0 |
| 4 | Dogfish | 0.051 | 0.32 | 3.7 | - | 0.0267 | 0.0865 | 0.0004356 | 0 |
| 5 | Flounder | 0.00048 | 0.65 | 3.1 | - | 0.0806 | 0.21 | 1.331e-05 | 0 |
| 6 | Grenadier | - | 0.16 | 2.8 | 0.8 | - | 0.0571 | 0.0008363 | 0 |
| 7 | Hake Austral | 0.003 | 0.34 | 1.8 | - | 0.274 | 0.189 | 0.0002791 | 0 |
| 8 | Hake Common | 1.18 | 0.245 | 2.3 | - | 0.977 | 0.107 | 0.2176 | 0 |
| 9 | Hoki | 0.3133 | 0.301 | 2.3 | - | 0.976 | 0.131 | 0.03861 | 0 |
| 10 | I. argentinus | 0.6606 | 6.5 | 16 | - | 0.296 | 0.406 | 0.3451 | 0 |
| 11 | Jellyfish | - | 6 | 15 | 0.95 | - | 0.4 | 8.98e-06 | 0 |
| 12 | Kelp | 100 | 7 | - | - | 0 | - | 0 | 0 |
| 13 | Kingclip | 0.04658 | 0.12 | 1.6 | - | 1.52 | 0.075 | 0.008317 | 0 |
| 14 | Large Demersal Fish | - | 0.35 | 2.7 | 0.8 | - | 0.13 | 0.0003477 | 0 |
| 15 | Large Zoobenthos | - | 1.1 | 10 | 0.65 | - | 0.11 | 0 | 0 |
| 16 | D. gahi ASC | 0.1782 | 3.5 | 11 | - | 0.855 | 0.318 | 0.1501 | 0 |
| 17 | D. gahi SSC | 0.3399 | 3.5 | 11 | - | 0.85 | 0.318 | 0.1547 | 0 |
| 18 | Myctophidae | - | 0.6 | 5 | 0.98 | - | 0.12 | 0 | 0 |
| 19 | Octopods | - | 2 | 5 | 0.95 | - | 0.4 | 1.079e-05 | 0 |
| 20 | Pelagic Fish | 0.655 | 0.373 | 5.6 | - | 0.937 | 0.0666 | 0.003947 | 0 |
| 21 | Penguins | 0.006838 | 1.5 | 65 | - | 0.529 | 0.0231 | 6.59e-09 | 0 |
| 22 | Phytoplankton | - | 80 | - | 0.4 | - | - | 0 | 0 |
| 23 | Red Cod | 0.1133 | 0.26 | 2.9 | - | 0.871 | 0.0897 | 0.007129 | 0 |
| 24 | Rock Cod | 0.1112 | 0.37 | 3.2 | - | 0.921 | 0.116 | 0.004066 | 0 |
| 25 | Seabirds | 0.02 | 1.223 | 70 | - | 0.0356 | 0.0175 | 6.73e-07 | 0 |
| 26 | Seals and Sea Lion | 0.02106 | 0.4 | 17.44 | - | 0.00218 | 0.0229 | 4.64e-07 | 0 |
| 27 | Sharks | 0.0003 | 0.08 | 0.85 | - | 0.0417 | 0.0941 | 1e-06 | 0 |
| 28 | Skates | 0.06647 | 0.218 | 2.1 | - | 0.769 | 0.104 | 0.007079 | 0 |
| 29 | Small Demersal Fish | - | 0.37 | 6.5 | 0.95 | - | 0.0569 | 4e-05 | 0 |
| 30 | Small Zoobenthos | - | 3 | 11 | 0.85 | - | 0.273 | 0.0001041 | 0 |
| 31 | Squid | - | 3.5 | 10 | 0.9 | - | 0.35 | 1.929e-05 | 0 |
| 32 | Toothed Whales and Dolphins | 0.002 | 0.42 | 10.46 | - | 0.0133 | 0.0402 | 0 | 0 |
| 33 | Toothfish juv | - | 0.585 | 1 | 0.85 | - | 0.585 | 0.001443 | 0 |
| 34 | Zooplankton | - | 25 | 93.5 | 0.7 | - | 0.267 | 0.0001041 | 0 |
| 35 | Discards | 0.00586 | - | - | - | - | - | 0 | 0 |
| 36 | Detritus | - | - | - | 0 | - | - | 0 | 0 |
