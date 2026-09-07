# Meeting a table layout you haven't seen before

Contents: [The premise](#the-premise) · [Map before you extract](#map-before-you-extract) ·
[Header vocabulary](#header-vocabulary) · [Layout patterns](#layout-patterns) ·
[Notation inside cells](#notation-inside-cells) · [Units](#units) ·
[When mapping is genuinely ambiguous](#when-mapping-is-genuinely-ambiguous) ·
[Recording the layout](#recording-the-layout)

## The premise

Every paper in this corpus lays its tables out differently: different column
order, different names for the same parameter, different conventions for marking
computed values, different languages, tables split across pages, tables rotated,
tables with two header rows. There is no template to match against.

So the failure mode to guard against is *pattern completion*: assuming the
fourth numeric column is Q/B because it was Q/B in the last three papers. The
fix is a mapping step that happens before any value is read, and that gets
written down.

## Map before you extract

Work through this before extracting a single number from an unfamiliar table.

1. **Read the caption and every footnote in full**, including the ones in
   smaller type below the rule. The caption says what the table contains; the
   footnotes say which cells are exceptions. Footnotes that point into the text
   are the subject of `prose-extraction.md` — handle them there, but read them
   now, because they determine which cells you should *not* try to read off the
   table.

2. **Write down the column mapping explicitly** — paper's header → EwE field —
   before extracting. Even a scratch note is enough; the point is to commit to
   an interpretation you can check rather than deciding column by column while
   reading numbers. Anything you can't map confidently goes in the report as an
   open question rather than into a plausible-looking slot.

3. **Confirm the mapping against a row you can verify independently.** Pick a
   group where the paper also states a value in the text or where the arithmetic
   is checkable: P/Q should equal (P/B)/(Q/B); Z should be ≥ P/B for a group
   with fishing mortality; EE is a fraction in [0, 1]. If the mapping is wrong,
   these relationships break immediately, which is exactly why they're worth
   checking on one row before extracting forty.

4. **Establish the row identity.** Rows are keyed by group name, and the paper's
   group names may not match your group list from the basic input table (a
   species name in one table, a functional group in another). Match rows by
   name, never by position — a table that omits the non-consumer groups will
   otherwise shift every diet column.

5. **Count.** Rows in the table vs groups in your list; numeric columns vs
   consumers expected. A discrepancy here almost always means a continued table,
   a merged row, or a group you mis-split — resolve it before extracting.

## Header vocabulary

The same parameter appears under many names. This list is a starting point, not
a lookup table to apply mechanically — confirm against the caption and the
arithmetic checks above.

| EwE field | Also written as |
|---|---|
| Biomass | B, Biomass in habitat area, Biomasse, Standing stock, B (t/km²), B (t·km⁻²) |
| Total mortality | Z, Total mortality, Mortalité totale, Z (year⁻¹) |
| Production / biomass | P/B, PB, P/B ratio, Production rate, Turnover, Prod./biom., Z (when the author states P/B = Z) |
| Consumption / biomass | Q/B, QB, Consumption rate, Cons./biom., Ration, Q/B (year⁻¹) |
| Ecotrophic efficiency | EE, Ecotroph. eff., EE (0–1), Efficacité écotrophique |
| Production / consumption | P/Q, GE, Gross efficiency, Gross food conversion efficiency, GCE, Production/consommation |
| Unassim. consumption | GS, U, Unassimilated food, Unassim./cons., 1 − assimilation efficiency, Egestion, Non assimilé |
| Detritus import | Import, Detritus import, Immigration (check — immigration may mean biomass immigration instead) |
| Landings | Catch, Catches, Yield, Y, Débarquements, Captures |
| Discards | Discards, Rejets, By-catch discarded |
| Trophic level | TL, Trophic level, Niveau trophique |

Two traps worth naming:

- **P/B vs Z.** Many papers give a single column labelled Z and state in the
  methods that P/B was set equal to Z. That is a *stated equivalence*, not
  something to assume: if the paper doesn't say it, don't map Z into P/B.
  Basic_input.csv has separate columns for both — use the one the paper gives,
  and record which.
- **Gross efficiency direction.** GE/P/Q is production over consumption. Some
  papers tabulate its inverse or the assimilation efficiency next to it in a
  similar-looking column. Check the magnitude: P/Q is typically 0.05–0.3 for
  fish; an "efficiency" column sitting around 0.8 is assimilation, not P/Q, and
  its complement (0.2) is the unassimilated fraction.

## Layout patterns

| Pattern | How to recognise it | How to handle |
|---|---|---|
| **Continued table** | row count short; "cont.", "(continued)", "suite" in the caption; last row mid-alphabet | extract both parts, concatenate, then re-check counts. A diet matrix continued on the facing page is the single most common cause of columns summing to ~0.5 |
| **Split by column block** | predators 1–20 on one page, 21–38 on the next, same prey rows | extract as two grids, join on prey row label — not on row index, since blank rows may be dropped in one half |
| **Two-row header** | group numbers on one line, names on the line above | anchor the grid on the line with the *numbers* (`--anchor-line` at that line index); read names from the other line separately |
| **Stacked sub-columns** | one header spanning "mean / range" or "adult / juvenile" pairs | treat as separate columns; decide explicitly which one feeds the file, and record the choice |
| **Transposed table** | parameters as rows, groups as columns | extract as-is and transpose in code; don't try to read it in the target orientation |
| **Rotated page** | landscape table in a portrait PDF | rotate physically with `qpdf` first (see `pdf-extraction.md`) |
| **Multi-line group names** | one group's name wrapped over two lines, numbers on the first | the second line becomes a row with a label and no values — merge it into the preceding row, don't let it become a group |
| **Group with an aggregate row** | "Total", "Sum", "All fish", "Autres" | not a group; exclude from the group list, but use it as a check on the values above it |
| **Diet matrix as prey lists** | no matrix; text or table gives each predator's prey with percentages | this is prose extraction — see `prose-extraction.md` |
| **Fleet-disaggregated catch in one column** | landings and discards in a single "catch" column | do not split by assumption; if the paper gives only total catch, put it in Landings and record that discards were not separated |

## Notation inside cells

Cell contents in these papers carry meaning beyond the number:

| Notation | Usual meaning | What to do |
|---|---|---|
| `(0.95)` parentheses | value estimated by Ecopath, not input by the author | the caption almost always says which; extract the number, and record in the report that it was model-estimated rather than observed |
| **bold** or *italic* | same as above, or "value adjusted for balance" | check the caption; if unexplained, note the ambiguity |
| `0.95¹`, `0.95*`, `0.95 a` | footnote marker | read the footnote before extracting — it may redirect to the text |
| `—`, `–`, `n.a.`, `nd`, `.` | not applicable / not available | leave the cell blank, not zero |
| `0` | a stated zero | write `0`. Distinct from blank: EwE reads blanks as defaults |
| `<0.001`, `tr`, `+` | below detection / trace | leave blank and note it, or use the stated bound if the paper defines one — never silently substitute 0 |
| `2,4` (comma decimal) | 2.4 in francophone papers | convert the separator, and check you haven't converted a thousands separator |
| `1 234` (space thousands) | 1234 | strip the space |
| Empty cell in a diet matrix | prey not eaten by that predator | leave blank (equivalent to 0 for diet, but preserve the paper's own convention) |

## Units

Ecopath wants biomass in t·km⁻² wet weight and rates per year. Papers deviate:

- **Area basis**: t·km⁻² vs t per whole shelf vs kg·ha⁻¹ (÷10 for t·km⁻²). If a
  paper reports absolute tonnes, the model area appears in the methods — apply
  it, and record the conversion and the area used.
- **Wet vs dry weight vs carbon**: conversion factors are model-specific. Only
  convert if the paper states the factor; otherwise extract as given and flag it.
- **Rate basis**: per day for plankton groups (×365 for per year). A P/B of 0.11
  for phytoplankton is a daily rate that will be nonsense as an annual one.
- **Seasonal or per-quarter values**: check whether they should be summed or
  averaged; the methods will say. If they don't, flag it rather than choosing.

Every conversion applied goes in the report with the factor used, because a
converted number is no longer the paper's number.

## When mapping is genuinely ambiguous

If a column can't be mapped confidently after all of the above, leave the
corresponding cells blank and record the ambiguity in the report — specifically
naming the column, the candidate interpretations, and why they couldn't be
separated. Blank is recoverable by a human reading one page; a wrong mapping
propagates through the whole model and is nearly invisible afterwards.

The same applies to a table whose structure you can partially read: extract the
part you're sure of, leave the rest blank, and say so. A model that is 80%
extracted and honest about which 20% is missing is far more useful than one
that's 100% populated and wrong somewhere unmarked.

## Recording the layout

`REPORT.md` gets a short section per source table:

```markdown
### Table 3 (p. 47) — basic input
Columns as printed: Group | B | Z | Q/B | EE | GE
Mapped to: name | biomass | z | qb | ee | pq
P/B: not tabulated; methods (p. 45) state P/B = Z for all groups — used Z column for both.
Parenthesised values (7 cells): Ecopath-estimated per caption; extracted as given.
Units: t km-2 wet weight, annual rates — no conversion applied.
Rows: 41 in table, 41 in group list.
```

This is what makes a re-check cheap and a correction pass possible. Write it
while the table is in front of you, not afterwards from memory.
