# Hyperiid and salmon primary-source feeding recovery

The salmon recovery removes the nominal carbon energy contradiction for an admissible GS near 0.10, using the documented Amphipoda-to-hyperiid aggregate and independently sourced conversion factors. It does **not** identify a complete carbon Q, a complete 22-group DC column, or a balanced native model. The hyperiid recovery remains blocked by an unquantified “Other food” split and its carbon content. No model repair or normalization was performed.

Original sources: Gorbatenko (2018), dissertation, printed pages equal one-based PDF pages; Gorbatenko & Melnikov (2019), printed page = one-based PDF page + 142. Raw original page text, source hashes, transcription tables and rendered original pages are retained in this directory. The English translations below are audit translations.

## Hyperiids: complete two-category source total, incomplete model diet

Dissertation Table 4.11, printed/PDF p.117, explicitly covers mean 2000–2014 consumption in the whole-Sea Okhotsk epipelagic, in million wet tonnes/year. Its entire annual breakdown is:

| Source food | Annual consumption | Printed mass share | Model crosswalk |
|---|---:|---:|---|
| Копеподы / Copepods | 56.7 | 37.2% | Group 4 |
| Прочие / Other food | 95.8 | 62.8% | Unresolved |
| Total | 152.5 | 100% | — |

The 2019 article, printed p.153/PDF p.11, independently repeats annual Q = 152.5 and copepod Q = 56.7. These are not consumer-carbon conversions; copepod intake alone becomes 56.7/14 = **4.05 million tC/year** using the 2019 copepod factor.

The source describes the total as an expert estimate. Dissertation p.117: “Можно лишь дать экспертную оценку величины рациона”; the table footnote says “* Экспертная оценка рационов.” Translation: “Only an expert estimate of ration size can be given”; “Expert estimate of rations.” The authors explicitly report no dedicated hyperiid ration studies in the Okhotsk Sea and no available subarctic ration data, then assume seasonal ration of 6–8% body mass, similar to euphausiids. Quarterly values round inconsistently with annual prey totals (copepods sum 56.6 versus 56.7; Other sums 95.9 versus 95.8); annual totals were retained as printed.

Nearby original prose, pp.116–118, provides qualitative possibilities but no numerical decomposition of Other. It names euphausiids, chaetognaths, jellyfish, decapod larvae, fish larvae, other amphipods and cannibalism. Some statements refer to cited species-specific Themisto observations; other hyperiid species consume ctenophores and marine tunicates. Phytoplankton occurs in cited T. libellula fatty-acid evidence. Dead or weakened organisms are explicitly eaten, but this does not supply an Ecopath detritus-pool allocation. No quantified microheterotroph fraction was found. Exact passages and scope qualifiers are in `hyperiid_other_food_evidence.json`.

The Table 7.1 “Other zooplankton” factors **20.14 winter/spring and 15.66 summer/autumn** (p.298) do **not** establish the carbon content of Table 4.11 Other food. Table 4.11 Other includes all prey except copepods, including taxa that Table 7.1 enumerates separately. The same Russian word “Прочие” does not establish identical taxonomic composition. Assigning 62.8% to the existing Other-zooplankton model group, or using its carbon factor, would introduce an additional assumption and additional predation on that group.

With source carbon P = 4.752 million tC/year, R = Q(1−GS)−P. Let C_other be the unknown carbon intake represented by 95.8 million wet tonnes:

| GS | Required C_other for R ≥ 0 | Maximum effective Other wet/C factor |
|---:|---:|---:|
| 0.10 | 1.230000 million tC/year | 77.88617886 |
| 0.35 | 3.26076923 million tC/year | 29.37957065 |

Positive respiration requires a strict inequality. This establishes a quantitative feasibility threshold; it does not prove the source food mixture meets it or allocate a diet.

The mandatory **text + Figure** constraint case is recorded separately in `hyperiid_text_plus_figure_constraints.json`. It retains the clear Figure euphausiid arrow F13 = 0.283 million tC/year, which converts using the euphausiid factor 10.6 to 2.9998 million wet tonnes. The documented consistency assumption is that these euphausiids are included within Table 4.11 Other = 95.8; they are not extra food added beyond Q = 152.5. Remaining Other is therefore **92.8002 million wet tonnes**, and known carbon Q is **4.333**.

| Hybrid GS | Required residual Other carbon for R ≥ 0 | Maximum effective residual Other wet/C |
|---:|---:|---:|
| 0.10 | 0.947000 million tC/year | 97.99387540 |
| 0.35 | 2.97776923 million tC/year | 31.16433572 |

This combined constraint case also remains incomplete; no residual Other allocation or full carbon Q was inferred. It preserves Figure values without silently normalizing the text categories.

## Salmon: source total and all feeding rows recovered

The 2019 article, printed p.155/PDF p.13, explicitly calculates trophic-level-III salmon production for **pink, chum and sockeye**. Dissertation p.162 identifies predatory salmon as Chinook, coho and masu. Table 4.52, printed/PDF p.169, covers 2000–2014 and supplies the following exact wet feeding rows. All quantities are **thousand wet tonnes/year**. Group-8 totals are sums of the first three source columns, not source-printed aggregated observations.

| Source prey | Pink | Chum | Sockeye | Derived group-8 total |
|---|---:|---:|---:|---:|
| Euphausiids | 357.0 | 109.5 | 5.4 | 471.9 |
| Amphipods | 675.3 | 157.2 | 35.3 | 867.8 |
| Copepods | 23.2 | 12.8 | 15.3 | 51.3 |
| Chaetognaths | 34.9 | 25.4 | 0.2 | 60.5 |
| Pteropods | 48.9 | 21.8 | 6.1 | 76.8 |
| Decapods | 13.7 | 3.8 | 1.6 | 19.1 |
| Oikopleura | 21.2 | 40.0 | 0.0 | 61.2 |
| Gelatinous organisms | 0.7 | 44.0 | 0.1 | 44.8 |
| **Plankton subtotal** | **1174.9** | **414.5** | **64.2** | **1653.6** |
| **Nekton subtotal** | **98.1** | **38.9** | **6.2** | **143.2** |
| Squid | 29.6 | 12.8 | 4.5 | 46.9 |
| Fish | 68.8 | 26.0 | 1.7 | 96.5 |

The independent printed species totals are 1273.2, 453.34 and 70.4, giving **1796.94 thousand wet tonnes/year = 1.79694 million wet tonnes/year**. The ten leaf food rows sum to 1796.8 thousand tonnes, leaving a **0.14 thousand tonne rounding/unreconciled difference**. The two subtotals must not be counted again. Fractions in the ledger are divided by the independent Q and have not been normalized.

The consumption calculation already integrates presence in the Sea: species Tables 4.43/4.45/4.47 use **two summer months and three autumn months**, including adult and young cohorts as specified. Do not extrapolate these annual totals to 365 feeding days. Their summed salmon biomass is 740.2 thousand tonnes, whereas 2019 Table 3 rounds group-8 biomass to 800 thousand tonnes. This stock discrepancy remains explicit.

Copepods, euphausiids and chaetognaths match groups 4, 5 and 7. The Amphipoda row can be represented by group 6 only as a documented taxonomy aggregate: nearby original prose calls the main foods of pink (p.163), chum (pp.163–164) and sockeye (p.165) **гиперииды / hyperiids**. Amphipoda is broader than Hyperiidea; the full row does not independently quantify a subtype split. This aggregate caveat applies to every carbon bound below.

Pteropods and Oikopleura have independent source carbon factors but are absent from the 22-group network. Decapods also lack a matched group and a recovered applicable conversion factor. “Gelatinous” is not exactly jellyfish group 14: source p.162 identifies cnidarians, ctenophores, doliolids and salps as low-calorie chum prey. The pooled squid row lacks a quantified split between groups 9/16. The pooled fish row lacks a whole-year species/size allocation. These categories are retained independently.

## Seasonal factors and carbon energy bounds

Dissertation Table 7.1, printed/PDF p.298, gives explicit wet/C factors. Extra categories needed here are:

| Category | Winter/spring | Summer/autumn |
|---|---:|---:|
| Mysids | 17.27 | 12.53 |
| Pteropods | 22.27 | 17.79 |
| Oikopleura | 21.72 | 20.97 |

All nine Table 7.1 group factors are recorded in `seasonal_prey_conversion_factors.json`. The table note gives ±SE no greater than 10%. Original p.297 states the coefficients depend directly on the dominant group/species and season, and rejects a single coefficient for all zooplankton. A summer/autumn conversion case is appropriate to the source residence window, but remains a separately labelled conversion choice rather than a replacement of 2019 coefficients.

Using only six carbon-convertible categories (euphausiids, amphipods, copepods, chaetognaths, pteropods and Oikopleura), the following are **nominal lower bounds** on total salmon carbon intake. Unconverted prey can only add nonnegative intake. Source P remains 0.105 million tC/year.

| Conversion case | Known Q, million tC/year | R at GS = 0.10 | GS ceiling from known prey alone |
|---|---:|---:|---:|
| 2019 main factors; largest seasonal extra-prey factors | 0.1173226946 | +0.0005904251 | 0.1050324887 |
| 2019 main factors; summer/autumn extra-prey factors | 0.1182919165 | +0.0014627248 | 0.1123653828 |
| All six summer/autumn Table 7.1 factors | 0.1339149020 | +0.0155234118 | 0.2159199728 |

These cases demonstrate an admissible GS within [0.10, 0.35] with nominal positive R; they do not prove compatibility at every GS in that interval. At the listed ceiling the known-prey calculation has R = 0. Precision reflects arithmetic on rounded inputs, and factor SE prevents calling the small positive margins strict probabilistic guarantees. None of these cases is a complete carbon Q or a complete native model.

## Source discrepancies and remaining blockers

Individual supporting tables differ slightly from Table 4.52. Table 4.47 p.166 additionally names **0.1 thousand tonnes of sockeye mysid food**; this is retained separately rather than added silently to the aggregate table. Chum Table 4.45 differs by 0.1 thousand tonnes in several prey rows. Sockeye Table 4.47 total is 70.3 versus Table 4.52 70.4. Table 4.54 p.171 appears to swap salmon copepod/amphipod consumption (0.87/0.05 million tonnes), contradicting the direct species table (~0.0517/~0.8699). Appendix 46 p.456 gives Oikopleura summer dry-carbon percentage 40.80 versus Table 7.1 42.20; the printed Table 7.1 factors are retained as separate source observations. The structured discrepancy record preserves these differences.

Required before a complete source-supported model repair:

- Hyperiids: quantitative Other-prey breakdown or an explicitly accepted composition/conversion assumption, with consequent group-specific predation accounted for.
- Salmon: representation of prey categories absent from the 22 groups; applicable decapod and gelatinous factors; squid/fish group allocations; explicit handling of the Amphipoda aggregate and rounded closure difference.
- Both: rebuild complete carbon consumption and carbon diet together from prey-specific flows; preserve source independent Q rather than converting total Q with the consumer factor; then test the full native model. The nominal energy result alone does not establish all Ecopath balances.

`recover_source_feeding.py` recreates the structured outputs and verifies SHA-256 preservation of both originals, the canonical model, the accepted Figure model and its carbon reconstruction. Original pp.117, 169 and 298 were rendered and visually inspected for the tables. No canonical or selected-model file was changed.
