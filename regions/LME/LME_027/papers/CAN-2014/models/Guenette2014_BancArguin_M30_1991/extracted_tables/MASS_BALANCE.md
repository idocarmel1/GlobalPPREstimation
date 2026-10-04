## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 27_Canary_Current_Guenette2014_M30_Banc_d_Arguin_and_Mauritanian_Shelf_M30_(1991), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 3 error(s), 125 indeterminate, 10 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 1 of 51 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.463, group 35 (BA crustaceans).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Marine mammals, 0.003), 2 (Coastal birds, 0.004).

BA: carried for 50 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Marine mammals, +0), 2 (Coastal birds, +0), 3 (Meagre ad, +0), 4 (Meagre juv, +0), 5 (Mullets, +0), 6 (Pelagic L, +0), 7 (Mackerel, +0), 8 (Sardine, +0), 9 (Sardinelles, +0), 10 (Horse mackerels, +0), 11 (Coastal selacians, -0.062), 12 (Coastal M, +0), 13 (Coastal S, +0), 14 (Croakers ad, +0), 15 (Croakers juv, +0), 16 (Seabreams ad, +0), 17 (Seabreams juv., +0), 18 (Catfish ad, +0), 19 (Catfish juv, +0), 20 (Shelf selacians, +0), 21 (Shelf L, +0), 22 (Shelf M, +0), 23 (Groupers ad, -0.0055), 24 (Grouper juv, -0), 25 (Sparids ad, +0), 26 (Sparids juv, +0), 27 (Scianids, -0.011), 28 (Shelf soles, +0), 29 (Shelf S, +0), 30 (Octopus vulgaris, -0.0411), 31 (Cephalopods, -0.03), 32 (BA L crustaceans, +0), 33 (BA molluscs, +0), 34 (BA worms, +0), 35 (BA crustaceans, +0), 36 (BA other inverts, +0), 37 (BA meiobenthos, +0), 38 (shelf L crustaceans, +0), 39 (shelf molluscs, +0), 40 (shelf worms, +0), 41 (shelf crustaceans, +0), 42 (shelf other inverts, +0), 43 (shelf meiobenthos, +0), 44 (mesozoopl., +0), 45 (macrozoopl., +0), 46 (BA mesozoopl., +0), 47 (BA macrozoopl., +0), 48 (BA phytopl., +0), 49 (phytoplankton, +0), 50 (algae and eelgrass, +0). The remaining 1 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 13 (Coastal S) has Q/B=3.1 but no diet entries - its consumption is missing from every prey's budget
- group 19 (Catfish juv) has Q/B=22.3 but no diet entries - its consumption is missing from every prey's budget
- group 23: known source diet plus import subtotal 2.2006 exceeds one; no normalization applied

### Indeterminate (BA unknown)

- group 1: unassimilated fraction unknown; indicative checks use a software assumption
- group 1: discard removals unknown; reported catch does not establish complete removals
- group 2: diet/import has unknown cells; known subtotal 0.980331 is not a complete composition
- group 2: unassimilated fraction unknown; indicative checks use a software assumption
- group 2: discard removals unknown; reported catch does not establish complete removals
- group 3: diet/import has unknown cells; known subtotal 0.8461 is not a complete composition
- group 3: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 3: unassimilated fraction unknown; indicative checks use a software assumption
- group 3: discard removals unknown; reported catch does not establish complete removals
- group 4: diet/import has unknown cells; known subtotal 0.70807 is not a complete composition
- group 4: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 4: unassimilated fraction unknown; indicative checks use a software assumption
- group 4: discard removals unknown; reported catch does not establish complete removals
- group 5: diet/import has unknown cells; known subtotal 0.908 is not a complete composition
- group 5: unassimilated fraction unknown; indicative checks use a software assumption
- group 5: discard removals unknown; reported catch does not establish complete removals
- group 6: unassimilated fraction unknown; indicative checks use a software assumption
- group 6: discard removals unknown; reported catch does not establish complete removals
- group 7: unassimilated fraction unknown; indicative checks use a software assumption
- group 7: discard removals unknown; reported catch does not establish complete removals
- group 8: unassimilated fraction unknown; indicative checks use a software assumption
- group 8: discard removals unknown; reported catch does not establish complete removals
- group 9: unassimilated fraction unknown; indicative checks use a software assumption
- group 9: discard removals unknown; reported catch does not establish complete removals
- group 10: unassimilated fraction unknown; indicative checks use a software assumption
- group 10: discard removals unknown; reported catch does not establish complete removals
- group 11: diet/import has unknown cells; known subtotal 0.51811 is not a complete composition
- group 11: unassimilated fraction unknown; indicative checks use a software assumption
- group 11: discard removals unknown; reported catch does not establish complete removals
- group 12: diet/import has unknown cells; known subtotal 0.3639 is not a complete composition
- group 12: unassimilated fraction unknown; indicative checks use a software assumption
- group 12: discard removals unknown; reported catch does not establish complete removals
- group 13: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 13: unassimilated fraction unknown; indicative checks use a software assumption
- group 13: discard removals unknown; reported catch does not establish complete removals
- group 14: diet/import has unknown cells; known subtotal 0.29507 is not a complete composition
- group 14: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 14: unassimilated fraction unknown; indicative checks use a software assumption
- group 14: discard removals unknown; reported catch does not establish complete removals
- group 15: diet/import has unknown cells; known subtotal 0.0375 is not a complete composition
- group 15: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 15: unassimilated fraction unknown; indicative checks use a software assumption
- group 15: discard removals unknown; reported catch does not establish complete removals
- group 16: diet/import has unknown cells; known subtotal 0.164 is not a complete composition
- group 16: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 16: unassimilated fraction unknown; indicative checks use a software assumption
- group 16: discard removals unknown; reported catch does not establish complete removals
- group 17: diet/import has unknown cells; known subtotal 0.0184 is not a complete composition
- group 17: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 17: unassimilated fraction unknown; indicative checks use a software assumption
- group 17: discard removals unknown; reported catch does not establish complete removals
- group 18: diet/import has unknown cells; known subtotal 0.3844 is not a complete composition
- group 18: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 18: unassimilated fraction unknown; indicative checks use a software assumption
- group 18: discard removals unknown; reported catch does not establish complete removals
- group 19: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 19: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 19: unassimilated fraction unknown; indicative checks use a software assumption
- group 19: discard removals unknown; reported catch does not establish complete removals
- group 20: unassimilated fraction unknown; indicative checks use a software assumption
- group 20: discard removals unknown; reported catch does not establish complete removals
- group 21: unassimilated fraction unknown; indicative checks use a software assumption
- group 21: discard removals unknown; reported catch does not establish complete removals
- group 22: unassimilated fraction unknown; indicative checks use a software assumption
- group 22: discard removals unknown; reported catch does not establish complete removals
- group 23: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 23: unassimilated fraction unknown; indicative checks use a software assumption
- group 23: discard removals unknown; reported catch does not establish complete removals
- group 24: diet/import has unknown cells; known subtotal 0.3438 is not a complete composition
- group 24: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 24: unassimilated fraction unknown; indicative checks use a software assumption
- group 24: discard removals unknown; reported catch does not establish complete removals
- group 25: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 25: unassimilated fraction unknown; indicative checks use a software assumption
- group 25: discard removals unknown; reported catch does not establish complete removals
- group 26: diet/import has unknown cells; known subtotal 0.5454 is not a complete composition
- group 26: source P/B is missing or nonpositive; native/stanza production cannot be verified
- group 26: unassimilated fraction unknown; indicative checks use a software assumption
- group 26: discard removals unknown; reported catch does not establish complete removals
- group 27: unassimilated fraction unknown; indicative checks use a software assumption
- group 27: discard removals unknown; reported catch does not establish complete removals
- group 28: unassimilated fraction unknown; indicative checks use a software assumption
- group 28: discard removals unknown; reported catch does not establish complete removals
- group 29: unassimilated fraction unknown; indicative checks use a software assumption
- group 29: discard removals unknown; reported catch does not establish complete removals
- group 30: unassimilated fraction unknown; indicative checks use a software assumption
- group 30: discard removals unknown; reported catch does not establish complete removals
- group 31: unassimilated fraction unknown; indicative checks use a software assumption
- group 31: discard removals unknown; reported catch does not establish complete removals
- group 32: unassimilated fraction unknown; indicative checks use a software assumption
- group 32: discard removals unknown; reported catch does not establish complete removals
- group 33: unassimilated fraction unknown; indicative checks use a software assumption
- group 33: discard removals unknown; reported catch does not establish complete removals
- group 34: unassimilated fraction unknown; indicative checks use a software assumption
- group 34: discard removals unknown; reported catch does not establish complete removals
- group 35: unassimilated fraction unknown; indicative checks use a software assumption
- group 35: discard removals unknown; reported catch does not establish complete removals
- group 36: unassimilated fraction unknown; indicative checks use a software assumption
- group 36: discard removals unknown; reported catch does not establish complete removals
- group 37: unassimilated fraction unknown; indicative checks use a software assumption
- group 37: discard removals unknown; reported catch does not establish complete removals
- group 38: unassimilated fraction unknown; indicative checks use a software assumption
- group 38: discard removals unknown; reported catch does not establish complete removals
- group 39: unassimilated fraction unknown; indicative checks use a software assumption
- group 39: discard removals unknown; reported catch does not establish complete removals
- group 40: unassimilated fraction unknown; indicative checks use a software assumption
- group 40: discard removals unknown; reported catch does not establish complete removals
- group 41: unassimilated fraction unknown; indicative checks use a software assumption
- group 41: discard removals unknown; reported catch does not establish complete removals
- group 42: unassimilated fraction unknown; indicative checks use a software assumption
- group 42: discard removals unknown; reported catch does not establish complete removals
- group 43: unassimilated fraction unknown; indicative checks use a software assumption
- group 43: discard removals unknown; reported catch does not establish complete removals
- group 44: unassimilated fraction unknown; indicative checks use a software assumption
- group 44: discard removals unknown; reported catch does not establish complete removals
- group 45: unassimilated fraction unknown; indicative checks use a software assumption
- group 45: discard removals unknown; reported catch does not establish complete removals
- group 46: unassimilated fraction unknown; indicative checks use a software assumption
- group 46: discard removals unknown; reported catch does not establish complete removals
- group 47: unassimilated fraction unknown; indicative checks use a software assumption
- group 47: discard removals unknown; reported catch does not establish complete removals
- group 48: discard removals unknown; reported catch does not establish complete removals
- group 49: discard removals unknown; reported catch does not establish complete removals
- group 50: discard removals unknown; reported catch does not establish complete removals
- group 51: discard removals unknown; reported catch does not establish complete removals

### Warnings

- group 1 (Marine mammals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Coastal birds): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 32 (BA L crustaceans): printed EE 0.88 vs recomputed 0.684 (diff 0.196), BA 0.0 carried (absolute or derived internally from source BA rate)
- group 33 (BA molluscs): printed EE 0.93 vs recomputed 0.864 (diff 0.066), BA 0.0 carried (absolute or derived internally from source BA rate)
- group 34 (BA worms): printed EE 0.90 vs recomputed 0.736 (diff 0.164), BA 0.0 carried (absolute or derived internally from source BA rate)
- group 35 (BA crustaceans): printed EE 0.87 vs recomputed 0.407 (diff 0.463), BA 0.0 carried (absolute or derived internally from source BA rate)
- group 36 (BA other inverts): printed EE 0.93 vs recomputed 0.675 (diff 0.255), BA 0.0 carried (absolute or derived internally from source BA rate)
- group 38 (shelf L crustaceans): printed EE 0.83 vs recomputed 0.553 (diff 0.277), BA 0.0 carried (absolute or derived internally from source BA rate)
- group 39 (shelf molluscs): printed EE 0.51 vs recomputed 0.437 (diff 0.073), BA 0.0 carried (absolute or derived internally from source BA rate)
- group 41 (shelf crustaceans): printed EE 0.83 vs recomputed 0.699 (diff 0.131), BA 0.0 carried (absolute or derived internally from source BA rate)

### Notes

- 40 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Marine mammals), 2 (Coastal birds), 3 (Meagre ad), 4 (Meagre juv), 5 (Mullets), 6 (Pelagic L), 7 (Mackerel), 8 (Sardine) ...
- detritus pools (1): inflow ~6951, consumption ~3701 t/km^2/year, implied EE ~0.533 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Marine mammals | 0.01 | 0.04 | 12.5 | 0 | 0 | 0.0032 | 0 | 0 |
| 2 | Coastal birds | 0.01 | 0.28 | 67 | 0 | 0 | 0.00418 | 0 | 0 |
| 3 | Meagre ad | 0.12 | 0 | 2.1 | 0.66 | - | - | 0.014 | 0 |
| 4 | Meagre juv | 5e-05 | 0 | 17.9 | 0.97 | - | - | 0 | 0 |
| 5 | Mullets | 0.42 | 0.8 | 8.2 | 0.8 | 0.794 | 0.0976 | 0.103 | 0 |
| 6 | Pelagic L | 3.42 | 0.96 | 5.4 | 0.9 | 0.9 | 0.178 | 2.679 | 0 |
| 7 | Mackerel | 1.45 | 0.45 | 3 | 0.74 | 0.735 | 0.15 | 0.289 | 0 |
| 8 | Sardine | 11.79 | 0.65 | 4.3 | 0.77 | 0.771 | 0.151 | 1.801 | 0 |
| 9 | Sardinelles | 18 | 0.99 | 7.7 | 0.78 | 0.785 | 0.129 | 2.31 | 0 |
| 10 | Horse mackerels | 10 | 0.72 | 3.6 | 0.84 | 0.844 | 0.2 | 3.812 | 0 |
| 11 | Coastal selacians | 1.24 | 0.3 | 2 | 0.01 | 0.0147 | 0.15 | 0.063 | -0.062 |
| 12 | Coastal M | 0.83 | 0.58 | 2.9 | 0.86 | 0.86 | 0.2 | 0.121 | 0 |
| 13 | Coastal S | 4.21 | 0.62 | 3.1 | 0.95 | 0.951 | 0.2 | 0 | 0 |
| 14 | Croakers ad | 0.08 | - | 3.9 | 0.75 | - | - | 0.003 | 0 |
| 15 | Croakers juv | 0 | - | 9.9 | 0.71 | - | - | 0 | 0 |
| 16 | Seabreams ad | 1.69 | - | 4.7 | 0.88 | - | - | 0.167 | 0 |
| 17 | Seabreams juv. | 0.01 | - | 21.1 | 0.88 | - | - | 0 | 0 |
| 18 | Catfish ad | 0.6 | - | 4.1 | 0.23 | - | - | 0.034 | 0 |
| 19 | Catfish juv | 0 | - | 22.3 | 0.78 | - | - | 0 | 0 |
| 20 | Shelf selacians | 0.2 | 0.24 | 1.6 | 0.79 | 0.795 | 0.15 | 0.011 | 0 |
| 21 | Shelf L | 0.36 | 0.47 | 3.4 | 0.47 | 0.467 | 0.138 | 0.071 | 0 |
| 22 | Shelf M | 1.55 | 0.57 | 6.2 | 0.91 | 0.913 | 0.0919 | 0.146 | 0 |
| 23 | Groupers ad | 0.11 | - | 3.2 | 0.94 | - | - | 0.025 | -0.0055 |
| 24 | Grouper juv | 0 | - | 16.2 | 0.54 | - | - | 0 | -0 |
| 25 | Sparids ad | 1.29 | - | 2.4 | 0.87 | - | - | 0.014 | 0 |
| 26 | Sparids juv | 0.011 | - | 9.8 | 0.94 | - | - | 0 | 0 |
| 27 | Scianids | 0.22 | 0.29 | 4.3 | 0.67 | 0.653 | 0.0674 | 0.017 | -0.011 |
| 28 | Shelf soles | 0.35 | 0.58 | 2.9 | 0.88 | 0.884 | 0.2 | 0.009 | 0 |
| 29 | Shelf S | 6.19 | 0.82 | 7.6 | 0.95 | 0.952 | 0.108 | 0.005 | 0 |
| 30 | Octopus vulgaris | 1.37 | 1.4 | 4.7 | 0.63 | 0.632 | 0.298 | 0.883 | -0.0411 |
| 31 | Cephalopods | 1 | 1.2 | 4 | 0.84 | 0.84 | 0.3 | 0.255 | -0.03 |
| 32 | BA L crustaceans | 7.66 | 1.44 | 7.2 | 0.88 | 0.684 | 0.2 | 0 | 0 |
| 33 | BA molluscs | 14.01 | 1.5 | 16.7 | 0.93 | 0.864 | 0.0898 | 0 | 0 |
| 34 | BA worms | 4.15 | 3 | 33.3 | 0.9 | 0.736 | 0.0901 | 0 | 0 |
| 35 | BA crustaceans | 1.14 | 2.4 | 12 | 0.87 | 0.407 | 0.2 | 0 | 0 |
| 36 | BA other inverts | 0.57 | 1.8 | 9 | 0.93 | 0.675 | 0.2 | 0 | 0 |
| 37 | BA meiobenthos | 2.09 | 9 | 100 | 0.77 | 0.734 | 0.09 | 0 | 0 |
| 38 | shelf L crustaceans | 8.91 | 1.5 | 7.5 | 0.83 | 0.553 | 0.2 | 0.005 | 0 |
| 39 | shelf molluscs | 26.21 | 1.5 | 16.7 | 0.51 | 0.437 | 0.0898 | 3e-06 | 0 |
| 40 | shelf worms | 31.77 | 3 | 33 | 0.43 | 0.385 | 0.0909 | 0 | 0 |
| 41 | shelf crustaceans | 8.04 | 2.4 | 12 | 0.83 | 0.699 | 0.2 | 0 | 0 |
| 42 | shelf other inverts | 17.21 | 1.8 | 9 | 0.23 | 0.212 | 0.2 | 0 | 0 |
| 43 | shelf meiobenthos | 8.91 | 9 | 100 | 0.27 | 0.252 | 0.09 | 0 | 0 |
| 44 | mesozoopl. | 55.08 | 24 | 112 | 0.15 | 0.145 | 0.214 | 0 | 0 |
| 45 | macrozoopl. | 3.41 | 4.3 | 17 | 0.73 | 0.709 | 0.253 | 0 | 0 |
| 46 | BA mesozoopl. | 1.75 | 24 | 112 | 0.8 | 0.786 | 0.214 | 0 | 0 |
| 47 | BA macrozoopl. | 2.46 | 4.3 | 17 | 0.8 | 0.783 | 0.253 | 0 | 0 |
| 48 | BA phytopl. | 6 | 100 | 0 | 0.38 | 0.375 | - | 0 | 0 |
| 49 | phytoplankton | 68 | 100 | 0 | 0.85 | 0.85 | - | 0 | 0 |
| 50 | algae and eelgrass | 549 | 4.06 | 0 | 0.01 | 0.0069 | - | 0 | 0 |
| 51 | Detritus | 560 | 0 | 0 | 0.45 | - | - | 0 | unknown |
