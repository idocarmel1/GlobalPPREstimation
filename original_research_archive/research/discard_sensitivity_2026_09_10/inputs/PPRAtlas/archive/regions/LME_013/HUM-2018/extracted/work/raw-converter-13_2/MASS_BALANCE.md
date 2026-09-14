## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 13_Humboldt_Current_13_2_Northern_Humboldt_Current_(1995-1998), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 1 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 39 of 39 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 4219.158, group 6 (Gelatinous zooplankton).

Groups with recomputed EE > 1: 6 (Gelatinous zooplankton, 4220.108).

P/Q outside 0.02-0.5: 31 (Seabirds, 0.001), 32 (Pinnipeds, 0.003), 33 (Cetaceans, 0.005).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 6 (Gelatinous zooplankton): recomputed EE = 4220.108 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation

### Warnings

- group 31 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 32 (Pinnipeds): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 33 (Cetaceans): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 33 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Microzooplankton), 4 (Mesozooplankton), 5 (Macrozooplankton), 6 (Gelatinous zooplankton), 7 (Chrysaora plocamia), 8 (Macrobenthos), 9 (Sardine), 10 (Anchovy) ...
- detritus pools (4): inflow ~6925, consumption ~6162 t/km^2/year, implied EE ~0.890 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Diatoms | 34.09 | 237.5 | - | 0.8217 | 0.822 | - | 0 | unknown |
| 2 | Dino/silicoflagellates | 13.38 | 237.5 | - | 0.9669 | 0.967 | - | 0 | unknown |
| 3 | Microzooplankton | 13.54 | 256 | 1024 | 0.9567 | 0.957 | 0.25 | 0 | unknown |
| 4 | Mesozooplankton | 24.08 | 40 | 125 | 0.9262 | 0.936 | 0.32 | 0 | unknown |
| 5 | Macrozooplankton | 37.42 | 19.09 | 46.55 | 0.95 | 0.904 | 0.41 | 0 | unknown |
| 6 | Gelatinous zooplankton | 0.009068 | 0.584 | 2.92 | 0.95 | 4.22e+03 | 0.2 | 0 | unknown |
| 7 | Chrysaora plocamia | 8.464 | 15 | 56 | 6.118e-05 | 6.12e-05 | 0.268 | 0 | unknown |
| 8 | Macrobenthos | 23.17 | 1.2 | 10 | 0.7903 | 0.79 | 0.12 | 0 | unknown |
| 9 | Sardine | 10.74 | 1.4 | 12 | 0.97 | 0.97 | 0.117 | 5.826 | unknown |
| 10 | Anchovy | 58.32 | 2 | 15 | 0.8148 | 0.815 | 0.133 | 23.17 | unknown |
| 11 | Mesopelagic fish | 14.63 | 1.4 | 14 | 0.2639 | 0.264 | 0.1 | 0 | unknown |
| 12 | Jumbo squid | 0.3835 | 8.91 | 25.46 | 0.8 | 0.8 | 0.35 | 0.1055 | unknown |
| 13 | Other cephalopods | 1.806 | 4.3 | 10 | 0.95 | 0.95 | 0.43 | 0.03547 | unknown |
| 14 | Other small pelagic fish | 11 | 1 | 10 | 0.9 | 0.9 | 0.1 | 1.69 | unknown |
| 15 | Horse mackerel | 7.299 | 1.2 | 10 | 0.2355 | 0.236 | 0.12 | 1.747 | unknown |
| 16 | Chub mackerel | 7.69 | 0.85 | 10 | 0.1551 | 0.155 | 0.085 | 0.7427 | unknown |
| 17 | Other large pelagic fish | 1.173 | 0.625 | 6.25 | 0.534 | 0.534 | 0.1 | 0.3338 | unknown |
| 18 | Small hake | 2.008 | 1.122 | 7.483 | 0.7214 | 0.721 | 0.15 | 1.166 | unknown |
| 19 | Medium hake | 0.2885 | 1.786 | 11.91 | 0.1407 | 0.141 | 0.15 | 0.04868 | unknown |
| 20 | Large hake | 0.0415 | 1.28 | 8.533 | 0.8739 | 0.874 | 0.15 | 0.04633 | unknown |
| 21 | Flatfish | 0.025 | 0.304 | 2.027 | 0.9955 | 0.995 | 0.15 | 0.004058 | unknown |
| 22 | Small demersal fish | 5.23 | 2.3 | 15.33 | 0.7304 | 0.73 | 0.15 | 0.01934 | unknown |
| 23 | Benthic elasmobranchs | 0.0615 | 1 | 6.667 | 0.6587 | 0.659 | 0.15 | 0.04051 | unknown |
| 24 | Butter fishes | 0.019 | 0.8 | 4 | 0.5368 | 0.537 | 0.2 | 0 | unknown |
| 25 | Conger | 0.0115 | 0.75 | 5 | 0.01129 | 0.0113 | 0.15 | 0 | unknown |
| 26 | Medium demersal fish | 0.2055 | 1.9 | 12.67 | 0.8202 | 0.82 | 0.15 | 0.1496 | unknown |
| 27 | Medium sciaenids | 0.2935 | 0.9155 | 6.103 | 0.7098 | 0.71 | 0.15 | 0.0613 | unknown |
| 28 | Sea robin | 0.554 | 3.31 | 16.55 | 0.4585 | 0.459 | 0.2 | 0 | unknown |
| 29 | Catfish | 0.6135 | 0.9 | 6 | 0.8213 | 0.821 | 0.15 | 0.3398 | unknown |
| 30 | Chondrichthyans | 0.0525 | 0.486 | 3.24 | 0.5642 | 0.564 | 0.15 | 0.0144 | unknown |
| 31 | Seabirds | 0.0385 | 0.04 | 61 | 0 | 0 | 0.000656 | 0 | unknown |
| 32 | Pinnipeds | 0.0625 | 0.1 | 36.95 | 0 | 0 | 0.00271 | 0 | unknown |
| 33 | Cetaceans | 0.0645 | 0.1 | 20 | 0 | 0 | 0.005 | 0 | unknown |
| 34 | Green sea turtle | 0.000343 | 0.192 | 3.5 | 0 | 0 | 0.0549 | 0 | unknown |
| 35 | Leatherback turtle | 0.000162 | 0.192 | 3.5 | 0 | 0 | 0.0549 | 0 | unknown |
| 36 | Anchovy eggs | 0.436 | - | - | 0.8843 | - | - | 0 | unknown |
| 37 | Fishery offal | 0.05 | - | - | 0 | - | - | 0 | unknown |
| 38 | Pelagic detritus | 20 | - | - | 0 | - | - | 0 | unknown |
| 39 | Benthic detritus | 60 | - | - | 0.8891 | - | - | 0 | unknown |
