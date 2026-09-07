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
      const ppr=records.reduce((sum,r)=>sum+r.record.ppr[i],0);
      const npp=ratio?records.reduce((sum,r)=>sum+sample(r.unit.npp[state.npp],i),0):null;
      const catches=records.map(r=>r.unit.simple?.catch?.[i]);
      const covered=records.map(r=>r.record.covered_catch?.[i]);
      const totalCatch=catches.every(finite)?catches.reduce((a,b)=>a+b,0):null;
      const coveredCatch=covered.every(finite)?covered.reduce((a,b)=>a+b,0):null;
      return {year:Number(year),value:ratio?100*ppr/9/npp:ppr,ppr,npp,catch:totalCatch,covered_catch:coveredCatch,
        coverage:totalCatch>0 && coveredCatch!==null?coveredCatch/totalCatch:null};
    });
    return {points,included,excluded,selected:ids.length,npp_year:db.npp_year,
      model_ids:Object.fromEntries(included.filter(id=>modelIds[id]).map(id=>[id,modelIds[id]])),
      annual_npp:ratio && records.some(r=>Array.isArray(r.unit.npp[state.npp])),
      reason:!validRequest?'Unknown year, method or unsupported source scope.':ids.length?'':'Select at least one ecosystem.'};
  }

  function toCSV(result,state) {
    const escape=value=>value==null?'':`"${String(value).replaceAll('"','""')}"`;
    const header='year,value,ppr_tonnes_wet_pp,npp_tonnes_carbon,catch_tonnes,covered_catch_tonnes,catch_coverage,included_ecosystems,selected_ecosystems,metric,ppr_method,source_scope,npp_method,npp_baseline_year,included_ids,model_overrides,model_ids';
    return header+'\n'+result.points.map(p=>[p.year,p.value,p.ppr,p.npp,p.catch,p.covered_catch,p.coverage,
      result.included.length,result.selected,state.mode,state.method,state.scope,state.mode==='ratio'?state.npp:null,
      state.mode==='ratio' && !result.annual_npp?result.npp_year:null,result.included.join(';'),JSON.stringify(state.models||{}),JSON.stringify(result.model_ids)].map(escape).join(',')).join('\n')+'\n';
  }
  return {aggregate,toCSV,finite};
});
