# EwE Species-to-Group Mapper

Ecopath has no taxon level and Sea Around Us has no functional groups. This skill builds
the join between them, one ecosystem at a time, so that `SPPR` per group becomes `PPR` per
taxon per year.

The measure of a mapping is **the share of catch tonnage that lands on a named group**, not
the share of taxa. Those two numbers diverge badly — a mapping can leave 44 % of taxa
unresolved and still carry 90 % of the tonnage, because the unresolved tail is rarities.
PPR is a tonnage quantity. Optimise tonnage.

Target: **95 % of catch tonnage on a named group.** The first generation of mappings
reached 78 % and stopped, because a handful of coarse labels like
`Marine fishes not identified` were each written off as `Unresolved` while carrying a fifth
of the catch between them. Read `references/coarse-taxa-playbook.md`; that gap is the main
thing this skill exists to close.

## Inputs

Runs against a `GlobalPPREstimation` checkout. Set `GLOBALPPR_ROOT` if you are not inside
one.

Resolve the directory containing this skill's `SKILL.md` as `<skill-root>`.
`scripts/`, `references/`, `assets/` and `examples/` are relative to that root,
including when this workflow is copied into `references/`. Invoke bundled scripts
by quoted absolute path. Paths starting with `tools/`, `data/`, `PPREstimation/`,
`SeaAroundUsExtraction/` or `PPRAtlas/` are relative to the repository root.
`GLOBALPPR_ROOT` locates data for the mapping scripts; it does not change the shell's
working directory. Run repository tools by absolute path from the checkout root.

| what | where |
| --- | --- |
| the taxa to map | `SeaAroundUsExtraction/data/catch_by_taxon_year/<unit_id>.csv.gz` |
| the model's exact group list | `PPREstimation/output/top10/<model>.xlsx`, sheet `groups_df` — **authoritative** |
| membership evidence | `PPRAtlas/archive/regions/<unit_id>/<ARTICLE>/` — papers and supplements |
| which model to use | `data/model_selection.xlsx`, column `usable` |

`prepare_mapping.py` collects all of this into one work order, so you do not have to open
the archives by hand to find out what exists.

Two standing facts about this data:

**Group names are already extracted and exact.** Read them from `groups_df`, never from
the prose. The downstream join is on the exact string.

**Check `taxon_descr` in the actual model.** Older extractions often left it empty;
the combined skill's taxonomy stage populates it. Use documented membership when
present and consult the cited sources. Record an empty field as an extraction gap
only when it is actually empty; `not documented` records a completed source search.

## The loop

### 1. Prepare

```bash
python "<skill-root>/scripts/prepare_mapping.py" LME_047
```

Writes `data/<unit>/mapping/WORK_ORDER.md` — the models with their `usable` verdicts, the
exact group lists with TL, biomass and model catch, and every taxon ranked by tonnage with
a cumulative percentage and a `coarse` flag. It also stubs one CSV per model with a row for
every taxon, so the mapping is complete by construction.

**Check `usable` first.** A model can be extracted and still be unfit — unbalanced, or it
explodes, or its diet rows are far from 1. Mapping onto an unusable model produces
confident nonsense. If it is not usable, say so and stop.

### 2. Read the model before the taxa

Work out what axis the group list is built on — taxonomic, size and habitat, feeding
guild, spatial stratum, life stage — and what any prefix in the names means.
`references/model-structures.md` has the archetypes and the trap each one sets. Ten minutes
here changes every decision afterwards.

### 3. Find the membership evidence

Read the paper. Then look specifically for:

- a species-to-group table (often only in the supplement — the East China Sea one is a
  `.docx` data sheet, not a table in the PDF)
- the diet composition matrix, which constrains what a guild can contain
- group-definition prose, size or life-stage splits, synonyms used by older papers
- "based on", "adapted from", "following" — then read that earlier paper too

**If you find a species-to-group table, transcribe it to `<model_stem>.members.csv` before
mapping anything.** The validator then checks every decision against it and treats a
contradiction as an error. This is worth more than any other single step: in the Arabian Sea
the table was in the archive the whole time, and checking against it caught five wrong
assignments the previous mapping had carried for months. Format in
`references/output-format.md`.

Make real download attempts for supplements you can identify but do not have; record the
filename, URL and result. Never claim a supplement was read when only its citation was
found. Distinguish `direct source` (the paper adopts it), `supporting regional source`
(relevant but not stated as inherited) and `analyst inference` (yours).

### 4. Map, in tonnage order

The work order is sorted by catch. In a typical LME the top thirty taxa carry 90 % of it.
Work down that list; the two-tonne rarities at the bottom deserve a minute each, not an
hour.

Evidence hierarchy, in order:

1. the exact taxon listed in that group in that model
2. accepted-name or synonym match to a listed member
3. taxonomic containment — the group is defined by a taxon that contains this one
4. habitat, size band and feeding guild together, corroborated by TL
5. a classification explicitly inherited from a cited predecessor model
6. ecological analogue: diet, habitat, size, mobility and TL together
7. **apportionment across the groups the taxon spans** — see the playbook
8. `Unresolved`

Rule 7 is the new one and it is where the coverage is. A coarse label is apportioned, not
discarded. `Unresolved` still means *outside the model* — a billfish in a coastal-shelf
model, a mollusc where there is no benthic group — not *hard to decide*.

Never select a feeding guild from trophic level alone. TL corroborates; it never decides.

### 5. Validate, and iterate against the number

```bash
python "<skill-root>/scripts/validate_mapping.py" LME_047
```

Reports tonnage coverage by confidence tier and lists the largest unresolved taxa. Errors
are things that would make the PPR wrong: a missing taxon, a group name not verbatim in
`groups_df`, catch on `Detritus` or a primary producer, malformed weights, a confidence
that contradicts its decision.

Run it after every pass. When the verdict is `INCOMPLETE`, the largest unresolved taxa it
prints are your work list. Stop when it says `PASS`, or when the remaining unresolved
tonnage is genuinely outside the model and you can say so in one sentence per taxon.

### 6. Write the group dictionary and the notes

`<model>.groups.csv` and `<model>.notes.md`, per `references/output-format.md`. One row per
group whether or not catch lands on it; the notes carry the model's area, the axis, the
supplements you did and did not get, and the judgement calls a reviewer should push back
on.

### 7. Merge

```bash
python tools/build_model_workbook.py --units LME_047
python tools/verify_model_workbook.py --units LME_047
```

The builder refuses to run if a mapped group is absent from the model's own `groups_df`,
because every PPR derived from that row would be fiction. It writes one workbook per model
under `data/<unit>/models/`, plus `<model_stem>.resolved.csv` recording the weights it
actually used. The verifier then re-derives the workbook's formulas by hand and checks the
per-taxon and aggregate sheets against each other.

## Output

Under `data/<unit_id>/mapping/`, specified exactly in `references/output-format.md`:

```
<model_stem>.csv          taxon, common_name, functional_group, commercial_group,
                          group, weights, confidence, evidence, explanation
<model_stem>.members.csv  the paper's own species-to-group table, where it has one
<model_stem>.groups.csv   the group dictionary
<model_stem>.notes.md     provenance and limitations
```

Plain CSV. The builder renders it into the ecosystem workbook with the confidence
colouring — do not edit workbooks directly, and do not reorder or drop stub rows.

One set of files per **distinct model**, even when two models share a group list. Models
are distinct when they differ by period, area, scenario, season, depth stratum or group
structure. `47_1_East_China_Sea_(1997)` and `47_2_East_China_Sea_(2018)` are two mappings,
not one.

## Worked examples

`examples/` holds three first-generation mappings — Arabian Sea, Bay of Bengal, East China
Sea. Read one for the shape of the explanations. Two warnings about them:

- They are **reference output, not lookup tables.** Never copy an assignment from one
  ecosystem into another without evidence from that ecosystem's own sources.
- They reach only 78 % tonnage coverage, and the Bay of Bengal one puts every stratified
  taxon into stratum `2` without saying so. They are the baseline this skill is meant to
  beat, not the standard to match.

## Reporting

When you finish, report:

- models mapped, and any skipped because they are not usable
- **catch tonnage coverage per model**, then taxon counts by confidence tier
- the composite splits you made and the weight basis for each
- the unresolved taxa that carry real tonnage, and why each is outside the model
- supplements sought and not obtained
- anything about the model's structure that a reader of the PPR numbers must know

Do not report a mapping as complete while the validator says `FAIL`.
