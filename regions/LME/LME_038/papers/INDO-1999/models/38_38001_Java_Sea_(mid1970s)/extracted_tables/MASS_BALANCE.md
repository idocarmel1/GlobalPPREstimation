## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 38_Indonesian_Sea_38001_Java_Sea_(mid1970s), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 1 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 28 of 28 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.019, group 24 (Demersal rays).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 27 (Marine mammals, 0.003).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 27 (Marine mammals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 25 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Small herb. zoopl.), 4 (Lg. herb. zoopl.), 5 (Carn. zoopl.), 6 (Jelly fishes), 7 (Benthic infauna), 8 (SAF), 9 (Macrozoobenthos), 10 (LBS) ...
- detritus pools (1): inflow ~2379, consumption ~617.4 t/km^2/year, implied EE ~0.260 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Benthic producers | 153 | 11.88 | - | 0.003 | 0.00338 | - | 0 | unknown |
| 2 | Phytoplankton | 4.154 | 135 | - | 0.95 | 0.95 | - | 0 | unknown |
| 3 | Small herb. zoopl. | 2.43 | 60.23 | 220 | 0.47 | 0.47 | 0.274 | 0 | unknown |
| 4 | Lg. herb. zoopl. | 0.56 | 20 | 70 | 0.912 | 0.912 | 0.286 | 0.008 | unknown |
| 5 | Carn. zoopl. | 0.31 | 42.58 | 135.1 | 0.238 | 0.238 | 0.315 | 0 | unknown |
| 6 | Jelly fishes | 0.1 | 5.011 | 25.05 | 0.414 | 0.414 | 0.2 | 0.003 | unknown |
| 7 | Benthic infauna | 18.94 | 6.57 | 27.4 | 0.537 | 0.537 | 0.24 | 0 | unknown |
| 8 | SAF | 0.377 | 1.188 | 9.28 | 0.75 | 0.75 | 0.128 | 0.01 | unknown |
| 9 | Macrozoobenthos | 2.455 | 3 | 12.5 | 0.75 | 0.75 | 0.24 | 0.001 | unknown |
| 10 | LBS | 20 | 0.1 | 0.5 | 0.989 | 0.989 | 0.2 | 0.1 | unknown |
| 11 | Juv. pen. shrimps | 0.556 | 13 | 70 | 0.95 | 0.95 | 0.186 | 0.008 | unknown |
| 12 | Lg. pel. pred. (J) | 0.19 | 3.35 | 11.17 | 0.5 | 0.499 | 0.3 | 0.116 | unknown |
| 13 | Ad. pen. shrimps | 1.224 | 5 | 28.95 | 0.95 | 0.95 | 0.173 | 0.014 | unknown |
| 14 | Misc. pelagics | 0.221 | 2.174 | 10.87 | 0.95 | 0.95 | 0.2 | 0.117 | unknown |
| 15 | Leiognathids | 0.193 | 3.674 | 18.37 | 0.51 | 0.51 | 0.2 | 0.019 | unknown |
| 16 | Crabs + Lobsters | 0.765 | 4 | 21.9 | 0.95 | 0.95 | 0.183 | 0.001 | unknown |
| 17 | Cephalopods | 0.95 | 3.1 | 20.32 | 0.95 | 0.95 | 0.153 | 0.005 | unknown |
| 18 | Decapterus spp. | 0.087 | 2.81 | 14.05 | 0.95 | 0.947 | 0.2 | 0.071 | unknown |
| 19 | Rastrelliger spp. | 0.044 | 4.248 | 14.16 | 0.95 | 0.956 | 0.3 | 0.035 | unknown |
| 20 | Clupeoids | 0.899 | 3.35 | 17.62 | 0.95 | 0.95 | 0.19 | 0.116 | unknown |
| 21 | Small demersals | 1.687 | 2.568 | 12.84 | 0.553 | 0.553 | 0.2 | 0.066 | unknown |
| 22 | Med. demersals | 0.046 | 1.828 | 9.14 | 0.575 | 0.575 | 0.2 | 0.015 | unknown |
| 23 | Lg. dem. pred. (J) | 0.434 | 3.852 | 12.84 | 0.5 | 0.5 | 0.3 | 0.066 | unknown |
| 24 | Demersal rays | 0.009 | 1.3 | 8.2 | 0.6 | 0.581 | 0.159 | 0.006 | unknown |
| 25 | Lg. pel. pred (A) | 0.104 | 1.2 | 8.65 | 0.5 | 0.5 | 0.139 | 0.051 | unknown |
| 26 | Lg. dem. pred (A) | 0.13 | 0.92 | 6.13 | 0.174 | 0.174 | 0.15 | 0.02 | unknown |
| 27 | Marine mammals | 0.138 | 0.045 | 15.36 | 0.289 | 0.289 | 0.00293 | 0.001 | unknown |
| 28 | Detritus | 120 | - | - | 0.264 | - | - | 0 | unknown |
