# Kuroshio Oyashio Extension Chen (2023)

Source-faithful extraction of available published tables is complete, with unresolved source inputs retained. This model is NOT SELECTED and is not approved for production SPPR, catch matching, annual PPR or PPR/NPP.

## Source tables and reviewed evidence

The bundle supports one 2023 model with 25 groups (23 consumers, 1 producer, 1 detritus pool). The author is Gan Chen: the source citation is Chen et al. (2025), correcting the inherited catalog author Gan et al. The printed article title is “Study in the ecosystem structure and trophodynamics in the Kuroshio-Oyashio Extension area”. Table 2 (PDF/printed p.5) contains TL, B, P/B, Q/B, EE, catch and omnivory index; no unit conversion was applied. The source's model-estimated values are recorded as bold in source_cells.json. Source catch is placed in the single Total fishery landings column because no discard split is published; it remains source catch, not verified landings-only catch. Blank catch remains unknown, not zero.

The supplement DOCX was inspected as OOXML paragraphs and all five tables. Table S2 has 25 prey rows and 23 predator columns. Exact raw cell text and table/row/column coordinates are preserved. Fifty-four cells contain '+'. The caption says '+ indicates that it occurred at a percentage <0.01'; no exact numerical value or unambiguous conversion to a proportion is supplied. These cells remain blank in import CSV and -9999 in canonical JSON, with explicit censor metadata. Numeric diet subtotals range 0.98–1.00; neither the deficit nor censored cells were filled, distributed or normalized. S1 is a parameter/diet-study source list, not authoritative group composition; Table1 in the main article is the membership evidence. S3–S5 concern pedigree/uncertainty, not separate model versions. DOCX table structure is machine-readable; no layout-dependent cell interpretation was used. LibreOffice is unavailable, so a page-rendered DOCX check was not performed.

Table 1 (PDF/printed p.3) gives main species composition for all25 groups. It is not claimed exhaustive. Source spellings are retained, including questionable Salmon membership Oncorhynchus kawamurae and the spelling Tradhypterus ishikawae. No unverified synonym repair was applied. Chub mackerel includes Scomber australasicus and S. japonicus. Group13 comma was replaced with semicolon in import/canonical name to obey the importer no-quote CSV convention; original name remains in source-cell evidence.

SPPR: the isolated bounded wrapper completed22 methods with100 draws requested for each of two MC methods and180 seconds per method. GE, TE and With Egestion all FAIL divergence diagnostics: living-network spectral radii1.31171875,1.652892561983471,1.049375 respectively, all above1. Each MC method accepted0/100 and rejected100/100 as diverged. Numerous coefficients are negative, including source groups whose catch was unreported and loader-completed to zero. All source groups and all scopes/methods are retained in all_source_group_sppr_diagnostics.csv. A computational method status of ok records successful execution, not scientific validity.

These are CONDITIONAL LOADER DIAGNOSTICS, not exact published-model results. The loader converts censored diet sentinels to0, normalizes12 consumer columns, defaults missing GS, fills missing catches, creates a diet_import group, and solves unknown flows including biomass accumulation. The resulting tiny model-balance residual only describes that completed computational model; source BA remains unknown. loader_completion_audit.csv preserves those differences. No coefficients are eligible for production or matching.

## Biomass accumulation and prose sweep

The entire available main article was searched for biomass accumulation, assimilation/egestion, immigration/emigration, discards, detritus routing and numeric steady-state statements; the2025 DOCX paragraphs and all tables were searched too. No numeric BA, GS, detritus routing or discards were recovered. The2019 article is a static mass-balanced model with a steady-state methods reference, but no group-level numerical BA is printed. The2025 equation names BA and net migration but supplies no values. These remain missing. The unavailable2019 supplement remains an explicit completeness limitation. prose_sweep.txt and full source text are retained.

## Conventions, deliberate blanks and conversion

Source strings and precision are preserved in extracted_tables/model.json, source_cells.json and diet_source_cells.json. Unknown scalar values are blank in import files and -9999 in canonical model.json. No project GS/default habitat/BA/routing convention was imposed. EwE or the calculation loader may supply0.2 GS, habitat1, catch0, import0 or BA/flow estimates; none is a source-stated value. Missing detritus fate is not a zero routing observation. The converter's normalized intermediate and log are retained for audit; converter_transformations_reversed.json lists every difference restored in canonical model.json. Reconstructed canonical XLSX and independent JSON value assertions preserve printed PB/QB/EE, all diet values and censor sentinels, all group identities and taxonomy. Source TL remains authoritative in TL.xlsx; engine TL is recomputed, not a replacement source TL.

Model number 20252023 is a local project identifier required by the importer, not an EcoBase accession. Folder name is the project candidate id. Source files remain in papers/KUR-2025; source_manifest.json records exact byte sizes and SHA256. Local diagram/page render evidence is under extracted_tables/page_evidence. Original source bytes were not modified.

## Validation

Import validator: 3 error(s), 27 warning(s). Warnings primarily flag unknown biomass accumulation and detritus routing, and source censored biomass where applicable. Diet errors reflect printed non-unit columns/censored deficits, not repaired data. Both validation and mass-balance utilities were executed; logs are retained. **Verdict: INDETERMINATE** - 0 error(s), 16 indeterminate, 1 warning(s), 2 note(s).

MASS_BALANCE_CANONICAL.md contains per-group diagnostics. Recomputed EE is conditional on missing catch/BA/migration being omitted, missing predator biomass under-counting predation where applicable, and censored diet amounts being omitted; it does not prove source balance. Missing BA was not set to the checker’s suggested closure amount. The strict scientific eligibility gate remains failed/unsupported regardless of successful JSON construction or solver completion.

## Model profile and pending choice

Axis: taxonomic/size guilds. Study area148–164°E and35–45°N, high-seas Kuroshio–Oyashio Extension; June–August2023 survey,36 sampled trawl stations of76 planned,50–150m trawl depth. Partial LME relationship; no freshly verified percentage coverage.

Central metadata registration was applied to Project.xlsx on 2026-09-28; two unselected model rows and the corresponding paper records are registered. Regional LME_049.xlsx Overview and all production results/groups remain unchanged. The next user decision is the exact model to investigate/adopt; source preference alone does not authorize selection. Missing source inputs must be resolved before source-faithful SPPR can be supported.
