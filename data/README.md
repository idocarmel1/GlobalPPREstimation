# `data/` — one directory per ecosystem

This is the integration layer. Everything upstream is keyed differently: catch archives by
unit, articles by region directory, Ecopath models by a filename prefix, NPP by layer plus
region id. This directory joins all of it on **`unit_id`** (`LME_003`, `EEZ_711`, `HS_018`)
and gives each ecosystem one place to look.

Built by `tools/build_ecosystem_data.py`. Re-run it with `--force` after any upstream change.

## Layout

```
data/
  INDEX.csv                    coverage matrix — one row per ecosystem, read this first
  <unit_id>/
    <unit_id>.xlsx             the five-sheet summary (the thing to open)
    metadata.json              identity, geography, coverage, pointers to bulk sources
    npp.json                   net primary production by satellite model, when known
```

Bulk inputs are **referenced, not copied**. The catch archives and the article archive run
to gigabytes between them; duplicating those per ecosystem would add nothing and cost a lot.
`metadata.json` carries relative paths to the real files.

## The workbook

Five sheets, deliberately few columns.

| sheet | what it holds |
| --- | --- |
| **Summary** | identity and geography, then one row per year: catch, PPR, and PPR as a percentage of NPP |
| **Catch** | taxon × year, tonnes, 1950–2019, with functional and commercial group |
| **SPPR** | the simple per-taxon `(1/TE)^(TL-1)`, and — where an Ecopath model exists — that model's per-group SPPR across all 20 methods |
| **PPR** | taxon × year, catch × SPPR |
| **NPP** | the five satellite estimates plus the ensemble, 2019 |
| **Taxon SPPR** | *(where a mapping exists)* each taxon's Ecopath group, and that group's SPPR under all 20 methods |
| **PPR by method** | *(where a mapping exists)* year × method, tonnes, with a catch-coverage line |

A sheet with no data for an ecosystem says so in a line rather than sitting empty.

## Coverage — what actually exists

364 ecosystems have catch data. Beyond that the picture thins out fast, and the workbook is
honest about it rather than hiding the gaps.

| asset | ecosystems |
| --- | --- |
| catch, per taxon per year, 1950–2019 | **364** |
| archived source articles | 109 |
| net primary production | 82 |
| an extracted Ecopath model and SPPR results | **10** |

The ten complete ones are the pilot — the top ecosystems by the 1995 PPR ranking:
`HS_077`, `LME_013`, `LME_027`, `LME_028`, `LME_032`, `LME_034`, `LME_035`, `LME_036`,
`LME_047`, `LME_052`. Several carry more than one published model, which is why sixteen
model workbooks map onto ten ecosystems.

198 units have no `region_type` or geography because they fall outside the 167-region
curated selection in PPRAtlas. They still have catch and PPR.

## How PPR is computed here, and what it is not

`SPPR = (1/TE)^(TL - 1)` with `TE = 0.1`, so `10^(TL - 1)`, applied **per taxon** using each
taxon's own trophic level. `PPR = catch × SPPR`, summed over taxa.

This is verified against the upstream pipeline: the workbook's 2019 total reproduces
`ppr_species` from `SeaAroundUsExtraction` exactly — 0.000000 % difference on every unit
checked. What is new here is that it runs across all seventy years rather than one.

Taxa with no trophic level are omitted and contribute no PPR. Coverage is currently complete,
and a `tl_coverage_complete` check upstream fails loudly if that stops being true.

**The `PPR` sheet is always the first-pass estimate, never the network method.** It uses the
simple per-taxon calculation, which needs no group mapping and so works for all 364
ecosystems. Where an Ecopath model and a mapping both exist, the network results live in the
separate `PPR by method` sheet — see below. Keeping them apart matters: the two are not
interchangeable, they cover different fractions of the catch, and averaging or substituting
one for the other would be wrong.

## Ecopath PPR — done for three ecosystems

`LME_032`, `LME_034` and `LME_047` now carry the full chain: catch taxon → Ecopath group →
SPPR under 20 methods → PPR. The mappings came from the completed examples shipped with
`skills/ewe-species-to-group-mapper`; `tools/merge_taxon_sppr.py` performs the join and
refuses to run if any mapped group is absent from the model's own `groups_df`, since a
mismatch there would produce confident fiction.

Coverage is reported two ways, and the difference matters. `LME_052` has **44 % of its taxa
unresolved but 90 % of its catch tonnage resolved** — the unmapped taxa are overwhelmingly
small-catch strays. For PPR, tonnage coverage is the number that counts; taxon-count coverage
mostly measures how many rare species wandered into the catch record.

| ecosystem | taxa unresolved | catch tonnage resolved |
| --- | --- | --- |
| `LME_032` Arabian Sea | 14 / 393 | 78 % |
| `LME_034` Bay of Bengal | 12 / 288 | 78 % |
| `LME_047` East China Sea | 27 / 254 | 78 % |
| `LME_052` Sea of Okhotsk | 66 / 151 | 90 % |

`LME_052`'s high taxon-level unresolved rate is a real property of the source, not a mapping
failure. The usable model covers only the **northeastern** Okhotsk — cold water, mammal-focused,
1980s — while the catch series covers the whole LME and includes tropical and oceanic species
(snappers, groupers, tuna, billfish, mako) the model was never built to represent. Neither source
paper contains a species-to-group membership table, so assignments rest on taxonomic containment
rather than a documented list, and the explanations say so rather than overclaiming.

For `LME_047` in 2019 the network methods give 0.4–1.5 billion tonnes against the simple
trophic-chain method's 3.4 billion. Lower is expected: the network methods follow the real
diet matrix and recycling instead of assuming a pure chain at fixed transfer efficiency.
Part of the gap is also coverage — the simple method runs on every taxon.

## What is missing, deliberately

- **Ecopath PPR for the remaining ecosystems.** Needs the mapping run per ecosystem. Only
  seven models are marked usable in `model_selection.xlsx`, so seven is the ceiling until
  more articles are extracted.
- **NPP for EEZs.** The NPP dataset covers LME and High Seas only.
- **NPP over time.** A single 2019 value, so `ppr_over_npp_percent` uses a constant denominator
  across all years. Treat the trend in that column as driven by PPR alone.
