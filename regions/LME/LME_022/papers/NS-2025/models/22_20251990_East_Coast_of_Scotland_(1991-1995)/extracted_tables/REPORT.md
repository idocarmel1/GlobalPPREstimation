## 22_20251990_East_Coast_of_Scotland_(1991-1995)

Published 1991–1995 East-coast Scotland model: 25 groups, same topology and source locations as the1890–1895 version. Period-specific parameters and landings are retained separately. Source validation: 0 errors, 27 warnings; source mass balance INDETERMINATE, 0 errors, 2 indeterminate groups (Turbot and Ling),3 endotherm P/Q warnings. Unknown BA could reconcile the discrepancy, but no checker-suggested BA was inserted. GE/WithEgestion are OK for the completed engine model; TE still diverges with negative unfished Seabirds. These results do not remove the source BA uncertainty.

| Configuration | Status | Living spectral radius | Relative flow-balance gap |
|---|---|---:|---:|
| GE | OK | 0.21208967 | 0 |
| TE | FAIL | 1.1127784 | 2.1200343e-16 |
| With Egestion | OK | 0.16967174 | 0 |

MC_new_GE: 100/100 accepted; 0 divergent rejections and 0 negative rejections (not necessarily additive). MC_new_TE_EEfix: 13/100 accepted; 87 divergent rejections and 0 negative rejections (not necessarily additive).

SPPR_2015: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512. new_TE_noEEfix: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512. new_TE_EEfix: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512. sym_TE_asPP: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512. sym_TE_asDC: 1 negative aggregate groups, including 1 unfished groups; minimum SPPR -2376869.512.

Unavailable methods: none.

97 printed core values matched database JSON; 232 source diet slots including zeros/import matched without normalization; All group names, source BA unknowns and taxonomy carried through; All database exports equal retained fleet landings plus discards; Eight import tables and database round-trip workbook retained. Round-trip basic/diet cells independently verified: 775.

Evidence: `model.json`, `source_provenance.json`, `EXTRACTION_AUDIT.json`, `SPPR_DIAGNOSTICS.json`, `sppr_source.xlsx`, `candidate_diagnostics.xlsx`, `loaded_groups.csv`, `LOADER_TRANSFORMATIONS.csv`, executed-code snapshot/hashes and run log in this candidate folder. Canonical model SHA256: 5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691.

User preference (explicit instruction, 2026-09-28): this exact model is preferred because it has the "least SPPR failures". GE and WithEgestion are OK, but TE remains FAIL. This does not change production Overview or adopt computed results.

No production model selected. Exact diagnostic configurations and source/loader distinctions are described in the extraction-set report.
