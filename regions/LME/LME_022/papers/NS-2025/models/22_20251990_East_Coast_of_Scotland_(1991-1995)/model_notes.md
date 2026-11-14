# 22_20251990_East_Coast_of_Scotland_(1991-1995)

## Runtime correction prepared for review on 14 November 2026

The current regional Overview selects `ICES_WGSAM2015_North_Sea_1991`. This Scotland model is the explicitly named correction candidate; no regional selection or researcher decision is changed. The historical administrative/source descriptions below are retained as historical evidence.

Canonical publication inputs remain unchanged. A derived runtime variant retains all ecological groups and the computational import, removes only Seabirds self-feeding, proportionally redistributes that share to every remaining prey including Detritus, and refreshes predation at retained consumption. Only 13 affected BA entries whose ledger provenance and archived values prove prior loader derivation are recomputed; observed/manual/uncertain entries are not altered. No EE floor, broad balancing or changes to production, mortality, catch or migration are introduced.

Fresh historical-engine diagnostics are GE **OK**, TE **WARN**, and With Egestion **OK**. All strict model/SPPR balance flags are true, with no negative or nonfinite SPPR entries. The original TE self-loop divergence is removed. Near-zero TE warnings for Seabirds, Seals and Cetaceans and TE's no-detritus-recycling convention remain. These results support review, not registered approval or adoption into regional/map/trend outputs.

[Correction, provenance and exact before/after cells](results/diagnostics/2026-11-14_171200_seabird_derived_ba/correction_summary.md) · [Full execution evidence](results/diagnostics/2026-11-14_171200_seabird_derived_ba/evidence_index.json) · [Current review report](model_validation/validation.docx) · [Candidate mapping appendix](model_validation/taxon_mapping.xlsx).

## Preserved historical extraction and administrative record

## Source identity

NS-2025__LME_022

Regional application: `LME_022`. Canonical JSON SHA-256: `5cda503a847a6ea9bdcda077c184ac20119e0d8b47b064f93b72b72e3d7df691`. The byte-preservation check compares this retained representation with the pre-relocation working state; it is not a fresh extraction or a new approval.

## Modeled period and area

Period: 1991

Selected East Coast Scotland historical shelf/fleet model 1991–1995 is a subset of North Sea. Source Figure 1/PDF 3 red-outline marine trace gives A39.55% target covered and B99.84% study inside target; low-confidence approximate sensitivity brackets A37–42%, B99–100%, not statistical intervals. Inherited rectangle conflicts with source figure; target unchanged.

## Departures from the publication

Departures have not been independently re-extracted during this administrative task. No additional parameter correction is made. selected; GE and With Egestion OK, TE FAIL retained; all 384 total-catch labels reviewed, 372 mapped/12 freshwater unresolved; current report/appendix retained, provisional regional applicability

Existing departure summary retained: Published modern ECS model

The current validation document's Model extraction row records:

> Main PDF, four-sheet Table S1–S4 workbook and methods DOCX are retained. Existing audit matched 97 printed core parameters,232 source diet cells and 775 roundtrip values. Canonical parameters preserved; accepted diet normalization, GS defaults and residual BA completion are documented. Source Turbot/Ling balance is indeterminate without BA; computational balance is a separate finding.   Source/runtime audit  |  Runtime verification  |  Evidence review Retained departures and evidence limits:  model notes

Exact publication cells, values or decision provenance absent from retained evidence remain unknown. JSON loadability and an automated fidelity check do not by themselves establish source fidelity or scientific approval.

## Evidence links

- [Canonical Ecopath representation](model.json)
- [provenance.json](inputs/provenance.json)
- [validation.docx](model_validation/validation.docx)
- [source_review.md](model_validation/evidence/source_review/source_review.md)
- [REPORT.md](extracted_tables/REPORT.md)
- [result_manifest.json](results/result_manifest.json)
- [Portable source dispositions](../../../../../../../common_reference_data/provenance/source_paths.csv)

## Removed extraction evidence

Superseded extraction packages and their unique old evidence are removed under the agreed latest-only policy; they are not merged into this package. Original paths, hashes and reasons are metadata in the linked disposition ledger. A link to this paragraph records an unavailable former payload, not replacement evidence or completed scientific verification.
