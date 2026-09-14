## Mass balance

Checked by the bundled `database_json.py` equations plus the local source-preservation/integrity audit on the assembled JSON for 27_Canary_Current_27_3_Banc_d_Arguin_and_Mauritanian_Shelf_(1991), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 4 error(s), 16 indeterminate, 10 warning(s), 3 note(s).

Biomass accumulation is unknown (-9999) for 1 of 51 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.668, group 35 (BA crustaceans).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Marine mammals, 0.003), 2 (Coastal birds, 0.004).

BA: carried for 50 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Marine mammals, +0), 2 (Coastal birds, +0), 3 (Meagre ad, +0), 4 (Meagre juv, +0), 5 (Mullets, +0), 6 (Pelagic L, +0), 7 (Mackerel, +0), 8 (Sardine, +0), 9 (Sardinelles, +0), 10 (Horse mackerels, +0), 11 (Coastal selacians, -0.062), 12 (Coastal M, +0), 13 (Coastal S, +0), 14 (Croakers ad, +0), 15 (Croakers juv, +0), 16 (Seabreams ad, +0), 17 (Seabreams juv., +0), 18 (Catfish ad, +0), 19 (Catfish juv, +0), 20 (Shelf selacians, +0), 21 (Shelf L, +0), 22 (Shelf M, +0), 23 (Groupers ad, -0.0055), 24 (Grouper juv, -0), 25 (Sparids ad, +0), 26 (Sparids juv, +0), 27 (Scianids, -0.011), 28 (Shelf soles, +0), 29 (Shelf S, +0), 30 (Octopus vulgaris, -0.0411), 31 (Cephalopods, -0.03), 32 (BA L crustaceans, +0), 33 (BA molluscs, +0), 34 (BA worms, +0), 35 (BA crustaceans, +0), 36 (BA other inverts, +0), 37 (BA meiobenthos, +0), 38 (shelf L crustaceans, +0), 39 (shelf molluscs, +0), 40 (shelf worms, +0), 41 (shelf crustaceans, +0), 42 (shelf other inverts, +0), 43 (shelf meiobenthos, +0), 44 (mesozoopl., +0), 45 (macrozoopl., +0), 46 (BA mesozoopl., +0), 47 (BA macrozoopl., +0), 48 (BA phytopl., +0), 49 (phytoplankton, +0), 50 (algae and eelgrass, +0). The remaining 1 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 13 (Coastal S) has Q/B=3.1 but no diet entries - its consumption is missing from every prey's budget
- group 19 (Catfish juv) has Q/B=22.3 but no diet entries - its consumption is missing from every prey's budget
- group 2 (Coastal birds): published diet + Import = 0.980331 < 0.99; unexplained deficit preserved.
- group 23 (Groupers ad): source diet + Import = 2.2006 > 1.01; published diet cannot be a valid composition. Exact source preserved without normalization.

### Unresolved data and scope

- group 3 (Meagre ad): known diet sum 0.8461; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 4 (Meagre juv): known diet sum 0.70807; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 5 (Mullets): known diet sum 0.908; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 11 (Coastal selacians): known diet sum 0.51811; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 12 (Coastal M): known diet sum 0.3639; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 13 (Coastal S): known diet sum 0; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 14 (Croakers ad): known diet sum 0.29507; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 15 (Croakers juv): known diet sum 0.0375; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 16 (Seabreams ad): known diet sum 0.164; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 17 (Seabreams juv.): known diet sum 0.0184; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 18 (Catfish ad): known diet sum 0.3844; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 19 (Catfish juv): known diet sum 0; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 24 (Grouper juv): known diet sum 0.3438; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- group 26 (Sparids juv): known diet sum 0.5454; variant-specific prey components are unpublished and remain -9999, so predation checks are lower bounds.
- Unassimilated consumption and detritus routing/import/export are unknown. Stock detritus/respiration arithmetic uses a software GS assumption only as an indicative check, not as a verified source value.
- P/B is zero for Meagre despite nonzero Z/PQ and is absent for 10 other multi-stanza groups; those production identities cannot be verified from the printed inputs.

### Warnings

- group 1 (Marine mammals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Coastal birds): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 32 (BA L crustaceans): printed EE 0.83 vs recomputed 0.572 (diff 0.258), BA 0.00 carried
- group 33 (BA molluscs): printed EE 0.91 vs recomputed 0.814 (diff 0.096), BA 0.00 carried
- group 34 (BA worms): printed EE 0.86 vs recomputed 0.612 (diff 0.248), BA 0.00 carried
- group 35 (BA crustaceans): printed EE 0.98 vs recomputed 0.312 (diff 0.668), BA 0.00 carried
- group 36 (BA other inverts): printed EE 0.90 vs recomputed 0.553 (diff 0.347), BA 0.00 carried
- group 37 (BA meiobenthos): printed EE 0.93 vs recomputed 0.850 (diff 0.080), BA 0.00 carried
- group 38 (shelf L crustaceans): printed EE 0.74 vs recomputed 0.614 (diff 0.126), BA 0.00 carried
- group 41 (shelf crustaceans): printed EE 0.78 vs recomputed 0.645 (diff 0.135), BA 0.00 carried

### Notes

- 40 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Marine mammals), 2 (Coastal birds), 3 (Meagre ad), 4 (Meagre juv), 5 (Mullets), 6 (Pelagic L), 7 (Mackerel), 8 (Sardine) ...
- detritus pools (1): inflow ~6996, consumption ~4003 t/km^2/year, implied EE ~0.572 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)
- Stock equation-only verdict before integrity/missing-data guards: NOT BALANCED. Final verdict concerns this extraction, not whether the authors had an internally balanced operational model.

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Marine mammals | 0.01 | 0.04 | 12.5 | 0 | 0 | 0.0032 | 0 | 0 |
| 2 | Coastal birds | 0.01 | 0.28 | 67 | 0 | 0 | 0.00418 | 0 | 0 |
| 3 | Meagre ad | 0.12 | 0 | 2.1 | 0.66 | - | - | 0.014 | 0 |
| 4 | Meagre juv | 5e-05 | 0 | 17.9 | 0.97 | - | - | 0 | 0 |
| 5 | Mullets | 0.42 | 0.8 | 8.2 | 0.8 | 0.794 | 0.0976 | 0.103 | 0 |
| 6 | Pelagic L | 3.89 | 0.96 | 5.4 | 0.8 | 0.8 | 0.178 | 2.679 | 0 |
| 7 | Mackerel | 1.45 | 0.45 | 3 | 0.75 | 0.755 | 0.15 | 0.289 | 0 |
| 8 | Sardine | 11.79 | 0.65 | 4.3 | 0.83 | 0.83 | 0.151 | 1.801 | 0 |
| 9 | Sardinelles | 18 | 0.99 | 7.7 | 0.85 | 0.855 | 0.129 | 2.31 | 0 |
| 10 | Horse mackerels | 10 | 0.72 | 3.6 | 0.87 | 0.869 | 0.2 | 3.812 | 0 |
| 11 | Coastal selacians | 1.24 | 0.3 | 2 | 0.01 | 0.0147 | 0.15 | 0.063 | -0.062 |
| 12 | Coastal M | 0.83 | 0.58 | 2.9 | 0.86 | 0.867 | 0.2 | 0.121 | 0 |
| 13 | Coastal S | 5.18 | 0.62 | 3.1 | 0.8 | 0.8 | 0.2 | 0 | 0 |
| 14 | Croakers ad | 0.08 | - | 3.9 | 0.75 | - | - | 0.003 | 0 |
| 15 | Croakers juv | 0 | - | 9.9 | 0.71 | - | - | 0 | 0 |
| 16 | Seabreams ad | 1.69 | - | 4.7 | 0.9 | - | - | 0.167 | 0 |
| 17 | Seabreams juv. | 0.01 | - | 21.1 | 0.88 | - | - | 0 | 0 |
| 18 | Catfish ad | 0.6 | - | 4.1 | 0.23 | - | - | 0.034 | 0 |
| 19 | Catfish juv | 0 | - | 22.3 | 0.78 | - | - | 0 | 0 |
| 20 | Shelf selacians | 0.2 | 0.24 | 1.6 | 0.79 | 0.795 | 0.15 | 0.011 | 0 |
| 21 | Shelf L | 0.36 | 0.47 | 3.4 | 0.47 | 0.467 | 0.138 | 0.071 | 0 |
| 22 | Shelf M | 1.55 | 0.57 | 6.2 | 0.91 | 0.92 | 0.0919 | 0.146 | 0 |
| 23 | Groupers ad | 0.11 | - | 3.2 | 0.94 | - | - | 0.025 | -0.0055 |
| 24 | Grouper juv | 0 | - | 16.2 | 0.54 | - | - | 0 | -0 |
| 25 | Sparids ad | 1.29 | - | 2.4 | 0.93 | - | - | 0.014 | 0 |
| 26 | Sparids juv | 0.01 | - | 9.8 | 0.94 | - | - | 0 | 0 |
| 27 | Scianids | 0.22 | 0.29 | 4.3 | 0.67 | 0.658 | 0.0674 | 0.017 | -0.011 |
| 28 | Shelf soles | 0.35 | 0.58 | 2.9 | 0.88 | 0.884 | 0.2 | 0.009 | 0 |
| 29 | Shelf S | 7.61 | 0.82 | 7.6 | 0.8 | 0.801 | 0.108 | 0.005 | 0 |
| 30 | Octopus vulgaris | 1.37 | 1.4 | 4.7 | 0.63 | 0.632 | 0.298 | 0.883 | -0.0411 |
| 31 | Cephalopods | 1 | 1.2 | 4 | 0.87 | 0.868 | 0.3 | 0.255 | -0.03 |
| 32 | BA L crustaceans | 11.02 | 1.44 | 7.2 | 0.83 | 0.572 | 0.2 | 0 | 0 |
| 33 | BA molluscs | 22.86 | 1.5 | 16.7 | 0.91 | 0.814 | 0.0898 | 0 | 0 |
| 34 | BA worms | 6.84 | 3 | 33.3 | 0.86 | 0.612 | 0.0901 | 0 | 0 |
| 35 | BA crustaceans | 2.09 | 2.4 | 12 | 0.98 | 0.312 | 0.2 | 0 | 0 |
| 36 | BA other inverts | 0.95 | 1.8 | 9 | 0.9 | 0.553 | 0.2 | 0 | 0 |
| 37 | BA meiobenthos | 2.66 | 9 | 100 | 0.93 | 0.85 | 0.09 | 0 | 0 |
| 38 | shelf L crustaceans | 8.1 | 1.5 | 7.5 | 0.74 | 0.614 | 0.2 | 0.005 | 0 |
| 39 | shelf molluscs | 26.21 | 1.5 | 16.7 | 0.49 | 0.466 | 0.0898 | 3e-06 | 0 |
| 40 | shelf worms | 31.77 | 3 | 33 | 0.43 | 0.409 | 0.0909 | 0 | 0 |
| 41 | shelf crustaceans | 9.04 | 2.4 | 12 | 0.78 | 0.645 | 0.2 | 0 | 0 |
| 42 | shelf other inverts | 17.21 | 1.8 | 9 | 0.22 | 0.216 | 0.2 | 0 | 0 |
| 43 | shelf meiobenthos | 8.91 | 9 | 100 | 0.26 | 0.257 | 0.09 | 0 | 0 |
| 44 | mesozoopl. | 55.08 | 24 | 112 | 0.15 | 0.147 | 0.214 | 0 | 0 |
| 45 | macrozoopl. | 3.41 | 4.3 | 17 | 0.75 | 0.736 | 0.253 | 0 | 0 |
| 46 | BA mesozoopl. | 1.91 | 24 | 112 | 0.8 | 0.761 | 0.214 | 0 | 0 |
| 47 | BA macrozoopl. | 2.59 | 4.3 | 17 | 0.8 | 0.758 | 0.253 | 0 | 0 |
| 48 | BA phytopl. | 6 | 100 | 0 | 0.44 | 0.428 | - | 0 | 0 |
| 49 | phytoplankton | 68 | 100 | 0 | 0.85 | 0.85 | - | 0 | 0 |
| 50 | algae and eelgrass | 549 | 4.06 | 0 | 0.01 | 0.00907 | - | 0 | 0 |
| 51 | Detritus | 560 | 0 | 0 | 0.48 | - | - | 0 | unknown |
