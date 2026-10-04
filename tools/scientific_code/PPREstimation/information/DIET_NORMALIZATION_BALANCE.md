# Runtime balance after diet normalization

`PPRCalculator.from_modeldata(normalize_DC=True)` preserves the supplied raw
`ModelData` and constructs a normalized runtime diet. After deterministic
completion and any requested LIM completion, it compares raw and normalized
predation using the **same finalized consumer consumption**. PP, DET and Import
rows contribute no feeding consumption in either calculation.

All three loading APIs (`PPRCalculator(...)`, `from_modeldata(...)` and
`from_dict(...)`) accept `normalize_DC=False`, `DC_tol=0.001` and the binary flag
`balance_BA_after_DC_normalization=True`. The BA flag defaults to True, preserving
the correction described here. False still allows diet normalization and normal
property completion but prevents any new BA correction. `normalize_DC=False`
and unchanged diet rows produce no correction regardless of the BA flag.
The new arguments follow existing positional arguments, with the BA flag
immediately after `DC_tol`.

For example, load the same model with or without computational BA closure:

```python
enabled = PPRCalculator(
    model_path, normalize_DC=True, DC_tol=0.001,
    balance_BA_after_DC_normalization=True,
)
disabled = PPRCalculator.from_modeldata(
    ModelData(model_path), normalize_DC=True, DC_tol=0.001,
    balance_BA_after_DC_normalization=False,
)
reloaded = PPRCalculator.from_dict(
    disabled.__dict__, normalize_DC=True, DC_tol=0.001,
    balance_BA_after_DC_normalization=False,
)
```

Dictionary loading copies its supplied groups and diet. With normalization
disabled it preserves legacy diet handling; when requested it normalizes the
supplied diet before completion. A False BA flag does not undo accumulation
already present in a serialized state. Each load replaces the normalization
audit ledger, so previous corrections are not reported as newly applied.

For a Regular or PP group whose raw production equation already passes the
existing `np.isclose` balance tolerance, the runtime adjustment is:

```
BA_runtime = BA_before_adjustment - (predation_normalized - predation_raw)
```

This additive correction preserves a supplied nonzero accumulation and the
small residual already present in the raw equation. It changes only runtime
biomass accumulation. It does not recompute EE, M0, production, consumption,
catch, migration, respiration, egestion, detritus routing or exports. DET and
Import accumulation are excluded. Ordinary defaults and LIM completion still
precede this correction and retain their existing behavior.

The correction is a computational closure associated with diet normalization;
it is **not an observed ecological biomass trend**. Raw production inconsistencies
are recorded and receive no biomass accumulation correction. Missing production
terms, unknown feeding
consumption or diet cells, and finalized predation inconsistent with the diet
also prevent correction. Disabled normalization and unchanged diets leave
accumulation unchanged. Consumption-balance failures and SPPR convergence
warnings are not repaired by this procedure.

When recorded accumulation corrections leave the runtime balanced, its
`balanced_model` is a copy of that corrected state: table, vectors and ledger
retain identical accumulation, with no second parameter adjustment. Disabled
normalization, unchanged diets and runtimes that remain unbalanced retain the
existing legacy balanced-copy construction, as does a False BA flag.

Two DataFrame attributes provide an audit record and can be retained by existing
state serializers:

- `diet_normalization_rows`: raw/runtime row totals and changed rows.
- `diet_normalization_balance_ledger`: per-group eligibility, reason, original
  source accumulation (missing source stays missing), original and adjusted
  runtime accumulation, raw and normalized predation, adjustment,
  and raw/final production residuals. All rows explicitly label the correction
  as computational.

The ledger records the requested BA flag. Eligible trophic groups skipped
because it is False receive `reason='ba_balance_disabled'`; disabled diet
normalization receives `reason='normalization_disabled'`. These reasons report
the control that prevented adjustment, while the raw and normalized predation
and pre-correction BA remain available for inspection. Original source inputs
are never rewritten by either flag setting.

The direct GE, TE and With Egestion coefficients depend on the diet, production,
consumption and mortality/egestion flows rather than accumulation. Their full
SPPR, A and L matrices remain exactly equal when this correction is applied
under the existing LME027 direct configuration (`det_collapse_mode='never'`,
`det_open_mode='none'`, `det_theta=1`, `det_external_sppr=0`). Catch multiplied
by these unchanged coefficients also stays unchanged. The global budget
diagnostic includes accumulation, so its result can change. This does not claim
invariance for experimental routines that rebalance other flows.

The implementation changes future runtime construction. It does not replace
retained calculations, source JSONs, regional results or reviewed documents.
