# Ecopath: the model behind the numbers

Contents: [What the model is](#what-the-model-is) ·
[Master equation 1](#master-equation-1-production) ·
[Master equation 2](#master-equation-2-energy-balance-within-a-group) ·
[Three of four](#three-of-four) · [Derived quantities](#derived-quantities) ·
[Balance criteria](#balance-criteria) · [Detritus](#detritus) ·
[Fisheries](#fisheries) · [Magnitude ranges](#magnitude-ranges) ·
[Beyond Ecopath](#beyond-ecopath-what-the-papers-may-also-report) ·
[Why this matters for extraction](#why-this-matters-for-extraction)

Read this if you're unsure what a parameter *is*, why a value looks wrong, or
which cells in a paper are inputs versus model outputs. Knowing the equations
turns vague unease about a number into a specific arithmetic check.

## What the model is

Ecopath represents a food web as a set of functional groups over a defined area
and a defined period — usually one year — assumed to be in mass balance: what
each group produces is accounted for by what eats it, what fishes it, what it
exports, and what dies of other causes.

It is a **static snapshot**, solved as a system of linear equations, one per
group. It is not a simulation. Ecosim adds time dynamics on top of a balanced
Ecopath model; Ecospace adds space. The models in this corpus are Ecopath
parameterisations — the mass-balance snapshot is the thing being extracted.

The usual biomass convention in this corpus is **t·km⁻² wet weight**, with
**year⁻¹** rates and t·km⁻²·year⁻¹ flows. Confirm each source's units; some
models use carbon, dry biomass or energy. Record any conversion explicitly.

## Master equation 1: production

For every group *i*, production is fully accounted for:

```
production = catch + predation + net migration + biomass accumulation + other mortality
```

```
B_i · (P/B)_i = Y_i  +  Σ_j [ B_j · (Q/B)_j · DC_ji ]  +  E_i  +  BA_i
                     +  B_i · (P/B)_i · (1 − EE_i)
```

| Symbol | Meaning |
|---|---|
| `B_i` | biomass of group *i* (t·km⁻²) |
| `(P/B)_i` | production per unit biomass (year⁻¹); equals total mortality *Z* under the steady-state assumption |
| `Y_i` | total fishery catch rate = landings + discards (t·km⁻²·year⁻¹) |
| `DC_ji` | fraction of prey *i* in the diet of predator *j* |
| `EE_i` | ecotrophic efficiency: the fraction of production used within the system (predation + fishing + export) |
| `E_i` | net migration (emigration − immigration) |
| `BA_i` | biomass accumulation over the period |
| `(1 − EE_i)` | the "other mortality" fraction — death by anything not predation, fishing or export |

Written per unit biomass, the same equation is a mortality budget:

```
(P/B)_i  =  M2_i  +  F_i  +  M0_i      ( + migration and accumulation terms )
```

with predation mortality `M2_i = Σ_j B_j (Q/B)_j DC_ji / B_i`, fishing mortality
`F_i = Y_i / B_i`, and other mortality `M0_i = (P/B)_i (1 − EE_i)`.

Here `M0_i` is a rate. The repository calculator's `model.M0` attribute is instead
the flow `B_i * (P/B)_i * (1-EE_i)`. Natural mortality in an article can also include
predation. Read `references/mortality-and-discards.md` before comparing those values
or changing a source parameter.

Rearranged, this gives the check that catches most extraction errors:

```
EE_i  =  ( Y_i + Σ_j B_j (Q/B)_j DC_ji )  /  ( B_i (P/B)_i )
```

`scripts/massbalance_check.py` computes exactly this from the extracted files. A
group whose recomputed EE lands above 1 is being eaten faster than it produces —
either the model was never balanced, or a number was mis-parsed.

Most `E` and `BA` are zero in these older models, which is why the check above
usually reproduces published EE closely. Where a paper does report migration or
accumulation, note it in the report: the recomputed EE will legitimately differ.

## Master equation 2: energy balance within a group

```
consumption = production + respiration + unassimilated food
Q = P + R + U        with  U = GS · Q
```

Per unit biomass:

```
R/B  =  (Q/B) · (1 − GS)  −  (P/B)
```

`GS` is the **unassimilated consumption** fraction — the `Unassim. consumption`
column in `Basic_input.csv`. This equation is why that column matters far more
than its obscurity suggests: it sets how much of intake is available for
production and respiration at all.

Two hard consequences:

- Respiration must be positive: `(Q/B)(1 − GS) > (P/B)`, i.e. `P/Q < 1 − GS`.
  With the usual `GS = 0.2`, `P/Q` cannot exceed 0.8.
- Net efficiency `P / (Q(1 − GS))` must be ≤ 1.

Primary producers have no consumption and no `GS`; detritus has neither
production nor respiration.

## Three of four

For each group, Ecopath needs **three of the four** basic parameters — `B`,
`P/B`, `Q/B`, `EE` — and solves for the fourth across the whole system. Diet
composition is required for every consumer.

This is why blanks in published tables are systematic rather than sloppy:

| Pattern | Meaning |
|---|---|
| `B` given, `EE` blank | EE was estimated by Ecopath |
| `EE` assumed (often 0.9–0.95), `B` blank | biomass was estimated by Ecopath — common for groups with no survey |
| all four given | over-determined; the paper is reporting an input and an output together, usually with the estimate in parentheses |
| fewer than three given | the group cannot be solved — check for a value stated in the prose before concluding the table is incomplete |

A group with only two of four is a strong signal to go back to
`prose-extraction.md` and sweep for the missing one, rather than a signal to
leave it and move on.

## Derived quantities

Values a paper may tabulate that are *outputs*, not inputs. Extract them if
present, but never compute them to fill a gap — a computed value is no longer the
paper's number, and for `TL` it depends on the very diet matrix you're checking.

| Quantity | Definition |
|---|---|
| Trophic level | `TL_i = 1 + Σ_j DC_ij · TL_j`; producers and detritus = 1 (so a pure herbivore is 2.0) |
| Predation mortality `M2` | `Σ_j B_j (Q/B)_j DC_ji / B_i` |
| Other mortality `M0` | `(P/B)(1 − EE)` |
| Fishing mortality `F` | `Y / B` |
| Gross efficiency `GE` | `P/Q = (P/B)/(Q/B)` |
| Net efficiency | `P / (Q(1 − GS))` |
| Respiration | `Q(1 − GS) − P` |
| Flow to detritus | `B(P/B)(1 − EE) + GS·Q`, distributed per `Detritus_fate.csv` |
| Omnivory index | `Σ_j DC_ij (TL_j − (TL_i − 1))²` — variance of prey trophic levels |

## Balance criteria

What "balanced" means in practice, and therefore what an extracted model should
mostly satisfy:

| Criterion | Why |
|---|---|
| `EE ≤ 1` for every group | more consumption than production is impossible |
| `EE ≤ 1` for detritus | detritus consumption cannot exceed detritus input |
| `0 < P/Q < 1 − GS` | respiration must be positive |
| `P/Q` typically 0.1–0.3 for fish | higher for larvae, bacteria and some invertebrates; 0.5+ warrants a second look |
| `R/B > 0` | same constraint, stated as a rate |
| `P/R < 1` for consumers | high-turnover groups are the exception |
| diet columns sum to 1 (with import) | by definition of a composition |
| `Detritus_fate` rows sum to 1 | detritus goes somewhere |

Published models are balanced, so an extracted model that violates these is
usually evidence of an extraction error — that's the point of running the check.
But not always: some papers report a nearly-balanced model and discuss the
residual, and some report the pre-balance parameters alongside the balanced ones.
Investigate before changing anything, and record what you found.

## Detritus

Detritus groups are structurally different: no `P/B`, no `Q/B`, no `GS`, no
respiration. They have biomass, they receive flows, and they are eaten.

Inflow to the detritus pools = Σ over groups of `B(P/B)(1 − EE)` (other
mortality) + `GS · Q` (unassimilated food) + discards, allocated by
`Detritus_fate.csv`. Outflow = consumption by detritivores + export. The detritus
`EE` is outflow over inflow.

Models often have several pools — pelagic detritus, benthic detritus, fishery
offal, sometimes anchovy eggs or DOM — and the split between them is
model-specific and frequently stated only in prose. Leave rows blank rather than
inventing an allocation.

## Fisheries

Catch enters as `Y = landings + discards`, disaggregated by fleet.

- Landings leave the system; discards normally flow to a detritus pool (often a
  dedicated "fishery offal" group), which is why `Detritus_fate.csv` and the
  discard columns interact.
- `F = Y/B`, so a catch that's large relative to biomass drives `EE` up. A group
  with `EE > 1` after extraction and a suspiciously large catch is often a unit
  error in the catch — absolute tonnes not divided by model area.
- Where a paper reports only total catch, it goes in Landings with a note; do not
  synthesise a discard split.

## Magnitude ranges

Indicative orders of magnitude for catching parse errors — a `Q/B` of 3 for
zooplankton or 130 for a large fish means a column was misread. These are **not**
validation criteria; real models sit outside them for good reasons.

| Group type | `B` (t·km⁻²) | `P/B` (yr⁻¹) | `Q/B` (yr⁻¹) |
|---|---|---|---|
| Whales, marine mammals | 0.001–0.5 | 0.02–0.1 | 4–25 |
| Seabirds | 0.0001–0.01 | 0.05–0.3 | 60–120 |
| Large demersal fish | 0.1–10 | 0.2–1.5 | 1–6 |
| Small pelagic fish | 0.5–30 | 0.5–2.5 | 5–20 |
| Benthic invertebrates | 1–100 | 1–5 | 5–25 |
| Zooplankton | 1–30 | 10–60 | 40–200 |
| Phytoplankton | 1–100 | 50–400 | — |
| Bacteria | 0.1–10 | 100–800 | 300–2000 |
| Detritus | 10–200 | — | — |

Watch for **daily rates**: a phytoplankton `P/B` printed as 0.5 is almost
certainly per day (≈180 per year). Plankton and bacteria groups are where this
happens.

## Beyond Ecopath: what the papers may also report

Not extracted into these eight files, but worth recognising so it isn't mistaken
for basic input:

- **Network analysis indices** — total system throughput, Finn's cycling index,
  ascendency, transfer efficiency between trophic levels, primary production
  required, system omnivory index. Ecopath outputs, usually in a separate table.
- **Mixed trophic impact / keystoneness** — matrices of indirect effects.
- **Ecosim vulnerabilities** — dynamic parameters, not part of the mass-balance
  snapshot.
- **Pedigree** — a data-quality index for each input, per parameter. If a paper
  reports it, mention it in the report; it's a useful signal about how much
  confidence the author placed in each value.
- **Multi-stanza groups** — juvenile/adult splits linked by growth parameters
  (von Bertalanffy `K`, `L∞`, weight at maturity). Each stanza is its own group
  with its own row; keep them separate and match rows by full name, since
  "Cod (0–1)" and "Cod (2+)" are two groups whose values are easy to swap.

## Why this matters for extraction

Three practical uses:

1. **Distinguish inputs from outputs.** Parenthesised or italic values are
   usually Ecopath-estimated. Extract them as given, but record them as
   model-estimated — a reader needs to know that number was not observed.
2. **Check a table mapping in one row.** `P/Q = (P/B)/(Q/B)`, `EE ∈ [0,1]`,
   `(Q/B)(1 − GS) > (P/B)`. If the mapping is wrong, these break immediately —
   which is why `table-layouts.md` asks for this check before extracting forty
   rows on an assumed column order.
3. **Run the full check before calling a model done.**

```text
python <skill-root>/scripts/massbalance_check.py <model-dir>
```

This recomputes EE from the diet matrix, biomasses and catches, flags groups
where consumption exceeds production, checks respiration positivity and gross
efficiency, and reports consumers missing a diet column — the error that makes a
model quietly unbalanced without breaking any single number.

## Sources

The equations above are standard Ecopath formulation, originating in Polovina's
ECOPATH and developed as Ecopath II by Christensen & Pauly (Ecological
Modelling, 1992), with the EwE synthesis in Christensen & Walters (Ecological
Modelling, 2004). The `13-north-*` corpus of Fisheries Centre Research Reports
uses this formulation throughout.

These citations are from memory and were not verified against a database — check
them before quoting any of them in a publication. The equations themselves are
worth sanity-checking against the EwE user guide the first time you rely on
them, particularly the sign conventions on `E` (net migration) and `BA`, which
differ between presentations.
