# Regional key run source preparation

Historical source-only stage. Canonical JSON extraction was subsequently completed; see the current [JSON creation report](JSON_CREATION_REPORT.md). Statements below describe the earlier stage, rather than current model availability.

Prepared on 14 October 2026. Work stopped before map publication, as requested.

Three new paper folders now hold the key-run sources alongside the existing regional papers. Separate folders are necessary because these are distinct ICES publications and configurations, not updates to the existing Mackinson 2007, Baltic 2026 or Celtic Sea 1985 model records.

## Regional packages

| Region | Folder | Material added |
|---|---|---|
| North Sea, LME_022 | [ICES WGSAM 2015](../../../regions/LME/LME_022/papers/ICES-WGSAM-2015/README.md) | ICES review and model documentation; official output ZIP; 60 original CSV outputs; two Excel output workbooks; published North Sea Rpath model object and configuration; Mackinson et al. 2018 paper applying the key-run model. |
| Baltic Sea, LME_023 | [ICES WGSAM 2016](../../../regions/LME/LME_023/papers/ICES-WGSAM-2016/README.md) | ICES review and model documentation; official output ZIP; 22 original CSV outputs; one Excel output workbook; published Baltic Rpath model object and configuration; Bauer et al. 2019 related Baltic ecosystem paper. |
| Irish Sea within Celtic-Biscay Shelf, LME_024 | [ICES WGSAM 2019 Irish Sea](../../../regions/LME/LME_024/papers/ICES-WGSAM-2019-Irish-Sea/README.md) | ICES acceptance and model documentation; SAMS 2019 key-run technical report; Bentley et al. 2021 fisheries-advice paper. No original model CSV bundle or runnable model file was located. |

The packages contain 98 verified source files in total, including **82 CSVs**, **three Excel output workbooks**, **seven PDFs**, **two output ZIPs** and **four Rpath files**. CSVs were unpacked without changing any bytes. They are simulation outputs, not the standard Ecopath input/import tables.

Each package has a source manifest, bibliographic metadata, model source notes and explicit material-availability limits. Published Rpath model objects and scripts are under the candidate's `inputs/native/rpath_port/`; related publications are under the paper's `sources/context/`; original output archives and unpacked tables are under `sources/supplements/`. Context sources are recorded in the shared source-role catalogue. The original research package remains intact.

## Model availability

The accepted native EwE databases have not been obtained. North Sea and Baltic Rpath files are published ports in another software framework; equivalence to the exact accepted EwE configurations remains untested. No R scripts or model simulations were executed, no parameters were repaired and no canonical `model.json` was invented.

These are **prepared source packages, not newly registered selectable models**. Conversion and source comparison remain necessary before a canonical model can be registered. In particular, model input CSVs, diet imports and biomass accumulation tables have not been generated. Original output CSVs cannot substitute for those inputs.

The paper accompanying the Rpath ports, Del Santo O'Neill et al. 2024, DOI [10.1111/faf.12817](https://doi.org/10.1111/faf.12817), was identified, but its PDF could not be downloaded: the institutional endpoint returned HTML and the publisher endpoint returned HTTP 403. These attempts are retained in [the retrieval record](evidence/related_paper_retrieval_20261014.json). The model configuration scripts and the original ICES documentation are available locally.

## Selection and coverage findings

No existing model registered for LME_022, LME_023 or LME_024 has `Validated by researcher` status. Therefore the user's verified-model exception did not require a replacement approval at this stage. No new researcher verification was conferred.

- North Sea retains its current East Coast of Scotland 1991–1995 selection.
- Baltic Sea retains its current empty selection.
- Celtic-Biscay Shelf retains its current Celtic Sea 1985 selection.

Baltic Proper excludes the Gulf of Riga and does not cover the whole Baltic LME. Irish Sea is a subregion of Celtic-Biscay Shelf; the project has no standalone Irish Sea region. These limitations are recorded, and no overlap percentage or whole-region coverage claim was invented.

## Stop point and verification

**Project.xlsx, the three regional workbooks, every pre-existing canonical model JSON in those regions, and map, trends and source HTML pages remain unchanged.** There was no registry write, selection change, regional refresh, map build or model calculation.

The verification checks source hashes, copied PDF bytes, ZIP integrity, every unpacked output's equality to its archive member, CSV readability, RData serialization headers and local documentation links. [Verification results](evidence/region_preparation_verification.json), [regional inventory](evidence/region_preparation_inventory.json) and [CSV inventory](evidence/regional_csv_inspection.json) record the exact scope.

The next integration stage remains paused: recover or faithfully convert the missing native model inputs, register supported canonical model candidates, then apply the requested selections and publish the map with the scientific and geographic limitations retained.
