# Global PPR across years

## Use the workbook

Open **PPR_global_summary.xlsx**, select the **Global Estimation** sheet, and change the yellow **B3** year cell. The year dropdown, totals, regional PPR, descending ranking, shares and cumulative shares update together. The selected geographic set stays fixed across years.

If a year change does not update the results, set Excel's calculation mode to **Automatic** or press **F9**. Calculation mode can be inherited from another open workbook.

Use B3 as the input. The supporting data/formula sheets are fixed lookup tables: filtering is fine, but do not manually sort, move, or delete their rows. Copy a data sheet first if you want to rearrange it for exploration. The Global Estimation ranking sorts itself automatically.

The delivered archive covers **1950–2019**, the full history in the frozen downloaded catch files: **366 regions and 25,620 region-year records**. The global-estimation sheet uses **167 selected regions: 66 LMEs, 84 EEZs and 17 High Seas regions**. Some regions lack records in some years; these are explicitly marked unavailable, not estimated as zero. The geographic coverage percentage describes the fixed polygons and does not imply that all selected regions have catch observations in every year.

- **Global Estimation** contains only the selected whole regions.
- **Annual Regional PPR** contains the annual results for every LME, High Seas and EEZ alternative, including regions not selected for the global estimate.
- **Selected Regions** records membership, selection reasons and spatial overlap for each chosen region.
- **Spatial Coverage** explains the selection objective, actual geographic coverage, residual overlap and sensitivity comparisons.
- **Selected Year** contains the transparent lookup/ranking formulas. **Available Years** supplies the year dropdown.
- The original sheets remain unchanged as the 2019 reference. Their scope has not silently changed to the new selected set.

Missing records and empty archives remain blank and are counted separately from genuine recorded zero catches. Years with incomplete regional data have a visible warning. A total with missing trophic levels represents only the known-TL component of PPR.

## Method

For each taxon and catch year, specific PPR is `(1 / 0.1)^(TL - 1)` and PPR is catch in tonnes multiplied by specific PPR. TE is **0.1 for all regions and all years**. The optional wet-weight-to-carbon divisor of 9 is not applied, consistent with the established pipeline. PPR is expressed as tonnes of primary-production equivalent under this convention.

The 2020 supplement supplies trophic levels, not the 2020 alternative PPR method. The established matching hierarchy is retained. The same frozen trophic reference is used across years: these are changing catch series, not reconstructed annual trophic levels. Group fallbacks, if needed, use only the relevant year and original matching cohort (EEZ separately from LME/High Seas).

Commercial and functional outputs retain both correct species-first PPR and the deliberate Jensen shortcut. Correct group PPR sums taxon PPR; group specific PPR divides by matched catch. The shortcut first takes catch-weighted mean TL, then computes specific PPR and PPR on the same matched-catch basis.

## Spatial selection

The recommended fixed set starts with LMEs and Sea Around Us High Seas. An EEZ may replace corresponding LMEs only under the earlier rule: at least 90% of each LME is contained in the EEZ, and the EEZ is at least 1.2 times its area. The replacement must also improve the coverage/overlap objective. The 1.1–1.2 review band remains reported.

Additional EEZs are selected when their newly covered area exceeds the new duplicate area. The practical objective weights uncovered area and duplicate area equally. Local additions, removals and one-for-one swaps improve that objective while protecting the LME preference. A High Seas unit can be omitted if removing it improves this same objective; its lost coverage is reported. Full-coverage and stronger-overlap-penalty scenarios document the trade-off. This is a reproducible heuristic, not proof of a global mathematical optimum.

The recommended set covers **97.3023%** of the available source-polygon union. **4.0131%** of its covered area is covered at least twice; the multiplicity-weighted excess is **4.0132%**. A stricter-overlap alternative covers 92.9853% with 2.3210% multiplicity-weighted excess. Full mapped coverage is possible with 360 regions, but would create 23.4545% twice-covered area (24.5459% multiplicity-weighted excess).

The final replacement audit identifies a marginal Australia alternative: replacing seven LMEs would lose about 39,709 km² of coverage while reducing duplicate excess by about 40,873 km². The small net objective improvement is not used because the retained set better respects the preference for LMEs and has higher geographic coverage. Thus the recommendation is explicitly LME-prioritized, not a claim of strict local optimality over every eligible replacement. See `tables/selection_replacement_groups.csv` for the full audit.

Areas are measured on the WGS84 ellipsoid with an equal-area projection after antimeridian normalization and geometry repair. Reported coverage is relative to the union of the available source polygons, not a separately validated global ocean mask. Both sum-minus-union overlap (which counts multiplicity) and area covered at least twice are reported.

**The global estimate is a sum of selected whole-region PPR estimates. Residual overlap can still double-count catch, and gaps can omit catch. We cannot quantify either PPR contribution from whole-region catch files. No area-based PPR correction, clipped-region PPR, or claim of verified 99% global PPR coverage is made.** Geographic coverage is used to choose a practical set, not substituted for PPR coverage.

## Files

- `tables/annual_regions.csv`: all region-year summary results, also available in Excel.
- `tables/regions/<unit_id>/annual.csv`: each region's annual series.
- `tables/regions/<unit_id>/species.csv.gz`: all-year taxon catch, TL provenance and PPR.
- `tables/regions/<unit_id>/commercial.csv.gz` and `functional.csv.gz`: all-year group calculations, including Jensen comparisons.
- `tables/historical_run_metadata.json`, `historical_validation.csv` and `historical_2019_reproduction.csv`: calculation checks and comparison with the completed 2019 release.
- `tables/selection_metrics.json`, `selection_candidates.csv` and `selection_scenarios.csv`: selection audit and alternatives.
- `spatial/selected_regions.geojson`, `selected_union.geojson`, `gaps.geojson`, `overlaps.geojson`, plus all three source polygon layers: geopandas-compatible geometry.
- `workbook_validation.json` and `saved_workbook_validation.json`: live-year and exported-Excel checks.
- `code/`: reproducible historical and selection code. Reuse the raw catch archives and trophic reference from the preceding complete release; the results ZIP does not duplicate those large source archives.

Gzip CSV files can be opened directly by pandas (`read_csv` detects compression) or extracted with a ZIP/archive application. The annual workbook sheet is the convenient Excel view of all regions and years.

## Sources

- Sea Around Us area definitions: https://www.seaaroundus.org/sea-around-us-area-parameters-and-definitions/
- Catch reconstruction and allocation: https://www.seaaroundus.org/catch-reconstruction-and-allocation-methods/
- Downloaded catch API: https://api.seaaroundus.org/api/v1/

Original source files and the completed 2019 release are preserved. The new release is separate so earlier checksums and results remain reproducible.
