# Gulf of Thailand (1973)

**Source:** Vibunpant, S., N. Khongchai, J. Seng-eid, M. Eiamsa-ard and M. Supongpan. 2003. Trophic model of the coastal fisheries ecosystem in the Gulf of Thailand. In Assessment, Management and Future Directions for Coastal Fisheries in Asian Countries, WorldFish Center Conference Proceedings 67, pp.365-386.

**LME:** 35 Gulf of Thailand. **Model number:** 35_1 (assigned atlas extraction identifier).
**Groups:** 40 (37 consumers, 2 primary producers, 1 detritus). **Fleets:** Otter board trawl; Pair trawl; Beam trawl; Pushnet; Purse seine; Other gear.
**Extracted:** 2026-09-04. **Status:** partial, source transcription complete; not ready for a defensible complete EwE reconstruction. **Mass-balance verdict:** NOT BALANCED for the source-preserving reconstruction.

## Source inventory and model eligibility

README.md and metadata.json were read first. The only published source supplied is content-d78aa261.pdf, 22 pages (printed pp.365-386). SHA-256: d78aa261b62cc6592cbab508d0aade9554851ffdacd47eee39e34b1950c8b33c. The article folder also contains README.md, metadata.json and footprint.geojson; these are catalog/spatial context, not author model inputs. No supplement, native EwE file, spreadsheet, prior extraction or prior calculation is supplied. Sources were not changed.

One static 1973 model is independently parameterized in Tables 1-3. The 1973-1993 time series, 1993 fishery results, 1993-2000 management scenarios, optimization strategies, and 1998 aspect-ratio measurements are not separately parameterized static Ecopath models. They were reviewed and no extra model was invented.

## Source tables

### Table 1, printed pp.368-369 (PDF pp.4-5): group list and basic input

Columns: Ecological group | Biomass (t/km²) | P/B (year⁻¹) | Q/B (year⁻¹) | EE | P/Q | Biom.acc. (t/km²/year). Mapped to name, biomass, pb, qb, ee, pq, and absolute ba. No unit conversion. The 13 rows on p.368 plus 27 continued rows on p.369 establish all 40 groups; Table 3 supplies numbering in the same order. Group 28 Seaweeds and group 39 Phytoplankton are producers; group 40 is Detritus. Group 20's comma is removed (Crab, Lobster → Crab Lobster) solely for the required unquoted CSV format. Table 1's Lutianidae spelling is retained and explicitly matched to Lutjanidae in Tables 2-3. Ponyfishes is matched to Pony fishes; capitalization differences for medium demersal groups are immaterial.

Caption states parenthesized values are estimated by Ecopath to fit mass-balance constraints. All 43 parenthesized values are extracted, with cell-level provenance in source_cells.json. Estimated group lists: {'biomass': ['1', '5', '6', '8', '11', '13', '19', '20', '22', '25', '29', '30', '32', '35', '36', '37', '38'], 'pb': ['2', '3', '4'], 'qb': ['2', '3', '4'], 'ee': ['7', '9', '10', '12', '14', '15', '16', '17', '18', '21', '23', '24', '26', '27', '28', '31', '33', '34', '39', '40']}. Parentheses are provenance notation, not negative signs. The mapping check is Scomberomorus: 0.07 / 0.35 = P/Q 0.20. Carangidae and Pomfret are consistent within printed precision. Q/B is dashed in 33 consumers; stated P/Q is retained rather than manufacturing Q/B source cells.

Coordinates were read with the bundled pdfgrid.py (Poppler backend); Table 1 lines 28-40 on PDF p.4 and lines 4-30 on p.5. All table rows were visually verified on 220-dpi renders. Detritus B is printed 10 000, extracted as 10000, not 10.000 or 10.0.

### Table 2, printed p.371 (PDF p.7): catch by fleet

Columns: ecological group, six fleets, Total. Each of 31 printed catch rows is matched by name to Table 1. Catch is already t/km²/year. Every printed zero is retained; nine omitted group rows remain unknown. All eight deliverable group tables retain the complete 40-group spine. Catch goes to Landings because no discard split is stated; Discards remains blank. Fleet Other gear is defined in the caption as shrimp gillnet, fish gillnet, swimming crab gillnet and trap.

The printed fleet totals 0.991, 0.543, 0.023, 0.072, 0.158, 0.646 sum to 2.433 and match the reconstructed individual cells exactly. All rows and fleet headers were visually checked at 220 dpi. Table 4 (p.374) gives juvenile fractions of trashfish for Otter board trawl, Pair trawl and Pushnet. These are not applied again to Table 2 because juvenile catches already have their own explicit rows; a second split would double count or overwrite the source.

### Table 3, printed pp.372-373 (PDF pp.8-9): diet

Prey rows 1-23 and continued 24-40; same 31 predator columns on both pages: 1-25 and 29-34. Predator numbering is anchored to the numbered header, never inferred from dense body values. pdfgrid merge_gap=0.4; header lines 5 and 2 after a clockwise coordinate transform. The installed rotate_pdf.py required unavailable PyMuPDF; no package was installed. Original Poppler word boxes were rotated in memory (x′=792-y, y′=x), saved with originals in work, and reconstructed using the bundled pdfgrid. Separate rendered page images were turned upright solely as working views. All flagged columns were compared to the 300-dpi pages.

The paper really omits columns 26,27,35,36,37,38. These six consumers receive blank output columns to show missing diets. Printed columns 6,12,22,32 contain only dashes/zeros and have no positive diet. A blank/dash in an otherwise populated diet is preserved as absent feeding; an entirely absent/empty diet is unresolved, not a producer. The source prints a literal -0 at prey 11 / predator 29; it is retained exactly and represents numeric zero. Source blank at prey 31 / predator 31 remains blank.

Nonzero-column sums range 0.90-2.00. Fifteen nonzero columns exceed ±0.01 from one: {'1': '1.1', '2': '1.02', '3': '1.1', '7': '1.2', '8': '1.02', '9': '1.1', '10': '1.2', '11': '1.1', '15': '1.1', '17': '1.2', '18': '0.9', '20': '2', '21': '1.2', '23': '1.2', '31': '1.2'}. Coastal tuna sums 0.99 (at tolerance), also retained. Crab Lobster has both Benthos=1 and Detritus=1; Rastrelliger has Zooplankton=0.9, Juvenile small pelagics=0.1, Phytoplankton=0.1. These are visible source problems, not rounding to be repaired. No normalization was applied to final outputs.

### Figure 2 and other material

Figure 2 (p.377/PDF p.13) shows boxes against a trophic-level axis, not numeric per-group TL. Box heights vary with biomass and no unique point for digitizing TL is specified. TL.xlsx therefore remains blank for all 40 groups; no spurious precision is assigned from a schematic. Figure 2's Lutianidae B=0.015 differs from Table 1's 0.016; Table 1 is retained as the primary parameter table. Table 8 gives aggregate biomass per integer trophic level, not group TL. Figures 3-4 are mixed impacts and Ecosim fits. Appendix A (p.386) contains 1998 caudal-fin/aspect-ratio inputs, not another model.

## Biomass accumulation

Absolute BA is explicitly tabulated for every group in Table 1; 14 entries are nonzero and 26 are stated zero. Nonzero entries (group: value): 2: -0.003, 3: -0.007, 4: 0.001, 7: -0.001, 9: 0.012, 10: -0.004, 13: 0.086, 14: -0.004, 15: -0.006, 16: -0.01, 17: -0.005, 18: -0.1, 21: -0.045, 24: -0.042. Positive Sillago 0.086 and Saurida 0.012; negative values including Cephalopod -0.1 and Rays -0.01 were visually checked. BA rate stays blank in the import file; the database alone derives BA/B and the workbook labels that derived form. The table's zeros are paper-stated, even though they coincide with the EwE default. General mass balance does not imply BA=0, and the nonzero terms disprove a blanket steady-state assumption. Whole-chapter accumulation search and Figure 4 were reviewed; no figure-derived BA replaces Table 1.

## Values from prose

No numerical import parameter was added from prose. The model survey/swept-area calculation uses A=101384 km² (p.367), whereas p.366 reports the whole Gulf seabed area of 304000 km². Neither is a reported habitat-area fraction; neither was used to rescale already normalized table biomass/catch. Mean habitat temperature is 29°C; primary-production carbon-to-wet-weight factor 7.47 is described on p.374, but Table 1 already gives the model parameters, so it was not applied again. The printed conversion expression on p.374 was not used to create new rates. Trashfish is defined in the p.366 footnote and includes low-value and juvenile/undersized fish, not discarded fish.

## Conventions applied

- Only format-level conventions: full group-row spine, comma removal from group 20, thousands-space removal from detritus biomass, and catch placed in Landings without inventing a discard split.
- The bundled writer emits Import=0 and (1 - Sum)=0 as required by its export format even though no diet import is stated. These are explicit file-format conventions, not author values. Final DB diet_imp stays -9999, and the round-trip workbook leaves Import blank to preserve source silence.
- No GS, habitat-area fraction, detritus fate, missing catch, missing diet or missing TL default is filled. No zooplankton convention is applied to the pooled Zooplankton group. No diet normalization.

## Deliberate blanks

The complete 22-page source bundle, all captions/footnotes, methods, results, figures and Appendix A were searched, then targeted searches revisited the groups/fields still missing. Assimilation/GS and detritus routing are not stated. GS remains blank for all groups (structurally inapplicable for producers/detritus); EwE may supply GS=0.2 for consumers at import, but this is not the author's input. Habitat area is unreported (software default 1); detritus import/export/fate unreported (unassigned fate can be exported by EwE). Discards are not separated (software default 0). No catch rows are supplied for groups 26,27,28,31,32,33,34,39,40 (software default 0). No migration, other mortality, total mortality or numerical group TL is reported. Q/B dashes, and P/Q dashes for Mammals/producers/detritus, are retained. The final database uses -9999 for unknowns.

## Unresolved and flagged

The published diet has missing consumers, zero-only columns and substantial column-sum contradictions. Reported catches also conflict: Table 2 total 2.433 for 1973 vs Ecosim fitted 1973 Table 10 total 1.454 (p.381); p.379 explicitly identifies the latter as time-series simulation results. Table 10 has no group allocation. Tables 1-3 are extracted together; no attempt is made to infer a revised group-by-fleet catch set from the totals. Table 4 prose says purse seines but the actual third header says Pushnet; header retained as contextual evidence and no numerical transformation depends on it.

The stock converter silently normalizes diets, discards stated P/Q, classifies blank-Q/B/empty-diet consumers as producers, and substitutes several zero/one defaults. Its initial outputs are archived only in work/bundled_*. The local adapt_database.py restores exact CSV diet values including zeros, carries P/Q in supported ge/ge_input, establishes pp from the group list, restores unknown sentinels, and rebuilds the final workbook. The log's final adapter entry supersedes earlier raw messages. source_parameters.json preserves six-fleet catch detail that the core database schema otherwise collapses into export totals. This is documented compatibility work, not a source correction.

## Validation

Bundled validate.py: 15 errors (the confirmed source diet sums) and 52 warnings (40 unknown detritus fates; 10 empty diets; one GS summary; one TL summary). CSV structures, numbering, source row counts, numeric precision, CRLF and lack of quotes are valid. All 40 detritus-fate rows are blank, not normalized. The eight required files, model.json, database JSON and reconstructed workbook exist.

Bundled massbalance_check.py: 1 error, 44 warnings, 6 notes. It ignores usable source P/Q when computing missing Q/B and undercounts predation; it also suggests BA for printed zeros, which must not be adopted. The raw database converter reported BALANCED after normalizing diets and omitting consumption; this is invalid evidence for the final transcription. The final analysis below uses source P/Q internally and unnormalized source diets. ROUNDTRIP_CHECK.md confirms 2280 independently reopened source/JSON/workbook checks. No native EwE import/load test was run, and the package is explicitly not presented as a complete loadable model.

## Mass balance

**Verdict: NOT BALANCED as the published tables are transcribed.** This verdict concerns the available reconstruction, not a claim that the authors failed to balance their unpublished model.

This final analysis uses the corrected database JSON, exact unnormalized diet proportions, stated biomass/catch/BA, and the source P/Q (database ge). When Q/B is dashed but P/Q is stated, Q/B = (P/B)/(P/Q) is calculated for arithmetic only; no derived Q/B is written to the import files or database. The bundled raw calculation and its normalized database result are retained only as working evidence.

Q/B is derived internally for 33 consumers. Ten consumers have no positive diet entries: 6, 12, 22, 26, 27, 32, 35, 36, 37, 38. Their predation is unreported, so recomputed prey demands are lower bounds. Missing catch for nine groups is likewise treated as zero only for this lower-bound calculation. No unknown detritus fate or assimilation fraction is supplied.

8 groups have lower-bound recomputed EE > 1: 1 (Rastrelliger spp., 1.044), 2 (Scomberomorus spp., 1.116), 4 (Pomfret, 5.386), 5 (Small pelagic fish, 1.072), 22 (Small demersal fish, 1.357), 23 (Medium demersal piscivore, 1.798), 25 (Shellfish, 1.064), 35 (Juvenile small pelagics, 1.127).
31 groups differ from printed EE by more than 0.05; maximum absolute difference 4.436 at group 4 (Pomfret).

Every group has a source-stated absolute BA, including 26 printed zeros and 14 nonzero entries. No BA is inferred to close a gap. Migration terms were not reported in the chapter; they cannot be used to reconcile the discrepancies.

Mammals P/Q = 0.05 / 30.00 = 0.001667 is unusually low and was visually verified in Table 1, printed p.369. The other stated P/Q values are 0.20 or 0.25. Assimilation is not reported, so positive respiration cannot be proved without an import assumption. Under the EwE GS = 0.2 assumption, none implies non-positive respiration; that assumption is not extracted as data. Detritus-pool balance is undecidable because routing and GS are unreported.

The overproduction flags are supported by verified Table 1 B/PB/BA, Table 2 catch, and Table 3 feeding values. Known diet columns with sums above one inflate consumption, but normalizing them would alter the publication and is prohibited. Some EE mismatches can also reflect the conflicting catch versions discussed in REPORT.md.

| Group | Name | Printed EE | Recomputed lower-bound EE | Reported catch | BA |
|---|---|---|---|---|---|
| 1 | Rastrelliger spp. | 0.95 | 1.0439 | 0.166 | 0 |
| 2 | Scomberomorus spp. | 0.95 | 1.1161 | 0.001 | -0.003 |
| 3 | Carangidae | 0.95 | 0.6187 | 0.022 | -0.007 |
| 4 | Pomfret | 0.95 | 5.3864 | 0.003 | 0.001 |
| 5 | Small pelagic fish | 0.95 | 1.0722 | 0.113 | 0 |
| 6 | False trevally | 0.95 | 0.8000 | 0.001 | 0 |
| 7 | Large piscivores | 0.68 | 0.3242 | 0.018 | -0.001 |
| 8 | Sciaenidae | 0.95 | 0.8602 | 0.04 | 0 |
| 9 | Saurida spp. | 0.44 | 0.4074 | 0.032 | 0.012 |
| 10 | Lutianidae | 0.54 | 0.6445 | 0.009 | -0.004 |
| 11 | Plectorhynchidae | 0.95 | 0.4688 | 0.003 | 0 |
| 12 | Priacanthus spp. | 0.30 | 0.4183 | 0.029 | 0 |
| 13 | Sillago spp. | 0.95 | 0.5295 | 0.003 | 0.086 |
| 14 | Nemipterus spp. | 0.66 | 0.4220 | 0.034 | -0.004 |
| 15 | Ariidae | 0.68 | 0.2500 | 0.015 | -0.006 |
| 16 | Rays | 0.26 | 0.1250 | 0.013 | -0.01 |
| 17 | Sharks | 0.57 | 0.4615 | 0.008 | -0.005 |
| 18 | Cephalopod | 0.82 | 0.7299 | 0.151 | -0.1 |
| 19 | Shrimps | 0.95 | 0.6341 | 0.218 | 0 |
| 20 | Crab Lobster | 0.95 | 0.0104 | 0.109 | 0 |
| 21 | Trashfish | 0.88 | 0.9162 | 0.694 | -0.045 |
| 22 | Small demersal fish | 0.95 | 1.3566 | 0.042 | 0 |
| 23 | Medium demersal piscivore | 0.47 | 1.7979 | 0.001 | 0 |
| 24 | Medium demersal benthivore | 0.59 | 0.8638 | 0.007 | -0.042 |
| 25 | Shellfish | 0.95 | 1.0635 | 0.426 | 0 |
| 26 | Jellyfish | 0.00 | 0.0000 | unknown | 0 |
| 27 | Sea cucumber | 0.00 | 0.0000 | unknown | 0 |
| 28 | Seaweeds | 0.00 | 0.0000 | unknown | 0 |
| 29 | Coastal tuna | 0.95 | 0.9375 | 0.011 | 0 |
| 30 | Sergestid shrimp | 0.95 | 0.7134 | 0.041 | 0 |
| 31 | Mammals | 0.00 | 0.0000 | unknown | 0 |
| 32 | Pony fishes | 0.95 | 0.5274 | unknown | 0 |
| 33 | Benthos | 0.65 | 0.7944 | unknown | 0 |
| 34 | Zooplankton | 0.20 | 0.1366 | unknown | 0 |
| 35 | Juvenile small pelagics | 0.95 | 1.1269 | 0.096 | 0 |
| 36 | Juvenile Caranx spp. | 0.95 | 0.3466 | 0.026 | 0 |
| 37 | Juvenile Saurida spp. | 0.95 | 0.7175 | 0.043 | 0 |
| 38 | Juvenile Nemipterus spp. | 0.95 | 0.7575 | 0.058 | 0 |
| 39 | Phytoplankton | 0.44 | 0.4897 | unknown | 0 |
| 40 | Detritus | 0.17 | undecidable | unknown | 0 |
