## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for EEZ_939_Israel_Mediterranean_ICS_2008_2012_Israeli_Mediterranean_continental_shelf_(2008–2012), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 121 indeterminate, 1 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 41 of 41 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.990, group 36 (Large pelagic fishes).

Groups with recomputed EE > 1: 23 (Earlier alien dem. fishes, 1.009).

P/Q outside 0.02-0.5: 39 (Dolphins, 0.008).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 8 (Native shrimps): printed EE 0.95 vs recomputed 0.871 (diff 0.079) with BA unknown - a BA of +0.0196 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 9 (Alien shrimps): printed EE 0.95 vs recomputed 0.868 (diff 0.082) with BA unknown - a BA of +0.02549 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 10 (Native crabs): printed EE 0.95 vs recomputed 0.473 (diff 0.477) with BA unknown - a BA of +0.02679 t/km^2/year (+0.48 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 13 (Benthic cephalopods): printed EE 0.95 vs recomputed 0.795 (diff 0.155) with BA unknown - a BA of +0.01478 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 14 (Benthopelagic cephalopods): printed EE 0.95 vs recomputed 0.751 (diff 0.199) with BA unknown - a BA of +0.03496 t/km^2/year (+0.20 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 15 (Mullets): printed EE 0.98 vs recomputed 0.128 (diff 0.852) with BA unknown - a BA of +0.01594 t/km^2/year (+0.85 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 17 (Hake): printed EE 0.97 vs recomputed 0.255 (diff 0.715) with BA unknown - a BA of +0.00636 t/km^2/year (+0.71 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 18 (Flatfishes): printed EE 0.96 vs recomputed 0.771 (diff 0.189) with BA unknown - a BA of +0.005796 t/km^2/year (+0.19 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 19 (Rocky fishes): printed EE 0.98 vs recomputed 0.691 (diff 0.289) with BA unknown - a BA of +0.02513 t/km^2/year (+0.29 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 21 (Large native dem. fishes): printed EE 0.97 vs recomputed 0.566 (diff 0.404) with BA unknown - a BA of +0.008884 t/km^2/year (+0.40 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 22 (Alien herbivores): printed EE 0.95 vs recomputed 0.096 (diff 0.854) with BA unknown - a BA of +0.02954 t/km^2/year (+0.85 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Earlier alien dem. fishes): recomputed EE = 1.009 > 1 without BA, and BA is unknown - a BA of -0.00623 t/km^2/year (-0.04 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 24 (New alien dem. fishes): printed EE 0.95 vs recomputed 0.874 (diff 0.076) with BA unknown - a BA of +0.01238 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 25 (Alien lizardfish): printed EE 0.93 vs recomputed 0.188 (diff 0.742) with BA unknown - a BA of +0.02628 t/km^2/year (+0.74 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 26 (Demersal fishes (upper slope)): printed EE 0.93 vs recomputed 0.880 (diff 0.050) with BA unknown - a BA of +0.000509 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 27 (Benthopelagic fishes): printed EE 0.95 vs recomputed 0.899 (diff 0.051) with BA unknown - a BA of +0.01379 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 28 (Mesopelagic fishes): printed EE 0.95 vs recomputed 0.880 (diff 0.070) with BA unknown - a BA of +0.006163 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 30 (Rays and skates): printed EE 0.89 vs recomputed 0.743 (diff 0.147) with BA unknown - a BA of +0.006898 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 33 (Mackerel): printed EE 0.95 vs recomputed 0.675 (diff 0.275) with BA unknown - a BA of +0.03173 t/km^2/year (+0.28 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 34 (Native medium pelagic fishes): printed EE 0.90 vs recomputed 0.203 (diff 0.697) with BA unknown - a BA of +0.04199 t/km^2/year (+0.70 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 35 (Alien medium pelagic fishes): printed EE 0.90 vs recomputed 0.588 (diff 0.312) with BA unknown - a BA of +0.0053 t/km^2/year (+0.31 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 36 (Large pelagic fishes): printed EE 0.99 vs recomputed 0.000 (diff 0.990) with BA unknown - a BA of +0.05346 t/km^2/year (+0.99 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 37 (Turtles): printed EE 0.50 vs recomputed 0.000 (diff 0.500) with BA unknown - a BA of +0.0051 t/km^2/year (+0.50 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 39 (Dolphins): printed EE 0.48 vs recomputed 0.000 (diff 0.480) with BA unknown - a BA of +0.000432 t/km^2/year (+0.48 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
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
- group 15: discard removals unknown; reported catch does not establish complete removals
- group 16: diet/import has unknown cells; known subtotal 1.01 is not a complete composition
- group 16: unassimilated fraction unknown; indicative checks use a software assumption
- group 17: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 17: unassimilated fraction unknown; indicative checks use a software assumption
- group 17: discard removals unknown; reported catch does not establish complete removals
- group 18: diet/import has unknown cells; known subtotal 0.98 is not a complete composition
- group 18: unassimilated fraction unknown; indicative checks use a software assumption
- group 19: diet/import has unknown cells; known subtotal 0.99 is not a complete composition
- group 19: unassimilated fraction unknown; indicative checks use a software assumption
- group 19: discard removals unknown; reported catch does not establish complete removals
- group 20: diet/import has unknown cells; known subtotal 0.97 is not a complete composition
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
- group 25: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 25: unassimilated fraction unknown; indicative checks use a software assumption
- group 25: discard removals unknown; reported catch does not establish complete removals
- group 26: diet/import has unknown cells; known subtotal 1.01 is not a complete composition
- group 26: unassimilated fraction unknown; indicative checks use a software assumption
- group 27: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 27: unassimilated fraction unknown; indicative checks use a software assumption
- group 28: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 28: unassimilated fraction unknown; indicative checks use a software assumption
- group 28: discard removals unknown; reported catch does not establish complete removals
- group 29: diet/import has unknown cells; known subtotal 0.99 is not a complete composition
- group 29: unassimilated fraction unknown; indicative checks use a software assumption
- group 30: diet/import has unknown cells; known subtotal 0.99 is not a complete composition
- group 30: unassimilated fraction unknown; indicative checks use a software assumption
- group 31: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 31: unassimilated fraction unknown; indicative checks use a software assumption
- group 32: diet/import has unknown cells; known subtotal 0.98 is not a complete composition
- group 32: unassimilated fraction unknown; indicative checks use a software assumption
- group 33: diet/import has unknown cells; known subtotal 1.01 is not a complete composition
- group 33: unassimilated fraction unknown; indicative checks use a software assumption
- group 33: discard removals unknown; reported catch does not establish complete removals
- group 34: diet/import has unknown cells; known subtotal 0.97 is not a complete composition
- group 34: unassimilated fraction unknown; indicative checks use a software assumption
- group 34: discard removals unknown; reported catch does not establish complete removals
- group 35: diet/import has unknown cells; known subtotal 0.98 is not a complete composition
- group 35: unassimilated fraction unknown; indicative checks use a software assumption
- group 36: diet/import has unknown cells; known subtotal 0.98 is not a complete composition
- group 36: unassimilated fraction unknown; indicative checks use a software assumption
- group 36: discard removals unknown; reported catch does not establish complete removals
- group 37: diet/import has unknown cells; known subtotal 1.01 is not a complete composition
- group 37: unassimilated fraction unknown; indicative checks use a software assumption
- group 38: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 38: unassimilated fraction unknown; indicative checks use a software assumption
- group 39: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 39: unassimilated fraction unknown; indicative checks use a software assumption
- group 40: discard removals unknown; reported catch does not establish complete removals
- group 41: discard removals unknown; reported catch does not establish complete removals

### Warnings

- group 39 (Dolphins): P/Q = 0.008 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 37 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Micro and mesozooplankton), 4 (Macrozooplankton), 5 (Gelatinous plankton), 6 (Polychaetes), 7 (Suprabenthos), 8 (Native shrimps), 9 (Alien shrimps), 10 (Native crabs) ...
- detritus pools (2): inflow ~219.5, consumption ~57.62 t/km^2/year, implied EE ~0.262 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 3.04 | 78.9 | - | 0.23 | 0.229 | - | 0 | unknown |
| 2 | Benthic primary producers | 0.07 | 5.5 | - | 0.7 | 0.698 | - | 0 | unknown |
| 3 | Micro and mesozooplankton | 1.05 | 23.19 | 70.27 | 0.95 | 0.943 | 0.33 | 0 | unknown |
| 4 | Macrozooplankton | 0.15 | 17.43 | 58.09 | 0.95 | 0.974 | 0.3 | 0 | unknown |
| 5 | Gelatinous plankton | 0.06 | 15.82 | 57.57 | 0.3 | 0.325 | 0.275 | 0 | unknown |
| 6 | Polychaetes | 0.72 | 5.37 | 23.17 | 0.8 | 0.799 | 0.232 | 0 | unknown |
| 7 | Suprabenthos | 0.23 | 11.88 | 57.31 | 0.8 | 0.783 | 0.207 | 0 | unknown |
| 8 | Native shrimps | 0.08 | 3.11 | 9.8 | 0.95 | 0.871 | 0.317 | 0.03 | unknown |
| 9 | Alien shrimps | 0.1 | 3.11 | 10.16 | 0.95 | 0.868 | 0.306 | 0 | unknown |
| 10 | Native crabs | 0.02 | 2.81 | 9.29 | 0.95 | 0.473 | 0.302 | 0 | unknown |
| 11 | Alien crabs | 0.09 | 2.81 | 9.59 | 0.95 | 0.947 | 0.293 | 0.07 | unknown |
| 12 | Benthic invertebrates | 1.21 | 3.28 | 10.94 | 0.8 | 0.799 | 0.3 | 0 | unknown |
| 13 | Benthic cephalopods | 0.05 | 1.91 | 6.82 | 0.95 | 0.795 | 0.28 | 0 | unknown |
| 14 | Benthopelagic cephalopods | 0.07 | 2.51 | 26.56 | 0.95 | 0.751 | 0.0945 | 0 | unknown |
| 15 | Mullets | 0.01 | 1.87 | 8.37 | 0.98 | 0.128 | 0.223 | 0 | unknown |
| 16 | Goatfishes | 0.03 | 1.89 | 8.6 | 0.99 | 0.959 | 0.22 | 0.04 | unknown |
| 17 | Hake | 0.01 | 0.89 | 5.84 | 0.97 | 0.255 | 0.152 | 0 | unknown |
| 18 | Flatfishes | 0.02 | 1.53 | 8.26 | 0.96 | 0.771 | 0.185 | 0.01 | unknown |
| 19 | Rocky fishes | 0.05 | 1.74 | 7.2 | 0.98 | 0.691 | 0.242 | 0 | unknown |
| 20 | Small native dem. fishes | 0.21 | 1.5 | 6.67 | 0.96 | 0.939 | 0.225 | 0.17 | unknown |
| 21 | Large native dem. fishes | 0.02 | 1.1 | 6.1 | 0.97 | 0.566 | 0.18 | 0.01 | unknown |
| 22 | Alien herbivores | 0.02 | 1.73 | 6.92 | 0.95 | 0.0963 | 0.25 | 0 | unknown |
| 23 | Earlier alien dem. fishes | 0.1 | 1.59 | 6.81 | 0.97 | 1.01 | 0.233 | 0.07 | unknown |
| 24 | New alien dem. fishes | 0.11 | 1.49 | 6.67 | 0.95 | 0.874 | 0.223 | 0.07 | unknown |
| 25 | Alien lizardfish | 0.03 | 1.18 | 7.04 | 0.93 | 0.188 | 0.168 | 0 | unknown |
| 26 | Demersal fishes (upper slope) | 0.01 | 1.01 | 5.94 | 0.93 | 0.88 | 0.17 | 0 | unknown |
| 27 | Benthopelagic fishes | 0.13 | 2.06 | 10.28 | 0.95 | 0.899 | 0.2 | 0.05 | unknown |
| 28 | Mesopelagic fishes | 0.05 | 1.75 | 8.73 | 0.95 | 0.88 | 0.2 | 0 | unknown |
| 29 | Demersal sharks | 0.04 | 0.7 | 4.68 | 0.7 | 0.736 | 0.15 | 0.02 | unknown |
| 30 | Rays and skates | 0.05 | 0.94 | 5.72 | 0.89 | 0.743 | 0.164 | 0.03 | unknown |
| 31 | Small pelagic fishes | 0.58 | 2.45 | 12.27 | 0.95 | 0.944 | 0.2 | 0.05 | unknown |
| 32 | Horse mackerel | 0.09 | 1.46 | 8.13 | 0.95 | 0.969 | 0.18 | 0.05 | unknown |
| 33 | Mackerel | 0.08 | 1.44 | 7.99 | 0.95 | 0.675 | 0.18 | 0 | unknown |
| 34 | Native medium pelagic fishes | 0.07 | 0.86 | 7.09 | 0.9 | 0.203 | 0.121 | 0 | unknown |
| 35 | Alien medium pelagic fishes | 0.02 | 0.85 | 7.11 | 0.9 | 0.588 | 0.12 | 0.01 | unknown |
| 36 | Large pelagic fishes | 0.06 | 0.9 | 5.38 | 0.99 | 0 | 0.167 | 0 | unknown |
| 37 | Turtles | 0.06 | 0.17 | 2.83 | 0.5 | 0 | 0.0601 | 0 | unknown |
| 38 | Sea birds | 0 | 5.1 | 75.23 | 0.01 | - | 0.0678 | 0 | unknown |
| 39 | Dolphins | 0.01 | 0.09 | 10.95 | 0.48 | 0 | 0.00822 | 0 | unknown |
| 40 | Detritus | 17.95 | - | - | 0.24 | - | - | 0 | unknown |
| 41 | Discards | 0.29 | - | - | 0.49 | - | - | 0 | unknown |
