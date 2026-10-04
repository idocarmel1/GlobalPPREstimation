"""Separate reader guides from current agent rules without changing science."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
RUN = Path(__file__).resolve().parent.parent
QA = RUN / 'qa'

def write(name, text):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + '\n', encoding='utf8')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    QA.mkdir(parents=True, exist_ok=True)
    assert (ROOT / 'explainers/structure.md').read_text('utf8').startswith('# Authoritative project structure'), 'One-time migration requires the768dffbe documentation baseline; do not rerun against rewritten guides.'
    baseline = {p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / 'explainers').rglob('*.md')}
    write('explainers/README.md', '''
# Guides to the project

These guides explain the project to researchers and other readers. Start with the question you want to answer.

| Question | Guide |
|---|---|
| Where are the workbooks, papers, models and results? | [Project layout](structure.md) |
| How do I work on a region or update the map? | [Regional workflow](workflow.md) |
| How do I choose a model, and what happens to its results? | [Model selection](model_selection.md) |
| How does a validation report relate to researcher approval? | [Validation and review](validation.md) |
| How do extracted model values become calculation inputs? | [Model loading](model_loading.md) |
| What do the SPPR methods calculate? | [SPPR methods](sppr_methods.md) |
| What do the default settings mean? | [SPPR parameters](sppr_parameters.md) |
| How do I use the scientific engine's classes and methods? | [PPREstimation user guide](PPREstimation/USER_GUIDE.md) |
| Which results or operations still have limitations? | [Current limitations](limitations.md) |

The [root project guide](../README.md) gives the quick start and workbook-table reference. Model-specific departures and evidence are next to each model in `model_notes.md` and `model_validation/`.

Agent operating instructions are in [agents/project_contract.md](agents/project_contract.md). They are separate from these reader guides. Current guides describe the working project; superseded implementation plans can be recovered through Git history.
''')
    old_structure = (ROOT / 'explainers/structure.md').read_text('utf8')
    body = old_structure[old_structure.index('## Regions, papers and models'):]
    agent_contract = '''
# Project operating contract for agents

Read the root [project guide](../../README.md) and this contract before modifying project content. Both active skills follow root [AGENTS.md project_contract](../../AGENTS.md#project_contract). Reuse an unchanged contract already read in this execution context; read it in a new context or after it changes. Choose the requested operation through the [shared operation contract](../../tools/skills/paper-to-ppr/references/operation-contract.md) and read its additional scientific references only as needed.

This document contains the current directory, ownership, preservation and execution rules. It supersedes the operating rules formerly embedded in the reorganization and skill-efficiency plans. Human explanations live in the parent directory; completed plans are recovered from Git rather than retained as current authority.

Current user instructions take precedence. Preserve scientific inputs, researcher edits, missingness, diagnostic restrictions and source identity. Selection, schema loading, construction, numerical readiness and researcher approval are separate. Administrative work must not repair parameters, normalize diets, invent provenance or adopt a scientific result.

''' + body + '''

## Snapshot identity and publication details

Save outgoing full-workbook bytes atomically before replacing usable results, and save the successful current workbook under the selected model afterward. A snapshot may contain the incoming Overview selection and the outgoing results; retain both identities honestly. Never overwrite a useful snapshot with an empty pending state.

Result manifests distinguish schema version, region and actual model identity, snapshot selection, timezone-aware timestamp, snapshot/model/coefficient-source hashes, effective loader/calculator flags, executed code identity, separate catch/matching/NPP/settings dependency hashes and relative artifact paths. Unknown historical flags or code remain unknown. Source JSON, workbook-byte and dependency hashes have distinct meanings. A changed independent input need not force an unrelated SPPR run.

Restoration uses an explicit allowlist of compatible model-dependent tables. Matching may be reused only while taxon/group identities and assumptions still apply. Current inputs, human Diagnostics entries, review freshness and failure/provisional states remain protected. On technical publication failure roll back coherently; on missing scientific prerequisites retain the requested selection and an exact pending reason. Serialize Project.xlsx writes.

## Scientific and human-review boundaries

The two active skills are the scientific procedures, not this directory contract. Direct diagnostics ordinarily retain GE, TE and With Egestion; full validation report rows retain GE/TE. Broad inventories, global methods and Monte Carlo require their own authorized scope. Reuse the audited input and actual configuration rather than substituting defaults. Record unsuccessful construction, exceptions, timeouts and unavailable matrices truthfully.

A composed pipeline resolves taxon-to-group mapping once, using the union of pipeline and validation requirements. Hand off the same keyed group/weight/confidence/evidence decision set; validation checks and reports it. Changed inputs or missing evidence return only affected gaps to that stage. Full validation still covers all catch taxa, including zero rows, and separate membership/allocation confidence.

Preserve current researcher-authored Word text, manual appendix cells, deletions, signatures, breaks and links. Render and inspect every output page after a Word edit. If an edit touches parser-consumed headings/labels, compare the existing signoff summary before/after; unexpected identity/date/sections/reference changes block adoption. Signed-source registration and bounded map refresh follow the existing handoff, preserve the exact human verdict, and do not authorize recalculation or reselection.

Read-only saved-table inspection and content-checked in-memory ReadSession reuse establish only their stated evidence scope. Recheck consumed input bytes before publication and retain the existing mutation guards. A session that observed any input change cannot publish a mixture of versions.

## Evidence and navigation

Use the one canonical [knowledge graph](../../tools/knowledge_graph/graph.json) and its [scope](../../tools/knowledge_graph/REFRESH_SCOPE.md). Query `graphify query "question" --graph tools/knowledge_graph/graph.json` before architecture exploration. Hash-eligible unchanged evidence may be reused; changed sources and relocated concepts require current verification. An outdated graph indexes its recorded snapshot and does not prove current scientific validity.

[Current limitations](../limitations.md) explain unresolved project restrictions to human readers. Model-local notes, diagnostics and review evidence establish actual scientific state. Work QA records what was checked; do not turn a partial trial, historical execution record or graph into approval.
'''
    write('explainers/agents/project_contract.md', agent_contract)
    write('explainers/structure.md', '''
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
└── research/                    Scientific studies with their methods and evidence
```

## Inside a region

For example, the regional workbook for the Sulu-Celebes Sea is `regions/LME/LME_028/LME_028.xlsx`. Its folder also contains the papers, candidate models and work relevant to that region.

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
''')
    write('explainers/workflow.md', '''
# Working with a region

Start with the regional workbook, for example `regions/LME/LME_028/LME_028.xlsx`. `Project.xlsx` brings together paper/model metadata, researcher reviews and saved regional summaries. The map and trends show those saved results. [Project layout](structure.md) explains where their source material lives.

## Choose an existing model

1. In the regional Overview, set `selected_model_id` and write `selection_rationale`.
2. Save the workbook.
3. From the project root, run:

```powershell
python tools/cli/region.py refresh --region regions/LME/LME_028
```

Refresh saves usable outgoing results, derives the new path and shortcut, restores compatible model material, recalculates ready arithmetic and updates the affected project/map/trend/source views. It keeps current Catch, Classic PPR, NPP and unrelated human settings. Repeating the command is safe.

Read the resulting saved status. A selected model can remain pending if coefficients, matching or recorded execution settings are missing. Outgoing values are then unavailable for that selection. Selecting a model does not approve it. See [model selection](model_selection.md) and [current limitations](limitations.md).

## Inspect a saved field

Open the relevant workbook table, or read one table without changing anything:

```powershell
python tools/cli/region.py inspect --region regions/LME/LME_038 --sheet Overview --table Settings
```

This returns the saved table and its input hash. It explains the saved state rather than assessing the whole model's readiness. Blank values mean missing; zero means an actual zero. Consult [SPPR methods](sppr_methods.md) and [parameters](sppr_parameters.md) for the meaning of calculated fields.

## Recalculate arithmetic after changing regional inputs

When compatible group coefficients and matching are available, recalculate dependent regional tables with:

```powershell
python tools/cli/region.py --region regions/LME/LME_028 --stage calculate
```

Changing catch, mapping, coefficients or NPP makes affected saved totals stale. Calculation uses the current inputs; it does not extract a model or run SPPR anew. Missing coefficients, unsupported years and failed/provisional restrictions remain visible. A changed model JSON needs a separate check of loading, diagnostics and coefficient identity before its numbers are used.

To publish fresh saved results for a region, update the project and then the map:

```powershell
python tools/cli/project.py --region regions/LME/LME_028/LME_028.xlsx
python -m tools.project_core.maps.build_html --workbook Project.xlsx
```

These commands consume saved regional state. A project update rejects stale results, preserves human metadata and review records, and changes generated summaries. Model selection uses its combined `refresh` command above. Signed-review registration uses its own bounded handoff rather than a general rebuild.

## Add a paper or prepare a review

A new paper/model needs its actual citation and model metadata registered once in `Project.xlsx`, plus the original sources and any applicable extraction work. Filesystem discovery finds model identities and paths; it cannot supply missing citation, area or scientific interpretation. [Model loading](model_loading.md) explains why an extracted JSON differs from the in-memory calculation model.

The [paper-to-PPR workflow](../tools/skills/paper-to-ppr/SKILL.md) describes the scientific stages. The [validation guide](validation.md) explains the report, mapping appendix and researcher decision. In a composed pipeline, mapping is resolved once and its same decisions feed arithmetic and validation. Evidence gaps remain explicit.

Fresh direct diagnostics normally cover GE, TE and With Egestion; validation report rows cover GE/TE. Broad method inventories and Monte Carlo are separate scientific work. The current model's source evidence and recorded settings determine the appropriate configuration.

## View the result

Double-click `interactive_map/Open map.cmd`, or run `python tools/cli/map.py`. The launcher serves the map on this computer. Inspect the model heading, diagnostic/review flags, source links and displayed year/basis together. A displayed provisional value is available for review and retains its diagnostic qualifications.
''')
    write('explainers/validation.md', '''
# Validation reports and researcher decisions

A validation report brings together the evidence needed for a researcher to assess one model in one region. It is stored with that exact model as `model_validation/validation.docx`; the accompanying `taxon_mapping.xlsx` gives the detailed catch-taxon mapping and confidence evidence. The extraction row links to `model_notes.md`, which describes the source model and supported departures from it.

## What the report covers

The review considers extraction/source fidelity, model loading and calculation settings, GE/TE diagnostics, taxon-to-group assignments and weights, separate membership/allocation confidence, catch/PPR coverage, and the modeled period and geography. Full mapping review includes zero-catch taxa as well as positive-catch taxa. Arithmetic and coverage denominators are checked against the stated reference year and catch basis.

Pipeline calculation and validation use the same mapping decision set. Validation checks and explains those decisions; it does not repeat a separate assignment of every taxon. An unresolved assignment or conflicting evidence remains a stated gap until its affected decision is reviewed.

Evidence can be reused when its inputs and settings still match. A reused report is different from independently extracting a paper or regenerating numerical diagnostics. Construction failures, unavailable matrices, unknown provenance and proposed changes remain visible in the report. The [current limitations](limitations.md) explain common restrictions.

## Different questions, different states

| State | What it tells you |
|---|---|
| Selected | This is the model chosen for the region. |
| Loadable | Its canonical JSON can be read; construction can still fail. |
| Diagnosed | The recorded method/configuration ran and produced its stated health result. |
| Ready for arithmetic | Required compatible coefficients, matching and inputs are available. |
| Validated by researcher | An explicit human decision is registered against the reviewed source and input identities. |
| Disqualified by researcher | The explicit negative review and reason are registered. |

A folder, successful file load or displayed number does not answer all of these questions. A diagnostic FAIL stays a FAIL, and a provisional display keeps its qualifications even when it contains finite values.

## Signing and displaying a decision

The researcher decision is made in the actual Word report. A signed final report can record `MODEL VALIDATED` or `MODEL DISQUALIFIED`, with the researcher name, date and applicable review findings. Drafting, moving or relinking the report does not itself register a new decision.

After authorized registration, `Project.xlsx` records the review for the exact `(unit_id, model_id)` pair, and the map/trends display it. Validated models have green Ecopath headings/names. Disqualified models have red headings/names, the exact verdict and reason, and are excluded from the validated-only filter. Disqualification preserves selection/results and transfers no approved sections or group exclusions.

Approved group exclusions affect webpage PPR contributions only. Saved catch, SPPR, diagnostics, regional results and NPP remain intact; omitted weights are not reassigned. The report's confidence table retains its reference year and catch basis. Changes to the signed report or relevant model/calculation inputs require a fresh registration check.

The [signed-review handoff](../tools/skills/ecopath-model-validation/references/researcher-signoff-and-map.md) describes registration. The [validation skill](../tools/skills/ecopath-model-validation/SKILL.md) and [template guide](../tools/templates/instructions.md) contain the detailed preparation and acceptance procedures. Human-authored text, signatures and manual appendix cells stay part of the review evidence.
''')
    write('explainers/limitations.md', '''
# Current limitations and what they mean

Availability, numerical validity and researcher approval are separate. Use the selected model's `model_notes.md`, saved diagnostics, coefficient identities and signed review to interpret a particular result. The restrictions below remain present in the verified project; reorganizing documentation or improving a skill does not resolve them.

| Limitation | Practical consequence |
|---|---|
| Some models have unsupported multiple-detritus construction paths. | A readable JSON is not proof that a calculator can construct or diagnose that model. Record the actual construction failure. |
| Some saved snapshots lack historical loader flags or executed code identity. | Their full workbooks can be inspected, but unknown provenance prevents automatic reuse of numerical results. Current defaults cannot reconstruct that history. |
| The selected Java Sea model in LME_038 has pending current coefficients. | Its selection and historical evidence remain available; a model switch or documentation update cannot make its current numerical results ready. |
| Some original publication/reference files are absent. | Source fidelity cannot be independently established from a JSON or derived table alone. Missing citations or bytes stay missing. |
| Decimal negative diet sentinels and an apostrophe-sensitive validation case remain known check discrepancies. | Keep their failure dispositions explicit; they are not resolved by folder or instruction changes. |
| Mapping evidence and descriptive audit metadata can disagree. | Reusing identical group/weight decisions preserves that numerical decision set; complete evidence readiness still requires the conflicting fields to be resolved. |

The [read-only verification summary](../regions/LME/LME_028/work/2026-10-04_000005_final_checks/qa/read_only_final_verification_summary.json) and [construction audit](../regions/LME/LME_028/work/2026-10-04_000005_final_checks/qa/construction_notes_audit.json) record the applicable checks and their scope. These are evidence records, not substitutes for the current model's scientific state.

## What the skill-efficiency trials establish

The bounded trials verified identical reported source values, saved-mapping arithmetic and full diagnostic returns/matrices within their stated comparisons. They also found unresolved limits: strict source diet construction failed for the independently extracted example; canonical missing masks and role fields differed; GE/TE saved aggregate coefficients exceeded the frozen absolute `1e-12` comparison tolerance; and an inherited broken source hyperlink blocked one rejected-review registration.

The isolated Word wording trial preserved package/render content but changed the signoff parser's captured sections, so that edit was not adopted. Shared instructions now require the relevant parser comparison for edits to those headings/labels. These findings do not establish full paper-to-PPR pipeline equivalence or authorize scientific repairs. The [trial report](../regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency/qa/completion_report.json) separates independently completed stages, reused evidence, regenerated outputs and remaining gaps.

## Reading a provisional or pending result

Pending means a required compatible input or stage is unavailable. Provisional means a specifically admitted display retains its diagnostic/interpretation flags. Neither state supplies researcher approval. Missing is distinct from zero, and a zero-catch row with an unknown coefficient is distinct from a positive-catch row with an unknown coefficient. [Model selection](model_selection.md), [validation](validation.md) and the [workbook reference](../README.md#workbook-reference) explain those states in context.
''')
    write('AGENTS.md', '''
# Project instructions

## project_contract

Before modifying project content, read [README.md](README.md) and [the current agent project contract](explainers/agents/project_contract.md). Both active project skills follow this contract. Reuse an unchanged contract already read in the same execution context; new contexts or changed contracts require reading it. Human guides live in `explainers/`; agent rules live in `explainers/agents/`. Current instructions replace superseded implementation plans; Git history supplies their recovery.

Preserve scientific inputs, researcher edits, missingness and diagnostic restrictions. Selection, loadability, readiness and researcher approval are separate. Do not repair parameters or invent provenance during administrative work. Serialize Project.xlsx writes. Use only canonical discovery and model-local outputs. Each distinct model retains only its latest extraction; Git history supplies recovery.

## graphify

Use the current graph at `tools/knowledge_graph/graph.json`; its scope describes coverage and freshness. Query with `graphify query "question" --graph tools/knowledge_graph/graph.json`. An outdated graph is an index of its stated snapshot, not evidence about current scientific results. `/graphify` uses the installed graphify skill; do not create a second graph location.
''')
    readme = (ROOT / 'README.md').read_text('utf8')
    old = 'Read [structure.md](explainers/structure.md) for the authoritative directory and ownership contract and [workflow.md](explainers/workflow.md) for operations. The [reorganization plan and execution record](explainers/plans/project_reorganization_plan.md) document agreements, verification, deviations and unresolved limitations. [Skill-efficiency ideas](explainers/plans/skill_efficiency_ideas.md) are reserved for the fresh follow-up chat.'
    new = 'The [reader guides](explainers/README.md) explain the [project layout](explainers/structure.md), [regional workflow](explainers/workflow.md), scientific methods and [current limitations](explainers/limitations.md). Agent operating rules are maintained separately in [explainers/agents/project_contract.md](explainers/agents/project_contract.md).'
    assert old in readme
    write('README.md', readme.replace(old, new))
    changes = [
        ('tools/skills/paper-to-ppr/SKILL.md', '[structure](../../../explainers/structure.md) and [workflow](../../../explainers/workflow.md)', '[agent project contract](../../../explainers/agents/project_contract.md)'),
        ('tools/skills/ecopath-model-validation/SKILL.md', '[structure](../../../explainers/structure.md) and [workflow](../../../explainers/workflow.md)', '[agent project contract](../../../explainers/agents/project_contract.md)'),
        ('tools/skills/ecopath-model-validation/SKILL.md', 'Read [structure.md](../../../explainers/structure.md)', 'Read [the agent project contract](../../../explainers/agents/project_contract.md)'),
        ('tools/skills/paper-to-ppr/resources/mapping/references/output-format.md', '[structure](../../../../../../explainers/structure.md)', '[agent project contract](../../../../../../explainers/agents/project_contract.md)'),
        ('tools/skills/paper-to-ppr/resources/extraction/procedure.md', '[structure contract](../../../../../explainers/structure.md)', '[agent project contract](../../../../../explainers/agents/project_contract.md)'),
    ]
    for name, old, new in changes:
        path = ROOT / name
        text = path.read_text('utf8')
        assert old in text, (name, old)
        write(name, text.replace(old, new))
    removed = []
    for path in sorted((ROOT / 'explainers/plans').glob('*.md')):
        absolute = path.resolve()
        assert absolute.is_relative_to((ROOT / 'explainers/plans').resolve()) and not path.is_symlink()
        removed.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path),
                        'disposition': 'Superseded plan removed from current docs; current requirements in agents/project_contract.md and human guides, verification in existing work QA; recover original through Git768dffbe.'})
        path.unlink()
    plan_dir = ROOT / 'explainers/plans'
    if not any(plan_dir.iterdir()): plan_dir.rmdir()
    kept = ['model_loading.md', 'sppr_methods.md', 'sppr_parameters.md', 'model_selection.md', 'PPREstimation/USER_GUIDE.md']
    for name in kept:
        assert sha(ROOT / 'explainers' / name) == baseline['explainers/' + name]
    save = {'baseline_commit': '768dffbee84c014e07850f88f042983caa186a41', 'baseline_sha256': baseline,
            'existing_human_guides_preserved_byte_for_byte': kept, 'removed_plans': removed,
            'scientific_artifact_writes': 0, 'user_instruction': 'Make explainers human-oriented; agents subdirectory allowed; no legacy plans; assess other guides individually.'}
    (QA / 'documentation_dispositions.json').write_text(json.dumps(save, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'human_guides_preserved': len(kept), 'superseded_plans_removed': len(removed), 'new_agent_contract': True}))

if __name__ == '__main__': main()
