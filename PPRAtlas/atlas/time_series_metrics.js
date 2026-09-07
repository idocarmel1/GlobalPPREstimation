/* Pure aggregation shared by the browser and numerical checks. */
(function(root, factory) {
  const api=factory();
  if(typeof module==='object' && module.exports) module.exports=api;
  else root.PPRTimeSeries=api;
})(typeof globalThis==='object'?globalThis:this, function() {
  'use strict';
  const finite=v=>typeof v==='number' && Number.isFinite(v);
  const sample=(v,i)=>Array.isArray(v)?v[i]:v;

  function aggregate(db,state) {
    const years=state.years || db.years;
    const indices=years.map(y=>db.years.indexOf(Number(y)));
    const ids=[...new Set(state.units || [])];
    const method=db.ppr_methods.find(m=>m.id===state.method);
    const ratio=state.mode==='ratio';
    const gaps=state.allow_gaps && ids.length===1;
    const validRequest=indices.every(i=>i>=0) && years.length>0 && method &&
      method.scopes.includes(state.scope) && (!ratio || db.npp_methods.some(m=>m.id===state.npp));
    const included=[],excluded=[],records=[],modelIds={};
    for(const id of ids) {
      const unit=db.units[id];let reason=null,record=null;
      if(!validRequest) reason='Unknown year, method or unsupported source scope.';
      else if(!unit) reason='Ecosystem is absent from this export.';
      else if(method.kind==='taxon') record=unit.simple;
      else {
        const chosen=state.models?.[id] ?? unit.default_model;
        const model=unit.models.find(m=>m.id===chosen);
        if(!model) reason='No model selected or model unavailable.';
        else if(!model.verified) reason='Model has no verified PPR workbook.';
        else {
          modelIds[id]=model.id;
          record=model.scopes?.[state.scope]?.methods?.[state.method];
          if(!record) reason='Method unavailable for this model and scope.';
          else if(record.status!=='ok') reason=`Method unavailable: ${record.status}.`;
        }
      }
      const present=i=>finite(record?.ppr?.[i]) && record.ppr[i]>=0;
      if(!reason && (!record || !(gaps?indices.some(present):indices.every(present))))
        reason='PPR lacks a complete annual series.';
      const nppPresent=i=>finite(sample(unit?.npp?.[state.npp],i)) && sample(unit.npp[state.npp],i)>0 && present(i);
      if(!reason && ratio && !(gaps?indices.some(nppPresent):indices.every(nppPresent)))
        reason='NPP unavailable or nonpositive for one or more years.';
      if(reason) excluded.push({id,name:unit?.name || id,reason});
      else {included.push(id);records.push({unit,record});}
    }
    const points=years.map((year,k)=>{
      const i=indices[k];
      if(!records.length || records.some(r=>!finite(r.record.ppr[i]) || r.record.ppr[i]<0 || ratio && (!finite(sample(r.unit.npp[state.npp],i)) || sample(r.unit.npp[state.npp],i)<=0)))
        return {year:Number(year),value:null,ppr:null,npp:null,catch:null,covered_catch:null,coverage:null};
      // Audited input totals are wet weight; plot and CSV masses use carbon.
      const ppr=records.reduce((sum,r)=>sum+r.record.ppr[i],0) / 9;
      const npp=ratio?records.reduce((sum,r)=>sum+sample(r.unit.npp[state.npp],i),0):null;
      const catches=records.map(r=>r.unit.simple?.catch?.[i]);
      const covered=records.map(r=>r.record.covered_catch?.[i]);
      const totalCatch=catches.every(finite)?catches.reduce((a,b)=>a+b,0):null;
      const coveredCatch=covered.every(finite)?covered.reduce((a,b)=>a+b,0):null;
      return {year:Number(year),value:ratio?100*ppr/npp:ppr,ppr,npp,catch:totalCatch,covered_catch:coveredCatch,
        coverage:totalCatch>0 && coveredCatch!==null?coveredCatch/totalCatch:null};
    });
    return {points,included,excluded,selected:ids.length,npp_year:db.npp_year,
      model_ids:Object.fromEntries(included.filter(id=>modelIds[id]).map(id=>[id,modelIds[id]])),
      annual_npp:ratio && records.some(r=>Array.isArray(r.unit.npp[state.npp])),
      reason:!validRequest?'Unknown year, method or unsupported source scope.':ids.length?'':'Select at least one ecosystem.'};
  }

  function toCSV(result,state) {
    const escape=value=>value==null?'':`"${String(value).replaceAll('"','""')}"`;
    const header='year,value,ppr_tonnes_carbon,npp_tonnes_carbon,catch_tonnes,covered_catch_tonnes,catch_coverage,included_ecosystems,selected_ecosystems,metric,ppr_method,source_scope,npp_method,npp_baseline_year,included_ids,model_overrides,model_ids';
    return header+'\n'+result.points.map(p=>[p.year,p.value,p.ppr,p.npp,p.catch,p.covered_catch,p.coverage,
      result.included.length,result.selected,state.mode,state.method,state.scope,state.mode==='ratio'?state.npp:null,
      state.mode==='ratio' && !result.annual_npp?result.npp_year:null,result.included.join(';'),JSON.stringify(state.models||{}),JSON.stringify(result.model_ids)].map(escape).join(',')).join('\n')+'\n';
  }

  function compare(db,state) {
    const methods=[...new Set(state.methods || [])];
    const ids=[...new Set(state.units || [])];
    const baseline=state.baseline || null;
    const normalized=baseline!==null;
    const usable=result=>result.points.some(point=>finite(point.value));
    const unavailableReason=result=>result.reason ||
      [...new Set(result.excluded.map(item=>item.reason))].join(' ') || 'No usable annual values.';
    const initial=new Map([...new Set([...methods,...(baseline?[baseline]:[])])]
      .map(method=>[method,aggregate(db,{...state,method})]));

    // Keep the established single-method result and download exactly as before.
    if(methods.length===1 && !normalized) {
      const result=initial.get(methods[0]);
      return {...result,series:[{method:methods[0],...result}],baseline:null,baseline_model_ids:{},normalized:false};
    }
    if(!methods.length) {
      const empty=aggregate(db,{...state,method:state.method || db.ppr_methods[0]?.id,units:[]});
      return {...empty,series:[],selected:ids.length,baseline,baseline_model_ids:{},normalized,
        excluded:ids.map(id=>({id,name:db.units[id]?.name || id,reason:'No calculation method selected.'})),
        reason:'Select at least one calculation method.'};
    }

    const active=methods.filter(method=>usable(initial.get(method)));
    const baselineInitial=baseline?initial.get(baseline):null;
    const baselineFailure=baseline && !usable(baselineInitial)?
      `Baseline ${baseline} unavailable: ${unavailableReason(baselineInitial)}`:'';
    const constraints=[...new Set([...active,...(baseline?[baseline]:[])])];
    const common=!active.length || baselineFailure?[]:
      ids.filter(id=>constraints.every(method=>initial.get(method).included.includes(id)));
    const excluded=ids.filter(id=>!common.includes(id)).map(id=>{
      const causes=(constraints.length?constraints:methods).flatMap(method=>{
        const exclusion=initial.get(method).excluded.find(item=>item.id===id);
        return exclusion?[`${method===baseline?'Baseline':'Method'} ${method}: ${exclusion.reason}`]:[];
      });
      return {id,name:db.units[id]?.name || id,
        reason:causes.join(' ') || baselineFailure || 'No common ecosystem cohort across the selected methods.'};
    });
    const sharedReason=!ids.length?'Select at least one ecosystem.':baselineFailure ||
      (!active.length?'No selected calculation method has an available series.':
        !common.length?'No common ecosystem cohort across the selected methods.':'');
    const baselineResult=baseline && common.length?
      aggregate(db,{...state,method:baseline,units:common}):null;

    const series=methods.map(method=>{
      const original=initial.get(method),isActive=active.includes(method);
      const result=isActive?aggregate(db,{...state,method,units:common}):original;
      const reason=isActive?sharedReason:
        [unavailableReason(original),baselineFailure].filter(Boolean).join(' ');
      const points=result.points.map((point,index)=>{
        const reference=baselineResult?.points[index];
        const baselineValue=reference?.value ?? null;
        let value=point.value;
        if(normalized) {
          value=finite(value) && finite(baselineValue) && baselineValue>0?value/baselineValue:null;
          if(!finite(value)) value=null;
        }
        const pointReason=finite(value)?'':reason ||
          (normalized && !finite(baselineValue)?`Baseline ${baseline} is unavailable for ${point.year}.`:
            normalized && baselineValue<=0?`Baseline ${baseline} is zero or nonpositive for ${point.year}.`:
              !finite(point.value)?`Method ${method} is unavailable for ${point.year}.`:
                `Normalized value is not finite for ${point.year}.`);
        return {...point,value,unnormalized_value:point.value,
          baseline_value:baselineValue,baseline_ppr:reference?.ppr ?? null,
          baseline_covered_catch:reference?.covered_catch ?? null,unavailable_reason:pointReason};
      });
      return {...result,method,points,selected:ids.length,
        ...(isActive?{included:common,excluded}:{}),
        reason:reason || (normalized && !points.some(point=>finite(point.value))?
          `Baseline ${baseline} has no positive matching annual values.`:'')};
    });
    return {series,included:common,excluded,selected:ids.length,points:series[0].points,
      baseline,baseline_model_ids:baselineResult?.model_ids || {},normalized,reason:sharedReason ||
        (normalized && !series.some(result=>usable(result))?`Baseline ${baseline} has no positive matching annual values.`:''),
      npp_year:db.npp_year,annual_npp:series.some(result=>result.annual_npp) || Boolean(baselineResult?.annual_npp)};
  }

  function comparisonToCSV(result,state) {
    if(result.series.length===1 && !result.normalized)
      return toCSV(result.series[0],{...state,method:result.series[0].method});
    const escape=value=>value==null?'':`"${String(value).replaceAll('"','""')}"`;
    const header='year,ppr_method,value,ppr_tonnes_carbon,npp_tonnes_carbon,catch_tonnes,covered_catch_tonnes,catch_coverage,included_ecosystems,selected_ecosystems,metric,source_scope,npp_method,npp_baseline_year,included_ids,model_overrides,model_ids,baseline_method,baseline_model_ids,baseline_value,baseline_ppr_tonnes_carbon,baseline_covered_catch_tonnes,unnormalized_value,normalized,unavailable_reason';
    const rows=result.series.flatMap(series=>series.points.map(point=>[
      point.year,series.method,point.value,point.ppr,point.npp,point.catch,point.covered_catch,point.coverage,
      series.included.length,series.selected,state.mode,state.scope,state.mode==='ratio'?state.npp:null,
      state.mode==='ratio' && !series.annual_npp?series.npp_year:null,series.included.join(';'),
      JSON.stringify(state.models || {}),JSON.stringify(series.model_ids),result.baseline,JSON.stringify(result.baseline_model_ids || {}),
      point.baseline_value,point.baseline_ppr,point.baseline_covered_catch,point.unnormalized_value,
      result.normalized,point.unavailable_reason || series.reason].map(escape).join(',')));
    return header+'\n'+rows.join('\n')+(rows.length?'\n':'');
  }
  return {aggregate,toCSV,compare,comparisonToCSV,finite};
});
