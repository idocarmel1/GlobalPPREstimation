# Why only 19 matches, and how to improve them

**The 19 matches are a conservative first pass, not a proven limit of the model.** The mapper used exact species names from Supplement Table S3 plus three verified synonyms. It did not implement broader group aliases, taxonomic containment, ecological guilds or composite allocations. That restriction explains part of the low coverage; the coastal Kyoto model's limited representation of the whole Sea of Japan explains the rest.

My earlier explanation was too restrictive for **Scomber**: the model puts the two documented Japanese mackerels into one Mackerel group. Their proportions are unnecessary when both receive the same coefficient. This is the clearest useful improvement to review first.

No production mapping, selection, canonical model or workbook was changed. The selected year remains 2013; switching to 1985 would not add missing groups because both years have the same group structure.

## Counts versus catch coverage

The 253 entries are taxon labels, not 253 species: they include genera, families, orders and unidentified aggregates. The 19 matched species labels occupy 17 model groups and represent **7.51% of labels**, **25.0500% of 2019 catch** (648,029.94 of 2,586,941.84 tonnes), and **24.6845% of recorded catch summed over 1950–2019**.

Five matched taxa—sardine, anchovy, chub mackerel, Japanese flying squid and Japanese jack mackerel—already account for 23.46% of 2019 catch. Adding rare names can improve the taxon count without materially improving PPR coverage.

## Ten largest unmatched 2019 catches

Percentages use all recorded 2019 catch.

| Label | Tonnes | Share | Diagnosis |
|---|---:|---:|---|
| Gadus chalcogrammus — Alaska pollock | 494,220 | 19.10% | No documented pollock/cod or generic cold-water fish group |
| Marine fishes not identified | 315,222 | 12.19% | Unknown composition includes stocks absent from the model |
| Clupea pallasii — Pacific herring | 109,935 | 4.25% | Source Round herring is Etrumeus, not Clupea |
| Scomber | 106,956 | 4.13% | Strong pooled-group alias; first-pass rule was overly strict |
| Pectinidae — scallops | 86,406 | 3.34% | Potential Bivalve extension, but source representatives are oysters |
| Gadus macrocephalus — Pacific cod | 80,662 | 3.12% | No cod group |
| Cololabis saira — Pacific saury | 62,419 | 2.41% | No saury group |
| Oncorhynchus gorbuscha — pink salmon | 61,706 | 2.39% | No salmon group |
| Ammodytes personatus — sand lance | 42,703 | 1.65% | No documented sand-lance group |
| Oncorhynchus aggregate | 41,709 | 1.61% | No salmon group |

Together these are **54.19% of all 2019 catch**. Historical priorities are similar: pollock contributes 47.53 million tonnes, unidentified fish 18.94 million, Scomber 10.64 million and saury 7.86 million over 1950–2019. The top ten historical unmatched labels account for 54.50%; [the historical table](TOP10_UNMATCHED_1950_2019.csv) additionally highlights Pleuronectidae and Pleurogrammus azonus. These are not the source's Paralichthys flounder or Scomber mackerel.

## Exact names and source corrections

I queried **all 70 binomial strings in representative Table S3** against WoRMS. Sixty-six returned records; four source spellings did not. **No additional unambiguous accepted-name match** was found among unresolved catch labels. The useful Sardinops sagax, Magallana gigas and Hemitrygon akajei synonym matches were already included. [Complete query audit](source_name_taxonomy_audit.json).

Two source issues warrant review:

- **Scomber australasicus → Mackerel:** S3 prints Scomber austlasicus. This is a well-supported spelling inference, not an exact synonym hit. It adds zero 2019 catch but 6,375 historical tonnes. Preserve the printed spelling and document any mapping correction. [WoRMS](https://www.marinespecies.org/rest/AphiaRecordByAphiaID/219715) and [FAO's Japanese fisheries account](https://www.fao.org/4/t0179e/T0179E05.htm) support the intended species.
- **Thunnus orientalis → Tuna:** the main paper explicitly identifies this species on [p.585](../../../papers/SOJ-2023/evidence/page_13.txt), while S3 says T. thynnus. Prioritizing the main text could add 2,392.56 tonnes, or **0.0925 percentage points**. This needs a source-precedence decision: bare T. thynnus and T. orientalis are distinct accepted names; only T. thynnus orientalis is the relevant synonym. [WoRMS taxon list](https://www.marinespecies.org/aphia.php?p=taxlist&tName=Thunnus+thynnus).

The other unrecognized source spellings were Cypselurus doederleini, Apostichopus armata and Crossostrea nippona. They do not reveal an immediate unmatched catch-species counterpart. No silent corrections were made.

## Pooled aliases and broader membership

S3 supplies **representative taxa**, not an exhaustive roster. The [main methods, p.576](../../../papers/SOJ-2023/evidence/page_04.txt), describe pooling by trophic properties and distribution. Exact-only matching is therefore narrower than a complete ecological mapping.

**Recommended first package for review:**

| Proposal | Added 2019 catch | Coverage gain | Basis |
|---|---:|---:|---|
| Scomber → Mackerel | 106,955.52 t | +4.1344 pp | Both documented Japanese mackerels share this group; FAO supports mixed reporting. Their proportions do not affect its coefficient |
| Auxis → Frigate tuna | 483.67 t | +0.0187 pp | Source explicitly pools A. rochei and A. thazard; catch label is bullet and frigate tunas |
| Document S. australasicus spelling inference | 0 t | +0 pp | Historical gain only; source spelling retained |

This would give **22/253 labels**, **29.2032% of 2019 catch**, and **29.9794% of historical catch**. These are proposed coverage totals, not applied mappings. Separately accepting the main-text Tuna identification would give **29.2957% in 2019**.

The Scomber recommendation is restricted to the documented regional genus pool, not unrelated fish also called mackerel. FAO's historical account supports mixed japonicus/australasicus reporting; it does not establish every contemporary Sea Around Us record's composition. Keep that distinction in the mapping evidence.

Other candidates have potential but need fuller group definitions or ecological review:

| Candidate | Maximum 2019 gain from that row | Remaining issue |
|---|---:|---|
| Pectinidae → Bivalve | +3.3401 pp | Whether scallops belong in this oyster-represented pool and its rates are representative |
| Seriola → Yellowtail | +1.0204 pp | S3 Amberjack/main Yellowtail is a group-name alias; representative S. quinqueradiata does not prove all amberjacks belong |
| Bivalvia → Bivalve | +0.3200 pp | Broad taxonomic fit; full group and geographic scope unverified |
| Octopus → Octopus | +0.2793 pp | Scope beyond representative O. vulgaris and the source's benthic definition |
| Trachurus → Jack mackerel | +0.0290 pp | Regional genus record versus representative T. japonicus |
| Crassostrea → Bivalve | +0.0023 pp | Genus aggregate versus named oyster representatives |

These are conditional opportunities, not confirmed omitted members. Group labels establish candidates; they do not validate the modeled rates for every related fishery. [All proposals and historical gains](PROPOSED_EXTENSIONS.csv).

## Composite labels require supported groups and weights

**Teuthida** could add **1.2682 pp** through Flying squid and Other squids, after verifying the candidate set and a between-group split. Those groups have different coefficients, unlike the Scomber case. Identified catch composition, source fleet catches or another documented composition source could support a reviewed split; automatic equal weights would add an assumption.

**Miscellaneous marine crustaceans** could add **1.2535 pp**, but the source's Prawn/Shrimp distinction is specific: Prawn lists Metapenaeus ensis while Shrimp includes other penaeids and Crangon. A generic shrimp classification does not determine that split. **Octopoda** could add **0.2950 pp**, but its catch label includes argonauts whereas the source group is benthic Octopus; incompatible members must not be hidden in a composite.

**Unidentified marine fish** represent **12.1851 pp**, but distributing them only among Kyoto groups would omit major regional stocks. Better weights cannot compensate for an incomplete candidate set.

## How far can improvement go?

Pollock, Pacific cod, Pacific herring, saury, sand lance and three salmon labels alone represent **36.1392% of 2019 catch** without documented source counterparts. If these eight labels remain unresolved, even assigning every other label would cover at most **63.8608%**. Other scope gaps would lower that ceiling. A 95% target cannot be achieved solely by safe name and alias cleanup under the currently documented model structure.

Review the small pooled-alias package first, then seek the authors' complete membership definitions or native model to assess broader groups and the unresolved year-specific diets. Substantially higher whole-LME coverage will likely need a wider or complementary model, or an explicitly approved ecological-proxy scheme with separate uncertainty. This does not replace the user's 2013 selection. No new paper was extracted and no proxy adopted.

## Verification

[REVIEW_NUMBERS.json](REVIEW_NUMBERS.json) retains exact arithmetic. Historical percentages sum recorded 1950–2019 catch. Proposed package gains use distinct currently unresolved rows, avoiding double counting. [FINAL_VERIFICATION.json](FINAL_VERIFICATION.json) records unchanged workbook/model hashes and report checks. No SPPR or Monte Carlo rerun was needed.
