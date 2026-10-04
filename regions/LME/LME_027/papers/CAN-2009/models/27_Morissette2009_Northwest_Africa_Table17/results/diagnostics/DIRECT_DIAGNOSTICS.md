# Direct diagnostics of the official native companion

This is EcoBase118, source-audited against Table17, not a distinct replacement. The paper-only reconstruction remains NOT_RUN.

## GE

```json
{
  "status": "WARN",
  "model_input": {
    "status": "WARN",
    "is_model_balanced": false,
    "p_max_rel_residual": 1.651894153799687e-05,
    "q_max_rel_residual": 1.651894153799687e-05,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.220446049250313e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 16,
    "total_catch": 0.5164791377,
    "has_catch": true,
    "has_ee_issues": true,
    "n_ee0": 10,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [
      11,
      9,
      8,
      7,
      6,
      5,
      4,
      3,
      2,
      1
    ],
    "ee_marginal_groups": []
  },
  "divergence": {
    "status": "OK",
    "solve_error": null,
    "b": 0.3694082945710039,
    "b_converges": true,
    "rho_living": 0.16615874785448084,
    "living_converges": true,
    "sppr_det": {
      "27": 2.097497839630072
    },
    "max_sppr_det": 2.097497839630072,
    "max_sppr_group": {
      "seq": 9,
      "tl": 3.938113389450028,
      "sppr": 756531.9820485468,
      "inv_te": 388.16999999999996
    },
    "max_tl_group": {
      "seq": 7,
      "tl": 4.199027795682816,
      "sppr": 15651.792880153253,
      "inv_te": 275.65
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 12460.853469902122,
    "outflow": 12459.813735932821,
    "rel_gap": 8.344002855119328e-05
  },
  "footprint": {
    "ppr_all": 12.299820660231267,
    "ppr_inner": 12.299820660231267,
    "ppr_pp_only": 9.862088187769473,
    "npp": 12460.712646,
    "ppr2npp": 0.0009870880590589352,
    "ppr2npp_pp_only": 0.0007914545875460254
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
    "model": "official_EcoBase118 (nan)"
  },
  "warnings": [
    "10 group(s) with EE=0 (all production is non-predatory death): 11 (Seabirds), 9 (Killer whales), 8 (Sperm whales), 7 (Beaked whales), 6 (Baleen whales), 5 (Sei whales), 4 (Brydes whales), 3 (Humpback whales), 2 (Fin whales), 1 (Minke whales). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed"
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
    "p_max_rel_residual": 1.651894153799687e-05,
    "q_max_rel_residual": 1.651894153799687e-05,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.220446049250313e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 16,
    "total_catch": 0.5164791377,
    "has_catch": true,
    "has_ee_issues": true,
    "n_ee0": 10,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [
      11,
      9,
      8,
      7,
      6,
      5,
      4,
      3,
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
    "rho_living": 0.9907169786465047,
    "living_converges": true,
    "sppr_det": {
      "27": 1.6080319213502223
    },
    "max_sppr_det": 1.6080319213502223,
    "max_sppr_group": {
      "seq": 13,
      "tl": 3.9298839512443298,
      "sppr": 2774448.0998087376,
      "inv_te": 61.919811165406536
    },
    "max_tl_group": {
      "seq": 7,
      "tl": 4.199027795682816,
      "sppr": 0.0,
      "inv_te": null
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": [
      17
    ]
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 12460.853469902122,
    "outflow": 12461.120119854315,
    "rel_gap": 2.1399011940631314e-05
  },
  "footprint": {
    "ppr_all": 2918.3213912799083,
    "ppr_inner": 2918.3213912799083,
    "ppr_pp_only": 1598.02296164768,
    "npp": 12460.712646,
    "ppr2npp": 0.2342018048395262,
    "ppr2npp_pp_only": 0.12824490918347753
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
    "model": "official_EcoBase118 (nan)"
  },
  "warnings": [
    "10 group(s) with EE=0 (all production is non-predatory death): 11 (Seabirds), 9 (Killer whales), 8 (Sperm whales), 7 (Beaked whales), 6 (Baleen whales), 5 (Sei whales), 4 (Brydes whales), 3 (Humpback whales), 2 (Fin whales), 1 (Minke whales). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed",
    "TE_option='TE' has no detritus recycling matrix: b reported as 0.0 (mortality-derived SPPR is written off as lost)",
    "rho(A_LL)=0.9907 is within 0.3 of divergence (max SPPR 2.77e+06 at group 13 (Mesopelagic predators), TL 3.93)",
    "1 group(s) have near-zero TE (SPPR ~ 1/te is near-singular): [17]"
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
    "p_max_rel_residual": 1.651894153799687e-05,
    "q_max_rel_residual": 1.651894153799687e-05,
    "dc_rows_sum_to_1": true,
    "dc_max_deviation": 2.220446049250313e-16,
    "n_negative_catch": 0,
    "n_zero_catch": 16,
    "total_catch": 0.5164791377,
    "has_catch": true,
    "has_ee_issues": true,
    "n_ee0": 10,
    "n_ee_marginal": 0,
    "n_ee_gt_1": 0,
    "ee0_groups": [
      11,
      9,
      8,
      7,
      6,
      5,
      4,
      3,
      2,
      1
    ],
    "ee_marginal_groups": []
  },
  "divergence": {
    "status": "OK",
    "solve_error": null,
    "b": 0.3694662733647247,
    "b_converges": true,
    "rho_living": 0.13292699828358467,
    "living_converges": true,
    "sppr_det": {
      "27": 2.0983746042926557
    },
    "max_sppr_det": 2.0983746042926557,
    "max_sppr_group": {
      "seq": 9,
      "tl": 3.938113389450028,
      "sppr": 310395.1437024966,
      "inv_te": 310.53599999999994
    },
    "max_tl_group": {
      "seq": 7,
      "tl": 4.199027795682816,
      "sppr": 6826.030010911733,
      "inv_te": 220.52
    },
    "n_negative_sources": 0,
    "expect_negatives": false,
    "near_singular_te": []
  },
  "balance": {
    "status": "OK",
    "is_balanced": false,
    "inflow": 12460.853469902122,
    "outflow": 12460.310886433252,
    "rel_gap": 4.354304223068788e-05
  },
  "footprint": {
    "ppr_all": 7.593847642852181,
    "ppr_inner": 7.593847642852179,
    "ppr_pp_only": 6.185322617456396,
    "npp": 12460.712646,
    "ppr2npp": 0.0006094232214952707,
    "ppr2npp_pp_only": 0.000496385944622673
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
    "model": "official_EcoBase118 (nan)"
  },
  "warnings": [
    "10 group(s) with EE=0 (all production is non-predatory death): 11 (Seabirds), 9 (Killer whales), 8 (Sperm whales), 7 (Beaked whales), 6 (Baleen whales), 5 (Sei whales), 4 (Brydes whales), 3 (Humpback whales), 2 (Fin whales), 1 (Minke whales). Under TE_option='TE' their TE row is 0, which severs them from the nullspace and leaks the PP they consumed"
  ]
}
```