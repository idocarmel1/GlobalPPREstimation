# Resumed source and balance investigation — 2026-10-03

This is a separate investigation of the existing provisional Figure 9 reconstruction. Source originals, the selected NE model, validation DOCX and map are unchanged. No new value is adopted solely because it improves balance.

- `arrow_audit/`: independent visual tracing of source labels and endpoints. F77 was accepted as medium pollock15→predatory fish20 in the separate revision; F13/F22 confidence improved. Dense red routes remain uncertain. A later targeted audit found no drawn copepod→smelt link.
- `article_constraints/`: independent source audit of conversion factors, parameter interpretation and observable article results.
- `balance_audit/`: parent calculations comparing carbon and wet-weight budgets, exact reproduction inputs and identifiability limits.
- Earlier user-requested F62/F67 crops remain in `../audit/user_review_20261003/`.
- The accepted figure revision is `../assumption_variants/researcher_readings_20261003/`: human F62=.023, alternative .025, F67=.05; bacteria wet/carbon9.4 from dissertationp60; all authorized GS/detritus assumptions. It has20/20 numerical carbon diets and18/20 wet diets under adopted routes, but remains scientifically blocked. Original B/PB and the baseline files are unchanged.
- `text_feeding_audit/` preserves all primary2019 prose connections and partial diets. The article calls Figure9 generalized, but does not explicitly say it omits links. Text supplies copepods→smelt(DCwet.407) and chaetognath cannibalism(ambiguous numeric percentage).
- `../assumption_variants/text_plus_figure_20261003/` is the separate partial combined source case. SmeltDC4=.407 andDC5=.461 leave.132 unresolved; no forced normalization is used. Ten partial source diets and aggregate constraints remain explicit.
- `../BALANCE_CHECK_INPUTS.json` records the user's requirement that **both** figure-only and text-plus-figure cases be included in later balance reviews. The initial combined checks cover9 source-Q wet energy budgets and5 quantified-prey carbon lower bounds; full-network hybrid balance is not yet testable.
- The earlier GS-only snapshot remains in `../assumption_variants/user_defaults_20261003/`. Living catches, accumulation and migration remain unknown. Detritus BA is an uncomputed residual.
- The English article and its translation work are under `../../../papers/OKH-GM2019/` and its `English_translation_work/` directory. The Russian original remains authoritative.

The source extraction is preserved in the parent directory. `../CURRENT_VARIANT.json` points to the accepted revision and combined case. `../assumption_variants/researcher_readings_20261003/REPORT.md` answers the factor, source-target and existing-balance questions. Verified artifact arithmetic is distinct from biological balance; the user's loadable-and-balanced validation gate remains unmet.
