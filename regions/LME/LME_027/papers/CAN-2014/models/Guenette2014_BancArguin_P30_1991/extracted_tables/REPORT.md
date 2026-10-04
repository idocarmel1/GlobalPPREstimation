# Banc d'Arguin and Mauritanian Shelf — P30 (1991)

**Source extraction status: partial; not ready as a complete source model.** The published Base diet contains unresolved composition defects and multistanza production fields are incomplete. The P30 variant additionally has 114 unpublished prey cells across 14 consumers. This concerns the published reconstruction; it does not establish that the authors' operational native model was unbalanced.

Source: Guénette, Meissa and Gascuel (2014), *Assessing the Contribution of Marine Protected Areas to the Trophic Functioning of Ecosystems*, PLoS ONE 9:e94742, [DOI](https://doi.org/10.1371/journal.pone.0094742). Original [article](../../../sources/file-e30dfe50.pdf), [Table 1](../../../sources/Table_1-f0424c0e.xls), and [supplement](../../../sources/pone.0094742.s001-eb18ca66.docx).

51 groups: 47 consumers, 3 primary producers, 1 detritus pool. Three reported catch fleets: Artisanal, Industrial demersal, Industrial pelagic. The reference period is 1991, within a 33,224 km² Mauritanian shelf area; the 1991–2006 Ecosim fits and 2056 projections are separate outputs.

## Source tables and field meanings

Table 1 (article pp. 4–5; original XLS Table_1) fixes group IDs/names. Columns C–J map to TL, B, Z, P/B, Q/B, EE, P/Q and BA rate; K–M retain the three fleet catches and N the reported total. XLS stored strings and bold markup were reread independently; fresh page renders and word coordinates were retained. Bold B/rate/EE/PQ values are marked model-estimated, not silently described as author inputs. Z is separate from P/B, P/Q is separate from Q/B, and each source zero is retained.

Supplement S2, physical DOCX tables 2–4 (retained rendered pp. 8–10), is prey rows × consumer columns 1–47 with import row 52. Every printed percentage is divided by exactly 100 using Decimal, retaining source precision. The four original blank cells are predator/prey 14/36, 15/36, 2/39 and 15/39. They stay blank/-9999, distinct from the explicitly unpublished variant cells. A computational structural-zero convention for source blanks requires its own recorded transformation; it cannot fill a diet deficit.

S8 (physical DOCX table 10, retained rendered pp. 15–16) supplies variant B/EE, aggregate Banc invertebrate shares and Ecosim vulnerability values. P30 takes its B/EE directly from S8. Other scalar parameters, catches and unchanged diet components are inherited Base data, not independently published variant values. TL is unknown. Aggregate pBA does not uniquely determine the 114 changing individual prey shares; they remain unknown. All original supplementary tables and their additional fields are retained in separate [companion CSVs](companions/manifest.json), including S8 formatting roles and scenario outputs; these evidence CSVs are not asserted to be directly importable by EwE.

## Biomass accumulation and multistanza structure

The supplement's Fish section states that BA values are rates per year derived from pre-1991 biomass trends. 50/51 group BA rates are known; the detritus rate is unreported. Negative rates: 11 Coastal selacians -0.05, 23 Groupers ad -0.05, 24 Grouper juv -0.05, 27 Scianids -0.05, 30 Octopus vulgaris -0.03, 31 Cephalopods -0.03. Printed zeros remain known zeros. Absolute BA stays unknown in source imports/JSON; B×rate is used only inside the check and retained separately as arithmetic evidence. A steady-state statement for the last projected year does not establish BA=0 for 1991.

Six stocks have juvenile (age 0–1 year) and adult stanzas, with adults leading the native linked equations. Source P/B is explicitly zero for [3, 4] and unreported for [14, 15, 16, 17, 18, 19, 23, 24, 25, 26]. Table1 provides Z and P/Q separately. P/B=Z is stated only for equilibrium; QB×PQ is a rounded arithmetic reconstruction, not proof of the native stanza solution. VBK is unavailable. No missing P/B or known zero was replaced.

## Values from prose and deliberate blanks

All source documents were swept for BA, assimilation, diets/imports, detritus, fishing, migration and stanza fields. No numeric unassimilated consumption, habitat fractions, detritus routing/import or migration inputs were identified. These remain unknown; EwE/loader defaults would be computational assumptions. The source explicitly reports no discard information. Each fleet catch is retained independently, and total removals stay unknown. The database export field uses an explicit reported-landings scope recorded in metadata; it does not assert zero discards.

## Unresolved source conflicts

- Coastal birds' sum of printed cells is **0.980331**, leaving 0.019669 unexplained; its blank shelf-mollusc cell is not an authorized allocation of the deficit.
- Adult groupers' Banc large-crustacean cell is **134% = 1.34**, and its printed column sum is **2.2006**. The original DOCX and retained render agree. The old **0.1347275** value is not the published literal, and no actual researcher decision authorizing that correction was found. Neither correction nor normalization was adopted.
- 50 Table1/S8 Base numeric differences are retained in [SOURCE_CONFLICTS.json](SOURCE_CONFLICTS.json). Most reflect rounding, while Banc phytoplankton EE is **0.260 versus 0.40**. Dedicated Table1 remains the Base authority; the disagreement is unresolved.
- Supplement prose says P/Q was fixed at 0.2 for mackerel/sardine/horse mackerels, while Table1 gives 0.150 for mackerel and sardine. The tabulated values are retained and the prose disagreement is not averaged.
- The separately recovered EcoBase 689 native model has different diet, precision, fleet and stanza representations. It is source context, not proof that its cells can replace any of these three published variants.

## Conventions and validation

No source diet or detritus routing was normalized. No project GS, habitat or discard default was inserted. Table percentages were converted to proportions; B remains the source's whole-study-area density. The directory name intentionally supplies a stable unique identity for each published variant.

The eight standard EwE import schemas retain their required headers/order. Extra fields are in 22 purpose-specific companion CSVs. The improved installed writer/converter were run; standard JSON fields were reconciled with fresh source extraction, and all eight import tables plus companions were reopened and checked in [ROUNDTRIP_CHECK.json](ROUNDTRIP_CHECK.json). Workbook standard cells are numeric; JSON/ledgers retain source literals and missing masks. Taxonomy is source-backed and shared by the three variants, with the S1 Hake row-30 conflict retained separately.

`validate.py`: **14 error(s), 55 warning(s)**. Base source diet defects, incomplete variant columns, missing routing/GS and rounded S8 zero biomass are retained findings, not repaired inputs. [MASS_BALANCE.md](MASS_BALANCE.md) includes equation arithmetic and completeness guards; its failure/indeterminate findings do not license source repairs. Canonical source admission and any runtime GE/TE/With Egestion experiments are separate stages owned by the regional assessment.

Reproducible source extraction and converter regression evidence: [extraction evidence](../../../../../work/2026-10-04_000003_retained_investigation/qa/BancArguin_20261003/extraction/evidence_index.json). Source-cell provenance: [diet ledger](DIET_CELL_LEDGER.json), [parameter ledger](PARAMETER_CELL_LEDGER.json), and [published CSV companions](companions/manifest.json).
