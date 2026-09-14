/* Retain the original catch allocations when selecting model groups. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.PPRGroups=api;
})(typeof globalThis==='object'?globalThis:this,function(){
  'use strict';
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const valid=v=>finite(v)&&v>=0;
  const key=(unitId,model)=>unitId+'::'+model.id;
  function selection(model,ids){
    const list=model?.group_data?.groups||[];
    const names=new Set(Array.isArray(ids)?ids:list.map(g=>g.id));
    const indices=list.flatMap((g,i)=>names.has(g.id)?[i]:[]);
    return {ids:indices.map(i=>list[i].id),indices,count:indices.length,total:list.length,
      active:Array.isArray(ids)&&list.length>0&&indices.length<list.length,empty:indices.length===0};
  }
  const active=(model,ids)=>selection(model,ids).active;
  const inputs=unit=>unit.group_inputs?{...unit,...unit.group_inputs}:unit;
  function mcAcceptanceFailure(model,method){
    const d=method?.startsWith('MC_')?model.mc_diagnostics?.[method]:null;
    if(!d||!finite(d.n_samples)||!finite(d.n_accepted)||d.n_samples<=0||d.n_accepted<0||d.n_accepted>d.n_samples||d.n_accepted/d.n_samples>=.8)return null;
    return `MC acceptance: ${d.n_accepted} of ${d.n_samples} runs accepted (${Number((100*d.n_accepted/d.n_samples).toFixed(2))}%), below the 80% minimum.`;
  }
  const unavailable=status=>({value:null,coverage:null,catch:null,status});
  function evaluate(unit,model,state,ids){
    const source=inputs(unit),selected=selection(model,ids),data=model.group_data;
    if(!model.verified)return unavailable('Mapping workbook not verified');
    const scope=(model.taxon_scopes||model.scopes)?.[state.scope];
    const ratio=state.mode==='ratio',methods=ratio?[state.method,state.denominator]:[state.method];
    if(!scope||!Array.isArray(scope.methods))return unavailable('Group taxon inputs unavailable for this scope');
    for(const method of methods){
      const failure=mcAcceptanceFailure(model,method);
      if(failure)return unavailable(failure);
      if(!scope.methods.includes(method)||scope.status?.[method]!=='ok')return unavailable(method+': '+(scope.status?.[method]||'unavailable'));
    }
    const yi=(source.years||[]).indexOf(Number(state.year));
    if(yi<0)return unavailable('Catch or year unavailable');
    const basis=state.catch_basis||'landings',treatment=state.unidentified||'method';
    if(!['catch','landings','discards'].includes(basis))return unavailable('Unknown catch basis');
    if(!['method','zero','simple'].includes(treatment))return unavailable('Unknown unidentified-catch treatment');
    if(treatment==='simple'&&state.scope!=='all')return unavailable('Reference-TL sensitivity is total-only; select All sources. No source decomposition is available.');
    if(treatment!=='method'&&!source.unidentified)return unavailable('Unidentified-catch sensitivity unavailable in this export');
    const matrix=(basis==='catch'?(source.full_precision_catch||source.catch):source[basis])||(!source.catch_basis_policy?source.catch:null);
    if(!matrix)return unavailable('Catch classification unavailable for this basis');
    if(matrix.some(row=>!valid(row?.[yi])))return unavailable('Catch amounts are missing or invalid for this basis and year');
    if(!data?.mappings)return unavailable('Group catch allocations unavailable');
    const retained=new Set(selected.indices),affected=new Map((source.unidentified?.taxa||[]).map(t=>[t.name,t]));
    let numerator=0,denominator=0,total=0,support=0,unidentified=0,missingSimple=0;
    const fractions=matrix.map((_,i)=>(data.mappings[i]||[]).reduce((sum,[g,w])=>sum+(retained.has(g)&&valid(w)?w:0),0));
    const coefficient=(i,method,residual)=>{
      const j=scope.methods.indexOf(method),baseline=scope.values?.[i]?.[j],fraction=fractions[i];
      // Selection cannot restore an unsupported original taxon coefficient.
      if(!valid(baseline))return null;
      if(residual&&treatment!=='method')return treatment==='zero'?0:valid(residual.simple_sppr)?residual.simple_sppr*fraction:null;
      if(method==='simple trophic chain')return valid(source.simple_sppr?.[i])?source.simple_sppr[i]*fraction:null;
      const column=data.methods.indexOf(method),values=data.scopes?.[state.scope];
      if(column<0||!values)return null;
      let sum=0;
      for(const [g,w] of data.mappings[i]||[]){
        if(!retained.has(g)||w===0)continue;
        const v=values[g]?.[column];if(!valid(w)||!valid(v))return null;
        sum+=w*v;
      }
      return Math.round(sum*1e6)/1e6;
    };
    matrix.forEach((years,i)=>{
      const c=years[yi],fraction=fractions[i],residual=affected.get(source.taxa?.[i]);
      total+=c*fraction;
      if(residual){unidentified+=c*fraction;if(!valid(residual.simple_sppr))missingSimple+=c*fraction;}
      if(fraction===0)return;
      const a=coefficient(i,state.method,residual),b=ratio?coefficient(i,state.denominator,residual):0;
      if(!valid(a)||!valid(b))return;
      numerator+=c*a;denominator+=c*b;support+=c*fraction;
    });
    if(total>0&&support===0)return unavailable('No catch with available method values');
    if(ratio&&denominator===0)return unavailable('Zero denominator on common catch');
    const selectedTotal=matrix=>Array.isArray(matrix)&&matrix.every(row=>valid(row?.[yi]))?matrix.reduce((sum,row,i)=>sum+row[yi]*fractions[i],0):null;
    return {value:ratio?numerator/denominator:numerator/9,numerator:numerator/9,ppr_wet:numerator,denominator:ratio?denominator/9:null,
      catch:support,total_catch:total,coverage:total>0?support/total:null,catch_basis:basis,
      total_catch_all:selectedTotal(source.full_precision_catch||source.catch),total_discards:selectedTotal(source.discards),
      unidentified_catch:source.unidentified?unidentified:null,unidentified_share:source.unidentified&&total>0?unidentified/total:null,
      unidentified_missing_simple_catch:source.unidentified?missingSimple:null,
      sensitivity:{status:'not_assessed',min_tC:null,max_tC:null,lower:null,upper:null,reason:'Discard-routing sensitivity for this group subset is not assessed.'},
      status:selected.empty?'No groups selected':'ok',group_selection:selected};
  }
  function rows(unit,model,options){
    const data=model?.group_data;if(!data)return [];
    const column=data.methods.indexOf(options.method);
    return data.groups.map((g,i)=>{
      const result=evaluate(unit,model,{...options,mode:'ppr'},[g.id]);
      return {...g,sppr_all:data.scopes?.all?.[i]?.[column]??null,sppr_inner:data.scopes?.inner?.[i]?.[column]??null,ppr:result.value};
    });
  }
  return {key,selection,active,rows,evaluate,inputs,mcAcceptanceFailure};
});
