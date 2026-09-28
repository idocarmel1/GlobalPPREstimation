# Direct SPPR diagnostics — Visayan Sea 1997

Only full returns from `PPRCalculator.diagnose_sppr(TE_option=..., short=False, flat=False)` are shown below. The exact computational input and defaults are saved beside these returns; source/admission evidence is in the separate extraction report. No global option.

## GE

```json
{
  "status": "WARN",
  "model_input": {
    "status": "WARN",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.009387100591716007,
    "q_max_rel_residual": 0.0043620129341540624,
    "dc_rows_sum_to_1": false,
    "dc_max_deviation": 0.0020000000000000018,
    "n_negative_catch": 0,
    "n_zero_catch": 8,
    "total_catch": 15.159999999999998,
    "has_catch": true,
    "has_ee_issues": false,
    "n_ee0": 0,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [],
    "ee_marginal_groups": []
  },
  "divergence": {
    "status": "OK",
    "solve_error": null,
    "b": 0.23206068027451643,
    "b_converges": true,
    "rho_living": 0.6590909090909091,
    "living_converges": true,
    "sppr_det": {
      "33": 1.7394024286902872
    },
    "max_sppr_det": 1.7394024286902872,
    "max_sppr_group": {
      "seq": 1,
      "tl": 3.614023682650661,
      "sppr": 10537.20394562013,
      "inv_te": 160.0
    },
    "max_tl_group": {
      "seq": 2,
      "tl": 4.074007694948496,
      "sppr": 1088.5272890020003,
      "inv_te": 7.467391304347826
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 2570.7149999999997,
    "outflow": 2578.7102000790474,
    "rel_gap": 0.0031101075300247845
  },
  "footprint": {
    "ppr_all": 1391.244258945492,
    "ppr_inner": 1391.244258945492,
    "ppr_pp_only": 965.197176858884,
    "npp": 2570.7149999999997,
    "ppr2npp": 0.5411896141522853,
    "ppr2npp_pp_only": 0.37545864744200896
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
    "model": "Visayan_Sea_Bacalso_baseline (1997)"
  },
  "warnings": [
    "model input mass-balance residual 0.00939 exceeds 0.0001",
    "diet rows deviate from 1 by up to 0.002 (> 1e-06; ModelData.validate_DC only guards 1e-3)"
  ]
}
```

## TE

```json
{
  "status": "WARN",
  "model_input": {
    "status": "WARN",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.009387100591716007,
    "q_max_rel_residual": 0.0043620129341540624,
    "dc_rows_sum_to_1": false,
    "dc_max_deviation": 0.0020000000000000018,
    "n_negative_catch": 0,
    "n_zero_catch": 8,
    "total_catch": 15.159999999999998,
    "has_catch": true,
    "has_ee_issues": false,
    "n_ee0": 0,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [],
    "ee_marginal_groups": []
  },
  "divergence": {
    "status": "WARN",
    "solve_error": null,
    "b": 0.0,
    "b_converges": true,
    "rho_living": 0.6937799043062202,
    "living_converges": true,
    "sppr_det": {
      "33": 0.4174936764260955
    },
    "max_sppr_det": 0.4174936764260955,
    "max_sppr_group": {
      "seq": 1,
      "tl": 3.614023682650661,
      "sppr": 673074.0763931716,
      "inv_te": 7999.999999999948
    },
    "max_tl_group": {
      "seq": 2,
      "tl": 4.074007694948496,
      "sppr": 5318.321494054711,
      "inv_te": 16.233459357277884
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": [
      1
    ]
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 2570.7149999999997,
    "outflow": 2580.001261465786,
    "rel_gap": 0.0036123263239161416
  },
  "footprint": {
    "ppr_all": 2294.9841123475617,
    "ppr_inner": 2294.9841123475617,
    "ppr_pp_only": 2075.5657582754097,
    "npp": 2570.7149999999997,
    "ppr2npp": 0.8927415572506333,
    "ppr2npp_pp_only": 0.8073885118635905
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
    "model": "Visayan_Sea_Bacalso_baseline (1997)"
  },
  "warnings": [
    "model input mass-balance residual 0.00939 exceeds 0.0001",
    "diet rows deviate from 1 by up to 0.002 (> 1e-06; ModelData.validate_DC only guards 1e-3)",
    "TE_option='TE' has no detritus recycling matrix: b reported as 0.0 (mortality-derived SPPR is written off as lost)",
    "1 group(s) have near-zero TE (SPPR ~ 1/te is near-singular): [1]"
  ]
}
```

## With Egestion

```json
{
  "status": "WARN",
  "model_input": {
    "status": "WARN",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.009387100591716007,
    "q_max_rel_residual": 0.0043620129341540624,
    "dc_rows_sum_to_1": false,
    "dc_max_deviation": 0.0020000000000000018,
    "n_negative_catch": 0,
    "n_zero_catch": 8,
    "total_catch": 15.159999999999998,
    "has_catch": true,
    "has_ee_issues": false,
    "n_ee0": 0,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [],
    "ee_marginal_groups": []
  },
  "divergence": {
    "status": "OK",
    "solve_error": null,
    "b": 0.3392730023673118,
    "b_converges": true,
    "rho_living": 0.5272727272727273,
    "living_converges": true,
    "sppr_det": {
      "33": 2.7302207121384696
    },
    "max_sppr_det": 2.7302207121384696,
    "max_sppr_group": {
      "seq": 1,
      "tl": 3.614023682650661,
      "sppr": 4530.536248032628,
      "inv_te": 128.0
    },
    "max_tl_group": {
      "seq": 2,
      "tl": 4.074007694948496,
      "sppr": 427.0638124314977,
      "inv_te": 5.9739130434782615
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 2570.7149999999997,
    "outflow": 2579.3342295705265,
    "rel_gap": 0.003352853027475563
  },
  "footprint": {
    "ppr_all": 715.4503726973439,
    "ppr_inner": 715.450372697344,
    "ppr_pp_only": 400.2549447703136,
    "npp": 2570.7149999999997,
    "ppr2npp": 0.27830793094424866,
    "ppr2npp_pp_only": 0.15569790691317928
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
    "model": "Visayan_Sea_Bacalso_baseline (1997)"
  },
  "warnings": [
    "model input mass-balance residual 0.00939 exceeds 0.0001",
    "diet rows deviate from 1 by up to 0.002 (> 1e-06; ModelData.validate_DC only guards 1e-3)"
  ]
}
```
