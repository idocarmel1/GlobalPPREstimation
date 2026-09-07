# `data/` — one directory per ecosystem

This is the integration layer. Everything upstream is keyed differently: catch archives by
unit, articles by region directory, Ecopath models by a filename prefix, NPP by layer plus
region id. This directory joins all of it on **`unit_id`** (`LME_003`, `EEZ_711`, `HS_018`)
and gives each ecosystem one place to look.

## Layout

```
data/
  INDEX.csv                     coverage matrix — one row per ecosystem, read this first
  model_selection.xlsx          which article and model each ecosystem uses, and why
  <unit_id>/
    <unit_id>.xlsx              the ecosystem workbook (the thing to open first)
    metadata.json               identity, geography, coverage, pointers to bulk sources
    npp.json                    net primary production by satellite model, when known
    mapping/                    one CSV per Ecopath model: which group each catch taxon is in
    models/<model_stem>.xlsx    one workbook per Ecopath model
```

Bulk inputs are **referenced, not copied**. The catch archives and the article archive run
to gigabytes between them; duplicating those per ecosystem would add nothing and cost a lot.
`metadata.json` carries relative paths to the real files.

Built by `tools/build_ecosystem_data.py` (the base workbook) and
`tools/build_model_workbook.py` (the model workbooks). `tools/verify_model_workbook.py`
checks the latter, including the formulas nothing else evaluates.

## Two kinds of workbook, and why they are separate

**`<unit_id>.xlsx` holds catch, trophic-chain SPPR/PPR, NPP and model-group scope tables.**
It exists for all 364 ecosystems with catch. Scoped rows name their model explicitly;
models are never averaged. An ecosystem with no extracted model has a clear missing-data note.

| sheet | what it holds |
| --- | --- |
| **Summary** | identity and geography, then one row per year: catch, PPR, PPR as a percentage of NPP |
| **Catch** | taxon × year, tonnes, 1950–2019, with functional and commercial group |
| **SPPR** | the simple per-taxon `(1/TE)^(TL-1)` |
| **PPR** | taxon × year, catch × SPPR |
| **NPP** | the five satellite estimates plus the ensemble, 2019 |
| **sppr_all / sppr_inner / sppr_PP** | per-group SPPR, one row per model and exact group name |
| **Recycling** | `b`, `rho living`, convergence, health status and diagnostic configuration |

**`models/<model_stem>.xlsx` holds one Ecopath model's answer.** One workbook per model, so
every column inside belongs to that model and none needs a model prefix.

| sheet | what it holds |
| --- | --- |
| **Summary** | identity, coverage, and per-year catch, PPR and PPR/NPP under a headline method |
| **Catch** | taxon × year, as above |
| **Taxon-Group Map** | each taxon's group, weights, confidence (coloured) and the reasoning |
| **SPPR** | taxon × method — the simple per-taxon value and the model's, side by side |
| **PPR by method** | method × year, summed over every taxon |
| **PPR by taxon** | taxon × method for one year, chosen from a dropdown |
| **Model groups** | the model's own `groups_df` and per-group SPPR |
| **NPP** | as above |
| **sppr_inner / sppr_PP** | mapped taxon SPPR in each source scope |
| **PPR inner / PPR PP** | annual PPR by method in the matching scope |
| **Recycling** | upstream diagnostic values and configurations |

An ecosystem with two published models has two of these, and **they are not averageable**.
They rest on different areas, years and group structures. Keeping them in separate files is
the point: a single sheet holding both invites a reader to take a mean of two answers to
different questions.

Inside one workbook the twenty methods are likewise not alternatives to be averaged. The
spread between them is the result.

`PPR by method` carries a **status** column, because not every method works on every model.
Diagnostic and result checks are kept separate:

| flag | what happened | example |
| --- | --- | --- |
| `DIVERGED` | negative SPPR anywhere in the source model, including unfished groups | Sea of Okhotsk under the `TE` solver variants: four groups negative, one at −2.7 × 10¹⁰, giving −71 billion tonnes |
| `IMPLAUSIBLE` | positive but orders of magnitude above the trophic-chain estimate | Bay of Bengal `sym_GE_asDC`: 2.1 × 10¹³ tonnes, 6,700× the simple method and thousands of times that sea's annual primary production |
| zero / did not resolve | the method returned nothing usable | `SPPR_1986` on three models; the six `sym_*` methods on the Gulf of Thailand |

Across the healthy models the network methods run 0.1–4.6× the trophic-chain estimate, so
the implausibility threshold sits at 25×. It is a plausibility flag, not a claim about which
method is right — the flagged numbers are still in the sheet, marked. **The Summary sheet
chooses its headline method from the unflagged ones**, which is why the Sea of Okhotsk leads
with `Ulanowicz_TE` rather than the usual `new_TE_EEfix`. A flag describes the model under
that method, not the mapping; `model_health` in the SPPR workbook is the upstream record.

The exact SPPR_new configurations `new_GE`, `new_TE_EEfix` and `new_WithEgestion` also inherit a failed `diagnose_sppr()` verdict. A diagnostic for one configuration is not silently applied to a different solver or Monte Carlo setup.

Two grey rows apply the simple method to the **catch-weighted mean trophic level of each Sea
Around Us group** rather than to each taxon. SPPR is convex in trophic level, so aggregating
first and exponentiating after always understates the per-taxon sum — Jensen's inequality.
For the Sea of Okhotsk in 2019 that is 2.13 against 2.80 billion tonnes, a 24 % gap. Those
rows exist to size that effect, not to be used as estimates.

## Coverage — what actually exists

364 ecosystems have catch data. Beyond that the picture thins out fast, and the workbooks
are honest about it rather than hiding the gaps.

| asset | ecosystems |
| --- | --- |
| catch, per taxon per year, 1950–2019 | **364** |
| archived source articles | 109 |
| net primary production | 82 |
| an extracted Ecopath model and SPPR results | 10 |
| a taxon-to-group mapping | 8 |
| **a model workbook, i.e. PPR by method** | **8** |

Those last three rows are deliberately separate in `INDEX.csv` too, as `ecopath_models`,
`models_mapped` and `model_workbooks`. An extracted model is not an answer: it needs a
mapping before any PPR comes out of it, and several extracted models are marked unfit and
will never get one. Sixteen model workbooks exist upstream; eight ecosystems have mappings and
ten downstream model workbooks. A workbook can retain failed methods for audit; its presence
does not make every value scientifically usable.

The ten are the pilot — the top ecosystems by the 1995 PPR ranking: `HS_077`, `LME_013`,
`LME_027`, `LME_028`, `LME_032`, `LME_034`, `LME_035`, `LME_036`, `LME_047`, `LME_052`.
Several carry more than one published model, which is why sixteen model workbooks map onto
ten ecosystems. `model_selection.xlsx` records which are actually usable — a model can be
extracted and still be unfit.

198 units have no `region_type` or geography because they fall outside the 167-region
curated selection in PPRAtlas. They still have catch and PPR.

## How PPR is computed, and the two answers that are not the same thing

`SPPR = (1/TE)^(TL - 1)` with `TE = 0.1`, applied **per taxon** using each taxon's own
trophic level. `PPR = catch × SPPR`, summed over taxa. This needs no model, so it runs for
all 364 ecosystems, and it is what the `PPR` sheet of the base workbook holds.

It is verified against the upstream pipeline: the 2019 total reproduces `ppr_species` from
`SeaAroundUsExtraction` exactly — 0.000000 % difference on every unit checked. What is new
here is that it runs across all seventy years rather than one.

The network methods are different animals. They follow the model's real diet matrix and
recycling instead of assuming a pure chain at fixed transfer efficiency, and they live in
the model workbooks. For `LME_047` in 2019 they give 0.4–1.5 billion tonnes against the
simple method's 3.4 billion. Lower is expected. Part of the gap is also coverage — the
simple method runs on every taxon, the network methods only on taxa mapped to a group.

Taxa with no trophic level are omitted from the simple method and contribute no PPR.
Coverage is currently complete, and a `tl_coverage_complete` check upstream fails loudly if
that stops being true.

## The mapping, and how coverage is measured

`mapping/<model_stem>.csv` is produced by `skills/claude/ewe-species-to-group-mapper` and holds one
row per catch taxon: the Ecopath group, the confidence, the evidence code and the reasoning.
`<model_stem>.resolved.csv` alongside it records the weights the builder actually used, so
an apportioned taxon can be audited.

**Coverage is reported by tonnage, not by taxon count, and the two diverge sharply.**
`LME_052` had 44 % of its taxa unresolved and 90 % of its catch tonnage resolved — the
unmapped taxa were overwhelmingly small-catch strays. PPR is a tonnage quantity, so tonnage
coverage is the number that counts; taxon-count coverage mostly measures how many rare
species wandered into the catch record.

A taxon whose label sits above genus — `Marine fishes not identified`, `Decapoda`,
`Sciaenidae` — may genuinely belong to several groups. It is **apportioned** across them,
weighted by the catch that identified taxa already put on each, rather than discarded. Those
labels carry 20–45 % of an LME's catch, and writing them off is what held the first
generation of mappings at 78 %. `Unresolved` still exists and still means *outside the
model* — a billfish in a coastal-shelf model with no oceanic compartment.

`tools/build_model_workbook.py` refuses to run if a mapped group is absent from the model's
own `groups_df`, since a mismatch there would produce confident fiction.

## What is missing, deliberately

- **Ecopath PPR for most ecosystems.** Needs a usable model and a mapping per ecosystem.
  `model_selection.xlsx` is the ceiling on how far this can go without more extractions.
- **Complete source verification everywhere.** Seven pilot models now have reviewed
  taxonomy/member/profile records. Source-only evidence remains incomplete for some groups;
  inference and unresolved catch remain labelled, with geographic/period mismatches recorded.
- **NPP for EEZs.** The NPP dataset covers LME and High Seas only.
- **NPP over time.** A single 2019 value, so `ppr_over_npp_percent` uses a constant
  denominator across all years. Treat the trend in that column as driven by PPR alone.

## Scope, comparison and map rules

`all` includes all basal sources and imports; `inner` excludes imports; `PP` retains
primary producers only. Older scalar methods without a PP decomposition remain blank
in that scope. The simple trophic chain is an unpartitioned reference, not a PP-only
component. Raw PPR stays in wet-weight PP equivalents. PPR/NPP divides by **9** to compare
with carbon NPP, whose 2019 denominator stays fixed across catch years.

`atlas_selection.json` explicitly gates the ten selected-article pilot ecosystems and
selected source overlays. `tools/build_network_atlas.py` verifies model workbooks before
exporting their rounded catches/SPPR to the atlas. Method ratios use the same available
catch taxa for numerator and denominator, with coverage displayed and zero denominators
unavailable. Finite recycling diagnostics are visible even when their status is FAIL.

Thailand's filename `35_412_Gulf_of_Thailande_(1963)` is retained for stable joins, but
its payload matches the published **1980** model. Guinea covers 111,932 km² off the country
Guinea, not the whole Guinea Current LME. Okhotsk `NE` means new detailed Ecopath model,
not northeastern. Read each model's source-check/profile before treating a regional
catch application as the original study's spatial or historical footprint.
