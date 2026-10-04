# Southern Benguela (1978): BEN-2020 extraction

**Source:** Shannon LJ, Ortega-Cisneros K, Lamont T, Winker H, Crawford R, Jarre A and Coll M (2020), *Exploring Temporal Variability in the Southern Benguela Ecosystem Over the Past Four Decades Using a Time-Dynamic Ecosystem Model*, Frontiers in Marine Science 7:540. DOI: 10.3389/fmars.2020.00540.

**Model:** `BEN2020_Southern_Benguela_1978`. Local extraction number 20201978 is a project identifier, not an EcoBase accession. **LME:** 029, Benguela Current. **Groups:** 49 (45 consumers, 3 primary producers, 1 detritus). **Fleets:** 31. **Selection:** not selected. **Review date:** 2026-09-28.

The article and its 42-page supplement support one 1978 Ecopath baseline. The 1978–2015 time span is the fitted Ecosim period, not a set of independently parameterized baseline years. Alternative fitting scenarios and predecessor models are discussed but have no additional complete static parameter sets in this bundle.

The source transcription and roundtrip are complete, with missing source fields retained. Numerical diagnostics require two explicitly derived P/B values and documented defaults. All three requested direct diagnostics return **FAIL**, so this candidate is not ready for adoption. This is a finding about the reconstructed inputs and their translation into the current calculator, not proof that the authors' native multi-stanza EwE implementation failed.

## Source tables and identities

- **Main Table 2, PDF/printed pages 8–9:** exact row names, trophic level, B, total mortality Z, P/B, Q/B, EE and P/Q. B is t/km², rates per year. Columns were assigned using separate x coordinates on the two pages. Blank cells remain blank. Bold numeric cells mean model-estimated parameters; their locations are retained in `source_model_estimated_cells.json`.
- **Supplement Table S1, page 1:** multi-stanza parameters. Eight explicit P/B values supplement Table 2's blank P/B cells: anchovy, sardine, horse mackerel and shallow-water hake stanzas. The deep-water hake P/B cells are blank in S1 as well and remain unknown in canonical. All ten Table 2 Z values remain separately recorded; Z was not silently copied to P/B. S1 growth K and transition ages are retained as source evidence; the single-group calculator does not implement native EwE stanza dynamics.
- **Supplement Table S3, pages 7–10:** 48 group rows, 31 fleet columns plus printed totals, all units t/km²/year. The two fleet blocks were joined by group name. All 48 fleet sums exactly equal their printed group totals, and total catch is **2.94626 t/km²/year**. No area conversion was needed. Rotated header text overflowing into adjacent cells was resolved against the rendered pages and main Table 1 fleet names.
- **Supplement Table S4, pages 12–15:** 49 prey rows and 45 consumer columns plus explicit diet imports (2,250 numeric cells). Header numbers 3–26 and 27–43, 45–48 refer to this table's numbering. Asterisks mean 0.0001. Every column sums to exactly 1 except group 37 (1.0001) and group 42 (1.0002); these printed sums are preserved.
- **Main Table 1, page 4, and supplement Table S2, pages 2–3:** taxonomy and group definitions. Table 1 uses a different ordering from numerical Table 2/S4. Canonical numbering follows S4; joins use group identity, never the Table 1 ordinal.

The eight EwE files live in this directory. `model.json` here is the extraction-writer input; `../model.json` is the authoritative, source-faithful database JSON. The generated `29_Benguela_Current_...json` and original converter reconstruction are retained as conversion audit artifacts only: the converter automatically normalizes two diets and omits printed P/Q and Z. The local source-fidelity adapter restores exact diets, retains printed P/Q as `ge`, records Z/TL as source fields, and preserves missing routing and habitat-area fractions. Use `../model.json` for any later review or selection.

## Biomass accumulation

Supplement S1 reports **sardine stock BA/B = 0.3/year**, and explains this is to facilitate stock increases. The shared proportional rate is represented for both juvenile and adult sardine stanzas. This is an explicit expansion of a stock-level statement to stanza rows, not two independent measurements. It implies 0.0684 and 0.18 t/km²/year with the printed biomasses. The meaning of this shared growth term in native EwE multi-stanza accounting needs confirmation before treating it as an ordinary, additive BA term in the current single-group production equation.

Main Table 2's page-9 footnote explicitly gives **WC rock lobster BA = −0.603 t/km²**, interpreted as the model's annual accumulation flow; supplement section 3.9 confirms the intended decline. It is stored in the absolute BA column. The remaining 46 groups have unknown BA. The entire paper and supplement were searched; a missing BA is not a source assertion of zero.

## Prose, taxonomy and fisheries evidence

Supplement section 3.10 gives conditional unassimilated fractions: 0.35 for zooplanktivorous fish, 0.30 for mixed zooplankton/fish diets, and 0.20 for heavily predatory groups. The source does not enumerate the groups assigned to each class or define mixed-diet thresholds. Source-derived 0.35 is assigned only to the five fish with entirely zooplankton diets in S4: Redeye, Other small pelagics, Juvenile Hmack, Lanternfish and Lightfish. Broader automatic classification was avoided. Other groups retain unknown GS; numerical defaults below are not an assertion of the authors' exact values.

Main page 5 deliberately retains a **single detritus pool**. Fish/offal scavenged from fishing nets by birds and seals are represented as consumption from the live fish source group, especially large hake, to retain their origin. No additional offal pool, discard split or discard return was invented. S3 reports catches rather than separate retained and discarded components; total removals are carried in `Landings.csv` as the importer convention, with `Discards.csv` blank.

`Taxonomy.xlsx` and all canonical `taxon_descr` fields retain the paper's definitions. S2 lists **examples**, not exhaustive guild membership. Its original spellings are preserved; unverified names were not silently synonymized. Main page 5 clarifies that Agulhas sole has its own dedicated group and West Coast sole remains in benthic-feeding demersals, despite an overlapping S2 example list. A material unresolved source conflict remains for South Coast rock lobster: main Table 1 says **Panulirus homarus**, but supplement section 3.9 says **Palinurus gilchristi**. These are retained as distinct conflicting source identifications, not assumed synonyms. Tuna/Swordfish labels also differ from the Table 1 listing of Thunnus spp. and Atlantic bonito.

## Spatial fit

The modeled area is **220,000 km²**, from the Orange River mouth at about 29°S to East London at 28°E (main page 3, Figure 1). It represents the southern Benguela west and south coasts; it does not represent the northern Benguela off Namibia. It is therefore a **partial LME029 fit**.

The inherited 50% coverage estimate has not been established by a source polygon overlap. The existing 14–28°E, 37–29°S rectangle is a display/search envelope, not the blue shelf polygon in Figure 1. No precise coverage fraction is reported from that rectangle. The inspected map and spatial evidence are retained in the extraction review directory.

## Deliberate blanks and conventions

Canonical deep-water hake P/B (groups 30 and 31), unreported GS, 46 unreported BA values, numeric detritus routing, detritus import, habitat fractions, migration, and the landing/discard split remain unknown. All 49 biological B values are published; no biological biomass was defaulted to 1. Unknown routing is `-9999` in canonical and blank in the import table. Published diet zeroes and stated catch zeroes remain zero.

The canonical schema retains source growth K for the ten stanzas; missing growth and price fields are unknown. Table 2's printed precision is retained in import files. Converter-derived BA rates/absolute equivalents are identified by the original form in the extraction and source notes.

## Source and numerical balance

The raw import checker reports **3 errors and 10 warnings**, including recomputed EE above 1 for juvenile sardine, adult sardine and Agulhas sole. The canonical-aware converter checker calls the sole case indeterminate because BA is unknown. These verdicts do not authorize changing any parameter. The small P/Q ratios of seabirds and marine mammals are present in the source and were visually checked.

With the shared sardine BA/B term represented as additive BA, juvenile sardine gives recomputed EE about **1.200** versus printed **0.984**, and adult sardine about **1.219** versus **0.979**. Their printed catch and diet cells were independently verified. The discrepancy is tied to the reported multi-stanza/accumulation convention and is not an extraction-column shift. Resolving the native model's treatment of mortality versus production and stock growth is the priority before proposing a correction.

The direct numerical run uses only these separate completions:

1. Deep-water hake P/B = published P/Q × Q/B: **2.00375** for small M. paradoxus and **0.799** for large M. paradoxus. These derive from rounded printed ratios; they do not overwrite canonical P/B unknowns or silently replace Z.
2. Standard calculator completion: unknown BA becomes zero; 40 consumers receive GS=0.2 while the five source-supported planktivores retain 0.35; unreported migration/imports receive zero; the sole detritus pool receives the loader's closed-pool routing assumption. Detritus EE is forced to 1 and its accumulation completed. All source departures and loaded values are retained in `../diagnostics/`.
3. Diet validation tolerance is 0.001 with **normalization disabled**. Source sums 1.0001 and 1.0002 remain visible and the stricter diagnostic diet check flags them. No detritus merge was needed, no parameter was tuned to achieve balance, and no shared scientific code was changed.

Only full direct GE, TE and With Egestion diagnostics were invoked; there was no global option, Monte Carlo run, broad method inventory or annual regional PPR. The uncompleted canonical cannot be certified as a complete source numerical model because two P/B cells and other source parameters remain unknown. The diagnostic staging is explicitly qualified.

## Validation and review limits

`validate.py`: **0 formatting errors, 50 warnings**, comprising the missing-GS warning and 49 missing detritus-fate rows. These are preserved source gaps. Independent Poppler coordinates cross-check the PyMuPDF numeric extraction; source/canonical comparisons check every scalar, diet and catch value, and a semantic roundtrip reconstructs all eight EwE files from canonical fields and retained fleet records. Exact trailing-zero/ZIP-byte identity is not claimed. The original converter reconstruction is retained with its known normalization/omission limitations; the `roundtrip_imports` directory is the source-preserving reconstruction.

`VERIFICATION.json` records the actual checks and source hashes. Source files and the regional workbook are unchanged. Scientific FAIL statuses remain FAIL even when extraction checks pass. No model was selected, no annual results were published, and central registration is proposed for the parent agent's serialized update only.
