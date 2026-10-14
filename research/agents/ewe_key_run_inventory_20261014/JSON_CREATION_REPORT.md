# Canonical JSON creation report

Completed 14 October 2026, following the request for a `model.json` for each regional package. This records the extraction stage, when publication was on hold. The user subsequently authorized selecting North Sea and Baltic Proper; see the current [selection report](SELECTION_PUBLICATION_REPORT.md). Publication statements below describe the earlier stage.

| Model | Canonical JSON | Groups | Source represented | Additional tables |
|---|---|---:|---|---|
| North Sea, 1991 | [model.json](../../../regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991/model.json) | 69 | Published Rpath port snapshot | Eight standard imports; 31 companions |
| Baltic Proper, 2004 | [model.json](../../../regions/LME/LME_023/papers/ICES-WGSAM-2016/models/ICES_WGSAM2016_Baltic_Proper_2004/model.json) | 22 | Published Rpath port snapshot | Eight standard imports; 17 companions |
| Irish Sea, 1973 | [model.json](../../../regions/LME/LME_024/papers/ICES-WGSAM-2019-Irish-Sea/models/ICES_WGSAM2019_Irish_Sea_1973/model.json) | 41 | Published ICES Table 0.1 baseline, with competing values retained separately | Eight standard imports; nine companions |

Each model has `model_notes.md`, a group profile, original sources, source comparisons and validation evidence. Standard imports are `Basic_input.csv`, `Diet_composition.csv`, `Landings.csv`, `Discards.csv`, `Detritus_fate.csv`, `Biomass_accumulation.csv`, `TL.xlsx` and `Metadata.xlsx`. Original ICES output CSVs remain separately labelled as outputs. Related papers remain in each paper's `sources/context/` folder.

## Source identity and acceptance limits

The North Sea and Baltic ports **materially differ from the accepted native EwE configurations**. Examples include North Sea cod QB and herring growth, and Baltic adult sprat biomass/PB and zooplankton PB. Their JSON files preserve the deposited ports; corrections from the ICES reports were not inserted into them. Where deposited parameters were missing, only estimates already present in the deposited model outputs were used, with their estimated roles recorded and original unknown inputs retained in companions. No new biological solve was performed.

Irish Sea unknowns remain explicit, including GS, group biomass accumulation, routing, habitat fractions and actual fleet catch allocations. Eight documented fleets are retained as identities, while available catches use one explicitly labelled aggregate reporting column. Competing Table 0.2 values and review changes remain in companions. Equivalence to the final accepted native database is unresolved.

No accepted native EwE database was recovered. These files describe Ecopath data snapshots, rather than complete accepted Ecosim simulations. Their historical folder names identify associated review material; they do not confer ICES acceptance on the extracted variants.

## Verification and retained restrictions

All three JSON files pass syntax, finite-value, group identity/order, import cardinality and canonical discovery checks. Numeric values and missing masks survived writer/converter round trips: North Sea 127,787 cells, maximum difference 4e-15; Baltic 30,122 cells, 4e-16; Irish Sea 35,634 cells, exact numeric equality. These differences are within the maintained tolerances; North Sea and Baltic spreadsheet round trips are not literal decimal-string equality. All source manifests and model evidence inventories passed their hash checks.

Source problems were preserved. North Sea has three detritus-fate sum errors; Baltic has one. Irish Sea has 43 structural missing-field warnings and one import mass-balance error; its source-preserving budget check contains 82 indeterminate outcomes. No parameter repair, invented defaults or diet normalization was applied.

Read-only loader checks also exposed downstream changes: North Sea's adapter drops TL, supplies unspecified imports, forces detritus self-routing and hardcodes LME 13 despite canonical LME 22; Baltic routing changes phytoplankton-to-detritus 1→0 and detritus self-routing 0→1. These observations are documented model-locally. Canonical values remain unchanged. Successful schema loading therefore does not establish readiness for calculation.

## Publication remains on hold

All 12 protected pre-existing files retain their original hashes, including Project.xlsx, regional selection workbooks, map pages and existing canonical models. No model was selected or centrally registered, no map was updated, and no Ecosim or SPPR calculation was run. Scientific readiness and researcher approval have not been conferred.

The [snapshot inventory](evidence/canonical_snapshot_inventory.json) records identities, hashes, companions and evidence checks. The [independent verification](evidence/canonical_json_verification.json) records discovery and preservation. The earlier [source preparation report](REGIONAL_PREPARATION_REPORT.md) remains a historical record of the stage before JSON extraction.
