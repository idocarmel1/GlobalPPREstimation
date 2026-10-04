from pathlib import Path
import json,shutil,hashlib,csv
import pandas as pd
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
MID='941_20190101_Warm_Pool_Detritus_Pooled_Experiment_(2005)';OUT=ROOT/'regions/EEZ_941/models'/MID;DIAG=OUT/'diagnostics';EV=OUT/'evidence'
def dump(p,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False,default=str)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(BASE/'GRIFFITHS_ROUTING_SEARCH_20260928.md',EV/'ONLINE_ROUTING_SEARCH.md')
src=pd.read_csv(DIAG/'loaded_diet.csv',index_col=0);loaded=pd.read_csv(DIAG/'_DC_after_completion.csv',index_col=0)
changes=[]
for i in src.index:
    for j in src.columns:
        a=src.loc[i,j];b=loaded.loc[i,j]
        if pd.isna(a) or a!=b:changes.append({'predator':int(i),'prey':int(j),'before':None if pd.isna(a) else a,'loaded':b,'reason':'unknown import becomes zero' if pd.isna(a) else 'documented consumer row normalization'})
dump(EV/'LOADER_DIET_TRANSFORMATIONS.json',changes)
g=pd.read_csv(DIAG/'_groups_df_after_completion.csv',index_col=0)
audit={'canonical_diet_normalized':False,'runtime_normalize_DC':True,'unknown_import_handling':'normalize_DC=True fills synthetic import-column NaNs with zero; source remains unknown.','consumer_GS':'default_gs=True fills missing regular groups with 0.2; named small-zooplankton whitelist receives 0.4 if matched. These are engine assumptions.','consumer_GS_values':g.loc[g.trophic_info=='Regular',['group_name','gs']].to_dict('index'),'detritus_runtime':g.loc[45].to_dict(),'detritus_transformations':['Closed sole-pool fate: every living group routes 1 to pool45.','Engine sets detritus EE=1 and M0/egestion=0.','Engine replaces source zero detritus BA with net inflow minus predation (pool accumulation); source JSON BA remains zero.','Pool production and consumption derive from natural M0 plus egestion; fleet returns are not included.'],'catch':'Exact source fleet landings plus discards in export; unspecified catches default zero. No catch-total repairs.','net_migration':'Explicit source net migration=0 assigned to ModelData; separate gross rates unknown in source but engine defaults zero.','habitat':'No new habitat rescaling','scope':'Computational loaded experiment, not validation of original Ecopath balance.'}
dump(EV/'LOADER_TRANSFORMATIONS.json',audit)
hist=BASE/'history_before_pooled_experiment';hist.mkdir(exist_ok=True)
for n in ['GRIFFITHS_VS_WCP_OPTION1.md','PACIFIC_PAPER_COMPARISON.md','PROGRESS_STATUS.json','REGISTRATION_PROPOSAL.json','MASTER_INDEX.md']:
    if not (hist/n).exists():shutil.copy2(BASE/n,hist/n)
results=json.loads((DIAG/'DIRECT_DIAGNOSTICS.json').read_text(encoding='utf-8'))
assert set(results)=={'GE','TE','With Egestion'}
assert all(r['status']=='FAIL' for r in results.values())
benchmark=ROOT/'regions/EEZ_941/models/941_200701_WCPO_Warm_Pool_Final_(mixed_periods)/balance_investigation/correction_scenarios/D_fixed_M0'
wcp={o:json.loads((benchmark/('diagnose_'+o.replace(' ','_')+'.json')).read_text(encoding='utf-8')) for o in results}
assert all(r['status']=='WARN' for r in wcp.values())
comparison={o:{'Griffiths_pooled':{'status':results[o]['status'],'PP_budget':results[o]['balance'],'model_input':results[o]['model_input']},'WCP_option1_D':{'status':wcp[o]['status'],'PP_budget':wcp[o]['balance'],'model_input':wcp[o]['model_input']}} for o in results}
dump(BASE/'POOLED_VS_WCP_OPTION1_COMPARISON.json',comparison)
rows='\n'.join(f"| {o} | **{results[o]['status']}** | {results[o]['balance']['status']}; {100*results[o]['balance']['rel_gap']:.6f}% | **{wcp[o]['status']}** | {wcp[o]['balance']['status']}; {100*wcp[o]['balance']['rel_gap']:.6f}% |" for o in results)
report=f'''# Griffiths2019 pooled experiment versus WCP2007 option 1

**Pooling allows Griffiths2019 to run, but all three requested diagnostics return FAIL. WCP2007 option 1 (D_fixed_M0) remains WARN for all three.** Pooling therefore does not resolve the reason to prefer further examination of WCP option 1 over adopting this Griffiths reconstruction. Neither model has been selected.

| Direct method | Griffiths pooled overall | Griffiths PP budget; relative gap | WCP option 1 overall | WCP PP budget; relative gap |
|---|---|---|---|---|
{rows}

These are full direct `diagnose_sppr(TE_option=..., short=False, flat=False)` returns. No global method, annual PPR calculation, or model selection was performed. The original 46-group Griffiths model remains NOT_RUN_LOADER_BLOCKED because its two-pool routing is unknown. The table concerns only the separately authorized 45-group experiment. With Egestion's PP-budget status is OK under its threshold although its raw `is_balanced` flag is false; the overall model-input FAIL remains decisive.

## Why the pooled experiment still fails

The maximum production residual in the loaded normalized-diet experiment is **7128.367912%** of group production; the maximum consumption residual is **780.840301%**. All solves converge and produce zero negative source columns, but convergence does not validate the inputs. All three also warn about the living food-web amplification and near-zero seabird efficiency; GE and With Egestion warn about the recycling amplification.

The independent source-only equation already identifies the major contradiction: Pomfret production is 0.000294752 and production times EE is 0.0002800144 t/km²/year, while the exact final S3 diet implies predation 0.02128530003 before catch. Its source-equation residual is 7128.07195%. Large yellowfin consumption alone is about 19.92 times the printed Pomfret production. The small difference between this source residual and the diagnostic residual comes from documented runtime normalization; neither value was repaired. Source and loaded residuals should not be conflated.

Final S3 contains 46 prey by 42 consumers, with all 567 nonzero cells independently matching DOCX and rendered PDF coordinates. All 172 nonblank S4 fleet/total cells also match. Twenty-two printed totals disagree with their fleet components; exact components were retained, with total removals 0.033458867 t/km²/year. Main-paper ocean area is 11,543,000 km², while S1 catch derivations repeatedly use 12,086,900 km² and initial discard biomass uses 12,555,000 km². No density rescaling or catch repair was made. Initial diet S2 was excluded.

## What was authorized and what the loader did

The online routing review covered the publisher's sole Appendix S1–S4, author-posted appendix, primary institutional record, BMIS manuscript and EcoBase catalogue/native links. No recoverable exact-model numerical split was found in those available sources; this is a scoped finding, not proof of universal absence. Full URLs, findings and access limits are in `GRIFFITHS_ROUTING_SEARCH_20260928.md`.

Only source group45 Detritus and group46 Fishery discards were merged. Their known biomasses sum to **53.001775 t/km²**; each consumer's two prey proportions were summed exactly. All 42 original consumer diet sums and scalar biological/catch/taxonomy inputs are preserved in the experimental canonical, and both phytoplankton groups are unchanged. Pooled EE was left unknown, never averaged. The original 46-group canonical SHA256 remains `523cefaa423538f0609b96b75064594f426d87c8dca997a7973515792c1bafc3`.

The computational run uses the documented single-pool closed fate default, GS defaults, zero unspecified catches/imports, and normalized rounded diets, matching the benchmark's normalization convention. The first exact-diet runtime attempt is separately preserved: unknown synthetic import entries propagated NaN into basal-row detection and caused a KeyError before any return. The existing normalize_DC=True path resolves this without editing engine code. Every runtime diet change is recorded separately from source extraction.

The loader also sets detritus EE=1 and **replaces the source detritus BA=0 with derived accumulation**, approximately {g.loc[45,'biomass_accum']:.6f} t/km²/year. Thus the successful run is a computational sensitivity model, not an exact steady-state reproduction. No source BA cell was changed. The pooled representation loses the separate suspended-discard pathway: routing applies natural other mortality plus egestion, and the engine does not separately return fleet discards to the pool. Catch export includes both retained and discarded removals. This limitation is not solved by pooling.

## Benchmark identity and regional choice

Option 1 is **D_fixed_M0**, not A_fixed_EE and not unchanged WCP2007. It preserves original juvenile other mortality while increasing juvenile production: small bigeye PB1.4129713563375232 / EE0.7898725981469387, small yellowfin PB2.5304972811160384 / EE0.8816702937266387. It remains an experimental correction without native multistanza validation. Its maximum production residual is approximately 0.727940% (adult bigeye); all PP-budget checks are OK. The exact saved direct returns were reused without rerunning WCP.

| Region | Griffiths source-domain target coverage | WCP2007 source-domain target coverage |
|---|---:|---:|
| HS_071 |29.09639%|57.57808%|
| EEZ_941 Kiribati Gilbert Islands |99.71577%|99.71577%|
| EEZ_598 Papua New Guinea |99.79181%|100.00000%|

These intersections use actual stored regional polygons and the stated study domains; evidence is in SPATIAL_OVERLAP.json. WCP-2007 already serves as a shared paper for EEZ_598. Later selection should review all three regions jointly. The EEZ_941 archive home is retained; it was chosen when comparing the first two regions, not as a claim that Papua New Guinea is less applicable. Only 9.07086% of Griffiths' reported ocean model area falls within EEZ_941 and 20.73849% within EEZ_598. These are broad pelagic proxies and do not establish coastal/reef representativeness.

For HS_071, WCP has substantially greater coverage, though neither spans the full target. For both EEZs, coverage is similarly high, and the present diagnostic evidence favors WCP option1 for further scrutiny. This is evidence for the user's later decision, not adoption. Do not rank the models by total PPR: their area, year, catch and group structure differ; Griffiths' returned footprints are outputs of a failed input model.

Allain2021 remains a separately archived 65-group, 2013 model. Its verified four-page report and associated context document lack the full numerical inputs required for reconstruction; it remains NOT_RUN, without substitution of older models. Its separately verified coverage is 74.48550% of HS_071 and 100% of EEZ_941; EEZ_598 applicability was not extrapolated.

## Reusable artifacts

Original Griffiths: `regions/EEZ_941/models/941_201901_Warm_Pool_(2005)` (46-group canonical, eight imports, taxonomy, cell evidence, source checks and original admission block).

Pooled experiment: `regions/EEZ_941/models/{MID}` (45-group canonical, eight imports, taxonomy, canonical reconstruction, changes-only audit, full raw direct diagnostic JSON, frozen executed code, runtime transformations and preserved exception attempt).

The diagnostic JSON files contain only direct diagnostic output. Extraction, assumptions and comparison are separate. Previous blocked reports are preserved under `history_before_pooled_experiment`, alongside the pre-supplement history. No central workbook writes were made.
'''
(BASE/'GRIFFITHS_VS_WCP_OPTION1.md').write_text(report,encoding='utf-8')
(OUT/'MODEL_PROFILE.md').write_text(report,encoding='utf-8')
(BASE/'PACIFIC_PAPER_COMPARISON.md').write_text('# Pacific paper review\n\nCurrent completed comparison: [Griffiths pooled versus WCP option1](GRIFFITHS_VS_WCP_OPTION1.md). Griffiths authorized pooled experiment returns FAIL in all three direct methods; WCP2007 D_fixed_M0 returns WARN in all three. Original Griffiths 46-group source remains routing-blocked. Allain2021 remains source-data-incomplete. No model selection or annual PPR publication was made.\n\nReview HS_071, EEZ_941 and EEZ_598 jointly before later selection; WCP-2007 is already shared with EEZ_598.\n',encoding='utf-8')
status=json.loads((BASE/'PROGRESS_STATUS.json').read_text(encoding='utf-8'))
status.update(stage='authorized_pooled_experiment_and_comparison_complete',pooled_experiment={'model_id':MID,'load_status':'LOADED','diagnostic_status':{o:r['status'] for o,r in results.items()},'source_unchanged':True,'selection':'none','global_excluded':True},next_evidence='Native source model or author-supported resolution of biological and catch contradictions; no further unapproved repairs.')
dump(BASE/'PROGRESS_STATUS.json',status)
proposal=json.loads((BASE/'REGISTRATION_PROPOSAL.json').read_text(encoding='utf-8'));proposal['pooled_experiment']={'model_id':MID,'parent_model_id':'941_201901_Warm_Pool_(2005)','group_count':45,'status':'EXPERIMENT_FAIL_ALL_THREE','selected':False,'model_path':str((OUT/'model.json').relative_to(ROOT)),'diagnostic_path':str(DIAG.relative_to(ROOT)),'report':str((BASE/'GRIFFITHS_VS_WCP_OPTION1.md').relative_to(ROOT)),'later_selection_regions':['HS_071','EEZ_941','EEZ_598']};dump(BASE/'REGISTRATION_PROPOSAL.json',proposal)
(BASE/'MASTER_INDEX.md').write_text('# Current review index\n\n- Griffiths2019 source: extracted 46-group canonical; missing two-pool routing and source imbalance.\n- Griffiths2019 authorized pooled experiment: 45 groups; loaded; GE/TE/With Egestion all FAIL.\n- WCP2007 option1 D_fixed_M0: saved GE/TE/With Egestion all WARN; no adoption.\n- Allain2021: archived complete report; full numerical inputs missing; NOT_RUN.\n\nSee GRIFFITHS_VS_WCP_OPTION1.md for the completed comparison and provenance. HS_071, EEZ_941 and EEZ_598 remain a joint later selection decision.\n',encoding='utf-8')
print(json.dumps({o:r['status'] for o,r in results.items()},indent=2))
dump(EV/'ARTIFACT_MANIFEST.json',{'files':[{'path':str(p.relative_to(OUT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in OUT.rglob('*') if p.is_file() and p.name!='ARTIFACT_MANIFEST.json']})
