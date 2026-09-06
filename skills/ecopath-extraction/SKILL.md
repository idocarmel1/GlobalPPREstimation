---
name: ecopath-extraction
description: "Extract Ecopath with Ecosim (EwE) mass-balance model parameters from published papers into the EwE import files (Basic_input.csv, Diet_composition.csv, Landings.csv, Discards.csv, Detritus_fate.csv, Biomass_accumulation.csv, TL.xlsx, Metadata.xlsx) and the per-model database JSON the loader reads. Use whenever the user mentions Ecopath, EwE, mass-balance or trophic models, diet composition matrices, B/PB/QB/EE parameters, biomass accumulation, or Fisheries Centre Research Reports, or asks to pull model parameters, basic input tables, landings or diet matrices out of a paper or PDF - even if they never name the output files. Also use when building or checking the model JSON, running a mass-balance check, mapping an unfamiliar table layout onto EwE fields, chasing values stated in prose or footnotes, adding a model to an extraction set, re-checking an extracted model, or updating MASTER_INDEX.md."
---

# Ecopath model data extraction

Turn a published Ecopath model into the eight files the EwE database importer
expects and the JSON the downstream loader reads, with every number traceable to
the page it came from.

The hard part is not the file format — the scripts handle that. The hard part is
that a plausible-looking wrong number survives review forever. A diet
proportion parsed one column left, a P/B read off the row above, an
assimilation fraction quietly defaulted instead of read from the paper's prose:
all of these import cleanly and balance almost as well as the truth. So the
workflow below is built around making mistakes *visible* rather than making
extraction fast.

## What one model produces

One directory per model, named
`<model_number>_<model_name>_<model_year>` — for example
`680_North_Sea_1981`. `write_outputs.py` derives that name from the JSON
metadata and creates the directory itself, so the name is never typed by hand
and never drifts between models. It contains:

| File | Contents |
|---|---|
| `Basic_input.csv` | one row per functional group: B, Z, P/B, Q/B, EE, P/Q, unassimilated fraction, detritus import |
| `Diet_composition.csv` | prey rows x consumer columns, plus `Import`, `Sum`, `(1 - Sum)` rows |
| `Landings.csv` | catch by group and fleet |
| `Discards.csv` | discards by group and fleet |
| `Detritus_fate.csv` | where each group's detritus goes |
| `Biomass_accumulation.csv` | BA per group, absolute and/or as a rate — blank for a steady-state model |
| `TL.xlsx` | trophic level per group |
| `Metadata.xlsx` | LME, model number, model name, model year |
| `model.json` | the extraction JSON the eight files above were written from |
| `<LME>_<number>_<name>_(<year>).json` | the database JSON, built back out of the eight files |
| `<...>_reconstructed.xlsx` | round-trip workbook rebuilt from the database JSON |
| `MASS_BALANCE.md` | the mass-balance findings, ready to paste into `REPORT.md` |
| `ewe_conversion.log` | every decision the JSON conversion made |
| `REPORT.md` | what was found, what was inferred, what is missing, page citations |

Then update `MASTER_INDEX.md` at the top of the extraction set with this
model's status.

`Taxonomy.xlsx` is **not** part of the deliverable — it is deliberately out of
scope for this project. The database JSON reads one if a directory happens to
have it, and leaves `taxon_descr` null otherwise.

## Step 0: is the source actually a model?

Some volumes contain data compilations that were assembled *toward* a model but
never balanced — species lists, survey biomass tables, landings statistics with
no diet matrix and no P/B or Q/B. These have no extractable model.

If there is no balanced parameter set (no basic-input-style table, no diet
matrix), stop and say so rather than assembling a partial model out of the
fragments. Record the exclusion and the reason in `MASTER_INDEX.md`. Precedent:
the Sierra Leone chapters (135/136/137) were excluded on exactly this ground.

## Step 1: establish the group list first

Every file is keyed to group number and order, so the group list is the spine.
Get it from the paper's own basic input table and keep its numbering exactly —
including the position of detritus groups, which usually sit last but not
always.

Fix the list before extracting any values. Renumbering halfway through is how
diet columns end up shifted.

If you're unsure what a parameter is, which cells in a paper are inputs versus
Ecopath outputs, or why a value looks implausible, read
`references/ecopath-model.md`. It has the two master equations, the "three of
four" rule that explains why published tables have systematic blanks, the balance
criteria, and indicative magnitude ranges per group type. Knowing the equations
is what turns vague unease about a number into a specific arithmetic check.

## Step 2: read the PDF with coordinates, not with `-layout`

Read `references/pdf-extraction.md` before touching the PDF. Short version:
`pdftotext -layout` silently misassigns numbers between columns in these
densely-set tables, so use `scripts/pdfgrid.py`, which reconstructs columns from
word bounding boxes. Rotated landscape pages must be physically rotated with
`qpdf` first — their text layer has reversed x-coordinates and cannot be parsed
in place.

## Step 3: map each table's layout before extracting from it

Every paper in this corpus lays its tables out differently — different column
order, different names for the same parameter, different marks for
model-estimated values, sometimes a different language. There is no template to
match against, so the risk is *pattern completion*: assuming the fourth numeric
column is Q/B because it was Q/B in the last three papers.

For any table whose layout you haven't already mapped in this session:

1. Read the caption and **every** footnote in full first.
2. Write down the mapping (paper's header → EwE field) before reading values.
3. Check the mapping on one row using a relationship that must hold — P/Q =
   (P/B)/(Q/B), EE in [0, 1], Z ≥ P/B for a fished group, and respiration
   positive so P/Q < 1 − GS. A wrong mapping breaks these immediately. The
   magnitude table in **EwE defaults and sanity ranges** below is the second
   half of this check: a P/Q of 0.8 or a fish P/B of 40 is a slipped column,
   not a surprising ecosystem.
4. Match rows by group name, never by position.
5. Count rows and columns against your group list before extracting.

`references/table-layouts.md` has the header-vocabulary table, the recognised
layout patterns (continued tables, two-row headers, transposed tables,
stacked sub-columns), the meaning of in-cell notation (parentheses, dashes,
`<0.001`, comma decimals), and unit-conversion rules. Read it before Step 4 the
first time and whenever a table doesn't fit a pattern you've already mapped.

If a column can't be mapped confidently, leave those cells blank and name the
ambiguity in the report. A blank costs a reviewer one page of reading; a wrong
mapping propagates silently through the whole model.

## Step 4: sweep the prose and the footnotes

This is where extractions go wrong most often, because a table looks complete —
a blank cell reads as "no value exists" when it often means "the value is in the
methods section".

Start with the pointers, because they tell you which cells *not* to read off the
table:

```bash
python scripts/prose_sweep.py paper.pdf --family pointers   # "see text", "voir texte", ...
python scripts/prose_sweep.py paper.pdf --numbers-only      # the full sweep
```

A caption or footnote saying *"see text"*, *"as described in the text"*,
*"explained in the text"* or *"voir texte"* is the author stating outright that
the table is incomplete and where the rest is. Resolve every one of them before
extracting that table, with a specific question attached: which cells does this
cover, and what does the text say about them? An unresolvable pointer is a real
finding — record it and leave the cells blank.

Then sweep for the parameters that habitually live in prose:

- **Unassimilated consumption**, frequently stated only in running text
  ("assimilation efficiency was assumed to be 80% for fish...", → 0.2). The
  North Sea paper does exactly this.
- **Diets of plankton and microbial groups**, described in sentences rather than
  in the matrix. "Ciliates feed entirely on bacteria" is a diet composition of
  1.0. But "mainly" and "predominantly" are not numbers — don't turn them into
  0.7.
- **Discard rates** given as a proportion of landings: a rate to apply, with the
  arithmetic recorded.
- **Model area**, needed whenever catches are in absolute tonnes.
- **Biomass accumulation**, which breaks the steady-state identity and so has
  to be found before any mass-balance mismatch can be read as an extraction
  error. See Step 4b.
- **Provenance phrases** — "assumed", "taken from", "adjusted to balance" —
  which change what a number means even when the number itself is tabulated.
  "We used the Ecopath default" is one of these: it makes the software's number
  a paper-stated value, and the report says which default was adopted.

Run the sweep twice: once over the whole chapter, and again after the tables are
extracted with the list of still-blank cells in hand, searching for those group
names specifically. The second pass is what catches the rest.

A prose statement that happens to match a documented EwE default word for word
("assimilation efficiency was assumed to be 80%", "20% of consumption was taken
as unassimilated") is still a paper-stated value — the author adopted the
convention, and adopting it is a statement. Extract it, and note in `REPORT.md`
that it was stated in prose and coincides with the software default.

`references/prose-extraction.md` covers the sweep in detail, how to scope a prose
statement to specific groups, the percentage/complement arithmetic, and what to
do when the table and the text disagree.
`references/parameter-conventions.md` has the parameter-by-parameter rules,
including when the 0.35 / 0.4 unassimilated-consumption conventions may and may
not be applied.

## Step 4b: find the biomass accumulation, including in figures

Ecopath's production identity is `B(P/B)EE = Y + BA + Σ_j B_j (Q/B)_j DC_ji`.
Papers that report BA are a minority, but on those papers a recomputed EE will
differ from the printed EE by `BA / (B·P/B)` — and that difference looks exactly
like a mis-parsed Q/B or a catch left in absolute tonnes. So BA gets searched
for **before** Step 6 flags anything, not after.

```bash
python scripts/prose_sweep.py paper.pdf --family accumulation
```

BA is rarely in the basic input table. Where it actually turns up, in rough
order of frequency:

1. **A mortality table.** A column headed `BA` next to `Z`, `F`, `M0`, `M2`, on
   the reasoning that `Z = F + BA + M0 + M2`. This is the North Sea worked
   example: Table 5 on p. 16, not Table 1.
2. **A sentence about the stock.** "the stock was declining through the study
   period", "biomass was accumulating at some 5% per year". A percentage is a
   rate; a tonnage is absolute. A *qualitative* statement is not a number —
   "declining" alone gets recorded in the report and left blank, exactly like a
   qualitative diet statement.
3. **A biomass time series** — a figure or a table of biomass by year. BA is
   then the slope over the model's own year, which is a derivation, not a
   reading. Only do it if the paper's model period is unambiguous, and record
   the two endpoints and the arithmetic in `REPORT.md`.
4. **A flow diagram.** Some Ecopath figures label the BA term on the box.

EwE's own default for BA is **0** — "the default value for BA is zero indicating
no biomass accumulation" (EwE User Guide, *Ecopath Input*). That is why a paper
can be silent about BA and still have been built with BA sitting at zero — and
it is emphatically *not* a licence to write `0` into
`Biomass_accumulation.csv`. Here a blank stays blank and means unknown; see the
defaults section below for why that distinction is load-bearing.

### Reading a value off a figure

Digitising a graph is a last resort and the report must say that is what
happened. If you do it:

```bash
pdftoppm -f 12 -l 12 -r 300 -png paper.pdf /tmp/fig     # 300 dpi, not 150
```

Then view the image and work from the axis ticks, not from the impression the
curve gives. The rules that keep this honest:

- **Read against labelled gridlines only.** Interpolating between two ticks is
  fine; extrapolating past the last one is not.
- **Round to the precision the figure can actually support** — usually one or
  two significant figures. A BA of `0.2` read off a graph must not be written
  as `0.23`, because the extra digit claims a precision the source doesn't
  have and is indistinguishable from a tabulated value afterwards.
- **Never digitise a log-scale axis by eye.**
- **Check the sign.** A falling biomass is a negative BA. This is the single
  most common error, and it flips the direction of the EE correction.
- If the figure can't be read to one significant figure with confidence, leave
  the cell blank and say so. A blank BA is *unknown*, which is reviewable; a
  wrong BA quietly re-balances the model.

Whatever the source, write the form the paper states — absolute into
`Biomass accumulation (t/km^2/year)`, per-biomass into
`Biomass accumulation rate (/year)` — and do not convert between them. The
conversion needs B and would manufacture digits at B's rounding.
`massbalance_check.py` and `database_json.py` do the conversion internally for
their own arithmetic; that is the right place for it, because there the result
is never written into an import file.

If the paper is steady-state and says nothing about BA, the file stays blank and
`REPORT.md` says the paper was checked. `validate.py` warns on an entirely blank
file for exactly this reason — the warning is discharged by the report, not by
inventing values. A blank BA is not an assertion of steady state: Step 7 treats
it as unknown and says so.

## Step 5: assemble the extraction JSON, then write the files

Put the extracted values into one JSON file — the **extraction JSON**, shape
documented in `references/output-formats.md` — then:

```bash
python scripts/write_outputs.py model.json --outdir <extraction-set-dir>
```

`--outdir` is the *parent* — the top of the extraction set, defaulting to the
current directory. The writer creates
`<extraction-set-dir>/<model_number>_<model_name>_<model_year>` inside it and
prints that path on stdout, so the later steps can just use it:

```bash
d=$(python scripts/write_outputs.py model.json --outdir .)
python scripts/validate.py "$d"
```

Add `--zip` to get `<model_number>_<model_name>_<model_year>.zip` alongside the
directory, which is what to hand over when the files are going somewhere other
than the extraction set. The archive is a snapshot of the directory as it stands,
so zip on the *last* pass — after Steps 7 and 8 have put the database JSON, the
log and `REPORT.md` in there — not on the first. Re-running the writer is
idempotent, so `--zip` at the end costs nothing.

`--dir-name` overrides the derived name; use it only with a reason, and say what
the reason was in `REPORT.md`.

Set `model_number`, `model_name` and `model_year` in the JSON before running
the writer — without the first two it stops rather than inventing a name.
`model_name` should be the place alone (`North Sea`, not `North Sea 1981`),
though a year already trailing the name won't be repeated.

The writer exists so that formatting is never a judgement call: no quote
characters anywhere, CRLF line endings, numbers passed through as text so
`0.10` keeps its trailing zero, and derived cells (Sum, Total) computed in
decimal rather than binary floating point.

Blank and zero are different values. A key omitted or set to `null` writes an
empty cell; `0` writes a zero. This matters because EwE substitutes its own
default of **0.2** for a blank unassimilated-consumption cell on import — so a
blank has to be a decision you made, never a gap you didn't notice.

Keep `model.json` in the model directory. A correction pass edits it and re-runs
the writer, which is how a fix stays consistent across all eight files.

## EwE defaults and sanity ranges

Two different kinds of number live here, and conflating them is how a convention
ends up in the database wearing a paper's clothes.

**Defaults** are what the EwE software itself supplies when a field is left
empty. They matter twice over: a blank cell in our import files is not neutral,
because EwE will fill it; and a published table showing exactly the default
across every group is often the software's number being reported back rather
than a measured one.

**Sanity ranges** are the magnitudes the EwE literature treats as
physiologically plausible. They exist to help *recognise* a mis-parsed column,
never to fill a cell.

Neither kind is ever written into a file as though the paper had said it. Rule 2
below governs both.

### What EwE substitutes for a blank

| Field | EwE default | Source wording |
|---|---|---|
| Unassimilated consumption (GS) | **0.2**, all groups, energy-currency models | "For models whose currency is energy, the default is 0.20, i.e. 20% of consumption for all groups"; the User Guide adds "a default value of 0.2 is suggested for carnivorous fish groups if other estimates are not available" |
| GS, herbivores / zooplankton grazing phytoplankton | **0.4** suggested | "For zooplankton eating phytoplankton a value of 0.4 results in more detritus being produced" |
| Biomass accumulation (BA) | **0** | "The default value for BA is zero indicating no biomass accumulation" |
| Habitat area | **1** | "Default is that the group occurs in the total area" |
| Landings, discards, migration, prices | **0** | "the default value is 0" |
| Immigration / emigration | **0** — but EwE *estimates* net migration if B, P/B, Q/B and EE are all entered | User Guide, *Ecopath Input* |
| Diet `Import` | **0** | import is "treated as a 'prey' in the diet composition" and defaults to zero |
| Detritus fate | remainder **exported** | "If these fractions sum to less than 1, the remaining part of the surplus detritus will be exported out of the system" |

How this changes the work:

- **A blank GS cell becomes 0.2 on import.** Leaving it blank is a decision with
  a numeric consequence, so `REPORT.md` must say the paper was searched and
  stated nothing — not merely that the cell is empty.
- **A blank BA cell is unknown here, not zero.** EwE's own default is 0, but the
  database JSON writes `-9999`, and Step 7's INDETERMINATE verdict exists
  precisely because "the paper is steady state" and "the paper never said" are
  different claims. Never write `0` into `Biomass_accumulation.csv` on the
  strength of the software default.
- **A GS column reading 0.2 for literally every group** — producers and detritus
  included — is a sign the author accepted the default rather than
  parameterising per group. Extract the printed values as printed, and note the
  pattern in `REPORT.md`; it tells a later reader how much weight that column
  carries. The same goes for a habitat-area column of all 1s.
- **The 0.4 figure is EwE's suggestion**, for zooplankton grazing phytoplankton.
  The project's own rules in `references/parameter-conventions.md` — 0.4 only
  for unambiguously small zooplankton, 0.35 for zooplankton-like groups, blank
  for anything ambiguous — are narrower, and the project rules win.
- **Net migration is a thing EwE estimates**, so a paper that entered all four
  of B, P/B, Q/B and EE may be carrying an implicit migration term that
  `massbalance_check.py` does not model. That is one of the legitimate reasons
  Step 6 flags a correctly extracted group.

### Sanity ranges from the EwE literature

Use these in Step 3's one-row mapping check and when Step 6 flags something.

| Quantity | Plausible range | Note |
|---|---|---|
| P/Q (gross food-conversion efficiency, GE) | **0.1 – 0.3** for most consumers | "production/consumption ratios will range from 0.1 to 0.3"; positive respiration also requires P/Q < 1 − GS |
| R/B, fish | **1 – 10 /year** | "should as a rule be in the range 1-10 year⁻¹" |
| R/B, copepods | **~50 – 100 /year** | |
| P/B | equals **Z** at steady state (Allen 1971) | B/P read as mean longevity in years is the fastest sniff test |
| P/B, small zooplankton | ~45 /year (*Acartia tonsa*) | |
| P/B, large copepods | ~7 – 8 /year (*Calanus finmarchicus*) | |
| P/B, small pelagic fish | ~2.0 /year (anchovy) | |
| P/B, large demersal fish | ~0.25 /year (cod) | |
| P/B, pinnipeds | ~0.14 /year | |
| P/B, large whales | < 0.1 /year (blue whale ~0.025) | |
| EE, the classic starting point | **0.95** | "an EE of 0.95, based on Ricker (1968) was used for many groups in Polovina's original model" |
| EE, small heavily-preyed groups | approaching **1.0** | predation dominates other mortality |
| EE, phytoplankton in bloom systems | **≤ 0.5** | "phytoplankton simply die off (as 'snow')" |
| EE, kelps and seagrasses | **~0.1** | "hardly consumed when alive" |
| EE, apex predators under light fishing | low | |

A value outside its range is a prompt to re-render the page and re-check the
column mapping, in that order. It is not evidence the paper is wrong, and it is
never grounds for substituting a range midpoint.

Sources: EwE User Guide, *Ecopath Input*
(<https://pressbooks.bccampus.ca/eweguide/chapter/ecopath-input/>); EwE textbook
chapters *Mass balance*, *Ecotrophic efficiency*, *Production/biomass*
(<https://pressbooks.bccampus.ca/ewemodel/>).

## Step 6: validate, then investigate what it flags

```bash
python scripts/validate.py <model-dir>
```

This checks structure and arithmetic: group numbering contiguous and consistent
across files, diet columns summing to 1 within ±0.01, detritus fate rows summing
to 1, Totals matching their fleets, no quotes, CRLF throughout.

When a diet column comes back at 0.94, render the page and look at it:

```bash
pdftoppm -f 14 -l 14 -r 200 -png paper.pdf /tmp/page
```

Then check the numbers against the model's own equations:

```bash
python scripts/massbalance_check.py <model-dir>
```

This recomputes each group's EE from the diet matrix, biomasses, catches and
biomass accumulation
(`EE = (Y + BA + Σ_j B_j (Q/B)_j DC_ji) / (B (P/B))`), flags groups eaten faster than
they produce, checks that respiration comes out positive and gross efficiency is
sane, tests whether the detritus pools can balance, and catches consumers that
have a Q/B but no diet column — the error that unbalances a model without making
any single number look wrong.

Published models are balanced, so what this flags is usually an extraction error:
a Q/B read from the neighbouring column, a catch left in absolute tonnes, a diet
proportion under the wrong predator. Occasionally it's real — a paper reporting
migration terms this ignores, or pre-balance parameters alongside balanced ones.
Investigate, then record what you found. The sanity ranges above are how a flag
turns into a specific hypothesis about which column slipped.

Where `Biomass_accumulation.csv` is blank, an EE mismatch comes with the BA that
*would* close it, as an absolute rate and as a fraction of production. Treat that
as a prompt to go back to Step 4b, not as a value to enter: a plausible-looking
number the check suggested is not a number the paper stated, and writing it back
in would make the check validate its own guess.

Do **not** normalise the column to make the check pass. Published matrices do
contain rounding drift, and preserving it is correct; the check exists to make
you look, not to license editing. If the paper says 0.94, write 0.94 and note it
in `REPORT.md`.

## Step 7: build the database JSON

The eight import files are what the EwE importer reads. The **database JSON** is
what the downstream loader reads: one object per group, carrying the same numbers
in the shape the database expects.

```bash
python scripts/database_json.py -d <model-dir> --update-report
```

Into the same directory it writes
`<LME>_<model_number>_<model_name>_(<model_year>).json`,
`<...>_reconstructed.xlsx` (the round-trip workbook), `MASS_BALANCE.md` and
`ewe_conversion.log`.

Two JSONs live in the directory and they are not the same file. `model.json` is
the *extraction* JSON from Step 5 — what you typed, the input to
`write_outputs.py`. The database JSON is built from the eight CSV/XLSX files, not
from `model.json`, which is exactly what makes it useful: it round-trips the
files themselves, so a mistake made *by* the writer, or an edit made to a CSV by
hand afterwards, still shows up here.

`-j <database.json>` rebuilds only the workbook from a JSON that already exists.
`--ee-tol` sets the EE tolerance (default 0.05). `--update-report` replaces
`REPORT.md`'s `## Mass balance` section with the findings, appending the section
if the report has none — that is what fills that part of the Step 8 template.

Requires `pandas`, `numpy` and `openpyxl`.

### `-9999` means unknown

The database JSON writes `-9999` wherever the source states nothing and `0`
where the source states zero. The two are not interchangeable, and `-9999` is
never replaced by a value that is not in the files — an EwE software default
included. For biomass accumulation:

- a blank cell, or a missing `Biomass_accumulation.csv`, leaves **both**
  `biomass_accum` and `biomass_accum_rate` at `-9999`. Blank is unknown, never
  zero, and nothing is derived from nothing. EwE's BA default of 0 does not
  apply here: the database records what the paper stated, not what the software
  would assume in its absence.
- where the source states one of the two forms, that form is written through
  verbatim and the other is derived from B and logged as derived.
- the file's absolute column is per habitat area, so it is multiplied by the
  habitat area to match the JSON's `biomass` field, keeping
  `biomass_accum / biomass == biomass_accum_rate` as EwE holds it. Any scaling
  is logged.
- where both forms are stated they are cross-checked through B, the same check
  `validate.py` runs on the file.

`TL.xlsx` is located but not yet carried into the database JSON; trophic level
still lives only in the spreadsheet.

### Three verdicts

The script re-runs the mass-balance equations on the assembled model, using the
JSON's own `biomass` field, so biomass, catch and BA are all on the model-area
basis rather than the habitat-area basis `massbalance_check.py` uses. On a model
with habitat areas of 1 the two agree to three or four significant figures;
where they differ, this one is the one that matches what EwE will build.

- **BALANCED** — nothing failed and nothing was undecidable.
- **INDETERMINATE** — no failures, but at least one group's EE does not
  reconcile and its BA is unknown. The gap could be an extraction error or the
  BA the paper never printed, and the arithmetic cannot tell which.
- **NOT BALANCED** — a group with a *known* BA consumes more than it produces,
  or a P/Q implies non-positive respiration, or the detritus pools cannot close.

A group that reconciles without BA is reported as *consistent with* steady state,
which is not the same as being shown to be steady state. Every indeterminate
line names the BA that would close its gap: that is a prompt to go back to
Step 4b, never a value to enter. A BA this check suggested and then validated
itself against would prove nothing.

The verdict stays out of the JSON deliberately — it is a property of the
extraction, not of the model EwE loads — and lives in the log and
`MASS_BALANCE.md` only.

## Step 8: write REPORT.md and update MASTER_INDEX.md

The report is what makes the extraction reviewable a year later. For each
parameter that was not read directly off a table, record where it came from.
Template and required sections are in `references/output-formats.md`; the
`## Mass balance` section is filled by Step 7's `--update-report`.

The defaults make two further things reportable, and so required:

- every field left blank where EwE has a default — GS above all — with the note
  that the paper was searched and stated nothing, so a reader knows the 0.2 EwE
  will import is the software's number and not the author's;
- any extracted value that coincides with a documented default (GS 0.2 or 0.4,
  habitat area 1, BA 0), saying whether the paper stated it or it merely looks
  that way.

## The four rules that override convenience

1. **Numbers match the source exactly.** No recomputation, no rounding, no
   tidying of sums that don't quite reach 1.
2. **Blank is a value.** Never fill a blank with a convention, a default, or a
   value borrowed from a similar group, unless the paper tells you to — and then
   say so in the report. That includes the EwE software defaults above: knowing
   EwE would supply 0.2 or 0 is a reason to *report* the blank, never a reason
   to fill it. In the database JSON a blank is `-9999`, meaning unknown, and it
   is never quietly read as zero.
3. **Provenance stays distinguishable.** A reader must be able to tell a
   paper-stated number from a convention-derived one. The files can't carry that
   distinction, so `REPORT.md` must.
4. **When the paper is ambiguous, leave it blank and flag it.** An honest gap
   costs one line in the report; a confident guess corrupts the database.

## Reference files

- `references/ecopath-model.md` — the mass-balance equations, what each
  parameter means, balance criteria, magnitude ranges, and which published values
  are model outputs. Read when a value looks wrong or a blank looks odd.
- `references/pdf-extraction.md` — bbox extraction, `pdfgrid.py` usage,
  `merge_gap` tuning, rotated pages, troubleshooting. Read before Step 2.
- `references/table-layouts.md` — mapping an unfamiliar table to EwE fields:
  header vocabulary, layout patterns, in-cell notation, units. Read before
  Step 3.
- `references/prose-extraction.md` — footnote pointers, the prose sweep, diets
  and rates stated in text, reading a value off a figure, table-vs-text
  conflicts. Read before Step 4.
- `references/parameter-conventions.md` — what each EwE parameter is, where it
  hides in these papers, the unassimilated-consumption conventions, and the
  biomass-accumulation rules. Read alongside Step 4. Where its conventions are
  narrower than the software suggestions in **EwE defaults and sanity ranges**,
  its rules are the ones that apply.
- `references/output-formats.md` — exact column specs for all eight files, the
  extraction JSON schema, and the `REPORT.md` / `MASTER_INDEX.md` templates.
  Read before Step 5.
- `assets/templates/` — the reference templates (`T*.csv`, `T*.xlsx`) from the
  `13-north-*` example. Headers must match these verbatim; `aaa`/`bbb`/`ccc`/
  `ddd` are placeholders showing shape.

## Scripts

- `scripts/pdfgrid.py` — column-aware table extraction from word bounding boxes.
- `scripts/prose_sweep.py` — finds footnote pointers and prose-stated parameters.
- `scripts/write_outputs.py` — extraction JSON → the eight files, formatting
  enforced, written into a `<model_number>_<model_name>_<model_year>` directory
  it names and creates itself (`--zip` to archive it).
- `scripts/validate.py` — structural and arithmetic checks on a finished model.
- `scripts/massbalance_check.py` — checks the extracted numbers against the
  Ecopath equations.
- `scripts/database_json.py` — the eight files → the database JSON and the
  round-trip workbook, with the mass-balance verdict and `MASS_BALANCE.md`.

All six run standalone with `--help`. They need `poppler-utils` (`pdftotext`,
`pdftoppm`, `pdfinfo`), `qpdf` for rotated pages, `openpyxl` for the
spreadsheets, and `pandas` + `numpy` for `database_json.py`.