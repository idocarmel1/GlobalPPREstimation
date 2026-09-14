## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 27_Canary_Current_27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 1 of 51 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.138, group 48 (BA phytopl.).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Marine mammals, 0.003), 2 (Coastal birds, 0.004).

BA: carried for 50 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Marine mammals, +0), 2 (Coastal birds, +0), 3 (Meagre ad, +0), 4 (Meagre juv, +0), 5 (Mullets, +0), 6 (Pelagic L, +0), 7 (Mackerel, +0), 8 (Sardine, +0), 9 (Sardinelles, +0), 10 (Horse mackerels, +0), 11 (Coastal selacians, -0.062), 12 (Coastal M, +0), 13 (Coastal S, +0), 14 (Croakers ad, +0), 15 (Croakers juv, +0), 16 (Seabreams ad, +0), 17 (Seabreams juv., +0), 18 (Catfish ad, +0), 19 (Catfish juv, +0), 20 (Shelf selacians, +0), 21 (Shelf L, +0), 22 (Shelf M, +0), 23 (Groupers ad, -0.0055), 24 (Grouper juv, -2e-05), 25 (Sparids ad, +0), 26 (Sparids juv, +0), 27 (Scianids, -0.011), 28 (Shelf soles, +0), 29 (Shelf S, +0), 30 (Octopus vulgaris, -0.0411), 31 (Cephalopods, -0.03), 32 (BA L crustaceans, +0), 33 (BA molluscs, +0), 34 (BA worms, +0), 35 (BA crustaceans, +0), 36 (BA other inverts, +0), 37 (BA meiobenthos, +0), 38 (shelf L crustaceans, +0), 39 (shelf molluscs, +0), 40 (shelf worms, +0), 41 (shelf crustaceans, +0), 42 (shelf other inverts, +0), 43 (shelf meiobenthos, +0), 44 (mesozoopl., +0), 45 (macrozoopl., +0), 46 (BA mesozoopl., +0), 47 (BA macrozoopl., +0), 48 (BA phytopl., +0), 49 (phytoplankton, +0), 50 (algae and eelgrass, +0). The remaining 1 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 1 (Marine mammals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Coastal birds): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 48 (BA phytopl.): printed EE 0.26 vs recomputed 0.398 (diff 0.138), BA 0 carried

### Notes

- 40 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Marine mammals), 2 (Coastal birds), 3 (Meagre ad), 4 (Meagre juv), 5 (Mullets), 6 (Pelagic L), 7 (Mackerel), 8 (Sardine) ...
- detritus pools (1): inflow ~7023, consumption ~3794 t/km^2/year, implied EE ~0.540 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Marine mammals | 0.01 | 0.04 | 12.5 | 0 | 0 | 0.0032 | 0 | 0 |
| 2 | Coastal birds | 0.01 | 0.28 | 67 | 0 | 0 | 0.00418 | 0 | 0 |
| 3 | Meagre ad | 0.12 | 0 | 2.1 | 0.657 | - | - | 0.014 | 0 |
| 4 | Meagre juv | 5e-05 | 0 | 17.9 | 0.974 | - | - | 0 | 0 |
| 5 | Mullets | 0.42 | 0.8 | 8.2 | 0.8 | 0.795 | 0.0976 | 0.103 | 0 |
| 6 | Pelagic L | 3.42 | 0.96 | 5.4 | 0.9 | 0.9 | 0.178 | 2.679 | 0 |
| 7 | Mackerel | 1.45 | 0.45 | 3 | 0.735 | 0.735 | 0.15 | 0.289 | 0 |
| 8 | Sardine | 11.79 | 0.65 | 4.3 | 0.771 | 0.77 | 0.151 | 1.801 | 0 |
| 9 | Sardinelles | 18 | 0.99 | 7.7 | 0.785 | 0.785 | 0.129 | 2.31 | 0 |
| 10 | Horse mackerels | 10 | 0.72 | 3.6 | 0.844 | 0.844 | 0.2 | 3.812 | 0 |
| 11 | Coastal selacians | 1.24 | 0.3 | 2 | 0.015 | 0.0147 | 0.15 | 0.063 | -0.062 |
| 12 | Coastal M | 0.83 | 0.58 | 2.9 | 0.858 | 0.861 | 0.2 | 0.121 | 0 |
| 13 | Coastal S | 4.21 | 0.62 | 3.1 | 0.95 | 0.952 | 0.2 | 0 | 0 |
| 14 | Croakers ad | 0.077 | - | 3.9 | 0.754 | - | - | 0.003 | 0 |
| 15 | Croakers juv | 0.004 | - | 9.9 | 0.706 | - | - | 0 | 0 |
| 16 | Seabreams ad | 1.69 | - | 4.7 | 0.884 | - | - | 0.167 | 0 |
| 17 | Seabreams juv. | 0.012 | - | 21.1 | 0.884 | - | - | 0 | 0 |
| 18 | Catfish ad | 0.6 | - | 4.1 | 0.226 | - | - | 0.034 | 0 |
| 19 | Catfish juv | 0.002 | - | 22.3 | 0.78 | - | - | 0 | 0 |
| 20 | Shelf selacians | 0.2 | 0.24 | 1.6 | 0.787 | 0.794 | 0.15 | 0.011 | 0 |
| 21 | Shelf L | 0.36 | 0.47 | 3.4 | 0.467 | 0.467 | 0.138 | 0.071 | 0 |
| 22 | Shelf M | 1.55 | 0.57 | 6.2 | 0.908 | 0.913 | 0.0919 | 0.146 | 0 |
| 23 | Groupers ad | 0.11 | - | 3.2 | 0.938 | - | - | 0.025 | -0.0055 |
| 24 | Grouper juv | 0.0004 | - | 16.2 | 0.536 | - | - | 0 | -2e-05 |
| 25 | Sparids ad | 1.29 | - | 2.4 | 0.871 | - | - | 0.014 | 0 |
| 26 | Sparids juv | 0.01 | - | 9.8 | 0.939 | - | - | 0 | 0 |
| 27 | Scianids | 0.22 | 0.29 | 4.3 | 0.665 | 0.654 | 0.0674 | 0.017 | -0.011 |
| 28 | Shelf soles | 0.35 | 0.58 | 2.9 | 0.882 | 0.886 | 0.2 | 0.009 | 0 |
| 29 | Shelf S | 6.195 | 0.82 | 7.6 | 0.95 | 0.951 | 0.108 | 0.005 | 0 |
| 30 | Octopus vulgaris | 1.37 | 1.4 | 4.7 | 0.632 | 0.632 | 0.298 | 0.883 | -0.0411 |
| 31 | Cephalopods | 1 | 1.2 | 4 | 0.839 | 0.84 | 0.3 | 0.255 | -0.03 |
| 32 | BA L crustaceans | 9.12 | 1.44 | 7.2 | 0.877 | 0.878 | 0.2 | 0 | 0 |
| 33 | BA molluscs | 17.86 | 1.5 | 16.7 | 0.888 | 0.89 | 0.0898 | 0 | 0 |
| 34 | BA worms | 5.32 | 3 | 33.3 | 0.805 | 0.806 | 0.0901 | 0 | 0 |
| 35 | BA crustaceans | 1.14 | 2.4 | 12 | 0.975 | 0.975 | 0.2 | 0 | 0 |
| 36 | BA other inverts | 0.57 | 1.8 | 9 | 0.868 | 0.869 | 0.2 | 0 | 0 |
| 37 | BA meiobenthos | 2.09 | 9 | 100 | 0.93 | 0.93 | 0.09 | 0 | 0 |
| 38 | shelf L crustaceans | 8.1 | 1.5 | 7.5 | 0.732 | 0.734 | 0.2 | 0.005 | 0 |
| 39 | shelf molluscs | 26.21 | 1.5 | 16.7 | 0.5 | 0.5 | 0.0898 | 3e-06 | 0 |
| 40 | shelf worms | 31.77 | 3 | 33 | 0.409 | 0.409 | 0.0909 | 0 | 0 |
| 41 | shelf crustaceans | 8.04 | 2.4 | 12 | 0.797 | 0.796 | 0.2 | 0 | 0 |
| 42 | shelf other inverts | 17.21 | 1.8 | 9 | 0.224 | 0.224 | 0.2 | 0 | 0 |
| 43 | shelf meiobenthos | 8.91 | 9 | 100 | 0.253 | 0.253 | 0.09 | 0 | 0 |
| 44 | mesozoopl. | 55.08 | 24 | 112 | 0.146 | 0.146 | 0.214 | 0 | 0 |
| 45 | macrozoopl. | 3.41 | 4.3 | 17 | 0.728 | 0.728 | 0.253 | 0 | 0 |
| 46 | BA mesozoopl. | 1.78 | 24 | 112 | 0.8 | 0.801 | 0.214 | 0 | 0 |
| 47 | BA macrozoopl. | 2.5 | 4.3 | 17 | 0.8 | 0.8 | 0.253 | 0 | 0 |
| 48 | BA phytopl. | 5.9 | 100 | 0 | 0.26 | 0.398 | - | 0 | 0 |
| 49 | phytoplankton | 67.8 | 100 | 0 | 0.853 | 0.852 | - | 0 | 0 |
| 50 | algae and eelgrass | 548.8 | 4.06 | 0 | 0.011 | 0.00785 | - | 0 | 0 |
| 51 | Detritus | 560 | 0 | 0 | 0.455 | - | - | 0 | unknown |
