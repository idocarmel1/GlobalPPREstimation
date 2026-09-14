---
name: update-ppr-project
description: Consolidate regional Global PPR workbooks into Project.xlsx and generate the original map and annual graphs; use for a single-region update, full project refresh, or supplementary release.
---

Project.xlsx owns central paper and model metadata. Regional Overview owns selections and rationales. Numerical project tables are generated region-level outputs; do not insert taxa, catch matrices, or group coefficients into them.

For a regional path, resolve its containing project and run:

```
python tools/update_project.py --region regions/LME_028/LME_028.xlsx
python tools/build_html.py --workbook Project.xlsx --output interactive_map/index.html
```

For a full refresh use `--all` instead of `--region`. Commands are run from the project root; absolute paths and `--root` also work. The updater preserves central paper/model metadata and replaces the complete set of generated records for updated regions. The all-region build removes orphaned generated rows. Neither command executes SPPR or performs matching.

If a selected model is absent from Models & coverage, register it from its known source identity. Do not invent publication metadata. A first selection may have no results yet. If results belong to a previous model or input hashes changed, refresh the affected regional processing; never rewrite hashes merely to bypass a stale-result error. Use calculate-regional-ppr for that stage if requested. The HTML generator reads Project.xlsx, automatically locates regional workbooks for detailed views, and uses the preserved atlas source context inside the reorganized package. The output pages retain the original layouts and controls.

The common-catch tables use anonymous cohort IDs to avoid transporting taxa into Project.xlsx. Paired method ratios must use their common-catch totals. Annual comparisons use a stable common region cohort and disclose per-method catch coverage. Preserve blanks, zero denominators, exact method health, source scopes, catch bases, unidentified treatments, and carbon conversion.

Verify updated regional totals, source links and missing states in Project.xlsx. Check the generated HTML, allowing the original map’s Leaflet, font and basemap dependencies, including a region source panel, common-catch ratio, annual PPR/NPP, and unavailable data. Do not claim an online deployment: the delivered artifact is a local standalone file. Preserve alternative model and frozen experimental evidence outside production tables.

Read `../original_skill_resources/claude/ecopath-paper-to-ppr/references/integration-contract.md` for the original integration semantics, and `references/mortality-and-discards.md` relative to the same original skill when interpreting discard or mortality comparisons. Retain source-use distinctions, exact diagnostic configuration gates and experiment boundaries. Their historical repository commands are superseded by the two current scripts above. The project guide and dependency instructions are in `../../../README.md`.
