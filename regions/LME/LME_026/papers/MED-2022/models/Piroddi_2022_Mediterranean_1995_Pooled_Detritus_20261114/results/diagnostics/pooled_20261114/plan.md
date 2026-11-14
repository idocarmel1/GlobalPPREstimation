# Mediterranean pooled detritus implementation plan

**Goal:** Create and diagnose a separate 1995 Mediterranean model with the original Discards and Detritus compartments pooled, using EE floor ON at 0.1.

**Authority:** The researcher requested planning followed by execution, then explicitly chose 100% pooled routing while retaining the EE-floor external sink, and required EE = 1 - M0/P with M0 the production-derived flow into the pooled detritus. This authorizes this experiment and its direct diagnostics; it does not register a researcher verdict, change selection, or authorize publication.

**Architecture:** One new canonical `model.json` in this model folder, with source departures in `model_notes.md`. The original model is immutable. Model-local scripts build the aggregation and construct the runtime using the current frozen engine. Full direct diagnostic returns and their matrices remain beside this plan. No shared code changes.

## Design and alternatives

The selected approach merges source groups 70 (Discards) and 71 (Detritus) into new group 70, with IDs 1–69 unchanged. Biomass is summed (0.51582324 t/km²), consumer diet shares are summed without normalization, and known fleet amounts are retained. Missing values are never converted to zero during aggregation. The original detrital EE values are not averaged. A single unselected experimental model is preferable to changing the source model because pooling removes separate routing and mixing dynamics. Keeping unknown routing would preserve source uncertainty but would not answer the requested experiment; the researcher explicitly chose the stated 100% routing scenario instead.

## Steps and acceptance checks

1. Build the new input and record a source-to-pool crosswalk and complete change ledger. Verify unchanged living biology, summed biomass, prey shares, fleet removals, import shares, source text and missing masks. Preserve source hashes and original metadata provenance.
2. Encode 100% biological routing into the sole pool. In the model-local constructor bridge, route recorded fleet discard quantities into the same pool exactly once, preserving total fishery removals. Keep the external EE-floor sink distinct.
3. Use documented initialization: unlisted landings assumed zero only at runtime while recorded discards remain; `zero_catch=False`, `zero_biomass_accum=True`, `default_gs=True`, `underdetermined=False`, `normalize_DC=False`. Retain all defaults and completed values in a transformation ledger. Do not solve a residual into living EE, alter catch, or repair the fin-whale discrepancy.
4. Set `use_ee_floor=True`, `ee_floor=0.1`, `ee_threshold=0.1`. Retain source, pre-floor and effective EE/M0, floor sinks and skips. Check EE = 1 - M0/P for every living group with positive production. Egestion and fishery returns remain separate inflows. Detrital EE is a runtime convention, not an average of source detrital EE.
5. Run `diagnose_sppr(TE_option=option, short=False, flat=False, return_sppr=True)` independently for GE, TE and With Egestion on the initialized, unforced calculator. Preserve failures, exceptions, all groups, exact coefficients, returned matrices, axes, nonfinite masks, negative source/group entries, recycling metrics and strict balance flags.
6. Independently verify reloaded input and initialized state, source and engine hashes, retained coefficient/matrix reconciliation and evidence completeness. Produce a concise human-readable diagnostic summary. Do not copy source-model review approval or publish regional arithmetic.

## Bounds and review focus

Only this new model folder is writable for this experiment. Original model, original validation DOCX/appendix, regional workbook, Project.xlsx, map, trends, templates and shared engines remain outside the write scope. Direct deterministic diagnostics only: no global methods, symbolic variants or Monte Carlo inventory. Anticipated runtime is minutes, subject to actual solver behavior; failures remain results, not repair authorization.

Key risks checked independently are double-counted fleet returns, improper averaging of detritus EE, missing values becoming zeros, loss of living source identity, and confusion between original diagnostics and the calculator's internally forced-balanced copy. Numerical success does not establish source fidelity, ecological validity or researcher approval.
