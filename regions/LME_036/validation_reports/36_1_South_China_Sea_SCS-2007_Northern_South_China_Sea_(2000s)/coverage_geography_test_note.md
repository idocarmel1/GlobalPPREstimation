# Coverage and geographic evidence check

Created during this template test on 29 September 2026. This is a new read-only arithmetic/evidence note, not a historical report, model approval, new extraction or SPPR calculation.

## Identity and reference coverage

Selected model: `36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)`. [Regional workbook](../../LME_036.xlsx) Overview supplies the exact selection and rationale. Source workbook SHA-256: `827c0a288dfaa437f4ff30c9351aa52356c02cc1cfe9aadc2475f519eab6ce83`.

Reference: year 2019; `catch` = landings plus discards; `new_GE`; scope `all` = every basal-source contribution including detritus and import; default unidentified treatment `method` = use the method's saved taxon coefficient. All catch records in the region are included; no fleet, sector or source subset was selected. The Overview's landings setting controls an inspected view and is not this reference basis.

Numerator: sum 2019 tonnes for taxa with finite saved all-source GE taxon SPPR = 11,064,125.639450839 t. Denominator: sum all 374 catch rows = 11,101,666.087778976 t. Ratio = **99.66184852%**. Values agree with PPR / Annual covered_catch and catch within 0.000001 t. No missing coefficient is treated as zero. A measured zero catch contributes zero; unsupported coefficients remain unavailable.

Recorded stage assumptions: 135 unique taxa, 270 candidate rows; supported catch relying on these assumptions = 2,966,894.686341749 t / 11,101,666.087778976 t = **26.72476962% of total catch** (26.81544645% of covered catch). This reproduces Diagnostics / Size allocation impact. Existing weights were documented with zero numerical coverage gain. This is the recorded stage-allocation share; it excludes additional low-confidence taxonomic/guild composites and is not the total share of all scientific assumptions.

TE (`new_TE_EEfix` and `new_TE_noEEfix`) has exactly the same supported taxa and coverage; no second, different TE coverage is claimed. Native treatment retains mapped unidentified labels. Results remain provisional.

Unsupported catch = 37,540.448328137 t (0.33815148%). Twelve labels are unresolved in the retained mapping; some contribute zero in 2019:

| Taxon | 2019 total catch t |
|---|---:|
| Ruvettus pretiosus | 34,712.023932 |
| Xiphias gladius | 1,182.732930 |
| Istiophorus platypterus | 601.551547 |
| Istiophoridae | 512.237124 |
| Istiophorus | 390.631500 |
| Makaira mazara | 106.538087 |
| Istiompax indica | 27.867201 |
| Makaira | 4.072234 |
| Kajikia audax | 1.664924 |
| Lampris guttatus | 1.128850 |
| Lepidocybium flavobrunneum | 0.000000 |
| Tetrapturus angustirostris | 0.000000 |

The older mapping notes' 99.7884% uses the entire 1950–2019 series, not this reference year. [Copied mapping notes](mapping/notes.md), [adopted-allocation results](allocation/RESULTS.md), [saved field snapshot](saved_evidence_snapshot.json), [arithmetic record](qa/coverage_arithmetic.json).

## Geographic fit

R = LME_036 South China Sea; S = the 2000s northern shelf model domain. A = 100 × area(R ∩ S) / area(R); B = 100 × area(R ∩ S) / area(S).

**A: Not determined. B: Not determined.** R has an existing Sea Around Us EPSG:4326 GeoJSON boundary. S has no verified digital study polygon in current project records. Cheung (2007), Figure 6.1, printed p.170 / PDF p.185, describes the area from the coast to a broken line, mainly the Chinese EEZ shelf shallower than 200 m. The figure does not supply georeferenced vertices or enough cartographic control to establish a compatible polygon. Broad coordinate bounds do not supply that footprint. The source metadata explicitly says the legacy approximate footprint was removed pending geographic verification. No area or overlap percentage was manufactured; no bounding rectangle or map marker was used.

Required missing input is a verified model-domain polygon or defensible georeferencing and digitization of the study boundary, including the shelf/EEZ and Gulf of Tonkin treatment. A compatible equal-area or geodesic area method would then be needed. No overlap calculation was performed in this test.

[Boundary copy](geography/LMEs.geojson); [article metadata](source/article_metadata.json); [article PDF](source/Cheung_2007.pdf#page=185). The generated boundary view draws original GeoJSON vertices in a longitude/latitude display with cosine adjustment at 15°N; it is illustrative and is not an area calculation. Natural Earth 1:50m land is display context only. [Basemap provenance](geography/basemap_provenance.json).

## Limits and identity checks

Selected model SHA-256 matches Overview results_model_sha256: `9a199f06809165104ed59b9fb53cb48e6bb9cd0439be081dc518da26a681cfc7`. Current calculation-input fingerprint matches Overview. Thesis PDF and raw catch ZIP match their retained source hashes. All 38 canonical group IDs/names match the saved Groups records, with an additional synthetic import group 39. These checks do not independently validate every extraction cell or reproduce the historical solver environment.

[Saved-state comparison](canonical_saved_state_comparison.json) was created during this test. It records canonical unknown GS/BA/migration/import markers versus numeric runtime values, detritus EE 0.005 versus saved loaded EE 1, and synthetic import in the snapshot. The source reconstruction report is for the separately retained `36_South_China_Sea...` candidate; its source findings are useful context, but its INDETERMINATE verdict is not substituted for selected-model GE/TE statuses.

No full selected-model direct-diagnostic Markdown report or complete historical loader transformation ledger was located. Use [saved SPPR workbook](diagnostics/sppr_source.xlsx), [GE/TE saved-field transcription](saved_evidence_snapshot.json) and [retained verification](mapping/verification.json). The [historical export report](diagnostics/historical_sppr_export_report.txt) supplies matching warning text, but is an earlier run (75 Monte Carlo draws versus 100 in current notes); its configuration and coefficients are not silently adopted as a new run. The current flattened diagnostic record does not preserve the full original warnings/return object or executed-engine hash.

Template test scope: document evidence and saved calculations; no scientific source, workbook, mapping, selection, method status or map was edited; no extraction, SPPR solver or Monte Carlo was run. Manual research decisions remain for the researcher.
