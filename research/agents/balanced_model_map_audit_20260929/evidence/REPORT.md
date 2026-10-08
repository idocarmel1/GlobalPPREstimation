# Balanced calculator state, regional results and map audit

Date: 2026-09-29. Status: read-only audit; implementation not performed.

## Scope and conclusion

Requirement: every PPRCalculator used to produce SPPR calculations available on the map must calculate using the balanced model exposed as `PPRCalculator.balanced_model`. The linked model and model-dependent interactions, including group filtering, must represent that same state.

**The requirement is not currently enforced.** The shared loader creates the balanced copy but returns the original calculator. Selecting `.balanced_model` alone is insufficient because its group table remains unchanged, regional adapters bypass the loader, and the publication chain has no enforced balanced-state identity.

The audit used the existing knowledge graph at `tools/knowledge_graph/graph.json` for orientation and verified findings in source. It inspected the current Project.xlsx selection metadata and generated map payload without writing either. No extraction, SPPR rerun, model adjustment, workbook write, map generation or skill update was performed. `Model_validation.docx` and `notes for AI.txt` were excluded and were not opened. The separate validation-report task was not used as evidence. Creating this Markdown report is the only authorized output of this follow-up.

Source references below are relative to this report's directory, three levels below the repository root. Line numbers identify the audited source revision and can move after implementation.

## 1. Actual balanced_model API and state

[PPRCalculator.py](../../../tools/scientific_code/PPREstimation/PPRCalculator.py), lines 218–275:

- `_fill_properties()` copies the completed group table into `_groups_df`, creates runtime pandas Series, resolves TL and records the original balance Boolean.
- Line 275 assigns `self.balanced_model = self.balance_model(change_production=False)`.
- The attribute contains a **PPRCalculator object**. It is not a method, dictionary, ModelData object or directly serializable JSON.

The same file, lines 696–735: `balance_model()` deep-copies the calculator and changes `growth`, `net_migration`, `predation`, `M0`, and `n_balance_runs`. The constructor's `change_production=False` retains production `p`.

### Limitations that affect implementation

1. **Stored tables are not synchronized.** The method does not update `_groups_df`, `_model.groups_data`, `_model.data_json`, or `is_balanced`. `get_groups_df()` at lines 815–821 returns the copied pre-balancing table; `get_model()` at lines 803–813 returns the original ModelData representation. Exporting either as the balanced model would misrepresent its runtime vectors.
2. **The first balanced copy normally has no nested balanced_model attribute.** The deepcopy occurs before its parent receives that attribute. A helper must not repeatedly descend through `.balanced_model`.
3. **The name is not a guarantee of strict balance.** The loop stops when predation and M0 stabilize, not when both balance identities pass. `is_model_balanced()` at lines 672–694 compares production with `p` and production plus egestion/respiration with `q`. Because `p`, `q`, egestion and respiration remain fixed under `change_production=False`, an existing `q != p + egestion + respiration` discrepancy can remain. The returned state's balance must be checked afresh; the copied `is_balanced` flag is stale.
4. **from_dict() is not exact restoration.** Lines 82–124 rerun defaults, optional LIM, property filling and balancing. Feeding a persisted balanced state through it can transform that state again.
5. **Runtime and source conventions differ.** At line 249 the loader sets runtime `net_migration` to table net migration minus `detritus_import`. Writing that runtime value into an ordinary Ecopath input and loading again can subtract the import twice. BA versus BA rate, immigration/emigration and derived flow fields also need explicit serialization semantics.

### Canonical, loaded and balanced states are distinct

[ModelData.py](../../../tools/scientific_code/PPREstimation/ModelData.py), lines 250–324, adds a synthetic import group, completes detritus routing and sets detritus catch to zero. [PPRCalculator.py](../../../tools/scientific_code/PPREstimation/PPRCalculator.py), lines 129–195 and 278–465, applies candidate-dependent defaults, optional LIM and optional diet normalization. These steps can complete biomass, GS, flows and BA. The subsequent balanced copy is another transformation. Neither loaded state nor balanced state is synonymous with canonical paper extraction.

SPPR methods operate on `self`; they do not automatically select `.balanced_model`. For example, `SPPR_new()` at lines 2485–2492 gets diets and TE from the supplied object, then uses its runtime flows in detritus calculations. `diagnose_sppr()` checks and solves the supplied object; lines 1048–1053 recompute its balance.

Coefficients may sometimes stay numerically identical after balancing, especially when only BA/migration changes. Numerical equality alone does not establish balanced-state provenance or preserve the validity of old diagnostic labels.

## 2. Shared implementation change points

| Source and lines | Current behavior | Required change |
|---|---|---|
| [create_PPRS_excel.py](../../../tools/scientific_code/PPREstimation/create_PPRS_excel.py), 954–960 | Constructs with underdetermined=True, zero_biomass_accum=False and normalized diets; returns the original calculator. | Establish an explicit publication loader that selects the constructor's balanced object while preserving candidate-specific audited settings and original-state evidence. |
| Same file, 810–950 | Runs methods, diagnostics, footprint and export on the object passed by the caller; worker receives that object at line 854. | Require one identified balanced state for the whole coefficient/diagnostic/export bundle. Guard direct callers as well as load_model callers. |
| Same file, 679–685 | Exports get_groups_df(), which remains stale after balancing. | Export a coherent balanced-state group projection from actual runtime vectors; retain the source table separately. |
| [run_region.py](../../../tools/project_core/calculations/run_region.py), 35–76 | Copies JSON into temporary input, runs exporter, copies Groups/Group SPPR/diagnostics, saves sppr_source.xlsx and records selected ID/input hash. | Persist and record balanced artifact, settings/code identity and coefficient-bundle identity together; retain the actual computational-input path. |
| Same file, 7–23 | Selection invalidation compares model ID and input JSON hash. | Also invalidate a changed balanced state or run under the same selected model ID; clear generated state identities when preparing a pending selection. |
| [regional.py](../../../tools/project_core/calculations/regional.py), 36–103 | Uses saved Group SPPR/matching, checks input JSON hash, then stamps that hash. | Require a verified balanced coefficient bundle before calculation; carry its identity into taxon/annual results. Do not stamp current identity onto unverified earlier coefficients. |
| [workbooks.py](../../../tools/project_core/workbooks/workbooks.py), 65–68 and 164–176 | Checks table freshness and optional input JSON hash; does not enforce balanced-state, engine/settings, diagnostics or computational-state identity. | Add central publication validation for state → coefficients → mapping → results, including missing-provenance rejection. |
| [update_project.py](../../../tools/project_core/registry/update_project.py), 8–56 | Copies validated regional annual values, selections, workbook hash and diagnostics. | Propagate compact balanced-state/result metadata without moving taxa/group coefficients into Project.xlsx. |
| [original_atlas_data.py](../../../tools/project_core/maps/original_atlas_data.py), 159–198 | Groups come from workbook Groups; TE is stored GE × EE; coefficients come from Group SPPR; allocations use names. Provenance lists workbook/sheets. | Build these fields from the adopted balanced bundle, with state/mapping/result IDs and stable group sequence identities. |
| Same file, 240–268 | Retains compressed historical alternatives and can reuse migrated selected detail. Chooses models/<selected>/sppr_source.xlsx, otherwise model.json, irrespective of Overview.model_path. | Gate or replace every computationally selectable model by verified state identity; resolve source links from manifest fields rather than guessed paths. |
| [build_html.py](../../../tools/project_core/maps/build_html.py), 33–63 | Emits map, trends, archive and downloads; page fingerprint identifies Project.xlsx. | Verify the complete publication bundle before emitting every view; expose consistent state identity and balanced-model links. |

Changing the general scientific constructors to silently return another object is not required. A publication boundary can select the balanced state explicitly while preserving source-state diagnostic and extraction workflows that intentionally inspect the original loaded state.

## 3. Regional producers and bypasses

These are dated producers of current data, not extra official general entry points. They prove that a shared-loader change cannot certify existing regional coefficients. Preserve frozen scripts and evidence; route future replacements through the shared publication boundary.

| Region/route | Verified producer and consumer |
|---|---|
| California | [prepare_selected_coefficients.py](../../../regions/LME/LME_003/papers/CAL-2016/models/CAL-2016_California_Current_2000-2014/model_validation/evidence/source_review/extraction_review_20260928/prepare_selected_coefficients.py), 23–55: loads the author-solved computational JSON with candidate settings, calls original m.diagnose_sppr(), writes groups and coefficients directly. |
| Falklands | [run_selected_sppr.py](../../../regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native__source/extracted_tables/evidence/run_selected_sppr.py), 25–56: monkey-patches cpe.load_model with an audited constructor returning the original calculator, then calls run_region.sppr. |
| WCPO: EEZ_941, EEZ_598, HS_071 | [reproduce_and_integrate_wcpo.py](../../../regions/EEZ/EEZ_941/papers/WCP-2007/models/941_20070101_WCPO_Warm_Pool_Option1_(mixed_periods)/model_validation/evidence/source_review/evidence/2026-09-28_integration/reproduce_and_integrate_wcpo.py), 29–66: original calculator/direct diagnoses; one coefficient state supplies three regional workbooks. |
| Eastern tropical Pacific | [reproduce.py](../../../regions/HS/HS_077/papers/ETP-2003/models/077HS_1_Eastern_tropical_Pacific_(1993-1997)/model_validation/evidence/source_review/evidence/2026-09-28_integration_audit/reproduce.py), 55–78: saves original-state coefficients. [integrate_provisional.py](../../../regions/HS/HS_077/papers/ETP-2003/models/077HS_1_Eastern_tropical_Pacific_(1993-1997)/model_validation/evidence/source_review/evidence/2026-09-28_integration_audit/integrate_provisional.py), 12–33: adopts them while retaining other legacy methods. A partial method refresh can leave mixed-state methods. |
| North Sea | [audit_runtime.py](../../../common_reference_data/provenance/source_paths.csv), 51–102: typed serialization restores original full calculator state, then diagnoses c/restored rather than their balanced copies. [integrate.py](../../../common_reference_data/provenance/source_paths.csv), 58–71, and [adopt_provisional.py](../../../common_reference_data/provenance/source_paths.csv), 11–13, adopt saved groups/coefficients. |
| Northwest Africa | [reproduce_direct.py](../../../regions/LME_027/models/27_118_Northwest_Africa_(1987)/integration_20260928/reproduce_direct.py), 34–60: retained engine and original-state direct returns. [integrate.py](../../../regions/LME_027/models/27_118_Northwest_Africa_(1987)/integration_20260928/integrate.py), 75–98, writes coefficients/provenance. |
| Benguela | [reproduce_direct.py](../../../regions/LME/LME_029/papers/BEN-2020/models/BEN2020_Southern_Benguela_1978/extracted_tables/evidence/integration_20260928/reproduce_direct.py), 34–60, and [integrate.py](../../../regions/LME/LME_029/papers/BEN-2020/models/BEN2020_Southern_Benguela_1978/extracted_tables/evidence/integration_20260928/integrate.py), 23–32: original runtime → saved CSVs → workbook. |
| Kyoto | [run_selected_sppr.py](../../../common_reference_data/provenance/source_paths.csv), 15–24, and [complete_supported_pipeline.py](../../../common_reference_data/provenance/source_paths.csv), 13–24: original runtime → saved groups/SPPR → workbook. |
| Patagonia and Visayan | Archived coordinator [audit_pending_runtime.py](../../regional_ge_integration_20260928/evidence/audit_pending_runtime.py), 13–39, serializes original state and diagnoses it. [integrate_pending_regions.py](../../regional_ge_integration_20260928/evidence/integrate_pending_regions.py), 16–23 and 55–62, adopts CSVs and writes computational_state_sha256. Shared validation does not enforce that field. |
| Watari pooled variant | Archived coordinator [audit_lme049_runtime.py](../../regional_ge_integration_20260928/evidence/audit_lme049_runtime.py), 13–37, serializes and diagnoses original state; [integrate_lme049.py](../../regional_ge_integration_20260928/evidence/integrate_lme049.py), 16–23 and 38–45, adopts it and records state hash. |
| Migrated retained outputs | [migrate.py](../../../common_reference_data/provenance/source_paths.csv), 90–134: copies saved SPPR workbooks without constructing a calculator. Inherited coefficients need balanced provenance/equivalence verification or must remain unavailable under the new contract. |

The selected Java model named “normalized BA completed” does not establish use of `.balanced_model`. [derive_selected_variant.py](../../../common_reference_data/provenance/source_paths.csv), 9–30, persists loader-completed BA and diet normalization, then compares ordinary loaded group tables.

Candidate-only extraction/diagnostic scripts are not automatically publication routes. Their source-state checks should remain distinguishable from adopted balanced-state calculations. The Mediterranean selection can remain selected with NOT_RUN results if construction is blocked; the new requirement must not invent a calculator or coefficients for it.

## 4. Experimental and stochastic states

### Celtic Sea exception

[run_experiment.py](../../../common_reference_data/provenance/source_paths.csv), 78–91, creates RoutingExperimentCalculator, explicitly sets `balanced_model=None`, then adjusts discard-return flows and restores printed BA. [routing_adapter.py](../../../common_reference_data/provenance/source_paths.csv), 15–64, changes detritus flow/budget equations and refuses unsupported TE. [reproduce_retained.py](../../../regions/LME/LME_024/papers/LME024-Hernvann-2020/models/Hernvann_2020_Celtic_Sea_1985/extracted_tables/evidence/integration_20260928/reproduce_retained.py), 25–48, reloads its pickle and supplies current coefficients.

There is no usable balanced_model in this retained state. Selecting an earlier constructor snapshot would discard later experimental changes. A balanced derivative of the finalized adapter is a new computational variant: it needs its own identity, must preserve subclass behavior, and cannot silently erase the printed-BA interpretation.

### Monte Carlo and historical sensitivity

[PPRCalculator.py](../../../tools/scientific_code/PPREstimation/PPRCalculator.py), 3200–3279, samples TE matrices and solves against `self`; it does not create a new calculator for every draw. The base must be the adopted balanced state, with random settings/results recorded separately. `_sample_SPPR_new_forced_balance()` at 3039–3074 solves a detritus SPPR scale; it is not the balanced_model transformation.

Frozen discard-sensitivity LedgerCalculator experiments intentionally clear balanced_model; see [scenarios.py](../../discard_sensitivity_2026_09_10/code/scenarios.py), 37–39. Preserve them as historical experiments, not automatic publication fallbacks. Do not modify experimental-engine copies merely because they contain the same class name.

## 5. Map, trends, archive and interaction identities

Read-only inspection of current selection metadata found **23 selected regions**. The existing map payload has **29 model entries** across those regions. Six retained alternatives occur in LME_013 (Humboldt), LME_027 (Banc d'Arguin), LME_028 (Guinea 1985), LME_036 (SCS 1970s), LME_047 (East China Sea 1997), and LME_052 (southern Okhotsk). If alternatives remain computationally usable, the requirement covers them too.

The inspected map payload links California, Falklands and Celtic to canonical `model.json`, although their calculations use a separate computational input or runtime state. Those sampled payloads have no balanced artifact/hash fields. Regional Overview paths confirm California uses a selected_pipeline author-solved JSON and Falklands a computational_input JSON.

- Browser group filtering uses embedded group coefficients and taxon allocation weights, not a loaded model JSON: [index.html](../../../tools/project_core/maps/original_html_layout/index.html), 218–300, duplicated in [trends.html](../../../tools/project_core/maps/original_html_layout/trends.html), 133–215.
- Group-table TL and TE come from Groups through original_atlas_data. TE is defined as stored GE × EE, not necessarily a method's effective TE. This meaning must remain explicit when moving to balanced-state values.
- Group identity is currently the group name; preference keys are `unit_id::model.id`. See index.html 423–452 and trends.html 338–367. A new state under the same model ID inherits browser model/group/range preferences without any state check.
- The map calculation-source links are rendered at index.html 852–855; trends primarily links the workbook at trends.html 856. Both need a clearly labelled balanced calculation-model link.
- Paper/native-model links are separate: [original_atlas_data.py](../../../tools/project_core/maps/original_atlas_data.py), 23–82, discovers/reconciles them, and [archive_layout.py](../../../tools/project_core/maps/original_html_layout/archive_layout.py), 11–14, renders them. Keep these canonical evidence links and add derived calculation-state links; do not relabel a derived artifact as the paper's original model.
- [provisional_display.py](../../../tools/project_core/maps/provisional_display.py), 7–31, explicitly admits provisional signed results in generated views. State migration must preserve diagnostic/provisional meaning and must not promote scientific grades merely because a balanced copy is selected.

## 6. Minimal coherent implementation plan

1. **Define a publication-state contract.** Preserve canonical source ID/hash and audited computational-input ID/hash. Add balanced-state ID/hash, engine/settings identity, adapter identity, transformation ledger and diagnostic identity. Distinguish the scientific selected model from a particular computational state.
2. **Persist the balanced state separately.** A durable artifact is needed for the exact download link and independently verifiable workbook/map/report identity. A typed, versioned JSON format is suitable; plain `json.dumps(vars(calculator))` is not. Serialize indexed matrices, runtime vectors, group identities/classifications and adapter state. Restore without rerunning defaults. Do not overwrite canonical model.json. Existing typed codecs demonstrate feasibility, not a completed shared contract.
3. **Produce one coherent bundle from that exact state.** Coefficients, full diagnostics and displayed group parameters must come from the same adopted object/state. Resolve stale-table exports explicitly without rerunning scientific completion. Record balancing deltas as computational adjustments, not measurements. Recompute strict flags and preserve failures.
4. **Route all publication producers through one boundary.** Cover stock exporter, candidate-specific constructor adapters, exact-state restoration and finalized experimental variants. Legacy methods without matching provenance cannot silently remain alongside updated methods. Source-state diagnostics remain separately available.
5. **Bind state, mapping and result adoption.** Record a mapping digest including group assignments, weights, confidence, evidence and explanations, plus coefficient, diagnostic and result digests. Store the adopted manifest in regional Overview/Diagnostics. Propagate compact identities through Project.xlsx and generated views.
6. **Gate alternatives and inherited data.** Verify balanced provenance for every model users can choose. Retain historical evidence as archived evidence when it cannot satisfy the computational contract. Do not silently reuse old migrated group detail or sensitivity bounds.
7. **Update links and browser identities.** Resolve links from manifest fields. Include state/result IDs in map/trends payloads and downloads. Use stable group sequence IDs and state-aware checks for localStorage and URL settings; preserve unrelated preferences. Apply the same rule to both pages.
8. **Update the active workflow instructions later.** The combined skill and its direct-diagnostics, regional-calculation and project-integration references should eventually document the source/input/balanced/adopted distinction. This audit does not edit them.

### Later skill requirement: report/data/map agreement

The user's later clarification is a **design requirement for the future skill update**, not authorization to change a current report, mapping, confidence, workbook or map during this audit.

The validation report should consume the same adopted model-state, mapping, diagnostic and result manifest as regional data and the map. It must not independently change adopted assignments or confidence labels. Proposed revisions can be labelled as proposals. Once a revision is adopted, update regional records and dependent calculations as appropriate, refresh Project.xlsx and pages, then generate the report from those same final identities. A report-only mapping/confidence change does not satisfy agreement.

## 7. Verification plan for implementation

Existing insertion points include [test_workflow.py](../../../tools/workflow_checks/test_workflow.py), [test_html_adapter.py](../../../tools/workflow_checks/test_html_adapter.py), calculator/exporter tests and map/trends JavaScript checks. No test or scientific rerun is claimed by this audit.

- Verify the publication path actually uses the selected balanced object and leaves original source/loaded evidence unchanged.
- Test runtime/group-export consistency, including BA, migration/import conventions, flow fields, diet/detritus matrices, stable IDs and fresh strict balance flags.
- Round-trip balanced state exactly without constructor defaults, including a finalized adapter fixture; avoid recursive nested balanced copies in serialization.
- Preserve candidate-specific normalization, tolerance, missing-data and LIM settings; reject unsupported finalized states instead of falling back to a different calculator.
- Reject missing/changed balanced artifacts, engine/settings, coefficient or diagnostic identities even when canonical JSON is unchanged.
- Reject mixed legacy/new methods and stale alternative-model payloads.
- Check row reordering and stable group-ID alignment, one-to-many weighted mappings, all/inner/PP scopes, catch bases, missing values, provisional negatives and one carbon conversion.
- Compare all-groups and selected-subset calculations between regional arithmetic, map and trends. Verify TL/TE filtering reads the adopted group state.
- Verify selected and alternative model links, page payload identities, result downloads and browser saved/URL preferences.
- Verify report, regional workbook and map share adopted identities and mapping/confidence values; report recommendations must not silently become adopted data.
- In a later authorized migration, run only the required scientific configurations on the exact persisted states, retain new diagnostics/deltas, invalidate/reassess historical sensitivities and refresh dependent outputs. Do not invoke a broad Monte Carlo inventory merely to migrate direct GE/TE/With Egestion results.

## 8. Two unresolved interpretation choices

1. **Exact exposed object versus guaranteed balance:** does the requirement mean the exact object currently exposed as balanced_model, even if is_model_balanced() remains false, or must the balancing algorithm additionally be corrected to guarantee both identities? The latter changes scientific behavior beyond choosing an existing state. Do not infer a successful diagnosis from the attribute name.
2. **Finalized experimental states:** how should states such as the Celtic adapter, which intentionally have balanced_model=None after post-constructor changes, be admitted? A new balanced derivative requires a distinct computational identity and a decision about its BA/return interpretation. Reusing an earlier cached balanced copy or substituting the native calculator would violate state fidelity.

These choices cannot be resolved from code alone. Until resolved, the safe publication behavior is explicit unavailability for states that cannot satisfy the chosen contract, while preserving the selected model and original evidence.
