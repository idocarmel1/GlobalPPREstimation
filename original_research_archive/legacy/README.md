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

Scientific manifests hash exact source and output bytes. The repository's scoped
`.gitattributes` preserve line endings for those files across platforms, including
the frozen study inputs. Do not normalize their line endings independently of a
new, explicitly recorded provenance run. Skills use their own package policy.

## The pipeline

    1. sweep          find published Ecopath models for each ecosystem
    2. archive        store the article, supplements and provenance   -> PPRAtlas/archive/regions/<unit_id>/
    3. extract        pull model parameters out of the paper          -> skills/claude/ecopath-extraction/
    4. taxonomy       record which taxa are in each model group       -> skills/claude/ecopath-paper-to-ppr/
    5. estimate       compute SPPR per group by several methods       -> PPREstimation/
    6. map taxa       assign every catch taxon to a model group       -> skills/claude/ewe-species-to-group-mapper/
    7. integrate      join SPPR with catch and NPP data               -> data/
    8. publish        render the result on one interactive map        -> PPRAtlas/index.html

Steps 3, 4 and 6 all read the same paper, which is why `skills/claude/ecopath-paper-to-ppr/`
combines them into one pass. It is assembled from the other two by
`skills/build_combined_skill.py` rather than forked, so a fix lands in one place.

Ecosystems are keyed by `unit_id` throughout: `LME_003`, `EEZ_711`, `HS_018`.

The same three agent skills are available in [`skills/claude/`](skills/claude/) and
[`skills/codex/`](skills/codex/), with agent-specific entry points and shared domain
resources. See [`skills/README.md`](skills/README.md) for usage and rebuilding.
Current results, verification and remaining scientific limits are in
[`docs/INTEGRATION_COMPLETION.md`](docs/INTEGRATION_COMPLETION.md). The initial
[`takeover review`](docs/CODEX_TAKEOVER.md) and original handoff retain the history.

The [map](PPRAtlas/index.html) and [annual graph](PPRAtlas/trends.html) offer
PPR from **landings** (default), **all catch**, or **discards only**, calculated
separately at taxon resolution. The landings view has an optional, model-specific
discard-routing sensitivity envelope where assessed. All-catch/discards views
have no envelope. Annual NPP, source scope and unidentified-taxon settings remain
independent controls. Source workbooks retain their total-catch calculations;
plotted-data downloads record the selected view.

The map exposes **all 366 ecosystem identities** and opens with the independent
simple trophic-chain method. It uses catch-taxon trophic levels at TE=0.1, with
no article or Ecopath-model requirement. Catch is available for 364 identities;
the two no-catch regions remain unavailable for PPR. The 167-region curated
article archive and ten selected model regions remain separate subsets.
References and their specific uses are recorded in the
[article reference/use log](external/ARTICLE_REFERENCE_USE_LOG.md).

The annual graph also plots **NPP through time** in tonnes carbon per year,
including ecosystems with NPP but no catch or usable Ecopath model. For PPR/NPP,
choose the selected ecosystems' NPP or a fixed **Global atlas NPP** reference.
The latter integrates the dissolved boundary of all 66 LMEs and 18 high-seas
identities and takes the median of the union-wide model totals. Its denominator
stays fixed when numerator regions or PPR methods change. It is a coverage-limited
estimate for that atlas geography; it is not complete world-ocean NPP. Annual
support, gaps and explicit earlier-year proxies appear in the graph and CSV/JSON
downloads. See the [reference method](docs/GLOBAL_ATLAS_NPP_REFERENCE.md).

The [discard-routing study](research/discard_sensitivity_2026_09_10/README.md)
contains the standalone report, reproducible scenario results, source audit and
scientific reporting protocol. Its ranges are sensitivity scenarios, not
confidence intervals or global uncertainty bounds.

## Sub-projects

| Directory | Role | Key inputs | Key outputs |
| --- | --- | --- | --- |
| [`SeaAroundUsExtraction/`](SeaAroundUsExtraction/README.md) | Fishing-catch and spatial-unit extraction from Sea Around Us, plus a first-pass PPR ranking | `raw_data/SAU_downloads/*.zip` | `global_output/`, `eez_output/`, `data/catch_by_taxon_year/` |
| [`PPRAtlas/`](PPRAtlas/README.md) | Curated archive of source articles per ecosystem, and the interactive map | `archive/regions/`, `data/catalog.json` | `index.html`, `archive/index.html` |
| [`PPREstimation/`](PPREstimation/README.md) | The main algorithm: Ecopath model loading, automatic balancing, SPPR estimation by several methods | `real_models/*.json` | `output/` — one workbook per model |
| [`NPPExtraction/`](NPPExtraction/README.md) | Regional and fixed atlas-union annual net primary production, up to five satellite algorithms | Satellite products, SAU boundaries and regional inventory | `output/annual_npp.csv`, coverage and provenance reports |
| `skills/` | Packaged skills: parameter extraction from papers, group taxonomy capture, taxon-to-group mapping | source papers, catch archives | model JSON, `data/<unit>/mapping/*.csv` |
| `data/` | The integration layer — one directory per ecosystem, joined on `unit_id` | everything above | `INDEX.csv`, per-ecosystem and per-model workbooks |

## Coverage

This is the honest state of the work, not a target.

| Asset | Coverage |
| --- | --- |
| Ecosystems in the curated article-archive selection | 167 |
| Displayed ecosystem identities / catch-bearing simple-PPR identities | 366 / 364 |
| Annual regional NPP | All 366 identities × 22 years, 1998–2019: 8,052 ensemble estimates, including two retained legacy 2019 cells |
| Canonical NPP inventory | 25,211 rows, 1950–2019; 17,161 unsupported rows remain blank |
| Fixed global-atlas NPP reference | All 22 years, 1998–2019; one dissolved LME/high-seas union |
| Regions in the legacy 2019 NPP reference | 84; retained separately from the canonical annual extraction |
| Ecosystems with an extracted model | 16 models, spanning 10 ecosystems |
| SPPR workbooks produced for that pilot set (`PPREstimation/output/top10/`) | 16 |

The modelled set is a pilot: the top ten ecosystems by the 1995 PPR ranking, which
yielded more models (16) than ecosystems (10) because several ecosystems have more
than one published model. Archive coverage, annual NPP estimates and extracted
models describe different stages. The 167 archived ecosystems include one without
catch data. The expanded canonical CSV has 5,938 five-model and 2,112 partial-model
rows, with no failed or pending rows. All 11,310 original rows were preserved
field-for-field; HS_018 and LME_064 retain NPP without invented catch. See the
[publication proof](NPPExtraction/output/regional_expansion/publication_verification.json),
[all-identity review](data/regional_npp_publication_review.json) and
[reproduction guide](NPPExtraction/ANNUAL.md). Finite estimates do not imply full
satellite-water coverage. The earlier archived-scope coverage report is historical.

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

The catch inputs and curated source articles are committed, including the raw
Sea Around Us catch archives (366 `*-catch.zip` archives under
`SeaAroundUsExtraction/raw_data/SAU_downloads/`; two of them, `HS_018` and `LME_064`,
are genuinely empty) and the curated article archive (240 files in the
content-addressed store, `PPRAtlas/archive/files/`). Clones are large. NPP source
rasters are downloaded from their public providers by `NPPExtraction` and cached
locally; they are not committed. See its README for a fresh installation and run.

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
- The upstream Excel builders require Codex's bundled `@oai/artifact-tool` runtime,
  which is not a public npm package. It is available in this environment. All **368**
  upstream workbooks have been regenerated and independently checked against the current
  CSVs and group arithmetic: **85 global + 283 EEZ**, with no formula errors.
  `tools/run_workbook_exports.ps1 -Scope global` (or `eez`) resolves that runtime
  without installing repository-local packages. Revalidation uses
  `SeaAroundUsExtraction/tools/verify_global_workbooks.py` and
  `SeaAroundUsExtraction/tools/validate_eez_release.py`.
- Published source coverage and numerical validity remain separate. In particular,
  Thailand's Ecobase 412 payload matches **1980**, despite its inherited `1963` filename;
  the Guinea model is a geographic transfer; several Humboldt configurations fail.
  See the per-model source checks and mapping notes before scientific use.

## `data/` — the integration layer

`data/<unit_id>/` holds one directory per ecosystem, joining catch, geography, articles,
the selected Ecopath model, SPPR results and NPP on `unit_id`. Each catch-bearing
ecosystem has a workbook with catch, simple PPR, NPP, model SPPR scopes and recycling diagnostics,
built by `tools/build_ecosystem_data.py`. Model identities remain explicit on every scoped row.
Start at `data/INDEX.csv`, which is the workbook coverage matrix. The two no-catch
identities remain available in NPP-only atlas views. See `data/README.md`.

Bulk inputs are referenced rather than copied.

The workbook computes PPR independently and its 2019 total reproduces the pipeline's
`ppr_species` exactly, then extends across all seventy years. Annual NPP is matched
by ecosystem and year; missing years stay blank. The map and graph offer a labeled
earliest-year proxy for earlier years. Central and model workbooks expose final
taxon/group assignments with the exact numerical weights used to calculate PPR.

## Not yet built

- **Further source verification.** Seven pilot models now have reviewed taxonomy,
  member evidence and model profiles; the older mappings retain documented evidence
  limits. The combined skill preserves source membership during extraction.
- **Ecopath PPR beyond the pilot.** The chain is built and runs, but only for ecosystems
  with a usable model and a mapping. `data/model_selection.xlsx` records the ceiling.
- **Sweeping new articles** into `PPRAtlas/archive/regions/` and extracting models from
  them, which is what would lift coverage above the current ten ecosystems.
The atlas shows independent simple-chain results across catch-bearing ecosystems,
verified network results, source-scope switching, method ratios on common catch,
and GE/TE recycling diagnostics. Model-based coloring retains the ten selected
pilot ecosystems. The new-paper validation remains isolated; see
[`docs/NEW_PAPER_VALIDATION.md`](docs/NEW_PAPER_VALIDATION.md).

Designed in `docs/superpowers/specs/`.
