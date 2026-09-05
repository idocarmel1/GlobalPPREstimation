# Projects Integration — Design

Date: 2026-09-05
Status: revision 2, awaiting user review

## Purpose

Five loosely related sub-projects live side by side in `GlobalPPREstimation` with no
declared relationship, one nested git repository, and roughly 3.2 GB of redundant
archives. This pass unifies them into a single repository with one documented pipeline,
simplifies the SeaAroundUs PPR calculation down to what is actually used, and produces
the per-taxon-per-year catch data that later integration work depends on.

The end-state pipeline is:

    sweep articles online -> PPRAtlas/archive/regions -> extract model JSON per article
    -> estimate SPPR by several methods -> integrate with catch and NPP data
    -> render on the atlas map

## Scope

In scope this pass: **A** repo hygiene and git unification, **B** SeaAroundUs
calculation simplification, **D** all-years catch distillation, **F** knowledge graph,
**G** pipeline documentation, **H** package the species-to-group mapper skill.

Deferred to their own spec: **C** the canonical `data/<unit_id>/` spine, and **E** the
per-ecosystem final workbook. Task D is in scope this pass because a clone must carry
usable per-taxon-per-year catch data, and that data exists nowhere else.

Work happens directly on `main`. The repository is still before its real initial commit,
so no branch is used.

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

### Trophic-level coverage

Measured across every group table in the current global output: **2268 group rows in 168
files, none below 100 % TL coverage, zero tonnes of missing TL.** This is what licenses
dropping the coverage columns in task B. It is measured on the 2019 analysis year only,
so task B replaces those columns with an assertion rather than an assumption.

### Git

- Parent `GlobalPPREstimation` -> `github.com/idocarmel1/GlobalPPREstimation`; `main`
  holds the initial commit plus this spec.
- `FishEstimationAI/.git` -> `github.com/idocarmel1/PPREstimation`; working tree is
  dirty with uncommitted deletions from an on-disk reorganisation.
- **Two independent clones of the same `PPREstimation` remote exist outside this
  repository**, at `../קוד/FishEstimation/` and `../קוד/FishEstimationAI/`. Neither is
  touched by this work. This is why the nested `.git` here can simply be deleted: its
  history is preserved in those clones and on GitHub, and nothing needs pushing.
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
intended — its method is the superseded 1995 calculation — but it means the zip's
deletion is not recoverable from the directory, unlike the other three rows here.

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

### A5. Rename FishEstimationAI to PPREstimation

`FishEstimationAI/` becomes `PPREstimation/`, matching the name of the repository it came
from. References to update: `CLAUDE.md`, `README.md`, `information/USER_GUIDE.md`,
`notebooks/hackaton040926.ipynb`, `.claude/settings.local.json`. The `.idea/` files that
mention it are IDE state and are moved to `.gitignore` rather than edited.

Compiled `__pycache__` matches are ignored — they are regenerated artifacts.

### A6. Collapse the nested git repository

Delete `FishEstimationAI/.git` (after the rename, `PPREstimation/.git`). The parent then
tracks those files as ordinary directories.

**No push to `PPREstimation` is performed and no commit is made inside it.** Its history
is already preserved on GitHub and in the two independent clones at
`../קוד/FishEstimation/` and `../קוד/FishEstimationAI/`, which this work does not touch.
Per-file history for these paths starts fresh in the monorepo, which is accepted.

Before deleting, `git -C` status and remote of the nested repo are recorded into the
commit message so the provenance is written down.

### A7. Fix `.gitignore`

The stock Python `.gitignore` rules are unanchored and reach into project data.
Confirmed: line 14 `downloads/` matches `PPRAtlas/research/downloads/`, which would have
been silently excluded from the first commit.

- Anchor `/lib/`, `/var/`, `/downloads/`, `/share/python-wheels/` to the repository root.
- Add `.venv/`, `.idea/`, `.vscode/`, `.pytest_cache/`, `__pycache__/`.
- Fold in the rules from the nested `FishEstimationAI/.gitignore` that still apply,
  rescoped to `PPREstimation/`: notably `output/*` with `!output/top10/`, which currently
  excludes `output/Ecobase_models/` and `output/collected_PPRs.xlsx`. **Flagged for
  confirmation** — carrying this rule forward means those results do not reach a cloner,
  which may conflict with the "a cloner gets all relevant data" requirement.
- Verify with `git check-ignore -v` against a sampled path from every data directory,
  and assert the sample comes back clean.

This must land **before** the first `git add`.

## B — Simplify the SeaAroundUs PPR calculation

Two unrelated things share the name "Jensen". Only one is affected.

**Untouched** — `PPREstimation` (formerly `FishEstimationAI`) is the main algorithm
folder. Its Jensen's-inequality correction in `monte_carlo_SPPR` and every related
effect stay exactly as they are. Also untouched: `PPRAtlas/research/text/*.txt`, which
contains the author *Jensen, A.L. (1996)* and the species *Jensen's skate* inside
extracted paper text.

**Changed** — SeaAroundUs currently computes each group two ways and compares them. The
comparison is dropped and only the naive aggregation is kept.

### What is kept and why

`calculate_sppr(tl, te)` is `(1/te) ** (tl - 1)`; at the configured `te = 0.1` this is
exactly `10 ** (TL - 1)`. It is retained unchanged and applied at three levels:

| Level | TL used | Output |
| --- | --- | --- |
| taxon | the taxon's own TL | `sppr`, `ppr` |
| commercial group | catch-weighted mean TL of the group | `tl_weighted`, `sppr`, `ppr` |
| functional group | catch-weighted mean TL of the group | `tl_weighted`, `sppr`, `ppr` |

The group figures are deliberately the Jensen-affected ones. Their purpose is to expose
the bias introduced by moving from taxa to groups — an effect `PPRCalculator` cannot show
on its own, because Ecopath models are group-based and have no taxon level. The
correctly-aggregated value is not stored because it is exactly the sum of taxon `ppr`
within the group, recoverable from the taxon table with a `groupby` whenever the
comparison is wanted.

### Column changes in `aggregate_groups`

Of the 15 columns currently emitted, 5 are kept and 10 removed.

| Column | Fate |
| --- | --- |
| `<group>` | kept |
| `catch_tonnes_matched` | kept — the multiplicand in `ppr = catch_matched * sppr` |
| `tl_weighted_jensen` | kept, **renamed** `tl_weighted` |
| `sppr_jensen` | kept, **renamed** `sppr` |
| `ppr_jensen` | kept, **renamed** `ppr` |
| `sppr_correct`, `ppr_correct` | removed — the corrected aggregation |
| `jensen_difference`, `jensen_ratio_correct_to_error`, `jensen_percent_difference` | removed — comparison machinery |
| `taxon_count_total`, `taxon_count_matched` | removed — QA metadata |
| `catch_tonnes_total`, `catch_tonnes_missing_tl`, `catch_coverage_fraction` | removed — see the assertion below |

The `_jensen` suffix is dropped because the file name already states the grouping. At
summary level the columns become `ppr_commercial` and `ppr_functional`, with
`ppr_species` unchanged as the taxon-level total. The naming convention records that
these group values are not the corrected calculation; the documentation in task G states
it explicitly.

### The coverage assertion

Dropping `catch_coverage_fraction` is safe only while TL coverage is complete. Verified
today at 100 % across all 2268 group rows, but only for the 2019 analysis year, and
task D extends to 1950-2019 where older taxa may lack TL matches.

So the five removed QA columns are replaced by one check in `validation.py`:
`tl_coverage_complete`, which fails loudly if any group in any processed year carries
catch with no TL. This converts a silent-underestimate risk into a hard error, and costs
one row rather than five columns.

### Other code changes

| File | Change |
| --- | --- |
| `src/ppr_pipeline/validation.py` | remove `_jensen_violations` and its two check rows; add `tl_coverage_complete` |
| `src/ppr_pipeline/notebook.py` | remove the correct-versus-Jensen narrative section and the underestimation plot |
| `src/ppr_pipeline/pipeline.py` | drop `ppr_commercial_correct` / `ppr_functional_correct`; rename the `_jensen` pair to `ppr_commercial` / `ppr_functional`; stop writing `jensen_comparison.csv` |

`jensen_comparison.csv` is deleted rather than trimmed: once the corrected columns are
gone it is a duplicate of `commercial.csv` plus `functional.csv`.

### Data changes

Apply the same column removal and renaming to the existing outputs so they match the
code: `global_summary.csv`, per-region `commercial.csv` and `functional.csv`,
`PPRAtlas/inputs/annual_regions.csv`, and the corresponding README and manifest prose.
Outputs are edited by column removal rather than regenerated, so the change is
deterministic and diffable.

### Verification

SeaAroundUs tests pass before and after. A column-level diff proves every surviving
value is byte-identical to its pre-change counterpart — only whole columns disappear or
change name. Tests covering the removed columns are rewritten, not deleted, so the
retained behaviour stays covered.

## D — All-years catch distillation

New module `src/ppr_pipeline/annual_catch.py`.

Input: `raw_data/SAU_downloads/<unit_id>-catch.zip`.
Output: `SeaAroundUsExtraction/data/catch_by_taxon_year/<unit_id>.csv.gz`.

This is an interim location scoped to SeaAroundUs. Task C's canonical `data/<unit_id>/`
spine will later absorb or reference these tables; the path is deliberately not the
repository root so the two do not collide before C is designed.

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
coverage reality (167 archived / 84 NPP / 16 modelled, the latter being the top-10
pilot). State explicitly that SeaAroundUs group-level PPR is the Jensen-affected
aggregation and why it is kept that way. Cross-link the existing per-project READMEs.
Note the deferred C and E work so the `data/<unit_id>/` target is written down rather
than remembered.

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

For the deferred task E, the per-ecosystem workbook should be lean enough for a human
reader: only the columns the map visualisation needs, and few sheets rather than many.
Recorded here so the constraint survives into that spec.

## Verification and commit

- All three test suites (SeaAroundUs 11 files, PPRAtlas 3, PPREstimation 3) run before
  any change to establish a baseline, and again after.
- Every deletion is verified against the artifact it duplicates before it runs.
- `git check-ignore` sampling proves no real data is excluded.
- Commits are grouped by task (A, B, D, F, G, H) rather than squashed, on `main`.
- The push is confirmed with the user before it runs.

## Risks

| Risk | Mitigation |
| --- | --- |
| Promotion loses work unique to the old tree | manifest-first, explicit resolution of every differing path |
| `.gitignore` silently drops data | anchor the stock rules, verify by sampling before the first `add` |
| Column removal perturbs surviving values | column-level byte-identity diff |
| TL coverage is incomplete in historical years | `tl_coverage_complete` assertion fails loudly instead of underestimating |
| Distillation misreads the raw schema | 2019 slice must reproduce existing `species.csv` totals |
| Deleting `PPR_global_te005_results/` was not explicitly authorised | flagged in A3 for confirmation at spec review |
| Carrying `output/*` ignore forward hides Ecobase results from cloners | flagged in A7 for confirmation at spec review |
