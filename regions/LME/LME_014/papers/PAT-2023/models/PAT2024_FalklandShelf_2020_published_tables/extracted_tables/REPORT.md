# Source extraction report — PAT2024_FalklandShelf_2020_published_tables

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
WARN  36 group(s) have a blank Unassim. consumption — EwE will substitute 0.2 on import: Baleen whales, Benthic crustaceans, Blue whiting (Micromesistius australis), Dogfish, Flounder, Grenadier, Hake Austral (Merluccius australis), Hake common (Merluccius hubbsi) ...
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
WARN  Detritus_fate.csv row 27: no fate recorded
WARN  Detritus_fate.csv row 28: no fate recorded
WARN  Detritus_fate.csv row 29: no fate recorded
WARN  Detritus_fate.csv row 30: no fate recorded
WARN  Detritus_fate.csv row 31: no fate recorded
WARN  Detritus_fate.csv row 32: no fate recorded
WARN  Detritus_fate.csv row 33: no fate recorded
WARN  Detritus_fate.csv row 34: no fate recorded
WARN  Detritus_fate.csv row 35: no fate recorded
WARN  Detritus_fate.csv row 36: no fate recorded

0 error(s), 38 warning(s)
```

Source mass-balance tool: 9 error(s), 17 warning(s), 33 note(s). Full arithmetic and flags: `extracted_tables/source_massbalance.txt`. Its printed recomputed EEs are conditional comparisons: unknown BA/catch is numerically omitted, missing predator B/QB undercounts predation, and immigration is not represented in its eight-table contract. Critically, the standalone massbalance_check.py uses the habitat-biomass column without multiplying habitat area, making its Falkland predation comparisons inconsistent with model-area catches. Its PAT errors must not be read as native model failure. The separate native audit uses model-area B and includes immigration. Suggested BA values were not adopted. `MASS_BALANCE.md` is the stock converter's check, not a claim of strict source admission.

## Direct diagnostics and production status

The separate diagnostic report contains only the full direct returns of `PPRCalculator.diagnose_sppr(short=False, flat=False)` for GE, TE and With Egestion, or an exact not-run reason. `diagnostics_raw.json` retains the returned objects. Statuses: {'GE': 'NOT_RUN', 'TE': 'NOT_RUN', 'With Egestion': 'NOT_RUN'}. All numerical runs disable diet normalization and detritus pooling (`det_collapse_mode=never`, `det_open_mode=none`). No global variants, method inventory or Monte Carlo were run.

`diagnostic_run_record.json` records all boundary settings, warnings and exceptions. `loader_input_groups.csv`, `loader_diet.csv`, `loader_detritus_fate.csv` and `loader_completed_groups.csv` make loader alterations reviewable. The legacy loader requires a numeric filename and a parenthesized year; `loader_input/` contains an escaped copy under a local diagnostic placeholder id, not a model renumbering or EcoBase claim. For native PAT, this diagnostic copy also contains explicitly derived missing B/EE values listed in the run record; canonical source JSON remains unchanged. The loader hardcodes LME=13 internally; the canonical extraction metadata correctly says LME=14. Diagnostic calculations do not establish region identity or authorize adoption.

Production eligibility: **not established / false**. Successful computation is distinct from scientific source fidelity. No candidate is selected.

## Source tables and numerical identity

Same Büring et al. (2024) article and 2020 Falkland shelf period as the native candidate. This is the **published-table reconstruction**, retained separately because the tabulated parameters and native database conflict. Table 4 (PDF/printed pp14–15) provides 36 basic rows in exact source order. Header mapping: Trophic level→TL; Habitat area→hab_area; Biomass in habitat area→habitat B; Biomass→model-area B; Production/biomass→P/B; Consumption/biomass→Q/B; EE→EE; Production/consumption→P/Q. Parentheses indicate Ecopath-estimated B and user-input EE per caption. The source matrix and basic table have no rounding repairs.

Table 4 was extracted through displayed word bounding boxes, respecting the PDF p14 rotation and locally rotating the p15 continuation in memory. Published model-area B is separately retained: it sometimes differs from multiplying independently rounded habitat B and habitat area (e.g. Baleen whales 0.003 versus 0.01×0.2). Canonical B uses the directly printed model-area column; eight-table conversion uses multiplication. Both values and the transformation are recorded. Published zero B for Flounder, Hake Austral and Sharks remains zero, despite positive native values.

S2 CSV has 32 consumer columns, 35 prey rows including producers but one Detritus category, Import and Sum. It reports percentages, divided by 100 exactly; calculated sums range 0.99998–1.00002. CSV numbering differs from basic numbering because producer groups are absent among consumers. Names, not column positions, determine the explicit mapping. The S2 Detritus label maps to Table4 Detritus=36; Table4 Discards=35 has no separate S2 row and stays unknown. This is an unresolved mismatch, not evidence that discards were pooled or absent. Source raw CSV and per-cell mappings are retained. Table S4 (supplement DOCX table3, rendered p5) supplies separate Trawling/Jigging landings/discards; '-' stays unknown, while Baleen Whales discard zeros are sourced. Detritus in S4 is #35 and maps by name to Table4 #36.

## Biomass accumulation, deliberate blanks and conflicts

The full paper, S2, S3, S4 and remaining supplement were checked. The basic Ecopath equation names BA but supplies no numeric BA in the printed-table evidence; every BA import cell stays blank. No printed GS or detritus routing was found. Unlike the native database, the printed-source version does not borrow native zeros/GS/fates/immigration. The Table2 versus Table4 Kelp definition differs: Table4 label names Macrocystis pyrifera; Table2 composition also includes Lessonia spp., retained in taxonomy. Native and printed diet/EE differences are listed in the comparison evidence. Table S3 initial 45-group rates are preserved as an incomplete initial parameter compilation, not merged into this final reconstruction.

The direct loader rejects this two-detritus model because no living-group routing to Discards vs Detritus is given. All three requested diagnostics are explicitly NOT_RUN; no synthetic split or pooling was introduced. Native routing cannot simply be copied into this conflicting published version.

## Spatial applicability

Falkland shelf to 300 m, about 200,000 km²; not the entire Patagonian Shelf LME. Coverage percent is unknown. Source membership includes cohort and pooled-taxonomy overlaps requiring later model-specific matching; no catch mapping has been adopted.

## Final round-trip cell audit

Compared 1440 numeric/basic/diet cells between canonical JSON and the reconstructed workbook at1e-12 relative/absolute tolerance: no numeric mismatches. The stock reconstruction displays 891 canonical unknown diet cells as zero; this is a documented presentation loss, never written back into source outputs. It also collapses fleet catches, omits printed P/Q from Basic input, and loses metadata when the filename is model.json. These limitations are recorded in `roundtrip_cell_validation.json`; original eight tables and Metadata.xlsx remain authoritative.
