from pathlib import Path
import json,shutil
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists());OUT=Path(__file__).parent;MODELS=ROOT/'regions/LME_049/models'
orig='49_20192013_Western_North_Pacific_Watari_(2013)';chen='49_20252023_Kuroshio_Oyashio_Extension_Chen_(2023)';chosen='49_2019201301_Watari_Detritus_Pooled_Experiment_(2013)';opts=['GE','TE','With Egestion']
previous_raw=OUT/'DIAGNOSE_SPPR_RESULTS.json';all_called_archive=OUT/'DIAGNOSE_SPPR_ALL_CALLED_OPTIONS_ARCHIVE.json'
if previous_raw.exists() and not all_called_archive.exists():shutil.copy2(previous_raw,all_called_archive)
raw={};summary=[]
for mid in [chosen,chen]:
    raw[mid]={o:json.loads((MODELS/mid/'evidence'/('diagnose_sppr_'+o.replace(' ','_')+'.json')).read_text()) for o in opts}
    for o,entry in raw[mid].items():
        r=entry['direct_diagnose_sppr_return'];summary.append([mid,o,r['status'] if r else 'EXCEPTION — no return',r['divergence']['rho_living'] if r else None,r['divergence']['b'] if r else None,r['divergence']['n_negative_sources'] if r else None,r['balance']['rel_gap'] if r and r['balance'] else None])
(OUT/'DIAGNOSE_SPPR_RESULTS.json').write_text(json.dumps({'original_41_group':{'model_id':orig,'load_status':'blocked','diagnose_sppr_executed':False,'reason':'missing detritus routing for groups39,40,41'},'direct_calls':raw},ensure_ascii=False,indent=2),encoding='utf-8')
def fmt(x):
    if x is None:return 'null'
    if isinstance(x,bool):return 'true' if x else 'false'
    if isinstance(x,(list,dict)):return '`'+json.dumps(x,ensure_ascii=False)+'`'
    return str(x).replace('|','/')
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|',*['| '+' | '.join(fmt(x) for x in r)+' |' for r in rows]])
label={'status':'Status','is_model_balanced':'Ecopath identities balanced','p_max_rel_residual':'Production maximum relative residual','q_max_rel_residual':'Consumption maximum relative residual','dc_rows_sum_to_1':'Diet rows sum to one','dc_max_deviation':'Maximum diet-sum deviation','n_negative_catch':'Negative-catch groups','n_zero_catch':'Zero-catch groups','total_catch':'Total source-model catch','has_catch':'Has catch','has_ee_issues':'Has EE issues','n_ee0':'EE-zero count','n_ee_marginal':'Marginal-EE count','n_ee_gt_1':'EE-above-one count','ee0_groups':'EE-zero groups','ee_marginal_groups':'Marginal-EE groups','solve_error':'Solve error','b':'Recycling gain b','b_converges':'Recycling converges','rho_living':'Living spectral radius','living_converges':'Living network converges','sppr_det':'Detritus coefficients by group','max_sppr_det':'Maximum detritus coefficient','max_sppr_group':'Maximum-SPPR group (seq, TL, SPPR, inverse TE)','max_tl_group':'Maximum-TL group (seq, TL, SPPR, inverse TE)','n_negative_sources':'Basal-source columns containing negatives','expect_negatives':'Negatives predicted from recycling','near_singular_te':'Near-singular TE groups','is_balanced':'Strict SPPR balance','inflow':'PP inflow','outflow':'SPPR-weighted outflow','rel_gap':'Relative SPPR balance gap'}
parts=['# LME049 — direct SPPR diagnostics','Only results returned by `PPRCalculator.diagnose_sppr(short=False, flat=False, return_sppr=False)` are shown below, for GE, TE and With Egestion. Calls use the same loader-completed model state and closed-detritus configuration as the retained diagnostics.','[Full returned data](DIAGNOSE_SPPR_RESULTS.json) · [Caller/settings provenance](DIRECT_DIAGNOSE_PROVENANCE.json)','## Summary',table(['Model','TE option','Returned status','Living spectral radius','Recycling gain b','Negative basal-source columns','Relative balance gap'],summary),'## Original Watari — 41 groups',f'`{orig}`: loading is blocked by absent detritus routing for groups39,40,41. No `diagnose_sppr()` result exists.']
for mid,title in [(chosen,'Selected Watari detritus-pooling variant — 39 groups'),(chen,'Chen source candidate — 25 groups')]:
    results={o:raw[mid][o]['direct_diagnose_sppr_return'] for o in opts[:3]};parts.extend(['## '+title,'`'+mid+'`'])
    for section,name in [('config','Returned configuration'),('model_input','Model input'),('divergence','Convergence and coefficients'),('balance','SPPR balance'),('footprint','Returned footprint (ungraded)')]:
        keys=list(dict.fromkeys(k for r in results.values() for k in (r.get(section) or {})))
        parts.extend(['### '+name,table(['Returned field','GE','TE','With Egestion'],[[label.get(k,k),*[results[o].get(section,{}).get(k) if results[o].get(section) else None for o in opts[:3]]] for k in keys])])
    parts.append('### Returned warnings')
    for o in opts[:3]:
        warnings=results[o]['warnings'];parts.append('**'+o+'**\n\n'+('\n'.join('- '+w for w in warnings) if warnings else 'None (`[]`).'))
report='\n\n'.join(parts)+'\n';old=OUT/'EXTRACTION_AND_SPPR_REPORT.md';arch=OUT/'EXTRACTION_AND_FULL_METHOD_EVIDENCE_20260928.md'
if not arch.exists():shutil.copy2(old,arch)
old.write_text(report,encoding='utf-8');(OUT/'SPPR_DIAGNOSTICS_REPORT.md').write_text(report,encoding='utf-8')
# Historic detailed evidence remains available with a clear current selection note.
text=arch.read_text(encoding='utf-8');note='> Selection update, 2026-09-28: the user subsequently selected `'+chosen+'`. Earlier "unselected" statements below describe the diagnostic run at that time. Scientific limitations remain; the deferred TE investigation is recorded in the separate DECISIONS_AND_LIMITATIONS.md. This is retained research evidence; the current SPPR report contains only direct diagnose_sppr outputs.\n\n'
if not text.startswith('> Selection update'):arch.write_text(note+text,encoding='utf-8')
print(json.dumps(summary,indent=2))
