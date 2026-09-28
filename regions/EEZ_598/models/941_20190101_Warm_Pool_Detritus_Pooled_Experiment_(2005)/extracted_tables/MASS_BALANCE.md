## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 941_EEZ_Kiribati_Gilbert_Islands_proxy_20190101_Warm_Pool_Detritus_Pooled_Experiment_(2005), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 2 error(s), 0 indeterminate, 14 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 0 of 45 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 71.284, group 28 (Pomfret).

Groups with recomputed EE > 1: 28 (Pomfret, 72.234), 35 (Migratory mesopelagic molluscs, 1.005).

P/Q outside 0.02-0.5: 1 (Seabirds, 0.001).

BA: carried for 45 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Seabirds, +0), 2 (Cetaceans, +0), 3 (Sea turtles, +0), 4 (Small swordfish, +0), 5 (Large swordfish, +0), 6 (Blue marlin, +0), 7 (Striped marlin, +0), 8 (Other billfish, +0), 9 (Mako shark, +0), 10 (Blue shark, +0), 11 (Silky shark, +0), 12 (Oceanic whitetip shark, +0), 13 (Other sharks, +0), 14 (Small bigeye tuna, +0), 15 (Large bigeye tuna, +0), 16 (Small yellowfin tuna, +0), 17 (Large yellowfin tuna, +0), 18 (Juvenile skipjack, +0), 19 (Small skipjack, +0), 20 (Large skipjack, +0), 21 (Albacore, +0), 22 (Wahoo, +0), 23 (Dolphinfish, +0), 24 (Small tunas, +0), 25 (Escolar & Oilfish, +0), 26 (Lancetfish, +0), 27 (Opah, +0), 28 (Pomfret, +0), 29 (Rainbow runner, +0), 30 (Epipelagic crustaceans, +0), 31 (Epipelagic fish, +0), 32 (Epipelagic small fish, +0), 33 (Epipelagic molluscs, +0), 34 (Migratory mesopelagic fish & crustaceans, +0), 35 (Migratory mesopelagic molluscs, +0), 36 (Mesopelagic fish & crustaceans, +0), 37 (Mesopelagic molluscs, +0), 38 (Highly migratory bathypelagic forage, +0), 39 (Migratory bathypelagic forage, +0), 40 (Bathypelagic forage, +0), 41 (Mesozooplankton, +0), 42 (Microzooplankton, +0), 43 (Large phytoplankton, +0), 44 (Small phytoplankton, +0), 45 (Detritus and fishery discards (pooled experiment), +0). The remaining 0 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 28 (Pomfret): recomputed EE = 72.234 > 1 - catch+BA+predation (0.02129) exceeds production (0.0002948)
- group 35 (Migratory mesopelagic molluscs): recomputed EE = 1.005 > 1 - catch+BA+predation (2.772) exceeds production (2.758)

### Warnings

- group 1 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 6 (Blue marlin): printed EE 0.292 vs recomputed 0.222 (diff 0.070), BA 0 carried
- group 11 (Silky shark): printed EE 0.484 vs recomputed 0.359 (diff 0.125), BA 0 carried
- group 14 (Small bigeye tuna): printed EE 0.712 vs recomputed 0.337 (diff 0.375), BA 0 carried
- group 16 (Small yellowfin tuna): printed EE 0.42 vs recomputed 0.338 (diff 0.082), BA 0 carried
- group 17 (Large yellowfin tuna): printed EE 0.472 vs recomputed 0.153 (diff 0.319), BA 0 carried
- group 19 (Small skipjack): printed EE 0.514 vs recomputed 0.420 (diff 0.094), BA 0 carried
- group 20 (Large skipjack): printed EE 0.706 vs recomputed 0.430 (diff 0.276), BA 0 carried
- group 21 (Albacore): printed EE 0.144 vs recomputed 0.073 (diff 0.071), BA 0 carried
- group 22 (Wahoo): printed EE 0.71 vs recomputed 0.591 (diff 0.119), BA 0 carried
- group 23 (Dolphinfish): printed EE 0.95 vs recomputed 0.629 (diff 0.321), BA 0 carried
- group 25 (Escolar & Oilfish): printed EE 0.95 vs recomputed 0.694 (diff 0.256), BA 0 carried
- group 26 (Lancetfish): printed EE 0.95 vs recomputed 0.712 (diff 0.238), BA 0 carried
- group 28 (Pomfret): printed EE 0.95 vs recomputed 72.234 (diff 71.284), BA 0 carried

### Notes

- 42 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Seabirds), 2 (Cetaceans), 3 (Sea turtles), 4 (Small swordfish), 5 (Large swordfish), 6 (Blue marlin), 7 (Striped marlin), 8 (Other billfish) ...
- detritus pools (1): inflow ~1564, consumption ~1147 t/km^2/year, implied EE ~0.734 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Seabirds | 0.00058 | 0.044 | 74.99 | 0.02 | 0.0203 | 0.000587 | 4.61e-07 | 0 |
| 2 | Cetaceans | 0.00028 | 0.839 | 14.6 | 0.113 | 0.0953 | 0.0575 | 9.343e-06 | 0 |
| 3 | Sea turtles | 0.0013 | 0.19 | 7.3 | 0.159 | 0.162 | 0.026 | 5e-07 | 0 |
| 4 | Small swordfish | 0.00033 | 0.375 | 5.56 | 0.146 | 0.146 | 0.0674 | 1.28e-05 | 0 |
| 5 | Large swordfish | 0.00125 | 0.325 | 3.431 | 0.431 | 0.431 | 0.0947 | 0.0001725 | 0 |
| 6 | Blue marlin | 0.0003 | 0.429 | 7.3 | 0.292 | 0.222 | 0.0588 | 2.457e-05 | 0 |
| 7 | Striped marlin | 5.7e-05 | 0.902 | 13.14 | 0.389 | 0.388 | 0.0686 | 1.733e-05 | 0 |
| 8 | Other billfish | 0.00022 | 0.902 | 13.14 | 0.315 | 0.315 | 0.0686 | 5.978e-05 | 0 |
| 9 | Mako shark | 7e-05 | 0.577 | 7.3 | 0.438 | 0.453 | 0.079 | 1.824e-05 | 0 |
| 10 | Blue shark | 0.00097 | 0.44 | 3 | 0.204 | 0.204 | 0.147 | 8.7e-05 | 0 |
| 11 | Silky shark | 0.000738 | 0.577 | 3.5 | 0.484 | 0.359 | 0.165 | 0.0001529 | 0 |
| 12 | Oceanic whitetip shark | 9.2e-05 | 0.591 | 5.1 | 0.648 | 0.648 | 0.116 | 3.518e-05 | 0 |
| 13 | Other sharks | 0.0005 | 0.45 | 4.5 | 0.31 | 0.31 | 0.1 | 6.751e-05 | 0 |
| 14 | Small bigeye tuna | 0.00435 | 1.1 | 11 | 0.712 | 0.337 | 0.1 | 0.0006325 | 0 |
| 15 | Large bigeye tuna | 0.00271 | 0.51 | 5.011 | 0.519 | 0.512 | 0.102 | 0.0004986 | 0 |
| 16 | Small yellowfin tuna | 0.0311 | 1.5 | 14.6 | 0.42 | 0.338 | 0.103 | 0.009704 | 0 |
| 17 | Large yellowfin tuna | 0.00419 | 1.67 | 9.406 | 0.472 | 0.153 | 0.178 | 0.0009688 | 0 |
| 18 | Juvenile skipjack | 0.0204 | 1.66 | 13.03 | 0.422 | 0.43 | 0.127 | 8.454e-06 | 0 |
| 19 | Small skipjack | 0.0288 | 1 | 7.9 | 0.514 | 0.42 | 0.127 | 0.002707 | 0 |
| 20 | Large skipjack | 0.05101 | 0.878 | 6.227 | 0.706 | 0.43 | 0.141 | 0.01661 | 0 |
| 21 | Albacore | 0.0265 | 0.9 | 11 | 0.144 | 0.0729 | 0.0818 | 0.0002188 | 0 |
| 22 | Wahoo | 0.000102 | 1.8 | 17 | 0.71 | 0.591 | 0.106 | 5.289e-05 | 0 |
| 23 | Dolphinfish | 0.002629 | 3.485 | 20.44 | 0.95 | 0.629 | 0.17 | 0.0001069 | 0 |
| 24 | Small tunas | 0.034 | 1.5 | 7.957 | 0.95 | 0.913 | 0.189 | 0.0001797 | 0 |
| 25 | Escolar & Oilfish | 0.001646 | 0.408 | 3.6 | 0.95 | 0.694 | 0.113 | 5.37e-06 | 0 |
| 26 | Lancetfish | 0.006384 | 0.47 | 4 | 0.95 | 0.712 | 0.117 | 6.54e-06 | 0 |
| 27 | Opah | 0.000107 | 0.392 | 3.9 | 0.94 | 0.946 | 0.101 | 2.73e-05 | 0 |
| 28 | Pomfret | 0.000302 | 0.976 | 8.91 | 0.95 | 72.2 | 0.11 | 4.849e-06 | 0 |
| 29 | Rainbow runner | 0.02416 | 0.868 | 7.957 | 0.95 | 0.909 | 0.109 | 0.0009975 | 0 |
| 30 | Epipelagic crustaceans | 13.28 | 3.3 | 14.6 | 0.95 | 0.95 | 0.226 | 0 | 0 |
| 31 | Epipelagic fish | 3.046 | 3.4 | 14 | 0.95 | 0.947 | 0.243 | 7.28e-05 | 0 |
| 32 | Epipelagic small fish | 7.28 | 6 | 22 | 0.95 | 0.948 | 0.273 | 0 | 0 |
| 33 | Epipelagic molluscs | 2.832 | 4.7 | 14.6 | 0.95 | 0.945 | 0.322 | 0 | 0 |
| 34 | Migratory mesopelagic fish & crustaceans | 1.439 | 4.6 | 13 | 0.993 | 0.983 | 0.354 | 0 | 0 |
| 35 | Migratory mesopelagic molluscs | 0.613 | 4.5 | 15 | 0.977 | 1 | 0.3 | 0 | 0 |
| 36 | Mesopelagic fish & crustaceans | 0.384 | 4.45 | 13 | 0.988 | 0.98 | 0.342 | 0 | 0 |
| 37 | Mesopelagic molluscs | 0.224 | 4.4 | 15 | 0.975 | 0.97 | 0.293 | 0 | 0 |
| 38 | Highly migratory bathypelagic forage | 0.798 | 2.2 | 9 | 0.646 | 0.644 | 0.244 | 0 | 0 |
| 39 | Migratory bathypelagic forage | 0.302 | 2 | 8 | 0.983 | 0.983 | 0.25 | 0 | 0 |
| 40 | Bathypelagic forage | 0.221 | 1.7 | 6.5 | 0.767 | 0.767 | 0.262 | 0 | 0 |
| 41 | Mesozooplankton | 4.358 | 70 | 218 | 0.325 | 0.325 | 0.321 | 0 | 0 |
| 42 | Microzooplankton | 3.842 | 110 | 365 | 0.506 | 0.506 | 0.301 | 0 | 0 |
| 43 | Large phytoplankton | 1.849 | 131 | - | 0.829 | 0.829 | - | 0 | 0 |
| 44 | Small phytoplankton | 10.48 | 152 | - | 0.665 | 0.665 | - | 0 | 0 |
| 45 | Detritus and fishery discards (pooled experiment) | 53 | - | - | - | - | - | 0 | 0 |
