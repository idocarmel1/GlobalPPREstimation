# Chilean Patagonia (1980)

Source: Neira et al. (2026), Analysing ecosystem and demersal-stock dynamics in Chilean Patagonia system (41°28.6′S–57°S) from 1980 to 2020 using food web modelling. Progress in Oceanography 241, 103631. DOI 10.1016/j.pocean.2025.103631.
Model number: 13_1. LME: 13 Humboldt Current (archive assignment; actual model spans southern Patagonia). Extracted: 2026-09-04.
15 groups: 14 living and one detritus; 13 consumers. Three named fleets in the study; the published basic table gives only pooled landings, retained as one reporting column.

Status: partial reconstruction. All available basic parameters, diets and pooled landings were extracted. GS, detritus routing, detritus biomass, BA and fleet allocation are not numerically reported in the supplied material. Native EwE loading was not tested.

## Source bundle and eligibility

README.md and metadata.json were read first. Both claim no recovered source, but 1-s2.0-S0079661125002198-main.pdf exists and is a readable 15-page paper. SOURCE_INVENTORY.json records all article files and hashes. The paper has one 1980 mass-balanced Ecopath model. 1980–2020 time series and fitting hypotheses concern Ecosim and are not separate static parameterizations. Supplements S1–S7 are referenced but absent from this source bundle; no values were borrowed from them.

## Source tables

### Table 3, PDF/printed page 6
Header: Functional group | TL | B | P/B | Q/B | EE | P/Q | Y.
Mapping: name | tl | biomass | pb | qb | ee | pq | pooled landings.
B is tons/km²; rates are annual; Y is tons/km²/year. All 15 groups retained in source order. No biomass conversion: the approximate 290,000 km² area on page 4 is contextual.
The Q/B column is blank for phytoplankton and detritus. Table 3 bold values are Ecopath estimates: TL throughout, biomass groups 2–7, P/Q for consumers, and EE except the input 0.95 for groups 2–4 and 6–7. Retained exact printed digits.
Header mapping check: juvenile hoki P/B 1.20 / Q/B 6.24 = approximately 0.19, matching tabulated P/Q.
Extraction: pdfgrid word boxes, merge_gap=2, explicit group-name matches; page rendered at 220 dpi and inspected.

### Table 4, PDF/printed page 7
Prey rows 1–15 plus Import; predator columns 2–14. pdfgrid merge_gap=0.4, header anchor line4. Every label matched against Table3.
Consumer imports: Hoki adults0.270, Kingklip0.220, Skates0.820, Sea lions0.590. Other imports left blank as printed.
Sea lions diet sums1.002 although the printed total says1.000. The individual values, including Kingklip0.002, were visually checked and preserved.

## Biomass accumulation

Searched all 15 pages, methods equations on page4, Figures2/9/10 and the accumulation sweep. BA and migration are defined symbolically, but no static 1980 group BA value is given. Figure2 contains long-term biomass histories, not a declared Ecopath BA input; no slope was manufactured. Hoki stable age distribution is not a numerical BA statement. BA stays blank/-9999.

## Values from prose

Page4: model area approximately290,000 km²; year1980; three fleets (industrial trawl, artisanal vertical longline, artisanal bottom longline); hoki juvenile/adult definitions. Fleet catches are not apportioned by assumption.
Page3 Figure2 and page6 describe corrected landings accounting for discards/underreporting. This does not provide a numeric discard split, so Table3 Y was preserved as labeled.
No numeric assimilation efficiency or GS found in prose. Table2 supplies references/pedigree sources, not replacement numeric values.

## Conventions applied

None used to fill ecological inputs. No project 0.35/0.4 zooplankton GS defaults. The pooled reporting label is explicit because only total Y is available.

## Deliberate blanks

Habitat fractions, GS, BA, migration, other mortality, detritus routing/import/biomass, and unprinted catches/discards remain unknown. EwE may fill habitat1, GS0.2, BA0 and catch0 on import; these are software assumptions, not extracted source values. Primary producers/detritus have no Q/B or GS by definition.
Single detritus pool does not establish numeric routing or export fractions. No Taxonomy.xlsx is produced.

## Unresolved and flagged

Skates EE0.09 has no documented landings and no incoming predation in Table4; reconstructed EE from reported flows is0.000. Both cells checked visually. The suggested BA that would close this is not extracted.
Sea lions P/Q0.01 is printed and plausible for an endotherm; no adjustment.
The geography is broader than the archived LME label; the model is not a full Humboldt Current model.

## Validation

validate.py:0 errors,17 warnings (unknown GS, BA and 15 detritus fate rows).
Input mass balance:0 errors,2 warnings (Skates EE mismatch and low sea-lion P/Q).
All 13 diet sums within ±0.01; sea-lion1.002 retained. No numeric detritus-fate row is available.
Final source-preserving JSON check: INDETERMINATE. See below and ROUND_TRIP_AUDIT.md.

## Conversion and round trip

The installed Ecopath scripts wrote the eight import files and initial database JSON. Their converter normalizes non-unit diet columns, fills unknown habitat with 1, omits P/Q and loses fleet splits on workbook reconstruction. The local preserve_database.py adapter reverses those transformations using the CSV files, carries stated P/Q in ge, and preserves metadata, TL, fleet data and all eight source tables in JSON extensions. The final workbook is rebuilt from the saved JSON, with exact cell comparisons recorded in ROUND_TRIP_AUDIT.md. Unmodified converter results are archived in extracted/work and are not the final model.

Unknown habitat stays -9999. Biomass retains the publication's density over the model domain for mass-balance arithmetic; this does not assert a habitat fraction of 1. Unknown BA, GS, Z, detritus import, migration and prices are not populated from software defaults. Sparse blank diet cells mean absent prey links; missing complete fields remain unknown. The checker may assume GS=0.2 internally for diagnostic calculations, but that assumption is not written into source files.

## Reproduction

Use the source JSON in this model directory with the installed write_outputs.py, run validate.py and massbalance_check.py, run database_json.py, then run extracted/work/preserve_database.py with this model directory as its argument. The adapter is mandatory to retain unnormalized source values. Installed skill files were not changed.

## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for Chilean Patagonia, EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 1 indeterminate, 1 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 15 of 15 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.090, group 12 (Skates).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 14 (Sea lions, 0.014).

BA: not stated for any group. Every EE below is recomputed without a BA term, as a diagnostic with unreported terms omitted. It is not a bound because BA may be positive or negative.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 12 (Skates): printed EE 0.09 vs recomputed 0.000 (diff 0.090) with BA unknown - a BA of +0.0009855 t/km^2/year (+0.09 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 14 (Sea lions): P/Q = 0.014 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 13 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 2 (Microzooplankton), 3 (Mesozooplankton), 4 (Macrozooplankton), 5 (Benthos), 6 (Small pelagic fish), 7 (Other demersal fish), 8 (Hoki (j)), 9 (Hoki (a)) ...
- detritus pools (1): inflow ~1.948e+04, consumption ~419.2 t/km^2/year, implied EE ~0.022 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 146.2 | 137 | - | 0.05 | 0.052 | - | 0 | unknown |
| 2 | Microzooplankton | 0.67 | 534 | 1476 | 0.95 | 0.95 | 0.362 | 0 | unknown |
| 3 | Mesozooplankton | 7.271 | 14.6 | 40.15 | 0.95 | 0.95 | 0.364 | 0 | unknown |
| 4 | Macrozooplankton | 8.331 | 5.48 | 17.52 | 0.95 | 0.95 | 0.313 | 0 | unknown |
| 5 | Benthos | 11.64 | 2.7 | 36 | 0.24 | 0.239 | 0.075 | 0 | unknown |
| 6 | Small pelagic fish | 8.427 | 1.15 | 10 | 0.95 | 0.95 | 0.115 | 0 | unknown |
| 7 | Other demersal fish | 0.774 | 0.7 | 3.5 | 0.95 | 0.95 | 0.2 | 0 | unknown |
| 8 | Hoki (j) | 2.927 | 1.2 | 6.24 | 0.81 | 0.808 | 0.192 | 0.006 | unknown |
| 9 | Hoki (a) | 2.722 | 0.7 | 3.11 | 0.04 | 0.0388 | 0.225 | 0.056 | unknown |
| 10 | Southern blue whiting | 1.4 | 0.42 | 3.6 | 0.91 | 0.908 | 0.117 | 0.011 | unknown |
| 11 | Kingklip | 0.197 | 0.39 | 1.4 | 0.21 | 0.206 | 0.279 | 0.013 | unknown |
| 12 | Skates | 0.073 | 0.15 | 1.24 | 0.09 | 0 | 0.121 | 0 | unknown |
| 13 | Southern hake | 3.14 | 0.19 | 0.68 | 0.66 | 0.661 | 0.279 | 0.125 | unknown |
| 14 | Sea lions | 0.035 | 0.2 | 14.36 | 0 | 0 | 0.0139 | 0 | unknown |
| 15 | Detritus | - | - | - | 0.02 | - | - | 0 | unknown |


### Source-fidelity and completeness limits

These findings were recomputed from the final, unnormalized JSON. Known-flow EE checks omit unknown catch/BA/migration. The checker uses GS=0.2 internally for missing GS in respiration/detritus diagnostics only; the JSON retains -9999. Unstated detritus routing prevents pool-specific validation.

Diet columns outside +/-0.01: none.

The physiological check derives P/B divided by Q/B; any differently rounded stated P/Q is preserved separately in ge and Basic_input.csv.
