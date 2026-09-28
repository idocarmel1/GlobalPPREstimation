> Selection update, 2026-09-28: the user subsequently selected `49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)`. Earlier "unselected" statements below describe the diagnostic run at that time. Scientific limitations remain; the deferred TE investigation is recorded in the separate DECISIONS_AND_LIMITATIONS.md. This is retained research evidence; the current SPPR report contains only direct diagnose_sppr outputs.

# LME049 extraction and full SPPR diagnostic review

The two available source bundles support two published parameterizations: Watari et al.(2019), year2013,41groups; and Chen et al.(2025), year2023,25groups. A separately authorized39-group detritus-only experiment is derived from Watari; it is not another published model. None is selected or production eligible. The user's preference for2019 reflects its finer group structure, not adoption of an exact model.

## Evidence and source admission

Watari uses35consumers,3regional phytoplankton and3detritus pools in one linked913102km² model (OYC186128,KC186220,OF540754). Table2 PDFp6 printed299 reports habitat and whole-model-area biomasses; Table3 PDFp8 printed301 has1435diet cells. Canonical JSON preserves printed whole-area B and diet precision, including non-unit totals .995,1.012,1.002,1.002,1.005 for consumers2,3,5,6,8. Seabird B<.01 and five catches<.01 remain unknown sentinels with censor evidence. No GS, numerical BA, migration or detritus routing was recovered. Main-article taxonomy and11single-species stocks are retained; detailed pooled membership is incomplete because the46-page supplement could not be archived (HTTP401). Source manifest, rendered pages, cell/font evidence, exact printed text and import/converter audits are retained in the original model folder. This is one spatially structured parameterization, not3independent models.

Chen2025 contains23consumers,1PP,1DET; Table2 p5 and DOCX supplementS2 supply parameters/diet.54'+' diet entries remain censored unknowns; the caption's '<0.01 percentage' was not silently assigned a numerical fraction. Diet known subtotals .98–1.00, GS/BA/migration/catches and fate gaps remain unresolved. Table1 p3 retains all25main composition lists, source spellings and imperfectly resolved membership. This is one2023survey-based parameterization, not separate models for supplemental uncertainty tables. DOCX's five tables were inspected as OOXML, not page-rendered (LibreOffice unavailable). The corrected citation is Chen et al.; Gan is the lead author's given name.

Both source extractions passed JSON reconstruction and exact source-value assertions; source errors/missingness were not repaired. Import validation reports1error/43warnings for Watari and diet/missingness findings for Chen in their validate.log. Watari canonical mass balance is INDETERMINATE for7groups (max EE difference .450; righteye flounder computed EE1.026), and Chen for16groups (max44.158;8EE>1). These conditional checks omit unknown terms; no finding establishes source steady state. Full details are in each extracted_tables/MASS_BALANCE_CANONICAL.md and REPORT.md. Source hashes are in source_manifest.json; source bytes and original canonical files are preserved.

## Original41-group Watari: blocked before calculation

49_20192013_Western_North_Pacific_Watari_(2013) fails loading: missing detritus routing for pools39,40,41 cannot be inferred. Habitat fractions0.2/0.2/0.6 and prey diets do not supply mortality/egestion fate. Therefore0methods and0MCdraws executed; spectral radii, health, SPPR balances, coefficients/negatives and acceptance tests were NOT RUN, not passed. All41groups have explicit unavailable records in source_group_diagnostic_status.csv; bounded_diagnostic_output retains the error and trace. No original model was modified to bypass this failure.

## Approved detritus-only experiment: exact changes and assumptions

49_2019201301_Watari_Detritus_Pooled_Experiment_(2013) maps1–38 identically and39/40/41 to39. It preserves all35consumer scalar/catch parameters, all3phytoplankton records and non-detritus diets. Total-area detritus B=9.58+6.04+28.50=44.12t/km²; habitat fractions are not applied a second time. A whole-domain pooled habitat1.00/Bhab44.12 is a derived representation, not a printed estimate. Each consumer's pooled detritus fraction is the exact decimal sum of its3source fractions; every full diet total is unchanged. Source DET EE remains unknown (no average). The original pools have no diet rows or supported internal transfer amounts; no internal transfer, catch or import was duplicated or invented. Unknown fate entries remain unknown in canonical JSON; the loader supplies its existing one-pool identity/default matrix.

The explicit experiment assumes shared cross-block detritus mixing and routes all living M0+egestion to the sole pool with full retention; real external losses and the source's spatial routing remain unknown. M0 is flow B×PB×(1−EE), not total mortality Z or its rate. All routing/default assumptions and the exact original-to-derived map, changed parameters, diet aggregation and unchanged totals are under evidence/. Original canonical SHA256 is7448c7ac1a4f8aebdc3aa27d236adc31c8bd7600dd39591271b9f2ce22615eb7.

The former multi-DET loading obstacle is removed. Source admission is still unsupported. The loader normalizes83nonzero diet cells in5consumers (exact changes in evidence/all_loader_diet_transformations.csv), defaults missing catch/migration/import to0 and regular GS to.2, and adds a zero-flow diet_import pseudo-group40.17source groups have missing catch defaulted0, including the five '<.01' catches. These zeros are not observed absence of fishing. Critically, seabird B<.01 becomes1t/km², and its printed PB.12 and QB36.67 become0 in the completed table. This is a consequential loader artifact, not a supported source correction. All299mapped scalar differences/completions and full raw/completed tables are retained. All other known scalar parameters stay unchanged within1e−12.

BA is solved for every group, not taken from the paper. The three phytoplankton BA values are−1.373122,+.299280,−1.496462t/km²/y. Pooled detritus inflow1075.514299 minus direct predation53.887700 is absorbed into BA+1021.626599t/km²/y, with assumed external loss0. This is roughly23.16times standing detritus biomass per year, an unresolved accumulation/loss issue, not evidence of realistic steady state. Its diagnostic utilization ratio is.0501041; loader DET EE=1 is a bookkeeping convention, not source EE or that budget ratio. Absolute completed production/consumption residuals are at most1.14e−13; this follows from completion and does not validate source balance. Source-level mass balance remains INDETERMINATE for7groups with all39BA unknown.

## Exact computational settings and interpretation

Isolated minimal candidate workbooks were run through the current bounded regional SPPR wrapper with180seconds per method and health configuration.100draws were requested for each of MC_new_GE and MC_new_TE_EEfix. TE uncertainty10%, cut20%, kind=new, exclude_diverged=True; TE MC fixesEE0 cases. No seed was fixed or exposed by the wrapper, so accepted stochastic outputs are not bitwise repeatable;100draws are screening, not evidence of stable tails. MC rejections distinguish negative from diverged and are not added twice. Failed/all-rejected outputs remain missing.

Loading uses underdetermined=True,zero_biomass_accum=False,normalize_DC=True,DC_tol=.001; default zero_catch=True,default_gs=True,weight_flow=weight_guess=1. The raw source and derived canonical models remain untouched by this completion. For all health rows: det_collapse_mode=never,det_open_mode=none,det_theta=1,det_external_sppr=0,explicit_TE=False. Theta is inert for these closed configurations; this is not an openness/sensitivity sweep. Scopes all/inner/PP respectively include every basal source, exclude Import, or retain only primary producers. Method configuration distinctions appear below and full executed code/settings/hashes are retained per candidate. Health grades configurations, not whole model validity.

GE and With Egestion in the experiment return health OK with gaps.00676480/.00387648; these are below the warning threshold but balance_is_balanced remainsFalse under the strict equality check. TE has rho<1 but FAIL from4negative basal-source coefficients, all in zero-catch/defaulted seabird group3 (DET39 andPP36/37/38), plus2near-singular TEcases; its gap.0335435 is WARN. TE coefficients are unusable. GE/Egestion coefficients describe only this heavily completed assumption scenario and should not be adopted as source-valid production estimates. Their MC100/100 acceptance does not resolve ecological input uncertainty. Chen's3configurations allFAIL, allMCdraws rejected, and negative groups include groups with no recorded fishing.

No production catch matching, annual PPR, adopted PPR/NPP or map refresh was performed. The generic diagnostic exporter includes a footprint sheet using source catches; those incidental diagnostic values are not annual regional estimates or adopted results. Original source candidate metadata is already registered unselected. Experimental metadata is STAGED ONLY and leaves the41-group record intact. Project.xlsx was not written by this experiment; the production regional workbook remains byte-identical. Next decision: retain this as an assumption experiment, or resolve seabird/censoring, BA/retention and spatial routing evidence before considering model adoption. No additional numerical repair is authorized or silently applied.


### Independent reconstruction check

The experimental review XLSX was independently read back:39group scalar/catch records and1365diet entries agree with canonical values. The converter intermediate fills unknown fates/imports and absent producer diets with zero; it is retained separately as converter_reconstructed_intermediate.xlsx. Those review-only zero fills were restored to blanks in canonical_reconstructed.xlsx, with an explicit audit in reconstruction_value_checks.json. The computational canonical JSON and all executed SPPR inputs remain unchanged.

## 49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023)

Groups: 25. No production selection. All22 method workers returned `ok`; no failures or timeouts. Runtime approximately 33 seconds. Execution success is distinct from numerical health and source admission.

| TE_option | status | divergence_rho_living | divergence_b | divergence_n_negative_sources | divergence_n_near_singular_te | balance_rel_gap | model_input_p_max_rel_residual | model_input_q_max_rel_residual |
|---|---|---|---|---|---|---|---|---|
| GE | FAIL | 1.31171875 | 0.01495535578600322 | 2 | 0 | 0 | 7.529181753371558e-16 | 1.807003620809174e-16 |
| TE | FAIL | 1.652892561983471 | 0 | 2 | 0 | 1.234022539872428e-15 | 7.529181753371558e-16 | 1.807003620809174e-16 |
| With Egestion | FAIL | 1.049375 | 0.05147982272749826 | 2 | 0 | 2.056704233120713e-16 | 7.529181753371558e-16 | 1.807003620809174e-16 |

### Monte Carlo

| method | requested | accepted | rejected negative | rejected diverged |
|---|---|---|---|---|
| MC_new_GE | 100 | 0 | 0 | 100 |
| MC_new_TE_EEfix | 100 | 0 | 0 | 100 |

### Every method and source scope

Entries show available values / negative values for ALL source groups, including unreported or zero-defaulted catch groups. Parentheses list negative group IDs; `z` is the number of those with loaded catch zero. The complete values and original/loaded catch evidence are retained in each candidate’s all_source_group_sppr_diagnostics.csv. Blank source attribution for1986/1995 is unavailable, not zero.

| method | execution | all | inner | PP only | configuration |
|---|---|---|---|---|---|
| SPPR_1986 | ok | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | 0 / 0 (none; z=0) | Pauly & Christensen (1986): one catch-weighted TL, fixed TE=0.1. |
| SPPR_1995_TE0.1 | ok | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | 0 / 0 (none; z=0) | Pauly & Christensen (1995): per-group TE^(1-TL) with global_TE=0.1. |
| SPPR_1995_TEmean | ok | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | 0 / 0 (none; z=0) | Pauly & Christensen (1995): per-group TE^(1-TL) with global_TE='mean'. Arithmetic mean with consumer consumption weights. |
| SPPR_1995_TEmean_catch | ok | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | 0 / 0 (none; z=0) | Pauly & Christensen (1995): per-group TE^(1-TL) with global_TE='mean'. Arithmetic mean with consumer catch weights. Consumer biomass fallback when consumer catch is zero. |
| Ulanowicz_globalTEmean | ok | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | Nullspace form of the EwE path sum, global TE at the consumer consumption-weighted arithmetic mean (Jensen-able on TL). |
| Ulanowicz_globalTEmean_catch | ok | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | Nullspace form of the EwE path sum, global TE at the consumer catch-weighted arithmetic mean. Consumer biomass fallback when consumer catch is zero (Jensen-able on TL). |
| Ulanowicz_TE | ok | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | Nullspace form of the EwE path sum, per-group TE (Jensen-able on TE). |
| EwE_TE_noEE | ok | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | EwE path enumeration without EE weighting -- heavy method. |
| EwE_TE_EE | ok | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | 25 / 0 (none; z=0) | EwE path enumeration with EE weighting -- heavy method. |
| SPPR_2015 | ok | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 2015 Leontief method, includes cycles. Takes no arguments: PP-only filtering is applied downstream via get_PPR. |
| new_TE_noEEfix | ok | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | Primary solver, TE_option='TE', EE=0 groups left unrepaired (reproduces 2015). |
| new_TE_EEfix | ok | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | Primary solver, TE_option='TE', EE=0 groups repaired. |
| new_GE | ok | 25 / 9 (19,14,13,12,9,4,3,2,1; z=4) | 25 / 9 (19,14,13,12,9,4,3,2,1; z=4) | 25 / 9 (19,14,13,12,9,4,3,2,1; z=4) | Primary solver, TE_option='GE' (should sit below TE). |
| new_WithEgestion | ok | 25 / 13 (20,19,14,13,12,9,8,7,5,4,3,2,1; z=7) | 25 / 13 (20,19,14,13,12,9,8,7,5,4,3,2,1; z=7) | 25 / 13 (20,19,14,13,12,9,8,7,5,4,3,2,1; z=7) | Primary solver, TE_option='With Egestion' (should sit below GE). |
| sym_TE_asPP | ok | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | Symbolic solver, TE_option='TE', diet_import_option='as_PP'. |
| sym_TE_asDC | ok | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | 25 / 10 (19,14,13,12,8,5,4,3,2,1; z=5) | Symbolic solver, TE_option='TE', diet_import_option='as_DC'. |
| sym_GE_asPP | ok | 25 / 9 (19,14,13,12,9,4,3,2,1; z=4) | 25 / 9 (19,14,13,12,9,4,3,2,1; z=4) | 25 / 9 (19,14,13,12,9,4,3,2,1; z=4) | Symbolic solver, TE_option='GE', diet_import_option='as_PP'. |
| sym_GE_asDC | ok | 25 / 9 (19,14,13,12,9,4,3,2,1; z=4) | 25 / 9 (19,14,13,12,9,4,3,2,1; z=4) | 25 / 9 (19,14,13,12,9,4,3,2,1; z=4) | Symbolic solver, TE_option='GE', diet_import_option='as_DC'. |
| sym_WithEgestion_asPP | ok | 25 / 13 (20,19,14,13,12,9,8,7,5,4,3,2,1; z=7) | 25 / 13 (20,19,14,13,12,9,8,7,5,4,3,2,1; z=7) | 25 / 13 (20,19,14,13,12,9,8,7,5,4,3,2,1; z=7) | Symbolic solver, TE_option='With Egestion', diet_import_option='as_PP'. |
| sym_WithEgestion_asDC | ok | 25 / 13 (20,19,14,13,12,9,8,7,5,4,3,2,1; z=7) | 25 / 13 (20,19,14,13,12,9,8,7,5,4,3,2,1; z=7) | 25 / 13 (20,19,14,13,12,9,8,7,5,4,3,2,1; z=7) | Symbolic solver, TE_option='With Egestion', diet_import_option='as_DC'. |
| MC_new_GE | ok | 0 / 0 (none; z=0) | 0 / 0 (none; z=0) | 0 / 0 (none; z=0) | Monte-Carlo over TE (10%/20%), kind='new', TE_option='GE', diverged draws excluded. |
| MC_new_TE_EEfix | ok | 0 / 0 (none; z=0) | 0 / 0 (none; z=0) | 0 / 0 (none; z=0) | Monte-Carlo over TE (10%/20%), kind='new', TE_option='TE' with fix_EE_0_cases=True, diverged draws excluded. |

## 49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)

Groups: 39. No production selection. All22 method workers returned `ok`; no failures or timeouts. Runtime approximately 80.47 seconds. Execution success is distinct from numerical health and source admission.

| TE_option | status | divergence_rho_living | divergence_b | divergence_n_negative_sources | divergence_n_near_singular_te | balance_rel_gap | model_input_p_max_rel_residual | model_input_q_max_rel_residual |
|---|---|---|---|---|---|---|---|---|
| GE | OK | 0.3334302325581396 | 0.0401728788278649 | 0 | 0 | 0.006764798141402979 | 1.67606132944619e-16 | 1.701491225479167e-16 |
| TE | FAIL | 0.5462783830567154 | 0 | 4 | 2 | 0.03354352350520768 | 1.67606132944619e-16 | 1.701491225479167e-16 |
| With Egestion | OK | 0.2667441860465117 | 0.0457181749968441 | 0 | 0 | 0.003876479626862391 | 1.67606132944619e-16 | 1.701491225479167e-16 |

### Monte Carlo

| method | requested | accepted | rejected negative | rejected diverged |
|---|---|---|---|---|
| MC_new_GE | 100 | 100 | 0 | 0 |
| MC_new_TE_EEfix | 100 | 0 | 0 | 100 |

### Every method and source scope

Entries show available values / negative values for ALL source groups, including unreported or zero-defaulted catch groups. Parentheses list negative group IDs; `z` is the number of those with loaded catch zero. The complete values and original/loaded catch evidence are retained in each candidate’s all_source_group_sppr_diagnostics.csv. Blank source attribution for1986/1995 is unavailable, not zero.

| method | execution | all | inner | PP only | configuration |
|---|---|---|---|---|---|
| SPPR_1986 | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 0 / 0 (none; z=0) | Pauly & Christensen (1986): one catch-weighted TL, fixed TE=0.1. |
| SPPR_1995_TE0.1 | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 0 / 0 (none; z=0) | Pauly & Christensen (1995): per-group TE^(1-TL) with global_TE=0.1. |
| SPPR_1995_TEmean | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 0 / 0 (none; z=0) | Pauly & Christensen (1995): per-group TE^(1-TL) with global_TE='mean'. Arithmetic mean with consumer consumption weights. |
| SPPR_1995_TEmean_catch | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 0 / 0 (none; z=0) | Pauly & Christensen (1995): per-group TE^(1-TL) with global_TE='mean'. Arithmetic mean with consumer catch weights. Consumer biomass fallback when consumer catch is zero. |
| Ulanowicz_globalTEmean | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | Nullspace form of the EwE path sum, global TE at the consumer consumption-weighted arithmetic mean (Jensen-able on TL). |
| Ulanowicz_globalTEmean_catch | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | Nullspace form of the EwE path sum, global TE at the consumer catch-weighted arithmetic mean. Consumer biomass fallback when consumer catch is zero (Jensen-able on TL). |
| Ulanowicz_TE | ok | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | Nullspace form of the EwE path sum, per-group TE (Jensen-able on TE). |
| EwE_TE_noEE | ok | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | EwE path enumeration without EE weighting -- heavy method. |
| EwE_TE_EE | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | EwE path enumeration with EE weighting -- heavy method. |
| SPPR_2015 | ok | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | 2015 Leontief method, includes cycles. Takes no arguments: PP-only filtering is applied downstream via get_PPR. |
| new_TE_noEEfix | ok | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | Primary solver, TE_option='TE', EE=0 groups left unrepaired (reproduces 2015). |
| new_TE_EEfix | ok | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | Primary solver, TE_option='TE', EE=0 groups repaired. |
| new_GE | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | Primary solver, TE_option='GE' (should sit below TE). |
| new_WithEgestion | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | Primary solver, TE_option='With Egestion' (should sit below GE). |
| sym_TE_asPP | ok | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | Symbolic solver, TE_option='TE', diet_import_option='as_PP'. |
| sym_TE_asDC | ok | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | 39 / 1 (3; z=1) | Symbolic solver, TE_option='TE', diet_import_option='as_DC'. |
| sym_GE_asPP | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | Symbolic solver, TE_option='GE', diet_import_option='as_PP'. |
| sym_GE_asDC | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | Symbolic solver, TE_option='GE', diet_import_option='as_DC'. |
| sym_WithEgestion_asPP | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | Symbolic solver, TE_option='With Egestion', diet_import_option='as_PP'. |
| sym_WithEgestion_asDC | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | Symbolic solver, TE_option='With Egestion', diet_import_option='as_DC'. |
| MC_new_GE | ok | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | 39 / 0 (none; z=0) | Monte-Carlo over TE (10%/20%), kind='new', TE_option='GE', diverged draws excluded. |
| MC_new_TE_EEfix | ok | 0 / 0 (none; z=0) | 0 / 0 (none; z=0) | 0 / 0 (none; z=0) | Monte-Carlo over TE (10%/20%), kind='new', TE_option='TE' with fix_EE_0_cases=True, diverged draws excluded. |

## Retained output locations

- Original41-group: ../49_20192013_Western_North_Pacific_Watari_(2013)/
- Chen25-group: ../49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023)/
- Experiment39-group: ../49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)/
- Compact full results: LME049_DIAGNOSTIC_RESULTS.json
- Each available candidate: sppr_source.xlsx, all_source_group_sppr_diagnostics.csv, model_health.csv, mc_diagnostics.csv and run_notes.csv. Experiment adds all_basal_source_coefficients.csv and evidence/complete audits.
