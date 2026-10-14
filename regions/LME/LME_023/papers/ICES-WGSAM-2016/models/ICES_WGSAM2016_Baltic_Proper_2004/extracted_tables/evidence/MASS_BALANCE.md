## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 23_Baltic_Sea_ICES_WGSAM2016_Baltic_Proper_2004_Baltic_Proper_Rpath_port_(2004), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 2 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 0 of 22 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.000, group 16 (Mysids).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (GreySeal, 0.006), 2 (FishFeedingBirds, 0.001).

BA: carried for 22 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (GreySeal, +0.00036), 2 (FishFeedingBirds, +0), 3 (JuvCod, +0), 4 (AdCod, +0), 5 (JuvHerring, +0), 6 (AdHerring, +0), 7 (JuvSprat, +0), 8 (AdSprat, +0), 9 (JuvFlounder, +0), 10 (AdFlounder, +0), 11 (SaduriaEntemon, +0), 12 (MytilusSp, +0), 13 (MacomaBalthica, +0), 14 (OtherMacrozoobenthos, +0), 15 (Meiobenthos, +0), 16 (Mysids, +0), 17 (OtherZooplankton, +0), 18 (PseudocalanusSp, +0), 19 (AcartiaSp, +0), 20 (TemoraSp, +0), 21 (Phytoplankton, +0), 22 (Detritus, +0). The remaining 0 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 1 (GreySeal): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (FishFeedingBirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 21 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (GreySeal), 2 (FishFeedingBirds), 3 (JuvCod), 4 (AdCod), 5 (JuvHerring), 6 (AdHerring), 7 (JuvSprat), 8 (AdSprat) ...
- detritus pools (1): inflow ~943, consumption ~354.1 t/km^2/year, implied EE ~0.375 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GreySeal | 0.006 | 0.1 | 16.28 | 0.6 | 0.6 | 0.00614 | 0 | 0.00036 |
| 2 | FishFeedingBirds | 0.002 | 0.1 | 130 | 0 | 0 | 0.000769 | 0 | 0 |
| 3 | JuvCod | 0.3537 | 1.092 | 7.649 | 0.07569 | 0.0757 | 0.143 | 0.001716 | 0 |
| 4 | AdCod | 0.33 | 0.885 | 3.81 | 0.9831 | 0.983 | 0.232 | 0.284 | 0 |
| 5 | JuvHerring | 1.021 | 0.948 | 5.626 | 0.2287 | 0.229 | 0.169 | 0.02353 | 0 |
| 6 | AdHerring | 2.72 | 0.79 | 3 | 0.5716 | 0.572 | 0.263 | 0.3639 | 0 |
| 7 | JuvSprat | 4.692 | 1.605 | 8.704 | 0.1418 | 0.142 | 0.184 | 0.3138 | 0 |
| 8 | AdSprat | 4.48 | 1.07 | 4.63 | 0.4656 | 0.466 | 0.231 | 1.06 | 0 |
| 9 | JuvFlounder | 0.3816 | 1.143 | 9.08 | 0.1056 | 0.106 | 0.126 | 0.008315 | 0 |
| 10 | AdFlounder | 0.463 | 0.762 | 4.21 | 0.7823 | 0.782 | 0.181 | 0.273 | 0 |
| 11 | SaduriaEntemon | 2 | 1.3 | 5 | 0.3011 | 0.301 | 0.26 | 0 | 0 |
| 12 | MytilusSp | 10 | 1.75 | 8.73 | 0.05049 | 0.0505 | 0.2 | 0 | 0 |
| 13 | MacomaBalthica | 45 | 0.4 | 2 | 0.03678 | 0.0368 | 0.2 | 0 | 0 |
| 14 | OtherMacrozoobenthos | 11.38 | 2 | 10 | 0.9018 | 0.902 | 0.2 | 0 | 0 |
| 15 | Meiobenthos | 6.8 | 6.17 | 31.17 | 0.9243 | 0.924 | 0.198 | 0 | 0 |
| 16 | Mysids | 2.202 | 5 | 15 | 0.75 | 0.75 | 0.333 | 0 | 0 |
| 17 | OtherZooplankton | 4.006 | 30 | 100 | 0.223 | 0.223 | 0.3 | 0 | 0 |
| 18 | PseudocalanusSp | 1.93 | 7 | 27 | 0.9415 | 0.941 | 0.259 | 0 | 0 |
| 19 | AcartiaSp | 3.027 | 25 | 83 | 0.1914 | 0.191 | 0.301 | 0 | 0 |
| 20 | TemoraSp | 2.271 | 25 | 83 | 0.5498 | 0.55 | 0.301 | 0 | 0 |
| 21 | Phytoplankton | 7.05 | 200 | 0 | 0.715 | 0.715 | - | 0 | 0 |
| 22 | Detritus | 1645 | 0.5733 | 0 | 0.3755 | 0.375 | - | 0 | 0 |
