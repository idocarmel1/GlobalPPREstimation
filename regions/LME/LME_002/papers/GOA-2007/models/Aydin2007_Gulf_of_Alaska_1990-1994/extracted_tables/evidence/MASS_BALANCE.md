## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 2_Gulf_of_Alaska_Aydin2007_Gulf_of_Alaska_(1990-1994), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 14 error(s), 189 indeterminate, 31 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 130 of 133 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.654, group 23 (Puffins).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Transient Killers, 0.002), 2 (Sperm and beaked whale, 0.007), 3 (Resident Killers, 0.002), 4 (Porpoises, 0.002), 5 (Gray Whales, 0.007), 6 (Humpbacks, 0.005), 7 (Fin Whales, 0.004), 8 (Sei whales, 0.005), 9 (Right whales, 0.004), 10 (Minke whales, 0.007), 11 (Sea Otters, 0.002), 12 (N. Fur Seal, 0.002), 13 (N. Fur Seal_Juv, 0.002), 14 (Central S.S.L., 0.005), 15 (Central S.S.L._Juv, 0.005), 16 (West S.S.L., 0.005), 17 (West S.S.L_Juv, 0.005), 18 (Resident seals, 0.005), 19 (Shearwater, 0.001), 20 (Murres, 0.002), 21 (Kittiwakes, 0.001), 22 (Auklets, 0.002), 23 (Puffins, 0.001), 24 (Fulmars, 0.001), 25 (Storm Petrels, 0.001), 26 (Cormorants, 0.002), 27 (Gulls, 0.002), 28 (Albatross Jaeger, 0.001), 30 (Salmon shark, 0.017).

BA: carried for 3 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 32 (W. Pollock, -1.35), 36 (Herring, -0.11), 78 (Greenlings, -0.002). The remaining 130 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 1 (Transient Killers) has Q/B=11.157 but no diet entries - its consumption is missing from every prey's budget
- group 3 (Resident Killers) has Q/B=11.157 but no diet entries - its consumption is missing from every prey's budget
- group 19 (Shearwater) has Q/B=73.000 but no diet entries - its consumption is missing from every prey's budget
- group 20 (Murres) has Q/B=72.000 but no diet entries - its consumption is missing from every prey's budget
- group 21 (Kittiwakes) has Q/B=110.000 but no diet entries - its consumption is missing from every prey's budget
- group 22 (Auklets) has Q/B=110.000 but no diet entries - its consumption is missing from every prey's budget
- group 23 (Puffins) has Q/B=73.000 but no diet entries - its consumption is missing from every prey's budget
- group 24 (Fulmars) has Q/B=73.000 but no diet entries - its consumption is missing from every prey's budget
- group 25 (Storm Petrels) has Q/B=144.000 but no diet entries - its consumption is missing from every prey's budget
- group 26 (Cormorants) has Q/B=73.000 but no diet entries - its consumption is missing from every prey's budget
- group 27 (Gulls) has Q/B=73.000 but no diet entries - its consumption is missing from every prey's budget
- group 58 (Black skate) has Q/B=2.000 but no diet entries - its consumption is missing from every prey's budget
- group 43: known source diet plus import subtotal 1.0546 exceeds one; no normalization applied
- group 46: known source diet plus import subtotal 1.0693 exceeds one; no normalization applied

### Indeterminate (BA unknown)

- group 4 (Porpoises): printed EE 0.05450 vs recomputed 0.000 (diff 0.054) with BA unknown - a BA of +4.079e-05 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 6 (Humpbacks): printed EE 0.07181 vs recomputed 0.000 (diff 0.072) with BA unknown - a BA of +0.0004868 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 7 (Fin Whales): printed EE 0.10880 vs recomputed 0.007 (diff 0.102) with BA unknown - a BA of +0.0007297 t/km^2/year (+0.10 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 8 (Sei whales): printed EE 0.06766 vs recomputed 0.000 (diff 0.068) with BA unknown - a BA of +1.713e-05 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 9 (Right whales): printed EE 0.08259 vs recomputed 0.000 (diff 0.083) with BA unknown - a BA of +9.675e-06 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 10 (Minke whales): printed EE 0.05294 vs recomputed 0.000 (diff 0.053) with BA unknown - a BA of +6.372e-06 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 19 (Shearwater): printed EE 0.27538 vs recomputed 0.013 (diff 0.262) with BA unknown - a BA of +6.025e-06 t/km^2/year (+0.26 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 20 (Murres): printed EE 0.16248 vs recomputed 0.008 (diff 0.154) with BA unknown - a BA of +0.000126 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 21 (Kittiwakes): printed EE 0.35819 vs recomputed 0.018 (diff 0.341) with BA unknown - a BA of +2.335e-05 t/km^2/year (+0.34 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 22 (Auklets): printed EE 0.16248 vs recomputed 0.008 (diff 0.154) with BA unknown - a BA of +7.827e-06 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Puffins): printed EE 0.68845 vs recomputed 0.034 (diff 0.654) with BA unknown - a BA of +0.0001696 t/km^2/year (+0.65 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 24 (Fulmars): printed EE 0.50069 vs recomputed 0.025 (diff 0.476) with BA unknown - a BA of +2.145e-05 t/km^2/year (+0.48 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 25 (Storm Petrels): printed EE 0.22948 vs recomputed 0.011 (diff 0.218) with BA unknown - a BA of +6.025e-06 t/km^2/year (+0.22 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 26 (Cormorants): printed EE 0.17349 vs recomputed 0.009 (diff 0.165) with BA unknown - a BA of +9.175e-06 t/km^2/year (+0.16 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 27 (Gulls): printed EE 0.16611 vs recomputed 0.008 (diff 0.158) with BA unknown - a BA of +1.493e-05 t/km^2/year (+0.16 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 28 (Albatross Jaeger): printed EE 0.40757 vs recomputed 0.020 (diff 0.388) with BA unknown - a BA of +6.066e-06 t/km^2/year (+0.39 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 29 (Sleeper shark): printed EE 0.84261 vs recomputed 0.772 (diff 0.070) with BA unknown - a BA of +0.000124 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 31 (Dogfish): printed EE 0.89714 vs recomputed 0.706 (diff 0.191) with BA unknown - a BA of +0.00172 t/km^2/year (+0.19 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 33 (W. Pollock_Juv): printed EE 0.81664 vs recomputed 0.681 (diff 0.135) with BA unknown - a BA of +0.2428 t/km^2/year (+0.14 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 35 (P. Cod_Juv): printed EE 0.80272 vs recomputed 0.469 (diff 0.333) with BA unknown - a BA of +0.08805 t/km^2/year (+0.33 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 37 (Herring_Juv): printed EE 0.77995 vs recomputed 0.689 (diff 0.091) with BA unknown - a BA of +0.07733 t/km^2/year (+0.09 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 38 (Arrowtooth): printed EE 0.24254 vs recomputed 0.188 (diff 0.054) with BA unknown - a BA of +0.08125 t/km^2/year (+0.05 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 40 (P. Halibut): printed EE 0.40976 vs recomputed 0.348 (diff 0.061) with BA unknown - a BA of +0.0177 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 42 (YF. Sole): printed EE 0.17200 vs recomputed 0.017 (diff 0.155) with BA unknown - a BA of +0.007361 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 43 (FH. Sole): printed EE 0.34620 vs recomputed 0.260 (diff 0.086) with BA unknown - a BA of +0.01147 t/km^2/year (+0.09 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 45 (N. Rock sole): printed EE 0.27131 vs recomputed 0.151 (diff 0.120) with BA unknown - a BA of +0.005025 t/km^2/year (+0.12 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 46 (S. Rock sole): printed EE 0.20336 vs recomputed 0.105 (diff 0.099) with BA unknown - a BA of +0.006946 t/km^2/year (+0.10 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 47 (AK Plaice): printed EE 0.14337 vs recomputed 0.074 (diff 0.069) with BA unknown - a BA of +0.0002022 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 50 (Misc. Flatfish): printed EE 0.53350 vs recomputed 0.474 (diff 0.059) with BA unknown - a BA of +0.002324 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 51 (Alaska skate): printed EE 0.44411 vs recomputed 0.232 (diff 0.212) with BA unknown - a BA of +9.973e-05 t/km^2/year (+0.21 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 52 (Bering skate): printed EE 0.59166 vs recomputed 0.379 (diff 0.213) with BA unknown - a BA of +0.001238 t/km^2/year (+0.21 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 53 (Aleutian skate): printed EE 0.85155 vs recomputed 0.639 (diff 0.213) with BA unknown - a BA of +0.0001659 t/km^2/year (+0.21 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 54 (Whiteblotched skate): printed EE 0.62816 vs recomputed 0.414 (diff 0.214) with BA unknown - a BA of +2.016e-05 t/km^2/year (+0.21 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 56 (Longnosed skate): printed EE 0.78242 vs recomputed 0.570 (diff 0.213) with BA unknown - a BA of +0.002116 t/km^2/year (+0.21 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 57 (Big skate): printed EE 0.50942 vs recomputed 0.297 (diff 0.213) with BA unknown - a BA of +0.00452 t/km^2/year (+0.21 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 61 (Eelpouts): printed EE 0.80000 vs recomputed 0.725 (diff 0.075) with BA unknown - a BA of +0.03221 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 65 (Misc. fish deep): printed EE 0.80000 vs recomputed 0.720 (diff 0.080) with BA unknown - a BA of +0.000341 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 66 (POP): printed EE 0.47480 vs recomputed 0.255 (diff 0.220) with BA unknown - a BA of +0.01665 t/km^2/year (+0.22 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 68 (Sharpchin Rock): printed EE 0.80000 vs recomputed 0.642 (diff 0.158) with BA unknown - a BA of +0.005617 t/km^2/year (+0.16 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 69 (Northern Rock): printed EE 0.65053 vs recomputed 0.454 (diff 0.197) with BA unknown - a BA of +0.007137 t/km^2/year (+0.20 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 70 (Dusky Rock): printed EE 0.89610 vs recomputed 0.699 (diff 0.197) with BA unknown - a BA of +0.002748 t/km^2/year (+0.20 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 71 (Shortraker Rock): printed EE 0.61132 vs recomputed 0.421 (diff 0.190) with BA unknown - a BA of +0.001471 t/km^2/year (+0.19 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 72 (Rougheye Rock): printed EE 0.39262 vs recomputed 0.202 (diff 0.190) with BA unknown - a BA of +0.003125 t/km^2/year (+0.19 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 73 (Shortspine Thorns): printed EE 0.81817 vs recomputed 0.727 (diff 0.091) with BA unknown - a BA of +0.0007502 t/km^2/year (+0.09 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 75 (Other Sebastes): printed EE 0.80000 vs recomputed 0.627 (diff 0.173) with BA unknown - a BA of +0.001548 t/km^2/year (+0.17 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 80 (Other sculpins): printed EE 0.80000 vs recomputed 0.715 (diff 0.085) with BA unknown - a BA of +0.02779 t/km^2/year (+0.09 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 81 (Misc. fish shallow): printed EE 0.80000 vs recomputed 0.618 (diff 0.182) with BA unknown - a BA of +0.06119 t/km^2/year (+0.18 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 84 (Salmon returning): printed EE 0.49750 vs recomputed 0.386 (diff 0.111) with BA unknown - a BA of +0.1734 t/km^2/year (+0.11 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 85 (Salmon outgoing): printed EE 0.12440 vs recomputed 0.000 (diff 0.124) with BA unknown - a BA of +0.003499 t/km^2/year (+0.12 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 88 (Capelin): printed EE 0.80000 vs recomputed 0.656 (diff 0.144) with BA unknown - a BA of +0.8118 t/km^2/year (+0.14 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 89 (Sandlance): printed EE 0.80000 vs recomputed 0.649 (diff 0.151) with BA unknown - a BA of +0.2944 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 90 (Eulachon): printed EE 0.80000 vs recomputed 0.665 (diff 0.135) with BA unknown - a BA of +0.124 t/km^2/year (+0.13 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 91 (Oth. managed forage): printed EE 0.80000 vs recomputed 0.661 (diff 0.139) with BA unknown - a BA of +0.1583 t/km^2/year (+0.14 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 92 (Oth. pelagic smelt): printed EE 0.80000 vs recomputed 0.681 (diff 0.119) with BA unknown - a BA of +0.06121 t/km^2/year (+0.12 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 99 (Urchins dollars cucumber): printed EE 0.35036 vs recomputed 0.249 (diff 0.101) with BA unknown - a BA of +0.101 t/km^2/year (+0.10 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 102 (Misc. crabs): printed EE 0.80000 vs recomputed 0.735 (diff 0.065) with BA unknown - a BA of +0.0921 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 109 (Sea Pens): printed EE 0.20133 vs recomputed 0.139 (diff 0.063) with BA unknown - a BA of +3.163e-06 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 1: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 2: diet/import has unknown cells; known subtotal 0.85 is not a complete composition
- group 3: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 4: diet/import has unknown cells; known subtotal 0.693 is not a complete composition
- group 5: diet/import has unknown cells; known subtotal 0.9 is not a complete composition
- group 6: diet/import has unknown cells; known subtotal 0.01 is not a complete composition
- group 7: diet/import has unknown cells; known subtotal 0.2 is not a complete composition
- group 8: diet/import has unknown cells; known subtotal 0.85 is not a complete composition
- group 9: diet/import has unknown cells; known subtotal 0.95 is not a complete composition
- group 10: diet/import has unknown cells; known subtotal 0.04 is not a complete composition
- group 11: diet/import has unknown cells; known subtotal 0.05 is not a complete composition
- group 12: diet/import has unknown cells; known subtotal 0.925 is not a complete composition
- group 13: diet/import has unknown cells; known subtotal 0.805 is not a complete composition
- group 14: diet/import has unknown cells; known subtotal 0.762 is not a complete composition
- group 15: diet/import has unknown cells; known subtotal 0.135 is not a complete composition
- group 16: diet/import has unknown cells; known subtotal 0.768 is not a complete composition
- group 17: diet/import has unknown cells; known subtotal 0.232 is not a complete composition
- group 18: diet/import has unknown cells; known subtotal 0.145 is not a complete composition
- group 19: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 20: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 21: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 22: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 23: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 24: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 25: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 26: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 27: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 28: diet/import has unknown cells; known subtotal 0.5 is not a complete composition
- group 29: diet/import has unknown cells; known subtotal 0.9682 is not a complete composition
- group 30: diet/import has unknown cells; known subtotal 0.95 is not a complete composition
- group 31: diet/import has unknown cells; known subtotal 0.554 is not a complete composition
- group 32: diet/import has unknown cells; known subtotal 0.9998 is not a complete composition
- group 33: diet/import has unknown cells; known subtotal 1.0001 is not a complete composition
- group 34: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 35: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 36: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 37: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 38: diet/import has unknown cells; known subtotal 0.9998 is not a complete composition
- group 39: diet/import has unknown cells; known subtotal 1.0002 is not a complete composition
- group 40: diet/import has unknown cells; known subtotal 0.9995 is not a complete composition
- group 41: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 42: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 43: diet/import has unknown cells; known subtotal 1.0546 is not a complete composition
- group 44: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 45: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 46: diet/import has unknown cells; known subtotal 1.0693 is not a complete composition
- group 47: diet/import has unknown cells; known subtotal 0.9998 is not a complete composition
- group 48: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 49: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 50: diet/import has unknown cells; known subtotal 1.0001 is not a complete composition
- group 51: diet/import has unknown cells; known subtotal 0.883 is not a complete composition
- group 52: diet/import has unknown cells; known subtotal 0.998 is not a complete composition
- group 53: diet/import has unknown cells; known subtotal 0.847 is not a complete composition
- group 54: diet/import has unknown cells; known subtotal 0.891 is not a complete composition
- group 55: diet/import has unknown cells; known subtotal 0.891 is not a complete composition
- group 55: discard removals unknown; reported catch does not establish complete removals
- group 56: diet/import has unknown cells; known subtotal 0.275 is not a complete composition
- group 57: diet/import has unknown cells; known subtotal 0.707 is not a complete composition
- group 58: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 58: discard removals unknown; reported catch does not establish complete removals
- group 59: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 60: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 61: diet/import has unknown cells; known subtotal 1.0002 is not a complete composition
- group 62: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 63: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 64: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 65: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 66: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 67: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 68: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 69: diet/import has unknown cells; known subtotal 1.0001 is not a complete composition
- group 70: diet/import has unknown cells; known subtotal 1.0001 is not a complete composition
- group 71: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 72: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 73: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 74: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 75: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 76: diet/import has unknown cells; known subtotal 0.9999 is not a complete composition
- group 77: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 78: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 79: diet/import has unknown cells; known subtotal 0.9692 is not a complete composition
- group 80: diet/import has unknown cells; known subtotal 0.9998 is not a complete composition
- group 81: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 82: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 83: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 84: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 85: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 86: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 87: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 88: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 89: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 90: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 91: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 92: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 93: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 94: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 95: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 96: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 97: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 98: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 99: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 100: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 101: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 102: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 103: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 104: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 105: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 106: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 107: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 108: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 109: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 110: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 111: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 112: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 113: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 114: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 115: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 116: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 117: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 118: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 119: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 120: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 121: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 122: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 123: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 124: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 128: discard removals unknown; reported catch does not establish complete removals
- group 129: discard removals unknown; reported catch does not establish complete removals
- group 130: discard removals unknown; reported catch does not establish complete removals
- group 131: discard removals unknown; reported catch does not establish complete removals
- group 132: discard removals unknown; reported catch does not establish complete removals
- group 133: discard removals unknown; reported catch does not establish complete removals

### Warnings

- group 1 (Transient Killers): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Sperm and beaked whale): P/Q = 0.007 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Resident Killers): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Porpoises): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 5 (Gray Whales): P/Q = 0.007 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 6 (Humpbacks): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 7 (Fin Whales): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 8 (Sei whales): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 9 (Right whales): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 10 (Minke whales): P/Q = 0.007 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 11 (Sea Otters): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 12 (N. Fur Seal): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 13 (N. Fur Seal_Juv): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 14 (Central S.S.L.): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 15 (Central S.S.L._Juv): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 16 (West S.S.L.): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 17 (West S.S.L_Juv): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 18 (Resident seals): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 19 (Shearwater): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 20 (Murres): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 21 (Kittiwakes): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 22 (Auklets): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 23 (Puffins): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 24 (Fulmars): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 25 (Storm Petrels): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 26 (Cormorants): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 27 (Gulls): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 28 (Albatross Jaeger): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 30 (Salmon shark): P/Q = 0.017 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 32 (W. Pollock): printed EE 0.98173 vs recomputed 0.914 (diff 0.068), BA -1.35 carried (absolute or derived internally from source BA rate)
- group 36 (Herring): printed EE 0.96844 vs recomputed 0.868 (diff 0.100), BA -0.11 carried (absolute or derived internally from source BA rate)

### Notes

- 128 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Transient Killers), 2 (Sperm and beaked whale), 3 (Resident Killers), 4 (Porpoises), 5 (Gray Whales), 6 (Humpbacks), 7 (Fin Whales), 8 (Sei whales) ...
- detritus pools (5): inflow ~4058, consumption ~1451 t/km^2/year, implied EE ~0.358 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Transient Killers | 0.00014 | 0.025 | 11.16 | 0 | 0 | 0.00224 | 0 | unknown |
| 2 | Sperm and beaked whale | 0.04509 | 0.047 | 6.609 | 0 | 0 | 0.00711 | 0 | unknown |
| 3 | Resident Killers | 0.00136 | 0.025 | 11.16 | 0.02055 | 0.0212 | 0.00224 | 7.196e-07 | unknown |
| 4 | Porpoises | 0.01507 | 0.05 | 30 | 0.0545 | 0.000364 | 0.00167 | 2.741e-07 | unknown |
| 5 | Gray Whales | 0.05543 | 0.063 | 8.873 | 0.04275 | 2.94e-05 | 0.0071 | 1.028e-07 | unknown |
| 6 | Humpbacks | 0.1784 | 0.038 | 7.577 | 0.07181 | 0 | 0.00502 | 0 | unknown |
| 7 | Fin Whales | 0.2661 | 0.027 | 6.517 | 0.1088 | 0.00723 | 0.00414 | 5.195e-05 | unknown |
| 8 | Sei whales | 0.00633 | 0.04 | 8.788 | 0.06766 | 0 | 0.00455 | 0 | unknown |
| 9 | Right whales | 0.00355 | 0.033 | 8 | 0.08259 | 0 | 0.00413 | 0 | unknown |
| 10 | Minke whales | 0.00236 | 0.051 | 7.782 | 0.05294 | 0 | 0.00655 | 0 | unknown |
| 11 | Sea Otters | 0.00345 | 0.117 | 73 | 0.02326 | 8.49e-05 | 0.0016 | 3.427e-08 | unknown |
| 12 | N. Fur Seal | 0.00904 | 0.091 | 39.03 | 0.02983 | 0 | 0.00233 | 0 | unknown |
| 13 | N. Fur Seal_Juv | 5e-05 | 0.116 | 49.53 | 0.02338 | 0.0236 | 0.00234 | 1.371e-07 | unknown |
| 14 | Central S.S.L. | 0.01085 | 0.11 | 24.07 | 0.04715 | 0.0225 | 0.00457 | 2.68e-05 | unknown |
| 15 | Central S.S.L._Juv | 0.00103 | 0.494 | 108.3 | 0.00989 | 0.00444 | 0.00456 | 2.262e-06 | unknown |
| 16 | West S.S.L. | 0.00508 | 0.11 | 24.07 | 0.04569 | 0.021 | 0.00457 | 1.175e-05 | unknown |
| 17 | West S.S.L_Juv | 0.00066 | 0.494 | 108.3 | 0.00988 | 0.00441 | 0.00456 | 1.439e-06 | unknown |
| 18 | Resident seals | 0.00329 | 0.083 | 17.44 | 0.2253 | 0.192 | 0.00476 | 5.239e-05 | unknown |
| 19 | Shearwater | 0.00023 | 0.1 | 73 | 0.2754 | 0.0134 | 0.00137 | 3.084e-07 | unknown |
| 20 | Murres | 0.00483 | 0.169 | 72 | 0.1625 | 0.00806 | 0.00235 | 6.579e-06 | unknown |
| 21 | Kittiwakes | 0.00089 | 0.077 | 110 | 0.3582 | 0.0175 | 0.0007 | 1.199e-06 | unknown |
| 22 | Auklets | 0.0003 | 0.169 | 110 | 0.1625 | 0.00811 | 0.00154 | 4.112e-07 | unknown |
| 23 | Puffins | 0.00648 | 0.04 | 73 | 0.6885 | 0.034 | 0.000548 | 8.806e-06 | unknown |
| 24 | Fulmars | 0.00082 | 0.055 | 73 | 0.5007 | 0.0251 | 0.000753 | 1.131e-06 | unknown |
| 25 | Storm Petrels | 0.00023 | 0.12 | 144 | 0.2295 | 0.0112 | 0.000833 | 3.084e-07 | unknown |
| 26 | Cormorants | 0.00035 | 0.159 | 73 | 0.1735 | 0.00862 | 0.00218 | 4.797e-07 | unknown |
| 27 | Gulls | 0.00057 | 0.166 | 73 | 0.1661 | 0.00833 | 0.00227 | 7.881e-07 | unknown |
| 28 | Albatross Jaeger | 0.00023 | 0.068 | 75 | 0.4076 | 0.0197 | 0.000907 | 3.084e-07 | unknown |
| 29 | Sleeper shark | 0.01765 | 0.1 | 3 | 0.8426 | 0.772 | 0.0333 | 0.001363 | unknown |
| 30 | Salmon shark | 0.03459 | 0.1 | 6 | 0.1351 | 0.135 | 0.0167 | 0.0004674 | unknown |
| 31 | Dogfish | 0.09011 | 0.1 | 3 | 0.8971 | 0.706 | 0.0333 | 0.004289 | unknown |
| 32 | W. Pollock | 5.553 | 0.41 | 3.78 | 0.9817 | 0.914 | 0.108 | 0.3429 | -1.35 |
| 33 | W. Pollock_Juv | 0.6718 | 2.669 | 6.83 | 0.8166 | 0.681 | 0.391 | 0 | unknown |
| 34 | P. Cod | 1.39 | 0.42 | 2.19 | 0.5359 | 0.486 | 0.192 | 0.2508 | unknown |
| 35 | P. Cod_Juv | 0.1303 | 2.026 | 4.59 | 0.8027 | 0.469 | 0.441 | 0 | unknown |
| 36 | Herring | 0.2806 | 0.4 | 3.52 | 0.9684 | 0.868 | 0.114 | 0.05556 | -0.11 |
| 37 | Herring_Juv | 0.5976 | 1.419 | 4.334 | 0.78 | 0.689 | 0.327 | 0 | unknown |
| 38 | Arrowtooth | 5.766 | 0.26 | 1.44 | 0.2425 | 0.188 | 0.181 | 0.06808 | unknown |
| 39 | Arrowtooth_Juv | 0.5465 | 0.898 | 2.45 | 0.125 | 0.11 | 0.367 | 0 | unknown |
| 40 | P. Halibut | 1.52 | 0.19 | 1.1 | 0.4098 | 0.348 | 0.173 | 0.09832 | unknown |
| 41 | P. Halibut_Juv | 0.1825 | 0.382 | 1.42 | 0.3683 | 0.332 | 0.269 | 0 | unknown |
| 42 | YF. Sole | 0.2379 | 0.2 | 2 | 0.172 | 0.0173 | 0.1 | 0.0002412 | unknown |
| 43 | FH. Sole | 0.7394 | 0.18 | 1.69 | 0.3462 | 0.26 | 0.107 | 0.00728 | unknown |
| 44 | FH. Sole_Juv | 0.0578 | 1.1 | 3.13 | 0.8 | 0.779 | 0.351 | 0 | unknown |
| 45 | N. Rock sole | 0.2097 | 0.2 | 2 | 0.2713 | 0.151 | 0.1 | 0.006353 | unknown |
| 46 | S. Rock sole | 0.3521 | 0.2 | 2 | 0.2034 | 0.105 | 0.1 | 0.006354 | unknown |
| 47 | AK Plaice | 0.01467 | 0.2 | 2 | 0.1434 | 0.0744 | 0.1 | 5.071e-06 | unknown |
| 48 | Dover Sole | 0.3185 | 0.2 | 2 | 0.8099 | 0.766 | 0.1 | 0.02561 | unknown |
| 49 | Rex Sole | 0.3182 | 0.2 | 2 | 0.6675 | 0.633 | 0.1 | 0.009741 | unknown |
| 50 | Misc. Flatfish | 0.1958 | 0.2 | 2 | 0.5335 | 0.474 | 0.1 | 0.01735 | unknown |
| 51 | Alaska skate | 0.00235 | 0.2 | 2 | 0.4441 | 0.232 | 0.1 | 0.000109 | unknown |
| 52 | Bering skate | 0.02908 | 0.2 | 2 | 0.5917 | 0.379 | 0.1 | 0.002172 | unknown |
| 53 | Aleutian skate | 0.0039 | 0.2 | 2 | 0.8516 | 0.639 | 0.1 | 0.0004983 | unknown |
| 54 | Whiteblotched skate | 0.00047 | 0.2 | 2 | 0.6282 | 0.414 | 0.1 | 3.889e-05 | unknown |
| 55 | Mud skate | 0 | 0.2 | 2 | 0.2127 | - | 0.1 | 0 | unknown |
| 56 | Longnosed skate | 0.04974 | 0.2 | 2 | 0.7824 | 0.57 | 0.1 | 0.005668 | unknown |
| 57 | Big skate | 0.1063 | 0.2 | 2 | 0.5094 | 0.297 | 0.1 | 0.006307 | unknown |
| 58 | Black skate | 0 | 0.2 | 2 | 0.2127 | - | 0.1 | 0 | unknown |
| 59 | Sablefish | 0.9315 | 0.19 | 1.03 | 0.856 | 0.813 | 0.184 | 0.06218 | unknown |
| 60 | Sablefish_Juv | 0.00597 | 1.65 | 3.32 | 0.8 | 0.791 | 0.497 | 0 | unknown |
| 61 | Eelpouts | 1.069 | 0.4 | 2 | 0.8 | 0.725 | 0.2 | 2.426e-05 | unknown |
| 62 | Giant Grenadier | 0.9076 | 0.15 | 2 | 0.3205 | 0.274 | 0.075 | 0.03725 | unknown |
| 63 | Pacific Grenadier | 0.00103 | 0.15 | 2 | 0.1686 | 0.122 | 0.075 | 1.881e-05 | unknown |
| 64 | Other Macruids | 0.00913 | 0.15 | 2 | 0.3092 | 0.262 | 0.075 | 0.0003575 | unknown |
| 65 | Misc. fish deep | 0.02137 | 0.2 | 2 | 0.8 | 0.72 | 0.1 | 0.001238 | unknown |
| 66 | POP | 0.8407 | 0.09 | 1.99 | 0.4748 | 0.255 | 0.0452 | 0.01577 | unknown |
| 67 | POP_Juv | 0.00593 | 1.1 | 3.48 | 0.0072 | 0 | 0.316 | 0 | unknown |
| 68 | Sharpchin Rock | 0.3554 | 0.1 | 2 | 0.8 | 0.642 | 0.05 | 0.02282 | unknown |
| 69 | Northern Rock | 0.3624 | 0.1 | 2 | 0.6505 | 0.454 | 0.05 | 0.01644 | unknown |
| 70 | Dusky Rock | 0.1396 | 0.1 | 2 | 0.8961 | 0.699 | 0.05 | 0.009757 | unknown |
| 71 | Shortraker Rock | 0.0774 | 0.1 | 2 | 0.6113 | 0.421 | 0.05 | 0.003258 | unknown |
| 72 | Rougheye Rock | 0.1644 | 0.1 | 2 | 0.3926 | 0.202 | 0.05 | 0.003328 | unknown |
| 73 | Shortspine Thorns | 0.06315 | 0.13 | 0.44 | 0.8182 | 0.727 | 0.295 | 0.00504 | unknown |
| 74 | Shortspine Thorns_Juv | 0.00061 | 0.21 | 0.57 | 0.8 | 0.759 | 0.368 | 0 | unknown |
| 75 | Other Sebastes | 0.08924 | 0.1 | 2 | 0.8 | 0.627 | 0.05 | 0.00137 | unknown |
| 76 | Atka mackerel | 0.4545 | 0.35 | 5.65 | 0.698 | 0.684 | 0.0619 | 0.01457 | unknown |
| 77 | Atka mackerel_Juv | 0.06491 | 1.9 | 8.9 | 0.8 | 0.773 | 0.213 | 0 | unknown |
| 78 | Greenlings | 0.01111 | 0.4 | 2 | 0.0533 | 0.0408 | 0.2 | 4.972e-05 | -0.002 |
| 79 | Lg. Sculpins | 0.08889 | 0.4 | 2 | 0.6763 | 0.65 | 0.2 | 0.004449 | unknown |
| 80 | Other sculpins | 0.8169 | 0.4 | 2 | 0.8 | 0.715 | 0.2 | 0 | unknown |
| 81 | Misc. fish shallow | 0.839 | 0.4 | 2 | 0.8 | 0.618 | 0.2 | 0.001239 | unknown |
| 82 | Octopi | 0.7835 | 0.8 | 3.65 | 0.8 | 0.794 | 0.219 | 0.0003331 | unknown |
| 83 | Squids | 1.265 | 3.2 | 10.67 | 0.8 | 0.776 | 0.3 | 0.0003451 | unknown |
| 84 | Salmon returning | 0.8566 | 1.816 | 11.83 | 0.4975 | 0.386 | 0.154 | 0.3202 | unknown |
| 85 | Salmon outgoing | 0.01713 | 1.642 | 14.39 | 0.1244 | 0 | 0.114 | 0 | unknown |
| 86 | Bathylagidae | 0.07371 | 0.8 | 3.65 | 0.8 | 0.776 | 0.219 | 0 | unknown |
| 87 | Myctophidae | 0.6348 | 0.8 | 3.65 | 0.8 | 0.777 | 0.219 | 0 | unknown |
| 88 | Capelin | 7.025 | 0.8 | 3.65 | 0.8 | 0.656 | 0.219 | 0.0001906 | unknown |
| 89 | Sandlance | 2.443 | 0.8 | 3.65 | 0.8 | 0.649 | 0.219 | 4.797e-07 | unknown |
| 90 | Eulachon | 1.15 | 0.8 | 3.65 | 0.8 | 0.665 | 0.219 | 0.0002012 | unknown |
| 91 | Oth. managed forage | 1.424 | 0.8 | 3.65 | 0.8 | 0.661 | 0.219 | 1.073e-05 | unknown |
| 92 | Oth. pelagic smelt | 0.6421 | 0.8 | 3.65 | 0.8 | 0.681 | 0.219 | 4.441e-05 | unknown |
| 93 | Bairdi | 0.6284 | 1 | 3 | 0.8 | 0.798 | 0.333 | 0.003691 | unknown |
| 94 | King Crab | 0.00615 | 0.6 | 3 | 0.9062 | 0.91 | 0.2 | 7.854e-05 | unknown |
| 95 | Pandalidae | 10.69 | 0.576 | 2.41 | 0.8 | 0.798 | 0.239 | 0.0001983 | unknown |
| 96 | NP shrimp | 11.54 | 0.576 | 2.41 | 0.8 | 0.798 | 0.239 | 5.482e-06 | unknown |
| 97 | Sea stars | 0.09552 | 1.21 | 6.05 | 0.4919 | 0.487 | 0.2 | 0.003116 | unknown |
| 98 | Brittle stars | 4.544 | 1.21 | 6.05 | 0.2014 | 0.2 | 0.2 | 0 | unknown |
| 99 | Urchins dollars cucumber | 1.631 | 0.61 | 3.05 | 0.3504 | 0.249 | 0.2 | 7.771e-05 | unknown |
| 100 | Snails | 0.8639 | 1.81 | 9.05 | 0.8 | 0.8 | 0.2 | 3.427e-07 | unknown |
| 101 | Hermit crabs | 2.846 | 0.82 | 4.1 | 0.8 | 0.799 | 0.2 | 0 | unknown |
| 102 | Misc. crabs | 1.738 | 0.82 | 4.1 | 0.8 | 0.735 | 0.2 | 8.022e-05 | unknown |
| 103 | Misc. Crustacean | 2.12 | 7.4 | 37 | 0.8 | 0.798 | 0.2 | 0 | unknown |
| 104 | Benthic Amphipods | 5.869 | 7.4 | 37 | 0.8 | 0.8 | 0.2 | 0 | unknown |
| 105 | Anemones | 0.08887 | 1 | 5 | 0.00191 | 0.000836 | 0.2 | 7.432e-05 | unknown |
| 106 | Corals | 0.00519 | 0.046 | 0.23 | 0.1034 | 0.0847 | 0.2 | 2.022e-05 | unknown |
| 107 | Hydroids | 0.1051 | 1 | 5 | 0.8 | 0.798 | 0.2 | 0 | unknown |
| 108 | Urochordata | 0.2448 | 3.58 | 17.9 | 0.00936 | 0.00911 | 0.2 | 6.75e-06 | unknown |
| 109 | Sea Pens | 0.00055 | 0.092 | 0.461 | 0.2013 | 0.139 | 0.2 | 7.024e-06 | unknown |
| 110 | Sponges | 0.1075 | 1 | 5 | 0.00269 | 0.000196 | 0.2 | 2.111e-05 | unknown |
| 111 | Bivalves | 13.85 | 1.3 | 6.5 | 0.8 | 0.799 | 0.2 | 0.0002807 | unknown |
| 112 | Polychaetes | 3.923 | 2.97 | 14.85 | 0.8 | 0.8 | 0.2 | 0 | unknown |
| 113 | Misc. worms | 3.668 | 2.23 | 11.15 | 0.8 | 0.799 | 0.2 | 0 | unknown |
| 114 | Scyphozoid Jellies | 0.11 | 0.88 | 3 | 0.4836 | 0.483 | 0.293 | 0.0003371 | unknown |
| 115 | Fish Larvae | 0.00378 | 5.475 | 15.64 | 0.8 | 0.797 | 0.35 | 0 | unknown |
| 116 | Chaetognaths | 0.5853 | 5.475 | 15.64 | 0.8 | 0.783 | 0.35 | 0 | unknown |
| 117 | Euphausiids | 20.16 | 5.475 | 15.64 | 0.8 | 0.785 | 0.35 | 0 | unknown |
| 118 | Mysids | 0.3579 | 5.475 | 15.64 | 0.8 | 0.784 | 0.35 | 0 | unknown |
| 119 | Pelagic Amphipods | 1.351 | 2.5 | 7.143 | 0.8 | 0.769 | 0.35 | 0 | unknown |
| 120 | Gelatinous filter feeders | 0.9392 | 5.475 | 15.64 | 0.8 | 0.8 | 0.35 | 0 | unknown |
| 121 | Pteropods | 0.5998 | 5.475 | 15.64 | 0.8 | 0.783 | 0.35 | 0 | unknown |
| 122 | Copepods | 21.86 | 6 | 27.74 | 0.8 | 0.799 | 0.216 | 0 | unknown |
| 123 | Pelagic microbes | 12.26 | 36.5 | 104.3 | 0.8 | 0.8 | 0.35 | 0 | unknown |
| 124 | Benthic microbes | 7.252 | 36.5 | 104.3 | 0.8 | 0.8 | 0.35 | 0 | unknown |
| 125 | Macroalgae | 0.8772 | 4 | 0 | 0.8 | 0.8 | - | 0 | unknown |
| 126 | Lg Phytoplankton | 7.861 | 166.5 | 0 | 0.2532 | 0.253 | - | 0 | unknown |
| 127 | Sm Phytoplankton | 27.66 | 113.4 | 0 | 0.3453 | 0.345 | - | 0 | unknown |
| 128 | Outside Production | 4 | 1 | 0 | 0 | 0 | - | 0 | unknown |
| 129 | Discards | 0 | 0 | 0 | 0.0591 | - | - | 0 | unknown |
| 130 | Offal | 0 | 0 | 0 | 0.6084 | - | - | 0 | unknown |
| 131 | Pelagic Detritus | 0 | 0 | 0 | 0.1928 | - | - | 0 | unknown |
| 132 | Benthic Detritus | 0 | 0 | 0 | 0.5164 | - | - | 0 | unknown |
| 133 | Outside Detritus | 0 | 0 | 0 | 0 | - | - | 0 | unknown |
