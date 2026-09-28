# Source extraction report — OcampoReinaldo2016_SanMatiasGulf_1970

Extracted 2026-09-28. Scope: source-faithful reconstruction and isolated model diagnostics. LME_014 Overview has no selected model; it remains unchanged. No regional PPR or central workbook values were written. The local model identifier is not an EcoBase accession.

## Bundle and evidence

All actual files in both supplied paper folders were inventoried before extraction; `../extraction_review_20260928/evidence/source_manifest.json` records filenames, byte sizes and SHA-256. The final `source_hash_verification.json` verifies every byte unchanged. Source PDFs, supplement DOCX tables and native database tables are retained through read-only evidence extraction. `extracted_tables/cell_provenance.json` maps basic, diet and fishery values to source pages/cells/record keys. PDF coordinate cells and rendered review pages reside in the shared evidence folder. Both supplementary DOCX files were rendered through Word in read-only mode; Ocampo diet pages 1–2 and PAT Table S4 page 5 were visually checked. Paper table pages were rendered and visually checked.

## Group structure and taxonomy

26 source groups. All have `Taxonomy.xlsx`, a source-qualified `taxonomy.csv`, and canonical JSON `taxon_descr`. Source spellings are preserved; no external synonym corrections or taxon assignment weights were invented. No Selected model groups worksheet update is appropriate before selection. Scientific names in labels are preserved separately from guild composition, and size/cohort definitions remain distinct.

## Import and converter validation

All eight required EwE tables are in `extracted_tables/`. The writer override `--dir-name extracted_tables` follows the active regional project contract. The extraction-input JSON is separate from canonical database `model.json`. Source CSV blanks remain blank, published zeros remain zero. Source unknown database values use `-9999`.

The stock converter ran and produced its own database JSON, conversion log, MASS_BALANCE.md and reconstructed workbook. Its output is explicitly an intermediate: it normalizes some diets, converts missing catches/imports/routing to zeros, defaults habitat area, drops printed P/Q, and converts habitat biomass. These transformations cannot silently become source data. `converter_canonical_differences.json` records each restoration in the canonical JSON; canonical diet values are never normalized. Canonical `model_reconstructed.xlsx` was regenerated and checked for workbook structure, group count, names and taxonomy. The converter's reconstruction is not a lossless source representation: it cannot retain all native fleet routing or paper-specific input/output font markers; source inputs and cell evidence remain authoritative.

Structural validator output:

```
WARN  26 group(s) have a blank Unassim. consumption — EwE will substitute 0.2 on import: Dolphins, Sea Lions, Other rays, Large rays, Small rays, Large sharks, Medium-sized sharks, Juvenile sharks ...
WARN  Biomass_accumulation.csv is entirely blank — BA is unknown in this extraction; say in REPORT.md where BA and any explicit steady-state statement were checked
WARN  Detritus_fate.csv row 1: no fate recorded
WARN  Detritus_fate.csv row 2: no fate recorded
WARN  Detritus_fate.csv row 3: no fate recorded
WARN  Detritus_fate.csv row 4: no fate recorded
WARN  Detritus_fate.csv row 5: no fate recorded
WARN  Detritus_fate.csv row 6: no fate recorded
WARN  Detritus_fate.csv row 7: no fate recorded
WARN  Detritus_fate.csv row 8: no fate recorded
WARN  Detritus_fate.csv row 9: no fate recorded
WARN  Detritus_fate.csv row 10: no fate recorded
WARN  Detritus_fate.csv row 11: no fate recorded
WARN  Detritus_fate.csv row 12: no fate recorded
WARN  Detritus_fate.csv row 13: no fate recorded
WARN  Detritus_fate.csv row 14: no fate recorded
WARN  Detritus_fate.csv row 15: no fate recorded
WARN  Detritus_fate.csv row 16: no fate recorded
WARN  Detritus_fate.csv row 17: no fate recorded
WARN  Detritus_fate.csv row 18: no fate recorded
WARN  Detritus_fate.csv row 19: no fate recorded
WARN  Detritus_fate.csv row 20: no fate recorded
WARN  Detritus_fate.csv row 21: no fate recorded
WARN  Detritus_fate.csv row 22: no fate recorded
WARN  Detritus_fate.csv row 23: no fate recorded
WARN  Detritus_fate.csv row 24: no fate recorded
WARN  Detritus_fate.csv row 25: no fate recorded
WARN  Detritus_fate.csv row 26: no fate recorded

0 error(s), 28 warning(s)
```

Source mass-balance tool: 2 error(s), 2 warning(s), 25 note(s). Full arithmetic and flags: `extracted_tables/source_massbalance.txt`. Its printed recomputed EEs are conditional comparisons: unknown BA/catch is numerically omitted, missing predator B/QB undercounts predation, and immigration is not represented in its eight-table contract. Critically, the standalone massbalance_check.py uses the habitat-biomass column without multiplying habitat area, making its Falkland predation comparisons inconsistent with model-area catches. Its PAT errors must not be read as native model failure. The separate native audit uses model-area B and includes immigration. Suggested BA values were not adopted. `MASS_BALANCE.md` is the stock converter's check, not a claim of strict source admission.

## Direct diagnostics and production status

The separate diagnostic report contains only the full direct returns of `PPRCalculator.diagnose_sppr(short=False, flat=False)` for GE, TE and With Egestion, or an exact not-run reason. `diagnostics_raw.json` retains the returned objects. Statuses: {'GE': 'FAIL', 'TE': 'FAIL', 'With Egestion': 'FAIL'}. All numerical runs disable diet normalization and detritus pooling (`det_collapse_mode=never`, `det_open_mode=none`). No global variants, method inventory or Monte Carlo were run.

`diagnostic_run_record.json` records all boundary settings, warnings and exceptions. `loader_input_groups.csv`, `loader_diet.csv`, `loader_detritus_fate.csv` and `loader_completed_groups.csv` make loader alterations reviewable. The legacy loader requires a numeric filename and a parenthesized year; `loader_input/` contains an escaped copy under a local diagnostic placeholder id, not a model renumbering or EcoBase claim. For native PAT, this diagnostic copy also contains explicitly derived missing B/EE values listed in the run record; canonical source JSON remains unchanged. The loader hardcodes LME=13 internally; the canonical extraction metadata correctly says LME=14. Diagnostic calculations do not establish region identity or authorize adoption.

Production eligibility: **not established / false**. Successful computation is distinct from scientific source fidelity. No candidate is selected.

## Source tables and numerical identity

Ocampo Reinaldo et al. (2016), *Assessing the effects of demersal fishing and conservation strategies of marine mammals over a Patagonian food web*, Ecological Modelling 331, 31–43, DOI 10.1016/j.ecolmodel.2015.10.025 (article PDF p1). The source contains one reference Ecopath model for **1970**, with Ecosim simulation through 2009. Simulated annual time series and prospective fishing scenarios are not separate fully tabulated Ecopath parameterizations.

Table2 on PDF p5/printed p35 contains 26 rows, including three separate hake sizes, Phytoplankton and Detritus; the prose's 23 groups is not used to collapse that explicit structure. Columns: group; TL; B t/km²; P/B year−1; Q/B year−1; EE; P/Q; omnivory index. Bounding boxes fix numeric columns before reading values. Bold B indicates model estimates for Juvenile sharks, Flounders, Benthic-demersal fish I, Small pelagic fishes, Squids, Jellyfishes, Zooplankton and Phytoplankton. Bold EEs are estimates for Dolphins, Sea Lions, Other rays, Large rays, Small rays, Large sharks, Medium-sized sharks, Narrownose smooth-hound, Benthic-demersal fish II, Plownose chimaera, Large hake, Medium-sized hake, Pink cusk-eel, Patagonian hoki, Medium-sized pelagic fishes, Benthic organisms and Detritus. Hake Z=P/B is explicitly stated on p35 and recorded only for the three hake groups.

The new Appendix A DOCX supplies two 29×14 diet blocks (including merged caption/header): predators1–12 and13–24, 26 named prey plus Import. All 648 numerical cells (26 prey+Import ×24 consumers) were extracted from exact DOCX table cells and reviewed against rendered pages1–2. Diet sums are 0.999–1.002; Benthic-demersal fish II sums1.002. The imported diet fractions up to0.655 are explicit source inputs. No rescaling was performed. Later vulnerability matrices in Appendix A are Ecosim vulnerabilities, never diet values. Pedigree and system-metric tables were retained but not mistaken for missing basic inputs.

## Biomass accumulation and deliberate blanks

The article describes a reference steady-state model on p32 and defines BA on p34, but reports no numeric BA in its tables, supplement or relevant figures. BA remains blank. GS/assimilation fractions, habitat proportions, detritus imports and detritus fate were not numerically specified in the reviewed bundle and remain unknown. The paper says synthetic incipient fishing effort equal to1‰ of later fleet maxima was introduced (p35), despite the nominal pre-fishery period. That statement is not a group catch table, and effort is not automatically a catch multiplier. No source catches were invented or back-calculated from EE. All three fleet landings/discards files therefore remain blank. The printed note that long-liner/jigger discards are negligible is qualitative, not exact zero.

## Source balance, loader completion and diagnostic interpretation

Juvenile hake B=0.098, P/B=0.880, EE=0.999 on p35 was visually confirmed. The supplied diet implies predation≈3.755 t/km²/year versus production0.08624, equivalent to EE≈43.539 before catch/BA/migration. Benthic-demersal fish I gives EE≈1.006. These source conflicts were not repaired. Source P/Q for Large hake is0.5064, also confirmed, rather than replaced by a generic fish value. Hake is a multistanza group; the eight-table/JSON workflow does not encode age-transition/maturation flows. Such omitted flows may be relevant, and the large juvenile imbalance should not be attributed uniquely to a typo without the original EwE file and multistanza settings.

Strict default loading rejects the diet tolerance at the published1.002 sum. The isolated diagnostic allows DC_tol=0.0021 solely to admit the unchanged three-decimal diet. Full diagnose_sppr continues to flag its0.002 deviation. There is no normalization. The source JSON retains missing nonconsumer diet import; the diagnostic boundary sets PP/DET import contributions to0 because they do not consume. Otherwise NaN propagates through the engine and produces a missing detritus-column exception; no consumer cell is altered. ModelData automatically assumes all living detritus flows reach the sole detritus pool, forces detritus self-routing, and the calculator supplies missing catches=0, BA=0, GS=0.2 and missing migration/import=0. It also overrides detritus EE to1 and infers detritus accumulation. These are loader conventions, not source findings; `diagnostic_run_record.json` and loader snapshots expose them. All three full direct diagnostics return FAIL. Their catch footprint has zero catch because catch is unavailable in the source; it does not establish zero historical catch or a usable regional PPR coefficient.

## Taxonomy and spatial applicability

Article Table1 (PDF p4/printed p34) explicitly lists species/class/order composition. Original spellings such as Milyobatis, Carcharinus, Xistreurys and Polichaeta are preserved with source scope. Juvenile sharks are juveniles of Large and Medium-sized sharks. Hake classes are <23 cm,24–53 cm and>53 cm/6 years, per p34; the apparent23–24 cm boundary gap is retained. The model describes the demersal-pelagic web of the San Matías Gulf trawl-operating area, about10,000 km² (p32), not the entire LME. No regional coverage fraction is inferred.

## Final round-trip cell audit

Compared 832 numeric/basic/diet cells between canonical JSON and the reconstructed workbook at1e-12 relative/absolute tolerance: no numeric mismatches. The stock reconstruction displays 0 canonical unknown diet cells as zero; this is a documented presentation loss, never written back into source outputs. It also collapses fleet catches, omits printed P/Q from Basic input, and loses metadata when the filename is model.json. These limitations are recorded in `roundtrip_cell_validation.json`; original eight tables and Metadata.xlsx remain authoritative.
