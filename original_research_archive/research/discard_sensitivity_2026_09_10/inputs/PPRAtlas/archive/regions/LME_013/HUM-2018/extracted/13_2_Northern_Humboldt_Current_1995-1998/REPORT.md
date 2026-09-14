# Northern Humboldt Current (1995–1998) — fully resolved

Source: Chiaverano et al. (2018), Evaluating the role of large jellyfish and forage fishes as energy pathways, and their interplay with fisheries, in the Northern Humboldt Current System. Progress in Oceanography164:28–36. DOI10.1016/j.pocean.2018.04.009.
Model number: 13_2. LME13 Humboldt Current. Extracted2026-09-04.
39 Ecopath groups:35 living (2 producers,33 consumers) and4 detritus/egg pools;2 fleets.

Status: partial reconstruction with source inconsistencies. Numeric source fields were transcribed, including failed diet and mass-balance checks; native EwE loading was not tested.

## Source bundle and eligibility

README and metadata were read before extraction; their no-verified-file claims are stale. The bundle includes the nine-page article, Supplementary material revised and final.xls (12 visible worksheets), and Peru paper figures and tables II.docx (figures/table images and scenario-results Table2). footprint.geojson is spatial context.
Workbook Index and all 12 sheet contents were inventoried, including scenarios and pedigree. An installed Excel instance opened the XLS read-only, macros disabled, and saved a working XLSX under extracted/work; original files remain unchanged. Source table renderings were made from the working copy. SOURCE_INVENTORY.json records filenames/hashes.
The paper p30 states the reference inputs average1995–1998; metadata1995–2004 is not supported. This is one of two published model resolutions. Four ECOTRAN scenarios and uncertainty simulations are not separately specified Ecopath input models.

## Source tables

Table A-resolved parameters!A4:L44: columns Group/code, Functional group, B, P/B, Q/B, P/Q, AE, EE, Artisanal/Commercial landings, Artisanal/Commercial discards. Mapping to n/name/biomass/pb/qb/pq/(1−AE)/ee and two fleet tables. Rows6–44 supply groups1–39; rows45–46 are fleets40–41 and are not biological groups.
Stored numeric values are retained at the precision present in the machine-readable source. Cell display formats often round to2 decimals (even turning tiny turtle biomass/PQ into0.00); those display formats and bold-estimated flags are retained in SOURCE_CELLS.csv, avoiding replacement of nonzero stored values by rounded display zeros.
Table B-resolved diet!B3:AN43: group1–39 headers, rows4–42 prey, row43 Import. Consumers3–35 only are exported as diet columns; primary producer/detritus columns are structural zeros. Name matches verified individually.
Table C-resolved detritus fate!A3:G42:39 group routes to Anchovy eggs, Fishery offal, Pelagic detritus, Benthic detritus, Export; all row sums1. Fleet routes in rows43–44 are retained separately in FLEET_DETRITUS_FATE.json (all fishery discards to offal).
P/Q consistency check: microzooplankton256/1024=0.25. Original zero cells remain zero.

## Biomass accumulation

All nine paper pages, workbook sheets (including production and scenario tables), and DOCX content searched for accumulation/migration. Paper p30 explicitly describes steady state and defines BA symbolically but reports no numeric group BA values. BA remains blank/-9999 rather than assumed0. Scenario production changes are not static baseline biomass accumulation.

## Values from prose

Paper p30 gives model area165,000 km² (4°S–16°S, to111 km offshore), input reference period1995–1998, a10% artisanal discard assumption, and a sardine catch adjustment from5.65 to1.4 t/km²/year.
Assimilation efficiency is explicitly tabulated as AE; GS is the exact complement1−AE. Thus AE0.65 givesGS0.35, AE0.80 givesGS0.20; these are source-derived, not defaults.
The source table's catch/discards take precedence over recalculation from generic rates; contradictions are recorded below.

## Conventions applied

No unstated ecological defaults. Names normalized only for whitespace/ligatures and explicit synonyms to match tables. Fisheries are fleet columns rather than biological groups. Anchovy/fish eggs are classified as the source's non-consuming detritus recipient pool, matching blank P/B/Q/B and the dedicated detritus-fate column; biological eggs are not given an invented turnover rate.
Source group numbers1–39 retained; fleets40–41 separated without renumbering the biological groups.

## Deliberate blanks

TL is not numerically tabulated in these parameter sources and remains blank. Habitat fractions, numeric BA/migration, Z, other mortality and external detritus imports are unreported. EwE may substitute habitat1, GS0.2, BA0 or catch0; those software assumptions were not copied into missing inputs.
Q/B/GS are structurally inapplicable to primary producers and four detritus pools. Detritus fates are fully supplied by TableC.

## Unresolved and flagged

- Large jellyfish/Chrysaora column totals1.04499999999999783 (about1.045), not1. No normalization. Both workbook diet tables retain the same defect.
- Gelatinous/small jellyfish biomass is about0.00907 in resolved TableA (display0.01), but the Chrysaora diet includes0.0492610837438424 on that group (TableB H9; aggregate TableF H9). That single flow is already far larger than its production. Verified against the formatted parameter and diet tables. No source-supported BA correction exists. The formal checker labels the gap INDETERMINATE because BA is unknown; it is a major failure to reproduce the paper's claimed steady-state balance.
- Paper p30 says sardine landings were reduced to1.4, but resolved TableA J14 stores5.6513425 and aggregated Table1 forage-fish landings28.13 remain consistent with the unreduced sardine plus anchovy catch. Published table values are retained; the stated revision is not silently applied across resolutions.
- TableA column label gives biomass t/km²/year, a dimensional labeling problem. Values are the model's standing biomass B per km² as defined in the methods; no time conversion applied.
- Workbook TableE misassigns fish-egg/offal/pelagic detritus aggregate codes relative to article Table1 and TableF. Matching uses names and the parameter/diet tables, not TableE code positions.
- Nonzero turtle biomasses and endotherm P/Q are retained from underlying cells, despite display0.00. Prose discard rates are approximate and do not override the stored fleet-specific values.

## Validation

validate.py:1 error (Chrysaora diet1.045),3 warnings (GS in6 non-consumers, unknown BA, missing TL). Detritus fate39/39 rows sum1. Known-flow EE for gelatinous zooplankton is about4409.97, versus printed0.95. Other major parameters reconcile much more closely.
Final JSON uses preserved source diets. Formal balance verdict INDETERMINATE; this does not establish a runnable balanced model. See exact comparisons in ROUND_TRIP_AUDIT.md.

## Conversion and round trip

The installed Ecopath scripts wrote the eight import files and initial database JSON. Their converter normalizes non-unit diet columns, fills unknown habitat with 1, omits P/Q and loses fleet splits on workbook reconstruction. The local preserve_database.py adapter reverses those transformations using the CSV files, carries stated P/Q in ge, and preserves metadata, TL, fleet data and all eight source tables in JSON extensions. The final workbook is rebuilt from the saved JSON, with exact cell comparisons recorded in ROUND_TRIP_AUDIT.md. Unmodified converter results are archived in extracted/work and are not the final model.

Unknown habitat stays -9999. Biomass retains the publication's density over the model domain for mass-balance arithmetic; this does not assert a habitat fraction of 1. Unknown BA, GS, Z, detritus import, migration and prices are not populated from software defaults. Sparse blank diet cells mean absent prey links; missing complete fields remain unknown. The checker may assume GS=0.2 internally for diagnostic calculations, but that assumption is not written into source files.

## Reproduction

Use the source JSON in this model directory with the installed write_outputs.py, run validate.py and massbalance_check.py, run database_json.py, then run extracted/work/preserve_database.py with this model directory as its argument. The adapter is mandatory to retain unnormalized source values. Installed skill files were not changed.

## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for Northern Humboldt Current, EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 1 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 39 of 39 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 4409.020, group 6 (Gelatinous zooplankton).

Groups with recomputed EE > 1: 6 (Gelatinous zooplankton, 4409.970).

P/Q outside 0.02-0.5: 31 (Seabirds, 0.001), 32 (Pinnipeds, 0.003), 33 (Cetaceans, 0.005).

BA: not stated for any group. Every EE below is recomputed without a BA term, as a diagnostic with unreported terms omitted. It is not a bound because BA may be positive or negative.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 6 (Gelatinous zooplankton): recomputed EE = 4409.970 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation

### Warnings

- group 31 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 32 (Pinnipeds): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 33 (Cetaceans): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 33 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Microzooplankton), 4 (Mesozooplankton), 5 (Macrozooplankton), 6 (Gelatinous zooplankton), 7 (Chrysaora plocamia), 8 (Macrobenthos), 9 (Sardine), 10 (Anchovy) ...
- detritus pools (4): inflow ~6925, consumption ~6165 t/km^2/year, implied EE ~0.890 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Diatoms | 34.09 | 237.5 | - | 0.8217 | 0.822 | - | 0 | unknown |
| 2 | Dino/silicoflagellates | 13.38 | 237.5 | - | 0.9669 | 0.967 | - | 0 | unknown |
| 3 | Microzooplankton | 13.54 | 256 | 1024 | 0.9567 | 0.957 | 0.25 | 0 | unknown |
| 4 | Mesozooplankton | 24.08 | 40 | 125 | 0.9262 | 0.951 | 0.32 | 0 | unknown |
| 5 | Macrozooplankton | 37.42 | 19.09 | 46.55 | 0.95 | 0.907 | 0.41 | 0 | unknown |
| 6 | Gelatinous zooplankton | 0.009068 | 0.584 | 2.92 | 0.95 | 4.41e+03 | 0.2 | 0 | unknown |
| 7 | Chrysaora plocamia | 8.464 | 15 | 56 | 6.118e-05 | 6.12e-05 | 0.268 | 0 | unknown |
| 8 | Macrobenthos | 23.17 | 1.2 | 10 | 0.7903 | 0.79 | 0.12 | 0 | unknown |
| 9 | Sardine | 10.74 | 1.4 | 12 | 0.97 | 0.969 | 0.117 | 5.826 | unknown |
| 10 | Anchovy | 58.32 | 2 | 15 | 0.8148 | 0.814 | 0.133 | 23.17 | unknown |
| 11 | Mesopelagic fish | 14.63 | 1.4 | 14 | 0.2639 | 0.264 | 0.1 | 0 | unknown |
| 12 | Jumbo squid | 0.3835 | 8.91 | 25.46 | 0.8 | 0.8 | 0.35 | 0.1055 | unknown |
| 13 | Other cephalopods | 1.806 | 4.3 | 10 | 0.95 | 0.948 | 0.43 | 0.03547 | unknown |
| 14 | Other small pelagic fish | 11 | 1 | 10 | 0.9 | 0.899 | 0.1 | 1.69 | unknown |
| 15 | Horse mackerel | 7.299 | 1.2 | 10 | 0.2355 | 0.236 | 0.12 | 1.747 | unknown |
| 16 | Chub mackerel | 7.69 | 0.85 | 10 | 0.1551 | 0.155 | 0.085 | 0.7427 | unknown |
| 17 | Other large pelagic fish | 1.173 | 0.625 | 6.25 | 0.534 | 0.534 | 0.1 | 0.3338 | unknown |
| 18 | Small hake | 2.008 | 1.122 | 7.483 | 0.7214 | 0.722 | 0.15 | 1.166 | unknown |
| 19 | Medium hake | 0.2885 | 1.786 | 11.91 | 0.1407 | 0.141 | 0.15 | 0.04868 | unknown |
| 20 | Large hake | 0.0415 | 1.28 | 8.533 | 0.8739 | 0.874 | 0.15 | 0.04633 | unknown |
| 21 | Flatfish | 0.025 | 0.304 | 2.027 | 0.9955 | 0.995 | 0.15 | 0.004058 | unknown |
| 22 | Small demersal fish | 5.23 | 2.3 | 15.33 | 0.7304 | 0.73 | 0.15 | 0.01934 | unknown |
| 23 | Benthic elasmobranchs | 0.0615 | 1 | 6.667 | 0.6587 | 0.659 | 0.15 | 0.04051 | unknown |
| 24 | Butter fishes | 0.019 | 0.8 | 4 | 0.5368 | 0.54 | 0.2 | 0 | unknown |
| 25 | Conger | 0.0115 | 0.75 | 5 | 0.01129 | 0.0113 | 0.15 | 0 | unknown |
| 26 | Medium demersal fish | 0.2055 | 1.9 | 12.67 | 0.8202 | 0.82 | 0.15 | 0.1496 | unknown |
| 27 | Medium sciaenids | 0.2935 | 0.9155 | 6.103 | 0.7098 | 0.712 | 0.15 | 0.0613 | unknown |
| 28 | Sea robin | 0.554 | 3.31 | 16.55 | 0.4585 | 0.459 | 0.2 | 0 | unknown |
| 29 | Catfish | 0.6135 | 0.9 | 6 | 0.8213 | 0.821 | 0.15 | 0.3398 | unknown |
| 30 | Chondrichthyans | 0.0525 | 0.486 | 3.24 | 0.5642 | 0.564 | 0.15 | 0.0144 | unknown |
| 31 | Seabirds | 0.0385 | 0.04 | 61 | 0 | 0 | 0.000656 | 0 | unknown |
| 32 | Pinnipeds | 0.0625 | 0.1 | 36.95 | 0 | 0 | 0.00271 | 0 | unknown |
| 33 | Cetaceans | 0.0645 | 0.1 | 20 | 0 | 0 | 0.005 | 0 | unknown |
| 34 | Green sea turtle | 0.000343 | 0.192 | 3.5 | 0 | 0 | 0.0549 | 0 | unknown |
| 35 | Leatherback turtle | 0.000162 | 0.192 | 3.5 | 0 | 0 | 0.0549 | 0 | unknown |
| 36 | Anchovy eggs | 0.436 | - | - | 0.8843 | - | - | 0 | unknown |
| 37 | Fishery offal | 0.05 | - | - | 0 | - | - | 0 | unknown |
| 38 | Pelagic detritus | 20 | - | - | 0 | - | - | 0 | unknown |
| 39 | Benthic detritus | 60 | - | - | 0.8891 | - | - | 0 | unknown |


### Source-fidelity and completeness limits

These findings were recomputed from the final, unnormalized JSON. Known-flow EE checks omit unknown catch/BA/migration. The checker uses GS=0.2 internally for missing GS in respiration/detritus diagnostics only; the JSON retains -9999. All group detritus routes are explicitly supplied in Table C. The bundled checker reports a pooled detritus diagnostic; it does not certify each routed pool.

Diet columns outside +/-0.01: Group 7 (Chrysaora plocamia): diet+import = 1.04499999999999783.

The physiological check derives P/B divided by Q/B; any differently rounded stated P/Q is preserved separately in ge and Basic_input.csv.
