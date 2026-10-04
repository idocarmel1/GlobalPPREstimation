# LME_027 selected-model integration, 2026-09-28

The selected Northwest Africa 1987 model remains selected and its canonical JSON is unchanged. The 2019 all-source, total-catch GE subtotal is **11,094,298.214141272 tC**, covering **4,282,782.005742099 of 5,771,015.257329413 wet tonnes (74.21193351209392%)**. There are 292 mapped catch labels out of 512 labels appearing in the historical catch table. This is a provisional, supported-catch subtotal, not a complete or scientifically validated LME estimate. Unmapped catch is omitted, not assigned a zero coefficient. Fixed 1987 coefficients applied across 1950–2019 catch do not reconstruct changing annual ecosystems.

## Source identity, extent and taxonomy

The selected source JSON and `papers/CAN-2009/27_118_Northwest_Africa_(1987).json` are semantically identical; their formatting hashes differ. The selected hash is `4d2152f4836dddcb32e90def39b4d1cf1b3399d168e803173fe2bd524f115bb2`. EcoBase accession 118 identifies Morissette's 1987, 27-group Northwest Africa model and the 2009 report. Its metadata area is 3,561,029 km²; its broader offshore extent is not the exact present LME boundary. No geographic coverage fraction or catch multiplier is inferred. The old metadata's 0.78 target ratio is not used as a catch allocation.

Recovered primary-author **2008 preliminary report**, hosted by Pew: https://www.pew.org/-/media/assets/2008/06/food_web_models_data_studying_interactions.pdf . Original PDF, extracted text, and Table 1 page images are retained in `papers/CAN-2009/`. Table 1 pp20–23 explicitly describes group composition; bold members are the representative species used for rates/diets, not the only members. Its source group order differs for whales. `source_group_crosswalk.csv` records identity-based alignment, including the source spelling variants Costal tunas, Coastal demersals, Mesopelagics predators and Bathydemersal predators. Source spelling is preserved in the evidence; runtime names remain unchanged.

**Version limitation:** this is predecessor composition, not verified final 2009 membership. The group architecture, model location, authors and lineage support provisional transfer, but this work does not establish exact final-version species completeness. All accepted matches therefore have medium confidence and explicit precursor evidence. `taxonomy.csv` includes all 27 biological/source groups; the workbook separately labels synthetic Import. The canonical source's null taxonomy fields were not rewritten.

Matches use exact labels, explicitly named genus-sp. containment where no competing group is listed, and the explicit Cephalopoda pool for catch classified as cephalopods. No catch-share or equal weights between groups are invented. Known overlapping coarse labels (Elasmobranchii, Gadiformes, Scombridae, Carangidae, Pristidae, Centrolophidae and Scomberomorus) remain unresolved. Named species are not moved solely because a broad ecological guild sounds appropriate. The preliminary table's conspicuous Centrolophidae-in-Sharks anomaly is retained in source evidence and excluded from resolved matching. The largest unresolved 2019 label is Marine fishes not identified (1,275,540.7 t); there is no supported group allocation.

## Recovery log

- Final 2009 FCRR 17(2) report identified at `https://epub.sub.uni-hamburg.de/epub/volltexte/2011/11876/pdf/17_2.pdf`; actual HTTPS and HTTP requests returned 403. Search indexing establishes its identity, not full table verification.
- The author CV at `https://search.asu.edu/profile/388442/cv` was readable and linked the report to Google Drive file `1i-Jw0zYrVopuP4n8HP980NB5WYeaYlux`. Public view returned 401; public download routes returned HTML rather than PDF. No authentication bypass attempted.
- The metadata's `http://publications.oceans.ubc.ca/node/3767` host no longer resolved on the HTTPS attempt. UBC report-page and candidate historical PDF routes returned HTML, not recovered originals. A Sea Around Us candidate path returned 403. None is represented as a recovered final report.
- Pew's linked 2008 original returned HTTP 200, 2,510,869 bytes, a valid 52-page PDF. Table pages 20, 22 and 23 were rendered and visually reviewed; page21 was transcribed from the same PDF text. This recovery supplies composition evidence with the limitation above.

## Canonical input, loader and exact runtime

`27_118_Northwest_Africa_(1987).json` is a byte-identical computational copy of the canonical JSON with the filename required by the existing loader's metadata parser. There is no invented eight-file extraction for this existing EcoBase JSON. Original fleet-level landings and discards are absent in this JSON schema; `export` is the inherited group catch used by the existing engine. Regional catch/landings/discards are preserved independently. `source_admission.json` retains accession metadata and raw diet sums. Every real consumer has known B, P/B, Q/B and EE; no biological biomass is filled with B=1.

The constructor exactly reproduces the retained export: `underdetermined=True`, `zero_catch=True`, `zero_biomass_accum=False`, `default_gs=True`, both weights 1, `normalize_DC=True`, `DC_tol=0.001`. This audits the previously selected numerical configuration; it does not introduce a new repair. The raw maximum consumer diet-sum deviation is 0.0004. Normalization changes 40 cells, maximum absolute cell change 0.00036014405762307966. Every changed loaded group field and diet cell appears in `transformation_ledger.json`. `canonical_to_loaded_fields.json` distinguishes raw literals, sentinels and initial loaded fields.

Notable existing loader conventions:

- Synthetic Import seq28 receives bookkeeping biomass 1, zero production and zero catch; it is not a measured biological group.
- Detritus EE is forced from 0 to 1, P/B from 0.5 to 941.288511731773, and Q/B from a missing sentinel to that same throughput ratio. These are engine throughput conventions, not observed rates.
- Known detritus accumulation **5934.798** is replaced with the derived closure residual **5934.458515326964**. It is not an observed accumulation estimate and does not establish source steady state.
- Producer Q/B 0 becomes P/B (138.189 and 107.36) under basal algebra. Known living biomass and rates are preserved apart from floating-point arithmetic; predation is recomputed from the normalized diet.
- Partial natural detritus routing for Sei/Brydes whales is treated as external export by the retained engine. No new routing or discarded-fish completion is added.

## Diagnostics and method scope

`DIRECT_DIAGNOSTICS.md` and `direct_reports.json` contain the full actual direct returns, separate from this interpretation. GE, TE and With Egestion all return **WARN**, model-input grade WARN, strict model balance false. GE divergence grade OK; no negative source columns; detritus gain 0.3694082945710039 and living spectral radius 0.16615874785448084. GE balance grade is OK while its strict Boolean is **false**, relative gap 0.00008344002855119328. Ten EE-zero consumers drive the input warning; TE also has near-singular/convergence warnings. Neither an overall WARN nor an OK component is relabeled as an overall pass.

Only GE coefficients are integrated into annual outputs; TE and With Egestion are retained as diagnostics. No global, broad exporter or Monte Carlo was run. All biological groups, including unfished groups, are checked for nonfinite/negative contributions. All GE scopes are joined by exact group identity, not positional array order, and agree with retained coefficients within floating-point tolerance.

`reproduce_direct.py` imports the retained three-file engine snapshot, reloads the persisted computational input twice, and asserts exact equality of the complete captured state, flows and three direct returns. `execution_evidence.json` retains engine hashes, settings and package identities. Full source-decomposed solutions are in `direct_solutions.json`.

## Workbook update and verification

`integrate.py` replays matching and GE integration using the current workbook reader/calculator. `LME_027_before_integration.xlsx` preserves original bytes. After recalculation, the original Classic PPR blocks and their ratio rows are restored; Catch and NPP, selection/rationale and unrelated diagnostic blocks are preserved. Generated hashes are recorded normally after the final result state; no stale-input check is bypassed. Full-region production eligibility remains false, while the scoped GE arithmetic is available with its warnings and partial-support note.

`integration_verification.json` records the exact result, coverage, hashes, highest unresolved catches, coefficient comparison and passing regional freshness validation. Run the two regional scripts in order from this project root to reproduce diagnostics and integration. `tools/run_region.py --region regions/LME_027 --stage validate` validates the final workbook. Shared tools, Project.xlsx, the map and other regions were not modified by this regional integration.
