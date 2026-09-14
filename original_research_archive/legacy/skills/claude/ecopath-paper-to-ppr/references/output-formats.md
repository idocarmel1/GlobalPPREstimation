# Output formats

Contents: [Where the files go](#where-the-files-go) ·
[Conventions](#conventions-that-apply-to-every-file) ·
[File specs](#file-specs) · [Model JSON](#model-json) ·
[REPORT.md](#reportmd) · [MASTER_INDEX.md](#master_indexmd)

## Where the files go

All ten artefacts — the eight import files, `REPORT.md` and the model JSON —
live in one directory per model, named:

```
<model_number>_<model_name>_<model_year>        e.g. 680_North_Sea_1981
```

`write_outputs.py` derives the name from `metadata` and creates the directory,
so it is never typed. Rules the derivation follows:

- Spaces and punctuation collapse to single underscores; `Denmark, Faroe
  Islands` becomes `Denmark_Faroe_Islands`.
- A year already trailing `model_name` is not repeated, so a `model_name` of
  `North Sea 1981` with `model_year` 1981 still gives `680_North_Sea_1981`.
  Prefer setting `model_name` to the place alone.
- A missing `model_number` or `model_name` is an error, not a default.
- `model_number` is the model's own identifier (EcoBase, where the source has
  one), not its position in the extraction set — a set that gets reordered must
  not rename its directories.

`--zip` writes `<model_number>_<model_name>_<model_year>.zip` next to the
directory for handing over; the directory stays the working copy. `--dir-name`
overrides the derived name and belongs in `REPORT.md` when used.

The path is printed on stdout. Capture it and pass that exact path to
`validate.py` and `massbalance_check.py`; do not depend on shell-specific command
substitution. Invoke every script by absolute path from the installed skill
directory.

## Conventions that apply to every file

- **No quote characters anywhere.** Not around headers, not around group names.
  This overrides any default CSV-quoting habit. A group name containing a comma
  therefore can't be written — rename it (and note the rename) rather than
  quoting it.
- **CRLF line endings**, including on the final line.
- **UTF-8**, no BOM.
- **Header text verbatim** from `assets/templates/`, including `(/year)`,
  `(t/km^2)` and the caret notation.
- **Row 1 is the header; the first column is the group number**, 1..N with no
  gaps, in the same order in every file.
- **Numbers exactly as the source prints them.** `write_outputs.py` reads the
  model JSON with `parse_float=str` precisely so `0.10` doesn't become `0.1`.

Run `scripts/write_outputs.py` rather than hand-writing these files; it enforces
all of the above. Then run `scripts/validate.py`.

## File specs

Templates live in `assets/templates/` (`aaa`/`bbb` are placeholder group names,
`ccc`/`ddd` placeholder fleet names).

**`Basic_input.csv`** — one row per group.
```
,Group name,Hab area (proportion),Biomass in habitat area (t/km^2),Total mortality (/year),Production / biomass (/year),Consumption / biomass (/year),Ecotrophic Efficiency,Other mortality,Production / consumption,Unassim. consumption,Detritus import (t/km^2/year)
```

**`Diet_composition.csv`** — prey rows, consumer columns. Header is
`,Source / fate,` followed by the *group numbers* of consumers. After the prey
rows come three rows with an empty first column: `Import`, `Sum`, `(1 - Sum)`.
```
,Source / fate,1,2,3,...
1,Baleen whales,,,0.05,...
...
,Import,0,0,0.13,...
,Sum,1,1,1,...
,(1 - Sum),0,0,0,...
```

**`Landings.csv`** / **`Discards.csv`** — `,Group name,<fleet 1>,<fleet 2>,...,Total`.
`Total` is the row sum across fleets; blank where the row has no entries.

**`Detritus_fate.csv`** — `,Source / fate,<detritus group 1>,...,Export,Sum`.
Rows sum to 1.

**`Biomass_accumulation.csv`** — one row per group.
```
,Group name,Biomass accumulation (t/km^2/year),Biomass accumulation rate (/year)
```
Write whichever form the paper states and leave the other blank; do not convert
between them, since the conversion needs B and would manufacture digits at B's
rounding. A negative value is a declining stock and is normal. An entirely blank
file means no numeric BA was extracted, not that BA is known to be zero.
`validate.py` warns on it so the report must say where BA and any steady-state
statement were checked. Where both columns are filled it cross-checks them
through B.

**`TL.xlsx`** — single sheet. `C1` holds the literal `TL`; `A1` and `B1` empty.
From row 2: group number in A, group name in B, trophic level in C.

**`Metadata.xlsx`** — single sheet, column A rows 1–4 hold the literal keys
`LME`, `model_number`, `model_name`, `model_year`; column B holds the values.

**Not produced:** `Taxonomy.xlsx`. Out of scope for this project.

### Row counts

Basic_input, Detritus_fate and TL carry a row for every group. Diet_composition,
Landings and Discards carry a row per prey/catchable group, which in the
reference example stops short of the full group list. Set `diet_rows` (and, if
they differ, `landings_rows` / `discards_rows`) in the JSON to match the model
being extracted, and state the counts in the report so a reviewer can see the
choice was deliberate.

## Model JSON

The intermediate file the extraction produces; `write_outputs.py` turns it into
the eight outputs. Omit a key or set it to `null` for a blank cell; use `0` for a
stated zero.

```json
{
  "metadata": {
    "LME": "22 North Sea",
    "model_number": 13,
    "model_name": "North Sea 1981",
    "model_year": 1981
  },
  "groups": [
    {"n": 1, "name": "Baleen whales", "hab_area": 1,
     "biomass": 0.0169, "z": null, "pb": 0.02, "qb": 3.29,
     "ee": null, "other_mort": null, "pq": null,
     "unassim": 0.2, "detritus_import": null, "tl": 4.1,
     "ba": null, "ba_rate": null}
  ],
  "consumers": [1, 2, 3],
  "fleets": ["Beam trawl", "Otter trawl"],
  "landings":  {"3": {"Beam trawl": 0.012, "Otter trawl": 0.008}},
  "discards":  {"3": {"Beam trawl": 0.003}},
  "detritus_groups": ["Pelagic detritus", "Benthic detritus"],
  "detritus_fate": {"1": {"Pelagic detritus": 1},
                    "3": {"Pelagic detritus": 0.5, "Benthic detritus": 0.5}},
  "diet": {"3": {"1": 0.25, "2": 0.62, "import": 0.13}},
  "diet_rows": 39
}
```

Notes:
- `groups` is ordered and `n` runs 1..N; the order is the paper's.
- `consumers` lists the group numbers that get a diet column, in order.
- `landings`, `discards`, `detritus_fate` and `diet` are keyed by group number
  **as a string**; groups absent from a mapping get blank cells.
- Inside `diet`, keys are prey group numbers plus the special key `import`.
- `tl` lives on the group and feeds `TL.xlsx`.
- `ba` (t/km^2/year) and `ba_rate` (/year) live on the group and feed
  `Biomass_accumulation.csv`. Set at most one of the two per group — whichever
  the paper printed.

Keep the JSON in the model directory alongside the outputs. A correction pass
edits the JSON and re-runs the writer, which is how a fix stays consistent
across all eight files — and why the directory name has to come from the JSON
rather than from the shell, so re-running can never scatter a corrected model
across two differently-named directories.

## REPORT.md

One per model, in the model directory. Required sections:

```markdown
# <Model name> (<year>)

**Source**: <full citation, chapter, pages>
**LME**: <number and name>   **Model number**: <n>
**Groups**: <N> (<n living>, <n detritus>)   **Fleets**: <list>
**Extracted**: <date>

## Source tables
### Table 3 (p. 47) — basic input
Columns as printed: ...
Mapped to: ...
Units: ...
Rows: <table> vs <group list>

### Table 4 (pp. 48-49) — diet composition
<layout notes, continuation, anchor line used, merge_gap used>

## Biomass accumulation
<state where BA and any steady-state claim were searched; distinguish an
explicit steady-state statement from source silence; then give any values with
their source — table and page, sentence and page, or the two
endpoints of a series and the arithmetic. If read off a figure, say so, give the
figure number and dpi, and state the precision it supports.>

## Values from prose
- <value, group(s), page, derivation>

## Conventions applied
- <e.g. Unassim. consumption 0.35 for Large zooplankton (group 19): project
  convention for unambiguous zooplankton groups; not stated in the paper.>

## Deliberate blanks
- <field, group(s), why — and what EwE will default them to>

## Unresolved and flagged
- <pointers that led nowhere, ambiguous mappings, conflicts between table and text>

## Validation
Diet column sums: <range>, <n> columns outside +/-0.01 (listed below with the
page checked against).
Detritus fate rows: all 1.0 / exceptions listed.
validate.py: <n> errors, <n> warnings — <what the warnings are>

## Mass balance
massbalance_check.py: <n> errors, <n> warnings.
Recomputed vs printed EE: <max difference, and which group>.
Groups with recomputed EE > 1: <list, with what was checked on the page and the
conclusion — extraction error corrected, or genuine feature of the paper>.
P/Q outside 0.02-0.5: <list with explanation>.
Migration (E) reported by the paper: <yes/no — if yes, the recomputed EE will
legitimately differ and by roughly how much>.
BA: <carried in Biomass_accumulation.csv, so the check accounts for it — note any
group where a mismatch survives anyway, or where the check suggested a BA that
the paper does not support>.
```

The sections that matter most on re-reading are **Conventions applied**,
**Deliberate blanks** and **Unresolved and flagged**. Those three are what
distinguish this from an unreviewable pile of numbers.

## MASTER_INDEX.md

One per extraction set, at the top level. A row per model:

```markdown
| # | Model | Year | LME | Groups | Fleets | Status | Notes |
|---|---|---|---|---|---|---|---|
| 13 | North Sea | 1981 | 22 | 41 | 2 | complete | |
| 14 | Mauritania | 1998 | 27 | 34 | 3 | complete | diet matrix at merge_gap 0.4 |
| 15 | Sierra Leone | - | 28 | - | - | excluded | data compilation, no balanced parameters |
```

Statuses: `complete`, `partial` (with what's missing in Notes), `excluded` (with
the reason), `pending`. Update it in the same pass that finishes the model —
an index that lags is worse than no index, because it gets trusted.
