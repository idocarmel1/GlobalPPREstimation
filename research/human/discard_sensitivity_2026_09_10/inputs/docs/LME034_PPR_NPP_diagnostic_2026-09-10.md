# LME_034 PPR/NPP investigation

Investigation date: 10 September 2026. Ecosystem: Bay of Bengal. This is an analysis of the saved atlas export inspected during this session. No model inputs, mappings, workbooks, or application code were changed for this investigation. Annual-NPP integration code was changing concurrently, so historical-denominator findings are explicitly tied to the saved export, not every future build.

## Main finding

The time-series plot displays **100 × PPR/NPP**, and its axis is **PPR / NPP (%)**. A value of 40 is a fraction of **0.40**, or 40%, rather than 40 times NPP. For 2019, using the exported regional ensemble median and the default model `34_1_Bay_of_Bengal_(1978)`, I reproduced:

| Quantity | Simple trophic chain | SPPR_1995_TE0.1 |
|---|---:|---:|
| Catch, million tonnes wet weight/year | 6.697726 | 6.697726 |
| PPR, million tonnes carbon/year | 391.717984 | 463.914011 |
| NPP, million tonnes carbon/year | 973.683757 | 973.683757 |
| PPR/NPP, fraction | 0.402305 | 0.476452 |
| Plotted PPR/NPP, percent | **40.2305%** | **47.6452%** |
| Catch with coefficients | 100% | 100% |

The two methods share the catches, 10% transfer efficiency, exponential trophic-chain assumption, carbon conversion, and NPP denominator. Agreement between them is therefore not independent validation.

These percentages are large, but tens of percent occur in the PPR literature. Pauly and Christensen's original analysis reported 24–35% for shelf, upwelling, and freshwater ecosystem categories. Those old, broad categories are context, not a Bay of Bengal validation or a sustainability threshold. [Original study record and abstract](https://www.worldfishcenter.org/publication/primary-production-required-sustain-global-fisheries).

## Calculation path checked

For taxon i, year y, wet-weight catch C, and transfer efficiency TE:

`PPR_carbon(y) = sum_i[C_i(y) × TE^(1 − TL_i)] / 9`

`plotted value(y) = 100 × PPR_carbon(y) / NPP_carbon(y)`

The simple method uses catch-taxon trophic levels. The model method first computes each functional group's trophic level from the diet/flow system, with cycles removed and detritus basal, then calculates `TE^(1−TL)`. Catch taxa mapped to several groups receive the weighted mean of those groups' SPPR coefficients. An effective TL inferred from such a coefficient is not necessarily the arithmetic mean of group TLs.

Relevant local sources:

- `PPRAtlas/atlas/time_series_metrics.js`, lines 58 and 64: carbon conversion and percentage calculation.
- `PPRAtlas/atlas/time_series_view.js`, line 145: percentage axis, or multiples when explicit baseline normalization is enabled.
- `PPRAtlas/trends.html`: saved, self-contained graph; inspected percentage formula and fixed-2019 data policy.
- `tools/build_time_series.py`, function `simple_annual`: sum of catch-taxon products.
- `PPREstimation/PPRCalculator.py`, functions `get_TL` and `SPPR_1995`: group TL and coefficient calculation.
- `tools/build_model_workbook.py`, functions `resolve_weights` and `build_taxon_sppr`: mapping coefficients.
- `PPRAtlas/data/time_series.json` and `PPRAtlas/data/network_ppr.json`: saved annual totals and group-mapped taxon coefficients.
- `SeaAroundUsExtraction/data/catch_by_taxon_year/LME_034.csv.gz` and `SeaAroundUsExtraction/global_output/tables/regions/LME_034/species.csv`: catches and TL inputs.
- `NPPExtraction/NPP_2019_filled_SAU_regions.csv`: denominator input.

The atlas uses satellite NPP, not `PPRCalculator.get_NPP()` or the calculator's within-model `get_PPR2NPP_ratio()`. Confusing these denominators would compare different quantities.

## Hypotheses and evidence

### 1. A universal 10% transfer efficiency is too low for the relevant pathways

**Strong sensitivity demonstrated; true regional TE remains unvalidated.** Raising TE makes each trophic step less costly. Recomputing the simple method with the same 2019 catches, TLs, and NPP gives:

| TE | PPR/NPP |
|---|---:|
| 5% | 335.71% |
| 10% | 40.23% |
| 12% | 23.36% |
| 15% | 12.12% |
| 20% | 5.29% |

This is the largest quantified lever. Baumann (1995), *A comment on transfer efficiencies*, showed that changing global TE from 10% to 15% changed the earlier global PPR result from 8% to 2.6%. [Paper](https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1365-2419.1995.tb00150.x).

The project's `SPPR_1995_TEmean` uses a model-derived catch-weighted mean of about 19.29% and gives 6.72% for 2019. Its efficiency definition and weighting need biological scrutiny; that lower answer is not evidence it is the correct one. Do not choose TE merely to obtain a comfortable ratio.

### 2. Trophic levels are too high for the fish actually caught

**Plausible, with exponential sensitivity.** Published species/family TLs can differ from local, seasonal, size-specific, or juvenile catch TLs. At TE=0.1, increasing TL by 0.3 multiplies PPR by approximately 2; by 0.5, by 3.16. Conversely, lowering every used TL by 0.3 would approximately halve the simple result. This uniform shift is a sensitivity scenario, not an estimated correction.

The simple-method 2019 TL range is 2.00–4.94. Taxa with TL ≥4 contribute only **17.99% of catch but 63.31% of simple PPR**. Name matching is exact for all 288 active 2019 catch labels, but exact matching does not establish biological accuracy of the assigned TL.

### 3. Summing separate trophic costs yields much more than using one average TL

**Confirmed mathematical explanation, not an arithmetic bug.** The catch-weighted mean TL is 3.4013. Applying the chain formula once at that mean produces **19.26%**, whereas summing taxon-specific PPR produces **40.23%**. The exponential function is convex: high-TL catches have disproportionate influence. A back-of-envelope calculation using mean TL will therefore underpredict this implementation. True TL variability and uncertain/noisy TL estimates should be distinguished; the latter can also introduce nonlinear estimation bias.

### 4. The unidentified-fish mapping carries excessive trophic cost

**Strongest identified explanation of the difference between methods.** “Marine fishes not identified” is **20.34% of 2019 catch**. Its simple TL is 3.28 and SPPR is 190.546. Its model-weighted SPPR is 624.961, equivalent to TL 3.7959 for this formula.

This one label contributes **2.96 percentage points** in the simple method and **9.71 points** in the model method. The difference, **6.75 points**, accounts for **91.06% of the net 7.41-point difference between the two methods**. Other positive and negative differences partly cancel. It is not 91% of total model PPR.

The mapping assigns this residual catch to several demersal groups using biomass weights. Its actual species and size composition should be checked before treating either assigned trophic cost as representative. Using only the simple coefficient for this label would put the model total at approximately **40.89%**, leaving all other model coefficients unchanged.

### 5. Regional/group allocation weights overrepresent expensive groups

**Real uncertainty; modest measured effect for the requested method.** The source model separates regional groups. The mapping uses fixed biomass proportions to allocate LME catches across regional pools. Replacing only the `model_biomass` weight rules, while keeping other rules unchanged, gives:

- Existing mapping: **47.65%**.
- Model-catch weighting: **46.47%**.
- Equal weighting: **49.88%**.

Weights sum to one, so these results do not support a duplication error. Existing mapping notes report larger sensitivity for another method (`new_GE`); those numbers should not be transferred to `SPPR_1995_TE0.1`.

### 6. A 1978 food web is being applied to decades of changed fisheries

**Confirmed assumption; direction of bias uncertain.** The default model's diets and group coefficients remain fixed across 1950–2019. The annual model curve changes with catch amounts and composition, not evolving food-web structure. Changed prey availability, fishing down, juvenile capture, and migration can make historical TLs inappropriate for recent catches. The simple method likewise applies fixed reference TLs through time.

Guénette's report explicitly describes a 1978 Ecopath baseline and limited time-series constraints. [Archived original report](<C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/PPRAtlas/archive/regions/LME_034/LME034-Guenette-2013/009031359-84f3dc3d.pdf>), especially abstract and methods. The source model was recomputed, but this investigation did not independently re-transcribe every diet entry from the PDF.

### 7. Reconstructed catches are being compared with literature based on reported landings

**Confirmed and substantial.** The numerator includes reported and unreported catches and discards. In 2019, unreported catch is **23.22% of total catch**. Using only reported catches gives **31.10% / 36.96%**, compared with **40.23% / 47.65%** using total reconstructed catches. These are alternative catch definitions, not proposed corrections.

Using landings only gives **38.96% / 46.06%**. Discards account for only **1.27 / 1.58 percentage points**. Reported/unreported and landings/discards are two partitions of the same total; their reductions must not be added together.

The TWAP Bay of Bengal assessment reported PPR approaching **20% in 1998** for reported landings. The current simple calculation for 1998 is **33.41% with all catches** or **22.80% with reported catches only**, both using the saved 2019 NPP. This is useful reconciliation, not an exact replication of the assessment's historical NPP, catch coverage, or trophic assignments. [TWAP assessment, LME 34](https://iwlearn.net/documents/download/4348c7eb-92aa-45ac-aa62-891c35e53268), indexed text under “Primary Production Required”.

### 8. Catch reconstruction or geographic catch allocation is biased upward

**Plausible; not established by this audit.** Country reports, reconstruction multipliers, spatial allocation, taxonomic aggregates, or accidental inclusion of catch from outside the boundary could inflate PPR linearly. The TWAP assessment itself raised possible overestimation of reported landings, but high PPR alone cannot prove that claim. The raw regional file has no duplicate taxon–year rows; upstream reconstruction and catch-location assignment still require separate validation. There is no evidence here that aquaculture was actually included.

### 9. The selected satellite NPP algorithm is low

**Confirmed uncertainty, with a twofold spread among available inputs.** Holding catches and coefficients fixed:

| NPP source | NPP, million t C/year | Simple | Model TE0.1 |
|---|---:|---:|---:|
| Antoine–Morel / ensemble median | 973.68 | 40.23% | 47.65% |
| VGPM | 613.98 | 63.80% | 75.56% |
| Eppley-VGPM | 1,255.28 | 31.21% | 36.96% |
| CbPM | 1,063.42 | 36.84% | 43.62% |
| CAFE | 626.71 | 62.50% | 74.02% |

This is algorithm spread, not a statistical confidence interval. Shared inputs mean these estimates are correlated, and the median is not ground truth. A directly relevant validation reference is Kalita and Lotliker's *Assessment of satellite-based Net Primary Productivity models in different biogeochemical provinces over the northern Indian Ocean*, [DOI](https://doi.org/10.1080/01431161.2023.2247533). Bibliographic identity was verified through INCOIS/MoES records; publisher full text was not accessible in this session, so no model-ranking result is inferred from it.

### 10. The graph uses the unscaled NPP column instead of the coverage-adjusted estimate

**Specific integration discrepancy supported by the files.** Both NPP tables contain unscaled `ens_median_tC_yr = 973.684 million t C/year` and `scaled_median_tC_yr = 1,061.393 million t C/year`. The atlas reads the former. The documented ensemble workflow scales common-mask algorithm ratios onto the filled baseline; see `NPPExtraction/METHODS.md`, §6.2, and `npp/ensemble.py`.

Using the available scaled median gives **36.91% / 43.71%**, an 8.26% relative reduction in each ratio. This is a concrete column-choice issue to resolve, not proof that the scaled estimate is unbiased. The common-area number is about 97.19% of water area, but it is not sufficient to characterize month-by-month gaps or production lost to them. No satellite rasters were redownloaded or reintegrated for this audit.

### 11. Historical catches are divided by a fixed 2019 denominator

**Confirmed in the saved JSON and HTML inspected.** The data policy says the 2019 regional NPP is reused for every catch year. Historical ratios consequently do not describe historical changes in NPP. The direction of bias depends on whether actual historical NPP was above or below the 2019 value. This does not explain the high 2019 endpoint.

Annual-denominator integration was being edited concurrently. A future/rebuilt graph may behave differently; verify its exported NPP arrays and provenance before carrying this finding forward.

### 12. Fishing pressure relative to actual production really is high

**Ecologically plausible; not proven solely by PPR.** With the fixed denominator, simple PPR rises from **17.11% in 1978 to 40.23% in 2019**, alongside catch increasing from 3.044 to 6.698 million tonnes. Much of the Bay is nutrient-limited despite productive coastal zones. The mechanism whereby freshwater stratification limits nutrient supply was investigated by Prasanna Kumar et al. (2002), *Why is the Bay of Bengal less productive during summer monsoon compared to the Arabian Sea?* [Paper](https://doi.org/10.1029/2002GL016013).

Stock depletion can temporarily support catches above steady-state replacement, and fish caught in one year accumulated production over previous years. These are possible ecological/time-scale explanations, not evidence that the present catch is sustainable or that the model measures depletion.

### 13. Satellite retrievals miss or misrepresent productive places and periods

**Plausible; bias direction not established.** Clouds, coastal masking, turbid water, coloured dissolved matter, and unusual vertical chlorophyll profiles can distort integrated NPP. Subsurface productivity varies strongly in the Bay: Schlosser et al. (2026), *Monsoons, plumes, and blooms: intraseasonal variability of subsurface primary productivity in the Bay of Bengal*, documents this with autonomous observations. [Paper](https://os.copernicus.org/articles/22/443/2026/).

Satellite NPP products estimate water-column production; they are not simply surface chlorophyll sums. An observed subsurface chlorophyll maximum does not by itself quantify missed carbon production. Turbidity can also inflate apparent chlorophyll, and monsoon clouds reduce real productivity as well as retrieval availability. It would be unjustified to assume all such effects lower the denominator.

### 14. Phytoplankton NPP omits other basal support for catches

**Plausible, unquantified.** Benthic algae, seagrass, mangrove-derived organic matter, and imported terrestrial carbon can support food webs while lying outside a pelagic phytoplankton NPP denominator. The chain methods produce a basal-production equivalent without separating locally photosynthesized carbon from imported support. Adding every detrital flow to NPP would be wrong: locally recycled detritus is not new primary production. Establish source fractions and avoid double-counting before adjusting the denominator.

### 15. The ecological support area differs from the catch/NPP polygon

**Documented model-domain mismatch; numerical impact unquantified.** Guénette's study covers approximately **6.205 million km²**, including Maldives/high-seas areas, whereas the project's LME water area is about **3.656 million km²**. The mapping already excludes region-1 shelf groups, but the diets of shared pelagic groups still come from the larger system. Mobile fish may feed outside the catch polygon. These facts justify a representativeness/source-support audit; they do not justify multiplying the ratio by the ratio of the two areas.

Concentrating fishing in coastal hotspots while summing NPP over the entire LME does not mechanically inflate the whole-LME ratio. For a fixed numerator, including additional offshore NPP increases the denominator and lowers the ratio. The whole-LME percentage can mask larger local pressure. [Mapping geographic rationale](<C:/Users/idoca/Desktop/אישי/אקדמיה/תואר שני/מחקר/BTN/GlobalPPREstimation/data/LME_034/mapping/34_1_Bay_of_Bengal_(1978).notes.md>).

### 16. A single wet-weight-to-carbon conversion is imperfect

**Low-priority biological assumption; no missing factor of nine found.** Both numerator and denominator are put into carbon units by dividing wet-weight PPR once by 9, following the conventional formula. Species/group carbon fractions can differ. If the correct wet:carbon factor were larger than 9, the current numerator would be too large; a smaller factor would increase the ratio. There is no evidence for a factor-of-nine implementation error in these curves.

### 17. A trophic-chain footprint is being interpreted as a strictly measured fraction of local NPP

**Important conceptual limitation.** The calculation is a catch-associated production-equivalent estimate under fixed transfer assumptions. It does not enforce annual mass balance with the satellite denominator, resolve all pathways, track mobile carbon, or demonstrate sustainability. A high ratio may reflect a poor approximation or genuine pressure; a ratio below one is not automatically safe.

Nor is there a general guarantee that replacing the chain with a detailed network lowers PPR. Luong, Dewulf and De Laender (2020), *Quantifying the primary biotic resource use by fisheries: A global assessment*, found conventional estimates could underestimate network-based PPR by up to a factor of five in their study. [Authors' institutional research summary](https://ilee.unamur.be/publications-1/natural-resources-characterization-and-management), [article DOI](https://doi.org/10.1016/j.scitotenv.2020.137352).

## Computational explanations checked and deprioritized

- **40 as a raw ratio or a baseline multiple:** the investigated calculation was explicitly unnormalized percentage mode. The saved axis and formula agree.
- **Missing carbon conversion:** the plot divides PPR by 9 once, then calculates the percentage.
- **Wrong trophic exponent:** both requested calculations use `TL−1`, equivalently `TE^(1−TL)`.
- **Duplicate annual rows or duplicated mapping weights:** no duplicate taxon–year rows; all 315 mapping labels unique; resolved weights sum to one within floating-point precision.
- **A stale/incorrect model SPPR workbook:** recomputing `SPPR_1995(0.1)` from the model JSON matches saved group coefficients to maximum absolute difference about **1.55 × 10⁻¹¹**.
- **A singularity in the chain calculation:** the model's uncut TLs are higher than the cycle-removed values for the inspected top groups; cycle removal is not inflating those TLs. Divergence flags for other symbolic methods do not explain these two requested curves.
- **Annual summation/plot arithmetic:** independently recomputed 2019 raw-catch products agree with saved totals within the documented rounding. Running the actual graph aggregation gives 40.230514% and 47.645245%.
- **Model catch added to observed catch:** the annual numerator is regional catch multiplied by coefficients. Model catches influence some coefficients/weights but are not added as a second catch total.

These checks validate the observed computational path. They do not constitute a complete source-data audit or proof that every biological assumption is correct.

## What to investigate first

1. Resolve the NPP column choice and verify annual denominators in the rebuilt export.
2. Audit “Marine fishes not identified” and the high-TL taxa contributing most PPR, using local composition and catch-size data.
3. Carry TE, TL, NPP algorithm, and catch-definition sensitivity into the reported results rather than publishing a single percentage as exact.

## Internet and Perplexity provenance

Internet access was verified by successful web searches, article/repository retrievals, and a completed Perplexity website query. [Perplexity search session](https://www.perplexity.ai/search/f3ade8ca-aac0-4c49-8469-5e5ffa90e81f).

Perplexity was used for discovery; its response was not treated as authoritative. In particular, it mislabeled the 2020 Luong et al. DOI as a Libralato 2008 reference, and made overly strong claims about absence of Bay-specific papers and the direction of optical/detrital effects. Those claims are not adopted here. Several publisher full-text endpoints denied automated access; where relevant, evidence came from accessible original abstracts, authors' institutions, or indexed assessment text, with limitations identified above.

The inspected export is identified by SHA-256 `a25c00a123e730ef5321d448f8547ddd901e111d431ca74d5b18c1b1b8f297ba` for `PPRAtlas/data/time_series.json`. Its default LME_034 NPP is a scalar, 973,683,756.8091958 t C/year. The matching network export hash is `a4332428464cdfbf4c261def461c1a30abad7800841850c32a45a14ea0199f77`. These identifiers distinguish this diagnosis from the concurrent annual-NPP integration.
