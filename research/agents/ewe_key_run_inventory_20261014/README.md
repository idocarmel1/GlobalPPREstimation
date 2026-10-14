# Accepted Ecopath with Ecosim key runs and model sources

Research date: 14 October 2026. This study identifies regions with documented ICES WGSAM acceptance of an Ecopath with Ecosim (EwE) key run and locates the corresponding model sources.

Regional source packages and canonical `model.json` snapshots are now prepared under LME_022, LME_023 and LME_024. The user subsequently authorized selecting the two balanced snapshots: North Sea and Baltic Proper are registered, selected and published; Irish Sea remains unselected. See the [selection report](SELECTION_PUBLICATION_REPORT.md). The [JSON creation report](JSON_CREATION_REPORT.md) describes the three snapshots, imports, verification and source limitations. The [regional preparation report](REGIONAL_PREPARATION_REPORT.md) records the earlier source-only stage.

**Three regions have documented EwE key runs: the North Sea, Baltic Proper and Irish Sea.** The regional names identify particular model footprints, rather than acceptance of every model for those seas. The review reports establish historical acceptance; they do not establish that every subsequent update has been reviewed.

## Meaning of acceptance

A key run is a specific model run reviewed for a specific advice product. The latest WGSAM definition explicitly limits the status to the reviewed configuration, input data, software and problem. Changing these requires another review. It is therefore more precise to call these ICES WGSAM reviewed and accepted configurations than globally accepted models. Journal peer review alone does not confer this status.

Source: [WGSAM 2025 meeting report, published in 2026](https://doi.org/10.17895/ices.pub.31224250), section 1, printed p. 4 / PDF p. 8; local [report](inputs/ICES_WGSAM_2025_meeting_published_2026.pdf).

## Verified regional list

| Region and actual footprint | Documented EwE key run | Baseline and calibration period | Groups | Acceptance evidence |
|---|---|---|---|---|
| North Sea, ICES divisions IVa, IVb and IVc | First key run in 2011; second key run in 2015, finalized in January 2016 | Ecopath baseline 1991; Ecosim 1991–2013 for the second run | 69 | WGSAM 2015 report, printed p. 28 describes approval following agreed corrections; Annex 6, printed pp. 102–206 describes the model. |
| Baltic Proper, approximately ICES subdivisions 25–29 excluding 28-1, the Gulf of Riga | First key run in 2016 | Ecopath baseline 2004; Ecosim 2004–2013 | 22 | WGSAM 2016 report, printed pp. 22–23 and Annex 3, pp. 46–94; ICES still distributes the official 2016 output archive. |
| Irish Sea, ICES division VIIa / 7.a | Accepted in October 2019 | Ecopath baseline 1973; Ecosim 1973–2016 | 41 | WGSAM 2019, section 2.2, printed p. 13 / PDF p. 20 explicitly approves the model as a key run. Annex 3, printed pp. 37–109 documents it. |

Original reports: [North Sea 2015](inputs/ICES_WGSAM_2015.pdf), [Baltic 2016](inputs/ICES_WGSAM_2016.pdf), [Irish Sea 2019](inputs/ICES_WGSAM_2019.pdf). Online references: [2015 report](https://www.diva-portal.org/smash/get/diva2%3A929847/FULLTEXT01.pdf), [2016 ICES record](https://ices-library.figshare.com/articles/report/Report_of_the_Working_Group_on_Multispecies_Assessment_Methods_WGSAM_/18615806), [2019 ICES record](https://ices-library.figshare.com/articles/report/Working_Group_on_Multispecies_Assessment_Methods_WGSAM_/18621824), and [ICES review criteria](https://ices-eg.github.io/wg_WGSAM/ReviewCriteria.html).

The 2024 WGSAM report and the 2025 meeting report published in February 2026 were also checked. No additional accepted EwE region was identified. This is the complete verified list from the reviewed ICES material, rather than a claim that a worldwide certification registry exists.

## Model files obtained

| Region | Material saved in this folder | What it contains |
|---|---|---|
| North Sea | [Official 2015 outputs](inputs/EwE-NS_KeyRun%202015%20Outputs.zip) | 63 archive entries: annual yield, predation tables, biomass and mortality workbooks. There is no native EwE database in the archive. |
| Baltic Proper | [Official 2016 outputs](inputs/EwE_BS_KeyRun%202016%20Outputs.zip) | 23 archive entries: annual biomass, catch, mortality and predation outputs. There is no native EwE database in the archive. |
| North Sea | [Published Rpath model object](inputs/NorthSeaModel.RData) and [parameter configuration](inputs/NorthSeaModel_config.R) | An R implementation derived from the EwE key-run model, distributed with the authors' multispecies MSY study. |
| Baltic Proper | [Published Rpath model object](inputs/BalticSeaModel.RData) and [parameter configuration](inputs/BalticSeaModel_config.R) | An R implementation derived from the EwE key-run model, distributed with the same study. |
| Irish Sea | [ICES acceptance and model documentation](inputs/ICES_WGSAM_2019.pdf) and [SAMS technical report](inputs/IrishSea_key_run_technical_report_2019.pdf) | Model structure, parameter tables, diet, fitting and review information. The SAMS report was published before the October review; the final ICES documentation and review corrections take precedence when establishing the accepted configuration. |

The two RData files are complete gzip-compressed R workspaces with an RDX3 serialization header, rather than Git LFS pointers. Their configuration scripts contain model parameters, diet, fisheries, stanza and simulation settings. They were downloaded and inspected without executing the model scripts or testing the simulations.

The Rpath sources are available in [the authors' repository](https://github.com/ThomasDelSantoONeill/nash/tree/main/FnFData). The [study's reproducibility guide](https://thomasdelsantooneill.github.io/nash/articles/FnFpaper.html) identifies them as ports of the North Sea and Baltic EwE key-run parameterizations; the associated paper is [Del Santo O'Neill et al., An efficient tool to find multispecies MSY for interacting fish stocks](https://doi.org/10.1111/faf.12817). **A port to Rpath does not inherit the original EwE acceptance**, under the current WGSAM definition. Subsequent source comparison during JSON extraction established material parameter differences from the ICES accepted configurations; see the [JSON creation report](JSON_CREATION_REPORT.md) and model-local evidence. Full native equivalence remains unestablished.

## Exact native models still to obtain

| Region | Native identity or supporting files named by the reviewed report | Acquisition route |
|---|---|---|
| North Sea | `Keyrun 2015_NorthSea1991_12Jan16.eweaccdb`; model name `NorthSea1991–2013 Key Run`; scenario `Basic setup`; time series `North Sea Time Serie 1991_2013_12Jan2016.csv`; EwE 6.4.11414 | WGSAM 2015, printed pp. 172 and 196 lists the database. Annex 6 names Steven Mackinson, Clement Garcia and Christopher Lynam at Cefas as contacts. The database was not in the official output ZIP. |
| Baltic Proper | `Baltic2004_keyrun65.eweaccdb`; model name `2000sFishModel`; EwE 6.5.14040.0. Supporting workbooks include `Baltic 2004_Key Run_Ecopath.xlsx` and `Baltic 2004_Key Run_Ecosim.xlsx`. | WGSAM 2016, printed pp. 47 and 83 names these files. Authors are Barbara Bauer and Maciej T. Tomczak, Baltic Sea Centre, Stockholm University. Some original plankton time series are explicitly described as non-public on printed p. 67. |
| Irish Sea | Exact database filename was not located in the reviewed documentation. Request the configuration accepted at WGSAM 2019, including final review changes, its forcing/fitting series and Ecosim scenario. | Jacob Bentley and coauthors; the final ICES WGSAM 2019 documentation is the reference for identifying the correct version. A public native model download was not located. |

No native `.eweaccdb`, `.ewedb` or `.ewemodel` file was retrieved. The source documentation and Rpath sources provide useful access to model information, but are distinct deliverables from an accepted native EwE database.

## Related regions and models outside the EwE list

Georges Bank appears in recent WGSAM reviews, but its food-web implementation is **Rpath**, alongside Hydra and multispecies production models. It is not an additional EwE entry. The [2022 review report](https://literatur.thuenen.de/digbib_extern/dn066046.pdf), section 2, identifies those frameworks. The [2024 WGSAM report](https://doi.org/10.17895/ices.pub.27919473) discusses the Georges Bank review and subsequent work.

The Baltic and North Sea also have SMS key runs. The latest 2025 Baltic review is an SMS review and does not update the 2016 EwE model's acceptance. Wider inventories of all multispecies key runs must therefore be kept separate from this EwE list.

## Existing repository candidates

The local search found existing North Sea, central Baltic and Irish Sea EcoBase JSONs. Their titles and baseline years alone do not prove identity with the accepted configurations. In particular, the existing North Sea source record 628 describes a 1973 model, and the project's Mackinson 2007 sources predate the 2015 key run. These existing models were not relabeled as accepted key runs, copied into this study as newly obtained models, selected or modified.

## Evidence and files

- [Source manifest](evidence/source_manifest.json) records download URLs, file roles, byte lengths and SHA-256 hashes.
- [Archive inventory](evidence/archive_inventory.json) records every entry in the two official output archives.
- [Regional inventory](evidence/regional_inventory.json) records the accepted footprints and outstanding native-model gaps.
- Relevant report pages are retained as text with one-based PDF page numbers under `evidence/`; the original PDFs remain the primary sources.

This supporting research does not register models, change Project.xlsx, assess PPR readiness or confer researcher approval.
