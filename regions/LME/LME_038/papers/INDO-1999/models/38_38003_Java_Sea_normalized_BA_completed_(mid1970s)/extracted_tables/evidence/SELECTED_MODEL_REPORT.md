# Selected model: Buchary1999, Java Sea mid-1970s

**Selected:** `38_38003_Java_Sea_normalized_BA_completed_(mid1970s)`. User rationale: **best available model**. The original source-faithful model38001 is preserved; Nurhakim38002 remains an unselected, blocked later-test candidate.

This is a user-authorized computational variant. Macrozoobenthos existing diet fractions were divided by0.660 (factor1.5151515151515151); no omitted prey was recovered or invented. All28 signed loader-completed BA values were stored explicitly as computed values. Source BA remains unknown in the source canonical JSON. No other source numeric parameters were edited. Exact reload comparison across29 rows and18 state/flow fields found zero differences at relative1e-10/absolute1e-9 tolerance. Existing basal/default-migration conventions remain documented in DERIVED_RELOAD_VALIDATION.json.

The source article covers Java Sea approximately471000km², not the full Indonesian Sea LME. The mid-1970s food web is extrapolated through1950–2019. Neither the old36% coverage estimate nor numerical equivalence to EcoBase410 is verified. Source fleet/discard splits are absent; original Harvest includes an assumed LBS bycatch proxy. Model group catch enters only explicit stage-weight proxies; regional PPR uses independent local Sea Around Us catch bases.

## Numerical decisions and scope

The fresh bounded run completed22 methods,180seconds allowed per method. GE and With Egestion are OK; TE is WARN, with Marine mammals TE approximately0.0008469558 (inverse1180.6997). The direct report contains two TE warnings: no detritus recycling matrix (b=0; mortality-derived SPPR written off as lost), and near-zero TE in group27. This is not network divergence. Computational method status `ok` means a result returned; it does not erase the TE warnings or validate printed source data. The concise [SPPR diagnostic report](SPPR_DIAGNOSTICS.md) contains only complete returned diagnose_sppr sections and fields for GE, TE and With Egestion; no global summary configuration is added. Its direct three-option retention matched every saved flattened field and did not rerun the22 methods or Monte Carlo.

No negative available all/inner/PP group coefficient occurred, including all28 biological groups and6 unfished groups (Import is a separate29th bookkeeping row). All three diagnostic configurations report0 negative source columns. Other methods lack retained full source matrices, so their per-source signs are not claimed. Scalar1986/1995 methods do not have PP decompositions.

| Method | Run outcome |
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

Monte Carlo used100 draws per configuration,10% TE error,20% cutoff, kind=new, exclude_diverged=True; TE fixesEE=0. No explicit seed: this is the fresh selected realization.

| Method | Draws | Accepted | Rejected negative | Rejected divergent |
|---|---:|---:|---:|---:|
| MC_new_GE | 100 | 100 | 0 | 0 |
| MC_new_TE_EEfix | 100 | 100 | 0 | 0 |

## Every signed BA completion

Units t/km²/year; source value unknown in every row. Seventeen are negative, including tiny rounding residuals and material values. These signed values reconcile loaded budgets; they do not establish biomass decline or gain. Diet normalization was not isolated as the sole cause.

| Group | Computational BA |
|---|---:|
| 1 Benthic producers | -3.06714665818187 |
| 2 Phytoplankton | -4.51529888515154 |
| 3 Small herb. zoopl. | -2.1526292248485 |
| 4 Lg. herb. zoopl. | -0.0151524921212118 |
| 5 Carn. zoopl. | -1.11316844848485 |
| 6 Jelly fishes | 5.91999999999815e-05 |
| 7 Benthic infauna | -0.0371039999999709 |
| 8 SAF | -0.000114859999999994 |
| 9 Macrozoobenthos | 1.73399999994217e-05 |
| 10 LBS | -0.158692411212122 |
| 11 Juv. pen. shrimps | -0.00190080000000048 |
| 12 Lg. pel. pred. (J) | 0.000565670000000018 |
| 13 Ad. pen. shrimps | -0.000238699999999703 |
| 14 Misc. pelagics | -0.000113870000000016 |
| 15 Leiognathids | 0.000259630000000011 |
| 16 Crabs + Lobsters | -0.000240909999999595 |
| 17 Cephalopods | -0.000758639999999922 |
| 18 Decapterus spp. | 0.000820400000000054 |
| 19 Rastrelliger spp. | -0.00107949000000004 |
| 20 Clupeoids | -0.00129814999999978 |
| 21 Small demersals | 0.00132886799999987 |
| 22 Med. demersals | -2.39900000000015e-05 |
| 23 Lg. dem. pred. (J) | 0.000661360000000055 |
| 24 Demersal rays | 0.0002231 |
| 25 Lg. pel. pred (A) | 8.15000000000017e-06 |
| 26 Lg. dem. pred (A) | 1.34999999999924e-05 |
| 27 Marine mammals | -2.21000000000021e-06 |
| 28 Detritus | 1761.423470522 |

## Catch matching and annual calculation

All181 catch taxa reviewed: 153 mapped, 28 unresolved. All numeric weights sum1 and exact group identifiers are checked. Stage pairs use printed group Harvest shares. Coarse pools use fixed1950–2019 identified total-catch composition after direct/stage assignments; no circular coarse allocation. SAU functional class narrows unidentified marine fish to Small/Medium demersals, Decapoda to Crabs + Lobsters, and residual crustaceans to shrimp stages. Source specific membership overrides broad guild labels; Acetes/Sergestidae maps to source group4, which explicitly contains sergestids and reports harvest. Netuma follows source Arius thalassinus via WoRMS synonym evidence. Full decisions and citations are in evidence/CATCH_MAPPING.csv and MAPPING_DECISIONS.json.

|2019 basis|Total tonnes|Mapped tonnes|Coverage|
|---|---:|---:|---:|
|landings|2741447.824|2652610.817|96.759%|
|catch|2883541.954|2787544.988|96.671%|
|discards|142094.130|134934.171|94.961%|

Largest unresolved2019 catch:

- Lates calcarifer: 82097.322t.
- Cypselurus poecilopterus: 11840.717t.
- Platycephalidae: 688.952t.
- Exocoetidae: 391.424t.
- Xiphias gladius: 307.544t.
- Alopias: 243.191t.
- Istiompax indica: 106.595t.
- Plotosus: 80.979t.

Annual results cover1950–2019, three catch bases and explicit unidentified treatments. Below are total-source PPR values for method treatment; unresolved taxa contribute missing coefficients, so these are covered-catch estimates, not complete catch totals. TE estimates remain warning-qualified.

|Method|Basis|1950 PPR wet tonnes|2019 PPR wet tonnes|
|---|---|---:|---:|
|new_GE|landings|8.74176e+06|2.12624e+08|
|new_GE|catch|8.89955e+06|2.25671e+08|
|new_GE|discards|157793|1.30478e+07|
|new_TE_EEfix|landings|6.3408e+07|1.58056e+09|
|new_TE_EEfix|catch|6.46634e+07|1.70513e+09|
|new_TE_EEfix|discards|1.25536e+06|1.24571e+08|
|new_WithEgestion|landings|3.6233e+06|8.92726e+07|
|new_WithEgestion|catch|3.68865e+06|9.46528e+07|
|new_WithEgestion|discards|65355.7|5.38012e+06|

PPR/NPP divides wet-equivalent PPR by9 exactly once. Existing ensemble-median NPP2019 is749758870.0793715tC/year. No new NPP extraction; algorithms and available years are retained, all missing years stay blank.

|Method|2019 landings PPR/NPP ensemble median|
|---|---:|
|new_GE|3.15099%|
|new_TE_EEfix|23.4232%|
|new_WithEgestion|1.32298%|

## Verification and provenance

Regional bounded prepare-selection, sppr, calculate and validate completed. Original regional workbook preserved in evidence/LME_038_before_user_selection.xlsx and models/previous_results. Source and derived hashes, exact28 signed changes, loader comparison, mappings, code snapshot and fresh SPPR workbook retained. Source diagnostics remain historical evidence; they were not substituted for this fresh selected run. Central selection is generated from regional Overview; all other regions and native tables are protected by the integration audit. Map refresh is coordinated separately by the parent task.

Source SHA256: `1740de76fad9cabab2791209cf96c73e8271e431ae4d6e5b858fa9fa6329b4ef`. Derived SHA256: `db0bc803ea5a068e346b82df8d8b4e4b13f8351bf61103c6507997cb6996ae35`.
