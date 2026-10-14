# Corrales_2017_ICS_1990_1994_gray_fit

Source identity: Corrales et al. (2017), Modeling the role and impact of alien species and fisheries on the Israeli marine continental shelf ecosystem, Journal of Marine Systems 170:88–102, doi:10.1016/j.jmarsys.2017.02.004. [Article](../../sources/1-s2.0-S0924796316302329-main.pdf), [author supplement](../../sources/supplements/1-s2.0-S0924796316302329-mmc1.docx). The researcher-supplied Corrales-2010 folder alias is retained; publication year is 2017.

Modeled period and area: 1990–1994; Israeli Mediterranean continental shelf at 0–200 m depth, 3,725 km²; 39 source groups. Whole-model-area biomass basis is published. This is partial shelf coverage of EEZ_939, not a full-EEZ model.

Departures from publication: Researcher-authorized assumed natural detritus fate; source biology and fleet components retained. Ordinary blank diets become zero only at runtime; source gray diet cells are -9999, not measured zero. Unpublished BA, GS, habitat fraction and missing fisheries components remain unknown in source tables. The source prints seabird B=0.00 and rounded consumer diets; neither supplies unrounded native precision. See article Table 1 PDF 4, Table 2 PDF 6, Table 3 PDF 8 and supplement sections 1 and 5.

Actual direct outcomes: {"GE": "FAIL", "TE": "FAIL", "With Egestion": "FAIL"}. The executed runtime uses recorded zero-catch/BA and GS defaults, restores explicit producer fate, and normalizes diets on a copy. Detritus EE/accumulation are software-derived. Explicit native fleet returns to Discards are not represented. Strict mass balance is false.

The researcher explicitly authorized filling gray diet cells on 14 October 2026. Fitted raw values are nonnegative and strictly below 0.01. All printed diet fractions and non-diet biological parameters remain unchanged before runtime normalization. The constrained linear-program solution is not unique source recovery; exact balance is infeasible. [Fitted cells and feasibility](extracted_tables/evidence/gray_diet_fit/fit_summary.json).

Evidence links: [extraction account](extracted_tables/evidence/REPORT.md), [current parameter/diet comparison](extracted_tables/evidence/CURRENT_VARIANT_CHECK.json), [round-trip check](extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json), [diagnostics and settings](results/diagnostics).

Automatic detritus collapse and removing Discards remain deferred: the researcher requested those only after a mass-balanced model still fails, and strict balance has not been reached.
