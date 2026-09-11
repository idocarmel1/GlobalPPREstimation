# Source evidence for the discard-routing experiment

Audited 10 September 2026 against the frozen `inputs/` tree. PDF page numbers below are **one-based file pages**, followed by printed page numbers where they differ. This is a source and conversion audit, not a validation of the experimental solver. Machine-readable evidence, exact input SHA-256 hashes and biological fate rows are in [source_evidence.json](source_evidence.json); the four-model inventory is in [model_inventory.csv](model_inventory.csv).

## Decisions that control the experiment

| Frozen model | Original living-group harvest H, native flow units | Published discard evidence | Source-supported SR destination? |
|---|---:|---|---|
| Humboldt 13_2 | 35.5395489180725 | Separate fleet landings and discards; D=1.4202697425725, D/H=3.996307735% | **Yes:** both fleets to Fishery offal, then 10% pelagic / 90% benthic detritus; fraction-grid amounts remain hypothetical |
| Bay 34_1 | 1.025531307 | Author explicitly combines landings and discards; separate original D unavailable | **No:** generic-detritus return is a hypothetical destination |
| Okhotsk 52_1 | 0 | Frozen group catches all zero; no group catch/discard table in recovered chapter | **Unavailable for a nonzero-harvest experiment:** fH is zero at every fraction |
| Guinea 28_646 | 0.86795216265 | Separate 1998 D assumptions appear in Table 16, despite absent JSON split fields | **No:** published D does not establish fleet destination; generic-detritus return is hypothetical |

H excludes detritus exports. In particular, **Guinea's detritus export of 1670.48071 is not harvested fish**. The frozen loader also forces detritus catch to zero. Raw whole-file export sums are therefore inappropriate harvest totals.

No independently quantified **processing-offal** flow was recovered for these four models. Do not invent or add one. Humboldt's named Fishery offal compartment is the documented destination for fleet discard routing; a compartment name is not an additional biomass source.

The study can designate D=fH without recovering an observed discard rate. That authorization does not make an assumed destination source-supported, nor does it permit inserting new harvest into Okhotsk's zero-H frozen baseline.

## Humboldt: original supplement supports return routing

Chiaverano et al. (2018), *Evaluating the role of large jellyfish and forage fishes as energy pathways, and their interplay with fisheries, in the Northern Humboldt Current System*, Progress in Oceanography 164:28–36, DOI [10.1016/j.pocean.2018.04.009](https://doi.org/10.1016/j.pocean.2018.04.009). The original frozen article and XLS supplement, rather than the catalog's shortened title, are authoritative.

- **Domain and units:** PDF 3 / printed 30 gives 165,000 km², 4°S–16°S, extending 111 km offshore. The baseline averages 1995–1998 inputs. Catches are t wet weight km⁻² yr⁻¹. The article and Table A incorrectly attach a time dimension to some biomass labels; biomass is a standing-stock input and must not be treated as annual production.
- **Original split:** XLS `Table A-resolved parameters!I6:L44` contains artisanal/commercial landings and discards. Direct cell sums yield L=34.1192791755 and D=1.4202697425725. Their sum exactly agrees with the frozen JSON catch vector to floating-point precision. The article's 10% artisanal discard-rate statement and gear-based reconstruction are model assumptions; retain the actual supplement cells, including exceptions, rather than imposing a fresh uniform rate.
- **Fleet destination:** original `Table C-resolved detritus fate!D43:D44` equals 1 for Artisanal and Commercial fisheries. The other four destination/export columns in those rows equal zero. These are source-supported routing fractions. They are not evidence that a new experimental f was observed, nor independent measurements of post-release survival.
- **Onward route:** Table C row 40, Fishery offal, has E40=0.1 to Pelagic detritus and F40=0.9 to Benthic detritus. Row 41 sends Pelagic detritus to Benthic detritus; row 42 sends unused Benthic detritus to export. These are detritus-fate routes; consumption by detritivores and resulting surplus must remain distinct in the solver.
- **No direct scavenger diet link:** Table B's offal prey row `B40:AN40` is all zero. Table A `H42` gives offal EE=0. The offal pool therefore cannot be described as a published direct seabird/scavenger food pathway in this model. Its ecological pathway runs through onward detritus routing.
- **Conversion boundary:** the frozen JSON retains group-level landings/discards as extensions and includes `source_tables`. The frozen `ModelData.py` extracts neither those extensions nor fleet fates. Its explicit detrital input calculation uses biological other mortality plus unassimilated consumption, together with separate detritus import. Loading the source JSON alone does **not** restore the original fleet return route. S0 is the preserved converted baseline, not a claim of a complete reconstruction of original EwE/ECOTRAN fishery routing.

Two fidelity issues must stay visible. The paper says sardine landings were reduced from 5.65 to 1.4, while original XLS J14=5.6513425 and the frozen model follows that table. Do not silently change H to resolve the disagreement. Also, the prior fleet sidecar cites rows 44–45, but the original XLS fleet rows are **43–44**. Existing frozen Table C image/PDF exports omit the fleet rows altogether; they cannot establish their absence. Original XLS reading independently verified 3,055 cells, including blank padding, across Tables A/B/C against the saved extraction with zero mismatches.

Evidence: [article PDF 3](../verification/source_pages/humboldt-pdf-003.png), [direct original-XLS fleet-cell transcription](../verification/source_pages/humboldt-original-xls-fleet-cells.png). The latter is clearly labeled a new transcription, not a publication screenshot.

**Double-counting rule:** represent the designated return once in the fishery ledger. If an experimental source-reference baseline first restores the published original D route, replace/reclassify that return when changing f; do not add fH on top of it. If comparing directly to converted S0, label restoration as such. Keep the original biological M0/egestion and any solved detritus inflow adjustments separate from explicit fishery returns. Never count the same D as both M0 and SR return, or as a new external detritus subsidy.

## Bay of Bengal: total catch, unpublished split and route

Guénette (December 2013), *An exploratory ecosystem model of the Bay of Bengal Large Marine Ecosystem*, recovered 62-page report. The exact frozen PDF is identified by hash; catalog descriptions of a 69-page distribution are not page locators for this copy.

PDF/printed **9**, Catch section, explicitly says the 1978 Ecopath input is landings plus discards, including reconstructed unreported catches. [Appendix A2.1, PDF/printed 46](../verification/source_pages/bay-pdf-046.png), is a **total catch** table by fleet and group, in t km⁻² yr⁻¹ divided by the entire study area. Its printed total 1.025534 is close to the precise frozen sum 1.025531307; rounding differs. There is no separate discard time series or split in that table.

PDF/printed **7** gives 6,205,000 km² and explicitly extends the Bay LME to northern Sumatra and the Maldives. Use that source boundary for native totals; the modern atlas polygon is not interchangeable. [Table 16, PDF/printed 24](../verification/source_pages/bay-pdf-024.png), distinguishes habitat biomass from area-adjusted biomass. The frozen model uses the latter for its food-web calculations.

The frozen model has one Detritus group (49; B=137, detritus import=0), and living-group biological detritus fate is 1 to that group. No separately documented fleet return fraction, destination, or processing offal was recovered. A full return to generic Detritus is a valid **hypothetical** routing choice if the numerical model supports it; it is not a recovered source fact. Unknown original D does not prevent the fH grid.

Evidence: [catch semantics, PDF 9](../verification/source_pages/bay-pdf-009.png), [domain, PDF 7](../verification/source_pages/bay-pdf-007.png). Original official distribution identified in the frozen metadata: [BOBLME report](https://www.boblme.org/documentRepository/Bengal%20report%2028april2014.pdf); the frozen recovered copy came from a public mirror. No claim that this official link was freshly downloadable is needed for the frozen-file audit.

## Okhotsk: period and geographic correction; zero recorded harvest

Chaikina (2020), *A model of the Okhotsk Sea with a focus on marine mammals*, printed pp. 23–34 in *Marine and Freshwater Miscellanea II*, Fisheries Centre Research Reports 28(2). The [chapter opening, PDF 24](../verification/source_pages/okhotsk-pdf-024.png), explicitly identifies its basis as Chaikina's 2004 BSc thesis on the **1980s**; the original 49-page thesis is not among the frozen materials. [Public report location](https://epic.awi.de/id/eprint/52730/1/Palomares20_FishCentResaRep28.pdf).

[PDF 25 / printed 24](../verification/source_pages/okhotsk-pdf-025.png) describes the study's Ecopath model as **NE**, contrasted with an SD model from Shuntov and Dulepova. It does not establish a northeastern subregion. The stated whole-Sea area is 1,590,000 km². The source baseline is the 1980s, with seasonal parameters combined into annual means; the `1980` filename is a catalog label.

[Table 1, PDF 27 / printed 26](../verification/source_pages/okhotsk-pdf-027.png), matches the 29-group frozen model's identifying parameters, including baleen-whale B=0.958, P/B=0.02, Q/B=8.31 and EE=0.365. **It contains no catch or discard column.** All 29 frozen group export fields equal zero. Regional catch figures in the prose prove that real fisheries existed but do not recover a group-specific model catch vector. Do not fill that missing vector from broad regional totals.

The sole Detritus group (29) has unknown biomass/import sentinels and no dedicated offal pool. Biological fates to this pool do not establish fleet return. Neither zero recorded catch nor a hypothetical fH grid establishes zero real-world discard effects. Keep this candidate as an explicit zero-H/unavailable experiment, not as empirical evidence of routing invariance under positive discards. The source table's biomass unit includes an erroneous per-year factor; retain the caveat and use stock dimensions consistently.

## Guinea: published assumed D, but no established destination

Guénette and Diallo (2004), *Addendum: Modèles de la côte guinéenne, 1985 et 1998*, printed pp. 124–159 / PDF pp. 128–163 in Palomares and Pauly (eds.), *West African marine ecosystems: models and fisheries impacts*, Fisheries Centre Research Reports 12(7). [Public compilation](https://www.seaaroundus.org/doc/publications/books-and-reports/2004/Palomares-et-al-west-africa-ecosystems.pdf). Do not borrow discard assumptions from the neighboring Gambia or Guinea-Bissau chapters, or substitute the 1985 variant for this 1998 model.

[PDF 129 / printed 125, Table 1](../verification/source_pages/guinea-pdf-129.png), totals **111,932 km²**, rounded to 112,000 in the prose, and states that the modeled area extends beyond Guinea's EEZ. This is not a model of the full Guinea Current LME. [Table 9, PDF 147 / printed 143](../verification/source_pages/guinea-pdf-147.png), identifies the 44-group balanced 1998 model and its annual P/B and Q/B units.

[PDF 153 / printed 149, Rejets](../verification/source_pages/guinea-pdf-153.png), says discard information was nearly absent. The authors estimated small-capitaine (*Galeoides decadactylus*) discards from size-retention information; D was approximately **30% of industrial landings**, not 30% of total catch. They extended this assumption to other commercial species, assumed little artisanal discarding, and used additional assumptions for noncommercial species. These are **published model assumptions**, not measured fleet-wide rates. At D/L=0.3 the corresponding D/(L+D) is about 0.23077 for that applicable component; neither ratio applies uniformly to all source H.

[Table 16, PDF 157 / printed 153](../verification/source_pages/guinea-pdf-157.png), supplies separate 1985/1998 artisanal and industrial landings and industrial discards. The 1998 half was transcribed with PDF bounding-box coordinates and visually checked. [Transcription](../verification/source_pages/guinea-table16-1998-transcription.json) preserves every unprinted entry as null and explicit zeros as zero. Nonblank D cells sum 0.090762 t km⁻² for the annual 1998 table. This is a sum of rounded published entries, **not a precision-matched full original D total**; an exact discard fraction is left unavailable rather than manufactured from rounded subtraction.

The frozen JSON lacks separate D fields but its living exports are consistent with L+D in checked examples: Bars 0.089+0.01152 versus precise export 0.100516438; benthos has discard-only 0.00562 versus 0.005621521; Ethmalose has landings about 0.249 versus 0.248826936. Minor rounding differences must not prompt a baseline rewrite. The detritus group's export, 1670.48071, is categorically excluded from H.

No explicit fleet discard destination or return fraction was recovered from the correct chapter. The single generic Detritus group (44, B=290, import=0) and biological fate rows of 1 do not prove that all fisheries returns were routed there. Original return is therefore **unknown**, while the frozen loader has no explicit fishery-return path. Generic-detritus SR must remain hypothetical. Authors also flag potentially underestimated illegal catches, uncertain tuna/shark biomass and catch, and incomplete discard composition.

## Primary EwE guidance and scope of inference

The current [EwE User Guide, Ecopath Input](https://pressbooks.bccampus.ca/eweguide/chapter/ecopath-input/) distinguishes landings, discards, discard mortality and discard fate. Catch is landings plus discards; flows use the total model area. Discard fate can allocate to detritus or external export. A dedicated discarded-fish pool is supported. Biological detritus fate is a different input. These definitions justify the study's separate mortality/return ledger; they do not supply missing historical model fractions or imply every discarded organism dies.

[Spatial fishery dynamics](https://pressbooks.bccampus.ca/ewemodel/chapter/spatial-fishery-dynamics/) likewise lists landings, discards, mortality and fate separately in fleet specification. [Bycatch and discards](https://pressbooks.bccampus.ca/ewemodel/chapter/bycatch-and-discards/) motivates examining scavenger and subsequent trophic effects under alternative scenarios. None of these sources establishes a universal return fraction for this experiment.

## Verification and limitations

Twelve publication pages were rendered with Poppler and visually reviewed. Humboldt's frozen rendered Tables A/C were also inspected; direct original-XLS cell comparison resolves omitted fleet rows. Guinea Table 16 used bounding-box coordinates, not layout-text columns. Original files were never modified. SHA-256 identifiers and exact source paths are in the adjacent JSON, together with a hash of the frozen loader.

The audit establishes source semantics and provenance, not a mass-balanced return restoration. The numerical audit must still verify solver reachability, source versus solved detritus inflows, and whether compensating imports/exports or EE adjustments already account for the designated flow. Unknown source information stays unknown; scenarios can be hypothetical without claiming it was observed.
