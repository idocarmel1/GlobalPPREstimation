"""Publish current source findings and comparison; leave regional selection untouched."""
from pathlib import Path
import json,hashlib,shutil,re
from decimal import Decimal as D
import openpyxl
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
MID='941_201901_Warm_Pool_(2005)';M=ROOT/'regions/EEZ_941/models'/MID;R=M/'source_review';T=M/'extracted_tables';DIAG=M/'diagnostics'
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source=json.loads((R/'FINAL_EXTRACTION.json').read_text(encoding='utf-8'))
summary=json.loads((R/'EXTRACTION_SUMMARY.json').read_text())
balance=json.loads((T/'SOURCE_PRODUCTION_BALANCE.json').read_text())
conflicts=[x for x in json.loads((R/'SOURCE_CATCH_TOTAL_AUDIT.json').read_text()) if x['difference_fleet_minus_printed'] and D(x['difference_fleet_minus_printed'])!=0]
totalcatch=sum((D(v) for kind in ['landings','discards'] for row in source[kind].values() for v in row.values()),D(0))
benchmark=ROOT/'regions/EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)/balance_investigation/correction_scenarios'
hashes={};raw_results={}
for option in ['GE','TE','With Egestion']:
    f=benchmark/'D_fixed_M0'/('diagnose_'+option.replace(' ','_')+'.json')
    r=json.loads(f.read_text());assert r['status']=='WARN'
    hashes[f.relative_to(ROOT).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest();raw_results[option]=r
dump(DIAG/'WCP_OPTION1_REFERENCE.json',{'scenario':'D_fixed_M0','experimental_not_adopted':True,'reused_without_rerun':True,'raw_return_hashes':hashes})
# Raw saved diagnostic returns only; explanation belongs in comparison, not this JSON.
dump(BASE/'WCP_OPTION1_SAVED_DIRECT_DIAGNOSTICS.json',raw_results)

report='''# Griffiths2019 Warm Pool model 2005

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
'''
(T/'REPORT.md').write_text(report,encoding='utf-8')
(M/'MODEL_PROFILE.md').write_text('''# Warm Pool 2005 structural profile

Mixed taxonomic, life-stage and vertical-habitat model: 46 source groups; 42 consumers, 2 phytoplankton producers, Detritus and Fishery discards. Main Table1 names/order are canonical. Migratory mesopelagic and bathypelagic prefixes describe vertical habitat behavior, not regional subareas. Swordfish, bigeye, yellowfin and skipjack stages belong to native multistanza populations; independent source rows do not reproduce full stanza links.

Study limits are 140–180E and15S–10N; reported ocean area11,543,000km². It is a broad mixed-jurisdiction pelagic proxy, with no separately resolved reef/coastal web. Catch allocations must respect life-stage definitions and source-supported memberships; overlapping life-stage groups do not justify arbitrary regional weights. Main/Supplement area and catch inconsistencies are documented in extracted_tables/REPORT.md. No model is selected.
''',encoding='utf-8')
status={'status':'EXTRACTED_SOURCE_INCONSISTENT_AND_ROUTING_BLOCKED','supplement_access_blocker_resolved':True,
        'eight_imports':'created with deliberate source unknowns','canonical_json':'created; source unknowns preserved','reconstruction':'created and checked',
        'source_mass_balance':'FAIL','diagnostic_status':'NOT_RUN_LOADER_BLOCKED','diagnostic_results':None,
        'requested_methods':['GE','TE','With Egestion'],'global_excluded':True,
        'remaining_blockers':['Unknown two-pool detritus-fate routing and explicit fleet-discard return representation','Unreported GS/import values','Severe Table1/S3 production inconsistency (Pomfret)','22 S4 printed-total versus fleet-sum conflicts'],
        'history':'history_before_supplement','report':'../extracted_tables/REPORT.md'}
dump(R/'ADMISSION_STATUS.json',status)
(R/'SOURCE_ADMISSION.md').write_text('# Current source admission\n\nThe user-supplied supplement resolves the earlier retrieval blocker. The eight-file source extraction, taxonomy, canonical JSON and reconstructed workbook are now present. Source balance fails and exact loader attempts stop on unreported routing for detritus groups45 and46. GE/TE/With Egestion remain not run. See ../extracted_tables/REPORT.md and ../diagnostics/LOAD_ATTEMPTS.json. The previous blocked reports are retained in history_before_supplement.\n',encoding='utf-8')

comparison='''# Griffiths2019 versus WCP2007 option 1

**The new supplement does not currently make Griffiths2019 a stronger runnable candidate than WCP2007 option 1.** Its final tables have now been extracted and independently verified, but reveal substantial source balance inconsistencies and omit numerical routing for its two non-living pools. Option 1 is specifically the existing experimental **D_fixed_M0** scenario, not A_fixed_EE and not the unchanged WCP2007 source. It returns WARN for all three requested methods; it is not an adopted or native-validated correction.

| Criterion | Griffiths2019 source reconstruction | WCP2007 option1: D_fixed_M0 |
|---|---|---|
| Source structure | 46 groups, baseline2005, 2 detritus pools | 31 groups, mixed-period source, single detritus pool |
| Extraction | Eight imports, taxonomy, canonical JSON and reconstruction created; unknowns preserved | Existing extraction plus isolated experimental juvenile correction |
| Diet transcription | All567 nonzero final S3 cells match DOCX grid and rendered PDF coordinates | Existing verified source; computational loader normalizes rounded diets |
| GE | Not run: loader routing block | WARN; PP budget OK |
| TE | Not run: loader routing block | WARN; PP budget OK |
| With Egestion | Not run: loader routing block | WARN; PP budget OK |
| Main numerical concern | Pomfret used-production residual7128.07195% of production; catch-total conflicts | Remaining maximum production residual0.727940%, adult bigeye |
| Scientific limitation | Missing native routing/GS/return settings and inconsistent published tables | Hypothetical independent-group repair; native multistanza consistency unverified |

The percentages above concern distinct evidence: Griffiths is an independent check of the exact source production equation, whereas WCP's value is the returned diagnostic on the existing loaded experimental model. Griffiths is not being assigned a fabricated diagnostic FAIL or WARN.

## What the supplied supplement changed

The exact4,115,453-byte DOCX is archived. Its final S3 is46 prey rows ×42 consumer columns, with567 nonzero cells; initial S2 is excluded. S4 fleet values and totals were cross-checked against a68-page Word-rendered PDF. Every nonzero diet and every nonblank catch/total matched. The earlier retrieval-only block is historical, not the current explanation.

Source-faithful imports preserve exact fleet cells, scaled once by1e-6, and computed fleet sums. Twenty-two printed Total cells disagree with their fleets. For example, small bigeye landings sum631.834 versus printed2431.834; large bigeye sum498.591 versus printed57.591, in the printed1e-6 units. Both alternatives are retained in the audit, with no model repair. Areas also differ between main-paper domain and several input derivations; no density was silently rescaled.

Pomfret is the clearest balance contradiction. Table1 gives P=0.000294752 and P×EE=0.0002800144 t/km²/year. S3 yields predation0.02128530003 before catch. Large yellowfin alone consumes0.00587225986—about19.92 times the printed Pomfret production. This persists with either catch-total convention and cannot be explained by the small diet-rounding error. The source does not identify which value/native version is wrong.

Two admission attempts, retaining the source diet and testing both strict GS and ordinary GS-default behavior, stop at the same documented multi-detritus error. Missing natural M0/egestion routing and the separate fleet-discard-return representation are distinct issues. The qualitative suspended-discard-pool description does not supply the needed numerical matrix. Neither pooling nor guessed routing was used to force a run.

## Exact benchmark identity and evidence

WCP option1 preserves the original juvenile other-mortality flow M0 while increasing production: small bigeye PB1.4129713563375232 / EE0.7898725981469387; small yellowfin PB2.5304972811160384 / EE0.8816702937266387. Existing B, QB, diet and catch are unchanged by that scenario. It is an experimental explanation of missing fishing turnover, not a recovered source correction. Other loader-completed flows and remaining discrepancies are retained.

The saved D_fixed_M0 diagnostics were reused without rerunning. Their PP budget gaps are GE0.097858%, TE0.134701%, With Egestion0.024524%; each budget check is OK. All solves converge with zero negative source columns, but the remaining adult-bigeye production residual and method warnings keep overall status at WARN. The original unmodified WCP2007 returns FAIL and must not be mislabeled as this option.

`WCP_OPTION1_SAVED_DIRECT_DIAGNOSTICS.json` contains only the full saved three direct diagnostic returns. Original paths and SHA-256 values are recorded in the Griffiths diagnostics/WCP_OPTION1_REFERENCE.json. Griffiths has no direct return because construction stops before diagnose_sppr. Its LOAD_ATTEMPTS.json and CALL_OUTCOMES.json explicitly say so. No global or annual-PPR computation was made.

## Regional applicability and choice implications

| Region | Griffiths2019 target coverage | WCP2007 target coverage |
|---|---:|---:|
| HS_071 |29.09639%|57.57808%|
| EEZ_941 Kiribati Gilbert Islands |99.71577%|99.71577%|
| EEZ_598 Papua New Guinea |99.79181%|100.00000%|

These figures use the actual stored regional polygons and explicit source study rectangles, with WGS84 geodesic intersection. The parent independently added EEZ_598 to SPATIAL_OVERLAP.json. WCP-2007 is already shared with EEZ_598. The existing EEZ_941 archive home is retained; it was chosen in the earlier two-region comparison and does not exclude applicability review for Papua New Guinea.

For HS_071, WCP2007 covers substantially more of the target than Griffiths2019, although neither represents all of it. For both EEZs, geographic coverage is similarly high, so present numerical consistency and ecological scope carry more weight. Griffiths remains a broad pelagic proxy: only9.07086% of its reported ocean model area falls in EEZ_941 and20.73849% in EEZ_598. Neither source fully resolves each EEZ's coastal/reef fisheries.

If choosing a **working sensitivity scenario today**, the evidence favors retaining WCP option1 D_fixed_M0 for further scrutiny over replacing it with the currently inconsistent Griffiths reconstruction. That recommendation is conditional: D is still an unvalidated experimental correction and is not selected or published by this review. For a source-faithful production choice, obtain the original native model or author-supported corrections before adopting either repaired option. Do not rank these studies by total PPR: their domains, periods, source catches and group structures differ, and Griffiths has no valid diagnostic footprint to compare.

Allain2021 remains a separate65-group2013 model whose complete retrieved four-page report lacks the numerical input set. Its previous source review remains applicable. It was not substituted for either model.
'''
(BASE/'GRIFFITHS_VS_WCP_OPTION1.md').write_text(comparison,encoding='utf-8')
(BASE/'PACIFIC_PAPER_COMPARISON.md').write_text('# Current Pacific candidate review\n\nThe user-supplied Griffiths supplement has now been extracted. Current results and the requested comparison to WCP2007 option1 D_fixed_M0 are in [GRIFFITHS_VS_WCP_OPTION1.md](GRIFFITHS_VS_WCP_OPTION1.md). Griffiths has source production inconsistencies and remains blocked at two-pool routing; WCP option1 has existing WARN returns. No model is selected.\n\nAllain2021 remains archived under EEZ_941 with verified2013/65-group identity and missing final numerical inputs. Its target coverage remains74.48550% of HS_071 and100% of EEZ_941. No Allain2021 diagnostics were run. The previous full two-paper comparison and source-access block are preserved in the Griffiths source_review/history_before_supplement. Current shared WCP2007 applicability to EEZ_598 is included in the new comparison using the parent’s verified spatial result.\n',encoding='utf-8')

meta_path=ROOT/'regions/EEZ_941/papers/Griffiths-2019/metadata.json';meta=json.loads(meta_path.read_text(encoding='utf-8'))
sup=json.loads((R/'SUPPLEMENT_SOURCE.json').read_text())
meta.update(supplement_status='downloaded_verified_user_supplied',extraction_readiness='source_extracted_with_unknowns',full_model_loadable='Blocked by unreported two-pool routing; source production equation also fails',diagnostic_status='NOT_RUN_LOADER_BLOCKED',blockers=status['remaining_blockers'],canonical_model_path=(M/'model.json').relative_to(ROOT).as_posix())
meta['material_files']=[m for m in meta.get('material_files',[]) if m.get('role')!='supplement']+[{'relative_path':sup['archive'].replace('\\','/'),'role':'supplement','sha256':sup['sha256'],'size_bytes':sup['size_bytes'],'status':'user_supplied_verified','provenance':sup['provenance']}]
meta['later_selection_context']='Review HS_071, EEZ_941 and EEZ_598 jointly. WCP-2007 shared with EEZ_598; actual EEZ_598 spatial comparison now verified by parent. No selection authorized.'
dump(meta_path,meta)
(meta_path.parent/'README.md').write_text('# Griffiths et al.2019 Just a FAD\n\nMain paper and user-supplied original Word supplement are archived with hashes in metadata.json. The source-faithful extraction now includes final S3 diets and S4 fleet catch, taxonomy, eight imports and canonical/reconstructed files. Source production balance fails and diagnostics are blocked by unreported two-pool routing. See the model extracted_tables/REPORT.md and shared GRIFFITHS_VS_WCP_OPTION1.md. No model is selected.\n',encoding='utf-8')
proposal=json.loads((BASE/'REGISTRATION_PROPOSAL.json').read_text(encoding='utf-8'))
proposal['records']=[meta if r['paper_id']=='Griffiths-2019' else r for r in proposal['records']]
proposal['status']='updated_source_extraction_and_diagnostic_admission_metadata_for_parent';dump(BASE/'REGISTRATION_PROPOSAL.json',proposal)
dump(BASE/'PROGRESS_STATUS.json',{'as_of':'2026-09-28','stage':'supplement_extraction_and_comparison_complete_with_exact_admission_block',
    'Griffiths2019':status,'WCP_option1':'D_fixed_M0 existing direct results WARN for GE/TE/With Egestion; not adopted',
    'next_evidence':'Native final model or corrected source tables plus detritus/fishery-return routing and GS/imports','central_workbook_writes':False})
(BASE/'MASTER_INDEX.md').write_text('| Model | Baseline | Groups | Extraction | Scientific admission |\n|---|---|---:|---|---|\n| Griffiths2019 Warm Pool |2005|46|Eight imports, taxonomy, canonical JSON, roundtrip; unknowns retained|Blocked: source production failure and missing two-pool routing|\n| Allain2021 Western Tropical Pacific |2013|65|No full numerical input set in retrieved publication|Not run; final inputs required|\n| WCP2007 option1 D_fixed_M0 |mixed source periods|31|Existing experimental correction, reused|WARN all three; not adopted or native-validated|\n',encoding='utf-8')
# Verify the reconstructed workbook exists and retains 46 row identities in its basic sheet.
wb=openpyxl.load_workbook(T/'CANONICAL_reconstructed.xlsx',read_only=True,data_only=True)
sheet_stats={s.title:[s.max_row,s.max_column] for s in wb};wb.close()
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for base in [T,R,DIAG] for p in base.rglob('*') if p.is_file() and 'history_before_supplement' not in p.parts}
manifest[(M/'model.json').relative_to(ROOT).as_posix()]=hashlib.sha256((M/'model.json').read_bytes()).hexdigest()
dump(M/'artifact_manifest.json',manifest)
dump(BASE/'POST_SUPPLEMENT_FINAL_VERIFICATION.json',{'canonical_sha256':summary['canonical_sha256'],'eight_imports_present':all((T/n).is_file() for n in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx']),
    'reconstruction_sheets':sheet_stats,'independent_cell_check':'567 final diet +172 catch cells match Word XML and rendered PDF',
    'source_balance':'FAIL','diagnostics':'NOT_RUN_LOADER_BLOCKED','WCP_option1':'D_fixed_M0 saved exact returns reused; WARN all3',
    'catch_fleet_total_t_km2_year':str(totalcatch),'artifact_manifest_files':len(manifest),'source_repair_applied':False,'selected_model_changed':False})
print(json.dumps({'files_hashed':len(manifest),'eight_imports':True,'catch_total':str(totalcatch),'reconstruction_sheets':sheet_stats},indent=2))
