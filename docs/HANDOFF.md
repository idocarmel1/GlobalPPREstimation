# GlobalPPREstimation — handoff

Written for someone, human or AI, picking this project up with no prior context. It
assumes you have the repository and nothing else. Read it start to finish once; after
that, `data/README.md` and the skill files are the working references.

Last updated: 2026-09-07.

---

## 1. What the project is trying to answer

**How much primary production does the world's marine fishing actually consume, and what
fraction of the ocean's primary production is that?**

The quantity is **PPR** — primary production required. For a catch of one tonne at trophic
level `TL`, the primary production needed to support it is

```
SPPR = (1 / TE) ^ (TL - 1)          TE = transfer efficiency, conventionally 0.1
PPR  = catch_tonnes x SPPR
```

`SPPR` is *specific* PPR — per tonne of catch. At `TE = 0.1` this is `10^(TL-1)`: a tonne
of TL-4 tuna needs 1,000 tonnes of primary production; a tonne of TL-2 sardine needs 10.

That simple formula is the **1995 trophic-chain method** (Pauly & Christensen). It assumes
a single unbranched food chain at a fixed transfer efficiency. Real ecosystems branch,
recycle detritus, and have different efficiencies per compartment. **Ecopath with Ecosim
(EwE)** models a whole ecosystem as a mass-balanced network, and from such a model you can
compute SPPR by around twenty different methods that follow the real diet matrix instead
of assuming a chain.

So the project computes PPR two ways and compares them:

- **the simple method**, per taxon, which needs no model and therefore runs for every
  ecosystem with catch data (364 of them);
- **the network methods**, per Ecopath functional group, which need a published, balanced,
  extracted model of that ecosystem (currently five have one that works end to end).

The methods are **not alternatives to be averaged**. The spread between them is the
result.

### Jensen's inequality — why one comparison keeps recurring

`SPPR` is convex in `TL`. So aggregating catch into a group, taking a catch-weighted mean
trophic level, and *then* exponentiating always gives a smaller answer than exponentiating
per taxon and summing. The gap is 16–28 % in the ecosystems measured here.

This matters because much published work computes PPR from aggregated groups. The project
therefore keeps a deliberately "wrong" aggregated calculation alongside the correct
per-taxon one, to size the effect. In `data/<unit>/models/<model>.xlsx`, sheet
`PPR by method`, two grey rows do exactly this and are labelled as such. **Do not remove
them and do not treat them as estimates.**

Separately, `PPREstimation/` contains a genuine Monte-Carlo Jensen *correction* inside the
SPPR methods themselves. That is different work and must not be confused with the
comparison rows. The project owner has said explicitly: **never change Jensen-related
behaviour inside `PPREstimation/`.**

---

## 2. Repository layout

Five sub-projects plus an integration layer. Everything is keyed on **`unit_id`**:
`LME_003`, `EEZ_711`, `HS_018` (Large Marine Ecosystem, Exclusive Economic Zone, High
Seas area).

| directory | role |
| --- | --- |
| `SeaAroundUsExtraction/` | catch data per taxon per year per unit, from Sea Around Us, plus a first-pass PPR ranking |
| `PPRAtlas/` | curated archive of source articles per ecosystem, and an interactive map (`index.html`) |
| `PPREstimation/` | **the main algorithm.** Loads Ecopath models, balances them, computes SPPR by ~20 methods |
| `NPPExtraction/` | net primary production per region from five satellite models (one CSV) |
| `skills/` | packaged agent skills: extract models from papers, capture group taxonomy, map catch taxa to groups |
| `data/` | **the integration layer.** One directory per ecosystem, joining everything on `unit_id` |
| `tools/` | the scripts that build and check `data/` |
| `tests/` | tests for the mapping arithmetic (`pytest tests`) |
| `docs/` | this file, plus design specs and plans under `docs/superpowers/` |

`PPREstimation` was formerly called `FishEstimationAI`. Two clones of its **own** git
repository live outside this one at `../קוד/FishEstimation/` and `../קוד/FishEstimationAI/`
and must be left intact.

**Windows note.** The checkout path contains Hebrew characters and some paths are long.
Run `git config core.longpaths true` before cloning or checking out, or git fails partway
with `Filename too long`.

---

## 3. The pipeline

```
 1. sweep      find published Ecopath models for each ecosystem        (manual / online)
 2. archive    store article + supplements + provenance                PPRAtlas/archive/regions/<unit_id>/
 3. extract    pull model parameters out of the paper                  skills/ecopath-extraction/
 4. taxonomy   record which taxa are in each functional group          skills/ecopath-paper-to-ppr/  <-- the seam
 5. estimate   compute SPPR per group by ~20 methods                   tools/run_sppr.py
 6. map taxa   assign every catch taxon to a model group               skills/ewe-species-to-group-mapper/
 7. integrate  join SPPR with catch and NPP                            tools/build_model_workbook.py
 8. publish    render on the interactive map                           PPRAtlas/index.html  (not yet wired to network results)
```

Steps 3, 4 and 6 all read the same paper. `skills/ecopath-paper-to-ppr/` combines them
into one pass; it is **assembled** from the other two skills by
`skills/build_combined_skill.py`, never edited directly.

---

## 4. The data model

### Catch

`SeaAroundUsExtraction/data/catch_by_taxon_year/<unit_id>.csv.gz`

Columns: `unit_id, year, taxon, common_name, functional_group, commercial_group,
catch_tonnes, landings_tonnes, discards_tonnes, reported_tonnes, unreported_tonnes`.
1950–2019, roughly 150–430 taxa per LME.

`functional_group` is Sea Around Us's **habitat-and-size** class (`Medium demersals
(30 - 89 cm)`, `Small pelagics (<30 cm)`, `Cephalopods`, `Shrimps`, …). It is present on
*every* row including `Marine fishes not identified`, and it is the strongest single
signal available for mapping coarse catch labels. `commercial_group` is coarser
(`Perch-likes`, `Herring-likes`, `Other fishes & inverts`, …) and useful mainly for
exclusion.

Trophic levels come from `SeaAroundUsExtraction/global_output/tables/regions/<unit>/species.csv`.

### Ecopath models

Two forms, and the difference matters:

- **Extracted from a paper** — a directory of eight EwE import CSVs plus `Taxonomy.xlsx`,
  from which `database_json.py` builds the database JSON. Produced by
  `skills/ecopath-extraction/`.
- **From Ecobase** — a finished database JSON with no extraction directory. Several of the
  pilot models are these (Gulf of Thailand 412, Guinea 646/726, Okhotsk).

Either way the model ends up as `PPREstimation/real_models/global_cover_jsons/<stem>.json`,
a `{"group": [ ... ]}` array. Each group carries `group_name`, `group_seq`, `biomass`,
`pb`, `qb`, `ee`, `pp`, diet, and **`taxon_descr`** — which taxa are in the group.

Model stems encode the unit: `35_412_Gulf_of_Thailande_(1963)` is LME 35; `077HS_1_...`
is HS_077. `mapping_io.unit_from_model_filename()` does the parsing.

### SPPR workbooks

`PPREstimation/output/top10/<stem>.xlsx`, one per model, sheets:

- `groups_df` — **the authoritative group list**: `seq, group_name, group_type, tl, ge,
  ee, catch, biomass, …, taxon_descr`. Every downstream join is on `group_name`
  *character for character*.
- `sppr_all`, `sppr_inner`, `sppr_PP` — group × method SPPR under three basal-source
  scopes. `sppr_all` is the one used.
- `model_health` — per-configuration balance diagnostics. **Read this before trusting a
  model.**
- `run_notes` — what each method is and whether it succeeded.

`NaN` in these sheets means *not available*, never zero.

### The integration layer

```
data/
  INDEX.csv                     one row per ecosystem — read this first
  model_selection.xlsx          which article and model each ecosystem uses, and the `usable` verdict
  <unit_id>/
    <unit_id>.xlsx              model-independent workbook (Summary, Catch, SPPR, PPR, NPP)
    metadata.json               identity, geography, coverage, relative paths to bulk inputs
    npp.json                    net primary production, 2019
    mapping/                    the taxon-to-group mapping, as CSV — see below
    models/<model_stem>.xlsx    one workbook per Ecopath model
```

Bulk inputs are **referenced, not copied**. The whole spine is about 45 MB.

`INDEX.csv` distinguishes three things that are easy to conflate: `ecopath_models`
(extracted), `models_mapped` (has a taxon-to-group mapping), `model_workbooks` (has PPR).
Currently **10 / 6 / 5**.

### The mapping files

`data/<unit>/mapping/`:

| file | what it is |
| --- | --- |
| `WORK_ORDER.md` | generated brief: models, `usable` verdicts, exact group lists, every taxon ranked by tonnage |
| `<stem>.csv` | **the mapping** — one row per catch taxon |
| `<stem>.members.csv` | the paper's own species-to-group table, transcribed |
| `<stem>.taxonomy.csv` | stage-2 output: `seq, group_name, taxon_descr`, one row per group |
| `<stem>.groups.csv` | the group dictionary — grouping basis, members, provenance |
| `<stem>.notes.md` | provenance, area, judgement calls, limitations |
| `<stem>.resolved.csv` | generated: the apportionment weights actually used |

The mapping CSV columns are `taxon, common_name, functional_group, commercial_group,
group, weights, confidence, evidence, explanation`. Full contract in
`skills/ewe-species-to-group-mapper/references/output-format.md`.

**`group` may name one group, several separated by `|`, or `Unresolved`.**

---

## 5. The central problem, and how it was solved

Sea Around Us reports a large share of catch under labels no Ecopath paper will ever name:
`Marine fishes not identified`, `Perciformes`, `Decapoda`, `Sciaenidae`,
`Miscellaneous marine crustaceans`. They sit above genus and span several model groups.

The first generation of mappings marked all of these `Unresolved`, and stalled at **78 %
of catch tonnage** in all three ecosystems tried. `Marine fishes not identified` alone was
12–19 % of an LME's catch. Fourteen decisions were throwing away a fifth of the answer.

### Apportionment

A taxon that genuinely spans groups is now **split across them**, not discarded:

```
group    = Clupeids | Anchovies | Small Benthopelagics
weights  =                          (blank -> weight by observed catch composition)
evidence = composite_split
```

The mapper names the candidate set; `tools/build_model_workbook.py` computes the weights
from the ecosystem's own identified catch, falling back through model catch → model
biomass → equal shares and **recording which basis it actually used**. Weights do not vary
by year, so each taxon keeps one SPPR per method and `PPR = catch(taxon, year) x
SPPR(taxon, method)` stays exact.

`Unresolved` survives and still means *outside the model* — a billfish in a coastal-shelf
model with no oceanic compartment — not *hard to decide*.

### Measurement

**Coverage is measured by tonnage, not by taxon count**, and the two diverge sharply. One
mapping had 44 % of taxa unresolved and 90 % of tonnage resolved, because the unresolved
tail was rarities. PPR is a tonnage quantity.

`validate_mapping.py` reports coverage by confidence tier and rejects anything that would
make the PPR wrong. Target is 95 % of tonnage.

### The member list — the biggest lever

Two of the three papers re-examined contained a **species-to-group table nobody had read**:

- Arabian Sea: CMFRI Bulletin 51, "Components of Ecological Groupings", 129 species
  numbered under 24 groups. The first mapping had used a one-line summary from a different
  paper. Checking against the real table caught **five wrong assignments** carrying 2.3 %
  of the catch — every one the same failure, the Sea Around Us size class read in
  preference to the model's own placement. Two were invisible without the printed
  nomenclature: `Formio niger` is the same fish as `Parastromateus niger`.
- Bay of Bengal: Appendix A1.1 maps catch names directly to groups.
- East China Sea: Supplementary Table S1, a `.docx` data sheet, not a table in the PDF.

So `<stem>.members.csv` is now first-class, and **`validate_mapping.py` treats a row
contradicting it as an error**, not a difference of opinion. It matches on both the
printed and the accepted name, and for a genus-level catch row against species in the
table it checks the union of their groups.

`taxon_descr` is empty for every model extracted so far, and the `taxons_included` field
in the Ecobase dump (`PPREstimation/real_models/SpeciesGroups.json`) is empty for **all
5,553 groups in it**. The gap is systematic. That is what stage 4 of the combined skill
exists to fix going forward.

---

## 6. Model archetypes — read the group list before mapping anything

Ecopath modellers do not agree on what a group is, and the axis decides every later
decision. `skills/ewe-species-to-group-mapper/references/model-structures.md` has the full
treatment. In brief:

- **Taxonomic** (`Cephalopods`, `Sharks`, `Clupeids`) — easiest; containment decides.
- **Size and habitat** (`Large/Med/Small Benthic Carnivores`) — Arabian Sea. The Sea Around
  Us `functional_group` column is directly commensurable here and is the strongest signal.
- **Feeding guild** (`Planktivores`, `Benthivores/piscivores`, `Omnivores`) — East China
  Sea. Hardest: a family name says nothing about diet, so the paper's species list is not
  optional. **Never select a guild from trophic level alone.**
- **Spatially stratified** (`1 L pisc`, `2 L pisc`, `3 L pisc`) — Bay of Bengal. **This is
  the trap.** The first mapping put every stratified taxon into stratum 2 with nothing
  saying so, silently attributing a whole LME's catch to one sub-area. Reading the paper
  established that region 1 is the *Maldives shelf, outside LME 34 entirely*, and regions
  2 and 3 are both inside — so the default was wrong in both directions.
- **Life stage** (`Cod juvenile` / `Cod adult`) — catch is not split by stage, so a taxon
  is a composite over stages.

Groups that never take catch: `Detritus`, `diet_import`, and every `PP` group. The
validator rejects catch on them. Zooplankton and meiobenthos take catch almost nowhere.

---

## 7. How to run each stage

```bash
# 0. environment
pip install openpyxl pypdf shapely pyproj olefile pandas
pytest tests SeaAroundUsExtraction/tests        # 40 + 185 tests, all should pass

# 3-4. extract a model from a paper, and capture its group taxonomy
#      -> use the skill; it is a workflow, not a script

# 5. regenerate SPPR for named models  (~13 s per model)
python tools/run_sppr.py --models "35_412_Gulf_of_Thailande_(1963)" --out /tmp/sppr --compare
python tools/run_sppr.py --models "<stem>" --in-place        # replace the committed workbook

# apply a stage-2 taxonomy into a model JSON so groups_df carries it
python tools/apply_taxonomy.py "data/LME_035/mapping/<stem>.taxonomy.csv" --check
python tools/apply_taxonomy.py "data/LME_035/mapping/<stem>.taxonomy.csv"

# 6. map catch taxa to groups
python skills/ewe-species-to-group-mapper/scripts/prepare_mapping.py LME_047
#    ... the agent fills in data/LME_047/mapping/<stem>.csv ...
python skills/ewe-species-to-group-mapper/scripts/validate_mapping.py LME_047

# 7. build and check the outputs
python tools/build_ecosystem_data.py                      # metadata + INDEX for all 364
python tools/build_ecosystem_data.py --units LME_047 --force
python tools/build_model_workbook.py --units LME_047
python tools/verify_model_workbook.py                     # checks the Excel formulas too

# comparing two mappings of the same model (e.g. skill A/B tests)
python tools/make_eval_root.py LME_028 /tmp/evalA
python tools/compare_mappings.py LME_028 "28_646_Guinea_(1998)" --other /tmp/evalA
```

`skills/build_combined_skill.py` regenerates `ecopath-paper-to-ppr` and repackages all
three `.skill` zips. `--check` fails if the assembled tree has drifted from its sources.

---

## 8. Traps — things that will bite you

**`PPREstimation/create_PPRS_excel.py` must never be run from a shell.** Its `__main__`
block has `raise SystemExit(main())` commented out and hardcodes a full sixteen-model
regeneration into `PPREstimation/output/top10`. *Any* invocation with *any* arguments —
including `--help` — silently overwrites the committed workbooks. This cost two accidental
overwrites during this work. Use `tools/run_sppr.py`, which calls `run_directory()`
directly. Fixing the `__main__` block would be a kindness but has not been done, because
`PPREstimation/` is the owner's main algorithm folder.

**Regeneration is deterministic except for Monte Carlo.** Re-running SPPR reproduces the
committed workbook exactly for 18 of 20 methods; `MC_new_GE` and `MC_new_TE_EEfix` differ
by a few per cent because they draw samples.

**Some methods diverge, and the failures look like numbers.** Four Sea of Okhotsk groups
come out with negative SPPR under the `TE` solver variants, one at −2.7 × 10¹⁰, giving −71
billion tonnes of PPR. Bay of Bengal `sym_GE_asDC` returns +2.1 × 10¹³ tonnes, 6,700× the
trophic-chain estimate. `PPR by method` now carries a `status` column flagging `DIVERGED`,
`IMPLAUSIBLE` (>25× the trophic-chain estimate; healthy methods run 0.1–4.6×), and methods
that returned nothing or zero. **The Summary sheet picks its headline method from the
unflagged ones.**

**A mapped group name must match `groups_df` exactly.** `tools/build_model_workbook.py`
refuses to run otherwise. A near-miss would silently drop that taxon's PPR.

**Excel file locks.** If the owner has a workbook open, `openpyxl` save fails with
`PermissionError` and a `~$name.xlsx` file is present. Skip that unit and say so; do not
force.

**`git add -A` and nested repos.** `PPREstimation` once contained its own `.git`, which
made `git add -A` stage it as a gitlink (mode 160000) so a clone would receive none of its
files. Check with `git ls-files -s | awk '$1=="160000"'` — it must return nothing.

**Heredocs into `cat` are unreliable in this shell.** Write files with a proper file-write
tool or a Python script.

**Do not average across methods, or across two models of the same ecosystem.** They answer
different questions. This is why each model gets its own workbook.

---

## 9. Current state

### Coverage

| asset | ecosystems |
| --- | --- |
| catch, per taxon per year, 1950–2019 | **364** |
| archived source articles | 109 |
| net primary production (LME and High Seas only) | 82 |
| an extracted Ecopath model and SPPR results | 10 |
| a taxon-to-group mapping | 6 |
| **a model workbook — PPR by method** | **5** |

### The mapped ecosystems

| unit | model | tonnage coverage | notes |
| --- | --- | --- | --- |
| `LME_032` Arabian Sea | `32_1_..._(2000)` | **100 %** | 13 apportioned; 5 inherited errors corrected; 22.6 % of tonnage still `inherited_mapping`, unverified |
| `LME_034` Bay of Bengal | `34_1_..._(1978)` | **100 %** | 239 apportioned across regions 2/3; 259 taxa confirmed against Appendix A1.1, 0 contradictions |
| `LME_047` East China Sea | `47_1_(1997)`, `47_2_(2018)` | **100 %** each | all 276 decisions re-derived from Table S1; 52 taxa confirmed, 0 contradictions |
| `LME_035` Gulf of Thailand | `35_412_..._(1963)` | 97.6 % | old-skill mapping; being re-run |
| `LME_052` Sea of Okhotsk | `52_1_..._NE_(1980)` | 90.2 % | old-skill mapping; model covers only the **northeastern** sea against a whole-LME catch series, so part of the shortfall is genuine |

All six model workbooks pass `tools/verify_model_workbook.py`.

### Work in flight at the time of writing

Four agents were running and their results are **not** in this document:

1. **A/B test of the combined skill** on `LME_028` Guinea, model `28_646_Guinea_(1998)`.
   Arm B uses `skills/ewe-species-to-group-mapper` in the repo; arm A uses
   `skills/ecopath-paper-to-ppr` in an isolated eval root so neither sees the other's
   answers. Compare with `tools/compare_mappings.py`. **Caveat: the member-list step was
   back-ported into the standalone mapper, so this is a non-inferiority test — it can show
   whether combining hurts, not whether it helps a lot.**
2. **`LME_035` and `LME_052` stages 1–2** — verifying the models against their
   publications and writing `<stem>.taxonomy.csv`, `<stem>.members.csv` and a
   `MODEL_PROFILE`. When those land: run `tools/apply_taxonomy.py`, then
   `tools/run_sppr.py --in-place`, then re-run stage 4 mapping against the refreshed work
   order.

Check `data/LME_028/mapping/`, `data/LME_035/mapping/` and `data/LME_052/mapping/` for
what actually arrived.

---

## 10. What to do next, in priority order

1. **Finish the two in-flight ecosystems** (§9). The sequence after stage 2 lands is:
   `apply_taxonomy.py` → `run_sppr.py --in-place` → `prepare_mapping.py` (the work order
   will now print each group's membership) → agent maps → `validate_mapping.py` →
   `build_model_workbook.py` → `verify_model_workbook.py`.

2. **Sweep the Arabian Sea inherited tail.** 335 rows (22.6 % of tonnage) still read
   `evidence = inherited_mapping`, meaning carried over from the first-generation mapping
   and never re-checked. In the ~30 rows that *were* checked, **4 were wrong**. The
   CMFRI Bulletin 51 table exists and makes the check mechanical: transcribe it to
   `32_1_Arabian_Sea_off_Karnataka_(2000).members.csv` and let the validator do the rest.

3. **Map the remaining usable models.** `LME_013` Humboldt (`13_2_Northern_Humboldt_Current_(1995-1998)`)
   and `LME_036` South China Sea (`36_1`, `36_2`) have usable models and no mapping.
   `data/model_selection.xlsx` is the authority on which models are fit.

4. **Test stage 1 of the combined skill for real.** Nothing has yet gone paper →
   extraction → `Taxonomy.xlsx` → SPPR → mapping in a single pass. Every test so far
   started from an already-extracted model. `LME_022` North Sea (Saygu et al.) and
   `LME_049` Kuroshio (Gan et al. 2025) are archived candidates that have never been
   extracted.

5. **Wire the network results into the map.** `PPRAtlas/index.html` still shows only the
   simple trophic-chain PPR.

6. **Extend coverage.** Only 10 of 364 ecosystems have a model at all. Sweeping and
   extracting more articles is the only thing that lifts this.

### Smaller known gaps

- `PPRAtlas` holds 368 committed `.xlsx` workbooks that are **stale** and contradict the
  CSVs beside them. Disclosed in the root `README.md`, not yet regenerated.
- NPP covers LME and High Seas only, not EEZs, and is a single 2019 value — so
  `ppr_over_npp_percent` uses a constant denominator across all 70 years. Treat the trend
  in that column as driven by PPR alone.
- `SPPR_1986` returns zero for every group on three models. Not diagnosed.
- 198 units have no geography because they fall outside PPRAtlas's 167-region curated
  selection. They still have catch and PPR.

---

## 11. Conventions the owner has set

These are decisions already made. Do not relitigate them without asking.

- **Work on `main`, no feature branches.** The project is still before its real initial
  commit.
- **Never modify Jensen-related behaviour in `PPREstimation/`.** It is the main algorithm
  folder and the Jensen effects must stay.
- **Keep the external `PPREstimation` git repository intact** — the clones at
  `../קוד/FishEstimation/` and `../קוד/FishEstimationAI/` are linked to another project.
- **Final workbooks stay lean.** Few sheets, few columns, aimed at a human reader.
- **Honesty over completeness.** An `Unresolved` with a one-sentence reason beats a
  plausible guess; a coverage target is a target, not a quota. Every tool here reports
  what it could not do rather than hiding it.
- Commit messages explain *why*, in prose, and end with
  `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

---

## 12. Where to look for more

| question | file |
| --- | --- |
| what is in `data/` and why | `data/README.md` |
| the whole project at a glance | `README.md` |
| how to map catch taxa | `skills/ewe-species-to-group-mapper/SKILL.md` |
| coarse catch labels | `skills/.../references/coarse-taxa-playbook.md` |
| model group structures | `skills/.../references/model-structures.md` |
| the mapping file format | `skills/.../references/output-format.md` |
| the full paper-to-PPR pipeline | `skills/ecopath-paper-to-ppr/SKILL.md` |
| capturing group membership | `skills/ecopath-paper-to-ppr/references/group-taxonomy.md` |
| extracting a model from a paper | `skills/ecopath-extraction/SKILL.md` |
| which model each ecosystem uses | `data/model_selection.xlsx` |
| design history | `docs/superpowers/specs/`, `docs/superpowers/plans/` |

## 13. Codex takeover addendum — 2026-09-07

The original handoff above is retained as the record of Claude's session. Read
[`CODEX_TAKEOVER.md`](CODEX_TAKEOVER.md) for the inspected current state, completed
skill reorganization, verification and remaining integration priorities.

The old `skills/<skill-name>/` paths above now resolve under
`skills/claude/<skill-name>/`; matching Codex variants live under
`skills/codex/<skill-name>/`. The builder now regenerates both complete sets and
all six archives. See [`../skills/README.md`](../skills/README.md).

The Guinea mapping is still a stub, despite its newly arrived member list; the
Thailand and Okhotsk taxonomy/member/profile files described as in flight above
were not present in their mapping directories at takeover. Do not treat those
agent assignments as completed work.

## 14. Integration completion — 2026-09-07

The status in section 13 describes takeover, not the current state. Tasks 1–5
are now complete, including the Guinea mapping/comparison, source reviews,
remaining usable pilot mappings, isolated new-paper validation, upstream workbook
refresh and verified atlas integration. The requested inner/PP sheets, scope and
method-ratio controls, and GE/TE recycling views are implemented. Coloring is
restricted to the ten selected pilot ecosystems. Coverage expansion (task 6)
has not started.

Read [INTEGRATION_COMPLETION.md](INTEGRATION_COMPLETION.md) for the current results,
verification and scientific limitations. In particular, Thailand's inherited
1963 filename contains a 1980 payload; Okhotsk NE refers to the whole Sea; Guinea
requires geographic extrapolation; failing SPPR configurations remain flagged.
The knowledge graph is refreshed for this integrated state before the requested
commit and push.

## 15. Annual graph view — 2026-09-07

The atlas now has a separate `PPRAtlas/trends.html` view for annual PPR and PPR/NPP,
with PPR/NPP method selectors, source scope, ecosystem presets/custom selection,
and separate model-version choices. Every map ecosystem links to its own graph.
The original global preset includes 84 LME/High Seas identities; all 366 known
LME/High Seas/EEZ identities are selectable. Missing and failed values remain
unavailable, and each curve uses a fixed cohort across years.
The year-range control can narrow that period. Individual ecosystem links open
their available catch span and preserve gaps inside it; regional sums exclude
incomplete annual series from the whole chosen period.

The owner explicitly requested repeating **2019 NPP for every catch year** for
now. Use a matched ecosystem cohort and `100 × ΣPPR / 9 / ΣNPP` for percentages;
do not average regional ratios or include NPP from ecosystems lacking PPR.
The existing six NPP choices are exposed; the ensemble option sums regional
medians. The page and CSV disclose the fixed baseline and catch coverage.

Read the annual-graphs section of `PPRAtlas/README.md` for usage and regeneration.
`tools/build_time_series.py` independently checks the raw catch/TL and mapped
SPPR totals against saved annual workbook rows before publishing the graph data.
No PPREstimation algorithm or Jensen behavior was changed; coverage expansion
(task 6) remains separate from allowing the existing simple method in the graph.
