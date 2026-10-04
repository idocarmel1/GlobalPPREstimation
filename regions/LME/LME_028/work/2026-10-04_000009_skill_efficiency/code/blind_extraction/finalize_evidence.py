"""Finalize the extraction handoff; inventory ONLY our artifacts and isolated PDF."""
from pathlib import Path
import csv, datetime, hashlib, importlib.metadata, json, platform, subprocess, sys
ROOT=Path(__file__).resolve().parents[7]
RUN=ROOT/'regions/LME/LME_028/work/2026-10-04_000009_skill_efficiency'
OUT=RUN/'outputs/blind_extraction'; E=OUT/'evidence'; MODEL=OUT/'model_2000s'
PDF=RUN/'inputs/blind_extraction/original_publication.pdf'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
load=json.loads((E/'load_checks.json').read_text(encoding='utf-8'))
data=json.loads((MODEL/'model.json').read_text(encoding='utf-8'))
fidelity=json.loads((MODEL/'SOURCE_FIDELITY_CHECK.json').read_text(encoding='utf-8'))
checks=json.loads((E/'extraction_checks.json').read_text(encoding='utf-8'))
identity=json.loads((E/'source_identity.json').read_text(encoding='utf-8'))
assert load['canonical_sha256']==hashlib.sha256((MODEL/'model.json').read_bytes()).hexdigest()
assert len(data['group'])==38 and len(data['published_companions'])==14
assert fidelity['exact_value_and_missing_mask_match'] and fidelity['max_numeric_difference']=='0'
assert load['known_B_PB_QB_EE_same_within_1e12'] and load['diet_known_positive_cells_unchanged']
assert load['denied_preload_attempts'] and not load['constructor']['completed']
source_check={'checked_utc':now,'source_only':True,'no_comparison_answers_read':True,'pdf_sha256':identity['sha256'],'group_count':38,'consumer_count':35,'positive_diet_cells':417,'final_table_order_joined_by_verified_identity':True,'visual_pages_read':[185,191,193,194,197,199,205,207,345,357,358,359,360,361,362,363],'source_pages_and_cells':'Coordinate companions retain exact numeric bboxes. Prose companions identify PDF/printed pages and sections. PDF full text retains original footnotes/captions.','independent_source_conflict_resolution':'Final Table6.1(b) and6.2 retained. Appendix source estimates not substituted; source explicitly describes iterative balance adjustments PDF193.','flag_source_inspection':[{'group_seq':n,'finding':'Indicative EE residual','basic_source':'PDF191 printed176 Table6.1(b)','diet_source_pages':pages,'result':'Cell values/order retained after source image inspection; unknown BA/migration/discards/native stanza equations prohibit ecological verdict'} for n,pages in [(4,[357]),(15,[358]),(23,[360]),(25,[361]),(26,[361]),(35,[363]),(37,[363])]],'pq_flags':[{'group_seq':n,'source':'PDF191 Table6.1(b)','result':'Published PB/QB columns visually checked; source value retained'} for n in [34,35,36]],'diet_sign_check':'PDF363 juvenilelargepelagic prey in marine turtles diet0.0009: hiddentext stray hyphen; sourceimage showspositive0.0009 with nearby scanning mark. No negative diet repaired.','unknowns_preserved':['GS','habitat fraction','diet import','BA and BA rate','migration','detritus routing','discards','TL','detritus import'],'single_detritus_pool_not_proof_of_routing':True,'printed_diet_sums':'Only PDF357 supplies printed Sum row (9 consumers); no invented Sum rows for remaining source pages. All35 prey sums independently calculated without normalization.','catch_total_note':'Exact six-fleet cell sum7.7375; printedfooter7.736; printed group total differences at most0.0005. PDF205 prosecatch7.35also conflicts. Every source total retained separately.','unsupported_native_equations':'Four linked two-stanza stocks retained; flat calculator does not reproduce native growth/recruitment/maturity equations.','unmapped_appendix_group':'Large benthopelagic fish Appendix6.1.22 has no separate final38group row; retained in companion without invented crosswalk.'}
(E/'source_checks.json').write_text(json.dumps(source_check,ensure_ascii=False,indent=2),encoding='utf-8')
profile='''# Northern South China Sea, 2000s: source group profile

This is an independent paper extraction from Cheung Wai Lung's May2007 UBC PhD thesis, Chapter6. The modeled period is the early2000s; it differs from the publication year, survey years (mostly late1990s), and source landings years (mostly2000; jellyfish1993proxy). The local trial identifier `NSCS_2000s_blind` supplies no EcoBase accession or researcher selection.

The final model has38 groups: two producers,35 consumers and one detritus pool. Preserve Table6.1(b) PDF191/printed176 order, names, spelling and parenthesized estimates. [Source membership](companions/Source_membership.csv) records family/guild definitions and representative species from Appendix6.1; it is not an externally verified taxonomy or an exhaustive species list. Commercial fish families are separate from residual demersal, pelagic and benthopelagic guilds. Source fish divisions use≤30cm versus>30cm, and four juvenile/adult stocks: hairtail (18months), largecroakers (24months), largedemersal (18months with conflicting belowage2wording), largepelagic (18months). [Stanza parameters](companions/Source_stanzas.csv) retain K, recruitment power, maturity fraction and transition age. Native stanza equations have not been reproduced.

There are no spatial prefixes in group names. Figure6.1 PDF185/printed170 describes the shelf<200m,106°53′–119°48′E and17°10′–25°52′N, primarily the Chinese EEZ, from coast to broken line. It is a study-region map, not a measured overlap polygon. No area, habitat fraction, coverage percentage or LME-overlap metric is inferred. Biomass is treated as whole modeled-area density because Eq6.1 describes total B and Appendix6.1 reports NSCS biomass/km²; the EwE habitat-area fraction remains unknown.

Six fishing fleets are PSt(pair/sterntrawl),ShT(shrimptrawl),PS(purseseine),H&L(hook/line),GN(gillnet),Others. Species composition by fleets uses a HongKong proxy (PDF193), not independently measured national composition. Catch cells in Table6.2 PDF193–194 are preserved as reported landings; discards and total removals including discards remain unknown. The Appendix6.2 diet is explicitly shared by the1970s and2000s models; sparse source blanks, absent prey rows and unknown outside import have distinct companion statuses.

Important source structure conflicts remain: Appendix6.1.22 describes a large benthopelagic group absent as a separate final row; Table6.1 has one Benthopelagic fish group. Appendix6.1.24 says demersal under the largepelagic heading. `Demesral` and `Agyrosomus` source spellings are preserved without external taxonomic correction. See [unmapped source groups](companions/Unmapped_source_groups.csv), [source context](companions/Source_context.csv) and [parameter alternatives](companions/Published_parameter_notes.csv).
'''
(MODEL/'MODEL_PROFILE.md').write_text(profile,encoding='utf-8')
report=f'''# Independent extraction: Northern South China Sea, 2000s

The source-available extraction is complete within this isolated trial:38 groups,35 consumers,417 positive diet cells and six fleets. Eight standard imports and14 companion tables convert to one canonical [model.json](model.json). This is an extraction/conversion/load audit; full paper-to-PPR replication, ecological readiness, researcher approval, model selection and live integration have not been established.

The only scientific source read was the supplied369-page original PDF (SHA-256 `{identity['sha256']}`). No retained model JSON/table, native answer, SPPR workbook, model notes, previous review/trial output, regional workbook or Project.xlsx content was read, hashed or copied. Graph retrieval was excluded. Source identity and page/cell evidence are in [source checks](../evidence/source_checks.json), [source identity](../evidence/source_identity.json) and the companions. [MODEL_PROFILE](MODEL_PROFILE.md) describes group membership and geography.

## Source extraction and decisions

Final Table6.1(b) PDF191/printed176 supplies B/PB/QB/EE; its caption PDF190 defines parentheses as Ecopath-estimated values. Their numbers and source roles remain retained. Table6.2 PDF193–194/printed178–179 supplies six2000s fleet columns; the1970s columns were not imported. Exact fleet-cell sum is7.7375t/km²/year; the printedfooter7.736 and group totals are retained separately, as is the conflicting7.35 in PDF205 prose. Group total rounding differences are at most0.0005. No catch multiplier was inferred.

Appendix6.2 PDF357–363/printed342–348 explicitly applies to both model periods. Prey are rows, consumers columns; coordinate anchors plus name crosswalks preserve the orientation. Raw consumer prey-only sums range0.9990–1.0011. The cephalopod sum is0.99947; all35 sums are retained exactly. Source blank prey cells remain blank in the imports, with structural absence distinguished from unknown outside import in Diet_source_cells.csv. No matrix normalization or missing import0 assumption occurred in canonical files. Source printed Sum rows exist only on PDF357 and are retained separately from calculated sums.

Numeric prose from Appendix6.1 is retained: source-stated Z and explicit P/Q, original survey estimates and alternatives, natural/fishing mortality assumptions, catch/stage proportions, four native stanza links with K/recruitment/maturity/ages, source membership, and an unmapped large benthopelagic group. Published pedigree categories/indices (PDF197/199), mortality outputs F/M/M0 (PDF205), and ecosystem/PPR outputs (PDF206–208) are companions. M0 is a mortality rate output, not an unassimilated-food or Other-mortality fraction. Native stanza equations remain unsupported by the flat calculator. No investigator edits or parameter repair were introduced.

GS, habitat-area fraction, detritus routing/import, BA/rate, migration, external diet import, group TL, and separated discards are not numerically reported for this parameterization and remain unknown (`-9999` in canonical JSON). The generic steady-state Ecopath description does not authorize BA0. One detritus pool does not prove all fate fractions1. Published landings are an explicitly scoped export convention; total removals including unknown discards remain unknown. Basal/DET unused Q/B or P/B remain unused rather than biological unknown reconstructions. Source spelling and contradictions are preserved.

## Verification

Structural validation:0errors,41warnings (unknown GS/BA/routing/TL). The indicative checker:0errors,10warnings,36notes; it uses defaults for missing GS and omits unknown BA/migration/discards in its indicative arithmetic. Seven EE residuals and unusual PB/QB of seabirds/mammals were checked against source images and retained. Its success exit code is not a source balance verdict. The missingness-aware converter gives **INDETERMINATE**:0errors,115indeterminate,3warnings,2notes. [MASS_BALANCE](MASS_BALANCE.md) contains the exact report; proposed BA closures in generated diagnostics were never adopted.

Import→canonicalJSON→reconstructed workbook: all{fidelity['cells_checked']} checked cells across8imports and14companions match values and missing masks exactly; max difference0 at absolute tolerance1e-12/relative1e-14. See [SOURCE_FIDELITY_CHECK](SOURCE_FIDELITY_CHECK.json). The reconstructed workbook is retained as round-trip evidence, not a native EwE model.

Raw ModelData JSON load succeeds:38source groups plus synthetic diet_import. All148 known B/PB/QB/EE cells, group names and417 positive diet values remain unchanged within1e-12. [Loader ledger](../evidence/loader_transformation_ledger.csv) records each field/cell and runtime changes: absent-prey cells→0, single-pool routing→1 and detritus self-identity, M0=PB(1−EE), unknowns→NaN, and a synthetic import group. The loader hardcodes LME13 despite metadata28. Its eager legacy model preload was blocked before reading by an audit hook, allowing no retained answers into the trial.

Strict PPRCalculator constructor with normalization/defaultGS/zeroBA/zeroCatch/underdetermined completion all disabled fails at diet validation (tol0.001): consumer33=1.0011 and consumer20=0.9990. Consumer20 crosses the floating tolerance boundary. Imports remain unknown; no tolerance expansion or normalization was used. This failure is saved in [load checks](../evidence/load_checks.json), with the exact settings/code/input hashes. No PPR/diagnostics call, external taxonomy lookup, catch/species mapping, geographic overlap calculation, selection or integration was executed. Published PPR benchmark values are source outputs, not results of this trial.

## Handoff stages

| Stage | Actual outcome |
|---|---|
|Isolated source identity/read, coordinate extraction and visual checks|Complete|
|Eight imports plus required/source companion evidence|Complete|
|Canonical conversion and exact round trip|Complete|
|Source mass-balance interpretation|Indeterminate; restrictions retained|
|Raw ModelData load and transformation audit|Complete, with documented runtime assumptions|
|Strict calculator initialization|Attempted; failed source diet-sum tolerance|
|Native multistanza reconstruction|Retained inputs only; equations not reproduced|
|Taxonomy/catch mapping, overlap, PPR diagnostic/coefficient calculation|Inapplicable to authorized extraction trial; not performed|
|Researcher review/adoption, live integration and selection|Not performed|

Supporting execution timestamps, hashes and artifact integrity are in [evidence index](../evidence/index.json), [stage trace](../evidence/stage_trace.json) and [completeness](../evidence/completeness.json). Source recovery has not established full computational pipeline readiness.
'''
(MODEL/'REPORT.md').write_text(report,encoding='utf-8')
(MODEL/'model_notes.md').write_text('Independent source-preserving2000s extraction. LocalID NSCS_2000s_blind, not EcoBase. No normalization/parameter repair/live integration. Finaltable values prevail; alternatives retained. See REPORT.md and MODEL_PROFILE.md for unknowns/nativeunsupported fields. Raw loadability and strict-calculator readiness are separate; strict initialization fails. Researcher approval/selection not performed.\n',encoding='utf-8')
environment={'checked_utc':now,'python':sys.version,'platform':platform.platform(),'libraries':{name:importlib.metadata.version(name) for name in ['pandas','numpy','openpyxl','PyMuPDF','pypdf']},'read_scope':'Only mandatoryrootcontract/skills/resources/helpers/enginecode and singleisolatedPDF; strictretainedanswer exclusions. Own generatedevidence maybereopened.','read_started_utc':identity['timestamp_utc'],'helper_code_sha256':{name:hashlib.sha256((ROOT/'tools/skills/paper-to-ppr/resources/extraction/scripts'/name).read_bytes()).hexdigest() for name in ['write_outputs.py','validate.py','massbalance_check.py','database_json.py','source_fidelity.py','pdfgrid.py','prose_sweep.py']}}
(E/'environment.json').write_text(json.dumps(environment,ensure_ascii=False,indent=2),encoding='utf-8')
roles={'model_2000s/model.json':'canonical_model','model_2000s/REPORT.md':'extraction_report','model_2000s/MODEL_PROFILE.md':'source_membership_profile','model_2000s/SOURCE_FIDELITY_CHECK.json':'roundtrip_checks','evidence/source_checks.json':'source_checks','evidence/load_checks.json':'load_checks','evidence/loader_transformation_ledger.csv':'loader_ledger','evidence/stage_trace.json':'execution_trace','model_2000s/MASS_BALANCE.md':'source_balance_evidence'}
for name in ['Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx']:roles['model_2000s/'+name]='import_'+name
for name in data['published_companions']:roles['model_2000s/companions/'+name]='companion_'+name
artifacts=[]
for file in sorted(OUT.rglob('*')):
    if not file.is_file() or file in [E/'index.json',E/'completeness.json']:continue
    rel=file.relative_to(OUT).as_posix();artifacts.append({'role':roles.get(rel,'supporting_evidence'),'path':file.relative_to(E).as_posix() if file.is_relative_to(E) else '../'+file.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'availability':'present'})
# Include only our own bounded reproduction entrypoints and exact supplied PDF.
for file in sorted((RUN/'code/blind_extraction').glob('*.py')):
    artifacts.append({'role':'reproduction_code','path':'../../../code/blind_extraction/'+file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'availability':'present'})
artifacts.append({'role':'source_document','path':'../../../inputs/blind_extraction/original_publication.pdf','sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'availability':'present'})
for role,reason in [('strict_calculator_ready','Strictconstructorfailsdiettol;failure recorded, no repairs authorized'),('PPR_calculation','Not an authorized stage of this extraction trial'),('external_taxonomy_mapping','No external lookup or retained mapping inputs authorized'),('spatial_overlap','No regionboundary/source trace evaluated in this trial'),('researcher_approval','No reviewer approvalorselection performed'),('live_integration','All artifacts isolated under trial output')]:artifacts.append({'role':role,'availability':'failed' if role=='strict_calculator_ready' else 'inapplicable','reason':reason,'acquisition_status':'Notperformed;requiresappropriatescope/assumptions/review' if role!='strict_calculator_ready' else 'Attempted, savedfailure; noindependentnextscientificrun'})
index={'schema_version':1,'run_id':'2026-10-04_000009_skill_efficiency/blind_extraction','region_id':'LME_028','model_id':'NSCS_2000s_blind','variant_id':'source_2000s_no_repair','source_identity':{'sha256':identity['sha256'],'pages':369,'publication':'Cheung WaiLung,2007,UBCPhDthesis','period':'2000s'},'computational_input_identity':{'sha256':load['canonical_sha256'],'path':'../model_2000s/model.json','source_preserving':True},'methods':['source_only_coordinate_and_prose_extraction','eight_imports_conversion_exact_roundtrip','indicative_mass_balance_missingness_aware_report','guarded_ModelData_load','strict_PPRCalculator_constructor_attempt'], 'constructor_options':load['constructor_settings'],'required_roles':['source_document',*roles.values()], 'artifacts':artifacts,'reconciliation':{'exact_values_and_missing_masks':fidelity['exact_value_and_missing_mask_match'],'known_B_PB_QB_EE_load_unchanged':load['known_B_PB_QB_EE_same_within_1e12'],'positive_diets_load_unchanged':load['diet_known_positive_cells_unchanged'],'names_load_identical':load['known_group_names_identical']},'finalized_utc':now,'scientific_scope_complete':'source-available extraction/conversion/load audit only; strict readinesstestfailed, no fullpipelineclaim'}
(E/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
command=[sys.executable,'-X','utf8',str(ROOT/'tools/skills/paper-to-ppr/scripts/check_evidence.py'),str(E/'index.json'),'--output',str(E/'completeness.json')]
result=subprocess.run(command,cwd=ROOT,capture_output=True,encoding='utf-8');print(result.stdout);assert result.returncode==0,result.stderr
print('Finalized',now,'canonical',load['canonical_sha256'],'companions',len(data['published_companions']))
