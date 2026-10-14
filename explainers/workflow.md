# Working with a region

Start with the regional workbook, for example `regions/LME/LME_028/LME_028.xlsx`. `Project.xlsx` brings together paper/model metadata, researcher reviews and saved regional summaries. The map and trends show those saved results. [Project layout](structure.md) explains where their source material lives.

## Choose an existing model

1. In the regional Overview, set `selected_model_id` and write `selection_rationale`.
2. Save the workbook.
3. From the project root, run:

```powershell
python tools/cli/region.py refresh --region regions/LME/LME_028
```

Refresh saves usable outgoing results, derives the new path and shortcut, restores compatible model material, recalculates ready arithmetic and updates the affected project/map/trend/source views. It keeps current Catch, Classic PPR, NPP and unrelated human settings. Repeating the command is safe.

Read the resulting saved status. A selected model can remain pending if coefficients, matching or recorded execution settings are missing. Outgoing values are then unavailable for that selection. Selecting a model does not approve it. See [model selection](model_selection.md) and [current limitations](limitations.md).

## Inspect a saved field

Open the relevant workbook table, or read one table without changing anything:

```powershell
python tools/cli/region.py inspect --region regions/LME/LME_038 --sheet Overview --table Settings
```

This returns the saved table and its input hash. It explains the saved state rather than assessing the whole model's readiness. Blank values mean missing; zero means an actual zero. Consult [SPPR methods](sppr_methods.md) and [parameters](sppr_parameters.md) for the meaning of calculated fields.

## Recalculate arithmetic after changing regional inputs

When compatible group coefficients and matching are available, recalculate dependent regional tables with:

```powershell
python tools/cli/region.py --region regions/LME/LME_028 --stage calculate
```

Changing catch, mapping, coefficients or NPP makes affected saved totals stale. Calculation uses the current inputs; it does not extract a model or run SPPR anew. Missing coefficients, unsupported years and failed/provisional restrictions remain visible. A changed model JSON needs a separate check of loading, diagnostics and coefficient identity before its numbers are used.

To publish fresh saved results for a region, update the project and then the map:

```powershell
python tools/cli/project.py --region regions/LME/LME_028/LME_028.xlsx
python -m tools.project_core.maps.build_html --workbook Project.xlsx
```

These publication commands first ensure the authorized full method coverage for registered researcher-validated models, preserving compatible saved methods and computing only missing inventory entries, then consume saved regional state. A new coverage schema does not justify rerunning existing methods or replacing saved Monte Carlo draws. A project update rejects stale results, preserves human metadata and review records, and changes generated summaries. Model selection uses its combined `refresh` command above. Signed-review registration uses its own bounded handoff rather than a general rebuild.

An explicitly authorized [EE-floor migration](../tools/skills/paper-to-ppr/references/ee-floor.md) changes a calculation dependency. It records ON/OFF and threshold per exact validated model-region pair, including candidates, and reruns genuinely affected methods and diagnostics before recalculating regional totals. Preserve the rest of each audited setup and Monte Carlo sample count. Compatible unaffected results and metadata-only draws remain intact. The migration preserves source inputs, mappings, selections, signed reviews and their exclusions; transformed diagnostics have their own status.

Use `python tools/cli/project.py --migrate-ee-floor --ee-floor 0.1` for an authorized ON migration, or `python tools/cli/project.py --migrate-ee-floor --no-ee-floor` for explicit OFF. Ordinary publication does not silently convert historical settings.

## Add a paper or prepare a review

A new paper/model needs its actual citation and model metadata registered once in `Project.xlsx`, plus the original sources and any applicable extraction work. Filesystem discovery finds model identities and paths; it cannot supply missing citation, area or scientific interpretation. [Model loading](model_loading.md) explains why an extracted JSON differs from the in-memory calculation model.

The [paper-to-PPR workflow](../tools/skills/paper-to-ppr/SKILL.md) describes the scientific stages. The [validation guide](validation.md) explains the report, mapping appendix and researcher decision. In a composed pipeline, mapping is resolved once and its same decisions feed arithmetic and validation. Evidence gaps remain explicit.

Standalone direct diagnostics normally cover GE, TE and With Egestion; validation report rows cover GE/TE. These limited diagnostic/report scopes do not replace the full method inventory required for researcher-validated models on the map. That full inventory is authorized and includes the engine's global, legacy, six symbolic and both Monte Carlo methods. The model's source evidence and actual recorded settings determine its configuration.

## View the result

Double-click `interactive_map/Open map.cmd`, or run `python tools/cli/map.py`. The launcher only serves existing files locally for street detail and opens the browser. It performs no validation, publication preparation, project locking or HTML writes, and does not establish freshness. Generate updated views separately with `python -m tools.project_core.maps.build_html --workbook Project.xlsx`. Publication checks full canonical SPPR method coverage for every registered researcher-validated model, including nondefault candidates. It preserves compatible saved methods and computes only missing inventory entries, preserving inputs, mappings, selections and signed reviews. Researcher validation remains tied to extraction and reviewed SPPR diagnostics; new method outcomes or Monte Carlo coefficients do not revoke it. Unsupported or failed methods remain explicitly unavailable or retain their permitted diagnostic flags; coverage is not approval of every method. Inspect the model heading, diagnostic/review flags, source links and displayed year/basis together. A displayed provisional value is available for review and retains its diagnostic qualifications.
