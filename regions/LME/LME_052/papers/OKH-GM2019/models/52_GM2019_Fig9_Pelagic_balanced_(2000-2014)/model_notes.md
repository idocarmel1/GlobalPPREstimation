# 52_GM2019_Fig9_Pelagic_balanced_(2000-2014)

## Source identity

OKH-GM2019__LME_052

Regional application: `LME_052`. Canonical JSON SHA-256: `9beff5a4e525dcf4253bf83472253c7a4a9f7e7db10379ecef64eb33cd32a656`. The byte-preservation check compares this retained representation with the pre-relocation working state; it is not a fresh extraction or a new approval.

## Modeled period and area

Period: 2000–2014

Whole Okhotsk Sea 0–200 m epipelagic community; excludes benthic guilds. LME polygon is an intended-domain approximation; exact author-polygon overlap unmeasured. Implied source reporting denominator 1,544,000 km² is separate from target polygon area.

## Departures from the publication

This is the explicitly authorized scientific assumption model, not an author-confirmed Ecopath export. Native stocks/flows use tC/km² and annual rates. Table 3 implies area 1,544,000 km²; this is not a measured regional-overlap fraction. The retained production totals and source wet stocks/carbon factors determine B/PB. Microbial stock splitting gives 6.81 million tC and 65.067 million wet tonnes versus rounded source 6.8 million tC/64 million wet tonnes; protozoa's carbon factor 10 is an explicit estimate.

Twelve Figure 9 arrows use low-confidence 10×/100× decimal hypotheses. These have not been established as publication errors. Accepted F62=0.023, F67=0.05 and F77's medium-pollock origin remain unchanged. The food ledger retains 74 components, including hyperiid residual assumptions 40% chaetognaths/50% absent larvae and tunicates/10% gelatinous, squid unresolved food splitting, imported prey, jellyfish 2006–2014 versus overall 2000–2014 periods, and salmon's 0.14 kt rounded-total discrepancy.

Living BA is zero by assumption. GS is unknown for 20 consumers and solved by the standard LIM, not supplied as 0.2. Detritus import/export are zero, all living mortality/egestion routes to the sole pool, and its assumed inventory 15.5 million tC represents 18.25 days turnover. The retained diagnostic detritus BA=242.50886238380988 tC/km²/year is an imposed nonsteady residual, not measured burial or a stock trend. A native import helperB=1 is nonbiological. All direct methods remain WARN. Runtime settings and source-to-final ledger record the accepted decisions; reorganization introduces none.
The sibling source reconstruction uses wet-weight stock density, while this computational variant uses carbon stock density with group-specific conversions. Consequently the B comparison records a unit/representation change as well as the documented stock-splitting choices; it is not a new biological correction.

The following exact input differences compare this JSON with [retained source variant](../52_GM2019_Fig9_Pelagic_(2000-2014)/model.json). The source representation is an evidence locator; it is not proof that every source field is a published measurement. `-9999` remains an unknown sentinel, and absent fields are shown as `None`. No difference was introduced by this reorganization.

| Group IDs | Field | Source representation | Retained representation |
|---|---|---|---|
| 1 | `biomass` | `40.93264248704663212435233160621761658031` | `2.0466321243523318` |
| 1 | `pb` | `220.0` | `219.87341772151896` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 | `biomass_accum` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 | `biomass_accum_rate` | `-9999` | `0` |
| 1, 22 | `gs` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 | `detritus_import` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 | `immigration` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 | `emigration` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 | `emigration_rate` | `-9999` | `0` |
| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22 | `export` | `-9999` | `0` |
| 2 | `biomass` | `-9999` | `3.2739637305699483` |
| 2, 3, 22 | `b_hab_area_input` | `false` | `true` |
| 2, 3 | `pb` | `-9999` | `20` |
| 2, 3 | `pb_input` | `false` | `true` |
| 2 | `qb` | `-9999` | `61.325420375865484` |
| 2, 3, 4, 5, 18 | `qb_input` | `false` | `true` |
| 3 | `biomass` | `-9999` | `1.1366580310880829` |
| 3 | `qb` | `-9999` | `61.538461538461533` |
| 4 | `biomass` | `70.14248704663212435233160621761658031088` | `5.0101776461880085` |
| 4 | `pb` | `15.2` | `15.150507848568791` |
| 4 | `qb` | `-9999` | `23.638947957800436` |
| 4 | `diet_imp` | `0` | `0.020585148961506268` |
| 5 | `biomass` | `38.01813471502590673575129533678756476684` | `3.5866164825496143` |
| 5 | `pb` | `10.10` | `10.130494037478705` |
| 5 | `qb` | `-9999` | `15.885306198010733` |
| 5 | `diet_imp` | `0` | `0.021004753703369506` |
| 6 | `biomass` | `3.821243523316062176165803108808290155440` | `0.26353403609076292` |
| 6 | `pb` | `11.70` | `11.678644067796609` |
| 6 | `qb` | `10.23725423728813559322033898305084745763` | `23.864227705332574` |
| 6 | `diet_imp` | `0` | `0.35928234931546821` |
| 7 | `biomass` | `27.65544041450777202072538860103626943005` | `1.3827720207253886` |
| 7 | `pb` | `6.0` | `5.9859484777517551` |
| 7 | `qb` | `6.730669789227166276346604215456674473068` | `10.827708615801798` |
| 7 | `diet_imp` | `0` | `0.10603197442774341` |
| 8 | `biomass` | `0.5181347150259067357512953367875647668394` | `0.063187160369013035` |
| 8 | `pb` | `1.14` | `1.0762499999999997` |
| 8 | `qb` | `1.247425` | `1.3829519824085723` |
| 8 | `diet_imp` | `0` | `0.06434898838559204` |
| 9 | `biomass` | `0.3238341968911917098445595854922279792746` | `0.027212957721948879` |
| 9 | `pb` | `2.50` | `2.4990000000000001` |
| 9 | `qb` | `38.184904` | `45.971434197163568` |
| 9 | `diet_imp` | `0` | `0.12309287921917203` |
| 10 | `biomass` | `1.619170984455958549222797927461139896373` | `0.22488485895221644` |
| 10 | `pb` | `0.34` | `0.34271999999999997` |
| 10 | `qb` | `13.4248` | `8.7307165638647533` |
| 10 | `diet_imp` | `0` | `0.090878744953040672` |
| 11 | `biomass` | `1.165803108808290155440414507772020725389` | `0.13400035733428622` |
| 11 | `pb` | `0.29` | `0.28999999999999998` |
| 11 | `qb` | `2.76225` | `4.0866003758216287` |
| 11 | `diet_imp` | `0` | `0.1009346488526924` |
| 12 | `biomass` | `0.5181347150259067357512953367875647668394` | `0.050797521080971256` |
| 12 | `pb` | `2.50` | `2.5117499999999997` |
| 12 | `qb` | `20.62475` | `16.648068654068556` |
| 12 | `diet_imp` | `0` | `0.0025910649722343921` |
| 13 | `biomass` | `0.5181347150259067357512953367875647668394` | `0.058878944889307588` |
| 13 | `pb` | `0.35` | `0.32999999999999996` |
| 13 | `qb` | `14.246875` | `14.453277529152222` |
| 13 | `diet_imp` | `0` | `0.19706793309733761` |
| 14 | `biomass` | `2.655440414507772020725388601036269430052` | `0.0093108008923834928` |
| 14 | `pb` | `10.0` | `10.016780487804878` |
| 14 | `qb` | `0.1763658536585365853658536585365853658537` | `16.305341377731384` |
| 14 | `diet_imp` | `0` | `0.094592887712810422` |
| 15 | `biomass` | `5.518134715025906735751295336787564766839` | `0.49668179253158479` |
| 15 | `pb` | `0.70` | `0.76935446009389663` |
| 15 | `qb` | `7.149988262910798122065727699530516431925` | `5.9336136737089209` |
| 16 | `biomass` | `0.3238341968911917098445595854922279792746` | `0.027121792034438166` |
| 16 | `pb` | `2.50` | `2.3879999999999999` |
| 16 | `qb` | `19.3068` | `24.7140627582225` |
| 16 | `diet_imp` | `0` | `0.88306424450433618` |
| 17 | `biomass` | `0.01295336787564766839378238341968911917098` | `0.0015796790092253256` |
| 17 | `pb` | `0.84` | `0.81999999999999984` |
| 17 | `qb` | `54.3655` | `13.119999999999997` |
| 18 | `biomass` | `0.4669689119170984455958549222797927461140` | `0.085997957995782401` |
| 18 | `pb` | `0.01` | `0.0075312066574202505` |
| 18 | `qb` | `-9999` | `1.6128079056865465` |
| 19 | `biomass` | `0.3238341968911917098445595854922279792746` | `0.029147992519459199` |
| 19 | `pb` | `0.20` | `0.19997999999999999` |
| 19 | `qb` | `1.520896` | `1.5518448` |
| 20 | `biomass` | `0.07772020725388601036269430051813471502591` | `0.014313113674748804` |
| 20 | `pb` | `0.20` | `0.18100000000000002` |
| 20 | `qb` | `39.92983333333333333333333333333333333333` | `5.3983250000000007` |
| 21 | `biomass` | `0.1580310880829015544041450777202072538860` | `0.029103331138655906` |
| 21 | `pb` | `0.03` | `0.022254098360655738` |
| 21 | `qb` | `4.741885245901639344262295081967213114754` | `2.3188770491803279` |
| 22 | `biomass` | `-9999` | `10.038860103626943` |


## Evidence links

- [Canonical Ecopath representation](model.json)
- [provenance.json](inputs/provenance.json)
- [validation.docx](model_validation/validation.docx)
- [REPORT.md](extracted_tables/evidence/REPORT.md)
- [source_to_final_ledger.json](extracted_tables/evidence/source_to_final_ledger.json)
- [runtime_provenance.json](extracted_tables/evidence/runtime_provenance.json)
- [result_manifest.json](results/result_manifest.json)
- [Portable source dispositions](../../../../../../../common_reference_data/provenance/source_paths.csv)

## Removed extraction evidence

Superseded extraction packages and their unique old evidence are removed under the agreed latest-only policy; they are not merged into this package. Original paths, hashes and reasons are metadata in the linked disposition ledger. A link to this paragraph records an unavailable former payload, not replacement evidence or completed scientific verification.
