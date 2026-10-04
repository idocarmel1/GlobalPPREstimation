# Source admission and limitations

Just a FAD? Ecosystem impacts of tuna purse-seine fishing associated with fish aggregating devices in the western Pacific Warm Pool Province

The main PDF is complete and its identity verified. This is a source review, not a runnable Ecopath model. No SPPR result is claimed.

- Final balanced diet matrix (Appendix S1 Table S3, supplementary PDF pages 29–30) not coordinate-verifiable: direct publisher and author-upload downloads returned HTTP 403; flattened web text loses blank-cell positions.
- Fleet landings/discards (Table S4, supplementary PDF page 31) not column-verifiable; header scaling 1e-6 t/km² must be preserved.
- Unassimilated fractions, numerical detritus fate/discard routing and imports remain unverified. Qualitative discard pathway is not a numeric allocation.
- Full functional-group membership in supplementary Table S1 remains to be verified.

All three requested diagnostics (GE, TE, With Egestion) are **not run**, not FAIL. No global diagnostic was run. No file posing as direct diagnostic output was created.

Unknown inputs remain unknown. No diet normalization, pooling, migration repair, borrowed matrix, default unassimilated fraction or invented routing has been applied. The eight-file bundle, canonical database JSON and reconstruction validation await the listed source inputs.

Table 1 (printed pp98–99; PDF pp5–6) supplies 46 exact labels and B/PB/QB/EE/PQ/TL. PDF page/cell coordinates and printed decimal precision are retained. Source dashes become null, not zero. B is t wet weight/km²; PB and QB are annual rates. EE and PQ are dimensionless despite the table’s year label. Bold values are Ecopath estimates, not direct field measurements.

The web-readable author supplement distinguishes initial Table S2 from final balanced Table S3. Its page4 explicitly states net migration=0 and biomass accumulation=0. These prose facts are recorded separately from the locally archived parameter table. Catch Table S4 uses 1e-6 t/km². Main-paper ocean area is 11,543,000km², while some supplement derivations use 12,086,900km²; no published density was rescaled. Main p99 describes multistanza reconciliation and a distinct suspended fishery-discard pool but does not provide a numerical allocation.

Supplement source: https://www.researchgate.net/profile/Shane-Griffiths/publication/325700136_Griffiths_FOG-17-1431_Early_View_Supp_Info/data/5b9feef0299bf13e6038a3f9/Warm-Pool-Ecopath-FAD-Griffiths-et-al-2018-APPENDICES.pdf

Recovery requirement: obtain the original AppendixS1-S4 DOCX/PDF or native model, inspect final Table S3 and Table S4 by coordinates, verify missing routing/GS/import inputs and membership, then finish imports, canonical JSON, reconstruction and the exact three diagnostic calls.
