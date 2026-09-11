"""Paired decomposition, signed reference comparisons and versioned map responses."""
from collections import defaultdict
from pathlib import Path
import json, csv, hashlib
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def valid_intervals(rows,method):
    rows=sorted(rows,key=lambda r:r['fraction'])
    intervals=[]
    for left,right in zip(rows,rows[1:]):
        if not left['valid'] or not right['valid']: continue
        if method in ('SPPR_1995_TEmean','SPPR_1986') and left['diagnostics'].get('catch_weight_mode')!=right['diagnostics'].get('catch_weight_mode'):
            continue
        intervals.append([left['fraction'],right['fraction']])
    return intervals


def scenario_envelope(rows):
    accepted=[r for r in rows if r['valid'] and r['ppr_fixed_H_tC'] is not None]
    result=dict(n_total=len(rows),n_valid=len(accepted),n_invalid_or_unavailable=len(rows)-len(accepted),
        valid_routes=[r['route'] for r in accepted],
        excluded_routes=[r['route'] for r in rows if r not in accepted],
        uncertainty_type='discard-routing sensitivity envelope; not a confidence interval')
    for field,outfield in [('ppr_fixed_H_tC','fixed_H_tC'),('ppr_retained_L_tC','retained_L_tC')]:
        vals=[r[field] for r in accepted if r[field] is not None]
        result['min_'+outfield]=min(vals) if vals else None
        result['max_'+outfield]=max(vals) if vals else None
        result['range_'+outfield]=max(vals)-min(vals) if vals else None
    result['relative_spread_pct']=100*(result['max_fixed_H_tC']/result['min_fixed_H_tC']-1) if result['min_fixed_H_tC'] is not None and result['min_fixed_H_tC']>0 else None
    return result


def process():
    path=ROOT/'results/study.json'
    study=json.loads(path.read_text(encoding='utf-8'))
    records=study['records'];grouped=defaultdict(list)
    # The legacy loader uses locale-default text decoding. Numeric identity is
    # immutable group seq; use the hash-verified workbook names for display and
    # mapping compatibility, preserving any original engine label as provenance.
    canonical_names={}
    for model in study['models']:
        source=ROOT/'inputs/PPREstimation/output/top10'/f'{model["model_id"]}.xlsx'
        if hashlib.sha256(source.read_bytes()).hexdigest()!=model['source_workbook_sha256']:
            raise ValueError('Frozen group-identity workbook hash changed: '+str(source))
        frame=pd.read_excel(source,'sppr_all')
        canonical_names[model['model_id']]=dict(zip(frame['seq'],frame['group_name']))
        model['group_identity_source']='Frozen upstream workbook sppr_all seq/group_name; numeric identities and coefficients unchanged.'
    for record in records:
        for group in study['groups'].get(record['scenario_id'],[]):
            canonical=canonical_names[record['model_id']][group['group_id']]
            if group['name']!=canonical:
                group.setdefault('engine_name_original',group['name'])
                group['name']=canonical
    # Preserve CSV numeric text verbatim while repairing public name columns.
    for filename in ('flow_ledger.csv','parameter_changes.csv'):
        csvpath=ROOT/'results'/filename
        with csvpath.open(encoding='utf-8',newline='') as stream:
            reader=csv.DictReader(stream);fields=list(reader.fieldnames);rows=list(reader)
        if 'engine_name_original' not in fields: fields.append('engine_name_original')
        for row in rows:
            canonical=canonical_names[row['model_id']][int(row['group_id'])]
            if row['group_name']!=canonical:
                row['engine_name_original']=row.get('engine_name_original') or row['group_name']
                row['group_name']=canonical
        with csvpath.open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    flow_ledger=pd.read_csv(ROOT/'results/flow_ledger.csv')
    native_import={}
    for model in study['models']:
        baseline=next(r for r in records if r['model_id']==model['model_id'] and r['route']=='S0' and r['method']=='standard_fixed_baseline_TL' and r['scope']=='all')
        ids=[g['group_id'] for g in study['groups'][baseline['scenario_id']] if g['trophic_info']=='Import']
        rows=flow_ledger[(flow_ledger.model_id==model['model_id'])&(flow_ledger.route=='S0')&flow_ledger.group_id.isin(ids)]
        model['native_import_production_tC']=float(rows.production.sum()/9.)
        native_import[model['model_id']]=model['native_import_production_tC']
    for row in records:
        compatible=not(row['scope']=='all' and native_import[row['model_id']]>0)
        row['native_denominator_compatible']=compatible
        row['native_ratio_reason']=None if compatible else 'All-source PPR includes imported support, while this denominator is internal model PP only; the boundary-mismatched native ratio is unavailable. PPR remains available.'
        if not compatible:
            row['ppr_to_native_pp_pct']=None
            row['ppr_retained_to_native_pp_pct']=None
    # Physical biomass closure and a method's own PP-equivalent identity are
    # distinct checks. The new solver family promises the latter; cycle-pruned
    # Ulanowicz and trophic-chain references do not promise that same identity.
    for row in records:
        targeted=row['method'] in ('new_GE','new_TE_EEfix','new_WithEgestion')
        gap=row['diagnostics'].get('ledger_sppr_relative_gap')
        conservation=None if not targeted or gap is None else gap<=.05
        row['method_conservation_valid']=conservation
        row['diagnostics']['method_conservation_valid']=conservation
        row['diagnostics']['method_conservation_tolerance']=.05 if targeted else None
        if conservation is False:
            reason='The method-specific PP-equivalent export identity exceeds the frozen diagnostic 5% failure threshold; biomass-ledger closure and solver convergence are separate.'
            if reason not in row['reasons']: row['reasons'].append(reason)
            row['valid']=False;row['status']='invalid_method_conservation'
            for field in ['ppr_fixed_H_tC','ppr_retained_L_tC','standard_relative_excess_pct',
                          'standard_absolute_difference_tC','ppr_to_native_pp_pct','ppr_retained_to_native_pp_pct']:
                row[field]=None
            row['decomposition']={k:None for k in ['coefficient_effect','catch_effect','interaction','total_change','residual']}
    for r in records:
        if r['route']!='S0': grouped[r['model_id'],r['method'],r['scope'],r['fraction']].append(r)
    envelopes=[]
    for key,rows in grouped.items():
        model,method,scope,fraction=key
        out=dict(model_id=model,method=method,scope=scope,fraction=fraction,**scenario_envelope(rows))
        baseline=rows[0]['baseline_ppr_fixed_H_tC']
        out['baseline_ppr_fixed_H_tC']=baseline
        out['meaningful_sensitivity']=rows[0]['meaningful_sensitivity']
        out['status']='assessed' if rows[0]['meaningful_sensitivity'] and out['n_valid']>=2 else 'not_assessed'
        out['assumption_class']='hypothetical_designated_amounts'
        envelopes.append(out)
    decomposition=[];comparison=[]
    for row in records:
        identity={k:row[k] for k in ['scenario_id','model_id','method','scope','fraction','route','valid']}
        decomposition.append({**identity,**row['decomposition']})
        comparison.append({**identity,'reference':'fixed baseline group TL; TE=.1; same original H; all basal sources only',
            'standard_ppr_tC':row['fixed_standard_ppr_tC'],'scenario_ppr_tC':row['ppr_fixed_H_tC'],
            'signed_excess_pct':row['standard_relative_excess_pct'],
            'absolute_difference_tC':row['standard_absolute_difference_tC']})
    ranks=[];rank_groups=defaultdict(list)
    for row in records:
        if row['valid'] and row['ppr_fixed_H_tC'] is not None:
            rank_groups[row['model_id'],row['scope'],row['fraction'],row['route']].append(row)
    for key,rows in rank_groups.items():
        ordered=sorted(rows,key=lambda r:r['ppr_fixed_H_tC'])
        for rank,row in enumerate(ordered,1):
            ranks.append({k:row[k] for k in ['model_id','scope','fraction','route','method','ppr_fixed_H_tC']}|{'rank_ascending':rank})
    response_models=[]
    for model in study['models']:
        mid=model['model_id']
        response=dict(model_id=mid,source_json_sha256=model['source_json_sha256'],
            source_workbook_sha256=model['source_workbook_sha256'],
            source_validity=model['source_validity'],native_harvest=model['native_harvest'],
            status='tested_constrained_accounting' if model['native_harvest']>0 else 'not_assessed_zero_source_harvest',
            limitations=model['limitations'],methods={})
        for method in study['methods']:
            if method=='standard_fixed_baseline_TL': continue
            method_response={}
            for scope in study['scopes']:
                relevant=[r for r in records if r['model_id']==mid and r['method']==method and r['scope']==scope]
                baseline=next(r for r in relevant if r['route']=='S0')
                basegroups=study['groups'].get(baseline['scenario_id'],[])
                group_ids=[g['group_id'] for g in basegroups]
                routes={}
                for route in study['routes']:
                    rows=[r for r in relevant if r['route']==route]
                    points=[]
                    for row in rows:
                        gmap={g['group_id']:g for g in study['groups'].get(row['scenario_id'],[])}
                        points.append(dict(fraction=row['fraction'],valid=bool(row['valid'] and row['meaningful_sensitivity']),
                            status=row['status'],evidence_status=row['evidence_status'],reasons=row['reasons'],
                            coefficients=[gmap[i]['sppr'] if i in gmap else None for i in group_ids],
                            catch_weight_mode=row['diagnostics'].get('catch_weight_mode')))
                    routes[route]=dict(points=points,valid_intervals=valid_intervals(rows,method) if model['native_harvest']>0 else [],
                        interpolation='linear in each group coefficient only within listed verified adjacent intervals; no interpolation through invalid points or endpoint weight changes')
                method_response[scope]=dict(baseline_valid=baseline['valid'],
                    group_ids=group_ids,group_names=[g['name'] for g in basegroups],
                    group_identity_source=model['group_identity_source'],
                    baseline_coefficients=[g['sppr'] for g in basegroups],routes=routes,
                    source_scope=scope,coefficient_units='wet primary-production equivalent per wet unit harvested',
                    evaluation='Apply scenario group coefficients to the same actual landed taxon vector, with frozen mapping weights, then divide by 9.',
                    central_policy='landings_only',
                    construction_invariant=method=='SPPR_1995_TE0.1',
                    limitation='The model-TL chain is routing-invariant by construction; an invariant tested response is not proof of no ecological recycling uncertainty.' if method=='SPPR_1995_TE0.1' else None)
            response['methods'][method]=method_response
        response_models.append(response)
    responses=dict(schema_version=1,study_version=study['study_version'],
        uncertainty_type=study['uncertainty_type'],response_models=response_models,
        donor_rule='Exact tested model and source-workbook hash only; unsupported models/methods/scopes not assessed; no global pooled proxy.',
        discard_exposure='D/(L+D); not D/L',catch_boundary='same actual retained landings vector for every route',
        denominator_rule='Divide every endpoint by the same selected annual NPP; NPP uncertainty remains separate.',
        weighting_rule='Reuse frozen taxon-to-group weights; do not refit models by year.',
        tested_fraction_grid=study['fraction_grid'])
    study['envelopes']=envelopes
    study['standard_comparisons']=comparison
    study['rankings']=ranks
    source_path=ROOT/'results/source_evidence.json'
    if source_path.exists(): study['source_evidence']=json.loads(source_path.read_text(encoding='utf-8'))
    external=ROOT/'results/external_reference_audit.json'
    if external.exists(): study['external_reference_audit']=json.loads(external.read_text(encoding='utf-8'))
    path.write_text(json.dumps(study,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    (ROOT/'results/discard_responses.v1.json').write_text(json.dumps(responses,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    pd.DataFrame(decomposition).to_csv(ROOT/'results/effect_decomposition.csv',index=False)
    pd.DataFrame(envelopes).to_csv(ROOT/'results/scenario_envelopes.csv',index=False)
    pd.DataFrame(comparison).to_csv(ROOT/'results/standard_method_comparison.csv',index=False)
    pd.DataFrame(ranks).to_csv(ROOT/'results/method_rankings.csv',index=False)
    flat=[];groupflat=[];diags=[]
    for row in records:
        flat.append({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items() if k not in ['diagnostics','decomposition']})
        diags.append(dict(scenario_id=row['scenario_id'],**row['diagnostics']))
        for g in study['groups'].get(row['scenario_id'],[]):
            groupflat.append(dict(scenario_id=row['scenario_id'],model_id=row['model_id'],method=row['method'],scope=row['scope'],route=row['route'],fraction=row['fraction'],valid=row['valid'],**g))
    pd.DataFrame(flat).to_csv(ROOT/'results/ecosystem_ppr.csv',index=False)
    pd.DataFrame(groupflat).to_csv(ROOT/'results/group_sppr.csv',index=False)
    pd.DataFrame(diags).to_csv(ROOT/'results/diagnostics.csv',index=False)
    print('Wrote',len(envelopes),'envelopes and',len(response_models),'model response packages.')


if __name__=='__main__': process()
