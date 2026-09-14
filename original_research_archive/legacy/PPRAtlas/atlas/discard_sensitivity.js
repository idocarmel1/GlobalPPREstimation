/* Display/aggregation of verified response exports; no food-web solving here. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.PPRDiscardSensitivity=api;
})(typeof globalThis==='object'?globalThis:this,function(){
  'use strict';
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const basis=state=>state.catch_basis||'landings';
  const enabled=state=>basis(state)==='landings'&&state.uncertainty!==false&&state.uncertainty!=='0';
  const unavailable=reason=>({status:'not_assessed',min_tC:null,max_tC:null,lower:null,upper:null,reason});
  function display(band,state,denominator=null){
    if(!enabled(state))return {...unavailable(basis(state)==='landings'?'Sensitivity hidden.':'Sensitivity is available for the landings view only.'),discard_fraction:band?.discard_fraction??null,hidden:true};
    if(!band)return unavailable('No tested compatible discard response for this model, method and scope.');
    const ratio=state.mode==='npp_ratio'||state.mode==='ratio';
    if(band.status!=='assessed'||!finite(band.min_tC)||!finite(band.max_tC))return {...band,lower:null,upper:null};
    if(ratio&&!(finite(denominator)&&denominator>0))return {...band,lower:null,upper:null,reason:'Annual NPP unavailable; carbon PPR endpoints remain in the export.'};
    const scale=ratio?100/denominator:1;
    return {...band,lower:band.min_tC*scale,upper:band.max_tC*scale,hidden:false};
  }
  function combine(bands){
    if(!bands.length||bands.some(b=>b?.status!=='assessed'))return unavailable('A compatible discard response is not assessed for every included ecosystem.');
    // Sum the same named route across the complete cohort, never independent
    // extrema that could mix different physical conventions among ecosystems.
    const names=['SC','SM','SE','SR'].filter(name=>bands.every(b=>finite(b.route_ppr_tC?.[name])));
    if(names.length<2)return unavailable('Fewer than two valid routing scenarios are shared by the complete ecosystem cohort.');
    const routes=Object.fromEntries(names.map(name=>[name,bands.reduce((sum,b)=>sum+b.route_ppr_tC[name],0)]));
    const values=Object.values(routes);
    return {status:'assessed',min_tC:Math.min(...values),max_tC:Math.max(...values),route_ppr_tC:routes,
      valid_routes:names,excluded_routes:['SC','SM','SE','SR'].filter(n=>!names.includes(n)),
      interpolated:bands.some(b=>b.interpolated),uncertainty_type:'Discard-routing sensitivity envelope; not a confidence interval',
      construction_invariant:bands.every(b=>b.construction_invariant),
      sources:bands.map(b=>({model_id:b.model_id,source_hash:b.source_hash,study_version:b.study_version,discard_fraction:b.discard_fraction})),
      reason:'The same named routes are summed across every included ecosystem; unsupported routes are excluded explicitly.'};
  }
  return {basis,enabled,display,combine,unavailable,finite};
});
