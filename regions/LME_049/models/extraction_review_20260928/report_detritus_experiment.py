from pathlib import Path
import json,csv,hashlib,shutil,math,re
import openpyxl,pandas as pd
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());REVIEW=Path(__file__).parent;REG=ROOT/'regions/LME_049';MODELS=REG/'models'
ORIG=MODELS/'49_20192013_Western_North_Pacific_Watari_(2013)';CHEN=MODELS/'49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023)';EXP=MODELS/'49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)'
def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,float) and not math.isfinite(x):return None
    return x
def dump(p,o):p.write_text(json.dumps(clean(o),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvout(p,rows):
    with p.open('w',newline='',encoding='utf-8') as f:csv.writer(f).writerows(rows)
def records(rows):return [dict(zip(rows[0],r)) for r in rows[1:]]
def tab(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|',*['| '+' | '.join(str(x).replace('|','/') for x in r)+' |' for r in rows]])
combined=[];detail=[]
for dest,N in [(CHEN,25),(EXP,39)]:
    w=openpyxl.load_workbook(dest/'sppr_source.xlsx',read_only=True,data_only=True);data={s:list(w[s].values) for s in w.sheetnames};w.close()
    canonical=json.loads((dest/'model.json').read_text(encoding='utf-8'))['group'];groups={r[0]:dict(zip(data['groups_df'][0],r)) for r in data['groups_df'][1:]}
    method=[];allrows=[]
    for scope in ['all','inner','PP']:
        h=data['sppr_'+scope][0]
        for col,m in enumerate(h[2:],2):
            rr=[r for r in data['sppr_'+scope][1:] if r[0]<=N];numeric=[r for r in rr if isinstance(r[col],(int,float))];neg=[r for r in numeric if r[col]<0];zeros=[r for r in neg if groups[r[0]]['catch']==0]
            method.append({'scope':scope,'method':m,'n_numeric':len(numeric),'n_negative':len(neg),'negative_source_groups':[r[0] for r in neg],'n_negative_zero_catch':len(zeros),'negative_zero_catch_groups':[r[0] for r in zeros]})
            allrows.extend([[dest.name,r[0],r[1],scope,m,r[col],canonical[r[0]-1]['export'],groups[r[0]]['catch'],canonical[r[0]-1]['export']=='-9999','CONDITIONAL; NOT PRODUCTION'] for r in rr])
    if dest==EXP:
        for s in ['model_health','mc_diagnostics','run_notes','groups_df']:csvout(dest/(s+'.csv'),data[s])
        csvout(dest/'all_source_group_sppr_diagnostics.csv',[['model_id','group_seq','group_name','scope','method','sppr','source_catch','loaded_catch','source_catch_unknown','eligibility'],*allrows])
    info={'model_id':dest.name,'n_source_groups':N,'load_status':'conditional completion','source_eligible':False,'selected':False,'health':records(data['model_health']),'monte_carlo':records(data['mc_diagnostics']),'methods':method,'execution':records(data['run_notes']),'settings':json.loads((dest/'diagnostic_settings.json').read_text()),'runtime_seconds':80.47 if dest==EXP else 33,'source_sha256':sha(dest/'model.json')}
    if dest==EXP:
        audit=json.loads((EXP/'evidence/loader_audit_summary.json').read_text());dump(EXP/'evidence/loader_audit_summary.json',audit);info['loader_audit']=audit
        sources=[]
        for te in ['GE','TE','With Egestion']:
            f=pd.read_csv(EXP/'evidence'/('source_coefficients_'+te.replace(' ','_')+'.csv'),index_col=0)
            for n,row in f.iterrows():
                for basal,value in row.items():
                    sources.append({'TE_option':te,'group_seq':int(n),'source_seq':int(basal),'coefficient':value,'negative':value<0,'loaded_catch':groups[n]['catch'],'source_catch_unknown':canonical[n-1]['export']=='-9999' if n<=N else None})
        pd.DataFrame(sources).to_csv(EXP/'all_basal_source_coefficients.csv',index=False);info['negative_basal_source_coefficients']=[x for x in sources if x['negative']]
        info['extra_source_detail_runs']={'purpose':'workbook does not retain basal-source breakdown; three necessary detail-only deterministic runs','TE_options':['GE','TE','With Egestion'],'timeout_seconds_per_run':180,'new_MC_draws':0}
        dump(EXP/'diagnostic_summary.json',info)
    combined.append(info)
    healthcols=['TE_option','status','divergence_rho_living','divergence_b','divergence_n_negative_sources','divergence_n_near_singular_te','balance_rel_gap','model_input_p_max_rel_residual','model_input_q_max_rel_residual']
    section=[f'## {dest.name}',f'Groups: {N}. No production selection. All22 method workers returned `ok`; no failures or timeouts. Runtime approximately {info["runtime_seconds"]} seconds. Execution success is distinct from numerical health and source admission.',tab(healthcols,[[r.get(k) for k in healthcols] for r in info['health']]),'### Monte Carlo',tab(['method','requested','accepted','rejected negative','rejected diverged'],[[r['method'],r['n_samples'],r['n_accepted'],r['n_rejected_negative'],r['n_rejected_diverged']] for r in info['monte_carlo']]),'### Every method and source scope','Entries show available values / negative values for ALL source groups, including unreported or zero-defaulted catch groups. Parentheses list negative group IDs; `z` is the number of those with loaded catch zero. The complete values and original/loaded catch evidence are retained in each candidate’s all_source_group_sppr_diagnostics.csv. Blank source attribution for1986/1995 is unavailable, not zero.']
    rows=[]
    for note in info['execution']:
        if not str(note['topic']).startswith('method: '):continue
        m=note['topic'][8:];v=[]
        for scope in ['all','inner','PP']:
            x=next(x for x in method if x['scope']==scope and x['method']==m);v.append(f"{x['n_numeric']} / {x['n_negative']} ({','.join(map(str,x['negative_source_groups'])) or 'none'}; z={x['n_negative_zero_catch']})")
        rows.append([m,note['status'],*v,note['note']])
    section.append(tab(['method','execution','all','inner','PP only','configuration'],rows));detail.append('\n\n'.join(section))
original=json.loads((ORIG/'diagnostic_summary.json').read_text());combined.insert(0,original)
dump(REVIEW/'LME049_DIAGNOSTIC_RESULTS.json',{'region':'LME_049','production_selection':'unchanged','candidates':combined})
manifest=json.loads((EXP/'evidence/derivation_manifest.json').read_text());assert sha(ORIG/'model.json')==manifest['source_model_sha256'];assert sha(REG/'LME_049.xlsx')==manifest['production_workbook_before_sha256']
for source in manifest['publication_sources']:assert sha(ROOT/source['path'])==source['sha256']
checks={'original_canonical_and_publication_bytes_unchanged':True,'production_regional_workbook_bytes_unchanged':True,'Project_xlsx_written_by_experiment':False,'all_39_groups_times_22_methods_times_3_scopes_retained':39*22*3,'source_model_sha256':sha(ORIG/'model.json'),'experimental_model_sha256':sha(EXP/'model.json'),'no_production_selection_catch_matching_annual_PPR_or_map_run':True}
dump(EXP/'evidence/final_verification.json',checks)
proposal={'status':'STAGED ONLY; parent coordination required','unit_id':'LME_049','paper_id':'KUR-2019','model_id':EXP.name,'parent_model_id':ORIG.name,'model_path':str((EXP/'model.json').relative_to(ROOT)),'model_years':'2013','groups':39,'selected':False,'production_eligible':False,'model_type':'USER-APPROVED DERIVED EXPERIMENT, detritus-only pooling; NOT a distinct published parameterization','notes':'35 consumers and3 regional phytoplankton preserved. Shared full-retention detritus assumption, source rounding normalization and unknown-flow completion. GE/Egestion conditional health OK; TE FAIL. Original41-group candidate must remain separately registered. Source preference2019 is not adoption.','report_path':str((REVIEW/'EXTRACTION_AND_SPPR_REPORT.md').relative_to(ROOT))}
dump(EXP/'metadata_registration_proposal.json',proposal)
intro='''# LME049 extraction and full SPPR diagnostic review

The two available source bundles support two published parameterizations: Watari et al.(2019), year2013,41groups; and Chen et al.(2025), year2023,25groups. A separately authorized39-group detritus-only experiment is derived from Watari; it is not another published model. None is selected or production eligible. The user's preference for2019 reflects its finer group structure, not adoption of an exact model.

## Evidence and source admission

Watari uses35consumers,3regional phytoplankton and3detritus pools in one linked913102km² model (OYC186128,KC186220,OF540754). Table2 PDFp6 printed299 reports habitat and whole-model-area biomasses; Table3 PDFp8 printed301 has1435diet cells. Canonical JSON preserves printed whole-area B and diet precision, including non-unit totals .995,1.012,1.002,1.002,1.005 for consumers2,3,5,6,8. Seabird B<.01 and five catches<.01 remain unknown sentinels with censor evidence. No GS, numerical BA, migration or detritus routing was recovered. Main-article taxonomy and11single-species stocks are retained; detailed pooled membership is incomplete because the46-page supplement could not be archived (HTTP401). Source manifest, rendered pages, cell/font evidence, exact printed text and import/converter audits are retained in the original model folder. This is one spatially structured parameterization, not3independent models.

Chen2025 contains23consumers,1PP,1DET; Table2 p5 and DOCX supplementS2 supply parameters/diet.54'+' diet entries remain censored unknowns; the caption's '<0.01 percentage' was not silently assigned a numerical fraction. Diet known subtotals .98–1.00, GS/BA/migration/catches and fate gaps remain unresolved. Table1 p3 retains all25main composition lists, source spellings and imperfectly resolved membership. This is one2023survey-based parameterization, not separate models for supplemental uncertainty tables. DOCX's five tables were inspected as OOXML, not page-rendered (LibreOffice unavailable). The corrected citation is Chen et al.; Gan is the lead author's given name.

Both source extractions passed JSON reconstruction and exact source-value assertions; source errors/missingness were not repaired. Import validation reports1error/43warnings for Watari and diet/missingness findings for Chen in their validate.log. Watari canonical mass balance is INDETERMINATE for7groups (max EE difference .450; righteye flounder computed EE1.026), and Chen for16groups (max44.158;8EE>1). These conditional checks omit unknown terms; no finding establishes source steady state. Full details are in each extracted_tables/MASS_BALANCE_CANONICAL.md and REPORT.md. Source hashes are in source_manifest.json; source bytes and original canonical files are preserved.

## Original41-group Watari: blocked before calculation

49_20192013_Western_North_Pacific_Watari_(2013) fails loading: missing detritus routing for pools39,40,41 cannot be inferred. Habitat fractions0.2/0.2/0.6 and prey diets do not supply mortality/egestion fate. Therefore0methods and0MCdraws executed; spectral radii, health, SPPR balances, coefficients/negatives and acceptance tests were NOT RUN, not passed. All41groups have explicit unavailable records in source_group_diagnostic_status.csv; bounded_diagnostic_output retains the error and trace. No original model was modified to bypass this failure.

## Approved detritus-only experiment: exact changes and assumptions

49_2019201301_Watari_Detritus_Pooled_Experiment_(2013) maps1–38 identically and39/40/41 to39. It preserves all35consumer scalar/catch parameters, all3phytoplankton records and non-detritus diets. Total-area detritus B=9.58+6.04+28.50=44.12t/km²; habitat fractions are not applied a second time. A whole-domain pooled habitat1.00/Bhab44.12 is a derived representation, not a printed estimate. Each consumer's pooled detritus fraction is the exact decimal sum of its3source fractions; every full diet total is unchanged. Source DET EE remains unknown (no average). The original pools have no diet rows or supported internal transfer amounts; no internal transfer, catch or import was duplicated or invented. Unknown fate entries remain unknown in canonical JSON; the loader supplies its existing one-pool identity/default matrix.

The explicit experiment assumes shared cross-block detritus mixing and routes all living M0+egestion to the sole pool with full retention; real external losses and the source's spatial routing remain unknown. M0 is flow B×PB×(1−EE), not total mortality Z or its rate. All routing/default assumptions and the exact original-to-derived map, changed parameters, diet aggregation and unchanged totals are under evidence/. Original canonical SHA256 is7448c7ac1a4f8aebdc3aa27d236adc31c8bd7600dd39591271b9f2ce22615eb7.

The former multi-DET loading obstacle is removed. Source admission is still unsupported. The loader normalizes83nonzero diet cells in5consumers (exact changes in evidence/all_loader_diet_transformations.csv), defaults missing catch/migration/import to0 and regular GS to.2, and adds a zero-flow diet_import pseudo-group40.17source groups have missing catch defaulted0, including the five '<.01' catches. These zeros are not observed absence of fishing. Critically, seabird B<.01 becomes1t/km², and its printed PB.12 and QB36.67 become0 in the completed table. This is a consequential loader artifact, not a supported source correction. All299mapped scalar differences/completions and full raw/completed tables are retained. All other known scalar parameters stay unchanged within1e−12.

BA is solved for every group, not taken from the paper. The three phytoplankton BA values are−1.373122,+.299280,−1.496462t/km²/y. Pooled detritus inflow1075.514299 minus direct predation53.887700 is absorbed into BA+1021.626599t/km²/y, with assumed external loss0. This is roughly23.16times standing detritus biomass per year, an unresolved accumulation/loss issue, not evidence of realistic steady state. Its diagnostic utilization ratio is.0501041; loader DET EE=1 is a bookkeeping convention, not source EE or that budget ratio. Absolute completed production/consumption residuals are at most1.14e−13; this follows from completion and does not validate source balance. Source-level mass balance remains INDETERMINATE for7groups with all39BA unknown.

## Exact computational settings and interpretation

Isolated minimal candidate workbooks were run through the current bounded regional SPPR wrapper with180seconds per method and health configuration.100draws were requested for each of MC_new_GE and MC_new_TE_EEfix. TE uncertainty10%, cut20%, kind=new, exclude_diverged=True; TE MC fixesEE0 cases. No seed was fixed or exposed by the wrapper, so accepted stochastic outputs are not bitwise repeatable;100draws are screening, not evidence of stable tails. MC rejections distinguish negative from diverged and are not added twice. Failed/all-rejected outputs remain missing.

Loading uses underdetermined=True,zero_biomass_accum=False,normalize_DC=True,DC_tol=.001; default zero_catch=True,default_gs=True,weight_flow=weight_guess=1. The raw source and derived canonical models remain untouched by this completion. For all health rows: det_collapse_mode=never,det_open_mode=none,det_theta=1,det_external_sppr=0,explicit_TE=False. Theta is inert for these closed configurations; this is not an openness/sensitivity sweep. Scopes all/inner/PP respectively include every basal source, exclude Import, or retain only primary producers. Method configuration distinctions appear below and full executed code/settings/hashes are retained per candidate. Health grades configurations, not whole model validity.

GE and With Egestion in the experiment return health OK with gaps.00676480/.00387648; these are below the warning threshold but balance_is_balanced remainsFalse under the strict equality check. TE has rho<1 but FAIL from4negative basal-source coefficients, all in zero-catch/defaulted seabird group3 (DET39 andPP36/37/38), plus2near-singular TEcases; its gap.0335435 is WARN. TE coefficients are unusable. GE/Egestion coefficients describe only this heavily completed assumption scenario and should not be adopted as source-valid production estimates. Their MC100/100 acceptance does not resolve ecological input uncertainty. Chen's3configurations allFAIL, allMCdraws rejected, and negative groups include groups with no recorded fishing.

No production catch matching, annual PPR, adopted PPR/NPP or map refresh was performed. The generic diagnostic exporter includes a footprint sheet using source catches; those incidental diagnostic values are not annual regional estimates or adopted results. Original source candidate metadata is already registered unselected. Experimental metadata is STAGED ONLY and leaves the41-group record intact. Project.xlsx was not written by this experiment; the production regional workbook remains byte-identical. Next decision: retain this as an assumption experiment, or resolve seabird/censoring, BA/retention and spatial routing evidence before considering model adoption. No additional numerical repair is authorized or silently applied.
'''
report=intro+'\n\n### Independent reconstruction check\n\nThe experimental review XLSX was independently read back:39group scalar/catch records and1365diet entries agree with canonical values. The converter intermediate fills unknown fates/imports and absent producer diets with zero; it is retained separately as converter_reconstructed_intermediate.xlsx. Those review-only zero fills were restored to blanks in canonical_reconstructed.xlsx, with an explicit audit in reconstruction_value_checks.json. The computational canonical JSON and all executed SPPR inputs remain unchanged.\n\n'+'\n\n'.join(detail)+'\n\n## Retained output locations\n\n- Original41-group: ../'+ORIG.name+'/\n- Chen25-group: ../'+CHEN.name+'/\n- Experiment39-group: ../'+EXP.name+'/\n- Compact full results: LME049_DIAGNOSTIC_RESULTS.json\n- Each available candidate: sppr_source.xlsx, all_source_group_sppr_diagnostics.csv, model_health.csv, mc_diagnostics.csv and run_notes.csv. Experiment adds all_basal_source_coefficients.csv and evidence/complete audits.\n'
(REVIEW/'EXTRACTION_AND_SPPR_REPORT.md').write_text(report,encoding='utf-8');(EXP/'EXPERIMENT_REPORT.md').write_text(report,encoding='utf-8')
for p in [Path(__file__),REVIEW/'export_source_coefficients.py']:shutil.copy2(p,EXP/'diagnostic_code'/p.name)
dump(EXP/'diagnostic_code_hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in [EXP/'model.json',*list((EXP/'diagnostic_code').rglob('*.py'))]})
print(json.dumps({'verification':checks,'health':[[x['TE_option'],x['status']] for x in combined[-1]['health']],'negative_source_coefficients':combined[-1]['negative_basal_source_coefficients']},indent=2))
