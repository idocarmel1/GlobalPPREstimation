# Scotland candidate: seabird diet and derived BA correction

This is an unadopted derived runtime variant for researcher review. The canonical source model, its missing values and original diet, publications/native inputs, historical diagnostics and old result manifest are preserved. LME_022 remains selected to ICES_WGSAM2015_North_Sea_1991; this package concerns only the explicitly named Scotland candidate.

## Correction and provenance

All 25 ecological groups and the synthetic diet-import group remain. Only the Seabirds (22) consumer diet changes. Source Table S3!W24 self-feeding is 0.0002; the exact archived normalized entry is 0.0002000800320128051. It is set to zero in the runtime copy, and all remaining prey (including Detritus 25) are proportionally normalized. The retained factor is 1.0002001200720434; the carried-forward value 1.0002001200720432 differs by one double-precision ULP (2.220446049250313e-16), without a biological difference. The archived diet sum is 0.9999999999999998 and the resulting sum is 1. Exact before/after cells are listed below and in the linked ledger. All other consumers’ diets are byte-equivalent at the typed-state level. This user-authorized derived scenario does not establish that the published self-diet was a typographical error.

All prey predation was recomputed from the changed diet and retained consumption. Only 13 affected BA entries were recomputed. Each has a source -9999 missing marker, explicit loader-derived evidence in LOADER_TRANSFORMATIONS.csv, and an archived value matching that ledger within 1e-12 absolute/relative tolerance. No affected BA has observed/manual/uncertain provenance; there are no skipped affected entries. Unaffected BA is preserved exactly. BA remains a derived balancing residual, not measured accumulation or an author-confirmed biological correction.

The equation is BA = P - M0 - catch - predation - net migration. Production, consumption, mortality, EE, catch, migration, egestion, respiration, biomass, routing and all other protected biological fields are unchanged. The historical broad balance_model routine and constructors are never called. No EE floor is introduced.

Detritus receives the same routed M0 + egestion inflow (1879.1437 t wet weight km^-2 year^-1). Its predation removal rises from 220.72839973232996 to 220.72842765756852, and its proven-derived BA falls by the same amount, from 1658.41530026767 to the exact value in the table below. Detritus catch, M0, net migration and external export remain zero.

## Exact changed diet cells

| Publication cell | Prey ID/name | Canonical source | Archived runtime before | Corrected runtime after |
|---|---|---:|---:|---:|
| Table S3!W27 | 25 Detritus | 0.20899999999999999 | 0.20908363345338132 | 0.20912547528517111 |
| Table S3!W24 | 22 Seabirds | 0.00020000000000000001 | 0.00020008003201280511 | 0 |
| Table S3!W22 | 20 Large Pelagics | 0.029999999999999999 | 0.030012004801920761 | 0.030018010806483888 |
| Table S3!W21 | 19 Small pelagics | 0.53100000000000003 | 0.53121248499399754 | 0.53131879127476489 |
| Table S3!W20 | 18 Herring | 0.035999999999999997 | 0.036014405762304913 | 0.03602161296778067 |
| Table S3!W19 | 17 Large Dem. fish | 0.0089999999999999993 | 0.0090036014405762282 | 0.0090054032419451674 |
| Table S3!W17 | 15 Saithe | 0.014 | 0.014005602240896357 | 0.014008405043025817 |
| Table S3!W15 | 13 Whiting | 0.014 | 0.014005602240896357 | 0.014008405043025817 |
| Table S3!W14 | 12 Haddock | 0.025000000000000001 | 0.025010004001600639 | 0.025015009005403245 |
| Table S3!W12 | 10 Cod | 0.014 | 0.014005602240896357 | 0.014008405043025817 |
| Table S3!W8 | 6 Crustacea | 0.00040000000000000002 | 0.00040016006402561022 | 0.00040024014408645192 |
| Table S3!W5 | 3 Large zooplankton | 0.066000000000000003 | 0.066026410564225688 | 0.066039623774264575 |
| Table S3!W4 | 2 Small zooplankton | 0.050999999999999997 | 0.051020408163265293 | 0.051030618371022608 |

## Exact eligible BA changes

Units: t wet weight km^-2 year^-1. Every row below is a retained missing-source, loader-derived value.

| Group | Before | After | Change | Provenance CSV line |
|---|---:|---:|---:|---:|
| 25 Detritus | 1658.4153002676699 | 1658.4152723424313 | -2.7925238555326359e-05 | 6 |
| 22 Seabirds | -1.3533413365345812e-05 | 0.00012000000000000031 | 0.00013353341336534613 | 12 |
| 20 Large Pelagics | -0.00093512444673993222 | -0.00093913285418523174 | -4.0084074452995111e-06 | 16 |
| 19 Small pelagics | -0.20284218678993149 | -0.20291313560171531 | -7.0948811783821952e-05 | 18 |
| 18 Herring | -0.004368877387005865 | -0.0043736874759403577 | -4.8100889344926401e-06 | 20 |
| 17 Large Dem. fish | -0.00031487643291228107 | -0.00031607895514590423 | -1.20252223362316e-06 | 22 |
| 15 Saithe | 0.0020488355367673794 | 0.0020469649466262063 | -1.8705901411730785e-06 | 26 |
| 13 Whiting | -0.0077950146189808556 | -0.0077968852091220564 | -1.8705901412008341e-06 | 30 |
| 12 Haddock | -0.0050231192748760867 | -0.0050264596144139473 | -3.3403395378606149e-06 | 32 |
| 10 Cod | 0.006566610400744799 | 0.0065647398106036259 | -1.8705901411730785e-06 | 36 |
| 6 Crustacea | 0.026921430302358829 | 0.02692137685692586 | -5.3445432968146633e-08 | 44 |
| 3 Large zooplankton | -0.041852447483627486 | -0.041861265980010387 | -8.8184963829007756e-06 | 50 |
| 2 Small zooplankton | 0.12513040779009543 | 0.12512359349742042 | -6.8142926750169863e-06 | 52 |

## Actual diagnostics

| State | Method | Grade | rho living | PP budget gap (%) | Strict model / SPPR balance | Negative SPPR entries |
|---|---|---|---:|---:|---|---:|
| Retained reproduced baseline | GE | OK | 0.21208967414456642 | 0 | True / True | 0 |
| Retained diet-only, BA fixed | GE | WARN | 0.21208967414456642 | 0.034074014956383604 | False / False | 0 |
| Fresh corrected variant | GE | OK | 0.21208967414456642 | 0 | True / True | 0 |
| Retained reproduced baseline | TE | FAIL | 1.1127784447112168 | 2.1200342698669657e-14 | True / True | 2 |
| Retained diet-only, BA fixed | TE | WARN | 0.2757420229532071 | 1.668794667118878 | False / False | 0 |
| Fresh corrected variant | TE | WARN | 0.2757420229532071 | 2.1200342698669657e-14 | True / True | 0 |
| Retained reproduced baseline | With Egestion | OK | 0.16967173931565332 | 0 | True / True | 0 |
| Retained diet-only, BA fixed | With Egestion | WARN | 0.16967173931565332 | 0.01179040711235492 | False / False | 0 |
| Fresh corrected variant | With Egestion | OK | 0.16967173931565332 | 0 | True / True | 0 |

The baseline TE self-loop A[22,22] = 1.1127784447112168 caused living-network divergence; no other consumer eats seabirds. It generated negative Phytoplankton (1) → Seabirds (22) = -1916160.3191561818 and Detritus (25) → Seabirds (22) = -460709.19237909134. The corrected A[22,22] is zero, rho living is 0.2757420229532071, and every SPPR contribution is nonnegative in all three fresh methods.

TE remains WARN because Cetaceans (24), Seals (23) and Seabirds (22) have near-zero transfer efficiencies. This is distinct from the removed feedback divergence and from budget balance. TE reports b=0 by convention because mortality-derived requirements are written off; that value does not establish absence of physical recycling. No overall OK claim is made for TE.

Fresh GE b = 0.0698576437258916; With Egestion b = 0.09711476293526844. Fresh seabird total SPPR: GE 5506.446079035624, TE 268113.2909082857, With Egestion 1908.2357402357948. Detritus (25) total SPPR: GE 1.0828711378491187; TE 0.8104489294778254; With Egestion 1.2093390220288438. Full named basal-source coefficients, detritus coefficients, masks, axes, negative entries (including operator entries), thresholds and exact returns are retained in each method artifact.

## Reproduction and limitations

Run code/run_correction.py using the scientific Python environment in run_manifest.json, then code/finalize_evidence.py. The first script restores persisted typed attributes via __new__ without rerunning defaults; verifies the unchanged 47-artifact prior experiment; writes exact before/corrected/all-method before-and-after state; and runs only GE, TE and With Egestion. The second script clarifies the name of the intermediate diet-only state and creates this summary, without running a solver or changing values.

The prior nine-run baseline evidence is reused after hash verification, not claimed to have been executed again in this package. Its matching original source matrices support the comparison. The original direct-return loss and the old result manifest’s unknown historical execution remain historical limitations; this fresh execution does not rewrite them. This package does not establish publication-native equivalence, whole-North-Sea geographic applicability, researcher approval, selection, or adoption of regional coefficients.

Actual diagnostic configuration: historical engine PPRCalculator.py SHA-256 b2bb08f0564c8cd0fcc873eb1c681fd924c3dd113e22d6b388456248fc0162a7; canonical model SHA-256 5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691; det_collapse_mode=never, det_open_mode=none, det_theta=1, det_external_sppr=0, fix_EE_0_cases=True; full (short=False, flat=False) returns, with SPPR/A/L from the same calls. EE floor OFF; historical thresholds unchanged. Exact runtime/code/source hashes and interpreter/dependency versions are in the manifest.

Evidence navigation: [manifest](run_manifest.json), [correction/BA ledger](inputs/intervention.json), [comparison](outputs/comparison.json), [matrix QA](qa/reopened_matrix_checks.json), [evidence index](evidence_index.json), [completeness](qa/completeness.json).
