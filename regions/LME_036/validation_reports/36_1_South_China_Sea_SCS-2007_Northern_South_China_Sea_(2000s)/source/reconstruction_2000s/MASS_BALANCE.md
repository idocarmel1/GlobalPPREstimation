## Mass balance

Checked by the source-preserving local copy of `database_json.py` on the assembled JSON for 36_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 7 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 38 of 38 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.288, group 35 (Pinnipeds).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 34 (Seabirds, 0.001), 35 (Pinnipeds, 0.003), 36 (Other mammals, 0.011).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is an assumption for this diagnostic calculation; negative or positive unreported BA would change it in either direction.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 4 (Jellyfish): printed EE 0.52 vs recomputed 0.440 (diff 0.080) with BA unknown - a BA of +0.6156 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 15 (Lizard fish (synodontids)): printed EE 0.658 vs recomputed 0.780 (diff 0.122) with BA unknown - a BA of -0.006243 t/km^2/year (-0.12 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Croakers (> 30 cm)): printed EE 0.587 vs recomputed 0.665 (diff 0.078) with BA unknown - a BA of -0.001043 t/km^2/year (-0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 25 (Juvenile demersal fish (> 30 cm)): printed EE 0.722 vs recomputed 0.780 (diff 0.058) with BA unknown - a BA of -0.02928 t/km^2/year (-0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 26 (Adult demersal fish (> 30 cm)): printed EE 0.747 vs recomputed 0.832 (diff 0.085) with BA unknown - a BA of -0.003729 t/km^2/year (-0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 35 (Pinnipeds): printed EE 0.29 vs recomputed 0.002 (diff 0.288) with BA unknown - a BA of +5.966e-05 t/km^2/year (+0.29 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 37 (Marine turtles): printed EE 0.3 vs recomputed 0.019 (diff 0.281) with BA unknown - a BA of +5.626e-06 t/km^2/year (+0.28 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 34 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 35 (Pinnipeds): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 36 (Other mammals): P/Q = 0.011 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 35 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Zooplankton), 4 (Jellyfish), 5 (Polychaetes), 6 (Echinoderms), 7 (Benthic crustaceans), 8 (Non-ceph molluscs), 9 (Sessile/other invertebrates), 10 (Shrimps) ...
- detritus pools (1): inflow ~1.297e+05, consumption ~627.6 t/km^2/year, implied EE ~0.005 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 323 | 398 | - | 0.01 | 0.00952 | - | 0 | unknown |
| 2 | Benthic producer | 153 | 11.89 | - | 0.01 | 0.0103 | - | 0.0056 | unknown |
| 3 | Zooplankton | 9 | 32 | 192 | 0.306 | 0.306 | 0.167 | 0.0948 | unknown |
| 4 | Jellyfish | 1.53 | 5 | 20 | 0.52 | 0.44 | 0.25 | 0.044 | unknown |
| 5 | Polychaetes | 2.24 | 6.75 | 22.5 | 0.673 | 0.673 | 0.3 | 0 | unknown |
| 6 | Echinoderms | 1.98 | 1.2 | 3.58 | 0.444 | 0.444 | 0.335 | 0.0021 | unknown |
| 7 | Benthic crustaceans | 1.43 | 5.65 | 26.9 | 0.617 | 0.619 | 0.21 | 0.0391 | unknown |
| 8 | Non-ceph molluscs | 2.68 | 3.5 | 11.7 | 0.951 | 0.951 | 0.299 | 0.7623 | unknown |
| 9 | Sessile/other invertebrates | 2.61 | 1 | 9 | 0.575 | 0.575 | 0.111 | 0.003 | unknown |
| 10 | Shrimps | 0.194 | 7.6 | 28.94 | 0.95 | 0.953 | 0.263 | 0.6788 | unknown |
| 11 | Crabs | 0.368 | 3 | 12 | 0.95 | 0.954 | 0.25 | 0.1997 | unknown |
| 12 | Cephalopods | 0.68 | 3.1 | 8 | 0.393 | 0.394 | 0.388 | 0.2733 | unknown |
| 13 | Threadfin bream (nemipterids) | 0.26 | 3.08 | 15.4 | 0.847 | 0.88 | 0.2 | 0.657 | unknown |
| 14 | Bigeyes (priacanthids) | 0.13 | 3.33 | 11.3 | 0.55 | 0.538 | 0.295 | 0.206 | unknown |
| 15 | Lizard fish (synodontids) | 0.032 | 1.6 | 5.407 | 0.658 | 0.78 | 0.296 | 0.0234 | unknown |
| 16 | Juvenile Hairtail (trichiurids) | 0.015 | 3.08 | 14.89 | 0.749 | 0.753 | 0.207 | 0.028 | unknown |
| 17 | Adult hairtail (trichiurids) | 0.012 | 1.47 | 6.207 | 0.545 | 0.563 | 0.237 | 0.0072 | unknown |
| 18 | Pomfret (stromateids) | 0.108 | 3.03 | 15.15 | 0.95 | 0.95 | 0.2 | 0.239 | unknown |
| 19 | Snappers | 0.0013 | 1.75 | 8.984 | 0.95 | 0.982 | 0.195 | 0.0011 | unknown |
| 20 | Adult groupers | 0.0064 | 1.75 | 6.1 | 0.95 | 0.954 | 0.287 | 0.0089 | unknown |
| 21 | Croakers (≤ 30 cm) | 0.07 | 3.3 | 11.28 | 0.958 | 0.967 | 0.293 | 0.0351 | unknown |
| 22 | Juvenile large croakers | 0.04 | 3.3 | 16.37 | 0.564 | 0.6 | 0.202 | 0.071 | unknown |
| 23 | Croakers (> 30 cm) | 0.0094 | 1.43 | 6.232 | 0.587 | 0.665 | 0.229 | 0.008 | unknown |
| 24 | Demesral fish (≤ 30 cm) | 0.316 | 4.7 | 23.5 | 0.95 | 0.955 | 0.2 | 0.1788 | unknown |
| 25 | Juvenile demersal fish (> 30 cm) | 0.143 | 3.5 | 16.14 | 0.722 | 0.78 | 0.217 | 0.3165 | unknown |
| 26 | Adult demersal fish (> 30 cm) | 0.021 | 2.1 | 6.207 | 0.747 | 0.832 | 0.338 | 0.0352 | unknown |
| 27 | Benthopelagic fish | 0.922 | 3.08 | 15.42 | 0.479 | 0.512 | 0.2 | 0.6025 | unknown |
| 28 | Melon seed | 0.07 | 2.41 | 24 | 0.994 | 0.994 | 0.1 | 0.0499 | unknown |
| 29 | Pelagic fish (≤ 30 cm) | 1.772 | 4.26 | 17.04 | 0.74 | 0.741 | 0.25 | 2.345 | unknown |
| 30 | Juvenile large pelagic fish | 0.289 | 4.26 | 16.12 | 0.622 | 0.645 | 0.264 | 0.7384 | unknown |
| 31 | Pelagic fish (> 30 cm) | 0.079 | 1.4 | 6.27 | 0.759 | 0.76 | 0.223 | 0.0821 | unknown |
| 32 | Demersal sharks and rays | 0.001 | 1.2 | 6 | 0.867 | 0.884 | 0.2 | 0.001 | unknown |
| 33 | Pelagic sharks and rays | 0.0011 | 0.68 | 3.4 | 0.95 | 0.981 | 0.2 | 0.0007 | unknown |
| 34 | Seabirds | 0.0022 | 0.06 | 67.76 | 0.046 | 0.00283 | 0.000885 | 0 | unknown |
| 35 | Pinnipeds | 0.0046 | 0.045 | 14.77 | 0.29 | 0.00181 | 0.00305 | 0 | unknown |
| 36 | Other mammals | 0.0158 | 0.112 | 10.52 | 0.034 | 0.000211 | 0.0106 | 0 | unknown |
| 37 | Marine turtles | 0.0002 | 0.1 | 3.5 | 0.3 | 0.0187 | 0.0286 | 0 | unknown |
| 38 | Detritus | 100 | - | - | 0.005 | - | - | 0 | unknown |
