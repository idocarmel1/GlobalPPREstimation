# ICES_WGSAM2019_Irish_Sea_1973

## Source identity

ICES(2019), WGSAM, ICES Scientific Reports1:91, DOI10.17895/ices.pub.5758. The [main report](../../sources/ICES_WGSAM_2019.pdf) Annex3 supplies the extraction; Section2 supplies final review history. The accepted native EwE database is unavailable. Pre-October technical report and Bentley2021 remain contextual; EcoBase448 supplied no values. ICES-WGSAM2019 in Metadata.xlsx is a package identifier, not an EcoBase accession.

## Modeled period and area

Ecopath baseline1973; Ecosim hindcast1973–2016. Irish Sea,58,000km2, ICESVIIa/7.a; subregion within Celtic-Biscay Shelf LME024. Overlap has not been measured.

## Departures from the publication

The standard fields preserve Table0.1 printed38/PDF45 literally, with parenthetical model-estimated roles retained; no normalization, balance repair or guessed defaults were applied. The diet is the five printed blocks of Table0.4/1.4 printed57–61/PDF64–68, including numerical zero and source dash masks. Table0.2's more precise and competing values are retained in companions rather than silently replacing summary values. Material unresolved conflicts include Epifauna PB1.01 vs1.7, gelatinous zooplankton EE0.69 vs0.938 and Discards EE0.54 vs0.127; complete comparison is in Published_parameter_origins.csv.

Published landings/discards are preserved through one explicitly labelled Reported group total reporting column. This column is an aggregate representation, not an actual fleet; all eight actual fleet identities and unknown allocations are separate companions. Post-review plaice fleet redistribution lacks printed numeric fractions. It remains an explicit configuration gap. Post-review vulnerabilities are retained verbatim as companions, including inequalities.

Stock-level BA/B0 in Table0.3 is retained with stanza fields; it is not assumed to apply independently to adult/juvenile groups. Group BA, GS, habitat fractions, import, migration and fate remain unknown. The converter's unknown sentinel is -9999. Taxon descriptions remain null. Eight imports and canonical JSON are source evidence; native multistanza equations and the accepted final dynamic configuration are not reproduced. Import mass-balance check has1 error10 warnings; source-preserving budget check has82 indeterminate outcomes. No balance, runnable native equivalence, scientific readiness or researcher approval is claimed.

## Evidence links

[Extraction report](extracted_tables/evidence/REPORT.md), [source-cell evidence](extracted_tables/companions/Source_cells.csv), [competing parameter-origin values](extracted_tables/companions/Published_parameter_origins.csv), [fidelity checks](extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json), [evidence inventory](extracted_tables/evidence/evidence_index.json), [model profile](extracted_tables/MODEL_PROFILE.md).

This extraction does not change regional selections, workbooks, coefficients, Project.xlsx or maps. Source key-run approval does not register project researcher approval.
