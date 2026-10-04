# Jellyfish feeding reconstruction from Gorbatenko (2018)

The dissertation supports a complete annual **wet-mass diet over twelve source prey categories**, but it does not yet support a complete carbon diet or a complete diet over the selected model's 22 groups. No partial diet was normalized and no canonical source, model, map, or validation document was changed.

## Exact source reconstruction

Tables 4.13–4.16, printed/PDF pages 124–125, concern the whole Okhotsk Sea, 2006–2014. Table 4.15 gives large-jellyfish consumption of 772.7 thousand wet tonnes/year; Table 4.16 gives small-jellyfish consumption of 2404.4, yielding **3177.1 thousand wet tonnes/year**. Large jellyfish have ten leaf prey rows and small jellyfish four; shared copepod and euphausiid rows combine into twelve categories. Zooplankton and ichthyoplankton subtotal rows must not be added as separate prey.

The complete combined wet diet is each category's annual consumption divided by 3177.1. It closes exactly because the complete annual leaf flows are available. It is not a carbon diet. Source printed percentages remain separately preserved in the CSV/JSON; they are not used to override the absolute annual flows.

| Source prey category | Annual wet consumption, thousand t | Full combined wet diet, % | Current model prey group |
|---|---:|---:|---|
| Copepods | 2477.3 | 77.973624 | 4 |
| Euphausiids | 332.2 | 10.456076 | 5 |
| Amphipods | 36.7 | 1.155141 | Unresolved; conditional hyperiid mapping discussed below |
| Chaetognaths | 25.9 | 0.815209 | 7 |
| Pteropods | 5.8 | 0.182556 | No dedicated group |
| Mysids | 5.7 | 0.179409 | No dedicated group |
| Decapod larvae | 4.8 | 0.151081 | No stage-matched group |
| Jellyfish | 32.8 | 1.032388 | 14, with prey-size uncertainty |
| Fish eggs | 62.9 | 1.979793 | Taxon/stage allocation unresolved |
| Fish larvae | 12.0 | 0.377703 | Taxon/size allocation unresolved |
| Meroplankton | 63.9 | 2.011268 | Composition/allocation unresolved |
| Other | 117.1 | 3.685751 | Composition/allocation unresolved |

Table 4.13 gives seasonal stock, in thousand wet tonnes:

| Consumer | Spring | Summer | Autumn | Winter |
|---|---:|---:|---:|---:|
| Small <20 mm* | 1185 | 11230 | 555 | 912 |
| Large >20 mm** | 1022 | 2539 | 1618 | 1329 |
| Combined, 1.5–750.0 mm | 2207 | 13769 | 2173 | 2241 |
| Small daily ration, % body mass | 0.15 | 0.20 | 0.20 | 0.15 |
| Large daily ration, % body mass | 0.10 | 0.15 | 0.15 | 0.10 |

The equal-four-season combined mean stock is 5097.5 thousand wet tonnes. Using that stock and the table's full Q gives wet QB = **0.623266307/year**. This mean is calculated, not a separately printed annual stock. Table 3.9 on p.88 gives different small-jellyfish stocks in several seasons (1185,11953,703,974 thousand tonnes, versus Table 4.13's 1185,11230,555,912); it must not silently replace the stocks actually used for feeding. The source does not explain the differences, which could reflect a subset discrepancy rather than a numerical typo. The 2019 article's 4.1 million wet tonnes is another stock/period basis. Source * and ** markers after size classes lack an explanation on pp.124–125. Earlier Table 3.9 p.88 explains * as BSD plankton-net plus trawl catches and ** as trawl catches; that earlier explanation is retained as separate evidence, without claiming an explicitly restated Table 4.13 footnote.

## Recovered carbon factors and limitations

Table 7.1 p.298 supplies seasonal taxonomic-group wet/carbon factors. Page 295 describes the 2006–2014 chemical sampling (March–December, 424 samples). These factors are temporally compatible with the feeding tables. Winter–spring factors were applied separately to winter and spring flows; summer–autumn factors to summer and autumn flows. The conversion is `Q_C [million t C/year] = sum(Q_wet_season [thousand t/year] / wet_to_C_factor_season) / 1000`.

| Group | Winter–spring wet/C | Summer–autumn wet/C |
|---|---:|---:|
| Copepods | 16.02 | 12.51 |
| Euphausiids | 12.60 | 9.11 |
| Mysids | 17.27 | 12.53 |
| Hyperiids | 16.66 | 12.88 |
| Pteropods | 22.27 | 17.79 |
| Oikopleura | 21.72 | 20.97 |
| Chaetognaths | 22.98 | 17.78 |
| Jellyfish | 320.27 | 279.33 |
| Other zooplankton | 20.14 | 15.66 |

The table notes SE does not exceed 10%. Direct printed factors are preferable to reciprocals of heavily rounded carbon-per-mg columns. These are **taxonomic group means**, not demonstrated biomass-weighted or prey-stage-specific factors. The dissertation itself cautions on pp.298–299 that species proportions and seasons matter when using taxonomic averages. Applying group factors to the table's matching prey groups is an explicit aggregate approximation; the small-jellyfish copepod row includes copepod eggs and early stages (p.124), and jellyfish prey lacks a size allocation. Appendix 46 p.456 lists group/species composition but does not provide the annual prey-stage mix.

Using those source seasonal means gives accounted prey-carbon Q of **0.228010885949 million t C/year**:

| Accounted category | Million t C/year |
|---|---:|
| Copepods | 0.192005227279 |
| Euphausiids | 0.033739332323 |
| Chaetognaths | 0.001421057681 |
| Pteropods | 0.000312456381 |
| Mysids | 0.000415479976 |
| Jellyfish | 0.000117332310 |

This is a lower bound **conditional on the aggregate-factor conversions**, because six other prey rows have positive wet consumption but unresolved matching carbon factors. It is not an unconditional statistical bound. Under the same group-mean approximation, equal-four-season jellyfish carbon stock is **0.017740140465 million t C**; net jellyfish are mainly Aglantha (>90%, p.86) while trawl jellyfish are mainly scyphozoans, so that group-factor stock conversion is also conditional.

A separately labelled comparison preserves the 2019 article's annual anchor factors for copepods (14), euphausiids (10.6), chaetognaths (20), and jellyfish (285.2), adding seasonal source factors only for mysids and pteropods. It gives **0.210427566011 million t C/year** accounted Q, compared with the prior three-prey minimum 0.209584622642. This mixes the dissertation feeding period with the 2019 model's conversion basis and must remain a scenario, not an exact replacement extraction.

## Exact remaining gaps

The following categories lack a genuinely demonstrated factor matching their full prey composition/stages:

| Category | Unconverted wet consumption, thousand t/year | Specific missing evidence |
|---|---:|---|
| Amphipods | 36.7 | Fraction that is model hyperiids versus other amphipods |
| Decapod larvae | 4.8 | Larval-stage wet/C and taxon mix; adult benthic decapod tissue is mismatched |
| Fish eggs | 62.9 | Species mix and egg-stage wet/C; not solely pollock eggs |
| Fish larvae | 12.0 | Species/size mix and appropriate whole-prey larval wet/C |
| Meroplankton | 63.9 | Mixed early invertebrate composition and larval wet/C |
| Other | 117.1 | Actual Table 4.16 prey composition and its conversion factor |
| **Total** | **297.4** | **9.3607378% of full source wet Q** |

Table 7.1's `Other zooplankton` factor is **not proven to describe Table 4.16's `Other` food row**. Matching the word alone cannot establish prey composition. Page 118 mentions protozoans and other small plankton in small jellyfish feeding, but does not allocate the 117.1 thousand tonnes among those components. Likewise, Appendix 47 adult benthos chemistry and Appendices 48–50 fish muscle chemistry are not factors for mixed eggs or larval whole prey. Whole-dissertation keyword searches found no directly matching conversion for those unresolved categories; this is a documented search result, not proof that no further external source exists.

Amphipod mapping has some support: p.118 identifies hyperiids among main crustacean prey, and Appendix 14 p.422 explicitly lists Themisto pacifica/libellula. However, its Amphipoda subtotal also has an `Other` fraction (0.8% for A. limbata, 0.2% for Chrysaora melanaster). Its consumer-specific summer diets, published from 2005 observations, lack matched 2006–2014 annual consumer weights. Thus mapping all 36.7 thousand tonnes to hyperiids is a declared scenario only. It adds 0.002488256172 million t C/year with the dissertation seasonal hyperiid factors, or 0.002531034483 with the 2019 factor 14.5, leaving **260.7 thousand wet tonnes/year** unconverted. A full carbon diet still cannot be calculated.

Exactly **308.9 thousand wet tonnes/year** have no unambiguous allocation to the current 22 groups under the strict crosswalk, including pteropods and mysids whose carbon factors are recovered. A source total plus arbitrary aggregate mappings cannot close these gaps without adding new assumptions. Appropriate options are to retain explicit extra prey nodes or documented imports, or obtain justified composition/allocation; dropping the rows and normalizing survivors would change the reconstructed diet.

## Assimilation and human-error investigation

Pages 120 and 123 explicitly use **70% food assimilation** when calculating jellyfish daily ration. Its complement is 30%, so `GS = 0.30` is source-supported for that feeding calculation. Page 20 explains that the ration calculation derives from a balance relating growth, metabolic costs and feeding, expressed in calories. Therefore transferring 0.30 into a carbon-currency Ecopath GS assumes energy/carbon assimilation equivalence; the feeding Q is not independent of the source growth/metabolism assumptions. This is stronger evidence than an undocumented universal GS of 0.20, but does not establish measured carbon assimilation.

Under that assumption and retaining the 2019 production P = 0.144 million t C/year only for comparison, accounted Q × 0.70 − P is positive: **0.015607620164** for seasonal dissertation factors, or **0.003299296208** for the mixed 2019-anchor scenario. Consequently these textual feeding estimates do not force negative respiration at that production. This is a scoped energy feasibility check, **not native Ecopath balance**: model periods/stocks and the missing food rows remain unresolved. Substituting a different stock while retaining PB changes P and invalidates this fixed-P comparison.

The original source preserves several small inconsistencies:

1. Prose on p.124 gives large Q = 772.8, versus Table 4.15 total and exact annual leaf sum 772.7 thousand tonnes/year. The table value is used, and the prose alternative is retained.
2. Small copepod seasonal cells sum to 2178.2 versus annual 2178.1; small euphausiid seasonal cells sum to 45.2 versus annual 45.3. Seasonal carbon conversions use seasonal cells; complete annual wet diet uses annual cells. Neither is silently changed.
3. Some source printed annual percentages do not equal ordinary one-decimal rounding of annual flows divided by the printed total. They remain raw source percentages; reconstructed wet DC uses annual flows.
4. Seasonal consumption is approximately daily consumption ×90 days, consistent with 360-day annual arithmetic. This explains a possible 365/360 (~1.39%) convention difference, not an order-of-magnitude correction. No rescaling was performed.
5. Daily ration uses percent of body weight: 0.10% = 0.001, 0.15% = 0.0015, 0.20% = 0.002. Seasonal stock × these fractions ×90 broadly reproduces the source totals after rounding. Interpreting 0.10 as a fraction would create a 100-fold error unsupported by the table.

These verified details do not justify multiplying source consumption by 10 or 1000 or moving a decimal to force balance. They support recovering omitted feeding pathways and distinguishing wet prey from prey carbon and jellyfish carbon.

## Evidence products and verification

`source_tables_4_15_4_16.csv/json` preserve all 18 source rows, all daily/seasonal/annual columns and printed percentages. `source_tables_4_13_4_14.json` preserve stocks, rations and large seasonal diets. `table7_1_carbon_factors.csv/json` preserve all nine factor pairs. `wet_prey_flows_and_carbon_contributions.csv/json` retain all fourteen leaf rows, source provenance, rounding differences, wet diet and partial carbon contributions; exact carbon DC stays null. `aggregated_source_prey_categories.csv/json` combine them into twelve source categories. `summary.json` contains the scoped calculations and unresolved masses. The reproducible script is `extract_jellyfish.py`.

Tables 4.15/4.16: **180 numeric cells** match independent pypdf text extraction against coordinate-based extraction. Tables 4.13, 4.14 and Table 7.1 factors add **64 checked source cells**. Source pages 123,124,125,298,422,456 were rendered from the original PDF and visually reviewed. `source_coordinate_lines.json`, `source_page_text.json`, `dissertation_p*_source.png` and `verification.json` retain this evidence. The original PDF hash remains `a26ef69acf1c00b32f49772e52b66f85baa79cf1e0ba3fecefe3800827787d45`, matching prior evidence. Computed decimal precision is for auditing; it does not imply corresponding measurement precision.
