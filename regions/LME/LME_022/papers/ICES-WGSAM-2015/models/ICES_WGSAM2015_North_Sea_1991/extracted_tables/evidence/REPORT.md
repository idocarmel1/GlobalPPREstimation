# North Sea 1991 — Rpath source extraction

Extracted 2026-10-14 from deposited NorthSeaModel.RData and NorthSeaModel_config.R, not an accepted native EwE database. Source hashes, version identity and departures are in [model_notes.md](../../model_notes.md). The model has 69 ecological groups, 11 fleets, 5 stanza stocks; 31 companions retain all Ecopath parameter/static-output/pedigree/stanza fields and all literal configuration vectors.

## Source tables

`Rpath.parameters$model` is the native parameter/fleet/routing table: Biomass → B, PB → P/B, QB → Q/B, EE → EE, ProdCons → P/Q, BioAcc → absolute BA, Unassim → GS, DetInput → detritus external import. Type identifies consumer/producer/detritus/fleet. Fleet `.disc` fields are discarded removals. Whole model area biomass/flows require no scaling; missing habitat area remains blank.

`Rpath.parameters$diet` has prey rows and consumer columns, followed by Import. The 65 literal consumer vectors were parsed from R c()/rep() expressions without executing R and matched to persisted values. The producer placeholder is retained in companion evidence. Standard diet/landings/discards have 69 rows; the diet has 65 consumer columns. All ecological groups occur in basic, BA, fate and TL tables.

Report Table 2.1 on printed pp. 106–109 was extracted using PDF word coordinates, with every field's rectangle in [report_basic_comparison.csv](report_basic_comparison.csv). All four table pages were rendered and visually checked, including a merged cell for group 48. Source table brackets indicate previous key-run values. Port and current accepted report parameters are materially different; source raw/persisted/solved values remain separately available.

## Biomass accumulation

Native BioAcc is explicitly zero for all 69 ecological groups; stored as absolute t/km²/year. Per-biomass BA remains blank. The whole report was checked for biomass-accumulation prose, including printed p. 171 (PDF p. 173), which explains its steady-state base-state decision. No BA was derived or solved during extraction.

## Values from prose

No port parameters were replaced with prose values. Report p. 110 documents horse-mackerel Z=0.58, while Table 2.1 gives P/B=0.9; the port's PB=0.58 is preserved and the conflict recorded. Report p. 110 gives herring K=0.42, whereas the port has K=0.46. The 2018 context paper describes 10 fleets; it was not used to overwrite this port's 11 fleets.

## Conventions applied

No numerical defaults, diet normalization, routing normalization or parameter repair was applied. Known persisted parameter cells are retained. Missing biological B, QB and EE use only directly deposited static-output estimates, with explicit roles and original unknown inputs retained in companions. No new solve was run. The name/order and whole-area units come from the port and report context; no species definitions were invented.

## Deliberate blanks

Habitat fractions, migration, unreported mortality, per-biomass BA, growth constants, prices, producer QB and detrital PB/QB remain unknown in standard fields. Unknown detritus external imports outside detritus pools remain missing. Detrital surplus Export is not supplied by the port, and is unknown. Blank EwE imports may trigger software defaults; these defaults are not source values. Native output structural zeros/turnover values are retained in companions instead of being promoted as inputs.

## Unresolved and flagged

Accepted native Keyrun 2015_NorthSea1991_12Jan16.eweaccdb remains unavailable. Material report/version differences preclude transferring ICES acceptance. Static construction does not reproduce Rpath stanza dynamics. No taxonomic membership or catch matching stage was requested. No R scripts, simulations, SPPR, model selection or map publication were run.

## Validation

The maintained structural validator reports 3 errors and 0 warnings: native zero detritus-fate rows 67–69 violate its sum-to-one check. Source values were preserved; no unsupported Export=1 or recycling was inserted. All 65 diet columns otherwise pass its tolerance; sums and exact literals are in [DIET_SOURCE_SUMS.json](DIET_SOURCE_SUMS.json) and companions. SurfaceFeedingSeabirds import=0.0654 is the sole nonzero import.

The maintained source round trip checked 127,787 cells from eight standard tables and 31 companions, including missing masks. Numeric value/missing-mask reconciliation passes; maximum workbook numeric difference 4e-15. [SOURCE_FIDELITY_CHECK.json](SOURCE_FIDELITY_CHECK.json) records the tolerances and distinguishes numeric from exact decimal equality.

## Mass balance

The maintained checker returns BALANCED, with five P/Q range warnings for mammals/seabirds (groups 1–4 and 65). All four known fields per consumer include source model estimates, whose roles are explicitly preserved; the checker does not use those provenance flags.

An independent source-valued production/pool calculation reconciles the 66 living groups and three detritus pools. Maximum living residual 1.9895196601282805e-12 t/km²/year, maximum living EE difference 3.344680088446239e-11. Maximum pool residual 6.821210263296962e-13 t/km²/year. Fleet discard returns are routed once into pool 69. Consumer respiration is positive. Full cells and operands are in [physical_living_budget.csv](physical_living_budget.csv), [physical_detritus_budget.csv](physical_detritus_budget.csv), and [physical_budget_check.json](physical_budget_check.json).

## Source load and limits

ModelData schema load succeeds, adding synthetic import group 70. Its adapter replaces unspecified non-detritus imports with zero, forces detritus self-identities and does not retain source TL in its current group DataFrame. [source_load_check.json](source_load_check.json) records field-by-field transformations. The original canonical source cells remain unchanged. No computational or annual-result readiness is established.
