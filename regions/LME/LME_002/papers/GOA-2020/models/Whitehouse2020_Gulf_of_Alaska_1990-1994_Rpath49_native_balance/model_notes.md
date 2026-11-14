# Gulf of Alaska Rpath49 — native balance computational variant

## Source identity

Whitehouse & Aydin (2020), DOI 10.1016/j.ecolmodel.2020.109074. Official NOAA-EDAB/Rpath Ecosense.GOA inputs at commit fe63f6d370d942ff1786f4d649e432fbfb85f81b. The [raw parameter extraction](../Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49/model_notes.md) remains a separate model. This variant records the native-equation completion, not new observations.

## Modeled period and area

The baseline is 1990–1994 and covers 291,840 km² of Gulf of Alaska shelf and slope. Nearshore waters shallower than 50 m were excluded. Coverage of the complete LME has not been measured. The publication year is not the ecosystem baseline year.

## Departures from the publication

Unmodified, pinned Rpath equations solved 49 EE values, two detritus biomasses and trophic levels, and calculated GE. Native NA-diet-to-zero and missing-detritus-input-to-zero conventions and nonfeeding QB zero placeholders are explicit in the ledger. Known parameters, BA, catch, group identities and fate fractions were preserved without diet normalization, parameter fitting or balancing repair. The comma-free import alias for group 31 is reversible; the canonical name is exact. Raw inputs and missingness remain in the parent model and retained companions.

## Native balance and PPR outcomes

The native system has full rank and all 49 EE values lie between zero and one. The maximum absolute living-group balance residual is 5.68434e-14 t/km²/year. The archived RDA model, diet and pedigree exactly match the CSV reader objects. Independent native and variant verification passed 9,485 checks.

The GE, TE and With Egestion direct PPR diagnostics all returned **FAIL**, reproduced from the persisted variant. Their production-budget gaps are 100.5891%, 75.6690% and 100.4364%, respectively. The current PPR runtime forces detritus EE to one while the native solution leaves unused detritus inputs. The saved-output decomposition accounts for each entire budget gap using those two residuals. Native balance success does not establish PPR validity.

All raw source EE values were unknown. The EE-floor setting was ON at 0.1, with source missingness preserved: zero groups were modified and no external mortality sink was added. Known detritus BA values of zero were preserved. No parameters were repaired to make diagnostics pass.

## Remaining limitations

The PPR translation needs an explicit, source-consistent treatment of native detritus non-consumption before the coefficients can support an accepted annual estimate. GE and TE also warn about near-zero efficiencies; TE produces an especially large coefficient for toothed whales. An accounting correction alone would not establish ecological validity.

The single Primary production group combines local and Outside production; the detritus pools combine external production and fishery returns. Engine labels inner and PP do not recover a geographic partition. These diagnostic outputs cannot establish LME-local PPR/NPP. Candidate taxonomy still needs source review, catch mapping has not been adopted, and current-year extrapolation and study/LME overlap remain unresolved.

## Evidence links

- [Results and accounting interpretation](results/diagnostics/DIAGNOSTIC_INTERPRETATION.md)
- [Full direct diagnostic returns](results/diagnostics/direct_diagnostics.md)
- [Native reproduction](extracted_tables/evidence/native_reproduction/)
- [Native-to-variant ledger](extracted_tables/evidence/native_to_variant_ledger.json)
- [Import round trip](extracted_tables/evidence/SOURCE_FIDELITY_CHECK.json)
- [Portable evidence index](extracted_tables/evidence/evidence_index.json)
- [Reproduction instructions](results/diagnostics/REPRODUCE.md)

The map, regional workbook, model selection and researcher approval were not changed. No annual regional PPR was calculated.
