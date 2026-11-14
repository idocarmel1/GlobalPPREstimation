# EE floor ON: direct diagnostics

Exact model: `941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)`; EE floor and threshold 0.1. This review evidence does not adopt results or register a researcher decision.

The retained September 28 loader and settings initialize the current canonical bytes. The pre-floor group table, diets and routing match the retained audited state within 1e-12; current floor accounting is then applied once. The scoped compatibility audit excludes the changed legacy SPPR_1995 method, which is not used by these direct diagnostics. See [configuration and code identity](run_provenance.json) and [scoped dependency check](scoped_compatibility.json).

Source M0 qualification: canonical `other_mort` values remain missing sentinels. The engine ledger field `source_M0` is a ModelData-derived value, not an independently published mortality observation. Canonical source missingness is retained in [source mortality provenance](source_mortality_provenance.json).

## GE

Full direct return (no interpretation removed):

```json
{
  "status": "WARN",
  "model_input": {
    "status": "WARN",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.007279402209226768,
    "q_max_rel_residual": 0.00046102880658427267,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.220446049250313e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 21,
    "total_catch": 0.05402029999999999,
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
    "external_mortality_export": 0.0008174999999999997,
    "negative_detritus_stock_residuals": {}
  },
  "divergence": {
    "status": "OK",
    "solve_error": null,
    "b": 0.629379721549255,
    "b_converges": true,
    "rho_living": 0.5467665518138085,
    "living_converges": true,
    "sppr_det": {
      "type": "mapping",
      "items": [
        [
          31,
          2.506075940943192
        ]
      ]
    },
    "max_sppr_det": 2.506075940943192,
    "max_sppr_group": {
      "seq": 4,
      "tl": 5.500979585206764,
      "sppr": 75957.82254528154,
      "inv_te": 10.0
    },
    "max_tl_group": {
      "seq": 2,
      "tl": 5.527371025227983,
      "sppr": 41767.08245465415,
      "inv_te": 8.333333333333332
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 1097.9547,
    "outflow": 1096.9021126216333,
    "rel_gap": 0.0009586801517100405
  },
  "footprint": {
    "ppr_all": 548.862183855993,
    "ppr_inner": 548.862183855993,
    "ppr_pp_only": 163.861495457781,
    "npp": 1097.9547,
    "ppr2npp": 0.49989510847395885,
    "ppr2npp_pp_only": 0.1492424919332109
  },
  "config": {
    "use_ee_floor": true,
    "ee_floor": 0.1,
    "ee_threshold": 0.1,
    "ee_floor_assumption": {
      "use_ee_floor": true,
      "ee_floor": 0.1,
      "ee_threshold": 0.1,
      "affected_groups": [
        10,
        3,
        2,
        1
      ],
      "external_mortality_export_total": 0.0008174999999999997,
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
    "method": "single_detritus",
    "would_pool": false,
    "model": "WCPO_Warm_Pool_Option1 (mixed_periods)"
  },
  "warnings": [
    "model input mass-balance residual 0.00728 exceeds 0.0001"
  ]
}
```

[Lossless return, all matrices and runtime state](new_GE_full_return.json.gz)

[Standalone SPPR matrix with ordered axes and missingness masks](new_GE_SPPR_matrix.json)

## TE

Full direct return (no interpretation removed):

```json
{
  "status": "WARN",
  "model_input": {
    "status": "WARN",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.007279402209226768,
    "q_max_rel_residual": 0.00046102880658427267,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.220446049250313e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 21,
    "total_catch": 0.05402029999999999,
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
    "external_mortality_export": 0.0008174999999999997,
    "negative_detritus_stock_residuals": {}
  },
  "divergence": {
    "status": "WARN",
    "solve_error": null,
    "b": 0.0,
    "b_converges": true,
    "rho_living": 0.7249377689422032,
    "living_converges": true,
    "sppr_det": {
      "type": "mapping",
      "items": [
        [
          31,
          0.2525090684652693
        ]
      ]
    },
    "max_sppr_det": 0.2525090684652693,
    "max_sppr_group": {
      "seq": 9,
      "tl": 5.147940816254866,
      "sppr": 611365.9722866042,
      "inv_te": 87.71929824561403
    },
    "max_tl_group": {
      "seq": 2,
      "tl": 5.527371025227983,
      "sppr": 460818.46552095417,
      "inv_te": 83.33333333333334
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 1097.9547,
    "outflow": 1096.7050820463169,
    "rel_gap": 0.001138132523758155
  },
  "footprint": {
    "ppr_all": 769.572033987903,
    "ppr_inner": 769.572033987903,
    "ppr_pp_only": 622.9323073012674,
    "npp": 1097.9547,
    "ppr2npp": 0.700914194354196,
    "ppr2npp_pp_only": 0.5673570205594707
  },
  "config": {
    "use_ee_floor": true,
    "ee_floor": 0.1,
    "ee_threshold": 0.1,
    "ee_floor_assumption": {
      "use_ee_floor": true,
      "ee_floor": 0.1,
      "ee_threshold": 0.1,
      "affected_groups": [
        10,
        3,
        2,
        1
      ],
      "external_mortality_export_total": 0.0008174999999999997,
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
    "method": null,
    "would_pool": false,
    "model": "WCPO_Warm_Pool_Option1 (mixed_periods)"
  },
  "warnings": [
    "model input mass-balance residual 0.00728 exceeds 0.0001",
    "TE_option='TE' has no detritus recycling matrix: b reported as 0.0 (mortality-derived SPPR is written off as lost)",
    "rho(A_LL)=0.7249 is within 0.3 of divergence (max SPPR 6.11e+05 at group 9 (Small Billfish), TL 5.15)"
  ]
}
```

[Lossless return, all matrices and runtime state](new_TE_EEfix_full_return.json.gz)

[Standalone SPPR matrix with ordered axes and missingness masks](new_TE_EEfix_SPPR_matrix.json)

## With Egestion

Full direct return (no interpretation removed):

```json
{
  "status": "WARN",
  "model_input": {
    "status": "WARN",
    "is_model_balanced": false,
    "p_max_rel_residual": 0.007279402209226768,
    "q_max_rel_residual": 0.00046102880658427267,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.220446049250313e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 21,
    "total_catch": 0.05402029999999999,
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
    "external_mortality_export": 0.0008174999999999997,
    "negative_detritus_stock_residuals": {}
  },
  "divergence": {
    "status": "WARN",
    "solve_error": null,
    "b": 0.761378511750852,
    "b_converges": true,
    "rho_living": 0.4374132414510465,
    "living_converges": true,
    "sppr_det": {
      "type": "mapping",
      "items": [
        [
          31,
          4.520427186069605
        ]
      ]
    },
    "max_sppr_det": 4.520427186069605,
    "max_sppr_group": {
      "seq": 4,
      "tl": 5.500979585206764,
      "sppr": 16117.759850065291,
      "inv_te": 8.000000000000002
    },
    "max_tl_group": {
      "seq": 2,
      "tl": 5.527371025227983,
      "sppr": 10599.415996137604,
      "inv_te": 6.666666666666666
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 1097.9547,
    "outflow": 1097.686760472949,
    "rel_gap": 0.00024403513829041601
  },
  "footprint": {
    "ppr_all": 151.37044819617512,
    "ppr_inner": 151.37044819617515,
    "ppr_pp_only": 21.880340489110615,
    "npp": 1097.9547,
    "ppr2npp": 0.13786584109178196,
    "ppr2npp_pp_only": 0.019928272531745266
  },
  "config": {
    "use_ee_floor": true,
    "ee_floor": 0.1,
    "ee_threshold": 0.1,
    "ee_floor_assumption": {
      "use_ee_floor": true,
      "ee_floor": 0.1,
      "ee_threshold": 0.1,
      "affected_groups": [
        10,
        3,
        2,
        1
      ],
      "external_mortality_export_total": 0.0008174999999999997,
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
    "method": "single_detritus",
    "would_pool": false,
    "model": "WCPO_Warm_Pool_Option1 (mixed_periods)"
  },
  "warnings": [
    "model input mass-balance residual 0.00728 exceeds 0.0001",
    "b=0.7614 is within 0.3 of divergence (max sppr_det 4.52 PP-units per unit detritus)"
  ]
}
```

[Lossless return, all matrices and runtime state](new_WithEgestion_full_return.json.gz)

[Standalone SPPR matrix with ordered axes and missingness masks](new_WithEgestion_SPPR_matrix.json)
