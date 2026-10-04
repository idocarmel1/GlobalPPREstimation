## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 49_Kuroshio_Current_20252023_Kuroshio_Oyashio_Extension_Chen_(2023), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 16 indeterminate, 1 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 25 of 25 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 44.814, group 8 (Large mesopelagic fishes).

Groups with recomputed EE > 1: 6 (Ocean sunfish, 1.056), 8 (Large mesopelagic fishes, 45.364), 9 (Large pelagic fishes, 4.835), 10 (Small mesopelagic fishes, 1.334), 11 (Small pelagic fishes, 1.083), 18 (Lantern fish, 12.703), 19 (Cephalopoda, 2.145), 22 (Other crustaceans, 1.687).

P/Q outside 0.02-0.5: 23 (Zooplankton, 0.511).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 3 (Swordfish): printed EE 0.16 vs recomputed 0.000 (diff 0.160) with BA unknown - a BA of +0.0009173 t/km^2/year (+0.16 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 4 (Tunas): printed EE 0.81 vs recomputed 0.603 (diff 0.207) with BA unknown - a BA of +0.001303 t/km^2/year (+0.21 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 6 (Ocean sunfish): recomputed EE = 1.056 > 1 without BA, and BA is unknown - a BA of -0.0001746 t/km^2/year (-0.11 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 8 (Large mesopelagic fishes): recomputed EE = 45.364 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 9 (Large pelagic fishes): recomputed EE = 4.835 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 10 (Small mesopelagic fishes): recomputed EE = 1.334 > 1 without BA, and BA is unknown - a BA of -0.137 t/km^2/year (-0.38 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 11 (Small pelagic fishes): recomputed EE = 1.083 > 1 without BA, and BA is unknown - a BA of -0.02016 t/km^2/year (-0.13 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 12 (Pomfret): printed EE 0.13 vs recomputed 0.782 (diff 0.652) with BA unknown - a BA of -0.006913 t/km^2/year (-0.65 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 13 (Medusafish; barrelfish and driftfish): printed EE 0.79 vs recomputed 0.541 (diff 0.249) with BA unknown - a BA of +0.000142 t/km^2/year (+0.25 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 14 (Chub mackerel): printed EE 0.17 vs recomputed 0.062 (diff 0.108) with BA unknown - a BA of +0.02245 t/km^2/year (+0.11 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 15 (Japanese anchovy): printed EE 0.95 vs recomputed 0.100 (diff 0.850) with BA unknown - a BA of +0.2811 t/km^2/year (+0.85 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 18 (Lantern fish): recomputed EE = 12.703 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 19 (Cephalopoda): recomputed EE = 2.145 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 20 (Small cephalopoda): printed EE 0.95 vs recomputed 0.097 (diff 0.853) with BA unknown - a BA of +0.1568 t/km^2/year (+0.85 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 21 (Krill): printed EE 0.95 vs recomputed 0.476 (diff 0.474) with BA unknown - a BA of +0.5626 t/km^2/year (+0.47 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 22 (Other crustaceans): recomputed EE = 1.687 > 1 without BA, and BA is unknown - a BA of -1.593 t/km^2/year (-0.74 of production) would close it - undecidable until the source is checked for biomass accumulation

### Warnings

- group 23 (Zooplankton): P/Q = 0.511 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 23 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Blue shark), 2 (Other sharks), 3 (Swordfish), 4 (Tunas), 5 (Pelagic stingray), 6 (Ocean sunfish), 7 (Salmon), 8 (Large mesopelagic fishes) ...
- detritus pools (1): inflow ~958.9, consumption ~3.242 t/km^2/year, implied EE ~0.003 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Blue shark | 0.0111 | 0.46 | 2.75 | 0.05 | 0.0564 | 0.167 | 0 | unknown |
| 2 | Other sharks | 0.0057 | 0.39 | 2.5 | 0.13 | 0.135 | 0.156 | 0.0003 | unknown |
| 3 | Swordfish | 0.0117 | 0.49 | 2.5 | 0.16 | 0 | 0.196 | 0 | unknown |
| 4 | Tunas | 0.015 | 0.42 | 4.6 | 0.81 | 0.603 | 0.0913 | 0.0038 | unknown |
| 5 | Pelagic stingray | 0.0005 | 0.75 | 2.5 | 0.51 | 0.533 | 0.3 | 0.0002 | unknown |
| 6 | Ocean sunfish | 0.0022 | 0.75 | 2.5 | 0.95 | 1.06 | 0.3 | 0 | unknown |
| 7 | Salmon | 0.0044 | 1.94 | 6.47 | 0.11 | 0.0722 | 0.3 | 0 | unknown |
| 8 | Large mesopelagic fishes | 0.0002 | 0.45 | 1.5 | 0.55 | 45.4 | 0.3 | 0 | unknown |
| 9 | Large pelagic fishes | 0.0008 | 1.59 | 5.3 | 0.6 | 4.83 | 0.3 | 0.0008 | unknown |
| 10 | Small mesopelagic fishes | 0.1429 | 2.5 | 10 | 0.95 | 1.33 | 0.25 | 0.0004 | unknown |
| 11 | Small pelagic fishes | 0.1 | 1.52 | 5.07 | 0.95 | 1.08 | 0.3 | 0.0002 | unknown |
| 12 | Pomfret | 0.0221 | 0.48 | 5.8 | 0.13 | 0.782 | 0.0828 | 0 | unknown |
| 13 | Medusafish; barrelfish and driftfish | 0.0006 | 0.95 | 4.86 | 0.79 | 0.541 | 0.195 | 0 | unknown |
| 14 | Chub mackerel | 0.0743 | 2.79 | 11.63 | 0.17 | 0.0617 | 0.24 | 0.0125 | unknown |
| 15 | Japanese anchovy | 0.1117 | 2.96 | 9.87 | 0.95 | 0.0997 | 0.3 | 0.0001 | unknown |
| 16 | Pacific sardine | 0.5777 | 0.9 | 5.61 | 0.74 | 0.72 | 0.16 | 0.1037 | unknown |
| 17 | Pacific saury | 0.3984 | 1.25 | 4.17 | 0.95 | 0.94 | 0.3 | 0.46 | unknown |
| 18 | Lantern fish | 0.0383 | 3.2 | 10 | 0.65 | 12.7 | 0.32 | 0 | unknown |
| 19 | Cephalopoda | 0.1278 | 2.56 | 7.3 | 0.95 | 2.14 | 0.351 | 0.0006 | unknown |
| 20 | Small cephalopoda | 0.0525 | 3.5 | 13.64 | 0.95 | 0.0966 | 0.257 | 0 | unknown |
| 21 | Krill | 0.4641 | 2.56 | 12.05 | 0.95 | 0.476 | 0.212 | 0 | unknown |
| 22 | Other crustaceans | 0.2702 | 8 | 30 | 0.95 | 1.69 | 0.267 | 0 | unknown |
| 23 | Zooplankton | 10.48 | 23.16 | 45.35 | 0.06 | 0.0458 | 0.511 | 0 | unknown |
| 24 | Phytoplankton | 7.189 | 153.8 | - | 0.43 | 0.433 | - | 0 | unknown |
| 25 | Detritus | 28.5 | - | - | 0.01 | - | - | 0 | unknown |
