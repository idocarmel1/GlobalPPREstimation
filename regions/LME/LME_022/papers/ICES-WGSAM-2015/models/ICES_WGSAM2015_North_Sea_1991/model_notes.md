# North Sea 1991 — published Rpath port snapshot

## Source identity

The canonical [model.json](model.json) is an Ecopath-compatible extraction of the deposited `Rpath.parameters` and `Rpath.model` in [NorthSeaModel.RData](inputs/native/rpath_port/NorthSeaModel.RData), accompanied by [NorthSeaModel_config.R](inputs/native/rpath_port/NorthSeaModel_config.R). It is a **published Rpath port snapshot; materially different from the ICES accepted native configuration**. The historical folder ID associates its source package with the report; it does not establish native Key Run equivalence or acceptance of this port.

Native source SHA-256: RData `661ac1fc2ad94c946561e37e8512560f416906265eb2df36a80ffc61107d87bc`; configuration `22a88832aa54a72512c1dd5b0a172bc60b9b184f4282e8ad63fa9b28df5ea9c9`. Source URLs and acquisition roles remain in [inputs/provenance.json](inputs/provenance.json) and the paper [source manifest](../../source_manifest.json). The stored Rpath software version is not identified; current Rpath documentation was consulted for field semantics, without claiming it reproduces the archived run.

ICES WGSAM Report 2015, Annex 6, printed pp. 102–206 is comparison evidence. Its accepted database is `Keyrun 2015_NorthSea1991_12Jan16.eweaccdb`, named in Table 4.9 on printed p. 172 and again p. 196. That native database remains unavailable. The [2018 management-plan paper](../../sources/context/Mackinson_2018_North_Sea_plan.pdf) is contextual evidence for a subsequent application, with 69 functional groups and 10 fleets; its distinct 10-fleet configuration was not substituted for the deposited 11-fleet port.

## Modeled period and area

The static Ecopath base state is **1991**. The report's temporal calibration covers 1991–2013. Area is the North Sea, ICES divisions IVa, IVb and IVc; overlap with LME_022 is not measured. Biomass and flow values are interpreted on the whole model area in t/km² and t/km²/year, with PB/QB per year. No habitat fractions or absolute area were supplied by the port: habitat cells remain missing, rather than being filled with one. No areal conversion was applied.

There are 69 ecological groups: 65 consumers, one primary producer, and three detritus pools. Eleven fleet rows in the native table are retained as fleet columns and companion evidence, rather than extra ecological groups. Five multistanza stocks link juvenile/adult cod, whiting, haddock, saithe and herring. Names and sequence are the deposited Rpath spelling, not silently replaced by the report's spaced names.

## Departures from the publication

Known deposited `Rpath.parameters$model` values were retained. Missing biological biomass (8 groups), consumer QB (11 groups), and EE (61 groups, including basal groups) were supplemented only with values already present in deposited `Rpath.model`; these carry `parameter_source_roles: model_estimated` and false importer-input flags. No new biological solve was performed. The original missing inputs, deposited estimates and retained decisions are all preserved in [Source_parameter_decisions.csv](extracted_tables/companions/Source_parameter_decisions.csv).

Rpath's prior `rpath.stanzas` call modified juvenile biomass/QB in the persisted parameter table. Those deposited parameter cells are retained as the snapshot, while exact pre-stanza configuration decimals and all stanza outputs remain in companions. For example, JuvCod biomass is `0.10018209127912465` in the persisted snapshot versus raw configuration `0.1001798`; QB is `8.011734205608454` versus raw configuration `8.01195`. This difference is source processing, not a calculation performed during this extraction. The full crosswalk documents all five stock pairs. The snapshot does not reproduce stanza transitions, recruitment or dynamic equations in the project calculator.

The coordinate-based comparison of report Table 2.1, printed pp. 106–109 (PDF pp. 108–111), found substantive version differences. Examples:

| Group / field | Report current value | Port retained value | Evidence / interpretation |
|---|---:|---:|---|
| JuvCod QB | 4.96 | 8.011734205608454 | Table 2.1 p. 106; report previous value 8.01 is bracketed. |
| AduCod QB | 2.17 | 3.5 | Table 2.1 p. 106; port equals report bracketed previous value. |
| HorseMackerel PB | 0.9 | 0.58 | Table 2.1 p. 107 differs; report p. 110 prose separately describes Z=0.58. Conflict retained. |
| JuvHerring EE | 0.89 | 0.9723237996650456 | Table 2.1 p. 107; distinct model result, not a precision restoration. |
| Herring stanza growth K | 0.42 per year | 0.46 per year | Report p. 110 prose versus config line 431 / deposited stanza table. |
| EpifaunalMacrobenthosMobileGrazers PB | 0.38 | 0.3883938 | Table 2.1 p. 108; port value preserved. |

The [complete 276-cell basic comparison](extracted_tables/evidence/report_basic_comparison.csv) distinguishes exact equality, numerical/version differences, printed missingness and unknowns. It does not classify every difference as substantive: many are display precision, while the examples above establish material non-equivalence. An unusual merged EE cell for group 48 was checked visually and explicitly located. Report brackets are prior values, not replacement input. No ICES table revision was inserted into the port.

All 4,550 consumer prey/import cells preserve exact configuration decimal literals, independently matched against deposited parameter values. Only SurfaceFeedingSeabirds has nonzero dietary import (`0.0654`). Diet sums have small source precision deviations; none were normalized or repaired. Phytoplankton's native all-zero diet column is a producer placeholder, retained in companions; it is not represented as a feeding consumer.

Unassimilated fractions are native specified inputs: `0.2` for most consumers, `0.38` for the herbivorous/omnivorous copepod group, `0.3` for both microflora groups, and `0` for phytoplankton/detritus. These are port values, not inserted EwE defaults. BioAcc is explicit absolute zero for all 69 ecological groups; the per-biomass BA column remains blank. The report printed p. 171 explains the decision to omit BA from its base state, but this does not establish complete native equivalence.

Native natural-loss routing is preserved. Detritus rows 67–69 route zero to every pool; their surplus Export fraction is not explicitly supplied and remains unknown. The generic importer validator reports **three errors** because it expects these rows to sum to one. No Export=1, self-recycling, or row normalization was invented to clear that result. Fleet discard routing is separate: every fleet routes discarded material to pool 69 `Discards` (fraction 1). All fleet routing, landings and discards remain in companions, including native NA fleet placeholders.

Detrital PB/QB, producer QB, habitat fractions, migration, unreported total mortality/other mortality, growth constants and prices remain unknown in the corresponding canonical standard fields. Rpath's output detrital turnover PB and zero basal/fleet placeholders remain in companions, without being promoted into biological inputs. No species membership was newly inferred; `taxon_descr` remains null.

All eight EwE imports and 31 companion tables were round-tripped through the maintained writer/converter. All 127,787 compared workbook cells preserve their numerical values and missing masks within the maintained tolerances; maximum numeric difference is `4e-15`. Text/literal representations remain in canonical source tables and CSV companions. This is source fidelity to the deposited port, not confirmation of the accepted native database.

The maintained physical checker returns BALANCED with five P/Q range warnings for mammals/seabirds. A separate, source-valued arithmetic check reconciles all 66 living-group production budgets and all three detritus pool budgets, including fleet discard returns counted once. Maximum living residual is `1.9895196601282805e-12` t/km²/year; maximum EE difference `3.344680088446239e-11`. Maximum detritus residual is `6.821210263296962e-13` t/km²/year. Consumer respiration is positive. These results establish a consistent deposited static snapshot, with the importer routing restriction above still active.

Read-only `ModelData` schema loading succeeds for 69 groups plus its synthetic import group. Its ephemeral adapter discards the source TL values into NaN, supplies zero detritus import for unspecified non-detritus cells, and forces detritus self-identities. The current source loader also hardcodes LME=13 despite the source metadata identifying LME_022; its metadata observation is recorded, without project adoption. A [field-by-field source-load ledger](extracted_tables/evidence/source_load_check.json) records these departures. The canonical values are unchanged. No PPRCalculator, Ecosim, R script or SPPR method was executed, and no numerical readiness or researcher approval is claimed.

## Evidence links

[Extraction report](extracted_tables/evidence/REPORT.md), [checks](extracted_tables/evidence/extraction_check.json), [source round trip](extracted_tables/evidence/source_roundtrip.xlsx), [physical budgets](extracted_tables/evidence/physical_budget_check.json), [diet evidence](extracted_tables/companions/Source_diet_cells.csv), [evidence inventory](extracted_tables/evidence/evidence_index.json), and [group profile](extracted_tables/MODEL_PROFILE.md).

No regional selection, workbook, catalogue or map publication was changed. Creation of a canonical source snapshot does not transfer another model's results or any researcher/native Key Run acceptance.
