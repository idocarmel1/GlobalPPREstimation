# Western North Pacific Watari (2013)

Source-faithful extraction of available published tables is complete, with unresolved source inputs retained. This model is NOT SELECTED and is not approved for production SPPR, catch matching, annual PPR or PPR/NPP.

## Source tables and reviewed evidence

The table prints one 2013 model with 41 groups (35 consumers, 3 producers, 3 detritus pools), not three independent regional model versions. OYC/KC/OF are linked spatial pools. Main article Table 2 (PDF p.6, printed p.299) contains B in habitat area AND B in total model area. Import CSV preserves habitat B and habitat fraction; canonical JSON uses the explicitly printed total-area B, avoiding manufacture of digits from multiplying rounded habitat values. The conversion audit preserves both representations. Table 3 is rotated in the original (PDF p.8, printed p.301): prey rows 1–41 and predator columns 1–35. Coordinate anchors retain all 1,435 printed cells, including zeros and 0.001 precision. The source sum 1.012 for Seabirds was checked visually; no correction was made. Other non-unit columns are Toothed whales 0.995, Tunas 1.002, Skipjack 1.002 and Yellowtail 1.005.

Seabird habitat and whole-model biomasses are both printed <0.01. Five landings are <0.01: Baleen whales, Toothed whales, Flatfishes (KC), Seabreams (KC), Mesopelagic fishes (KC). These are numeric missing values with the original bounds in censored_values.json, not zero or half the bound. The source's model-estimated cells are flagged by bold font in source_cells.json. Section 2.1 explicitly equates P/B and Z; both fields are retained in the import.

The supplement at https://www.int-res.com/articles/suppl/m617p295_supp.pdf was identified from printed p.297. The web reader initially exposed the 46-page supplement, including species descriptions, but exact-byte retrieval returned HTTP 401 and a publisher bot check; subsequent web fetch failed too. Browser navigation did not yield an exportable artifact. It is not represented as a locally archived or completely reviewed source. Source taxonomy therefore retains the 11 single-species groups documented in the main article and main-article definitions/spatial pools for the remaining groups; detailed pooled species membership remains incomplete. No new names were inferred from diet references.

USER-PREFERRED SOURCE: the user prefers Watari 2019 because its group structure is more detailed. Exact-model selection remains pending.

SPPR: the bounded wrapper and a retained single-model API attempt both failed on missing detritus routing for the three pools 39/40/41. This cannot be inferred from habitat fractions or prey diets. No methods or MC draws executed. All 41 source groups have an explicit unavailable diagnostic record.

## Biomass accumulation and prose sweep

The entire available main article was searched for biomass accumulation, assimilation/egestion, immigration/emigration, discards, detritus routing and numeric steady-state statements; the2025 DOCX paragraphs and all tables were searched too. No numeric BA, GS, detritus routing or discards were recovered. The2019 article is a static mass-balanced model with a steady-state methods reference, but no group-level numerical BA is printed. The2025 equation names BA and net migration but supplies no values. These remain missing. The unavailable2019 supplement remains an explicit completeness limitation. prose_sweep.txt and full source text are retained.

## Conventions, deliberate blanks and conversion

Source strings and precision are preserved in extracted_tables/model.json, source_cells.json and diet_source_cells.json. Unknown scalar values are blank in import files and -9999 in canonical model.json. No project GS/default habitat/BA/routing convention was imposed. EwE or the calculation loader may supply0.2 GS, habitat1, catch0, import0 or BA/flow estimates; none is a source-stated value. Missing detritus fate is not a zero routing observation. The converter's normalized intermediate and log are retained for audit; converter_transformations_reversed.json lists every difference restored in canonical model.json. Reconstructed canonical XLSX and independent JSON value assertions preserve printed PB/QB/EE, all diet values and censor sentinels, all group identities and taxonomy. Source TL remains authoritative in TL.xlsx; engine TL is recomputed, not a replacement source TL.

Model number 20192013 is a local project identifier required by the importer, not an EcoBase accession. Folder name is the project candidate id. Source files remain in papers/KUR-2019; source_manifest.json records exact byte sizes and SHA256. Local diagram/page render evidence is under extracted_tables/page_evidence. Original source bytes were not modified.

## Validation

Import validator: 1 error(s), 43 warning(s). Warnings primarily flag unknown biomass accumulation and detritus routing, and source censored biomass where applicable. Diet errors reflect printed non-unit columns/censored deficits, not repaired data. Both validation and mass-balance utilities were executed; logs are retained. **Verdict: INDETERMINATE** - 0 error(s), 7 indeterminate, 3 warning(s), 3 note(s).

MASS_BALANCE_CANONICAL.md contains per-group diagnostics. Recomputed EE is conditional on missing catch/BA/migration being omitted, missing predator biomass under-counting predation where applicable, and censored diet amounts being omitted; it does not prove source balance. Missing BA was not set to the checker’s suggested closure amount. The strict scientific eligibility gate remains failed/unsupported regardless of successful JSON construction or solver completion.

## Model profile and pending choice

Axis: taxonomic guilds plus spatial pools. OYC coastal Oyashio (186128 km²), KC coastal Kuroshio (186220 km²), OF offshore (540754 km²); total 913102 km². Paper assigns rounded habitat fractions0.2/0.2/0.6; multi-block groups span these pools. Regional representativeness is partial; no freshly verified percent LME coverage.

Central metadata registration was applied to Project.xlsx on 2026-09-28; two unselected model rows and the corresponding paper records are registered. Regional LME_049.xlsx Overview and all production results/groups remain unchanged. The next user decision is the exact model to investigate/adopt; source preference alone does not authorize selection. Missing source inputs must be resolved before source-faithful SPPR can be supported.
