# Workflow review, 2026-09-29

The central skill now routes size/stage/cohort requests to its allocation reference. Independent behavioral review exercised: positive catch with zero juvenile catch; all-zero and missing catches; geographic prefixes; distinct large/small croaker species; registration-gated evidence; explicit provisional authorization for a FAIL model; one fixed mapping across years/bases; and preservation of an existing taxonomic composite.

The review led to three clarifications: normalization requires a positive sum, not positive values in every group; the calculating helper requires calculation to be in scope; and observed count-to-mass conversions must retain bins, equations, raising factors and boundary treatment. These were incorporated. The skill frontmatter validator passed.

Independent code review found a pre-existing source-scope recalculation defect: an unavailable simple-reference treatment could overwrite the status of a numeric PP/inner method. A reproducing regression failed before the fix and passed afterward. Regional recalculation now takes base status from the native method treatment. Adoption also asserts that no previously numeric annual cells become unavailable.

All 41 workflow tests passed. The focused four allocation tests passed again after supporting the existing group_seq header variant. The allocation tests cover weighted PPR/catch mass, provenance, invalid-plan atomicity, zero-weight missing coefficients and source-scope status preservation. Live-data verification additionally checks exact source/group identities, original source/diagnosis preservation, all saved hashes, and independent annual method arithmetic.

Observed composition reused across all years/bases intentionally remains confidence=assumed; its source evidence is distinguished in weight_evidence. This choice prevents an observed source-period distribution from being presented as observed historical regional composition.
