# Source extraction report — PAT2024_FalklandShelf_2020_native

Extracted 2026-09-28. Scope: source-faithful reconstruction and isolated model diagnostics. LME_014 Overview has no selected model; it remains unchanged. No regional PPR or central workbook values were written. The local model identifier is not an EcoBase accession.

## Bundle and evidence

All actual files in both supplied paper folders were inventoried before extraction; `../extraction_review_20260928/evidence/source_manifest.json` records filenames, byte sizes and SHA-256. The final `source_hash_verification.json` verifies every byte unchanged. Source PDFs, supplement DOCX tables and native database tables are retained through read-only evidence extraction. `extracted_tables/cell_provenance.json` maps basic, diet and fishery values to source pages/cells/record keys. PDF coordinate cells and rendered review pages reside in the shared evidence folder. Both supplementary DOCX files were rendered through Word in read-only mode; Ocampo diet pages 1–2 and PAT Table S4 page 5 were visually checked. Paper table pages were rendered and visually checked.

## Group structure and taxonomy

36 source groups. All have `Taxonomy.xlsx`, a source-qualified `taxonomy.csv`, and canonical JSON `taxon_descr`. Source spellings are preserved; no external synonym corrections or taxon assignment weights were invented. No Selected model groups worksheet update is appropriate before selection. Scientific names in labels are preserved separately from guild composition, and size/cohort definitions remain distinct.

## Import and converter validation

All eight required EwE tables are in `extracted_tables/`. The writer override `--dir-name extracted_tables` follows the active regional project contract. The extraction-input JSON is separate from canonical database `model.json`. Source CSV blanks remain blank, published zeros remain zero. Source unknown database values use `-9999`.

The stock converter ran and produced its own database JSON, conversion log, MASS_BALANCE.md and reconstructed workbook. Its output is explicitly an intermediate: it normalizes some diets, converts missing catches/imports/routing to zeros, defaults habitat area, drops printed P/Q, and converts habitat biomass. These transformations cannot silently become source data. `converter_canonical_differences.json` records each restoration in the canonical JSON; canonical diet values are never normalized. Canonical `model_reconstructed.xlsx` was regenerated and checked for workbook structure, group count, names and taxonomy. The converter's reconstruction is not a lossless source representation: it cannot retain all native fleet routing or paper-specific input/output font markers; source inputs and cell evidence remain authoritative.

Structural validator output:

```
ERROR Detritus_fate.csv row 35: fate sums to 0.0, expected 1
ERROR Detritus_fate.csv row 36: fate sums to 0.0, expected 1

2 error(s), 0 warning(s)
```

Source mass-balance tool: 5 error(s), 4 warning(s), 2 note(s). Full arithmetic and flags: `extracted_tables/source_massbalance.txt`. Its printed recomputed EEs are conditional comparisons: unknown BA/catch is numerically omitted, missing predator B/QB undercounts predation, and immigration is not represented in its eight-table contract. Critically, the standalone massbalance_check.py uses the habitat-biomass column without multiplying habitat area, making its Falkland predation comparisons inconsistent with model-area catches. Its PAT errors must not be read as native model failure. The separate native audit uses model-area B and includes immigration. Suggested BA values were not adopted. `MASS_BALANCE.md` is the stock converter's check, not a claim of strict source admission.

## Direct diagnostics and production status

The separate diagnostic report contains only the full direct returns of `PPRCalculator.diagnose_sppr(short=False, flat=False)` for GE, TE and With Egestion, or an exact not-run reason. `diagnostics_raw.json` retains the returned objects. Statuses: {'GE': 'WARN', 'TE': 'WARN', 'With Egestion': 'WARN'}. All numerical runs disable diet normalization and detritus pooling (`det_collapse_mode=never`, `det_open_mode=none`). No global variants, method inventory or Monte Carlo were run.

`diagnostic_run_record.json` records all boundary settings, warnings and exceptions. `loader_input_groups.csv`, `loader_diet.csv`, `loader_detritus_fate.csv` and `loader_completed_groups.csv` make loader alterations reviewable. The legacy loader requires a numeric filename and a parenthesized year; `loader_input/` contains an escaped copy under a local diagnostic placeholder id, not a model renumbering or EcoBase claim. For native PAT, this diagnostic copy also contains explicitly derived missing B/EE values listed in the run record; canonical source JSON remains unchanged. The loader hardcodes LME=13 internally; the canonical extraction metadata correctly says LME=14. Diagnostic calculations do not establish region identity or authorize adoption.

Production eligibility: **not established / false**. Successful computation is distinct from scientific source fidelity. No candidate is selected.

## Source tables and numerical identity

Büring et al. (2024), *Unveiling the wasp-waist structure of the Falkland shelf ecosystem: the role of Doryteuthis gahi as a keystone species and its trophic influences*, J. Mar. Biol. Assoc. UK 104 e2, DOI 10.1017/S0025315423000887. Folder PAT-2023 reflects the accepted manuscript/DOI year, not the printed publication year. The model is **Falkland Islands 2020**, FirstYear 2020 / NumYears 1, area 200,000 km², saved EwE 6.6.8.18072. The author-supplied native sup002.eweaccdb contains exactly one EcopathModel, 36 EcopathGroup rows, 1,296 EcopathDietComp records, 72 catch rows and two fleets (Trawling, Jigging). Ecosim scenario/shape tables are not additional published Ecopath model periods.

Native `Sequence`, not Access `GroupID`, fixes group order. Native group IDs and source records are retained in evidence. Native biomass is on model-area basis: B=0.002500000176951289 for Baleen Whales at habitat area=0.20000000298023224, consistent with the article's ~0.01 habitat biomass/~0.003 model-area biomass. Import-table habitat B is derived by dividing native B by Area; canonical model-area B is restored exactly from the binary value. Single-precision binary artifacts are retained, not rounded into allegedly printed values.

Native basic mapping: Area→hab_area; Biomass/Area→habitat biomass; ProdBiom→P/B; ConsBiom→Q/B; EcoEfficiency→EE; Unassim→GS; DtImports→detritus import; BiomAcc→BA. Native -9999 is unknown/unresolved. Native native `OtherMort`/`ProdCons` are unknown where sentinel-coded. Article Table 4 TL values are recorded as published outputs, not native resolved outputs. Native ImpVar supplies exact imports for every group (including stated zeros for nonconsumers). Diet rows map PredID to predator and PreyID to prey. Each native consumer diet plus import sums to within 1.2e-7 of 1; no normalization was applied.

Native `EcopathDietComp.DetritusFate` routes every living group to Detritus=36; both nonliving fate rows contain printed/native zeros. The validator expects every fate row to sum to one and flags these two source rows; they were deliberately not replaced with invented identity routing. ModelData itself forces a detritus identity block; that alteration exists only in the loader. `EcopathDiscardFate` sends both fleets' discards to Detritus=36, not Discards=35. Five consumer groups nevertheless consume Discards=35. This native configuration and the eight-table/engine omission of fleet-specific discard supply are retained as material limitations. Full fleet routing is in the native evidence JSON.

## Biomass accumulation and prose

Native BiomAcc and BiomAccRate are explicitly zero for all 36 groups; zero is therefore sourced here. Native GS=0.2 (binary representation retained) for regular groups, with producer and Detritus values zero; no convention was substituted. Kingclip has native immigration=0.003000000026077032, preserved in canonical JSON although the eight-table format has no migration table. Unknown native B (13 living/producer groups plus Detritus) and many EEs remain unresolved source fields.

## Source conflicts and independent arithmetic

The article Table 4 has 36 groups with separate Discards/Detritus, but Table 2/S2 use 35 groups and combine the detritus category. CSV S2 and native diet/import values differ beyond rounding. Native Detritus EE=0 versus printed Table 4 EE=0.05. These are not reconciled by pooling or averaging. The published-table candidate remains separate. Table S3 is explicitly *initial* P/B/Q/B/EE, lists 45 rows including groups absent from the final model, and has no complete aligned B/diet model. Its full cell contents are retained as initial/predecessor evidence, not adopted as a fourth balanced model.

The independent audit `../extraction_review_20260928/evidence/native_independent_balance_audit.json` solves the native unknown living biomasses from the coupled production equations, preserving all source diet, catch, migration and EE inputs. The matrix residual is1.13e-14; every solved living/producer biomass is positive and every recomputed EE lies in[0,1]. Solved B agrees with the article's printed outputs to source rounding (e.g. Benthic Crustaceans1.371551, Phytoplankton3.255569). The eight-table massbalance helper's contrary errors arise partly from omitting habitat-area scaling and immigration; its raw results remain visible, not silently repaired.

The diagnostic loader copy explicitly fills only native-unknown living/producer B and EE with this algebraic solution. Canonical model.json retains the native unknowns and every source value. The full direct diagnostics on this declared completion all return **WARN**: model production/consumption residuals are approximately1.67e-14/1.08e-15. GE and With Egestion PP-budget gaps are about1.17e-16; TE's gap is0.0001256. Baleen Whales EE=0 is a remaining warning, and TE has additional convergence/magnitude warning details in the direct return. The earlier uncompleted stock-loader run is retained under `default_loader_diagnostics/`; its FAIL results came from replacing unknown B with1 and losing unresolved p/q, so they do not describe the faithful coupled reconstruction. Native Discards receives no modeled detritus-fate inflow, and the loader compensates its consumption with negative detritus accumulation; fleet discard routing and native-vs-printed EE remain explicit caveats. No detritus supply, routing, diet, catches, migration or GS was invented by the algebraic completion.

## Spatial applicability

Article p.6 defines the Falkland shelf to 300 m, about 200,000 km², inside the wider Patagonian Shelf LME. It excludes adult deep-water toothfish, and separates D. gahi seasonal cohorts. No LME catch-coverage fraction is supplied or inferred. Table 2 lists Pygoscelis papua in both Penguins and Seabirds; that source overlap remains explicit for later matching.

## Final round-trip cell audit

Compared 1448 numeric/basic/diet cells between canonical JSON and the reconstructed workbook at1e-12 relative/absolute tolerance: no numeric mismatches. The stock reconstruction displays 8 canonical unknown diet cells as zero; this is a documented presentation loss, never written back into source outputs. It also collapses fleet catches, omits printed P/Q from Basic input, and loses metadata when the filename is model.json. These limitations are recorded in `roundtrip_cell_validation.json`; original eight tables and Metadata.xlsx remain authoritative.
