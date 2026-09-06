# LME_032 — `32_1_Arabian_Sea_off_Karnataka_(2000)`

## Read this first: the model's area is a small fraction of the unit

The model is a **27,000 km² continental-shelf model of the Karnataka coast, shore to the
shelf edge**, balanced on landings averaged over **1999–2001**. The catch it is being
joined to is the whole Arabian Sea LME, 1950–2019, 197.9 Mt. Every SPPR derived from this
mapping is therefore a Karnataka-shelf rate applied to LME-wide catch. Two consequences a
reader must carry:

- Taxa that are abundant elsewhere in the LME but absent from the Karnataka shelf still
  get a group and an SPPR. The clearest case is the Bombay-duck *Harpadon nehereus*
  (3.2 % of LME tonnage), which is a Maharashtra/Gujarat resource and appears nowhere in
  the Karnataka species list.
- The model has no oceanic compartment. Billfishes, escolar and opah have no natural home
  in it; see the judgement calls below.

## The model

- Mohamed, K.S., Zacharia, P.U., Muthiah, C., Abdurahiman, K.P. and Nayak, T.H. (2008).
  *Trophic Modelling of the Arabian Sea Ecosystem off Karnataka and Simulation of Fishery
  Yields.* CMFRI Bulletin 51, 151 pp. (catalogued as 2005 in EcoBase; the archive
  metadata corrects this to the 2008 bulletin.)
  Landing page <https://eprints.cmfri.org.in/3945/>. No DOI.
  Archived at `PPRAtlas/archive/regions/LME_032/ARAB-2005/CMFRI-Bulletin-51-88a9c885.pdf`.
- Companion paper: Mohamed, K.S. and Zacharia, P.U. (2009). *Prediction and modelling of
  marine fishery yields from the Arabian Sea off Karnataka using Ecosim.* Indian J. Mar.
  Sci. 38(1): 69–76. Archived under `LME032-Mohamed-2009`. This is the Ecosim paper built
  on the same Ecopath model; its Table 1 is the group-definition summary.
- 24 living-and-dead groups in the paper; the extracted workbook has 25, the extra one
  being the bookkeeping compartment `diet_import`.
- `usable = yes` in `data/model_selection.xlsx`.

## The axis the group list is built on

**Size and habitat, with taxonomic pools at the ends.** The paper states the criterion
explicitly (printed p. 11): species were grouped so that within a group they share
similar sizes, population parameters, food and predators.

- A **demersal-carnivore continuum** — `Small Benthic Carnivores` (mean L∞ 23 cm) →
  `Med Benthic Carnivores` (35 cm) → `Large Benthic Carnivores` (55 cm). Note that
  "Large" here tops out around 70 cm; it is not the Sea Around Us ≥90 cm band. That is
  why the SAU class *Medium demersals (30 – 89 cm)* spans two of these groups and why
  `Marine fishes not identified` is apportioned over all three.
- A **benthopelagic pair** — `Small Benthopelagics` (scads, small carangids, moonfish,
  myctophids) and `Large Benthopelagics` (ribbonfish, horse mackerel, queenfish, wolf
  herring, sea catfish; mean L∞ 73 cm).
- **Taxonomic pools** — `Sharks`, `Skates & Rays`, `Cephalopods`, `Tunas`, `Clupeids`,
  `Anchovies`, `Crabs & Lobster`, `Shrimps`.
- **Single stock** — `Mackerel` is the one species *Rastrelliger kanagurta*.
- **Feeding guilds** at the base — `Benthic Omnivores`, `Heterotrophic Benthos`,
  `Meiobenthos`, `Micro Nekton`, the two zooplankton groups.

No prefixes, no spatial strata, no life-stage splits. Groups that cannot take catch:
`Phytoplankton` (PP), `Detritus` (DET), `diet_import` (Import). `Meiobenthos`,
`Large zooplankton` and `Micro Zooplankton` can in principle but nothing is landed on
them here. `Micro Nekton` and `Heterotrophic Benthos` carry zero catch **in the model**
but are explicitly defined to contain jellyfish and bivalves/gastropods/echinoderms
respectively, all of which are landed in this LME, so this mapping does put catch on them.

Two group names to watch when reading the paper against the workbook: the paper prints
the batoid group as "Stakes & Rays" (a typo) and group 20 as "Nekton"; the workbook
spellings `Skates & Rays` and `Micro Nekton` are the authoritative strings.

## Membership evidence

`taxon_descr` is **empty for every group in the extracted workbook**, so the extraction
step captured no membership. That is a gap in the extraction skill, not in the paper.

The paper more than fills it. CMFRI Bulletin 51 carries a table headed **"Components of
Ecological Groupings"** (PDF pp. 21–22, printed 11–12) that names **129 species numbered
1–129 under the 24 groups** — a complete species-to-group table, the strongest membership
evidence available for any mapping in this repository so far. It is backed by per-group
accounts (PDF pp. 24–30, printed 14–20) that repeat the membership in prose and tabulate
L∞, P/B, aspect ratio and Q/B per species, and by species diet accounts (printed pp.
61–76) and life-history sheets for 55 species (printed pp. 77–132).

The paper states that this grouping covers more than 86 % of the commercial catches
recorded from the area, so roughly 14 % of even the Karnataka landings sit outside the named
species list; taxa mapped by containment or analogue are filling that residual.

Every group row in `<model>.groups.csv` carries `source_relationship = direct source`
against this table, except `Detritus` and `diet_import`, which the paper does not
enumerate.

### Supplements sought

| item | where looked | result |
| --- | --- | --- |
| separate species list / appendix for Bulletin 51 | <https://eprints.cmfri.org.in/3945/> | **none exists** — the record page lists one file, the 151-page bulletin itself, which already contains the species table, the diet database (9,786 stomachs, 56 species) and the 55 life-history sheets |
| the EwE model file | EcoBase, <https://ecobase.ecopath.org/> | model **574**, "Arabian Sea", Mohamed K.S., 1999–2001, is listed; no direct file link surfaced and the file was **not obtained**. It would add nothing here — the printed species table is more explicit than an EwE group list |
| Mohamed & Zacharia (2009), Ind. J. Mar. Sci. | archived locally | obtained; Table 1 is the group-definition summary and agrees with the Bulletin |
| Mohamed (2024), NE Arabian Sea (Maharashtra/Gujarat) | archived locally | read; a **different model** with a different group list, not used for membership |
| Vivekanandan et al. (2003), SW coast of India | archived locally | read; an 11-group **feeding-guild** model of a different area, not used for membership |

Nothing was copied from another ecosystem's mapping.

## What changed in this pass

Baseline (first-generation mapping): 78.2 % of tonnage on a named group, 14 taxa
`Unresolved` carrying 21.8 %, 37 rows with no decision.

Now: **100.0 % of tonnage on a named group.** 430 rows, no errors, validator `PASS`.
By tonnage: `high` 65.0 %, `medium` 35.0 %, `low` <0.05 %, `unresolved` <0.001 %.
18 of the model's 25 groups take catch. 13 taxa are composites carrying 21.8 % of
tonnage. 335 taxa (22.6 % of tonnage) still carry `evidence = inherited_mapping` and have
**not** been re-derived here — that is honest provenance, not a claim of correctness.

### Five inherited decisions were wrong

All five contradict the Bulletin's own species table, and all five were size/habitat
misreadings of the Sea Around Us class against the model's placement. Together they move
**2.3 % of LME tonnage** off groups whose SPPR are 3–26× higher than the correct ones,
depending on the taxon and the SPPR method.

| taxon(s) | was | now | the paper says |
| --- | --- | --- | --- |
| `Leiognathidae`, `Photopectoralis bindus`, `Leiognathus`, `Leiognathus equula`, `Equulites klunzingeri` (2.62 Mt, 1.32 %) | `Small Benthopelagics` | `Small Benthic Carnivores` | *Leiognathus bindus* (51) and *Secutor insidiator* (50) are members of Grp10, and the group account names silverbellies among its dominant species with life-history rows for both |
| `Parastromateus niger` (0.88 Mt, 0.45 %) | `Small Benthopelagics` | `Med Benthic Carnivores` | listed as "Formio niger" (39) in Grp9; the group account names "Black pomfret (*Parastromateus niger*)" and tabulates its parameters |
| `Lactarius lactarius` (0.81 Mt, 0.41 %) | `Large Benthopelagics` | `Small Benthic Carnivores` | member 49 of Grp10, "whitefish (*Lactarius lactarius*)", with its own life-history row |
| `Megalaspis cordyla` (0.19 Mt, 0.10 %) | `Small Benthopelagics` | `Large Benthopelagics` | member 25 of Grp7, "horse mackerel (*Megalaspis cordyla*)" |
| `Plotosidae`, `Plotosus lineatus` (507 t) | `Large Benthopelagics` | `Benthic Omnivores` | *Plotosus* sp. is member 86 of Grp17 |

A sixth, smaller fix is not a wrong group but a wrong source claim: five `Gerres` /
`Gerreidae` rows justified themselves as the Bulletin's "silverbellies". The Bulletin's
silverbellies are Leiognathidae, not Gerreidae. The group (`Small Benthic Carnivores`) is
unchanged; the evidence code dropped from `explicit_member`/`high` to `analogue`/`medium`.

## The composite splits

Candidate sets and the groups deliberately excluded are written out in each row's
`explanation`. Weights are blank — i.e. **catch composition**, each candidate group's
share of the tonnage that single-group taxa already put on it — except where noted. The
shares the merge step will compute from the current file:

| taxon | % of LME catch | candidate set → weight |
| --- | --- | --- |
| `Marine fishes not identified` | 12.51 | Med Benthic Carnivores 0.36 · Small Benthic Carnivores 0.24 · Large Benthic Carnivores 0.40 |
| `Decapoda` | 3.38 | Shrimps 0.88 · Crabs & Lobster 0.12 |
| `Clupeiformes` | 2.58 | Clupeids 0.89 · Anchovies 0.11 |
| `Elasmobranchii` | 1.26 | Sharks 0.72 · Skates & Rays 0.28 |
| `Perciformes` | 0.92 | same three demersal-carnivore groups, same shares |
| `Scombridae` | 0.56 | Mackerel 0.40 · Tunas 0.29 · Large Pelagics 0.32 |
| `Marine pelagic fishes not identified` | 0.34 | Clupeids 0.62 · Mackerel 0.19 · Small Benthopelagics 0.11 · Anchovies 0.08 |
| `Pleuronectiformes` | 0.16 | Benthic Omnivores 0.83 · Med Benthic Carnivores 0.17 — **explicit weights** |
| `Chondrichthyes` | 0.03 | as `Elasmobranchii` |
| `Marine groundfishes not identified` | 0.01 | as `Marine fishes not identified` |
| `Miscellaneous marine crustaceans`, `Malacostraca` | <0.01 | Shrimps 0.88 · Crabs & Lobster 0.12 |
| `Scombroidei` | <0.01 | Large Pelagics 0.52 · Tunas 0.48 |

`Mollusca` and `Miscellaneous aquatic invertebrates` were **not** split: Sea Around Us
classes both as *Other demersal invertebrates* rather than *Cephalopods*, which is a
statement that the pile is benthic molluscs, and this LME's cephalopod landings are
near-completely identified to family or genus. Both go whole to `Heterotrophic Benthos`.

`Pleuronectiformes` is the one composite with explicit weights. Catch composition would
have set the split from the croaker-dominated catch of `Med Benthic Carnivores` rather
than from its flatfish members, so the weights come instead from this LME's own
identified flatfish landings: `Soleidae` 1,764,086 t against `Psettodes erumei` +
`Bothus pantherinus` + `Bothidae` 370,194 t → 0.83 / 0.17. Recomputable from
`SeaAroundUsExtraction/data/catch_by_taxon_year/LME_032.csv.gz`.

## Where a reviewer should push back

1. **`Scombridae` is the most consequential judgement in the file.** The three candidate
   groups' SPPR differ by two orders of magnitude, because the model treats `Mackerel`
   (*Rastrelliger kanagurta*) as an 88 %-diatom feeder at TL 2.0 while `Tunas` and
   `Large Pelagics` sit above TL 4.1. Sea Around Us gives this record commercial group
   *Perch-likes* rather than *Tuna & billfishes*, which hints the pile leans to
   *Rastrelliger* and *Scomberomorus*; a reviewer who accepts that hint should drop
   `Tunas` from the set, which would roughly halve this record's PPR.
2. **`Harpadon nehereus`, 3.2 % of tonnage, is not in the model.** It is placed in
   `Large Benthic Carnivores` with its closest listed relatives, the lizardfishes
   *Saurida* (same order, same ambush-piscivore habit, group TL 4.14 against the record's
   4.20). `Large Benthopelagics` (TL 4.15) is the defensible alternative and matches the
   SAU benthopelagic class. This is `medium`/`analogue`, not a paper-backed decision.
3. **`Decapoda`, 3.4 % of tonnage.** Sea Around Us classes the record as *Lobsters, crabs*
   while catch composition puts 88 % of it on `Shrimps`, because this LME's identified
   crustacean landings are shrimp-dominated. The two signals disagree. Catch composition
   was kept because it is this ecosystem's own data and because the two groups' SPPR stay
   within a factor of 2.5 on every one of the 20 methods and even swap order between
   them, so the split is not load-bearing — but a reviewer who
   trusts the SAU class should override with explicit crab-weighted shares.
4. **`Carangidae`, 1.6 % of tonnage, was not split** even though the model places three
   carangids outside `Small Benthopelagics` (*Megalaspis cordyla* and *Scomberoides tol*
   in `Large Benthopelagics`, *Parastromateus niger* in `Med Benthic Carnivores`). All
   three are separately and substantially identified in this catch, and the catch on
   `Large Benthopelagics` is well over half sea catfish, so a catch-composition split
   would have been set by non-carangid tonnage. Same reasoning kept `Siluriformes` whole
   on `Large Benthopelagics` and `Engraulidae` whole on `Anchovies`.
5. **Billfishes stay on `Large Pelagics`** (`Xiphias gladius`, `Istiophoridae`,
   `Istiophorus platypterus`, `Istiompax indica`, `Makaira`, `Kajikia audax`,
   `Tetrapturus angustirostris` — 0.21 % of tonnage together), inherited from the
   first-generation mapping and not re-derived. The coarse-taxa playbook would call these
   `Unresolved` in a shelf model with no oceanic compartment. They were left as they were
   found because they are outside the top-tonnage set this pass verified; the two
   genuinely bathypelagic records, `Lepidocybium flavobrunneum` and `Lampris guttatus`
   (under 1 t each), *were* set to `Unresolved` on exactly that reasoning, so the file is
   currently inconsistent on this point by design rather than by oversight.
6. **335 taxa, 22.6 % of tonnage, still read `inherited_mapping`.** They were not
   re-derived. The four errors found in the ~30 rows that were checked were all of one
   kind — the SAU size/habitat class read in preference to the model's own placement — so
   the same failure mode is likely to recur in the unchecked tail.

## What this mapping cannot cover

Nothing of consequence is left `Unresolved`: the two remaining rows, `Lepidocybium
flavobrunneum` (escolar) and `Lampris guttatus` (opah), carry under 1 tonne each over the
whole 1950–2019 period. Both are oceanic bathypelagic species classed by Sea Around Us as
*Large bathypelagics (≥90 cm)*, and this is a 27,000 km² shelf model with no oceanic or
bathypelagic compartment, so forcing them onto `Large Pelagics` would attach a
coastal-predator SPPR to a fishery the model never represented.

The real limit is not coverage but the area mismatch stated at the top of this file, and
the 22.6 % of tonnage still carrying an unverified inherited decision.
