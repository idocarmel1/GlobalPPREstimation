"""Administrative documentation reconciliation; never edits scientific data."""
from pathlib import Path
import hashlib, json, re, difflib
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'Project.xlsx').is_file())
QA = Path(__file__).resolve().parents[1] / 'qa'
QA.mkdir(parents=True, exist_ok=True)
edits = []

def revise(relative, changes, reason):
    path = ROOT / relative
    before = path.read_bytes()
    text = before.decode('utf-8-sig').replace('\r\n', '\n')
    for old, new in changes:
        if old not in text:
            if new in text:
                continue
            raise ValueError(f'Missing audited text in {relative}: {old[:120]}')
        text = text.replace(old, new)
    after = text.encode('utf-8')
    if before != after:
        path.write_bytes(after)
        edits.append({'path':relative, 'before_sha256':hashlib.sha256(before).hexdigest(), 'after_sha256':hashlib.sha256(after).hexdigest(), 'reason':reason})
        (QA/'documentation_changes.json').write_text(json.dumps({'schema_version':1,'edits':edits,'scientific_data_edited':False,'skill_efficiency_implemented':False},indent=2),encoding='utf-8')

revise('tools/skills/paper-to-ppr/SKILL.md', [
    ('Read the [project guide and workbook contract]', 'Follow root [AGENTS.md project_contract](../../../AGENTS.md#project_contract): read [README.md](../../../README.md), [structure.md](../../../explainers/structure.md) and [workflow.md](../../../explainers/workflow.md) before modifying project content. Read the [project guide and workbook contract]'),
], 'Both active skills must explicitly follow all three must-read project_contract documents; no efficiency routing change.')
revise('tools/skills/ecopath-model-validation/SKILL.md', [
    ('- Read the [project workbook contract]', '- Follow root [AGENTS.md project_contract](../../../AGENTS.md#project_contract): read [README.md](../../../README.md), [structure.md](../../../explainers/structure.md) and [workflow.md](../../../explainers/workflow.md) before modifying project content.\n- Read the [project workbook contract]'),
    ('[Model_validation_template.docx]', '[validation.docx]'),
    ('Keep source tables, canonical JSON, computational input, loaded state, and saved diagnostic outputs distinguishable.', 'Keep source tables, the exact canonical JSON of the reviewed model/variant, ephemeral loaded state, and saved diagnostic outputs distinguishable. Each distinct computational variant has its own single canonical model.json and departure notes; no redundant computational-input JSON is retained.'),
], 'Explicit contract precedence, current template name and one-JSON ownership; report scope and approval gates preserved.')
revise('tools/skills/paper-to-ppr/references/model-preparation.md', [
    ('Paths inside retained domain documents remain relative to their own original skill directory; their old integration commands are superseded by this combined workflow.', 'Domain references resolve from their current resource directory. Their scientific rules apply with the current structure contract; obsolete repository commands are not an execution route.'),
    ('The schema is in `../../../../../README.md#workbook-reference`; the public table reader/writer is `../../../../workbooks.py`.', 'The schema is in [README](../../../../README.md#workbook-reference); the public table reader/writer is [workbooks.py](../../../project_core/workbooks/workbooks.py).'),
    ('For paper extraction, resolve the current `ecopath-extraction` skill from the available skill catalog and run its scripts from that resolved root. If unavailable, use the maintained portable fallback at `../../claude/ecopath-extraction/`, whose writer/converter support the same published-companion schema. Do not mix installed and fallback script versions within a run.', 'For paper extraction, use the maintained [extraction procedure](../resources/extraction/procedure.md) and scripts under `tools/skills/paper-to-ppr/resources/extraction/scripts/`. Resolve the resource directory from the procedure file, run scripts with quoted absolute paths and keep one recorded script version throughout a run.'),
    ('The archived resources preserve the original scientific procedures.', 'The retained domain resources preserve the scientific procedures.'),
    ("For discovery, place papers and supplements in the region's `papers/<paper_id>/`.", "For discovery, place the original paper in the region's `papers/<paper_id>/sources/`, supplements in `sources/supplements/`, and contextual sources in `sources/context/`, with explicit roles in source_manifest.json."),
    ('For extraction, write source-faithful EwE tables under `models/<model_id>/extracted_tables/` and source JSON to `models/<model_id>/model.json`.', 'For extraction, write the latest EwE tables under the exact paper-owned `papers/<paper_id>/models/<model_id>/extracted_tables/` and its sole Ecopath-compatible canonical JSON as `model.json` beside `model_notes.md`. JSON-only EcoBase candidates use regional `ecobase/<model_id>/`. Writer-input JSON and conversion intermediates stay in temporary regional work and are removed after reconciliation, rather than becoming additional permanent model JSONs.'),
    ('Model selection is owned by regional Overview: selected_model_id, model_path and selection_rationale.', 'Model selection is owned by regional Overview: editable selected_model_id and selection_rationale; model_path is generated by refresh.'),
    ('After changing Overview, use `--stage prepare-selection` to archive/clear old model results and leave the new selection pending.', 'After changing Overview, use `python tools/cli/region.py refresh --region regions/<type>/<unit_id>` to save full model-local snapshots, selectively restore compatible material, and publish a ready or precisely pending selection.'),
    ('For a paper extraction, read the resolved current extraction skill (or the maintained portable fallback above)', 'For a paper extraction, read the maintained extraction procedure above'),
    ('Read `../../claude/ecopath-paper-to-ppr/references/source-bundle.md`', 'Read [source-bundle.md](../resources/extraction/references/source-bundle.md)'),
], 'Remove obsolete skill distributions, flat extraction destinations and prepare-selection; preserve scientific extraction/diagnostic boundaries.')
revise('tools/skills/paper-to-ppr/references/direct-diagnostics.md', [
    ('Confirm canonical and computational-input identities.', 'Confirm the exact canonical model/variant identity and its recorded source departures.'),
    ('Reload the persisted computational input', 'Reload the exact canonical JSON of the audited model/variant'),
    ('Changing selection archives/clears obsolete model results with `prepare-selection`; catch, classic PPR and NPP remain.', 'An authorized selection change uses `python tools/cli/region.py refresh --region regions/<type>/<unit_id>` to save a complete outgoing snapshot and restore compatible selected-model content; current catch, classic PPR, NPP and unrelated human diagnostics remain.'),
], 'Current selection command and single canonical scientific input; no solver scope change.')
revise('tools/skills/paper-to-ppr/references/reconstruction-audit.md', [
    ('Keep four layers identifiable: source evidence, source-faithful canonical model, explicit computational input, and loaded calculator state.', 'Keep source evidence, the exact canonical model/variant with documented departures, and ephemeral loaded calculator state identifiable. A scientifically distinct computational variant has its own model ID and one model.json; do not retain separate source_model.json, computational_input.json or loaded-model JSON companions.'),
    ('Archive raw converter output when restoring changed source values.', 'Keep raw converter output in temporary work while reconciling changed source values; promote necessary cell evidence, then remove redundant conversion packages.'),
    ('solve the coupled system in a separate computational input;', 'solve the coupled system as an explicitly authorized distinct computational variant with one canonical model.json and model_notes.md;'),
    ('The extraction\nskill documents their manifest/schema in `references/published-companions.md`.', 'The extraction\n[companion reference](../resources/extraction/references/published-companions.md) documents their manifest/schema.'),
], 'One JSON per distinct variant and finite work lifecycle; preserve equation checks and historical runtime-equivalence restrictions.')
revise('tools/skills/paper-to-ppr/references/regional-calculation.md', [
    ('Paths inside retained domain documents remain relative to their own original skill directory; their old integration commands are superseded by this combined workflow.', 'Domain references resolve from their current resource directory. Scientific rules apply with the current structure contract; obsolete repository commands are not an execution route.'),
    ('with `../../../../workbooks.py`. See `../../../../../README.md#workbook-reference`.', 'with [workbooks.py](../../../project_core/workbooks/workbooks.py). See [README](../../../../README.md#workbook-reference).'),
    ('original downloads belong in raw/.', 'original downloads belong in regional raw/catch/.'),
    ('`../../../../scientific_code/SeaAroundUsExtraction/src/ppr_pipeline/`', '`tools/scientific_code/SeaAroundUsExtraction/src/ppr_pipeline/` (project-root path)'),
    ("the original mapper's scientific workflow at `../../claude/ewe-species-to-group-mapper/SKILL.md`", 'the retained [mapping procedure](../resources/mapping/procedure.md)'),
    ('Shared extraction code is in `../../../../scientific_code/NPPExtraction/`;', 'Shared extraction code is in project-root `tools/scientific_code/NPPExtraction/`;'),
    ("Global satellite inputs live once in `../../../../../common_reference_data/npp/raw/`, not in regional raw folders. Read that directory's parent README and `../../../../scientific_code/NPPExtraction/ANNUAL.md`", 'Global satellite inputs live once in project-root `common_reference_data/npp/raw/<product>/<year>/`, not in regional raw folders. Read [NPPExtraction/ANNUAL.md](../../../scientific_code/NPPExtraction/ANNUAL.md)'),
    ('in a versioned research archive or regional evidence folder', 'under an approved versioned research/<study_id>/evidence/ or regional work location, promoting current evidence to its permanent owner'),
    ('including `../../claude/ewe-species-to-group-mapper/references/model-structures.md`, `references/coarse-taxa-playbook.md` and `references/output-format.md` relative to that original mapper root.', 'including [model structures](../resources/mapping/references/model-structures.md), [coarse taxa](../resources/mapping/references/coarse-taxa-playbook.md) and [evidence output format](../resources/mapping/references/output-format.md).'),
    ("read its `references/mortality-and-discards.md`.", 'read [mortality and discards](../resources/extraction/references/mortality-and-discards.md).'),
], 'Correct current paths/resource ownership without changing missing-data, confidence or diagnostic rules.')
revise('tools/skills/paper-to-ppr/references/project-integration.md', [
    ('Paths inside retained domain documents remain relative to their own original skill directory; their old integration commands are superseded by this combined workflow.', 'Domain references resolve from their current resource directory. Historical release evidence is explicitly scoped; current commands below govern publication.'),
    ('For a full refresh use `--all` instead of `--region`. This discovers only canonical `regions/<unit>/<unit>.xlsx` files;', 'For a separately authorized all-region central update use `python tools/cli/project.py --all`, followed by the map builder above. The single-selection refresh command has no --all mode. Central discovery uses only canonical `regions/<type>/<unit>/<unit>.xlsx` files;'),
    ('under `../../../../../common_reference_data/npp/raw/`;', 'under project-root `common_reference_data/npp/raw/<product>/<year>/`;'),
    ('Their historical repository commands are superseded by the two current scripts above.', 'Historical release counts and study findings remain historical; current publication uses the commands above.'),
], 'Correct full-update interface and grouped paths; avoid implying refresh launches broader science.')
revise('tools/skills/paper-to-ppr/references/size-stage-allocations.md', [
    ('`tools/size_allocations.py`', '`tools/project_core/calculations/size_allocations.py`'),
    ('python tools/size_allocations.py --region regions/UNIT/UNIT.xlsx --plan reviewed-plan.json --backup retained-study/baseline/UNIT.xlsx', 'python tools/project_core/calculations/size_allocations.py --region regions/LME/LME_028/LME_028.xlsx --plan regions/LME/LME_028/work/<run_id>/inputs/reviewed-plan.json --backup regions/LME/LME_028/work/<run_id>/inputs/LME_028_before.xlsx'),
], 'Actual helper location and approved run placement; supported rule enum unchanged.')
revise('tools/skills/paper-to-ppr/references/evidence-handoff.md', [
    ('rebuild/verify map, trends and archive.', 'rebuild/verify map, trends and sources pages.'),
    ('Preserve checkpoint and old-skill baselines before editing.', 'Use committed old-skill instructions or a temporary checkpoint as comparison evidence; do not install a third active skill or retain superseded extraction packages.'),
], 'Current page naming and no disguised obsolete skill/extraction archive; replication rules unchanged.')
revise('tools/skills/ecopath-model-validation/references/evidence-and-calculations.md', [
    ('`common_reference_data/paper_file_roles.json`', '`common_reference_data/provenance/paper_file_roles.json`'),
    ('in the report and shared archive.', 'in the report and source-role evidence.'),
], 'Actual source-role registry location, distinguish contextual source from focal paper.')
revise('tools/skills/ecopath-model-validation/references/document-production.md', [
    ('Record source/copy paths and provenance in `reports_index.md` without replacing unrelated entries.', 'Record source/copy roles, portable paths and hashes in model_validation/evidence/evidence_index.json without replacing unrelated evidence. This index is provenance, not a separate editable status registry.'),
    ('`tools/validation_percentage_format.py --check <final.docx>`', '`python tools/project_core/validation/validation_percentage_format.py --check <final.docx>`'),
], 'Evidence index and formatting checker in their current owners; manual OOXML preservation rules untouched.')
revise('tools/skills/ecopath-model-validation/references/researcher-signoff-and-map.md', [
    ('`tools/validation_percentage_format.py --check <final.docx>`', '`python tools/project_core/validation/validation_percentage_format.py --check <final.docx>`'),
    ("sys.path.insert(0, str(root / 'tools'))\nfrom researcher_review import read_report, register_review\nfrom validation_percentage_format import verify_report\nfrom build_html import refresh_reviews", "from tools.project_core.validation.researcher_review import read_report, register_review\nfrom tools.project_core.validation.validation_percentage_format import verify_report\nfrom tools.project_core.maps.build_html import refresh_reviews\nfrom tools.project_core.registry.discovery import region_directory, resolve_model"),
    ("report = root / 'regions' / unit_id / f'Model_validation_{model_id}.docx'", "report = resolve_model(region_directory(root, unit_id), model_id).parent / 'model_validation' / 'validation.docx'"),
    ('[LME034 researcher review](../../../../regions/LME/LME_034/validation_reports/34_1_Bay_of_Bengal_(1978)/researcher_review_20261001/)', '[LME034 researcher review](<../../../../regions/LME/LME_034/papers/LME034-Guenette-2013/models/34_1_Bay_of_Bengal_(1978)/model_validation/evidence/source_review/researcher_review_20261001/>)'),
], 'Runnable namespaced imports and canonical report resolution; bounded replay/freshness gate remains strict.')
revise('tools/templates/instructions.md', [
    ('Use with `Model_validation_template.docx`.', 'Use with [validation.docx](validation.docx) and the authoritative [structure contract](../../explainers/structure.md).'),
    ('For example, a report in `regions/LME/LME_036/` links to `LME_036.xlsx`, `LME036_taxon_mapping_appendix.xlsx`, `papers/.../source.pdf` or `../../Project.xlsx`.', 'For example, a report at `regions/LME/LME_036/papers/<paper_id>/models/<model_id>/model_validation/validation.docx` links to `taxon_mapping.xlsx`, `../model.json`, `../model_notes.md`, `../../../../LME_036.xlsx`, `../../../sources/<paper.pdf>` and `../../../../../../../Project.xlsx`. EcoBase reports use the corresponding relative depth from their exact model folder; resolve and verify every target instead of copying a depth blindly.'),
    ('If supporting reports must be copied into `validation_reports/<model_id>/`, copy rather than move originals;', 'If needed supporting reports are copied into the exact model\'s `model_validation/evidence/source_review/`, copy rather than move originals;'),
    ('retain an appropriate permitted copy in the regional evidence folder', 'retain an appropriate permitted copy in the exact model\'s validation evidence folder'),
], 'Fixed current template/report/evidence destinations and portable links; scientific report field definitions preserved.')
revise('explainers/model_loading.md', [
    ('a selected JSON can already be an accepted transformed variant, a separate computational input can be selected, and loading changes the in-memory representation further.', 'a selected JSON can already be an accepted transformed variant, and loading changes the in-memory representation further. Each distinct variant owns its single canonical model.json and adjacent model_notes.md under the [structure contract](structure.md); no redundant source-model or computational-input JSON accompanies it.'),
    ('| `DC_tol` | `0.001` | `0.001` in `from_modeldata()` | Allow 0.001 absolute consumer-row deviation before a warning under normalization, or rejection without it. The code documents rounding as the rationale; a material deficit still needs source review. |', '| `DC_tol` | `0.001` | `0.001` in `from_modeldata()` | Allow 0.001 absolute consumer-row deviation before a warning under normalization, or rejection without it. The code documents rounding as the rationale; a material deficit still needs source review. |\n| `balance_BA_after_DC_normalization` | `True` | `True` | When runtime normalization changes a living group\'s predation, add the corresponding negative predation delta to its runtime biomass accumulation, retaining the original production residual. The input ModelData/JSON remains unchanged; this is a computational transformation, not observed BA. |'),
    ('The bare constructor delegates without normalization.', 'The bare constructor defaults to normalize_DC=False and passes an explicit request through; it does not normalize unless requested.'),
], 'Record current public loader flag omitted from older explainer, verified against existing engine code; no parameter/default changes.')
revise('explainers/sppr_parameters.md', [
    ('regional departures belong in the relevant region\'s own explainer.', 'model-specific departures belong in adjacent model_notes.md and effective loading/method settings in actual result provenance.'),
], 'Current model-local departure owner; method equations/defaults retained.')

# The old pipeline and retained mapper contracts have identical scientific text;
# their sole existing difference is the relocation of one study input path.
old = ROOT/'tools/skills/original_skill_resources/claude/ecopath-paper-to-ppr/references/integration-contract.md'
new = ROOT/'tools/skills/paper-to-ppr/resources/mapping/references/integration-contract.md'
diff = list(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(), new.read_text(encoding='utf-8').splitlines(), fromfile=str(old.relative_to(ROOT)), tofile=str(new.relative_to(ROOT))))
(QA/'integration_contract_comparison.diff').write_text('\n'.join(diff)+'\n', encoding='utf-8')
(QA/'documentation_changes.json').write_text(json.dumps({'schema_version':1,'edits':edits,'scientific_data_edited':False,'skill_efficiency_implemented':False},indent=2),encoding='utf-8')
print(f'Reconciled {len(edits)} active documentation files; data untouched.')
