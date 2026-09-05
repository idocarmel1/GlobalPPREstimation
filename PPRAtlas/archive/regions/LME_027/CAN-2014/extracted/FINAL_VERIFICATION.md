# Final verification

2026-09-04: three model directories verified; all eight import files plus database JSON, reconstructed workbook, provenance/report and validation artifacts present. All CSVs have CRLF, UTF-8 without BOM and no quotes. Every reconstructed workbook matches all eight source tables cell-for-cell. Database diet values preserve published percentages after exact /100 conversion with no normalization; all unreported habitat/GS/diet components remain -9999. Group classes are 47 consumers, 3 producers and 1 detritus. All 16 source files match pre-extraction hashes; the 13 publication downloads match recorded SHA-256 values. No source file or installed skill source was edited.

Known failures are reported rather than repaired: source diet totals 0.980331 and 2.2006; incomplete variant diets; missing multi-stanza P/B, habitat, GS, discards and detritus routing. All models are partial; final guarded mass-balance verdict is NOT BALANCED.

Integration metadata audit: each final database JSON includes top-level metadata exactly matching model.json and extraction_metadata, including model_number strings 27_1, 27_2, 27_3. Ecological values and all eight source-table payloads were verified unchanged. Report lower-bound statements concern missing consumer diet entries only, not omitted unknown BA.
