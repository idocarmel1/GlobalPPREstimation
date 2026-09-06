# Coarse taxa: the labels that decide your coverage

Sea Around Us reports a large share of catch under labels that no Ecopath paper will ever
name: `Marine fishes not identified`, `Perciformes`, `Decapoda`, `Sciaenidae`,
`Miscellaneous marine crustaceans`. They sit above genus, they span several model groups,
and there is no single group that is right for them.

Earlier mappings marked all of these `Unresolved`. The cost, measured on three finished
mappings:

| ecosystem | taxa unresolved | catch tonnage unresolved | largest single offender |
| --- | --- | --- | --- |
| `LME_032` Arabian Sea | 14 / 393 (3.6 %) | **21.8 %** | `Marine fishes not identified`, 12.5 % |
| `LME_034` Bay of Bengal | 12 / 288 (4.2 %) | **22.3 %** | `Marine fishes not identified`, 18.5 % |
| `LME_047` East China Sea | 27 / 254 (10.6 %) | **22.1 %** | `Marine fishes not identified`, 12.9 % |

Fourteen decisions threw away a fifth of the Arabian Sea's PPR. Getting these right is
worth more than every species-level decision in the workbook combined.

## The rule

**A taxon that genuinely spans several groups is apportioned across them, not discarded.**
Write the groups it spans, pipe-separated, and let the merge step weight them:

```
group     = Clupeids | Anchovies | Small Benthopelagics
weights   =                       (blank: weight by observed catch composition)
evidence  = composite_split
confidence= medium
```

`Unresolved` survives, and it is still the right answer when a taxon has no home in the
model at all — a billfish in a model of a coastal shelf that has no oceanic compartment,
a mollusc in a model with no benthic invertebrate group. Unresolved means *outside the
model*, not *hard to decide*.

## Choosing the candidate set

The candidate set is the group of groups the taxon could belong to, and nothing wider.
Three things narrow it, in this order.

**1. Taxonomic containment.** `Clupeiformes` cannot include a shark. If the model has
`Clupeids` and `Anchovies`, both engraulid and clupeid, both are candidates; `Mackerel`
is not.

**2. The Sea Around Us functional group.** This is the axis the earlier version of this
skill overlooked, and it is the reason coarse labels are tractable. Every catch row —
including `Marine fishes not identified` — carries a habitat-and-size class:

```
Marine fishes not identified   ->  Medium demersals (30 - 89 cm)
Miscellaneous marine crustaceans -> Shrimps
Sciaenidae                     ->  Medium demersals (30 - 89 cm)
Carangidae                     ->  Medium pelagics (30 - 89 cm)
Decapoda                       ->  Lobsters, crabs
```

Sea Around Us assigned that class from the composition of the catch it aggregated, so it
is evidence about what is actually in the pile, not a guess. A model group whose habitat
or size band contradicts it is not a candidate: `Marine fishes not identified` in the
Arabian Sea is medium demersal, so `Med Benthic Carnivores` and `Small Benthic Carnivores`
are in and `Large Pelagics`, `Tunas` and `Marine Mammals` are out.

The class is a *hint about the centre of the distribution*, not a hard bound. `Marine
fishes nei` really does contain some large and some small fish. Let it choose the centre
of the candidate set and let neighbouring size bands in; do not let it admit a group from
a different habitat entirely.

**3. The commercial group.** `Perch-likes`, `Herring-likes`, `Anchovies`, `Cod-likes`,
`Tuna & billfishes`, `Sharks & rays`, `Flatfishes`, `Crustaceans`, `Molluscs`,
`Scorpionfishes`, `Salmon, smelts, etc`, `Other fishes & inverts`. Useful mainly to
exclude: a `Herring-likes` record is not going into a demersal carnivore group.

Note what `Other fishes & inverts` means — it is the residual, so it excludes nothing.

## How the weights are chosen

Leave `weights` blank and the merge step computes them by **catch composition**: within
the candidate set, each group's share of the catch that other, identified taxa already
put on it, summed over the whole period. This is the standard way unidentified landings
are pro-rated, it uses this ecosystem's own data, and it is reproducible from the files
in the repository.

Weights are constant over time by design, so each taxon keeps one SPPR per method and the
arithmetic stays `PPR = catch(taxon, year) x SPPR(taxon, method)`.

Override the basis when catch composition would be circular or empty:

| write in `weights` | when |
| --- | --- |
| *(blank)* | the default. Other identified taxa already sit on these groups. |
| `model_biomass` | the split is between spatial strata or between compartments the fishery does not distinguish, so observed catch cannot inform it |
| `model_catch` | the model reports landings per group and those landings are the best statement of what the fishery takes |
| `equal` | nothing better exists, and you say so in the explanation |
| `0.6 \| 0.3 \| 0.1` | the paper, or a species-composition table, states the proportions |

If the candidate groups have no catch on them at all, the merge step falls back through
`model_catch` to `model_biomass` to `equal` on its own and records which it used.

## Confidence for a composite

- **medium** — the candidate set is well founded and the weights come from data. This is
  the normal outcome, and it is the honest one: the set is right, the split is estimated.
- **low** — the set is defensible but wide, or the weights are `equal`. Still far better
  than discarding the tonnage, and visibly flagged.
- **high** — reserve for a stated species composition. Rare.

Never write **high** on a composite whose weights the script computed.

## The recurring labels

**`Marine fishes not identified`** (typically 10–20 % of an LME's catch). Candidate set:
the model's finfish groups in the habitat band the SAU functional group names, plus the
adjacent size band. Exclude mammals, invertebrates, primary producers, detritus, and any
single-species commercial group. In a guild-structured model like East China Sea this is
`Planktivores | Benthivores | Piscivores | Planktivores/Benthivores | Benthivores/piscivores`;
in a size-structured model like the Arabian Sea it is
`Med Benthic Carnivores | Small Benthic Carnivores | Large Benthic Carnivores`.

**Order and family labels** — `Perciformes`, `Clupeiformes`, `Pleuronectiformes`,
`Scombridae`, `Carangidae`, `Sciaenidae`, `Monacanthidae`. Take the model groups whose
membership intersects that taxon. Where the model has a dedicated single-species group
inside the family (`Small yellow croakers` inside Sciaenidae), include it *and* the generic
guild group — the nei record contains both.

**`Elasmobranchii`, `Chondrichthyes`, `Batoidea`, `Carcharhinus`** — if the model has both
`Sharks` and `Skates & Rays`, split; if only `Sharks`, and the label is `Batoidea`, that is
a genuine `Unresolved` unless a demersal carnivore group plausibly absorbs rays, which the
paper must support.

**`Decapoda`, `Miscellaneous marine crustaceans`** — split across `Shrimps`,
`Crabs & Lobster`, and any benthic crustacean group. The SAU functional group
(`Shrimps` vs `Lobsters, crabs`) tells you where the mass is.

**Higher invertebrate labels** — `Mollusca`, `Cephalopoda`, `Bivalvia`. Cephalopods almost
always have their own group. `Mollusca` unqualified splits across cephalopod and benthic
mollusc groups where both exist.

**Single-species records the model predates** — swordfish, marlins, sailfish in a 1960s
coastal-shelf model. These are `Unresolved`, correctly: the model has no oceanic pelagic
compartment, and forcing them into `Large Pelagics` would attach that group's SPPR to a
fishery the model never represented. Say that in the explanation.

## What not to do

- Do not build a candidate set from trophic level. TL corroborates; it never selects.
- Do not include every group of the right habitat "to be safe". A wide set with computed
  weights looks quantitative and is not: it just reproduces the ecosystem's average SPPR.
  Keep the set to the groups the taxon can actually contain.
- Do not split a taxon that has one clear home. A composite where a single group is right
  adds noise to a correct answer.
- Do not write a composite to dodge a hard single decision. If one group is right and you
  are unsure which, that is `low` confidence on your best single choice, with the doubt in
  the explanation — not a split.
