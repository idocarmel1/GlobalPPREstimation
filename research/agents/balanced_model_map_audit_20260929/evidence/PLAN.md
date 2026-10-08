# Minimal balanced-state implementation plan

Date: 2026-09-29. **Planning only — no implementation or scientific execution authorized.**

This plan narrows the earlier [audit](REPORT.md). It proposes the fewest safe edits to make `balance_model()` return a coherent state and let map-bound calculations opt into that state. Canonical models, workbooks, maps and skills have not been changed. The two excluded files, `notes for AI.txt` and `Model_validation.docx`, were not read or modified.

Paths below resolve relative to this report directory. Line numbers refer to the audited code.

## Recommended API and default

Add a trailing keyword-only `use_balanced_model: bool = False` to all three public entry points in [PPRCalculator.py](../../../tools/scientific_code/PPREstimation/PPRCalculator.py):

- `__init__()` at line 43;
- `from_modeldata()` at line 129;
- `from_dict()` at line 82.

**Default False preserves the current active calculator behavior for existing source reviews, diagnostics, tests and experimental callers.** The separate balanced copy will have corrected bookkeeping, but unflagged calculations continue to use their original active fields. Enable True explicitly only in calculation routes that supply the map.

Proposed control flow:

```text
__init__(..., use_balanced_model=False)
    → from_modeldata(..., use_balanced_model=flag)
    → copy returned attributes into the actual self, as today

from_modeldata(...) or from_dict(...)
    → existing load/defaults/LIM pipeline, unchanged
    → existing _fill_properties creates the balanced copy
    → existing sort
    → shared small finalizer:
          flag False: retain original active fields
          flag True: adopt fields from the generated balanced copy
    → return instance
```

The finalizer should copy the balanced copy's scientific attributes into the same instance, retain its separate `balanced_model` snapshot, and record `use_balanced_model=True`. Copy the scientific attribute dictionary deeply, excluding lineage/cache references; do not alias mutable active vectors/tables to the retained snapshot. This gives every construction route the same behavior and keeps `calculator.balanced_model` available. For False, record False and otherwise preserve active fields.

`self = self.balanced_model` inside `__init__` only rebinds a local variable. It does not replace the object returned to the caller. Updating the actual instance's attributes is the small correct solution. Factories could instead return the balanced object, but then the constructor and factories have different snapshot/identity details unless further normalized; avoid that extra variation.

An `original_model` copy is **optional**, not needed to select the balanced state. If retained, define it as the completed pre-balancing calculator state, not the canonical paper model. Create it before adoption and strip nested lineage references; do not create an original↔balanced reference cycle. The existing `_model` remains source/loader evidence as described below.

## Essential balance_model() changes: state consistency

Modify `balance_model()` in [PPRCalculator.py](../../../tools/scientific_code/PPREstimation/PPRCalculator.py), lines 696–735. Keep the existing equations and `change_production=False` policy for this implementation.

1. **Copy scientific state without old lineage snapshots.** A repeat call or from_dict input may already contain `balanced_model` or a future `original_model`. Exclude those references when making the working copy; never return a stale nested balance snapshot as the newly balanced state.
2. **Synchronize the stored group representation with the returned runtime.** At least write the returned `p`, `q`, `catch`, `predation`, `M0` and `growth` into the corresponding table columns, with growth represented as `biomass_accum`. Preserve the original group IDs, names and trophic classifications. Synchronize vector/table mirrors for the other recorded runtime quantities, without inventing or re-solving additional biological values.
3. **Respect the existing net-migration convention.** `_fill_properties()` line 249 subtracts table `detritus_import` to obtain runtime `net_migration`. To retain that table convention, write table net migration as runtime net migration plus the retained detritus-import term. Do not simply write the runtime vector as an ordinary input value and subtract the import again on reconstruction. Keep immigration/emigration source fields explicitly source-derived; do not invent an arbitrary decomposition of the adjusted net migration.
4. **Synchronize dependent mirrors whose defining values changed.** For example, if `change_production=True` is used elsewhere, `GE`/table `ge` and production-per-biomass must agree with the returned `p` and unchanged biomass. Handle zero/missing denominators with the existing conventions. Preserve the current stored TL policy rather than silently introducing a new TL reconstruction. If balancing actually changes a TL-defining flow, treat the need to recompute a derived TL as an explicit follow-up policy/test; do not call all Ecopath defaults to repair it. Likewise do not silently change detritus Q or routing to enforce another physical equation.
5. **Refresh cached balance status.** After the final state is assembled, set `is_balanced = is_model_balanced()[0]`, preserving False when that is the actual result. Keep `n_balance_runs` meaningful. Sort consistently before returning.
6. **Do not call `_fill_properties()` to synchronize.** It would regenerate another balanced copy, reset bookkeeping and risk recursion. Do not rerun defaults/LIM or reconstruct through ModelData/from_dict merely to synchronize fields.

This is a bookkeeping correction to the result of the existing algorithm. It does not establish source fidelity or successful ecological balance.

### get_model() remains source-only

`get_model()` at lines 803–813 returns `_model`; `get_groups_df()` at 815–821 returns `_groups_df`. **Keep `_model` as the original ModelData evidence and document get_model() as source/loader input, not the adopted balanced runtime.** Do not mutate `_model.data_json` to resemble the balanced state. Callers needing displayed/calculated group state must use the synchronized `get_groups_df()` and the active runtime matrices/vectors.

This is narrower and safer than retrofitting a full inverse Ecopath serializer. The map must link the calculation workbook containing balanced group values, not use get_model().data_json as a supposed balanced export.

### from_dict is reconstruction, not exact restoration

Before rebuilding, remove inherited snapshot/selection markers from the copied attribute dictionary. Honor the explicitly supplied new flag, not a stale value in that dictionary. Retain the current reconstruction pipeline. Its documented contract must not promise exact restoration: defaults/LIM run again. Existing exact-state restoration code that uses `__new__` and `__dict__.update`, or pickle, bypasses these constructors and requires explicit handling below.

## Minimum exporter propagation and opt-in sites

In [create_PPRS_excel.py](../../../tools/scientific_code/PPREstimation/create_PPRS_excel.py):

| Function | Minimum change |
|---|---|
| `load_model()` at 954 | Add flag default False and pass it to `PPRCalculator.from_modeldata`. Keep all current settings unchanged. |
| `run_directory()` at 1342 | Add flag default False and pass it to load_model and build_model_tables. |
| `write_model_excel()` at 993 | Add flag default False and forward the same way. This keeps the single-file export route consistent. |
| `build_model_tables()` at 810 | Add flag default False as a **requirement check**, not a second model switch. With True, require an opted-in, unchanged active balanced state before `runner.set_model()` and method execution. Export groups/diagnostics/results from that same object. |

The build check must not silently do `model = model.balanced_model`. A caller may have edited the model after construction, leaving a cached balanced snapshot from before those edits. Check the flag and equality of the calculation-input fields with the retained balanced snapshot (indexed vectors, groups, diet and detritus matrices, names/types, and relevant adapter state); exclude diagnostic/output caches. If they differ, fail clearly and require the caller to make an explicit new balanced choice. An input-only fingerprint is an alternative implementation, but a comprehensive manifest system is not necessary for this check.

At [run_region.py](../../../tools/project_core/calculations/run_region.py), `sppr()` line 45, pass `use_balanced_model=True` to run_directory. This is the single opt-in for the ordinary regional route. Do not change its requested method list or turn direct three-method work into a broad inventory.

`resume=True` in run_directory currently skips any existing workbook at lines 1382–1387. With True balanced mode, require the existing output's balanced-use marker before reuse; otherwise reject/refresh it. A filename alone cannot establish opt-in.

### Special map-bound callers

Use the verified producer list in [REPORT.md](REPORT.md), section 3. The minimum future edits are flag opt-ins at their existing constructor calls, retaining every candidate's settings and method configuration:

- California: [prepare_selected_coefficients.py](../../../regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014/model_validation/evidence/source_review/extraction_review_20260928/prepare_selected_coefficients.py), constructor line 29.
- WCPO trio: [reproduce_and_integrate_wcpo.py](../../../regions/EEZ/EEZ_941/papers/WCP-2007/models/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)/model_validation/evidence/source_review/evidence/2026-09-28_integration/reproduce_and_integrate_wcpo.py), construction and comparison reload at 29 and 46.
- HS_077: [reproduce.py](../../../regions/HS/HS_077/papers/ETP-2003/models/077HS_1_Eastern_tropical_Pacific_(1993-1997)/model_validation/evidence/source_review/evidence/2026-09-28_integration_audit/reproduce.py), adopted-runtime construction/reload at 55 and 77; leave the separate strict-source admission probe unchanged.
- North Sea: [audit_runtime.py](../../../common_reference_data/provenance/source_paths.csv), constructor at 51. Its restored state must retain the new active state and marker; an old saved state cannot acquire the marker by relabelling it.
- Northwest Africa and Benguela: the `run()` constructors in their `integration_20260928/reproduce_direct.py` files, line 40 (links in REPORT.md).
- Kyoto: [run_selected_sppr.py](../../../common_reference_data/provenance/source_paths.csv), line 15.
- Falklands: [run_selected_sppr.py](../../../regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native__source/extracted_tables/evidence/run_selected_sppr.py), `audited_load()` at 25 must accept/forward the new keyword to its constructor. Keep its candidate-specific loader rather than switching it to stock normalized diets.
- Patagonia, Visayan and Watari: their archived coordinator scripts are evidence. Use future active wrappers with the same reviewed settings and explicit flag; do not rewrite frozen studies just to retrofit the policy.

For direct callers, use the same publication-state check before writing groups/coefficients. Existing saved methods, frozen engine copies and exact-state snapshots require fresh verification or regeneration later; do not claim an opt-in code edit retroactively changes them. Preserve original scientific reproduction scripts when they are frozen evidence, creating a small current wrapper instead if needed.

Do not globally opt in candidate-only source diagnostics, historical experimental engines, Monte Carlo draw internals or frozen sensitivity scripts. Monte Carlo already solves against its active base calculator; it needs a balanced base only when its results are being adopted for the map.

## Smallest workbook and map connection

Reuse existing `Selected model groups / Groups`, `Group SPPR`, Diagnostics and `sppr_source.xlsx`. They must all be produced from the same opted-in object. No new coefficient schema is required.

1. In the SPPR producer, record an Overview/diagnostic marker such as `results_use_balanced_model=True` and the **actual** relative calculation-workbook path, e.g. `sppr_source_path`. Clear it with model-dependent results in `prepare_selection()`. Do not let `regional.recalculate()` fabricate it; calculation only consumes existing verified coefficients.
2. Add the minimal validation gate in [workbooks.py](../../../tools/project_core/workbooks/workbooks.py), `validate_region()`, and at [regional.py](../../../tools/project_core/calculations/regional.py), `recalculate()`, before map-bound model calculation/publication. Require the marker and a matching saved calculation source for model numerical results under the new policy. Keep selected-but-NOT_RUN/pending states valid with no numerical result. Existing input/table/workbook hashes remain in use; source-workbook hash can reuse the existing sha helper.
3. In [original_atlas_data.py](../../../tools/project_core/maps/original_atlas_data.py), `detail_from_book()` continues reading Groups and Group SPPR, now synchronized by the producer. At lines 264–268 replace guessed model-folder links with the recorded calculation-workbook path. For direct integrations without a separate source workbook, the regional workbook itself is the valid parameter/results view. Do not fall back to canonical model.json and imply it is the balanced runtime.
4. The map's existing source link and the trends workbook link can point to that balanced calculation record, with an accurate label. Original paper/native-model links remain source evidence. A workbook link exposes balanced parameters/results; **it is not a promise of an exactly reloadable calculator JSON**. If the required deliverable is specifically a balanced JSON model, a separate serializer/export is additionally required.
5. Do not retain historical selected detail based solely on the “migrated” status. Rebuild selected group detail from the opted-in workbook. Old alternative payloads without the balanced marker cannot remain computationally selectable under this requirement; keep their source evidence, and show unavailable until independently prepared. This needs a small payload gate, not a redesign of browser preference keys.

The existing browser group calculations can remain unchanged because group IDs/names, allocation weights and coefficient shapes are preserved. Verify that both map and trends receive the same updated group data. Existing model-level preferences can stay when group identity is unchanged; reject unavailable alternatives rather than silently using their old data.

## Scientific decisions not hidden inside this patch

1. **Current equations do not guarantee both identities.** With change_production=False, fixed p/q/egestion/respiration may leave a consumption residual. The minimum patch reports the true result and uses the requested exposed balanced state; it does not alter biology to make the flag True. If the user requires strict balance, choose which physical quantity may change before changing the equations. A strict publication rejection is distinct from silently repairing those quantities.
2. **Finalized experimental states, especially Celtic.** Its RoutingExperimentCalculator deliberately has balanced_model=None after discard-return/printed-BA changes. No flag can safely select a nonexistent or pre-mutation cached copy. A new balanced derivative of the finalized adapter needs an explicit scientific decision about BA/return semantics and its identity. Until resolved, fail/mark unavailable for the balanced publication route while preserving the selection and original evidence.

Optional robustness: bound iterations and detect nonfinite values in balance_model. Recommended separately, but do not change the convergence equations under a bookkeeping patch or introduce new constructor failures without tests. Similarly, a changed-production/TL derivation policy is not implied by a map opt-in that uses change_production=False.

## Minimum implementation sequence and focused verification

No steps below were executed scientifically in this planning task.

1. Correct balance_model snapshot/table/status bookkeeping and document source-only get_model.
2. Add the shared flag finalizer to both factories; forward from __init__. Keep defaults False.
3. Thread the flag through the exporter; opt in ordinary regional SPPR and the candidate-specific production adapters. Add the pre-export unchanged-state check and balanced-aware resume check.
4. Save the small marker/source-path metadata; add regional publication guards and use recorded workbook links/current group data in the adapter. Gate unsupported old alternatives.
5. Run focused synthetic/unit tests before any authorized real-model migration. Later migrate only authorized regions/methods and refresh dependent outputs; preserve prior scientific outputs as evidence.

Focused tests to add/run at implementation time:

- All three constructor routes: False preserves existing active values; True adopts balanced fields; no `self` rebinding bug, mutable aliasing or recursive snapshots.
- from_dict ignores inherited selection/cache markers and honors the explicitly supplied flag.
- balance_model leaves its input untouched; returned Groups mirrors runtime with correct net-migration/import convention; cached is_balanced equals a fresh check. An intentionally incompatible consumption fixture remains False rather than being falsely labelled balanced.
- Existing get_model remains source evidence while get_groups_df exposes adopted balanced parameters.
- Mock exporter methods verify the same active object supplies worker calculation, diagnostics and groups. Post-construction mutation is rejected rather than switching to the old snapshot.
- Default and balanced exporter forwarding, Falklands loader keyword compatibility, and refusal to resume an unmarked legacy export.
- Tiny workbook fixture: pending selection accepted; unmarked model coefficients rejected for balanced publication; marker/path cleared on selection change; calculation cannot create the marker.
- Adapter/JavaScript fixture: all-group and subset calculations agree with saved coefficients; links resolve to the actual balanced calculation workbook; stale alternatives stay unavailable. Preserve provisional failures, source scopes, catch weights and single carbon conversion.

## Deferred, not part of the minimum patch

- Generic exact-state JSON serializer/deserializer and comprehensive manifests.
- Broad source/canonical/model identity redesign, group-ID migration and browser storage-key versioning.
- Rewriting archived scripts, scientific engines or existing report evidence.
- New balancing equations, changing source biology, rerunning all models or Monte Carlo inventories.
- Skill updates. The user's later report/data/map alignment requirement remains a future design constraint: a report must consume adopted mapping/confidence/results rather than changing them only in prose. It does not expand this plan into a current report or data update.
