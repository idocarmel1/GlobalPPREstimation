# ICES retained publication driver

Ready for coordinator review: `code/publish_ices.py`. It has NOT been executed. No shared implementation or live workbook/page/source was modified.

Frozen package: sibling `2026-11-14_230000_retained_adoption/outputs/retained_package_v2`. `inputs/package_pin.json` records the ready handoff's wrapper SHA fb7e602603bb4ea892d0e029a8ac8731259192add5ca774e1113ab527bfe0882 and preparation SHA b185578c27f803c9600bff4d919e99edcd1772c4395e0b61e6ab1728c3e9fdcc. No current Project hash is pinned; either negative-review batch may complete first.

Run with the existing scientific Python:

- Default or `--preflight`: lock, authenticate package and current sources, verify current Project/page coherence, then rehearse exact signed registration + bounded gate + candidate display in a model-local isolated root. All eight staged promotions are copied to their canonical relative paths in that fixture. Thus Groups are present there without touching the currently empty live Groups. No mock overrides change review semantics. Copies of current Project/pages are compared by hash, and live Project/pages remain unchanged. Fixture cleanup is scoped to the generated model-local temp directory.
- `--publish`: after package/source checks and a fresh current Project snapshot, enter rollback transaction tracking ALL eight promotion targets (including evidence_index and the new retained diagnostic files). Apply retained package FIRST, register current signed ICES report with [1,2,3,4,65] SECOND, verify bounded replay against the true immediately-prior Project/pages, then _update one regional workbook and _build only_units={LME_022}. No refresh_reviews publication is performed before numerical consolidation, so this is one final page build.

The driver prohibits ensure_validated_coverage via a runtime guard. It never calls full scientific inventory, arithmetic, selection, or the public update wrapper. Package verification reuses the staged results. Default selection is read from current regional Overview; final LME022 pages must select that ICES model. Other ecosystems' exact review metadata, exclusions, pending states and default model identities are compared before/after, including whichever negative reviews were published in the meantime. Other LME022 candidate reviews also remain unchanged.

Final checks compare every installed promotion byte to staged bytes, consumed inputs excluding intentional promotion targets, signed/canonical source hashes, actual report sections/signature, preserved Catch/Classic/NPP inputs, regional selection/rationale/path, production_eligible=False, 70 group IDs, 630 coefficient cells/scopes, exact page candidate health/provenance and taxon coefficients/missingness/statuses. GE/TE/With Egestion WARN and EE floor ON .1 remain mandatory. Group removals affect display only. Exclusion identity is the exact five names; their registered order follows the actual staged Groups order (which is reversed relative to the numeric list), and pages retain that same source order.

Static QA: `qa/static_review.json`. Python AST compiled; verified apply→register→bounded gate→one-region update→bounded build→final controls and complete promotion rollback tracking. Narrow staged inspection confirmed 70 groups and exact named sequences BaleenWhales1,ToothedWhales2,Seals3,SurfaceFeedingSeabirds4,DivingSeabirds65. Actual default preflight/publication remain for the root coordinator after its active transaction finishes. This is not a claim that ICES was registered or published.

The package's historical basking-shark allocation and source annual status policy remain unchanged: annual status ok with detailed WARN and production eligibility false; no reinterpretation of prior diagnostics or hypothetical sensitivity adoption.

## Final bounded preservation correction

The initial generic coverage._preserved_inputs check was unsuitable for this first import. It has been replaced with the package's verified independent scope: complete Catch, Classic PPR and NPP tables, plus separate exact selection/rationale/path checks. All four authorized model/mapping tables are independently bound to their staged digest, and final installed bytes remain equal to all eight authenticated promotions. No generated-output preservation loop was added.

Read-only live/staged check passed with independent digest 5d3c44c07fe38418be911a9c2221524165c0987c68c0d9e4c256d8e77ce26dcc. Authoritative records() counts in live Groups/Matching/Allocation assumptions/Mapping review are all zero; staged counts are 70/715/715/384. The earlier narrow XML count included blank/styled rows and was not populated data. The original pre-adoption snapshot remains protected by package input guards.

Progress is written to qa/progress.json and stdout with UTC timestamps, status and elapsed seconds for each stage, including slow consolidation and page build. No driver execution or shared mutation was performed while the prior batch was running.
