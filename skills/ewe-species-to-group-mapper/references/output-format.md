# Output format

Up to four files per model, under `data/<unit_id>/mapping/`. The model stem is the exact
filename stem of the SPPR workbook in `PPREstimation/output/top10/`, so
`47_2_East_China_Sea_(2018).xlsx` gives:

```
data/LME_047/mapping/47_2_East_China_Sea_(2018).csv          the mapping
data/LME_047/mapping/47_2_East_China_Sea_(2018).groups.csv   the group dictionary
data/LME_047/mapping/47_2_East_China_Sea_(2018).notes.md     provenance and limits
```

Plain CSV, not a workbook. The mapping is data; `tools/build_model_workbook.py` renders it
into `data/<unit_id>/models/<model_stem>.xlsx` with the confidence colouring. That split means a mapping is
diffable in git, cannot corrupt a workbook someone has open, and cannot be silently
reformatted.

`prepare_mapping.py` writes the mapping CSV pre-filled with one row per catch taxon and
empty decisions. Fill the decisions in; do not add, remove or reorder rows.

## `<model>.csv`

| column | contents |
| --- | --- |
| `taxon` | verbatim from the catch. Pre-filled. Never edit. |
| `common_name` | pre-filled from Sea Around Us |
| `functional_group` | pre-filled — the SAU habitat-and-size class |
| `commercial_group` | pre-filled |
| `group` | one verbatim `group_name`, several separated by ` \| `, or `Unresolved` |
| `weights` | blank, a basis name, or one number per group separated by `\|` |
| `confidence` | `high` / `medium` / `low` / `unresolved` |
| `evidence` | the code for the decisive rule, from the list below |
| `explanation` | why, in a sentence a reviewer can check |

### `group`

Copy group names character for character from `groups_df`, including capitalisation,
punctuation, spaces and abbreviations (`Sm.dem.benth.`, `2 SM inv`, `Crabs & Lobster`).
The join downstream is on the exact string; a near-miss silently drops the taxon's PPR.

```
Piscivores                                     one group
Clupeids | Anchovies | Small Benthopelagics    composite, apportioned
Unresolved                                     outside the model
```

### `weights`

| value | meaning |
| --- | --- |
| *(blank)* | apportion by **catch composition**: each candidate group's share of the catch that other identified taxa put on it, over the whole period |
| `model_biomass` | apportion by the groups' biomass in `groups_df` |
| `model_catch` | apportion by the groups' catch in `groups_df` |
| `equal` | equal shares |
| `0.6 \| 0.3 \| 0.1` | explicit, one per group in order; normalised to sum to 1 |

Ignored when `group` names one group or `Unresolved`. If the chosen basis yields nothing —
no candidate group has any catch, say — the merge step falls back through `model_catch`,
`model_biomass`, `equal` and records which it used.

Weights do not vary by year. A taxon has one SPPR per method, so
`PPR = catch(taxon, year) x SPPR(taxon, method)` stays exact.

### `confidence`

| value | fill | when |
| --- | --- | --- |
| `high` | green `#C6EFCE` | the taxon is listed in the group, is a synonym of a listed member, or the group is defined by a taxon that contains it |
| `medium` | yellow `#FFEB9C` | habitat, size, diet and TL together select one group; or a well-founded composite with data-derived weights |
| `low` | orange `#FFC49C` | defensible but thin — an analogue, a wide candidate set, or equal weights |
| `unresolved` | red `#FFC7CE` | `group` is `Unresolved` |

`high` and `Unresolved` are mutually exclusive, and so are `unresolved` and a named group.
The validator enforces both.

### `evidence`

`explicit_member`, `synonym`, `taxonomic_containment`, `habitat_size_guild`,
`inherited_model`, `analogue`, `composite_split`, `none`.

A row with several groups must use `composite_split`. `Unresolved` uses `none`.

### `explanation`

State the decisive fact. A reviewer must be able to go to the source and check it.

Good:

> Table 3 lists *Trichiurus lepturus* under Hairtails; this record is that species.
> Nemipteridae are small benthic invertebrate feeders on the Gulf trawl grounds, matching
> the model's `Sm.dem.benth.` definition on habitat, size and diet.
> Order-level record spanning both clupeid groups; apportioned by the catch composition of
> the identified clupeids in this LME.
> The model is a 1963 coastal-shelf model with no oceanic pelagic compartment, so a
> swordfish record has no home in it.

Not good: "best match", "closest group", "similar species", "see above".

Say when the evidence is inference. Do not write that the paper states something it does
not.

## `<model>.members.csv` — transcribe the paper's own table when it has one

If the paper contains a species-to-group table, **transcribe it to disk before mapping**.
This is the single highest-value thing you can do, and it is the difference between a
mapping a reviewer can check and one they have to trust.

```
printed_name, accepted_name, group_name, source_page
Formio niger, Parastromateus niger, Med Benthic Carnivores, p.21
Leiognathus bindus, Photopectoralis bindus, Small Benthic Carnivores, p.21
```

`printed_name` is the paper's spelling, `accepted_name` the current one. Both are indexed,
because the mismatches hide in the older nomenclature: a table printed in 1998 says
`Formio niger` where the catch record says `Parastromateus niger`, and a mapping can
contradict a documented member without either name looking wrong on its own.

`validate_mapping.py` picks the file up automatically and **treats a contradiction as an
error, not a difference of opinion**. It also reports how much tonnage the table confirms,
which is the honest measure of how much of the mapping is evidence rather than judgement.

Why this matters more than it sounds: in the Arabian Sea the table existed in the archive
all along — 129 species numbered under 24 groups in CMFRI Bulletin 51 — and the first
mapping never found it. Checking against it caught five wrong assignments carrying 2.3 % of
the catch, every one of them the same failure: the Sea Around Us size class read in
preference to the model's own placement.

## `<model>.groups.csv`

One row per group, whether or not any catch lands on it. This is what lets someone audit
the mapping without re-reading the paper.

```
group_name, model_tl, grouping_basis, explicit_members, supporting_taxa,
membership_source, source_relationship, source_location, source_url, notes
```

- `grouping_basis` — taxonomic, feeding guild, habitat, size, life stage, single stock,
  residual pool, non-living, spatial stratum
- `membership_source` — where the member list came from, or `not documented`
- `source_relationship` — `direct source`, `supporting regional source`, or
  `analyst inference`
- `source_location` — file plus page, table, figure or sheet

## `<model>.notes.md`

Short. What a reader needs before trusting the numbers:

- the model: citation, DOI, years, area, and how that area relates to the unit
- the axis the group list is built on, and what any prefix means
- which supplements you looked for, which you got, and which you did not
- the substantive judgement calls, and where a reviewer should push back
- what the mapping cannot cover, and why

If the model's area is smaller than the unit — the northeastern Okhotsk against the whole
sea — say so at the top. It is the first thing that explains an odd coverage number.
