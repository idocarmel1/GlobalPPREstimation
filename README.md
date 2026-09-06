# GlobalPPREstimation

Estimating the primary production required (PPR) to sustain global marine fisheries,
ecosystem by ecosystem.

## Cloning on Windows

`PPRAtlas/archive` contains paths beyond Windows' 260-character limit. Before cloning
or checking out this repository, run:

```
git config core.longpaths true
```

Without it, `git clone` / `git checkout` fails with `Filename too long` partway through
the archive.

## The pipeline

    1. sweep          find published Ecopath models for each ecosystem
    2. archive        store the article, supplements and provenance   -> PPRAtlas/archive/regions/<unit_id>/
    3. extract        pull model parameters out of the paper          -> skills/ecopath-extraction-*.skill
    4. estimate       compute SPPR per group by several methods       -> PPREstimation/
    5. integrate      join SPPR with catch and NPP data               -> (in design)
    6. map            render the result on one interactive map        -> PPRAtlas/index.html

Ecosystems are keyed by `unit_id` throughout: `LME_003`, `EEZ_711`, `HS_018`.

## Sub-projects

| Directory | Role | Key inputs | Key outputs |
| --- | --- | --- | --- |
| [`SeaAroundUsExtraction/`](SeaAroundUsExtraction/README.md) | Fishing-catch and spatial-unit extraction from Sea Around Us, plus a first-pass PPR ranking | `raw_data/SAU_downloads/*.zip` | `global_output/`, `eez_output/`, `data/catch_by_taxon_year/` |
| [`PPRAtlas/`](PPRAtlas/README.md) | Curated archive of source articles per ecosystem, and the interactive map | `archive/regions/`, `data/catalog.json` | `index.html`, `archive/index.html` |
| [`PPREstimation/`](PPREstimation/README.md) | The main algorithm: Ecopath model loading, automatic balancing, SPPR estimation by several methods | `real_models/*.json` | `output/` — one workbook per model |
| `NPPExtraction/` | Net primary production per region, five satellite models | — | `NPP_2019_filled_SAU_regions.csv` |
| `skills/` | Packaged skills: parameter extraction from papers, taxon-to-group mapping | source papers, catch workbooks | model JSON, mapping workbooks |

## Coverage

This is the honest state of the work, not a target.

| Asset | Coverage |
| --- | --- |
| Ecosystems with an archived source article (`PPRAtlas/archive/regions/`) | 167 |
| Regions with an NPP value | 84 |
| Ecosystems with an extracted model | 16 models, spanning 10 ecosystems |
| SPPR workbooks produced for that pilot set (`PPREstimation/output/top10/`) | 16 |

The modelled set is a pilot: the top ten ecosystems by the 1995 PPR ranking, which
yielded more models (16) than ecosystems (10) because several ecosystems have more
than one published model. 167 archived articles, 84 NPP values and 16 extracted
models are three different, mostly non-overlapping counts — do not read this as
"16 of 167 done."

## How PPR is calculated, and the two different meanings of "Jensen"

Two calculations in this repository share a name and are easy to confuse.

**SeaAroundUsExtraction — a first-pass estimate.** Specific PPR is `(1/TE)^(TL-1)`,
which at the configured `TE = 0.1` is `10^(TL-1)`. It is applied at three levels:

- **per taxon**, using that taxon's own trophic level — the unbiased figure, in
  `species.csv`.
- **per commercial group** and **per functional group**, using the group's
  catch-weighted mean trophic level, in `commercial.csv` and `functional.csv`.

The group figures are **deliberately Jensen-affected**. Because `10^(TL-1)` is convex,
exponentiating a mean trophic level understates the sum of the individual taxa
whenever a group spans more than one level. That gap is kept on purpose: it measures
what is lost by moving from taxa to groups, and an Ecopath model cannot show it
because Ecopath has no taxon level. The corrected value is not stored — it is exactly
the taxon-`ppr` sum within the group, recoverable with a `groupby`. The relationship
is enforced by a validation check named `group_ppr_within_convexity_bound`. Measured
across the current (migrated) outputs, the group aggregation understates
taxon-summed PPR by **22.93%** for commercial groups and **16.48%** for functional
groups, globally.

**PPREstimation — the real method.** `monte_carlo_SPPR` applies a genuine
**Jensen's-inequality correction**, resampling transfer efficiency and averaging,
because `SPPR` is convex in `1/TE` and solving once at the mean underestimates the
expectation. This is unrelated to the SeaAroundUs comparison above and is documented
in [`PPREstimation/information/SPPR_Methods.md`](PPREstimation/information/SPPR_Methods.md).

## Data

Everything needed to reproduce the analysis is committed, including the raw
Sea Around Us catch archives (366 `*-catch.zip` archives under
`SeaAroundUsExtraction/raw_data/SAU_downloads/`; two of them, `HS_018` and `LME_064`,
are genuinely empty) and the curated article archive (240 files in the
content-addressed store, `PPRAtlas/archive/files/`). Clones are large.

`SeaAroundUsExtraction/data/catch_by_taxon_year/<unit_id>.csv.gz` holds catch per
taxon per year, 1950–2019 — 2,098,040 rows across 364 files, 65.6 MB. Every other
processed table covers a single analysis year.

## Known limitations

- **`PPREstimation`'s test suite has 1 failure and 18 errors.** The 18 are
  `FileNotFoundError`s because their fixture model lives in
  `real_models/new_EwE_jsons/`, a directory the owner deliberately removed; the 1 is
  a pre-existing method-count assertion (the registry now holds 20 methods, the test
  asserts 19). Both pre-date this integration. See
  [`PPREstimation/README.md` — "Known test failures"](PPREstimation/README.md) for
  detail; it is not duplicated here.
- **The Excel workbook builders cannot currently be run by anyone.** `tools/build_workbooks.mjs`
  and `tools/eez_workbook.mjs` import `@oai/artifact-tool`, a package that is **not on the
  public npm registry** (404) and is not vendored here — there is no `package.json` anywhere
  in the repository. Node itself is installed and the other `.mjs` tooling works, so this is
  a missing dependency, not a missing runtime.

  Consequences: `regional_calculations/*.xlsx` carry stale headers from before the column
  schema changed and cannot be rebuilt; `validate_eez_release.py` therefore passes only with
  `--skip-workbooks`; and `tests/test_eez_workbook.mjs` cannot execute.

  What *is* verified: all eight `.mjs` files pass `node --check`, and
  `tests/test_scope_args.mjs` and `tests/test_workbook_metadata.mjs` both run and pass (2/2
  each). The column-letter corrections inside `eez_workbook.mjs` — made when the group schema
  shrank from 15 columns to 5 and the summary from 17 to 15 — are verified by analysis against
  the real schemas, but **not by execution**. Anyone who can supply `@oai/artifact-tool`, or
  port those two files onto a public spreadsheet library, closes this.

## Not yet built

- **The per-ecosystem data spine** — one directory per ecosystem gathering catch,
  geography, articles, the selected model, SPPR results and NPP.
- **The per-ecosystem workbook** — a single lean spreadsheet per ecosystem: catch per
  taxon per year, taxon SPPR by method, PPR, NPP, and a PPR/NPP summary.

Both are designed in `docs/superpowers/specs/`. Output locations named above are
staging locations until that spine exists.
