## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 52_Sea_of_Okhotsk_GM2019-Fig9-balanced_Sea_of_Okhotsk_pelagic_balanced_assumption_reconstruction_(2000-2014), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 20 indeterminate, 8 warning(s), 1 note(s).

Biomass accumulation is unknown (-9999) for 1 of 22 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: no group has both a printed EE and enough inputs to recompute one.

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 4 (Copepods, 0.641), 5 (Euphausiids, 0.638), 7 (Chaetognaths, 0.553), 8 (Salmon, 0.778), 14 (Jellyfish, 0.614), 18 (Baleen whales, 0.005), 21 (Predatory mammals, 0.010).

BA: carried for 21 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Phytoplankton, +0), 2 (Bacteria, +0), 3 (Protozoa, +0), 4 (Copepods, +0), 5 (Euphausiids, +0), 6 (Hyperiids, +0), 7 (Chaetognaths, +0), 8 (Salmon, +0), 9 (Squid III, +0), 10 (Herring, +0), 11 (Deep-sea smelt, +0), 12 (Pollock less than 30 cm, +0), 13 (Capelin, +0), 14 (Jellyfish, +0), 15 (Pollock 30-60 cm, +0), 16 (Squid IV, +0), 17 (Predatory salmon, +0), 18 (Baleen whales, +0), 19 (Pollock greater than 60 cm, +0), 20 (Predatory fish, +0), 21 (Predatory mammals, +0). The remaining 1 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 2: unassimilated fraction unknown; indicative checks use a software assumption
- group 3: unassimilated fraction unknown; indicative checks use a software assumption
- group 4: unassimilated fraction unknown; indicative checks use a software assumption
- group 5: unassimilated fraction unknown; indicative checks use a software assumption
- group 6: unassimilated fraction unknown; indicative checks use a software assumption
- group 7: unassimilated fraction unknown; indicative checks use a software assumption
- group 8: unassimilated fraction unknown; indicative checks use a software assumption
- group 9: unassimilated fraction unknown; indicative checks use a software assumption
- group 10: unassimilated fraction unknown; indicative checks use a software assumption
- group 11: unassimilated fraction unknown; indicative checks use a software assumption
- group 12: unassimilated fraction unknown; indicative checks use a software assumption
- group 13: unassimilated fraction unknown; indicative checks use a software assumption
- group 14: unassimilated fraction unknown; indicative checks use a software assumption
- group 15: unassimilated fraction unknown; indicative checks use a software assumption
- group 16: unassimilated fraction unknown; indicative checks use a software assumption
- group 17: unassimilated fraction unknown; indicative checks use a software assumption
- group 18: unassimilated fraction unknown; indicative checks use a software assumption
- group 19: unassimilated fraction unknown; indicative checks use a software assumption
- group 20: unassimilated fraction unknown; indicative checks use a software assumption
- group 21: unassimilated fraction unknown; indicative checks use a software assumption

### Warnings

- group 1 (Phytoplankton): only 2 of B/P-B/Q-B/EE given (B, P/B) - Ecopath needs three
- group 4 (Copepods): P/Q = 0.641 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 5 (Euphausiids): P/Q = 0.638 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 7 (Chaetognaths): P/Q = 0.553 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 8 (Salmon): P/Q = 0.778 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 14 (Jellyfish): P/Q = 0.614 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 18 (Baleen whales): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 21 (Predatory mammals): P/Q = 0.010 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- detritus pools (1): inflow ~490.5, consumption ~200.8 t/km^2/year, implied EE ~0.409 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 2.047 | 219.9 | - | - | 0.353 | - | 0 | 0 |
| 2 | Bacteria | 3.274 | 20 | 61.33 | - | 0.943 | 0.326 | 0 | 0 |
| 3 | Protozoa | 1.137 | 20 | 61.54 | - | 0.933 | 0.325 | 0 | 0 |
| 4 | Copepods | 5.01 | 15.15 | 23.64 | - | 0.226 | 0.641 | 0 | 0 |
| 5 | Euphausiids | 3.587 | 10.13 | 15.89 | - | 0.184 | 0.638 | 0 | 0 |
| 6 | Hyperiids | 0.2635 | 11.68 | 23.86 | - | 0.163 | 0.489 | 0 | 0 |
| 7 | Chaetognaths | 1.383 | 5.986 | 10.83 | - | 0.155 | 0.553 | 0 | 0 |
| 8 | Salmon | 0.06319 | 1.076 | 1.383 | - | 0.31 | 0.778 | 0 | 0 |
| 9 | Squid III | 0.02721 | 2.499 | 45.97 | - | 0.707 | 0.0544 | 0 | 0 |
| 10 | Herring | 0.2249 | 0.3427 | 8.731 | - | 0.537 | 0.0393 | 0 | 0 |
| 11 | Deep-sea smelt | 0.134 | 0.29 | 4.087 | - | 0.667 | 0.071 | 0 | 0 |
| 12 | Pollock less than 30 cm | 0.0508 | 2.512 | 16.65 | - | 0.0797 | 0.151 | 0 | 0 |
| 13 | Capelin | 0.05888 | 0.33 | 14.45 | - | 0.911 | 0.0228 | 0 | 0 |
| 14 | Jellyfish | 0.009311 | 10.02 | 16.31 | - | 0.232 | 0.614 | 0 | 0 |
| 15 | Pollock 30-60 cm | 0.4967 | 0.7694 | 5.934 | - | 0.186 | 0.13 | 0 | 0 |
| 16 | Squid IV | 0.02712 | 2.388 | 24.71 | - | 0.61 | 0.0966 | 0 | 0 |
| 17 | Predatory salmon | 0.00158 | 0.82 | 13.12 | - | 0 | 0.0625 | 0 | 0 |
| 18 | Baleen whales | 0.086 | 0.007531 | 1.613 | - | 0 | 0.00467 | 0 | 0 |
| 19 | Pollock greater than 60 cm | 0.02915 | 0.2 | 1.552 | - | 0.633 | 0.129 | 0 | 0 |
| 20 | Predatory fish | 0.01431 | 0.181 | 5.398 | - | 0 | 0.0335 | 0 | 0 |
| 21 | Predatory mammals | 0.0291 | 0.02225 | 2.319 | - | 0 | 0.0096 | 0 | 0 |
| 22 | Detritus | 10.04 | - | - | - | - | - | 0 | unknown |
