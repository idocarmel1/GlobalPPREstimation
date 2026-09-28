# LME049 — direct SPPR diagnostics

Only results returned by `PPRCalculator.diagnose_sppr(short=False, flat=False, return_sppr=False)` are shown below, for GE, TE and With Egestion. Calls use the same loader-completed model state and closed-detritus configuration as the retained diagnostics.

[Full returned data](DIAGNOSE_SPPR_RESULTS.json) · [Caller/settings provenance](DIRECT_DIAGNOSE_PROVENANCE.json)

## Summary

| Model | TE option | Returned status | Living spectral radius | Recycling gain b | Negative basal-source columns | Relative balance gap |
|---|---|---|---|---|---|---|
| 49_2019201301_Watari_Detritus_Pooled_Experiment_(2013) | GE | OK | 0.3334302325581396 | 0.040172878827864904 | 0 | 0.006764798141402979 |
| 49_2019201301_Watari_Detritus_Pooled_Experiment_(2013) | TE | FAIL | 0.5462783830567154 | 0.0 | 4 | 0.03354352350520768 |
| 49_2019201301_Watari_Detritus_Pooled_Experiment_(2013) | With Egestion | OK | 0.2667441860465117 | 0.0457181749968441 | 0 | 0.003876479626862391 |
| 49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023) | GE | FAIL | 1.31171875 | 0.01495535578600322 | 2 | 0.0 |
| 49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023) | TE | FAIL | 1.6528925619834711 | 0.0 | 2 | 1.2340225398724276e-15 |
| 49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023) | With Egestion | FAIL | 1.0493750000000002 | 0.051479822727498264 | 2 | 2.0567042331207126e-16 |

## Original Watari — 41 groups

`49_20192013_Western_North_Pacific_Watari_(2013)`: loading is blocked by absent detritus routing for groups39,40,41. No `diagnose_sppr()` result exists.

## Selected Watari detritus-pooling variant — 39 groups

`49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)`

### Returned configuration

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| TE_option | GE | TE | With Egestion |
| det_open_mode | none | none | none |
| det_theta | 1.0 | 1.0 | 1.0 |
| det_external_sppr | 0.0 | 0.0 | 0.0 |
| det_collapse_mode | never | never | never |
| explicit_TE | false | false | false |
| method | single_detritus | null | single_detritus |
| would_pool | false | false | false |
| model | Watari_Detritus_Pooled_Experiment (2013) | Watari_Detritus_Pooled_Experiment (2013) | Watari_Detritus_Pooled_Experiment (2013) |

### Model input

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| Status | OK | OK | OK |
| Ecopath identities balanced | true | true | true |
| Production maximum relative residual | 1.6760613294461905e-16 | 1.6760613294461905e-16 | 1.6760613294461905e-16 |
| Consumption maximum relative residual | 1.7014912254791672e-16 | 1.7014912254791672e-16 | 1.7014912254791672e-16 |
| Diet rows sum to one | true | true | true |
| Maximum diet-sum deviation | 4.440892098500626e-16 | 4.440892098500626e-16 | 4.440892098500626e-16 |
| Negative-catch groups | 0 | 0 | 0 |
| Zero-catch groups | 18 | 18 | 18 |
| Total source-model catch | 1.7200000000000002 | 1.7200000000000002 | 1.7200000000000002 |
| Has catch | true | true | true |
| Has EE issues | false | false | false |
| EE-zero count | 0 | 0 | 0 |
| Marginal-EE count | 0 | 0 | 0 |
| EE-above-one count | 0 | 0 | 0 |
| EE-zero groups | `[]` | `[]` | `[]` |
| Marginal-EE groups | `[]` | `[]` | `[]` |

### Convergence and coefficients

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| Status | OK | FAIL | OK |
| Solve error | null | null | null |
| Recycling gain b | 0.040172878827864904 | 0.0 | 0.0457181749968441 |
| Recycling converges | true | true | true |
| Living spectral radius | 0.3334302325581396 | 0.5462783830567154 | 0.2667441860465117 |
| Living network converges | true | true | true |
| Detritus coefficients by group | `{"39": 1.40229804525697}` | `{"39": 0.6465430116983203}` | `{"39": 1.4433651760558324}` |
| Maximum detritus coefficient | 1.40229804525697 | 0.6465430116983203 | 1.4433651760558324 |
| Maximum-SPPR group (seq, TL, SPPR, inverse TE) | `{"seq": 2, "tl": 4.023508207551435, "sppr": 2231.7870221623607, "inv_te": 102.0}` | `{"seq": 2, "tl": 4.023508207551435, "sppr": 989826.1613197, "inv_te": 10200.000000000106}` | `{"seq": 2, "tl": 4.023508207551435, "sppr": 1003.6380839598, "inv_te": 81.6}` |
| Maximum-TL group (seq, TL, SPPR, inverse TE) | `{"seq": 4, "tl": 4.227693165663254, "sppr": 160.02840375385853, "inv_te": 5.615384615384615}` | `{"seq": 4, "tl": 4.227693165663254, "sppr": 8134.885505769225, "inv_te": 62.39316239316241}` | `{"seq": 4, "tl": 4.227693165663254, "sppr": 66.99837590872269, "inv_te": 4.4923076923076914}` |
| Basal-source columns containing negatives | 0 | 4 | 0 |
| Negatives predicted from recycling | false | false | false |
| Near-singular TE groups | `[]` | `[3, 2]` | `[]` |

### SPPR balance

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| Status | OK | WARN | OK |
| Strict SPPR balance | false | false | false |
| PP inflow | 1506.7714 | 1506.7714 | 1506.7714 |
| SPPR-weighted outflow | 1516.9644043662393 | 1557.3138218728748 | 1512.612368634439 |
| Relative SPPR balance gap | 0.006764798141402979 | 0.03354352350520768 | 0.003876479626862391 |

### Returned footprint (ungraded)

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| ppr_all | 89.06925072177393 | 667.8536001911467 | 41.60698001986465 |
| ppr_inner | 89.06925072177393 | 667.8536001911467 | 41.60698001986465 |
| ppr_pp_only | 72.00476328904145 | 639.2762170404162 | 33.63680005765025 |
| npp | 1506.7714 | 1506.7714 | 1506.7714 |
| ppr2npp | 0.05911265021473989 | 0.44323485313773986 | 0.027613332732400315 |
| ppr2npp_pp_only | 0.047787450232358704 | 0.4242688818226947 | 0.022323757975264362 |

### Returned warnings

**GE**

None (`[]`).

**TE**

- TE_option='TE' has no detritus recycling matrix: b reported as 0.0 (mortality-derived SPPR is written off as lost)
- 4 basal source column(s) contain negative SPPR
- 2 group(s) have near-zero TE (SPPR ~ 1/te is near-singular): [3, 2]
- PP balance gap 3.354% exceeds 1.0%

**With Egestion**

None (`[]`).

## Chen source candidate — 25 groups

`49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023)`

### Returned configuration

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| TE_option | GE | TE | With Egestion |
| det_open_mode | none | none | none |
| det_theta | 1.0 | 1.0 | 1.0 |
| det_external_sppr | 0.0 | 0.0 | 0.0 |
| det_collapse_mode | never | never | never |
| explicit_TE | false | false | false |
| method | single_detritus | null | single_detritus |
| would_pool | false | false | false |
| model | Kuroshio_Oyashio_Extension_Chen (2023) | Kuroshio_Oyashio_Extension_Chen (2023) | Kuroshio_Oyashio_Extension_Chen (2023) |

### Model input

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| Status | OK | OK | OK |
| Ecopath identities balanced | true | true | true |
| Production maximum relative residual | 7.529181753371558e-16 | 7.529181753371558e-16 | 7.529181753371558e-16 |
| Consumption maximum relative residual | 1.807003620809174e-16 | 1.807003620809174e-16 | 1.807003620809174e-16 |
| Diet rows sum to one | true | true | true |
| Maximum diet-sum deviation | 2.220446049250313e-16 | 2.220446049250313e-16 | 2.220446049250313e-16 |
| Negative-catch groups | 0 | 0 | 0 |
| Zero-catch groups | 15 | 15 | 15 |
| Total source-model catch | 0.5826 | 0.5826 | 0.5826 |
| Has catch | true | true | true |
| Has EE issues | false | false | false |
| EE-zero count | 0 | 0 | 0 |
| Marginal-EE count | 0 | 0 | 0 |
| EE-above-one count | 0 | 0 | 0 |
| EE-zero groups | `[]` | `[]` | `[]` |
| Marginal-EE groups | `[]` | `[]` | `[]` |

### Convergence and coefficients

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| Status | FAIL | FAIL | FAIL |
| Solve error | null | null | null |
| Recycling gain b | 0.01495535578600322 | 0.0 | 0.051479822727498264 |
| Recycling converges | true | true | true |
| Living spectral radius | 1.31171875 | 1.6528925619834711 | 1.0493750000000002 |
| Living network converges | false | false | false |
| Detritus coefficients by group | `{"25": 1.0558845580362732}` | `{"25": 0.6571335047118464}` | `{"25": 0.9107975616663341}` |
| Maximum detritus coefficient | 1.0558845580362732 | 0.6571335047118464 | 0.9107975616663341 |
| Maximum-SPPR group (seq, TL, SPPR, inverse TE) | `{"seq": 8, "tl": 4.742666434248014, "sppr": 1224.6859598439335, "inv_te": 3.3333333333333335}` | `{"seq": 9, "tl": 4.662414592892487, "sppr": 41472.97100785466, "inv_te": 5.555555555555555}` | `{"seq": 10, "tl": 4.508353846153846, "sppr": 60.56405570771217, "inv_te": 3.2}` |
| Maximum-TL group (seq, TL, SPPR, inverse TE) | `{"seq": 3, "tl": 5.78208798748216, "sppr": -3180.745170470326, "inv_te": 5.1020408163265305}` | `{"seq": 3, "tl": 5.78208798748216, "sppr": -1367919.9040613163, "inv_te": 31.88775510204081}` | `{"seq": 3, "tl": 5.78208798748216, "sppr": -4636.701249301614, "inv_te": 4.081632653061225}` |
| Basal-source columns containing negatives | 2 | 2 | 2 |
| Negatives predicted from recycling | false | false | false |
| Near-singular TE groups | `[]` | `[]` | `[]` |

### SPPR balance

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| Status | OK | OK | OK |
| Strict SPPR balance | true | true | true |
| PP inflow | 1105.52442 | 1105.52442 | 1105.52442 |
| SPPR-weighted outflow | 1105.52442 | 1105.5244199999986 | 1105.5244199999997 |
| Relative SPPR balance gap | 0.0 | 1.2340225398724276e-15 | 2.0567042331207126e-16 |

### Returned footprint (ungraded)

| Returned field | GE | TE | With Egestion |
|---|---|---|---|
| ppr_all | -2.3636635532553556 | -1552.4260824213914 | -13.426889804487354 |
| ppr_inner | -2.3636635532553556 | -1552.4260824213914 | -13.426889804487352 |
| ppr_pp_only | -1.1644376534326901 | -1531.578012139995 | -10.200356954885722 |
| npp | 1105.52442 | 1105.52442 | 1105.52442 |
| ppr2npp | -0.002138047347027717 | -1.4042440441264892 | -0.012145267496205423 |
| ppr2npp_pp_only | -0.0010532898526408763 | -1.385385962021531 | -0.009226713377245635 |

### Returned warnings

**GE**

- living network diverges: rho(A_LL)=1.312 >= 1; this corrupts the basis B is built from, so b is unreliable
- 2 basal source column(s) contain negative SPPR

**TE**

- TE_option='TE' has no detritus recycling matrix: b reported as 0.0 (mortality-derived SPPR is written off as lost)
- living network diverges: rho(A_LL)=1.653 >= 1; this corrupts the basis B is built from, so b is unreliable
- 2 basal source column(s) contain negative SPPR

**With Egestion**

- living network diverges: rho(A_LL)=1.049 >= 1; this corrupts the basis B is built from, so b is unreliable
- 2 basal source column(s) contain negative SPPR
