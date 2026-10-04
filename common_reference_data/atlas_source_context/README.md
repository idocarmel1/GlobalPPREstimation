# Atlas source context

These files preserve only the source data needed by the current atlas adapter and
its numerical parity check. Current annual results, selections and metadata still
come from `Project.xlsx` and current regional workbooks. Current page layouts and
calculation modules remain under `tools/project_core/maps/original_html_layout/`.

- `catalog.json.gz`: the exact UTF-8 JSON assigned to `const DB=` in the historical
  atlas map, including source context and alternative-model network evidence.
- `time_series.json.gz`: the exact UTF-8 JSON assigned to `const SERIES_DB=` in the
  historical time-series page.
- `eez_searches.csv` and `lme_searches.csv`: unchanged search-history downloads.
- `provenance.json`: original HTML hashes, extracted payload hashes and retained-file
  hashes. Gzip files use a fixed timestamp for reproducible compression.

Both payloads were decoded and compared with their original embedded objects before
the historical HTML shells were removed. Every numeric value and embedded string is
preserved. The historical paths recorded in provenance describe the extraction source;
they are not runtime dependencies. Embedded source-file references are resolved through
`common_reference_data/provenance/source_paths.csv` during the current atlas
build. Intentionally removed interface files have blank retained destinations and are
omitted from generated material links.

Historical provenance strings such as `source_region_workbook` remain unchanged in
scientific workbooks. Use `SourcePaths(root).resolve(historical_path)` from
`tools/project_core/registry/paths.py` to locate a retained source; the result is a current
repository-relative path, or `None` for an intentionally removed artifact. Keeping
the original provenance string preserves its historical meaning without requiring
obsolete directory structures to remain present.

`tools/workflow_checks/maps/test_html_adapter.py` checks retained-file integrity and source
membership. `tools/workflow_checks/maps/compare_original_html.js` compares the current map
and time-series calculations against these payloads, using the current calculation
modules. The default parity baseline is this directory; historical HTML is unnecessary.
