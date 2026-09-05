# All Sea Around Us EEZs — TE = 0.1

This extension retains **all 282 Sea Around Us EEZ units** and adds the earlier geographic selection rules as advisory flags. No EEZ is filtered out, and no LME is actually replaced. The previous TE=0.1 and TE=0.05 releases and the user-edited reference workbook remain unchanged.

The completed analysis uses **2019**, the latest common year across all 366 EEZ/LME/High Seas archives. It contains 24,223 EEZ taxon rows, 100% catch-weighted TL matching coverage and no Jensen inequality violations. All EEZs have catch in the selected year. The sum across EEZ source units is 102,851,768.50 tonnes of catch and 66,442,175,603.65 tonnes of PPR equivalent; these are **not deduplicated world totals**.

## Open the results

- `eez_output/PPR_eez_summary.xlsx`: full EEZ summary, a `summarized summary` sheet modeled on the supplied workbook, spatial flags, all positive EEZ/LME pairs, and an all-area comparison.
- `eez_output/regional_calculations/`: one workbook per EEZ, with Species, Commercial, Functional, Missing TL, Validation and Metadata sheets.
- `eez_output/PPR_EEZ_validation_executed.html`: the executed validation notebook in a browser-friendly format. The editable `.ipynb` is beside it.
- `eez_output/tables/`: machine-readable calculations, source/version/year audits, all 350 positive EEZ/LME intersections, and selection flags.
- `eez_output/spatial/`: GeoJSON layers in EPSG:4326 for EEZs, LMEs and Sea Around Us-defined High Seas. Use `LMEs_normalized.geojson` and `HighSeas_normalized.geojson` with `EEZs.geojson` to reproduce the new dateline-safe overlays. Original LME/HS exports are also retained.
- `eez_output/release_validation.json`: independently verified run totals, matching coverage and workbook checks.

The all-area comparison contains 282 EEZs, 66 LMEs and 18 High Seas units. Its percentages, ranks and cumulative shares are calculated **within each spatial type**, not across overlapping spatial systems. Sorting ties uses the stable unit ID. If editing values in Excel, re-sort the compact table by type and descending PPR to interpret the cumulative column as a ranked cumulative curve.

## Spatial rules

The following are the requested defaults for this release. The run's actual thresholds are recorded in `tables/spatial_validation.json` and the workbook's Selection Rules sheet; the notebook displays those recorded values.

| Flag | Exact condition |
|---|---|
| `flag_add_low_lme_overlap` | area(EEZ intersect union of all LMEs) / area(EEZ) **< 0.10** |
| `flag_prefer_eez_candidate` | At least **90% of the whole LME** is inside the EEZ, and area(EEZ) / area(LME) **>= 1.20** |
| `flag_review_110_120` | Same containment condition, and **1.10 <=** area ratio **< 1.20** |

“Mostly contained” was not numerically specified, so **90% is a provisional, configurable interpretation**. Every exact fraction and denominator is retained, allowing later review with a different threshold. Preferences are pair-specific; an EEZ may contain several LMEs. Different pairs can trigger preference and review flags independently. All overlapping pairs are listed, not just the preferred pair.

The initial geographic run yields 68 low-overlap EEZ flags, 9 preference-candidate EEZs (16 pairs), and no review-band candidates. The nine preference candidates are Australia, Brazil (mainland), Faeroe Islands, Russia (Far East), Russia (Laptev to Chukchi Sea), Canada (Arctic), Canada (East Coast), Mexico (Pacific), and USA (Alaska, Subarctic). These are candidates, not selected replacements.

Areas use a WGS84 ellipsoidal equal-area calculation with densified source-linear edges, checked against geodesic areas. The geographic overlay preserves the meaning of the source GeoJSON edges. Invalid source geometries are repaired explicitly (147 EEZs), and periodic longitude representations are normalized. Source precision, boundary definitions and repairs still limit geographic accuracy; numerical agreement is not a claim of legal boundary accuracy.

## Important interpretation limits

**Do not add EEZ + LME + High Seas PPR as a unique world total.** EEZ units also overlap one another: the sum of individual EEZ polygon areas exceeds their union by about 5.19 million km². EEZ sums in this release are descriptive sums across source units, not deduplicated ocean totals.

Small area overlap does not guarantee small catch overlap. No catch is removed, prorated by area or inferred for uncovered polygon fragments. These flags are a screening tool for later selection; constructing an exact disjoint catch partition would require spatial catch information and a separate decision about overlaps.

Sea Around Us EEZs can be separate ocean-facing coasts, territories, islands or EEZ-equivalent waters, rather than one dissolved polygon per sovereign country. Use the official unit IDs to join catches and polygons.

## PPR method and matching

Only the approved 1995 trophic-chain calculation is used:

`SPPR = (1 / TE) ** (TL - 1) = 10 ** (TL - 1)`

`PPR = catch_tonnes * SPPR`

TE is 0.1 throughout this release. The separate wet-weight-to-carbon divisor of 9 remains off, as in the approved pipeline; units are tonnes of primary-production equivalent, not tonnes of carbon. The supplied 2020 supplement contributes MeanTL, not its alternative SPPR regressions.

TL matching retains the existing documented hierarchy: exact 2020 supplement match; exact same-unit Sea Around Us exploited-organism match; supported genus mean; commercial-group fallback; functional-group fallback; otherwise unmatched. Source, method, confidence and reference taxon remain visible. Broad Sea Around Us taxa are not relabeled as species.

For commercial and functional groups, correct PPR is the sum of matched taxon PPR, and group SPPR is that sum divided by matched catch. The deliberate Jensen shortcut uses catch-weighted mean TL before exponentiation, on the same matched-catch support. Unmatched catch is retained and reported, not treated as zero TL. Entirely unmatched groups have undefined PPR; matched taxa with zero catch have zero PPR but undefined SPPR/Jensen metrics.

In this 2019 EEZ run, all matches use the exact 2020-supplement or exact same-unit Sea Around Us routes; no genus/group fallback is needed. Across EEZ source units, the Jensen shortcut underestimates correct PPR by **22.27% for commercial groups** and **14.44% for functional groups**, measured relative to correct PPR. These comparisons share the same overlapping-unit support and are not unique-world totals.

Catches retain all downloaded landings and discards, reported and unreported, across entities, sectors, gears and end uses. Original archives preserve every available year. The selected analysis year is the latest year common to all nonempty EEZ, LME and High Seas catch archives; empty official archives are explicitly audited and retained without constraining the year.

## Reproduce or change the year

Python requirements are in `requirements.txt`. From the extracted project folder:

```text
python -m pip install -r requirements.txt
python download_eez_data.py
python run_eez_pipeline.py
```

To calculate another supported common year:

```text
python run_eez_pipeline.py --year 2018
```

Configuration is in `config/eez.yml`, including the four spatial thresholds. The runner checks archive IDs and source version 50.1, selects the year across all spatial systems, recalculates every EEZ, and uses TE=0.1 LME/HS comparisons for the same year. If a different comparison year is needed, it calculates into `eez_comparison_output`, preserving `global_output`.

The Python pipeline produces all scientific CSV/GeoJSON outputs. Spreadsheet creation uses the `@oai/artifact-tool` JavaScript runtime supplied by Codex; it is not a Python package. In a Codex environment with that dependency available:

```text
node tools/build_workbooks.mjs --scope-label=eez --output-directory=eez_output
python tools/validate_eez_release.py
python build_eez_notebook.py
```

`--summary-only` and `--regions-only` support targeted workbook regeneration. `--resume` skips existing regional workbooks and is suitable only for resuming the same unchanged calculation; omit it after changing year, TE, source data or formulas. Run the independent validator after export. It checks catch totals, matching coverage, species and group equations, Jensen differences, every compact comparison row, spatial flag arithmetic and exported Excel cached values.

Regional exports may run in disjoint parallel batches using `--regions-only --shards=3 --shard=0`, then the same command with shard 1 and 2. Every batch is required; each writes its own audit. The default unsharded command still exports every region.

Tests: `python -m pytest tests -q` and `node --test tests/*.mjs`. The package omits runtime libraries, caches and temporary renders; code, inputs, raw archives, polygons and final outputs are retained.

Packaging reruns independent validation and verifies a successful notebook execution record against the current tables, polygons, workbooks and notebook files. Changing these files requires regenerating the notebook. All destination names are checked before publishing; earlier release folders, ZIPs and delivery records are never replaced.

## Sources

- [Sea Around Us area definitions](https://www.seaaroundus.org/sea-around-us-area-parameters-and-definitions/).
- [Sea Around Us catch reconstruction and allocation](https://www.seaaroundus.org/catch-reconstruction-and-allocation-methods/).
- [Download fields and tools](https://www.seaaroundus.org/tools-guide/).
- [Sea Around Us API](https://api.seaaroundus.org/api/v1/).
- Pauly & Christensen (1995), *Primary production required to sustain global fisheries*, Nature 374, 255–257.
- Supplied 2020 supplement MeanTL, frozen in `input/trophic_levels_2020.csv`.

Input URLs, SHA-256 checksums and acquisition metadata are recorded in `input/eez_provenance.json`. `eez_output/deliverable_manifest.json` inventories the delivered outputs. The prior reference workbook was inspected without modification.
