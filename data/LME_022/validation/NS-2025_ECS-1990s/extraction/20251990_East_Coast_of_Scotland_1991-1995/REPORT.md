# East Coast of Scotland (1991-1995)

**Source:** Saygu et al. (2025), *Historical ecosystem models can serve as a baseline for indicator-based assessment: the North Sea*. Frontiers in Marine Science, doi:10.3389/fmars.2025.1646031. Main PDF pp. 1-18, archived author XLSX Tables S1-S4, and DOCX Supplementary Material S1.

**LME:** 22 North Sea. **Local model number:** 20251990. This is a deterministic extraction-local identifier for the publication's 1990s parameterisation, not a claimed EcoBase accession. **Groups:** 25 (24 living, including phytoplankton; 1 detritus). **Fleets:** Herring fisheries, Whitefish fisheries, Creels. **Extracted:** 2026-09-07.

## Source tables

### Table 1, PDF and printed p. 6: basic inputs and outputs

The landscape page was rendered at 220 dpi and inspected. Poppler bounding boxes were used through `pdfgrid.get_words(merge_gap=0.4)` in Python UTF-8 mode. The header has 13 numeric anchors: Both TL, and paired 1890s/1990s B, P/B, Q/B, EE, P/Q, E. The extraction uses Both TL and the right-hand 1990s subcolumn of B, P/B, Q/B, EE and P/Q. The exploitation-rate E column is not migration, EE, or another import field and is not imported.

There are 25 complete rows. Names use the basic-input table; typographic ligatures are expanded (`Flatfishes`, `Monkfish`, `Large Dem. fish`). Supplementary variants such as `Flatfish` and `Large Demersal fish` are aligned by the source group number after checking the labels. No numeric row is joined by unverified position. Biomass is tonnes wet weight per km²; turnover rates are annual (methods p. 4). No unit conversion was needed.

The caption marks bold values as inputs; plain values are Ecopath outputs. All published values were retained, so the presence of B/PB/QB/EE together does not assert four independent measurements. In particular, the 1990s EE values for most living groups are model outputs. Their input flags in the database converter indicate an extracted numeric cell, not the publication's input/output typography. See the archived page for per-cell typography.

### Author XLSX Table S1: landings

Rows 4-28 identify groups 1-25. Columns G:I contain the 1990s Herring fisheries, Whitefish fisheries and Creels values, in t/km²/year. All 75 source slots, including blanks, were cross-checked. The Total Catch column J is independently rounded; the import's Total is the sum of the three unaltered fleet cells. Total model landings are 3.4617151025401 t/km²/year, consistent with the paper's rounded 3.46.

### Author XLSX Table S3: diet composition

Source C3:Y27 has 25 prey rows by 23 consumer columns (groups 2-24). Headers and all row IDs were verified. There are 232 numeric source cells; 575 matrix slots were compared to the extraction. Source blanks stay absent/blank. Consumer sums range from 0.9996 to 1.0005. No trace marks, inequalities or missing continued block occurs.

The import CSV and `model.json` preserve these values without normalization. The existing database converter normalizes ten columns by their sums, a relative change at most 0.05%. This is a pre-existing conversion behavior, not source data. `VALIDATION_RESULT.json` lists all ten factors and verifies every converted value. No shared converter or algorithm code was changed.

### Author XLSX Table S2: taxonomy

Rows 3-27 supply group number, group name and Main Species. The entire definition is carried in the 25-row `Taxonomy.xlsx`. Parenthetical taxon names were transcribed to a 124-row member list before mapping. Printed misspellings and nomenclature were preserved; the `accepted_name` column repeats the printed name and does not claim current nomenclatural verification. Basal-group hyphens are recorded as no species list documented. The SPPR exporter adds an external `diet_import` group; it has no author species membership.

All four XLSX sheets are visible. S4 contains pedigree information. The DOCX supplement contains indicator formulas, not additional Ecopath parameter, fate or membership tables.

## Biomass accumulation

Numeric BA and migration were searched in the full main paper, all XLSX sheets and the DOCX supplement. Methods p. 5 state steady-state conditions when deriving P/B for fished groups. No numeric BA input is supplied. The across-century change discussed on pp. 9 and 15 is a contrast between parameterisations, not an annual BA term in the 1991-1995 model. All BA cells therefore remain blank and database BA remains `-9999`.

The independent mass-balance check flags Turbot and Ling as indeterminate. Their low, two-decimal biomasses make rounding material. Holding the other extracted terms fixed, B=0.0241633 for Turbot and B=0.0639997 for Ling would reconcile the printed EE without BA; both values lie within the rounding interval of their printed B (0.02 and 0.06). This diagnostic explains a plausible rounding mechanism. Neither value is adopted, and it does not prove that BA was zero.

## Values from prose

- Methods p. 4 provide wet-weight and annual units; no conversion is needed.
- Methods p. 5 state P/B=total mortality for fished groups. Z is left blank because no separate Z column was extracted.
- Discussion p. 14 explicitly says discard data were omitted from both models, using landings alone. `Discards.csv` stays blank. This records exclusion, not evidence that real discards were zero.

## Conventions applied

No numerical biological defaults were entered into source import cells. In particular, no GS convention was applied to zooplankton. Source names use normalized Unicode ligatures solely for interoperable keys.

The existing converter supplies habitat area 1 where no fraction is reported, normalizes ten diet columns, represents absent diet links/fates as zero and leaves GS/BA unknown. The existing SPPR loader supplies GS 0.2 to regular groups except Small zooplankton (0.4), fills the single detritus destination and solves unknown BA while balancing the rounded data. The resulting `groups_df` is a transformed computational model. `LOADER_TRANSFORMATIONS.csv` preserves the loaded BA, GS, detritus flows and EE beside their source status. These numbers must not be attributed to the paper.

## Deliberate blanks

- GS: no numeric fraction is reported in the whole source bundle. Import cells and database `gs=-9999` remain unknown; the downstream software convention is 0.2.
- BA and migration: no numerical values reported; source unknown is preserved.
- Detritus fate/import and habitat-area fractions: no author routing table or numerical prose statement found. Fate/import cells remain blank; habitat area is not asserted in the extraction.
- QB for primary producer/detritus, PB for detritus, and inapplicable P/Q fields remain blank.
- Discards remain blank because the authors excluded them.
- No source import diet row is supplied; the software treats it as zero and adds its own external-import compartment.

## Unresolved and flagged

This model describes the East Coast of Scotland fishing grounds, not the entire North Sea. Applying it to whole-LME catch over 1950-2019 is an integration test with a spatial and temporal mismatch. It is excluded from production model selection and the colored atlas pilot.

The published rounded P/Q values for Seabirds (0.01), Seals (0.00) and Cetaceans (0.00) are retained. PB/QB yields positive but small efficiencies for these endotherms; no table column was shifted. The converter leaves database GE to be derived from PB/QB.

The TE computational configuration diverges (living-network spectral radius 1.11278); GE and With Egestion configurations pass their health checks. Merely obtaining a finite PPR for fished groups does not validate the divergent TE solve.

## Validation

- `validate.py`: 0 errors, 27 warnings (unknown GS, wholly unknown BA, 25 unknown fate rows).
- Source audit: 650 spreadsheet slots checked, 25 group identities, 25 taxonomy descriptions carried into database JSON and SPPR, all eight import files present.
- Database round-trip workbook was created and its names/values were inspected programmatically.
- Standalone `massbalance_check.py`: 1 error (Ling recomputed EE 1.003), 5 warnings, 24 notes. It evaluates the rounded import data with unreported BA effectively absent. The newer converter explicitly classifies unknown-BA ambiguity as 2 indeterminate groups rather than an error. Both outputs are retained; neither suggested BA nor rounding-adjusted B was inserted.
- SPPR: 20/20 methods returned; 1/1 workbook created. The method health distinction is retained.
- Actual North Sea mapping: 384 taxa, 14 composites, 62 unresolved; 99.597% catch tonnage on groups; 96 taxa/81.2% catch confirmed by source membership and zero contradictions. Low-confidence assignments account for 15.9% of catch, predominantly unidentified demersal fish.
- PPR: one workbook with 70 catch years built and independently verified. The validation report distinguishes arithmetic completion from source-model and geographic validity.

## Mass balance

See `MASS_BALANCE.md`, generated from the assembled database JSON: 0 errors, 2 indeterminate groups (Turbot and Ling), 3 endotherm P/Q warnings. The source remains unmodified after these findings.
