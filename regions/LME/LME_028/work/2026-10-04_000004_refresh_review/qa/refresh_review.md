# Independent refresh review — 2026-10-04

Conclusion: no remaining reproducible material defect in the reviewed refresh/snapshot/workbook/updater paths after the fixes below. The final isolated regression run passed **12 tests, 0 failures, 0 errors in 60.874 seconds**. The five reviewed implementation files stayed byte-identical throughout that run; exact hashes are in `regression_review_results.json`.

Scope: `selection.py`, `snapshots.py`, `workbooks.py`, `update_project.py`, and the introduced shared `writes.py` guard. The reviewer read the project contract and agreed reorganization plan. Tests used temporary synthetic projects and a mocked publisher. No live regional workbook, Project.xlsx, scientific input or generated map was edited by the review. No scientific engine, broad SPPR or Monte Carlo execution was performed.

| Reproduced defect | Verified correction |
|---|---|
| Rejected split matching still restored cached numerical Annual/Taxon SPPR rows | Incompatible matching leaves the incoming model pending and those numerical tables empty. |
| Same-model refresh could relabel coefficients with changed loader flags; incoming models inherited outgoing flags | Pinned execution identity rejects mismatches; a distinct incoming model restores its own known flags. |
| Publication failure changed saved snapshot members | Snapshot, regional and central bytes roll back together on injected publication failure. |
| Direct central updater bypassed the lock | A held shared central lock rejects another updater. |
| Updating an Overview table deleted manual cells outside its columns; native table ranges lacked matching column definitions | Outside-column notes survive and native table range widths equal their column counts. |
| A human edit arriving between the first workbook read and hashing was lost | Preflight detects the change and preserves the human note. |
| NOT_RUN source/matching evidence with no numerical coefficients was reported ready | Useful evidence restores while the model stays pending; the NOT_RUN diagnosis survives. |
| A fresh compatible snapshot lost an existing true production-eligibility value | Exact compatible, fresh dependency identity preserves the saved flag without inferring new approval. |
| Unknown matching groups bypassed validation through the cached-results shortcut | Invalid membership leaves the model pending without old Annual values. |
| A valid changed mapping in a stale snapshot reused old PPR | Stored input/result freshness is checked and compatible arithmetic is recalculated; missing coefficients remain missing. |
| Cached uncertainty or independent NPP could be overwritten during restoration | Fresh bounds survive exact restoration. Changed NPP remains current, missing NPP produces missing ratios, and the existing recalculation policy invalidates historical bounds rather than labeling them current. |

The reproducible permanent-test candidates are in `test_review_regressions.py`; the final output is `regression_review.log`. Earlier reproduction files describe defects before correction and are historical review evidence, not current failure claims. They can be removed after the permanent checks and completion record incorporate the results.

Limits: this review does not certify the production HTML publisher, complete scientific-baseline preservation, current report approval identities, all concurrent-editor schedules, or independent replication of scientific results. Those belong to the release verification. Researcher-review registration was observed writing Project.xlsx outside the shared guard; the implementing agent agreed to add its wrapper and should verify that separate central-write path before release. An explicit `lock_held` argument is an internal coordinator interface, not a public concurrent-write bypass.
