# Griffiths2019 Warm Pool model 2005

Source: Griffiths et al. (2019), DOI 10.1111/fog.12389. Main Table 1, printed pp98–99; Appendix S1 Tables S1, final S3 pp29–30 and S4 p31. The user supplied the exact original Word supplement on 28 September 2026. Its SHA-256 is `57e279d21458a7e56011ae706a30f210d5c4d6580d211a8e767292e4c52f5d35`. It is archived unchanged under the regional paper folder. Prior inaccessible-source findings remain in source_review/history_before_supplement.

The source-supported extraction is now complete, including eight imports, taxonomy, a source-preserving canonical JSON and reconstructed workbook. **Numerical source inconsistencies and missing routing prevent model admission.** Extraction completion does not mean all required values were published or that the model balances. No model was selected.

## Source tables and verification

- Main Table 1: 46 groups in printed order, 42 consumers, 2 phytoplankton producers, 2 non-living pools. B is t wet weight/km²; PB and QB are annual rates, EE and PQ dimensionless. Printed dashes remain unknown/not applicable. Exact strings and bold estimated-value provenance are preserved. Six table cells per row give 266 numeric values plus 10 dashes.
- Supplement final S3: Word XML tables 4 and 5. These are 46 prey rows by consumer columns 1–19 and 20–42. All 1,932 positions are preserved, including 567 nonzero values. The initial S2 matrices (XML tables 2–3) are not used. Empty displayed diet cells are structural absent links; no nonzero proportion was altered. Published column sums span 0.99952–1.00047; no normalization was performed. The writer's Import and residual rows use its zero formatting convention; diet imports are unreported and remain -9999 in the canonical JSON.
- Supplement S4: XML table 6. Columns 2–5 in zero-based indexing hold LL/PSA/PSU/PL landings; 8–11 hold their discards. Both headers specify 1e-6 t/km². Each value is multiplied by exactly 0.000001 once. Printed totals are retained separately from the sum of fleet entries. Catches are not divided by area again.
- The original DOCX was exported read-only through Word to a 68-page PDF. Final diets pp29–30 and catches p31 were visually inspected. Every one of the 567 nonzero diet cells and 172 nonblank catch cells, including printed totals, independently matched the rendered PDF's word coordinates. POST_SUPPLEMENT_VERIFICATION.json and the cell evidence record this check.
- Source group aliases such as Turtles/Sea turtles, White tip shark/Oceanic whitetip shark, and Escolar/Oilfish are aligned by explicit group number. Main Table 1 names remain canonical.

## Biomass accumulation and migration

Appendix S1 p4 explicitly sets BA=0 in the current model and net migration=0. Zero BA is written for every source group. Gross immigration and emigration separately remain unknown; net migration is recorded as its own source field and copied explicitly into the model-data admission probe. No residual was absorbed into artificial BA.

## Taxonomy and structure

Taxonomy.xlsx has seq, group_name, taxon_descr and all 46 rows. Table S1's actual membership cells, age classes and source spelling are retained in TAXONOMY_EVIDENCE.json. Named species lists are identified as source membership. For coarse forage/plankton groups with no detailed membership list, the source label and absence of a detailed definition are recorded. Species from borrowed diet studies are not silently promoted into exhaustive group composition. Misspellings in the source, such as Katsuwonis, are preserved with an explicit spelling note; no unverified synonym resolution is claimed.

The model mixes taxonomic groups, life stages and vertical habitats. Swordfish, bigeye, yellowfin and skipjack are multistanza groups in the source. Main p99 notes adjustments needed to reconcile stock-assessment estimates with stanza calculations. These printed standalone group parameters do not encode all native stanza settings.

## Missing values and converter/loader behavior

No numerical unassimilated-consumption/GS values, detritus-fate matrix, quantitative fleet-discard return fractions/destinations, detritus imports or habitat-area fractions were found in the main paper and complete supplement. These remain blank in imports and -9999 where applicable in canonical JSON. Software defaults are not relabeled as source data. The converter output is retained unchanged; converter_to_canonical_audit.json records all source-restoring changes, including restored printed PQ/TL/precision and removal of unsupported default fields.

The main paper p99 gives a distinct suspended Fishery discards pool to make discarded material available to predators, and Table S1 derives its initial biomass from discards. That supports the pool's meaning and intended fishery association. It does not quantify the allocation of every group's natural M0 and egestion across Detritus and Fishery discards, the treatment of unused material, or native fishery-return controls. A diet link from pool 46 is consumption of discards, not a detritus-fate allocation.

There are two separate issues: (1) source numerical routing is missing; (2) the current engine's detritus-fate matrix routes natural M0+egestion, while its export/catch field records retained plus discarded removals and has no separate fleet-return pathway. Setting natural fate to 45 and fleet discards to 46 would therefore require an explicitly documented representation of both processes. It cannot be repaired merely by guessing a two-column fate row, counting fishery discards as natural mortality, adding an external import, or pooling the two source pools.

ModelData maps unknown fate entries to zero and sets detritus self-links to identity. It defaults a fully missing living fate matrix only for a single-detritus model. For this two-pool model it correctly leaves the unknown split unresolved. Both the strict-source and standard-default-GS admission attempts raise the same ValueError: `det_fate carries no detritus routing for any living group. For a multi-DET model the per-pool split cannot be inferred -- supply DetritusFate data for model with detritus groups [45, 46].` Frozen engine code, hashes, settings and attempts are in diagnostics. No engine changes were made.

## Published inconsistencies

S4 contains 22 disagreements between its printed Total columns and the sum of explicit fleet entries. The import writer calculates sums from the preserved fleet entries. The independent source audit also calculates the production equation using the published Total alternative, without creating or adopting a repaired model. Two examples, in the table's 1e-6 units: small bigeye landings sum 631.834 versus printed 2431.834; large bigeye sum 498.591 versus printed 57.591. The conflicts are source contents verified in the rendered page.

Main paper ocean area is 11,543,000km². S1 catch derivations repeatedly use 12,086,900km², while the initial Fishery discards biomass derivation uses 12,555,000km². Other input derivations average different SEAPODYM extents. These differing provenance areas are recorded; no printed final density was rescaled. Main Table 1's final values take precedence over S1 descriptions of initial parameter estimates.

## Validation and source production balance

validate.py: 0 errors and 47 warnings (blank GS plus 46 unreported fate rows). massbalance_check.py: 2 errors, 14 warnings, 43 notes. The converter/reconstructed workbook completed, but this does not resolve missing source values. Canonical nonzero diets, B/PB/QB/EE, taxonomy and stated BA/net migration were checked against the extraction; source dashes and unknowns remain intact.

Independent production balance uses `B*PB*EE = predation + retained catch + discarded catch + BA + net migration`, with the unnormalized published S3 and explicit zero BA/migration. It does not require GS or detritus routing. It fails strongly for Pomfret: B=0.000302, PB=0.976, EE=0.950 give production 0.000294752 and utilized production 0.0002800144 t/km²/year; published predators consume 0.02128530003, and fleet catch removal adds 0.000004849. The resulting residual is 0.02101013463, or 7128.07195% of production; required EE would be 72.23071949. Large yellowfin alone consumes 0.004190*9.406*0.14900 = 0.00587225986 of Pomfret, about 19.92 times Pomfret's entire printed production. These exact cells were cross-checked visually and by coordinates. Replacing fleet sums with printed Total values does not materially change this mismatch.

Migratory mesopelagic molluscs also require EE slightly above 1 (about 1.005). Other rows show material used-production residuals, including small bigeye, dolphinfish and large yellowfin. Detailed exact values are in SOURCE_PRODUCTION_BALANCE.json/.csv. Suggested BA/EE corrections from generic checkers were not used. The evidence establishes inconsistency between the published tables under the stated production equation; it does not establish which native model value or version is correct.

## Direct SPPR status

GE, TE and With Egestion are **NOT_RUN_LOADER_BLOCKED**. There are no direct diagnostic returns for Griffiths2019 to display, and no global call was made. This differs from a returned SPPR FAIL. The separate source production-equation failure is nevertheless substantive evidence against admitting the current reconstruction. CALL_OUTCOMES.json reports the missing calls; LOAD_ATTEMPTS.json preserves the actual exception. No narrative has been substituted for a direct return.

To proceed scientifically, obtain the final native model or author-supported corrections that resolve Table1 versus final S3 and S4, plus detritus/fishery-return routing and GS/import settings. No authors were contacted, no source repair was applied, and no production model or annual PPR was published.
