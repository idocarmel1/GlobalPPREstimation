"""Report persisted selected run and annual outputs, without recomputation."""
from pathlib import Path
import json,sys,shutil,math
import openpyxl
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=Path(__file__).parent;REG=ROOT/'regions/LME_038'
sys.path.insert(0,str(ROOT/'tools'));from workbooks import *
b=read_book(REG/'LME_038.xlsx');o=overview(b);mid=o['selected_model_id'];dest=REG/'models'/mid;ev=dest/'evidence';src=REG/'models/38_38001_Java_Sea_(mid1970s)'
w=openpyxl.load_workbook(dest/'sppr_source.xlsx',read_only=True,data_only=True)
def wr(s):
 rr=list(w[s].values);return [dict(zip(rr[0],r)) for r in rr[1:]]
health=wr('model_health');mc=wr('mc_diagnostics');notes=wr('run_notes');groups=wr('groups_df');negative=[]
for s in ['sppr_all','sppr_inner','sppr_PP']:
 rr=list(w[s].values)
 for r in rr[1:]:
  for j,v in enumerate(r[2:],2):
   if finite(v) and v<0:negative.append({'scope':s,'seq':r[0],'group':r[1],'method':rr[0][j],'sppr':v})
assert len([r for r in groups if r['group_type']!='Import'])==28
can=json.loads((dest/'model.json').read_text(encoding='utf8'))
assert {r['group_name']:r['taxon_descr'] for r in groups if r['group_type']!='Import'}=={g['group_name']:g['taxon_descr'] for g in can['group']}
methods=[r for r in notes if str(r['topic']).startswith('method:')]
settings={'wrapper':'tools/run_region.py --region regions/LME_038/LME_038.xlsx --stage sppr --timeout180','timeout_per_method_seconds':180,'MC_draws_per_method':100,'TE_error_percent':10,'TE_error_cut_percent':20,'exclude_diverged':True,'seed':'not explicitly fixed; fresh selected realization, not reused source diagnostic','health_detritus_config':{'det_collapse_mode':'never','det_open_mode':'none','det_theta':1.,'det_external_sppr':0.},'loader':'underdetermined=True; zero_biomass_accum=False; DC_tol=.001; normalize_DC=True; persisted normalized diets and signedBA reproduce previous loaded state'}
diag={'health':health,'method_status':methods,'mc':mc,'negative_scoped_group_coefficients_all_groups':negative,'negative_source_counts_three_health_configs':{h['TE_option']:h['divergence_n_negative_sources'] for h in health},'settings':settings,'taxonomy_comparison':'28/28 descriptions match selected and original canonical','negative_source_limit':'Only three health configurations retain source-column sign counts; no full-source claim for unexported other-method matrices.'}
(ev/'sppr_diagnostic_audit.json').write_text(json.dumps(diag,indent=2),encoding='utf8')
changes=json.loads((ev/'SOURCE_TO_DERIVED.json').read_text(encoding='utf8'));ba=[r for r in changes if r['field']=='biomass_accum'];near=[]
for g in groups:
 if g['group_type']=='Regular':
  te=g['p']/g['q']*(1-g['M0']/g['p'])
  if 0<abs(te)<.001:near.append({'group':g['group_name'],'seq':g['seq'],'TE':te,'inverse_TE':1/te,'P':g['p'],'Q':g['q'],'M0':g['M0']})
coverage=json.loads((ev/'MAPPING_COVERAGE.json').read_text(encoding='utf8'))
annual=[r for r in records(b,'PPR','Annual') if r['scope']=='all' and r['unidentified']=='method' and r['metric']=='ppr']
selected_metrics=[{k:r[k] for k in ['method','catch_basis','status',1950,2019]} for r in annual if r['method'] in ['new_GE','new_TE_EEfix','new_WithEgestion']]
ratios=[r for r in records(b,'PPR–NPP','Ratios') if r['model_id']==mid and r['scope']=='all' and r['catch_basis']=='landings' and r['unidentified']=='method' and r['npp_method']=='ens_median_tC_yr' and r['method'] in ['new_GE','new_TE_EEfix','new_WithEgestion']]
assert len(ratios)==3
npp=[{'method':r['method'],'years':[y for y in YEARS if finite(r[y])],'tonnes_carbon2019':r[2019]} for r in records(b,'NPP','NPP')]
out={'selected_model_id':mid,'rationale':o['selection_rationale'],'source_model_id':'38_38001_Java_Sea_(mid1970s)','model_sha256':sha(dest/'model.json'),'source_sha256':sha(src/'model.json'),'selected_SPPR_sha256':sha(dest/'sppr_source.xlsx'),'regional_workbook_sha256':sha(REG/'LME_038.xlsx'),'diagnostics':diag,'near_zero_TE':near,'all28_signed_computational_BA':ba,'negative_BA_count':sum(float(r['derived'])<0 for r in ba),'mapping':coverage,'annual_all_scope_method_treatment_wet_tonnes':selected_metrics,'landings2019_ensemble_NPP_percent':[{k:r[k] for k in ['method','npp_method',2019]} for r in ratios],'existing_NPP':npp,'limitations':['Printed source still fails strict admission; this is explicitly authorized derived state','Negative BA is computational budget completion, not observed ecological trend','TE WARN persists at Marine mammals; no claim of all-configuration validity','Java Sea subregion and mid1970s baseline extrapolated to Indonesian Sea1950-2019; no verified spatial fraction','Catch totals remain partial where taxon membership unresolved; coarse/stage weights are proxies','Scalar SPPR PP scope unavailable; missing NPP years remain blank']}
(ev/'SELECTED_RESULTS_SUMMARY.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
# The concise diagnostic deliverable contains only returned flattened diagnose_sppr fields.
lines=['# SPPR diagnostics — selected Buchary model','']
for h in health:
 lines+=['## '+str(h['TE_option']),'','| Returned field | Value |','|---|---|']
 for key,value in h.items():
  if value is not None:lines.append('| '+str(key)+' | '+str(value).replace('|','\\|').replace('\n','<br>')+' |')
 lines.append('')
(dest/'SPPR_DIAGNOSTICS.md').write_text('\n'.join(lines),encoding='utf8')
(ev/'DIAGNOSE_SPPR_RETURNED_FIELDS.json').write_text(json.dumps(health,indent=2),encoding='utf8')
lines=['# Selected model: Buchary1999, Java Sea mid-1970s','',f'**Selected:** `{mid}`. User rationale: **best available model**. The original source-faithful model38001 is preserved; Nurhakim38002 remains an unselected, blocked later-test candidate.','',
'This is a user-authorized computational variant. Macrozoobenthos existing diet fractions were divided by0.660 (factor1.5151515151515151); no omitted prey was recovered or invented. All28 signed loader-completed BA values were stored explicitly as computed values. Source BA remains unknown in the source canonical JSON. No other source numeric parameters were edited. Exact reload comparison across29 rows and18 state/flow fields found zero differences at relative1e-10/absolute1e-9 tolerance. Existing basal/default-migration conventions remain documented in DERIVED_RELOAD_VALIDATION.json.','',
'The source article covers Java Sea approximately471000km², not the full Indonesian Sea LME. The mid-1970s food web is extrapolated through1950–2019. Neither the old36% coverage estimate nor numerical equivalence to EcoBase410 is verified. Source fleet/discard splits are absent; original Harvest includes an assumed LBS bycatch proxy. Model group catch enters only explicit stage-weight proxies; regional PPR uses independent local Sea Around Us catch bases.','',
'## Numerical decisions and scope','',
'The fresh bounded run completed22 methods,180seconds allowed per method. GE and With Egestion are OK; TE is WARN, with Marine mammals TE approximately0.0008469558 (inverse1180.6997). This is a near-zero transfer-efficiency warning, not network divergence. Computational method status `ok` means a result returned; it does not erase the TE warning or validate printed source data. The concise [SPPR diagnostic report](SPPR_DIAGNOSTICS.md) contains only returned diagnose_sppr fields for GE, TE and With Egestion; no global summary configuration is added.','',
'No negative available all/inner/PP group coefficient occurred, including all28 biological groups and6 unfished groups (Import is a separate29th bookkeeping row). All three diagnostic configurations report0 negative source columns. Other methods lack retained full source matrices, so their per-source signs are not claimed. Scalar1986/1995 methods do not have PP decompositions.','',
'| Method | Run outcome |','|---|---|']
for r in methods:lines.append(f"| {r['topic'].removeprefix('method: ')} | {r['status']} |")
lines+=['','Monte Carlo used100 draws per configuration,10% TE error,20% cutoff, kind=new, exclude_diverged=True; TE fixesEE=0. No explicit seed: this is the fresh selected realization.','', '| Method | Draws | Accepted | Rejected negative | Rejected divergent |','|---|---:|---:|---:|---:|']
for r in mc:lines.append(f"| {r['method']} | {r['n_samples']} | {r['n_accepted']} | {r['n_rejected_negative']} | {r['n_rejected_diverged']} |")
lines+=['','## Every signed BA completion','', 'Units t/km²/year; source value unknown in every row. Seventeen are negative, including tiny rounding residuals and material values. These signed values reconcile loaded budgets; they do not establish biomass decline or gain. Diet normalization was not isolated as the sole cause.','', '| Group | Computational BA |','|---|---:|']
for r in ba:lines.append(f"| {r['seq']} {r['group']} | {float(r['derived']):.15g} |")
lines+=['','## Catch matching and annual calculation','',f"All181 catch taxa reviewed: {coverage['resolved']} mapped, {coverage['unresolved']} unresolved. All numeric weights sum1 and exact group identifiers are checked. Stage pairs use printed group Harvest shares. Coarse pools use fixed1950–2019 identified total-catch composition after direct/stage assignments; no circular coarse allocation. SAU functional class narrows unidentified marine fish to Small/Medium demersals, Decapoda to Crabs + Lobsters, and residual crustaceans to shrimp stages. Source specific membership overrides broad guild labels; Acetes/Sergestidae maps to source group4, which explicitly contains sergestids and reports harvest. Netuma follows source Arius thalassinus via WoRMS synonym evidence. Full decisions and citations are in evidence/CATCH_MAPPING.csv and MAPPING_DECISIONS.json.",'', '|2019 basis|Total tonnes|Mapped tonnes|Coverage|','|---|---:|---:|---:|']
for basis,rr in coverage['coverage'].items():
 r=rr['2019'];lines.append(f"|{basis}|{r['total_tonnes']:.3f}|{r['mapped_tonnes']:.3f}|{100*r['coverage_fraction']:.3f}%|")
lines+=['','Largest unresolved2019 catch:','']
for r in coverage['unresolved_by_2019_catch'][:8]:lines.append(f"- {r['taxon']}: {r['tonnes2019']:.3f}t.")
lines+=['','Annual results cover1950–2019, three catch bases and explicit unidentified treatments. Below are total-source PPR values for method treatment; unresolved taxa contribute missing coefficients, so these are covered-catch estimates, not complete catch totals. TE estimates remain warning-qualified.','', '|Method|Basis|1950 PPR wet tonnes|2019 PPR wet tonnes|','|---|---|---:|---:|']
for r in selected_metrics:lines.append(f"|{r['method']}|{r['catch_basis']}|{r[1950]:.6g}|{r[2019]:.6g}|")
lines+=['','PPR/NPP divides wet-equivalent PPR by9 exactly once. Existing ensemble-median NPP2019 is749758870.0793715tC/year. No new NPP extraction; algorithms and available years are retained, all missing years stay blank.','', '|Method|2019 landings PPR/NPP ensemble median|','|---|---:|']
for r in ratios:lines.append(f"|{r['method']}|{r[2019]:.6g}%|")
lines+=['','## Verification and provenance','',
'Regional bounded prepare-selection, sppr, calculate and validate completed. Original regional workbook preserved in evidence/LME_038_before_user_selection.xlsx and models/previous_results. Source and derived hashes, exact28 signed changes, loader comparison, mappings, code snapshot and fresh SPPR workbook retained. Source diagnostics remain historical evidence; they were not substituted for this fresh selected run. Central selection is generated from regional Overview; all other regions and native tables are protected by the integration audit. Map refresh is coordinated separately by the parent task.','',f"Source SHA256: `{out['source_sha256']}`. Derived SHA256: `{out['model_sha256']}`."]
(dest/'SELECTED_MODEL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
# Retain the preselection report, then make current decision explicit at its entry point.
main=OUT/'EXTRACTION_AND_SPPR_REPORT.md';historic=OUT/'EXTRACTION_PRESELECTION_REPORT.md'
if not historic.exists():shutil.copy2(main,historic)
text=historic.read_text(encoding='utf8');intro=f'''# LME038 extraction and selection decisions — 28 September2026

**Current selection:** [{mid}](../{mid}/SELECTED_MODEL_REPORT.md), reason **best available model**, with user-authorized diet normalization and all28 computational BA completions. The source-faithful38001 is unchanged; Nurhakim38002 remains blocked and unselected for later tests.

The concise [SPPR diagnostics](../{mid}/SPPR_DIAGNOSTICS.md) contains only direct flattened diagnose_sppr return fields for GE, TE and With Egestion. Extraction, all22 method outcomes, MC, transformations, mapping and annual estimates are retained separately in the selected-model decisions report. TE WARN remains visible.

The remainder below is the preserved **preselection source assessment**, not the current selection state. Statements that no production selection or matching changed describe that earlier assessment. Current regional results and provenance supersede those historical status statements.

---

'''
main.write_text(intro+text,encoding='utf8')
summary=json.loads((OUT/'SPPR_RESULTS_SUMMARY.json').read_text(encoding='utf8'));summary['current_selected_variant']=out;summary['registration']='Source candidates preserved;38003 user-selected derived model, central integration audited separately';(OUT/'SPPR_RESULTS_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf8')
# Preserve exact current executed code, with portable hashes.
code=dest/'diagnostic_code';hashes={}
for p in list((ROOT/'tools/scientific_code/PPREstimation').glob('*.py'))+[ROOT/'tools'/n for n in ['run_region.py','regional.py','workbooks.py']]+[ROOT/'tools/scientific_helpers/ppr_scopes.py']:
 rel=p.relative_to(ROOT/'tools');target=code/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);hashes[target.relative_to(ROOT).as_posix()]=sha(target)
hashes[(dest/'model.json').relative_to(ROOT).as_posix()]=sha(dest/'model.json');(ev/'executed_code_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
print(json.dumps({'selected':mid,'methods':len(methods),'health':[(h['TE_option'],h['status']) for h in health],'mc':mc,'metrics':selected_metrics,'ratios2019':[{r['method']:r[2019]} for r in ratios],'coverage':coverage['coverage'],'reports_saved':True},indent=2))

