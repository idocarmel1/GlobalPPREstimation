# Sea of Okhotsk Figure 9 reconstruction (2000–2014)

**Status: provisional extraction completed; scientific interpretation requires review. NOT READY for a balanced Ecopath model or SPPR/PPR.**

**Source:** Gorbatenko, K.M. & Melnikov, I.V. (2019). *Trophodynamics of marine organisms in the epipelagic layer of the Okhotsk Sea in 2000s*. Izvestiya TINRO 198:143–163. DOI: [10.26428/1606-9919-2019-198-143-163](https://doi.org/10.26428/1606-9919-2019-198-143-163).
**LME:** 52, Sea of Okhotsk. **Candidate ID:** GM2019-Fig9, an internal research identifier rather than a published Ecopath accession.
**Groups:** 22 (21 living, one detritus); 20 consumers. **Fleets:** not extracted or assumed absent.
**Extraction date:** 2026-10-02. **Scope:** epipelagic community, 0–200 m, average reporting period 2000–2014. This does not represent the complete benthic and deep-water ecosystem.

The user authorized a reconstruction in which missing displayed feeding arrows are zeros. This produces 19 numerically complete carbon diet columns and 16 numerically complete wet-weight diet columns under the adopted routes. However, 33 arrow endpoints are tentative and two labels are partly overprinted. These are research hypotheses, not a recovered author diet matrix. A separate illustrative carbon variant substitutes two possible label readings; it is not the main extraction.

Start with [DC_reconstruction_review.xlsx](DC_reconstruction_review.xlsx). The direct carbon data are in [carbon_reconstruction.json](../../model_notes.md#removed-extraction-evidence). [model.json](../../model.json) preserves all groups and unknowns in the project database shape, with an explicit blocked status. No source parameter has been changed to improve balance.

## Source tables

### Table 3 — production and stock inputs

Printed p.154 / PDF p.12 in the [primary article](../../../../sources/gorbatenko_melnikov_2019.pdf). All 23 source rows are preserved in [the source ledger](audit/table3_source_readings.json) and `extracted_tables/Table3_source_parameters.csv`.

The printed columns are biomass in million tonnes wet weight, wet/carbon multiplier, biomass in million tonnes carbon, P/B per year, production in million tonnes wet weight/year, production in million tonnes carbon/year, production in gC/m²/year, and contribution within a trophic tier. The carbon-biomass header carries an apparent `/year` printing error; the values are treated as stocks, with the literal source transcription preserved.

Nineteen living figure groups have mapped Table 3 B and P/B. The single microheterotroph row combines bacteria and protozoa: its B, P/B and conversion factor are not allocated between those two figure groups. Three additional “other” rows in tiers II–IV are retained in the source ledger but are absent from the figure group list. The tier V “other****” row is tentatively mapped to predatory fish using the footnote; it remains a flagged crosswalk. Squid III/IV and all three pollock size groups remain distinct.

Biomass density is derived as `source B_wet × 1,000,000 / 1,544,000 km²`. The denominator is the article's implied whole-Sea reporting area (e.g. 694.8 million tC/year divided by 450 gC/m²/year), not an independently measured geographic coverage polygon. Original total stocks remain available.

### Figure 9 — carbon food flows

Printed p.157 / PDF p.15. Box numbers represent production; arrow numbers represent consumption, both in million tC/year. The PDF's original 1318 × 1627 embedded raster is retained byte-for-byte as [figure9_original.tif](audit/figure9_original.tif), with an RGB viewing copy [figure9_original.png](audit/figure9_original.png). Numeric labels, endpoints, source hash and pixel positions are recorded in [flow_readings.json](audit/flow_readings.json). Coordinates are in the original raster, not the clipboard screenshot.

There are 78 transcribed label readings: 43 clearly traced routes, 33 tentative routes and two overprinted labels. The adopted routes create 75 distinct nonzero/unknown feeding pairs and 365 missing-arrow zero cells among 22 prey × 20 consumers. Three duplicated pairs may be artifacts of uncertain endpoint assignment: F26/F47, F41/F42 and F52/F57. Their readable labels are summed only in the explicitly provisional routing hypothesis; the aggregate is not an author-confirmed cell.

The conservative label treatment leaves F62 and F67 unknown. Their literal beginnings are `0,02[overprinted]` and `0,05[overprinted]`. The possible values 0.023 and 0.05 are confined to [carbon_label_hypothesis.json](../../model_notes.md#removed-extraction-evidence), the workbook's **Label hypothesis** tab and clearly named hypothesis CSVs. All routes touching uncertain lines remain flagged even when a label is readable.

For consumer j, the reconstructed carbon fraction is `DC_C(i,j) = F_C(i,j) / sum_i F_C(i,j)`. Production in a box is never used as the diet denominator. An unresolved positive flow makes the other positive fractions in that consumer column unresolved; known zeros remain zeros. Column 18 (baleen whales) is unresolved in the main carbon extraction.

For the wet-weight variant, each prey's carbon flow is multiplied by that prey's Table 3 wet/carbon factor, then normalized within the consumer column. The microbial and detritus factors are unknown. Therefore consumers 3, 4, 5 and 18 have incomplete wet diets. Consumer 2 (bacteria) has one represented prey, detritus, so its diet fraction is identifiable as 1 although its wet Q and Q/B are unknown. Carbon fractions are not silently imported as wet-weight fractions.

### Supporting documents

Six original PDFs and full text extractions are organized under [papers/OKH-GM2019](../../../..), with original URLs and SHA-256 hashes in `source_manifest.json` and current use decisions in `source_use.json`. The 2016 pollock, herring, euphausiid and Sagitta feeding studies are supporting context rather than replacement cells. The 2018 dissertation's Table 8.2 is on printed/PDF p.316 and Figure 8.2 on printed/PDF p.322. The latter has extra arrows absent from the 2019 diagram; those arrows were not added. Earlier discovery notes that refer to p.325 are historical and incorrect for this figure. The recovered dissertation page is retained in `audit/dissertation_figure8_2_p322.png`.

## Biomass accumulation

The primary article's prose, tables and figures were checked for an applicable BA input or explicit Ecopath steady-state assumption. The source is a trophodynamic network rather than an available native Ecopath parameter file. Stock dynamics and period averages do not establish zero annual BA. No unambiguous per-group BA, BA rate or migration input was extracted for this candidate. All BA cells remain blank in the import table and `-9999` in the preserved database-shaped JSON. No balance-implied BA is entered.

## Values from prose

Independent wet-weight annual consumption is retained as a check rather than a diet denominator: copepods 2945, euphausiids 1445.6, hyperiids 152.5 and chaetognaths 320 million t/year (p.153); herring 36.9 and deep-sea smelt 10.29 (p.155); capelin 14.74, small pollock 16.5 and medium pollock 80.8 (p.156).

The adopted figure routes imply hyperiid Q = 60.3998 million t wet/year, about 39.6% of the prose value. Medium-pollock Q = 60.917900 million t wet/year, about 75.4% of the prose value. Small-pollock Q agrees at about 16.5. The full comparison, with unrounded derived values, is in [independent_consumption_comparison.json](audit/independent_consumption_comparison.json). Most checked groups do not reconcile within 5%; no rescaling is applied. The article also mentions zoobenthos in nekton feeding, while the reconstructed Figure 9 group list has no zoobenthos node (abstract, p.143). These findings limit the interpretation of “missing arrows = zero.”

## Conventions applied

- Missing displayed feeding arrows are zero by explicit user instruction. This applies to the adopted endpoint interpretation, not to catch, BA, migration, mortality, egestion or detritus routing.
- Habitat area = 1 uses the entire reporting denominator for density conversion; it is a project convention, not a source habitat-occupancy measurement.
- Diet imports = 0 is the reconstruction convention of representing only the displayed network, not an author-reported external import estimate.
- Carbon and wet diets are researcher calculations from flows, not printed proportions. Source flows retain their decimal precision; stored proportions are not rounded to make sums pass.
- Q/B is derived for 15 consumers as summed wet-weight consumption divided by source wet-weight stock. It is separately identified from published B and P/B.
- Figure tiers I–V are categorical placements, not precise fractional trophic levels. `TL.xlsx` remains blank. `Derived_TL_label_hypothesis.csv` is a separate illustrative carbon-network calculation, not a published model output.
- Eight import files were generated by the Ecopath extraction skill's writer in the explicitly named `extracted_tables` directory, with all 22 prey/stock rows, overriding the usual generated directory name to fit the requested regional model layout.

## Deliberate blanks

Separate bacterial/protozoan B, P/B and conversion factors; detritus stock/conversion; five consumers' wet Q/B; every EE, GS/unassimilated fraction, BA and BA rate, migration, other mortality, detritus import and fate; all fleet/landings/discards inputs; source trophic levels remain unknown. No fleet names are invented. These blanks are part of the extraction.

The source search did not establish a GS input. A checker or EwE import may apply GS = 0.2, or apply zero BA/catch assumptions; these are software assumptions and are not stored as author parameters. The unknown routing cells are not filled with ones merely because only one detritus group is represented. A future Ecopath import must review all software defaults before calculation.

## Unresolved and flagged

The 33 tentative routes, two overprinted labels, three duplicated-pair hypotheses and microbial partition are unresolved. Figure medium-pollock production is 0.59 million tC/year, versus Table 3's 0.537; Figure Squid IV is 0.1 versus the table's 0.105; predatory fish is 0.004 versus tentatively mapped table production 0.005. Both readings are preserved, with no harmonization. The source prose also differs from Table 3 for some P/B descriptions; Table 3 supplies the tabulated B/PB variant rather than mixing incompatible variants.

Automatic raster skeleton traces were tried as reading aids but jump between crossing curves. `trace_*`, masks and graph files in `audit/` are exploratory aids, not source-authoritative assignments. The manual per-label ledger is the actual computational input. No researcher has yet approved its uncertain routes.

## Validation

The main 19 complete carbon and 16 complete wet columns sum to 1 at preserved precision, within 1e-12 in independent reconciliation. The 20-column illustrative carbon variant also normalizes. These checks establish arithmetic only. Unresolved columns remain explicitly unknown. The 365 absent-arrow cells are zero in carbon flows, wet flows and their diets.

`validate.py` on the eight import files reports **0 errors and 32 warnings**, mainly missing essential parameters, source TL and BA/routing completeness. Detritus fate is unknown rather than asserted to close. The saved workbook's 440 cells on each of four matrix tabs are reconciled against JSON and CSV, including formula caches and unknowns. Original source hashes and page counts are checked. [verification.json](audit/verification.json) and [evidence_integrity.json](audit/evidence_integrity.json) report artifact integrity separately from scientific validity.

## Mass balance

**Verdict: not ready; the reconstruction is not a balanced Ecopath model.** The user's readiness gate is a loadable and balanced model; it has not been met. A database-shaped file that parses is not an operational Ecopath input with all essential parameters. Direct carbon-flow checks find P > Q for hyperiids, salmon and jellyfish under the adopted routes. Hypothesis predation/P exceeds 1 for Squid III, herring, deep-sea smelt, capelin, Squid IV and large pollock. These are failures of the adopted reconstruction/closure assumptions, not proof that the authors' complete model was wrong.

`massbalance_check.py` on the wet import files reports **10 errors, 11 warnings and 2 notes**. Four energy flags use default GS = 0.2: hyperiids, chaetognaths, salmon and jellyfish. Six predation flags assume the currently represented consumption and no BA/catch correction. Because BA and migration are unknown and endpoints tentative, those six do not establish an author steady-state inconsistency. With all basic parameters blank, this checker also heuristically treats bacteria and protozoa as detritus pools; that is a checker limitation, not their source identity. Exact output is retained in [import_massbalance.txt](audit/import_massbalance.txt).

The native database converter's separate `MASS_BALANCE.md` gives 4 errors, 6 indeterminate cases and 7 warnings, but it operates on a lossy 19-group conversion. It dropped bacteria, protozoa and detritus, and misclassified copepods, euphausiids and baleen whales as producers because their Q/B was unavailable. Its raw JSON and round-trip workbook remain unmodified and explicitly rejected. [converter_preservation_audit.json](audit/converter_preservation_audit.json) records the differences. The preserved `model.json` restores all 22 groups, true group types, 440 diet cells and source unknowns without filling parameters to appease the importer. It remains blocked; no downstream PPR calculation was run.

## Handoff and reproduction

`extracted_tables/extraction.json` is the skill-writer intermediate; root `model.json` is the preserved database-shaped review candidate. `carbon_reconstruction.json` is the direct carbon extraction. These have different schemas and roles. The `Label hypothesis` variant is illustrative only. The extraction-set index is `../MASTER_INDEX.md`.

Run `python reconstruct.py`, then the Ecopath writer using that intermediate, then the workbook builder `node audit/build_review.mjs` with the bundled artifact-tool runtime, and finally `python finalize_package.py`. The last script retains converter evidence, captures structural/balance logs, checks source hashes and CSV/JSON/XLSX preservation, and produces a portable evidence index. It does not validate biological interpretation. The original sources and scripts provide a reproducible review package; no map, validation DOCX, regional workbook, knowledge graph or existing selected model is changed by this extraction.
