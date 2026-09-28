from pathlib import Path
import csv,json,re,hashlib,openpyxl,sys,shutil
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REG=ROOT/'regions/LME_049';REVIEW=Path(__file__).parent
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def writecsv(p,rows):
    with p.open('w',newline='',encoding='utf-8') as f:csv.writer(f).writerows(rows)
proposal={'unit_id':'LME_049','production_selection':'UNCHANGED; none selected','user_preferred_source':'KUR-2019','preference_rationale':'User prefers 2019 because it has more detailed group structure; this preference is not adoption of an exact model.','models':[],'paper_updates':[]}
for dest in REG.glob('models/49_*'):
    et=dest/'extracted_tables';ex=json.loads((et/'model.json').read_text(encoding='utf-8'));canonical=json.loads((dest/'model.json').read_text(encoding='utf-8'));year=ex['metadata']['model_year'];old=year==2013;pid='KUR-2019' if old else 'KUR-2025';N=len(ex['groups']);ncons=len(ex['consumers']);sums={int(k):sum(float(x) for x in v.values()) for k,v in ex['diet'].items()}
    diag={'candidate_model_id':dest.name,'scientific_status':'NOT ELIGIBLE: unresolved source inputs; not selected','n_source_groups':N,'n_source_consumers':ncons,'source_diet_known_subtotals':sums,'requested_MC_draws_per_method':100,'method_timeout_seconds':180,'production_model_selected':False,'source_model_json_sha256':hashlib.sha256((dest/'model.json').read_bytes()).hexdigest()}
    if old:
        retained=json.loads((dest/'bounded_diagnostic_output/summary.json').read_text(encoding='utf-8'));diag.update({'load_status':'FAIL','load_error':retained['entries'][0]['load_error'],'MC_draws_executed':0,'methods_executed':0,'negative_group_counts':'unavailable; model did not load'})
        writecsv(dest/'source_group_diagnostic_status.csv',[['group_seq','group_name','status'],*[[g['n'],g['name'],'UNAVAILABLE: missing 3-pool detritus routing; model failed to load'] for g in ex['groups']]])
    else:
        w=openpyxl.load_workbook(dest/'sppr_source.xlsx',read_only=True,data_only=True)
        data={s:list(w[s].values) for s in w.sheetnames};w.close()
        for s in ['model_health','mc_diagnostics','run_notes','groups_df']:writecsv(dest/(s+'.csv'),data[s])
        gh=data['groups_df'][0];groups={r[0]:dict(zip(gh,r)) for r in data['groups_df'][1:]};full=[];counts=[]
        for scope in ['all','inner','PP']:
            h=data['sppr_'+scope][0]
            for i,method in enumerate(h[2:],2):
                rr=[r for r in data['sppr_'+scope][1:] if r[0]<=N];neg=[r for r in rr if isinstance(r[i],(float,int)) and r[i]<0];available=[r for r in rr if isinstance(r[i],(float,int))]
                counts.append({'scope':scope,'method':method,'n_numeric':len(available),'n_negative':len(neg),'negative_source_groups':[r[0] for r in neg],'n_negative_loader_zero_catch':sum(groups[r[0]]['catch']==0 for r in neg)})
                full.extend([[dest.name,r[0],r[1],scope,method,r[i],canonical['group'][r[0]-1]['export'],groups[r[0]]['catch'],'CONDITIONAL LOADER DIAGNOSTIC; NOT PUBLISHABLE'] for r in rr])
        writecsv(dest/'all_source_group_sppr_diagnostics.csv',[['candidate_model_id','group_seq','group_name','scope','method','sppr','source_catch','loader_catch','eligibility'],*full])
        writecsv(dest/'loader_completion_audit.csv',[['group_seq','group_name','source_BA','loader_BA','source_GS','loader_GS','source_TL','loader_TL','source_EE','loader_EE'],*[[seq,groups[seq]['group_name'],canonical['group'][seq-1]['biomass_accum'],groups[seq]['biomass_accum'],canonical['group'][seq-1]['gs'],groups[seq]['gs'],ex['groups'][seq-1]['tl'],groups[seq]['tl'],canonical['group'][seq-1]['ee'],groups[seq]['ee']] for seq in range(1,N+1)]])
        diag.update({'load_status':'completed conditional computational transformation','methods':counts,'health':[dict(zip(data['model_health'][0],r)) for r in data['model_health'][1:]],'monte_carlo':[dict(zip(data['mc_diagnostics'][0],r)) for r in data['mc_diagnostics'][1:]],'method_execution':[dict(zip(data['run_notes'][0],r)) for r in data['run_notes'][1:]],'engine_added_groups':[g for seq,g in groups.items() if seq>N]})
    dump(dest/'diagnostic_summary.json',diag)
    validation=(dest/'validate.log').read_text(encoding='utf-8');vsum=re.findall(r'\d+ error\(s\), \d+ warning\(s\)',validation)[-1]
    mb=(et/'MASS_BALANCE_CANONICAL.md').read_text(encoding='utf-8');verdict=next(x for x in mb.splitlines() if '**Verdict:' in x)
    if old:
        specific='''The table prints one 2013 model with 41 groups (35 consumers, 3 producers, 3 detritus pools), not three independent regional model versions. OYC/KC/OF are linked spatial pools. Main article Table 2 (PDF p.6, printed p.299) contains B in habitat area AND B in total model area. Import CSV preserves habitat B and habitat fraction; canonical JSON uses the explicitly printed total-area B, avoiding manufacture of digits from multiplying rounded habitat values. The conversion audit preserves both representations. Table 3 is rotated in the original (PDF p.8, printed p.301): prey rows 1–41 and predator columns 1–35. Coordinate anchors retain all 1,435 printed cells, including zeros and 0.001 precision. The source sum 1.012 for Seabirds was checked visually; no correction was made. Other non-unit columns are Toothed whales 0.995, Tunas 1.002, Skipjack 1.002 and Yellowtail 1.005.

Seabird habitat and whole-model biomasses are both printed <0.01. Five landings are <0.01: Baleen whales, Toothed whales, Flatfishes (KC), Seabreams (KC), Mesopelagic fishes (KC). These are numeric missing values with the original bounds in censored_values.json, not zero or half the bound. The source's model-estimated cells are flagged by bold font in source_cells.json. Section 2.1 explicitly equates P/B and Z; both fields are retained in the import.

The supplement at https://www.int-res.com/articles/suppl/m617p295_supp.pdf was identified from printed p.297. The web reader initially exposed the 46-page supplement, including species descriptions, but exact-byte retrieval returned HTTP 401 and a publisher bot check; subsequent web fetch failed too. Browser navigation did not yield an exportable artifact. It is not represented as a locally archived or completely reviewed source. Source taxonomy therefore retains the 11 single-species groups documented in the main article and main-article definitions/spatial pools for the remaining groups; detailed pooled species membership remains incomplete. No new names were inferred from diet references.

USER-PREFERRED SOURCE: the user prefers Watari 2019 because its group structure is more detailed. Exact-model selection remains pending.

SPPR: the bounded wrapper and a retained single-model API attempt both failed on missing detritus routing for the three pools 39/40/41. This cannot be inferred from habitat fractions or prey diets. No methods or MC draws executed. All 41 source groups have an explicit unavailable diagnostic record.'''
        profile='Axis: taxonomic guilds plus spatial pools. OYC coastal Oyashio (186128 km²), KC coastal Kuroshio (186220 km²), OF offshore (540754 km²); total 913102 km². Paper assigns rounded habitat fractions0.2/0.2/0.6; multi-block groups span these pools. Regional representativeness is partial; no freshly verified percent LME coverage.'
    else:
        specific='''The bundle supports one 2023 model with 25 groups (23 consumers, 1 producer, 1 detritus pool). The author is Gan Chen: the source citation is Chen et al. (2025), correcting the inherited catalog author Gan et al. The printed article title is “Study in the ecosystem structure and trophodynamics in the Kuroshio-Oyashio Extension area”. Table 2 (PDF/printed p.5) contains TL, B, P/B, Q/B, EE, catch and omnivory index; no unit conversion was applied. The source's model-estimated values are recorded as bold in source_cells.json. Source catch is placed in the single Total fishery landings column because no discard split is published; it remains source catch, not verified landings-only catch. Blank catch remains unknown, not zero.

The supplement DOCX was inspected as OOXML paragraphs and all five tables. Table S2 has 25 prey rows and 23 predator columns. Exact raw cell text and table/row/column coordinates are preserved. Fifty-four cells contain '+'. The caption says '+ indicates that it occurred at a percentage <0.01'; no exact numerical value or unambiguous conversion to a proportion is supplied. These cells remain blank in import CSV and -9999 in canonical JSON, with explicit censor metadata. Numeric diet subtotals range 0.98–1.00; neither the deficit nor censored cells were filled, distributed or normalized. S1 is a parameter/diet-study source list, not authoritative group composition; Table1 in the main article is the membership evidence. S3–S5 concern pedigree/uncertainty, not separate model versions. DOCX table structure is machine-readable; no layout-dependent cell interpretation was used. LibreOffice is unavailable, so a page-rendered DOCX check was not performed.

Table 1 (PDF/printed p.3) gives main species composition for all25 groups. It is not claimed exhaustive. Source spellings are retained, including questionable Salmon membership Oncorhynchus kawamurae and the spelling Tradhypterus ishikawae. No unverified synonym repair was applied. Chub mackerel includes Scomber australasicus and S. japonicus. Group13 comma was replaced with semicolon in import/canonical name to obey the importer no-quote CSV convention; original name remains in source-cell evidence.

SPPR: the isolated bounded wrapper completed22 methods with100 draws requested for each of two MC methods and180 seconds per method. GE, TE and With Egestion all FAIL divergence diagnostics: living-network spectral radii1.31171875,1.652892561983471,1.049375 respectively, all above1. Each MC method accepted0/100 and rejected100/100 as diverged. Numerous coefficients are negative, including source groups whose catch was unreported and loader-completed to zero. All source groups and all scopes/methods are retained in all_source_group_sppr_diagnostics.csv. A computational method status of ok records successful execution, not scientific validity.

These are CONDITIONAL LOADER DIAGNOSTICS, not exact published-model results. The loader converts censored diet sentinels to0, normalizes12 consumer columns, defaults missing GS, fills missing catches, creates a diet_import group, and solves unknown flows including biomass accumulation. The resulting tiny model-balance residual only describes that completed computational model; source BA remains unknown. loader_completion_audit.csv preserves those differences. No coefficients are eligible for production or matching.'''
        profile='Axis: taxonomic/size guilds. Study area148–164°E and35–45°N, high-seas Kuroshio–Oyashio Extension; June–August2023 survey,36 sampled trawl stations of76 planned,50–150m trawl depth. Partial LME relationship; no freshly verified percentage coverage.'
    report=f'''# {ex['metadata']['model_name']} ({year})

Source-faithful extraction of available published tables is complete, with unresolved source inputs retained. This model is NOT SELECTED and is not approved for production SPPR, catch matching, annual PPR or PPR/NPP.

## Source tables and reviewed evidence

{specific}

## Biomass accumulation and prose sweep

The entire available main article was searched for biomass accumulation, assimilation/egestion, immigration/emigration, discards, detritus routing and numeric steady-state statements; the2025 DOCX paragraphs and all tables were searched too. No numeric BA, GS, detritus routing or discards were recovered. The2019 article is a static mass-balanced model with a steady-state methods reference, but no group-level numerical BA is printed. The2025 equation names BA and net migration but supplies no values. These remain missing. The unavailable2019 supplement remains an explicit completeness limitation. prose_sweep.txt and full source text are retained.

## Conventions, deliberate blanks and conversion

Source strings and precision are preserved in extracted_tables/model.json, source_cells.json and diet_source_cells.json. Unknown scalar values are blank in import files and -9999 in canonical model.json. No project GS/default habitat/BA/routing convention was imposed. EwE or the calculation loader may supply0.2 GS, habitat1, catch0, import0 or BA/flow estimates; none is a source-stated value. Missing detritus fate is not a zero routing observation. The converter's normalized intermediate and log are retained for audit; converter_transformations_reversed.json lists every difference restored in canonical model.json. Reconstructed canonical XLSX and independent JSON value assertions preserve printed PB/QB/EE, all diet values and censor sentinels, all group identities and taxonomy. Source TL remains authoritative in TL.xlsx; engine TL is recomputed, not a replacement source TL.

Model number {ex['metadata']['model_number']} is a local project identifier required by the importer, not an EcoBase accession. Folder name is the project candidate id. Source files remain in papers/{pid}; source_manifest.json records exact byte sizes and SHA256. Local diagram/page render evidence is under extracted_tables/page_evidence. Original source bytes were not modified.

## Validation

Import validator: {vsum}. Warnings primarily flag unknown biomass accumulation and detritus routing, and source censored biomass where applicable. Diet errors reflect printed non-unit columns/censored deficits, not repaired data. Both validation and mass-balance utilities were executed; logs are retained. {verdict}

MASS_BALANCE_CANONICAL.md contains per-group diagnostics. Recomputed EE is conditional on missing catch/BA/migration being omitted, missing predator biomass under-counting predation where applicable, and censored diet amounts being omitted; it does not prove source balance. Missing BA was not set to the checker’s suggested closure amount. The strict scientific eligibility gate remains failed/unsupported regardless of successful JSON construction or solver completion.

## Model profile and pending choice

{profile}

Central metadata registration is staged for parent-agent serialization. Regional LME_049.xlsx Overview and all production results/groups remain unchanged. The next user decision is the exact model to investigate/adopt; source preference alone does not authorize selection. Missing source inputs must be resolved before source-faithful SPPR can be supported.
'''
    (et/'REPORT.md').write_text(report,encoding='utf-8');(et/'MODEL_PROFILE.md').write_text(profile+'\n',encoding='utf-8')
    entry={'unit_id':'LME_049','model_id':dest.name,'model_path':str((dest/'model.json').relative_to(ROOT)),'paper_id':pid,'model_years':str(year),'groups':N,'consumers':ncons,'coverage_class':'partial','coverage_percent':None,'extraction_status':'source tables extracted; unresolved/censored parameters retained','taxonomy_status':'main-article single stocks and group/spatial definitions; detailed supplement unavailable' if old else 'all25 group main composition lists retained; source spelling; scope not exhaustive','sppr_status':diag['load_status'],'scientific_status':diag['scientific_status'],'selected':False,'preference_status':'USER-PREFERRED SOURCE' if old else 'complementary candidate','preference_rationale':proposal['preference_rationale'] if old else None,'report_path':str((et/'REPORT.md').relative_to(ROOT)),'diagnostic_path':str((dest/'diagnostic_summary.json').relative_to(ROOT))}
    proposal['models'].append(entry)
    mp=REG/'papers'/pid/'metadata.json';meta=json.loads(mp.read_text(encoding='utf-8'))
    meta['verified_source_update_20260928']={'source_manifest':str((dest/'source_manifest.json').relative_to(ROOT)),'model_id':dest.name,'groups':N,'modeled_year':year,'extraction_status':entry['extraction_status'],'scientific_status':entry['scientific_status'],'production_selected':False,'user_source_preference':old,'preference_rationale':proposal['preference_rationale'] if old else None,'legacy_geometry_assessment':'Inherited percentage/footprint is retained for provenance, not freshly verified by this extraction.'}
    meta['main_file_status']='verified_local_pdf';meta['download_status']='local_source_bundle_verified';meta['downloaded_file_count']=1 if old else 2;meta['material_files']=[x['path'] for x in json.loads((dest/'source_manifest.json').read_text(encoding='utf-8'))];meta['functional_groups']=N;meta['model_years']=str(year);meta['full_model_loadable']='FAIL: missing three-pool detritus routing' if old else 'Loader completed conditionally; exact source SPPR unsupported and all3 diagnostic configurations FAIL';meta['supplement_status']='identified but exact-byte download blocked HTTP401' if old else 'verified_local_docx'
    if old:meta['recommendation']='USER-PREFERRED SOURCE because of more detailed group structure; exact model not selected; missing detritus routing and source censoring require resolution.';meta['doi']='10.3354/meps12508'
    else:meta['legacy_authors_before_pdf_verification']=meta['authors'];meta['authors']='Chen et al.';meta['legacy_title_before_pdf_verification']=meta['title'];meta['title']='Study in the ecosystem structure and trophodynamics in the Kuroshio-Oyashio Extension area'
    dump(mp,meta)
    proposal['paper_updates'].append({'paper_id':pid,'authors':meta['authors'],'title':meta['title'],'doi':meta['doi'],'publication_year':meta['publication_year'],'main_file_status':meta['main_file_status'],'supplement_status':meta['supplement_status'],'functional_groups':N,'model_years':str(year),'full_model_loadable':meta['full_model_loadable'],'recommendation':meta.get('recommendation'),'source_files':meta['material_files'],'notes':entry['report_path']})
dump(REVIEW/'metadata_registration_proposal.json',proposal)
dump(REG/'papers/KUR-2019/supplement_retrieval_log.json',{'url':'https://www.int-res.com/articles/suppl/m617p295_supp.pdf','date':'2026-09-28','initial_web_reader':'46-page PDF metadata and initial species descriptions visible; not a retained exact-byte copy','direct_requests':['PowerShell Invoke-WebRequest HTTP401 bot check','Python requests HTTP401, text/html,89522bytes; not saved as PDF','int-res.com without www HTTP401','download=1 URL HTTP401','http URL HTTP401'],'browser_attempt':'in-app navigation created blank PDF page; content export unsupported','final_status':'source supplement not archived; no exact source hash possible; detailed review incomplete'})
print(json.dumps(proposal,ensure_ascii=False,indent=2))
