# LME_014 — selected native model and regional calculation

Updated 2026-09-28. The user selected **PAT2024_FalklandShelf_2020_native** because it did not fail. The exact ID and rationale are saved in [LME_014.xlsx](../../../../../../LME_014.xlsx), Overview. GE, TE and With Egestion all remain **WARN**, not OK. The selected regional calculation is complete and validated. Central registration/consolidation is queued for the parent task; this task did not write Project.xlsx.

The earlier source reports and extraction comparison are frozen preselection evidence. Their statements that no model was selected describe that earlier stage. This report is the current selection record.

## What was selected

| Candidate | Evidence and outcome | Selection |
|---|---|---|
| PAT2024_FalklandShelf_2020_native | Exact author-supplied native 2020 database; coupled completion of unknown living/producer B and EE; GE / TE / With Egestion = WARN / WARN / WARN | Selected by the user |
| PAT2024_FalklandShelf_2020_published_tables | Article Table 4 plus supplements retained separately; no documented alignment of the one-detritus S2 diet with two final detritus pools | Not selected; all three NOT_RUN |
| OcampoReinaldo2016_SanMatiasGulf_1970 | Article and newly supplied complete diet supplement; standalone juvenile-hake production/predation inconsistency and unresolved source fields | Not selected; FAIL / FAIL / FAIL |

Büring et al. (2024), DOI [10.1017/S0025315423000887](https://doi.org/10.1017/S0025315423000887), supplies a Falkland shelf model for 2020, 36 groups, two fleets and approximately 200,000 km² to 300 m depth. PAT-2023 is the retained paper-folder identifier, not the publication year. The native database and printed tables differ in diet/import values beyond rounding and in detritus EE. Initial Table S3 is not another complete balanced model. No variants were averaged or pooled.

## Computational input and source fidelity

- Canonical native extraction: [model.json](../../model.json), SHA-256 `151d6005486718dd76ce4343dd5792561c5da40112191dc4db64968ba649592e`. Missing native values remain missing.
- Selected computational input: [derived JSON](computational_input/14_140001_PAT2024_FalklandShelf_2020_native_(2020).json), SHA-256 `9880e521a406974367530ffb06f13392714dba57b9645c38a1b1448926d83d17`. It is byte-identical to the input that produced the audited three WARN diagnoses.
- [Completion provenance](selection_20260928/selection_provenance.json) lists every derived cell; the native Access file and all eleven inventoried source files are unchanged.

The native database stores inputs and leaves 13 living/producer biomasses and some EEs unresolved. The computational input solves the coupled production equations

`B_i × PB_i × EE_i = catch_i + BA_i + emigration_i − immigration_i + Σ_j(B_j × QB_j × DC_ji)`.

Known native biomass, diet, catches, rates, EE, habitat area and migration are retained. Unknown biomasses are solved simultaneously, then missing EE is calculated from the same balances. Kingclip immigration is included. The matrix residual is 1.13 × 10⁻¹⁴; all solved biomasses are positive and recomputed EE lies within [0,1]. The solution reproduces the printed Table 4 outputs to their rounding, including benthic crustacean B = 1.371551 and phytoplankton B = 3.255569 t km⁻². These are Ecopath-derived quantities, not arbitrary biomass defaults.

The region-local adapter uses the supported regional SPPR stage and shared exporter with only the three selected methods, each bounded at 180 seconds. It verifies the input hash, accommodates the legacy filename parser and restores the audited loader settings: underdetermined=False, normalize_DC=False, DC_tol=0.001, zero_catch=True, zero_biomass_accum=True, default_gs=True. Native living inputs explicitly supply the relevant zeros and GS. Both detritus pools remain separate (collapse=never, opening=none). All three calculations completed; none timed out. The shared default loader is unsuitable for rerunning this exact selection because it changes those settings. Use the region-local adapter documented below.

The selected workbook reproduces all 777 numeric cells of the previously audited completed group table. This verifies that the production coefficients use the same computational state as the WARN diagnostics. The earlier uncompleted default-loader FAIL run is retained under default_loader_diagnostics/ and is not selected.

## Remaining warnings and limitations

The full direct diagnostic returns remain in [diagnostic_report.md](diagnostic_report.md) and [diagnostics_raw.json](diagnostics_raw.json). That diagnostic report contains only GE, TE and With Egestion returns.

- Baleen Whales has EE = 0. TE additionally has near-zero TE in Toothed Whales and Dolphins, Seals and Sea Lion, and Seabirds. TE’s relative PP-budget gap is approximately 0.0001256 (0.01256%); GE and With Egestion are approximately 1.17 × 10⁻¹⁶. The TE warning was retained.
- The native fleet discard fate sends both fleets to Detritus, while five consumers eat the separate Discards pool. The loader does not retain explicit fleet-specific discard supply. It forces detritus identity routing/EE = 1 and derives detritus accumulation, including negative accumulation for Discards. Native BA = 0 is preserved in source and computational JSON; loader completion is separately visible. The unknown native Detritus biomass is also assigned the loader’s nonliving placeholder of 1. This is not a source biomass estimate or a new living-group completion. These facts limit ecological interpretation despite numerical balance.
- The model represents the Falkland shelf, not the entire Patagonian Shelf LME. Adults of toothfish and certain deep-water skates and grenadiers are explicitly excluded. No model-area percentage or catch-area fraction was invented. Historical regional calculations transfer 2020 coefficients to 1950–2019 catches; they do not reconstruct annual historical food webs.
- WARN acceptance follows the existing regional configuration policy and the user’s selection. It does not establish that all source inconsistencies have disappeared. Annual status “ok” means the calculation was admitted; the diagnostic status remains WARN.

## Catch matching and coverage

All 250 regional taxa were reviewed. Twenty-nine have supported assignments and 221 remain unresolved. Explicit Table 2 membership takes precedence over broad group labels. Nine bivalve records are contained by the paper’s explicit Bivalves/Scallops definition; their primary WoRMS records are retained in [mapping taxonomy evidence](selection_20260928/mapping_taxonomy_evidence.json). For example, [Zygochlamys patagonica](https://www.marinespecies.org/aphia.php?p=taxdetails&id=236717) is the Patagonian scallop. Membership support is distinct from geographic representativeness.

D. gahi is split between ASC (0.49237747138886107) and SSC (0.507622528611139) using native 2020 cohort landings. This constant historical mixture is an approximation. The genus-level Merluccius record uses the region’s identified hake catches over 1950–2019: M. hubbsi 0.994820308056964 and M. australis 0.005179691943036082. This is inferred composition, not a published annual split. [Split weights](selection_20260928/split_weights.csv), [all mapping decisions](selection_20260928/mapping_review.csv) and [exact numeric mapping](selection_20260928/mapping_resolved.csv) are retained.

| Catch basis | Period | Covered tonnes | Total tonnes | Coverage |
|---|---|---:|---:|---:|
| landings | 1950–2019 | 49,534,348.32 | 68,086,080.21 | 72.75% |
| landings | 2019 | 964,673.12 | 1,497,627.62 | 64.41% |
| catch | 1950–2019 | 53,548,449.68 | 73,387,141.17 | 72.97% |
| catch | 2019 | 1,038,310.57 | 1,589,890.94 | 65.31% |
| discards | 1950–2019 | 4,014,101.36 | 5,301,060.96 | 75.72% |
| discards | 2019 | 73,637.44 | 92,263.32 | 79.81% |

The largest unresolved cumulative catches are shown below. Whole-LME aggregates are not assigned using only their modeled members when that would hide unsupported components.

| Unresolved taxon | 1950–2019 catch tonnes |
|---|---:|
| Marine fishes not identified | 6,127,998 |
| Pleoticus muelleri | 3,045,018 |
| Micropogonias furnieri | 2,306,289 |
| Engraulis anchoita | 1,446,833 |
| Rajiformes | 1,405,017 |
| Cynoscion guatucupa | 595,512 |
| Cynoscion striatus | 534,624 |
| Teuthida | 437,672 |
| Mustelus schmitti | 414,631 |
| Nemadactylus bergi | 384,225 |

Pleoticus shrimp is not Munida lobster krill; croakers and anchovies are not listed within the source fish groups. Unsplit adult/juvenile toothfish and deep-water skates are not silently assigned to the shelf compartments. Missing SPPR remains blank. The standard zero/simple treatments for unidentified records are separate labeled scenarios; they are not source mappings.

## Regional results and NPP

Annual PPR is saved for 1950–2019, with all / inner / PP source scopes and landings / catch / discards bases. The three configurations have nonnegative coefficients for every source group, including unfished groups. Unresolved catch contributes no estimate to the covered-catch PPR; these are partial estimates, not a claim that the omitted catches require zero production.

Illustrative 2019 values below use all-source scope, landings, and the method treatment for unidentified catch. Covered landings are 964,673.12 of 1,497,627.62 tonnes.

| Configuration | PPR, wet-weight-equivalent tonnes | PPR / inherited NPP ensemble | Diagnosis |
|---|---:|---:|---|
| GE | 52,971,168.28 | 1.33612% | WARN |
| TE | 136,371,249.69 | 3.43976% | WARN |
| With Egestion | 26,861,230.26 | 0.67753% | WARN |

PPR/NPP divides wet-weight-equivalent PPR by nine exactly once. Existing NPP values, algorithm identities and missing years were preserved: Antoine–Morel and ensemble support 1998–2019; the other four algorithms support 2003–2019. Earlier ratios remain blank. The inherited NPP series includes documented gap filling and model-ratio methods; this task did not perform a new satellite extraction. Twenty-two historic provenance links were resolved to retained research-archive files using the relocation manifest and verified hashes; [link audit](selection_20260928/npp_provenance_links.json). No frozen NPP evidence was rewritten.

## Verification and reproduction

[Validation evidence](selection_20260928/selected_results_validation.json) records 2,250 coefficient checks, 17,010 annual-value checks and 37,800 ratio checks. Original catch, classic-taxon coefficients and numerical NPP inputs are unchanged. The supported region validator passes. Executed scientific code snapshots and hashes are retained under selection_20260928/executed_code/.

To reproduce from the project root, use:

```powershell
python regions/LME_014/models/PAT2024_FalklandShelf_2020_native/run_selected_sppr.py
python regions/LME_014/models/PAT2024_FalklandShelf_2020_native/prepare_catch_mapping.py
python tools/run_region.py --region regions/LME_014/LME_014.xlsx --stage calculate
python regions/LME_014/models/PAT2024_FalklandShelf_2020_native/validate_selected_results.py
python tools/run_region.py --region regions/LME_014/LME_014.xlsx --stage validate
```

Central metadata proposals are [here](selection_20260928/central_registration_proposal.json). Shared code, Project.xlsx and the map were not modified by this regional task.
