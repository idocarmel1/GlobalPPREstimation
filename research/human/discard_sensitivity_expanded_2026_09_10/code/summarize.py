"""Validated postprocessing, fixed-support aggregates and compact report interface."""
from pathlib import Path
from collections import defaultdict,Counter
import json,csv,hashlib,gzip,base64
import numpy as np
import pandas as pd
from baseline import ROOT,FRACTIONS,METHODS,SCOPES
from metrics import decompose
from run_study import clean,write_json
from provenance import fingerprint

NEW=['new_GE','new_TE_EEfix','new_WithEgestion']
FIELDS=['model_id','method','scope','route','fraction','status','valid','ppr_fixed_H_tC','ppr_retained_L_tC',
        'baseline_ppr_fixed_H_tC','baseline_ppr_retained_L_tC','coefficient_change_pct','retained_change_pct',
        'standard_relative_excess_pct','ppr_to_native_pp_pct','ppr_retained_to_native_pp_pct','native_denominator_compatible',
        'coefficient_effect','catch_effect','interaction','total_change','reasons','diagnostics','vector_id']

def saved_checks(study):
    meta=study['models'][0];mid=meta['model_id'];book=ROOT/'inputs/workbooks'/f'{mid}.xlsx'
    if not book.exists():return study
    digest=hashlib.sha256(book.read_bytes()).hexdigest();meta['source_workbook_sha256']=digest
    meta['baseline_validation']='Existing saved workbook plus fresh unmodified frozen-calculator/zero-discard equality and independent analytic/conservation checks.'
    study['baseline_checks']=[c for c in study['baseline_checks'] if c.get('provenance')=='fresh_unmodified_vs_adapter']
    for scope in SCOPES:
        saved=pd.read_excel(book,'sppr_'+scope).set_index('seq')
        for r in study['records']:
            if r['route']!='S0' or r['scope']!=scope or r['method'] not in saved:continue
            groups=study['groups'].get(r['scenario_id'],[])
            if not groups:continue
            fresh=pd.Series({g['group_id']:g['sppr'] for g in groups},dtype=float);expect=saved[r['method']].reindex(fresh.index)
            mask=np.isfinite(fresh)&np.isfinite(expect);diff=(fresh[mask]-expect[mask]).abs()
            study['baseline_checks'].append(dict(model_id=mid,method=r['method'],scope=scope,provenance='existing_saved_workbook',
                passed=None if not np.isfinite(expect).any() else bool(mask.any() and np.array_equal(np.isfinite(fresh),np.isfinite(expect)) and np.allclose(fresh[mask],expect[mask],rtol=2e-7,atol=1e-7)),
                reason='Saved method/scope block has no finite coefficients; fresh baseline remains independently audited' if not np.isfinite(expect).any() else None,
                finite_mask_matches=bool(np.array_equal(np.isfinite(fresh),np.isfinite(expect))),
                compared_groups=int(mask.sum()),max_absolute_error=float(diff.max()) if mask.any() else None,
                source_workbook_sha256=digest,tolerance='atol=1e-7 + rtol=2e-7*abs(saved)'))
    for r in study['records']:r['source_workbook_sha256']=digest
    return study

def finalize_model(study):
    meta=study['models'][0];records=study['records'];denom=meta['denominator_value'];imports=meta['native_import_production_tC']
    for r in records:
        gap=r['diagnostics'].get('ledger_sppr_relative_gap')
        conservation=None if r['method'] not in NEW or gap is None else gap<=.05
        r['method_conservation_valid']=conservation
        if conservation is False:
            r['valid']=False;r['status']='invalid_method_conservation'
            reason='Method PP-equivalent export identity exceeds the frozen 5% failure threshold'
            if reason not in r['reasons']:r['reasons'].append(reason)
        if not r['valid']:
            for f in ['ppr_fixed_H_tC','ppr_retained_L_tC','standard_relative_excess_pct','standard_absolute_difference_tC']:r[f]=None
        r['native_denominator_compatible']=not(r['scope']=='all' and imports>0)
        r['native_ratio_reason']=None if r['native_denominator_compatible'] else 'All-source numerator includes imports; internal PP denominator has a different source boundary'
        for value,field in [('ppr_fixed_H_tC','ppr_to_native_pp_pct'),('ppr_retained_L_tC','ppr_retained_to_native_pp_pct')]:
            r[field]=100*r[value]/denom if r['native_denominator_compatible'] and r[value] is not None and denom>0 else None
    bases={(r['method'],r['scope']):r for r in records if r['route']=='S0'}
    for r in records:
        b=bases[r['method'],r['scope']];baseline=b['ppr_fixed_H_tC'] if b['valid'] else None
        r['baseline_ppr_fixed_H_tC']=baseline;r['baseline_ppr_retained_L_tC']=baseline*(1-r['fraction']) if baseline is not None else None
        r['decomposition']=decompose(baseline,r['ppr_fixed_H_tC'],r['baseline_ppr_retained_L_tC'],r['ppr_retained_L_tC'])
        r['coefficient_change_pct']=100*(r['ppr_fixed_H_tC']/baseline-1) if baseline and r['ppr_fixed_H_tC'] is not None else None
        r['retained_change_pct']=100*(r['ppr_retained_L_tC']/baseline-1) if baseline and r['ppr_retained_L_tC'] is not None else None
        r['paired_baseline_valid']=b['valid'];r['cohort']=meta['cohort']
    return study

def distribution(values):
    if not values:return dict(min=None,p10=None,p25=None,median=None,p75=None,p90=None,max=None,mean=None)
    a=np.asarray(values,float);return dict(zip(['min','p10','p25','median','p75','p90','max'],map(float,np.quantile(a,[0,.1,.25,.5,.75,.9,1]))),mean=float(a.mean()))

def summarize():
    old=json.loads((ROOT/'inputs/original_results/study.json').read_text(encoding='utf-8'));oldmap={r['scenario_id']:r for r in old['records']}
    allrows=[];models=[];compact=[];vectors=[];vseen={};groupmeta={};checks=[];overlap=[];envs=[];decomps=[];responses=[];screen=json.loads((ROOT/'results/candidate_screening.json').read_text(encoding='utf-8'))
    selected={r['model_id']:r for r in json.loads((ROOT/'results/selected_models.json').read_text(encoding='utf-8'))}
    excluded=[r for r in screen['candidates'] if r['status']=='rejected_source_fidelity']
    family_counts=Counter(r['metadata'].get('model_name',r['model_id']) for r in selected.values())
    replay_path=ROOT/'verification/saved_workbook_differences.json'
    replay={x['model_id']:x for x in json.loads(replay_path.read_text(encoding='utf-8'))} if replay_path.exists() else {}
    totals=Counter();groupcsv=ROOT/'results/group_sppr.csv'
    groupfields=['scenario_id','model_id','method','scope','route','fraction','valid','group_id','name','sppr','H','L','trophic_info','contribution_H_tC','contribution_L_tC']
    with groupcsv.open('w',encoding='utf-8',newline='') as gf:
        gw=csv.DictWriter(gf,fieldnames=groupfields,extrasaction='ignore');gw.writeheader()
        for path in sorted((ROOT/'results/models').glob('*/study.json')):
            study=finalize_model(saved_checks(json.loads(path.read_text(encoding='utf-8'))));meta=study['models'][0];mid=meta['model_id']
            if meta['cohort']=='additional':
                source=selected[mid];family=source['metadata'].get('model_name',mid)
                meta.update(source_screening=source['screening'],selection_rank=source['selection_rank'],ecosystem_family=family,
                    ecosystem_family_case_count=family_counts[family],detritus_fate_class=source['screening']['detritus_source_checks']['fate_class'],
                    source_validity='eligible_under_source_fidelity_revision_2')
                meta['limitations'] += ['Detritus zero-row to identity changes are bookkeeping only; nonzero overwritten source fates and unsupplied baseline stock draw are excluded.',
                    'Time models from the same named ecosystem are dependent observations, not independent ecosystems.']
            differences=[]
            for c in study['baseline_checks']:
                if c.get('provenance')=='existing_saved_workbook' and c['passed'] is False:
                    rc=next((x for x in replay.get(mid,{}).get('checks',[]) if x['method']==c['method'] and x['scope']==c['scope']),{})
                    c['configuration_difference_verified']=rc.get('reproduced',False)
                    c['difference_reason']='The existing workbook uses unnormalized source diet rows; replay with normalize_DC=False reproduces it. The experiment keeps original-study normalize_DC=True within the recorded source-rounding tolerance.' if c['configuration_difference_verified'] else 'Saved coefficient difference remains unresolved; fresh unmodified-calculator validation is separate.'
                    differences.append({k:c[k] for k in ['method','scope','configuration_difference_verified','difference_reason','max_absolute_error']})
            meta['saved_workbook_differences']=differences
            if differences:meta['baseline_validation']+=' Saved differences are explicitly retained; see normalization replay provenance.'
            models.append(meta);checks+=study['baseline_checks']
            original_file_digest=hashlib.sha256(path.read_bytes()).hexdigest()
            write_json(path.parent/'study.validated.json',study)
            source_path=next((ROOT/x['snapshot_path'] for x in screen['candidates'] if x['model_id']==mid and meta['cohort']=='additional'),ROOT/'inputs/references'/f'{mid}.json')
            write_json(path.parent/'calculation_provenance.json',fingerprint(source_path))
            records=study['records'];groups=study['groups'];bykey=defaultdict(list)
            basegroups=next((groups[r['scenario_id']] for r in records if r['route']=='S0' and r['method']=='standard_fixed_baseline_TL' and r['scope']=='all'),[])
            groupmeta[mid]=[{k:g[k] for k in ['group_id','name','H','trophic_info']} for g in basegroups]
            response=dict(model_id=mid,cohort=meta['cohort'],source_json_sha256=meta['source_json_sha256'],source_workbook_sha256=meta['source_workbook_sha256'],
                ecological_sha256=meta.get('ecological_sha256'),group_identity=groupmeta[mid],status='not_assessed_zero_harvest' if meta['native_harvest']==0 else 'tested_constrained_accounting',methods={})
            for r in records:
                sid=r['scenario_id'];g=groups.get(sid,[]);coeff=[x['sppr'] for x in g] if g else None
                if coeff is not None:
                    key=(mid,json.dumps(coeff,separators=(',',':')))
                    if key not in vseen:vseen[key]=len(vectors);vectors.append(coeff)
                    vid=vseen[key]
                else:vid=None
                relevant={k:r['diagnostics'].get(k) for k in ['catch_weight_mode','max_living_production_relative_residual','max_consumption_relative_residual','whole_system_relative_residual','max_detritus_residual','negative_physical_flows','rho_living','rho_detritus','ledger_sppr_relative_gap','nonfinite_cells','negative_source_cells']}
                c={**r,**r['decomposition'],'vector_id':vid,'diagnostics':relevant}
                compact.append([c.get(k) for k in FIELDS])
                flat={k:v for k,v in r.items() if k not in ['diagnostics','decomposition']};allrows.append(flat)
                totals['scenario_records']+=1;totals['group_coefficient_rows']+=len(g)
                for gg in g:gw.writerow({**{k:r[k] for k in ['scenario_id','model_id','method','scope','route','fraction','valid']},**gg})
                decomps.append({k:r[k] for k in ['scenario_id','model_id','method','scope','route','fraction','valid']}|r['decomposition'])
                if r['route']!='S0':bykey[r['method'],r['scope'],r['fraction']].append(r)
                if sid in oldmap:
                    o=oldmap[sid];og=old['groups'].get(sid,[])
                    a=np.asarray([x['sppr'] if x['sppr'] is not None else np.nan for x in og]);b=np.asarray([x['sppr'] if x['sppr'] is not None else np.nan for x in g])
                    same=a.shape==b.shape and np.allclose(a,b,rtol=2e-7,atol=1e-7,equal_nan=True)
                    num=lambda x,y: x is None and y is None or x is not None and y is not None and np.isclose(x,y,rtol=2e-7,atol=1e-7)
                    overlap.append(dict(scenario_id=sid,coefficients_match=bool(same),valid_mask_match=r['valid']==o['valid'],ppr_match=bool(num(r['ppr_fixed_H_tC'],o['ppr_fixed_H_tC']))))
            for (method,scope,f),rr in bykey.items():
                good=[r for r in rr if r['valid']];out=dict(model_id=mid,cohort=meta['cohort'],method=method,scope=scope,fraction=f,n_total=len(rr),n_valid=len(good),invalid_routes=[r['route'] for r in rr if not r['valid']],valid_routes=[r['route'] for r in good])
                for field in ['ppr_fixed_H_tC','ppr_retained_L_tC']:
                    vv=[r[field] for r in good if r[field] is not None];out['min_'+field]=min(vv) if vv else None;out['max_'+field]=max(vv) if vv else None
                out['meaningful_sensitivity']=meta['native_harvest']>0;envs.append(out)
            for method in METHODS:
                response['methods'][method]={}
                for scope in SCOPES:
                    rr=[r for r in records if r['method']==method and r['scope']==scope];b=next(r for r in rr if r['route']=='S0')
                    package=dict(baseline_valid=b['valid'],baseline_coefficients=[g['sppr'] for g in groups.get(b['scenario_id'],[])],routes={})
                    for route in ['SC','SM','SE','SR']:
                        points=[]
                        for r in rr:
                            if r['route']!=route:continue
                            points.append(dict(fraction=r['fraction'],valid=r['valid'] and meta['native_harvest']>0,status=r['status'],reasons=r['reasons'],
                                coefficients=[g['sppr'] for g in groups.get(r['scenario_id'],[])],catch_weight_mode=r['diagnostics'].get('catch_weight_mode')))
                        intervals=[[a['fraction'],b['fraction']] for a,b in zip(points,points[1:]) if a['valid'] and b['valid'] and (method not in ['SPPR_1986','SPPR_1995_TEmean'] or a['catch_weight_mode']==b['catch_weight_mode'])]
                        package['routes'][route]=dict(points=points,eligible_adjacent_intervals=intervals)
                    response['methods'][method][scope]=package
            responses.append(response)
            print('SUMMARIZED',mid,len(records),flush=True)
    assert len([m for m in models if m['cohort']=='additional'])==20
    df=pd.DataFrame(allrows);added=df[df.cohort=='additional'];aggregates=[];fixed_supports={}
    for key,support in added[added.route!='S0'].groupby(['method','scope','route']):
        fixed_supports[key]=[mid for mid,sub in support.groupby('model_id') if len(sub)==27 and sub.valid.all() and sub.coefficient_change_pct.notna().all()]
    for (method,scope,route,f),rr in added[added.route!='S0'].groupby(['method','scope','route','fraction']):
        valid=rr[rr.valid];paired=valid[valid.coefficient_change_pct.notna()]
        row=dict(method=method,scope=scope,route=route,fraction=f,n_total=len(rr),n_valid=len(valid),n_paired=len(paired),n_invalid_or_unavailable=len(rr)-len(valid),invalid_models=rr.loc[~rr.valid,'model_id'].tolist())
        for metric in ['coefficient_change_pct','retained_change_pct','standard_relative_excess_pct']:
            row[metric]=distribution(valid[metric].dropna().tolist())
        # Compare across fractions only on the same models with valid pairs at every grid point.
        fixed=fixed_supports[method,scope,route]
        row['all_grid_fixed_support_models']=fixed;row['n_all_grid_fixed_support']=len(fixed)
        row['fixed_support_coefficient_change_pct']=distribution(paired[paired.model_id.isin(fixed)].coefficient_change_pct.tolist())
        aggregates.append(row)
    for name,data in [('ecosystem_ppr',allrows),('effect_decomposition',decomps),('scenario_envelopes',envs),('aggregate_distributions',aggregates),('baseline_checks',checks)]:
        pd.DataFrame([{k:json.dumps(clean(v),ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in data]).to_csv(ROOT/'results'/f'{name}.csv',index=False)
        if name!='ecosystem_ppr':write_json(ROOT/'results'/f'{name}.json',data)
    write_json(ROOT/'verification/original_overlap.json',dict(n_compared=len(overlap),passed=all(r['coefficients_match'] and r['valid_mask_match'] and r['ppr_match'] for r in overlap),checks=overlap))
    write_json(ROOT/'results/model_catalog.json',models)
    write_json(ROOT/'results/standard_method_comparison.json',[{k:r[k] for k in ['scenario_id','model_id','cohort','method','scope','route','fraction','valid','fixed_standard_ppr_tC','ppr_fixed_H_tC','standard_relative_excess_pct']} for r in allrows])
    package=dict(schema_version=2,study_version='2026-09-10.discard-routing.expanded.v2',fractions=FRACTIONS,methods=METHODS,scopes=SCOPES,routes=['SC','SM','SE','SR'],
        fields=FIELDS,records=compact,vectors=vectors,groups=groupmeta,models=models,aggregates=aggregates,envelopes=envs,screening=screen,totals=dict(totals),
        ecosystem_family_counts=dict(family_counts),excluded_provisional_models=excluded,
        warning='Scenario envelopes are sensitivity ranges, not confidence intervals. Twenty selected models do not establish global validity.',
        basis='Fixed original native H for coefficient response; retained L=(1-f)H for landings footprint; carbon convention /9.',
        grid_semantics='Every shown fraction was solved; no interpolation is presented as a solved point.')
    write_json(ROOT/'results/report_data.v2.json',package)
    response=dict(schema_version=2,study_version=package['study_version'],tested_fraction_grid=FRACTIONS,response_models=responses,
        donor_rule='Exact source JSON ecological identity and immutable group IDs only; metadata/units must match. No pooled global validity or automatic transfer.',
        evaluation='Apply group coefficients to the same actual landings vector with fixed mapping weights, then divide by 9. No model re-fit by catch year.',
        denominator='The same selected annual NPP denominator for all compared endpoints; native all-source ratios unavailable with positive import support.',
        interpolation='Eligible adjacent intervals are provided for a later consumer; report points themselves are exact solved calculations. No interpolation through invalid points or weight changes.',
        uncertainty_type='discard-routing sensitivity envelope, not a confidence interval')
    write_json(ROOT/'results/discard_responses.v2.json',response)
    write_json(ROOT/'verification/summary_counts.json',dict(totals,models=len(models),added_models=20,reference_models=len(models)-20,unique_coefficient_vectors=len(vectors),baseline_checks=len(checks)))
    print('SUMMARY',dict(totals),flush=True)
if __name__=='__main__':summarize()
