# Coastal Kyoto (2013) source extraction

**Status:** tabulated reconstruction; source admission unresolved; exact model selection pending. Local model ID `50_502013_Coastal_Kyoto_Inoue_(2013)` is not an EcoBase accession.

Source: Inoue, Watari, Sawada, Lavergne and Yamashita (2023), Fisheries Science 89:573–593, DOI 10.1007/s12562-023-01691-9. Paper chosen by the user because it is the only available paper. Both publication-defined model periods, 1985 and 2013, are retained separately.

## Source tables and numerical meaning

Table 1, PDF pp.5–6 / printed pp.577–578, gives 40 groups in exact order: 38 consumers, phytoplankton (#39), detritus (#40). Columns map TL→tl, B→biomass (t/km²), P/B→pb (/year), Q/B→qb (/year), P/Q→ge, EE→ee. Bold cells are author inputs; regular-font cells are Ecopath estimates. Font status and bounding boxes are retained for all 240 parameter cells per model. The main article's final Table1 is preferred over supplementary input-source tables, with conflicts retained.

Table 2, PDF pp.7–8 / printed pp.579–580, has prey rows 1–40 and predator columns 1–38, plus Import and printed Sum rows. Pages were rotated +90° for reading. Tokens were reconstructed from raw PDF characters; numerical LEFT edges match numbered column headers within 0.3 pt, and prey row anchors were checked visually. This avoids fused adjacent cells. Printed zeros remain separate from blank cells. Nine columns have exact nonunit totals; #11 and #12 total 1.01, although the printed Sum row is 1. Canonical source diets were not normalized.

**Year ambiguity:** this single table is captioned for both years, yet p.585 says diets differed, with sardine dominant in 1985 and anchovy dominant in 2013. The table is preserved in both caption-linked reconstructions. No year-specific swap or invented alternative diet was made. These files cannot be represented as a verified recovery of either original model.

Supplement Table S4 (DOCX table 5) gives 6 fleet columns: set net, trawl net, gill net, dredge net, angling, other. Source fleet cells are preserved without renaming. The narrative calls these six methods, but the 1985 table has seven columns including `others`. Total catch is placed in Landings as the import-format convention; no landings/discards split was stated. Printed row totals and recomputed fleet sums differ because of source precision and are retained in catch_total_comparison.json. Rounded printed 0.000 totals are not substituted for positive detailed fleet cells. Missing nonfishery catch stays blank.

## Deliberate blanks and prose sweep

The complete 21-page main article, all nine online resources in the DOCX, 12 XML tables, and embedded S6-1 / S9 images were checked. No numeric GS/unassimilated consumption, per-group BA, immigration/emigration, detritus import or detritus-routing fraction was found. Those fields remain blank in imports and -9999 in canonical JSON. A static mass-balanced description is not an explicit BA=0 statement. No zooplankton GS convention was added. Habitat-area proportion is unreported: Table1 B is model-area biomass; canonical biomass is the printed B while habitat fraction stays missing. The Basic_input importer places B in its only biomass column, with this semantic limitation recorded.

Methods pp.576/578/581 and Discussion p.590 explain diet imports for migrating fish; diet imports are prey consumption outside the modeled system, not numeric immigration or emigration fluxes. The discussion mentions discarded fish and recreational catch as statistical error sources without a numeric discard amount, survival or return destination. Discards and routing therefore remain unknown. No offal group or fleet-return pathway was invented.

Supplementary S6-1 is an embedded image, not a native model. Its panel labeled 1985 contains catches resembling 2013 and many biomasses conflicting with final Table1 (e.g. sardine 2.085 versus 114.92 for 1985). The 2013 panel also has rounding/detailed-value differences. Both images and all 40 biomass comparisons per panel are retained; they do not define another complete balanced model. The publisher site lists one DOCX supplement containing nine resources, verified byte-identical on 2026-09-28; no native EwE file was found.

## Taxonomy and structure

Supplement S3 provides representative taxa, not an exhaustive membership list. Its #6 Amberjack is associated with main #6 Yellowtail through Seriola quinqueradiata and the main prose. S3 reverses #29 Sole and #30 Dragonet relative to Table1 (#29 Dragonet, #30 Tongue sole); taxonomy was reconciled by names, with both source numbers retained. S3 Tuna says Thunnus thynnus but main p.585 says Thunnus orientalis; the conflict is retained without treating the names as synonyms. Source spellings, including apparent typographical errors, remain unchanged. Three basal groups have no species list; Polychaeta points to 29 species in an earlier reference without listing them. Taxonomy.xlsx has exactly one row per source group.

The model is a mixture of named taxa and species pools, with no spatial strata. Coastal Kyoto area is 2,230 km² to 240 m depth, a local portion of the Sea of Japan. No whole-LME coverage percentage was derived and no annual regional PPR was calculated.

## Validation and loader audit

All eight import tables exist. Format validation returned 0 errors and 42 warnings (unreported GS, BA, routing); this is a format result, not scientific admission. The separate massbalance_check returned 0 errors and 6 warnings under its conditional treatment of unknown BA/migration as zero and defaults. EE discrepancies >0.05 occur for #12 Flounder, #13 Black porgy, #23 Ivory shell, #26 Crab, #27 Prawn, #37 Mysid. Flagged values were checked against rendered Table1 and Table2; no values were repaired. Inference from these checks must retain the unknown BA/migration caveat.

The converter's normalized database output is retained only as a conversion artifact in extracted_tables. All its diet normalization and undocumented defaults were reversed in source model.json, with a field-level reversal audit. Supported source numeric fields and explicit diet cells roundtrip successfully. The converter reconstruction is lossy for blank diets/routing and fleet detail; those losses are documented in evidence/ROUNDTRIP_VERIFICATION.json and never overwrite the eight import files.

The current regional loader successfully built the source JSON for diagnostics, normalizing diet totals, defaulting missing consumer GS to 0.2 and catch/migration terms, closing the single-detritus routing, recalculating TL and GE, and solving unreported BA/flows. It changed 508 recorded parameter/flow cells and 108 diet cells relative to the retained ModelData state. Exact loaded matrices, parameters, all solved BA values and field-by-field changes are under evidence/. Its numerically balanced state is not source validation. Direct SPPR return values are reported separately in SPPR_DIAGNOSTICS.md.

## Provenance and decision

Main PDF SHA-256 eaca3b45c0e93645aa071099876a4490ac5cac4418a3eb4472ef8a85188a46c3.
Supplement SHA-256 8d668bb077ed7149b8bd83a862d46911fabb16c3b34bb3553b399ecc7071602e.
Source URLs, byte counts, retrieval results, extraction code and exact diagnostic-code hashes are retained. No source bytes were changed. Project.xlsx and the regional workbook were not edited. Central registration is proposed, with model adoption pending. Author/native year-specific files would resolve the principal source-admission blocker; a repaired or pooled experiment would require a separate explicit decision.
