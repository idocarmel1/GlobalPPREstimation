# Mediterranean 1995 — extraction and source assessment

Piroddi et al. (2022), *Modelling the Mediterranean Sea ecosystem at high spatial resolution to inform the ecosystem-based management in the region*, Scientific Reports 12:19680, DOI 10.1038/s41598-022-18017-x.

One distinct baseline was recovered: **Piroddi_2022_Mediterranean_1995**, representing **1995** (main article pp. 7–8). The workbook labels it “1990s.” The 1995–2016 Ecosim/Ecospace simulations are not separately tabulated Ecopath parameterizations. The model has 71 groups: 65 consumers, 4 producers, and 2 nonliving pools; 37 geographically labeled fleet entries spanning 10 gear categories. The serialization number 2602022 is a local identifier, not an EcoBase accession.

## Sources and exact locations

- `41598_2022_18017_MOESM1_ESM-75e4d6d3.xlsx`, four visible worksheets, no formulas or hidden sheets.
- Basic input: `'Basic input parameters'!A5:H75`; source columns C=TL, D=B, E=PB, F=QB, G=EE, H=PQ.
- Diet: `Diets!C4:BO74` (71 prey × 65 consumers), plus `C75:BO75` imports. Rows are prey, columns consumers. All 4,680 source cells are retained exactly.
- Landings: `Catches!C5:AY41`, 49 group columns × 37 fleets; group IDs are row 3. Despite the sheet name, its caption explicitly says **Landings**.
- Discards: `Discards!C5:BY41`; use numbered group headers only. Four unnumbered Sardine/Anchovy/Hake/Mullet aggregate columns contain no fleet numbers and are excluded. The remaining 71 × 37 cells are retained, including explicit zeros.
- `41598_2022_18017_MOESM2_ESM-7d26163a.docx`: all 926 body paragraphs, five tables, XML text and foot/endnotes checked. Table S2 (second Word table) supplies group composition and methods; the full supplement was rendered to 87 pages. Juvenile groups 22, 24, 30 and 38 share the explicitly stated adult-and-juvenile species definitions for 21, 23, 29 and 37. Large phytoplankton (69) has no numbered composition heading in Table S2; this is recorded as not documented rather than assigned an invented taxon. Rendered pp. 21–22 confirm the missing heading.
- Main PDF: 12 pages, methods pp. 7–8 and Figs. 3–4 specify the 1995 baseline, multistanza structure, whole-basin geography and ~8 km grid. Main and supplement source bytes were preserved; `source_manifest.json` lists hashes.

The XLSX uses coarse display formats (some positive biomass or EE values display as 0.000/0.00). Extraction uses its stored numbers, retaining original XML numeric strings, rather than copying these display-rounding artifacts. `cell_evidence.json` traces 9,546 basic, diet, landings and discard cells. Excel-rendered original views and Word-rendered pages are in `visual_evidence/`.

## Deliberate unknowns and model admission

All 71 B, all 69 living PB, all 65 consumer QB and all 71 EE values are supplied; no B=1 completion or coupled-B reconstruction is needed. No per-group GS, BA, migration or natural-mortality detritus-routing fractions were found in the source bundle. These remain blank in imports and -9999 in canonical fields. Pool biomasses and EE do not uniquely determine routing.

The 22 groups absent from the landings table retain unknown landings and unknown total export, with their explicitly reported discards separately preserved. A diagnostic staging copy assumes only those unlisted landings are zero, then adds all reported discards; it does not discard known bycatch. This is a stated computational assumption, not a source value. Missing BA=0 and GS defaults were requested only in the standard-default constructor attempt. Routing admission stops the constructor before those defaults are applied. Canonical habitat area is unknown; B remains the source model-area density. No diet normalization, pooling, routing assignment, biological repair, LIM or annual PPR was performed.

## Source arithmetic and flagged values

Diet sums including import range **0.99956013582–1.00000013576**, within the calculator's 0.001 tolerance. Printed diets are unchanged. The tiny rounding differences are not the loading blocker.

The **Fin whale (4)** merits source investigation independently of routing:

| Quantity | Source cell / calculation | Value |
|---|---|---:|
| B | Basic input parameters!D8 | 0.008637933 t/km² |
| PB | Basic input parameters!E8 | 0.022/year |
| Published EE | Basic input parameters!G8 | 0.00001 |
| Production | B × PB | 0.000190034526 t/km²/year |
| Reported discard removals | Discards!F5:F41 | 0.0002808 t/km²/year |
| Predation | Source diet × B × QB | 0 |
| Conditional required EE | (predation + discards)/production | 1.477626228825 |

The nonzero Fin-whale discard entries are F8=0.0000144, F10=0.000072, F18=0.0000144, F20=0.000072, F27=0.0000144, F29=0.000072 and F36=0.0000216. Their sum exceeds production even before any unlisted landings. This calculation assumes unreported BA and net migration are zero. To retain the printed EE, the missing BA+net-export residual would be **−0.00028079809965474 t/km²/year**. That is an unexplained residual, not a justified value to enter. Unreported immigration/biomass decline or inconsistent source parameters could account for it; the supplied material does not resolve which.

Other substantial printed-versus-conditional EE differences occur for Common dolphin (0.01 versus 0.85247), Bottlenose dolphin (0.05 versus 0.20075), Striped dolphin (0.65 versus 0.49860), Loggerhead turtle (0.95 versus 0.67541), Green turtle (0.99 versus 0.64127), and Bluefin tuna (0.408032 versus 0.335364). Missing BA, migrations and multistanza accounting limit interpretation. All 71 source budgets, units, known removals and residuals are retained in `source_balance_groups.csv`; none were used to repair the model. The generic mass-balance checker reported conditional warnings/failures with implicit assumptions; the independent audit explicitly distinguishes those assumptions from source statements.

## SPPR result

GE, TE and With Egestion are all **NOT_RUN**, because neither constructor can infer routing between **70 Discards** and **71 Detritus**. Diet admission passed. These are constructor exceptions, not returned SPPR diagnostic failures. The concise direct-only report is `../diagnostics/DIRECT_SPPR_REPORT.md`, with full constructor traces beside it. No unsupported numerical health or coefficient summary is substituted.

## Geographic applicability

The authors explicitly model the entire Mediterranean basin (article pp. 7–8) with Western, Adriatic, Ionian/Central and Aegean/Levantine fleet subdivisions. This is an intended full-basin candidate for LME026. The supplied footprint is an inherited copy of the target region polygon, not the author's model-cell boundary; its prior 100% overlap is not independent measured evidence. No new numerical overlap fraction or exact model ocean area is claimed. A basin-mean Ecopath network does not preserve the later Ecospace cell-specific outputs.

## Verification and use status

Eight EwE import files, 71-row taxonomy, source-faithful canonical JSON and a lossless `SOURCE_ROUNDTRIP.xlsx` were produced. Validation: **0 errors, 73 warnings**, comprising missing BA, missing GS and 71 missing routing rows. Original numeric precision, source blank/zero distinctions and all fleet data were verified against source cells. The generic converter initially normalizes/rounds some fields and converts unknowns; its original output and exact restoration ledger are retained separately. Its generic `_reconstructed.xlsx` is a lossy convenience view (fleet/discard split and BA omitted; unknown fate shown as zero); use `SOURCE_ROUNDTRIP.xlsx` and the eight source imports. The lossless roundtrip was reread and compared to canonical B/PB/QB/EE/PQ/TL, all diets and all fleet cells.

No model has been selected, and this blocked extraction is not production eligible. Regional workbook, Project.xlsx, the shared map and shared calculation code are unchanged. `central_metadata_proposal.json` is ready for the coordinating agent. A native EwE database or original routing and missing-flow specification is the next evidence needed; routing/pooling experiments and biological corrections require a separate decision.
