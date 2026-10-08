> **Reorganization scope: frozen historical evidence.** This guide retains the original study/release statements, counts, scientific assumptions and execution history. Its former paths or build commands are not the current project workflow. Follow the [current structure contract](../../../explainers/structure.md) and resolve retained dependencies through the portable source-path ledger before any separately authorized reproduction. Reorganization does not certify old results as current or authorize reruns.

# Expanded discard-routing sensitivity

Open `report.html` for the standalone interactive experiment. It contains all data
and scripts, with no external assets. The report separates **20 added eligible
models** from **four original references**, including zero-harvest Okhotsk NE.

This directory is the sole write boundary. Original study inputs/results,
production calculators, source JSONs, workbooks, PPRAtlas and NPP work were preserved.
No new paper extraction, model parameter recovery, annual reconstruction, fisheries
mapping or production export is part of this expansion.

The numerical grid is every integer percentage 0–20%, then 25%, 30%, 40%, 50%, 75%
and 100%. Each displayed point is solved. Native H stays fixed; D=fH and retained
L=(1−f)H. Methods, physical ledger, carbon convention and source scopes follow the
original experiment. Incompatible native denominator boundaries remain unavailable.
Scenario ranges are sensitivity envelopes, not confidence intervals.

## Audit files

- `SELECTION_POLICY.md`: recorded selection, eligibility and resource policy.
- `input_manifest.json`, `workbook_input_manifest.json`: immutable source snapshots
  and SHA-256 hashes. Existing workbooks were found after selection was fixed.
- `results/candidate_screening.json` and `.csv`: all 252 files, including exclusions,
  scientific rejections, resource-limited cases and untested remaining candidates.
- `results/selected_models.json` and `model_catalog.json`: source metadata and the
  independently screened addition cohort, plus separate reference metadata.
- `results/raw_to_initialized_parameters.csv`, `loader_transformations.json`:
  exact raw-field, loader and initialized values, missing sentinels and fate changes.
- `results/models/<id>/`: raw/validated study JSON, full flow ledger, parameter
  changes, numerical diagnostics, group coefficients and baseline checks.
- `results/ecosystem_ppr.csv`, `group_sppr.csv`, `effect_decomposition.csv`,
  `scenario_envelopes.csv`, `aggregate_distributions.csv`: combined numerical data.
- `results/standard_method_comparison.json`: signed excess/deficit versus fixed
  baseline group TL and TE=0.1, evaluated on the same H.
- `results/discard_responses.v2.json`: proposed exact-model group response interface.
- `verification/`: tests, input/output checks, original overlap, browser checks and
  runtime evidence. Browser verification is explicitly documented after execution.
- `METHODS_AND_FINDINGS.md`: scientific methods, findings and limitations.

## Reproduce

Use the existing scientific Python runtime; do not install into shared environments.
This run uses `C:/Users/idoca/miniconda3/python.exe` with UTF-8 and one BLAS thread.
From this directory:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
python -X utf8 src/run_all.py
python -X utf8 src/audit_saved_differences.py
python -X utf8 src/summarize.py
python -X utf8 src/audit_inputs.py
python -X utf8 src/verify_outputs.py
python -X utf8 src/findings.py
python -X utf8 -m pytest tests -q -o cache_dir=verification/pytest_cache
python -X utf8 src/static_checks.py
python -X utf8 src/render_report.py
node src/verify_report_runtime.cjs
```

`run_all.py` runs one model at a time and reuses a completed run only if source,
settings, fraction grid and calculation-code fingerprints match. Each heavy model
runs in its own process to bound memory. `screen.py` can repeat deterministic
selection from the immutable corpus, retaining cached screening outcomes. Snapshot
scripts are initial inventory utilities and are not required to reproduce results.
They refuse to replace an existing snapshot with changed live bytes.

The standalone HTML's embedded compression uses the browser's native
`DecompressionStream`; the report is tested in an actual supported browser through
an unused loopback port. Its CSV/JSON buttons use the same embedded verified data.

The final source-fidelity rule replaces four provisional cases without using
sensitivity direction or magnitude. The original candidate order is preserved;
20 additions qualify among the first 52 queued candidates. The four excluded
provisional runs remain in `results/excluded_provisional_models/`. Santa Pola is
explicitly a marine fish farm and is excluded. The valid cohort contains 18 named
ecosystems, including two Atlantic temporal pairs; it is not 20 independent
ecosystem replicates. See the amendment in `SELECTION_POLICY.md` and the immutable
provisional catalogs. Initial and final saved-workbook manifests are both retained.

No atlas data are updated automatically. See `RESPONSE_INTERFACE.md` before a later
coordinated integration with selected/global annual NPP denominator controls.
