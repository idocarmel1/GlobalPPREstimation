# Selected-model size/stage allocation results

Reviewed all 23 selected model-region pairs. Online primary-source searches preceded adoption of model-catch proxies. No compatible observed whole-region caught-mass shares were adopted. All adopted weights remain provisional assumptions; no model diagnosis was upgraded.

Recorded 342 taxon-pair allocations across 14 pairs, including existing allocations preserved and relabeled. LME026 retains four blocked mapping proposals because usable groups/SPPR are absent.

Coverage below uses 2019 total catch, GE, all source categories, native unidentified treatment. Assumed coverage includes previously present assumptions; it is not simply the gain. PPR is tonnes carbon equivalent. Regions overlap; do not sum them.

| Region | Taxa recorded | Before coverage | After coverage | Gain (pp) | Catch dependent on these assumptions | Before PPR (tC) | After PPR (tC) |
|---|---:|---:|---:|---:|---:|---:|---:|
| EEZ_598 | 12 | 0.68% | 88.54% | 87.86 | 87.86% | 4,899,070.58 | 619,779,265.77 |
| EEZ_941 | 12 | 0.90% | 94.54% | 93.64 | 93.64% | 7,274,368.63 | 506,058,237.94 |
| HS_071 | 10 | 0.49% | 94.67% | 94.18 | 94.18% | 3,772,892.07 | 626,259,411.80 |
| HS_077 | 12 | 48.30% | 92.51% | 44.21 | 44.21% | 83,035,026.17 | 385,531,916.00 |
| LME_003 | 52 | 76.51% | 76.51% | 0.00 | 32.16% | 16,942,301.85 | 16,942,301.85 |
| LME_013 | 1 | 67.28% | 67.31% | 0.03 | 0.03% | 41,071,101.26 | 41,125,565.91 |
| LME_014 | 1 | 65.31% | 65.31% | 0.00 | 1.18% | 6,490,048.08 | 6,490,048.08 |
| LME_022 | 0 | 85.79% | 85.79% | 0.00 | 0.00% | 23,495,811.45 | 23,495,811.45 |
| LME_024 | 4 | 74.80% | 79.45% | 4.65 | 4.65% | 17,635,031.28 | 19,632,768.20 |
| LME_026 | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| LME_027 | 0 | 74.21% | 74.21% | 0.00 | 0.00% | 11,094,298.21 | 11,094,298.21 |
| LME_028 | 0 | 98.66% | 98.66% | 0.00 | 0.00% | 1,176,656,737.83 | 1,176,656,737.83 |
| LME_029 | 3 | 6.29% | 29.22% | 22.93 | 22.93% | 7,742,064.47 | 18,042,369.16 |
| LME_032 | 0 | 98.81% | 98.81% | 0.00 | 0.00% | 264,764,335.90 | 264,764,335.90 |
| LME_034 | 0 | 100.00% | 100.00% | 0.00 | 0.00% | 756,889,998.56 | 756,889,998.56 |
| LME_035 | 48 | 99.98% | 99.98% | 0.00 | 3.10% | 22,572,463.87 | 22,572,463.87 |
| LME_036 | 135 | 99.66% | 99.66% | 0.00 | 26.72% | 54,031,633.54 | 54,031,633.54 |
| LME_037 | 10 | 12.06% | 30.20% | 18.14 | 18.14% | 4,902,213.84 | 9,401,097.06 |
| LME_038 | 41 | 96.67% | 96.67% | 0.00 | 13.39% | 25,074,586.06 | 25,074,586.06 |
| LME_047 | 0 | 100.00% | 100.00% | 0.00 | 0.00% | 26,990,183.87 | 26,990,183.87 |
| LME_049 | 0 | 20.65% | 20.65% | 0.00 | 0.00% | 8,730,857.02 | 8,730,857.02 |
| LME_050 | 0 | 25.05% | 25.05% | 0.00 | 0.00% | 1,110,649.64 | 1,110,649.64 |
| LME_052 | 1 | 98.05% | 98.05% | 0.00 | 54.92% | 1,151,857,971.59 | 1,120,096,045.39 |

65 taxon-pair allocations are new or revised; 277 document existing weights.

The assumption column covers the stage/cohort allocations recorded in this review. A zero there does not certify that the other mappings or model are validated. Rounded 100.00% coverage may still include a small uncovered remainder.

## Interpretation and retained gaps

- Source model catch mixtures are fixed historical proxies, not measured annual regional size composition. Pool-to-species and catch-basis transfers are recorded.
- Baby skipjack source catch is missing, not observed zero; assumed uncaught infant stages retain both raw sentinel and explicit effective-zero assumption.
- LME052 pollock replaces biomass weighting with an explicit adult-only assumption. Its numerical cutoff remains unknown. Broader Gadidae/Gadiformes taxonomic weights remain flagged for separate review.
- LME003/014/035/036/038 existing allocations are documented and preserved numerically. Geographic strata, distinct species with size-like common names, ambiguous aliases and unsupported mixed guilds remain unresolved.
- LME026 has mapping evidence but no usable numerical SPPR; no PPR was fabricated.
- Existing model diagnostic problems remain visible in workbooks and the map. Improved coverage does not validate models.

## Evidence and verification

Per-pair source proposals and online-search audits are in pacific/, lme_west/ and lme_east/. reviewed_plans.json records normalized adoption inputs. Active candidate ledgers and impact tables live in the regional workbooks. Baseline bytes and source hashes are retained in baseline/ and baseline_manifest.json.

Verified 1,487,850 central annual cells against the saved regional outputs, plus NPP, source metadata, selections, all existing diagnosis tables and 343 unselected regional workbooks. FINAL_VERIFICATION.json records resulting hashes. The source-scope recalculation regression has a dedicated passing test.

Central workflow updated: tools/skills/original_skill_resources/combined-src/SKILL.md and references/size-stage-allocations.md.

Final display checks: 2,280,180 annual values and all NPP values agree between the generated pages and Project.xlsx. Executing the actual map/trend calculation code independently reproduced all 14 affected pairs. Browser checks confirmed HS077 GE coverage 92.51%, displayed PPR 385,500,000 tC (rounded), and the assumption note; switching to TE retained its FAIL and negative source-group SPPR flags with a provisional numeric result.


---
Copy navigation added during the template test; historical text above is unchanged.

[Eastern LME review](lme_east/REVIEW.md) · [LME036 audit](lme_east/LME_036_audit.json) · [Proposals](lme_east/proposals.json) · [Search audit](lme_east/online_search_audit.json)
