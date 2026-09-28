# Pacific paper comparison — source and applicability review

Both papers are archived under **EEZ_941 (Kiribati, Gilbert Islands)** because each covers that target region more completely than HS_071. This registers candidates, not a model selection. Neither candidate currently supports a valid full extraction or the requested SPPR diagnostic calls with verified inputs. Griffiths2019 is closer to extractable because its main parameter table is available and the missing final diet/catch appendix is identified.

| Evidence | Griffiths et al.2019 | Allain et al.2021 |
|---|---|---|
| Exact publication | DOI10.1111/fog.12389; 19-page main paper | SC17-EB-IP-11; complete 4-page report |
| Baseline | 2005 | 2013 |
| Groups | 46 total: 44 living, detritus, fishery discards | 65 total: 63 living, detritus, fishery discards |
| Fisheries | Four fleets: longline, associated/unassociated purse seine, pole-and-line | Five, including other fisheries |
| Explicit geographic limits | 140–180E;15S–10N | 140E–150W;20S–20N |
| HS_071 target covered | 29.09639% | 74.48550% |
| EEZ_941 target covered | 99.71577% | 100.00000% |
| HS_071 intersection | 1,510,912km² | 3,867,870km² |
| EEZ_941 intersection | 1,047,050km² | 1,050,034km² |
| Local numerical evidence | Table1: all46 labels and B/PB/QB/EE/PQ/TL; 276 page/cell records | No full numbered group or numerical input tables |
| Immediate source barrier | Supplement final TableS3 diets and TableS4 catches cannot be obtained with coordinates; additional GS/routing/imports remain unverified | Final65-group native model or full numerical tables missing |
| GE / TE / With Egestion | Not run / Not run / Not run | Not run / Not run / Not run |

Target coverage is intersection divided by the target region's stored polygon area. Larger absolute intersection with HS_071 does not reverse the target-coverage comparison. The rectangles are explicit study limits, not bounds inferred from a map marker. Calculations use WGS84 geodesic areas with 0.05-degree densification and a 0.01-degree refinement; the area changes are below0.00001%. Scripts and source geometry hashes are retained in SPATIAL_OVERLAP.json and ALLAIN2021_SPATIAL_OVERLAP.json. No land mask was silently applied.

Both remain broad oceanic pelagic proxies spanning multiple jurisdictions. The Griffiths paper reports 11,543,000km² of ocean within the domain; only9.07086% of that area intersects EEZ_941. Allain's gross rectangle is33,787,380km² and only3.10777% lies in EEZ_941. This broad domain and the absence of reef/coastal food-web detail limit inference for all EEZ fisheries. The EcoSEA2020 development report's stated38,000,040km² is not consistent with the 2021 explicit rectangle; it was not used as a denominator or to alter the bounds.

For **HS_071**, Allain2021 is spatially more relevant than Griffiths2019 by verified target coverage, and its baseline is newer. It still excludes about25.5% of HS_071 and cannot be selected on diagnostic health because that health is unknown. For **EEZ_941**, both largely cover the target, while Griffiths2019 has a clearly identified route to recover the missing published input tables. Source recoverability and geographic applicability are separate considerations; neither establishes scientific health.

## Extraction and diagnostic limits

Griffiths source-only artifacts are in `regions/EEZ_941/models/941_201901_Warm_Pool_(2005)/source_review/`. Table1 values retain exact printed precision, coordinates, source dashes, group labels and bold estimated-value provenance. Basic_input_PARTIAL.csv is explicitly partial; TL_source.xlsx contains published trophic levels. Taxonomy_unverified.xlsx preserves labels but leaves taxon_descr blank pending TableS1 membership verification. SOURCE_ONLY_PARTIAL.json is not canonical database JSON. Nothing imports a missing matrix as zeros.

The final Griffiths diet is **TableS3**, not the initial TableS2. The web parser loses blank-cell locations, so its flattened numeric text cannot safely assign prey to predator columns. Catch TableS4 uses1e-6 t/km² and also requires column verification. Main paper p99's qualitative fishery-discard pathway does not specify a numerical detritus fate matrix. Appendix prose states net migration and biomass accumulation equal zero; those source facts are retained separately. No assumptions or model repairs were used to manufacture diagnostics.

Allain2021 describes a substantial update of the2019 model, with a different baseline, domain, group structure and fisheries. Its antecedent sources cannot supply its missing final parameters by substitution. The downloaded EcoSEA2020 development report is context only.

The complete eight import files, canonical database JSON, full taxonomy, reconstruction and source mass-balance validation remain blocked. The requested direct `PPRCalculator.diagnose_sppr(short=False, flat=False)` returns do not exist for these incomplete models. No global diagnostic was run. **Not run is not FAIL.** Explicit machine-readable admission status and recovery requirements accompany each candidate. No custom narrative has been presented as direct SPPR output.

## Existing WCP2007 and later regional selection

The existing WCP2007 extraction is a distinct31-group mixed-period model. Its prior GE, TE and With Egestion diagnostics FAIL; the existing `balance_investigation/BALANCE_CAUSE_REPORT.md` attributes PP-budget gaps to juvenile yellowfin/bigeye production residuals with an unresolved native catch/stanza discrepancy. This review references that existing work; it does not rerun, repair or replace it. WCP2007 covers57.57808% of HS_071 and99.71577% of EEZ_941 under the separately stored spatial calculation.

The user specifically notes **EEZ_598 (Papua New Guinea) is also linked to WCP-2007 (Allain et al.2007)**. Preserve that shared-paper relationship when later choosing models for **HS_071, EEZ_941 and EEZ_598 together**. No EEZ_598 overlap or new extraction was requested or performed here. Each region requires its own applicability assessment; the shared paper does not establish equal suitability.

No model was selected, no regional workbook was changed, and no annual PPR was published. REGISTRATION_PROPOSAL.json provides the candidate metadata for the parent task's controlled central workbook integration.

## Primary sources and next evidence

- [Griffiths2019 publisher record](https://doi.org/10.1111/fog.12389): obtain AppendixS1–S4 DOCX/PDF or the native2005 model, then verify final diets, catch, routing, GS/imports and membership before completing extraction.
- [Allain2021 official record](https://meetings.wcpfc.int/node/12403): obtain the final65-group2013 native model or complete input tables. The retrieved leaflet alone cannot reconstruct them.
- [EcoSEA2020 development report](https://meetings.wcpfc.int/node/11742): context for the update, not final numerical evidence.

SOURCE_SEARCH_AUDIT.md records retrieval outcomes and the sources checked. No author messages were sent.
