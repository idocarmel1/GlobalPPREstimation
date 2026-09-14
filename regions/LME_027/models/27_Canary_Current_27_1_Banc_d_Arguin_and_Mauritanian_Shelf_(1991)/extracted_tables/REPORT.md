# Banc d'Arguin and Mauritanian Shelf — Base (1991)

**Source:** Guénette S, Meissa B, Gascuel D (2014), Assessing the Contribution of Marine Protected Areas to the Trophic Functioning of Ecosystems: A Model for the Banc d'Arguin and the Mauritanian Shelf. PLOS ONE 9(4): e94742. DOI: 10.1371/journal.pone.0094742.

**LME:** 27 Canary Current. **Model number:** 27_1. **Groups:** 51 (50 living; 1 detritus). **Fleets:** Artisanal, Industrial demersal, Industrial pelagic. **Extracted:** 2026-09-04. **Status:** partial; publication values retained with explicit gaps.

## Eligibility and model identity
The source explicitly presents three balanced Ecopath parameterisations: Base, M30 and P30 (article pp. 2-5; Supplement Table S8). All represent 1991; 1991-2006 is the Ecosim fit interval. The catalog metadata value 2007-2009 is contradicted by the source and was not used. Habitat-loss, fictive-fleet, status-quo and 2056 endpoint simulations are dynamic scenarios, not separately parameterised static models. Supplement Table S9 2006 biomass/catch results are not another Ecopath snapshot.

## Source bundle and authority
README.md and metadata.json were read before extraction. The 16 top-level source files were inventoried. The 13 publication files match their recorded SHA-256 hashes (SOURCE_INVENTORY.json in the parent extraction directory).

- file-e30dfe50.pdf, 16 pages: article, static model Table 1 pp. 4-5, model scope/area pp. 2-3, scenarios p. 5, figures pp. 3 and 6-14.
- Table_1-f0424c0e.xls, one visible sheet Table_1 A1:N64, no hidden sheets/formulas: machine-readable version of article Table 1. Opened read-only in installed Excel, converted to an XLSX working copy in ../work; source never saved. HTML bold/italic tags were preserved separately and stripped from numeric text. The XLS and PDF table agree, including problematic zeros. This is the basic-input authority.
- Table_2-3434d627.xls, one visible sheet Table_2 A1:G6, no hidden sheets/formulas: aggregate food-web dependence percentages, not basic input.
- pone.0094742.s001-eb18ca66.docx: author supplement. Read document XML in source order, including all 11 physical tables, and rendered read-only using installed Word to ../work/supplement_rendered.pdf (21 pages). Text S1 pp. 1-6; Table S1 p. 7; Table S2 pp. 8-10; Table S3 and S4 p. 11; S5 p. 12; S6 p. 13; S7 p. 14; S8 pp. 15-16; S9 p. 17; Figure S1 p. 18. No supplementary numeric footnotes/endnotes outside the document body were found.
- Nine Figure_*.tif files were decoded and visually inventoried. Figure 1 gives area/map; Figures 2-3 depict dependence and trophic spectra; Figures 4-5 are 1991-2006 biomass/catch fits; Figure 6 compares trophic spectra; Figures 7-9 are simulated habitat/fishing outcomes. They do not supply a different static parameter set or a pre-1991 BA rate. No numbers were digitised from them.
- footprint.geojson supplies catalog geometry only; README and metadata are catalog context, not a substitute for published model parameters.

## Source tables
### Table 1 (article pp. 4-5; XLS Table_1 A1:N64)
Printed columns: number | Group name | TL | Biom (t/km2) | Z (/year | P/B/year | Q/B/year | EE | P/Q | BA | Artis. | Dem. | Pel. | Total.
Mapped to: n | name | tl | biomass | z | pb | qb | ee | pq | ba_rate | three catch fleets | sum check. BA units are resolved by Text S1 Fish (rendered p. 2), explicitly accumulation rates /year. Biomass and catches are already on the study-area density basis, so no 33,224 km2 division is applied. P/B and Q/B are annual rates.
51 groups, 47 consumers (1-47), 3 producers (48-50), 1 detritus pool (51). All eight import tables retain this group order; source diet row 52 is Import and is not a biological group. Figure and supplement abbreviations are mapped by published group number and name; the primary Table 1 names are retained exactly.
Columns were checked visually against both pages and arithmetically: Mackerel 0.45/3.0 = 0.150, Coastal M 0.58/2.9 = 0.200. Meagre P/B=0 conflicts with its nonzero Z and P/Q and remains as printed. Z is kept in its own field for multi-stanza groups; missing P/B is not silently replaced by Z. Source-stated producer/detritus zeros in Q/B/P/Q/P/B are retained even though ordinary import templates often leave them blank.
Bold values are Ecopath-estimated per Table 1 footnote; PROVENANCE.json records each basic parameter cell and the original markup. Italic biomass/QB cells for Croakers juv and Seabreams juv are retained and identified; the footnote only explicitly explains bold, so italics are not independently claimed to be measurements.

### Table S2 (DOCX physical tables 2-4; rendered pp. 8-10)
Prey rows 1-51 plus Import row 52; consumer blocks 1-15, 16-34, 35-47. Columns were matched to the explicit predator number and rows to the explicit prey number, then checked against the group names in the first block. OOXML preserves blank cells without coordinate guessing. PDF raw coordinates/visual renders support the audit; article Table 1 raw page coordinates are stored in ../work/page4_raw.txt. No layout-based plain-text table extraction was used.
The table entries are percentages: entire-food diets are 100 and most columns total approximately 100. Each stated numeric cell, including Import, is divided by exactly 100 using decimal arithmetic. No column is normalised; printed trailing precision is retained through decimal conversion. A source 00.10 is parsed numerically as 0.10 percent, not changed in magnitude. Blank cells remain blank.

### Table S8 (DOCX physical table 10; rendered pp. 15-16)
Headers distinguish imposed pBAi from balanced B/EE and from Ecosim vulnerability. B/EE columns are M30 6-7, Base 8-9, P30 10-11 (one-based physical cell columns). pBAi columns 3-5 are aggregate Banc-invertebrate diet shares, not new functional groups or a complete matrix. All 51 group rows are retained; unnumbered multi-stanza headings are skipped. S8 bold flags are captured in PROVENANCE.json. Vulnerability values are retained in SOURCE_DETAILS.json as contextual source data, not inserted into basic Ecopath inputs.

## Biomass accumulation
Table 1 column J states BA rates /year for groups 1-50. Nonzero rates: group 11 Coastal selacians, 23 Groupers ad, 24 Grouper juv and 27 Scianids each -0.05/year; group 30 Octopus vulgaris and 31 Cephalopods each -0.03/year. All other living groups have a printed zero. Detritus BA is blank. Negative signs and zeros were verified on article p. 4; Text S1 Fish p. 2 identifies these as rates estimated from trends before 1991, and balancing results p. 5 discuss their use. The absolute BA import column remains blank; database arithmetic may derive B times the rate and explicitly records that derivation.
The whole article and supplement, all tables/footnotes, and Figure 4 were searched. The 1991-2006 trajectories and Table S9 endpoints are Ecosim outputs; their slope is not substituted for the documented pre-1991 Ecopath BA. The 2056 equilibrium statement applies to forward simulations, not all 1991 groups. BA zero values here coincide with an EwE default because the paper actually states them.

## Values from prose
- Model year 1991, article p. 2; model area 33,224 km2 including Banc d'Arguin, article pp. 2-3. Area is documented but not inserted as habitat fraction.
- BA units and sign, Text S1 Fish p. 2, resolve the abbreviated column without changing numbers.
- Source catch data contain no information about discards (article p. 2; Text S1 Fishing data p. 3). The three reported catch series go into Landings as requested by the skill's total-catch rule; Discards remain unknown.
- Text S1 p. 1 discusses P/B=Z under equilibrium, while the table reports multi-stanza Z separately and nonzero BA in several groups. Consequently no universal replacement of P/B by Z is made.

## Conventions applied
No missing biological parameter was filled from EwE defaults or zooplankton conventions. Only exact percentage-to-proportion conversion was applied to S2 diet numbers. Fleet abbreviations Artis./Dem./Pel. are expanded to Artisanal/Industrial demersal/Industrial pelagic from source prose. Model names omit punctuation for portable directory naming; the actual citation preserves Banc d'Arguin.

## Deliberate blanks
After searching the whole bundle, GS/unassimilated consumption is unknown for every group, habitat-area proportion is unknown, detritus import/routing/export is not stated, and other mortality is not tabulated. The single detritus pool does not justify inventing a fate fraction of 1. EwE may default GS to 0.2, habitat to 1, catches/discards to 0 and unallocated detritus to export; these defaults are not source data and are not written into unknown extraction cells.
P/B is blank for groups 14-19 and 23-26 where Z is printed; the two Meagre P/B zeros are explicit, not blanks. Discards are entirely unknown. Detritus BA is unknown. Taxonomy.xlsx is outside scope. The database adapter records missing values as -9999 and retains stated zero separately.

## Unresolved and flagged
- Table S2 group 23 Groupers ad has prey 32 BA L crustaceans = 134 percent (rendered p. 9), an impossible single diet component. The resulting column sum is 220.06 percent (2.2006). The visual source unequivocally says 134; a plausible decimal correction to 13.4 is not authorised and is not made.
- Coastal birds column 2 sums to 98.0331 percent (0.980331), verified across every p. 8 row including Import 0.02 percent. No residual is invented.
- Meagre ad/juv P/B=0 while Z=0.21/0.3 and P/Q=0.100/0.017 (Table 1 p. 4). These source conflicts and multi-stanza structure limit mass-balance checks; the deliverables do not reconstruct stanza growth links.
- Table 1 BA phytoplankton B=5.9, EE=0.260 differs from S8 Base B=6, EE=0.40; recomputed EE using S2 is about 0.398. Table 1 remains the base authority. The arithmetic supports a source inconsistency, not permission to overwrite it.
- S8 differs from Table 1 mostly through rounding, including juvenile biomasses. SOURCE_DETAILS.json preserves every compared cell and all S8 rows. S9 gives initialization/output numbers with still different precision; these are retained context, not mixed into the static Table 1 input set.
- Text S1 balancing results say P/Q fixed at 0.2 for sardine/mackerel/horse mackerel, while Table 1 prints 0.150 for sardine/mackerel and 0.200 for horse mackerel. Structured Table 1 values are retained.
- Article p. 5 says M30 Banc share changes from 0.50 to 0.25; S8 gives 0.33 for those consumers. S8 parameter constraints are preserved and this prose discrepancy remains unresolved.
- Marine mammal P/Q=0.003 and bird P/Q=0.004 are genuinely printed; low homeotherm gross efficiency is not evidence of a column slip. Meagre juvenile P/Q=0.017 is also printed. Producer P/Q=0 is not a consumer physiology error.

## Variant scope
Base Table 1 supplies all stated basic inputs, catch and trophic levels. The full published S2 diet matrix is preserved including the two invalid column totals. This extraction is therefore source-faithful but partial for operational loading because of missing GS/routing/habitat and unresolved publication inconsistencies.

## Validation
Bundled validate.py: **2 error(s), 52 warning(s)**. See VALIDATION.txt for every flagged row/column. All file/group/header/CRLF/total checks ran. The base diet totals range from 0.980331 to 2.2006; affected variants have incomplete columns as documented above. Missing detritus fate produces 51 warnings; all-GS blank produces one; rounded zero juvenile biomasses account for the variants' additional 3 warnings. All flagged source values were checked on article pp. 4-5 and rendered Supplement pp. 8-10 and 15-16.

Bundled massbalance_check.py: 0 error(s), 7 warning(s), 41 note(s). Its detritus calculation is indicative because GS/routing are missing. It cannot test groups with missing/zero P/B. The final database analysis below includes extra integrity/missing-data guards.

Database source-preservation adapter ../work/audit_database.py corrects stock converter normalisation/defaulting and dropped fields, retaining exact CSV values and -9999 unknowns. The official bundled converter was run first, with original logs saved under ../work. The final section of ewe_conversion.log supersedes the preliminary stock-conversion values/verdict; the original pipeline record is also retained under ../work. ge retains source P/Q; z retains Z; the JSON extension holds all eight original import tables. The reconstructed XLSX is rebuilt solely from the final JSON extension and verified cell-by-cell against those eight files. No installed skill was modified.

## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 27_Canary_Current_27_1_Banc_d_Arguin_and_Mauritanian_Shelf_(1991), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 1 of 51 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.138, group 48 (BA phytopl.).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (Marine mammals, 0.003), 2 (Coastal birds, 0.004).

BA: carried for 50 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Marine mammals, +0), 2 (Coastal birds, +0), 3 (Meagre ad, +0), 4 (Meagre juv, +0), 5 (Mullets, +0), 6 (Pelagic L, +0), 7 (Mackerel, +0), 8 (Sardine, +0), 9 (Sardinelles, +0), 10 (Horse mackerels, +0), 11 (Coastal selacians, -0.062), 12 (Coastal M, +0), 13 (Coastal S, +0), 14 (Croakers ad, +0), 15 (Croakers juv, +0), 16 (Seabreams ad, +0), 17 (Seabreams juv., +0), 18 (Catfish ad, +0), 19 (Catfish juv, +0), 20 (Shelf selacians, +0), 21 (Shelf L, +0), 22 (Shelf M, +0), 23 (Groupers ad, -0.0055), 24 (Grouper juv, -2e-05), 25 (Sparids ad, +0), 26 (Sparids juv, +0), 27 (Scianids, -0.011), 28 (Shelf soles, +0), 29 (Shelf S, +0), 30 (Octopus vulgaris, -0.0411), 31 (Cephalopods, -0.03), 32 (BA L crustaceans, +0), 33 (BA molluscs, +0), 34 (BA worms, +0), 35 (BA crustaceans, +0), 36 (BA other inverts, +0), 37 (BA meiobenthos, +0), 38 (shelf L crustaceans, +0), 39 (shelf molluscs, +0), 40 (shelf worms, +0), 41 (shelf crustaceans, +0), 42 (shelf other inverts, +0), 43 (shelf meiobenthos, +0), 44 (mesozoopl., +0), 45 (macrozoopl., +0), 46 (BA mesozoopl., +0), 47 (BA macrozoopl., +0), 48 (BA phytopl., +0), 49 (phytoplankton, +0), 50 (algae and eelgrass, +0). The remaining 1 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 1 (Marine mammals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (Coastal birds): P/Q = 0.004 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 48 (BA phytopl.): printed EE 0.26 vs recomputed 0.398 (diff 0.138), BA 0 carried

### Notes

- 40 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (Marine mammals), 2 (Coastal birds), 3 (Meagre ad), 4 (Meagre juv), 5 (Mullets), 6 (Pelagic L), 7 (Mackerel), 8 (Sardine) ...
- detritus pools (1): inflow ~7023, consumption ~3794 t/km^2/year, implied EE ~0.540 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Marine mammals | 0.01 | 0.04 | 12.5 | 0 | 0 | 0.0032 | 0 | 0 |
| 2 | Coastal birds | 0.01 | 0.28 | 67 | 0 | 0 | 0.00418 | 0 | 0 |
| 3 | Meagre ad | 0.12 | 0 | 2.1 | 0.657 | - | - | 0.014 | 0 |
| 4 | Meagre juv | 5e-05 | 0 | 17.9 | 0.974 | - | - | 0 | 0 |
| 5 | Mullets | 0.42 | 0.8 | 8.2 | 0.8 | 0.795 | 0.0976 | 0.103 | 0 |
| 6 | Pelagic L | 3.42 | 0.96 | 5.4 | 0.9 | 0.9 | 0.178 | 2.679 | 0 |
| 7 | Mackerel | 1.45 | 0.45 | 3 | 0.735 | 0.735 | 0.15 | 0.289 | 0 |
| 8 | Sardine | 11.79 | 0.65 | 4.3 | 0.771 | 0.77 | 0.151 | 1.801 | 0 |
| 9 | Sardinelles | 18 | 0.99 | 7.7 | 0.785 | 0.785 | 0.129 | 2.31 | 0 |
| 10 | Horse mackerels | 10 | 0.72 | 3.6 | 0.844 | 0.844 | 0.2 | 3.812 | 0 |
| 11 | Coastal selacians | 1.24 | 0.3 | 2 | 0.015 | 0.0147 | 0.15 | 0.063 | -0.062 |
| 12 | Coastal M | 0.83 | 0.58 | 2.9 | 0.858 | 0.861 | 0.2 | 0.121 | 0 |
| 13 | Coastal S | 4.21 | 0.62 | 3.1 | 0.95 | 0.952 | 0.2 | 0 | 0 |
| 14 | Croakers ad | 0.077 | - | 3.9 | 0.754 | - | - | 0.003 | 0 |
| 15 | Croakers juv | 0.004 | - | 9.9 | 0.706 | - | - | 0 | 0 |
| 16 | Seabreams ad | 1.69 | - | 4.7 | 0.884 | - | - | 0.167 | 0 |
| 17 | Seabreams juv. | 0.012 | - | 21.1 | 0.884 | - | - | 0 | 0 |
| 18 | Catfish ad | 0.6 | - | 4.1 | 0.226 | - | - | 0.034 | 0 |
| 19 | Catfish juv | 0.002 | - | 22.3 | 0.78 | - | - | 0 | 0 |
| 20 | Shelf selacians | 0.2 | 0.24 | 1.6 | 0.787 | 0.794 | 0.15 | 0.011 | 0 |
| 21 | Shelf L | 0.36 | 0.47 | 3.4 | 0.467 | 0.467 | 0.138 | 0.071 | 0 |
| 22 | Shelf M | 1.55 | 0.57 | 6.2 | 0.908 | 0.913 | 0.0919 | 0.146 | 0 |
| 23 | Groupers ad | 0.11 | - | 3.2 | 0.938 | - | - | 0.025 | -0.0055 |
| 24 | Grouper juv | 0.0004 | - | 16.2 | 0.536 | - | - | 0 | -2e-05 |
| 25 | Sparids ad | 1.29 | - | 2.4 | 0.871 | - | - | 0.014 | 0 |
| 26 | Sparids juv | 0.01 | - | 9.8 | 0.939 | - | - | 0 | 0 |
| 27 | Scianids | 0.22 | 0.29 | 4.3 | 0.665 | 0.654 | 0.0674 | 0.017 | -0.011 |
| 28 | Shelf soles | 0.35 | 0.58 | 2.9 | 0.882 | 0.886 | 0.2 | 0.009 | 0 |
| 29 | Shelf S | 6.195 | 0.82 | 7.6 | 0.95 | 0.951 | 0.108 | 0.005 | 0 |
| 30 | Octopus vulgaris | 1.37 | 1.4 | 4.7 | 0.632 | 0.632 | 0.298 | 0.883 | -0.0411 |
| 31 | Cephalopods | 1 | 1.2 | 4 | 0.839 | 0.84 | 0.3 | 0.255 | -0.03 |
| 32 | BA L crustaceans | 9.12 | 1.44 | 7.2 | 0.877 | 0.878 | 0.2 | 0 | 0 |
| 33 | BA molluscs | 17.86 | 1.5 | 16.7 | 0.888 | 0.89 | 0.0898 | 0 | 0 |
| 34 | BA worms | 5.32 | 3 | 33.3 | 0.805 | 0.806 | 0.0901 | 0 | 0 |
| 35 | BA crustaceans | 1.14 | 2.4 | 12 | 0.975 | 0.975 | 0.2 | 0 | 0 |
| 36 | BA other inverts | 0.57 | 1.8 | 9 | 0.868 | 0.869 | 0.2 | 0 | 0 |
| 37 | BA meiobenthos | 2.09 | 9 | 100 | 0.93 | 0.93 | 0.09 | 0 | 0 |
| 38 | shelf L crustaceans | 8.1 | 1.5 | 7.5 | 0.732 | 0.734 | 0.2 | 0.005 | 0 |
| 39 | shelf molluscs | 26.21 | 1.5 | 16.7 | 0.5 | 0.5 | 0.0898 | 3e-06 | 0 |
| 40 | shelf worms | 31.77 | 3 | 33 | 0.409 | 0.409 | 0.0909 | 0 | 0 |
| 41 | shelf crustaceans | 8.04 | 2.4 | 12 | 0.797 | 0.796 | 0.2 | 0 | 0 |
| 42 | shelf other inverts | 17.21 | 1.8 | 9 | 0.224 | 0.224 | 0.2 | 0 | 0 |
| 43 | shelf meiobenthos | 8.91 | 9 | 100 | 0.253 | 0.253 | 0.09 | 0 | 0 |
| 44 | mesozoopl. | 55.08 | 24 | 112 | 0.146 | 0.146 | 0.214 | 0 | 0 |
| 45 | macrozoopl. | 3.41 | 4.3 | 17 | 0.728 | 0.728 | 0.253 | 0 | 0 |
| 46 | BA mesozoopl. | 1.78 | 24 | 112 | 0.8 | 0.801 | 0.214 | 0 | 0 |
| 47 | BA macrozoopl. | 2.5 | 4.3 | 17 | 0.8 | 0.8 | 0.253 | 0 | 0 |
| 48 | BA phytopl. | 5.9 | 100 | 0 | 0.26 | 0.398 | - | 0 | 0 |
| 49 | phytoplankton | 67.8 | 100 | 0 | 0.853 | 0.852 | - | 0 | 0 |
| 50 | algae and eelgrass | 548.8 | 4.06 | 0 | 0.011 | 0.00785 | - | 0 | 0 |
| 51 | Detritus | 560 | 0 | 0 | 0.455 | - | - | 0 | unknown |
