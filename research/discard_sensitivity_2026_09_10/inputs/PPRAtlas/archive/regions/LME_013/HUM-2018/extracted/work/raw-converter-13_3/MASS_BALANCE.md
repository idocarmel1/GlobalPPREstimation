## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 13_Humboldt_Current_13_3_Northern_Humboldt_Current_(1995-1998), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 2 indeterminate, 2 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 24 of 24 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 3850.419, group 6 (Small jellyfish).

Groups with recomputed EE > 1: 6 (Small jellyfish, 3851.369).

P/Q outside 0.02-0.5: 18 (Seabirds, 0.001), 19 (Marine mammals, 0.004).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 6 (Small jellyfish): recomputed EE = 3851.369 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 17 (Apex predatory fish): printed EE 0.56 vs recomputed 0.408 (diff 0.152) with BA unknown - a BA of +0.00372 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 18 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 19 (Marine mammals): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 18 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Microzooplankton), 4 (Mesozooplakton), 5 (Macrozooplankton), 6 (Small jellyfish), 7 (Large jellyfish), 8 (Macrobenthos), 9 (Forage fish), 10 (Mesopelagics) ...
- detritus pools (4): inflow ~6924, consumption ~6161 t/km^2/year, implied EE ~0.890 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Large phytoplankton | 34.09 | 237.5 | - | 0.82 | 0.822 | - | 0 | unknown |
| 2 | Small phytoplankton | 13.38 | 237.5 | - | 0.97 | 0.967 | - | 0 | unknown |
| 3 | Microzooplankton | 13.54 | 256 | 1024 | 0.96 | 0.957 | 0.25 | 0 | unknown |
| 4 | Mesozooplakton | 24.08 | 40 | 125 | 0.92 | 0.934 | 0.32 | 0 | unknown |
| 5 | Macrozooplankton | 37.42 | 19.09 | 46.55 | 0.95 | 0.901 | 0.41 | 0 | unknown |
| 6 | Small jellyfish | 0.01 | 0.58 | 2.92 | 0.95 | 3.85e+03 | 0.199 | 0 | unknown |
| 7 | Large jellyfish | 8.46 | 15 | 56 | 0 | 5.38e-05 | 0.268 | 0 | unknown |
| 8 | Macrobenthos | 23.17 | 1.2 | 10 | 0.79 | 0.788 | 0.12 | 0 | unknown |
| 9 | Forage fish | 69.05 | 1.91 | 14.51 | 0.82 | 0.816 | 0.132 | 29 | unknown |
| 10 | Mesopelagics | 14.63 | 1.4 | 14 | 0.26 | 0.262 | 0.1 | 0 | unknown |
| 11 | Cephalopods | 2.19 | 5.11 | 12.59 | 0.89 | 0.885 | 0.406 | 0.14 | unknown |
| 12 | Pelagic planktivorous fish | 11.01 | 1 | 9.98 | 0.89 | 0.886 | 0.1 | 1.69 | unknown |
| 13 | Pelagic piscivorous fish | 16.16 | 0.99 | 9.46 | 0.21 | 0.215 | 0.105 | 2.83 | unknown |
| 14 | Demersal piscivorous fish | 2.37 | 1.2 | 7.97 | 0.62 | 0.617 | 0.151 | 1.27 | unknown |
| 15 | Demersal planktivorous fish | 5.78 | 2.4 | 15.3 | 0.68 | 0.681 | 0.157 | 0.02 | unknown |
| 16 | Demersal benthivorous fish | 1.17 | 1.08 | 7.23 | 0.79 | 0.791 | 0.149 | 0.59 | unknown |
| 17 | Apex predatory fish | 0.05 | 0.49 | 3.24 | 0.56 | 0.408 | 0.151 | 0.01 | unknown |
| 18 | Seabirds | 0.04 | 0.04 | 61 | 0 | 0 | 0.000656 | 0 | unknown |
| 19 | Marine mammals | 0.13 | 0.1 | 25.83 | 0 | 0 | 0.00387 | 0 | unknown |
| 20 | Sea turtles | 0 | 0.19 | 3.5 | 0 | - | 0.0543 | 0 | unknown |
| 21 | Fish eggs | 0.44 | - | - | 0.87 | - | - | 0 | unknown |
| 22 | Detritus offal | 0.05 | - | - | 0 | - | - | 0 | unknown |
| 23 | Pelagic detritus | 20 | - | - | 0 | - | - | 0 | unknown |
| 24 | Benthic detritus | 60 | - | - | 0.89 | - | - | 0 | unknown |
