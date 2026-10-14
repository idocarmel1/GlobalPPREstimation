# ICES divisions IVa, IVb and IVc key-run sources

Prepared 2026-10-14. Key run 2015; publication 2016; modeled period 1991–2013; 69 functional groups.

[Primary ICES report](sources/ICES_WGSAM_2015.pdf), Annex 6, printed pp. 102–206; accepted native database listed on pp. 172 and 196.

[Model source package](models/ICES_WGSAM2015_North_Sea_1991/model_notes.md). Published Rpath model and configuration are retained under `models/ICES_WGSAM2015_North_Sea_1991/inputs/native/rpath_port/`. A Rpath port is not the accepted native EwE software configuration.

The original ICES output ZIP is retained in `sources/supplements/`, with 60 exact CSV files and 2 Excel output workbooks unpacked in `sources/supplements/key_run_outputs/`. These are simulation outputs, not model-input import tables.

Related publications retained as context:

- [Mackinson_2018_North_Sea_plan.pdf](sources/context/Mackinson_2018_North_Sea_plan.pdf)

[Metadata](sources/metadata.json) and [source manifest](source_manifest.json) record citations, roles and SHA-256 hashes. Canonical source extraction is complete. On 2026-10-14 the user subsequently authorized registration, regional selection and map publication; those administrative updates are now complete. Previously existing scientific inputs remain unchanged; Ecopath PPR results are pending.

## Canonical source snapshot

[model.json](models/ICES_WGSAM2015_North_Sea_1991/model.json) now contains 69 groups, with eight standard import tables and 31 source companions under `extracted_tables/`. Its identity is **published North Sea Rpath port snapshot; materially different from accepted native EwE configuration**. Missing values and source diagnostics remain explicit. This is an Ecopath data snapshot; it does not reproduce a complete accepted Ecosim scenario or confer researcher approval.

See [model notes](models/ICES_WGSAM2015_North_Sea_1991/model_notes.md) and the [JSON creation report](../../../../../research/agents/ewe_key_run_inventory_20261014/JSON_CREATION_REPORT.md) for source differences, validation limits and extraction-stage publication limits. The later [selection report](../../../../../research/agents/ewe_key_run_inventory_20261014/SELECTION_PUBLICATION_REPORT.md) records the authorized publication.

The source metadata, manifests and model-local extraction notes describe their recorded preparation stage. Current selection is owned by the regional Overview and Project.xlsx.
