from pathlib import Path
import hashlib, json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').is_file())
QA=Path(__file__).resolve().parents[1]/'qa'
records=[]
def replace(relative,text,reason):
    path=ROOT/relative;before=path.read_bytes();path.write_text(text,encoding='utf-8')
    records.append(dict(path=relative,before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reason=reason))

replace('tools/skills/paper-to-ppr/resources/mapping/procedure.md', '''# EwE species-to-group mapping procedure

This is a domain resource of the active [paper-to-PPR skill](../../SKILL.md), not a third skill. The [regional calculation contract](../../references/regional-calculation.md) and [validation guide](../../../../templates/instructions.md) govern current confidence, assumptions and adoption. Scripts and references resolve from this resource directory. The former stand-alone mapper's data/model_selection.xlsx, top10, work-order and builder paths are obsolete; they must not be recreated.

Ecopath groups and Sea Around Us taxa require an evidenced join. Measure both taxon coverage and the share of catch tonnage assigned to supported groups: a few coarse labels can carry most catch. Prefer near-complete coverage with transparent meaningful M10/M11 approximations; the former 95% target is not a pass criterion. Mapping coverage, coefficient availability, diagnostic health and researcher approval remain separate.

## Establish the exact inputs

Read the regional workbook through tools.project_core.workbooks.workbooks: Overview identifies the selected model; Catch contains taxa and annual bases; Selected model groups contains accepted group IDs/names. Resolve canonical JSON through tools.project_core.registry.discovery.resolve_model. Paper sources live in their paper's sources/, original catch under regional raw/catch/, and retained SPPR source/diagnostics under the model. A second selection workbook or work order is not authoritative.

Read exact group identifiers and accepted definitions before taxa. Names are joined literally, including punctuation and spatial prefixes. Verify taxon_descr in the actual model; an empty field differs from a completed search recorded as not documented. Source-faithful taxonomy is not overwritten with assumed analogue membership.

An evidenced group inventory can support mapping when the model is NOT_RUN or coefficients unavailable. Preserve that restriction and do not describe mapping controls as numerical eligibility. If group identity cannot be established, leave the affected mapping pending.

## Read membership evidence

Identify grouping axes: taxonomy, guild, habitat, spatial strata, life stage and size. Use [model structures](references/model-structures.md). Read paper/supplements for species-to-group tables, group definitions, size/depth boundaries, synonyms and explicitly adopted predecessors. Diet constrains a guild but does not establish exhaustive membership.

Transcribe source membership tables before decisions, retaining printed and verified accepted names, exact groups, source locators and table purpose. A diet-study list may be illustrative; reconcile dedicated groups and allocation tables before treating it as a constraint. Inspect every necessary candidate in a composite, not merely one overlapping member. Keep conflicts explicit.

Make real recovery attempts for identifiable missing supplements and record filename, URL, date and outcome. Distinguish direct adopted source, supporting regional evidence and analyst inference. Citation discovery alone does not establish that a source was read.

## Review taxa and weights

Work in catch-tonnage order while retaining all requested taxa, including zero-catch and unresolved rows. Evaluate explicit membership, verified synonyms, containment, habitat/size/guild, explicitly inherited classification and meaningful ecological analogues. TL corroborates but cannot select a feeding guild by itself. Use [coarse-taxa guidance](references/coarse-taxa-playbook.md) with current M10/M11 rules; offshore absence alone does not require Unresolved if a meaningful analogue is justified.

Establish eligible groups independently of coefficient availability. Prefer applicable direct caught-mass composition, then reviewed model-catch and model-biomass proxies. Both proxies retain Medium allocation confidence and transfer assumptions. Missing/default values do not become measured zeros. A justified W11 last resort is explicitly Very low. No automatic equal-share fallback, correction of erroneous totals by normalization, or silent candidate removal is allowed. Preserve genuine zero candidates in evidence.

Assess membership and allocation separately; the weaker necessary confidence governs High, Medium, Low, Very low or Unresolved. Weight one cannot strengthen unsupported membership. Nearby-model crosswalks require compatible definitions and actual donor evidence; donor weights and SPPR do not transfer automatically.

## Record, verify and integrate

Use [the current output contract](references/output-format.md). Adopted regional PPR / Matching has one exact taxon/group row per decision, numeric weights and evidence; unresolved group/weight stay blank. Preserve full precision, confidence, independent assumed flags and allocation evidence. Validate complete taxon coverage, duplicates, every composite member, nonnegative weights summing to one, basal-group errors, source contradictions and tonnage support for actual year/basis/method/scope. Structural success is not a source review or model approval.

For mapping-only work, finish requested evidence/decisions and state downstream work still required. For authorized adoption/arithmetic use the maintained regional API and python tools/cli/region.py --region regions/<type>/<unit>/<unit>.xlsx --stage calculate, then requested central/map integration. Preserve valid group coefficients, accepted model bytes, failures and independent Catch/Classic PPR/NPP. Selection changes use the single refresh command with complete snapshots and precise pending semantics.

Examples remain reference explanations, not cross-region assignment tables. Historical weak coverage or undisclosed stratum choices require assessment, never copying. Report taxon/tonnage coverage, confidence and assumption-dependent shares, composite weight bases, unresolved reasons, missing supplements and applicability. Keep extended source/numerical checks outside concise scientific report prose.
''','Remove obsolete standalone mapper schema and automatic fallback instructions; preserve current agreed membership/allocation semantics.')

replace('tools/skills/paper-to-ppr/resources/mapping/references/output-format.md', '''# Mapping records and supporting evidence

Regional PPR / Matching is the adopted mapping authority. Use the [regional contract](../../../references/regional-calculation.md) and [structure](../../../../../../explainers/structure.md). CSV transcriptions/proposals are evidence until authorized adoption, not a second mapping registry. Former data/<unit>/mapping, top10, builder and selection-workbook paths are obsolete.

## Adopted rows

One exact taxon/group row contains model_id,taxon,group,weight,confidence,evidence,explanation. Preserve full persisted precision, source/catch spelling and model identity. Resolved nonnegative weights sum to one within established tolerance; unresolved group/weight stay blank. Do not normalize erroneous totals or infer fallback from a blank weight. There is no automatic catch-to-biomass-to-equal cascade.

Keep one mapping per distinct model-region pair, including models sharing group lists. Period, area, scenario, season, strata and structure identities remain separate. Fixed weights across years/bases are an extrapolation, not evidence of invariant composition.

Membership/weight confidence and independent assumption flags belong in PPR / Mapping review and PPR / Allocation assumptions as applicable. Overall confidence is the weaker necessary component under High > Medium > Low > Very low > Unresolved. Direct applicable composition supports High allocation; reviewed model-catch/biomass proxies remain Medium assumptions. M10/M11 placement and W11 allocation retain Very low. Preserve zero candidates and rejected attempts. Numerical availability cannot establish membership.

## Source transcriptions and group dictionaries

Extraction membership evidence belongs in model-local extracted_tables/evidence/; validation assessment in model_validation/evidence/mapping/. Temporary proposal/import CSVs use work/<run_id>/inputs or outputs and are promoted or removed after checks. Use purpose-specific filenames, not a parallel permanent model-notes registry.

A membership transcription includes printed_name,accepted_name,group_name,source_page,table_purpose,evidence_scope. Preserve printed names separately from independently verified accepted names. State whether a list is exhaustive, illustrative, catch-allocation or diet evidence. Absence from an illustrative list does not prove exclusion. Reconcile broad diet-study placement with dedicated compartments and inspect every composite member. Bay of Bengal A3.1 diet-study versus A1.1/A1.3 allocation/composition is a source-specific example requiring version checks.

A dictionary retains every accepted group, including unfished groups: group_id,group_name,model_tl,grouping_basis,explicit_members,supporting_taxa,membership_source,source_relationship,source_location,source_url,notes. Grouping basis includes taxonomy, guild, habitat, size/life stage, stock, residual/nonliving pool and spatial stratum. Relationship distinguishes direct adopted source, supporting regional source and analyst inference. not documented means a completed search; blank means missing evidence. Preserve table purpose and source precision.

## Explanation and verification

State a decisive checkable fact with exact source locator: explicit membership, verified synonym, or described habitat/size/guild match. A coarse mixture requires eligible candidates, weight basis and applicability assumptions. Avoid unsupported best-match or similar-species claims. Never present inference as publication prose.

Link decisions from adjacent model_notes.md or the applicable evidence index. Record citation/DOI, period/area, grouping axes, available/missing supplements, judgments and limitations. Model area differs from target region; filename alone cannot establish coverage. Okhotsk NE is an identity label, not proof of northeastern-only scope.

Verify exact keys, all requested taxa, duplicates, sums, rejected/zero candidates, confidence/assumptions, missingness and numerical support. The old standalone mapper validator assumes an obsolete repository schema and is not a current workbook validator. Use maintained workbook/regional checks and independent source review.
''','Map evidence schema to adopted workbook contract, preserve source-scope cautions, eliminate obsolete normalization/fallback API.')

p=ROOT/'tools/skills/paper-to-ppr/resources/extraction/procedure.md'
t=p.read_text(encoding='utf-8')
t=t.replace('Resolve the directory containing this skill\'s `SKILL.md` as `<skill-root>`.','Resolve the directory containing this procedure.md as `<skill-root>` (the extraction resource root).')
start=t.index('## What one model produces');end=t.index('## Running the bundled tools')
t=t[:start]+'''## Permanent ownership and temporary conversion

The [structure contract](../../../../../explainers/structure.md) governs destinations. One distinct model owns one Ecopath-compatible model.json, adjacent model_notes.md, latest extracted_tables/ and evidence/. Paper originals belong to the paper's sources/; JSON-only candidates use regional ecobase/<model_id>/. Remove superseded extraction packages without merging their unique old evidence into the latest package.

The writer/converter use temporary representations. Stage an extraction in regional work/<run_id>/{inputs,outputs,code,qa}/. write_outputs.py creates a derived-name directory containing eight EwE imports: Basic_input.csv, Diet_composition.csv, Landings.csv, Discards.csv, Detritus_fate.csv, Biomass_accumulation.csv, TL.xlsx and Metadata.xlsx. Validate and round-trip those tables, retaining source-cell/missing-mask evidence and required companions. Promote the supported converted database JSON as the sole permanent model.json; the writer-input JSON is not that schema and must not occupy the canonical path. Promote current import tables, taxonomy and necessary REPORT.md/MASS_BALANCE.md/conversion evidence under extracted_tables/. Remove redundant staged JSONs, rebuilt workbooks and ZIP packages after reconciliation. They are not extra model representations or legacy retention.

Taxonomy.xlsx is produced when membership is requested under the active pipeline taxonomy contract. The converter reads it when present; otherwise taxon_descr remains null. Record source/model identity and known departures in model_notes.md, with exact field/group, published and retained values including missingness, rationale, limitations and evidence. This procedure does not authorize scientific corrections or guessed chronology.

''' +t[end:]
t=t.replace('Then update `MASTER_INDEX.md` at the top of the extraction set with this\nmodel\'s status.','Record scientific findings in the model evidence and its source provenance; do not add another editable status index.')
t=t.replace('Record the exclusion and the reason in `MASTER_INDEX.md`.','Record the exclusion and its source evidence in the paper source manifest and requested metadata handoff.')
t=t.replace('Keep `model.json` in the model directory. A correction pass edits it and re-runs\nthe writer, which is how a fix stays consistent across all eight files.','Keep the writer-input JSON in temporary work. A scientifically authorized correction edits that staging input and reruns the writer/converter checks; canonical model.json is the supported converted export. Do not overwrite accepted parameters merely to clear a check.')
t=t.replace('Two JSONs live in the directory and they are not the same file. `model.json` is\nthe *extraction* JSON from Step 5 — what you typed, the input to\n`write_outputs.py`. The database JSON is built from the eight CSV/XLSX files, not\nfrom `model.json`, which is exactly what makes it useful:', 'Two temporary JSON representations occur during conversion and have different schemas. The writer-input model.json in staging is not canonical. The database JSON is built from the eight CSV/XLSX files, independently of that input, which makes it useful:')
t=t.replace('## Step 8: write REPORT.md and update MASTER_INDEX.md','## Step 8: retain current REPORT.md and departure notes')
t=t.replace('Put the extracted values into one JSON file — the **extraction JSON**, shape','In temporary work, put extracted values into the writer-input **extraction JSON**, shape')
t=t.replace('Add `--zip` to get', 'Only when explicitly delivering an external package, add `--zip` to get')
t=t.replace('zip on the *last* pass', 'zip on the *last* pass')
t=t.replace('TL.xlsx` is located but not yet carried into the database JSON; trophic level\nstill lives only in the spreadsheet.', 'TL.xlsx` is located but not carried into the database JSON by this converter; preserve the source spreadsheet and its explicit applicability. The runtime TL calculation is a separate quantity.')
replace(str(p.relative_to(ROOT)).replace('\\','/'),t,'Preserve extraction science but separate temporary writer schemas from single permanent canonical Ecopath JSON and clean work lifecycle.')

p=ROOT/'tools/skills/paper-to-ppr/resources/extraction/references/source-bundle.md'
t=p.read_text(encoding='utf-8');start=t.index('## Project reference-use log')
t=t[:start]+'''## Project source roles and numerical use

Record paper source identities, bytes/hashes and roles in paper-local source_manifest.json and common_reference_data/provenance/paper_file_roles.json as applicable. Inputs/provenance.json identifies actual native/derived model inputs; the portable source_paths.csv records relocation/removal, not scientific use. Project.xlsx owns bibliographic metadata. Do not reinstate the obsolete root external/ reference-log builder or treat catalog presence as numerical use.

Distinguish archived/contextual candidates, selected sources, exact verified calculation input, isolated validation, rejected attribution and contextual methods. State what every source supports. Unknown identities and access limits remain unknown; inherited bibliography is not fresh verification. Preserve exact source bytes under current Git/LFS policy.

Independent catch/TL PPR and satellite NPP need no Ecopath extraction. Coverage gaps do not themselves authorize a new model or inclusion of separately owned unfinished research.
'''
replace(str(p.relative_to(ROOT)).replace('\\','/'),t,'Current source ownership replaces obsolete external reference-log command while retaining evidence/use distinctions.')

p=ROOT/'tools/skills/paper-to-ppr/resources/mapping/references/integration-contract.md'
t=p.read_text(encoding='utf-8')
# Preserve substantive scientific/history paragraphs; replace only stale execution
# sections and explicitly mark frozen study statements rather than certify them.
t=t.replace('This contract describes the implemented\npipeline;', 'Scientific rules below retain the original integration semantics. Current execution follows [project integration](../../../references/project-integration.md) and [regional calculation](../../../references/regional-calculation.md); obsolete historical API paths are not commands to recreate. Historical release counts and study availability below describe their cited snapshot;')
s=t.index('`data/<unit>/<unit>.xlsx`');e=t.index('Keep weights fixed across years')
t=t[:s]+'''Regional PPR / Matching contains the exact adopted model/taxon/group weights, confidence, evidence and explanation. Allocation assumptions retain all candidates, zero/rejected attempts and basis. Use full numeric precision, not a rounded CSV or preview. An authorized mapping change uses the maintained workbook/regional checks and dependent arithmetic; source-specific CSVs are evidence, not a second mapping authority.

''' +t[e:]
s=t.index('Use `NPPExtraction/ANNUAL.md`');e=t.index('Unsupported, partial, pending')
t=t[:s]+'''Read [NPPExtraction/ANNUAL.md](../../../../../scientific_code/NPPExtraction/ANNUAL.md) for current engine setup. Current shared originals are common_reference_data/npp/raw/<product>/<year>/ with source_manifest.json; use python tools/workflow_checks/structure/verify_npp_sources.py for actual source bytes and python tools/cli/npp.py plan before an authorized run. Extraction does not adopt values into workbooks. New derived output/cache stays local until its necessary provenance is promoted to versioned evidence.

The retained September 2026 expansion described 366 identities, preserved 11,310 original rows, added 4,398 supported records, reused 14 cells and produced 25,211 rows with 8,050 supported rows plus two historical 2019 cells. These are frozen release facts, not current reorganization verification targets. Its expansion writer and execution snapshots are historical study evidence under research/npp_extraction_2026_09/. Do not execute historical paths against live regional workbooks or recreate old output/data containers.

Preserve source-specific distinctions in any future reproduction: canonical npp_*_tC_yr fields were regional totals; the historical 2019 reference used scaled_* rather than unscaled npp_* totals. Never scale twice. Validate exact source/configuration/geometry/code provenance for the requested run; use isolated work and current engine instructions, not the obsolete tools/npp_data.py or expansion publication commands.

''' +t[e:]
t=t.replace('The current atlas displays 366 identities; 167 belong to its\ncurated archive and ten to its selected model set.', 'The historical source atlas described 366 identities, 167 curated members and ten selected models; current membership and selections must be read from saved Project/regional metadata.')
t=t.replace('Use the shared catch components and simple calculation from `tools/simple_atlas_data.py`;', 'Use the current regional/atlas implementation for shared catch components and independent simple PPR;')
t=t.replace('Read\n`docs/GLOBAL_ATLAS_NPP_REFERENCE.md` for its calculation and annual support.', 'Use the retained atlas-reference provenance and current Project Definitions & build metadata for its calculation identity and annual support.')
s=t.index('Hash actual raw bytes at validation boundaries:');e=t.index('When exact bytes are hashed, preserve them')
t=t[:s]+'''Hash actual raw bytes at validation boundaries: path, size and modification time can survive byte replacement. The frozen expansion helper used a metadata checksum cache; its separate September 11 audit reported 1,104 files/32,049,287,447 bytes. That historical audit does not prove present freshness or uncached checking at every past boundary. Current original-byte verification uses the canonical source manifest/verifier; a fresh scientific helper/run requires its own reviewed input/code identity. Never modify completed study code or provenance to match a new run.

''' +t[e:]
s=t.index('Maintain `external/ARTICLE_REFERENCE_USE_LOG.md`');e=t.index('## Transfer discard-routing responses')
t=t[:s]+'''Maintain current paper source manifests, native input provenance and source roles rather than the removed root external/ log/builder. Distinguish candidate/contextual presence, selected sources, actual numerical use, isolated validation and rejected attribution. Catalog membership is not numerical use or fresh bibliography. Separately owned unfinished research needs explicit inclusion authorization.

''' +t[e:]
t=t.replace('The production reader is `tools/discard_data.py`; its versioned input is', 'The original study integration used a separate discard reader. Its retained versioned response input is')
t=t.replace('The 2026 study supports 31 production method/scope combinations:', 'The frozen 2026 study reported 31 production method/scope combinations:')
s=t.index('Unset `PPR_ANNUAL_NPP_PATH`');
t=t[:s]+'''Use the current regional/project/map commands and applicable workflow_checks for requested publication; no historical builder command is an active route. Recheck actual controls/exports and distinguish handler tests from an observed saved download. Full global scientific verification belongs to a requested global reproduction, not an administrative relocation or bounded selection.

Preserve both historical Jensen calculations and their source evidence. Fresh diagnostics obey the active direct GE/TE/With Egestion contract; broad inventories or Monte Carlo need their own authorization. Never execute the broad create_PPRS_excel.py CLI merely to fill evidence. Selection, adoption, scientific repairs, fresh runs and researcher approval remain separate; a documentation update does not authorize them.
'''
replace(str(p.relative_to(ROOT)).replace('\\','/'),t,'Retain unique scientific NPP/discard/provenance semantics and historical findings; remove obsolete build APIs and false current-release claims.')
(QA/'resource_changes.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Reconciled',len(records),'domain resources without data changes.')
