# EE floor and external mortality export

Read this reference when constructing, migrating, diagnosing or reviewing an EE-floor calculation. It defines a calculation assumption; canonical `model.json`, extracted/source tables, model identity and researcher-authored review records remain unchanged.

## One transformation after audited initialization

`PPRCalculator(...)` and `PPRCalculator.from_modeldata(...)` default to `use_ee_floor=True, ee_floor=0.1`. Explicit `use_ee_floor=False` preserves the previous audited numerical behavior. The threshold must be a finite number in `[0, 1]`, even when OFF; Boolean thresholds are rejected. These are constructor settings, not per-SPPR-method settings. Complete the candidate's recorded loading, diet handling and optional LIM first, then apply the floor once to that completed runtime state.

`from_dict(..., use_ee_floor=None, ee_floor=None)` preserves an existing completed state's configuration, otherwise defaults to ON at 0.1. `apply_ee_floor(...)` returns the calculator: repeating the same configuration is a no-op, and changing it restores the saved pre-floor state before applying the new configuration. Never compound the transformation or rerun an archived loader on already transformed state.

Eligible groups are real living `Regular` and `PP` groups with positive finite production, finite nonnegative completed M0, and a finite valid pre-floor EE in `[0, 1]` below the threshold. Source EE must also be finite and valid in `[0, 1]`: an unknown, negative or otherwise invalid source EE stays excluded even if the loader filled or solved a runtime value. Include primary producers; exclude detritus, synthetic/import groups, operational nonfeeding groups and invalid/missing inputs. A fallback value must not turn an invalid or missing input into an eligible observation. Record skipped groups and their reasons.

For each eligible group, with `P` unchanged:

```text
EE_effective = max(EE_before_floor, ee_floor)
M0_effective = P * (1 - EE_effective)
external_mortality_export = M0_before_floor - M0_effective
```

The new flow is an explicit hypothetical nonfishery sink. It is neither observed catch nor additional predation. Preserve living biomass, production, consumption, diets, predation, catch, respiration, egestion, living biomass accumulation and migration. Distinguish original `source_EE`/`source_M0`, completed `EE_before_floor`/`M0_before_floor`, effective EE/M0 and the external sink in the transformation ledger and provenance. Source and completed values may already differ through the audited loader. A raw independent source M0 may be absent or unknown; retain that missingness rather than claim every canonical model reported it.

## Close the accounting without inventing a source

Route only reduced `M0_effective + egestion` through the existing detritus fate fractions. Refresh detritus inflows, stock residuals and unrouted `det_export`; do not add the removed mortality to detritus as well as the external sink. If reduced inflow cannot sustain unchanged detritus demand, retain the negative detritus stock residual as an explicit limitation. Do not invent an import or repair a living flow to conceal it.

The actual living production equation becomes `P = predation + catch + living_BA + net_migration + M0_effective + external_mortality_export`. Both actual `is_sppr_balanced` branches and forced-balance accounting include the SPPR-weighted external sink, separately from existing detritus export. Preserve the original source scopes. Fishery PPR remains catch × SPPR; catch allocations, global catch weights and fisheries comparisons never count the new sink as catch. An algebraically closed equation does not establish ecological validity or diagnostic eligibility.

The ledger describes the transformation at completed audited initialization. A later forced-balanced copy retains that ledger and sink, while its current vectors and group table describe its separate balanced state. Diagnose that copy directly; do not present the initialization ledger as a new audit of post-balance production or M0.

## Configuration migration and method reuse

An authorized migration persists explicit `use_ee_floor` and `ee_floor` in each exact model-region result configuration. Discover registered researcher-validated pairs generically, including nondefault candidates; do not hard-code a regional list. Preserve the rest of each audited configuration, including Humboldt's `det_collapse_mode='auto'`, `balance_BA_after_DC_normalization=False` where recorded, method options and Monte Carlo sample counts.

From the project root, use the authorized migration entry point:

```powershell
python tools/cli/project.py --migrate-ee-floor --ee-floor 0.1
python tools/cli/project.py --migrate-ee-floor --no-ee-floor
```

The first command records ON at the requested threshold (0.1 is also the default); the second explicitly records OFF. Ordinary coverage publication does not silently migrate a historical calculation.

Archived loader bytes remain the historical base. An explicit `calculation_engine_upgrade='ee_floor_v1'` runs current accounting after the archived audited initialization and records both base-loader and current-engine hashes. An omitted historical floor flag is unknown historical provenance, not evidence that the floor was ON. Reject a requested ON configuration when its pinned engine cannot implement the floor and no explicit supported upgrade is recorded; never silently ignore it or relabel old results.

Check every engine `ALL_METHOD_KEYS` entry (currently 22). Rerun methods and diagnostics whose actual numerical dependencies changed, including affected Monte Carlo methods within the authorized migration. Preserve compatible unaffected results and their restrictions. Metadata-only changes, broader fingerprints and coverage-schema changes do not justify new Monte Carlo draws. Record fresh draws as fresh results, retain the existing sample count/settings, and do not claim equality with historical draws. Recalculate dependent regional arithmetic, invalidate affected sensitivity bounds, and publish only within the existing authorized adoption scope.

## Review and evidence boundary

The user's adoption of this calculation assumption is neither a correction to published model parameters nor renewed researcher approval. Original signed reports and the reviewed diagnostics remain historical, read-only supporting evidence; transformed diagnostics have their own execution identity, status and eligibility. Preserve exact signed verdicts, selections, review/group exclusions and all FAIL, NOT_RUN, provisional, missing-value and Monte Carlo restrictions. A new OK result does not rewrite an old FAIL, and an old signature does not approve a transformed result.

Retain the requested full returns/matrices, the floor ledger and skips, source/completed/effective states, detritus accounting/residuals, method dependency decisions, old/new configuration and code hashes, regional reconciliation and publication checks in the existing model-local evidence/results destinations. Use the [evidence handoff](evidence-handoff.md), [direct diagnostics](direct-diagnostics.md) and [coverage contract](project-integration.md#full-method-coverage-for-validated-models) for the stages actually performed; do not create a second scientific model or approval sidecar.
