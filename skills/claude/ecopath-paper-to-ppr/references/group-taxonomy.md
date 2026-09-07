# Stage 2 — capture what is in each group

The standalone extraction workflow leaves taxonomy to this stage. A full PPR
pipeline also needs the model's group membership, so capture it while the paper
is open. An explicitly extraction-only request still stops at stage 1.

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

## Existing database JSON with no extraction folder

Ecobase models may have only a finished JSON. Do not invent an eight-file extraction
to fit the workbook route. Read the JSON's `group` array and create
`data/<unit>/mapping/<model-stem>.taxonomy.csv` with `seq,group_name,taxon_descr`,
one row for every group. Match names exactly, preserve group numbers, and record
the model profile and any paper member table beside the taxonomy CSV.

```text
python "<repo-root>/tools/apply_taxonomy.py" "<taxonomy.csv>" --model "<model-stem>" --json-dir "<json-dir>" --check
python "<repo-root>/tools/apply_taxonomy.py" "<taxonomy.csv>" --model "<model-stem>" --json-dir "<json-dir>" --out "<patched-json-dir>"
python "<repo-root>/tools/run_sppr.py" --models "<model-stem>" --json-dir "<patched-json-dir>" --out "<staged-sppr-dir>" --compare
```

The application tool checks group-name coverage; independently check each `seq`
against the source JSON. Inspect `groups_df` and `model_health` in the result.
Replacing the repository JSON/workbook is a separate choice within the requested
scope; then regenerate the mapping work order from the refreshed workbook.

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
`groups_df` for the recorded `taxon_descr` values. When the refreshed workbook is
placed in the repository, regenerate the stage 4 work order so it shows that
membership instead of an empty-field warning.
