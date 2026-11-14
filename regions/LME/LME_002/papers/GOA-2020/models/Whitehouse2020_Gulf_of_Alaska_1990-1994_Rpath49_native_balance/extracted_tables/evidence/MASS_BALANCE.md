## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 2_Gulf_of_Alaska_Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance_Gulf_of_Alaska_(1990-1994), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 10 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 0 of 49 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.000, group 23 (Octopods).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Toothed whales, 0.004), 2 (Gray whale, 0.007), 3 (Other baleen, 0.004), 4 (Other pinnipeds, 0.003), 5 (Procellarids, 0.001), 6 (Alcids piscivorous, 0.001), 7 (Larids, 0.001), 8 (Alcids planktivorous, 0.002), 9 (Other seabirds, 0.001), 10 (Cormorants, 0.002).

BA: carried for 49 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Toothed whales, +0), 2 (Gray whale, +0), 3 (Other baleen, +0), 4 (Other pinnipeds, +0), 5 (Procellarids, +0), 6 (Alcids piscivorous, +0), 7 (Larids, +0), 8 (Alcids planktivorous, +0), 9 (Other seabirds, +0), 10 (Cormorants, +0), 11 (Sharks, +0), 12 (Walleye pollock, -1.35), 13 (Pacific cod, +0), 14 (Pelagic forage fish, -0.11), 15 (Lg.-mouth flatfish, +0), 16 (Sm.-mouth flatfish, +0), 17 (Skates, +0), 18 (Other demersals, -0.002), 19 (Eelpouts, +0), 20 (Lg.-mouth sculpins, +0), 21 (Other sculpins, +0), 22 (Misc. shallow fish, +0), 23 (Octopods, +0), 24 (Squid, +0), 25 (Salmon returning, +0), 26 (Salmon outgoing, +0), 27 (Other crabs, +0), 28 (Shrimps, +0), 29 (Sea stars, +0), 30 (Brittle stars, +0), 31 (Urchins dollars cucumbers, +0), 32 (Snails, +0), 33 (Misc. crustaceans, +0), 34 (Benthic amphipods, +0), 35 (Anemones, +0), 36 (Corals and sea pens, +0), 37 (Worms etc., +0), 38 (Benthic urochordate, +0), 39 (Sponge, +0), 40 (Bivalves, +0), 41 (Polychaetes, +0), 42 (Scyphozoid jellies, +0), 43 (Other zooplankton, +0), 44 (Copepods, +0), 45 (Pelagic microbes, +0), 46 (Benthic microbes, +0), 47 (Primary production, +0), 48 (Pelagic detritus, +0), 49 (Benthic detritus, +0). The remaining 0 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 1 (Toothed whales): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Gray whale): P/Q = 0.007 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Other baleen): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Other pinnipeds): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 5 (Procellarids): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 6 (Alcids piscivorous): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 7 (Larids): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 8 (Alcids planktivorous): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 9 (Other seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 10 (Cormorants): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 47 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Toothed whales), 2 (Gray whale), 3 (Other baleen), 4 (Other pinnipeds), 5 (Procellarids), 6 (Alcids piscivorous), 7 (Larids), 8 (Alcids planktivorous) ...
- detritus pools (2): inflow ~4058, consumption ~1451 t/km^2/year, implied EE ~0.358 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Toothed whales | 0.06166 | 0.04714 | 12.44 | 0.01438 | 0.0144 | 0.00379 | 9.74e-07 | 0 |
| 2 | Gray whale | 0.05543 | 0.06337 | 8.873 | 0.04275 | 0.0427 | 0.00714 | 8.57e-08 | 0 |
| 3 | Other baleen | 0.4567 | 0.03134 | 6.981 | 0.09 | 0.09 | 0.00449 | 5.19e-05 | 0 |
| 4 | Other pinnipeds | 0.03346 | 0.1223 | 36.81 | 0.0453 | 0.0453 | 0.00332 | 9.479e-05 | 0 |
| 5 | Procellarids | 0.001052 | 0.06488 | 73 | 0.4245 | 0.425 | 0.000889 | 1.43e-06 | 0 |
| 6 | Alcids piscivorous | 0.01132 | 0.09529 | 72.57 | 0.289 | 0.289 | 0.00131 | 1.54e-05 | 0 |
| 7 | Larids | 0.001459 | 0.1116 | 95.56 | 0.247 | 0.247 | 0.00117 | 1.98e-06 | 0 |
| 8 | Alcids planktivorous | 0.0002997 | 0.1695 | 110 | 0.1626 | 0.163 | 0.00154 | 4.07e-07 | 0 |
| 9 | Other seabirds | 0.0004618 | 0.09378 | 109.5 | 0.2936 | 0.294 | 0.000856 | 6.27e-07 | 0 |
| 10 | Cormorants | 0.0003489 | 0.1587 | 73 | 0.1734 | 0.173 | 0.00217 | 4.74e-07 | 0 |
| 11 | Sharks | 0.1424 | 0.1 | 3.729 | 0.7052 | 0.705 | 0.0268 | 0.006119 | 0 |
| 12 | Walleye pollock | 6.224 | 0.6538 | 4.109 | 0.909 | 0.909 | 0.159 | 0.3429 | -1.35 |
| 13 | Pacific cod | 1.52 | 0.5577 | 2.396 | 0.619 | 0.619 | 0.233 | 0.2508 | 0 |
| 14 | Pelagic forage fish | 14.27 | 0.818 | 3.676 | 0.8002 | 0.8 | 0.223 | 0.05601 | -0.11 |
| 15 | Lg.-mouth flatfish | 8.015 | 0.293 | 1.444 | 0.2423 | 0.242 | 0.203 | 0.1664 | 0 |
| 16 | Sm.-mouth flatfish | 2.444 | 0.2152 | 1.933 | 0.468 | 0.468 | 0.111 | 0.07293 | 0 |
| 17 | Skates | 0.1918 | 0.2 | 2 | 0.5991 | 0.599 | 0.1 | 0.01479 | 0 |
| 18 | Other demersals | 4.506 | 0.1831 | 2.247 | 0.6575 | 0.658 | 0.0815 | 0.1934 | -0.002 |
| 19 | Eelpouts | 1.069 | 0.4 | 2 | 0.8 | 0.8 | 0.2 | 2.426e-05 | 0 |
| 20 | Lg.-mouth sculpins | 0.08889 | 0.4 | 2 | 0.6763 | 0.676 | 0.2 | 0.004449 | 0 |
| 21 | Other sculpins | 0.8169 | 0.4 | 2 | 0.8 | 0.8 | 0.2 | 0 | 0 |
| 22 | Misc. shallow fish | 0.839 | 0.4 | 2 | 0.8 | 0.8 | 0.2 | 0.00124 | 0 |
| 23 | Octopods | 0.7835 | 0.8 | 3.65 | 0.8 | 0.8 | 0.219 | 0.0003331 | 0 |
| 24 | Squid | 1.265 | 3.2 | 10.67 | 0.8 | 0.8 | 0.3 | 0.0003451 | 0 |
| 25 | Salmon returning | 0.8566 | 1.816 | 11.83 | 0.4975 | 0.498 | 0.154 | 0.3202 | 0 |
| 26 | Salmon outgoing | 0.01713 | 1.642 | 14.39 | 0.1244 | 0.124 | 0.114 | 0 | 0 |
| 27 | Other crabs | 5.218 | 0.8414 | 3.966 | 0.8001 | 0.8 | 0.212 | 0.003849 | 0 |
| 28 | Shrimps | 22.23 | 0.576 | 2.41 | 0.8 | 0.8 | 0.239 | 0.0002038 | 0 |
| 29 | Sea stars | 0.09552 | 1.21 | 6.05 | 0.4918 | 0.492 | 0.2 | 0.003116 | 0 |
| 30 | Brittle stars | 4.544 | 1.21 | 6.05 | 0.2014 | 0.201 | 0.2 | 0 | 0 |
| 31 | Urchins dollars cucumbers | 1.631 | 0.61 | 3.05 | 0.3504 | 0.35 | 0.2 | 7.771e-05 | 0 |
| 32 | Snails | 0.8639 | 1.81 | 9.05 | 0.8 | 0.8 | 0.2 | 3.27e-07 | 0 |
| 33 | Misc. crustaceans | 2.12 | 7.4 | 37 | 0.8 | 0.8 | 0.2 | 0 | 0 |
| 34 | Benthic amphipods | 5.869 | 7.4 | 37 | 0.8 | 0.8 | 0.2 | 0 | 0 |
| 35 | Anemones | 0.08887 | 1 | 5 | 0.001912 | 0.00191 | 0.2 | 7.431e-05 | 0 |
| 36 | Corals and sea pens | 0.00574 | 0.05046 | 0.2523 | 0.1206 | 0.121 | 0.2 | 2.728e-05 | 0 |
| 37 | Worms etc. | 3.773 | 2.196 | 10.98 | 0.8 | 0.8 | 0.2 | 0 | 0 |
| 38 | Benthic urochordate | 0.2448 | 3.58 | 17.9 | 0.00936 | 0.00936 | 0.2 | 6.744e-06 | 0 |
| 39 | Sponge | 0.1075 | 1 | 5 | 0.002693 | 0.00269 | 0.2 | 2.11e-05 | 0 |
| 40 | Bivalves | 13.85 | 1.3 | 6.5 | 0.8 | 0.8 | 0.2 | 0.0002807 | 0 |
| 41 | Polychaetes | 3.923 | 2.97 | 14.85 | 0.8 | 0.8 | 0.2 | 0 | 0 |
| 42 | Scyphozoid jellies | 0.11 | 0.88 | 3 | 0.4836 | 0.484 | 0.293 | 0.0003371 | 0 |
| 43 | Other zooplankton | 24 | 5.308 | 15.16 | 0.8 | 0.8 | 0.35 | 0 | 0 |
| 44 | Copepods | 21.86 | 6 | 27.74 | 0.8 | 0.8 | 0.216 | 0 | 0 |
| 45 | Pelagic microbes | 12.26 | 36.5 | 104.3 | 0.8 | 0.8 | 0.35 | 0 | 0 |
| 46 | Benthic microbes | 7.252 | 36.5 | 104.3 | 0.8 | 0.8 | 0.35 | 0 | 0 |
| 47 | Primary production | 40.4 | 110.2 | 0 | 0.3182 | 0.318 | - | 0 | 0 |
| 48 | Pelagic detritus | 3980 | 0.5 | 0 | 0.1927 | 0.193 | - | 0 | 0 |
| 49 | Benthic detritus | 4135 | 0.5 | 0 | 0.5165 | 0.516 | - | 0 | 0 |
