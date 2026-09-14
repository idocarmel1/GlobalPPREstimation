# Extracting values from prose

Contents: [Why the tables aren't enough](#why-the-tables-arent-enough) ·
[Footnote pointers](#footnote-pointers-the-highest-value-signal) ·
[The sweep](#the-sweep) · [What hides where](#what-hides-where) ·
[Reading a passage into a value](#reading-a-passage-into-a-value) ·
[Diets stated in prose](#diets-stated-in-prose) ·
[Percentages and complements](#percentages-and-complements) ·
[Conflicts](#conflicts) · [Recording it](#recording-it)

## Why the tables aren't enough

A table looks complete. That's the whole problem: a blank cell reads as "no
value exists" when it often means "the value is in the methods section". In this
corpus, parameters that routinely appear only in prose include the
unassimilated-consumption fraction, the diets of microbial and plankton groups,
discard rates expressed as a proportion of landings, the model area used for
converting absolute catches, and the assumptions behind any value the author
"took from" another model.

Extraction is therefore not done when the tables are transcribed. It's done when
the prose has been swept as well.

## Footnote pointers: the highest-value signal

When a caption or footnote says *"see text"*, *"as described in the text"*,
*"explained in the text"*, *"voir texte"*, or *"see Methods"*, the author is
telling you directly that the table is incomplete and where the rest is. Treat
every such pointer as a mandatory follow-up with a specific question attached:
*which cells does this pointer cover, and what does the text say about them?*

Do not extract the table and defer the pointer. Resolve it first, because it
changes which cells you should even try to read — a footnote may reveal that
the blank column is not missing data but data stated per-group in a paragraph
three pages earlier.

Related pointer types worth chasing:

- *"Values in parentheses were estimated by Ecopath"* — changes provenance of
  those cells, even though the numbers are on the table.
- *"Sources as in Table 2"* / *"as in Jarre-Teichmann (1992)"* — the value's
  origin, needed for the report.
- *"Adjusted to balance the model"* — the number is an output of balancing, not
  an observation.
- *"For details see section 3.2"* — a section pointer, same obligation.
- Superscript letters or daggers attached to individual numbers — always read
  the note before extracting that number.

If a pointer can't be resolved (the referenced text genuinely doesn't contain
the value, which happens), leave the cell blank and record the unresolved
pointer in the report. That is a real finding, not a failure.

## The sweep

`scripts/prose_sweep.py` makes this mechanical:

```text
# start here: every pointer in the paper, in one pass
python <skill-root>/scripts/prose_sweep.py <paper.pdf> --family pointers

# the full sweep, restricted to sentences containing numbers
python <skill-root>/scripts/prose_sweep.py <paper.pdf> --numbers-only

# chase one thing with surrounding context
python <skill-root>/scripts/prose_sweep.py <paper.pdf> --family assimilation --context 2

# group-specific hunting
python <skill-root>/scripts/prose_sweep.py <paper.pdf> --terms "phagotroph,ciliate,bacteria"
```

Families: `pointers`, `assimilation`, `diet`, `rates`, `biomass`, `catch`,
`detritus`, `trophic`, `provenance`. Pointer hits are always reported, even
under `--numbers-only`, because a pointer sentence usually contains no number.

The script reports candidate passages, not values. Every hit gets read in
context on the page before anything is extracted from it — the sweep is there
to guarantee coverage, not to do the reading.

Two habits make it reliable:

- Run it on the **whole chapter**, including the introduction and the discussion.
  Assumptions get restated in discussions, sometimes with the number that the
  methods omitted.
- Run it **again after the tables are extracted**, with the list of blank cells
  in hand. The second pass is targeted — searching for the group names whose
  cells are still empty — and it catches what a generic sweep misses.

## What hides where

| Parameter | Typical prose form |
|---|---|
| Unassimilated consumption | "assimilation efficiency was assumed to be 80%" → 0.2; "unassimilated fraction of 0.4 was used for zooplankton". Search *assimilat*, *unassimilat*, *egest*, *GS*, *faeces* |
| Diet of plankton / microbial groups | full sentences describing who eats whom, often with percentages; see below |
| Discards | "discards were estimated as 30% of landings" — a rate to apply, not a value to copy |
| P/B, Q/B for a few groups | "for [group], P/B was taken from [other model]" where the table has a blank |
| Biomass | "biomass was estimated by swept-area analysis"; sometimes the only place an absolute-to-density conversion is stated |
| Model area | needed whenever catches are in absolute tonnes; usually stated once, in the study-area section |
| Detritus fate / export | "detritus not consumed was assumed to be exported" |
| EE assumptions | "EE was assumed to be 0.95 for groups without biomass estimates" — a default the author applied deliberately, which is very different from a blank |
| Cannibalism | often removed or capped in the text while remaining in the matrix |

## Reading a passage into a value

Prose is looser than a table, so pin down four things before writing a number:

1. **Which groups does it cover?** "for all fish groups" is scoped; "for fish"
   might not include elasmobranchs the paper treats separately. If the scope
   can't be resolved to specific groups in your list, apply it only to the
   groups it unambiguously names and flag the rest.
2. **Is it a value or a rate to apply?** "discards were 30% of landings" needs
   the landings to produce a number; carry the arithmetic out and record it.
3. **Is it an assumption or a measurement?** Both are extractable, but they go
   in the report differently.
4. **Does it override the table, or fill a gap?** If the table has a value and
   the text has a different one, see [Conflicts](#conflicts).

Where prose gives an assimilation efficiency, the unassimilated fraction is its
complement: 80% assimilation → 0.2 unassimilated. Write the complement, and note
in the report that it was derived from a stated assimilation efficiency.

## Diets stated in prose

Microbial-loop and plankton groups are usually described narratively rather than
in the matrix, and those statements are data: "ciliates were assumed to feed
entirely on bacteria" is a diet composition of 1.0 on the bacteria group.

Converting prose diets:

- Map each named prey to a group number in your list. If the prose names a prey
  that isn't a group (e.g. "detritus of pelagic origin" when the model has one
  pooled detritus group), map it explicitly and record the mapping.
- "entirely", "exclusively" → 1.0. "mainly", "predominantly", "chiefly" are
  **not** numbers — do not turn them into 0.7 or 0.8. If the paper gives no
  proportion, leave the predator's diet blank and record that the diet was
  described only qualitatively.
- Where percentages are given for some prey but not all, enter what's stated and
  leave the remainder blank rather than distributing it. A column that sums to
  0.6 with a report line explaining why is honest; a column normalised to 1.0 by
  invention is not.
- Prose diets that don't sum to 1 will trip `validate.py`. That's correct
  behaviour — annotate it in the report rather than adjusting the numbers.

## Percentages and complements

Prose numbers frequently need one arithmetic step, and each step is a chance to
introduce an error that no check will catch:

| Prose says | Value |
|---|---|
| "assimilation efficiency 80%" | unassimilated = 0.2 |
| "20% of consumption is not assimilated" | unassimilated = 0.2 |
| "discards are 30% of the catch" | discards = 0.3 × catch; landings = 0.7 × catch |
| "discards are 30% of landings" | discards = 0.3 × landings (a different number) |
| "60% of the diet was bacteria" | diet proportion = 0.6 |
| "biomass of 240 t over the 100 km² shelf" | 2.4 t·km⁻² |

Write down the arithmetic in the report, not just the result. "0.2 (from 80%
assimilation, p. 45)" is checkable; "0.2" is not.

## Conflicts

When a table and the text disagree, or two passages disagree:

- Prefer the table for tabulated parameters — it's the author's structured
  statement — **unless** a footnote points to the text for that cell, in which
  case the text wins by the author's own instruction.
- Prefer the methods over the discussion for assumptions.
- Prefer the later, more specific statement over an earlier general one when the
  paper explicitly revises it ("for cod, however, P/B was set to...").
- Record both values and the choice made, every time. This is the single most
  useful thing in a report during a correction pass, because the alternative
  reading is already written down and doesn't have to be rediscovered.

Never average conflicting values, and never pick the one that balances better.

## Recording it

Every prose-derived value gets a line in `REPORT.md` under a dedicated section,
with the page and the reasoning:

```markdown
### Values from prose
- Unassim. consumption 0.2 for all fish groups (1–18, 22–29): complement of the
  80% assimilation efficiency stated on p. 45.
- Unassim. consumption 0.4 for Small zooplankton (19): stated directly, p. 45.
- Unassim. consumption blank for Meiofauna (30): the p. 45 statement covers
  "fish and zooplankton" only; no value found. EwE will default this to 0.2.
- Diet of Ciliates (20): 1.0 on Bacteria (21), stated p. 46 ("feed entirely on
  bacteria"). Not in Table 4.
- Diet of Heterotrophic flagellates (21): 0.6 Bacteria, 0.4 Picophytoplankton,
  stated p. 46.
- Discards: 0.3 x landings per fleet, rate stated p. 51; arithmetic applied,
  landings from Table 6.
- Unresolved pointer: Table 3 footnote b ("see text") for the EE column —
  no corresponding statement located anywhere in the chapter. EE left blank
  for the 6 affected groups.
```

The last entry matters as much as the others. A named gap is a finding; a
quietly filled one is a defect.


## Reading a value off a figure

Sometimes the only statement of a parameter is a graph — most often a biomass
time series that implies a biomass accumulation term, occasionally a flow
diagram with a labelled box. This is the weakest source in the hierarchy and the
report has to name it as such.

Render high, then read from the axes:

```text
python <skill-root>/scripts/render_pdf_page.py <paper.pdf> 12 --dpi 300 --outdir <work-dir>
```

300 dpi, not 150 — at 150 dpi a tick label and a curve are the same few pixels.

- Work from labelled gridlines. Interpolating between two ticks is acceptable;
  extrapolating past the last one is not.
- **Write only the precision the figure supports**, which is one or two
  significant figures. `0.2` read off a graph must not become `0.23`: the extra
  digit is indistinguishable from a tabulated value once it is in a CSV, and
  that is precisely the distinction this project exists to preserve.
- Check the sign against the direction of the curve, and say in the report which
  way it went. For a biomass series, falling means negative BA.
- Don't digitise a log axis by eye.
- If one significant figure isn't reachable with confidence, the value is not
  there. Leave it blank and record that the figure was read and found
  unreadable — that is a finding, and a reviewer can go and look.

A derived value — a slope between two years, a difference of two endpoints —
carries the endpoints and the arithmetic into `REPORT.md`, never just the
result.
