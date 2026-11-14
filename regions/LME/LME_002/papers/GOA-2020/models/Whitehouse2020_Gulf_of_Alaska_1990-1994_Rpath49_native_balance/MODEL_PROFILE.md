# Gulf of Alaska official Rpath aggregate (1990–1994)

**Model:** `Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49`. **Source:** Whitehouse, G.A. and Aydin, K.Y. (2020). Assessing the sensitivity of three Alaska marine food webs to perturbations: an example of Ecosim simulations using Rpath. Ecological Modelling 429, 109074. https://doi.org/10.1016/j.ecolmodel.2020.109074

**Structure:** Mixed taxonomic and functional/guild aggregation: marine mammals and seabirds; fish taxa and feeding/habitat guilds; pelagic and benthic invertebrates; microbes; primary production and detrital pools. Native types are 46 consumers (Type 0), one producer (Type 1), two detritus pools (Type 2) and one separate fleet (Type 3). The native group names and type codes below are exact. Ecological labels are source group labels, not new membership rules.

**Life stage and size:** Native `Salmon returning` and `Salmon outgoing` remain separate. Juvenile/adult pollock and cod, and several other original juvenile/adult groups, are combined in the 2020 Table 1 aggregate. The official Ecosense.GOA documentation explicitly states **no stanzas**. Numeric age, length or size cutoffs are not supplied by the inspected aggregate parameter files. `Lg.-mouth` and `Sm.-mouth` are source functional labels, not numerical length boundaries.

**Spatial prefixes:** None in the native 49-group labels. The documentation's “west/central” title describes the model context; it does not assign separate spatial strata to the native groups. Original west/central Steller sea-lion groups are not separately retained. No allocation between geographic pools is inferred.

**Period and area:** The 1990s source documentation inherits the original Aydin et al. 2007 base period, 1990–1994. Publication in 2020 is distinct from that base period. The 2020 article §2.2.3 (p.4) reports shelf waters from 140°W to 170°W and **291,840 km²**. Biomass and annual flow inputs are standardized to the whole modeled area. Relation to the current LME catch boundary and coverage percentage remains unmeasured; no equality with the entire LME catch unit is assumed.

**Single named stocks and pools:** `Gray whale`, `Walleye pollock` and `Pacific cod` are named taxa/stock groups. Labels such as `Toothed whales`, `Other pinnipeds`, `Pelagic forage fish`, `Other demersals`, `Other crabs` and `Other zooplankton` identify aggregated pools. Primary production combines the source production compartments; pelagic and benthic detritus combine source detrital compartments. The Table 1 membership companion records the source group constituents; it does not resolve every species or every original model version.

**Catch:** One source fleet, `Fishery/Subsistence`. Landings and discards are retained for all 49 biological rows. The list below records positive native removals only; zero catch is not a biological exclusion rule, and no regional catch assignment has been made.

Positive native removals: Toothed whales; Gray whale; Other baleen; Other pinnipeds; Procellarids; Alcids piscivorous; Larids; Alcids planktivorous; Other seabirds; Cormorants; Sharks; Walleye pollock; Pacific cod; Pelagic forage fish; Lg.-mouth flatfish; Sm.-mouth flatfish; Skates; Other demersals; Eelpouts; Lg.-mouth sculpins; Misc. shallow fish; Octopods; Squid; Salmon returning; Other crabs; Shrimps; Sea stars; Urchins, dollars, cucumbers; Snails; Anemones; Corals and sea pens; Benthic urochordate; Sponge; Bivalves; Scyphozoid jellies.

**Lineage caveat:** The official repository, pinned at `fe63f6d370d942ff1786f4d649e432fbfb85f81b`, identifies Ecosense.GOA as an aggregate of Aydin et al. (2007). The 2020 paper says the original GOA model had 138 groups, whereas the separate published Appendix C extraction contains 133 biological compartments. These counts do not establish a bijection or exact native-version equivalence. The Table 1 wording also does not resolve all west/central Steller sea-lion subdivisions. No native data from a different CGOA/EBS model was substituted.

**Candidate taxonomy and authority:** [Taxonomy.xlsx](extracted_tables/Taxonomy.xlsx) contains exactly `seq`, `group_name`, `taxon_descr`, with one row for every native biological group. Descriptions retain only Table 1's original functional-group membership. They are not an exhaustive scientific-name list. PDF visual verification and taxonomic-authority reconciliation are **pending**; no accepted names, synonym replacements or authority identifiers have been invented. [Candidate evidence](extracted_tables/evidence/candidate_taxonomy_evidence.json) records these limits per group. Canonical `taxon_descr` remains null for all 49 groups and the canonical hash is unchanged; this candidate workbook has not been applied to the model.

**Naming:** The candidate workbook uses exact native names, including group 31 `Urchins, dollars, cucumbers`. The strict eight imports use the documented representation-only alias `Urchins dollars cucumbers`. Any later authorized taxonomy import must use the [label crosswalk](extracted_tables/companions/Group_label_crosswalk.csv); no unreviewed converter rerun is implied.

**Evidence:** [Native provenance](inputs/provenance.json); [Table 1 membership](extracted_tables/companions/Aggregation_membership_Table1.csv); [candidate workbook checks](extracted_tables/evidence/candidate_taxonomy_check.json); [extraction report](extracted_tables/evidence/REPORT.md). The candidate workbook has a separate shape/content verification and is not part of the original eight-import reconstruction count.

| Native group ID | Exact native name | Native type |
| --- | --- | --- |
| 1 | Toothed whales | 0 |
| 2 | Gray whale | 0 |
| 3 | Other baleen | 0 |
| 4 | Other pinnipeds | 0 |
| 5 | Procellarids | 0 |
| 6 | Alcids piscivorous | 0 |
| 7 | Larids | 0 |
| 8 | Alcids planktivorous | 0 |
| 9 | Other seabirds | 0 |
| 10 | Cormorants | 0 |
| 11 | Sharks | 0 |
| 12 | Walleye pollock | 0 |
| 13 | Pacific cod | 0 |
| 14 | Pelagic forage fish | 0 |
| 15 | Lg.-mouth flatfish | 0 |
| 16 | Sm.-mouth flatfish | 0 |
| 17 | Skates | 0 |
| 18 | Other demersals | 0 |
| 19 | Eelpouts | 0 |
| 20 | Lg.-mouth sculpins | 0 |
| 21 | Other sculpins | 0 |
| 22 | Misc. shallow fish | 0 |
| 23 | Octopods | 0 |
| 24 | Squid | 0 |
| 25 | Salmon returning | 0 |
| 26 | Salmon outgoing | 0 |
| 27 | Other crabs | 0 |
| 28 | Shrimps | 0 |
| 29 | Sea stars | 0 |
| 30 | Brittle stars | 0 |
| 31 | Urchins, dollars, cucumbers | 0 |
| 32 | Snails | 0 |
| 33 | Misc. crustaceans | 0 |
| 34 | Benthic amphipods | 0 |
| 35 | Anemones | 0 |
| 36 | Corals and sea pens | 0 |
| 37 | Worms etc. | 0 |
| 38 | Benthic urochordate | 0 |
| 39 | Sponge | 0 |
| 40 | Bivalves | 0 |
| 41 | Polychaetes | 0 |
| 42 | Scyphozoid jellies | 0 |
| 43 | Other zooplankton | 0 |
| 44 | Copepods | 0 |
| 45 | Pelagic microbes | 0 |
| 46 | Benthic microbes | 0 |
| 47 | Primary production | 1 |
| 48 | Pelagic detritus | 2 |
| 49 | Benthic detritus | 2 |
| 50 (fleet only) | Fishery/Subsistence | 3 |
