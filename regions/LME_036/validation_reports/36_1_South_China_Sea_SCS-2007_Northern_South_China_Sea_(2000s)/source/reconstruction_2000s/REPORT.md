# Northern South China Sea (2000s)

**Status: partial reconstruction; balance INDETERMINATE.** Published core parameters, diets and catches have been extracted. Missing source fields and inconsistencies prevent a claim that this is a fully reproduced or load-tested native EwE model.

**Source:** Cheung, Wai Lung (2007). *Vulnerability of marine fishes to fishing: from global overview to the northern South China Sea*. University of British Columbia doctoral thesis. DOI 10.14288/1.0074894. Local source: `ubc_2007-317501-87ea9ea0.pdf`.
**LME:** 36 South China Sea. **Coverage:** northern continental shelf, mainly the Chinese EEZ; not the whole LME (printed p.170 / PDF p.185).
**Model identifier:** SCS-2007, the existing archive source identifier used as a surrogate in `model_number`; this is not a verified EcoBase numeric ID. Metadata reports EcoBase 410 without a verified period mapping, so it was not assigned to either model.
**Period:** 2000s; retained as a decade label, not an invented single year.
**Groups:** 38 (35 consumers, 2 primary producers, 1 detritus). **Fleets:** Pair and stern trawl, Shrimp trawl, Purse seine, Hook and line, Gillnet, Other fishing gears.
**Extracted:** 2026-09-04.

## Source inventory and authority

README.md and metadata.json were read first. The bundle contains one 369-page thesis and those two archive reference files; no supplement, workbook or native model is present. `../SOURCE_INVENTORY.json` records sizes and hashes. PDF printed pages are PDF page minus 15 in the relevant chapters. Core sources: Table 6.1 pp.175-176 / PDF 190-191; Table 6.2 pp.178-179 / PDF 193-194; Table 6.5 p.190 / PDF 205; Appendix 6.1 pp.322-341 / PDF 337-356; Appendix 6.2 pp.342-348 / PDF 357-363.

Final chapter tables take precedence over conflicting appendix parameterization prose. Alternatives remain listed in `../SOURCE_CONFLICTS.md`. Parenthesized values are retained and tagged as Ecopath estimates per Table 6.1 caption. All supplied source files are unchanged.

## Source tables

### Table 6.1 - basic inputs

Columns: Group no. | Functional group | B | P/B | Q/B | EE. Mapping: n | name | biomass | pb | qb | ee. There are exactly 38 rows per period, in the original order. Units are t/km2 wet weight for B and /year for P/B and Q/B, supported by Appendix 6.1. Dashes and empty cells stay blank. Right-aligned numeric columns were mapped using their PDF coordinates, approximately x=365,410,456,501 points. The 1970s jellyfish row checks the mapping: P/B=5.00, Q/B=20.0, giving diagnostic P/Q=0.25; EE=0.950.

Names were matched across tables using an explicit abbreviation map (Juv./Juvenile, Ad./Adult, Dem./Demersal; plankton singular/plural; taxonomic suffixes). The source spelling 'Demesral' is retained. The optical text layer's '<' in small-group labels was restored to the visible '≤'; whitespace around '>30' was standardized. No groups were merged or renumbered.

### Appendix 6.2 - diet composition

The appendix is labelled for both periods and contains one shared set of 35 predator columns. Prey are rows, predators are columns. There are 417 printed nonblank fractions. All ten blocks across seven pages were extracted from word coordinates with `pdfgrid.get_words(merge_gap=0.4)` and checked against 200-dpi images. Wrapped labels were joined before matching group names. Numeric right-edge clusters were aligned to the named predator headers; exact mappings are retained below and in `../work/table_layouts.json`.

| Printed / PDF page | Predator group numbers | Raw body line indices (inclusive) | Right-edge anchors (points) |
|---|---|---|---|
| 342 / 357 | 3, 4 | [3, 8] | 301.92, 353.08 |
| 342 / 357 | 5, 6, 7, 8, 9 | [13, 23] | 249.27, 316.84, 383.71, 437.76, 510.19 |
| 342 / 357 | 10, 11 | [27, 37] | 240.04, 283.99 |
| 343 / 358 | 12 | [2, 19] | 296.71 |
| 343 / 358 | 13, 14, 15 | [23, 43] | 306.38, 375.04, 441.91 |
| 344 / 359 | 16, 17, 18 | [3, 26] | 307.30, 375.65, 443.13 |
| 345 / 360 | 19, 20, 21, 22, 23 | [3, 27] | 289.11, 343.21, 398.86, 447.60, 498.56 |
| 346 / 361 | 24, 25, 26, 27 | [3, 29] | 298.43, 370.80, 443.48, 515.43 |
| 347 / 362 | 28, 29, 30, 31 | [3, 24] | 289.31, 361.63, 443.02, 506.17 |
| 348 / 363 | 32, 33, 34, 35, 36, 37 | [4, 46] | 248.69, 302.61, 351.13, 411.46, 465.75, 520.20 |

All 38 prey rows are retained, including primary producers and detritus; consumers are groups 3-37. Empty matrix cells remain empty. Diet Import is 0 under the skill's explicit no-reported-import convention, not a separately tabulated source observation. No diet fractions were normalized, including in the database JSON.

### Table 6.2 - catches

Columns: group | 1970s total | 2000s PSt | ShT | PS | H&L | GN | Others | total. PSt=pair and stern trawl; ShT=shrimp trawl; PS=purse seine; H&L=hook and line; GN=gillnet. Both parts were joined by group name to give 38 rows. The 1970s uses one aggregate column labelled Total fishery; the 2000s retains all six fleet columns. Reported catch is written to Landings; no discard split is supplied. These are annual catches (Table caption density units t/km2; Appendix 6.1 and chapter methods specify annual landings). No area conversion is applied.

Sum of extracted catch entries: **7.7375 t/km2/year**. The printed 1970s grand total is 0.8500 versus sum 0.8501. For the 2000s the six-fleet cell sum is 7.7375 versus printed grand total 7.736; printed group totals sum to 7.738. Generated Total cells use exact decimal sums of fleet entries. `SOURCE_CATCH_TOTALS.json` preserves each printed total so the differences remain reviewable.

### Table 6.5 - mortality outputs

Columns: group | 1970s F | M | M0 | 2000s F | M | M0. M0 is carried verbatim as an annual other-mortality rate for 37 living groups; detritus has no row. F and the column labelled M are retained in `SOURCE_MORTALITIES.json` for diagnostics. The M column behaves as predation mortality (M0 is separately listed), despite the caption saying natural mortality. No F+M or other sum was substituted for P/B. Some mortality rows do not reproduce Table 6.1 precisely; final table values remain separate.

## Biomass accumulation

Searched chapter6 and Appendix 6.1-6.2, then the entire thesis text for biomass accumulation, BA, dB/dt, steady state, migration and biomass change. Ecopath is described as steady-state on p.172 / PDF 187. The thesis revisits the steady-state assumption on p.289 / PDF 304. Equation6.1 defines BA but supplies no group-specific numeric BA. Figures6.2-6.5 compare period snapshots, not model-year accumulation; Ecosim trajectories in later chapters are simulations. No numeric BA was extracted. Both BA columns remain blank, and both database fields are -9999. No residual from the balance check was entered as data. No numeric net migration term was found for these static models.

## Values from prose

- Group 5 (Polychaetes): pq = 0.3; PDF p. 339 (printed p. 324). prose-stated assumption.
- Group 18 (Pomfret (stromateids)): pq = 0.2; PDF p. 346 (printed p. 331). prose-stated assumption.
- Group 27 (Benthopelagic fish): pq = 0.2; PDF p. 352 (printed p. 337). prose-stated assumption.
- Group 32 (Demersal sharks and rays): pq = 0.2; PDF p. 355 (printed p. 340). prose-stated assumption.
- Group 33 (Pelagic sharks and rays): pq = 0.2; PDF p. 355 (printed p. 340). prose-stated assumption.
- Group 7 (Benthic crustaceans): z = 5.65; PDF p. 339 (printed p. 324). prose-stated PB=Z; matching final table.
- Group 10 (Shrimps): z = 7.60; PDF p. 341 (printed p. 326). prose-stated PB=Z; matching final table.
- Group 13 (Threadfin bream (nemipterids)): z = 3.08; PDF p. 342 (printed p. 327). prose-stated PB=Z; matching final table.
- Group 14 (Bigeyes (priacanthids)): z = 3.33; PDF p. 342 (printed p. 327). prose-stated PB=Z; matching final table.
- Group 21 (Croakers (≤ 30 cm)): z = 3.30; PDF p. 348 (printed p. 333). prose-stated PB=Z; matching final table.
- Group 23 (Croakers (> 30 cm)): z = 1.43; PDF p. 349 (printed p. 334). prose-stated PB=Z; matching final table.
- Group 24 (Demesral fish (≤ 30 cm)): z = 4.70; PDF p. 350 (printed p. 335). prose-stated PB=Z; matching final table.
- Group 25 (Juvenile demersal fish (> 30 cm)): z = 3.50; PDF p. 351 (printed p. 336). prose-stated PB=Z; matching final table.
- Group 26 (Adult demersal fish (> 30 cm)): z = 2.10; PDF p. 351 (printed p. 336). prose-stated PB=Z; matching final table.
- Group 27 (Benthopelagic fish): z = 3.08; PDF p. 352 (printed p. 337). prose-stated PB=Z; matching final table.
- Group 28 (Melon seed): z = 2.41; PDF p. 347 (printed p. 332). prose-stated PB=Z; matching final table.
- Group 29 (Pelagic fish (≤ 30 cm)): z = 4.26; PDF p. 353 (printed p. 338). prose-stated PB=Z; matching final table.

P/Q assumptions are copied only where the text scopes them to the period/group. In particular, the pomfret assumption 0.2 slightly differs from the 1970s table-derived ratio 1.30/6.38; both are retained with distinct provenance. Total mortality Z is populated only for explicitly stated, matching P/B=Z cases. Appendix assumptions that disagree with the final basic table are not used to backfill Z.

## Conventions applied

No GS, BA, habitat, detritus routing or discard defaults were inserted into source fields. The only explicit numerical output convention is Diet Import0 when no import is reported. Decade labels and the source identifier are retained. The single aggregate 1970s fleet name is an output label.

## Deliberate blanks

The full bundle and whole-thesis text were searched, with a second targeted search after table extraction.

- Unassimilated consumption: no numerical assumption found for any consumer. All GS cells blank; EwE may use0.2 on import. The checker uses 0.2 for diagnostic respiration/detritus calculations, but this is not a paper value. No 0.35/0.4 zooplankton convention was authorized or applied. Producer/detritus GS is inapplicable.
- Habitat area: no group habitat fractions reported. CSV blank, database -9999. Biomass is the paper's model-area density; internal arithmetic uses that common area basis, without a biological habitat restriction. EwE's default habitat proportion is 1.
- Discards: not separated numerically from the published catch. Blank, not evidence of zero; catch remains in Landings. EwE may import blank discards as0.
- Detritus fate/export routing and detritus import: no numerical routing or import statement located. One detritus pool does not establish that 100% of all mortality enters it. Fate and import cells stay blank; database unknown fates are -9999. The checker's pooled detritus calculation is indicative and cannot validate this missing routing. EwE may export an unspecified routing remainder.
- Trophic levels: no complete group-specific numeric TL table located. TL.xlsx includes all 38 groups with blank TL cells; TL values were not manufactured from the matrix or read as false-precision values from a graph.
- Other blank Z/PQ cells: no unambiguous final-period numeric statement. No derived replacements.

## Model-estimated values

Parentheses in Table 6.1 denote values estimated by Ecopath. All are retained with this category in `PROVENANCE.json`.

| Group | Name | Field | Printed value |
|---|---|---|---|
| 1 | Phytoplankton | ee | (0.010) |
| 2 | Benthic producer | ee | (0.010) |
| 3 | Zooplankton | ee | (0.306) |
| 4 | Jellyfish | ee | (0.520) |
| 5 | Polychaetes | ee | (0.673) |
| 6 | Echinoderms | ee | (0.444) |
| 7 | Benthic crustaceans | ee | (0.617) |
| 8 | Non-ceph molluscs | ee | (0.951) |
| 9 | Sessile/other invertebrates | ee | (0.575) |
| 10 | Shrimps | biomass | (0.194) |
| 10 | Shrimps | ee | (0.950) |
| 11 | Crabs | biomass | (0.368) |
| 11 | Crabs | ee | (0.950) |
| 12 | Cephalopods | ee | (0.393) |
| 13 | Threadfin bream (nemipterids) | ee | (0.847) |
| 14 | Bigeyes (priacanthids) | ee | (0.550) |
| 15 | Lizard fish (synodontids) | ee | (0.658) |
| 16 | Juvenile Hairtail (trichiurids) | ee | (0.749) |
| 17 | Adult hairtail (trichiurids) | ee | (0.545) |
| 18 | Pomfret (stromateids) | qb | (15.15) |
| 19 | Snappers | biomass | (0.0013) |
| 20 | Adult groupers | biomass | (0.0064) |
| 21 | Croakers (≤ 30 cm) | ee | (0.958) |
| 22 | Juvenile large croakers | ee | (0.564) |
| 23 | Croakers (> 30 cm) | ee | (0.587) |
| 24 | Demesral fish (≤ 30 cm) | biomass | (0.316) |
| 25 | Juvenile demersal fish (> 30 cm) | ee | (0.722) |
| 26 | Adult demersal fish (> 30 cm) | ee | (0.747) |
| 27 | Benthopelagic fish | ee | (0.479) |
| 28 | Melon seed | ee | (0.994) |
| 29 | Pelagic fish (≤ 30 cm) | ee | (0.740) |
| 30 | Juvenile large pelagic fish | ee | (0.622) |
| 31 | Pelagic fish (> 30 cm) | ee | (0.759) |
| 32 | Demersal sharks and rays | ee | (0.867) |
| 33 | Pelagic sharks and rays | biomass | (0.0011) |
| 34 | Seabirds | ee | (0.046) |
| 35 | Pinnipeds | ee | (0.290) |
| 36 | Other mammals | ee | (0.034) |
| 37 | Marine turtles | ee | (0.300) |
| 38 | Detritus | ee | (0.005) |

## Unresolved and flagged

See `../SOURCE_CONFLICTS.md` for the cross-source conflict register. The appendix discusses an extra large-benthopelagic group which has no row in the final38-group table; it was not added. Juvenile/adult groups are kept separate. Appendix TableA6.3 provides stanza-growth settings beyond the eight-file schema; these are documented in `../MULTISTANZA.md`. Native stanza linkage and a native EwE load test have not been performed.

The 1970s turtle table values B 0.0002 and P/B 0.100 imply production 0.00002, while printed catch is 0.0001. This is a source-level inconsistency confirmed in the rendered tables. Table 6.5 instead prints F 0.05, which would imply 0.00001 catch with that B; the latter is a diagnostic inference and was not substituted. The 2000s pinniped catch is printed as zero in Table 6.2 although Table 6.5 F 0.01 is nonzero. Several 1970s diet/predation results disagree with the printed EE beyond rounding. Rechecking the source matrix did not reveal shifted columns. A shared published matrix may not fully reproduce both final parameterizations; a native author model would be needed to resolve that possibility.

## Validation

`validate.py`: **0 errors,41 warnings**: one aggregate GS warning, one all-blank BA warning,38 unknown detritus-fate rows, one warning covering38 blank TLs. All CSVs use consistent38-group numbering and CRLF. All35 diet sums are within±0.01 (range 0.9990 to1.0011). Non-unit sums below are preserved.

| Consumer | Name | Diet sum |
|---|---|---|
| 12 | Cephalopods | 0.99947 |
| 20 | Adult groupers | 0.9990 |
| 21 | Croakers (≤ 30 cm) | 0.9990 |
| 22 | Juvenile large croakers | 0.9990 |
| 23 | Croakers (> 30 cm) | 1.0003 |
| 24 | Demesral fish (≤ 30 cm) | 0.9992 |
| 25 | Juvenile demersal fish (> 30 cm) | 0.9999 |
| 26 | Adult demersal fish (> 30 cm) | 0.9998 |
| 27 | Benthopelagic fish | 1.0002 |
| 30 | Juvenile large pelagic fish | 1.0006 |
| 31 | Pelagic fish (> 30 cm) | 0.9997 |
| 32 | Demersal sharks and rays | 0.9991 |
| 33 | Pelagic sharks and rays | 1.0011 |
| 34 | Seabirds | 1.0002 |
| 36 | Other mammals | 1.0003 |
| 37 | Marine turtles | 0.9996 |

`MASS_BALANCE_SOURCE.txt` preserves the source-file arithmetic check. Database check: **INDETERMINATE**, with 7 EE discrepancies beyond 0.05 and 3 low-P/Q warnings for birds/mammals. The source-file checker reports 0 errors and 10 warnings; its hard turtle error assumes no BA. The database checker treats unknown BA explicitly, hence the different verdict wording. Neither result establishes a balanced native model. The low-P/Q values were visually confirmed and retained.

## Conversion and round-trip limitations

The installed converter normalized diet columns and filled several missing fields with defaults. A local copy under `../work/` was adapted to preserve source diet fractions, missing habitat/fate values, and P/Q, and to read metadata from the sibling workbook. `converter_changes.patch` records the exact differences; the installed skill is untouched. The source CSV/XLSX files and `model.json` are the authoritative extraction. The database JSON stores density biomass on the model-area basis; unknown fields use -9999. Its reconstruction workbook consolidates catches and does not reproduce individual fleets, all-zero catch rows, Z, or blank TL/BA sheets. It is a round-trip inspection artifact, not a substitute for the eight import files.

## Mass balance

Checked by the source-preserving local copy of `database_json.py` on the assembled JSON for 36_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s), EE tolerance 0.05.

**Verdict: INDETERMINATE** - 0 error(s), 7 indeterminate, 3 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 38 of 38 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.288, group 35 (Pinnipeds).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 34 (Seabirds, 0.001), 35 (Pinnipeds, 0.003), 36 (Other mammals, 0.011).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is an assumption for this diagnostic calculation; negative or positive unreported BA would change it in either direction.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Indeterminate (BA unknown)

- group 4 (Jellyfish): printed EE 0.52 vs recomputed 0.440 (diff 0.080) with BA unknown - a BA of +0.6156 t/km^2/year (+0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 15 (Lizard fish (synodontids)): printed EE 0.658 vs recomputed 0.780 (diff 0.122) with BA unknown - a BA of -0.006243 t/km^2/year (-0.12 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 23 (Croakers (> 30 cm)): printed EE 0.587 vs recomputed 0.665 (diff 0.078) with BA unknown - a BA of -0.001043 t/km^2/year (-0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 25 (Juvenile demersal fish (> 30 cm)): printed EE 0.722 vs recomputed 0.780 (diff 0.058) with BA unknown - a BA of -0.02928 t/km^2/year (-0.06 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 26 (Adult demersal fish (> 30 cm)): printed EE 0.747 vs recomputed 0.832 (diff 0.085) with BA unknown - a BA of -0.003729 t/km^2/year (-0.08 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 35 (Pinnipeds): printed EE 0.29 vs recomputed 0.002 (diff 0.288) with BA unknown - a BA of +5.966e-05 t/km^2/year (+0.29 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed
- group 37 (Marine turtles): printed EE 0.3 vs recomputed 0.019 (diff 0.281) with BA unknown - a BA of +5.626e-06 t/km^2/year (+0.28 of production) would close it - undecidable: this may be an extraction error or the BA the source never printed

### Warnings

- group 34 (Seabirds): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 35 (Pinnipeds): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 36 (Other mammals): P/Q = 0.011 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 35 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 3 (Zooplankton), 4 (Jellyfish), 5 (Polychaetes), 6 (Echinoderms), 7 (Benthic crustaceans), 8 (Non-ceph molluscs), 9 (Sessile/other invertebrates), 10 (Shrimps) ...
- detritus pools (1): inflow ~1.297e+05, consumption ~627.6 t/km^2/year, implied EE ~0.005 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 323 | 398 | - | 0.01 | 0.00952 | - | 0 | unknown |
| 2 | Benthic producer | 153 | 11.89 | - | 0.01 | 0.0103 | - | 0.0056 | unknown |
| 3 | Zooplankton | 9 | 32 | 192 | 0.306 | 0.306 | 0.167 | 0.0948 | unknown |
| 4 | Jellyfish | 1.53 | 5 | 20 | 0.52 | 0.44 | 0.25 | 0.044 | unknown |
| 5 | Polychaetes | 2.24 | 6.75 | 22.5 | 0.673 | 0.673 | 0.3 | 0 | unknown |
| 6 | Echinoderms | 1.98 | 1.2 | 3.58 | 0.444 | 0.444 | 0.335 | 0.0021 | unknown |
| 7 | Benthic crustaceans | 1.43 | 5.65 | 26.9 | 0.617 | 0.619 | 0.21 | 0.0391 | unknown |
| 8 | Non-ceph molluscs | 2.68 | 3.5 | 11.7 | 0.951 | 0.951 | 0.299 | 0.7623 | unknown |
| 9 | Sessile/other invertebrates | 2.61 | 1 | 9 | 0.575 | 0.575 | 0.111 | 0.003 | unknown |
| 10 | Shrimps | 0.194 | 7.6 | 28.94 | 0.95 | 0.953 | 0.263 | 0.6788 | unknown |
| 11 | Crabs | 0.368 | 3 | 12 | 0.95 | 0.954 | 0.25 | 0.1997 | unknown |
| 12 | Cephalopods | 0.68 | 3.1 | 8 | 0.393 | 0.394 | 0.388 | 0.2733 | unknown |
| 13 | Threadfin bream (nemipterids) | 0.26 | 3.08 | 15.4 | 0.847 | 0.88 | 0.2 | 0.657 | unknown |
| 14 | Bigeyes (priacanthids) | 0.13 | 3.33 | 11.3 | 0.55 | 0.538 | 0.295 | 0.206 | unknown |
| 15 | Lizard fish (synodontids) | 0.032 | 1.6 | 5.407 | 0.658 | 0.78 | 0.296 | 0.0234 | unknown |
| 16 | Juvenile Hairtail (trichiurids) | 0.015 | 3.08 | 14.89 | 0.749 | 0.753 | 0.207 | 0.028 | unknown |
| 17 | Adult hairtail (trichiurids) | 0.012 | 1.47 | 6.207 | 0.545 | 0.563 | 0.237 | 0.0072 | unknown |
| 18 | Pomfret (stromateids) | 0.108 | 3.03 | 15.15 | 0.95 | 0.95 | 0.2 | 0.239 | unknown |
| 19 | Snappers | 0.0013 | 1.75 | 8.984 | 0.95 | 0.982 | 0.195 | 0.0011 | unknown |
| 20 | Adult groupers | 0.0064 | 1.75 | 6.1 | 0.95 | 0.954 | 0.287 | 0.0089 | unknown |
| 21 | Croakers (≤ 30 cm) | 0.07 | 3.3 | 11.28 | 0.958 | 0.967 | 0.293 | 0.0351 | unknown |
| 22 | Juvenile large croakers | 0.04 | 3.3 | 16.37 | 0.564 | 0.6 | 0.202 | 0.071 | unknown |
| 23 | Croakers (> 30 cm) | 0.0094 | 1.43 | 6.232 | 0.587 | 0.665 | 0.229 | 0.008 | unknown |
| 24 | Demesral fish (≤ 30 cm) | 0.316 | 4.7 | 23.5 | 0.95 | 0.955 | 0.2 | 0.1788 | unknown |
| 25 | Juvenile demersal fish (> 30 cm) | 0.143 | 3.5 | 16.14 | 0.722 | 0.78 | 0.217 | 0.3165 | unknown |
| 26 | Adult demersal fish (> 30 cm) | 0.021 | 2.1 | 6.207 | 0.747 | 0.832 | 0.338 | 0.0352 | unknown |
| 27 | Benthopelagic fish | 0.922 | 3.08 | 15.42 | 0.479 | 0.512 | 0.2 | 0.6025 | unknown |
| 28 | Melon seed | 0.07 | 2.41 | 24 | 0.994 | 0.994 | 0.1 | 0.0499 | unknown |
| 29 | Pelagic fish (≤ 30 cm) | 1.772 | 4.26 | 17.04 | 0.74 | 0.741 | 0.25 | 2.345 | unknown |
| 30 | Juvenile large pelagic fish | 0.289 | 4.26 | 16.12 | 0.622 | 0.645 | 0.264 | 0.7384 | unknown |
| 31 | Pelagic fish (> 30 cm) | 0.079 | 1.4 | 6.27 | 0.759 | 0.76 | 0.223 | 0.0821 | unknown |
| 32 | Demersal sharks and rays | 0.001 | 1.2 | 6 | 0.867 | 0.884 | 0.2 | 0.001 | unknown |
| 33 | Pelagic sharks and rays | 0.0011 | 0.68 | 3.4 | 0.95 | 0.981 | 0.2 | 0.0007 | unknown |
| 34 | Seabirds | 0.0022 | 0.06 | 67.76 | 0.046 | 0.00283 | 0.000885 | 0 | unknown |
| 35 | Pinnipeds | 0.0046 | 0.045 | 14.77 | 0.29 | 0.00181 | 0.00305 | 0 | unknown |
| 36 | Other mammals | 0.0158 | 0.112 | 10.52 | 0.034 | 0.000211 | 0.0106 | 0 | unknown |
| 37 | Marine turtles | 0.0002 | 0.1 | 3.5 | 0.3 | 0.0187 | 0.0286 | 0 | unknown |
| 38 | Detritus | 100 | - | - | 0.005 | - | - | 0 | unknown |
