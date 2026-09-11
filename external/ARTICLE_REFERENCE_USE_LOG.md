# Article reference and use log

Audit date: 11 September 2026.

This log covers every row in the project’s article inventory: **192 regional records grouped under 155 source IDs**, plus **27 documented method, input, diagnostic and supporting references**. Source IDs are catalog identities, not a claim that all are unique or bibliographically verified publications.

Simple trophic-chain PPR uses catch and reference trophic levels independently of this article inventory. Model-based estimates use separately verified model/mapping evidence. Satellite NPP uses the documented raster products. An archived or selected paper alone does not establish computational coverage.

The inventory records what the project used: model inputs and mapping evidence, algorithm lineage, interpretation, or candidate discovery. It does not recursively list every reference printed inside every archived paper. Inaccessible, rejected and inherited records remain visible. The separate unfinished expanded discard study is outside this audit.

## Calculation methods, inputs and supporting references

### Pauly-Christensen-1995

Pauly, D. and Christensen, V. (1995). Primary production required to sustain global fisheries. Nature 374:255–257.

**Role:** calculation_method. Trophic-chain PPR framework and inclusion of discarded bycatch. The project retains TE=0.1 and applies its wet-equivalent-to-carbon divisor 9 once in display calculations.

**Evidence:** Original article on author institution site inspected 2026-09-11.

**Limit:** The expanded conversion-factor literature review remains deferred; this entry does not validate a universal region-specific conversion.

[Reference / source](https://www.seaaroundus.org/wp-content/uploads/2015/04/PrimaryProductionRequiredToSustainGlobalFisheries.pdf)

Local use: [README.md](../PPREstimation/README.md); [README.md](../docs/discard-audit-2026-09-10/README.md).

### Pauly-Christensen-1986-inherited

Pauly & Christensen (1986): inherited method attribution; complete reference unresolved.

**Role:** inherited_method_attribution. The calculator documentation attributes a catch-weighted trophic-level approximation to this label.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** The local label alone does not establish a publication identity, title, or DOI. It is retained as unresolved rather than invented.

Local use: [README.md](../PPREstimation/README.md).

### supplied-2020-MeanTL

User-supplied 2020 supplement (original filename: 2020 sup.xlsx); bibliographic identity unresolved in the inspected provenance.

**Role:** calculation_input. Supplies MeanTL reference values, frozen in SeaAroundUsExtraction/input/trophic_levels_2020.csv; its alternative SPPR regressions are not used for the simple chain.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** The original workbook hash is recorded in input/provenance.json. A year/filename is insufficient to equate it with Luong et al. (2020).

Local use: [README.md](../SeaAroundUsExtraction/README.md); [provenance.json](../SeaAroundUsExtraction/input/provenance.json); [trophic_levels_2020.csv](../SeaAroundUsExtraction/input/trophic_levels_2020.csv).

### Antoine-Morel-1996

Antoine, D. and Morel, A. (1996). Oceanic primary production 1. Adaptation of a spectral light-photosynthesis model in view of application to satellite chlorophyll observations.

**Role:** npp_algorithm. Algorithm lineage for the Copernicus Antoine–Morel NPP input.

**Evidence:** Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.

[Reference / source](https://orca.science.oregonstate.edu/references.php)

Local use: [METHODS.md](../NPPExtraction/METHODS.md).

### Behrenfeld-Falkowski-1997

Behrenfeld, M. J. and Falkowski, P. G. (1997). Photosynthetic rates derived from satellite-based chlorophyll concentration. Limnology and Oceanography 42:1–20.

**Role:** npp_algorithm. VGPM algorithm lineage.

**Evidence:** Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.

[Reference / source](https://orca.science.oregonstate.edu/references.php)

Local use: [METHODS.md](../NPPExtraction/METHODS.md).

### Eppley-1972

Eppley, R. W. (1972). Temperature and phytoplankton growth in the sea. Fishery Bulletin 70:1063–1085.

**Role:** npp_algorithm. Temperature-response lineage for Eppley-VGPM.

**Evidence:** Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.

[Reference / source](https://orca.science.oregonstate.edu/references.php)

Local use: [METHODS.md](../NPPExtraction/METHODS.md).

### Westberry-2008

Westberry, T., Behrenfeld, M. J., Siegel, D. A. and Boss, E. (2008). Carbon-based primary productivity modeling with vertically resolved photoacclimation.

**Role:** npp_algorithm. CbPM2 algorithm lineage.

**Evidence:** Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.

[Reference / source](https://orca.science.oregonstate.edu/references.php)

Local use: [METHODS.md](../NPPExtraction/METHODS.md).

### Silsbe-2016

Silsbe, G. M. et al. (2016). The CAFE model: A net production model for global ocean phytoplankton. Global Biogeochemical Cycles 30:1756–1777.

**Role:** npp_algorithm. CAFE algorithm lineage.

**Evidence:** Bibliographic identity checked on the OSU algorithm reference page, 2026-09-11.

[Reference / source](https://orca.science.oregonstate.edu/references.php)

Local use: [METHODS.md](../NPPExtraction/METHODS.md).

### Copernicus-GlobColour

E.U. Copernicus Marine Service. Global Ocean Colour (Copernicus-GlobColour), Bio-Geo-Chemical, L4. DOI:10.48670/moi-00281.

**Role:** npp_data_product. Monthly PP raster source, product OCEANCOLOUR_GLO_BGC_L4_MY_009_104, used for regional and fixed-atlas NPP.

**Evidence:** Primary product page checked in the parent task, 2026-09-10.

**Limit:** Data product citation, not an article. Annual coverage and pixel support come from the extraction provenance, not this citation.

[Reference / source](https://data.marine.copernicus.eu/product/OCEANCOLOUR_GLO_BGC_L4_MY_009_104/description)

Local use: [METHODS.md](../NPPExtraction/METHODS.md).

### Ryan-Keogh-2023

Ryan-Keogh, T. J., Thomalla, S. J., Chang, N. and Moalusi, T. (2023). A new global oceanic multi-model net primary productivity data product. Earth System Science Data 15:4829–4848. DOI:10.5194/essd-15-4829-2023.

**Role:** evaluated_alternative_not_used. Documents the OC-CCI multi-model alternative considered during NPP source selection.

**Evidence:** Publisher bibliography checked 2026-09-11.

**Limit:** The project did not ingest this alternative; the local methods document records download-size and resolution reasons.

[Reference / source](https://essd.copernicus.org/articles/15/4829/2023/)

Local use: [METHODS.md](../NPPExtraction/METHODS.md).

### Tam-2008

Tam et al. (2008). Trophic modeling of the Northern Humboldt Current Ecosystem, Part I: Comparing trophic linkages under La Niña and El Niño conditions. Progress in Oceanography 79:352–365.

**Role:** model_mapping_lineage. Explicitly adopted predecessor of Chiaverano et al.; supports species examples, hake size groups and model membership.

**Evidence:** Institutional repository identity checked 2026-09-11; prior mapping notes record original-page inspection.

[Reference / source](https://epic.awi.de/id/eprint/22464/)

Local use: [13_2_Northern_Humboldt_Current_(1995-1998).notes.md](../data/LME_013/mapping/13_2_Northern_Humboldt_Current_(1995-1998).notes.md).

### Christensen-1998

Christensen, V. (1998). Fishery-induced changes in a marine ecosystem: insight from models of the Gulf of Thailand. Journal of Fish Biology 53(Suppl. A):128–142. DOI:10.1111/j.1095-8649.1998.tb01023.x.

**Role:** model_identity_and_mapping. Table II identifies the imported Gulf model as 1980 despite its inherited 1963 filename; grouping prose supports catch mapping and the 10–50 m shelf domain.

**Evidence:** Prior source audit inspected author-linked full HTML and checked 11 biomasses.

**Limit:** Publisher PDF was inaccessible; no original-PDF retrieval or complete numerical re-extraction is claimed.

[Reference / source](https://doi.org/10.1111/j.1095-8649.1998.tb01023.x)

Local use: [35_412_Gulf_of_Thailande_(1963).notes.md](../data/LME_035/mapping/35_412_Gulf_of_Thailande_(1963).notes.md).

### Pauly-Chuenpagdee-2003

Pauly, D. and Chuenpagdee, R. (2003). Development of fisheries in the Gulf of Thailand Large Marine Ecosystem.

**Role:** model_lineage_context. Figure 14-3 supports Gulf model lineage; it does not replace the source model parameters.

**Evidence:** Local documented use; bibliography not freshly reverified online.

[Reference / source](https://www.seaaroundus.org/doc/Researcher%2BPublications/dpauly/PDF/2003/Books%26Chapters/DevelopmentFisheriesGulfThailandLargeMarineEcosystem.pdf)

Local use: [35_412_Gulf_of_Thailande_(1963).notes.md](../data/LME_035/mapping/35_412_Gulf_of_Thailande_(1963).notes.md).

### Vibunpant-2003-excluded

Vibunpant (2003), Gulf of Thailand model; full bibliographic identity not recovered in the inspected mapping note.

**Role:** inspected_alternative_not_used. Documents why a 40-group, 1973 model was excluded as direct evidence for the imported Gulf model.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** No title or DOI is inferred from the abbreviated source note.

Local use: [35_412_Gulf_of_Thailande_(1963).notes.md](../data/LME_035/mapping/35_412_Gulf_of_Thailande_(1963).notes.md).

### CMFRI-black-pomfret

CMFRI black-pomfret account, repository item 7854, B139.pdf; complete citation not recovered here.

**Role:** taxonomy_mapping_support. Reconciles Formio niger with Parastromateus niger in the Karnataka mapping.

**Evidence:** Prior use documented locally; repository recheck failed 2026-09-11 (robots endpoint unreachable).

[Reference / source](https://eprints.cmfri.org.in/7854/1/B139.pdf)

Local use: [32_1_Arabian_Sea_off_Karnataka_(2000).notes.md](../data/LME_032/mapping/32_1_Arabian_Sea_off_Karnataka_(2000).notes.md).

### Baumann-1995

Baumann (1995). A comment on transfer efficiencies. DOI:10.1111/j.1365-2419.1995.tb00150.x.

**Role:** diagnostic_context. Supports sensitivity of a trophic-chain PPR assessment to transfer-efficiency assumptions.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** Does not establish the true transfer efficiency of any current atlas region.

[Reference / source](https://onlinelibrary.wiley.com/doi/pdf/10.1111/j.1365-2419.1995.tb00150.x)

Local use: [LME034_PPR_NPP_diagnostic_2026-09-10.md](../docs/LME034_PPR_NPP_diagnostic_2026-09-10.md).

### TWAP-Bay-assessment

TWAP Bay of Bengal Large Marine Ecosystem assessment, LME 34; complete publication metadata not recovered in the diagnostic.

**Role:** diagnostic_comparison. Provides a historical reported-landings PPR comparison used to explain why catch definitions change the percentage.

**Evidence:** Prior diagnostic used indexed assessment text under Primary Production Required.

**Limit:** The project comparison was not an exact replication of the assessment’s NPP baseline, catch coverage or trophic assignments.

[Reference / source](https://iwlearn.net/documents/download/4348c7eb-92aa-45ac-aa62-891c35e53268)

Local use: [LME034_PPR_NPP_diagnostic_2026-09-10.md](../docs/LME034_PPR_NPP_diagnostic_2026-09-10.md).

### Kalita-Lotliker-2023

Kalita and Lotliker (2023). Assessment of satellite-based Net Primary Productivity models in different biogeochemical provinces over the northern Indian Ocean. DOI:10.1080/01431161.2023.2247533.

**Role:** diagnostic_reference_identity_only. Identifies a relevant regional satellite-NPP validation study.

**Evidence:** Prior diagnostic verified bibliography via INCOIS/MoES records.

**Limit:** Publisher full text was unavailable; no model-ranking conclusion was taken from it.

[Reference / source](https://doi.org/10.1080/01431161.2023.2247533)

Local use: [LME034_PPR_NPP_diagnostic_2026-09-10.md](../docs/LME034_PPR_NPP_diagnostic_2026-09-10.md).

### Prasanna-Kumar-2002

Prasanna Kumar et al. (2002). Why is the Bay of Bengal less productive during summer monsoon compared to the Arabian Sea? DOI:10.1029/2002GL016013.

**Role:** diagnostic_context. Supports freshwater-stratification and nutrient-supply mechanisms discussed for the Bay.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** Contextual mechanism, not a measured correction to the exported NPP denominator.

[Reference / source](https://doi.org/10.1029/2002GL016013)

Local use: [LME034_PPR_NPP_diagnostic_2026-09-10.md](../docs/LME034_PPR_NPP_diagnostic_2026-09-10.md).

### Schlosser-2026

Schlosser, T. L., Lucas, A. J., Omand, M. and Farrar, J. T. (2026). Monsoons, plumes, and blooms: intraseasonal variability of subsurface primary productivity in the Bay of Bengal. Ocean Science 22:443–458. DOI:10.5194/os-22-443-2026.

**Role:** diagnostic_context. Autonomous observations support discussion of subsurface productivity and monsoon variability.

**Evidence:** Publisher bibliography and abstract checked 2026-09-11.

**Limit:** Does not establish a uniform satellite NPP bias or provide an atlas correction factor.

[Reference / source](https://os.copernicus.org/articles/22/443/2026/)

Local use: [LME034_PPR_NPP_diagnostic_2026-09-10.md](../docs/LME034_PPR_NPP_diagnostic_2026-09-10.md).

### Luong-2020

Luong, Dewulf and De Laender (2020). Quantifying the primary biotic resource use by fisheries: A global assessment. DOI:10.1016/j.scitotenv.2020.137352.

**Role:** diagnostic_context. Supports the point that a detailed food-web method need not yield lower PPR than a conventional trophic chain.

**Evidence:** Prior diagnostic used author-institution evidence; DOI endpoint not retrievable in this pass.

**Limit:** The rejected discovery-service attribution to Libralato (2008) is not adopted. Linkage to the supplied 2020 MeanTL workbook remains unverified.

[Reference / source](https://ilee.unamur.be/publications-1/natural-resources-characterization-and-management)

Local use: [LME034_PPR_NPP_diagnostic_2026-09-10.md](../docs/LME034_PPR_NPP_diagnostic_2026-09-10.md).

### EwE-Ecopath-input

Ecopath with Ecosim User Guide: Ecopath Input.

**Role:** method_documentation. Defines landings, discards, mortality, discard fate and biological detritus fate as distinct inputs.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** Documentation, not an article or evidence for any historical fleet return fraction.

[Reference / source](https://pressbooks.bccampus.ca/eweguide/chapter/ecopath-input/)

Local use: [source_evidence.md](../research/discard_sensitivity_2026_09_10/results/source_evidence.md).

### EwE-spatial-fishery

Ecopath with Ecosim: Spatial fishery dynamics.

**Role:** method_documentation. Supports separate fleet landings, discards, mortality and fate fields.

**Evidence:** Local documented use; bibliography not freshly reverified online.

[Reference / source](https://pressbooks.bccampus.ca/ewemodel/chapter/spatial-fishery-dynamics/)

Local use: [source_evidence.md](../research/discard_sensitivity_2026_09_10/results/source_evidence.md); [README.md](../docs/discard-audit-2026-09-10/README.md).

### EwE-bycatch-discards

Ecopath with Ecosim: Bycatch and discards.

**Role:** method_documentation. Motivates examination of scavenger/trophic effects under alternative discard scenarios.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** Does not establish a universal return fraction.

[Reference / source](https://pressbooks.bccampus.ca/ewemodel/chapter/bycatch-and-discards/)

Local use: [source_evidence.md](../research/discard_sensitivity_2026_09_10/results/source_evidence.md).

### Sea-Around-Us-catch-methods

Sea Around Us catch reconstruction methods (2016 document) and FAQ.

**Role:** catch_data_documentation. Defines reconstructed catch to include reported and unreported landed and discarded catch; provides the catch-boundary interpretation used in the atlas.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** Data-method documentation; original per-region reconstruction citations remain upstream, not independently verified here.

[Reference / source](https://www.seaaroundus.org/doc/Methods/CatchReconstructionMethod/Methods-Catch-tab-May-02-2016.pdf)

Local use: [README.md](../SeaAroundUsExtraction/README.md); [README.md](../docs/discard-audit-2026-09-10/README.md).

### Sea-Around-Us-regions

Sea Around Us, University of British Columbia: LME, High Seas and EEZ geography and published regional metrics.

**Role:** geography_and_reference_data. Supplies ecosystem identities and polygons for regional extraction; published climatological NPP values provide a legacy comparison, not annual observations.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** Measured input-polygon areas and source provenance control the extraction. The fixed LME+High-Seas union is not a claim of complete world-ocean coverage.

[Reference / source](https://www.seaaroundus.org/)

Local use: [METHODS.md](../NPPExtraction/METHODS.md); [README.md](../SeaAroundUsExtraction/README.md).

### taxonomy-services

WoRMS, FishBase, NCBI Taxonomy, Eschmeyer’s Catalog of Fishes and IMARPE species records.

**Role:** taxonomy_mapping_support. Support nomenclature, taxonomic lineage and explicitly labeled ecological mapping inferences. Individual species citations and responses remain in each mapping taxonomy-sources.json and source-review files.

**Evidence:** Local documented use; bibliography not freshly reverified online.

**Limit:** Services are not model papers; taxonomic agreement does not establish membership or geographic model applicability.

[Reference / source](https://www.marinespecies.org/rest/)

Local use: [13_2_Northern_Humboldt_Current_(1995-1998).notes.md](../data/LME_013/mapping/13_2_Northern_Humboldt_Current_(1995-1998).notes.md); [32_1_Arabian_Sea_off_Karnataka_(2000).notes.md](../data/LME_032/mapping/32_1_Arabian_Sea_off_Karnataka_(2000).notes.md); [35_412_Gulf_of_Thailande_(1963).notes.md](../data/LME_035/mapping/35_412_Gulf_of_Thailande_(1963).notes.md).

## Complete catalog reference inventory

Bibliographic fields below are inherited from the catalog; corrections in the use paragraphs take precedence for the stated application. Repeated source IDs preserve every regional row in the companion JSON, including different bibliography, correction notes and retrieval status. No missing author, year, title or DOI is silently completed.

### AAT-2008

Cornejo-Donoso & Antezana (2008). Preliminary trophic model of the Antarctic Peninsula Ecosystem (CCAMLR Subarea 48.1).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `AAT-2008__HS_048`, `ANT-2008__LME_061`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2008.06.011)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### ALE-2007

Aydin et al. (2007). A comparison of the Bering Sea, Gulf of Alaska, and Aleutian Islands LMEs through food web modeling.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `ALE-2007__LME_065`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://repository.library.noaa.gov/view/noaa/22894)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### ARAB-2005

K. S. Mohamed; P. U. Zacharia; C. Muthiah; K. P. Abdurahiman; T. H. Nayak (2008). Trophic Modelling of the Arabian Sea Ecosystem off Karnataka and Simulation of Fishery Yields.

**Role:** model_parameters_and_mapping. CMFRI Bulletin 51 supports the Karnataka model and 129 numbered members. Repository metadata labels the report 2008; mapping notes call it 2005 and the source ID retains 2005. Preserve this discrepancy. Primary repository checked 2026-09-11: https://eprints.cmfri.org.in/3945/. Geographic transfer is Karnataka shelf to Arabian Sea LME.

Regional records: `ARAB-2005__LME_032`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://eprints.cmfri.org.in/3945/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json); [32_1_Arabian_Sea_off_Karnataka_(2000).notes.md](../data/LME_032/mapping/32_1_Arabian_Sea_off_Karnataka_(2000).notes.md).

### ARC-2012

Carder (2012). Lancaster Sound through a sunstone: an Ecopath model of mercury bioaccumulation and human exposure.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `ARC-2012__LME_066`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://harvest.usask.ca/handle/10388/ETD-2012-01-266)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### AZO-2016

Telmo Morato; Emile Lemey; Gui Menezes; Christopher K. Pham; Joana Brito; Ambre Soszynski; Tony J. Pitcher; Johanna J. Heymans (2016). Food-Web and Ecosystem Structure of the Open-Ocean and Deep-Sea Environments of the Azores, NE Atlantic.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `AZO-2016__EEZ_622`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2016.00245)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### BAL-2026

Kulatska, Tomczak & Bergström (2026). Ecopath with Ecosim for the Baltic Sea (ICES SD 22–32 excluding the Gulf of Riga): model description.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `BAL-2026__LME_023`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.54612/a.7s9j8fa2pv)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### BAR-2021

Pedersen et al. (2021). Overexploitation, Recovery, and Warming of the Barents Sea Ecosystem During 1950–2013.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `BAR-2021__LME_020`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2021.732637)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### BEA-2018

Suprenand, Ainsworth & Hoover (2018). Ecosystem model of the entire Beaufort Sea marine ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `BEA-2018__LME_055`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://digitalcommons.usf.edu/msc_facpub/261/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### BEN-2007

Heymans & Sumaila (2007). Updated ecosystem model for the Northern Benguela ecosystem, Namibia.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `BEN-2007__LME_029`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.researchgate.net/publication/303125785_Updated_ecosystem_model_for_the_Northern_Benguela_ecosystem_Namibia)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### BEN-2020

Shannon et al. (2020). Temporal variability in the Southern Benguela over four decades.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `BEN-2020__LME_029`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2020.00540)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### BIMINI-2001

Alan T. Grant (2001). Preliminary trophic model of a lemon shark (Negaprion brevirostris) nursery at Bimini, Bahamas.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `BIMINI-2001__EEZ_044`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://elasmo.org/meetings/abstracts/abst2001/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### BLS-2014

Akoglu et al. (2014). An indicator-based evaluation of Black Sea food web dynamics during 1960–2000.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `BLS-2014__LME_062`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.jmarsys.2014.02.010)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### BOB-2014

Guénette (2014). User's guide to the Ecopath with Ecosim model of the Bay of Bengal Large Marine Ecosystem.

**Role:** companion_sought_not_obtained. The model user guide was sought as a possible source of the original EwE model; the host failed. It was not used to supply membership or numerical data.

Regional records: `BOB-2014__LME_034`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.boblme.org/documentRepository/BOBLME-2014-Ecology-13.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [34_1_Bay_of_Bengal_(1978).notes.md](../data/LME_034/mapping/34_1_Bay_of_Bengal_(1978).notes.md).

### BOB-2014-EXPLORATORY

Sylvie Guénette (2014). An exploratory ecosystem model of the Bay of Bengal Large Marine Ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `BOB-2014-EXPLORATORY__EEZ_462`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.boblme.org/documentRepository/BOBLME-2014-Ecology-09.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### BOB-2019

Karim et al. (2019). Ecopath model of the coastal fisheries ecosystem of Bangladesh.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `BOB-2019__LME_034`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### CAL-2016

Koehn et al. (2016). Developing a high taxonomic resolution food web model to assess the functional role of forage fish in the California Current ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `CAL-2016__LME_003`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2016.05.010)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### CAN-2009

Morissette et al. (2009). Food-web model and data for marine-mammal and fishery interactions in Northwest Africa.

**Role:** selected_pilot_source_pending_model_evidence. Selected as a pilot source; selection alone does not establish a verified mapping/model or authorize every method.

Regional records: `CAN-2009__LME_027`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json).

### CAN-2014

Guénette et al. (2014). Marine protected areas and trophic functioning: Banc d'Arguin and Mauritanian Shelf.

**Role:** selected_pilot_source_pending_model_evidence. Selected as a pilot source; selection alone does not establish a verified mapping/model or authorize every method.

Regional records: `CAN-2014__LME_027`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1371/journal.pone.0094742)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json).

### CAN-ELHIERRO-2019

José Carlos Mendoza; José Carlos Hernández (2019). Modelo trófico del ecosistema rocoso litoral de la isla de El Hierro, islas Canarias.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `CAN-ELHIERRO-2019__EEZ_723`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://riull.ull.es/xmlui/handle/915/19325)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### CANTAB-2004

Francisco Sánchez; Ignacio Olaso (2004). Effects of fisheries on the Cantabrian Sea shelf ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `CANTAB-2004__EEZ_963`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2003.09.005)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### CAR-2009

Melgo et al. (2009). Food-web model and data for marine-mammal and fishery interactions in the Caribbean ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `CAR-2009__LME_012`, `CAR-2009__EEZ_474`, `CAR-2009__EEZ_660`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### CELT-2016

Lauria, Posen & Mackinson (2016). An Ecopath with Ecosim and Ecospace model for the Celtic Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `CELT-2016__LME_024`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.13140/RG.2.2.26937.36965)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### CELT-2017

Bentorcha et al. (2017). Trophic models: what do we learn about Celtic Sea and Bay of Biscay ecosystems?.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `CELT-2017__LME_024`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.jmarsys.2017.03.008)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### CHU-2013

Whitehouse (2013). Preliminary mass-balance food web model of the eastern Chukchi Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `CHU-2013__LME_054`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://repository.library.noaa.gov/view/noaa/4580)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### CROKER-2020

Lyndsay Clavareau; Martin P. Marzloff; Verena M. Trenkel; Catherine M. Bulman; Sophie Gourguet; Bertrand Le Gallic; Pierre-Yves Hernvann; Clara Péron; Nicolas Gasco; Johanna Faure; Paul Tixier (2020). Comparison of approaches for incorporating depredation on fisheries catches into Ecopath.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `CROKER-2020__EEZ_896`, `CROKER-2020__EEZ_897`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1093/icesjms/fsaa219)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### EBR-2005

Freire (2005). Fishing impacts on marine ecosystems off Brazil, with emphasis on the northeastern region.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `EBR-2005__LME_016`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### EBS-2025

Whitehouse, Aydin & McHuron (2025). Updating and extending the Ecopath model of the southeastern Bering Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `EBS-2025__LME_001`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.25923/7pef-2497)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### ECS-2022

Xu et al. (2022). Estimating the impact of a seasonal fishing moratorium on the East China Sea ecosystem, 1997–2018.

**Role:** model_parameters_and_mapping. Xu et al. (2022) and Table S1 support separate 1997/2018 East China Sea models and species-group mapping; variants are not averaged.

Regional records: `ECS-2022__LME_047`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2022.865645)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json); [47_1_East_China_Sea_(1997).notes.md](../data/LME_047/mapping/47_1_East_China_Sea_(1997).notes.md); [47_2_East_China_Sea_(2018).notes.md](../data/LME_047/mapping/47_2_East_China_Sea_(2018).notes.md).

### EKAS-2005

Elis Indrayanti (2005). Studi Ekosistem Teluk Ekas Melalui Pendekatan Keseimbangan Masa.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `EKAS-2005__EEZ_938`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.14710/ik.ijms.10.2.85-89)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### ETP-2003

Olson & Watters (2003). A model of the pelagic ecosystem in the eastern tropical Pacific Ocean.

**Role:** selected_pilot_source_pending_model_evidence. Selected as a pilot source; selection alone does not establish a verified mapping/model or authorize every method.

Regional records: `ETP-2003__HS_077`, `ETP-2003__EEZ_898`, `ETP-2003__EEZ_930`, `ETP-2003__EEZ_942`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.iattc.org/en-US/Publication/Commission/Bulletin)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json).

### FAR-2004

Zeller & Reinert (2004). Modelling spatial closures and fishing effort restrictions in the Faroe Islands marine ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `FAR-2004__LME_060`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2003.09.020)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### GAL-2021

Marjorie Riofrío-Lazo; Gunter Reck; Diego Páez-Rosas; Manuel J. Zetina-Rejón; Pablo Del Monte-Luna; Harry Reyes; Juan Carlos Murillo-Posada; Juan Carlos Hernández-Padilla; Francisco Arreguín-Sánchez (2021). Food web modeling of the southeastern Galapagos shelf ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `GAL-2021__EEZ_219`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolind.2021.108270)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### GAL-2024

K. McMullen; F. H. Vargas; P. Calle; O. Alavarado-Cadena; E. A. Pakhomov; J. J. Alava (2024). Modelling microplastic bioaccumulation and biomagnification potential in the Galápagos penguin ecosystem using Ecopath and Ecosim (EwE) with Ecotracer.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `GAL-2024__EEZ_219`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1371/journal.pone.0296788)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### GBR-2000

Gribble (2000). A model of the ecosystem and associated penaeid prawn community in the far Northern Great Barrier Reef.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `GBR-2000__LME_040`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/php/protect/base_model.php?action=base&model=54)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### GOA-2007

Aydin et al. (2007). Comparison of the Bering Sea, Gulf of Alaska and Aleutian Islands LMEs through food-web modelling.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `GOA-2007__LME_002`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://repository.library.noaa.gov/view/noaa/22894)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### GOC-2009

Lercari & Arreguín-Sánchez (2009). An ecosystem modelling approach to deriving viable harvest strategies for the Northern Gulf of California.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `GOC-2009__LME_004`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1002/aqc.978)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### GOM-2021

Berenshtein et al. (2021). Technical documentation of a U.S. Gulf of Mexico Ecopath with Ecosim model.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `GOM-2021__LME_005`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.25923/zj8t-e656)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### GOT-2003

Vibunpant et al. (2003). Trophic model of the coastal fisheries ecosystem in the Gulf of Thailand.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `GOT-2003__LME_035`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://hdl.handle.net/20.500.12348/2140)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### GUI-2004

Palomares & Pauly (eds.) (2004). West African marine ecosystems: models and fisheries impacts.

**Role:** model_parameters_mapping_and_original_discard_audit. The actual Guinea source is Guénette and Diallo (2004), Addendum: Modèles de la côte guinéenne, 1985 et 1998, pp.124–159 in this compilation. Tables support membership, 1998 model parameters and assumed discard amounts; fleet destination remains unknown. Compilation editors are not chapter authors.

Regional records: `GUI-2004__LME_028`, `GUI-2004__EEZ_132`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.seaaroundus.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json); [source_evidence.md](../research/discard_sensitivity_2026_09_10/results/source_evidence.md); [28_646_Guinea_(1998).notes.md](../data/LME_028/mapping/28_646_Guinea_(1998).notes.md).

### HAW-2013

Weijerman, Fulton & Parrish (2013). Comparison of coral reef ecosystems along a fishing pressure gradient.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `HAW-2013__LME_010`, `HAW-2013__EEZ_488`, `HAW-2013__EEZ_842`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1371/journal.pone.0063797)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### HUD-2010

Hoover (2010). Hudson Bay ecosystem: past, present, and future.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `HUD-2010__LME_063`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### HUM-2018

Chiaverano et al. (2018). Large jellyfish and forage fishes as energy pathways in the Northern Humboldt Current System.

**Role:** model_parameters_mapping_and_original_discard_audit. Chiaverano et al. (2018), original article and supplement, provide the Northern Humboldt model, added jellyfish groups, membership evidence and explicit fleet landings/discards/fates. Original title: Evaluating the role of large jellyfish and forage fishes as energy pathways, and their interplay with fisheries, in the Northern Humboldt Current System. The catalog title is abbreviated.

Regional records: `HUM-2018__LME_013`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.pocean.2018.04.009)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json); [source_evidence.md](../research/discard_sensitivity_2026_09_10/results/source_evidence.md); [13_2_Northern_Humboldt_Current_(1995-1998).notes.md](../data/LME_013/mapping/13_2_Northern_Humboldt_Current_(1995-1998).notes.md).

### HUM-2026

Neira et al. (2026). Analysing ecosystem and demersal-stock dynamics in Chilean Patagonia, 1980–2020.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `HUM-2026__LME_013`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.pocean.2025.103631)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### IBER-2019

Veiga-Malta et al. (2019). First representation of the trophic structure and functioning of the Portuguese continental shelf ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `IBER-2019__LME_025`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3354/meps12724)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### ICE-2018

Ribeiro et al. (2018). An overview of the marine food web in Icelandic waters using Ecopath with Ecosim.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `ICE-2018__LME_059`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.48550/arXiv.1810.00613)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### INDO-1999

Buchary (1999). Marine ecosystem and fisheries in the Java Sea: an Ecopath assessment.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `INDO-1999__LME_038`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/php/protect/base_model.php?action=base&model=410)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### IO-2025-HINDCAST

Roger Amate; Maria José Juan-Jordá; Xavier Corrales; Iker Zudaire; Eider Andonegi (2025). Hindcasting the food-web dynamics of the tropical Indian Ocean pelagic ecosystem over the last two decades.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `IO-2025-HINDCAST__EEZ_462`, `IO-2025-HINDCAST__EEZ_690`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://iotc.org/documents/hindcasting-food-web-dynamics-tropical-indian-ocean-pelagic-ecosystem-over-last-two)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### IO-2026

Amate I López-Sivera et al. (2026). Ecosystem structure and fishing impacts in the oceanic pelagic tropical Indian Ocean.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `IO-2026__HS_051`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.2139/ssrn.6636676)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### KER-2005

Pruvost, Duhamel & Palomares (2005). An ecosystem model of the Kerguelen Islands' EEZ.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `KER-2005__HS_058`, `KER-2005__EEZ_897`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### KPL-2020

Roshni C. Subramaniam; Stuart P. Corney; Kerrie M. Swadling; Jessica Melbourne-Thomas (2020). Exploring ecosystem structure and function of the northern Kerguelen Plateau using a mass-balanced food web model.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `KPL-2020__EEZ_334`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.dsr2.2020.104787)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### KPL-ECO-2020

Roshni C. Subramaniam; Jessica Melbourne-Thomas; Stuart P. Corney; Karen Alexander; Clara Péron; Philippe Ziegler; Kerrie M. Swadling (2020). Time-Dynamic Food Web Modeling to Explore Environmental Drivers of Ecosystem Change on the Kerguelen Plateau.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `KPL-ECO-2020__EEZ_334`, `KPL-ECO-2020__EEZ_897`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2020.00641)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### KUR-2019

Watari et al. (2019). Ecosystem modeling in the western North Pacific using Ecopath, with a focus on small pelagic fishes.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `KUR-2019__LME_049`, `KUR-2019__LME_051`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.jstor.org/stable/26789798)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### KUR-2025

Gan et al. (2025). Ecosystem structure and trophodynamics in the Kuroshio–Oyashio Extension area.

**Role:** inspected_alternative_not_used. Gan et al. (2025) and its supplement were inspected as an alternate extraction-validation candidate. Many diet cells report only + (<0.01), so it was not selected for the exact-value validation.

Regional records: `KUR-2025__LME_049`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2025.111152)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [NEW_PAPER_VALIDATION.md](../docs/NEW_PAPER_VALIDATION.md).

### LAPE-2008

Elizabeth Mohammed; Marcelo Vasconcellos; Steve Mackinson; Paul Fanning; Sherry Heileman; Fabio Carocci (2008). A trophic model of the Lesser Antilles pelagic ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LAPE-2008__EEZ_028`, `LAPE-2008__EEZ_052`, `LAPE-2008__EEZ_312`, `LAPE-2008__LME_012`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.researchgate.net/publication/278677766_A_Trophic_Model_of_the_Lesser_Antilles_Pelagic_Ecosystem)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME001-Whitehouse-2021

George A. Whitehouse et al. (2021). Bottom–Up Impacts of Forecasted Climate Change on the Eastern Bering Sea Food Web.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME001-Whitehouse-2021__LME_001`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2021.624301)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME004-MoralesZarate-2004

M. V. Morales-Zárate; F. Arreguín-Sánchez; J. López-Martínez; S. E. Lluch-Cota (2004). Ecosystem trophic structure and energy flux in the Northern Gulf of California, México.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME004-MoralesZarate-2004__LME_004`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2003.09.028)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME005-Allen-2023

Kira L. Allen; Jason A. Garwood; Kelin Hu; Ehab A. Meselhe; Kristy A. Lewis (2023). Simulating synergistic impacts of climate change and human induced stressors on a northern Gulf of Mexico estuarine food web.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME005-Allen-2023__LME_005`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2023.1213949)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME007-Buchheister-2017

Andre Buchheister; Thomas J. Miller; Edward D. Houde; David A. Loewensteiner (2017). Technical Documentation of the Northwest Atlantic Continental Shelf (NWACS) Ecosystem Model.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME007-Buchheister-2017__LME_007`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://hjort.cbl.umces.edu/NWACS/TS_694_17_NWACS_Model_Documentation.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME008-Araujo-2011

J. N. Araújo; A. Bundy (2011). Description of three Ecopath with Ecosim ecosystem models developed for the Bay of Fundy, Western Scotian Shelf and NAFO Division 4X.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME008-Araujo-2011__LME_008`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://publications.gc.ca/site/eng/9.573515/publication.html)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME009-Bundy-2000

Alida Bundy; George R. Lilly; Peter A. Shelton (2000). A mass balance model of the Newfoundland-Labrador Shelf.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME009-Bundy-2000__LME_009`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://publications.gc.ca/collections/collection_2012/mpo-dfo/Fs97-6-2310-eng.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME009-Tam-2019

Jamie C. Tam; Alida Bundy (2019). Mass-balance models of the Newfoundland and Labrador Shelf ecosystem for 1985-1987 and 2013-2015.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME009-Tam-2019__LME_009`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://publications.gc.ca/site/eng/9.877553/publication.html)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME011-Alms-2019

Viola Alms; Matthias Wolff (2019). The Gulf of Nicoya (Costa Rica) Fisheries System: Two Decades of Change.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME011-Alms-2019__LME_011`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1002/mcf2.10050)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME014-OcampoReinaldo-2016

Matías Ocampo Reinaldo; Andrés C. Milessi; María Alejandra Romero; Enrique Crespo; Matthias Wolff; Raúl A. González (2016). Assessing the effects of demersal fishing and conservation strategies of marine mammals over a Patagonian food web.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME014-OcampoReinaldo-2016__LME_014`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2015.10.025)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME016-Freire-2008

Kátia M. F. Freire; Villy Christensen; Daniel Pauly (2008). Description of the East Brazil Large Marine Ecosystem using a trophic model.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME016-Freire-2008__LME_016`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3989/scimar.2008.72n3477)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME017-Wolff-2006

Matthias Wolff (2006). Biomass flow structure and resource potential of two mangrove estuaries: insights from comparative modelling in Costa Rica and Brazil.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME017-Wolff-2006__LME_011`, `LME017-Wolff-2006__LME_017`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://tropicalstudies.org/rbt/attachments/suppls/sup54-1%20EACR%20IV/Wolff%20M%20-%20Biomass%20flow%20structure.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME022-Hill-2021

Clare Evelyn Hill; Jacob W. Bentley; Natalia Serpetti; Clive Fox; Chevonne Angus; Johanna Heymans (2021). Modelling the trophic interaction, structure, and function of the northern North Sea food web: Ecopath Technical Report.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME022-Hill-2021__LME_022`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://pure.uhi.ac.uk/en/publications/modelling-the-trophic-interaction-structure-and-function-of-the-n/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME022-Mackinson-2007

Steven Mackinson; Georgi Daskalov (2007). An ecosystem model of the North Sea to support an ecosystem approach to fisheries management: description and parameterisation.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME022-Mackinson-2007__LME_022`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.cefas.co.uk/publications/techrep/tech142.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME022-Pint-2024

Steven Pint; Martha Stevens; Marleen De Troch; Dick van Oevelen; Johanna Jacomina Heymans; Gert Everaert (2024). Ecopath model of the Southern Bight of the North Sea (version 3).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME022-Pint-2024__LME_022`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.48470/74)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME023-Scott-2022

Scotti, Opitz, MacNeil, Kreutle, Pusch and Froese (2022). Ecosystem-based fisheries management increases catch and carbon sequestration through recovery of exploited stocks: The western Baltic Sea case study.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME023-Scott-2022__LME_023`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2022.879998)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME024-Hernvann-2020

Hernvann, Gascuel, Gruss, Druon, Kopp, Perez, Piroddi and Robert (2020). The Celtic Sea Through Time and Space: Ecosystem Modeling to Unravel Fishing and Climate Change Impacts on Food-Web Structure and Dynamics.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME024-Hernvann-2020__LME_024`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2020.578717)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME025-Torres-2019

Torres, Fonseca, Erzini, Borges, Campos, Castro, Santos, Costa, Marcalo, Oliveira and Vingada (2019). Modelling the impact of deep-water crustacean trawl fishery in the marine ecosystem off Portuguese Southwestern and South Coasts: I) the trophic web and trophic flows.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME025-Torres-2019__LME_025`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.48550/arXiv.1903.11458)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME026-Piroddi-2017

Piroddi, Coll, Liquete, Macias, Greer, Buszowski, Steenbeek, Danovaro and Christensen (2017). Historical changes of the Mediterranean Sea ecosystem: modelling the role and impact of primary productivity and fisheries changes over time.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME026-Piroddi-2017__LME_026`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1038/srep44491)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME027-Villanueva-2004

Maria Concepcion Villanueva, Luis Tito-de-Morais, Jean-Yves Weigel and Jacques Moreau (2004). An Ecopath model of the Sine-Saloum Delta biosphere reserve (Senegal).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME027-Villanueva-2004__LME_027`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://horizon.documentation.ird.fr/exl-doc/pleins_textes/divers13-01/010056023.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME028-Gascuel-2009

Gascuel, Guenette, Diallo and Sidibe (2009). Impact de la peche sur l'ecosysteme marin de Guinee - Modelisation EwE 1985/2005.

**Role:** selected_pilot_source_pending_model_evidence. Selected as a pilot source; selection alone does not establish a verified mapping/model or authorize every method.

Regional records: `LME028-Gascuel-2009__LME_028`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://halieutique.institut-agro.fr/files/fichiers/pdf/3506.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json).

### LME029-Heymans-2004

Heymans, Shannon and Jarre (2004). Changes in the northern Benguela ecosystem over three decades: 1970s, 1980s and 1990s.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME029-Heymans-2004__LME_029`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2003.09.006)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME029-Roux-2004

Roux and Shannon (2004). Ecosystem approach to fisheries management in the northern Benguela: the Namibian experience.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME029-Roux-2004__LME_029`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.2989/18142320409504051)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME030-Silva-1993

De Paula E Silva, Sousa and Caramelo (1993). The Maputo Bay Ecosystem (Mozambique).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME030-Silva-1993__LME_030`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/php/protect/base_model.php?action=base&model=248)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME031-Wabnitz-2020

Wabnitz, Omukoto, Daw and Cheung (2020). Ecosystem modelling to support fisheries management efforts in the Nyali-Mombasa area, coastal Kenya.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME031-Wabnitz-2020__LME_031`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.14288/1.0395032)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME032-Mohamed-2009

K. S. Mohamed; P. U. Zacharia (2009). Prediction and modelling of marine fishery yields from the Arabian Sea off Karnataka using Ecosim.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME032-Mohamed-2009__LME_032`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://eprints.cmfri.org.in/6253/1/IJMS_38%281%29_69-76.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME032-Mohamed-2024

K. Sunil Mohamed (2024). An Ecopath model of the northeastern Arabian Sea (Maharashtra and Gujarat coasts) with emphasis on small pelagic herbivores.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME032-Mohamed-2024__LME_032`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.marin-trust.com/sites/marintrust/files/2025-06/Annex%203%20AN%20ECOPATH%20MODEL%20OF%20THE%20NORTHEASTERN%20ARABIAN%20SEA_0.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME032-Vivekanandan-2003

E. Vivekanandan; M. Srinath; V. N. Pillai; S. Immanuel; K. N. Kurup (2003). Trophic Model of the Coastal Fisheries Ecosystem of the Southwest Coast of India.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME032-Vivekanandan-2003__LME_032`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://eprints.cmfri.org.in/8510/1/Chapter-14-Fa.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME033-Tesfamichael-2012

Dawit Tesfamichael (2012). Assessment of the Red Sea ecosystem with emphasis on fisheries.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME033-Tesfamichael-2012__LME_033`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.14288/1.0072911)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME034-Dutta-2023

Dutta, Paul and Homechaudhuri (2023). Food web structure and trophic interactions of the Northern Bay of Bengal ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME034-Dutta-2023__LME_034`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.rsma.2023.102861)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME034-Guenette-2013

Sylvie Guenette (2013). An exploratory ecosystem model of the Bay of Bengal Large Marine Ecosystem.

**Role:** model_parameters_mapping_and_original_discard_audit. Guénette’s December 2013, 62-page report is the direct Bay model and mapping source: Appendices A1.1–A1.3, Table 16 and catch Appendix A2.1. It supports total-catch semantics; a separate original discard split and fleet return route remain unknown.

Regional records: `LME034-Guenette-2013__LME_034`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.boblme.org/documentRepository/Bengal%20report%2028april2014.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json); [source_evidence.md](../research/discard_sensitivity_2026_09_10/results/source_evidence.md); [34_1_Bay_of_Bengal_(1978).notes.md](../data/LME_034/mapping/34_1_Bay_of_Bengal_(1978).notes.md).

### LME034-Karim-2018

EHSANUL KARIM (2018). ECOSYSTEM MODELING OF THE RESETTLED MARITIME AREA OF THE BAY OF BENGAL, BANGLADESH THROUGH WELL-ADJUSTED ECOPATH APPROACH.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME034-Karim-2018__LME_034`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.15666/aeer/1603_31713196)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME035-Premcharoen-2012

S. Premcharoen (2012). Ecopath Model of the Mae Klong Estuary, Inner Gulf of Thailand.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME035-Premcharoen-2012__LME_035`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.4027/gpebfm.2012.01)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME036-DeepSeep-2020

Zhe-Yu Lin; Hsuan-Wien Chen; Hsing-Juh Lin (2020). Trophic model of a deep-sea ecosystem with methane seeps in the South China Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME036-DeepSeep-2020__LME_036`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.dsr.2020.103251)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME036-Dongzhaigang-2023

Chengpu Jiang; Daniel Pauly; Wenqing Wang; Jianguo Du; Jianhua Cheng; Mao Wang (2023). A preliminary model of the mangrove ecosystem of Dongzhaigang Bay, Hainan, (China) based on Ecopath and Ecospace.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME036-Dongzhaigang-2023__LME_036`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2023.1277226)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME036-PearlRanch-2026

Xue Feng; Xiaofan Hong; Pimao Chen; Jiangtao Fan (2026). Ecosystem characteristics and ecological carrying capacity of a subtropical marine ranch in the pearl river estuary: an ecopath modeling approach.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME036-PearlRanch-2026__LME_036`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2026.1744551)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME036-Pitcher-2000

T. J. Pitcher; R. Watson; N. Haggan; S. Guenette; R. Kennish; U. R. Sumaila; D. Cook; K. Wilson; A. Leung (2000). Marine Reserves and the Restoration of Fisheries and Marine Ecosystems in the South China Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME036-Pitcher-2000__LME_036`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.ecomarres.com/downloads/marinereserves.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME036-Xisha-2022

Xinyan Zhang; Yuanchao Li; Jianguo Du; Shuting Qiu; Bin Xie; Weilin Chen; Jianjia Wang; Wenjia Hu; Zhongjie Wu; Bin Chen (2022). Effects of ocean warming and fishing on the coral reef ecosystem: A case study of Xisha Islands, South China Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME036-Xisha-2022__LME_036`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2022.1046106)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME037-Bacalso-2014

Bacalso and Wolff (2014). Trophic flow structure of the Danajon ecosystem (Central Philippines) and impacts of illegal and destructive fishing practices.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME037-Bacalso-2014__LME_037`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.jmarsys.2014.05.014)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME037-Bacalso-2016

Regina Therese M. Bacalso, Matthias Wolff, Rina Maria Rosales and Nygiel B. Armada (2016). Effort reallocation of illegal fishing operations: A profitable scenario for the municipal fisheries of Danajon Bank, Central Philippines.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME037-Bacalso-2016__LME_037`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2016.01.015)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME037-Bacalso-2026

Regina Therese M. Bacalso; Matthias Wolff; Giovanni Romagnoni; Marie Fujitani (2026). Ecological and economic perspectives of two decades of change in a traditional fishing ground in the Philippines.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME037-Bacalso-2026__LME_037`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ocecoaman.2025.108027)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME038-Nurhakim-2003

Subhat Nurhakim (2003). Marine Fisheries Resources of the North Coast of Central Java, Indonesia: An Ecosystem Analysis.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME038-Nurhakim-2003__LME_038`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://digitalarchive.worldfishcenter.org/server/api/core/bitstreams/5436c26d-004a-4233-8d5d-6a3d720687fc/content)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME038-Zainuri-1999

Muhammad Zainuri and Hadi Endrawati (1999). A mass-balance trophic flow model at Awur Bay in the northern central Java Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME038-Zainuri-1999__LME_038`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ejournal.undip.ac.id/index.php/coastdev/article/view/5483)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME039-Griffiths-2011

Griffiths, Bustamante, Lozano-Montes, Robinson, Miller and Brown (2011). Simulated ecological effects of demersal trawling on the Gulf of Carpentaria ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME039-Griffiths-2011__LME_039`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.frdc.com.au/sites/default/files/products/2005-050-DLD.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME040-Gribble-2005

Neil Gribble (2005). Ecosystem Modelling Of The Great Barrier Reef: A Balanced Trophic Biomass Approach.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME040-Gribble-2005__LME_040`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://era.daf.qld.gov.au/id/eprint/11101/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME041-Fondo-2015

Fondo et al. (2015). Banning Fisheries Discards Abruptly Has a Negative Impact on the Population Dynamics of Charismatic Marine Megafauna.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME041-Fondo-2015__LME_041`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1371/journal.pone.0144543)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME042-Fulton-2002

Beth Fulton and Tony Smith (2002). Ecosim Case Study: Port Phillip Bay, Australia.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME042-Fulton-2002__LME_042`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.seaaroundus.org/doc/publications/books-and-reports/2002/Pitcher-et-al-Ecosystem-Models.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME043-WAMSI-2024

Lozano-Montes, Loneragan, Fourie and Wise (2024). Using conceptual, qualitative and quantitative ecosystem models to characterise the trophic structure, ecosystem attributes and functioning of Cockburn Sound.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME043-WAMSI-2024__LME_043`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://wamsi.org.au/wp-content/uploads/2024/04/WWMSP_1.3_-Conceptual_qualitative_quantitative_ecosystem_models_FINAL.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME044-Fulton-2011

Fulton et al. (2011). Ningaloo Collaboration Cluster: Adaptive Futures for Ningaloo.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME044-Fulton-2011__LME_044`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ningaloo-atlas.org.au/sites/default/files/Adaptive%20futures%20for%20Ningaloo.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME047-Cheng-2009

Jiahua Cheng; William W. L. Cheung; Tony J. Pitcher (2009). Mass-balance ecosystem model of the East China Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME047-Cheng-2009__LME_047`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.pnsc.2009.03.003)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME047-Li-2012

Yunkai Li; Yuying Zhang (2012). Fisheries impact on the East China Sea Shelf ecosystem for 1969–2000.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME047-Li-2012__LME_047`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1007/s10152-011-0278-8)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME048-Gao-2022

Shike Gao; Ze Chen; Yanan Lu; Zhen Li; Shuo Zhang; Wenwen Yu (2022). Comparison of Marine Ecosystems of Haizhou Bay and Lvsi Fishing Ground in China Based on the Ecopath Model.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME048-Gao-2022__LME_048`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3390/w14091397)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME054-Whitehouse-2016

George A. Whitehouse; Kerim Y. Aydin (2016). Trophic structure of the eastern Chukchi Sea: An updated mass balance food web model.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME054-Whitehouse-2016__LME_054`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.7289/V5/TM-AFSC-318)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME055-Hoover-2021

Carie Hoover; Wojciech Walkusz; Shannon MacPhee; Andrea Niemi; Andrew Majewski; Lisa Loseto (2021). Canadian Beaufort Sea Shelf Food Web Structure and Changes from 1970–2012.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME055-Hoover-2021__LME_055`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://publications.gc.ca/collections/collection_2021/mpo-dfo/Fs97-13-1313-eng.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME059-Mendy-1998

Asberr Natoumbi Mendy (1998). Trophic modelling as a tool to evaluate and manage Iceland’s multispecies fisheries.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME059-Mendy-1998__LME_059`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.grocentre.is/ftp/moya/gro/index/publication/trophic-modelling-as-a-tool-to-evaluate-and-manage-icelands-multispecies-fisheries)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME059-Sonjudottir-2024

Anika Sonjudóttir; Erla Sturludóttir; Bjarki Þór Elvarsson (2024). Modelling the food web in Icelandic waters.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME059-Sonjudottir-2024__LME_059`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.hafogvatn.is/static/research/files/modelling-the-food-web-in-icelandic-waters.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME061-Dahood-2019

Adrian Dahood; George M. Watters; Kim de Mutsert (2019). Using sea-ice to calibrate a dynamic trophic model for the Western Antarctic Peninsula.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME061-Dahood-2019__LME_061`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1371/journal.pone.0214814)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME062-Akoglu-2023

Ekin Akoglu (2023). Ecological indicators reveal historical regime shifts in the Black Sea ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME062-Akoglu-2023__LME_062`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.7717/peerj.15649)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME063-Hoover-2012

Carie Hoover (2012). Effects of harvest and climate change on polar marine ecosystems: Case studies from the Antarctic Peninsula and Hudson Bay.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME063-Hoover-2012__LME_061`, `LME063-Hoover-2012__LME_063`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://library-archives.canada.ca/eng/services/services-libraries/theses/Pages/item.aspx?idNumber=1033158617)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME065-Guenette-2006

Sylvie Guénette; Sheila J. J. Heymans; Villy Christensen; Andrew W. Trites (2006). Ecosystem models show combined effects of fishing, predation, competition, and ocean productivity on Steller sea lions (Eumetopias jubatus) in Alaska.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME065-Guenette-2006__LME_065`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1139/f06-136)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### LME066-Mohammed-2001

Elizabeth Mohammed (2001). A preliminary model for the Lancaster Sound region in the 1980s.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `LME066-Mohammed-2001__LME_066`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://epub.sub.uni-hamburg.de/epub/volltexte/2011/12279/pdf/9_4.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### MADEIRA-2024

Joana Romero; Hany Alonso; Luís Freitas; José Pedro Granadeiro (2024). Food web of the oceanic region of the archipelago of Madeira: The role of marine megafauna in the subtropical northeast Atlantic ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `MADEIRA-2024__EEZ_621`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.marenvres.2024.106382)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### MED-2022

Piroddi et al. (2022). Modelling the Mediterranean Sea ecosystem at high spatial resolution.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `MED-2022__LME_026`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1038/s41598-022-18017-x)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### MHI-2021

M. Weijerman; Z. S. Oyafuso; K. M. Leong; K. L. L. Oleson; M. Winston (2021). Supporting Ecosystem-based Fisheries Management in meeting multiple objectives for sustainable use of coral reef ecosystems.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `MHI-2021__EEZ_842`, `MHI-2021__LME_010`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1093/icesjms/fsaa194)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NBR-2000

Wolff, Koch & Isaac (2000). A trophic flow model of the Caeté Mangrove Estuary (North Brazil).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NBR-2000__LME_017`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1006/ecss.2000.0611)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NC-UVEA-2004

Yves-Marie Bozec; Didier Gascuel; Michel Kulbicki (2004). Trophic model of lagoonal communities in a large open atoll (Uvea, Loyalty islands, New Caledonia).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NC-UVEA-2004__EEZ_540`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1051/alr:2004024)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NEUS-2006

Link et al. (2006). Documentation for the Energy Modeling and Analysis eXercise (EMAX).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NEUS-2006__LME_007`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://repository.library.noaa.gov/view/noaa/5277)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NFL-2001

Bundy (2001). Fishing on ecosystems: the interplay of fishing and predation in Newfoundland–Labrador.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NFL-2001__LME_009`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1139/f01-074)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NICOYA-1998

Matthias Wolff; Volker Koch; Juan Bautista Chavarría; José A. Vargas (1998). A trophic flow model of the Golfo de Nicoya, Costa Rica.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NICOYA-1998__EEZ_930`, `NICOYA-1998__LME_011`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://cris.leibniz-zmt.de/id/eprint/5765/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NICOYA-2020

Viola Alms; Matthias Wolff (2020). Identification of Drivers of Change of the Gulf of Nicoya Ecosystem (Costa Rica).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NICOYA-2020__EEZ_930`, `NICOYA-2020__LME_011`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2020.00707)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NOR-2016

Skaret & Pitcher (2016). An Ecopath with Ecosim model of the Norwegian Sea and Barents Sea validated against time series of abundance.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NOR-2016__LME_021`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.hi.no/en/hi/nettrapporter/fisken-og-havet/2016/fh_7-2016_norbar_skaretpitcher_final_til_web)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NS-2014

Mackinson (2014). Building an Ecopath with Ecosim model of the North Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NS-2014__LME_022`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/index.php?action=base&m_EEZ=353)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NS-2025

Saygu et al. (2025). Historical ecosystem models can serve as a baseline for indicator-based assessment: the North Sea.

**Role:** isolated_validation_not_production. Saygu et al. (2025) author supplements were extracted for the isolated East Coast of Scotland 1991–1995 validation; this does not authorize production pilot inclusion.

Regional records: `NS-2025__LME_022`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2025.1646031)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [NEW_PAPER_VALIDATION.md](../docs/NEW_PAPER_VALIDATION.md).

### NWS-2006

North West Shelf Joint Environmental Management Study (2006). Trophic webs and modelling of Australia's North West Shelf.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NWS-2006__LME_045`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://library.dbca.wa.gov.au/FullTextFiles/064833.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NZ-2003

Bradford-Grieve et al. (2003). Pilot trophic model for subantarctic water over the Southern Plateau, New Zealand.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NZ-2003__LME_046`, `NZ-2003__EEZ_554`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/S0022-0981(03)00045-5)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### NZ-2021-TBGB

Vidette L. McGregor et al. (2021). From data compilation to model validation: comparing three ecosystem models of the Tasman and Golden Bays, New Zealand.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `NZ-2021-TBGB__EEZ_554`, `NZ-2021-TBGB__LME_046`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.7717/peerj.11712)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### OKH-2004

Chaikina (2004). Trophic model of the Sea of Okhotsk ecosystem.

**Role:** model_identity_mapping_and_original_discard_audit. The recovered source used is Chaikina (2020), A model of the Okhotsk Sea with a focus on marine mammals, pp.23–34, FCRR 28(2), based on her unavailable 2004 thesis. Tables support group/diet evidence and the 1980s whole-Sea identity; no source catch vector was recovered. The inherited 2004 catalog record must not be mistaken for a retrieved thesis.

Regional records: `OKH-2004__LME_052`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json); [source_evidence.md](../research/discard_sensitivity_2026_09_10/results/source_evidence.md); [52_1_Sea_of_Okhotsk_NE_(1980).notes.md](../data/LME_052/mapping/52_1_Sea_of_Okhotsk_NE_(1980).notes.md).

### OKH-2015

Radchenko (2015). Characterization of the Sea of Okhotsk Ecosystem Based on Ecosystem Modelling.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `OKH-2015__LME_052`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### OYA-2020

Booth et al. (2020). An Ecopath with Ecosim model for the Pacific coast of eastern Japan.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `OYA-2020__LME_051`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2020.109087)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### PAT-2005

Koen-Alonso & Yodzis (2005). Multispecies modelling of northern and central Patagonia, Argentina.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `PAT-2005__LME_014`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1139/f05-087)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### PAT-2023

Büring et al. (2024). Wasp-waist structure of the Falkland Shelf ecosystem and the role of Doryteuthis gahi.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `PAT-2023__LME_014`, `PAT-2023__EEZ_238`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1017/S0025315423000887)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### PCA-2016

Ruiz, Banks & Wolff (2016). Elucidating fishing effects in a large-predator dominated system: The case of Darwin and Wolf Islands (Galápagos).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `PCA-2016__EEZ_219`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### PEI-2013-THESIS

Leigh Josephine Gurney (2013). An ecosystem study of the Prince Edward Archipelago (Southern Ocean).

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `PEI-2013-THESIS__EEZ_711`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://library-archives.canada.ca/eng/services/services-libraries/theses/Pages/item.aspx?idNumber=1032916499)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### PEI-2014

Leigh J. Gurney; Evgeny A. Pakhomov; Villy Christensen (2014). An ecosystem model of the Prince Edward Island archipelago.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `PEI-2014__EEZ_711`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2014.09.008)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### PRVI-1996

Silvia Opitz (1996). Trophic interactions in Caribbean coral reefs.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `PRVI-1996__EEZ_092`, `PRVI-1996__LME_012`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://digitalarchive.worldfishcenter.org/items/f9b5124e-cb58-4ba7-8ca1-0748a9679de6)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### RIAS-2021

Oriol Giralt Paradell; Séverine Methion; Emer Rogan; Bruno Díaz López (2021). Modelling ecosystem dynamics to assess the effect of coastal fisheries on cetacean species.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `RIAS-2021__EEZ_963`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.jenvman.2021.112175)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### SBR-2004

Gasalla & Rossi-Wongtschowski (2004). Contribution of ecosystem analysis to investigating the effects of changes in fishing strategies in the South Brazil Bight coastal ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `SBR-2004__LME_015`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.ecolmodel.2003.09.012)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### SCO-2004

Bundy (2004). Mass balance models of the eastern Scotian Shelf before and after the cod collapse.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `SCO-2004__LME_008`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://publications.gc.ca/site/eng/9.574099/publication.html)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### SCS-1993

Pauly & Christensen (1993). Stratified models of large marine ecosystems: application to the South China Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `SCS-1993__LME_036`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://s3-us-west-2.amazonaws.com/legacy.seaaroundus/doc/Researcher+Publications/dpauly/PDF/1993/Books+and+Chapters/StratifiedModelsOfLargeMarineEcosystems.pdf)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### SCS-2007

Wai Lung Cheung (2007). Vulnerability of marine fishes to fishing: from global overview to the northern South China Sea.

**Role:** model_parameters_and_mapping. Cheung’s thesis Tables 6.1/6.2 and Appendices 6.1/6.2 support distinct 1970s/2000s models and functional-group membership. Source conflicts remain documented; models cover a northern shelf subregion.

Regional records: `SCS-2007__LME_036`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.14288/1.0074894)

Local use: [articles.csv](../PPRAtlas/data/articles.csv); [atlas_selection.json](../data/atlas_selection.json); [36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s).notes.md](../data/LME_036/mapping/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s).notes.md).

### SEAUS-2006

Klaer (2006). Changes in the structure of demersal fish communities of the southeast Australian continental shelf from 1915 to 1961.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `SEAUS-2006__LME_042`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### SEUS-2001

Okey & Pugliese (2001). A preliminary Ecopath model of the Atlantic continental shelf adjacent to the Southeastern United States.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `SEUS-2001__LME_006`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/php/protect/base_model.php?action=base&model=467)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### SG-2012

Simeon L. Hill; Kathryn Keeble; Angus Atkinson; Eugene Murphy (2012). A foodweb model to explore uncertainties in the South Georgia shelf pelagic ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `SG-2012__EEZ_239`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1016/j.dsr2.2011.09.001)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### SOJ-2023

Inoue et al. (2023). Impacts of regime shift on the fishery ecosystem in coastal Kyoto, Sea of Japan.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `SOJ-2023__LME_050`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1007/s12562-023-01691-9)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### SWP-2013

Watson et al. (2013). Ecosystem model of Tasmanian waters explores impacts of climate-change induced changes.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `SWP-2013__HS_081`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### TIH-1997

J. E. Arias-González; B. Delesalle; B. Salvat; R. Galzin (1997). Trophic functioning of the Tiahura reef sector, Moorea Island, French Polynesia.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `TIH-1997__EEZ_258`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.1007/s003380050079)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### WBS-2002

Aydin et al. (2002). A comparison of the eastern and western Bering Sea shelf/slope ecosystems through mass-balance food web models.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `WBS-2002__LME_053`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://repository.library.noaa.gov/view/noaa/61265)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### WCA-2026

Narváez Ruiz et al. (2026). Mapping trophic interactions in the Western Central Atlantic pelagic ecosystem: an Ecopath modeling approach.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `WCA-2026__HS_031`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://www.researchgate.net/publication/410668269)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### WCP-2007

Allain et al. (2007). An Ecopath with Ecosim model of the Western and Central Pacific Ocean warm-pool pelagic ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `WCP-2007__HS_071`, `WCP-2007__EEZ_090`, `WCP-2007__EEZ_316`, `WCP-2007__EEZ_520`, `WCP-2007__EEZ_548`, `WCP-2007__EEZ_580`, `WCP-2007__EEZ_583`, `WCP-2007__EEZ_584`, `WCP-2007__EEZ_585`, `WCP-2007__EEZ_598`, `WCP-2007__EEZ_798`, `WCP-2007__EEZ_941`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://meetings.wcpfc.int/node/6157)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### WGR-2001

Pedersen & Zeller (2001). A mass balance model for the West Greenland marine ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `WGR-2001__LME_018`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### YS-2013

Lin et al. (2013). Ecopath assessment of the Yellow Sea ecosystem.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `YS-2013__LME_048`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://ecobase.ecopath.org/)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

### YS-2022

Zhang et al. (2022). Differences between artificial-reef and natural-reef ecosystem characteristics in the Yellow Sea.

**Role:** archive_candidate_not_calculation_input. Supports the documented regional literature inventory and candidate assessment. No direct numerical use is established by catalog membership.

Regional records: `YS-2022__LME_048`.
Bibliography verification: inherited catalog record; consult the cited local source audit for corrections.

[Catalog reference link](https://doi.org/10.3389/fmars.2022.911714)

Local use: [articles.csv](../PPRAtlas/data/articles.csv).

## Maintaining this log

Update the authoritative article catalog and selection only when the underlying project evidence changes. Add a new method/context/input reference to `ADDITIONAL`, or a documented use/correction to `OVERRIDES`, in `external/build_reference_use_log.py`. State what claim or calculation it supports, its local evidence, access limits and verification date. Keep candidate-only, selected, verified computational, isolated-validation and contextual roles separate.

Run `python external/build_reference_use_log.py`, then `python external/build_reference_use_log.py --check`. The companion `ARTICLE_REFERENCE_USE_LOG.json` retains every source row, role and evidence-file hash. Regenerate after changes to any hashed evidence document. A changed hash requests review; it does not itself verify a publication.

Unresolved bibliography to retain explicitly: the supplied 2020 MeanTL workbook’s parent article; the inherited 1986 method attribution; incomplete contextual citations; and the CMFRI 2005/2008 year discrepancy. Do not equate a source filename with a publication identity. The conversion-factor literature review remains deferred.
