/* Graph-only NPP sums and fixed-reference lookup, independent of PPR availability. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.PPRTimeSeriesNPP=api;
})(typeof globalThis==='object'?globalThis:this,function(){
  'use strict';
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const valid=v=>finite(v)&&v>=0;
  const scope=state=>state.mode==='ratio'&&state.npp_scope==='global'?'global':'selected';
  function resolve(years,values,year,policy,metadata={},positiveOnly=false){
    const usableValue=v=>valid(v)&&(!positiveOnly||v>0);
    const i=years.indexOf(Number(year)),annual=Array.isArray(values);
    const raw=annual?values[i]:values;
    let value=raw,sourceYear=Number(year),substituted=false;
    if(i>=0&&annual&&raw==null&&policy==='earliest'){
      const first=years.map((y,j)=>({year:Number(y),value:values[j]})).filter(p=>usableValue(p.value)).sort((a,b)=>a.year-b.year)[0];
      if(first&&Number(year)<first.year){value=first.value;sourceYear=first.year;substituted=true;}
    }
    const usable=i>=0&&usableValue(value);
    return {value:usable?value:null,source_year:usable?sourceYear:null,substituted:usable&&substituted,metadata:metadata[String(usable?sourceYear:year)]||null};
  }
  function reference(db,ids,state){
    if(scope(state)==='global'){
      const source=db.global_npp||{};
      return {...source,values:undefined,metadata:undefined,id:source.id||'global_atlas_npp',label:source.label||'Global atlas NPP',unit_ids:source.unit_ids||[],method:'atlas_ensemble'};
    }
    const ensemble=state.npp?.startsWith('ens_');
    return {id:'selected_ecosystems',label:'Selected ecosystems',unit_ids:[...ids],method:state.npp,
      ensemble_convention:ensemble?'Sum of regional '+(state.npp.includes('median')?'ensemble medians':state.npp.includes('min')?'ensemble minima':'ensemble maxima')+'; each region retains its available algorithm support. This is not an ensemble statistic of global model totals.':'Sum of the selected regional NPP calculation.',
      geography:'Selected ecosystem identities; boundaries may overlap. This regional sum is not a unique world-ocean total.',
      overlap_policy:'Original selected regional totals retained; overlapping selections are not deduplicated.',source:db.npp_source};
  }
  function fields(ref,state,year,value,available,missing,provenance,extra={}){
    return {npp:value,npp_denominator:state.mode==='ratio'?value:null,npp_scope:scope(state),
      npp_reference_id:ref.id,npp_reference_ids:ref.unit_ids,npp_ensemble_convention:ref.ensemble_convention,
      npp_method:ref.method,npp_source:ref.source,npp_available_ids:available,npp_missing_ids:missing,
      npp_provenance:provenance,npp_reference_metadata:extra.metadata||null,
      npp_estimated:extra.estimated||false,npp_substituted_ids:extra.substituted||[],npp_source_years:extra.sourceYears||{},
      npp_status:value===null?'unavailable':extra.metadata?.coverage_limited?'coverage_limited':extra.estimated?'earliest_year_estimate':'available',
      npp_reason:value===null?(extra.reason||'Annual NPP unavailable for the complete reference geography.'):extra.metadata?.coverage_limited?extra.reason||'Coverage-limited source-water estimate.':'',
      npp_reference_geography:ref.geography,npp_overlap_policy:ref.overlap_policy};
  }
  function point(db,ids,state,year){
    const ref=reference(db,ids,state);
    if(scope(state)==='global'){
      const source=db.global_npp||{},resolved=resolve(db.years,source.values,year,state.npp_fill,source.metadata,true);
      const metadata=resolved.metadata;
      // The producer certifies the fixed geography. Explicitly incomplete rows
      // never become denominators even if an available-region subtotal is present.
      const incomplete=metadata?.complete===false||['incomplete','unsupported','unavailable','failed'].includes(metadata?.status);
      const value=!incomplete&&finite(resolved.value)&&resolved.value>0?resolved.value:null;
      return fields(ref,state,year,value,metadata?.available_ids||[],metadata?.missing_ids||(value===null?ref.unit_ids:[]),{[ref.id]:metadata||null},
        {metadata,estimated:value!==null&&resolved.substituted,substituted:value!==null&&resolved.substituted?[ref.id]:[],sourceYears:value!==null?{[ref.id]:resolved.source_year}:{},reason:metadata?.reason||'The fixed global atlas NPP reference is unavailable for this year.'});
    }
    const resolved=ids.map(id=>resolve(db.years,db.units[id]?.npp?.[state.npp],year,state.npp_fill,db.units[id]?.npp_metadata,state.mode==='ratio'));
    const available=ids.filter((id,i)=>valid(resolved[i].value)),missing=ids.filter(id=>!available.includes(id));
    let value=ids.length&&!missing.length?resolved.reduce((sum,item)=>sum+item.value,0):null;
    if(state.mode==='ratio'&&!(value>0))value=null;
    return fields(ref,state,year,value,available,missing,Object.fromEntries(ids.map((id,i)=>[id,resolved[i].metadata])),
      {estimated:resolved.some(r=>r.substituted),substituted:ids.filter((id,i)=>resolved[i].substituted),sourceYears:Object.fromEntries(ids.filter((id,i)=>resolved[i].source_year!==null).map(id=>[id,resolved[ids.indexOf(id)].source_year]))});
  }
  function aggregate(db,state){
    const years=state.years||db.years,ids=[...new Set(state.units||[])];
    const validRequest=years.length>0&&years.every(y=>db.years.includes(Number(y)))&&db.npp_methods.some(m=>m.id===state.npp);
    const included=validRequest?ids.filter(id=>db.units[id]):[];
    const excluded=ids.filter(id=>!included.includes(id)).map(id=>({id,name:db.units[id]?.name||id,reason:!validRequest?'Unknown NPP calculation or year.':'Ecosystem is absent from this export.'}));
    const points=years.map(year=>{
      const npp=point(db,included,{...state,mode:'npp'},year);
      return {year:Number(year),value:npp.npp,ppr:null,catch:null,covered_catch:null,coverage:null,...npp,
        sensitivity:{hidden:true,status:'not_applicable',reason:'Discard-routing sensitivity does not apply to NPP.'}};
    });
    const ref=reference(db,included,{...state,mode:'npp'});
    return {points,included,excluded,selected:ids.length,model_ids:{},annual_npp:true,npp_year:null,npp_source:db.npp_source,npp_scope:'selected',npp_reference:ref,npp_method:state.npp,
      reason:!validRequest?'Unknown NPP calculation or year.':!ids.length?'Select at least one ecosystem.':!points.some(p=>valid(p.value))?'Annual NPP is unavailable for the complete selected region set in every selected year.':''};
  }
  const csvHeader=',npp_denominator_scope,npp_denominator_tonnes_carbon,npp_reference_id,npp_reference_ids,npp_ensemble_convention,npp_reference_geography,npp_overlap_policy,npp_available_ids,npp_missing_ids,npp_reference_metadata,npp_status,npp_reason';
  const csv=(p,result,state)=>state.mode==='ratio'||state.mode==='npp'?[p.npp_scope,p.npp_denominator,p.npp_reference_id,JSON.stringify(p.npp_reference_ids||[]),p.npp_ensemble_convention,typeof p.npp_reference_geography==='string'?p.npp_reference_geography:JSON.stringify(p.npp_reference_geography||{}),p.npp_overlap_policy,JSON.stringify(p.npp_available_ids||[]),JSON.stringify(p.npp_missing_ids||[]),JSON.stringify(p.npp_reference_metadata||{}),p.npp_status,p.npp_reason]:Array(12).fill(null);
  return {aggregate,point,reference,scope,csvHeader,csv};
});
