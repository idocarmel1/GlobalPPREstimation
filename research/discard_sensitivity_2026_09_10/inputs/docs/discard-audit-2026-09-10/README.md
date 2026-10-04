# Discards and comparability of ecosystem PPR/NPP

Analysis snapshot: 10 September 2026. Catch year: **2019**. This is a read-only diagnostic; no live model, catch, mapping, or atlas files were changed.

## Finding and recommendation

The current annual catch pipeline consistently retains reported and unreported **landings plus discards**. Consequently the atlas is not simply including annual discarded catch in some ecosystems and excluding it in others according to the source article. The source-model assumptions can, however, affect the SPPR coefficients applied to that catch, especially for methods that explicitly trace detrital recycling.

Use a single reporting convention across ecosystems: **PPR supporting total reconstructed catch**, accompanied by landings-only PPR and the discard contribution. Do not interpret this gross catch footprint as net primary production physically exported from the ecosystem. Compare published PPR values only after checking their catch definition, method, basal-source scope, carbon conversion, year, and ecosystem boundary.

Pauly and Christensen (1995) explicitly included discarded bycatch in their PPR assessment. Sea Around Us currently describes its catch reconstruction as including reported and unreported catches, both landed and discarded. These support the recommended convention; they do not establish that discards have negligible ecological effects.

- [Pauly and Christensen (1995), original article](https://api.seaaroundus.org/wp-content/uploads/2015/04/PrimaryProductionRequiredToSustainGlobalFisheries.pdf)
- [Sea Around Us FAQ and catch definitions](https://www.seaaroundus.org/faq/)
- [Sea Around Us catch reconstruction methods](https://www.seaaroundus.org/doc/Methods/CatchReconstructionMethod/Methods-Catch-tab-May-02-2016.pdf)
- [EwE fisheries inputs, including discard mortality and fate](https://pressbooks.bccampus.ca/ewemodel/chapter/spatial-fishery-dynamics/)

## What was estimated

For ecosystem e, taxon i, and selected method m, hold mapped SPPR coefficients s_i,m fixed:

    PPR_landings = sum(landings_i * s_i,m) / 9
    PPR_discards = sum(discards_i * s_i,m) / 9
    PPR_total = PPR_landings + PPR_discards
    discard share (%) = 100 * PPR_discards / PPR_total
    increase over landings-only (%) = 100 * PPR_discards / PPR_landings
    discard contribution to PPR/NPP (percentage points) = 100 * PPR_discards / NPP

The divisor 9 is the project's existing wet-weight-to-carbon conversion. It cancels from the discard share. Landings and discards use the same taxon's coefficient, the current default selected-method treatment of unidentified taxa, and all-basal-source scope. These estimates quantify changing the annual catch boundary with fixed coefficients. They are **not** estimates of how much PPR would change if the original ecosystem model were reconstructed with different discard routing.

The simple-chain coefficients were independently recomputed as 10^(TL-1). Model coefficients came from the saved verified network export; source workbook hashes were checked. All numerical estimates retain missing mappings and exclude failed or unavailable model methods. A verified export is not a claim that the underlying ecological model is free of scientific uncertainty.

## Results for the ten selected ecosystems

Percent of estimated total PPR attributable to discarded catch; these are percentages of PPR, not percentage points of PPR/NPP. Model column: SPPR_1995_TE0.1 with the atlas default model for that region at the analysis snapshot.

| Ecosystem | Discards / catch | Simple-chain discard share of PPR | Model discard share of PPR |
|---|---:|---:|---:|
| Eastern Central Pacific high seas, HS_077 | 11.08% | 7.38% | Unavailable |
| Humboldt Current, LME_013 | 3.03% | 4.52% | 4.77% |
| Canary Current, LME_027 | 6.06% | 6.66% | Unavailable |
| Guinea Current, LME_028 | 17.01% | 19.35% | 18.14% |
| Arabian Sea, LME_032 | 3.91% | 2.16% | 3.64% |
| Bay of Bengal, LME_034 | 3.67% | 3.16% | 3.32% |
| Gulf of Thailand, LME_035 | 4.86% | 7.28% | 4.49% |
| South China Sea, LME_036 | 7.15% | 6.62% | 9.65% |
| East China Sea, LME_047 | 3.60% | 1.91% | 4.63% |
| Sea of Okhotsk, LME_052 | 27.03% | 20.15% | 27.67% |

Unavailable models were not replaced with zero. The model estimates cover 98.05–100% of catch and 96.95–100% of discards across the eight ecosystems with available defaults. Their shares refer to the portion with numerical coefficients, not an imputed complete ecosystem total. Missing taxa could have unusually high SPPR; catch coverage alone does not bound missing PPR. The full model table identifies the exact model and coverage for every result, including alternative South China Sea and East China Sea models.

Across the project's **65 LME identities with positive estimated PPR**, the simple-chain discard share has a median of **6.15%**, ranges from **0 to 35.85%**, exceeds 10% in **19** regions, and exceeds 20% in **6**. Largest examples include South Brazil Shelf (35.85%), Iberian Coastal (32.77%), and Gulf of California (26.78%). These are cross-region summaries, not a unique global aggregate.

For the 282 EEZ identities with positive estimated PPR, the median is 3.26%; the highest is Kuwait (73.79%). For 17 positive-PPR high-seas identities, the median is 1.16%; Northwest Atlantic high seas is highest (37.51%). These values describe the local 2019 reconstruction and the chosen simple-chain coefficients, not independent measurements of ecological impact. Do not sum EEZs, LMEs, and high-seas regions together: their geographical definitions can overlap.

### Bay of Bengal example

Using the current coverage-adjusted 2019 ensemble NPP of 1,061,393,189.80 t C/year:

- Model SPPR_1995_TE0.1: total PPR **463.91 million t C**, landings **448.52 million**, discards **15.40 million**. PPR/NPP changes from **43.71% to 42.26%** when discards are omitted: **1.45 percentage points**, or **3.32%** of total PPR.
- Under new_GE, the direct discard share is **3.85%** of total PPR; under new_TE_EEfix it is **3.94%**. Those methods have different overall PPR levels. Their fixed-coefficient discard shares do not quantify their sensitivity to rerouting discards inside the food web.

Thus direct discard inclusion is a modest part of the large Bay of Bengal estimate, but a major comparability issue for regions such as Guinea Current and Sea of Okhotsk.

## Source-model representation: what is known and what remains uncertain

The annual catch boundary and the source-model accounting are different layers:

1. `SeaAroundUsExtraction/src/ppr_pipeline/ingest.py` explicitly retains Landings and Discards; the annual distilled tables preserve separate totals. The atlas then sums the external catch against each taxon's coefficient. It does not directly reuse a paper's published total PPR.
2. `PPREstimation/ModelData.py` reads the source field `export` into `catch`. The imported schema does not consistently preserve a separate discard quantity. Some Humboldt JSONs have `landings_total`, `discards_total`, and fleet metadata, while 14 of the 16 selected model JSONs lack separate group-level discard keys. The Northern Humboldt model also has a Fishery offal compartment. Absence of a field is not evidence of zero discarding, and presence of an offal compartment does not by itself establish correct routing.
3. The inspected extraction converter combines Landings.csv and Discards.csv into `export`. Its reconstructed workbook labels that combined field Landings. This is a provenance/labeling risk when reading reconstructed workbooks as if they were original landings tables. It does not mean that adding SAU discards to annual catch double-counts the paper's catches: the latter are not separately added to the annual numerator.
4. The calculator derives ordinary flow to detritus from non-predation mortality plus egestion (`M0 + egestion`). It does not read separate `discards_total` or fleet discard-fate fields into a dedicated return flow. Returned discarded biomass may be represented incompletely, implicitly, or in source-specific ways; resolving this requires tracing each original model and its conversion.
5. Simple-chain SPPR is independent of the Ecopath source. SPPR_1995_TE0.1 uses a common TE and model-derived TL, treating detritus as basal. Methods that trace recycling or derive efficiencies from model flows need a more extensive source-accounting audit. Food-web structure and parameter inference can carry source assumptions even without an explicit discard term.

The Bay of Bengal source report says its 1978 model combined landings and discards as catch (Guénette 2013, catch subsection; archived text `PPRAtlas/research/text/84f3dc3dc64213b2f84c.txt`, lines 281–285). This is source-specific evidence, not a convention to assume for every article.

## Proposed solution for the project

1. **Standardize the reported quantity.** Main ecological catch footprint: total reconstructed catch. Always provide landings-only and discard-only components for the same year, method, NPP, taxon treatment and coverage. Retain the distinction between unreported landings and discards. A landings-only comparison removes direct discarded catch but does not harmonize the model's internal recycling assumptions.
2. **Add a discard-accounting record to every source model.** Record whether catches are landings only, landings plus discards, separate known values, or unspecified; retain source table/page, units, year, fleet/group, dead-versus-total-discard definition, return destination and survival assumptions. Keep unknown separate from numerical zero. Record offal separately where it is already part of landings and processing output.
3. **Preserve removals and return flows separately.** Fishery removal from a living group may include dead discards. Returned material must go to its documented internal compartment; material retained ashore or exported leaves the boundary. Do not put the same discard into both natural mortality and a new fishery return term. Do not treat internally generated discards as new external primary production or new external detritus input. Check both living-group and detritus balances.
4. **Keep the published model, and create explicitly labeled harmonized scenarios where evidence supports them.** For recycled-flow methods, compare coefficients/PPR with documented discard routing and an explicit no-return sensitivity. Recompute and check mass balance/convergence; do not inject a return term into an already balanced model and assume all other parameters remain valid. Models with insufficient source evidence remain flagged for uncertain accounting.
5. **Separate two uncertainty analyses.** First, hold coefficients fixed and vary catch/discard quantities. Second, hold the same external annual catch fixed and vary supported model-accounting scenarios, reporting the resulting change in coefficients and PPR. The numerical shares in this report quantify only the first layer.

As a practical audit priority, examine Sea of Okhotsk and Guinea Current first among the selected ecosystems; South Brazil Shelf, Iberian Coastal and Gulf of California also merit attention if their food-web models are added. This is a priority based on direct contribution, not proof that the unknown recycling error is largest there.

Discards may have a different size or species composition than landings. When they are juveniles or poorly identified mixtures, reusing the same taxon SPPR is an assumption. For fixed coefficients, a proportional error in discard PPR changes total PPR by that error multiplied by the discard share. An illustrative ±50% discard-component error gives ±1.66% total PPR in Bay of Bengal and ±13.84% in Sea of Okhotsk for the model method; these are scenarios, not confidence intervals. Indirect coefficient changes can affect landed taxa too, so the direct share is not an upper bound on full model uncertainty.

Sea Around Us's documented reconstruction generally assumes discarded organisms are dead, with exceptions where survival information is incorporated. Do not apply a second mortality correction without checking the data definition. [Source methods](https://www.seaaroundus.org/doc/Methods/CatchReconstructionMethod/Methods-Catch-tab-May-02-2016.pdf)

## Files and verification

- [All 366 ecosystem identities, simple-chain results](ecosystems_2019_simple_chain.csv): 364 positive-PPR results; Arctic Sea HS_018 and Central Arctic Ocean LME_064 have no catch and no defined discard share.
- [169 available model/method results across 10 model variants](model_methods_2019.csv): all basal sources, separate model identity, coverage, carbon totals, and PPR/NPP effects.
- [Unavailable model/method ledger](unavailable_models_and_methods.csv).
- [Taxon contributions to model-based discarded PPR](model_discard_taxa_2019.csv).
- [Source JSON discard-field inventory](input_model_discard_fields.csv): inventory, not a completed source-paper accounting audit.
- [Input hashes, assumptions, and checks](provenance_and_checks.json).
- [Independent raw ZIP checks](raw_archive_verification.json): South Brazil Shelf, Guinea Current, Bay of Bengal, and Sea of Okhotsk.

All 366 simple-chain source tables were checked against per-taxon TL products and saved annual totals; landings plus discards reconciled with total catch, and their PPR components reconciled with total PPR. Model coefficients were read from the saved export only when model/method status was available and workbook hashes matched. Model PPR uses unrounded source catch, so it can differ slightly from workbook totals calculated from rounded taxon catches. These numerical checks do not verify the biological accuracy of catch reconstructions, model coefficients, or NPP.
