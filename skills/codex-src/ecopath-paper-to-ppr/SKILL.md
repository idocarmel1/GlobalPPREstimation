---
name: ecopath-paper-to-ppr
description: "Use when extracting or integrating Ecopath/EwE models, group taxonomy, SPPR and catch-based PPR, or maintaining independent simple PPR, annual regional/global NPP and atlas integration in GlobalPPREstimation. Applies to published papers, extracted model files and existing Ecobase JSONs."
---

# From an Ecopath paper to PPR

Start at the requested stage and stop at the requested deliverable. Read
[the pipeline workflow](references/workflow.md) for stage transitions and repository
commands. This distribution includes the same extraction, taxonomy and mapping
resources as the Claude version.

Resolve this skill's directory as `<skill-root>` and the checkout as `<repo-root>`.
Bundled scripts/references/assets/examples always resolve from the skill root,
even inside a reference document. Use quoted absolute paths and the active shell.
Keep outputs in the selected workspace. For repository tools, use the checkout
as working directory; set `GLOBALPPR_ROOT` for bundled mapping scripts.

| Starting point / requested work | Read and execute |
| --- | --- |
| Paper → import files and database JSON | [extraction.md](references/extraction.md), plus [source-bundle.md](references/source-bundle.md); run the environment probe first |
| Group membership for an extracted model or Ecobase JSON | [group-taxonomy.md](references/group-taxonomy.md); choose the extraction-folder or JSON-only route |
| Database JSON → SPPR | Stage 3 in [workflow.md](references/workflow.md); use `tools/run_sppr.py` with explicit model stems and output directory |
| SPPR workbook + catch → PPR | [mapping.md](references/mapping.md), [model-structures.md](references/model-structures.md), [coarse-taxa-playbook.md](references/coarse-taxa-playbook.md) and [mapping-output-format.md](references/mapping-output-format.md) |
| Central workbooks, independent simple PPR, regional/global NPP or map/graph integration | [integration-contract.md](references/integration-contract.md); these paths do not require a model |
| Mortality comparison, discard fate or routing experiment | [mortality-and-discards.md](references/mortality-and-discards.md), plus the integration contract for regional responses |

For an extraction-only request, finish after stage 1. When taxonomy is requested,
capture group membership while reading the paper. For a JSON-only model, prepare
`<stem>.taxonomy.csv` and use repository `tools/apply_taxonomy.py`; the workbook
writer expects extraction files and cannot replace that route.

Distinguish composition/catch-allocation tables from diet-study examples. Exact
membership does not settle geographic weights. Integration preserves **Final
mappings**, year-specific carbon NPP, the single `/9` PPR conversion and separate
landings/all-catch/discards vectors. Routing ranges are optional landings scenarios;
unsupported responses remain unassessed. New model extraction and expanded
conversion-factor literature review remain separate requests; article availability
does not gate independent simple PPR or NPP. The integration contract covers
NPP-only/no-catch views, fixed-union ensembles, cache lineage and source-use records.

Use `tools/run_sppr.py --models "<stem>" --json-dir "<json-dir>" --out "<staged-dir>"
--compare` for a staged SPPR run. Never execute `PPREstimation/create_PPRS_excel.py`
from a shell, even for help: its current main block overwrites the pilot outputs.
Use the wrapper's `--in-place` only when replacing repository outputs is within
the requested scope. Refresh the mapping work order after that replacement.

Read `model_health` before relying on a model. Keep exact group names, paper member
lists, model area and grouping axes. Source membership outranks habitat inference.
Distinguish unknown values from zero, and report unsupported assignments honestly.
Validate each applicable stage; the final PPR workbook must pass
`tools/verify_model_workbook.py`. Keep models and methods separate, and preserve
the existing Jensen calculations and comparison rows.
