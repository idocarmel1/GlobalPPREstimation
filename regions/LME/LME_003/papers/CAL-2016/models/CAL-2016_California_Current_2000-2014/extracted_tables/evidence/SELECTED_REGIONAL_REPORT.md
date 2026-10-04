# Selected California Current model: regional calculation

User selection of `CAL-2016_California_Current_2000-2014` is recorded in LME_003.xlsx / Overview. The original source canonical JSON is unchanged. Overview points to an explicitly labeled runtime JSON containing the independently checked author-equation solution for the 26 unknown biomasses and 67 EEs. The original regional workbook is archived at `models/previous_results/LME_003_before_CAL2016_selection_278954f13498.xlsx`.

## Results and scientific scope

Only full direct GE, TE and With Egestion calculations were run, with source-resolved coefficients from the same calls. All three complete reports reproduce the previously audited results at 1e-12 tolerance. All 846 group/scope/method coefficients and all raw source contributions are finite and nonnegative, including unfished groups. Each configuration remains **WARN**, retaining zero-EE and near-zero-transfer-efficiency warnings. Standard method health permits these convergent, balanced configurations; WARN is not represented as an error-free source model.

Source and loader caveats remain: GS was unreported and is supplied as 0.2 for consumers; runtime routes egestion to the sole detritus pool in addition to author unused production, sets detritus EE to 1 and appends diet import. Total source catch includes bycatch/discards without a split. The runtime does not invent a discard return or reassign observed source values. Source diet values are not normalized. Model source area is 302,000 km²; the fraction of LME_003 represented geographically has not been established.

The regional workbook now includes matching, taxon coefficients, annual PPR (1950–2019), all/inner/PP source scopes, three catch bases, three unidentified treatments, and PPR/NPP where that year's retained NPP exists. Unsupported NPP years stay blank. The 2000–2014 model is held fixed across the catch history; these are historical catch-footprint calculations, not annual reconstructions of food-web change. No Monte Carlo, broad-method export or new NPP extraction was run.

## Catch mapping and coverage

Mapped **147 of 349 taxa**; **202 remain explicit unresolved rows**. Mapped-catch coverage is **78.85%** for 1950–2019 and **76.51%** for 2019. The 95% review target is not met. Annual PPR totals are **partial mapped-catch totals**, not whole-region estimates. Use the covered_catch series and `annual_mapping_coverage.csv` alongside PPR; missing model coefficients were never replaced by zero except the explicitly requested unidentified=zero view.

Appendix B group definitions provide direct membership and higher-taxon containment. Life-stage weighting uses author model catch; zero juvenile catch concentrates weights on adults, a source selectivity convention with uncertain applicability to regional juvenile discards. Coarse taxa receive constrained candidates and constant weights from identified regional catches, filtered by higher-taxon containment where pools mix taxa. Candidate groups, exact weights and confidence are retained in catch_mapping.csv and the workbook. Broad medium-demersal unidentified/ray-finned-fish records use pooled demersal groups, excluding named commercial single stocks and pelagic groups. This is a low-confidence catch-composition projection, not observed unidentified-catch composition. It cannot resolve missing geographic information.

Key deliberate exclusions: Albacore represents T. alalunga, not yellowfin or skipjack; Pacific Mackerel is Scomber japonicus, not Trachurus; Hake is Merluccius, not pollock/cod; Salmon explicitly contains Chinook/coho, not all salmonids. Source cephalopod prose excludes large predatory jumbo squid despite a broader initial class description. Pandalid/caridean definitions do not establish penaeid membership. Unsupported ray groups are not merged into Skates. Names and reasons for every unresolved taxon remain in unresolved_taxa.json.

Scientific-name checks: NOAA Pacific Mackerel profile confirms Scomber japonicus; NOAA InPort item24030 confirms Pacific Squalus suckleyi was formerly reported as S. acanthias. WoRMS Aphia836033 confirms Magallana gigas as an oyster. Source spelling remains unchanged in archived taxonomy; these checks only support matching.

## Independent verification

Fresh regional validation passes. Independently recomputed 3,141 taxon coefficients, 17,010 annual cells and 37,800 PPR/NPP cells agree within stated floating-point tolerances. Mapping weights sum to one; every catch taxon has a decision; no basal or synthetic-import group takes catch. Original Catch, Classic PPR taxon inputs and all NPP data/provenance are unchanged. Canonical source SHA-256 is unchanged. Runtime coefficients reproduce the audited direct results. Executed scientific and workbook code snapshots and hashes are retained in selected_pipeline/code and coefficient_verification.json.

No Project.xlsx or map files were written by this worker. Central registration is prepared separately for the parent coordinator.

## Largest unresolved historical catches

| Taxon | 1950–2019 catch (tonnes) | Reason |
|---|---:|---|
| Thunnus albacares | 1,388,790 | Albacore group is specifically Thunnus alalunga; other tunas/bonitos are not documented members. Coarse scombrid labels include these unsupported taxa. |
| Katsuwonus pelamis | 1,341,770 | Albacore group is specifically Thunnus alalunga; other tunas/bonitos are not documented members. Coarse scombrid labels include these unsupported taxa. |
| Trachurus symmetricus | 1,036,154 | Pacific Mackerel group is Scomber japonicus, not Trachurus; no jack-mackerel group. |
| Gadus chalcogrammus | 742,759 | Hake group is Merluccius productus; pollock and cod are not documented there or in the source benthic-fish pool. |
| Opisthonema libertate | 579,916 | Dedicated Sardine/Anchovy/Herring groups describe named species; thread herring/anchoveta are absent. Coarse labels span these unsupported species, so a full-support split cannot be established. |
| Elasmobranchii | 462,239 | Coarse label includes non-skate rays/chimaeras beyond the documented Skates pool; complete supported partition unavailable. |
| Orthopristis reddingi | 445,241 | No source-supported adult group or complete composite candidate set for this taxon in Appendix B; source group labels are not expanded solely to raise coverage. |
| Thunnus orientalis | 362,085 | Albacore group is specifically Thunnus alalunga; other tunas/bonitos are not documented members. Coarse scombrid labels include these unsupported taxa. |
| Scombridae | 341,053 | Albacore group is specifically Thunnus alalunga; other tunas/bonitos are not documented members. Coarse scombrid labels include these unsupported taxa. |
| Penaeus californiensis | 315,209 | Pandalid and benthic-shrimp definitions name Pandalus and Crangon/caridean groups; penaeid shrimp are not documented and were not forced into them. |
| Penaeus stylirostris | 315,175 | Pandalid and benthic-shrimp definitions name Pandalus and Crangon/caridean groups; penaeid shrimp are not documented and were not forced into them. |
| Dosidicus gigas | 310,629 | Appendix B cephalopod discussion says this pool represents smaller cephalopods, not large predatory jumbo/Humboldt squid; retain the conflicting broad class definition and do not assign this species. |
| Peprilus | 298,427 | No source-supported adult group or complete composite candidate set for this taxon in Appendix B; source group labels are not expanded solely to raise coverage. |
| Cetengraulis mysticetus | 261,068 | Dedicated Sardine/Anchovy/Herring groups describe named species; thread herring/anchoveta are absent. Coarse labels span these unsupported species, so a full-support split cannot be established. |
| Paralabrax maculatofasciatus | 241,967 | No source-supported adult group or complete composite candidate set for this taxon in Appendix B; source group labels are not expanded solely to raise coverage. |
