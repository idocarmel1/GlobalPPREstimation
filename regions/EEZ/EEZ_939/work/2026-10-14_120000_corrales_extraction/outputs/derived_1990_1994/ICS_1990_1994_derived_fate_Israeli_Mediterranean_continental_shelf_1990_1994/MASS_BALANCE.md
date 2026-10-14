## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for EEZ_939_Israel_Mediterranean_ICS_1990_1994_derived_fate_Israeli_Mediterranean_continental_shelf_(1990–1994), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 1 error(s), 113 indeterminate, 1 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 39 of 39 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.921, group 34 (Large pelagic fishes).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 37 (Dolphins, 0.008).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 28: known source diet plus import subtotal 1.03 exceeds one; no normalization applied

### Indeterminate (BA unknown)

- group 9 (Alien shrimps): printed EE 0.95 vs recomputed 0.785 (diff 0.165) with BA unknown - a BA of +0.03571 t/km^2/year (+0.16 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 10 (Native crabs): printed EE 0.95 vs recomputed 0.889 (diff 0.061) with BA unknown - a BA of +0.008585 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 11 (Alien crabs): printed EE 0.95 vs recomputed 0.544 (diff 0.406) with BA unknown - a BA of +0.02275 t/km^2/year (+0.41 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 13 (Benthic cephalopods): printed EE 0.95 vs recomputed 0.757 (diff 0.193) with BA unknown - a BA of +0.0147 t/km^2/year (+0.19 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 14 (Benthopelagic cephalopods): printed EE 0.95 vs recomputed 0.888 (diff 0.062) with BA unknown - a BA of +0.009291 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 15 (Mullets): printed EE 0.96 vs recomputed 0.896 (diff 0.064) with BA unknown - a BA of +0.005962 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 16 (Goatfishes): printed EE 0.99 vs recomputed 0.593 (diff 0.397) with BA unknown - a BA of +0.02237 t/km^2/year (+0.40 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 17 (Hake): printed EE 0.99 vs recomputed 0.453 (diff 0.537) with BA unknown - a BA of +0.0239 t/km^2/year (+0.54 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 18 (Flatfishes): printed EE 0.98 vs recomputed 0.486 (diff 0.494) with BA unknown - a BA of +0.01503 t/km^2/year (+0.49 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 19 (Rocky fishes): printed EE 0.95 vs recomputed 0.800 (diff 0.150) with BA unknown - a BA of +0.0156 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 22 (Alien herbivores): printed EE 0.95 vs recomputed 0.389 (diff 0.561) with BA unknown - a BA of +0.009652 t/km^2/year (+0.56 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Earlier alien dem. fishes): printed EE 0.99 vs recomputed 0.531 (diff 0.459) with BA unknown - a BA of +0.02175 t/km^2/year (+0.46 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 24 (Alien lizardfish): printed EE 0.93 vs recomputed 0.877 (diff 0.053) with BA unknown - a BA of +0.004369 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 25 (Demersal fishes (upper slope)): printed EE 0.96 vs recomputed 0.806 (diff 0.154) with BA unknown - a BA of +0.001554 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 27 (Mesopelagic fishes): printed EE 0.95 vs recomputed 0.867 (diff 0.083) with BA unknown - a BA of +0.00869 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 28 (Demersal sharks): printed EE 0.64 vs recomputed 0.714 (diff 0.074) with BA unknown - a BA of -0.00104 t/km^2/year (-0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 29 (Rays and skates): printed EE 0.87 vs recomputed 0.817 (diff 0.053) with BA unknown - a BA of +0.001482 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 32 (Mackerel): printed EE 0.95 vs recomputed 0.813 (diff 0.137) with BA unknown - a BA of +0.01361 t/km^2/year (+0.14 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 33 (Native medium pelagic fishes): printed EE 0.90 vs recomputed 0.465 (diff 0.435) with BA unknown - a BA of +0.03697 t/km^2/year (+0.43 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 34 (Large pelagic fishes): printed EE 0.98 vs recomputed 0.059 (diff 0.921) with BA unknown - a BA of +0.04971 t/km^2/year (+0.92 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 35 (Turtles): printed EE 0.50 vs recomputed 0.000 (diff 0.500) with BA unknown - a BA of +0.0051 t/km^2/year (+0.50 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 37 (Dolphins): printed EE 0.48 vs recomputed 0.000 (diff 0.480) with BA unknown - a BA of +0.000432 t/km^2/year (+0.48 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 1: discard removals unknown; reported catch does not establish complete removals
- group 2: discard removals unknown; reported catch does not establish complete removals
- group 3: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 3: unassimilated fraction unknown; indicative checks use a software assumption
- group 3: discard removals unknown; reported catch does not establish complete removals
- group 4: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 4: unassimilated fraction unknown; indicative checks use a software assumption
- group 4: discard removals unknown; reported catch does not establish complete removals
- group 5: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 5: unassimilated fraction unknown; indicative checks use a software assumption
- group 5: discard removals unknown; reported catch does not establish complete removals
- group 6: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 6: unassimilated fraction unknown; indicative checks use a software assumption
- group 6: discard removals unknown; reported catch does not establish complete removals
- group 7: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 7: unassimilated fraction unknown; indicative checks use a software assumption
- group 7: discard removals unknown; reported catch does not establish complete removals
- group 8: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 8: unassimilated fraction unknown; indicative checks use a software assumption
- group 9: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 9: unassimilated fraction unknown; indicative checks use a software assumption
- group 9: discard removals unknown; reported catch does not establish complete removals
- group 10: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 10: unassimilated fraction unknown; indicative checks use a software assumption
- group 10: discard removals unknown; reported catch does not establish complete removals
- group 11: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 11: unassimilated fraction unknown; indicative checks use a software assumption
- group 12: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 12: unassimilated fraction unknown; indicative checks use a software assumption
- group 12: discard removals unknown; reported catch does not establish complete removals
- group 13: diet/import has unknown cells; known subtotal 0.99 is not a complete composition
- group 13: unassimilated fraction unknown; indicative checks use a software assumption
- group 13: discard removals unknown; reported catch does not establish complete removals
- group 14: diet/import has unknown cells; known subtotal 0.99 is not a complete composition
- group 14: unassimilated fraction unknown; indicative checks use a software assumption
- group 14: discard removals unknown; reported catch does not establish complete removals
- group 15: diet/import has unknown cells; known subtotal 1.01 is not a complete composition
- group 15: unassimilated fraction unknown; indicative checks use a software assumption
- group 16: diet/import has unknown cells; known subtotal 1.01 is not a complete composition
- group 16: unassimilated fraction unknown; indicative checks use a software assumption
- group 17: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 17: unassimilated fraction unknown; indicative checks use a software assumption
- group 17: discard removals unknown; reported catch does not establish complete removals
- group 18: diet/import has unknown cells; known subtotal 1.01 is not a complete composition
- group 18: unassimilated fraction unknown; indicative checks use a software assumption
- group 19: diet/import has unknown cells; known subtotal 0.98 is not a complete composition
- group 19: unassimilated fraction unknown; indicative checks use a software assumption
- group 19: discard removals unknown; reported catch does not establish complete removals
- group 20: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 20: unassimilated fraction unknown; indicative checks use a software assumption
- group 21: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 21: unassimilated fraction unknown; indicative checks use a software assumption
- group 22: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 22: unassimilated fraction unknown; indicative checks use a software assumption
- group 22: discard removals unknown; reported catch does not establish complete removals
- group 23: diet/import has unknown cells; known subtotal 0.98 is not a complete composition
- group 23: unassimilated fraction unknown; indicative checks use a software assumption
- group 24: diet/import has unknown cells; known subtotal 0.99 is not a complete composition
- group 24: unassimilated fraction unknown; indicative checks use a software assumption
- group 25: diet/import has unknown cells; known subtotal 1.01 is not a complete composition
- group 25: unassimilated fraction unknown; indicative checks use a software assumption
- group 26: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 26: unassimilated fraction unknown; indicative checks use a software assumption
- group 27: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 27: unassimilated fraction unknown; indicative checks use a software assumption
- group 27: discard removals unknown; reported catch does not establish complete removals
- group 28: diet/import has unknown cells; known subtotal 1.03 is not a complete composition
- group 28: unassimilated fraction unknown; indicative checks use a software assumption
- group 29: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 29: unassimilated fraction unknown; indicative checks use a software assumption
- group 30: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 30: unassimilated fraction unknown; indicative checks use a software assumption
- group 31: diet/import has unknown cells; known subtotal 0.99 is not a complete composition
- group 31: unassimilated fraction unknown; indicative checks use a software assumption
- group 32: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 32: unassimilated fraction unknown; indicative checks use a software assumption
- group 32: discard removals unknown; reported catch does not establish complete removals
- group 33: diet/import has unknown cells; known subtotal 0.98 is not a complete composition
- group 33: unassimilated fraction unknown; indicative checks use a software assumption
- group 33: discard removals unknown; reported catch does not establish complete removals
- group 34: diet/import has unknown cells; known subtotal 0.98 is not a complete composition
- group 34: unassimilated fraction unknown; indicative checks use a software assumption
- group 34: discard removals unknown; reported catch does not establish complete removals
- group 35: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 35: unassimilated fraction unknown; indicative checks use a software assumption
- group 36: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 36: unassimilated fraction unknown; indicative checks use a software assumption
- group 37: diet/import has unknown cells; known subtotal 1.01 is not a complete composition
- group 37: unassimilated fraction unknown; indicative checks use a software assumption
- group 38: discard removals unknown; reported catch does not establish complete removals
- group 39: discard removals unknown; reported catch does not establish complete removals

### Warnings

- group 37 (Dolphins): P/Q = 0.008 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 35 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Micro and mesozooplankton), 4 (Macrozooplankton), 5 (Gelatinous plankton), 6 (Polychaetes), 7 (Suprabenthos), 8 (Native shrimps), 9 (Alien shrimps), 10 (Native crabs) ...
- detritus pools (2): inflow ~222.6, consumption ~56.82 t/km^2/year, implied EE ~0.255 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 2.78 | 88.42 | - | 0.24 | 0.24 | - | 0 | unknown |
| 2 | Benthic primary producers | 0.08 | 5.5 | - | 0.5 | 0.515 | - | 0 | unknown |
| 3 | Micro and mesozooplankton | 1.15 | 22.82 | 69.15 | 0.95 | 0.954 | 0.33 | 0 | unknown |
| 4 | Macrozooplankton | 0.16 | 17.15 | 57.17 | 0.95 | 0.966 | 0.3 | 0 | unknown |
| 5 | Gelatinous plankton | 0.07 | 15.56 | 56.65 | 0.3 | 0.295 | 0.275 | 0 | unknown |
| 6 | Polychaetes | 0.7 | 5.28 | 22.8 | 0.8 | 0.798 | 0.232 | 0 | unknown |
| 7 | Suprabenthos | 0.21 | 11.84 | 57.12 | 0.8 | 0.812 | 0.207 | 0 | unknown |
| 8 | Native shrimps | 0.12 | 3.1 | 9.76 | 0.95 | 0.97 | 0.318 | 0.05 | unknown |
| 9 | Alien shrimps | 0.07 | 3.1 | 10.12 | 0.95 | 0.785 | 0.306 | 0 | unknown |
| 10 | Native crabs | 0.05 | 2.8 | 9.25 | 0.95 | 0.889 | 0.303 | 0 | unknown |
| 11 | Alien crabs | 0.02 | 2.8 | 9.55 | 0.95 | 0.544 | 0.293 | 0 | unknown |
| 12 | Benthic invertebrates | 1.13 | 3.27 | 10.9 | 0.8 | 0.801 | 0.3 | 0 | unknown |
| 13 | Benthic cephalopods | 0.04 | 1.9 | 6.8 | 0.95 | 0.757 | 0.279 | 0 | unknown |
| 14 | Benthopelagic cephalopods | 0.06 | 2.5 | 26.47 | 0.95 | 0.888 | 0.0944 | 0 | unknown |
| 15 | Mullets | 0.05 | 1.86 | 8.32 | 0.96 | 0.896 | 0.224 | 0.05 | unknown |
| 16 | Goatfishes | 0.03 | 1.88 | 8.54 | 0.99 | 0.593 | 0.22 | 0.02 | unknown |
| 17 | Hake | 0.05 | 0.89 | 5.8 | 0.99 | 0.453 | 0.153 | 0 | unknown |
| 18 | Flatfishes | 0.02 | 1.52 | 8.23 | 0.98 | 0.486 | 0.185 | 0.01 | unknown |
| 19 | Rocky fishes | 0.06 | 1.73 | 7.18 | 0.95 | 0.8 | 0.241 | 0 | unknown |
| 20 | Small native dem. fishes | 0.24 | 1.49 | 6.62 | 0.98 | 0.968 | 0.225 | 0.15 | unknown |
| 21 | Large native dem. fishes | 0.11 | 1.1 | 6.08 | 0.97 | 0.932 | 0.181 | 0.08 | unknown |
| 22 | Alien herbivores | 0.01 | 1.72 | 6.9 | 0.95 | 0.389 | 0.249 | 0 | unknown |
| 23 | Earlier alien dem. fishes | 0.03 | 1.58 | 6.79 | 0.99 | 0.531 | 0.233 | 0.01 | unknown |
| 24 | Alien lizardfish | 0.07 | 1.18 | 7.01 | 0.93 | 0.877 | 0.168 | 0.05 | unknown |
| 25 | Demersal fishes (upper slope) | 0.01 | 1.01 | 5.92 | 0.96 | 0.806 | 0.171 | 0 | unknown |
| 26 | Benthopelagic fishes | 0.15 | 2.03 | 10.14 | 0.95 | 0.97 | 0.2 | 0.05 | unknown |
| 27 | Mesopelagic fishes | 0.06 | 1.74 | 8.7 | 0.95 | 0.867 | 0.2 | 0 | unknown |
| 28 | Demersal sharks | 0.02 | 0.7 | 4.67 | 0.64 | 0.714 | 0.15 | 0.01 | unknown |
| 29 | Rays and skates | 0.03 | 0.94 | 5.7 | 0.87 | 0.817 | 0.165 | 0.02 | unknown |
| 30 | Small pelagic fishes | 0.7 | 2.4 | 11.98 | 0.95 | 0.921 | 0.2 | 0.12 | unknown |
| 31 | Horse mackerel | 0.13 | 1.44 | 8.02 | 0.95 | 0.965 | 0.18 | 0.06 | unknown |
| 32 | Mackerel | 0.07 | 1.42 | 7.88 | 0.95 | 0.813 | 0.18 | 0 | unknown |
| 33 | Native medium pelagic fishes | 0.1 | 0.85 | 7.07 | 0.9 | 0.465 | 0.12 | 0 | unknown |
| 34 | Large pelagic fishes | 0.06 | 0.9 | 5.35 | 0.98 | 0.0594 | 0.168 | 0 | unknown |
| 35 | Turtles | 0.06 | 0.17 | 2.78 | 0.5 | 0 | 0.0612 | 0 | unknown |
| 36 | Sea birds | 0 | 5.1 | 75.23 | 0.01 | - | 0.0678 | 0 | unknown |
| 37 | Dolphins | 0.01 | 0.09 | 10.95 | 0.48 | 0 | 0.00822 | 0 | unknown |
| 38 | Detritus | 17.81 | - | - | 0.23 | - | - | 0 | unknown |
| 39 | Discards | 0.17 | - | - | 0.97 | - | - | 0 | unknown |
