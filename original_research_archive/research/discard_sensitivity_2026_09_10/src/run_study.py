"""Recompute the fixed-native-harvest discard-routing experiment, never by year."""
from pathlib import Path
from copy import deepcopy
import json, warnings, contextlib, io, time, hashlib, sys
if __name__=='__main__' and not sys.flags.utf8_mode:
    raise SystemExit('Run with Python -X utf8 (or PYTHONUTF8=1); the frozen engine reads source JSON using the interpreter text encoding.')
import numpy as np
import pandas as pd
from baseline import *
from scenarios import make_scenario,physical_diagnostics
from metrics import fixed_support_ppr,decompose

ROUTES=['SC','SM','SE','SR']
TE_OPTIONS={'new_GE':'GE','new_TE_EEfix':'TE','new_WithEgestion':'With Egestion','Ulanowicz_TE':'TE'}


def clean(value):
    if isinstance(value,dict): return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,np.ndarray)): return [clean(v) for v in value]
    if isinstance(value,(np.integer,)): return int(value)
    if isinstance(value,(bool,np.bool_)): return bool(value)
    if isinstance(value,(float,np.floating)): return float(value) if np.isfinite(value) else None
    return value


def write_json(path,value):
    Path(path).write_text(json.dumps(clean(value),ensure_ascii=False,allow_nan=False),encoding='utf-8')


def numeric_diagnostics(calc,method,frame,warning_messages):
    result=dict(warnings=warning_messages,rho_living=None,rho_detritus=None)
    if method in TE_OPTIONS:
        option=TE_OPTIONS[method]
        te=calc.get_TE(option,as_matrix=False)
        dc=calc.get_DC(DET_as_PP=True)
        living=calc.get_Regular_seq()
        A=dc.loc[living,living].div(te.loc[living],axis=0).fillna(0).to_numpy()
        A[~np.isfinite(A)]=0.
        result['rho_living']=calc._spectral_radius(A)
        if method in ('new_GE','new_WithEgestion'):
            result['recycling_resolution']=deepcopy(getattr(calc,'detritus_resolution_info',{}))
            result['rho_detritus']=result['recycling_resolution'].get('rho_B')
        if method=='Ulanowicz_TE':
            result['rho_living_unbroken_reference']=result.pop('rho_living')
            result['rho_living']=0.
            result['path_semantics']='Frozen Ulanowicz cycle removal; detritus stays a terminal basal source.'
    result['nonfinite_cells']=int((~np.isfinite(frame.to_numpy(dtype=float))).sum())
    result['negative_source_cells']=int((frame.to_numpy(dtype=float)<-1e-8).sum())
    result['minimum_coefficient']=float(np.nanmin(frame.to_numpy(dtype=float)))
    if 'sppr' not in frame.columns:
        coeff=frame.sum(axis=1,skipna=False).reindex(calc.p.index)
        inflow=calc.p.loc[calc.get_PP_seq()+calc.get_Import_seq()].sum()
        original=(calc.catch+calc.growth+calc.net_migration).dot(coeff)
        # Keep the original check for reproducibility, and include the SE sink and
        # subtract the internally returned SR removal in the separate ledger check.
        sink=calc.catch+calc.external_loss+calc.growth+calc.net_migration-calc.discard_return.sum(axis=1)
        out=sink.dot(coeff)
        result.update(legacy_sppr_inflow=float(inflow),legacy_sppr_outflow=float(original),
            legacy_sppr_relative_gap=abs(float(inflow-original))/max(abs(float(inflow)),1e-12),
            ledger_sppr_outflow=float(out),ledger_sppr_relative_gap=abs(float(inflow-out))/max(abs(float(inflow)),1e-12),
            sppr_budget_note='Weighted export check is method-specific; physical biomass budgets are assessed independently. Natural fate exports are reported separately.')
    return result


def source_adjustments(calc,meta):
    raw=calc._model.groups_data
    solved=calc._groups_df
    rows=[]
    for col in ['p','q','M0','ee','egestion','respiration','catch','biomass_accum','net_migration']:
        if col not in raw: continue
        for seq in solved.index:
            a=raw.at[seq,col]; b=solved.at[seq,col]
            if pd.isna(a) and pd.isna(b): continue
            if pd.isna(a) or pd.isna(b) or not np.isclose(a,b,rtol=1e-10,atol=1e-12):
                rows.append(dict(model_id=meta['model_id'],stage='source_initializer',group_id=int(seq),
                    group_name=calc.seq2name[seq],parameter=col,source_value=a,solved_value=b,
                    rule='Frozen exporter settings: normalize diet; deterministic defaults; LIM only where still missing.'))
    original_dc=calc._model.DC.reindex(index=calc._DC.index,columns=calc._DC.columns)
    for pred in calc._DC.index:
        for prey in calc._DC.columns:
            a=original_dc.loc[pred,prey];b=calc._DC.loc[pred,prey]
            if not np.isclose(a,b,rtol=1e-12,atol=1e-14):
                rows.append(dict(model_id=meta['model_id'],stage='source_initializer',group_id=int(pred),
                    group_name=calc.seq2name[pred],parameter=f'diet_fraction_prey_{prey}',source_value=a,
                    solved_value=b,rule='Frozen exporter normalize_DC=True; original rows retained in frozen input.'))
    return rows


def sr_destination(calc,model_id):
    if not model_id.startswith('13_2_'): return None,None
    # Independently verified original XLS Table C D43/D44: fleets -> offal 1;
    # E40/F40: nonconsumed offal -> pelagic .1 / benthic .9. Offal has no consumer.
    offal=calc.name2seq['Fishery offal']
    pelagic=calc.name2seq['Pelagic detritus'];benthic=calc.name2seq['Benthic detritus']
    dc=calc.get_DC(DET_as_PP=True)
    if not np.isclose(dc.loc[calc.get_Regular_seq(),offal].sum(),0):
        raise ValueError('Offal has direct consumers; collapsing this intermediate is not supported')
    _,raw_fate=ModelData.get_DC(calc._model.data_json)
    if not np.isclose(raw_fate.at[offal,pelagic],.1) or not np.isclose(raw_fate.at[offal,benthic],.9):
        raise ValueError('Raw frozen offal onward fate differs from source evidence')
    fate=pd.DataFrame(0.,index=calc.p.index,columns=calc.get_DET_seq())
    fate[pelagic]=.1;fate[benthic]=.9
    return fate,dict(intermediate_group_id=int(offal),intermediate_name='Fishery offal',
        downstream_fractions={str(pelagic):.1,str(benthic):.9},
        note='Source-supported unconsumed offal intermediate is algebraically collapsed for coefficient solving; original transfer ledger is retained. Frozen loader forces all detritus-to-detritus fates to identity, so the raw JSON/source fate is restored for this explicit return only. No extra processing-offal amount is invented.')


def run():
    start=time.time(); records=[];groups={};models=[];changes=[];ledger_rows=[];transfers=[];checks=[]
    baseline_outputs={};baseline_totals={};all_diagnostics=[]
    for path in model_paths():
        base,meta=load_baseline(path)
        model_id=meta['model_id']
        meta.update(native_units='t wet weight km-2 yr-1',ppr_units='t C equivalent km-2 yr-1',
            denominator_name='Native modeled primary-producer production / 9',
            denominator_kind='model_period_PP_not_satellite_NPP',carbon_conversion=9.,
            group_count=base.n_groups,raw_catch_status='explicit_zero_in_raw_source' if model_id.startswith('52_') else 'positive_living_harvest',
            source_validity='imported_source_with_documented_defaults',
            closure='Freeze completed living P,Q,diet,predation,accumulation,migration. Solve EE for SM; detritus accumulation absorbs the change in routed inflow at fixed detritus predation. No new consumption is assumed.')
        changes+=source_adjustments(base,meta)
        fate,sr_info=sr_destination(base,model_id)
        meta['sr_routing']=sr_info
        meta['limitations']=[]
        if model_id.startswith('13_'):
            meta['limitations']+=['Diet normalization and inferred living accumulation reproduce the saved pipeline, not the unchanged published EwE model.',
                'S0 omits explicit fleet discard return. SR uses documented offal fate with hypothetical designated amounts.',
                'Frozen GE and egestion configurations already contain divergent/negative coefficients.']
        if model_id.startswith('28_'):
            meta['limitations']+=['The loader zeroes raw detritus export 1670.48071 and stores completed detritus excess as accumulation; excluded from fishery H and catch weights.',
                'Small original source rounding residuals are preserved.',
                'Published source-period landings/discards exist but a fleet return fate is not established.']
        if model_id.startswith('34_'):
            meta['limitations']+=['Frozen initialization infers nonzero, often negative, living accumulation from source inconsistencies; this is a constrained accounting sensitivity, not a new steady-state Ecopath fit.',
                'Source-model catch is combined; observed source discard fraction and fleet return destination are unresolved.']
        if model_id.startswith('52_'):
            meta['limitations']+=['All source harvest fields are explicit zero; every designated discard amount is zero. This control cannot support a regional sensitivity envelope.',
                'NE is the source Ecopath model label, not an established northeast subregion; source represents the Sea of Okhotsk in the 1980s.']
        default,default_ledger=make_scenario(base,0,'SC')
        meta['baseline_diagnostics']=physical_diagnostics(default,default_ledger)
        meta['source_validity']='accounting_baseline_with_inferred_accumulation' if meta['baseline_diagnostics']['negative_living_accumulation'] else 'source_rounding_tolerance'
        raw_outputs={};cache={}
        standard=base.SPPR_1995(global_TE=.1)
        print('BASELINE',model_id,flush=True)
        for method in METHODS:
            with warnings.catch_warnings(record=True) as messages,contextlib.redirect_stdout(io.StringIO()):
                try:
                    frame=calculate(base,method,standard)
                    raw_outputs[method]=frame
                except Exception as e:
                    raw_outputs[method]=None
        checks+=compare_saved(base,meta,raw_outputs)
        for method,frame in raw_outputs.items():
            if frame is None: continue
            for scope in SCOPES:
                coeff=scoped(base,frame,scope)
                if coeff is not None: baseline_totals[model_id,method,scope]=fixed_support_ppr(coeff,base.catch)
        configurations=[('S0',0.)]+[(route,f) for f in FRACTIONS for route in ROUTES]
        for route,fraction in configurations:
            route_error=None
            try:
                if route=='SR' and fate is None: raise ValueError('SR unavailable: no verified source fleet-return destination')
                calc,ledger=make_scenario(base,fraction,route,return_fate=fate if route=='SR' else None)
                physical=physical_diagnostics(calc,ledger)
            except Exception as e:
                route_error=str(e);calc=None;ledger=None;physical={}
            ledger_id=f'{model_id}|{route}|{fraction:g}'
            if ledger is not None:
                for seq,r in ledger.iterrows(): ledger_rows.append(dict(model_id=model_id,route=route,fraction=fraction,group_id=int(seq),**r.to_dict()))
                if route=='SR':
                    for seq in base.get_Regular_seq():
                        d=float(ledger.loc[seq,'designated_discard'])
                        if d:
                            transfers.append(dict(model_id=model_id,fraction=fraction,donor_group_id=int(seq),
                                offal_group_id=sr_info['intermediate_group_id'],donor_to_offal=d,
                                offal_to_pelagic=.1*d,offal_to_benthic=.9*d))
                for field in ['p','q','M0','EE','catch','growth','external_loss']:
                    before=getattr(default,field);after=getattr(calc,field)
                    for seq in after.index:
                        if not np.isclose(before[seq],after[seq],rtol=1e-12,atol=1e-12):
                            changes.append(dict(model_id=model_id,route=route,fraction=fraction,stage='routing_scenario',
                                group_id=int(seq),group_name=calc.seq2name[seq],parameter=field,
                                source_value=float(before[seq]),solved_value=float(after[seq]),rule=meta['closure']))
            for method in METHODS:
                error=route_error;frame=None;number_diag={};warning_messages=[]
                if calc is not None:
                    # The frozen TE detritus formula has no explicit donor-return term.
                    # Keep a clear unsupported record instead of silently crediting only
                    # its denominator or pretending that natural M0 equals fishery return.
                    if route=='SR' and fraction>0 and method=='new_TE_EEfix':
                        error='Explicit SR donor ancestry is unsupported by frozen new_TE_EEfix direct-PP detritus scaling; no silent M0 substitution.'
                    else:
                        weights=calc.catch/calc.catch.sum() if calc.catch.sum()>0 else calc._groups_df.biomass/calc._groups_df.biomass.sum()
                        state=np.concatenate([calc.p.values,calc.q.values,calc.M0.values,weights.values,calc.discard_return.to_numpy().ravel()])
                        if method in ('standard_fixed_baseline_TL','SPPR_1995_TE0.1'): fingerprint='fixed_diet'
                        elif method=='SPPR_1986': fingerprint='weights_'+str(np.round(weights.values,13).tolist())
                        elif method=='SPPR_1995_TEmean': fingerprint=hashlib.sha256(np.round(np.r_[calc.M0.values,weights.values],13).tobytes()).hexdigest()
                        else: fingerprint=hashlib.sha256(np.round(state,13).tobytes()).hexdigest()
                        key=method,fingerprint
                        if key in cache:
                            frame,number_diag=deepcopy(cache[key])
                        else:
                            with warnings.catch_warnings(record=True) as messages,contextlib.redirect_stdout(io.StringIO()):
                                try:
                                    if hasattr(calc,'detritus_resolution_info'): del calc.detritus_resolution_info
                                    frame=calculate(calc,method,standard)
                                    warning_messages=[str(w.message) for w in messages]
                                    number_diag=numeric_diagnostics(calc,method,frame,warning_messages)
                                    cache[key]=deepcopy((frame,number_diag))
                                except Exception as e: error=str(e)
                        # Weight diagnostics and export checks are scenario-specific even
                        # when identical coefficient calculations are reused from cache.
                        if frame is not None and 'sppr' not in frame.columns:
                            old_recycling=number_diag.get('recycling_resolution')
                            exact=numeric_diagnostics(calc,method,frame,number_diag.get('warnings',[]))
                            if old_recycling is not None:
                                exact['recycling_resolution']=old_recycling
                                exact['rho_detritus']=old_recycling.get('rho_B')
                            number_diag=exact
                for scope in SCOPES:
                    sid=f'{model_id}|{method}|{scope}|{route}|{fraction:g}'
                    reasons=[]
                    if error: reasons.append(error)
                    coeff=scoped(calc,frame,scope) if frame is not None else None
                    if method not in FLOW_METHODS and scope!='all': reasons.append('This trophic-chain method has no source attribution for inner/PP scope.')
                    numeric_ok=frame is not None and not number_diag.get('nonfinite_cells') and not number_diag.get('negative_source_cells')
                    if number_diag.get('rho_living') is not None and number_diag['rho_living']>=1: reasons.append('Living requirement network does not converge (spectral radius >= 1).');numeric_ok=False
                    if number_diag.get('rho_detritus') is not None and number_diag['rho_detritus']>=1: reasons.append('Detritus recycling does not converge (spectral radius >= 1).');numeric_ok=False
                    if number_diag.get('negative_source_cells'): reasons.append('Solver returned negative basal-source coefficients; excluded from valid envelopes.')
                    if number_diag.get('nonfinite_cells'): reasons.append('Solver returned non-finite coefficients; excluded from valid envelopes.')
                    physical_ok=bool(physical.get('ledger_closes',False)) and not physical.get('negative_physical_flows')
                    if physical and not physical.get('ledger_closes'): reasons.append('Physical ledger exceeds the documented balance tolerance.')
                    if physical.get('negative_physical_flows'): reasons.append('Negative physical flows in constrained scenario.')
                    if physical.get('min_ee',0)<-1e-8 or physical.get('max_ee',1)>1+1e-8:
                        physical_ok=False;reasons.append('A living ecotrophic efficiency lies outside [0,1].')
                    valid=bool(numeric_ok and physical_ok and coeff is not None and not error)
                    h=base.catch;l=(1-fraction)*h
                    ppr=fixed_support_ppr(coeff,h) if coeff is not None else None
                    retained=fixed_support_ppr(coeff,l) if coeff is not None else None
                    # Invalid raw numeric totals remain separate audit diagnostics only.
                    raw_ppr=ppr
                    if not valid: ppr=None;retained=None
                    baseline_ppr=baseline_totals.get((model_id,method,scope))
                    fixed_standard=baseline_totals.get((model_id,'standard_fixed_baseline_TL','all')) if scope=='all' else None
                    base_L=baseline_ppr*(1-fraction) if baseline_ppr is not None else None
                    d=decompose(baseline_ppr,ppr,base_L,retained)
                    evidence='imported_baseline' if route=='S0' else ('source_supported_destination_hypothetical_amount' if route=='SR' and fate is not None else 'hypothetical')
                    status='valid' if valid else ('unavailable' if error or coeff is None else 'invalid')
                    if base.catch.sum()==0 and valid: status='degenerate_zero_harvest'
                    row=dict(scenario_id=sid,model_id=model_id,model_label=meta['model_label'],method=method,scope=scope,
                        fraction=fraction,route=route,status=status,valid=valid,numerical_valid=bool(numeric_ok),
                        physical_valid=physical_ok,source_validity=meta['source_validity'],evidence_status=evidence,
                        reasons=reasons,ppr_fixed_H_tC=ppr,ppr_retained_L_tC=retained,
                        raw_numeric_ppr_fixed_H_tC=raw_ppr,baseline_ppr_fixed_H_tC=baseline_ppr,
                        baseline_ppr_retained_L_tC=base_L,fixed_standard_ppr_tC=fixed_standard,
                        standard_relative_excess_pct=100*(fixed_standard/ppr-1) if fixed_standard is not None and ppr is not None and ppr>0 else None,
                        standard_absolute_difference_tC=fixed_standard-ppr if fixed_standard is not None and ppr is not None else None,
                        denominator_name=meta['denominator_name'],denominator_value=meta['denominator_value'],
                        ppr_to_native_pp_pct=100*ppr/meta['denominator_value'] if ppr is not None and meta['denominator_value']>0 else None,
                        ppr_retained_to_native_pp_pct=100*retained/meta['denominator_value'] if retained is not None and meta['denominator_value']>0 else None,
                        designated_discard_native=float(fraction*h.sum()),retained_native=float(l.sum()),
                        fixed_H_native=float(h.sum()),diagnostics={**physical,**number_diag},decomposition=d,
                        coverage_fraction=1. if coeff is not None and np.isfinite(coeff[h>0]).all() else None,
                        meaningful_sensitivity=bool(base.catch.sum()>0),source_json_sha256=meta['source_json_sha256'],
                        source_workbook_sha256=meta['source_workbook_sha256'],
                        assumptions=meta['closure'])
                    records.append(row)
                    if coeff is not None:
                        groups[sid]=[dict(group_id=int(i),name=base.seq2name[i],sppr=clean(coeff.get(i)),
                            H=float(h[i]),L=float(l[i]),trophic_info=base._groups_df.at[i,'trophic_info'],
                            contribution_H_tC=clean(coeff.get(i)*h[i]/9.),contribution_L_tC=clean(coeff.get(i)*l[i]/9.)) for i in base.p.index]
            print(model_id,route,fraction,'completed',flush=True)
        models.append(meta)
        write_json(ROOT/'results/study.partial.json',dict(schema_version=1,models=models,records=records,groups=groups))
        write_json(ROOT/'results/baseline_checks.json',checks)
    study=dict(schema_version=1,study_version='2026-09-10.discard-routing.v1',created_utc=pd.Timestamp.now(tz='UTC').isoformat(),
        fraction_grid=FRACTIONS,models=models,methods=METHODS,scopes=SCOPES,routes=ROUTES,
        records=records,groups=groups,baseline_checks=checks,elapsed_seconds=time.time()-start,
        uncertainty_type='discard-routing sensitivity envelope; not a confidence interval',
        evaluation='same frozen native living harvest H at every fraction; retained L=(1-f)H evaluated separately',
        native_carbon_conversion='Native wet-weight PP equivalents divided by 9, same assumed conversion as atlas; ratio uses identical conversion in numerator and denominator',
        scope_rule='Trophic-chain methods have no source attribution; inner and PP are unavailable.',
        source_rule='Destination evidence and hypothetical designated amount are separate. Numerical closure does not establish ecological truth.')
    write_json(ROOT/'results/study.json',study)
    write_json(ROOT/'results/scenario_definitions.json',dict(routes={
        'S0':'Saved imported baseline with frozen initializer settings.',
        'SC':'H stays fishery removal; L=(1-f)H retained and D=fH designated, with no credited return.',
        'SM':'Fishery catch L; M0 increases by D and EE decreases D/P. Returns follow existing biological fate; detritus accumulation closes fixed predation.',
        'SE':'Fishery catch L plus separate external loss D. M0, EE and combined removal unchanged; mean weights see L.',
        'SR':'H remains fishery mortality with explicit source-supported return of D. Only Humboldt destination established; offal intermediary transfers are explicit.'},
        fractions=FRACTIONS,settings=SETTINGS,closure=meta['closure']))
    pd.DataFrame(changes).to_csv(ROOT/'results/parameter_changes.csv',index=False)
    pd.DataFrame(ledger_rows).to_csv(ROOT/'results/flow_ledger.csv',index=False)
    pd.DataFrame(transfers).to_csv(ROOT/'results/explicit_offal_transfers.csv',index=False)
    flat=[];groupflat=[];diags=[]
    for row in records:
        flat.append({k:json.dumps(clean(v),ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items() if k not in ['diagnostics','decomposition']})
        diags.append(dict(scenario_id=row['scenario_id'],**row['diagnostics']))
        for g in groups.get(row['scenario_id'],[]): groupflat.append(dict(scenario_id=row['scenario_id'],model_id=row['model_id'],method=row['method'],scope=row['scope'],route=row['route'],fraction=row['fraction'],valid=row['valid'],**g))
    pd.DataFrame(flat).to_csv(ROOT/'results/ecosystem_ppr.csv',index=False)
    pd.DataFrame(groupflat).to_csv(ROOT/'results/group_sppr.csv',index=False)
    pd.DataFrame(diags).to_csv(ROOT/'results/diagnostics.csv',index=False)
    print('Finished',len(records),'records',len(groupflat),'group coefficients',round(time.time()-start,1),'seconds',flush=True)
    return study


if __name__=='__main__': run()
