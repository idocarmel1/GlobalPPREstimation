# Northern Humboldt Current (1995–1998) — aggregated

Source: Chiaverano et al. (2018), Evaluating the role of large jellyfish and forage fishes as energy pathways, and their interplay with fisheries, in the Northern Humboldt Current System. Progress in Oceanography164:28–36. DOI10.1016/j.pocean.2018.04.009.
Model number: 13_3. LME13 Humboldt Current. Extracted2026-09-04.
24 Ecopath groups:20 living (2 producers,18 consumers) and4 detritus/egg pools;1 pooled fishery.

Status: partial reconstruction with source inconsistencies. Numeric source fields were transcribed, including failed diet and mass-balance checks; native EwE loading was not tested.

## Source bundle and eligibility

README and metadata were read before extraction; their no-verified-file claims are stale. The bundle includes the nine-page article, Supplementary material revised and final.xls (12 visible worksheets), and Peru paper figures and tables II.docx (figures/table images and scenario-results Table2). footprint.geojson is spatial context.
Workbook Index and all 12 sheet contents were inventoried, including scenarios and pedigree. An installed Excel instance opened the XLS read-only, macros disabled, and saved a working XLSX under extracted/work; original files remain unchanged. Source table renderings were made from the working copy. SOURCE_INVENTORY.json records filenames/hashes.
The paper p30 states the reference inputs average1995–1998; metadata1995–2004 is not supported. This is one of two published model resolutions. Four ECOTRAN scenarios and uncertainty simulations are not separately specified Ecopath input models.

## Source tables

Article Table1, PDF page4/printed31: Group code | Functional group | Biomass | p/b | q/b | p/q | ae | ee | Landings | Discards. Numerical columns identified by bounding-box x positions209.9,266.3,309.0,355.2,390.7,426.2,461.7,518.1. Names matched to source parameter rows, preserving all2-decimal values and zero cells.
Supplement Table F-aggregated diet (caption calls it TableG)!A3:Y28 supplies24 prey groups plus Import and matching predator headers. Names, not TableE codes, define the mapping. Sea turtle↔Sea turtles and Eggs↔Fish eggs are explicit synonyms. Consumer columns3–20 exported.
Supplement Table G-aggregate detritus fate (caption calls it TableH) is explicitly for ECOTRAN and separates feces, senescence and NH4 excretion into surface/sub-surface pools. It is not one Ecopath detritus-fate matrix; its complete cells remain in extracted/work, but are not merged by invented weights.
Header check: microzooplankton256/1024=0.25. Table1 and workbook diet were visually inspected.

## Biomass accumulation

All nine paper pages, workbook sheets (including production and scenario tables), and DOCX content searched for accumulation/migration. Paper p30 explicitly describes steady state and defines BA symbolically but reports no numeric group BA values. BA remains blank/-9999 rather than assumed0. Scenario production changes are not static baseline biomass accumulation.

## Values from prose

Paper p30 gives model area165,000 km² (4°S–16°S, to111 km offshore), input reference period1995–1998, a10% artisanal discard assumption, and a sardine catch adjustment from5.65 to1.4 t/km²/year.
Assimilation efficiency is explicitly tabulated as AE; GS is the exact complement1−AE. Thus AE0.65 givesGS0.35, AE0.80 givesGS0.20; these are source-derived, not defaults.
The source table's catch/discards take precedence over recalculation from generic rates; contradictions are recorded below.

## Conventions applied

No unstated ecological defaults. Names normalized only for whitespace/ligatures and explicit synonyms to match tables. Fisheries are fleet columns rather than biological groups. Anchovy/fish eggs are classified as the source's non-consuming detritus recipient pool, matching blank P/B/Q/B and the dedicated detritus-fate column; biological eggs are not given an invented turnover rate.
Article Table1 codes4–27 become importer numbers1–24, preserving exact source order. GROUP_NUMBER_MAP.csv and source_group_code record every mapping. Codes1–3 in the ECOTRAN production matrix are nutrients, not Ecopath groups; code28 is Fisheries.

## Deliberate blanks

TL is not numerically tabulated in these parameter sources and remains blank. Habitat fractions, numeric BA/migration, Z, other mortality and external detritus imports are unreported. EwE may substitute habitat1, GS0.2, BA0 or catch0; those software assumptions were not copied into missing inputs.
Q/B/GS are structurally inapplicable to primary producers and four detritus pools. Aggregated Ecopath detritus routing is not explicitly supplied; separate ECOTRAN surface/subsurface fates cannot be collapsed without an assumption, so all24 rows stay blank.

## Unresolved and flagged

- Large jellyfish/Chrysaora column totals1.04499999999999783 (about1.045), not1. No normalization. Both workbook diet tables retain the same defect.
- Gelatinous/small jellyfish biomass is about0.00907 in resolved TableA (display0.01), but the Chrysaora diet includes0.0492610837438424 on that group (TableB H9; aggregate TableF H9). That single flow is already far larger than its production. Verified against the formatted parameter and diet tables. No source-supported BA correction exists. The formal checker labels the gap INDETERMINATE because BA is unknown; it is a major failure to reproduce the paper's claimed steady-state balance.
- Paper p30 says sardine landings were reduced to1.4, but resolved TableA J14 stores5.6513425 and aggregated Table1 forage-fish landings28.13 remain consistent with the unreduced sardine plus anchovy catch. Published table values are retained; the stated revision is not silently applied across resolutions.
- TableA column label gives biomass t/km²/year, a dimensional labeling problem. Values are the model's standing biomass B per km² as defined in the methods; no time conversion applied.
- Workbook TableE misassigns fish-egg/offal/pelagic detritus aggregate codes relative to article Table1 and TableF. Matching uses names and the parameter/diet tables, not TableE code positions.
- Article Table1 Sea turtles biomass0.00 and seabird/marine mammal P/Q0.00 are printed rounding zeros; retained exactly. Do not interpret as biological absence or zero production. Apex-predator rounded values also produce a0.152 EE discrepancy. No high-precision aggregate basic table was supplied.

## Validation

validate.py:1 error (large jellyfish diet1.045),27 warnings (GS in6 non-consumers, unknown BA,24 missing detritus routes,missing TL). Small-jellyfish known-flow EE is about4024.64.
Final JSON uses preserved source diets. Formal balance verdict INDETERMINATE; this does not establish a runnable balanced model. See exact comparisons in ROUND_TRIP_AUDIT.md.

## Conversion and round trip

The installed Ecopath scripts wrote the eight import files and initial database JSON. Their converter normalizes non-unit diet columns, fills unknown habitat with 1, omits P/Q and loses fleet splits on workbook reconstruction. The local preserve_database.py adapter reverses those transformations using the CSV files, carries stated P/Q in ge, and preserves metadata, TL, fleet data and all eight source tables in JSON extensions. The final workbook is rebuilt from the saved JSON, with exact cell comparisons recorded in ROUND_TRIP_AUDIT.md. Unmodified converter results are archived in extracted/work and are not the final model.

Unknown habitat stays -9999. Biomass retains the publication's density over the model domain for mass-balance arithmetic; this does not assert a habitat fraction of 1. Unknown BA, GS, Z, detritus import, migration and prices are not populated from software defaults. Sparse blank diet cells mean absent prey links; missing complete fields remain unknown. The checker may assume GS=0.2 internally for diagnostic calculations, but that assumption is not written into source files.

## Reproduction

Use the source JSON in this model directory with the installed write_outputs.py, run validate.py and massbalance_check.py, run database_json.py, then run extracted/work/preserve_database.py with this model directory as its argument. The adapter is mandatory to retain unnormalized source values. Installed skill files were not changed.

## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for Northern Humboldt Current, EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 2 indeterminate, 2 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 24 of 24 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 4023.691, group 6 (Small jellyfish).

Groups with recomputed EE > 1: 6 (Small jellyfish, 4024.641).

P/Q outside 0.02-0.5: 18 (Seabirds, 0.001), 19 (Marine mammals, 0.004).

BA: not stated for any group. Every EE below is recomputed without a BA term, as a diagnostic with unreported terms omitted. It is not a bound because BA may be positive or negative.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 6 (Small jellyfish): recomputed EE = 4024.641 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 17 (Apex predatory fish): printed EE 0.56 vs recomputed 0.408 (diff 0.152) with BA unknown - a BA of +0.00372 t/km^2/year (+0.15 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 18 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 19 (Marine mammals): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 18 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Microzooplankton), 4 (Mesozooplakton), 5 (Macrozooplankton), 6 (Small jellyfish), 7 (Large jellyfish), 8 (Macrobenthos), 9 (Forage fish), 10 (Mesopelagics) ...
- detritus pools (4): inflow ~6924, consumption ~6164 t/km^2/year, implied EE ~0.890 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Large phytoplankton | 34.09 | 237.5 | - | 0.82 | 0.822 | - | 0 | unknown |
| 2 | Small phytoplankton | 13.38 | 237.5 | - | 0.97 | 0.967 | - | 0 | unknown |
| 3 | Microzooplankton | 13.54 | 256 | 1024 | 0.96 | 0.957 | 0.25 | 0 | unknown |
| 4 | Mesozooplakton | 24.08 | 40 | 125 | 0.92 | 0.95 | 0.32 | 0 | unknown |
| 5 | Macrozooplankton | 37.42 | 19.09 | 46.55 | 0.95 | 0.904 | 0.41 | 0 | unknown |
| 6 | Small jellyfish | 0.01 | 0.58 | 2.92 | 0.95 | 4.02e+03 | 0.199 | 0 | unknown |
| 7 | Large jellyfish | 8.46 | 15 | 56 | 0 | 5.38e-05 | 0.268 | 0 | unknown |
| 8 | Macrobenthos | 23.17 | 1.2 | 10 | 0.79 | 0.788 | 0.12 | 0 | unknown |
| 9 | Forage fish | 69.05 | 1.91 | 14.51 | 0.82 | 0.815 | 0.132 | 29 | unknown |
| 10 | Mesopelagics | 14.63 | 1.4 | 14 | 0.26 | 0.262 | 0.1 | 0 | unknown |
| 11 | Cephalopods | 2.19 | 5.11 | 12.59 | 0.89 | 0.884 | 0.406 | 0.14 | unknown |
| 12 | Pelagic planktivorous fish | 11.01 | 1 | 9.98 | 0.89 | 0.885 | 0.1 | 1.69 | unknown |
| 13 | Pelagic piscivorous fish | 16.16 | 0.99 | 9.46 | 0.21 | 0.215 | 0.105 | 2.83 | unknown |
| 14 | Demersal piscivorous fish | 2.37 | 1.2 | 7.97 | 0.62 | 0.617 | 0.151 | 1.27 | unknown |
| 15 | Demersal planktivorous fish | 5.78 | 2.4 | 15.3 | 0.68 | 0.681 | 0.157 | 0.02 | unknown |
| 16 | Demersal benthivorous fish | 1.17 | 1.08 | 7.23 | 0.79 | 0.791 | 0.149 | 0.59 | unknown |
| 17 | Apex predatory fish | 0.05 | 0.49 | 3.24 | 0.56 | 0.408 | 0.151 | 0.01 | unknown |
| 18 | Seabirds | 0.04 | 0.04 | 61 | 0 | 0 | 0.000656 | 0 | unknown |
| 19 | Marine mammals | 0.13 | 0.1 | 25.83 | 0 | 0 | 0.00387 | 0 | unknown |
| 20 | Sea turtles | 0 | 0.19 | 3.5 | 0 | - | 0.0543 | 0 | unknown |
| 21 | Fish eggs | 0.44 | - | - | 0.87 | - | - | 0 | unknown |
| 22 | Detritus offal | 0.05 | - | - | 0 | - | - | 0 | unknown |
| 23 | Pelagic detritus | 20 | - | - | 0 | - | - | 0 | unknown |
| 24 | Benthic detritus | 60 | - | - | 0.89 | - | - | 0 | unknown |


### Source-fidelity and completeness limits

These findings were recomputed from the final, unnormalized JSON. Known-flow EE checks omit unknown catch/BA/migration. The checker uses GS=0.2 internally for missing GS in respiration/detritus diagnostics only; the JSON retains -9999. Unstated detritus routing prevents pool-specific validation.

Diet columns outside +/-0.01: Group 7 (Large jellyfish): diet+import = 1.04499999999999783.

The physiological check derives P/B divided by Q/B; any differently rounded stated P/Q is preserved separately in ge and Basic_input.csv.
