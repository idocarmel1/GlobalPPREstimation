# Projects Integration — Design

Date: 2026-09-05
Status: awaiting user review

## Purpose

Five loosely related sub-projects live side by side in `GlobalPPREstimation` with no
declared relationship, one nested git repository, and roughly 3.2 GB of redundant
archives. This pass unifies them into a single repository with one documented pipeline,
removes a superseded comparison calculation, and produces the per-taxon-per-year catch
data that later integration work depends on.

The end-state pipeline is:

    sweep articles online -> PPRAtlas/archive/regions -> extract model JSON per article
    -> estimate SPPR by several methods -> integrate with catch and NPP data
    -> render on the atlas map

## Scope

In scope this pass: **A** repo hygiene and git unification, **B** Jensen removal,
**D** all-years catch distillation, **F** knowledge graph, **G** pipeline documentation,
**H** package the species-to-group mapper skill.

Deferred to their own spec: **C** the canonical `data/<unit_id>/` spine, and **E** the
per-ecosystem final workbook. Task D is in scope this pass because a clone must carry
usable per-taxon-per-year catch data, and that data exists nowhere else.

## Current state

### Join key

`unit_id`, formatted `LME_003` / `EEZ_711` / `HS_018`, already joins SeaAroundUs and
PPRAtlas. Ecopath model filenames encode it as a numeric prefix (`36_1_South_China_Sea…`
is LME_036; `077HS_1_…` is HS_077). NPP uses `layer` + `region_id` and needs a small
mapping to `unit_id`.

### Coverage

| Asset | Coverage |
| --- | --- |
| Archived source articles | 167 ecosystems |
| NPP values | 84 regions |
| Extracted Ecopath model + SPPR workbook | 16 ecosystems |

The 16 are the pilot: the top 10 ecosystems ranked by the 1995 PPR method, which
expanded to 16 models because several ecosystems carry more than one model. Coverage,
not plumbing, is the binding constraint on the eventual per-ecosystem workbook.

### Catch data

Per-taxon-per-year catch exists **only** inside `raw_data/SAU_downloads/<unit_id>-catch.zip`
(1950-2019; columns include `year`, `scientific_name`, `functional_group`,
`commercial_group`, `tonnes`). Everything derived is narrower:

- `PPRAtlas/inputs/annual_regions.csv` — all 70 years across 366 units, but
  **region-level aggregates only**, no taxon breakdown.
- `global_output/tables/regions/<unit_id>/species.csv` — per taxon, but **2019 only**.

### Git

- Parent `GlobalPPREstimation` -> `github.com/idocarmel1/GlobalPPREstimation`; only
  `README.md` and `.gitignore` are committed.
- `FishEstimationAI/.git` -> `github.com/idocarmel1/PPREstimation`; working tree is
  **dirty with uncommitted deletions** from an on-disk reorganisation that was never
  committed (`SPPR_Methods.md` -> `information/`, notebooks and model JSONs moved).
- No submodules.

## A — Repo hygiene and git unification

### A1. Promote the SeaAroundUs release

`SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04/` is the newer, larger tree: 739 SAU
downloads against 172, an extra `eez_spatial.py`, extra `run_eez_pipeline.py` and
`run_global_te005_pipeline.py`, an `eez_output/`, and newer `download.py`, `ingest.py`,
`pipeline.py`, `provenance.py`, `years.py`. It becomes canonical.

It is **not** a strict superset, so this is a merge and not a move. Two known
exceptions: the release has no `notebooks/` directory (the old top level holds
`global_validation.ipynb`), and the two copies of `global_output/PPR_global_summary.xlsx`
differ.

Method:

1. Walk both trees and write `docs/superpowers/sau-promotion-manifest.csv` classifying
   every path as `only-in-old`, `only-in-release`, `identical`, or `differs`.
2. Carry `only-in-old` paths up into the promoted tree.
3. Resolve each `differs` path explicitly, recording the reason in the manifest. Nothing
   is overwritten on the basis of directory position alone.
4. Move the release contents to `SeaAroundUsExtraction/`, then remove the emptied
   release directory.
5. Re-run the SeaAroundUs test suite.

The old top-level `raw_data/` (405 MB, 172 files) and `input/examples/SAU` (20 MB) are
deleted only after step 1 confirms they are subsets of the release equivalents.

### A2. Delete redundant archives

Each is a compressed copy of a directory that also exists on disk. Before each deletion
the zip's entry list is compared against that directory; deletion proceeds only on a
match.

One exception to note: `Global_history_TE010_2026-09-04.zip` duplicates a directory that
A3 also deletes, so both copies go and that deliverable is removed entirely. That is
intended — the user's reasoning is that its method is the superseded 1995 calculation —
but it means the zip's deletion is not recoverable from the directory, unlike the other
three rows here.

| Path | Size | Duplicates |
| --- | --- | --- |
| `SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_complete.zip` | 1.7 GB | the release directory |
| `PPRAtlas/archive/regions.zip` | 579 MB | `PPRAtlas/archive/regions/` |
| `SeaAroundUsExtraction/Global_history_TE010_2026-09-04.zip` | 209 MB | the Global_history directory |
| `SeaAroundUsExtraction/EEZ_TE010_release_2026-09-04_results.zip` | 16 MB | `eez_output/` |

### A3. Delete superseded outputs

| Path | Size | Reason |
| --- | --- | --- |
| `SeaAroundUsExtraction/Global_history_TE010_2026-09-04/` | 261 MB | implements the 1995 SPPR/PPR method from `PPRCalculator`, which will be recomputed per LME |
| `SeaAroundUsExtraction/PPR_global_te005_results/` | 13 MB | **flagged for confirmation** — same 1995 pipeline at TE=0.05; covered by the same reasoning but not named explicitly by the user |
| `FishEstimationAI/graphify-out/` | 15 MB | superseded by the repo-wide graph built in task F |

### A4. What is explicitly kept

`PPRAtlas/archive/files/` **and** `PPRAtlas/archive/regions/` both stay. They hold the
same PDFs under two layouts and both are live: the built `index.html` references
`archive/files/` 565 times and `archive/regions/` 509 times. Git deduplicates identical
blobs, so committing both costs roughly the size of the union.

`raw_data/SAU_downloads/` stays and is committed: it is the only source of
per-taxon-per-year catch.

### A5. Git unification

1. In `FishEstimationAI/`, stage and commit the pending reorganisation, then push to
   `origin` (`PPREstimation`) so that repository's history is preserved remotely.
2. Remove `FishEstimationAI/.git`. The parent then tracks those files as ordinary
   directories.
3. Per-file history for FishEstimationAI lives on in `PPREstimation`; the monorepo log
   starts fresh for those paths. This is the accepted trade of the chosen approach.

Both pushes are confirmed with the user before they run.

### A6. Fix `.gitignore`

The stock Python `.gitignore` rules are unanchored and reach into project data.
Confirmed: line 14 `downloads/` matches `PPRAtlas/research/downloads/`, which would have
been silently excluded from the first commit.

- Anchor `/lib/`, `/var/`, `/downloads/`, `/share/python-wheels/` to the repository root.
- Add `.venv/`, `.idea/`, `.vscode/`, `.pytest_cache/`, `__pycache__/`.
- Verify with `git check-ignore -v` against a sampled path from every data directory,
  and assert the sample comes back clean.

This must land **before** the first `git add`.

## B — Jensen removal

Two unrelated things share the name. Only one is being removed.

**Removed** — SeaAroundUs computes an *intentional Jensen-error* comparison: a
deliberately wrong aggregation (catch-weighted mean TL, then exponentiate) kept as a
baseline to demonstrate convexity bias.

**Kept, untouched** — `FishEstimationAI` uses a genuine Jensen's-inequality correction
in `monte_carlo_SPPR`; it is core method. `PPRAtlas/research/text/*.txt` contains the
author *Jensen, A.L. (1996)* and the species *Jensen's skate* inside extracted paper
text.

### Code changes

| File | Change |
| --- | --- |
| `src/ppr_pipeline/calculations.py` | drop the 7 emitted columns (`tl_weighted_jensen`, `sppr_jensen`, `ppr_jensen`, `jensen_difference`, `jensen_ratio_correct_to_error`, `jensen_percent_difference`) and the docstring reference |
| `src/ppr_pipeline/validation.py` | remove `_jensen_violations` and the two check rows |
| `src/ppr_pipeline/notebook.py` | remove the narrative section and the underestimation plot |
| `src/ppr_pipeline/pipeline.py` | remove `ppr_commercial_jensen` / `ppr_functional_jensen` from the annual record and the `jensen_comparison.csv` write |

### Data changes

Delete every `jensen_comparison.csv`. Strip the jensen columns from `global_summary.csv`,
per-region `commercial.csv` and `functional.csv`, and `PPRAtlas/inputs/annual_regions.csv`.
Remove the corresponding README and manifest prose.

Existing outputs are edited by column removal rather than regenerated, so the change is
deterministic and diffable.

### Verification

SeaAroundUs tests pass before and after. A column-level diff proves every surviving
value is byte-identical to its pre-change counterpart — only whole columns disappear.

## D — All-years catch distillation

New module `src/ppr_pipeline/annual_catch.py`.

Input: `raw_data/SAU_downloads/<unit_id>-catch.zip`.
Output: `SeaAroundUsExtraction/data/catch_by_taxon_year/<unit_id>.csv.gz`.

This is an interim location scoped to SeaAroundUs. Task C's canonical
`data/<unit_id>/` spine will later absorb or reference these tables; the path is
deliberately not the repository root so the two do not collide before C is designed.

Columns: `unit_id, year, taxon, common_name, functional_group, commercial_group,
catch_tonnes, landings_tonnes, discards_tonnes, reported_tonnes, unreported_tonnes`.

Tonnage is summed over `fishing_entity`, `fishing_sector`, `gear_type` and
`end_use_type`, honouring the `include_catch_types` and `include_reporting_status`
filters already declared in `config/global.yml`. The landings/discards/reported/unreported
splits mirror the conventions of the existing `species.csv` and are retained because
re-running 739 archives later to add a column is expensive.

Sequence:

1. Probe three units of differing size and record actual compressed output size, to
   confirm or correct the 50-150 MB estimate for the full set.
2. Write the module with tests over a small fixture.
3. Assert that a distilled table filtered to 2019 reproduces the taxon-level catch
   totals in the existing `species.csv` for the same unit. This is the correctness gate.
4. Run across all units.

## F — Knowledge graph

Run the `graphify` skill over the cleaned repository, output to a root `graphify-out/`.
Runs after A, B and D so the graph reflects the unified structure rather than the
pre-cleanup mess.

## G — Pipeline documentation

Rewrite the root `README.md` to state the sweep -> extract -> estimate -> integrate ->
map pipeline, name each sub-project's role and its inputs and outputs, and record the
coverage reality (167 archived / 84 NPP / 16 modelled, the latter being the top-10 pilot).
Cross-link the existing per-project READMEs. Note the deferred C and E work so the
`data/<unit_id>/` target is written down rather than remembered.

## H — Package the species-to-group mapper skill

`.skill` files are plain zips containing one top-level directory. Build
`skills/ewe-species-to-group-mapper.skill` from
`skills/artifact-template-ewe-species-to-group-mapper/`:

- Include `SKILL.md`, `assets/`, and the example workbooks renamed from
  `example outputs/` to `examples/` (a space in the path is awkward to reference from
  `SKILL.md`).
- Exclude `artifact-template.json` and `agents/openai.yaml` — artifact-template and
  OpenAI packaging scaffolding that a Claude skill never reads. Both stay in the
  repository source directory for the later GPT adaptation.
- Rename the frontmatter `name` from `artifact-template-ewe-species-to-group-mapper` to
  `ewe-species-to-group-mapper`, and rename the source directory to match. No other file
  in the repository references the old name.
- Update any `SKILL.md` path references affected by the `examples/` rename.

## Carried-forward constraint

For the deferred task E, the per-ecosystem workbook should carry **only the columns the
map visualisation needs**. Recorded here so the constraint survives into that spec.

## Verification and commit

- All three test suites (SeaAroundUs 11 files, PPRAtlas 3, FishEstimationAI 3) run
  before any change to establish a baseline, and again after.
- Every deletion is verified against the artifact it duplicates before it runs.
- `git check-ignore` sampling proves no real data is excluded.
- Commits are grouped by task (A, B, D, F, G, H) rather than squashed.
- Nothing is pushed without explicit confirmation.

## Risks

| Risk | Mitigation |
| --- | --- |
| Promotion loses work unique to the old tree | manifest-first, explicit resolution of every differing path |
| `.gitignore` silently drops data | anchor the stock rules, verify by sampling before the first `add` |
| Jensen removal perturbs surviving values | column-level byte-identity diff |
| Distillation misreads the raw schema | 2019 slice must reproduce existing `species.csv` totals |
| Deleting `PPR_global_te005_results/` was not explicitly authorised | flagged in A3 for confirmation at spec review |
