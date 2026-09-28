# LME_014 extraction review — 28 September 2026

Both supplied paper bundles have been fully reviewed, with all supported values extracted. Source gaps and conflicting versions remain explicit. No model has been selected and no annual PPR was published.

| Candidate | Groups | GE | TE | With Egestion |
|---|---:|---|---|---|
| PAT2024_FalklandShelf_2020_native | 36 | WARN | WARN | WARN |
| PAT2024_FalklandShelf_2020_published_tables | 36 | NOT_RUN | NOT_RUN | NOT_RUN |
| OcampoReinaldo2016_SanMatiasGulf_1970 | 26 | FAIL | FAIL | FAIL |

Each candidate folder contains `source_report.md`, `diagnostic_report.md`, `diagnostics_raw.json`, canonical `model.json`, taxonomy and eight EwE tables. The native and published-table PAT versions are separate because basic group structures/diets/EE disagree. S3 initial rates are retained as incomplete precursor evidence. Ocampo has one1970 Ecopath model;1970–2009 is an Ecosim simulation.

Metadata registration is proposed only in metadata_registration_proposals.json. Project.xlsx and LME_014.xlsx were not edited. The final source_hash_verification.json confirms all source bytes unchanged.

The diagnostic report files contain only the full direct engine returns for the three requested choices. Source assumptions, missing fields, converter corrections, native-vs-table conflicts, loader completion and the Ocampo rounding tolerance are explained in source_report.md.

The native coupled Ecopath calculation reconstructs unknown living B/EE from native inputs with residual1.13e-14 and all living EE within[0,1]. Its separate diagnostic completion returns WARN for GE,TE and With Egestion; source JSON retains native missingness. The earlier default-B=1 loader diagnostic is preserved separately and is not the faithful reconstruction. Native detritus/discard handling caveats remain. The PAT published-table version is blocked by absent two-pool fate routing. Ocampo runs only as a declared loader-completed diagnostic and fails major source/flow checks.
