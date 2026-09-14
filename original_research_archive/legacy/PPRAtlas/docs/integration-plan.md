# PPR Ecopath Atlas integration

Goal: extend the final all-84 Ecopath map and archive to precisely the 167 ecosystems in the Global Estimation worksheet.

Inputs are preserved snapshots. The original workbook and earlier projects remain untouched. The new project is isolated in its own directory.

- [x] Read Global Estimation IDs and values; independently reconcile to Selected Regions and selected polygons.
- [x] Recover the final map catalog and preserve its interface. Recalculate ranks and cumulative shares using the selected set, retaining missing PPR as missing.
- [x] Search each of the 84 EEZs; reuse earlier articles only with explicit geographic evidence. Record queries, sources, limitations, and unsuccessful searches.
- [x] Preserve article/model quality components (55 loadability, 20 documentation, 15 spatial fit, 10 recency/validation). A downloadable PDF alone does not prove a loadable model.
- [x] Recover available old files and download new accessible materials. Validate file structure and save hashes and actual retrieval outcomes.
- [x] Build the selected-set archive, metadata CSV/JSON, map, README, and reproducible Python entry point.
- [x] Test selection, rankings/ties/missing values, article links, verified files, and map controls. Inspect the map in a browser.

Data flow: immutable input snapshots -> selected ecosystem join -> curated article-to-region assignments -> verified files -> archive and map. Article footprints retain their provenance; EEZ polygons must never be presented as measured study boundaries without evidence.

Research distinguishes direct whole-EEZ, subregional, and basin-scale proxy evidence. Unresolved regions remain explicit gaps. The selected PPR sum retains the source workbook's residual overlap and missing-data limitations.
