## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 26_2602022_Mediterranean_Piroddi_(1995), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 7 indeterminate, 10 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 71 of 71 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 1.478, group 4 (Fin whale).

Groups with recomputed EE > 1: 4 (Fin whale, 1.478).

P/Q outside 0.02-0.5: 1 (Bottlenose dolphin, 0.003), 2 (Striped dolphin, 0.002), 3 (Common dolphin, 0.002), 4 (Fin whale, 0.003), 5 (Sperm whale, 0.006), 6 (Deep Sea cetaceans, 0.005), 7 (Monk seal, 0.003), 8 (Pelagic Seabird, 0.003), 9 (Gull&Cormorant, 0.002), 10 (Tern, 0.002).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 1 (Bottlenose dolphin): printed EE 0.05 vs recomputed 0.201 (diff 0.151) with BA unknown - a BA of -2.251e-05 t/km^2/year (-0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 2 (Striped dolphin): printed EE 0.65 vs recomputed 0.499 (diff 0.151) with BA unknown - a BA of +3.303e-05 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 3 (Common dolphin): printed EE 0.01 vs recomputed 0.852 (diff 0.842) with BA unknown - a BA of -1.681e-05 t/km^2/year (-0.84 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 4 (Fin whale): recomputed EE = 1.478 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 11 (Loggerhead turtle): printed EE 0.95 vs recomputed 0.675 (diff 0.275) with BA unknown - a BA of +0.0001332 t/km^2/year (+0.27 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 12 (Green turtle): printed EE 0.99 vs recomputed 0.641 (diff 0.349) with BA unknown - a BA of +1.852e-05 t/km^2/year (+0.35 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 15 (Bluefin tuna): printed EE 0.408032 vs recomputed 0.335 (diff 0.073) with BA unknown - a BA of +0.00508 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 1 (Bottlenose dolphin): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Striped dolphin): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Common dolphin): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Fin whale): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 5 (Sperm whale): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 6 (Deep Sea cetaceans): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 7 (Monk seal): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 8 (Pelagic Seabird): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 9 (Gull&Cormorant): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 10 (Tern): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 65 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Bottlenose dolphin), 2 (Striped dolphin), 3 (Common dolphin), 4 (Fin whale), 5 (Sperm whale), 6 (Deep Sea cetaceans), 7 (Monk seal), 8 (Pelagic Seabird) ...
- detritus pools (2): inflow ~754.9, consumption ~30.21 t/km^2/year, implied EE ~0.040 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Bottlenose dolphin | 0.002223 | 0.06717 | 22.5 | 0.05 | 0.201 | 0.00299 | 2.997e-05 | unknown |
| 2 | Striped dolphin | 0.003356 | 0.065 | 35.99 | 0.65 | 0.499 | 0.00181 | 9.93e-05 | unknown |
| 3 | Common dolphin | 0.0004435 | 0.045 | 29.24 | 0.01 | 0.852 | 0.00154 | 1.334e-05 | unknown |
| 4 | Fin whale | 0.008638 | 0.022 | 7.25 | 1e-05 | 1.48 | 0.00303 | 0.0002808 | unknown |
| 5 | Sperm whale | 0.002594 | 0.05038 | 8.15 | 0.3226 | 0.323 | 0.00618 | 4.216e-05 | unknown |
| 6 | Deep Sea cetaceans | 0.003947 | 0.07472 | 16.56 | 0.4014 | 0.401 | 0.00451 | 0.0001184 | unknown |
| 7 | Monk seal | 2.352e-05 | 0.0816 | 27.32 | 0.5765 | 0.577 | 0.00299 | 1.107e-06 | unknown |
| 8 | Pelagic Seabird | 0.0001092 | 0.3946 | 114.6 | 0.5862 | 0.586 | 0.00344 | 2.143e-05 | unknown |
| 9 | Gull&Cormorant | 0.0003035 | 0.3072 | 158.2 | 0.1998 | 0.2 | 0.00194 | 1.068e-05 | unknown |
| 10 | Tern | 7.766e-06 | 0.2843 | 141.8 | 0.3282 | 0.328 | 0.00201 | 0 | unknown |
| 11 | Loggerhead turtle | 0.001797 | 0.27 | 2.517 | 0.95 | 0.675 | 0.107 | 0.0003276 | unknown |
| 12 | Green turtle | 0.0002655 | 0.2 | 9.839 | 0.99 | 0.641 | 0.0203 | 3.405e-05 | unknown |
| 13 | Pelagic shark | 0.08163 | 0.0976 | 1.379 | 0.01942 | 0.0194 | 0.0708 | 0.0001547 | unknown |
| 14 | NC large pelagic | 0.0879 | 0.1124 | 1.232 | 0.989 | 0.989 | 0.0912 | 6.867e-05 | unknown |
| 15 | Bluefin tuna | 0.1016 | 0.6882 | 3.12 | 0.408 | 0.335 | 0.221 | 0.009772 | unknown |
| 16 | Swordfish | 0.01282 | 0.6038 | 3.978 | 0.9606 | 0.961 | 0.152 | 0.006007 | unknown |
| 17 | O large pelagic f. | 0.01524 | 0.75 | 2.619 | 0.8514 | 0.851 | 0.286 | 0.00391 | unknown |
| 18 | Mackerel | 0.09972 | 0.84 | 3.918 | 0.6492 | 0.649 | 0.214 | 0.02084 | unknown |
| 19 | Horse mackerel | 0.1355 | 0.99 | 4.174 | 0.8564 | 0.856 | 0.237 | 0.01748 | unknown |
| 20 | O medium pelagic f. | 0.0884 | 0.662 | 4.8 | 0.9074 | 0.907 | 0.138 | 0.01743 | unknown |
| 21 | E. sardine Adult | 0.6621 | 1.287 | 8.902 | 0.7468 | 0.747 | 0.145 | 0.09268 | unknown |
| 22 | E. sardine Recruit | 0.05792 | 1.483 | 23.01 | 0.2937 | 0.294 | 0.0644 | 0.005894 | unknown |
| 23 | E. anchovy Adult | 0.3596 | 1.04 | 10.74 | 0.8367 | 0.837 | 0.0969 | 0.02581 | unknown |
| 24 | E. Anchovy Recruit | 0.01552 | 1.339 | 30.94 | 0.8564 | 0.856 | 0.0433 | 0.003238 | unknown |
| 25 | O small pelagic f. | 0.2659 | 1.2 | 8.388 | 0.9264 | 0.926 | 0.143 | 0.03199 | unknown |
| 26 | Benthopelagic f. | 0.1853 | 0.6391 | 4.988 | 0.9237 | 0.924 | 0.128 | 0.00959 | unknown |
| 27 | Mesopelagic f. | 3.2 | 0.6 | 6.25 | 0.8536 | 0.854 | 0.096 | 0.002674 | unknown |
| 28 | Anglerfish | 0.02226 | 0.2293 | 2.87 | 0.7212 | 0.721 | 0.0799 | 0.002839 | unknown |
| 29 | E. Hake Adult | 0.1293 | 1.079 | 4.097 | 0.6176 | 0.618 | 0.263 | 0.01844 | unknown |
| 30 | E. Hake Recruit | 0.05065 | 1.234 | 9.241 | 0.3233 | 0.323 | 0.134 | 0.001689 | unknown |
| 31 | OC large demersal f. | 0.02793 | 0.6633 | 2.334 | 0.9561 | 0.956 | 0.284 | 0.004512 | unknown |
| 32 | Gadidae | 0.1091 | 0.7193 | 3.152 | 0.8679 | 0.868 | 0.228 | 0.009635 | unknown |
| 33 | Sparidae | 0.1795 | 0.7597 | 5.714 | 0.9805 | 0.98 | 0.133 | 0.04153 | unknown |
| 34 | OC medium demersal f. | 0.08834 | 0.8276 | 4.1 | 0.9564 | 0.956 | 0.202 | 0.0257 | unknown |
| 35 | Flatfish | 0.08097 | 0.7953 | 4.844 | 0.9289 | 0.929 | 0.164 | 0.005771 | unknown |
| 36 | NC medium demersal f. | 0.1199 | 0.6917 | 4.077 | 0.8484 | 0.848 | 0.17 | 0.0002087 | unknown |
| 37 | Red mullet Adult | 0.2678 | 1.205 | 8 | 0.8652 | 0.865 | 0.151 | 0.008598 | unknown |
| 38 | Red mullet Recruit | 0.02574 | 1.03 | 19.03 | 0.8415 | 0.842 | 0.0541 | 0.0003566 | unknown |
| 39 | Surmullet | 0.09816 | 0.9155 | 8.005 | 0.953 | 0.953 | 0.114 | 0.006104 | unknown |
| 40 | OC small demersal f. | 0.1802 | 0.9278 | 6.326 | 0.9623 | 0.962 | 0.147 | 0.01025 | unknown |
| 41 | NC small demersal f. | 0.386 | 0.895 | 5 | 0.9888 | 0.989 | 0.179 | 0.001168 | unknown |
| 42 | Bathydemersal f. | 0.09962 | 0.5994 | 6.687 | 0.7156 | 0.716 | 0.0896 | 0.0006806 | unknown |
| 43 | Small-spotted catshark | 0.008862 | 0.3955 | 4.188 | 0.37 | 0.37 | 0.0944 | 0.0002993 | unknown |
| 44 | Blackmouth catshark | 0.006461 | 0.3298 | 3.925 | 0.9401 | 0.94 | 0.084 | 0.0003249 | unknown |
| 45 | O small demersal shark | 0.0574 | 0.2178 | 2.637 | 0.654 | 0.654 | 0.0826 | 0.005548 | unknown |
| 46 | Ray&Skate | 0.07434 | 0.1585 | 3.227 | 0.8816 | 0.882 | 0.0491 | 0.002503 | unknown |
| 47 | Torpedo | 0.05084 | 0.1847 | 3.099 | 0.585 | 0.585 | 0.0596 | 0.0003623 | unknown |
| 48 | Benthic cephalopod | 0.06199 | 1.949 | 6.8 | 0.901 | 0.901 | 0.287 | 0.02509 | unknown |
| 49 | Benthopelagic cephalopod | 0.07791 | 1.923 | 6.8 | 0.861 | 0.861 | 0.283 | 0.005917 | unknown |
| 50 | Mesopelagic cephalopod | 0.061 | 1.999 | 6.7 | 0.9575 | 0.957 | 0.298 | 0.004169 | unknown |
| 51 | Bivalve | 0.72 | 1.8 | 6 | 0.9902 | 0.99 | 0.3 | 0.02846 | unknown |
| 52 | Gastropod | 0.69 | 1.917 | 6.5 | 0.7802 | 0.78 | 0.295 | 0.003417 | unknown |
| 53 | Deep-water rose shrimp | 0.02 | 2.768 | 23 | 0.4165 | 0.416 | 0.12 | 0.006054 | unknown |
| 54 | Blue and red shrimp | 0.00767 | 1.911 | 23 | 0.5032 | 0.503 | 0.0831 | 0.001838 | unknown |
| 55 | Giant red shrimp | 0.002473 | 1.816 | 23 | 0.5339 | 0.534 | 0.0789 | 0.0007316 | unknown |
| 56 | Commercial prawn | 0.003526 | 1.959 | 23 | 0.8526 | 0.853 | 0.0852 | 0.002457 | unknown |
| 57 | NC shrimp/prawn | 0.599 | 3.675 | 25.94 | 0.8726 | 0.873 | 0.142 | 0.000462 | unknown |
| 58 | Norway lobster | 0.008127 | 1.1 | 8.483 | 0.8822 | 0.882 | 0.13 | 0.00756 | unknown |
| 59 | OC decapod | 0.01487 | 2.078 | 11.36 | 0.7431 | 0.743 | 0.183 | 0.005338 | unknown |
| 60 | NC decapod | 0.44 | 2.38 | 8 | 0.9831 | 0.983 | 0.297 | 0.009229 | unknown |
| 61 | Mobile benthos | 1.3 | 3 | 10 | 0.7862 | 0.786 | 0.3 | 0.00695 | unknown |
| 62 | Sessile benthos | 0.395 | 2.789 | 12.44 | 0.7622 | 0.762 | 0.224 | 7.127e-05 | unknown |
| 63 | Jellyfish&Salp | 0.35 | 3.55 | 16 | 0.5546 | 0.555 | 0.222 | 2.753e-06 | unknown |
| 64 | Coral&Gorgonian | 0.3541 | 0.24 | 1.15 | 0.9726 | 0.973 | 0.209 | 1.006e-05 | unknown |
| 65 | Zooplankton | 7.728 | 22 | 75 | 0.688 | 0.688 | 0.293 | 0 | unknown |
| 66 | Seagrass | 0.4419 | 2.583 | - | 0.1093 | 0.109 | - | 0.001115 | unknown |
| 67 | Seaweed | 0.3486 | 1.55 | - | 0.8642 | 0.864 | - | 1.71e-06 | unknown |
| 68 | Small Phytoplankton | 28.87 | 26.39 | - | 0.3402 | 0.34 | - | 0 | unknown |
| 69 | Large Phytoplankton | 8.246 | 38.65 | - | 0.8176 | 0.818 | - | 0 | unknown |
| 70 | Discards | 0.07582 | - | - | 0.4894 | - | - | 0 | unknown |
| 71 | Detritus | 0.44 | - | - | 0.03464 | - | - | 0 | unknown |
