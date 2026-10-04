# California Current, Koehn et al. (2016), 2000–2014

Extracted 2026-09-28. One author baseline model (Monte Carlo accepted draws were not supplied as separate named models): **93 groups, comprising 92 living groups and one detritus pool**. Model ID: `CAL-2016_California_Current_2000-2014`. Canonical source JSON preserves 26 unknown biomasses and 67 unknown EEs as -9999. All eight EwE import files and all 93 taxonomy rows are retained. This candidate is **not selected or approved for regional production**.

## Source tables and provenance

Koehn, L.E., Essington, T.E., Marshall, K.N., Kaplan, I.C., Sydeman, W.J., Szoboszlai, A.I., and Thayer, J.A. (2016). Developing a high taxonomic resolution food web model to assess the functional role of forage fish in the California Current ecosystem. Ecological Modelling 335:87–100. DOI: 10.1016/j.ecolmodel.2016.05.010.

The supplied PDF and ZIP remain unchanged. ZIP extraction checked resolved paths against the destination and verified bytes on repeated extraction. All six archive members were hashed. Publisher Appendix A (`mmc1.xlsx`) and Appendix B (`mmc2.docx`) were recovered from ars.els-cdn.com and archived exactly; actual retrieval results and SHA-256 hashes are in the review folder. Appendix A has one visible sheet, no hidden sheets. It contains 94 prey/import rows and 93 predator columns; the final two rows are diet pedigree and Dirichlet multipliers, not prey. Its 8,742 numeric diet cells match the author CSV exactly.

Author groupinfo gives B, EE, PB, QB, group type, BA and diet import. Author parameters repeats B/EE/PB/QB and provides total Yield and parameter CVs. All 372 repeated parameter cells agree numerically. Source `-1` means an input to be solved, never observed negative biomass. GCE=0 is an unused placeholder: author R computes PB/QB at output, so it is not imported as a true GE of zero. Source data are biomass density in t/km², rates per year, and catch in t/km²/year (Appendix B individual parameter explanations).

Table 1 (PDF pages 3–4, printed 89–90) has columns B, B CV, PB, PB CV, QB, QB CV, EE, C, C CV. Caption states dashes are model-solved parameters. Both pages were rendered; numerical cells were separately extracted by coordinates with page-specific boundaries. All 837 printed parameter/CV cells were compared at printed precision; **0 differences** are listed in `paper_vs_author_parameters.json`. The machine-readable author values are retained without averaging or adjustment. The manuscript is not numbered: sequence follows groupinfo and both diet sources; a crosswalk handles its different bird/mammal display order.

`parameters.csv` reverses Shelf/Slope rockfish names at rows 39 and 55 relative to groupinfo and manuscript Table 1. Groupinfo + Table 1 identities agree on B/PB/QB values and are retained; labels, matrix aliases and source cell positions are preserved in evidence files. This discrepancy is not concealed by matching names alone. Appendix B provides the separate Shelf Rockfish and Slope Rockfish sections used for membership.

## Biomass accumulation and migration

All 93 groupinfo BA cells explicitly equal zero, also enforced by author Monte Carlo code. These are source zeros. The paper PDF page 2 / printed 88 explicitly assumes steady state and excludes migration; canonical immigration/emigration are consequently zero. Imported feeding is retained separately, exactly matching groupinfo Import, the last CSV diet row and Appendix A Input Consumption. No time-series slopes were inferred.

## Values from prose and taxonomy

The model averages 2000–2014 (PDF page 2 / printed 88). Model area is 302,000 km²: northern Vancouver Island to Punta Eugenia, offshore to the 2,000-m isobath (PDF page 4 / printed 90, Fig. 1). These do not establish a measured percentage of LME_003 coverage. Prior inherited target-polygon geometry is contextual only.

Appendix B was read by paragraph, with full group sections retained in `taxonomy_source_evidence.json`; `Taxonomy.xlsx`, taxonomy.csv and canonical taxon_descr carry the section heading and first descriptive paragraph for every living group. Original scientific spellings, author examples and broad guild definitions are retained. The evidence artifact retains additional membership and diet paragraphs; diet examples do not establish exhaustive membership or catch allocation. No species matching/weights were inferred.

## Conventions applied

No source diet normalization, undocumented pooling, balancing correction or default B=1 was applied. Author R explicitly routes unused living production to the sole detritus pool; the 92 living fate rows record that single destination. The detritus self-row remains blank in the imports; the downstream loader inserts its self-identity. Habitat-area 1 in the converter is a representation convention because author biomass already refers to the whole model area.

The author code's detritus inflow omits egestion. GS is not parameterized anywhere in the retrieved bundle; canonical GS stays unknown. For numerical diagnostics only, the documented loader supplies GS=0.2 for 91 consumers and applies the same single-pool routing to egestion. This is an explicit extension of the author's accounting, not an author estimate. The loader sets detritus EE to 1, uses completed detritus inflow 3090.057754953629 t/km²/year as both q and p, and appends an external diet-import group; it does not normalize the diet. Complete source-to-staging changes and loaded group values are retained.

## Deliberate blanks

Biomass (26 groups), EE (67), GS (93), TL (93), total mortality as a separate input, source GE, and separate landings/discards remain absent where unreported. Author Yield is total catch including bycatch and discards (PDF page 2, Eq. 1); it is carried in Landings.csv under the explicitly labeled `Total catch including discards` column, per import convention. Discards.csv stays blank and no discard return to detritus is invented. Missing detritus import remains unknown in canonical; loader zero is a diagnostic default.

## Validation

The bundled validator reports 6 quote-character errors because it rejects literal apostrophes in authentic group labels (Cassin's auklet, Leach's S. Petrel, Brandt's corm.) in each of the six CSVs. These are label characters, not CSV quoting: exact names are intentionally preserved. A separate source-cell verification passes all scalar and diet checks. Its three warnings are blank GS, the unreported detritus self-fate row, and unknown TL. These are source/convention limitations, not silently filled source observations.

Canonical/source comparison verifies 465 scalar parameter cells, 8,463 internal consumer diet cells, 91 diet imports, 93 catches, and all taxonomy rows. The reconstructed workbook independently matches all 93 basic-input rows and their five numerical/missing fields. The converter round trip loses original metadata structure, blank-vs-zero diet cells, separate fleet/discard structure and unresolved detritus self-routing; those remain authoritative in the eight original imports. Canonical is copied from conversion with only explicit no-migration values and source metadata added. Roundtrip is not claimed as a byte-identical eight-file rebuild.

## Mass balance

The source-only bundled checker reports 0 errors, 32 warnings and 2 notes, but has incomplete B/EE and therefore cannot certify the source's solved balance. Warnings include very small P/Q of birds/mammals, which agree with the reported high Q/B; they were not adjusted. Its automated verdict is not substituted for admission review.

A separate audited transcription of the author R linear equations solves the 26 unknown B and 66 unknown living EE simultaneously. A second reduced system gives identical B. Maximum production-equation residual is 2.84e-14 t/km²/year; all living EE lie in [0, 0.99158987]. Author detritus input is 2534.091451176, consumption 650.915499698, EE 0.256863461; these explicitly exclude egestion. Derived values live in a separate solution and diagnostic staging, never overwrite canonical unknowns, and retain source input flags.

## Direct SPPR diagnostics

Only `PPRCalculator.diagnose_sppr(TE_option=..., short=False, flat=False)` was invoked for GE, TE and With Egestion. Each returned a full nested report; each complete unmodified return is retained in diagnostics. No global exporter, 22-method run, Monte Carlo run or regional PPR was performed. The adapter filename uses 2016 only as a required numeric loader token, not an EcoBase accession; its year string remains 2000–2014. Loader's hard-coded lme=13 was corrected to 3 in memory, without changing equations or canonical source.

- **GE: WARN**; input WARN; model balanced=True; recycling b=0.18583401; living spectral radius=0.454504269; PP-balance OK, relative gap=2.26e-16; negative sources=0.
- **TE: WARN**; input WARN; model balanced=True; recycling b=0; living spectral radius=0.562095966; PP-balance OK, relative gap=4.52e-16; negative sources=0.
- **With Egestion: WARN**; input WARN; model balanced=True; recycling b=0.200920643; living spectral radius=0.363603415; PP-balance OK, relative gap=2.26e-16; negative sources=0.

The exact method WARN results are distinct from source qualifications. Twenty-one zero-EE groups and near-singular TE groups include unfished predators; full group IDs and warnings are retained. Good completed balance includes documented loader defaults and does not validate missing source GS or authorize adoption.


## Subsequent user selection

After this extraction review, the user explicitly selected this model. Current selection and supported regional calculations are documented in `../selected_pipeline/SELECTED_REGIONAL_REPORT.md` and LME_003.xlsx / Overview. The original source JSON and extraction-stage flags remain an unchanged historical source snapshot. Current totals are partial mapped-catch estimates, with 76.51% catch coverage in 2019; source and diagnostic qualifications remain.
