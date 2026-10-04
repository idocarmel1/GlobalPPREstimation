# Northwest Africa, final Table 17 (2009 report)

**Status:** source-faithful partial extraction; incomplete executable input. Source-only constructor admission is NOT_RUN. This finding concerns incomplete publication of the inputs, not a demonstration that the authors' complete native model was unbalanced.

**Source:** Morissette, L., Melgo, J.L., Kaschner, K., Gerber, L., and Bamy, I.L. (2009), “Food web model and data for studying the interactions between marine mammals and fisheries in the Northwest African ecosystem,” in *Modelling the trophic role of marine mammals in tropical areas: data requirements, uncertainty, and validation*, Fisheries Centre Research Reports 17(2). Chapter printed pp. 6–52 including references. [Original PDF](../../27_118_Northwest_Africa_(1987)/model_validation/evidence/source_review/papers/FCRR_2009_17-2.pdf.pdf). Extraction date: 2026-10-03.

27 groups: 24 consumers, 2 primary producers, 1 detritus pool. Local and foreign fleets are described. The `Unallocated total catch` import column is a carrier for the printed cephalopod total, not an additional modeled fleet. The model describes the late 1980s (printed p. 6); catch prose gives 1990s averages. The source does not establish that those averages are the final model's baseline catch vector.

## Source tables

### Table 17, printed p. 37 / PDF p. 41

Columns are group, TL, biomass (t/km²), P/B (year⁻¹), Q/B (year⁻¹), EE, GE. GE maps to P/Q. Twenty-seven rows are preserved in their printed order. No biomass or annual-rate conversion was applied. A one-row check gives large-pelagics P/B ÷ Q/B = 1.9080 ÷ 11.6980 ≈ 0.1631, agreeing with the printed GE and confirming the column mapping. Dashes for producers/detritus are not numerical zeros.

Bold values are Ecopath estimates according to the caption: TL throughout; EE except group 14; GE for consumers except groups 14 and 18; B and Q/B for group 14; Q/B for group 18. All published estimates are retained, and input/output flags are recorded as source provenance rather than used to discard a reported value. The source spelling `Bathydeersal predators` and singular `Coastal demersal` are preserved.

### Table 18, printed pp. 38–39 / PDF pp. 42–43

Prey rows 1–27 are joined by explicit row labels; the first block has consumers 1–11 and the second 12–23. Numeric header coordinates anchor predator columns, with row-label coordinates defining prey bands. PyMuPDF word boxes and pdfgrid raw lines are retained. Both pages were visually checked at 200 dpi.

Consumer 25 (Zooplankton) is absent from both blocks. Its complete column and import fraction remain unknown. The table's “Total” row says 1.000 for each printed consumer. Actual printed cell totals range from 0.999 to 1.001: groups 2 and 6 total 0.999; groups 3, 5, 10, 12 and 17 total 1.001. These are preserved without normalization. Printed `0.000` entries are preserved; they may be rounded nonzero native values. Blank cells *inside a printed consumer column* denote structural nonfeeding cells. Blank imports for these printed columns are represented as structural zero, documented in the [cell ledger](evidence/evidence/source_extraction/diet_cells.json). An entirely omitted consumer is not treated this way.

### Tables 1–2, printed pp. 11–12 / PDF pp. 15–16

All 1987–2004 local/foreign catch values and totals are retained in [catch_time_series.json](evidence/evidence/source_extraction/catch_time_series.json), in the printed units of 1000 tonnes/year. The header IDs 10–21 are obsolete relative to Tables 17–18; matching the names gives final IDs 12–23. No year or mean was chosen as a final model input. The wrapped trailing digits in local-fleet Rays for 2000 (10.278) and 2004 (13.930) were joined by coordinates. Catch time-series rows are evidence, not adopted baseline catches.

## Values from prose

Partial catch densities are retained in `Landings.csv` as total catch, without a speculative discard split. Source locators and literals are in [catch_prose.json](evidence/evidence/source_extraction/catch_prose.json): large pelagics 0.0078 local + 0.0075 foreign (printed p. 27); sharks 0.0011 + 0.0004 and rays 0.0010 + 0.0008 (p. 29); coastal tunas 0.0013 + 0.0017 (p. 30); clupeids 0.1931 + 0.1423 (p. 31); other coastal pelagics 0.0487 + 0.0924 (p. 32); cephalopods total 0.0545 and crustaceans 0.0062 + 0.0014 (p. 33), all t/km²/year and identified as 1990s averages. The coastal-pelagics components sum to 0.1411 although the prose total is 0.1410; the original components and discrepancy are both retained.

The study area is 3,561,029 km² (printed p. 7). Prose densities are already expressed per model area; they were not divided by area again. Catch missing from the prose is unknown, even where time-series evidence proves fishing occurred.

## Biomass accumulation and deliberate blanks

The complete Northwest Africa chapter was searched for accumulation, changing biomass, steady-state statements, migration, assimilation, egestion, excretion, discards and routing, including a second sweep after table extraction. No group-specific final baseline BA, assimilation/GS, habitat fraction, detritus-import or detritus-routing parameter was identified. Historical biomass surveys and Ecosim time series concern differing areas/periods; they do not establish a numerical BA for this Ecopath baseline. General mass-balance language and a reference title containing “steady-state” are not explicit BA = 0 statements. All BA cells remain blank and both canonical BA fields are -9999.

`Discards.csv` and `Detritus_fate.csv` are wholly blank. The paper defines detritus content but does not give fractions routing production/egestion to it or export. GS remains unknown for every group, including the mixed `Zooplankton` group. No project convention was applied. EwE may substitute GS = 0.2, BA/catch = 0 and habitat area = 1 on import, but these are software defaults, not extracted values. The canonical JSON restores such unsupported defaults to explicit unknowns.

## Conflicts retained

- Table 3 / Table 15 ID 6 Blue whales maps to Table 17/18 ID 8 Baleen whales; ID 7 Sperm whales maps to 6; ID 8 Killer whales maps to 7. Table 3 “Small cetaceans” maps to final “Dolphins,” ID 10. [MODEL_PROFILE.md](MODEL_PROFILE.md) gives the full crosswalk context.
- Balancing prose on printed p. 36 gives dolphin biomass 0.02225, large-pelagics Q/B 11.60, and benthic-producers P/B 107.362. Final Table 17 gives 0.0225, 11.6980, and 107.3600. Final tabulated values are retained; no averaging or reverse rounding was used.
- The earlier prose and Table 16 report pre-balancing inputs. They are not substituted for the final Table 17 values. Table 17 also contains coastal-demersal P/B 13.9400 and Q/B 46.4667; high rates were verified in the rendered table and retained.
- Table 17 has zooplankton TL 2.00, but two primary-producer groups exist. TL does not uniquely determine its missing diet. It cannot justify setting a phytoplankton share to 1 by itself.

## Native lineage comparison

The independently retrieved official EcoBase 118 native record strongly matches this publication after matching group names: final IDs 6,7,8,9 map to native 8,9,6,7. All 644 compared cells (23 printed consumers × 27 prey plus import) agree within the source's printed precision. This includes structural blanks and explicit printed zeros; it does not claim exact full-precision equality. The native record supplies zooplankton feeding entirely on phytoplankton and other unpublished fields. They remain **unadopted** in this paper-only extraction. [Comparison evidence](evidence/evidence/source_extraction/paper_native_diet_comparison.json). The separate identity review records the one scalar discrepancy: printed detritus EE 0.3695 versus native 0.

## Conversion and round trip

`model.json` in this directory is the extraction JSON; [candidate model.json](../model.json) and `source_canonical_database.json` are the source-faithful database JSON. The writer's `--dir-name extracted_tables` override follows the active project directory contract and avoids giving the candidate an invented EcoBase accession.

The converter's raw JSON, workbook, log and mass-balance output are archived under [source_extraction](../../../../../../../LME_027/models/27_Morissette2009_Northwest_Africa_Table17/evidence/source_extraction). The original converter additionally creates its conventionally named JSON/workbook here; these are **raw, lossy converter products**, not the canonical candidate. The converter discards TL/GE, inserts habitat/catch defaults, drops explicit printed diet zeros and lacks complete unknown-routing/fleet representations. These changes are corrected in the candidate JSON with [a field-level restoration ledger](evidence/evidence/source_extraction/converter_restoration_ledger.json). Sparse native fields are supplemented with explicit source unknowns, per-fleet catch components and source metadata; canonical catch fields retain their temporal limitation.

An independent reconstruction from canonical numerical fields and those explicit extensions reproduces all eight import tables: exact byte equality for six CSV files; exact cell-value equality for TL/Metadata workbooks. [Round-trip verification](evidence/evidence/source_extraction/roundtrip_verification.json). It does not establish ecological balance.

## Validation and mass balance

Structural validator: **0 errors, 30 warnings**: 27 missing fate rows, one missing-GS summary, missing zooplankton diet, and missing BA. Arithmetic mass-balance helper: **0 errors, 12 warnings**, including the missing diet and low marine-mammal/seabird P/Q values. Those low efficiencies are explicitly permitted for these groups in the balancing discussion (printed p. 35); no values were altered.

Raw database checker: **NOT BALANCED**, with **1 error, 1 indeterminate finding, 10 warnings**. The error is the missing zooplankton diet. Without its consumption, phytoplankton EE recomputes to about 0.0148 versus the published 0.5151. The suggested closing BA is diagnostic output, not extracted data, and was not adopted. Source routing, GS, BA, catch completeness and baseline timing further prevent a complete source-only budget verdict. The raw checker uses defaults in indicative calculations; its numbers must not be treated as validation of the canonical incomplete source.

[Admission record](evidence/evidence/source_extraction/source_admission.json), [validator output](evidence/evidence/source_extraction/validate.txt), [mass-balance helper output](evidence/evidence/source_extraction/massbalance_check.txt), and [raw database balance report](evidence/evidence/source_extraction/raw_converter_MASS_BALANCE.md).
