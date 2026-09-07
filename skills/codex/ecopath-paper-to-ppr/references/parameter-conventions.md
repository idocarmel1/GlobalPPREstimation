# Parameter conventions

Contents: [The fields](#the-fields) · [Blank, zero, and default](#blank-zero-and-default) ·
[Unassimilated consumption](#unassimilated-consumption) · [Diet](#diet) ·
[Catch](#catch) · [Detritus](#detritus) ·
[Biomass accumulation](#biomass-accumulation) · [Provenance](#provenance)

## The fields

`Basic_input.csv` columns, and what each one is:

| Column | Meaning | Typical range | Notes |
|---|---|---|---|
| Hab area (proportion) | fraction of the model area the group occupies | 1 | extract a stated value; otherwise leave blank unless an explicit project convention authorises 1 and document it |
| Biomass in habitat area (t/km^2) | B, wet weight per unit habitat area | 1e-4 – 1e2 | blank is legitimate when the author let Ecopath estimate B from EE |
| Total mortality (/year) | Z | 0.01 – 20 | only if the paper gives Z as such |
| Production / biomass (/year) | P/B | 0.01 – 400 | equals Z in a steady-state model, but only enter it in both columns if the paper says so |
| Consumption / biomass (/year) | Q/B | 1 – 1000; 0 for producers | leave blank for primary producers and detritus, not 0 |
| Ecotrophic Efficiency | EE, fraction of production used in the system | 0 – 1 | often the estimated parameter; blank when B was given |
| Other mortality | 1 − EE | 0 – 1 | rarely tabulated; don't compute it if the paper doesn't |
| Production / consumption | P/Q, gross efficiency | 0.05 – 0.3 for fish | if the paper gives P/B and Q/B, enter those and leave P/Q blank rather than deriving it |
| Unassim. consumption | GS, fraction of intake not assimilated | 0.2 typical, 0.4 zooplankton | see below — the most commonly mis-handled field |
| Detritus import (t/km^2/year) | detritus entering from outside | usually blank | |

`TL.xlsx` carries trophic level per group; extract the paper's own TL values
rather than computing them, since a computed TL depends on the diet matrix and
would no longer be the paper's statement.

Ecopath needs exactly three of {B, P/B, Q/B, EE} per group to solve for the
fourth, so a blank in one of these is usually deliberate. Don't fill it.

## Blank, zero, and default

This distinction is the one that most affects downstream data quality:

- **Blank** = the paper does not state a value. On import, **EwE substitutes its
  own default — 0.2 for unassimilated consumption**. So a blank is not neutral;
  it silently becomes a number.
- **Zero** = the paper states zero. Write `0`.
- **A convention you applied** = a number that is yours, not the paper's. It goes
  in the file *and* in the report, named as a convention.

Because all three end up looking like data in the CSV, the report is the only
place the difference survives. Write it there every time.

### EwE software defaults

These values describe what EwE may supply on import; they are not evidence that
the paper stated the value.

| Field left blank | EwE behavior |
|---|---|
| Unassimilated consumption (GS) | defaults to 0.2 in energy-currency models; 0.4 is suggested for zooplankton grazing phytoplankton |
| Biomass accumulation (BA) | defaults to 0 |
| Habitat area | defaults to 1 |
| Landings, discards, migration, prices | default to 0 |
| Diet `Import` | defaults to 0 |
| Detritus fate | any remainder is exported |

Record the relevant consequence of a blank in `REPORT.md`. Keep the extraction
cell blank and the database JSON value at `-9999` unless the source states a
number or an explicitly authorised project convention applies. A printed value
that matches a default is still extracted, with its provenance noted.

## Unassimilated consumption

Sources, in order of preference:

1. **A value in the table.** Extract it.
2. **A value or an assimilation efficiency in the prose.** Very common — search
   for it explicitly (`prose_sweep.py --family assimilation`). An assimilation
   efficiency of 80% means an unassimilated fraction of 0.2; record the
   derivation.
3. **The project convention**, applied only under the conditions below.

The convention, and its limits:

- **0.4 applies only to small zooplankton.** Not to zooplankton generally, not to
  "mesozooplankton" or "macrozooplankton", not to a pooled "zooplankton" group.
  Only to a group that is unambiguously small zooplankton.
- **0.35** — the midpoint of the 0.3–0.4 range used for zooplankton-like groups —
  applies only where the group name makes the identification unambiguous.
- **Anything ambiguous stays blank.** A group called "Zooplankton", "Plankton",
  "Invertebrates", or "Other pelagics" does not get a convention value. Leave it
  blank and note it.

The reason for the asymmetry: a blank leaves a visible gap that the report names
and a reviewer can resolve in a minute. A convention applied to the wrong group
produces a number indistinguishable from data.

## Diet

`Diet_composition.csv` is prey rows × consumer columns, with three trailing rows:

- **`Import`** — the diet fraction taken outside the model area. Enter what the
  paper gives; `0` where it gives none.
- **`Sum`** — the column total including import, as computed from the values
  actually entered. Published matrices often land at 1.0002 or 0.9997 from
  rounding; that drift is preserved, not corrected.
- **`(1 - Sum)`** — written as `0` across the row, matching the reference export.

Rules:

- Columns exist for consumers only. Primary producers and detritus get no column.
- A blank cell means that prey isn't in that predator's diet.
- Never normalise a column to make it reach 1.0. If it doesn't, either the
  extraction is wrong (check the page) or the paper is like that (note it).
- Cannibalism (the diagonal) is real and gets extracted as given.
- Diets described only in prose still belong in the matrix — see
  `prose-extraction.md`.

## Catch

`Landings.csv` and `Discards.csv` share a shape: group rows, one column per
fleet, then `Total`.

- Fleet names come from the paper. If it reports a single undifferentiated
  fishery, use one column with the paper's own name for it.
- If only total catch is given, put it in Landings and record that discards
  weren't separated. Don't split by assumption.
- Discard rates stated as a proportion of landings need the arithmetic carried
  out; record the rate, the source page, and the result.
- Units: t·km⁻²·year⁻¹. Absolute catches need the model area, which is usually
  stated only in the prose.

## Detritus

`Detritus_fate.csv` gives, for each group, the proportion of its detritus going
to each detritus group, plus `Export`. Rows sum to 1.

Most papers don't tabulate this; the common case is a single detritus group
receiving everything, which the methods state in a sentence. Where a model has
several detritus pools (pelagic and benthic detritus, fishery offal, and so on),
the split is model-specific — extract it from wherever the paper states it, and
leave rows blank rather than assuming a split.

## Biomass accumulation

`Biomass_accumulation.csv` holds BA per group, in whichever of the two forms the
paper printed:

| Column | Meaning | Typical range |
|---|---|---|
| Biomass accumulation (t/km^2/year) | absolute BA | −0.5 to 0.5 for fish; scales with B |
| Biomass accumulation rate (/year) | BA/B | −0.6 to 0.6; rarely beyond ±1 |

Rules:

- **Set at most one of the two per group.** They differ by a factor of B, and
  converting would put B's rounding into a number that then looks tabulated.
  `massbalance_check.py` converts internally where it needs to, which is safe
  because that result is never written anywhere.
- **The sign is load-bearing.** Negative BA = the stock was being drawn down
  over the model year. It raises the printed EE relative to a steady-state
  recomputation; positive BA lowers it. Getting the sign wrong is worse than
  leaving the cell blank, because it moves the check in the wrong direction and
  makes a correct extraction look broken.
- **Blank means unknown**, not zero and not an assertion of steady state. Most
  models in this corpus appear to use steady-state BA = 0, but the extraction
  records what the source states. `validate.py` warns on a wholly blank file so
  the report must record where BA was searched for and whether steady state was
  explicitly stated.
- **A qualitative statement is not a value.** "The stock declined over the
  period" gets recorded in `REPORT.md` and left blank, the same way "mainly
  copepods" does not become 0.7.
- **Percentages are rates.** "biomass increased by about 5% per year" → 0.05 in
  the rate column. A tonnage or a t·km⁻²·y⁻¹ figure goes in the absolute column.
- **A slope taken off a biomass series is a derivation**, not a reading. Record
  the endpoints, the years, and the arithmetic. Same for anything digitised off
  a figure, plus the precision the figure supports — see
  `prose-extraction.md`.

BA is also the reason a published, balanced model can fail an EE check
legitimately: the identity is `B(P/B)EE = Y + BA + predation`, so a model with
BA terms and a blank BA file will show every one of those groups as a warning.
Fill the file and the warnings resolve; that resolution is itself a check that
the rest of the extraction is right.

## Provenance

Four categories, all of which must be distinguishable in `REPORT.md`:

1. **Tabulated** — read off a table. Cite table and page.
2. **Prose-derived** — stated in the text, possibly with one arithmetic step.
   Cite the page and show the step.
3. **Model-estimated** — parenthesised or otherwise marked as an Ecopath output
   in the source. Still extracted, but flagged.
4. **Convention-derived** — the 0.35/0.4 rules, or any other value not from the
   paper. Named as such.

A number whose category can't be determined is a number to leave out.
