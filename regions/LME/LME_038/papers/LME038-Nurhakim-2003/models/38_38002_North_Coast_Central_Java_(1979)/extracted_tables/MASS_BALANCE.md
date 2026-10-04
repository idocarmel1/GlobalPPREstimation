## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 38_Indonesian_Sea_38002_North_Coast_Central_Java_(1979), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 11 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 27 of 27 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 109.153, group 22 (Lg.dem.pred.(J)).

Groups with recomputed EE > 1: 19 (Rastrelliger spp., 1.039), 22 (Lg.dem.pred.(J), 110.103), 26 (Marine mammals, 2.722).

P/Q outside 0.02-0.5: 23 (Demersal rays, 0.019), 26 (Marine mammals, 0.003).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 4 (Lg. Herb. Zoopl.): printed EE 0.92 vs recomputed 0.979 (diff 0.059) with BA unknown - a BA of -0.6662 t/km^2/year (-0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 5 (Carn. Zoopl.): printed EE 0.21 vs recomputed 0.278 (diff 0.068) with BA unknown - a BA of -0.8974 t/km^2/year (-0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 6 (Jelly fishes): printed EE 0.53 vs recomputed 0.449 (diff 0.081) with BA unknown - a BA of +0.04069 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 10 (LBS): printed EE 0.95 vs recomputed 0.781 (diff 0.169) with BA unknown - a BA of +0.2955 t/km^2/year (+0.17 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 12 (Lg.pel.pred.(J)): printed EE 0.95 vs recomputed 0.872 (diff 0.078) with BA unknown - a BA of +0.07 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 14 (Misc.pelagic): printed EE 0.95 vs recomputed 0.890 (diff 0.060) with BA unknown - a BA of +0.05205 t/km^2/year (+0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 19 (Rastrelliger spp.): recomputed EE = 1.039 > 1 without BA, and BA is unknown - a BA of -0.0472 t/km^2/year (-0.09 of production) would close it - undecidable until the source is checked for biomass accumulation
- group 22 (Lg.dem.pred.(J)): recomputed EE = 110.103 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 23 (Demersal rays): printed EE 0.95 vs recomputed 0.654 (diff 0.296) with BA unknown - a BA of +0.004535 t/km^2/year (+0.30 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 24 (Lg.pel.pred (A)): printed EE 0.95 vs recomputed 0.877 (diff 0.073) with BA unknown - a BA of +0.01494 t/km^2/year (+0.07 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 26 (Marine mammals): recomputed EE = 2.722 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation

### Warnings

- group 1 (Benthic producers): only 2 of B/P-B/Q-B/EE given (B, P/B) - Ecopath needs three
- group 23 (Demersal rays): P/Q = 0.019 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 26 (Marine mammals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 24 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Small herb. Zoopl.), 4 (Lg. Herb. Zoopl.), 5 (Carn. Zoopl.), 6 (Jelly fishes), 7 (Benthic infauna), 8 (SAF), 9 (Macrozoobenthos), 10 (LBS) ...
- detritus pools (1): inflow ~2418, consumption ~917.6 t/km^2/year, implied EE ~0.380 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Benthic producers | 153 | 11.86 | - | - | 0.00286 | - | 0 | unknown |
| 2 | Phytoplankton | 4.68 | 135 | - | 0.95 | 0.95 | - | 0 | unknown |
| 3 | Small herb. Zoopl. | 2.43 | 60.22 | 220 | 0.46 | 0.445 | 0.274 | 0 | unknown |
| 4 | Lg. Herb. Zoopl. | 0.56 | 20 | 70 | 0.92 | 0.979 | 0.286 | 0.02 | unknown |
| 5 | Carn. Zoopl. | 0.31 | 42.58 | 135.1 | 0.21 | 0.278 | 0.315 | 0 | unknown |
| 6 | Jelly fishes | 0.1 | 5.01 | 25.05 | 0.53 | 0.449 | 0.2 | 0.05 | unknown |
| 7 | Benthic infauna | 34.48 | 6.57 | 27.4 | 0.43 | 0.427 | 0.24 | 0 | unknown |
| 8 | SAF | 0.32 | 3.81 | 7.63 | 0.3 | 0.297 | 0.499 | 0.03 | unknown |
| 9 | Macrozoobenthos | 2.21 | 3 | 12.5 | 0.75 | 0.749 | 0.24 | 0.01 | unknown |
| 10 | LBS | 17.48 | 0.1 | 0.5 | 0.95 | 0.781 | 0.2 | 0.26 | unknown |
| 11 | Juv.pen.shrimp | 0.47 | 13 | 70 | 0.95 | 0.953 | 0.186 | 0.02 | unknown |
| 12 | Lg.pel.pred.(J) | 0.19 | 4.73 | 15.75 | 0.95 | 0.872 | 0.3 | 0.71 | unknown |
| 13 | Ad.pen.shrimps | 1.27 | 5 | 28.94 | 0.95 | 0.951 | 0.173 | 0.1 | unknown |
| 14 | Misc.pelagic | 0.3 | 2.91 | 14.57 | 0.95 | 0.89 | 0.2 | 0.43 | unknown |
| 15 | Leiognathids | 0.71 | 3.52 | 15.59 | 0.28 | 0.269 | 0.226 | 0.2 | unknown |
| 16 | Crabs and Lobster | 0.63 | 4 | 21.9 | 0.95 | 0.936 | 0.183 | 0 | unknown |
| 17 | Cephalopods | 0.9 | 3.1 | 20.32 | 0.95 | 0.949 | 0.153 | 0.05 | unknown |
| 18 | Decapterus spp. | 0.24 | 3.73 | 13.89 | 0.95 | 0.946 | 0.269 | 0.63 | unknown |
| 19 | Rastrelliger spp. | 0.12 | 4.43 | 14.16 | 0.95 | 1.04 | 0.313 | 0.39 | unknown |
| 20 | Clupeoids | 0.81 | 6.2 | 15.75 | 0.95 | 0.962 | 0.394 | 0.71 | unknown |
| 21 | Small demersals | 0.5 | 3.25 | 15.24 | 0.98 | 0.98 | 0.213 | 0.39 | unknown |
| 22 | Lg.dem.pred.(J) | 0.32 | 3.254 | 15.2 | 0.95 | 110 | 0.214 | 0.39 | unknown |
| 23 | Demersal rays | 0.09 | 0.17 | 9.1 | 0.95 | 0.654 | 0.0187 | 0.01 | unknown |
| 24 | Lg.pel.pred (A) | 0.09 | 2.28 | 11.39 | 0.95 | 0.877 | 0.2 | 0.18 | unknown |
| 25 | Lg.dem.pred (A) | 0.07 | 3.5 | 7.49 | 0.26 | 0.286 | 0.467 | 0.07 | unknown |
| 26 | Marine mammals | 0.14 | 0.04 | 15.36 | 0.09 | 2.72 | 0.0026 | 0.01 | unknown |
| 27 | Detritus | 17.14 | - | - | 0.372 | - | - | 0 | unknown |
