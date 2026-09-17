"""Prespecified sequential screening; sensitivity outcomes never enter ordering."""
from pathlib import Path
from collections import defaultdict,Counter
import json,re,hashlib,contextlib,io,warnings,time,multiprocessing
import numpy as np
import pandas as pd
from baseline import ROOT,ModelData,PPRCalculator,SETTINGS,calculate,scoped
from scenarios import make_scenario,physical_diagnostics
from run_study import numeric_diagnostics,source_adjustments,write_json,clean

META=json.loads((ROOT/'inputs/corpus/model_metadatas.json').read_text(encoding='utf-8'))
def ecological_hash(data):
    keep=['group_seq','group_name','biomass','pb','qb','ee','pp','biomass_accum','biomass_accum_rate','respiration',
          'immigration','emigration','export','gs','ge','detritus_import','diet_imp','other_mort','flow_to_det']
    def num(v):
        try: return float(v)
        except (ValueError,TypeError):return v
    groups=[]
    for g in sorted(data['group'],key=lambda x:int(x['group_seq'])):
        row={k:num(g[k]) for k in keep if k in g}
        diet=(g.get('diet_descr') or {}).get('diet',[])
        if isinstance(diet,dict):diet=[diet]
        row['diet']=sorted([{k:num(d.get(k,0)) for k in ['prey_seq','proportion','detritus_fate']} for d in diet],key=lambda x:x['prey_seq'])
        groups.append(row)
    return hashlib.sha256(json.dumps(groups,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def metadata(path):
    parts=path.stem.split('_'); ident=parts[1] if len(parts)>1 else ''
    return dict(META.get(ident,{}).get('model',{}))

def strata(row):
    m=row['metadata']; region=m.get('region')
    if not region:
        nums=re.findall(r'-?\d+(?:\.\d+)?',m.get('geographic_extent',''))
        if len(nums)>=4:
            a,b,c,d=map(float,nums[:4]); region=f'lon{int(((a+c)/2+180)//60)}_'+('N' if b+d>=0 else 'S')
    return str(region or 'unknown')

def inventory():
    originals={ecological_hash(json.loads(p.read_text(encoding='utf-8'))) for p in (ROOT/'inputs/references').glob('*.json')}
    rows=[];seen={}
    paths=sorted((ROOT/'inputs/corpus').rglob('*.json'),key=lambda p:(0 if p.parent.name=='EwE_jsons' else 1,str(p)))
    for p in paths:
        raw=p.read_bytes();row=dict(model_id=p.stem,snapshot_path=str(p.relative_to(ROOT)),source_json_sha256=hashlib.sha256(raw).hexdigest(),
            metadata=metadata(p),status='inventory_candidate',reasons=[],selected=False)
        try:
            data=json.loads(raw);assert isinstance(data,dict) and isinstance(data.get('group'),list)
            row['group_count']=len(data['group']);row['ecological_sha256']=ecological_hash(data)
        except Exception as e:
            row.update(status='excluded',reasons=['Not a compatible individual-model group JSON']);rows.append(row);continue
        h=row['ecological_sha256'];m=row['metadata']; typ=m.get('ecosystem_type','').lower();name=m.get('model_name',p.stem).lower()
        if p.parent.name in ('ToyModels','broken_jsons') or 'toy' in str(p).lower():row['reasons'].append('Toy or intentionally broken source directory')
        if h in originals or p.stem.startswith(('13_2_','34_1_','28_646_','52_1_')) or p.stem.startswith('646_646_'):
            row['reasons'].append('Original reference model or canonical ecological copy')
        if h in seen: row['reasons'].append('Canonical ecological duplicate of '+seen[h])
        else:seen[h]=p.stem
        if not m:row['reasons'].append('No existing model metadata establishing real marine identity')
        currency=m.get('currency_units','').lower().replace(' ','')
        if 'wet' not in currency:row['reasons'].append('Native currency is unknown or not wet weight; incompatible with fixed /9 convention')
        if any(x in typ for x in ['fresh','reservoir','river','lake']) and not any(x in typ for x in ['estuar','coastal','marine']):
            row['reasons'].append('Metadata identifies a nonmarine ecosystem')
        if any(x in name for x in ['reservoir','tapajos','paraná river','garonne','sirinhaém river']):row['reasons'].append('Nonmarine model identity')
        if not row['reasons'] and not typ:row['reasons'].append('Missing ecosystem type; marine identity not established by metadata')
        row['stratum']=strata(row)
        if row['reasons']:row['status']='excluded'
        rows.append(row)
    return rows

def detritus_source_checks(data,growth,predation,production,migration):
    """Reject source routes erased by loading and unobserved baseline stock financing."""
    det=list(data.groups_data.index[data.groups_data.trophic_info=='DET']);_,fate=ModelData.get_DC(data.data_json)
    raw=fate.reindex(index=det,columns=det).fillna(0);final=data.det_fate.loc[det,det]
    meaningful=(raw.abs()>1e-12)&((raw-final).abs()>1e-8)
    reasons=[]
    if meaningful.any().any():reasons.append('Nonzero source detritus onward/retention fate is overwritten by the frozen loader; source-faithful recycling baseline not established')
    draws=[]
    for i in det:
        tol=max(1e-10,1e-4*max(abs(production[i]),abs(predation[i]),abs(migration[i])))
        supplied=data.groups_data.at[i,'biomass_accum']
        explicit=pd.notna(supplied) and supplied<0 and abs(growth[i]-supplied)<=tol
        if growth[i]<-tol and not explicit:draws.append(int(i))
    if draws:reasons.append('Baseline detritus consumption is financed by invented negative accumulation for groups '+str(draws)+'; missing source inflow cannot be repaired as stock draw')
    return reasons,dict(nonzero_fate_overwritten=bool(meaningful.any().any()),negative_inferred_detritus_accumulation_groups=draws,
        fate_class='explicit_nonzero_source_route_overwritten' if meaningful.any().any() else ('zero_row_identity_bookkeeping' if not np.allclose(raw,final) else 'unchanged'),
        raw_detritus_fate_matrix=raw.to_dict())

def refresh_cached_eligibility(row):
    data=ModelData(str(ROOT/row['snapshot_path']))
    ledger=pd.read_csv(ROOT/'results/models'/row['model_id']/'flow_ledger.csv');b=ledger[ledger.route=='S0'].set_index('group_id')
    reasons,details=detritus_source_checks(data,b.accumulation,b.predation,b.production,b.migration)
    row['screening']['detritus_source_checks']=details;row['eligibility_revision']=2
    if reasons:row.update(status='rejected_source_fidelity',selected=False,reasons=reasons)
    return row

def screen_one(row):
    path=ROOT/row['snapshot_path']; reasons=[];report={};changes=[]
    with warnings.catch_warnings(record=True) as caught,contextlib.redirect_stdout(io.StringIO()) as log:
        try:
            data=ModelData(str(path));raw=data.groups_data
            regular=raw.index[raw.trophic_info=='Regular'];living=raw.index[raw.trophic_info.isin(['PP','Regular'])];det=raw.index[raw.trophic_info=='DET']
            if not len(regular) or not len(det) or not (raw.trophic_info=='PP').any():reasons.append('Missing consumer, producer or detritus representation')
            for ids,cols in [(living,['biomass','p','ee','catch']),(regular,['q'])]:
                if not np.isfinite(raw.loc[ids,cols].to_numpy()).all():reasons.append('Missing/nonfinite required source inputs: '+','.join(cols))
            if (raw.loc[living,['biomass','p']]<=0).any().any() or (raw.loc[regular,'q']<=0).any():reasons.append('Nonpositive living biomass/production or consumer consumption')
            if (raw.loc[living,'ee']<-1e-8).any() or (raw.loc[living,'ee']>1+1e-8).any():reasons.append('Raw living EE outside [0,1]')
            if (raw.loc[living,'catch']<-1e-8).any():reasons.append('Negative living harvest')
            H=float(raw.loc[living,'catch'].sum());report['native_harvest']=H
            if not np.isfinite(H) or H<=0:reasons.append('No positive original living-group modeled harvest')
            dc=data.DC.loc[regular];dev=(dc.sum(axis=1)-1).abs()
            report['raw_diet_max_sum_deviation']=float(dev.max())
            if not np.isfinite(dc.to_numpy()).all() or (dc<0).any().any() or dev.max()>.001:reasons.append('Raw diet exceeds 0.001 rounding tolerance or contains invalid fractions')
            _,rawf=ModelData.get_DC(data.data_json);rawf=rawf.reindex(index=raw.index,columns=det).fillna(0)
            if rawf.loc[living].sum(axis=1).max()>1+1e-8 or (rawf<0).any().any():reasons.append('Raw detritus fate is negative/overallocated')
            if (rawf.loc[living].sum(axis=1)<=1e-9).all():reasons.append('No documented natural detritus fate; loader closed-system default is insufficient for added-model eligibility')
            report['raw_detritus_export']=float(raw.loc[det,'catch'].sum())
            report['raw_detritus_onward_fate_changed']=not np.allclose(rawf.loc[det].to_numpy(),data.det_fate.loc[det].to_numpy())
            if reasons:return dict(status='rejected_raw',reasons=reasons,screening=report),changes
            base=PPRCalculator.from_modeldata(data,**SETTINGS)
            missing_living=raw.loc[living,'biomass_accum'].isna(); inferred=base.growth.loc[living][missing_living]
            inferredrel=(inferred.abs()/base.p.reindex(inferred.index).abs().clip(lower=1e-10))
            report['inferred_living_accumulation_max_relative']=float(inferredrel.max()) if len(inferredrel) else 0.
            if (inferredrel>1e-4).any():reasons.append('Material inferred living biomass accumulation; no invented closure accepted')
            for col in ['biomass','p','q','ee','catch','biomass_accum','respiration','gs','net_migration']:
                ids=regular if col in ['q','respiration','gs'] else living
                a=raw.loc[ids,col];b=base._groups_df.loc[ids,col]; supplied=a.notna()
                delta=(a[supplied]-b[supplied]).abs()/a[supplied].abs().clip(lower=1e-10)
                if (delta>1e-4).any():reasons.append('Initializer materially changes supplied living '+col)
            cal,ledger=make_scenario(base,0,'SC');diag=physical_diagnostics(cal,ledger);report['physical']=diag
            det_reasons,det_details=detritus_source_checks(data,base.growth,base.predation,base.p,base.net_migration)
            reasons+=det_reasons;report['detritus_source_checks']=det_details
            if not diag['ledger_closes']:reasons.append('Physical baseline exceeds prespecified closure tolerances')
            if diag['negative_physical_flows']:reasons.append('Negative physical baseline flows')
            if diag['min_ee']<-1e-8 or diag['max_ee']>1+1e-8:reasons.append('Initialized living EE outside [0,1]')
            if not np.isfinite(base._groups_df.loc[living,['p','q','M0','respiration','egestion','biomass_accum']].to_numpy()).all():reasons.append('Nonfinite initialized required living flows')
            changes=source_adjustments(base,dict(model_id=row['model_id']))
            if reasons:return dict(status='rejected_physical',reasons=sorted(set(reasons)),screening=report),changes
            outcomes={}
            for method in ['standard_fixed_baseline_TL','new_GE','new_TE_EEfix','new_WithEgestion']:
                try:
                    frame=calculate(cal,method);d=numeric_diagnostics(cal,method,frame,[])
                    ok=not d['nonfinite_cells'] and not d['negative_source_cells'] and all(d.get(k) is None or d[k]<1 for k in ['rho_living','rho_detritus'])
                    if method!='standard_fixed_baseline_TL':ok=ok and d.get('ledger_sppr_relative_gap',float('inf'))<=.05
                    outcomes[method]=dict(valid=bool(ok),diagnostics=d)
                except Exception as e:outcomes[method]=dict(valid=False,error=str(e))
            report['baseline_methods']=outcomes
            if not outcomes['standard_fixed_baseline_TL']['valid']:reasons.append('Unusable standard baseline')
            if not any(outcomes[m]['valid'] for m in outcomes if m!='standard_fixed_baseline_TL'):reasons.append('No usable recycling-aware baseline at frozen settings')
            report['initializer_output']=log.getvalue();report['warnings']=[str(x.message) for x in caught]
            return dict(status='eligible' if not reasons else 'rejected_methods',reasons=reasons,screening=report),changes
        except Exception as e:
            report['initializer_output']=log.getvalue();report['warnings']=[str(x.message) for x in caught]
            return dict(status='rejected_exception',reasons=[type(e).__name__+': '+str(e)],screening=report),changes

def worker(row,target):
    result,changes=screen_one(row)
    write_json(target,dict(result=result,changes=changes))

def run():
    start=time.time();rows=inventory();buckets=defaultdict(list);changes=[]
    for row in rows:
        if row['status']=='inventory_candidate':buckets[(0 if '/EwE_jsons/' in row['snapshot_path'].replace('\\','/') else 1,row['stratum'])].append(row)
    for values in buckets.values():values.sort(key=lambda r:(r['metadata'].get('ecosystem_type',''),0 if r['group_count']<20 else 1 if r['group_count']<40 else 2,int(r['model_id'].split('_')[1])))
    queue=[]
    for corpus in [0,1]:
        while any(v for k,v in buckets.items() if k[0]==corpus):
            for key in sorted(k for k in buckets if k[0]==corpus):
                if buckets[key]:queue.append(buckets[key].pop(0))
    priorpath=ROOT/'results/candidate_screening.json'
    prior={r['model_id']:r for r in json.loads(priorpath.read_text(encoding='utf-8'))['candidates']} if priorpath.exists() else {}
    selected=[]
    for rank,row in enumerate(queue,1):
        row['selection_rank']=rank
        if len(selected)>=20:
            row['status']='not_screened_target_reached';continue
        print('SCREEN',rank,row['model_id'],flush=True)
        prev=prior.get(row['model_id'],{})
        cached=ROOT/'verification'/('screen_'+row['model_id']+'.json')
        if prev.get('status') in ['eligible','rejected_raw','rejected_physical','rejected_methods','rejected_exception','not_assessed_resource_limit','rejected_source_fidelity']:
            row.update(prev)
            if row['status']=='eligible' and row.get('eligibility_revision',1)<2:
                row=refresh_cached_eligibility(row)
            if cached.exists():changes+=json.loads(cached.read_text(encoding='utf-8'))['changes']
        else:
            proc=multiprocessing.get_context('spawn').Process(target=worker,args=(row,cached));proc.start();proc.join(180)
            if proc.is_alive():
                proc.terminate();proc.join()
                row.update(status='not_assessed_resource_limit',reasons=['Baseline screening exceeded the 180-second per-candidate resource limit; numerical eligibility not established'])
            elif cached.exists():
                out=json.loads(cached.read_text(encoding='utf-8'));row.update(out['result']);changes+=out['changes']
                row['eligibility_revision']=2
            else:row.update(status='rejected_exception',reasons=['Screening worker exited without a result'])
        if row['status']=='eligible':row['selected']=True;selected.append(row)
        print(row['status'],len(selected),'; '.join(row['reasons']),flush=True)
        write_json(ROOT/'results/candidate_screening.json',dict(policy_sha256=hashlib.sha256((ROOT/'SELECTION_POLICY.md').read_bytes()).hexdigest(),candidates=rows))
    write_json(ROOT/'results/candidate_screening.json',dict(policy_sha256=hashlib.sha256((ROOT/'SELECTION_POLICY.md').read_bytes()).hexdigest(),candidates=rows,elapsed_seconds=time.time()-start,status_counts=Counter(r['status'] for r in rows)))
    write_json(ROOT/'results/selected_models.json',selected)
    pd.DataFrame(changes).to_csv(ROOT/'results/screening_parameter_changes.csv',index=False)
    pd.DataFrame([{k:json.dumps(clean(v),ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows]).to_csv(ROOT/'results/candidate_screening.csv',index=False)
    print('SELECTED',len(selected),'elapsed',time.time()-start,flush=True)
if __name__=='__main__':run()
