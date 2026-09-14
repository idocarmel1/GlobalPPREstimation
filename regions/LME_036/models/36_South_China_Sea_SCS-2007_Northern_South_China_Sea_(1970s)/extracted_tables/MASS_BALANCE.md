## Mass balance

Checked by the source-preserving local copy of `database_json.py` on the assembled JSON for 36_South_China_Sea_SCS-2007_Northern_South_China_Sea_(1970s), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 17 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 38 of 38 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 4.770, group 37 (Marine turtles).

Groups with recomputed EE > 1: 37 (Marine turtles, 5.273).

P/Q outside 0.02-0.5: 34 (Seabirds, 0.001), 35 (Pinnipeds, 0.003), 36 (Other mammals, 0.011).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is an assumption for this diagnostic calculation; negative or positive unreported BA would change it in either direction.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 4 (Jellyfish): printed EE 0.95 vs recomputed 0.871 (diff 0.079) with BA unknown - a BA of +0.05764 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 10 (Shrimps): printed EE 0.95 vs recomputed 0.885 (diff 0.065) with BA unknown - a BA of +0.1483 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 11 (Crabs): printed EE 0.95 vs recomputed 0.606 (diff 0.344) with BA unknown - a BA of +0.7536 t/km^2/year (+0.34 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 13 (Threadfin bream (nemipterids)): printed EE 0.469 vs recomputed 0.298 (diff 0.171) with BA unknown - a BA of +0.1319 t/km^2/year (+0.17 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 14 (Bigeyes (priacanthids)): printed EE 0.328 vs recomputed 0.394 (diff 0.066) with BA unknown - a BA of -0.02535 t/km^2/year (-0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 19 (Snappers): printed EE 0.95 vs recomputed 0.412 (diff 0.538) with BA unknown - a BA of +0.01009 t/km^2/year (+0.54 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 21 (Croakers (≤ 30 cm)): printed EE 0.784 vs recomputed 0.571 (diff 0.213) with BA unknown - a BA of +0.1449 t/km^2/year (+0.21 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 22 (Juvenile large croakers): printed EE 0.913 vs recomputed 0.333 (diff 0.580) with BA unknown - a BA of +0.05817 t/km^2/year (+0.58 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Croakers (> 30 cm)): printed EE 0.541 vs recomputed 0.338 (diff 0.203) with BA unknown - a BA of +0.02764 t/km^2/year (+0.20 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 24 (Demesral fish (≤ 30 cm)): printed EE 0.95 vs recomputed 0.886 (diff 0.064) with BA unknown - a BA of +0.2655 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 25 (Juvenile demersal fish (> 30 cm)): printed EE 0.599 vs recomputed 0.665 (diff 0.066) with BA unknown - a BA of -0.01923 t/km^2/year (-0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 26 (Adult demersal fish (> 30 cm)): printed EE 0.355 vs recomputed 0.424 (diff 0.069) with BA unknown - a BA of -0.01941 t/km^2/year (-0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 27 (Benthopelagic fish): printed EE 0.95 vs recomputed 0.866 (diff 0.084) with BA unknown - a BA of +0.118 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 28 (Melon seed): printed EE 0.964 vs recomputed 0.808 (diff 0.156) with BA unknown - a BA of +0.03977 t/km^2/year (+0.16 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 30 (Juvenile large pelagic fish): printed EE 0.62 vs recomputed 0.115 (diff 0.505) with BA unknown - a BA of +0.1711 t/km^2/year (+0.51 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 35 (Pinnipeds): printed EE 0.679 vs recomputed 0.993 (diff 0.314) with BA unknown - a BA of -6.491e-05 t/km^2/year (-0.31 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 37 (Marine turtles): recomputed EE = 5.273 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation

### Warnings

- group 34 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 35 (Pinnipeds): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 36 (Other mammals): P/Q = 0.011 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 35 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Zooplankton), 4 (Jellyfish), 5 (Polychaetes), 6 (Echinoderms), 7 (Benthic crustaceans), 8 (Non-ceph molluscs), 9 (Sessile/other invertebrates), 10 (Shrimps) ...
- detritus pools (1): inflow ~1.286e+05, consumption ~2150 t/km^2/year, implied EE ~0.017 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 323 | 399 | - | 0.035 | 0.0354 | - | 0 | unknown |
| 2 | Benthic producer | 153 | 11.89 | - | 0.02 | 0.0201 | - | 0.0056 | unknown |
| 3 | Zooplankton | 33.8 | 32 | 192 | 0.052 | 0.055 | 0.167 | 0.01 | unknown |
| 4 | Jellyfish | 0.146 | 5 | 20 | 0.95 | 0.871 | 0.25 | 0.0012 | unknown |
| 5 | Polychaetes | 3.421 | 6.75 | 22.5 | 0.95 | 0.952 | 0.3 | 0 | unknown |
| 6 | Echinoderms | 3.065 | 1.2 | 3.58 | 0.398 | 0.408 | 0.335 | 0.0039 | unknown |
| 7 | Benthic crustaceans | 2.649 | 5.65 | 26.9 | 0.624 | 0.621 | 0.21 | 0.0019 | unknown |
| 8 | Non-ceph molluscs | 13.75 | 3 | 7 | 0.383 | 0.368 | 0.429 | 0.0056 | unknown |
| 9 | Sessile/other invertebrates | 3.114 | 1 | 9 | 0.845 | 0.847 | 0.111 | 0.0011 | unknown |
| 10 | Shrimps | 0.422 | 5.4 | 28.9 | 0.95 | 0.885 | 0.187 | 0.035 | unknown |
| 11 | Crabs | 0.731 | 3 | 12 | 0.95 | 0.606 | 0.25 | 0.01 | unknown |
| 12 | Cephalopods | 0.465 | 3.1 | 8 | 0.5 | 0.528 | 0.388 | 0.0244 | unknown |
| 13 | Threadfin bream (nemipterids) | 1.04 | 0.74 | 8.1 | 0.469 | 0.298 | 0.0914 | 0.044 | unknown |
| 14 | Bigeyes (priacanthids) | 0.318 | 1.21 | 11.3 | 0.328 | 0.394 | 0.107 | 0.035 | unknown |
| 15 | Lizard fish (synodontids) | 0.3 | 2.3 | 5.41 | 0.241 | 0.238 | 0.425 | 0.084 | unknown |
| 16 | Juvenile Hairtail (trichiurids) | 0.034 | 2.3 | 13.41 | 0.329 | 0.329 | 0.172 | 0.0038 | unknown |
| 17 | Adult hairtail (trichiurids) | 0.0426 | 1.5 | 6.21 | 0.327 | 0.327 | 0.242 | 0.0152 | unknown |
| 18 | Pomfret (stromateids) | 0.065 | 1.3 | 6.38 | 0.95 | 0.966 | 0.204 | 0.0053 | unknown |
| 19 | Snappers | 0.014 | 1.34 | 8.98 | 0.95 | 0.412 | 0.149 | 0.0053 | unknown |
| 20 | Adult groupers | 0.04 | 0.85 | 6.1 | 0.375 | 0.423 | 0.139 | 0.0029 | unknown |
| 21 | Croakers (≤ 30 cm) | 0.289 | 2.36 | 11.28 | 0.784 | 0.571 | 0.209 | 0.016 | unknown |
| 22 | Juvenile large croakers | 0.0425 | 2.36 | 15.65 | 0.913 | 0.333 | 0.151 | 0.011 | unknown |
| 23 | Croakers (> 30 cm) | 0.095 | 1.43 | 6.23 | 0.541 | 0.338 | 0.23 | 0.044 | unknown |
| 24 | Demesral fish (≤ 30 cm) | 1.541 | 2.7 | 13.03 | 0.95 | 0.886 | 0.207 | 0.0902 | unknown |
| 25 | Juvenile demersal fish (> 30 cm) | 0.112 | 2.6 | 15.46 | 0.599 | 0.665 | 0.168 | 0.0288 | unknown |
| 26 | Adult demersal fish (> 30 cm) | 0.195 | 1.44 | 6.21 | 0.355 | 0.424 | 0.232 | 0.115 | unknown |
| 27 | Benthopelagic fish | 0.47 | 3 | 15 | 0.95 | 0.866 | 0.2 | 0.0303 | unknown |
| 28 | Melon seed | 0.114 | 2.24 | 24.7 | 0.964 | 0.808 | 0.0907 | 0.0057 | unknown |
| 29 | Pelagic fish (≤ 30 cm) | 1.05 | 2.87 | 12.22 | 0.95 | 0.975 | 0.235 | 0.146 | unknown |
| 30 | Juvenile large pelagic fish | 0.118 | 2.87 | 14.37 | 0.62 | 0.115 | 0.2 | 0.0096 | unknown |
| 31 | Pelagic fish (> 30 cm) | 0.158 | 0.9 | 6.28 | 0.283 | 0.282 | 0.143 | 0.038 | unknown |
| 32 | Demersal sharks and rays | 0.04 | 1.26 | 6.3 | 0.364 | 0.364 | 0.2 | 0.0158 | unknown |
| 33 | Pelagic sharks and rays | 0.028 | 0.39 | 1.95 | 0.5 | 0.512 | 0.2 | 0.0051 | unknown |
| 34 | Seabirds | 0.0022 | 0.06 | 67.76 | 0.005 | 0.0414 | 0.000885 | 0 | unknown |
| 35 | Pinnipeds | 0.0046 | 0.045 | 14.77 | 0.679 | 0.993 | 0.00305 | 0.0002 | unknown |
| 36 | Other mammals | 0.0158 | 0.112 | 10.52 | 0.068 | 0.0596 | 0.0106 | 0.0001 | unknown |
| 37 | Marine turtles | 0.0002 | 0.1 | 3.5 | 0.503 | 5.27 | 0.0286 | 0.0001 | unknown |
| 38 | Detritus | 100 | - | - | 0.017 | - | - | 0 | unknown |
