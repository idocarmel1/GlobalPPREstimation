# Aydin2007 Gulf of Alaska — full published extraction

## Source identity

Aydin, K., Gaichas, S., Ortiz, I., Kinzey, D. and Friday, N. (2007). *A comparison of the Bering Sea, Gulf of Alaska, and Aleutian Islands large marine ecosystems through food web modeling*. NOAA Technical Memorandum NMFS-AFSC-178. [NOAA source](https://repository.library.noaa.gov/view/noaa/22894). The original 309-page PDF is retained in ../../sources/. Main numerical evidence is Appendix C, with Appendix A and main-text/Appendix B rules.

## Modeled period and area

Annual base 1990–1994, using some adjacent-period observations; 291,840 km² covering the Gulf of Alaska shelf and slope at 50–1000 m. Nearshore waters shallower than 50 m are excluded. Geographic overlap with the complete LME_002 boundary has not been measured. See extracted_tables/MODEL_PROFILE.md for stage, guild, unit and spatial details.

## Extraction and departures

The canonical JSON contains 133 reported groups (including two zero-biomass skate rows), with all eight standard import files, 13 published evidence companions and source-derived taxonomy. Original numeric values, explicit zeros, trace literals and unknowns are retained. No diet normalization, fitted parameter adjustment, inferred zero BA, or reconstruction from the later aggregate has been applied.

The full published model cannot be reconstructed completely from the recovered report. Preference allocations among multiple eligible prey require unpublished availability denominators, and the bird tables do not specify all final group-level diets. Singleton eligible pools are resolved exactly; multi-member pools remain unknown. Four overlaps between direct amounts and unresolved pools remain unknown in the final matrix. Three BA values are explicit: adult pollock −1.35, herring −0.11, greenlings −0.002 t/km²/year; the other 130 BA cells are unknown. Adult-pollock detrital routing is not explicitly covered by the printed group-range rule and remains unknown.

Published Flathead sole and Southern rock sole diet columns total 105.46% and 106.93%; these were checked against rendered source pages and retained. The Large sculpins table allocates 3.09% to juvenile Yellowfin sole and juvenile Northern rock sole, which are absent from the GOA group inventory; the allocations are preserved as unresolved source evidence rather than reassigned to adults. Source preference-column rounding discrepancies and 0.00% trace cells are also preserved.

Validation reports 29 diet-sum errors and 20 warnings. The maintained conversion mass-balance check reports **NOT BALANCED: 14 errors, 189 indeterminate, 31 warnings, 2 notes**. These are properties of the incomplete published reconstruction, not proof that the original authors' executable model was unbalanced. Generic checker headings and inferred explanatory BA values are diagnostic messages, not extracted parameters. The source deficits have not been repaired.

Round-trip verification checked 116,222 cells across eight standard tables and 13 companions: numeric values and missing masks match (maximum difference 3.16×10⁻¹⁷); literal exact equality is false because of numeric representation. ModelData admits 133 real groups plus its synthetic diet-import row. Constructor admission is separate from scientific readiness; unknown matrix entries remain NaN and the model is not ready for a defensible PPR calculation.

The official 49-group Whitehouse–Aydin 2020 Rpath descendant is extracted as a separate candidate under GOA-2020. It is not a replacement source for this model's unresolved cells. Neither candidate is selected or researcher-approved. No SPPR or annual PPR was calculated, and no map rebuild was performed.

## Evidence links

- [Source cell and prose inventory](extracted_tables/evidence/source_review.json)
- [Round-trip verification](extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json)
- [Constructor and transformation audit](extracted_tables/evidence/constructor_admission.json)
- [Published mass-balance check](extracted_tables/evidence/MASS_BALANCE.md)
- [Portable evidence index](extracted_tables/evidence/evidence_index.json)
- [Completeness assessment](extracted_tables/evidence/completeness.json)

The handoff is complete as a source-faithful partial extraction; the full numerical reconstruction remains incomplete. Model selection, taxonomy authority resolution, catch matching, diagnostics and annual readiness remain separate stages.
