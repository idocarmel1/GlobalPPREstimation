/* Additional trend views reuse the existing selected-model calculations. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.PPRTrendExtras=api;
})(typeof globalThis==='object'?globalThis:this,function(){
  'use strict';
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  function selectedUnits(db,state){
    const ids=[...new Set(state.units||[])];
    if(state.review_filter!=='validated')return ids;
    return ids.filter(id=>{
      const unit=db.units[id],chosen=state.models?.[id]??unit?.default_model;
      const model=typeof chosen==='number'?unit?.models?.[chosen]:unit?.models?.find(m=>m.id===chosen);
      return model?.researcher_review?.status==='Validated by researcher';
    });
  }
  const scaling=state=>Boolean(state.global_estimate&&state.mode==='ratio'&&state.npp_scope==='global'&&!state.baseline);
  function scale(db,state,result,aggregate,coverageResult=result){
    if(!scaling(state))return result;
    const ids=selectedUnits(db,state),reference=db.global_npp?.unit_ids||[];
    const outside=ids.filter(id=>!reference.includes(id)),cache=new Map();
    const share=year=>{
      if(cache.has(year))return cache.get(year);
      const index=db.years.indexOf(Number(year)),missing=[];
      let global=0;
      for(const id of reference){
        let record=db.units[id]?.simple;
        if(state.unidentified&&state.unidentified!=='method')record=record?.['unidentified_'+state.unidentified];
        if((state.catch_basis||'landings')!=='landings'){
          const basis=record?.catch_bases?.[state.catch_basis];record=basis?{...record,...basis}:null;
        }
        const value=record?.ppr?.[index];
        if(record?.status!=='ok'||!finite(value)||value<0)missing.push(id);else global+=value/9;
      }
      const selected=aggregate(db,{...state,units:ids,years:[Number(year)],method:'simple trophic chain',scope:'all',mode:'ppr'});
      const selectedMissing=ids.filter(id=>!selected.included.includes(id));
      const numerator=selected.points[0]?.ppr;
      let reason='';
      if(!reference.length)reason='The fixed atlas simple-chain reference is absent.';
      else if(outside.length)reason='Selected regions outside the fixed atlas reference: '+outside.join(', ')+'.';
      else if(missing.length)reason='Global approximation unavailable: simple-chain PPR is missing in the fixed atlas reference for '+missing.map(id=>(db.units[id]?.name||id)+' ('+id+')').join(', ')+'.';
      else if(selectedMissing.length)reason='Selected-set simple-chain PPR is unavailable for '+selectedMissing.join(', ')+'.';
      else if(!finite(numerator)||numerator<=0||global<=0)reason='The selected-set and global simple-chain PPR totals must both be positive.';
      const data={simple_ppr_share:reason?null:numerator/global,selected_simple_ppr_tC:finite(numerator)?numerator:null,
        global_simple_ppr_tC:missing.length?null:global,global_simple_missing_ids:missing,selected_simple_missing_ids:selectedMissing,
        global_reference_id:db.global_npp?.id,global_reference_ids:reference,scaling_reason:reason};
      cache.set(year,data);return data;
    };
    const series=result.series.map(series=>({...series,global_estimate:true,points:series.points.map(point=>{
      const data=share(point.year),coverage=coverageResult.series.find(item=>item.method===series.method);
      const support=coverage?.points.find(item=>item.year===point.year);
      const missing=ids.filter(id=>!(support?.included_ids||coverage?.included||[]).includes(id));
      const reason=data.scaling_reason||(missing.length?'Selected-method PPR is unavailable for '+missing.join(', ')+'.':'');
      const value=!reason&&finite(point.value)&&finite(data.simple_ppr_share)?point.value/data.simple_ppr_share:null;
      const band=point.sensitivity;
      return {...point,...data,scaling_reason:reason,selected_method_missing_ids:missing,global_estimate:true,unscaled_value:point.value,value,
        unavailable_reason:reason||point.unavailable_reason||'',
        ...(band?{sensitivity:{...band,lower:finite(band.lower)&&finite(value)?band.lower/data.simple_ppr_share:null,
          upper:finite(band.upper)&&finite(value)?band.upper/data.simple_ppr_share:null}}:{})};
    })}));
    return {...result,series,points:series[0]?.points||[],global_estimate:true,
      reason:series.some(s=>s.points.some(p=>finite(p.value)))?'':series[0]?.points[0]?.unavailable_reason||result.reason};
  }
  const csvHeader=',global_approximation,unscaled_percent,selected_simple_share,selected_simple_ppr_tC,global_simple_ppr_tC,global_simple_missing_ids,selected_simple_missing_ids,selected_method_missing_ids,global_approximation_reason';
  const csv=point=>[Boolean(point.global_estimate),point.unscaled_value,point.simple_ppr_share,point.selected_simple_ppr_tC,point.global_simple_ppr_tC,(point.global_simple_missing_ids||[]).join(';'),(point.selected_simple_missing_ids||[]).join(';'),(point.selected_method_missing_ids||[]).join(';'),point.scaling_reason];
  function table(db,state,year,compare,aggregate){
    const units=selectedUnits(db,state),annual={...state,units,years:[Number(year)]};
    const methods=state.mode==='npp'?['npp']:[...new Set(state.methods||[])];
    const totalComparison=compare(db,annual);
    const values=ids=>{
      const raw=ids===units?totalComparison:compare(db,{...annual,units:ids,allow_gaps:true});
      const result=scaling(annual)?scale(db,annual,raw,aggregate,totalComparison):raw;
      return methods.map(method=>{
        const series=result.series.find(s=>s.method===method),point=series?.points[0];
        return {...point,method,value:finite(point?.value)?point.value:null,
          reason:point?.unavailable_reason||point?.npp_reason||series?.reason||
            series?.excluded?.map(e=>e.reason).join(' ')||'No retained result for this region, method and year.'};
      });
    };
    return {year:Number(year),methods,
      rows:units.map(id=>({id,name:db.units[id]?.name||id,values:values([id])}))
        .sort((a,b)=>a.name.localeCompare(b.name)||a.id.localeCompare(b.id)),
      total:{name:'Selected set',values:values(units)}};
  }
  return {selectedUnits,table,scale,scaling,csvHeader,csv};
});
