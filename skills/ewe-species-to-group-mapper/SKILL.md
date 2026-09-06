---
name: ewe-species-to-group-mapper
description: "Map every taxon in an LME catch workbook to the closest functional group in every Ecopath with Ecosim model described by supplied papers and supplements. Produce model-specific mapping and explanation columns, confidence colors, a taxonomy/provenance sheet, and validated spreadsheet output. Use when the user selects EwE Species-to-Group Mapper or asks to match LME species/catch taxa to EwE functional groups."
---

# EwE Species-to-Group Mapper

Match an LME catch-taxon workbook to every distinct Ecopath model in the supplied source bundle. Use `assets/reference.xlsx` as a structural and visual example, not as a biological lookup table. Never copy East China Sea assignments into another ecosystem without evidence.

## Required inputs

This skill runs against the `GlobalPPREstimation` repository layout. For an ecosystem
identified by its `unit_id` (`LME_036`, `EEZ_711`, `HS_077`):

| what | where | notes |
| --- | --- | --- |
| the taxa to map | `data/<unit_id>/<unit_id>.xlsx`, sheet **`Catch`** | column `taxon`, plus `functional_group` and `commercial_group` from Sea Around Us |
| the model's exact group list | `PPREstimation/output/top10/<model>.xlsx`, sheet **`groups_df`** | **authoritative — use it, do not mine group names from the paper** |
| membership evidence | `PPRAtlas/archive/regions/<unit_id>/<ARTICLE>/` | the papers and supplements; this is where you learn *which taxa* belong to each group |
| which model to use | `data/model_selection.xlsx` | check the `usable` column first |
| coverage at a glance | `data/INDEX.csv` | |

Two things about this layout that change how you work:

**Group names and trophic levels are already extracted and exact.** `groups_df` gives
`seq`, `group_name`, `group_type`, `tl`, `ge`, `ee` per group. Read them from there.
Deriving group names from prose risks misspelling them, missing one, or inventing a group
the model does not have — and the downstream join is on the exact name.

**`taxon_descr` in `groups_df` is empty for every current model.** The extraction step did
not capture group membership, so the papers remain the only source for which taxa sit in
which group. That is the substantive work of this skill.

**Check `usable` before you start.** Several extracted models are unfit — a model can be
present on disk and still explode, be unbalanced, or have diet rows far from 1. Mapping onto
an unusable model produces confident nonsense. If the selected model is not `usable`, say so
and stop rather than mapping.

If a needed paper or supplement is missing, attempt to retrieve it online before mapping.

## Worked examples

`examples/` holds three completed mappings — `LME_032_Arabian_Sea.xlsx`,
`LME_034_Bay_of_Bengal.xlsx` and `LME_047_East_China_Sea.xlsx`. Read one before
starting to see the expected column layout, confidence colouring and provenance
sheet. They are reference output, not biological lookup tables: never copy an
assignment from one ecosystem into another without evidence from that ecosystem's
own sources.

## Capabilities to use

1. Use the available spreadsheet capability to inspect, edit, render, and validate the workbook while preserving its native structure.
2. Use the available PDF/document capabilities to inspect papers, tables, captions, footnotes, figures, and supplements.
3. Use the available `ecopath-extraction` capability, when present, to establish model boundaries, exact group lists/order, and model-specific TL values. This workflow does not require a full EwE parameter extraction unless the user requests it.
4. Browse primary publisher pages, DOI records, repositories, and cited scientific papers when supplements or group definitions are absent from the supplied files.

Do not begin biological assignments until the source bundle and distinct model list are fixed.

## 1. Inventory sources and enumerate models

Inventory every supplied paper, supplement, spreadsheet, appendix, and prior calculation file. For each paper, identify every distinct static Ecopath model. Treat models as distinct when they differ by period, scenario baseline, area, season, depth stratum, life-stage aggregation, or functional-group structure.

Create one mapping decision column for every model even when two models use identical functional groups. Never collapse models merely because their mappings happen to be the same.

Record for each model:

- Paper citation and DOI/URL
- Model label and modeled years
- Modeled area and relation to the LME
- Exact functional-group names and order
- Model-specific TL values when reported
- Whether group membership differs from other models in the paper
- Where membership/grouping criteria are documented

## 2. Recover supplementary and inherited taxonomy evidence

Search the paper, publisher page, XML/JATS metadata, DOI landing page, repositories, and cited sources for:

- Species-to-functional-group tables
- Diet matrices or stomach-content tables
- Group-definition tables
- Life-stage or size splits
- Taxonomic synonyms used by older papers
- Statements such as “based on,” “adapted from,” or “following” a prior model

Make real download attempts for identified supplementary files. Record the filename, URL, result, and limitation. Do not claim a supplement was read when only its filename or citation was found.

If the focal paper relies on an earlier paper, inspect the earlier paper. Distinguish:

- `direct source`: the focal paper explicitly adopts or adapts it
- `supporting regional source`: biologically relevant but not stated as inherited
- `analyst inference`: derived from taxonomy/ecology rather than a reported membership

## 3. Build a model-specific group dictionary

For every group in every model, record:

- `paper`
- `model`
- `functional_group`
- `model_tl`
- `grouping_basis`: taxonomic, feeding guild, habitat, size, life stage, commercial single-species group, residual pool, or non-living compartment
- `explicit_members`
- `supporting_taxa_or_examples`
- `membership_source`
- `source_relationship`
- `source_location`: file + page/table/figure/sheet
- `source_url`
- `notes_and_limitations`

Keep exact model spelling in output columns. Normalize spelling only in an internal comparison key.

## 4. Normalize workbook taxa

For each workbook row determine, as far as the sources support:

- Submitted scientific name
- Accepted scientific name
- Synonyms or historical combinations
- Taxonomic rank: species, genus, family, order, broad category, or “nei/not identified”
- Higher taxonomy relevant to model groups
- Common name
- Existing habitat/functional category
- Trophic level and its source
- Size, habitat, and feeding information when needed

Do not overwrite the workbook's existing taxonomy or functional-group columns. Treat them as evidence inputs.

## 5. Match each taxon independently to each model

Apply this evidence hierarchy in order:

1. Exact species explicitly listed in that model
2. Accepted-name or synonym match to an explicit member
3. Explicit genus/family/higher-rank containment supported by the model definition
4. Unambiguous broad taxonomic group, such as a cephalopod entering a dedicated Cephalopods group
5. Explicitly inherited classification from a cited predecessor model
6. Strong ecological analogue using diet, habitat, size/life stage, mobility, and TL together
7. Best-supported residual group, only if the model defines one that truly includes the taxon
8. `Unresolved` when no defensible group can be selected

Never assign a feeding guild from TL alone. TL is corroborating evidence, not a taxonomy substitute. Do not force unidentified fish into a precise feeding guild. Do not put every member of a family into a dedicated commercial species group unless the model defines that scope.

When models share an identical group dictionary, assignments may be identical, but retain separate decision and explanation columns.

## 6. Confidence rules and cell colors

Use exactly these outcomes:

- Green `#C6EFCE`: very sure. Direct membership/synonym evidence, explicitly inherited classification, or an unambiguous taxonomic group.
- Yellow `#FFEB9C`: almost sure. Best-supported ecological inference with enough evidence to choose one group.
- Red `#FFC7CE`: write exactly `Unresolved`. Evidence is insufficient or materially conflicting.

Color only the decision cells. Explanation cells remain neutral and readable. Do not hide uncertainty inside an explanation while coloring the decision green.

## 7. Write model-specific decision and explanation pairs

Append paired columns to the `Species` sheet:

```text
EwE_<Author>_<Year>_<ModelLabel>
EwE_<Author>_<Year>_<ModelLabel>_explanation
```

For each row, the explanation must state the decisive evidence, for example:

- exact membership and source
- accepted synonym and explicit listed name
- unambiguous taxonomic containment
- habitat + diet + TL ecological inference
- why the catch category remains unresolved

Avoid generic text such as “best match.” Name the traits, source relationship, or ambiguity that determined the decision.

## 7b. Where the output goes

Write the mapping back into `data/<unit_id>/<unit_id>.xlsx` as a new sheet named
**`Taxon-Group Map`**, leaving every existing sheet untouched. Required columns:

    taxon | functional_group | commercial_group | <model>_group | <model>_confidence | <model>_explanation

one `<model>_*` triple per distinct model, named with the model's exact stem from
`PPREstimation/output/top10/`. `<model>_group` must be a verbatim `group_name` from that
model's `groups_df` — anything else breaks the join that turns SPPR into PPR.

Use `Unresolved` where no defensible assignment exists. An honest `Unresolved` is worth more
than a plausible guess: the next step multiplies these by catch, so a wrong group silently
produces a wrong PPR for that taxon in every year.

## 8. Add an `EwE Taxonomy` evidence sheet

Create one row per model × functional group using the group-dictionary fields from Step 3. Repeat shared groups for each model so model-specific TL and provenance remain explicit.

Use plain-text URLs in source columns. Clearly flag unavailable supplements and incomplete species lists. Never present a supporting regional paper as a direct inherited taxonomy unless the focal paper says so.

## 9. Preserve and validate the workbook

- Preserve every existing sheet, formula, value, style, filter, table, freeze pane, and validation rule unless a requested addition requires a targeted change.
- Match the reference workbook's dark-blue headers, readable widths, wrapped explanations, and confidence colors.
- Keep formulas formula-driven; do not replace them with cached values.
- Ensure the pre- and post-mapping catch total is identical.
- Ensure every decision is an exact group name from that model or `Unresolved`.
- Ensure every species row has both a decision and explanation for every model.
- Count green, yellow, and red rows per model.
- Scan for formula errors.
- Render and visually inspect every sheet, including `Species` and `EwE Taxonomy`, before export.

## 10. Final response

Return the completed `.xlsx` and briefly report:

- Models mapped
- Number of taxa
- Confidence counts per model
- Unresolved categories
- Important supplement/provenance limitations
- Confirmation that formulas and catch totals were preserved

Do not claim that an inferred mapping came from the paper. The workbook must remain auditable enough that another researcher can revisit every yellow or red decision.
