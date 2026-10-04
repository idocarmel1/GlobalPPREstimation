# Full direct diagnostic returns

Authoritative but distinct EcoBase689 native parameterization; not a replacement for published Base/M30/P30. Runtime normalization only; no canonical repair. Direct diagnostics resolve whether native evidence supplies a valid equivalent. Candidate comparison only; no regional adoption.

## GE

```json
{
  "status": "FAIL",
  "model_input": {
    "status": "FAIL",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.11631254219420645,
    "q_max_rel_residual": 0.0158775851249233,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 6.661338147750939e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 18,
    "total_catch": 42.74664403305001,
    "has_catch": true,
    "has_ee_issues": true,
    "n_ee0": 2,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [
      2,
      1
    ],
    "ee_marginal_groups": []
  },
  "divergence": {
    "status": "OK",
    "solve_error": null,
    "b": 0.3640972895879962,
    "b_converges": true,
    "rho_living": 0.5555555333333333,
    "living_converges": true,
    "sppr_det": {
      "51": 1.7021196770842695
    },
    "max_sppr_det": 1.7021196770842695,
    "max_sppr_group": {
      "seq": 1,
      "tl": 3.747957659306951,
      "sppr": 40194.7875060365,
      "inv_te": 311.50000000000006
    },
    "max_tl_group": {
      "seq": 21,
      "tl": 3.9168846793467864,
      "sppr": 1588.7348510187142,
      "inv_te": 7.127659574468085
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 9601.670433240555,
    "outflow": 9597.433065244099,
    "rel_gap": 0.0004413157091694264
  },
  "footprint": {
    "ppr_all": 2164.7537275849527,
    "ppr_inner": 2162.6727290570884,
    "ppr_pp_only": 736.2101757112727,
    "npp": 9598.894487299998,
    "ppr2npp": 0.22530435477944405,
    "ppr2npp_pp_only": 0.07669739225546543
  },
  "config": {
    "TE_option": "GE",
    "det_open_mode": "none",
    "det_theta": 1.0,
    "det_external_sppr": 0.0,
    "det_collapse_mode": "never",
    "explicit_TE": false,
    "method": "single_detritus",
    "would_pool": false,
    "model": "Mauritanie  (1991)"
  },
  "warnings": [
    "model input not mass-balanced: max relative residual 0.116 exceeds fail threshold 0.1",
    "2 group(s) with EE=0 (all production is non-predatory death): 2 (Coastal birds), 1 (Marine mammals). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed"
  ]
}
```

## TE

```json
{
  "status": "FAIL",
  "model_input": {
    "status": "FAIL",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.11631254219420645,
    "q_max_rel_residual": 0.0158775851249233,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 6.661338147750939e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 18,
    "total_catch": 42.74664403305001,
    "has_catch": true,
    "has_ee_issues": true,
    "n_ee0": 2,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [
      2,
      1
    ],
    "ee_marginal_groups": []
  },
  "divergence": {
    "status": "WARN",
    "solve_error": null,
    "b": 0.0,
    "b_converges": true,
    "rho_living": 0.8158013829009628,
    "living_converges": true,
    "sppr_det": {
      "51": 0.4451775683165206
    },
    "max_sppr_det": 0.4451775683165206,
    "max_sppr_group": {
      "seq": 11,
      "tl": 3.6173092409494134,
      "sppr": 368233.2782887242,
      "inv_te": 456.8901316300459
    },
    "max_tl_group": {
      "seq": 21,
      "tl": 3.9168846793467864,
      "sppr": 6759.014230221388,
      "inv_te": 15.253254149729749
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 9601.670433240555,
    "outflow": 9592.613850965312,
    "rel_gap": 0.0009432298617425763
  },
  "footprint": {
    "ppr_all": 30516.65439989721,
    "ppr_inner": 30509.978920550897,
    "ppr_pp_only": 20202.646559344666,
    "npp": 9598.894487299998,
    "ppr2npp": 3.178488831283406,
    "ppr2npp_pp_only": 2.1046847203158827
  },
  "config": {
    "TE_option": "TE",
    "det_open_mode": "none",
    "det_theta": 1.0,
    "det_external_sppr": 0.0,
    "det_collapse_mode": "never",
    "explicit_TE": false,
    "method": null,
    "would_pool": false,
    "model": "Mauritanie  (1991)"
  },
  "warnings": [
    "model input not mass-balanced: max relative residual 0.116 exceeds fail threshold 0.1",
    "2 group(s) with EE=0 (all production is non-predatory death): 2 (Coastal birds), 1 (Marine mammals). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed",
    "TE_option='TE' has no detritus recycling matrix: b reported as 0.0 (mortality-derived SPPR is written off as lost)",
    "rho(A_LL)=0.8158 is within 0.3 of divergence (max SPPR 3.68e+05 at group 11 (Coastal selacians), TL 3.62)"
  ]
}
```

## With Egestion

```json
{
  "status": "FAIL",
  "model_input": {
    "status": "FAIL",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.11631254219420645,
    "q_max_rel_residual": 0.0158775851249233,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 6.661338147750939e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 18,
    "total_catch": 42.74664403305001,
    "has_catch": true,
    "has_ee_issues": true,
    "n_ee0": 2,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [
      2,
      1
    ],
    "ee_marginal_groups": []
  },
  "divergence": {
    "status": "OK",
    "solve_error": null,
    "b": 0.41677945648220915,
    "b_converges": true,
    "rho_living": 0.4444444266666666,
    "living_converges": true,
    "sppr_det": {
      "51": 1.9418030645386792
    },
    "max_sppr_det": 1.9418030645386792,
    "max_sppr_group": {
      "seq": 1,
      "tl": 3.747957659306951,
      "sppr": 16723.678838726944,
      "inv_te": 249.20000000000002
    },
    "max_tl_group": {
      "seq": 21,
      "tl": 3.9168846793467864,
      "sppr": 683.8496495233701,
      "inv_te": 5.702127659574468
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 9601.670433240555,
    "outflow": 9599.763617362732,
    "rel_gap": 0.0001985920982271403
  },
  "footprint": {
    "ppr_all": 1080.9650466149944,
    "ppr_inner": 1079.408992174408,
    "ppr_pp_only": 320.7101662745479,
    "npp": 9598.894487299998,
    "ppr2npp": 0.11245138631355317,
    "ppr2npp_pp_only": 0.033411156534626944
  },
  "config": {
    "TE_option": "With Egestion",
    "det_open_mode": "none",
    "det_theta": 1.0,
    "det_external_sppr": 0.0,
    "det_collapse_mode": "never",
    "explicit_TE": false,
    "method": "single_detritus",
    "would_pool": false,
    "model": "Mauritanie  (1991)"
  },
  "warnings": [
    "model input not mass-balanced: max relative residual 0.116 exceeds fail threshold 0.1",
    "2 group(s) with EE=0 (all production is non-predatory death): 2 (Coastal birds), 1 (Marine mammals). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed"
  ]
}
```