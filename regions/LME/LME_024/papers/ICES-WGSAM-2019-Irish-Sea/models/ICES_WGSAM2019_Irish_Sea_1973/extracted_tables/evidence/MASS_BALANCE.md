## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 24_Celtic-Biscay_Shelf_ICES-WGSAM2019_Irish_Sea_(1973), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 82 indeterminate, 5 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 41 of 41 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.139, group 18 (Monkfish).

Groups with recomputed EE > 1: 21 (Gurnards, 1.010).

P/Q outside 0.02-0.5: 1 (Toothed whales, 0.001), 2 (Minke whales, 0.003), 3 (Seals, 0.004), 4 (Seabirds (high discard diet), 0.006), 5 (Seabirds (low discard diet), 0.006).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 1 (Toothed whales): printed EE 0.64 vs recomputed 0.700 (diff 0.060) with BA unknown - a BA of -6e-06 t/km^2/year (-0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 6 (Sharks): printed EE 0.34 vs recomputed 0.288 (diff 0.052) with BA unknown - a BA of +0.006076 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 9 (Atlantic cod 0-1): printed EE 0.94 vs recomputed 0.830 (diff 0.110) with BA unknown - a BA of +0.007777 t/km^2/year (+0.11 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 12 (Haddock 2+): printed EE 0.99 vs recomputed 0.933 (diff 0.057) with BA unknown - a BA of +0.004594 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 18 (Monkfish): printed EE 0.69 vs recomputed 0.829 (diff 0.139) with BA unknown - a BA of -0.002041 t/km^2/year (-0.14 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 21 (Gurnards): recomputed EE = 1.010 > 1 without BA, and BA is unknown - a BA of -0.004952 t/km^2/year (-0.01 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 1: diet/import has unknown cells; known subtotal 1.0003 is not a complete composition
- group 1: unassimilated fraction unknown; indicative checks use a software assumption
- group 2: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 2: unassimilated fraction unknown; indicative checks use a software assumption
- group 3: diet/import has unknown cells; known subtotal 1.001 is not a complete composition
- group 3: unassimilated fraction unknown; indicative checks use a software assumption
- group 4: diet/import has unknown cells; known subtotal 1.001 is not a complete composition
- group 4: unassimilated fraction unknown; indicative checks use a software assumption
- group 5: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 5: unassimilated fraction unknown; indicative checks use a software assumption
- group 6: diet/import has unknown cells; known subtotal 1.0008 is not a complete composition
- group 6: unassimilated fraction unknown; indicative checks use a software assumption
- group 7: diet/import has unknown cells; known subtotal 1.001 is not a complete composition
- group 7: unassimilated fraction unknown; indicative checks use a software assumption
- group 8: diet/import has unknown cells; known subtotal 1.00014 is not a complete composition
- group 8: unassimilated fraction unknown; indicative checks use a software assumption
- group 9: diet/import has unknown cells; known subtotal 1.0003 is not a complete composition
- group 9: unassimilated fraction unknown; indicative checks use a software assumption
- group 10: diet/import has unknown cells; known subtotal 1.0001 is not a complete composition
- group 10: unassimilated fraction unknown; indicative checks use a software assumption
- group 11: diet/import has unknown cells; known subtotal 1.0014 is not a complete composition
- group 11: unassimilated fraction unknown; indicative checks use a software assumption
- group 12: diet/import has unknown cells; known subtotal 0.9995 is not a complete composition
- group 12: unassimilated fraction unknown; indicative checks use a software assumption
- group 13: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 13: unassimilated fraction unknown; indicative checks use a software assumption
- group 14: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 14: unassimilated fraction unknown; indicative checks use a software assumption
- group 15: diet/import has unknown cells; known subtotal 1.001 is not a complete composition
- group 15: unassimilated fraction unknown; indicative checks use a software assumption
- group 16: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 16: unassimilated fraction unknown; indicative checks use a software assumption
- group 17: diet/import has unknown cells; known subtotal 1.0001 is not a complete composition
- group 17: unassimilated fraction unknown; indicative checks use a software assumption
- group 18: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 18: unassimilated fraction unknown; indicative checks use a software assumption
- group 19: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 19: unassimilated fraction unknown; indicative checks use a software assumption
- group 20: diet/import has unknown cells; known subtotal 1.001 is not a complete composition
- group 20: unassimilated fraction unknown; indicative checks use a software assumption
- group 21: diet/import has unknown cells; known subtotal 0.999 is not a complete composition
- group 21: unassimilated fraction unknown; indicative checks use a software assumption
- group 22: diet/import has unknown cells; known subtotal 1.0013 is not a complete composition
- group 22: unassimilated fraction unknown; indicative checks use a software assumption
- group 23: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 23: unassimilated fraction unknown; indicative checks use a software assumption
- group 24: diet/import has unknown cells; known subtotal 0.9994 is not a complete composition
- group 24: unassimilated fraction unknown; indicative checks use a software assumption
- group 25: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 25: unassimilated fraction unknown; indicative checks use a software assumption
- group 26: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 26: unassimilated fraction unknown; indicative checks use a software assumption
- group 27: diet/import has unknown cells; known subtotal 1.001 is not a complete composition
- group 27: unassimilated fraction unknown; indicative checks use a software assumption
- group 28: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 28: unassimilated fraction unknown; indicative checks use a software assumption
- group 29: diet/import has unknown cells; known subtotal 1.001 is not a complete composition
- group 29: unassimilated fraction unknown; indicative checks use a software assumption
- group 30: diet/import has unknown cells; known subtotal 1.0004 is not a complete composition
- group 30: unassimilated fraction unknown; indicative checks use a software assumption
- group 31: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 31: unassimilated fraction unknown; indicative checks use a software assumption
- group 32: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 32: unassimilated fraction unknown; indicative checks use a software assumption
- group 33: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 33: unassimilated fraction unknown; indicative checks use a software assumption
- group 34: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 34: unassimilated fraction unknown; indicative checks use a software assumption
- group 35: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 35: unassimilated fraction unknown; indicative checks use a software assumption
- group 36: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 36: unassimilated fraction unknown; indicative checks use a software assumption
- group 37: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 37: unassimilated fraction unknown; indicative checks use a software assumption
- group 40: discard removals unknown; reported catch does not establish complete removals
- group 41: discard removals unknown; reported catch does not establish complete removals

### Warnings

- group 1 (Toothed whales): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Minke whales): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Seals): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Seabirds (high discard diet)): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 5 (Seabirds (low discard diet)): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 37 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Toothed whales), 2 (Minke whales), 3 (Seals), 4 (Seabirds (high discard diet)), 5 (Seabirds (low discard diet)), 6 (Sharks), 7 (Rays), 8 (Atlantic cod 2+) ...
- detritus pools (2): inflow ~2605, consumption ~303.9 t/km^2/year, implied EE ~0.117 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Toothed whales | 0.005 | 0.02 | 15.52 | 0.64 | 0.7 | 0.00129 | 7e-05 | unknown |
| 2 | Minke whales | 0.07 | 0.02 | 6.58 | 0.14 | 0.143 | 0.00304 | 0.0002 | unknown |
| 3 | Seals | 0.002 | 0.06 | 14.43 | 0.12 | 0.167 | 0.00416 | 2e-05 | unknown |
| 4 | Seabirds (high discard diet) | 0.002 | 0.4 | 66.02 | 0 | 0 | 0.00606 | 0 | unknown |
| 5 | Seabirds (low discard diet) | 0.002 | 0.4 | 69.21 | 0 | 0 | 0.00578 | 0 | unknown |
| 6 | Sharks | 0.29 | 0.4 | 4.01 | 0.34 | 0.288 | 0.0998 | 0.03 | unknown |
| 7 | Rays | 0.25 | 0.85 | 3.28 | 0.5 | 0.487 | 0.259 | 0.07 | unknown |
| 8 | Atlantic cod 2+ | 0.34 | 0.82 | 3.12 | 0.92 | 0.898 | 0.263 | 0.21 | unknown |
| 9 | Atlantic cod 0-1 | 0.07 | 1.01 | 7.64 | 0.94 | 0.83 | 0.132 | 0.021 | unknown |
| 10 | Whiting 2+ | 0.56 | 0.76 | 5.39 | 0.97 | 0.982 | 0.141 | 0.3 | unknown |
| 11 | Whiting 0-1 | 0.24 | 1.52 | 11.88 | 1 | 0.978 | 0.128 | 0.05 | unknown |
| 12 | Haddock 2+ | 0.09 | 0.89 | 4.42 | 0.99 | 0.933 | 0.201 | 0.037 | unknown |
| 13 | Haddock 0-1 | 0.05 | 1.78 | 10.28 | 0.99 | 0.958 | 0.173 | 0.0031 | unknown |
| 14 | European plaice 2+ | 0.16 | 0.79 | 3.75 | 0.99 | 0.946 | 0.211 | 0.09 | unknown |
| 15 | European plaice 0-1 | 0.03 | 1.38 | 10.3 | 0.9 | 0.949 | 0.134 | 0.00074 | unknown |
| 16 | Common sole | 0.11 | 0.81 | 5.61 | 0.96 | 0.993 | 0.144 | 0.0304 | unknown |
| 17 | Flatfish | 0.47 | 1.52 | 6.07 | 0.96 | 0.962 | 0.25 | 0.012 | unknown |
| 18 | Monkfish | 0.03 | 0.49 | 2.75 | 0.69 | 0.829 | 0.178 | 0.012 | unknown |
| 19 | European hake | 0.09 | 0.98 | 3.92 | 0.95 | 0.92 | 0.25 | 0.023 | unknown |
| 20 | Sandeels | 0.35 | 2.05 | 8.21 | 0.95 | 0.984 | 0.25 | 2e-05 | unknown |
| 21 | Gurnards | 0.34 | 1.4 | 5.61 | 1 | 1.01 | 0.25 | 0.002 | unknown |
| 22 | Other demersal fish | 0.36 | 0.96 | 4.32 | 0.95 | 0.955 | 0.222 | 0.054 | unknown |
| 23 | Other benthopelagic fish | 1.57 | 1.85 | 7.38 | 0.95 | 0.949 | 0.251 | 0.0025 | unknown |
| 24 | Atlantic herring | 0.72 | 1.35 | 6.59 | 0.95 | 0.965 | 0.205 | 0.4 | unknown |
| 25 | European sprat | 2.3 | 2.43 | 9.7 | 0.95 | 0.955 | 0.251 | 0.27 | unknown |
| 26 | Other pelagic fish | 4.18 | 1.28 | 5.11 | 0.95 | 0.951 | 0.25 | 0.0209 | unknown |
| 27 | Anadromous fish | 0.03 | 0.64 | 3.17 | 0.34 | 0.373 | 0.202 | 0.002 | unknown |
| 28 | Lobsters and large crabs | 0.51 | 0.62 | 4.13 | 0.95 | 0.96 | 0.15 | 0.0073 | unknown |
| 29 | Nephrops | 0.91 | 1.27 | 8.47 | 0.95 | 0.959 | 0.15 | 0.15 | unknown |
| 30 | Shrimp | 2.32 | 2.67 | 17.8 | 0.95 | 0.949 | 0.15 | 0.007 | unknown |
| 31 | Cephalopods | 0.32 | 1.98 | 15 | 0.95 | 0.949 | 0.132 | 0.0021 | unknown |
| 32 | Scallops | 1.24 | 1.15 | 7.64 | 0.95 | 0.95 | 0.151 | 0.232 | unknown |
| 33 | Epifauna | 25.45 | 1.01 | 4.03 | 0.95 | 0.949 | 0.251 | 0.07 | unknown |
| 34 | Infauna | 25.76 | 1.7 | 6.8 | 0.95 | 0.952 | 0.25 | 1e-05 | unknown |
| 35 | Gelatinous zooplankton | 1.7 | 0.76 | 2.54 | 0.69 | 0.693 | 0.299 | 0 | unknown |
| 36 | Large zooplankton | 6.81 | 10 | 33.33 | 0.68 | 0.681 | 0.3 | 0 | unknown |
| 37 | Small zooplankton | 16.18 | 18 | 60 | 0.52 | 0.521 | 0.3 | 0 | unknown |
| 38 | Seaweed | 29.3 | 1 | - | 0.39 | 0.392 | - | 0 | unknown |
| 39 | Phytoplankton | 13.83 | 226 | - | 0.33 | 0.327 | - | 0 | unknown |
| 40 | Discards | 0.22 | - | - | 0.54 | - | - | 0 | unknown |
| 41 | Detritus | 100 | - | - | 0.12 | - | - | 0 | unknown |
