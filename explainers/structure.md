# Where to find things

The project has three main places to open: `Project.xlsx` for the project-wide overview, a regional workbook for a particular ecosystem, and `interactive_map` for the generated map and plots. Papers, model inputs and review evidence are stored with the region they describe.

```text
GlobalPPREstimation/
├── Project.xlsx                 Papers, model metadata and researcher reviews
├── regions/                     Workbooks and scientific material by region
│   ├── LME/                     Large Marine Ecosystems
│   ├── EEZ/                     Exclusive Economic Zones
│   └── HS/                      High Seas units
├── interactive_map/             Map, trends and source pages
├── explainers/                  Guides for human readers
│   └── agents/                  Operating instructions for agents
├── tools/                       Commands, scientific code, skills and templates
├── common_reference_data/       Shared geography, taxonomy, EcoBase and NPP inputs
└── research/                    Studies and supporting evidence; see research/README.md
    ├── human/                   Researcher-owned experiments and method comparisons
    └── agents/                  Supporting audits, baselines, reviews and integration
```

## Inside a region

For example, the regional workbook for the Guinea Current is `regions/LME/LME_028/LME_028.xlsx`. Its folder also contains the papers, candidate models and work relevant to that region.

```text
regions/LME/LME_028/
├── LME_028.xlsx                  Current regional inputs and calculated results
├── selected_model.lnk            Shortcut to the currently selected model
├── raw/                         Regional catch, NPP and geography sources
├── papers/
│   └── <paper_id>/
│       ├── sources/              Publication and supporting source documents
│       ├── source_manifest.json  Source identities and roles
│       └── models/
│           └── <model_id>/        One model period or scientific scenario
├── ecobase/
│   └── <model_id>/               JSON-only EcoBase candidate
└── work/<run_id>/                Preparation, comparisons and verification
```

The same layout applies to EEZ and High Seas regions. Some folders are optional. One paper can contain several models, such as different periods or scenarios. A JSON-only EcoBase candidate has the same model layout as a paper model, even when its original publication is unavailable.

## Inside a model

```text
<model_id>/
├── model.json                    The model's canonical scientific input
├── model_notes.md                Source, period, area and documented departures
├── sppr_source.xlsx              Coefficient source, when available
├── inputs/                      Native inputs and their provenance
├── extracted_tables/            Latest extracted tables and supporting evidence
├── results/
│   ├── regional_snapshot.xlsx    Complete saved regional workbook
│   ├── result_manifest.json      Result identities, settings and dependencies
│   └── diagnostics/              Saved diagnostic returns and matrices
└── model_validation/
    ├── validation.docx           Human-readable review report
    ├── taxon_mapping.xlsx        Detailed mapping appendix
    ├── evidence/                 Source, geography and mapping evidence
    └── work/<run_id>/             Report preparation and verification
```

Each distinct model has one `model.json` and its latest extraction. Different periods, areas or scientific variants remain separate models. `model_notes.md` explains any supported differences from the publication; missing departure evidence does not establish exact source fidelity. Older superseded packages are recoverable through Git history.

A saved snapshot includes all workbook sheets, formatting and links. It is useful for inspecting earlier model results, but it may show the incoming selection in Overview while its calculations belong to the outgoing model. The adjacent manifest records both identities. [Model selection](model_selection.md) explains what can be restored and why some results remain pending.

## What to open for a particular question

| What you need | Where to look |
|---|---|
| Paper citation, model coverage or researcher decision | `Project.xlsx` |
| Current catch, model choice, mapping, annual PPR or NPP | The regional workbook |
| Published source or extracted parameter | The paper's `sources/`, then the model's `extracted_tables/` |
| Explanation of a transformed model | The model's `model_notes.md` |
| Numerical diagnostics or a saved full workbook | The model's `results/` |
| Review conclusions and taxon-level confidence | The model's `model_validation/` |
| Map, annual trends and source links | `interactive_map/` |
| Scientific methods and implementation | The guides here and `tools/scientific_code/` |

`Project.xlsx` and regional workbooks contain editable inputs alongside generated summaries. The [workbook reference](../README.md#workbook-reference) explains which fields to edit. The map and shortcut reflect saved state; they do not select or approve a model themselves. Double-click `interactive_map/Open map.cmd` to open the locally served map. Shortcuts are generated locally and may need regeneration after cloning or moving the project.

Preparation runs use `inputs`, `outputs`, `code` and `qa` subfolders. Source data, current results and review evidence stay with their paper/model; temporary work is not another model archive. Agent placement and preservation rules are in [agents/project_contract.md](agents/project_contract.md).

Research is organized by purpose and ownership, not by who typed the files. [The research index](../research/README.md) lists every retained study. Human research may use agent assistance; placement does not imply scientific approval. Move studies as complete packages and retain historical execution records.
