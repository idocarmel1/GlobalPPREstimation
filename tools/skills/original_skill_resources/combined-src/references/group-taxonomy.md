# Stage 2 — capture what is in each group

Apply the [evidence, execution and adoption contract](evidence-handoff.md) to this stage: explain fresh runs and honor existing scoped authorization, retain the applicable portable evidence, and verify completeness before handoff.

The standalone extraction workflow leaves taxonomy to this stage. A full PPR
pipeline also needs the model's group membership, so capture it while the paper
is open. An explicitly extraction-only request still stops at stage 1.

Record membership during the same source reading as the parameters. The resulting
evidence should remain usable by a later mapper without reconstructing its origin.

This stage records what the source actually says. Later catch mapping also permits
explicit broad-category and closest-analogue assignments under the unified
[broader mapping definitions](regional-calculation.md#broader-mapping-definitions-and-confidence).
Keep those assumptions in the mapping review with Very low confidence; do not add
them to source `taxon_descr` as though the paper documented their membership.
Missing exact source membership is not, by itself, a reason to leave catch unresolved.

## The file

`Taxonomy.xlsx`, one sheet, three columns, one row per group in `seq` order:

| column | contents |
| --- | --- |
| `seq` | the group number, same as everywhere else |
| `group_name` | verbatim, same string as `Basic_input.csv` |
| `taxon_descr` | who is in the group |

`database_json.py` picks it up by filename, indexes on the second column and takes the
**last** column as the description, so the column order matters and a fourth column would
be read instead. Three columns, in that order.

`<skill-root>/scripts/write_taxonomy.py` writes it from a CSV or a dict so the shape cannot drift:

```bash
python "<skill-root>/scripts/write_taxonomy.py" "<model_dir>/taxonomy.csv" "<model_dir>/Taxonomy.xlsx"
```

Then rebuild the database JSON. `taxon_descr` appears in it, and from there in the
`groups_df` sheet the mapper reads.

## Existing database JSON with no extraction folder

Ecobase models may have only a finished JSON. Do not invent an eight-file extraction to fit the workbook route. Read the JSON's `group` array and retain `taxonomy.csv` under the region's `models/<model_id>/` folder, with `seq,group_name,taxon_descr` for every group. Verify the actual JSON schema, identifiers and order; match names exactly and preserve group numbers. Keep table-purpose, membership and source evidence beside the taxonomy.

Apply supported `taxon_descr` values by verified group identity in the intended model variant; preserve all numerical fields and retain original bytes/hash. Independently compare group coverage, sequence and every changed field after saving. Follow [the reconstruction audit](reconstruction-audit.md), then [direct diagnostics](direct-diagnostics.md) only when that stage is requested or affected published coefficients need refreshing. Do not silently modify a published canonical source or relabel earlier SPPR outputs.

Candidate taxonomy stays with its model. Populate regional Selected model groups only for the selected model. For a JSON-only taxonomy request, no SPPR or annual calculation is implied. There is no current `tools/apply_taxonomy.py` or `tools/run_sppr.py`; their archived commands are superseded by this route and the current regional tools.

## What to write in `taxon_descr`

Whatever the paper actually supports, in this order of preference.

First identify what a table establishes: exhaustive composition, selected example
members, catch allocation, or species used in diet studies. Preserve that scope
in the description and provenance. A diet-study list is not automatically an
exhaustive membership inventory. Absence from it neither excludes a catch taxon
nor requires a weighted assignment. Weights are needed when several supported
groups or spatial pools remain, even for an explicitly named member.

For Guénette's Bay of Bengal report, A3.1 (pp.50–53) lists diet-study sources;
A1.1 (pp.37–41) allocates catch names and A1.3 (pp.43–45) describes composition.
Dedicated yellowfin/bigeye groups are supported elsewhere even where A3.1 says
“Tuna-like.” The retained Bay of Bengal source audit records this comparison; locate its current path using the project provenance relocation ledger. It does not validate regional weights. Confirm synonyms
against an authority and retain author-distinguished taxa when authorities differ.

Keep an unreconciled diet-study list in its own source-audit table. The mapping
validator treats `members.csv` group placements as authoritative and has no
table-scope or precedence field. Reconcile the exact model's composition before
putting a diet example into that file. Its overlap check cannot validate every
candidate in a composite or the weights between geographic pools.

**A species list, if the paper gives one.** Copy it. Semicolon-separated, scientific names,
the paper's spelling. This is the whole point and everything else is a substitute.

> `Sardinella aurita; Sardinella maderensis; Engraulis encrasicolus; Ethmalosa fimbriata`

**A taxonomic definition**, where the group is a taxon.

> `Cephalopoda — squid, cuttlefish and octopus`

**The definition the paper gives**, where the group is a guild, a size class or a pool.
Quote the operative words; do not paraphrase into something more precise than the source.

> `Demersal fish 30-89 cm feeding mainly on benthic invertebrates (paper Table 2 "medium
> benthic carnivores"); dominant taxa named in the text are Nemipteridae, Mullidae and
> Lethrinidae`

**"not documented"**, where the paper never says. Write those two words rather than leaving
the cell empty. An empty cell is ambiguous between "nobody looked" and "we looked and it is
not there"; the second saves the mapper an hour.

> `not documented — Table 1 names the group only; no species list in the paper or its
> supplement (checked Appendix A and the online supporting information)`

## Where the member list hides

In rough order of yield:

- a species-composition or group-definition table, often in an appendix
- the **supplement**, especially for guild-structured models. The East China Sea membership
  table is a `.docx` data sheet, not a table in the PDF. A `.docx` is a zip of XML, so
  `zipfile` plus `word/document.xml` reads it when `python-docx` is unavailable
- the diet composition matrix — inspect prey identities and trophic context, but do not treat what a group eats as evidence of which taxa belong to that predator group
- the methods section, where groups are usually justified as they are introduced
- figure captions and table footnotes
- the **predecessor model**. "Based on", "adapted from", "following" — then read that paper.
  Mark it `inherited_model`, not as the focal paper's own statement

Use [online recovery](missing-data-recovery.md), including publisher attachments, official repositories and verified predecessor lineage. Make real download attempts for supplements you can identify but do not have. Record the
filename, the URL and the result. Never write a member list you did not read.

## Also record the model's shape

Alongside `Taxonomy.xlsx`, write `MODEL_PROFILE.md` — a few lines that stage 4 needs and
that no other file carries:

```markdown
# <model name> (<year>)

Axis        : feeding guild   (taxonomic | size and habitat | feeding guild |
                               spatial stratum | life stage)
Prefixes    : none            (or: leading 1/2/3 are the three depth strata of Table 1)
Area        : <source-defined area, reported km², and relation to the catch unit>
Can take catch : all Regular groups except Zooplankton and Meiobenthos
Single stocks  : Hairtails, Bombay duck, Large and Small yellow croakers
Pools          : Piscivores, Benthivores, Omnivores
Membership     : Supplementary Table 1 lists species for 18 of 23 groups
```

Two of those lines exist because leaving them out has already cost real errors:

- **Area.** A model of part of a unit against a catch series for the whole unit produces a
  coverage number that looks like a mapping failure and is not. Read the geographic
  definition in the source: Okhotsk "NE" names the new detailed Ecopath model of the
  whole Sea, not its northeast. Never infer a regional fraction from a filename.
- **Prefixes.** A stratified model whose numeric prefixes nobody wrote down had every taxon
  put into stratum 2 by default, silently attributing an entire LME's catch to one
  sub-area.

## When you are done

The taxonomy artifact has a row for every group, including `not documented`
where appropriate: `Taxonomy.xlsx` for an extraction folder, or
`<model-stem>.taxonomy.csv` for a JSON-only model. The database JSON has been rebuilt
or patched through the applicable route. After the requested SPPR run, inspect
`groups_df` for the recorded `taxon_descr` values. For an adopted model, carry the verified membership into regional Selected model groups and use it in PPR / Matching. Follow [regional calculation](regional-calculation.md) for authorized dependent refreshes; no legacy work-order file is required.
