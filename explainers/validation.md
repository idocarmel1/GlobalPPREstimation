# Validation reports and researcher decisions

A validation report brings together the evidence needed for a researcher to assess one model in one region. It is stored with that exact model as `model_validation/validation.docx`; the accompanying `taxon_mapping.xlsx` gives the detailed catch-taxon mapping and confidence evidence. The extraction row links to `model_notes.md`, which describes the source model and supported departures from it.

## What the report covers

The review considers extraction/source fidelity, model loading and calculation settings, GE/TE diagnostics, taxon-to-group assignments and weights, separate membership/allocation confidence, catch/PPR coverage, and the modeled period and geography. Full mapping review includes zero-catch taxa as well as positive-catch taxa. Arithmetic and coverage denominators are checked against the stated reference year and catch basis.

Pipeline calculation and validation use the same mapping decision set. Validation checks and explains those decisions; it does not repeat a separate assignment of every taxon. An unresolved assignment or conflicting evidence remains a stated gap until its affected decision is reviewed.

Evidence can be reused when its inputs and settings still match. A reused report is different from independently extracting a paper or regenerating numerical diagnostics. Construction failures, unavailable matrices, unknown provenance and proposed changes remain visible in the report. The [current limitations](limitations.md) explain common restrictions.

## Different questions, different states

| State | What it tells you |
|---|---|
| Selected | This is the model chosen for the region. |
| Loadable | Its canonical JSON can be read; construction can still fail. |
| Diagnosed | The recorded method/configuration ran and produced its stated health result. |
| Ready for arithmetic | Required compatible coefficients, matching and inputs are available. |
| Validated by researcher | An explicit human decision is registered against the reviewed source and input identities. |
| Disqualified by researcher | The explicit negative review and reason are registered. |

A folder, successful file load or displayed number does not answer all of these questions. A diagnostic FAIL stays a FAIL, and a provisional display keeps its qualifications even when it contains finite values.

## Signing and displaying a decision

The researcher decision is made in the actual Word report. A signed final report can record `MODEL VALIDATED` or `MODEL DISQUALIFIED`, with the researcher name, date and applicable review findings. Drafting, moving or relinking the report does not itself register a new decision.

After authorized registration, `Project.xlsx` records the review for the exact `(unit_id, model_id)` pair, and the map/trends display it. Validated models have green Ecopath headings/names. Disqualified models have red headings/names, the exact verdict and reason, and are excluded from the validated-only filter. Disqualification preserves selection/results and transfers no approved sections or group exclusions.

Approved group exclusions affect webpage PPR contributions only. Saved catch, SPPR, diagnostics, regional results and NPP remain intact; omitted weights are not reassigned. The report's confidence table retains its reference year and catch basis. Changes to the signed report or relevant model/calculation inputs require a fresh registration check.

The [signed-review handoff](../tools/skills/ecopath-model-validation/references/researcher-signoff-and-map.md) describes registration. The [validation skill](../tools/skills/ecopath-model-validation/SKILL.md) and [template guide](../tools/templates/instructions.md) contain the detailed preparation and acceptance procedures. Human-authored text, signatures and manual appendix cells stay part of the review evidence.
