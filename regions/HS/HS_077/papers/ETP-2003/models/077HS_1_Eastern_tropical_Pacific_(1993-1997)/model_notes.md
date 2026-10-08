# 077HS_1_Eastern_tropical_Pacific_(1993-1997)

## Source identity

ETP-2003__HS_077

Regional application: `HS_077`. Current canonical JSON SHA-256: `86cd1a54316e1cdd401e49355a2a75f65f462e15d21c287b55f9894ec54c6e84`. The pre-correction canonical bytes are retained as [original_model.json](original_model.json), SHA-256 `9cc8a41414194be6f40f4fafd9d6ed23c38a1c5812acd55e6e39824e783c2998`, by explicit researcher instruction on 2026-10-08. This original file is the former working representation, not a claim of a pristine independent publication extraction.

## Modeled period and area

Period: 1993–1997

Source PDF p.7 / printed p.137: 20 N–20 S, from 150 W to the approximate American shelf break; published study area 32.8 million km². No original geographic study map was found; Figures 1–4 on PDF pp.18–21 show dynamics and sensitivity. A labelled reviewer reconstruction gives A ≈ 47% of the target covered and B ≈ 46–48% of the study covered, comparing reconstructed and published study-area denominators. Shelf-break, coast-mask and repaired-target uncertainty imply low geographic confidence. See the regional geographic_estimate.json.

## Departures from the publication

On 2026-10-08 the researcher explicitly adopted five diet-entry relocations after the bounded source-placement tests. Exact values were preserved; only predator-column assignments changed. All nine material diet totals are now 1.000. Albacore remains 1.001, with no rounding adjustment. The corrected model retains the existing identity at the researcher's explicit request. Author intent remains unconfirmed.

| Prey row / value | Former predator | Corrected predator | Publication locator |
|---|---|---|---|
| Small bigeye tuna (22), 0.022 | Large sailfish (11) | Large swordfish (12) | Table 3a, p. 158 / PDF 28, row 22 |
| Mesopelagic fishes (32), 0.575 | Small marlins (23) | Small bigeye tuna (22) | Table 3a, p. 159 / PDF 29, row 32 |
| Mesopelagic fishes (32), 0.121 | Small swordfish (25) | Small dorado (26) | Same row |
| Mesopelagic fishes (32), 0.030 | Small dorado (26) | Small wahoo (27) | Same row |
| Mesopelagic fishes (32), 0.070 | Small sharks (28) | Miscellaneous piscivores (29) | Same row |

All non-diet fields, diet imports, unknown markers and unrelated diets are unchanged. Source blanks at new destinations become the retained entries; original donor entries are absent after relocation. Dorado's 0.030 is moved out simultaneously with receiving 0.121. See the [misplaced diet entries report](misplaced_diet_entries_report.md) and its exact before/after ledger.

On 2026-10-08, the corrected canonical model and reviewed notebook constructor/default method settings were executed directly for GE, TE and With Egestion. All three current diagnostic grades are WARN; GE and With Egestion pass strict SPPR balance, TE fails that strict check. Current coefficients and regional arithmetic were refreshed and their exact source, engine, runtime and full returns retained in [review refresh evidence](model_validation/work/2026-10-08_151542_review_handoff/outputs/diagnostics/run_manifest.json). Production eligibility remains false; provisional numerical display is retained. Catch, NPP, taxon mappings and the independent classic coefficients are unchanged. Historical sensitivity bounds were invalidated. Ido Carmel signed MODEL VALIDATED on 08/10/2026; the seven named exclusions apply only to displayed PPR, and are registered in Project and the map. The signed Word retains researcher-written historical source/diagnostic descriptions; current scientific discrepancies are recorded here rather than rewriting the signed review.

Existing departure summary retained: ETP 7

The signed validation document still records the pre-correction input state quoted below; this passage is historical and superseded for the current canonical diet placements:

> Nine material published diet-sum errors are retained in canonical inputs. The accepted historical runtime normalizes ten diets at 0.001 tolerance, including Albacore 1.001; infers missing BA; supplies missing-catch zeros and detritus/import defaults. Source BA and detritus routing remain undocumented. Censored whale EE and fleet catches are distinct from exact zero. No source values were restored or rebalanced.   Reconstruction report  |  Source and runtime review Retained departures and evidence limits:  model notes

Exact publication cells, values or decision provenance absent from retained evidence remain unknown. JSON loadability and an automated fidelity check do not by themselves establish source fidelity or scientific approval.

## Evidence links

- [Corrected canonical Ecopath representation](model.json)
- [Preserved pre-correction representation](original_model.json)
- [Misplaced diet entries report](misplaced_diet_entries_report.md)
- [provenance.json](inputs/provenance.json)
- [validation.docx](model_validation/validation.docx)
- [source_review.md](model_validation/evidence/source_review/source_review.md)
- [result_manifest.json](results/result_manifest.json)
- [Portable source dispositions](../../../../../../../common_reference_data/provenance/source_paths.csv)

## Removed extraction evidence

Superseded extraction packages and their unique old evidence are removed under the agreed latest-only policy; they are not merged into this package. Original paths, hashes and reasons are metadata in the linked disposition ledger. A link to this paragraph records an unavailable former payload, not replacement evidence or completed scientific verification.
