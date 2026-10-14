# Selection and map publication

Completed 14 October 2026 on the user's instruction to select and publish the two balanced snapshots.

| Region | Saved default | Numerical status |
|---|---|---|
| North Sea, LME_022 | ICES_WGSAM2015_North_Sea_1991 | Static budget checks pass; Ecopath PPR pending |
| Baltic Sea, LME_023 | ICES_WGSAM2016_Baltic_Proper_2004 | Static budget checks pass; Ecopath PPR pending |

Both source snapshots and their associated ICES publications were registered in Project.xlsx. The regional Overview selections and rationales were saved through the existing workbook writer, followed by each region's maintained refresh command. The map, trends and sources pages were rebuilt. North Sea replaces the East Coast Scotland 1991–1995 default; Baltic previously had no selected model. No registered researcher-validated model was present in either target region before the switch.

These remain published Rpath variants that materially differ from the accepted native EwE configurations. Selection does not confer researcher approval. Native databases remain unavailable. Source routing restrictions and loader departures remain documented; no biological parameter, diet, missing field or model JSON was changed.

## Results and preservation

The outgoing North Sea results were saved under their actual East Coast Scotland model identity in its complete regional snapshot. The new selections have no compatible saved PPR coefficient/matching packages, so their Ecopath annual results remain unavailable. No result was copied from another model and no new SPPR or Ecosim calculation was executed. Normal publication preflight reused the existing complete 22-method packages for registered researcher-reviewed models.

Independent Catch, Classic PPR and NPP tables are unchanged in both target workbooks. All other regional workbooks retain their prior hashes, including LME_024 and its Celtic Sea selection. Every canonical scientific JSON retains its original hash. Existing central source metadata and researcher-review records were preserved; only authorized registration and derived selection/build fields changed. The source metadata/manifests and extraction notes remain evidence of their recorded preparation stage rather than editable current selection authorities.

The [map](../../../interactive_map/index.html), [trends](../../../interactive_map/trends.html) and [source catalogue](../../../interactive_map/sources.html) show the saved defaults and their sources. No new article footprint polygon or LME overlap percentage was inferred.

## Verification

The [selection verification](evidence/balanced_selection_verification.json) checks regional and central choices, current paths/hashes, unchanged independent values, blank researcher approvals, pending Ecopath results and map/trend defaults. Baltic Classic PPR model-ID cells changed only from empty strings to empty cells during serialization; no numerical value changed. The maintained HTML verifier checks current project fingerprints, layouts, annual values, NPP, selections and local source links. Separate [browser checks](evidence/balanced_selection_browser_checks.json) cover both model selectors, explicit unavailable Ecopath results, retained independent simple-chain values, source links and time-series views. An outdated agent-created tab was closed because it was synchronizing obsolete browser preferences; unrelated preferences were preserved.

Execution records: [North Sea refresh](evidence/north_sea_selection_refresh.log), [Baltic refresh](evidence/baltic_selection_refresh.log), [HTML verification](evidence/balanced_selection_html_verification.log). The [earlier JSON creation report](JSON_CREATION_REPORT.md) records the completed extraction stage and its scientific limitations.
