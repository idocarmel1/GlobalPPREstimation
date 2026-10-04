## 457_457_North_Sea_(1991)

EcoBase accession 457: 68 groups, registry period1991–1992 and local archive filename1991. The live record explicitly cites the Mackinson/Daskalov technical report. The original JSON bytes are archived; every original numerical field was preserved, with source-based taxonomy attached by group_seq only. It is a separate repository numerical variant, not an interchangeable paper extraction: the parameter comparison records 205 unequal fields including precision, BA unknown→0, catches and substantial changes (e.g. gelatinous QB 6.35111141 instead of printed0.18). The database export aggregates catch and does not preserve the12-fleet ledger. Its JSON-only route is retained with a reconstructed workbook; original repository bytes remain the authority.

Strict source diet admission PASS; independent source mass-balance checker BALANCED with 0 errors/0 indeterminate and 4 endotherm warnings. Nevertheless, all standard engine configurations FAIL. A fresh independent engine load reproduces the worst identity residual at Discards group 68: stored production0.2981897135 versus recomputed−99.7018102865. The source supplies both detritus_import 100 and immigration 100, unchanged; the engine's handling of this detritus/migration representation requires investigation. Do not describe this alone as proof that the repository living food web is grossly unbalanced. Separate overall balance gaps remain substantial. No negative aggregate group SPPR occurs in completed methods, but convergence/nonnegativity does not make the diagnostic model valid. Both MC methods and both EwE path methods timed out; six symbolic methods failed. No source or engine repair was attempted.

| Configuration | Status | Living spectral radius | Relative flow-balance gap |
|---|---|---:|---:|
| GE | FAIL | 0.33263683 | 2.9109828 |
| TE | FAIL | 0.58371892 | 0.12447885 |
| With Egestion | FAIL | 0.26610946 | 2.8741747 |

Both 100-sample Monte Carlo methods timed out at 180 seconds; acceptance/rejection counts are unavailable.

No negative aggregate group SPPR in completed methods; unavailable methods were not treated as passing.

Unavailable methods: EwE_TE_noEE: timeout; EwE_TE_EE: timeout; sym_TE_asPP: failed; sym_TE_asDC: failed; sym_GE_asPP: failed; sym_GE_asDC: failed; sym_WithEgestion_asPP: failed; sym_WithEgestion_asDC: failed; MC_new_GE: timeout; MC_new_TE_EEfix: timeout.

All original repository numerical fields unchanged; only taxon_descr attached by exact group_seq. Round-trip basic/diet cells independently verified: JSON-only repository route; reconstruction retained.

Evidence: `model.json`, `source_provenance.json`, `EXTRACTION_AUDIT.json`, `SPPR_DIAGNOSTICS.json`, `sppr_source.xlsx`, `candidate_diagnostics.xlsx`, `loaded_groups.csv`, `LOADER_TRANSFORMATIONS.csv`, executed-code snapshot/hashes and run log in this candidate folder. Canonical model SHA256: f6a8a64ecd52fca40117afe76503db2ea29db002a87bc789959dd75c31dbcfbc.

User-requested deferred review (2026-09-28): investigate why this model fails flow balancing despite passing the independent source check. The verified Discards/import/migration discrepancy above is evidence, not an established cause. No debugging experiment or repair was performed in this preference update.

No production model selected. Exact diagnostic configurations and source/loader distinctions are described in the extraction-set report.
