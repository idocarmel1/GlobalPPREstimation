# LME038 extraction and selection decisions — 28 September2026

**Current selection:** [38_38003_Java_Sea_normalized_BA_completed_(mid1970s)](../38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/SELECTED_MODEL_REPORT.md), reason **best available model**, with user-authorized diet normalization and all28 computational BA completions. The source-faithful38001 is unchanged; Nurhakim38002 remains blocked and unselected for later tests.

The concise [SPPR diagnostics](../38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/SPPR_DIAGNOSTICS.md) contains only direct flattened diagnose_sppr return fields for GE, TE and With Egestion. Extraction, all22 method outcomes, MC, transformations, mapping and annual estimates are retained separately in the selected-model decisions report. TE WARN remains visible.

The remainder below is the preserved **preselection source assessment**, not the current selection state. Statements that no production selection or matching changed describe that earlier assessment. Current regional results and provenance supersede those historical status statements.

---

# LME038 extraction and full SPPR diagnostic report - 28 September 2026

Two source-faithful candidates are archived and registered unselected. Buchary is the user-preferred spatial candidate; Nurhakim is retained only for later tests. Neither passes strict admission as printed. The Buchary run below is a loader-transformed diagnostic; Nurhakim downstream tests were not run. No production regional selection, catch matching, annual PPR, PPR/NPP or map publication changed.

## Source identity, geography and missingness

The BUCHARY-1991 folder contains Eny Anggraini Buchary’s April1999 UBC MSc thesis, *Evaluating the effect of the 1980 trawl ban in the Java Sea, Indonesia: An ecosystem-based approach*.1991 is the earlier degree year. The existing INDO-1999 catalog placeholder is reconciled to this supplied thesis using author/year/place and its explicit thesis-recovery note; it had no source PDF/hash or verified full citation. This bibliographic association is documented as an inference. Its old title and EcoBase410 URL are preserved as history; numerical equivalence to EcoBase410 remains unverified. The legacy36% bbox estimate was cleared from active coverage, not reused. Details: IDENTITY_AND_PATH_RECONCILIATION.json.

Buchary: one28-group mid-1970s static baseline (2 producers,25 consumers,1 detritus), Java Sea approximately471000 km² (PDF29/printed20); no verified LME intersection fraction. Later Ecosim trajectories are not distinct printed Ecopath parameter sets. All28 taxonomy descriptions captured from Table3.1; source spellings and stage distinctions retained. BA is unknown28/28. GS is source-stated0.2 for consumers except small/large herbivorous zooplankton0.4; basal3 groups remain blank. Single-pool detritus fate1 is explicitly stated. Discards are not independently quantified; the aggregate harvest includes an assumed LBS bycatch proxy. No modern synonym reconciliation or regional catch assignment performed.

Nurhakim2003: one27-group1979 north-coast Central Java survey baseline (2 producers,24 consumers,1 detritus); diet caption refers to mid-1970s. Model area and LME fraction unknown. All27 taxonomy descriptions captured; no separate Medium demersals group. BA, GS and numeric detritus fate remain missing for27/27;29 diet entries and producer EE are censored, with bounds retained. Printed GE is ambiguous/inconsistent with PB/QB and was not imported as PQ.

## 38_38001_Java_Sea_(mid1970s) - source admission and loader transformations

Strict source admission **FAILS**: Macrozoobenthos predator9 sums0.660. The source detritus cell is a dash, not0.340. The other24 consumer diets sum1.000. Required-import validation has1 error/2 warnings. The source-table mass-balance check has0 errors/1 endotherm warning, and the canonical converter check says BALANCED at its tolerance (maximum EE difference0.019 at Demersal rays). These limited balance results do not establish a complete diet or known BA. Canonical JSON preserves printed proportions and all unknown BA values.

The loader normalizes that consumer diet by **1/0.660 = 1.51515151515152** and completes underdetermined flows. It adds a zero-catch Import bookkeeping row, distinct from the28 biological groups. It recomputes trophic information and solves28 unknown BA values;17 are negative, while detritus BA is **1761.423470522 t/km²/year**. These completions reconcile the loaded budgets. Several negative values are tiny rounding-sized residuals; others are material. None is a demonstrated ecological biomass decline/gain, and no experiment isolated diet normalization as the sole cause of the17 values.

## Exact configuration health from the saved run

| Configuration | Status | Living spectral radius | Detritus recycling gain b | Relative flow gap | Max P residual | Max Q residual | Negative basal source columns |
|---|---|---:|---:|---:|---:|---:|---:|
| GE | OK | 0.401772825728 | 0.245460918923 | 0 | 1.32820226805e-16 | 1.78194501898e-16 | 0 |
| TE | WARN | 0.621299343271 | 0 | 3.82269928179e-16 | 1.32820226805e-16 | 1.78194501898e-16 | 0 |
| With Egestion | OK | 0.321418260582 | 0.254534959202 | 3.82269928179e-16 | 1.32820226805e-16 | 1.78194501898e-16 | 0 |

All three use det_collapse_mode=never, det_open_mode=none, det_theta=1 and det_external_sppr=0; no explicit sampled TE matrix for the health rows. GE/egestion use the single-detritus route. TE **WARN** is confirmed at **group27 Marine mammals** using retained rates and the engine formula TE=(P/Q)(1−M0/P): P=0.00621, Q=2.11899, M0=0.00441531, GE=0.00293064148485835, EE=0.289, TE=0.000846955389124064, inverseTE=1180.69973087274. It is the only regular group below the near-zero threshold0.001. The network spectral radius is below1, so this warning is not network divergence. Saved TE diagnostic has2 warnings and1 near-singular group. Near-zero TE can amplify SPPR; marine-mammal total SPPR is269815.0941253361 under TE versus20954.80161516027 under GE. These are candidate coefficients, not adopted regional results.

## All22 method outcomes

| Method | Outcome |
|---|---|
| SPPR_1986 | ok |
| SPPR_1995_TE0.1 | ok |
| SPPR_1995_TEmean | ok |
| SPPR_1995_TEmean_catch | ok |
| Ulanowicz_globalTEmean | ok |
| Ulanowicz_globalTEmean_catch | ok |
| Ulanowicz_TE | ok |
| EwE_TE_noEE | ok |
| EwE_TE_EE | ok |
| SPPR_2015 | ok |
| new_TE_noEEfix | ok |
| new_TE_EEfix | ok |
| new_GE | ok |
| new_WithEgestion | ok |
| sym_TE_asPP | ok |
| sym_TE_asDC | ok |
| sym_GE_asPP | ok |
| sym_GE_asDC | ok |
| sym_WithEgestion_asPP | ok |
| sym_WithEgestion_asDC | ok |
| MC_new_GE | ok |
| MC_new_TE_EEfix | ok |

All22 computations returned; no unavailable, failed or timed-out method. This computational success does not override source admission failure. SPPR_1986 and SPPR_1995 scalar variants have no source-resolved PP decomposition; their PP-only cells remain unavailable rather than zero. All28 biological groups, including6 with zero catch (the health count7 also includes the artificial Import row), were retained in sign checks. No negative scoped group coefficient appears in all/inner/PP among available values. GE, TE and With Egestion each report0 basal source columns containing negatives. Per-source matrices for the other methods were not retained by the exporter; no blanket claim about those unretained contributions is made.

## Monte Carlo and bounded-run settings

Each method/health row had a180-second limit via tools/run_region.py. The two Monte Carlo configurations used100 draws,10% TE error,20% cutoff, kind=new, exclude_diverged=True; TE additionally fixes EE=0 cases. No seed was explicitly fixed; these are the retained realization, summarized without a rerun.

| Method | Draws | Accepted | Rejected negative | Rejected diverged |
|---|---:|---:|---:|---:|
| MC_new_GE | 100 | 100 | 0 | 0 |
| MC_new_TE_EEfix | 100 | 100 | 0 | 0 |

## Every negative loader-solved BA

| Group | Solved BA (t/km²/year) |
|---|---:|
| 27 Marine mammals | -2.21000000000021e-06 |
| 22 Med. demersals | -2.39900000000015e-05 |
| 20 Clupeoids | -0.00129814999999978 |
| 19 Rastrelliger spp. | -0.00107949000000004 |
| 17 Cephalopods | -0.000758639999999922 |
| 16 Crabs + Lobsters | -0.000240909999999595 |
| 14 Misc. pelagics | -0.000113870000000016 |
| 13 Ad. pen. shrimps | -0.000238699999999703 |
| 11 Juv. pen. shrimps | -0.00190080000000048 |
| 10 LBS | -0.158692411212122 |
| 8 SAF | -0.000114859999999994 |
| 7 Benthic infauna | -0.0371039999999709 |
| 5 Carn. zoopl. | -1.11316844848485 |
| 4 Lg. herb. zoopl. | -0.0151524921212118 |
| 3 Small herb. zoopl. | -2.1526292248485 |
| 2 Phytoplankton | -4.51529888515154 |
| 1 Benthic producers | -3.06714665818187 |

These are solved bookkeeping quantities; source BA remains missing. Complete signed flows, including positive BA and detritus completion, are in the candidate evidence/loader_completed_flows.json.

## 38_38002_North_Coast_Central_Java_(1979) - blocked numerical diagnostics

Strict source admission **FAILS**. Table3 visually prints217 at prey22/predator25, giving a217.78 diet subtotal. Adult-shrimp subtotal0.28 plus two<0.01 entries cannot close to1; SAF0.87 plus one<0.01 likewise cannot close.29 censored diet cells include one>0.01. Producer EE is also censored. Bounds remain recorded; neither217→0.217 nor predecessor fractions were substituted. Required imports:4 errors/29 warnings. Source mass-balance:3 errors/14 warnings; recomputed EE exceeds1 for Rastrelliger1.039, juvenile large demersals110.103 and marine mammals2.722. Canonical converter check labels11 groups indeterminate because BA is unknown; that is not numerical validity.

**All22 SPPR methods, configuration health, spectral radii, flow-balance tests on an engine-loaded model, source sign tests and Monte Carlo are NOT RUN.** There are no accepted/rejected draws or calculated zero counts to report. The source is scientifically unsupported without authoritative corrected data. No later comparison experiment performed merely to complete this report. Source extraction, all27 taxonomy records and canonical/reconstructed numeric round trips are archived for future review.

## Provenance and eligibility

Original source bytes/hashes are preserved; folder alignment to exact engine IDs did not change either canonical JSON. Each candidate retains extracted_tables/REPORT.md, all eight imports, Taxonomy.xlsx, reconstructed workbook, evidence/source_manifest.json, source_cells.csv, censored_values.json, roundtrip_validation.json and page renders/coordinates. Converter-normalized intermediates remain separate from canonical source-faithful JSON. Compatibility round trips may display unknown diet cells as zeros; canonical source evidence/bounds are authoritative.

Buchary canonical SHA256: `1740de76fad9cabab2791209cf96c73e8271e431ae4d6e5b858fa9fa6329b4ef`. Its sppr_source.xlsx, isolated candidate_diagnostics.xlsx, final run log, executed-code snapshot/hashes and detailed diagnostic/flow audits preserve the numerical run. Nurhakim canonical SHA256: `5b75b4031a2fe321efce78645d6b8a59e332c30fcbe007eb091c70e499318318`. It has no SPPR run.

Central registration is recorded in CENTRAL_REGISTRATION_VERIFICATION.json; the existing INDO-1999 and Nurhakim paper records were updated and both unselected models added. Native tables/filter controls, other-region preferences/results, and existing ranks/scores were preserved. No updater or map rebuild ran. Compact machine-readable results: SPPR_RESULTS_SUMMARY.json. Neither candidate is production-eligible as printed; source preference does not constitute adoption.
