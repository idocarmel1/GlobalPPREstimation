---
name: ecopath-extraction
description: "Use when extracting or reviewing Ecopath/EwE model parameters from papers, supplements, tables or figures, including diet matrices, B/PB/QB/EE, catch, biomass accumulation, EwE import files and database JSON. For taxonomy, SPPR or the full integration chain, use ecopath-paper-to-ppr."
---

# Ecopath extraction

Produce traceable EwE import files and database JSON for each distinct published
model. Read [the extraction workflow](references/workflow.md) before extracting;
it carries the full scientific and reporting contract shared with the Claude skill.

## Execution

Resolve the directory containing this `SKILL.md` as the skill root. Use quoted
absolute paths for scripts, sources and outputs. In every reference, `scripts/`,
`references/` and `assets/` are relative to that root. Write work files in the
selected workspace, preserving sources and installed skill resources.

Run `scripts/check_environment.py` before the first extraction. Use the available
Python interpreter; the bundled PDF helpers prefer PyMuPDF with Poppler fallback.
Inspect rendered pages using the available image/PDF tools.

## Work sequence

1. Inventory the source bundle and confirm it contains a model parameter set.
   Read [source-bundle.md](references/source-bundle.md).
2. Fix group numbering and exact names. Read [pdf-extraction.md](references/pdf-extraction.md)
   and [table-layouts.md](references/table-layouts.md) before parsing unfamiliar tables.
3. Sweep prose, footnotes and figures, including biomass accumulation. Consult
   [prose-extraction.md](references/prose-extraction.md) and
   [parameter-conventions.md](references/parameter-conventions.md).
4. Follow [output-formats.md](references/output-formats.md): write the extraction
   JSON, run `write_outputs.py`, and use the model directory it prints.
5. Run `validate.py`, `massbalance_check.py`, then `database_json.py -d <model-dir>
   --update-report`. Investigate flags against the source; complete `REPORT.md`
   and the extraction-set index. Package outputs only after the last correction.

## Decisions that matter

Keep unknown values blank in import files and `-9999` in database fields; a printed
zero is different. Unknown biomass accumulation is not evidence of steady state.
Never use a balance check's suggested value as source data or normalize a printed
diet matrix to make validation pass. Preserve source precision and distinguish
paper statements, inherited information and explicit project conventions.

Use [ecopath-model.md](references/ecopath-model.md) for equations and balance
verdicts. Report findings and limitations, with file/page/table provenance.
For mortality-rate/flow comparisons, fleet returns, offal or routing experiments,
read [mortality-and-discards.md](references/mortality-and-discards.md). Keep source
evidence separate from importer omissions and experimental assumptions.
An extraction-only request stops here; taxonomy and downstream PPR are separate
stages of the combined skill.
In GlobalPPREstimation, the source-bundle reference also covers the root article
reference/use log and exact-byte evidence. Independent simple PPR or NPP coverage
does not itself require extracting an Ecopath model.
