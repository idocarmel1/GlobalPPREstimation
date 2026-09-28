# Direct SPPR diagnostics and exact runtime state

This project's default is GE, TE and With Egestion only. Global, broad inventories and Monte Carlo require a broader request. A narrower explicit request controls scope. Reuse retained full returns when exact input/configuration and engine identity meet the request; report formatting need not rerun science.

## Admission and execution

1. Read source and transformation evidence for the selected or explicitly named candidate. Confirm canonical and computational-input identities. Apply the [reconstruction audit](../../prepare-ecopath-model/references/reconstruction-audit.md), including missing biology, native-equation limitations and post-loader mutations.
2. Use the audited candidate-specific constructor/settings or reproduce them in a bounded regional script. Do not silently substitute stock defaults, change diet tolerance, normalize, solve new BA, pool groups or repair parameters. Authorized variants retain their own identities and changes ledgers.
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

Reload the persisted computational input and compare state, flows and requested returns with the audited state before using coefficients. Matching names alone are insufficient. Record accepted configuration-specific methods and warnings; do not change grades to satisfy publication gates.

Changing selection archives/clears obsolete model results with `prepare-selection`; catch, classic PPR and NPP remain. Selected FAIL/NOT_RUN candidates can remain pending without annual model estimates. Matching/calculation are separate authorized stages with freshness checks; never relabel earlier results or rewrite hashes to bypass them.
