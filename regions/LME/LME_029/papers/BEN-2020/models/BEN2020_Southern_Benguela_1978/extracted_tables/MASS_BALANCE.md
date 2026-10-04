## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 29_Benguela_Current_20201978_Southern_Benguela_(1978), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 2 error(s), 3 indeterminate, 8 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 46 of 49 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.240, group 10 (Adult sardine).

Groups with recomputed EE > 1: 9 (Juvenile sardine, 1.200), 10 (Adult sardine, 1.219), 34 (Agulhas Sole, 1.006).

P/Q outside 0.02-0.5: 38 (Seals, 0.013), 39 (Cetaceans, 0.015), 40 (African Penguin, 0.002), 41 (Cape Gannet, 0.002), 42 (Cape Cormorant, 0.002), 43 (Other seabirds, 0.002).

BA: carried for 3 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 9 (Juvenile sardine, +0.0684), 10 (Adult sardine, +0.18), 47 (WC rock lobster, -0.603). The remaining 46 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 9 (Juvenile sardine): recomputed EE = 1.200 > 1 - catch+BA+predation (0.3829) exceeds production (0.3192)
- group 10 (Adult sardine): recomputed EE = 1.219 > 1 - catch+BA+predation (0.8774) exceeds production (0.72)

### Indeterminate (BA unknown)

- group 34 (Agulhas Sole): recomputed EE = 1.006 > 1 without BA, and BA is unknown - a BA of -6.698e-05 t/km^2/year (-0.02 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 40 (African Penguin): printed EE 0.612 vs recomputed 0.560 (diff 0.052) with BA unknown - a BA of +2.105e-05 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 41 (Cape Gannet): printed EE 0.485 vs recomputed 0.565 (diff 0.080) with BA unknown - a BA of -3.195e-05 t/km^2/year (-0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 9 (Juvenile sardine): printed EE 0.984 vs recomputed 1.200 (diff 0.216), BA 0.0684 carried
- group 10 (Adult sardine): printed EE 0.979 vs recomputed 1.219 (diff 0.240), BA 0.18 carried
- group 38 (Seals): P/Q = 0.013 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 39 (Cetaceans): P/Q = 0.015 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 40 (African Penguin): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 41 (Cape Gannet): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 42 (Cape Cormorant): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 43 (Other seabirds): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 43 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Microzooplankton), 4 (Mesozooplankton), 5 (Macrozooplankton), 6 (Gelatinous zooplankton), 7 (Anchovy recruits), 8 (Anchovy spawners), 9 (Juvenile sardine), 10 (Adult sardine) ...
- detritus pools (1): inflow ~1.234e+04, consumption ~3113 t/km^2/year, implied EE ~0.252 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton 1 | 35 | 200 | - | 0.328 | 0.328 | - | 0 | unknown |
| 2 | Phytoplankton 2 | 40 | 154.4 | - | 0.028 | 0.0278 | - | 0 | unknown |
| 3 | Microzooplankton | 2.178 | 482 | 1928 | 0.95 | 0.95 | 0.25 | 0 | unknown |
| 4 | Mesozooplankton | 8.875 | 40 | 133.3 | 0.95 | 0.95 | 0.3 | 0 | unknown |
| 5 | Macrozooplankton | 13.74 | 13 | 31.71 | 0.95 | 0.95 | 0.41 | 0 | unknown |
| 6 | Gelatinous zooplankton | 4.545 | 0.584 | 1.669 | 0.321 | 0.321 | 0.35 | 0 | unknown |
| 7 | Anchovy recruits | 4.535 | 1.2 | 19.04 | 0.976 | 0.979 | 0.063 | 0.714 | unknown |
| 8 | Anchovy spawners | 7.063 | 1.2 | 14.4 | 0.323 | 0.323 | 0.0833 | 0.238 | unknown |
| 9 | Juvenile sardine | 0.228 | 1.4 | 21.82 | 0.984 | 1.2 | 0.0642 | 0.041 | 0.0684 |
| 10 | Adult sardine | 0.6 | 1.2 | 12.37 | 0.979 | 1.22 | 0.097 | 0.4 | 0.18 |
| 11 | Redeye | 5.555 | 1.3 | 13 | 0.787 | 0.787 | 0.1 | 0.305 | unknown |
| 12 | Other small pelagics | 0.493 | 1 | 10 | 0.99 | 0.974 | 0.1 | 0.001 | unknown |
| 13 | Juvenile Hmack | 0.937 | 1.2 | 19.08 | 0.247 | 0.246 | 0.0629 | 0.016 | unknown |
| 14 | Adult Hmack | 1.618 | 1 | 10 | 0.89 | 0.889 | 0.1 | 0.254 | unknown |
| 15 | Chub mackerel | 0.284 | 0.8 | 8 | 0.837 | 0.834 | 0.1 | 0.0392 | unknown |
| 16 | Lanternfish | 4.433 | 1.2 | 12 | 0.99 | 0.99 | 0.1 | 0.005 | unknown |
| 17 | Lightfish | 4.392 | 1.2 | 12 | 0.99 | 0.99 | 0.1 | 0 | unknown |
| 18 | Snoek | 0.198 | 0.5 | 5 | 0.9 | 0.899 | 0.1 | 0.06861 | unknown |
| 19 | Tuna&Swordfish | 0.029 | 0.47 | 9.4 | 0.9 | 0.899 | 0.05 | 0.01 | unknown |
| 20 | Large Sparids | 0.012 | 0.5 | 5 | 0.9 | 0.866 | 0.1 | 0.0003 | unknown |
| 21 | Medium Sparids | 0.027 | 0.5 | 5 | 0.9 | 0.9 | 0.1 | 0.00725 | unknown |
| 22 | Sciaenids | 0.021 | 0.5 | 5 | 0.9 | 0.895 | 0.1 | 0.0045 | unknown |
| 23 | Yellowtail | 0.033 | 0.5 | 5 | 0.9 | 0.894 | 0.1 | 0.002 | unknown |
| 24 | Other linefish | 0.019 | 0.5 | 5 | 0.9 | 0.886 | 0.1 | 0.00095 | unknown |
| 25 | Mullet | 0.063 | 0.5 | 5 | 0.9 | 0.904 | 0.1 | 0.007 | unknown |
| 26 | Chokka Squid | 0.455 | 3.5 | 10 | 0.988 | 0.989 | 0.35 | 0.02301 | unknown |
| 27 | Other cephalopods | 0.9 | 3.5 | 10 | 0.969 | 0.968 | 0.35 | 0.0001 | unknown |
| 28 | Small M. capensis | 1.076 | 2 | 15.01 | 0.94 | 0.935 | 0.133 | 0.001 | unknown |
| 29 | Large M. capensis | 0.823 | 0.8 | 4.4 | 0.845 | 0.845 | 0.182 | 0.122 | unknown |
| 30 | Small M. paradoxus | 1.293 | - | 16.03 | 0.96 | - | - | 0.102 | unknown |
| 31 | Large M. paradoxus | 0.989 | - | 4.7 | 0.931 | - | - | 0.41 | unknown |
| 32 | PF Demersals | 1.912 | 0.7 | 3.5 | 0.9 | 0.9 | 0.2 | 0.0221 | unknown |
| 33 | BF Demersals | 4.464 | 0.7 | 3.5 | 0.9 | 0.9 | 0.2 | 0.0932 | unknown |
| 34 | Agulhas Sole | 0.006 | 0.7 | 3.5 | 0.99 | 1.01 | 0.2 | 0.004 | unknown |
| 35 | PF Chondrichthyans | 0.582 | 0.5 | 4.545 | 0.266 | 0.266 | 0.11 | 0.002 | unknown |
| 36 | BF Chondrichthyans | 0.873 | 1 | 10 | 0.82 | 0.82 | 0.1 | 0.011 | unknown |
| 37 | Apex Chondrichthyans | 0.045 | 0.5 | 5 | 0 | 0 | 0.1 | 0 | unknown |
| 38 | Seals | 0.133 | 0.25 | 19.31 | 0.961 | 0.96 | 0.0129 | 0.005 | unknown |
| 39 | Cetaceans | 0.083 | 0.15 | 10 | 0.9 | 0.904 | 0.015 | 0 | unknown |
| 40 | African Penguin | 0.002 | 0.201 | 96.98 | 0.612 | 0.56 | 0.00207 | 0 | unknown |
| 41 | Cape Gannet | 0.002 | 0.199 | 99.92 | 0.485 | 0.565 | 0.00199 | 0 | unknown |
| 42 | Cape Cormorant | 0.003 | 0.199 | 125.3 | 0.039 | 0.0377 | 0.00159 | 0 | unknown |
| 43 | Other seabirds | 0.053 | 0.199 | 125.9 | 0.633 | 0.633 | 0.00158 | 0 | unknown |
| 44 | Benthic Producers | 6.218 | 15 | - | 0.5 | 0.5 | - | 0 | unknown |
| 45 | Meiobenthos | 11.66 | 4 | 33 | 0.95 | 0.95 | 0.121 | 0 | unknown |
| 46 | Macrobenthos | 54.18 | 1.2 | 10 | 0.95 | 0.95 | 0.12 | 0 | unknown |
| 47 | WC rock lobster | 0.5 | 0.42 | 1.9 | 0.99 | 0.988 | 0.221 | 0.03 | -0.603 |
| 48 | SC rock lobster | 0.981 | 1.2 | 4 | 0.99 | 0.99 | 0.3 | 0.007 | unknown |
| 49 | Detritus | 50 | - | - | 0.243 | - | - | 0 | unknown |
