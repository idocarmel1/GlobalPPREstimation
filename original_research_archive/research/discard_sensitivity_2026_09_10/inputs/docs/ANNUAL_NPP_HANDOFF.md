# Delegated historical NPP completion

The owner requested that the NPP extraction agent continue the full history
independently while the other tasks were finished. Tasks 1 and 4, the unidentified
catch controls, the PPR/NPP map selector and the legacy denominator correction are
complete. The full annual extraction and final all-ecosystem integration remain
assigned to that agent. The carbon conversion literature review and new Ecopath
coverage expansion remain deferred.

The live canonical file is `NPPExtraction/output/annual_npp.csv`. The current
atlas release and selected workbooks use an immutable intermediate snapshot,
`NPPExtraction/output/snapshots/annual_npp_for_task14.csv`, through the environment
variable `PPR_ANNUAL_NPP_PATH`. This is not full-history delivery. Earlier partial
ecosystem rebuilds also need replacement by the final full rebuild.

When extraction finishes, unset `PPR_ANNUAL_NPP_PATH` and run these from the
repository root, sequentially, stopping to resolve any failure:

1. `python tools/build_ecosystem_data.py --force` for all catch-bearing identities.
2. `python tools/build_model_workbook.py` for all ten mapped models.
3. `python tools/build_network_atlas.py`.
4. `python tools/build_time_series.py`.
5. `python tools/verify_model_workbook.py`.
6. `python tools/verify_annual_npp.py` without a unit restriction.
7. `node tools/verify_unidentified.cjs`.
8. `python tools/build_time_series.py --check`.
9. In this workspace, `python tmp/verify_task14.py` independently compares exact
   central/model mapping rows and confirms default PPR against the pre-change
   scientific snapshot for all 366 identities. It excludes only added sensitivity
   records and changed workbook hashes from that comparison.

Use the extraction project's installed environment, or another environment with
the documented dependencies. Model workbook saves now use atomic replacement
after an intermittent Windows destination-open error; errors must not be hidden.
The annual adapter already selects scaled regional totals in legacy files and
reads canonical annual values directly. Do not apply scaling again.

After all checks pass, update actual coverage and task status in
`docs/INTEGRATION_COMPLETION.md`, `README.md`, `data/README.md`, the implementation
plan, and relevant NPP documentation. Remove the temporary release note in the
data README and replace it with final coverage. Retain provenance, explicit
unavailable years, source/model counts and scientific limitations. Keep failed or
unsupported years distinct from successfully collected data. The optional
earliest-year proxy remains a display setting; workbook inputs stay annual.

Current verified baseline: 4,042 exact mapping rows across eight central LME and
ten model workbooks; 1,800 map/graph sensitivity comparisons; 88 root Python tests
plus two subtests and 39 JavaScript tests. Root production browser checks passed
for badge removal, workbook links, annual/proxy gaps, sensitivity controls,
source-scope limits, method changes, percentage labels and URL handoff.
