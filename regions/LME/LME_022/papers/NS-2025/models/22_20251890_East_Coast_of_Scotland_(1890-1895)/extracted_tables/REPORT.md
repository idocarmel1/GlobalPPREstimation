## 22_20251890_East_Coast_of_Scotland_(1890-1895)

Published 1890–1895 East-coast Scotland model: 25 groups, 23 consumers, 1 phytoplankton and 1 detritus group. Parameters: paper Table 1/PDF 6; diets: supplementary Table S3; three-fleet landings: Table S1; taxonomy: Table S2. Methods DOCX was inspected. GS, BA, detritus routing/import and habitat shares are not numerically documented. Discards are explicitly excluded by the paper. Printed seal biomass 0.00 remains 0.00; it was not replaced with an inferred small positive biomass. Source validation: 0 errors, 27 warnings; source mass-balance check BALANCED with 0 errors, 0 indeterminate and 3 endotherm P/Q warnings, conditional on its treatment of unknowns. This does not certify exact source completeness. GE/WithEgestion WARN involve the zero-biomass/EE historical seal case. TE diverges and has negative Seabirds SPPR despite zero catch.

| Configuration | Status | Living spectral radius | Relative flow-balance gap |
|---|---|---:|---:|
| GE | WARN | 0.21226276 | 0 |
| TE | FAIL | 1.1116113 | 1.2720206e-15 |
| With Egestion | WARN | 0.16981021 | 4.2400685e-16 |

MC_new_GE: 100/100 accepted; 0 divergent rejections and 0 negative rejections (not necessarily additive). MC_new_TE_EEfix: 21/100 accepted; 79 divergent rejections and 0 negative rejections (not necessarily additive).

SPPR_2015: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258. new_TE_noEEfix: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258. new_TE_EEfix: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258. sym_TE_asPP: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258. sym_TE_asDC: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -3191216.258.

Unavailable methods: none.

97 printed core values matched database JSON; 232 source diet slots including zeros/import matched without normalization; All group names, source BA unknowns and taxonomy carried through; All database exports equal retained fleet landings plus discards; Eight import tables and database round-trip workbook retained. Round-trip basic/diet cells independently verified: 775.

Evidence: `model.json`, `source_provenance.json`, `EXTRACTION_AUDIT.json`, `SPPR_DIAGNOSTICS.json`, `sppr_source.xlsx`, `candidate_diagnostics.xlsx`, `loaded_groups.csv`, `LOADER_TRANSFORMATIONS.csv`, executed-code snapshot/hashes and run log in this candidate folder. Canonical model SHA256: ad7cae363be6214a700845fcf15f5584b20de4c20c05e3ebf251fa03c89f1692.

No production model selected. Exact diagnostic configurations and source/loader distinctions are described in the extraction-set report.
