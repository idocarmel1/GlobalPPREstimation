# LME034 mapping review — final315-label audit

Reference:2019 landings; selected `34_1_Bay_of_Bengal_(1978)`. All315 recorded labels were reassessed, including28 zero-landings labels. The independent simple-chain denominator is379,324,412.0465857tC from6,452,157.579298264t landings. Missing assigned TL occurs for27 labels, all with genuine zero recorded landings and zero annual contribution.

The final proposals change35 eligible group sets and245 allocations;9 aggregate confidence labels change. Overall confidence is66 High,244 Medium,0 Low,5 Very low,0 Unresolved. Each taxon has separate membership and allocation rules; overall confidence is the weaker required component.

| Overall confidence | Taxa | Catch share | Independent simple-chain PPR share |
|---|---:|---:|---:|
| High | 66 | 20.004955% | 24.591019% |
| Medium | 244 | 59.173535% | 67.609999% |
| Low | 0 | 0.000000% | 0.000000% |
| Very low | 5 | 20.821510% | 7.798982% |
| Unresolved | 0 | 0.000000% | 0.000000% |

Very low membership is confined to Marine fishes not identified, Perciformes, Marine pelagic fishes not identified, Scombroidei and Malacostraca. Their candidate sets are meaningful reporting-category approximations, with explicit provider-scope assumptions and model catch proxies. They account for20.821510% of catch and 7.798982% of independent simple-chain PPR.

Species-specific source members were checked against generic genus/family/reporting allocations. These checks add dedicated tuna/marlin pools, explicit small-piscivore/invertebrate-feeder exceptions and cephalopods under Mollusca. Final cross-checks also add L pisc for Batoidea, Elasmobranchii and Chondrichthyes because source Pristis perotteti is a sawfish in that guild, and ML bathy for Anguilliformes because source Nemichthys scolopaceus belongs to that order. These enlarged sets are inferred M9 Medium; Dasyatidae and Rajiformes retain the explicit source two-shark-pool assignment at M1 High membership. Unknown mixture weights remain W4 Medium.

All split allocations use complete finite nonnegative source-model catches and a positive total, under the approved catch-first hierarchy. A2.1 normalizes every group catch by the same6,205,051km² study area, so its ratios equal caught-mass ratios. Each row retains the rounded printed total, canonical export/loaded catch, mass conversion, total and proposed weights. Pooled1978 landings+discards transferred to2019 landings are W4 Medium; they do not qualify as directly observed W10 allocation. The prior deliberate biomass rationale and residual-category identified-taxon catch-composition proxies remain in the old-field ledger.

Region1 shelf-fish pools represent the Maldives shelf outside LME034. Region1 open waters partly overlap its southern extent, so a blanket prefix1 exclusion is unsupported. Excluding1Macrobenthos/1Meiobenthos for landed benthic categories is a coastal-fishery applicability assumption: A1.2 defines them on the full region1area. Malacostraca retains all three Zooplankton candidate pools, including1Zooplankton, with genuine model zero catch and zero weight.

Verified synonyms retain exact catch labels and distinguish same-taxon identity from extensions based on source-listed representatives. Teuthida is treated as squids contained within Cephalopoda (M3), not as a synonym of Loliginidae. No model diet, biomass accumulation or numerical model field was edited by this audit.

| Method, all saved source scopes combined | Baseline PPR(tC) | Proposal PPR(tC) | Change |
|---|---:|---:|---:|
| new_GE | 727715670.608857 | 616708195.384933 | -15.254237% |
| new_TE_EEfix | 1059130737.109631 | 925646019.146273 | -12.603233% |
| new_WithEgestion | 214889388.168609 | 186828362.942845 | -13.058358% |
| SPPR_2015 | 1059130737.109631 | 925646019.146273 | -12.603233% |

These are arithmetic impacts using the saved unrounded group coefficients; they do not represent a new scientific pipeline run. They demonstrate sensitivity to the proposed candidate sets and catch proxies. Source-field audit and actual recalculation remain the parent task’s adoption steps. The generic L pisc catches do not observe sawfish abundance or residual elasmobranch composition.

Source group taxonomy contains exactly49 ecological groups in original sequence order. The separate runtime computational import50 is excluded. A1.1 catch assignments, A1.3 selected composition and A3.1 diet-study examples have separate roles; absent group enumeration is marked not documented. No inferred mapping extensions were inserted into the faithful source taxonomy.

Evidence: [all315 decisions](audit_decisions.json), [readable CSV ledger](audit_decisions.csv), [three-column source taxonomy](taxonomy.csv), [group scope/operative criteria](membership_scope.json), [source transcription](source_pages.txt), [source references and limitations](sources_read.json), [component-rule summary](rule_summary.csv), [source PDF](../../../../../../sources/009031359-84f3dc3d.pdf), [frozen baseline](../baseline_evidence.json).

Verification: [scientific arithmetic and universe checks](verification.json), [portable evidence inventory](evidence_index.json), [inventory check](evidence_index_check.json). These supporting links use repository-relative targets.

Final audit SHA256: `f9d65013d35b99515ba955e4f2652edcec8e23fcdac54bbb3cf8c892764a68c1`. The audit decisions, taxonomy and source-authority records are frozen for adoption.
