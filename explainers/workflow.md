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

These commands consume saved regional state. A project update rejects stale results, preserves human metadata and review records, and changes generated summaries. Model selection uses its combined `refresh` command above. Signed-review registration uses its own bounded handoff rather than a general rebuild.

## Add a paper or prepare a review

A new paper/model needs its actual citation and model metadata registered once in `Project.xlsx`, plus the original sources and any applicable extraction work. Filesystem discovery finds model identities and paths; it cannot supply missing citation, area or scientific interpretation. [Model loading](model_loading.md) explains why an extracted JSON differs from the in-memory calculation model.

The [paper-to-PPR workflow](../tools/skills/paper-to-ppr/SKILL.md) describes the scientific stages. The [validation guide](validation.md) explains the report, mapping appendix and researcher decision. In a composed pipeline, mapping is resolved once and its same decisions feed arithmetic and validation. Evidence gaps remain explicit.

Fresh direct diagnostics normally cover GE, TE and With Egestion; validation report rows cover GE/TE. Broad method inventories and Monte Carlo are separate scientific work. The current model's source evidence and recorded settings determine the appropriate configuration.

## View the result

Double-click `interactive_map/Open map.cmd`, or run `python tools/cli/map.py`. The launcher serves the map on this computer. Inspect the model heading, diagnostic/review flags, source links and displayed year/basis together. A displayed provisional value is available for review and retains its diagnostic qualifications.
