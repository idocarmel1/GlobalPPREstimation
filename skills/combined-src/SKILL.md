---
name: ecopath-paper-to-ppr
description: "Take a published Ecopath with Ecosim paper all the way to primary production required: extract the mass-balance model into the EwE import files and database JSON, capture which taxa sit in which functional group while the paper is open, run the SPPR methods, and map an ecosystem's catch taxa onto the model's groups so per-group SPPR becomes per-taxon PPR. Use when the user mentions Ecopath, EwE, mass-balance or trophic models, diet composition matrices, B/PB/QB/EE parameters, group membership or taxonomy tables, species-to-functional-group mapping, SPPR or PPR estimation, or asks to pull model parameters out of a paper - even if they never name the output files."
---

# From an Ecopath paper to PPR

One pipeline, four stages. Each has a workflow file; read the one you are in.

```
  paper (PDF + supplements)
      |
  1.  EXTRACT      -> the eight EwE import files + the database JSON
      |             references/extraction.md
      |
  2.  TAXONOMY     -> Taxonomy.xlsx: which taxa are in each group
      |             references/group-taxonomy.md          <- the seam
      |
  3.  SPPR         -> per-group SPPR under ~20 methods
      |             PPREstimation/create_PPRS_excel.py
      |
  4.  MAP          -> every catch taxon onto a group, then PPR per taxon per year
                    references/mapping.md
```

## Why these are one skill

Stages 1 and 4 both require reading the same paper closely enough to know what each
functional group *is*. Run separately, that reading happens twice, and the second time it
happens without the extractor's notes — which is how three finished mappings ended up
resting on taxonomic guesswork while the group list sat extracted and exact a directory
away.

Stage 2 is the fix and it is why the combination pays. Group membership is cheap to record
while you are already reading the basic-input table and the diet matrix, and expensive to
reconstruct months later from the same PDF. Captured once, it flows: `Taxonomy.xlsx` ->
`taxon_descr` in the database JSON -> the `groups_df` column the mapper reads -> `explicit
member` evidence instead of inference.

**If you are only doing one stage, say so and do only that.** A mapping request against an
already-extracted model starts at stage 4. A paper with no downstream mapping planned stops
after stage 2. Do not run stages the user did not ask for.

## Entry points

| you have | you want | start at |
| --- | --- | --- |
| a paper, nothing extracted | the model files, or the whole chain | stage 1 |
| an extracted model, no `Taxonomy.xlsx` | membership for a later mapping | stage 2 |
| a database JSON | per-group SPPR | stage 3 |
| an SPPR workbook and a catch series | PPR per taxon | stage 4 |

## Stage 1 — extract

`references/extraction.md`. Produces one directory per model with the eight EwE import
files, `model.json`, the database JSON, a round-trip workbook, a mass-balance report and
`REPORT.md`.

Two things in that workflow now carry downstream consequences, so do not treat them as
bookkeeping:

- **The group list is the spine.** Fix it before extracting any value, keep the paper's own
  numbering, and record the names exactly. Stage 4 joins on those strings.
- **Record what the group list is organised by** — taxonomy, size and habitat, feeding
  guild, spatial stratum, life stage — in `MODEL_PROFILE.md`. One paragraph.
  `references/model-structures.md` describes the archetypes and the trap each one sets.
  A stratified model whose prefixes nobody wrote down is how a whole sea's catch ends up
  attributed to one sub-area.

## Stage 2 — capture the taxonomy

`references/group-taxonomy.md`. This is new work relative to running the two skills apart,
and it is the point of combining them.

`Taxonomy.xlsx` is three columns — `seq`, `group_name`, `taxon_descr` — and the database
JSON already reads it if it is present. Write it while the paper is open. If the paper has
no membership table, say so in that file rather than leaving it absent: "not documented" is
information, and a later mapper will otherwise spend an hour rediscovering the absence.

## Stage 3 — SPPR

```bash
python PPREstimation/create_PPRS_excel.py <json_dir> <out_dir>
```

Reads the database JSONs in `<json_dir>` and writes one workbook per model with `groups_df`,
`sppr_all`, `sppr_inner`, `sppr_PP`, `model_health` and `run_notes`. Heavy methods have a
wall-clock budget; `--timeout SECONDS` changes it. A method that times out or raises is left
`NaN`, never zero.

**Read `model_health` before going further.** A model can extract cleanly, import cleanly
and still be unfit — unbalanced, diet rows far from 1, or exploding under one `TE_option`.
Mapping onto an unfit model produces confident nonsense. Record the verdict in
`data/model_selection.xlsx`.

## Stage 4 — map catch taxa to groups

`references/mapping.md`. Produces `data/<unit>/mapping/<model_stem>.csv` and, through
`tools/build_model_workbook.py`, one workbook per model with PPR by method and by taxon.

Where stage 2 ran, start from `taxon_descr` in `groups_df` — the work order surfaces it. Every
row it supports is `explicit_member` evidence rather than inference, which is the difference
between a mapping a reviewer can check and one they have to trust.

The measure is **the share of catch tonnage on a named group**, not the share of taxa.
Target 95 %. Coarse labels like `Marine fishes not identified` carry a fifth of an LME's
catch and are apportioned across the groups they span, not discarded;
`references/coarse-taxa-playbook.md` is the part of this skill that most changes the result.

## Rules that hold across every stage

**A plausible-looking wrong number survives review forever.** A diet proportion parsed one
column left, a P/B read off the row above, a family assigned to the wrong feeding guild:
all of these validate, balance and join cleanly. Every stage here is built to make mistakes
visible rather than to go fast.

**Never claim a source said something it did not.** Distinguish what the paper states, what
an earlier model it cites states, and what you inferred. Each stage has a field for this —
`REPORT.md`, `taxon_descr`, `membership_source`, `evidence`. Use them.

**Run the validator after every pass, not once at the end.**

```bash
python scripts/validate.py <model_dir>                        # stage 1
python scripts/massbalance_check.py <model_dir>               # stage 1
python scripts/validate_mapping.py <unit_id>                  # stage 4
```

**Unknown is a value.** `-9999` in the model files, blank in a mapping's weights,
`Unresolved` in a decision, `NaN` in an SPPR cell. None of them is zero, and turning any of
them into zero is the most common way this pipeline produces a wrong answer that looks
right.

## Reference files

| file | when |
| --- | --- |
| `references/extraction.md` | stage 1, the full workflow |
| `references/group-taxonomy.md` | stage 2 |
| `references/mapping.md` | stage 4, the full workflow |
| `references/model-structures.md` | stages 1 and 4 — what the group list is organised by |
| `references/coarse-taxa-playbook.md` | stage 4 — the labels that decide your coverage |
| `references/mapping-output-format.md` | stage 4 — the exact CSV contract |
| `references/ecopath-model.md` | the two master equations, balance criteria, magnitude ranges |
| `references/parameter-conventions.md` | units, defaults, what EwE substitutes for a blank |
| `references/output-formats.md` | the eight import files, column by column |
| `references/pdf-extraction.md` | reading a PDF with coordinates rather than `-layout` |
| `references/prose-extraction.md` | values stated in text and footnotes |
| `references/table-layouts.md` | mapping an unfamiliar table onto EwE fields |
| `references/source-bundle.md` | assembling papers and supplements |
