# Full direct diagnostic returns

These are the unabridged diagnostic dictionaries from the actual direct calls. Each companion lossless return retains the entire tuple including SPPR, A and L matrices.

## GE

```json
{
  "status": "FAIL",
  "model_input": {
    "status": "FAIL",
    "is_model_balanced": false,
    "p_max_rel_residual": 4219.15750763535,
    "q_max_rel_residual": 843.8315359765764,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.220446049250313e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 22,
    "total_catch": 35.5395489180725,
    "has_catch": true,
    "has_ee_issues": true,
    "n_ee0": 5,
    "n_ee_marginal": 1,
    "n_ee_gt_1": 0,
    "ee0_groups": [
      35,
      34,
      33,
      32,
      31
    ],
    "ee_marginal_groups": [
      7
    ]
  },
  "divergence": {
    "status": "FAIL",
    "solve_error": null,
    "b": 1.59176568425259,
    "b_converges": false,
    "rho_living": 0.7,
    "living_converges": true,
    "sppr_det": {
      "36": 6.10370815911851,
      "37": 6.10370815911851,
      "38": 6.10370815911851,
      "39": 6.10370815911851
    },
    "max_sppr_det": 6.10370815911851,
    "max_sppr_group": {
      "seq": 31,
      "tl": 3.8984436333758534,
      "sppr": 220732.16581630218,
      "inv_te": 1525.000034086407
    },
    "max_tl_group": {
      "seq": 30,
      "tl": 4.447238103051863,
      "sppr": 4195.506859329449,
      "inv_te": 6.666666176093461
    },
    "n_negative_sources": 0,
    "expect_negatives": true,
    "near_singular_te": [
      31
    ]
  },
  "balance": {
    "status": "FAIL",
    "is_balanced": false,
    "inflow": 11310.477371346196,
    "outflow": 13167.489567587258,
    "rel_gap": 0.1641851298819261
  },
  "footprint": {
    "ppr_all": 8517.658983839245,
    "ppr_inner": 8504.926634603287,
    "ppr_pp_only": 1836.2669164220374,
    "npp": 11273.056447505951,
    "ppr2npp": 0.7544472676250029,
    "ppr2npp_pp_only": 0.16288988926586034
  },
  "config": {
    "TE_option": "GE",
    "det_open_mode": "none",
    "det_theta": 1.0,
    "det_external_sppr": 0.0,
    "det_collapse_mode": "auto",
    "explicit_TE": false,
    "method": "pooled_detritus_scaling",
    "would_pool": true,
    "model": "Northern Humboldt Current (1995-1998)"
  },
  "warnings": [
    "model input not mass-balanced: max relative residual 4.22e+03 exceeds fail threshold 0.1",
    "5 group(s) with EE=0 (all production is non-predatory death): 35 (Leatherback turtle), 34 (Green sea turtle), 33 (Cetaceans), 32 (Pinnipeds), 31 (Seabirds). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed",
    "1 group(s) with 0 < EE < 0.001: 7 (Chrysaora plocamia). Their SPPR ~ 1/te is near-singular",
    "detritus recycling diverges: b=1.592 >= 1; the SPPR returned is not a convergent sum",
    "1 group(s) have near-zero TE (SPPR ~ 1/te is near-singular): [31]",
    "PP balance gap 16.419% exceeds fail threshold 5.0%"
  ]
}
```

Full returned tuple: [GE/full_return_lossless.json](GE/full_return_lossless.json).
Matrices: [SPPR](GE/SPPR.csv), [A](GE/A.csv), [L](GE/L.csv).

## TE

```json
{
  "status": "FAIL",
  "model_input": {
    "status": "FAIL",
    "is_model_balanced": false,
    "p_max_rel_residual": 4219.15750763535,
    "q_max_rel_residual": 843.8315359765764,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.220446049250313e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 22,
    "total_catch": 35.5395489180725,
    "has_catch": true,
    "has_ee_issues": true,
    "n_ee0": 5,
    "n_ee_marginal": 1,
    "n_ee_gt_1": 0,
    "ee0_groups": [
      35,
      34,
      33,
      32,
      31
    ],
    "ee_marginal_groups": [
      7
    ]
  },
  "divergence": {
    "status": "WARN",
    "solve_error": null,
    "b": 0.0,
    "b_converges": true,
    "rho_living": 0.7316477059387119,
    "living_converges": true,
    "sppr_det": {
      "36": 0.0,
      "37": 0.0,
      "38": 0.30428520886027294,
      "39": 0.0
    },
    "max_sppr_det": 0.30428520886027294,
    "max_sppr_group": {
      "seq": 25,
      "tl": 4.1173056366305385,
      "sppr": 447352.6497241629,
      "inv_te": 590.4578556431102
    },
    "max_tl_group": {
      "seq": 30,
      "tl": 4.447238103051863,
      "sppr": 7596.014295076642,
      "inv_te": 11.815484985703286
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": [
      7
    ]
  },
  "balance": {
    "status": "FAIL",
    "is_balanced": false,
    "inflow": 11310.477371346196,
    "outflow": 10246.896942629857,
    "rel_gap": 0.09403497251237147
  },
  "footprint": {
    "ppr_all": 8698.006193468416,
    "ppr_inner": 8663.728321283294,
    "ppr_pp_only": 8663.728321283294,
    "npp": 11273.056447505951,
    "ppr2npp": 0.7685341026745285,
    "ppr2npp_pp_only": 0.7685341026745285
  },
  "config": {
    "TE_option": "TE",
    "det_open_mode": "none",
    "det_theta": 1.0,
    "det_external_sppr": 0.0,
    "det_collapse_mode": "auto",
    "explicit_TE": false,
    "method": null,
    "would_pool": false,
    "model": "Northern Humboldt Current (1995-1998)"
  },
  "warnings": [
    "model input not mass-balanced: max relative residual 4.22e+03 exceeds fail threshold 0.1",
    "5 group(s) with EE=0 (all production is non-predatory death): 35 (Leatherback turtle), 34 (Green sea turtle), 33 (Cetaceans), 32 (Pinnipeds), 31 (Seabirds). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed",
    "1 group(s) with 0 < EE < 0.001: 7 (Chrysaora plocamia). Their SPPR ~ 1/te is near-singular",
    "TE_option='TE' has no detritus recycling matrix: b reported as 0.0 (mortality-derived SPPR is written off as lost)",
    "rho(A_LL)=0.7316 is within 0.3 of divergence (max SPPR 4.47e+05 at group 25 (Conger), TL 4.12)",
    "1 group(s) have near-zero TE (SPPR ~ 1/te is near-singular): [7]",
    "PP balance gap 9.403% exceeds fail threshold 5.0%"
  ]
}
```

Full returned tuple: [TE/full_return_lossless.json](TE/full_return_lossless.json).
Matrices: [SPPR](TE/SPPR.csv), [A](TE/A.csv), [L](TE/L.csv).

## With Egestion

```json
{
  "status": "FAIL",
  "model_input": {
    "status": "FAIL",
    "is_model_balanced": false,
    "p_max_rel_residual": 4219.15750763535,
    "q_max_rel_residual": 843.8315359765764,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.220446049250313e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 22,
    "total_catch": 35.5395489180725,
    "has_catch": true,
    "has_ee_issues": true,
    "n_ee0": 5,
    "n_ee_marginal": 1,
    "n_ee_gt_1": 0,
    "ee0_groups": [
      35,
      34,
      33,
      32,
      31
    ],
    "ee_marginal_groups": [
      7
    ]
  },
  "divergence": {
    "status": "FAIL",
    "solve_error": null,
    "b": 1.109823001872164,
    "b_converges": false,
    "rho_living": 0.5599999999999999,
    "living_converges": true,
    "sppr_det": {
      "36": 11.00350975195062,
      "37": 11.00350975195062,
      "38": 11.00350975195062,
      "39": 11.00350975195062
    },
    "max_sppr_det": 11.00350975195062,
    "max_sppr_group": {
      "seq": 31,
      "tl": 3.8984436333758534,
      "sppr": 76977.82354942671,
      "inv_te": 1220.0000272691257
    },
    "max_tl_group": {
      "seq": 30,
      "tl": 4.447238103051863,
      "sppr": 1166.9993325390387,
      "inv_te": 5.333332940874769
    },
    "n_negative_sources": 0,
    "expect_negatives": true,
    "near_singular_te": [
      31
    ]
  },
  "balance": {
    "status": "WARN",
    "is_balanced": false,
    "inflow": 11310.477371346196,
    "outflow": 11863.680627176293,
    "rel_gap": 0.048910690297791805
  },
  "footprint": {
    "ppr_all": 3481.1605525961427,
    "ppr_inner": 3474.7874782342146,
    "ppr_pp_only": 578.9405334297008,
    "npp": 11273.056447505951,
    "ppr2npp": 0.3082382754326557,
    "ppr2npp_pp_only": 0.05135612831582916
  },
  "config": {
    "TE_option": "With Egestion",
    "det_open_mode": "none",
    "det_theta": 1.0,
    "det_external_sppr": 0.0,
    "det_collapse_mode": "auto",
    "explicit_TE": false,
    "method": "pooled_detritus_scaling",
    "would_pool": true,
    "model": "Northern Humboldt Current (1995-1998)"
  },
  "warnings": [
    "model input not mass-balanced: max relative residual 4.22e+03 exceeds fail threshold 0.1",
    "5 group(s) with EE=0 (all production is non-predatory death): 35 (Leatherback turtle), 34 (Green sea turtle), 33 (Cetaceans), 32 (Pinnipeds), 31 (Seabirds). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed",
    "1 group(s) with 0 < EE < 0.001: 7 (Chrysaora plocamia). Their SPPR ~ 1/te is near-singular",
    "detritus recycling diverges: b=1.11 >= 1; the SPPR returned is not a convergent sum",
    "max sppr_det=11 >= 10: converged, but detritus is implausibly expensive",
    "1 group(s) have near-zero TE (SPPR ~ 1/te is near-singular): [31]",
    "PP balance gap 4.891% exceeds 1.0%"
  ]
}
```

Full returned tuple: [With_Egestion/full_return_lossless.json](With_Egestion/full_return_lossless.json).
Matrices: [SPPR](With_Egestion/SPPR.csv), [A](With_Egestion/A.csv), [L](With_Egestion/L.csv).
