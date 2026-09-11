# LME_034 — `34_1_Bay_of_Bengal_(1978)` mapping notes

## The regions, and how a whole-LME catch series is attributed across them

**Read this first. It is the decision that moves the PPR numbers most.**

Twenty-nine of the model's fifty groups carry a numeric prefix. The prefixes are **geographic
sub-areas of the study area**, not depth strata, life stages or countries. Guénette (2013),
p. 8:

> The Bay of Bengal was divided in 3 regions: 1. the Maldives and open waters; 2. Sri Lanka,
> Indian coast, and Bay of Bengal; 3. the eastern coast of the Bay that covers the coast of
> Myanmar, Thailand, Malaysia, Sumatra and the Andaman and Nicobar Islands.

Table 1 (p. 8) and Appendix A1.2 (p. 42) give the areas:

| region | entities | EEZ (km²) | shelf (km²) | shelf share |
| --- | --- | ---: | ---: | ---: |
| 1 | Maldives (915,423) + high seas (1,929,874) | 2,845,297 | 30,998 | 3.3 % |
| 2 | Bangladesh, India (east coast), Sri Lanka | 1,282,459 | 213,663 | 22.8 % |
| 3 | Myanmar, Thailand, W-peninsular Malaysia, W Indonesia, Andaman & Nicobar | 2,077,295 | 691,507 | 73.9 % |
| | **total study area** | **6,205,051** | **936,168** | |

Coastal fish and invertebrates are modelled as **relatively isolated per region** (p. 9), which
is why each shelf pool exists three times. Groups with no prefix — `Oceanic sharks`,
`Tuna-like`, `Coastal elasmobranch`, `Coastal scombrids`, `Jellyfish`, `Cephalopods`,
`S bathy`, `ML bathy`, `Bigeye tuna`, `Yellowfin tuna`, `Marlins` — are single stocks over the
whole study area, all EEZs, or all deep water (A1.2). `2-3 Hilsa` and `2-3 Indian mackerel`
are single stocks straddling the shelves of regions 2 and 3 and already encode their own
answer.

### Region 1 is outside this unit

The model's study area is **larger than the LME**: Figure 1 is captioned "the Bay of Bengal LME
**and the Maldives**", and region 1 adds the Maldives EEZ plus 1.93 M km² of high seas to it.
Region 1 contributes **the whole of its shelf from the Maldives** — the high-seas component has
zero shelf (Table 1) — and the Maldives lies at 72.5–73.8 °E, west of the western limit of the
LME_034 polygon this project uses (bounding box 77.57–103.47 °E, 0.15–23.61 °N). No Sea Around
Us LME_034 catch is taken there.

So the six region-1 shelf pools (`1 L pisc`, `1 Carangids`, `1 S pelagics`, `1 L pisc comm`,
`1 SM inv`, `1 SM pisc`) are **not candidates for any LME_034 catch record**, and neither are
`1 Macrobenthos`, `1 Meiobenthos` and `1 Zooplankton`, whose area is the Maldives EEZ plus the
high seas. Consistently, the model's own 1978 catch on `1 Macrobenthos` is 3.07 × 10⁻⁷ t/km²,
i.e. nothing.

Regions 2 + 3 (3.36 M km² of EEZ) are the Bay of Bengal proper and are what the LME_034 catch
series describes.

### The rule applied

- A taxon whose functional pool exists per region is a **composite over `2 X | 3 X`**, weights
  `model_biomass`.
- A taxon in an unprefixed group takes the whole catch on that group, no split.
- `2-3 Hilsa` / `2-3 Indian mackerel` take the whole catch, no split.
- `Crustaceans` and `Milkfish plus` exist only for regions 2 and 3 anyway.

Every prefixed decision in this file is therefore `2 X | 3 X`. That is not a default — it is what
excluding region 1 leaves.

### Why `model_biomass` and not `model_catch`

`groups_df.biomass` is Table 16's **"Biomass (t/km²)"** column, i.e. biomass in the habitat area
already multiplied by the habitat fraction, so it is expressed per km² of the *whole* study area.
Ratios between `2 X` and `3 X` are therefore ratios of **total standing stock**, which is what a
spatial apportionment needs.

`model_catch` (A2.1, also per whole-study-area km²) is a genuine alternative: the model does
record 1978 landings per region. I did not use it, for three reasons.

1. It is a **single-year snapshot of a fishery that moved**. In 1978 India and Bangladesh
   dominated landings; over 1950–2019 the Myanmar, Thai, Andaman and Sumatran fisheries of
   region 3 expanded greatly. Weighting a 70-year series so that roughly two thirds of it comes
   from 22.8 % of the shelf is hard to defend.
2. **The paper's own allocation rule for whole-area quantities is area, not catch.** When
   Guénette had to spread the coastal diet of wide-ranging predators over the regions she used
   shelf area, 3.3 / 22.8 / 73.9 % (p. 11). Renormalised over regions 2 and 3 that is
   23.6 / 76.4 %, close to the biomass split and far from the catch split.
3. The model's per-region catch was itself derived from an earlier Sea Around Us reconstruction —
   the same source as the series being mapped — so it is not independent evidence.

What is at stake, per stem (SPPR shown is `new_GE`, t PP per t catch):

| stem | biomass w. 2 / 3 | catch w. 2 / 3 | SPPR `2 X` | SPPR `3 X` | biomass-wtd | catch-wtd |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| L pisc | 45 / 55 | 68 / 32 | 1,179 | 3,649 | 2,539 | 1,969 |
| Carangids | 30 / 70 | 40 / 60 | 949 | 2,050 | 1,715 | 1,614 |
| S pelagics | 30 / 70 | 70 / 30 | 100 | 246 | 203 | 144 |
| L pisc comm | 48 / 52 | 64 / 36 | 799 | 2,331 | 1,597 | 1,349 |
| Milkfish plus | 44 / 56 | 69 / 31 | 378 | 1,137 | 803 | 613 |
| SM inv | 32 / 68 | 68 / 32 | 122 | 443 | 341 | 225 |
| SM pisc | 31 / 69 | 50 / 50 | 330 | 1,070 | 844 | 699 |
| Crustaceans | 21 / 79 | 52 / 48 | 51 | 129 | 113 | 88 |
| Macrobenthos | 36 / 64 | 61 / 39 | 32 | 160 | 113 | 81 |

Choosing biomass over catch raises the taxon SPPRs by roughly 10–40 %. **This is the single
judgement a reviewer should push on first**; switching the `weights` column of the stratified
rows from `model_biomass` to `model_catch` reproduces the right-hand column and nothing else in
the file changes.

### What this replaces

The first-generation mapping put **every** prefixed taxon in stratum 2 and nothing in 1 or 3,
with nothing in the workbook saying so. That was wrong in both directions: it silently dropped
region 3, which holds three quarters of the Bay's shelf and the higher-SPPR pools, and it
excluded region 1 only by accident rather than for the reason above. Region 3 SPPRs run 2–5 ×
their region 2 counterparts (`3 SM inv` 443 vs `2 SM inv` 122; `3 L pisc` 3,649 vs `2 L pisc`
1,179), so the old choice understated PPR for most demersal and benthic catch by a factor of
about two.

## The model

- **Guénette, S. (2013). An exploratory ecosystem model of the Bay of Bengal Large Marine
  Ecosystem.** EcOceans, St Andrews NB, for the Bay of Bengal Large Marine Ecosystem Project,
  December 2013, 62 pp. No DOI.
- Local copy: `PPRAtlas/archive/regions/LME_034/LME034-Guenette-2013/009031359-84f3dc3d.pdf`
  (SHA-256 `84f3dc3d…`), retrieved from a Doczz mirror after the BOBLME host failed.
- Original URL: <https://www.boblme.org/documentRepository/Bengal%20report%2028april2014.pdf>
- **Ecopath base year 1978**; an Ecosim run follows 1978–2010. The catch series mapped here is
  1950–2019, so the mapping applies a 1978 structure to seven decades — the standard limitation
  of this whole project, but worth restating because the region weights are 1978 quantities.
- **Area: 6,205,051 km², larger than the LME** — the Bay of Bengal LME plus the Maldives EEZ and
  the adjacent high seas. See above; the practical consequence is that region 1 is excluded.
- Model selection: `usable = yes` (note: "meiobenthos DC fixed to eat 100 % detritus").
- 50 groups, 20 SPPR methods. **`taxon_descr` is empty for every group in the extracted
  workbook**, so the paper is the only source of membership. That is a gap in the extraction
  step, not in the paper: this report happens to carry an unusually complete membership record,
  and it should be captured at extraction time.

## Sources used, and sources not used

| archived item | used? | why |
| --- | --- | --- |
| `LME034-Guenette-2013` | **yes, the sole source** | It *is* the model. Appendix A1.1 pp. 37–41 allocates Sea Around Us catch names to functional groups; A1.2 p. 42 gives the area of every group; A1.3 pp. 43–45 gives species lists per group; Table 16 p. 24 gives the balanced biomasses used as weights. |
| `LME034-Dutta-2023` | no | A 29-group model of the northern Bay off West Bengal only. A different model of a sub-area; nothing in it defines *this* model's groups. |
| `LME034-Karim-2018` | no | A local model of the "resettled maritime area" of Bangladesh. Same reason. |
| `BOB-2014` (Guénette 2014, user's guide, BOBLME-2014-Ecology-13) | **sought, not obtained** | Direct companion to this model and the likeliest home of the `.ewemdb`. See below. |
| `BOB-2019` (Karim et al., Bangladesh coastal) | no | Metadata only, no file, and a different model. |

Because Appendix A1.1 is an allocation of Sea Around Us catch names — the very names in the
catch file — this mapping is unusually direct. 259 of the 315 catch taxa are matched to a group
by a line the author wrote for exactly that purpose.

## Supplements sought and not obtained

- **`BOBLME-2014-Ecology-13.pdf` — "User's guide to the Ecopath with Ecosim model of the Bay of
  Bengal Large Marine Ecosystem", Guénette (2014).**
  URL <https://www.boblme.org/documentRepository/BOBLME-2014-Ecology-13.pdf>.
  Fetch attempted: **failed, `getaddrinfo ETIMEOUT www.boblme.org`** — the project host does not
  resolve, the same failure the archive metadata records. A web search for a mirror returned only
  the same dead host, a Semantic Scholar index page with no file, and unrelated BOBLME items. Not
  obtained. It is not needed for membership — the 2013 report's appendices already carry it — but
  it may hold the model file itself and a stated diet/landings breakdown per region.
- **`Bengal report 27aug2014 net.pdf`**, the later edition of the same report, listed in the
  archive metadata: on the same unreachable host; not retrieved. The December 2013 edition in
  the archive contains all three appendices used here.
- No separate data supplement is cited anywhere in the report. A1.1, A1.2 and A1.3 are printed
  inside the PDF.

## What the mapping does, and the numbers

| | before | after |
| --- | --- | --- |
| catch tonnage on a named group | 77.5 % | **100.0 %** |
| taxa unresolved | 12 (22.3 % of tonnage) | 0 |
| rows with no decision | 27 | 0 |
| rows carrying `inherited_mapping` | 276 (77.5 %) | 0 |
| model groups carrying catch | 20 of 50 | 30 of 50 |

Confidence, by tonnage: `high` 69 taxa / 16.5 %, `medium` 245 / 83.5 %, `low` 1 / < 0.1 %,
`unresolved` 0. 239 taxa (83.1 % of tonnage) are composites — nearly all of them the region
2 / region 3 split, which is why the file is dominated by `medium`: the *group* identity is
usually certain, the *region* share is estimated. A single-group row that A1.1 names outright is
`high`.

Coverage reaching 100 % is not a sign of forcing. Every one of the 315 catch labels is a Bay of
Bengal marine organism, and the model has a compartment for each habitat the fishery touches —
oceanic, neritic, shelf demersal, benthic, cephalopod, jellyfish and deep water. There is no
billfish-in-a-shelf-model case here: `Marlins`, `Tuna-like`, `Bigeye tuna` and `Yellowfin tuna`
are real groups in this model.

`34_1_Bay_of_Bengal_(1978).members.csv` transcribes Appendix A1.1 mechanically (390 printed
names, pp. 37–41) so the mapping can be checked against the paper rather than against itself.
The validator reports **259 taxa confirmed (74.2 % of tonnage), 0 contradicted**. Two conventions
in that file:

- A1.1's labels carry no region, so each stratified label is expanded to **all three** regional
  groups (`1 SM inv`, `2 SM inv`, `3 SM inv`). The check therefore tests the guild/taxonomic
  decision, which A1.1 does document, and stays silent on the region decision, which it does not.
  It cannot be satisfied by my region choice alone.
- A1.1's three residual labels — `Miscellaneous fishes`, `Perciformes`, `Pleuronectiformes` — are
  not model groups, so those rows are omitted rather than invented.

## The coarse labels

| label | t | decision | basis |
| --- | ---: | --- | --- |
| `Marine fishes not identified` | 46.5 M (18.5 %) | `2/3 L pisc comm` + `SM pisc` + `SM inv` + `L pisc` | A1.1 sends it to the paper's residual `Miscellaneous fishes`, spread over the fish groups of the region (p. 10). SAU classes the pile as **medium demersals**, so I kept the model's four demersal/benthic finfish pools and dropped the pelagic ones (`S pelagics`, `Carangids`, `Milkfish plus`, `Hilsa`, `Indian mackerel`). |
| `Elasmobranchii` | 3.44 M | `Oceanic sharks` + `Coastal elasmobranch` | A1.1 verbatim; weights by catch composition, which is available and non-circular here because both groups carry solo-assigned catch. |
| `Scombridae` | 2.46 M | `Tuna-like` + `Coastal scombrids` + `2-3 Indian mackerel` | p. 10 verbatim. |
| `Perciformes` | 1.19 M | same set as `Marine fishes not identified` | A1.1 residual; SAU class medium demersals, Perch-likes, and all four pools are largely perciform. |
| `Marine pelagic fishes not identified` | 0.89 M | `2/3 S pelagics` + `Carangids` | A1.1 residual; SAU class medium pelagics excludes the demersal pools. |
| `Batoidea`, `Dasyatidae`, `Rajiformes` | 0.89 M | `Coastal elasmobranch` | Deliberate narrowing of A1.1's blanket "oceanic, coastal sharks": A1.3 places every batoid in the model in `Coastal elasmobranch`, the sole exception being the oceanic pelagic stingray. |
| `Carcharhinus`, `Chondrichthyes`, `Carcharhinidae`, `Lamniformes` | 0.57 M | `Oceanic sharks` + `Coastal elasmobranch` | A1.1 verbatim. |
| `Pleuronectiformes` | 36 k | `2/3 SM inv` + `SM pisc` | A1.1 residual; A1.3 puts the model's flatfishes in exactly those two pools. |

## Judgement calls a reviewer should push on

1. **`model_biomass` rather than `model_catch` for the region 2 / 3 split** — the table above
   quantifies it. Biggest single lever in the file.
2. **Excluding region 1 outright.** It rests on the Maldives being west of the LME_034 polygon
   and on the region-1 high seas having no shelf. If this project's LME_034 unit were ever
   redefined to include Maldivian waters, six shelf pools would come back into every candidate
   set. The model's own region-1 shelf catch is tiny (0.29 % of its 1978 total), so the effect
   would be small, but it should be a decision rather than an oversight.
3. **`Scombridae` (2.46 M t) weighted by catch composition.** Because `Rastrelliger` records
   dominate identified scombrid landings here, that basis gives `2-3 Indian mackerel` about 69 %
   of the split and pulls the taxon SPPR down to roughly 1,200 against about 2,800 under equal
   weights. Sea Around Us reports `Rastrelliger` separately at 15.7 M t, which is an argument
   that the *residual* `Scombridae` pile leans towards tunas and seerfishes instead. The paper
   names the three groups but no proportions.
4. **The candidate set for `Marine fishes not identified`.** The paper spread it over *all* the
   region's fish groups; I narrowed it to the demersal four on the Sea Around Us habitat class.
   Widening it back would move 18.5 % of the tonnage towards the low-SPPR small-pelagic pools.
5. **`Balistidae` → `SM pisc`** (59 k t), against the first-generation `SM inv`. A1.1 names only
   one balistid, *Abalistes stellaris*, and puts it in SM pisc; the monacanthids it sends to
   SM inv are a different family.
6. **`Polynemus paradiseus` → `SM pisc`** (159 k t), against the first-generation `L pisc`.
   A1.1's genus-level line for *Polynemus* is "L pisc, SM inv", but A1.3 lists this species by
   name in the SM pisc list; the species-level statement wins.
7. **`Lepidocybium flavobrunneum` → `ML bathy`**, the only `low` row in the file and an analogue,
   not a documented member. 1 t of catch; it does not matter numerically.
8. **Where I split a family the first mapping did not.** `Ariidae` and `Siluriformes` (4.6 M t)
   go to `Milkfish plus | SM inv | SM pisc` because A1.1 says "Milkfish, Minv Mpisc", not to
   `Milkfish plus` alone; `Gobiidae`, `Soleidae`, `Holocentridae` and `Odontamblyopus rubicundus`
   go to `SM inv | SM pisc`; `Polynemidae` and `Polynemus` to `L pisc | SM inv`;
   `Tetraodontidae` to `Milkfish plus | SM inv`. Each follows a compound A1.1 label the earlier
   mapping had collapsed to its first term.

## What the mapping cannot cover

- **Nothing is unresolved**, so there is no tonnage outside the model. The uncertainty is not in
  *whether* a taxon belongs but in *how much of it belongs to region 2 versus region 3*, and that
  is carried by the `weights` column rather than by an unresolved row.
- **The region split is fixed over time by construction** (one SPPR per taxon per method), while
  the real balance of the Bay's fisheries shifted eastward across 1950–2019. A time-varying
  regional split would need a catch series resolved by EEZ within the LME, which this repository
  does not hold.
- **The 1978 base year** predates most of the region 3 expansion and all of the Bangladeshi
  industrial trawl growth.
- **`taxon_descr` is empty in the extracted workbook.** Everything in this mapping's
  `groups.csv` was re-read from the PDF by hand; a re-extraction that captured A1.1 and A1.3
  would make the join checkable without the paper.
