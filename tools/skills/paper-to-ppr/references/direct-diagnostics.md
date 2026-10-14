# Direct SPPR diagnostics and exact runtime state

Apply the [evidence, execution and adoption contract](evidence-handoff.md) to this stage: explain fresh runs and honor existing scoped authorization, retain the applicable portable evidence, and verify completeness before handoff.

A standalone direct-diagnostics request defaults to GE, TE and With Egestion. A narrower explicit request controls that diagnostic scope, and report formatting need not rerun science. This does not define the inventory for validated-model map publication: the [full coverage route](project-integration.md#full-method-coverage-for-validated-models) is already authorized and requires every canonical engine `ALL_METHOD_KEYS` method, including global, legacy, all six symbolic variants and Monte Carlo. Reuse retained full returns when exact input/configuration and engine identity meet the applicable request.

A diagnostic subset must not replace a broader saved coefficient/diagnostic inventory. Preserve compatible methods outside the requested scope. A coverage extension preserves all existing saved methods and runs only missing ones; it is not a request to rerun the reviewed diagnostic methods or replace saved Monte Carlo draws. Resolve genuinely changed scientific dependencies within their affected authorized scope and keep unresolved conflicts explicit. Before publishing a registered researcher-validated model, ensure full canonical coverage independently of the GE/TE report rows or the three direct diagnostic options.

## Admission and execution

For floor-enabled or migrated configurations, first read [EE-floor accounting](ee-floor.md). Apply the constructor transformation once after the exact audited initialization; never inject a floor inside a method. Retain source, pre-floor and effective EE/M0, external-mortality and detritus accounting with every new diagnostic identity. Floor OFF preserves the audited baseline; changed floor dependencies require their authorized rerun rather than relabeling retained diagnostics. Original signed diagnostics remain historical supporting evidence, and new returns retain their own grades and eligibility.

1. Read source and transformation evidence for the selected or explicitly named candidate. Confirm the exact canonical model/variant identity and its recorded source departures. Apply the [reconstruction audit](reconstruction-audit.md), including missing biology, native-equation limitations and post-loader mutations.
2. Use the audited candidate-specific constructor/settings or reproduce them in a bounded regional script. Do not silently substitute stock defaults, change diet tolerance, solve new BA, pool groups or repair parameters. Runtime diet normalization is always permitted on a separate copy, with raw/runtime sums, factors, changed cells and exact input identities recorded; it does not establish researcher trust or authorize a fresh run. Canonical/extraction/export values stay unnormalized. Authorized variants retain their own identities and changes ledgers.
3. If construction fails, retain the exception and report each unexecuted option as NOT_RUN. A source balance check does not substitute for a diagnostic return. After successful construction, call the actual method:

```python
# calculator is the already-audited PPRCalculator instance.
reports = {
    option: calculator.diagnose_sppr(TE_option=option, short=False, flat=False)
    for option in ("GE", "TE", "With Egestion")
}
```

The example shows the call contract, not a universal loader or exception handler. Handle each option independently so an exception/timeout does not erase other outcomes. If coefficients are needed, `return_sppr=True` returns them with the diagnostic in a tuple; retain the full diagnostic object and avoid solving twice.

4. Save exact returns, settings, source/runtime hashes, engine identity and before/after state. The readable diagnostic report contains only full direct returns and explicit unavailable records. Keep source interpretation, cell evidence, experiments and proposed repairs in a separate extraction/investigation report.

## Distinct outcomes

| State | Reporting and downstream treatment |
|---|---|
| Constructor blocked | NOT_RUN for unexecuted options; exact missing input/exception; no coefficients claimed |
| Execution exception or timeout | Preserve separately from a returned scientific grade; missing is not zero |
| Unsupported equation | Keep the explicit reason; a returned FAIL with null coefficients is not a numerical result |
| Returned FAIL | Retain input/divergence/budget evidence; do not publish that configuration as valid annual PPR |
| Returned WARN | Preserve all warnings, strict balance flags and assumptions; determine scoped eligibility from the concerns |
| Returned OK | Thresholds met for that configuration; source fidelity, ecological suitability and coverage still need evidence |

Keep overall status, component grades and strict Boolean flags distinct. A component OK is not an overall pass. Check negative/nonfinite contributions and coefficients across all biological groups, including unfished groups. Distinguish near-zero efficiency from network divergence, convergence from budget closure, and group residuals from global gaps.

Explain failures by comparing source and loaded arithmetic, verifying units/identities and tracing the worst residual through equations. When supported by the existing formulation, decompose global PP imbalance into weighted group residuals. Do not infer publication error where native stanza, migration, discard or BA conventions remain unrepresented. Loader-solved BA is not observed accumulation.

## Selected-model integration

Reload the exact canonical JSON of the audited model/variant and compare state, flows and requested returns with the audited state before using coefficients. Matching names alone are insufficient. Record accepted configuration-specific methods and warnings; do not change grades to satisfy publication gates.

An authorized selection change uses `python tools/cli/region.py refresh --region regions/<type>/<unit_id>` to save a complete outgoing snapshot and restore compatible selected-model content; current catch, classic PPR, NPP and unrelated human diagnostics remain. Selected FAIL/NOT_RUN candidates can remain pending without annual model estimates. Matching/calculation are separate authorized stages with freshness checks; never relabel earlier results or rewrite hashes to bypass them.
