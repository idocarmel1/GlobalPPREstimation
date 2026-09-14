## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 22_20251990_East_Coast_of_Scotland_(1991-1995), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 2 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 25 of 25 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.171, group 9 (Turbot).

Groups with recomputed EE > 1: 11 (Ling, 1.003).

P/Q outside 0.02-0.5: 22 (Seabirds, 0.006), 23 (Seals, 0.004), 24 (Cetaceans, 0.002).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 9 (Turbot): printed EE 0.82 vs recomputed 0.991 (diff 0.171) with BA unknown - a BA of -0.002731 t/km^2/year (-0.17 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 11 (Ling): recomputed EE = 1.003 > 1 without BA, and BA is unknown - a BA of -0.003647 t/km^2/year (-0.06 of production) would close it - undecidable until the source is checked for biomass accumulation

### Warnings

- group 22 (Seabirds): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 23 (Seals): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 24 (Cetaceans): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 23 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 2 (Small zooplankton), 3 (Large zooplankton), 4 (Infauna), 5 (Epifauna), 6 (Crustacea), 7 (Squid & Octopus), 8 (Flatfishes), 9 (Turbot) ...
- detritus pools (1): inflow ~1783, consumption ~220.7 t/km^2/year, implied EE ~0.124 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 7.5 | 286 | - | 0.29 | 0.287 | - | 0 | unknown |
| 2 | Small zooplankton | 16 | 9.17 | 30 | 0.84 | 0.839 | 0.306 | 0 | unknown |
| 3 | Large zooplankton | 14.32 | 4 | 12.5 | 0.9 | 0.901 | 0.32 | 0 | unknown |
| 4 | Infauna | 2.54 | 20 | 80 | 0.9 | 0.902 | 0.25 | 0 | unknown |
| 5 | Epifauna | 1.36 | 18.09 | 72.65 | 0.88 | 0.879 | 0.249 | 0.01509 | unknown |
| 6 | Crustacea | 2.41 | 2.26 | 13.44 | 0.81 | 0.805 | 0.168 | 0.04303 | unknown |
| 7 | Squid & Octopus | 0.09 | 2 | 15 | 0.95 | 0.918 | 0.133 | 0.003547 | unknown |
| 8 | Flatfishes | 1.11 | 0.71 | 4.28 | 0.91 | 0.908 | 0.166 | 0.1324 | unknown |
| 9 | Turbot | 0.02 | 0.8 | 3.95 | 0.82 | 0.991 | 0.203 | 0.009365 | unknown |
| 10 | Cod | 0.41 | 1.36 | 5.78 | 0.86 | 0.848 | 0.235 | 0.1528 | unknown |
| 11 | Ling | 0.06 | 0.97 | 3.25 | 0.94 | 1 | 0.298 | 0.04964 | unknown |
| 12 | Haddock | 0.54 | 1.39 | 8.09 | 0.92 | 0.927 | 0.172 | 0.2887 | unknown |
| 13 | Whiting | 0.25 | 1.21 | 7.61 | 0.89 | 0.916 | 0.159 | 0.09538 | unknown |
| 14 | Hake | 0.05 | 1.14 | 3.85 | 0.92 | 0.964 | 0.296 | 0.0467 | unknown |
| 15 | Saithe | 1.21 | 0.69 | 3.29 | 0.91 | 0.908 | 0.21 | 0.495 | unknown |
| 16 | Monkfish | 0.08 | 0.54 | 2.48 | 0.93 | 0.97 | 0.218 | 0.03812 | unknown |
| 17 | Large Dem. fish | 0.32 | 0.45 | 3.62 | 0.94 | 0.942 | 0.124 | 0.05281 | unknown |
| 18 | Herring | 2.6 | 1.31 | 6.55 | 0.9 | 0.901 | 0.2 | 1.082 | unknown |
| 19 | Small pelagics | 6.07 | 1.89 | 8.5 | 0.88 | 0.898 | 0.222 | 0.6157 | unknown |
| 20 | Large Pelagics | 2.41 | 0.54 | 4.83 | 0.9 | 0.901 | 0.112 | 0.3121 | unknown |
| 21 | Sharks & rays | 0.51 | 0.43 | 3.53 | 0.43 | 0.425 | 0.122 | 0.02917 | unknown |
| 22 | Seabirds | 0.01 | 0.4 | 66.74 | 0.03 | 0.0334 | 0.00599 | 0 | unknown |
| 23 | Seals | 0.02 | 0.06 | 14.39 | 0.03 | 0.0283 | 0.00417 | 3.4e-05 | unknown |
| 24 | Cetaceans | 0.12 | 0.02 | 8.43 | 0.04 | 0.0402 | 0.00237 | 9.65e-05 | unknown |
| 25 | Detritus | 100 | - | - | 0.12 | - | - | 0 | unknown |
