# Full direct diagnostic returns

## GE

```json
{
  "status": "FAIL",
  "model_input": {
    "status": "FAIL",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.8073177993064805,
    "q_max_rel_residual": 0.8073177993064805,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.2099999985591978e-07,
    "n_negative_catch": 0,
    "n_zero_catch": 15,
    "total_catch": 1.4381429207,
    "has_catch": true,
    "has_ee_issues": false,
    "n_ee0": 0,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [],
    "ee_marginal_groups": [],
    "diagnostic_basis": "effective calculation runtime",
    "before_floor_ee0_groups": [],
    "before_floor_ee_marginal_groups": [],
    "external_mortality_export": 0.0,
    "negative_detritus_stock_residuals": {}
  },
  "divergence": {
    "status": "WARN",
    "solve_error": null,
    "b": 0.4090673647283584,
    "b_converges": true,
    "rho_living": 0.26659952990268,
    "living_converges": true,
    "sppr_det": {
      "type": "mapping",
      "items": [
        [
          48,
          1.6440119304868739
        ],
        [
          49,
          1.8374194799762382
        ]
      ]
    },
    "max_sppr_det": 1.8374194799762382,
    "max_sppr_group": {
      "seq": 5,
      "tl": 4.614422446307798,
      "sppr": 191829.4348451434,
      "inv_te": 1125.1742478749622
    },
    "max_tl_group": {
      "seq": 1,
      "tl": 4.66233080093115,
      "sppr": 27116.370245501552,
      "inv_te": 263.87580348393647
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": [
      9,
      5
    ]
  },
  "balance": {
    "status": "FAIL",
    "is_balanced": false,
    "inflow": 4451.953547222999,
    "outflow": -26.226039466964746,
    "rel_gap": 1.0058909059110295
  },
  "footprint": {
    "ppr_all": 450.30747476608224,
    "ppr_inner": 450.30747476608224,
    "ppr_pp_only": 151.24233657263636,
    "npp": 4451.953547222999,
    "ppr2npp": 0.1011482869238317,
    "ppr2npp_pp_only": 0.03397212818336278
  },
  "config": {
    "use_ee_floor": true,
    "ee_floor": 0.1,
    "ee_threshold": 0.1,
    "ee_floor_assumption": {
      "use_ee_floor": true,
      "ee_floor": 0.1,
      "ee_threshold": 0.1,
      "affected_groups": [],
      "external_mortality_export_total": 0.0,
      "negative_detritus_stock_residuals": {},
      "assumption": "Hypothetical non-fishery external mortality sink; not a published parameter correction",
      "application_stage": "completed audited initialization",
      "researcher_approval": "Original signed review is separate from this calculation assumption"
    },
    "TE_option": "GE",
    "det_open_mode": "none",
    "det_theta": 1.0,
    "det_external_sppr": 0.0,
    "det_collapse_mode": "never",
    "explicit_TE": false,
    "method": "multi_detritus",
    "would_pool": false,
    "model": "Gulf of Alaska (1990-1994)"
  },
  "warnings": [
    "model input not mass-balanced: max relative residual 0.807 exceeds fail threshold 0.1",
    "2 group(s) have near-zero TE (SPPR ~ 1/te is near-singular): [9, 5]",
    "PP balance gap 100.589% exceeds fail threshold 5.0%"
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
    "p_max_rel_residual": 0.8073177993064805,
    "q_max_rel_residual": 0.8073177993064805,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.2099999985591978e-07,
    "n_negative_catch": 0,
    "n_zero_catch": 15,
    "total_catch": 1.4381429207,
    "has_catch": true,
    "has_ee_issues": false,
    "n_ee0": 0,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [],
    "ee_marginal_groups": [],
    "diagnostic_basis": "effective calculation runtime",
    "before_floor_ee0_groups": [],
    "before_floor_ee_marginal_groups": [],
    "external_mortality_export": 0.0,
    "negative_detritus_stock_residuals": {}
  },
  "divergence": {
    "status": "WARN",
    "solve_error": null,
    "b": 0.2672886407947974,
    "b_converges": true,
    "rho_living": 0.9766894020612613,
    "living_converges": true,
    "sppr_det": {
      "type": "mapping",
      "items": [
        [
          48,
          1.2167191798665116
        ],
        [
          49,
          1.4143535701610244
        ]
      ]
    },
    "max_sppr_det": 1.4143535701610244,
    "max_sppr_group": {
      "seq": 1,
      "tl": 4.66233080093115,
      "sppr": 852777853.9355636,
      "inv_te": 18354.683192912526
    },
    "max_tl_group": {
      "seq": 1,
      "tl": 4.66233080093115,
      "sppr": 852777853.9355636,
      "inv_te": 18354.683192912526
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": [
      39,
      35,
      10,
      9,
      8,
      7,
      6,
      5,
      4,
      3,
      2,
      1
    ]
  },
  "balance": {
    "status": "FAIL",
    "is_balanced": false,
    "inflow": 4451.953547222999,
    "outflow": 1083.206401978454,
    "rel_gap": 0.7566896441104767
  },
  "footprint": {
    "ppr_all": 3828.8116318063253,
    "ppr_inner": 3828.8116318063257,
    "ppr_pp_only": 1599.3668489069566,
    "npp": 4451.953547222999,
    "ppr2npp": 0.8600295558327711,
    "ppr2npp_pp_only": 0.3592505698772611
  },
  "config": {
    "use_ee_floor": true,
    "ee_floor": 0.1,
    "ee_threshold": 0.1,
    "ee_floor_assumption": {
      "use_ee_floor": true,
      "ee_floor": 0.1,
      "ee_threshold": 0.1,
      "affected_groups": [],
      "external_mortality_export_total": 0.0,
      "negative_detritus_stock_residuals": {},
      "assumption": "Hypothetical non-fishery external mortality sink; not a published parameter correction",
      "application_stage": "completed audited initialization",
      "researcher_approval": "Original signed review is separate from this calculation assumption"
    },
    "TE_option": "TE",
    "det_open_mode": "none",
    "det_theta": 1.0,
    "det_external_sppr": 0.0,
    "det_collapse_mode": "never",
    "explicit_TE": false,
    "method": "multi_detritus",
    "would_pool": false,
    "model": "Gulf of Alaska (1990-1994)"
  },
  "warnings": [
    "model input not mass-balanced: max relative residual 0.807 exceeds fail threshold 0.1",
    "rho(A_LL)=0.9767 is within 0.3 of divergence (max SPPR 8.53e+08 at group 1 (Toothed whales), TL 4.66)",
    "12 group(s) have near-zero TE (SPPR ~ 1/te is near-singular): [39, 35, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]",
    "PP balance gap 75.669% exceeds fail threshold 5.0%"
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
    "p_max_rel_residual": 0.8073177993064805,
    "q_max_rel_residual": 0.8073177993064805,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.2099999985591978e-07,
    "n_negative_catch": 0,
    "n_zero_catch": 15,
    "total_catch": 1.4381429207,
    "has_catch": true,
    "has_ee_issues": false,
    "n_ee0": 0,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [],
    "ee_marginal_groups": [],
    "diagnostic_basis": "effective calculation runtime",
    "before_floor_ee0_groups": [],
    "before_floor_ee_marginal_groups": [],
    "external_mortality_export": 0.0,
    "negative_detritus_stock_residuals": {}
  },
  "divergence": {
    "status": "OK",
    "solve_error": null,
    "b": 0.44064592215477894,
    "b_converges": true,
    "rho_living": 0.213279623922144,
    "living_converges": true,
    "sppr_det": {
      "type": "mapping",
      "items": [
        [
          48,
          1.5978036612968898
        ],
        [
          49,
          1.9048677640184206
        ]
      ]
    },
    "max_sppr_det": 1.9048677640184206,
    "max_sppr_group": {
      "seq": 5,
      "tl": 4.614422446307798,
      "sppr": 56821.36753124157,
      "inv_te": 900.1393982999698
    },
    "max_tl_group": {
      "seq": 1,
      "tl": 4.66233080093115,
      "sppr": 8719.685485000828,
      "inv_te": 211.1006427871492
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "FAIL",
    "is_balanced": false,
    "inflow": 4451.953547222999,
    "outflow": -19.427684104302582,
    "rel_gap": 1.0043638559787806
  },
  "footprint": {
    "ppr_all": 159.20959894361866,
    "ppr_inner": 159.2095989436187,
    "ppr_pp_only": 59.211975125961224,
    "npp": 4451.953547222999,
    "ppr2npp": 0.03576173858393673,
    "ppr2npp_pp_only": 0.013300223036445642
  },
  "config": {
    "use_ee_floor": true,
    "ee_floor": 0.1,
    "ee_threshold": 0.1,
    "ee_floor_assumption": {
      "use_ee_floor": true,
      "ee_floor": 0.1,
      "ee_threshold": 0.1,
      "affected_groups": [],
      "external_mortality_export_total": 0.0,
      "negative_detritus_stock_residuals": {},
      "assumption": "Hypothetical non-fishery external mortality sink; not a published parameter correction",
      "application_stage": "completed audited initialization",
      "researcher_approval": "Original signed review is separate from this calculation assumption"
    },
    "TE_option": "With Egestion",
    "det_open_mode": "none",
    "det_theta": 1.0,
    "det_external_sppr": 0.0,
    "det_collapse_mode": "never",
    "explicit_TE": false,
    "method": "multi_detritus",
    "would_pool": false,
    "model": "Gulf of Alaska (1990-1994)"
  },
  "warnings": [
    "model input not mass-balanced: max relative residual 0.807 exceeds fail threshold 0.1",
    "PP balance gap 100.436% exceeds fail threshold 5.0%"
  ]
}
```
