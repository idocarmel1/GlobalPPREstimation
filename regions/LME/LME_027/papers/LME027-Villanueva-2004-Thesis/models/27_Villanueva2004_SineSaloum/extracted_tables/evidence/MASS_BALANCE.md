## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 27_Canary_Current_Villanueva2004Thesis_Sine_Saloum_(1991-1992), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 1 error(s), 109 indeterminate, 0 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 37 of 37 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 700.488, group 37 (Détritus).

Groups with recomputed EE > 1: 37 (Détritus, 700.598).

P/Q outside 0.02-0.5: none.

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 20 (Epinephelus aeneus) has Q/B=6.992 but no diet entries - its consumption is missing from every prey's budget

### Indeterminate (BA unknown)

- group 20 (Epinephelus aeneus): printed EE 0.850 vs recomputed 0.028 (diff 0.822) with BA unknown - a BA of +0.1174 t/km^2/year (+0.82 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 22 (Pellonula leonensis): printed EE 0.700 vs recomputed 0.472 (diff 0.228) with BA unknown - a BA of +0.1819 t/km^2/year (+0.23 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 30 (Crevettes): printed EE 0.950 vs recomputed 0.866 (diff 0.084) with BA unknown - a BA of +1.083 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 37 (Détritus): recomputed EE = 700.598 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 1: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 1: unassimilated fraction unknown; indicative checks use a software assumption
- group 1: discard removals unknown; reported catch does not establish complete removals
- group 2: diet/import has unknown cells; known subtotal 0.999 is not a complete composition
- group 2: unassimilated fraction unknown; indicative checks use a software assumption
- group 2: discard removals unknown; reported catch does not establish complete removals
- group 3: diet/import has unknown cells; known subtotal 0.97 is not a complete composition
- group 3: unassimilated fraction unknown; indicative checks use a software assumption
- group 3: discard removals unknown; reported catch does not establish complete removals
- group 4: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 4: unassimilated fraction unknown; indicative checks use a software assumption
- group 4: discard removals unknown; reported catch does not establish complete removals
- group 5: diet/import has unknown cells; known subtotal 0.979 is not a complete composition
- group 5: unassimilated fraction unknown; indicative checks use a software assumption
- group 5: discard removals unknown; reported catch does not establish complete removals
- group 6: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 6: unassimilated fraction unknown; indicative checks use a software assumption
- group 6: discard removals unknown; reported catch does not establish complete removals
- group 7: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 7: unassimilated fraction unknown; indicative checks use a software assumption
- group 7: discard removals unknown; reported catch does not establish complete removals
- group 8: diet/import has unknown cells; known subtotal 0.98 is not a complete composition
- group 8: unassimilated fraction unknown; indicative checks use a software assumption
- group 8: discard removals unknown; reported catch does not establish complete removals
- group 9: diet/import has unknown cells; known subtotal 0.99 is not a complete composition
- group 9: unassimilated fraction unknown; indicative checks use a software assumption
- group 9: discard removals unknown; reported catch does not establish complete removals
- group 10: diet/import has unknown cells; known subtotal 0.989 is not a complete composition
- group 10: unassimilated fraction unknown; indicative checks use a software assumption
- group 10: discard removals unknown; reported catch does not establish complete removals
- group 11: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 11: unassimilated fraction unknown; indicative checks use a software assumption
- group 11: discard removals unknown; reported catch does not establish complete removals
- group 12: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 12: unassimilated fraction unknown; indicative checks use a software assumption
- group 12: discard removals unknown; reported catch does not establish complete removals
- group 13: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 13: unassimilated fraction unknown; indicative checks use a software assumption
- group 13: discard removals unknown; reported catch does not establish complete removals
- group 14: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 14: unassimilated fraction unknown; indicative checks use a software assumption
- group 14: discard removals unknown; reported catch does not establish complete removals
- group 15: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 15: unassimilated fraction unknown; indicative checks use a software assumption
- group 15: discard removals unknown; reported catch does not establish complete removals
- group 16: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 16: unassimilated fraction unknown; indicative checks use a software assumption
- group 16: discard removals unknown; reported catch does not establish complete removals
- group 17: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 17: unassimilated fraction unknown; indicative checks use a software assumption
- group 17: discard removals unknown; reported catch does not establish complete removals
- group 18: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 18: unassimilated fraction unknown; indicative checks use a software assumption
- group 18: discard removals unknown; reported catch does not establish complete removals
- group 19: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 19: unassimilated fraction unknown; indicative checks use a software assumption
- group 19: discard removals unknown; reported catch does not establish complete removals
- group 20: diet/import has unknown cells; known subtotal 0 is not a complete composition
- group 20: unassimilated fraction unknown; indicative checks use a software assumption
- group 20: discard removals unknown; reported catch does not establish complete removals
- group 21: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 21: unassimilated fraction unknown; indicative checks use a software assumption
- group 21: discard removals unknown; reported catch does not establish complete removals
- group 22: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 22: unassimilated fraction unknown; indicative checks use a software assumption
- group 22: discard removals unknown; reported catch does not establish complete removals
- group 23: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 23: unassimilated fraction unknown; indicative checks use a software assumption
- group 23: discard removals unknown; reported catch does not establish complete removals
- group 24: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 24: unassimilated fraction unknown; indicative checks use a software assumption
- group 24: discard removals unknown; reported catch does not establish complete removals
- group 25: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 25: unassimilated fraction unknown; indicative checks use a software assumption
- group 25: discard removals unknown; reported catch does not establish complete removals
- group 26: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 26: unassimilated fraction unknown; indicative checks use a software assumption
- group 26: discard removals unknown; reported catch does not establish complete removals
- group 27: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 27: unassimilated fraction unknown; indicative checks use a software assumption
- group 27: discard removals unknown; reported catch does not establish complete removals
- group 28: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 28: unassimilated fraction unknown; indicative checks use a software assumption
- group 28: discard removals unknown; reported catch does not establish complete removals
- group 29: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 29: unassimilated fraction unknown; indicative checks use a software assumption
- group 29: discard removals unknown; reported catch does not establish complete removals
- group 30: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 30: unassimilated fraction unknown; indicative checks use a software assumption
- group 30: discard removals unknown; reported catch does not establish complete removals
- group 31: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 31: unassimilated fraction unknown; indicative checks use a software assumption
- group 31: discard removals unknown; reported catch does not establish complete removals
- group 32: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 32: unassimilated fraction unknown; indicative checks use a software assumption
- group 32: discard removals unknown; reported catch does not establish complete removals
- group 33: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 33: unassimilated fraction unknown; indicative checks use a software assumption
- group 33: discard removals unknown; reported catch does not establish complete removals
- group 34: diet/import has unknown cells; known subtotal 1 is not a complete composition
- group 34: unassimilated fraction unknown; indicative checks use a software assumption
- group 34: discard removals unknown; reported catch does not establish complete removals
- group 35: discard removals unknown; reported catch does not establish complete removals
- group 36: discard removals unknown; reported catch does not establish complete removals
- group 37: discard removals unknown; reported catch does not establish complete removals

### Notes

- 34 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Sphyraena guanchancho), 2 (Scomberomorus tritor), 3 (Polydactylus quadrifilis), 4 (Galeoides decadactylus), 5 (Pseudotolithus elongatus), 6 (Pseudotolithus brachygnathus), 7 (Elops lacerta), 8 (Arius latiscutatus) ...
- detritus pools (1): inflow ~1.003e+04, consumption ~1191 t/km^2/year, implied EE ~0.119 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Sphyraena guanchancho | 0.03 | 1.7 | 8.645 | 0.671 | 0.671 | 0.197 | 0.034 | unknown |
| 2 | Scomberomorus tritor | 0.049 | 0.65 | 6.821 | 0.495 | 0.495 | 0.0953 | 0.015 | unknown |
| 3 | Polydactylus quadrifilis | 0.026 | 1.54 | 9.272 | 0.099 | 0.099 | 0.166 | 0.002 | unknown |
| 4 | Galeoides decadactylus | 0.363 | 3.28 | 16.82 | 0.402 | 0.401 | 0.195 | 0.461 | unknown |
| 5 | Pseudotolithus elongatus | 0.241 | 0.75 | 6.944 | 0.423 | 0.423 | 0.108 | 0.075 | unknown |
| 6 | Pseudotolithus brachygnathus | 0.092 | 1.28 | 7.294 | 0.511 | 0.511 | 0.175 | 0.057 | unknown |
| 7 | Elops lacerta | 0.056 | 1.82 | 13.88 | 0.5 | 0.5 | 0.131 | 0.048 | unknown |
| 8 | Arius latiscutatus | 0.09 | 2.655 | 7.53 | 0.871 | 0.871 | 0.353 | 0.201 | unknown |
| 9 | Pomadasys jubelini | 0.174 | 1.35 | 12.06 | 0.806 | 0.806 | 0.112 | 0.171 | unknown |
| 10 | Chloroscombrus chrysurus | 0.154 | 2.49 | 19.7 | 0.507 | 0.507 | 0.126 | 0.194 | unknown |
| 11 | Caranx hippos | 0.019 | 1.585 | 16.97 | 0.134 | 0.134 | 0.0934 | 0.002 | unknown |
| 12 | Trachinotus teraia | 0.045 | 0.611 | 8.445 | 0.205 | 0.204 | 0.0724 | 0 | unknown |
| 13 | Citarichthys stampflii | 0.029 | 1.649 | 14.28 | 0.5 | 0.51 | 0.115 | 0.017 | unknown |
| 14 | Cynoglossus senegalensis | 0.039 | 1.21 | 10.35 | 0.7 | 0.703 | 0.117 | 0.017 | unknown |
| 15 | Eucinostomus melanopterus | 0.098 | 1.59 | 12.88 | 0.966 | 0.964 | 0.123 | 0.067 | unknown |
| 16 | Drepane africana | 0.143 | 1.68 | 9.291 | 0.319 | 0.319 | 0.181 | 0.073 | unknown |
| 17 | Dasyatis margarita | 0.069 | 0.733 | 4.613 | 0.215 | 0.214 | 0.159 | 0.007 | unknown |
| 18 | Ilisha africana | 0.426 | 1.51 | 16.06 | 0.581 | 0.562 | 0.094 | 0.221 | unknown |
| 19 | Brachydeuterus auritus | 0.188 | 4.68 | 20.51 | 0.738 | 0.724 | 0.228 | 0.577 | unknown |
| 20 | Epinephelus aeneus | 0.191 | 0.748 | 6.992 | 0.85 | 0.028 | 0.107 | 0.004 | unknown |
| 21 | Hemiramphus brasiliensis | 0.035 | 1.117 | 13.25 | 0.173 | 0.173 | 0.0843 | 0.005 | unknown |
| 22 | Pellonula leonensis | 0.259 | 3.08 | 28.99 | 0.7 | 0.472 | 0.106 | 0 | unknown |
| 23 | Trichiurus lepturus | 0.027 | 0.42 | 4.163 | 0.291 | 0.291 | 0.101 | 0.002 | unknown |
| 24 | Monodactylus sebae | 0.024 | 1.91 | 16.72 | 0.54 | 0.536 | 0.114 | 0.007 | unknown |
| 25 | Ethmalosa fimbriata | 0.63 | 2.51 | 13.97 | 0.997 | 0.997 | 0.18 | 0.922 | unknown |
| 26 | Sardinella maderensis | 2.413 | 3.05 | 18.98 | 0.658 | 0.658 | 0.161 | 4.549 | unknown |
| 27 | Liza grandisquamis | 0.426 | 1.08 | 11.46 | 0.423 | 0.421 | 0.0942 | 0.092 | unknown |
| 28 | Sarotherodon melanotheron | 2.719 | 2.48 | 32.47 | 0.499 | 0.494 | 0.0764 | 3.086 | unknown |
| 29 | Tilapia guineensis | 0.073 | 2.4 | 35.26 | 0.841 | 0.841 | 0.0681 | 0.101 | unknown |
| 30 | Crevettes | 2.815 | 4.605 | 22 | 0.95 | 0.866 | 0.209 | 1.05 | unknown |
| 31 | Crabes | 1.858 | 2.5 | 8.5 | 0.8 | 0.803 | 0.294 | 0 | unknown |
| 32 | Macrobenthos | 93 | 1.2 | 10 | 0.226 | 0.221 | 0.12 | 0 | unknown |
| 33 | Meiobenthos | 19.6 | 4 | 50 | 0.315 | 0.314 | 0.08 | 0 | unknown |
| 34 | Zooplancton | 20.64 | 50 | 150 | 0.307 | 0.307 | 0.333 | 0 | unknown |
| 35 | Phytoplancton | 82 | 138.2 | - | 0.286 | 0.286 | - | 0 | unknown |
| 36 | Phytobenthos | 32.16 | 15 | - | 0.95 | 0.955 | - | 0 | unknown |
| 37 | Détritus | 1 | 1.7 | - | 0.11 | 701 | - | 0 | unknown |
