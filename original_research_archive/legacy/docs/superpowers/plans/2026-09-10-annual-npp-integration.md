# Annual NPP and mapping visibility implementation plan

Goal: execute the owner's tasks 1, 2 and 4; leave carbon-conversion literature review and new Ecopath coverage expansion deferred.

Architecture: preserve the supplied NPP methods as an installable Python package under NPPExtraction. Add a resumable archive/catch-year batch runner with explicit source availability. Publish one canonical annual CSV consumed by a shared integration adapter, workbooks and atlas exporters. The archive/catch grid must include unavailable years without inventing historical satellite data. Existing 2019 inputs remain traceable reference data.

Execution: use the subagent-driven-development skill for independent extraction, workbook and browser components, with root-owned data adapter/export integration and final review. Work in the current checkout because the user-supplied ZIP and this chat's task list/audit are uncommitted here. Preserve those changes; do not push or publish.

## Interfaces and constraints

- Canonical file: `NPPExtraction/output/annual_npp.csv`, one row per `unit_id,year`, with `npp_antoinemorel_tC_yr`, `npp_vgpm_tC_yr`, `npp_eppley_tC_yr`, `npp_cbpm_tC_yr`, `npp_cafe_tC_yr`, `ens_median_tC_yr`, `ens_min_tC_yr`, `ens_max_tC_yr`, `status`, `reason`, `provenance`. Missing numeric values are empty, never zero.
- Root-owned `tools/npp_data.py`: `load_npp(root)` returns a mapping of unit IDs to dictionaries with `annual` keyed by string years, retaining legacy 2019 scalar fields for compatibility; `npp_for_year(record, year)` returns that year's dictionary (no implicit fixed-year fallback).
- Root-owned time-series exporter: unit `npp` method values become arrays aligned to `years`; `npp_year` is null for annual data, `npp_source` points at the canonical CSV. Preserve full-series cohort comparisons and clearly disclose unavailable years.
- No changes to SPPR algorithms, mapping decisions, 1:9 conversion, pilot coloring eligibility, or new Ecopath coverage.
- Use original repository workbook builders; preserve their formulas and independent numerical verifiers.

## Work and verification

- [x] Extraction: safely unpack ZIP without overwriting unrelated files; install dependencies in a fresh environment; run supplied tests. Test archive-year identity enumeration, unsupported years, per-model missingness, resume configuration and annual output before implementing. Document Windows/Linux setup and exact reproduction commands. Probe sources and run actual extraction for supported years, retaining failure records and provenance.
- [x] Data integration: test year lookup, no fixed-year leakage and legacy 2019 compatibility; implement adapter and annual time-series/network export. Regenerate affected artifacts and verify hashes/annual arithmetic.
- [x] Workbooks: expose complete final mappings (including model identity, numeric weights, evidence, confidence and unresolved taxa) in central LME workbooks. Adapt NPP sheets and yearly PPR/NPP calculations to the shared adapter. Verify exact mapping parity and year-specific ratio behavior; inspect rendered representative sheets. The full annual population has been rebuilt and verified in all 364 central and ten model books.
- [x] Atlas: remove only the visible search-status badge; update map/time-series source links, year-aware NPP displays and availability language; retain search metadata. Test annual values, missing early years, preserved PPR and conversion, and source links.
- [x] Final: run affected Python and JavaScript checks, source/workbook/export audits and browser checks. Update README, data docs and task status with actual extraction coverage and any external limitations; do not label unsupported or failed years as collected.

Owner's decision: unavailable years remain blank by default. The optional display policy uses the earliest available value for earlier years only, retaining its source year and estimated status. It does not fill internal or later gaps or extrapolate a linear trend. Acquisition is separate from source availability; network errors remain errors and are resumable.

The owner explicitly confirmed processing the full available 1998–2019 history in
this chat after being informed that the native raster calculations may take hours.
Complete the full supported catch-year grid before the final integration rebuild.

Completion: the delegated extraction processed all 22 supported years and all
11,310 archive catch-year targets (2,796 complete, 842 partial, 7,672 unsupported;
no failed/pending rows). After the agent finished all workbook writes, root
rebuilt both atlas exports from the canonical CSV with no snapshot override.
Final annual, mapping and three-catch-basis audits passed. See
`docs/ANNUAL_NPP_HANDOFF.md` for the reproducible sequence and exact counts.

Additional user-authorized scope from the PPR/NPP investigation: add explicit
unidentified-catch treatments (selected-method default, zero assumption, reference
TL chain) to map/time series, URL state, coverage and downloads. Publish affected
labels and keep source decomposition unavailable for a total-only fallback.
Verify the legacy NPP denominator fields against the imported specification;
select existing scaled regional totals only where that semantic mismatch is
demonstrated, preserving canonical annual values without another scaling step.
The requested PPR/NPP map color option is already part of the annual integration;
verify that both method selectors and the sensitivity setting drive its values.
