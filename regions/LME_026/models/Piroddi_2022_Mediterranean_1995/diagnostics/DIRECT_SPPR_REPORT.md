# Direct SPPR diagnostics — Mediterranean 1995

Only `PPRCalculator.diagnose_sppr(TE_option=..., short=False, flat=False)` was scheduled for GE, TE and With Egestion. No global option, broad inventory, or Monte Carlo was run.

| TE option | Direct method outcome | Raw return |
|---|---|---|
| GE | NOT_RUN — model constructor blocked | None |
| TE | NOT_RUN — model constructor blocked | None |
| With Egestion | NOT_RUN — model constructor blocked | None |

The exact constructor exception, reproduced under both strict and documented standard-default settings, is:

> det_fate carries no detritus routing for any living group. For a multi-DET model the per-pool split cannot be inferred -- supply DetritusFate data for model with detritus groups [70, 71].

Diet validation passes without normalization. The constructor stops before parameter completion and `diagnose_sppr`; therefore no health, convergence, coefficients, negative-contribution test, or method balance result exists. NOT_RUN must not be read as FAIL or PASS. See `loader_audit.json` for the full exceptions and `diagnostics_results.json` for the three explicit not-run records. Source interpretation and arithmetic are deliberately kept in the extraction report.
