# Reading a model's group list before you map anything

Ecopath modellers do not agree on what a "group" is. Two models of neighbouring seas can
be organised on entirely different axes, and a mapping rule that is right for one is
nonsense for the other. Spend ten minutes on the group list first: the axis it is built on
determines every decision afterwards.

Look at `groups_df` — `seq`, `group_name`, `group_type`, `tl`, `biomass`, `catch` — and
ask which of these the names vary along.

## Taxonomic

`Cephalopods`, `Sharks`, `Skates & Rays`, `Clupeids`, `Anchovies`, `Mackerel`.

The easiest case. Taxonomic containment decides nearly everything, most decisions are
`high` confidence, and the paper is needed only for the residual groups.

Watch for a group named after one genus that is really a pool — a `Mackerel` group in a
model of the Arabian Sea is *Rastrelliger*, not every scombrid. Check the biomass and the
model catch: a group carrying a large share of the landings is a pool, a small one is a
single stock.

## Size and habitat

`Large Benthic Carnivores`, `Med Benthic Carnivores`, `Small Benthic Carnivores`,
`Small Benthopelagics`, `Large Pelagics`. Arabian Sea is this shape.

Here the Sea Around Us `functional_group` column is directly commensurable — it is the
same two axes, habitat and size band:

```
Small demersals (<30 cm)          Medium demersals (30 - 89 cm)     Large demersals (>=90 cm)
Small pelagics (<30 cm)           Medium pelagics (30 - 89 cm)      Large pelagics (>=90 cm)
Small benthopelagics (<30 cm)     Medium benthopelagics (30-89 cm)  Large benthopelagics (>=90 cm)
Small reef assoc. fish (<30 cm)   ...                                Large sharks / Large rays
Shrimps    Lobsters, crabs    Cephalopods    Jellyfish    Other demersal invertebrates
```

Use it. It is the single strongest signal in the workbook for this model shape, it is
present for every row including the unidentified ones, and it was assigned from the actual
composition of the catch rather than guessed.

Do not use it blindly against a taxonomic name: a species record's own biology wins when
the two disagree, because the SAU class is a class average.

## Feeding guild

`Planktivores`, `Benthivores`, `Piscivores`, `Planktivores/Benthivores`,
`Benthivores/piscivores`, `Omnivores`. East China Sea is this shape.

The hardest case, and the one that produces the most `Unresolved` rows, because a family
name says nothing about diet. Three consequences:

- **The paper's species list is not optional.** A guild model is unusable without it.
  Search the supplements hard — the East China Sea supplement is a `.docx` data sheet, not
  a table in the PDF.
- **Diet composition tables are membership evidence.** A group's diet row tells you what
  the guild eats, and therefore which families can be in it.
- **A family that spans guilds is a composite**, weighted by catch composition. Sciaenids
  in the East China Sea are croakers (dedicated groups), plus generic benthivores, plus
  piscivorous species.

Never assign a guild from trophic level alone. Two families with TL 3.4 can be a
benthivore and a planktivore.

## Spatially or vertically stratified

`1 L pisc`, `2 L pisc`, `3 L pisc`, `1 Phytoplankton`, `2 Phytoplankton`,
`2-3 Hilsa`, alongside unprefixed `Oceanic sharks`, `Tuna-like`, `Cephalopods`.
Bay of Bengal is this shape: numeric prefixes are sub-areas or depth strata, and the
unprefixed groups are the ones modelled across the whole domain.

**This is the trap.** A catch series for the whole LME cannot belong to one stratum. The
first Bay of Bengal mapping put every stratified taxon into stratum `2` and nothing into
`1` or `3` — a silent decision that attributed the entire LME's catch to one sub-area's
SPPR, with nothing in the workbook saying so.

Read the paper and find out what the prefixes mean before mapping. Then:

- A taxon that occurs across strata is a **composite over the strata**, weighted
  `model_biomass` — observed catch cannot inform a split the fishery does not record, so
  catch composition would be circular here.
- A taxon confined to one stratum by depth or habitat goes to that stratum alone; say why.
- A group carrying an explicit stratum range in its name, like `2-3 Hilsa`, already
  encodes the answer for that taxon.
- Unprefixed groups take the whole catch, no split.

## Life stage or size split within a stock

`Cod juvenile` / `Cod adult`, `Hake 0-1` / `Hake 2+`.

The catch record is not split by stage, so the taxon is a composite over the stages. Weight
by `model_catch` when the model reports landings per stage — that is the fishery's own
selectivity — and by `model_biomass` otherwise.

## Groups that never take catch

`Detritus`, `diet_import`, and every `PP` group. `group_type` marks them. A catch taxon
mapped there is an error and the validator rejects it; the only exception is harvested
seaweed, which genuinely lands on a primary producer group.

Zooplankton, meiobenthos and microbial groups take catch only where the fishery actually
lands them, which is almost nowhere. If a mapping puts tonnage on `Zooplankton`, something
is wrong.

## Before you map, write down

- the axis the model is built on, in one sentence
- what any prefix or suffix in the group names means
- which groups are single stocks and which are pools
- which groups can take catch at all
- whether the model's area is the whole unit or part of it, and what that does to coverage

Put this in the notes file. It is the context that makes every later decision checkable,
and it is what the next person needs in order to disagree with you.
