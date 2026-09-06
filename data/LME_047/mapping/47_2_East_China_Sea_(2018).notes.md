# `47_2_East_China_Sea_(2018)` — mapping notes

## The model

Xu L, Song P, Wang Y, Xie B, Huang L, Li Y, Zheng X, Lin L (2022). *Estimating the Impact
of a Seasonal Fishing Moratorium on the East China Sea Ecosystem From 1997 to 2018.*
Frontiers in Marine Science 9:865645. <https://doi.org/10.3389/fmars.2022.865645>

`M2018` is the later of the paper's two mass-balance models, parameterised on a joint
survey of the East China Sea in autumn 2018 and spring 2019. Its companion, `M1997`
(1997–2000 survey), is mapped separately as `47_1_East_China_Sea_(1997)`.

**Area.** The paper gives no model area in km² and no coordinates beyond Figure 1; the
study domain is "the East China Sea", which the archive treats as the LME_047 polygon.
Coverage is therefore assumed to be the whole unit. The two other East China Sea models in
the archive are explicitly sub-regional (Li & Zhang 2012 and Cheng et al. 2009 both cover
the continental shelf, ~500,000 km²) and neither is the model mapped here.

**`taxon_descr` is empty for all 25 groups in `groups_df`.** The Ecopath extraction step
did not capture group membership, so the paper and its supplement are the only source for
which taxa sit in which group. That is a gap in the extraction skill, not in the paper —
the paper documents its membership fully, and it is transcribed alongside this mapping in
`47_2_East_China_Sea_(2018).members.csv`.

## Relationship to the 1997 mapping: identical, and deliberately so

**The two mapping files are identical row for row.** A reader should not have to diff them
to find out. The reason is that the paper defines **one** set of functional groups and
applies it to both models:

1. §2.2 describes a single grouping: "There were 24 function groups in the ECS ecosystem,
   including … (**Table S1**). In addition, large yellow croakers, small yellow croakers,
   hairtails, and Bombay duck were treated as separate function groups." No second
   grouping is described anywhere in the paper or its supplement.
2. Table 1 reports M1997 and M2018 side by side under one list of group names, in the same
   order as the two diet matrices (Supplementary Tables 2 and 3) and as `groups_df` in both
   workbooks. The 25 group names in the two `groups_df` sheets are character-for-character
   the same.
3. The only difference the paper states between the models is in the **diet matrix**, not
   the membership: "We used similar diet matrices in the M1997 and M2018 models but made
   slight changes in several groups, e.g., hairtails, piscivores, and planktivores."

Supplementary Table S1 — the species composition table this mapping is built on — is
captioned "…for the East China Sea (ECS) ecosystem model in **M2018**". So for *this*
model the membership evidence is direct and undiluted; it is the 1997 mapping that carries
the caveat of applying an M2018-captioned table to the earlier model, and that caveat is
set out in `47_1_East_China_Sea_(1997).notes.md`.

What genuinely differs between the two models is not membership but **state**: the paper
notes that `Planktivores` came to be dominated by *Benthosema pterotum* by 2018, its
biomass rising from 0.710 to 4.701 t/km², while `Planktivores/piscivores` — the M1997
keystone, dominated by *Decapterus maruadsi* — fell from 2.588 to 1.294. Trophic levels
shift with it (`Piscivores` 3.571 → 3.940, `Planktivores/piscivores` 3.116 → 3.522). None
of that is a statement about which species the modellers assigned where, so none of it
changes a mapping decision. It does change the SPPR each group carries, which is the whole
point of mapping the two models separately.

One consequence worth knowing: because every composite in this mapping is weighted by
catch composition or by explicit weights, and never by `model_biomass`, the two files also
resolve to the *same* apportionment. A composite switched to `model_biomass` would resolve
differently per model, since the group biomasses above differ by factors of two to seven.
`catch` is 0 for every group in both `groups_df` sheets, so `model_catch` is unusable as a
weight basis here.

## The axis: feeding guild

The group list is built on **feeding guild**, not on taxonomy, size or habitat:
`Planktivores`, `Benthivores`, `Piscivores`, `Planktivores/Benthivores`,
`Planktivores/piscivores`, `Benthivores/piscivores`, `Omnivores`. Four commercially
important stocks are pulled out as single-species groups — `Hairtails`
(*Trichiurus lepturus*), `Bombay duck` (*Harpadon nehereus*), `Large yellow croakers`
(*Larimichthys crocea*), `Small yellow croakers` (*Larimichthys polyactis*) — and the
invertebrates, cephalopods, sharks and marine mammals are taxonomic. There are no prefixes
and no spatial or life-stage strata.

Consequences that shaped every decision:

- A family name says nothing about diet, so the paper's species list is not optional. The
  Sciaenidae alone are spread across six groups.
- Trophic level was used only to corroborate, never to select.
- Groups that cannot take catch: `Phytoplankton` (PP), `Detritus` (DET), `diet_import`
  (Import). `Zooplankton`, `Polychaetes`, `Benthic Crustaceans` and `Marine mammals` can
  in principle but no landed taxon belongs in them, so 18 of 25 groups carry catch.

**Watch the spelling.** `groups_df` and the paper's Table 1 write
`Planktivores/Benthivores` (capital B) but `Planktivores/piscivores` and
`Benthivores/piscivores` (lower-case p). The supplement's Table S1 capitalises all three
and lists Planktivores/Piscivores *before* Planktivores/Benthivores, the reverse of the
order in the diet matrices, in Table 1 and in `groups_df`. Membership here follows the
group **names**, not Table S1's row order; the names are internally consistent with the
model's trophic levels (group 16, TL 2.96, is the lower-TL plankton-and-benthos guild).
`members.csv` records the group under its `groups_df` spelling so the join is exact.

## Supplements: what was looked for and what was obtained

| item | result |
| --- | --- |
| `DataSheet_1_EstimatingtheImpactofaSeasonal-7491f315.docx` (Frontiers supplementary data sheet) | **obtained and read.** Contains Supplementary Table 1, the species composition of all 24 functional groups; Supplementary Tables 2 and 3, the M1997 and M2018 diet matrices; Supplementary Table 4, the M1997 time series; Supplementary Table 5, fishing effort. Transcribed into `47_2_East_China_Sea_(2018).members.csv`. |
| `pdf-e60d0358.pdf` (main article) | obtained and read. §2.2 defines the 24 groups; Table 1 gives TL, B, P/B, Q/B, EE for both models; Figure 5's caption confirms the group numbering. |
| `10152_2011_278_MOESM1_ESM-d161693b.doc` (Li & Zhang 2012 supplement) | obtained and read. A different model with a size-and-habitat group structure, so it is not membership evidence for these guilds. Used as a **supporting regional source** for one decision only: its crab group explicitly pooled "also the lobsters", which is the basis for placing Panulirus, Scyllaridae and Ibacus in `Crabs`. |
| Cheng, Cheung & Pitcher (2009), *Mass-balance ecosystem model of the East China Sea* | **not obtained.** The archive records repeated retrieval failures (NSFC PDF now redirects to a portal page, ScienceDirect blocked, no repository copy, empty Wayback listing). No further attempt was made here and nothing in this mapping depends on it. |

## Judgement calls a reviewer should test

**1. `Marine fishes not identified` (12.9 % of the LME's tonnage) excludes `Planktivores`.**
Sea Around Us classes this record *Medium demersals (30 – 89 cm)*. Every species Table S1
lists under `Planktivores` is under 30 cm — the paper stresses that its dominant member,
*Benthosema pterotum*, maxes out at 3.5 cm — so the size band contradicts the class and the
group was left out of the candidate set, along with `Planktivores/Benthivores` on habitat
(*Scomber japonicus*, *Setipinna tenuifilis*, *Remora remora* are pelagic). The record is
apportioned across the five remaining multi-species guilds by catch composition. This is
the single largest decision in the mapping, and it bites hardest on *this* model, where
`Planktivores` holds 4.701 t/km², a third of all consumer biomass. The opposite choice is
defensible — Chinese trawl "trash fish" landings do contain a great deal of small fish —
and it would move a large share of the tonnage onto a group whose SPPR is very different.

**2. `Pennahia argentata` was moved from `Piscivores` to `Benthivores/piscivores`,
correcting the inherited mapping (1.2 %).** Table S1 lists the species twice, as "Pennahia
argentata" under Piscivores and as "Pennahia argentatus" under Benthivores/piscivores. The
paper's discussion resolves it: "benthivores/piscivores (*Pennahia argentatus* and
*Nemipterus virgatus*)". The species' diet of shrimps, crabs and small fish agrees. Both
listings are transcribed in `members.csv`, so the file records the ambiguity rather than
hiding it.

**3. Northern species with no compartment in an East China Sea model (2.0 %).** Pacific cod
(1.2 %), walleye pollock, Gadidae and Pacific salmon (`Oncorhynchus` 0.6 % plus Salmonidae)
are reported by Sea Around Us in LME_047 but appear nowhere in the paper, and the model has
no anadromous or subarctic compartment. They were placed by functional analogy — cod in
`Benthivores/piscivores`, pollock and salmon in `Planktivores/piscivores` — and all such
rows carry `low` confidence and `analogue` evidence. Leaving them `Unresolved` is a
defensible alternative and would cost about two percentage points of coverage.

**4. Mullets and milkfish (1.3 %) have no honest home.** *Planiliza haematocheilus*,
*Mugil cephalus*, Mugilidae and *Chanos chanos* eat detritus and benthic microalgae. The
model has no herbivore or detritivore fish group; the mullets went to `Benthivores`, the
only bottom-feeding guild, and milkfish to `Omnivores`. All are flagged `low`.

**5. Oceanic predators were mapped, not discarded.** Tunas, billfishes, wahoo, swordfish
and dolphinfish all went to `Piscivores`, because Table S1 puts *Coryphaena hippurus* and
*Auxis thazard* in that group — the model's top fish-eating guild does extend to oceanic
predators. Billfishes, which the paper never names, are flagged `low`.

**6. Gastropods enter `Mollusks` on the group's name, not its stated membership.** Table S1
defines `Mollusks` as "Bivalves". *Turbo cornutus*, Haliotidae, *Rapana* and the Gastropoda
record have no other benthic mollusc compartment, so they were placed there at `medium`
with the discrepancy stated in each row.

**7. Stomatopods in `Shrimps`.** Squillidae and *Oratosquilla oratoria* (0.5 %) are not
decapods and are not listed anywhere in the paper. They were placed in `Shrimps` because
the trawl fishery lands them with the shrimp catch and Sea Around Us classes them as
Shrimps; the only other small-crustacean group is defined as Gammaridea and Cumacea, which
the fishery does not land.

**8. Inherited assignments changed on diet grounds** beyond *Pennahia*:
*Pleurogrammus azonus* (a midwater zooplanktivore, moved from `Benthivores/piscivores` to
`Planktivores/Benthivores`), *Oplegnathus fasciatus* and Haemulidae (hard-shelled benthos
feeders, moved from `Benthivores/piscivores` to `Benthivores`), the flyingfishes
(Exocoetidae, *Cypselurus*, *Cheilopogon unicolor* — zooplanktivores, moved from `Omnivores`
to `Planktivores`), and *Polydactylus sexfilis* (moved from `Omnivores` to `Benthivores`,
where Table S1 lists its congener *Polydactylus sextarius*).

## What the mapping cannot cover

Two taxa carrying 2,850 t between them, 0.001 % of the LME's tonnage, are `Unresolved`:

- **`Mola mola`** — an oceanic specialist on gelatinous zooplankton. The model has no
  gelatinous-feeder fish guild; cnidarians appear only as the prey group
  `Other invertebrates`.
- **`Scaridae`** — obligate reef herbivores. The model of the East China Sea shelf has no
  herbivorous fish group at all; its lowest fish guild, `Planktivores`, is a zooplankton
  feeder.

## Result

100.0 % of the LME's catch tonnage lands on a named group. By confidence: high 128 taxa
(45.0 % of tonnage), medium 128 (51.2 %), low 18 (3.8 %), unresolved 2 (0.0 %). 21 taxa are
composite splits, carrying 20.6 % of the tonnage; all but one are weighted by catch
composition (*Psenopsis anomala*, which Table S1 lists in two groups with no basis for
preferring either, uses `equal`).
