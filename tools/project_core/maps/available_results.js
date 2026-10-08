/* Display retained results without changing their scientific status or inputs. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.PPRAvailableResults=api;
})(typeof globalThis==='object'?globalThis:this,function(){
  'use strict';
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const provisional=status=>String(status).startsWith('provisional:');
  const reviewed=model=>model?.verified===true&&model.researcher_review?.status==='Validated by researcher';
  // These are retained numerical diagnoses, never readiness or missing-result states.
  const diagnostic=status=>/^(?:WARN\b|FAIL\b|DIVERGED\b|IMPLAUSIBLE\b|diagnostic\s+(?:WARN|FAIL)\b)/i.test(String(status));
  const admitted=(model,status,method)=>reviewed(model)&&!String(method||'').startsWith('MC_')&&diagnostic(status);
  const allowed=(model,status,method)=>status==='ok'||provisional(status)||admitted(model,status,method);
  const signed=(model,status,method)=>provisional(status)||(reviewed(model)&&!String(method||'').startsWith('MC_')&&allowed(model,status,method));

  function retainedAnnualRecord(unit,model,record,state,years){
    if(!record||!reviewed(model)||String(state.method).startsWith('MC_')||!allowed(model,record.status,state.method))return record;
    const source=unit.group_inputs?{...unit,...unit.group_inputs}:unit;
    const scope=model.taxon_scopes?.[state.scope],mappings=model.group_data?.mappings;
    const column=scope?.methods?.indexOf(state.method);
    if(!(column>=0)||!allowed(model,scope.status?.[state.method],state.method)||!Array.isArray(mappings))return record;
    const basis=state.catch_basis||'landings',treatment=state.unidentified||'method';
    const matrix=basis==='catch'?(source.full_precision_catch||source.catch):source[basis];
    if(!Array.isArray(matrix)||matrix.length!==(source.taxa||[]).length)return record;
    const affected=new Map((source.unidentified?.taxa||[]).map(t=>[t.name,t]));
    const ppr=[...(record.ppr||[])],covered=[...(record.covered_catch||[])];
    let reconstructed=false;
    years.forEach((year,index)=>{
      if(state.years&&!state.years.some(selected=>Number(selected)===Number(year)))return;
      if(finite(ppr[index]))return;
      const yi=(source.years||[]).indexOf(Number(year));
      if(yi<0||matrix.some(row=>!finite(row?.[yi])||row[yi]<0))return;
      let wet=0,support=0,total=0,hasCoefficient=false;
      matrix.forEach((row,i)=>{
        const c=row[yi];total+=c;
        const mapping=mappings[i]||[];
        // The producer preserves taxon order. Require its complete retained
        // allocation before using the existing taxon coefficient for display.
        if(!mapping.length||mapping.some(([g,w])=>!Number.isInteger(g)||!model.group_data.groups?.[g]||!finite(w)||w<0)||Math.abs(mapping.reduce((sum,[,w])=>sum+w,0)-1)>1e-6)return;
        let coefficient=scope.values?.[i]?.[column];
        const residual=affected.get(source.taxa[i]);
        if(residual&&treatment!=='method')coefficient=treatment==='zero'?0:residual.simple_sppr;
        if(!finite(coefficient)||(coefficient<0&&!signed(model,scope.status[state.method],state.method)))return;
        hasCoefficient=true;wet+=c*coefficient;support+=c;
      });
      if(!hasCoefficient||(total>0&&support===0)||!finite(wet))return;
      ppr[index]=wet;covered[index]=support;reconstructed=true;
    });
    return reconstructed?{...record,ppr,covered_catch:covered,retained_numeric_display:true}:record;
  }
  function compare(db,state,aggregate,nppSeries){
    const methods=[...new Set(state.methods||[])],ids=[...new Set(state.units||[])];
    const years=state.years||db.years;
    const series=methods.map(method=>{
      // One existing aggregate per year keeps every method's support independent.
      // NPP lookup and all mapping, diagnostic and group-selection gates stay there.
      const annual=years.map(year=>aggregate(db,{...state,method,years:[year]}));
      const included=ids.filter(id=>annual.some(result=>result.included.includes(id)));
      const excluded=ids.filter(id=>!included.includes(id)).map(id=>({id,name:db.units[id]?.name||id,
        reason:[...new Set(annual.flatMap(result=>result.excluded.filter(item=>item.id===id).map(item=>item.reason)))].join(' ')||'No available annual result.'}));
      const points=annual.map((result,index)=>{
        const point=result.points[0]||{year:Number(years[index]),value:null};
        return {...point,included:result.included,included_ids:result.included,included_count:result.included.length,
          excluded:result.excluded,missing_result_count:result.excluded.length,model_ids:result.model_ids,
          review_flags:result.review_flags||[],unnormalized_value:point.value,
          unavailable_reason:finite(point.value)?'':result.reason||result.excluded.map(item=>item.reason).join(' ')||`Method ${method} is unavailable for ${point.year}.`};
      });
      const empty=annual[0]||aggregate(db,{...state,method,years:[],units:[]});
      return {...empty,method,points,included,excluded,selected:ids.length,
        model_ids:Object.assign({},...annual.map(result=>result.model_ids)),
        review_flags:[...new Set(annual.flatMap(result=>result.review_flags||[]))],
        unidentified_taxa:Object.assign({},...annual.map(result=>result.unidentified_taxa)),
        unidentified_classifier:Object.assign({},...annual.map(result=>result.unidentified_classifier)),
        npp_reference:state.mode==='ratio'?nppSeries.reference(db,included,state):null,
        reason:points.some(point=>finite(point.value))?'':empty.reason||excluded.map(item=>item.reason).join(' ')||'No available annual result.'};
    });
    const included=ids.filter(id=>series.some(result=>result.included.includes(id)));
    const excluded=ids.filter(id=>!included.includes(id)).map(id=>({id,name:db.units[id]?.name||id,
      reason:series.flatMap(result=>result.excluded.filter(item=>item.id===id).map(item=>`${result.method}: ${item.reason}`)).join(' ')}));
    return {...series[0],series,included,excluded,selected:ids.length,points:series[0]?.points||[],
      baseline:null,baseline_model_ids:{},normalized:false,independent_availability:true,
      npp_reference:state.mode==='ratio'?nppSeries.reference(db,included,state):null,
      reason:!ids.length?'Select at least one ecosystem.':series.some(result=>result.points.some(point=>finite(point.value)))?'':'No selected calculation method has an available series.'};
  }
  return {allowed,signed,retainedAnnualRecord,compare};
});
