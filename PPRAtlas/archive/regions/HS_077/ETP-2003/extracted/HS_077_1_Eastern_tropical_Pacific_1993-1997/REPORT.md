# Eastern tropical Pacific (1993-1997), final model ETP7

**Extraction status: PARTIAL / NOT IMPORT-READY.** The published ETP7 basic inputs and fisheries were extracted, but nine published diet columns do not sum to one and numeric detritus parameters/routing are absent. Those source defects remain visible. The bundled EE arithmetic alone reports BALANCED; that does not validate the malformed diets or establish a complete loadable model.

**Source:** Olson, R. J. and Watters, G. M. (2003). A model of the pelagic ecosystem in the eastern tropical Pacific Ocean. Inter-American Tropical Tuna Commission Bulletin 22(3), pp.135-218 (bilingual volume).
**LME:** HS_077 Pacific Eastern Central high seas. **Model number:** HS_077_1.
**Groups:** 39 rows: 38 living (36 consumers; 2 producers) plus Detritus.
**Fleets:** Longliners; Baitboats; purse-seine unassociated; purse-seine floating-object; purse-seine dolphin.
**Extracted:** 2026-09-04.

## Source bundle and eligibility

Read README.md and metadata.json before extraction. The bundle has one 89-page PDF, README.md, metadata.json, and footprint.geojson; no supplement, spreadsheet, or author model file is supplied. Metadata supplies the HS_077 high-seas classification and intended envelope, not numerical model parameters. The article covers a broader pelagic ETP ecosystem than the high-seas target alone; the target identity is retained without claiming spatial equivalence.

The publication averages estimates over 1993-1997 where possible (printed p.137 / PDF7). Some component source observations are older (e.g. bluefin); 2003 is the publication year, not the model year.

- ETP7 is the final eligible published parameterization (Tables2a and3a).
- ETP1 is explicitly described as unbalanced (printed p.139 / PDF9; Appendix Tables1a/2a at PDF82 and84-85). It is excluded from balanced-model imports. The first balanced model is identified as ETP2 (printed p.141 / PDF11).
- Intermediate ETP2-ETP6 are discussed, but complete individual parameter sets are not published. ETP5 sensitivity perturbations (including Cephalopod Q/B9.8 and Auxis P/B1.5 on p.141) cannot be combined with ETP7's changed groups and parameters. Figure2 is a dynamic comparison, not a full parameter table.
- English and Spanish copies are translations of the same model, not distinct models.

PDF source SHA-256: c037fcbcc0ac55852fdf73ed8c24801b57b40c5ef5be7124360557f911f0179b.

## Source tables

### Table2a (printed p.156 / PDF26): basic parameters

Mapped headers: Component -> group name; Trophic level -> TL; B -> biomass; P/B -> production/biomass; Q/B -> consumption/biomass; EE -> ecotrophic efficiency; U/Q -> unassimilated consumption (GS).

There are 38 living rows. Group order was fixed from Table2a and checked against the explicit IDs in Table3a; the original row39 Detritus was retained from Table3a with blank basic parameters. Row40 is external prey and maps to Import, not an extra organism. Table1a (PDF22-23) describes taxa and size ranges; no taxonomy workbook is produced.

The header mapping was checked with Large yellowfin: P/B2.35, Q/B15.6 and GS0.30 give diagnostic P/Q about0.151 and positive respiration. No P/Q was inserted into source files. Consumer Q/B and GS are present for all36 consumers; producers have no Q/B or GS.

B is printed in tons per million km2; every B value is divided by1,000,000 using decimal scaling. Example: Large yellowfin6500 ->0.006500 t/km2. The paper's density is on its model-area basis, not a separately tabulated habitat-area density. Basic_input uses its mandatory B column for the reported density; habitat fractions remain unknown. The database's biomass field preserves the published model-area density directly, without fabricating a habitat fraction or multiplying by1.

Footnote1 marks Ecopath-computed values. Biomass is model-estimated for groups 7, 10, 11, 12, 13, 17, 18, 19, 23, 24, 25, 27, 29, 30, 31, 33, 34, 35, 36, 37, 38. EE is model-estimated for groups 1, 2, 3, 4, 5, 6, 8, 9, 14, 15, 16, 20, 21, 22, 26, 28, 32; other displayed basic values are supplied parameter estimates.

Sea turtle B appears as baseline '2601' in English Table2a. Spanish Table2b (printed p.157 / PDF27), inspected at300dpi, unambiguously prints260 with superscript1. This resolves it as260 t/million km2, an Ecopath estimate, not2601. EE for Baleen and Toothed whales is printed '<0.001'; exact numeric EE cells remain blank and the bounds are recorded here.

### Table3a (printed pp.158-159 / PDF28-29): diets

Prey rows1-40; predator columns1-18 on the first page and19-36 on the continuation. The layout is stored sideways. Raw pdfgrid output was examined first. Poppler bounding boxes from the bundled pdfgrid parser were assigned directly to the printed prey IDs along x and predator IDs along y; no positional text-layout parsing was used. This avoids merging narrow numeric gutters. Complete bbox XHTML and conventional-orientation TSVs are in work.

The bundled PDF rotation helper requires unavailable PyMuPDF; it was not installed. Instead the original PDF remained untouched, coordinate axes were mapped as stored, and 200dpi page renders were rotated into upright PNGs for visual inspection. All315 populated diet cells were independently compared against the Spanish Table3b (PDF30-31); both copies agree exactly, including the defects.

The external-prey fraction0.667 for Bluefin is carried as Import (source row40). The remaining import cells are blank. No diet is normalized. Empty prey cells remain blank in CSV; no unreported fractions are allocated.

### Tables5a and6a (printed pp.175 and177 / PDF45 and47): fisheries

Header mapping in order: Longliners; Baitboats; purse-seine Unassociated; Floating-object; Dolphin; Total. Rows1-34 match the source, and all five fleets are retained. Row and fleet totals are computed only from extracted fleet cells by the bundled writer. Landings and discards are separate published quantities, both in tons per million km2 per year, converted by1,000,000. Example: Large yellowfin longline landings520.00 ->0.00052000 t/km2/year.

Two censored Dolphin landings (Large swordfish and Large wahoo) are '<0.01' in source units, hence '<0.00000001' t/km2/year. They remain blank rather than becoming zero or the bound. Large swordfish reported total10.95 differs from the exact numeric fleet-cell sum10.94; the generated total is the latter, and the reported10.95 remains in work/provenance.json. Small swordfish unassociated landings0.00 is an explicit zero and is preserved.

Unreported catch cells remain blank; no coastal/artisanal/recreational fishery values were invented. The paper explicitly excludes those fisheries for lack of data (printed p.139).

## Biomass accumulation

The complete bilingual PDF was swept for accumulation terms, then revisited with group-specific searches. Printed pp.136-137 define BA in the general Ecopath/Ecosim equations but give no numerical static BA. No numeric BA is tabulated in Tables2-8 or the appendices. No per-group BA is set to zero.

Figures2-4 (printed pp.149-151 / PDF19-21) were rendered at300dpi and inspected. They show Ecosim trajectories, relative biomass/CPUE, fishing effort and climate forcing. Their curves are not statements of the BA term for the 1993-1997 Ecopath snapshot. No slope was digitized or inserted. 'Steady-state' occurs in discussion of model approaches, not as an explicit numeric BA assignment.

Biomass_accumulation.csv is intentionally blank for all39 rows. Both database BA fields are -9999. The arithmetic diagnostic omits unknown BA internally; its suggestions are never entered as data.

## Values from prose

- Model area approximately32.8million km2 and bounds20N-20S,150W to the shelf break along the Americas: p.137/PDF7. Density conversion is by1million because that is the source's stated denominator, not division by the whole32.8million area.
- P/B=Z is explicitly stated for stock-assessment estimates (p.138/PDF8). Z is carried alongside P/B for Large/Small yellowfin and Large/Small bigeye (groups8,9,21,22; sources Table4a), and for Bluefin group20 whose P/B source explicitly is biomass-weighted Z (Table4a p.164/PDF34). Other Z cells remain blank.
- The author derived U/Q from prey proximate composition and digestibility (pp.138-139); final U/Q values are already tabulated and copied unchanged, including Mesozooplankton0.35 and Microzooplankton0.42. No software or project assimilation convention is used.
- Bluefin overlap is7% of model area with four months' residency (p.142/PDF12). Table4a footnote10 (p.167/PDF37) explicitly applies those factors to predator diet contributions. They are already represented in the published diets; they are not reapplied to B or relabelled as an independently stated EwE habitat-area input.
- Immigration is assumed to balance emigration (pp.137 and146). This is a net-balance assumption, not numeric gross immigration/emigration inputs; the latter remain unknown.

## Conventions applied

None for ecological parameters. No default habitat area, GS, BA, detritus fate, missing diet residual, or catch value was supplied. Format-only transformations are unit scaling, removal of thousands separators and superscript footnote markers, explicit external-prey mapping, and writer-generated totals.

Group names follow the source; two 'Misc.' abbreviations are kept. Model name is the place alone; versionETP7 is in provenance and this report. Source period is retained as1993-1997.

## Deliberate blanks

- BA for all groups: not numerically stated; EwE may default0, while extraction/database retain unknown.
- Habitat fractions for all groups: not tabulated as model inputs. EwE may default1; extraction/database remain unknown. Bluefin overlap is not silently repurposed as a habitat scaling factor.
- Detritus basic parameters, TL, import and all39 detritus-fate rows: the source identifies the pool in Table3 but provides no numeric fate allocations, pool biomass, or TL. No assumption that all production routes to the sole pool was used. EwE may export the unspecified fate remainder.
- EE for groups3/4: censored '<0.001', not an exact number.
- Other mortality and P/Q: not printed as input columns. The diagnostic may derive ratios internally but import files stay blank.
- GS for the two primary producers and detritus: not applicable and absent. The generic validator warns of an EwE0.2 default; it is not a consumer-data omission.
- Missing catch/import cells and the two censored catch cells remain blank. EwE may substitute0; database fields remain -9999 where no numeric total/import is available.
- No numerical growth or price values were derived for database vbk/shadow_price placeholders. Ontogenetic Tables7-8 concern split-pool transition parameters, outside these eight static import files; no dynamic loadability claim is made.

## Unresolved and flagged

The following diet sums are source inconsistencies, visually verified in the English pages and identically reproduced in Spanish:

| Consumer | Group | Sum | Source |
|---|---|---|---|
| 11 | Large sailfish | 1.022 | Table3a p.158 / PDF28 |
| 12 | Large swordfish | 0.978 | Table3a p.158 / PDF28 |
| 22 | Small bigeye tuna | 0.425 | Table3a p.159 / PDF29 |
| 23 | Small marlins | 1.575 | Table3a p.159 / PDF29 |
| 25 | Small swordfish | 1.121 | Table3a p.159 / PDF29 |
| 26 | Small dorado | 0.909 | Table3a p.159 / PDF29 |
| 27 | Small wahoo | 0.970 | Table3a p.159 / PDF29 |
| 28 | Small sharks | 1.070 | Table3a p.159 / PDF29 |
| 29 | Miscellaneous piscivores | 0.930 | Table3a p.159 / PDF29 |

Albacore column18 sums1.001, within the structural tolerance; it also remains unchanged. All other columns sum1.000. Some adjacent excesses and deficits suggest typesetting displacement, but no value has been shifted or normalized to repair them.

Low diagnostic P/Q for birds and marine mammals (groups1-6) comes from the printed low turnover and high Q/B values; columns and values were visually verified on p.156. These are endotherm groups, and their positive respiration does not resolve the source diet defects elsewhere.

The generic mass-balance script estimates pooled detritus inflow despite absent routing. That estimate is conditional and does not establish an actually parameterized detritus balance. Habitat/input completeness is also outside its arithmetic verdict.

## Validation

Bundled validate.py: **9 errors,43 warnings**. The nine errors are the source diet sums above. Warnings:39 absent detritus-fate rows;1 all-blank detritus basic row;1 GS warning covering producers/detritus;1 entirely blank BA file;1 absent detritus TL. No CSV formatting, numbering, fleet-total, or row-consistency error remains.

Diet sums range0.425-1.575; nine columns exceed±0.01. All39 fate rows are unknown, not falsely asserted to sum1. The standalone massbalance_check.py reports0 errors,6 low-P/Q warnings and35 notes. Maximum absolute EE difference is0.014 for Small yellowfin; no reconstructed EE exceeds1.

## Database conversion and round-trip verification

The requested bundled write_outputs.py generated all eight import files. The bundled database_json.py was executed on those files, but its raw output normalizes diets, inserts habitat1 and other placeholder zeros, and drops the all-blank detritus row. Those behaviors conflict with the extraction's source-preservation rules. The untouched raw output, workbook and log were archived in work/raw_converter.

A documented local adapter (work/adapt_database.py) reads the actual generated CSVs, restores all source proportions exactly, retains39 groups, and restores -9999 for unknown fields. It carries B as the published model-area density directly. It reruns the bundled equations on the corrected JSON. The installed skill and source files were not modified.

The reconstructed workbook was rebuilt from the corrected database parameters. source_parameters.json preserves fleet-disaggregated catches, Z, TL and metadata that the database schema cannot represent. It supplements the reconstructed sheets without inventing values. The workbook was reopened and all3162 source/reconstructed cells were checked, including blanks; all315 populated diet cells remain exact. No source diet normalization remains in the final database or workbook. Database unknowns and the39-group count are verified in roundtrip_verification.json.

Numeric source values are retained as strings in the reconstruction to preserve printed precision after unit conversion. Missing detritus-fate and biological values remain blank. Numerical analyses can parse these strings; the eight CSV/XLSX imports remain the canonical EwE input artifacts.

## Mass balance

Checked by `database_json.py (corrected JSON via local adapter)` on the assembled JSON for Eastern tropical Pacific ETP7 (1993-1997), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 6 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 39 of 39 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.014, group 21 (Small yellowfin tuna).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Pursuit birds, 0.001), 2 (Grazing birds, 0.002), 3 (Baleen whales, 0.002), 4 (Toothed whales, 0.003), 5 (Spotted dolphin, 0.002), 6 (Mesopelagic dolphins, 0.002).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a conditional diagnostic, not a steady-state result or a bound when the sign of BA is unknown.

Migration (E): source assumes immigration balances emigration (printed pp.137 and 146); no separate numeric gross migration rates are provided. No migration rate was synthesized.

### Warnings

- group 1 (Pursuit birds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Grazing birds): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Baleen whales): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (Toothed whales): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 5 (Spotted dolphin): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 6 (Mesopelagic dolphins): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 34 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Pursuit birds), 2 (Grazing birds), 5 (Spotted dolphin), 6 (Mesopelagic dolphins), 7 (Sea turtles), 8 (Large yellowfin tuna), 9 (Large bigeye tuna), 10 (Large marlins) ...
- detritus pools (1): inflow ~308.1, consumption ~0 t/km^2/year, implied EE ~0.000 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Pursuit birds | 0.0006 | 0.08 | 65.7 | 0.233 | 0.234 | 0.00122 | 0 | unknown |
| 2 | Grazing birds | 0.000123 | 0.15 | 65.7 | 0.134 | 0.135 | 0.00228 | 0 | unknown |
| 3 | Baleen whales | 0.0091 | 0.02 | 9.1 | - | 0 | 0.0022 | 0 | unknown |
| 4 | Toothed whales | 0.031 | 0.02 | 6.8 | - | 0.000274 | 0.00294 | 1.7e-07 | unknown |
| 5 | Spotted dolphin | 0.0035 | 0.04 | 16.5 | 0.219 | 0.22 | 0.00242 | 3e-06 | unknown |
| 6 | Mesopelagic dolphins | 0.017 | 0.04 | 16.5 | 0.19 | 0.19 | 0.00242 | 2.5e-06 | unknown |
| 7 | Sea turtles | 0.00026 | 0.15 | 3.5 | 0.5 | 0.5 | 0.0429 | 7.9e-07 | unknown |
| 8 | Large yellowfin tuna | 0.0065 | 2.35 | 15.6 | 0.36 | 0.36 | 0.151 | 0.00536 | unknown |
| 9 | Large bigeye tuna | 0.009 | 0.76 | 13 | 0.33 | 0.33 | 0.0585 | 0.002127 | unknown |
| 10 | Large marlins | 0.000573 | 1 | 7.8 | 0.5 | 0.5 | 0.128 | 0.0002865 | unknown |
| 11 | Large sailfish | 5.2e-05 | 1.15 | 7.8 | 0.25 | 0.251 | 0.147 | 1.501e-05 | unknown |
| 12 | Large swordfish | 3.3e-05 | 0.44 | 7.8 | 0.75 | 0.753 | 0.0564 | 1.094e-05 | unknown |
| 13 | Large dorado | 0.000218 | 1.2 | 21.9 | 0.25 | 0.25 | 0.0548 | 6e-08 | unknown |
| 14 | Large wahoo | 0.0011 | 1.2 | 9.8 | 0.068 | 0.0682 | 0.122 | 7.499e-05 | unknown |
| 15 | Large sharks | 0.0004 | 0.32 | 7.8 | 0.479 | 0.479 | 0.041 | 6.129e-05 | unknown |
| 16 | Rays | 0.00023 | 0.25 | 3.9 | 0.361 | 0.361 | 0.0641 | 2.076e-05 | unknown |
| 17 | Skipjack tuna | 0.02644 | 1.88 | 21.5 | 0.4 | 0.401 | 0.0874 | 0.004073 | unknown |
| 18 | Albacore | 0.003026 | 0.77 | 17 | 0.75 | 0.753 | 0.0453 | 0.0004419 | unknown |
| 19 | Auxis spp. | 0.1432 | 2.5 | 25 | 0.95 | 0.95 | 0.1 | 7.698e-05 | unknown |
| 20 | Bluefin tuna | 0.0014 | 0.65 | 12.8 | 0.794 | 0.801 | 0.0508 | 4.514e-05 | unknown |
| 21 | Small yellowfin tuna | 0.0082 | 1.75 | 18.3 | 0.905 | 0.919 | 0.0956 | 0.002812 | unknown |
| 22 | Small bigeye tuna | 0.01 | 0.72 | 15.3 | 0.689 | 0.694 | 0.0471 | 0.000575 | unknown |
| 23 | Small marlins | 0.000145 | 0.5 | 9 | 0.75 | 0.75 | 0.0556 | 1.6e-07 | unknown |
| 24 | Small sailfish | 0.000127 | 0.57 | 9.8 | 0.75 | 0.75 | 0.0582 | 5e-08 | unknown |
| 25 | Small swordfish | 9.8e-05 | 0.21 | 9 | 0.75 | 0.749 | 0.0233 | 3.64e-06 | unknown |
| 26 | Small dorado | 0.002 | 3.15 | 27.4 | 0.99 | 0.992 | 0.115 | 6.109e-05 | unknown |
| 27 | Small wahoo | 0.00273 | 1.75 | 11.4 | 0.75 | 0.755 | 0.154 | 1.16e-05 | unknown |
| 28 | Small sharks | 0.00027 | 0.58 | 9.2 | 0.583 | 0.583 | 0.063 | 8.473e-05 | unknown |
| 29 | Miscellaneous piscivores | 0.01654 | 2.25 | 7.7 | 0.95 | 0.952 | 0.292 | 0.0002368 | unknown |
| 30 | Flyingfishes | 0.1606 | 2.88 | 25.8 | 0.95 | 0.95 | 0.112 | 0 | unknown |
| 31 | Misc. epipelagic fishes | 2.249 | 2.07 | 10.8 | 0.95 | 0.95 | 0.192 | 1.073e-05 | unknown |
| 32 | Misc. mesopelagic fishes | 2 | 2 | 10.8 | 0.927 | 0.925 | 0.185 | 0 | unknown |
| 33 | Cephalopods | 1.105 | 2 | 7 | 0.85 | 0.85 | 0.286 | 0 | unknown |
| 34 | Crabs | 0.1197 | 3.5 | 10 | 0.95 | 0.95 | 0.35 | 0 | unknown |
| 35 | Mesozooplankton | 0.7067 | 64 | 200 | 0.68 | 0.681 | 0.32 | 0 | unknown |
| 36 | Microzooplankton | 0.8264 | 143 | 600 | 0.98 | 0.98 | 0.238 | 0 | unknown |
| 37 | Large phytoplankton | 0.4261 | 125 | - | 0.9 | 0.9 | - | 0 | unknown |
| 38 | Small producers | 2.999 | 167 | - | 0.99 | 0.99 | - | 0 | unknown |
| 39 | Detritus | - | - | - | - | - | - | 0 | unknown |

## Scope of this arithmetic verdict

The bundled arithmetic verdict does not check unit diet sums, completeness of detritus routing, or all unknown fields. Nine source diet columns fail structural validation. This extraction is **PARTIAL / NOT IMPORT-READY**, even when its EE arithmetic is consistent. Detritus routing and BA are unknown; the reported pooled-detritus result is indicative and does not establish closure of the unpublished routing.
