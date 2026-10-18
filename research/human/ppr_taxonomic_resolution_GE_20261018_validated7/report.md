# GE PPR at taxon resolution: current validated cohort

This successor analysis uses the current exact validated cohort following withdrawal of researcher validation for `(LME_028, 28_646_Guinea_(1998))`. The earlier 16 October studies remain historical and unchanged. The active review decision determines cohort membership; it does not alter saved model inputs, coefficients, numerical diagnostics or method eligibility.

The reconstructed GE baseline is **1.038932 billion tC**. The within-ecosystem catch-weighted, review-included and all-consumer scenarios produce **1.440976**, **1.566564** and **1.788421 billion tC**, respectively: factors of **1.386978**, **1.507860** and **1.721404** relative to baseline. These are conditional arithmetic projections, not confidence bounds, a measured world total, or a reconstructed taxon food web.

## Scope and evidence

The [cohort manifest](inputs/cohort.json) binds **7 exact model-region pairs** to the final Project fingerprint and actual signed review identities: HS_077, LME_013, LME_032, LME_034, LME_035, LME_036, LME_047. The withdrawn Guinea pair is excluded from all calibration, allocation, scenario and influence calculations in this successor. The 1985 Guinea candidate is not substituted. Separate upstream reference overlays remain context only and are not fitted observations or catch contributors.

All totals use **2019 total catch including discards**, **all basal sources**, unidentified treatment **method**, saved `new_GE` coefficients, and the remaining models' signed-review default group exclusions. Original allocation shares are retained; excluded shares are not redistributed. The comparison contains **39,684,336.471269 tonnes** of allocated catch, **165 catch-bearing groups**, **1,693 region–taxon records**, and **2,624 taxon–group allocations**. Region–taxon records are not distinct biological species: taxa can recur across ecosystems and include broader catch categories.

The source experiment supplies 219 consumer-group coefficients. 219 are positive and enter log fits; zero-valued coefficients: 0. The review-included positive calibration sample has 202 groups. Expected counts come from the new upstream records and aggregation package, then are independently checked against current published taxon allocations. [The count manifest](inputs/sample_manifest.json) is evidence for this cohort, not a reusable hardcoded sample size.

Taxon TL is `1 + log10(saved simple_sppr)`. Model-group TL is `1 + log10(saved SPPR_1995_TE0.1)`, retaining the cycle-pruned/detritus-basal effective coordinate. It is not silently replaced with the ordinary displayed model TL. Treating the two TL conventions as comparable is an explicit projection assumption.

## Reconstruction and conditional prediction

Let `c_ig` be catch allocated to group `g`, `C_g = sum_i c_ig`, `S_g` its saved GE coefficient, `T_i` taxon TL and `T_g` effective group TL. The project carbon conversion gives `PPR0 = sum_g(C_g S_g)/9`.

The anchored projection is `s_ig(b) = S_g × 10^[b(T_i − T_g)]`. It retains each observed group coefficient, including its departure from the descriptive regression line. It assumes that a slope observed between functional groups also applies to taxa within those groups. Neither the regression nor this calculation establishes that assumption.

With allocation shares `q_ig = c_ig/C_g` and mean taxon TL `mu_g = sum_i q_ig T_i`, the exact multiplier is:

`R_g(b) = 10^[b(mu_g − T_g)] × sum_i q_ig 10^[b(T_i − mu_g)]`.

The first factor is the mean TL shift. The second is centered Jensen curvature, at least one. The full total is the sum of `c_ig S_g 10^[b(T_i − T_g)]/9` over actual allocations. A mean shift may be negative, so convexity alone does not guarantee that the full total exceeds baseline. Group factors must be weighted by this method's own baseline PPR contributions `C_g S_g / sum_h C_h S_h`.

This calculation does not rerun diets, mortality, detritus recycling, efficiency or feedback equations, and does not enforce flow balance in a finer network. A group network can already contain the cost of mixed diets: for two equally weighted terminal consumers with costs 10 and 100, a correctly aggregated linear diet calculation may already retain their mean cost 55, while the classic coefficient at mean TL is only 31.62. Thus an exponential TL projection is a sensitivity assumption, not a universal correction for network aggregation.

The fitted response is log SPPR. Anchoring retains each existing group residual, so no additional residual-smearing multiplier is applied; that would count the same observed group heterogeneity again. Unknown within-group residual variation remains unidentified. Scenario spread is not an estimated distribution of ecological true PPR.

## Numerical results

| Saved-coefficient reconstruction | Billion tC |
|---|---|
| Grouped classic | 1.576233 |
| Taxon simple chain | 2.917923 |
| GE baseline | 1.038932 |

| Conditional scenario | Slope b | Billion tC | Factor over baseline |
|---|---|---|---|
| Retain group coefficients | 0.000000 | 1.038932 | 1.000000 |
| Unit slope b=1 | 1.000000 | 1.664049 | 1.601692 |
| All positive consumers, pooled ecosystems | 1.110747 | 1.870813 | 1.800708 |
| All positive consumers, within ecosystems | 1.069806 | 1.788421 | 1.721404 |
| Review-included consumers, pooled ecosystems | 0.986958 | 1.642848 | 1.581286 |
| Review-included consumers, within ecosystems | 0.936707 | 1.566564 | 1.507860 |
| Catch-bearing groups, equal weights, pooled ecosystems | 0.966898 | 1.611395 | 1.551011 |
| Catch-bearing groups, equal weights, within ecosystems | 0.863233 | 1.468946 | 1.413900 |
| Catch weights, pooled ecosystems | 0.930752 | 1.558062 | 1.499677 |
| Catch weights, within ecosystems | 0.839840 | 1.440976 | 1.386978 |
| PPR weights; stress test, pooled ecosystems | 0.860317 | 1.465382 | 1.410470 |
| PPR weights; stress test, within ecosystems | 0.851536 | 1.454783 | 1.400268 |

All 12 scenarios use identical catch support. The pooled and within fits are recomputed from the new cohort rather than subtracting Guinea from an old fitted result. PPR weighting uses the response itself and is retained as an influence stress test, not a preferred estimator.

![Conditional total PPR](results/conditional_totals.png)

At fixed slope b=1, the full factor is **1.601692**, decomposing sequentially into a mean-shift factor **1.305017** and additional dispersion factor **1.227334**. The centered-Jensen-only factor **1.242896** answers a different question because it omits mean shifts. The sequential full/shift decomposition is not the product of independently averaged group factors.

## Refitted descriptive relationships

Five calibration choices are retained: all positive consumers, review-included consumers, catch-bearing groups with equal weights, catch weights and method-specific PPR weights. Pooled regressions fit one intercept; within regressions fit an intercept per ecosystem; between regressions fit one weighted centroid per ecosystem with equal weight per ecosystem. These are descriptions of functional groups, not independent-species regressions.

| Calibration and design | Slope | R² | Observations | Models |
|---|---|---|---|---|
| All positive consumers, pooled ecosystems | 1.110747 | 0.739297 | 219 | 7 |
| All positive consumers, within ecosystems | 1.069806 | 0.717984 | 219 | 7 |
| All positive consumers, between ecosystems | 1.277333 | 0.804214 | 7 | 7 |
| Review-included consumers, pooled ecosystems | 0.986958 | 0.795212 | 202 | 7 |
| Review-included consumers, within ecosystems | 0.936707 | 0.839809 | 202 | 7 |
| Review-included consumers, between ecosystems | 1.213873 | 0.742801 | 7 | 7 |
| Catch-bearing groups, equal weights, pooled ecosystems | 0.966898 | 0.804401 | 165 | 7 |
| Catch-bearing groups, equal weights, within ecosystems | 0.863233 | 0.837471 | 165 | 7 |
| Catch-bearing groups, equal weights, between ecosystems | 1.191261 | 0.806940 | 7 | 7 |
| Catch weights, pooled ecosystems | 0.930752 | 0.726314 | 165 | 7 |
| Catch weights, within ecosystems | 0.839840 | 0.885984 | 165 | 7 |
| Catch weights, between ecosystems | 1.034664 | 0.822692 | 7 | 7 |
| PPR weights; stress test, pooled ecosystems | 0.860317 | 0.792323 | 165 | 7 |
| PPR weights; stress test, within ecosystems | 0.851536 | 0.795297 | 165 | 7 |
| PPR weights; stress test, between ecosystems | 1.179494 | 0.837073 | 7 | 7 |

![Refitted trophic-level associations](results/tl_associations.png)

There are 7 food webs, not 219 independent ecosystem replicates. A positive TL association does not identify a universal transfer efficiency, a causal within-group slope or feedback omitted by the cycle-pruned TL coordinate.

## Leave-one-model-out calibration sensitivity

Each refit omits one model from calibration, then applies that slope to the same full current 7-model catch support. It does not remove the held-out model's catch from the scenario. The 70 refits and 21 per-model fits are saved in [regressions.json](results/regressions.json).

| Fit | Omission-refitted slope range | Full-cohort scenario range, billion tC |
|---|---|---|
| All positive consumers, pooled ecosystems | 1.083278–1.132110 | 1.814709–1.916895 |
| All positive consumers, within ecosystems | 1.043548–1.087058 | 1.739382–1.822225 |
| Catch weights, pooled ecosystems | 0.900125–0.963848 | 1.516027–1.606731 |
| Catch weights, within ecosystems | 0.793631–0.870990 | 1.389710–1.478536 |
| PPR weights; stress test, pooled ecosystems | 0.807802–0.968582 | 1.404890–1.613982 |
| PPR weights; stress test, within ecosystems | 0.826094–0.862568 | 1.425187–1.468130 |
| Catch-bearing groups, equal weights, pooled ecosystems | 0.941090–0.992798 | 1.572892–1.652268 |
| Catch-bearing groups, equal weights, within ecosystems | 0.834888–0.887708 | 1.435234–1.499760 |
| Review-included consumers, pooled ecosystems | 0.973497–1.002252 | 1.621591–1.667771 |
| Review-included consumers, within ecosystems | 0.907719–0.958479 | 1.526191–1.598596 |

These ranges describe calibration sensitivity, not confidence intervals for true PPR. Group and regional influence remain descriptive diagnostics and do not authorize further exclusions.

## GE–TE comparison on common support

The new [TE successor](../ppr_taxonomic_resolution_20261018_validated7/report.md) is the comparison source. Its full consumed-input ledger is checked transitively before GE analysis. Exact model/group identity, catch allocations, taxon TLs, effective group TLs and classic/simple totals are required to match. GE uses its own coefficients and PPR weights.

| Scenario | GE billion tC | TE billion tC | GE/TE total | GE factor | TE factor |
|---|---|---|---|---|---|
| Retain group coefficients | 1.038932 | 3.051529 | 0.340463 | 1.000000 | 1.000000 |
| Unit slope b=1 | 1.664049 | 5.458401 | 0.304860 | 1.601692 | 1.788743 |
| All positive consumers, pooled ecosystems | 1.870813 | 9.159593 | 0.204246 | 1.800708 | 3.001641 |
| All positive consumers, within ecosystems | 1.788421 | 9.525653 | 0.187748 | 1.721404 | 3.121601 |
| Review-included consumers, pooled ecosystems | 1.642848 | 7.088277 | 0.231770 | 1.581286 | 2.322861 |
| Review-included consumers, within ecosystems | 1.566564 | 7.176716 | 0.218284 | 1.507860 | 2.351843 |
| Catch-bearing groups, equal weights, pooled ecosystems | 1.611395 | 6.444940 | 0.250025 | 1.551011 | 2.112037 |
| Catch-bearing groups, equal weights, within ecosystems | 1.468946 | 6.224970 | 0.235976 | 1.413900 | 2.039952 |
| Catch weights, pooled ecosystems | 1.558062 | 6.185307 | 0.251897 | 1.499677 | 2.026954 |
| Catch weights, within ecosystems | 1.440976 | 6.208042 | 0.232114 | 1.386978 | 2.034404 |
| PPR weights; stress test, pooled ecosystems | 1.465382 | 6.492316 | 0.225710 | 1.410470 | 2.127562 |
| PPR weights; stress test, within ecosystems | 1.454783 | 6.028489 | 0.241318 | 1.400268 | 1.975564 |

At b=0 and b=1, every group's mean-shift, Jensen and full TL factors are identical across GE and TE because the catch/TL support and specified slopes are identical. Aggregate factors can differ because GE and TE assign different baseline PPR weights to those groups. Fitted scenarios also use different estimated slopes; their differences cannot be attributed solely to weights. GE's consumer ratio P/Q does not make the entire GE calculation automatically independent of the EE floor: saved detrital accounting may also depend on mortality. This study preserves the actual saved configuration.

## Retained diagnostic restrictions

Positive researcher review concerns the model extraction and signed diagnostics; it does not approve every additional coefficient, transformed calculation or annual outcome. The following saved flags remain in force. A finite reconstructed total is not a new annual publication permission.

| Region | Saved diagnostic | Published annual status | rho living | EE floor |
|---|---|---|---|---|
| HS_077 | WARN | provisional: diagnostic WARN | 0.538726168355331 | True / 0.1 |
| LME_013 | FAIL | provisional: DIRECT GE overall FAIL; balanced model; det_collapse_mode=always; pending researcher review; production-ineligible; refreshed diagnosis: FAIL: configuration diagnostic | 0.7 | True / 0.1 |
| LME_032 | WARN | ok | 0.5766952250936148 | True / 0.1 |
| LME_034 | OK | provisional: printed input plus researcher Detritus completions; separate runtime normalization; derived biomass accumulation; source fidelity unverified; diagnostic OK | 0.5858234430448512 | True / 0.1 |
| LME_035 | OK | provisional: assumed size/stage allocations; see allocation ledger | 0.24000000000000005 | True / 0.1 |
| LME_036 | WARN | provisional: assumed size/stage allocations; see allocation ledger | 0.32091875376096113 | True / 0.1 |
| LME_047 | WARN | ok | 0.6874103217047791 | True / 0.1 |

## Reproducibility

[Source hashes](inputs/source_hashes.json) bind the current cohort, generated pages, canonical model/source packages and transitive upstream results. [Analysis verification](evidence/verification.json) records direct-sum identities and actual runtime. [Independent verification](evidence/independent_verification.json) reconstructs catch allocations from current HTML and solves separate weighted design matrices for pooled, within, between, per-model and leave-one-model-out fits. [Figure review](evidence/figure_review.json) records visual checks of the regenerated figures. No production model solver, regional workbook recalculation or page publication is performed by this research package.
