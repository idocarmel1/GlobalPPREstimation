# Graph Report - .  (2026-09-06)

## Corpus Check
- 129 files · ~135,805 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1136 nodes · 2010 edges · 80 communities (62 shown, 18 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 78 edges (avg confidence: 0.71)
- Token cost: 549,092 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Spatial Unit Geometry|Spatial Unit Geometry]]
- [[_COMMUNITY_Sea Around Us Download|Sea Around Us Download]]
- [[_COMMUNITY_Excel Workbook Builders|Excel Workbook Builders]]
- [[_COMMUNITY_Ecopath Model Loading|Ecopath Model Loading]]
- [[_COMMUNITY_SPPR Workbook Export Tests|SPPR Workbook Export Tests]]
- [[_COMMUNITY_PPR Core Calculation|PPR Core Calculation]]
- [[_COMMUNITY_Pipeline Orchestration|Pipeline Orchestration]]
- [[_COMMUNITY_Catch Ingestion and Distillation|Catch Ingestion and Distillation]]
- [[_COMMUNITY_Monte Carlo SPPR Tests|Monte Carlo SPPR Tests]]
- [[_COMMUNITY_PPRCalculator Detritus Internals|PPRCalculator Detritus Internals]]
- [[_COMMUNITY_Model Report Tables|Model Report Tables]]
- [[_COMMUNITY_Archive Redundancy Verification|Archive Redundancy Verification]]
- [[_COMMUNITY_Atlas Catalog and Archive|Atlas Catalog and Archive]]
- [[_COMMUNITY_Validation Notebook Builders|Validation Notebook Builders]]
- [[_COMMUNITY_SPPR Excel Assembly|SPPR Excel Assembly]]
- [[_COMMUNITY_Source File Retrieval|Source File Retrieval]]
- [[_COMMUNITY_Integration Design Record|Integration Design Record]]
- [[_COMMUNITY_SPPR Diagnostics Tests|SPPR Diagnostics Tests]]
- [[_COMMUNITY_PPRCalculator Diagnostics|PPRCalculator Diagnostics]]
- [[_COMMUNITY_Pipeline Scope Configs|Pipeline Scope Configs]]
- [[_COMMUNITY_Ecopath Model Balancing|Ecopath Model Balancing]]
- [[_COMMUNITY_EEZ Release Validation Tests|EEZ Release Validation Tests]]
- [[_COMMUNITY_Atlas Integration Overview|Atlas Integration Overview]]
- [[_COMMUNITY_EEZ Release Validation|EEZ Release Validation]]
- [[_COMMUNITY_Method Documentation|Method Documentation]]
- [[_COMMUNITY_Ecopath Core Concepts|Ecopath Core Concepts]]
- [[_COMMUNITY_SPPR Solver Formulations|SPPR Solver Formulations]]
- [[_COMMUNITY_Unretrieved LME Sources|Unretrieved LME Sources]]
- [[_COMMUNITY_Cycle and Nullspace Utilities|Cycle and Nullspace Utilities]]
- [[_COMMUNITY_Transfer Efficiency Diagnostics|Transfer Efficiency Diagnostics]]
- [[_COMMUNITY_EEZ Notebook Execution|EEZ Notebook Execution]]
- [[_COMMUNITY_Delivery Manifest Tripwire|Delivery Manifest Tripwire]]
- [[_COMMUNITY_Taxon to Trophic Level Matching|Taxon to Trophic Level Matching]]
- [[_COMMUNITY_Region Validation Checks|Region Validation Checks]]
- [[_COMMUNITY_Model Table Formatting|Model Table Formatting]]
- [[_COMMUNITY_Worker Timeout Runner|Worker Timeout Runner]]
- [[_COMMUNITY_Model Accessor Methods|Model Accessor Methods]]
- [[_COMMUNITY_Common Year Selection|Common Year Selection]]
- [[_COMMUNITY_The Two Jensen Concepts|The Two Jensen Concepts]]
- [[_COMMUNITY_Cross-Model Collection|Cross-Model Collection]]
- [[_COMMUNITY_Distillation Tests|Distillation Tests]]
- [[_COMMUNITY_Validation Check Migration|Validation Check Migration]]
- [[_COMMUNITY_Task Dispatch Internals|Task Dispatch Internals]]
- [[_COMMUNITY_Execution Record Tests|Execution Record Tests]]
- [[_COMMUNITY_EEZ Notebook Tests|EEZ Notebook Tests]]
- [[_COMMUNITY_TE005 Release Validation|TE005 Release Validation]]
- [[_COMMUNITY_Mapper Output Format|Mapper Output Format]]
- [[_COMMUNITY_Monte Carlo Sampling|Monte Carlo Sampling]]
- [[_COMMUNITY_Catch Warning Tests|Catch Warning Tests]]
- [[_COMMUNITY_Stale PPR Row Repair|Stale PPR Row Repair]]
- [[_COMMUNITY_Delivery Manifest Builder|Delivery Manifest Builder]]
- [[_COMMUNITY_Global Package Builder|Global Package Builder]]
- [[_COMMUNITY_Skill Bundle Builder|Skill Bundle Builder]]
- [[_COMMUNITY_EEZ Packaging Tests|EEZ Packaging Tests]]
- [[_COMMUNITY_EEZ Pipeline Tests|EEZ Pipeline Tests]]
- [[_COMMUNITY_Group Column Migration|Group Column Migration]]
- [[_COMMUNITY_Promotion Manifest Builder|Promotion Manifest Builder]]
- [[_COMMUNITY_The 1995 PPR Method|The 1995 PPR Method]]
- [[_COMMUNITY_Global Scope Detection|Global Scope Detection]]
- [[_COMMUNITY_Alternate Source Discovery|Alternate Source Discovery]]
- [[_COMMUNITY_Supplement Discovery|Supplement Discovery]]
- [[_COMMUNITY_Atlas Packaging|Atlas Packaging]]
- [[_COMMUNITY_Input Snapshot Bootstrap|Input Snapshot Bootstrap]]
- [[_COMMUNITY_LME Source Retrieval|LME Source Retrieval]]
- [[_COMMUNITY_Pprcalculator|Pprcalculator]]
- [[_COMMUNITY_Run Distillation|Run Distillation]]
- [[_COMMUNITY_Init|Init]]
- [[_COMMUNITY_Pprcalculator|Pprcalculator]]
- [[_COMMUNITY_Test Diagnose Sppr|Test Diagnose Sppr]]
- [[_COMMUNITY_Test Diagnose Sppr|Test Diagnose Sppr]]
- [[_COMMUNITY_Test Diagnose Sppr|Test Diagnose Sppr]]
- [[_COMMUNITY_Test Diagnose Sppr|Test Diagnose Sppr]]
- [[_COMMUNITY_Test Diagnose Sppr|Test Diagnose Sppr]]
- [[_COMMUNITY_Test Diagnose Sppr|Test Diagnose Sppr]]
- [[_COMMUNITY_Test Diagnose Sppr|Test Diagnose Sppr]]

## God Nodes (most connected - your core abstractions)
1. `PPRCalculator` - 57 edges
2. `run_analysis()` - 30 edges
3. `DataFrame` - 28 edges
4. `ModelData` - 26 edges
5. `_TaskRunner` - 20 edges
6. `build_model_tables()` - 19 edges
7. `PPRCalculator` - 17 edges
8. `add_species_ppr()` - 17 edges
9. `aggregate_groups()` - 17 edges
10. `Series` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Article/Model Quality Rubric (55 Loadability / 20 Documentation / 15 Spatial Fit / 10 Recency)` --semantically_similar_to--> `Spatial Overlap Flags (low_lme_overlap, prefer_eez_candidate, review_110_120)`  [INFERRED] [semantically similar]
  PPRAtlas/README.md → SeaAroundUsExtraction/README.md
- `NPPExtraction — Net Primary Production per Region` --shares_data_with--> `get_NPP (Net Primary Production)`  [INFERRED]
  README.md → PPREstimation/PPRCalculator.py
- `Group-Level Jensen-Affected PPR Aggregation (SeaAroundUs)` --semantically_similar_to--> `monte_carlo_SPPR Jensen's-Inequality Correction`  [INFERRED] [semantically similar]
  SeaAroundUsExtraction/README.md → PPREstimation/information/SPPR_Methods.md
- `Pauly & Christensen (1995), Nature 374, 255–257` --references--> `Christensen & Pauly (1995)`  [AMBIGUOUS]
  SeaAroundUsExtraction/README.md → PPREstimation/information/SPPR_Methods.md
- `Pilot Modelled Set (Top-10 Ecosystems, 16 Models)` --shares_data_with--> `Global Estimation Worksheet (167 Ecosystems: 66 LME, 84 EEZ, 17 High Seas)`  [INFERRED]
  README.md → PPRAtlas/README.md

## Import Cycles
- 1-file cycle: `PPREstimation/PPRCalculator.py -> PPREstimation/PPRCalculator.py`
- 1-file cycle: `PPREstimation/create_PPRS_excel.py -> PPREstimation/create_PPRS_excel.py`
- 1-file cycle: `PPREstimation/tests/test_create_pprs_excel.py -> PPREstimation/tests/test_create_pprs_excel.py`
- 1-file cycle: `PPREstimation/tests/test_diagnose_sppr.py -> PPREstimation/tests/test_diagnose_sppr.py`
- 1-file cycle: `PPREstimation/tests/test_monte_carlo_sppr.py -> PPREstimation/tests/test_monte_carlo_sppr.py`

## Hyperedges (group relationships)
- **Two Distinct Meanings of Jensen's Inequality in GlobalPPREstimation** — readme_ppr, seaaroundusextraction_readme_group_jensen_aggregation, information_sppr_methods_jensen_correction, seaaroundusextraction_readme_convexity_bound_check [INFERRED 0.85]
- **Model Loading to SPPR Computation Pipeline** — pprestimation_modeldata_class, pprestimation_pprcalculator_class, pprestimation_pprcalculator_constructor, information_sppr_methods_sppr [INFERRED 0.80]
- **Detritus Recycling Fixed-Point Solve** — information_sppr_methods_detritus_recycling, pprestimation_pprcalculator_build_det_bc, pprestimation_pprcalculator_solve_det_scaling, information_sppr_methods_spectral_radius_condition, pprestimation_pprcalculator_sppr_new [EXTRACTED 1.00]
- **SeaAroundUs pipeline scope-config family (pilot/eez/global/comparison/sensitivity)** — config_eez, config_global, config_global_eez_comparison, config_global_te005, config_pilot [INFERRED 0.85]
- **LME catch extraction to EwE functional-group mapping workflow** — config_pilot, seaaroundusextraction_requirements, ewe_species_to_group_mapper_skill [INFERRED 0.75]
- **EwE Species-to-Group Mapper cross-product packaging** — ewe_species_to_group_mapper_skill, agents_openai, assets_icon [EXTRACTED 1.00]
- **Redundancy Verification and Corruption Repair Flow** — plans_2026_09_05_projects_integration_redundancy_verification, plans_2026_09_05_projects_integration_verify_redundant_script, superpowers_redundancy_verdicts_content_addressed_store, superpowers_redundancy_verdicts_corruption_repair [EXTRACTED 1.00]
- **Nested Git Repository Collapse Safety Flow** — specs_2026_09_05_projects_integration_design_nested_git_collapse, specs_2026_09_05_projects_integration_design_external_clone_safety_net, superpowers_ppre_provenance_doc [EXTRACTED 1.00]
- **Pre-Restructure Safety Net Flow** — specs_2026_09_05_projects_integration_design_gitignore_anchoring, plans_2026_09_05_projects_integration_safety_net_commit, plans_2026_09_05_projects_integration_redundancy_verification [INFERRED 0.85]

## Communities (80 total, 18 thin omitted)

### Community 0 - "Spatial Unit Geometry"
Cohesion: 0.07
Nodes (52): MultiPolygon, Polygon, _area_audit(), area_km2(), build_eez_spatial_outputs(), _crosses_dateline(), flags_for_eez(), flags_for_pair() (+44 more)

### Community 1 - "Sea Around Us Download"
Cohesion: 0.06
Nodes (44): catch_url(), _download(), download_pilot_inputs(), download_unit_inputs(), eez_units_from_catalog(), _endpoint(), exploited_url(), load_units_from_spatial_index() (+36 more)

### Community 2 - "Excel Workbook Builders"
Cohesion: 0.07
Nodes (43): addCsvSheet(), addKeyValueSheet(), applyFormatsByHeaders(), buildRegionalWorkbook(), buildSummaryWorkbook(), cleanName(), excelColumn(), inspectWorkbook() (+35 more)

### Community 3 - "Ecopath Model Loading"
Cohesion: 0.05
Nodes (35): get_DC(), get_model_data(), get_model_diet_data(), get_model_metadata(), get_seq2name(), load_json_dict(), Any, DataFrame (+27 more)

### Community 4 - "SPPR Workbook Export Tests"
Cohesion: 0.05
Nodes (15): PPRCalculator, one_health_row(), Tests for create_PPRS_excel.py -- the per-model SPPR/PPR Excel exporter and its, SPPR_2015 resolves only PP and Import, so dropping Import already leaves PP alon, SPPR_1986 returns one un-attributed column, so PP cannot be separated out of it., Trim model_health to a single TE option: each row costs a worker restart under a, cheap_tables ran under the default budget, i.e. in a worker. Inline must match i, Losing the worker costs the time budget, never the results. (+7 more)

### Community 5 - "PPR Core Calculation"
Cohesion: 0.09
Nodes (30): add_species_ppr(), aggregate_groups(), calculate_sppr(), Return specific PPR, `(1 / te) ** (tl - 1)`.      Scalars remain scalars; pandas, Add `sppr` and `ppr` to species/taxon catch rows., Aggregate taxa to groups using the catch-weighted mean trophic level.      This, _validate_te(), Primary production required pilot pipeline. (+22 more)

### Community 6 - "Pipeline Orchestration"
Cohesion: 0.14
Nodes (29): analysis_directories(), build_unit_manifest(), copy_spatial_deliverables(), _coverage_table(), load_analysis_units(), load_config(), load_trophic_reference(), prepare_trophic_reference() (+21 more)

### Community 7 - "Catch Ingestion and Distillation"
Cohesion: 0.13
Nodes (30): distill_archive(), Distill a Sea Around Us catch archive to one row per taxon per year.  The proces, Return one row per taxon per year for a single catch archive.      Tonnage is su, Write a distilled frame as gzipped CSV and return the path., write_distilled(), available_years(), available_years_from_archive(), _catch_csv_name() (+22 more)

### Community 8 - "Monte Carlo SPPR Tests"
Cohesion: 0.07
Nodes (29): PPRCalculator, black_sea(), _calc(), Tests for the method_kwargs / exclude_diverged / return_diagnostics additions to, Keys the wrapper already controls must not be settable twice from two places., Omitting method_kwargs must behave exactly like passing an empty dict., With exclude_diverged=True, FAIL-divergence draws must be dropped from the avera, The gate may only ever remove draws, and its rejections must be labelled 'diverg (+21 more)

### Community 9 - "PPRCalculator Detritus Internals"
Cohesion: 0.13
Nodes (16): Exception, ndarray, DataFrame, Build the per-group transfer-efficiency (TE) vector or matrix.          Args:, Christensen & Pauly (1995)-style per-group SPPR = TE^(1-TL).          Uses each, SPPR_1995 variant that linearly interpolates between bracketing integer trophic, Build the detritus recycling system (I - B) x = c for the GE / With Egestion mod, Return the spectral radius (largest absolute eigenvalue) of M.          Used to (+8 more)

### Community 10 - "Model Report Tables"
Cohesion: 0.13
Nodes (26): _budget_text(), build_footprint_table(), build_groups_table(), build_health_table(), build_mc_table(), build_model_tables(), build_notes_table(), build_sppr_tables() (+18 more)

### Community 11 - "Archive Redundancy Verification"
Cohesion: 0.15
Nodes (24): _make_zip(), Path, Tests for tools/verify_redundant.py.  Covers every category the verifier must di, Mirrors the real PPRAtlas case: the target directory has a file sitting AT the, An extra search root must not paper over a genuinely absent entry -- only conten, Regression case for the in-place content-hash check.      Same path AND same siz, An entry absent from the target directory, but whose content lives in a second, test_absent_entry_still_fails_even_with_extra_root() (+16 more)

### Community 12 - "Atlas Catalog and Archive"
Cohesion: 0.12
Nodes (15): archive_index(), Human-readable archive navigation with short relative paths., build_catalog(), new_article(), Join the fixed ecosystem selection to audited article assignments., read_json(), rank_regions(), select_regions() (+7 more)

### Community 13 - "Validation Notebook Builders"
Cohesion: 0.13
Nodes (20): build_scope_validation_notebook(), build_validation_notebook(), Create a compact, executable all-unit validation notebook., Create the executable pilot-validation research notebook., main(), main(), main(), Path (+12 more)

### Community 14 - "SPPR Excel Assembly"
Cohesion: 0.13
Nodes (24): _first(), _format_model_section(), _health_summary(), main(), _mc_summary(), MethodSpec, _pop_timeout_flag(), Export one Excel workbook per Ecopath model, holding every SPPR method side by s (+16 more)

### Community 15 - "Source File Retrieval"
Cohesion: 0.12
Nodes (12): Validate source files and recover ZIP members using short, generated paths., recover_archive(), save_material(), validate_bytes(), Retrieve MHI model tables through NOAA's published public FTP archive., Retrieve curated public URLs; record failures and validate actual response bytes, Recover a PDF wrapped in literal archived HTTP headers, preserving provenance., retrieve() (+4 more)

### Community 16 - "Integration Design Record"
Cohesion: 0.16
Nodes (24): aggregate_groups() Function, Projects Integration Implementation Plan, SAU Promotion Manifest Classification, Redundancy Verification Procedure, Pre-Restructure Safety-Net Commit, verify_redundant.py Script, All-Years Catch Distillation, calculate_sppr(tl, te) Function (+16 more)

### Community 18 - "PPRCalculator Diagnostics"
Cohesion: 0.15
Nodes (12): PPRCalculator, Series, Return the sorted seq IDs of all imported-diet (Import) groups.          Import, Convert a per-group SPPR into total primary production required (PPR) by the cat, Return the net primary production (NPP) of the system.          NPP is the total, Return the fraction of available NPP appropriated by the catch (PPR / NPP)., Relabel the index (and columns) of one or more SPPR-style results.          Typi, Check the two Ecopath mass-balance identities hold (within tolerance). (+4 more)

### Community 19 - "Pipeline Scope Configs"
Cohesion: 0.22
Nodes (22): openai.yaml (cross-product agent manifest), icon.svg (skill icon: three rising yellow/red/orange bars), eez.yml (EEZ scope config), global.yml (global scope config), global_eez_comparison.yml (global vs EEZ comparison scope config), global_te005.yml (transfer-efficiency=0.05 sensitivity config), include_catch_types (Landings/Discards filter), include_reporting_status (Reported/Unreported filter) (+14 more)

### Community 20 - "Ecopath Model Balancing"
Cohesion: 0.11
Nodes (12): ModelData, Core constructor used by __init__: build the calculator from a loaded ModelData., Normalize the ordering of every Series/DataFrame attribute on the instance., Unpack the fully-filled groups table into the individual named vectors., # NOTE: trophic levels are resolved further down, after the flow vectors exist -, Apply standard Ecopath defaults and sync the mass-balance flows with the ratios., Primary constructor: build the calculator directly from a model identifier., Fill missing mass-balance variables via a per-group Linear Inverse Model (SLSQP) (+4 more)

### Community 21 - "EEZ Release Validation Tests"
Cohesion: 0.20
Nodes (17): call(), cells(), group_fixture(), literal_comparison(), Mutation tests for the independent release audit; no spreadsheet authoring depen, A single taxon that is either TL-matched with zero catch, or has catch but no TL, test_check_workbooks_checks_real_export_boundaries(), test_compact_export_rejects_every_core_column_and_intermediate_cumulative() (+9 more)

### Community 22 - "Atlas Integration Overview"
Cohesion: 0.14
Nodes (19): Integration Task Checklist, Integration Data Flow (Snapshots → Selected Join → Curated Archive & Map), PPR Ecopath Atlas Integration Goal (Extend to 167 Ecosystems), Searchable Source Archive (archive/index.html), archive/files/ Content-Addressed Article Store, Damaged East China Sea PDF and Verified Replacement, Global Estimation Worksheet (167 Ecosystems: 66 LME, 84 EEZ, 17 High Seas), Interactive Ecopath Atlas Map (index.html) (+11 more)

### Community 23 - "EEZ Release Validation"
Cohesion: 0.22
Nodes (17): boolean_check(), check_compact_cells(), check_comparison(), check_empty_region(), check_groups(), check_table_cells(), check_value(), check_workbooks() (+9 more)

### Community 24 - "Method Documentation"
Cohesion: 0.15
Nodes (17): Pauly & Christensen (1986), SPPR Calculation Methods Reference (SPPR_Methods.md), ModelData Loading Guide Section, PPRCalculator Usage Guide Section, User Guide: ModelData and PPRCalculator, PPREstimation Claude Instructions Overview, ModelData Class, ModelData(model_input) Constructor (+9 more)

### Community 25 - "Ecopath Core Concepts"
Cohesion: 0.13
Nodes (16): Diet Composition Matrix (DC), SPPR (Specific Primary Production Required), Transfer Efficiency (TE) and TE_option, Trophic Level (TL), balance_model, PPRCalculator Class, PPRCalculator(...) Primary Constructor, PPRCalculator.from_dict (+8 more)

### Community 26 - "SPPR Solver Formulations"
Cohesion: 0.16
Nodes (16): Detritus Recycling Coupled System ((I − B)x = c), Gamma-Distribution TE Resampling, Leontief Input-Output Formulation ((I − A)⁻¹), Nullspace Fixed-Point Formulation (x = A·x, nullspace of L = A − I), Spectral Radius Convergence Condition (b = ρ(B) < 1, Perron–Frobenius), _build_det_BC (Assembles Detritus Recycling System), _collapse_det_scaling (Pooled Detritus Fallback), diagnose_sppr (Trust/Convergence Diagnostic) (+8 more)

### Community 27 - "Unretrieved LME Sources"
Cohesion: 0.14
Nodes (15): LME037-Bacalso-2014 (unretrieved; distinct from 2016/2026 papers), Bacalso 2026 — Visayan Sea Article and Supplement, LME007-Buchheister-2017 (unretrieved), LME047-Cheng-2009 (unretrieved), Cheung 2007 Thesis (369 pages, user-supplied), CMFRI Bulletin 51 (Karnataka, 151 pages, user-supplied), LME036-DeepSeep-2020 (unretrieved), Karim 2018 — Bangladesh Paper (Bay of Bengal) (+7 more)

### Community 28 - "Cycle and Nullspace Utilities"
Cohesion: 0.22
Nodes (13): Matrix (nullspace) reformulation of the EwE path-summation SPPR.          Instea, _find_all_cycles(), _get_circuit_probability(), mat_from_np(), move_scattered_identity(), Removes cycles from a flow matrix Z using the Ulanowicz method.     Z[i, j] rep, Identifies rows and columns that form an identity matrix,     even if they are, Convert numpy array to sympy Matrix with optional rational resolution. (+5 more)

### Community 29 - "Transfer Efficiency Diagnostics"
Cohesion: 0.13
Nodes (15): DataFrame, divergent_report(), _flat_te(), An explicit TE matrix overrides TE_option, and inv_te must follow it., Lower TE amplifies every path, so b must rise as TE falls., b is measured on diag(theta) @ B, so retention loss must lower it., det_collapse_mode is a remedy, not a diagnosis: b is measured pre-decision., A constant TE matrix at `value`, with detritus rows left at 1 (as SPPR_new expec (+7 more)

### Community 30 - "EEZ Notebook Execution"
Cohesion: 0.22
Nodes (13): build_notebook(), main(), Build and execute the EEZ validation notebook, also exporting readable HTML., fingerprint(), invalidate_execution(), Bind successful EEZ notebook execution to the exact current scientific outputs., Hash exact file membership and bytes; exclude the execution record itself., Invalidate previous success before starting any notebook rerun. (+5 more)

### Community 31 - "Delivery Manifest Tripwire"
Cohesion: 0.20
Nodes (14): DataFrame, _load_manifest_module(), Tripwire test for build_delivery_manifest.py's validation-check name coupling., A real validate_region() result, so tests read the current check names., The real, current set of check names validate_region emits., Just the checks validate_region labels as boolean pass/fail results., reconciliation_failures must count *all* the boolean checks, not just some., The manifest must not claim a jensen_violations result it never computes. (+6 more)

### Community 32 - "Taxon to Trophic Level Matching"
Cohesion: 0.24
Nodes (12): assign_trophic_levels(), normalize_taxon_name(), Assign TL values using explicit, ordered matches and transparent fallbacks., _set_matches(), _standardize_reference(), DataFrame, Series, test_group_fallback_builds_reference_mean_within_each_classification() (+4 more)

### Community 33 - "Region Validation Checks"
Cohesion: 0.21
Nodes (10): Return long-form validation metrics for one unit.      ``commercial_ppr_differen, _sum_ppr(), validate_region(), DataFrame, `10 ** (TL - 1)` is convex, so the group PPR can never exceed the taxon sum., A weighting error that inflates group PPR past the taxon sum must not pass., test_validate_region_detects_group_ppr_mismatch(), test_validate_region_flags_group_ppr_above_the_taxon_sum() (+2 more)

### Community 34 - "Model Table Formatting"
Cohesion: 0.14
Nodes (12): _autoformat(), load_model(), ModelTables, Every table for one model, plus everything worth telling the user about the run., Load one Ecopath JSON into a calculator, returning it with a human-readable labe, Freeze the labels, widen the columns and give the numbers a readable format., Build every table for one model JSON and write it to a single workbook.      A, write_model_excel() (+4 more)

### Community 35 - "Worker Timeout Runner"
Cohesion: 0.26
Nodes (4): Runs SPPR tasks in a worker process, killing the worker when one overruns its bu, Shut the worker down, politely first and then by force., Run one task under the time budget and return the standard envelope., _TaskRunner

### Community 36 - "Model Accessor Methods"
Cohesion: 0.19
Nodes (7): Return the diet-composition (DC) matrix, optionally redefining detritus rows., Return the flow matrix Z = DC * q (consumption-weighted diet), with DET rows red, Return the sorted seq IDs of all detritus (DET) groups.          Returns:, Return the sorted seq IDs of all regular (consumer) groups.          Returns:, Compute the trophic level of every group via the standard linear-algebra definit, Pauly & Christensen (1986)-style SPPR using a single catch-weighted trophic leve, 2015-method SPPR: a matrix-inversion (Leontief-style) formulation.          Detr

### Community 37 - "Common Year Selection"
Cohesion: 0.24
Nodes (8): common_year_for_archives(), latest_common_year(), Return a validated configured year or the latest year in the intersection., Choose a common year across spatial alternatives, excluding audited empty source, test_empty_year_intersection_is_rejected(), test_latest_common_year_uses_intersection(), test_requested_common_year_is_accepted(), test_requested_year_missing_from_a_unit_is_rejected()

### Community 38 - "The Two Jensen Concepts"
Cohesion: 0.24
Nodes (11): monte_carlo_SPPR Jensen's-Inequality Correction, Primary Production Required (PPR), All Sea Around Us EEZs — TE = 0.1 (EEZ_README), group_ppr_within_convexity_bound Validation Check, Group-Level Jensen-Affected PPR Aggregation (SeaAroundUs), Pauly & Christensen (1995), Nature 374, 255–257, All Sea Around Us EEZs — TE = 0.1 Release, Spatial Overlap Flags (low_lme_overlap, prefer_eez_candidate, review_110_120) (+3 more)

### Community 39 - "Cross-Model Collection"
Cohesion: 0.20
Nodes (10): _cell(), collect_models_excel(), _collected_frame(), _model_identity(), _ordered_union(), (model_number, model_name, model_year) for a workbook stem, via ModelData's own, `seen` ordered by `preferred`, with anything unknown to `preferred` appended as, table.at[row, col] or NaN -- missing row, missing column and duplicate labels in (+2 more)

### Community 40 - "Distillation Tests"
Cohesion: 0.39
Nodes (8): Path, archive(), _row(), test_distill_archive_honours_the_catch_type_filter(), test_distill_archive_returns_empty_frame_for_empty_archive(), test_distill_archive_returns_one_row_per_taxon_per_year(), test_distill_archive_sums_over_fishing_entity(), test_write_distilled_produces_a_readable_gzip()

### Community 41 - "Validation Check Migration"
Cohesion: 0.39
Nodes (8): compute_checks(), main(), migrate(), Path, Migrate existing validation.csv files to the checks validate_region now emits., Directory holding unit_id's species/commercial/functional.csv., Return (tl_coverage_complete, group_ppr_within_convexity_bound) or None each if, region_dir()

### Community 42 - "Task Dispatch Internals"
Cohesion: 0.25
Nodes (8): _dispatch_task(), _drop_unpicklable_extras(), Run one timed unit of work against `model`.      Kept at module level and keye, Run one task in this process, with no time budget, in the standard envelope., Salvage a method result whose extras dict cannot cross the process boundary., Worker-process entry point: hold one model and answer one task at a time over `c, _run_task_inline(), _worker_main()

### Community 43 - "Execution Record Tests"
Cohesion: 0.54
Nodes (7): module(), Execution records bind a successful notebook to the exact current release files., release(), test_changed_or_added_release_file_invalidates_record(), test_deleted_file_or_missing_record_is_rejected(), test_refuse_unsuccessful_notebook(), test_successful_execution_record_verifies_and_excludes_itself()

### Community 44 - "EEZ Notebook Tests"
Cohesion: 0.54
Nodes (6): builder(), prepare(), test_failed_rerun_preserves_old_artifacts_but_invalidates_success(), test_generated_notebook_has_no_jensen_comparison(), test_nondefault_thresholds_appear_in_generated_rule_narrative(), test_successful_builder_publishes_executed_notebook_html_and_record()

### Community 45 - "TE005 Release Validation"
Cohesion: 0.43
Nodes (6): DataFrame, Path, _bool_validation_passed(), main(), Independent validation of the TE=0.05 release against the TE=0.10 release., _read_species()

### Community 46 - "Mapper Output Format"
Cohesion: 0.60
Nodes (6): Confidence Color Coding (Red/Green/Yellow), Skill Output Preview Screenshot, Per-Mapping Rationale Text, PPR and Species PPR Columns, Species-to-Group Mapping Output Format, Xu et al. 2022 East China Sea EwE Models (M1997, M2018)

### Community 47 - "Monte Carlo Sampling"
Cohesion: 0.33
Nodes (3): Return the sorted seq IDs of all primary-producer (PP) groups.          Returns:, Run SPPR_new and force exact global balance by solving the single detritus SPPR., Monte-Carlo uncertainty propagation over transfer efficiency.          Repeatedl

### Community 48 - "Catch Warning Tests"
Cohesion: 0.47
Nodes (6): PPRCalculator, black_sea(), _calc(), test_negative_catch_is_warned(), test_zero_catch_is_warned_without_invalidating_divergence(), toy()

### Community 49 - "Stale PPR Row Repair"
Cohesion: 0.60
Nodes (5): fix_file(), main(), Path, Recompute the stale commercial_ppr/functional_ppr/*_ppr_difference rows.  These, unit_dir_for()

### Community 50 - "Delivery Manifest Builder"
Cohesion: 0.50
Nodes (4): Path, main(), Create a checksummed manifest for the completed global deliverables., sha256()

### Community 51 - "Global Package Builder"
Cohesion: 0.60
Nodes (4): Path, include(), main(), Package the global pipeline while leaving any open pilot workbooks untouched.

### Community 52 - "Skill Bundle Builder"
Cohesion: 0.60
Nodes (4): included(), main(), Path, Build ewe-species-to-group-mapper.skill from the source directory.

### Community 55 - "Group Column Migration"
Cohesion: 0.60
Nodes (4): main(), migrate(), Path, Rewrite existing SeaAroundUs outputs to the trimmed schema.  Every surviving val

### Community 56 - "Promotion Manifest Builder"
Cohesion: 0.67
Nodes (3): digest(), Path, walk()

### Community 57 - "The 1995 PPR Method"
Cohesion: 0.67
Nodes (3): Christensen & Pauly (1995), SPPR_1995 (Christensen & Pauly 1995 Method), SPPR_1995_TL_fix (Integer-TL Interpolation)

### Community 58 - "Global Scope Detection"
Cohesion: 0.67
Nodes (3): is_global_scope(), Return whether a named release covers the all-unit global scope., test_global_release_variants_keep_global_scope_behavior()

### Community 64 - "Pprcalculator"
Cohesion: 0.67
Nodes (3): get_NPP (Net Primary Production), get_PPR (SPPR → Total PPR Footprint), get_PPR2NPP_ratio (%PPR of NPP)

## Ambiguous Edges - Review These
- `Christensen & Pauly (1995)` → `Pauly & Christensen (1995), Nature 374, 255–257`  [AMBIGUOUS]
  SeaAroundUsExtraction/README.md · relation: references

## Knowledge Gaps
- **77 isolated node(s):** `Any`, `Series`, `Path`, `Path`, `DataFrame` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Christensen & Pauly (1995)` and `Pauly & Christensen (1995), Nature 374, 255–257`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `PPRCalculator` connect `PPRCalculator Diagnostics` to `Model Table Formatting`, `Worker Timeout Runner`, `Model Accessor Methods`, `Pprcalculator`, `SPPR Workbook Export Tests`, `Monte Carlo SPPR Tests`, `PPRCalculator Detritus Internals`, `Model Report Tables`, `SPPR Excel Assembly`, `Monte Carlo Sampling`, `Catch Warning Tests`, `Ecopath Model Balancing`, `Cycle and Nullspace Utilities`, `Transfer Efficiency Diagnostics`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `ModelData` connect `Model Table Formatting` to `Worker Timeout Runner`, `Ecopath Model Loading`, `SPPR Workbook Export Tests`, `PPRCalculator Detritus Internals`, `Model Report Tables`, `SPPR Excel Assembly`, `PPRCalculator Diagnostics`, `Ecopath Model Balancing`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `PPREstimation Project` connect `Method Documentation` to `Pprcalculator`, `SPPR Excel Assembly`, `Atlas Integration Overview`, `Ecopath Core Concepts`, `SPPR Solver Formulations`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `PPRCalculator` (e.g. with `Exception` and `MethodSpec`) actually correct?**
  _`PPRCalculator` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ModelData` (e.g. with `Exception` and `ModelData`) actually correct?**
  _`ModelData` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `_TaskRunner` (e.g. with `ModelData` and `PPRCalculator`) actually correct?**
  _`_TaskRunner` has 2 INFERRED edges - model-reasoned connections that need verification._