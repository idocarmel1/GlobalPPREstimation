# Global PPR research

Open **Project.xlsx** for publication/model metadata, review records and generated regional summaries. Open **regions/<type>/<unit_id>/<unit_id>.xlsx** to work on a region. Double-click **interactive_map/Open map.cmd** for the map, or run `python tools/cli/map.py`. The launcher serves read-only files on this computer at 127.0.0.1; direct file opening uses the bundled land background.

Read [structure.md](explainers/structure.md) for the authoritative directory and ownership contract and [workflow.md](explainers/workflow.md) for operations. The [reorganization plan and execution record](explainers/plans/project_reorganization_plan.md) document agreements, verification, deviations and unresolved limitations. [Skill-efficiency ideas](explainers/plans/skill_efficiency_ideas.md) are reserved for the fresh follow-up chat.

## Selecting an existing model

Edit only `selected_model_id` and `selection_rationale` in the regional Overview, then run:

```powershell
python tools/cli/region.py refresh --region regions/LME/LME_028
```

Refresh derives the path and shortcut, saves a full outgoing workbook snapshot under its actual results identity, restores only compatible model tables, recalculates ready arithmetic and publishes the affected central/map/trend/source views. Missing prerequisites are explicit pending states. Catch, Classic PPR, NPP and manual content remain current. Unknown historical loader/code provenance prevents numerical snapshot reuse. Selection, readiness, diagnostics and researcher approval remain separate.

Find the selected model through the generated `selected_model.lnk`. Its single `model.json` and adjacent `model_notes.md` describe the scientific input and documented departures. Current review artifacts use `model_validation/validation.docx` and `taxon_mapping.xlsx`; its complete saved workbook is `results/regional_snapshot.xlsx`. Shortcuts are local, ignored navigation files and must be regenerated after a move/clone.

Adding a new paper/model requires actual source metadata and scientific registration once. Paper models live under that paper’s `models/`; JSON-only EcoBase candidates use regional `ecobase/`. Discovery never supplies missing citations or coverage. Use the [pipeline skill](tools/skills/paper-to-ppr/SKILL.md) for authorized scientific stages and the [validation skill](tools/skills/ecopath-model-validation/SKILL.md) for reports/review. Both follow root project_contract. Work uses the fixed run folders in structure.md.

## Runtime and commands

Use Python 3.11+ with openpyxl >=3.1,<4 and numpy >=1.26,<3. New SPPR runs additionally need pandas >=2, scipy >=1.11, sympy >=1.12, igraph >=0.11 and tqdm >=4. Engine-specific optional dependencies remain documented with their engines.

For a read-only explanation or inspection of one saved table, use `python tools/cli/region.py inspect --region regions/LME/LME_038 --sheet Overview --table Settings`. It returns that table and its source hash; it does not assess whole-workbook readiness. Both skills choose the requested operation through their shared [operation and dependency contract](tools/skills/paper-to-ppr/references/operation-contract.md) before reading detailed scientific references. Repeated reads in one Python operation can use the content-checked in-memory read session; existing mutation/publication guards still apply.

```powershell
python tools/cli/project.py --region regions/LME/LME_028/LME_028.xlsx
python tools/cli/project.py --all
python -m tools.project_core.maps.build_html --workbook Project.xlsx
python tools/cli/region.py --region regions/LME/LME_028 --stage calculate
python tools/cli/npp.py plan
python -m unittest discover -s tools/workflow_checks -p 'test_*.py'
```

Project/map commands operate on saved fresh regional state. They do not extract models, guess mappings or run SPPR. Ordinary direct diagnostics retain GE, TE and With Egestion; validation report rows retain GE/TE. Broad inventory/Monte Carlo requires its own scientific authorization. New arithmetic invalidates affected historical sensitivity bounds; unchanged compatible full restoration preserves them. Missing values stay missing, and diagnostic FAIL/NOT_RUN/provisional restrictions survive.

## Preservation and evidence

The latest extraction of each distinct model is retained; superseded packages are removed. Git history supplies recovery. The portable [source dispositions](common_reference_data/provenance/source_paths.csv) record moves/removals and historical hashes. Substantive frozen studies live under `research/`, with historical statements distinguished from current workflow authority. Administrative relocation makes no parameter repair or renewed scientific approval claim.

Shared NPP originals use product/year folders and existing Git LFS policy. After cloning use `git lfs install` and `git lfs pull`. The versioned [source manifest](common_reference_data/npp/source_manifest.json) and `python tools/workflow_checks/structure/verify_npp_sources.py` verify full bytes; new extraction outputs do not adopt workbook values automatically.

The canonical graph is [tools/knowledge_graph/graph.json](tools/knowledge_graph/graph.json). Its [scope](tools/knowledge_graph/REFRESH_SCOPE.md) records corpus/freshness limits. Query with `graphify query "your question" --graph tools/knowledge_graph/graph.json`. An older indexed snapshot is not current-result evidence; graph retrieval is not a scientific approval authority.

Street tiles require HTTP(S); the local launcher sends a real referrer and retains attribution. Leaflet and fonts require online access. Scientific boundaries and calculation inputs remain distinct from bundled display basemaps.

## Workbook reference

The package uses one workbook per region and one Project.xlsx. All numerical calculations are performed by portable Python, then stored as typed values. It does not require Excel or a proprietary recalculation engine. Saving a workbook in Excel does not itself refresh generated values.

### Tables within sheets

A table starts with `@table` in column A and its table name in B. The next row is the column header. Rows continue until the next `@table`. Empty spacer rows are ignored. Do not rename these markers or headers. The format permits matching and annual results on the same PPR sheet without duplicating explanation columns across years. The public `tools/project_core/workbooks/workbooks.py` reader/writer preserves all blocks. Rows may be sorted inside a block. Literal text is stored as text; authoritative formulas are rejected rather than read from stale caches.

Years are numeric headers 1950–2019. Blank is missing; zero is a measured/calculated zero. Each table has keys described below; duplicate keys are invalid.

### Regional workbook

- Overview / Settings: field,value. unit_id equals the workbook stem. Editable selected_model_id and selection_rationale own selection; model_path is generated relative to the region folder. results_model_id and SHA-256 fields record actual calculation identity, not editable approvals. taxon_detail_year and catch_basis select the taxon PPR view. Paper metadata lives centrally.
- Catch / Catch: taxon, common_name, functional_group, commercial_group, catch_basis, unidentified, and annual tonnes. One row per taxon/basis. Bases are landings, catch, discards. The unidentified boolean preserves the source classifier; named higher taxa are not automatically unidentified.
- Classic PPR / Taxa: taxon, tl, sppr, tl_source, match_method, confidence. The frozen 2019 taxon lookup is retained during migration, including its historical gaps. `sppr` is the actual coefficient used; changes to TL must also update it.
- Classic PPR / Annual and PPR / Annual: model_id, scope, method, catch_basis, unidentified, metric, status, annual values. Unidentified choices are method/zero/simple. Metrics ppr are wet-weight equivalent tonnes; catch/covered_catch are wet-weight tonnes. min_tC/max_tC are sensitivity bounds already in carbon. `status=ok` is required for publication of PPR.
  Explicitly user-authorized research previews use `status=provisional: <diagnostic and interpretation flags>`. They retain finite numeric coefficients (including negative failed contributions), show flagged PPR on the local map/trends, and remain excluded from reviewed common-catch comparison tables. A provisional status does not establish scientific validity, remove diagnostic failures, bypass mapping/freshness checks, or create missing values. Ordinary FAIL/NOT_RUN results remain unavailable until explicitly admitted for this preview. The September 28 regional integration records the user's request to display selected-model numerical results for later validation.
- Selected model groups / Groups: preserved upstream group parameters and taxonomy. Group SPPR: model_id,group,scope,method,sppr. Scopes are all,inner,PP, preserving current source spelling. Unknown scope coefficients remain blank.
- PPR / Matching: model_id,taxon,group,weight,confidence,evidence,explanation. One row per taxon/group; weights total 1. Unresolved rows retain taxon with blank group/weight.
- PPR / Taxon SPPR: generated selected-model coefficients, one row per taxon/scope/method. PPR / Taxon PPR inspected year shows catch × coefficient for the requested year/basis; change via `python tools/cli/region.py --region <workbook> --stage inspect-year --year <year> --basis <basis>`. All annual regional totals remain present simultaneously. Detailed annual taxon results can be exported with the same local catch and coefficients.
- NPP / NPP: method,units,annual values. NPP / Provenance: annual source/availability records. Carbon units are tC/year.
- PPR–NPP / Ratios: explicit annual regional percentages for each PPR and NPP choice. Numerator is PPR/9. Unsupported NPP years remain blank.
- Diagnostics: source engine model_health, mc_diagnostics, run_notes, and additional review records.

### Project workbook

Papers and Models & coverage are central editable databases. One model can apply to several regions; each application has its own unit_id. Do not conflate a paper's multiple model periods. Coverage percentages need a stated basis; absent percentages are not zero. Legacy source labels and unresolved links are retained, not fabricated.

`atlas_region_rank` in Regions & status, Papers, and Models & coverage is generated from current Regional PPR values for 2019: simple trophic chain, all sources, total catch (landings plus discards), unidentified treatment `method`, and status `ok`. Only members of `curated_region_ids` in common_reference_data/atlas_source_context/catalog.json.gz are ranked. Rank 1 is largest; equal values share a rank with subsequent ranks skipped, matching the map. Nonmembers and unavailable or invalid values remain blank. The rank describes the region, so its papers and model candidates share it; older `region_rank` metadata is unchanged. Project refresh recalculates these ranks. Every Project.xlsx data block is a native Excel table with filter controls; keep the separate `@table` marker rows intact. Year headers appear as text for Excel table compatibility and are converted to integer years by the workbook reader.

Generated Regions & status contains one row per region. Regional PPR and Regional NPP contain only regional annual results. Method comparisons / Pairs maps method pairs to anonymous common-catch cohort IDs. Common catch totals contains regional numerator/denominator component totals and covered catch per method/cohort; the cohort's taxa never leave the regional workbook. This avoids storing repeated series for pairs sharing identical support. Ratios with missing or nonpositive denominators are unavailable.

Researcher review is recorded per `(unit_id, model_id)` in Models & coverage. `researcher_review_status`, `researcher_name`, `researcher_review_date` and `validation_report_path` describe the explicit human decision and its Word source. Hidden source hashes and `researcher_review_summary` retain the review snapshot and model/input identities. `Validated by researcher` shows green Ecopath headings/names and approved sections; `Disqualified by researcher` shows red headings/names with the exact `MODEL DISQUALIFIED` verdict and reason below it. A disqualification transfers no approved sections or group removals, preserves selection/results, and is excluded from validated-only filtering. Project refresh preserves these fields and green/red model-cell styles. HTML generation verifies source identities; changed reports or model/calculation inputs require fresh registration. Follow the [signed-review handoff](tools/skills/ecopath-model-validation/references/researcher-signoff-and-map.md) for final Word registration and a bounded map/trends refresh; a draft alone does not authorize adoption.

The map's “Ecosystems to display” menu includes “Validated by researcher”. This shows ecosystems whose currently chosen model has a registered researcher review, within the selected ecosystem set and existing search, type and download filters. Validation eligibility follows model changes independently of the displayed metric; ranks and colors still use the full selected set.

Approved researcher exclusions affect webpage PPR contributions only. Saved regional results, SPPR, diagnostics, catch metrics and NPP retain their original data. Displayed coefficients retain the original allocation weights, without reassigning omitted shares. The group picker shows researcher-excluded groups unchecked and disabled; browser settings cannot re-admit them to displayed PPR. The reviewed confidence table remains explicitly tied to its report's reference year and catch basis.

Map geography stores GeoJSON in ordered text chunks so no cell exceeds Excel's text limit. Definitions & build / Metadata similarly stores non-species shared visualization definitions and the fixed atlas-union NPP reference. Neither table is an editable regional status/configuration sidecar.

### Freshness and ownership

Changing Catch, Taxa, Groups, Group SPPR, Matching, or NPP invalidates calculation fingerprints. `python tools/cli/region.py --stage calculate --region <region>` validates and rebuilds dependent results. Changing the selected JSON requires regenerating and verifying affected SPPR results with the reviewed input/settings before annual publication; follow the direct-diagnostics workflow for the requested methods, rather than automatically launching the broader SPPR stage. the project updater refuses stale results; changing only selection rationale is allowed. Project refresh preserves central metadata and replaces generated records by region ID. `--all` deliberately reconstructs the full current region set.

Historical defaults and scientific limits remain in explicitly frozen retained study/source evidence. Migration does not rerun Monte Carlo, fill missing TLs, infer geographic coverage, or promote a validation model.
