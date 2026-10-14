# Irish Sea Ecopath published-table extraction (1973)

Source: ICES (2019), Working Group on Multispecies Assessment Methods (WGSAM), ICES Scientific Reports 1:91, DOI 10.17895/ices.pub.5758. Annex 3 printed37–109/PDF44–116 and Section2 printed9–14/PDF16–21. Main PDF SHA256: 0e8ab72d65a172d5891d22b576a36f9644154e6844644bc458db9409c3d20356.

41 groups: 37 consumers, 2 primary producers and 2 detritus pools. Eight actual fleet identities are retained in Published_fleets.csv. Import catch tables contain one explicitly named aggregate reporting column, Reported group total. This is not a ninth fleet or a recovered fleet allocation.

## Source tables

Table0.1 printed38/PDF45: group | TL | B | PB | QB | PQ | EE | L | D maps to exact group identity, trophic level, biomass, annual production/consumption rates, production/consumption, ecotrophic efficiency and landings/discards. Parentheses denote model-estimated values and are retained in the companion, with parameter input flags marked accordingly. Biomass and catches have t/km2 basis; annual rates are stated on printed39/PDF46. The area is 58,000km2. No mass/area conversion was applied. PB/QB for Atlantic cod2+ is 0.82/3.12 = 0.2628205, consistent with rounded published PQ0.26. All 41 ordered source names and values were matched.

Table0.2 printed39–53/PDF46–60: group | parameter | value | source | comment. The 232 parameter-origin rows are retained separately, with coordinate source/comments and original page locators. B first rows can precede the numbered group label across a page (Whiting2+ B0.56 on PDF49 with group label on PDF50); this continuation was explicitly checked. Table0.1 defines this candidate's standard fields; Table0.2 is competing published evidence, not a numerical repair source. Differences exceed rounding for some fields: juvenile cod PQ0.13 vs0.263; juvenile haddock PQ0.17 vs0.128; Epifauna PB1.01 vs1.7; gelatinous zooplankton EE0.69 vs0.938; Discards EE0.54 vs0.127. Every stated table value is retained; accepted native configuration is unavailable, so their final equivalence is unresolved.

Table0.4 printed57/PDF64 and continuation captions printed1.4 printed58–61/PDF65–68: prey rows1–41, consumer column blocks1–8,9–16,17–24,25–32,33–37. Orientation is prey rows/consumer columns. Coordinates anchor on each page's Predator/Prey header and first body dash positions; pdfgrid raw output uses merge_gap0.4. Source cell bounding boxes accompany all 1517 cells. Every row was matched by exact source name and count. The dash is preserved as a blank import cell and an explicit published no-link dash in companions; it is not replaced by a numeric zero. Published numeric 0.000 remains numeric zero. Wrapped cell prey37/consumer8 on PDF64 is 0.00004; wrapped European sprat discard on PDF45 is 0.000001. Both were visually checked.

Table0.3 printed54/PDF61 gives stock BA/B0 for cod, whiting, haddock and plaice alongside K, recruitment power, transition month and Wmat/Winf. These are stock-level stanza values; no individual stanza BA0 was fabricated. Eight group-level BA fields therefore remain blank along with all other group BA fields. Published_stanzas.csv retains all values. Native stanza equations are not reconstructed.

Table0.5 printed62/PDF69 gives the eight fleet identities and gear categories. Published group totals are Table0.1. Fleet proportions are not tabulated. Final post-review plaice redistribution is illustrated in Figure0.22 printed97/PDF104 without numeric percentages. No pie-chart percentages or fleet values were guessed. Pre/post vulnerabilities Tables0.13–0.14 printed98/PDF105 are retained with >100 and dash literals, separately from baseline Ecopath inputs. Additional pedigree, fitting, reference-point and calibration source fields are retained as coordinate line/word evidence companions, without calculation use.

## Biomass accumulation and prose

The entire Annex3 and Section2 were checked for accumulation, migration, assimilation, unassimilated consumption, habitat and routing. Section2 printed10/PDF17 discusses a possible negative cod BA in the critique but provides no adopted numeric group BA. Table0.3's stock BA/B0 remains a stock companion. No explicit numeric GS, habitat fraction, diet import, detritus import, migration or detritus routing was located in the ICES annex. Their fields remain unknown. EwE importer default GS0.2 and BA0 do not become source values. No convention-derived numerical values were applied.

Printed62/PDF69 describes the historical catch allocation using STECF proportions and marine mammal bycatch as discards. Printed96–97/PDF103–104 and Section2 printed11–12/PDF18–19 describe the post-review plaice correction. The source summaries and final fleet correction cannot be proven equivalent without the accepted database. The source's key-run approval printed13/PDF20 is the authors' review history; it does not confer project researcher approval on this extraction.

## Source version and geography

The final ICES report is the numerical authority. The pre-October technical report and Bentley2021 are contextual sources and supplied no borrowed model values. EcoBase448 was not reused. Baseline1973 is distinct from the Ecosim hindcast1973–2016 and the report publication2019. Irish Sea is a subregion within Celtic-Biscay Shelf LME024; whole-LME overlap was not measured.

## Deliberate blanks and version limits

Group habitat fractions, Z, other mortality, GS, group BA, import/migration/routing and prices are unknown. Finfish/invertebrate diets have source dashes; diet import is unreported. Actual catch-by-fleet values are unavailable; source group totals are retained in an explicitly labelled aggregate reporting column. Detritus catch dashes remain unknown. Taxon descriptions are null; no taxonomy/mapping stage was requested. This is an exact extraction of named published tables with version gaps, not a claim of runnable accepted native equivalence. No ecological reconstruction, normalization, solving, SPPR, Ecosim, selection or publication was performed.

## Validation

Structural import validation: 0 errors,43 warnings. Warnings concern blank GS, blank BA and41 unreported fate rows. All eight imports are present. Source to imports to canonical JSON checks matched group names/order, literal scalars,1517 diet cells and missing masks, catch components and protected unknowns. Reconstructed standard/companion workbook numeric/missing-mask check passed; its result is SOURCE_FIDELITY_CHECK.json. The workbook was temporary and is not another retained model representation.

Known prey-only diet subtotals range from 0.999 to 1.0014. They remain raw; import and dash cells preserve their source masks, so complete numerical diet-plus-import sums are unavailable. No normalization was applied.

## Mass balance

The import checker returned1 error,10 warnings,38 notes. Its Gurnards indicative recomputed EE1.010 exceeds1 at the retained source precision; Table0.1 prints B0.34/PB(1.40)/QB5.61/EE(1.00). These cells and the source diet were checked against rendered PDF45,64–68. The scalar check treats missing terms as its software conventions; it is not a native multistanza reconstruction. The source-preserving converter budget report instead returns0 errors,82 indeterminate outcomes,5 warnings,2 notes, because unknown BA, GS, import/dash cells and detritus catches prevent complete-source closure. Neither result proves a balanced or runnable recovered model. BA values suggested by the checker were not adopted. See import_massbalance.txt and MASS_BALANCE.md.
