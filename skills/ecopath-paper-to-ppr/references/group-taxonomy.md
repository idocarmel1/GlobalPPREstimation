# Stage 2 — capture what is in each group

The extraction workflow deliberately left this out: *"`Taxonomy.xlsx` is not part of the
deliverable — it is deliberately out of scope for this project."* That was a reasonable call
for extraction on its own. It is the wrong call for a pipeline that ends in PPR, because the
mapping stage cannot work without it and pays for its absence every time.

What that omission costs, measured on the first three finished mappings: `taxon_descr` null
for every group in every extracted model, so all three mappings rested on taxonomic
containment and habitat inference rather than a documented member list, and all three
stalled near 78 % of catch tonnage. Each spent an hour re-reading a PDF the extractor had
already read.

You are already reading the basic-input table and the diet matrix. Write down what the
groups contain while you are there.

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

`scripts/write_taxonomy.py` writes it from a CSV or a dict so the shape cannot drift:

```bash
python scripts/write_taxonomy.py <model_dir>/taxonomy.csv <model_dir>/Taxonomy.xlsx
```

Then rebuild the database JSON. `taxon_descr` appears in it, and from there in the
`groups_df` sheet the mapper reads.

## What to write in `taxon_descr`

Whatever the paper actually supports, in this order of preference.

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
- the diet composition matrix — prey row labels name taxa, and a group's diet constrains
  which families can be in it
- the methods section, where groups are usually justified as they are introduced
- figure captions and table footnotes
- the **predecessor model**. "Based on", "adapted from", "following" — then read that paper.
  Mark it `inherited_model`, not as the focal paper's own statement

Make real download attempts for supplements you can identify but do not have. Record the
filename, the URL and the result. Never write a member list you did not read.

## Also record the model's shape

Alongside `Taxonomy.xlsx`, write `MODEL_PROFILE.md` — a few lines that stage 4 needs and
that no other file carries:

```markdown
# <model name> (<year>)

Axis        : feeding guild   (taxonomic | size and habitat | feeding guild |
                               spatial stratum | life stage)
Prefixes    : none            (or: leading 1/2/3 are the three depth strata of Table 1)
Area        : the northeastern Okhotsk only, about 40 % of the LME
Can take catch : all Regular groups except Zooplankton and Meiobenthos
Single stocks  : Hairtails, Bombay duck, Large and Small yellow croakers
Pools          : Piscivores, Benthivores, Omnivores
Membership     : Supplementary Table 1 lists species for 18 of 23 groups
```

Two of those lines exist because leaving them out has already cost real errors:

- **Area.** A model of part of a unit against a catch series for the whole unit produces a
  coverage number that looks like a mapping failure and is not.
- **Prefixes.** A stratified model whose numeric prefixes nobody wrote down had every taxon
  put into stratum 2 by default, silently attributing an entire LME's catch to one
  sub-area.

## When you are done

`Taxonomy.xlsx` has a row for every group — including the ones where the answer is "not
documented" — the database JSON has been rebuilt, and `groups_df` in the SPPR workbook shows
`taxon_descr` populated. The stage 4 work order will then print the membership per group
instead of the warning that it is empty.
