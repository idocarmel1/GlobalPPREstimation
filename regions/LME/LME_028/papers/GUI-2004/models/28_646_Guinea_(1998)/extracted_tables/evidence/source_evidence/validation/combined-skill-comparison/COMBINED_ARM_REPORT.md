# Combined-skill Guinea arm report

Completed mapping of all **375 taxa** for `28_646_Guinea_(1998)`. The isolated combined validator reports **PASS**, with zero member-list contradictions.

Named groups carry **99.665235%** of 167,652,883.904 t reported across 1950-2019. Coverage is a joinability measure, not a finding of scientific accuracy or non-inferiority.

| Confidence | Taxa | Catch share |
| --- | ---: | ---: |
| high | 164 | 41.204162% |
| medium | 85 | 21.213179% |
| low | 121 | 37.247894% |
| unresolved | 5 | 0.334765% |

There are 56 composite rows carrying 41.395127% of catch. Weight bases: {'catch_composition': 22, 'model_biomass': 34}. The detailed model notes state the candidate-set assumptions, fallback rules and geographic limits.

Unresolved records:

| Taxon | Catch tonnes | Reason |
| --- | ---: | --- |
| Sarotherodon galilaeus | 405,273.307 | This predominantly freshwater tilapia has no documented freshwater/algal-feeding compartment in the offshore Guinea model. Its implausible SAU large-reef label does not establish marine ecological representation; the catch location/salinity requires review. |
| Chondrichthyes | 155,684.310 | The catch common name explicitly includes sharks, rays and chimaeras. Only the elasmobranch portion is documented in the model; there is no identified fraction with which to separate unsupported holocephalans. Do not silently assign the entire coarse record to sharks/rays. |
| Cyprinidae | 148.271 | This freshwater family has no corresponding freshwater compartment in the marine model; a medium-demersal SAU class does not establish a marine feeding pathway. |
| Inermiidae | 136.765 | This bonnetmouth family is absent from the source member list and its tropical western-Atlantic affinities leave the eastern-Atlantic model identity/occurrence unsupported. A generic small-pelagic SAU class is insufficient to establish that this taxon is represented. |
| Chimaeriformes | 0.982 | Chimaeras are Holocephali, not the sharks/rays documented in the four Sélaciens groups. The source provides no chimaera assignment, and finfish bathy guilds do not establish representation (WoRMS Holocephali https://www.marinespecies.org/aphia.php?id=10196&p=taxdetails). |

The validator confirms 166 taxa (52.1% of catch) against its member-name/genus intersection check. That includes genus extrapolations and partial intersections of composites; it must not be reported as 166 independent exact biological validations.

The 1998 workbook and all supplied biological/source evidence were read only. SPPR and PPR workbooks were not rebuilt. The copied 1985 model is outside this arm. Public-source spot checks supplemented the shared audited table. Production decisions and other agents’ mapping outputs were not consulted, but the shared source evidence and parent-held production arm mean this is not fully blinded.

Mapping SHA-256: `c569147a213a1108cee42be37c012bb27accfe1bbe90bf73a4b33ceb86d277fe`. Input hashes and exact metrics are in `combined_arm_metrics.json`; validator output is in `combined_arm_validation.txt`.

Composite decisions and weight bases:

| Taxon | Candidate groups | Basis | Confidence |
| --- | --- | --- | --- |
| Marine fishes not identified | Côtier L pred; Côtier M pred; Côtier M inv; Côtier S pred; Côtier S inv; Dem L pred; Dem L inv; Dem M pred; Dem M inv; Dem S pred; Dem S inv | catch_composition (blank) | low |
| Clupeiformes | Côtier pel S inv; Ethmalose | catch_composition (blank) | medium |
| Carangidae | Côtier pel L pred; Pel L pred; Pel S inv; Côtier M pred | catch_composition (blank) | low |
| Sciaenidae | Bars; Côtier L pred; Côtier S pred; Dem L pred; Dem L inv; Dem M pred | catch_composition (blank) | medium |
| Clupeidae | Côtier pel S inv; Ethmalose | catch_composition (blank) | medium |
| Scombridae | Thons majeurs; Thons mineurs; Pel S inv | catch_composition (blank) | medium |
| Elasmobranchii | Sélaciens L prof; Sélaciens L côtiers; Sélaciens M prof; Sélaciens M côtiers | model_biomass | low |
| Mugilidae | Mulets; Dem M inv | catch_composition (blank) | medium |
| Polynemidae | Gros capitaine; Petit capitaine; Capitaine royal | catch_composition (blank) | medium |
| Haemulidae | Côtier M inv; Côtier S inv; Dem M inv | catch_composition (blank) | medium |
| Lutjanidae | Côtier L pred; Dem L pred | model_biomass | low |
| Perciformes | Bars; Gros capitaine; Côtier L pred; Côtier M pred; Disques; Mulets; Petit capitaine; Côtier M inv; Côtier S pred; Capitaine royal; Côtier S inv; Dem L pred; Dem L inv; Dem M pred; Dem M inv; Dem S pred; Dem S inv | catch_composition (blank) | low |
| Scombroidei | Thons majeurs; Thons mineurs | catch_composition (blank) | medium |
| Dentex | Côtier L pred; Dem M pred | model_biomass | medium |
| Sparidae | Côtier L pred; Mulets; Côtier M inv; Côtier S inv; Dem L pred; Dem L inv; Dem M pred; Dem M inv | catch_composition (blank) | low |
| Dasyatidae | Sélaciens L côtiers; Sélaciens M côtiers | model_biomass | medium |
| Marine pelagic fishes not identified | Côtier pel L pred; Côtier pel S inv; Pel L pred; Pel S inv | catch_composition (blank) | low |
| Epinephelus | Côtier L pred; Dem L pred | model_biomass | medium |
| Squalidae | Sélaciens L prof; Sélaciens M prof | model_biomass | medium |
| Rajiformes | Sélaciens L prof; Sélaciens L côtiers; Sélaciens M prof; Sélaciens M côtiers | model_biomass | low |
| Pleuronectiformes | Côtier L pred; Côtier M inv; Côtier S pred; Côtier S inv; Dem L pred; Dem S pred; Dem S inv | catch_composition (blank) | low |
| Trichiuridae | Côtier L pred; Bathy L pred | model_biomass | low |
| Mollusca | Céphalopodes; Benthos | catch_composition (blank) | medium |
| Rajidae | Sélaciens L prof; Sélaciens M prof | model_biomass | medium |
| Serranidae | Côtier L pred; Dem L pred; Dem M pred | catch_composition (blank) | medium |
| Soleidae | Côtier M inv; Côtier S inv; Dem L pred; Dem S pred | catch_composition (blank) | low |
| Carcharhinus | Sélaciens L prof; Sélaciens L côtiers | model_biomass | medium |
| Mugil | Mulets; Dem M inv | model_biomass | medium |
| Scorpaenidae | Côtier S pred; Dem M pred; Dem S pred; Bathy L pred | model_biomass | low |
| Scorpaeniformes | Côtier S pred; Dem L inv; Dem M pred; Dem M inv; Dem S pred; Bathy L pred; Bathy SM inv | model_biomass | low |
| Carcharhinidae | Sélaciens L prof; Sélaciens L côtiers | model_biomass | medium |
| Sphyrna | Sélaciens L prof; Sélaciens L côtiers | model_biomass | low |
| Rhinobatos | Sélaciens L côtiers; Sélaciens M côtiers | model_biomass | medium |
| Raja | Sélaciens L prof; Sélaciens M prof | model_biomass | medium |
| Torpedinidae | Sélaciens L prof; Sélaciens L côtiers; Sélaciens M côtiers | model_biomass | medium |
| Tetraodontidae | Côtier L pred; Dem M pred; Dem S inv | catch_composition (blank) | low |
| Triglidae | Dem M pred; Dem M inv; Bathy SM inv | model_biomass | medium |
| Muraenidae | Côtier L pred; Côtier M pred | model_biomass | medium |
| Batoidea | Sélaciens L prof; Sélaciens L côtiers; Sélaciens M prof; Sélaciens M côtiers | model_biomass | low |
| Rhinobatidae | Sélaciens L côtiers; Sélaciens M côtiers | model_biomass | medium |
| Lophiidae | Dem M pred; Bathy L pred | model_biomass | medium |
| Gadiformes | Dem L pred; Bathy SM inv | model_biomass | low |
| Actinopterygii | Côtier L pred; Côtier M pred; Côtier M inv; Côtier S pred; Côtier S inv; Dem L pred; Dem L inv; Dem M pred; Dem M inv; Dem S pred; Dem S inv | catch_composition (blank) | low |
| Gerreidae | Côtier S pred; Côtier S inv | catch_composition (blank) | medium |
| Myliobatidae | Sélaciens L côtiers; Sélaciens M côtiers | model_biomass | low |
| Scorpaena | Côtier S pred; Dem M pred | model_biomass | low |
| Bothidae | Côtier M inv; Dem S pred | catch_composition (blank) | medium |
| Squaliformes | Sélaciens L prof; Sélaciens M prof | model_biomass | medium |
| Alopias | Sélaciens L prof; Sélaciens L côtiers | model_biomass | low |
| Marine finfishes not identified | Côtier L pred; Côtier M pred; Côtier M inv; Côtier S pred; Côtier S inv; Dem L pred; Dem L inv; Dem M pred; Dem M inv; Dem S pred; Dem S inv | catch_composition (blank) | low |
| Sphyrnidae | Sélaciens L prof; Sélaciens L côtiers | model_biomass | low |
| Carcharhiniformes | Sélaciens L prof; Sélaciens L côtiers; Sélaciens M prof | model_biomass | medium |
| Lamnidae | Sélaciens L prof; Sélaciens L côtiers | model_biomass | low |
| Lamniformes | Sélaciens L prof; Sélaciens L côtiers | model_biomass | medium |
| Squalus | Sélaciens L prof; Sélaciens M prof | model_biomass | medium |
| Labridae | Côtier M pred; Dem M inv | model_biomass | low |

Additional audit: PASS. All 375 rows preserve original catch order and metadata. Every exact-name and genus-union source group is retained, including multi-group source memberships.
