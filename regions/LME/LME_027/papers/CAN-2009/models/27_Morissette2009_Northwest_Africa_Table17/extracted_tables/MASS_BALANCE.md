## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 27_Canary_Current_Morissette2009_Table17_Northwest_Africa_(late 1980s), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 1 error(s), 1 indeterminate, 10 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 27 of 27 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.500, group 26 (Phytoplankton).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Minke whales, 0.012), 3 (Humpback whales, 0.019), 4 (Brydes whales, 0.016), 5 (Sei whales, 0.003), 6 (Sperm whales, 0.010), 7 (Killer whales, 0.003), 8 (Baleen whales, 0.012), 9 (Beaked whales, 0.004), 10 (Dolphins, 0.003), 11 (Seabirds, 0.001).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 25 (Zooplankton) has Q/B=274.805 but no diet entries - its consumption is missing from every prey's budget

### Indeterminate (BA unknown)

- group 26 (Phytoplankton): printed EE 0.5151 vs recomputed 0.015 (diff 0.500) with BA unknown - a BA of +5670 t/km^2/year (+0.50 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 1 (Minke whales): P/Q = 0.012 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Humpback whales): P/Q = 0.019 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Brydes whales): P/Q = 0.016 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 5 (Sei whales): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 6 (Sperm whales): P/Q = 0.010 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 7 (Killer whales): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 8 (Baleen whales): P/Q = 0.012 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 9 (Beaked whales): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 10 (Dolphins): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 11 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 24 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Minke whales), 2 (Fin whales), 3 (Humpback whales), 4 (Brydes whales), 5 (Sei whales), 6 (Sperm whales), 7 (Killer whales), 8 (Baleen whales) ...
- detritus pools (1): inflow ~9413, consumption ~3478 t/km^2/year, implied EE ~0.370 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Minke whales | 0.00844 | 0.099 | 8.421 | 0 | 0 | 0.0118 | 0 | unknown |
| 2 | Fin whales | 0.0122 | 0.099 | 4.161 | 0 | 0 | 0.0238 | 0 | unknown |
| 3 | Humpback whales | 0.00302 | 0.099 | 5.078 | 0 | 0 | 0.0195 | 0 | unknown |
| 4 | Brydes whales | 0.00785 | 0.099 | 6.26 | 0 | 0 | 0.0158 | 0 | unknown |
| 5 | Sei whales | 0.0016 | 0.02 | 6.178 | 0 | 0 | 0.00324 | 0 | unknown |
| 6 | Sperm whales | 0.0202 | 0.05 | 5.025 | 0 | 0 | 0.00995 | 0 | unknown |
| 7 | Killer whales | 0.000262 | 0.02 | 7.763 | 0 | 0 | 0.00258 | 0 | unknown |
| 8 | Baleen whales | 0.00276 | 0.04 | 3.398 | 0 | 0 | 0.0118 | 0 | unknown |
| 9 | Beaked whales | 0.000125 | 0.036 | 9.923 | 0 | 0 | 0.00363 | 0 | unknown |
| 10 | Dolphins | 0.0225 | 0.047 | 13.74 | 0.7386 | 0.739 | 0.00342 | 0 | unknown |
| 11 | Seabirds | 0.118 | 0.12 | 118 | 0 | 0 | 0.00102 | 0 | unknown |
| 12 | Large pelagics | 2.54 | 1.908 | 11.7 | 0.5045 | 0.505 | 0.163 | 0.0153 | unknown |
| 13 | Mesopelagic predators | 0.735 | 4.362 | 31.61 | 0.117 | 0.117 | 0.138 | 0 | unknown |
| 14 | Bathydeersal predators | 0.2928 | 2.71 | 9.033 | 0.95 | 0.94 | 0.3 | 0 | unknown |
| 15 | Sharks | 0.29 | 1.338 | 7.497 | 0.0116 | 0.00387 | 0.178 | 0.0015 | unknown |
| 16 | Rays | 0.112 | 1 | 6 | 0.0318 | 0.0161 | 0.167 | 0.0018 | unknown |
| 17 | Coastal tunas | 2.89 | 0.82 | 3.774 | 0.0026 | 0.00127 | 0.217 | 0.003 | unknown |
| 18 | Coastal demersal | 4.696 | 13.94 | 46.47 | 0.0492 | 0.0485 | 0.3 | 0 | unknown |
| 19 | Clupeids | 22.13 | 3.1 | 16.35 | 0.5217 | 0.523 | 0.19 | 0.3354 | unknown |
| 20 | Other coastal pelagics | 13.12 | 2.612 | 10.63 | 0.4112 | 0.411 | 0.246 | 0.1411 | unknown |
| 21 | Cephalopods | 2.409 | 4.7 | 16.73 | 0.7445 | 0.747 | 0.281 | 0.0545 | unknown |
| 22 | Crustaceans | 13.05 | 6.443 | 31.96 | 0.014 | 0.014 | 0.202 | 0.0076 | unknown |
| 23 | Benthos | 112.6 | 4.334 | 32.73 | 0.7222 | 0.722 | 0.132 | 0 | unknown |
| 24 | Benthic producers | 10.5 | 107.4 | - | 0.3266 | 0.327 | - | 0 | unknown |
| 25 | Zooplankton | 20.64 | 58.36 | 274.8 | 0.4266 | 0.427 | 0.212 | 0 | unknown |
| 26 | Phytoplankton | 82.01 | 138.2 | - | 0.5151 | 0.0148 | - | 0 | unknown |
| 27 | Detritus | 10 | - | - | 0.3695 | - | - | 0 | unknown |
