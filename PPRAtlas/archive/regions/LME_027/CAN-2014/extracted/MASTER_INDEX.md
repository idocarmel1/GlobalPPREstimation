# CAN-2014 extraction index

Source: Guénette, Meissa and Gascuel (2014), DOI 10.1371/journal.pone.0094742. Read README.md and metadata.json before extraction. All source files remain unchanged; all work and outputs are below this extracted directory.

**Three distinct Ecopath versions, all 1991.** The catalog's 2007-2009 label is incorrect. The 1991-2006 and 2056 outputs are Ecosim simulations and are not counted as separate static models.

| # | Model | Year | LME | Groups | Fleets | Status | Notes |
|---|---|---|---|---|---|---|---|
| 27_1 | [Banc d'Arguin and Mauritanian Shelf — Base](27_1_Banc_d_Arguin_and_Mauritanian_Shelf_1991/REPORT.md) | 1991 | 27 Canary Current | 51 | 3 | partial | 2 error(s), 52 warning(s); final database NOT BALANCED. Full base matrix; source Groupers diet 220.06% and birds 98.0331% preserved. |
| 27_2 | [Banc d'Arguin and Mauritanian Shelf — M30](27_2_Banc_d_Arguin_and_Mauritanian_Shelf_1991/REPORT.md) | 1991 | 27 Canary Current | 51 | 3 | partial | 14 error(s), 55 warning(s); final database NOT BALANCED. S8 B/EE preserved; 14 affected consumer diets incomplete; rounded juvenile zeros preserved. |
| 27_3 | [Banc d'Arguin and Mauritanian Shelf — P30](27_3_Banc_d_Arguin_and_Mauritanian_Shelf_1991/REPORT.md) | 1991 | 27 Canary Current | 51 | 3 | partial | 14 error(s), 55 warning(s); final database NOT BALANCED. S8 B/EE preserved; 14 affected consumer diets incomplete; rounded juvenile zeros preserved. |

Every directory contains the eight Ecopath import files, extraction model.json, database JSON, reconstructed XLSX, REPORT.md, provenance and source-conflict records, validation results and mass-balance report. No Taxonomy.xlsx is created.

These are source-faithful partial extractions, not clean/load-tested balanced models. Common unresolved fields are GS, habitat proportions, discards, detritus routing/import and multi-stanza P/B. The published base matrix itself has two invalid column totals. No value was normalized or invented to pass checks. The local adapter in work/audit_database.py restores exact source cells after auditing the bundled converter; its final workbook matches all eight input tables.
