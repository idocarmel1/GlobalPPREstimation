/* Attribute retained annual PPR to model groups without changing their inputs. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.PPRGroupContributions=api;
})(typeof globalThis==='object'?globalThis:this,function(){
  'use strict';
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const palette=['#087a80','#c26724','#7155a3','#3976b5','#b64065'];
  const compatible=state=>state.mode!=='npp'&&!state.baseline&&(state.methods||[]).length===1;
  const groupAPI=()=>globalThis.PPRGroups;

  function contributions(unit,model,state,year){
    const api=groupAPI(),data=model?.group_data;
    if(!api||!model?.verified||!data?.groups?.length||!data.mappings)return [];
    const method=state.methods[0],source=api.inputs(unit),scope=(model.taxon_scopes||model.scopes)?.[state.scope];
    const column=scope?.methods?.indexOf(method),groupColumn=data.methods?.indexOf(method);
    const policy=globalThis.PPRAvailableResults,status=scope?.status?.[method];
    if(!(column>=0)||!policy.allowed(model,status,method)||api.mcAcceptanceFailure(model,method))return [];
    const signed=policy.signed(model,status,method),validCoefficient=v=>finite(v)&&(v>=0||signed);
    const selected=api.selection(model,state.group_selections?.[api.key(state.unit_id,model)]),retained=new Set(selected.indices);
    const catchRetained=new Set(selected.catch_indices),yi=source.years?.indexOf(Number(year));
    const basis=state.catch_basis||'landings',treatment=state.unidentified||'method';
    const matrix=(basis==='catch'?(source.full_precision_catch||source.catch):source[basis])||(!source.catch_basis_policy?source.catch:null);
    if(!(yi>=0)||!Array.isArray(matrix)||matrix.some(row=>!finite(row?.[yi])||row[yi]<0))return [];
    const affected=new Map((source.unidentified?.taxa||[]).map(t=>[t.name,t]));
    const totals=data.groups.map(()=>0);
    matrix.forEach((row,i)=>{
      const baseline=scope.values?.[i]?.[column],mapping=data.mappings[i]||[];
      if(!validCoefficient(baseline)||!row[yi]||!mapping.length)return;
      if(mapping.some(([g,w])=>!Number.isInteger(g)||!data.groups[g]||!finite(w)||w<0))return;
      if(!mapping.some(([g,w])=>catchRetained.has(g)&&w>0))return;
      const kept=mapping.filter(([g,w])=>retained.has(g)&&w>0);
      if(!kept.length)return;
      const residual=affected.get(source.taxa?.[i]);
      const fallback=residual&&treatment!=='method'?treatment==='zero'?0:residual.simple_sppr:
        method==='simple trophic chain'?source.simple_sppr?.[i]:undefined;
      const usesFallback=(residual&&treatment!=='method')||method==='simple trophic chain';
      const parts=kept.map(([g,w])=>[g,w*(usesFallback?fallback:data.scopes?.[state.scope]?.[g]?.[groupColumn])]);
      if(parts.some(([,v])=>!validCoefficient(v)))return;
      const raw=parts.reduce((sum,[,v])=>sum+v,0);
      // The displayed taxon coefficient is rounded to six decimals. Reconcile
      // only that bounded rounding residual; incompatible attribution stays in Other.
      const target=usesFallback?raw:selected.active?Math.round(raw*1e6)/1e6:baseline;
      if(Math.abs(target-raw)>5.01e-7||target*raw<0)return;
      if(parts.every(([,v])=>v>=0)||parts.every(([,v])=>v<=0)){
        if(raw===0&&target!==0)return;
        if(raw!==0)for(const part of parts)part[1]*=target/raw;
      }else{
        const largest=parts.reduce((best,part,index)=>Math.abs(part[1])>Math.abs(parts[best][1])?index:best,0);
        const corrected=parts[largest][1]+target-raw;
        // Retain genuinely signed parts if rounding would reverse a part's sign;
        // the total's residual then remains explicitly in Other.
        if(corrected*parts[largest][1]>=0)parts[largest][1]=corrected;
      }
      for(const [g,value] of parts)totals[g]+=row[yi]*value/9;
    });
    return selected.indices.map(index=>({group:data.groups[index],ppr:totals[index]}));
  }

  function build(db,state,result){
    if(!compatible(state)||result.normalized||result.series?.length!==1)return {available:false,layers:[],reason:'Choose one PPR method without a baseline to see group contributions.'};
    const series=result.series[0],points=series.points,groups=new Map();
    const unattributed=points.map(()=>0),summationTerms=points.map(()=>0);
    points.forEach((point,index)=>{
      if(!finite(point.value))return;
      for(const id of point.included_ids||series.included||[]){
        const unit=db.units[id],chosen=point.model_ids?.[id]??series.model_ids?.[id]??state.models?.[id]??unit?.default_model;
        const model=unit?.models?.find(m=>m.id===chosen);
        summationTerms[index]+=1+(groupAPI()?.inputs(unit)?.taxa?.length||0)+
          (model?.group_data?.mappings||[]).reduce((sum,mapping)=>sum+mapping.length,0);
        for(const {group,ppr} of contributions(unit,model,{...state,unit_id:id},point.year)){
          const key=JSON.stringify([id,model.id,group.id]);
          if(!groups.has(key))groups.set(key,{id:key,unit_id:id,model_id:model.id,group_id:group.id,
            label:(group.name||group.id)+(state.units.length>1?' · '+(unit.name||id):''),ppr:points.map(()=>0)});
          groups.get(key).ppr[index]+=ppr;
        }
      }
      const attributed=[...groups.values()].reduce((sum,g)=>sum+g.ppr[index],0);
      unattributed[index]=finite(point.ppr)?point.ppr-attributed:0;
    });
    // Rank the included groups once over the displayed period, in carbon PPR,
    // keeping a group's identity and label fixed throughout the annual series.
    const top=[...groups.values()].filter(g=>g.ppr.some(v=>v!==0))
      .map(g=>({...g,total:g.ppr.reduce((a,b)=>a+b,0)}))
      .sort((a,b)=>b.total-a.total||a.id.localeCompare(b.id)).slice(0,5);
    const display=(ppr,point)=>{
      if(!finite(point.value))return null;
      let value=state.mode==='ratio'?100*ppr/point.npp:ppr;
      if(result.global_estimate)value/=point.simple_ppr_share;
      return finite(value)?value:null;
    };
    const layers=top.map((g,index)=>({...g,color:palette[index],other:false,
      points:points.map((point,i)=>({year:point.year,value:display(g.ppr[i],point)}))}));
    const topIds=new Set(top.map(g=>g.id)),remaining=[...groups.values()].filter(g=>!topIds.has(g.id));
    layers.push({id:'other',label:'Other',color:'#96a6ad',other:true,
      points:points.map((point,i)=>{
        if(!finite(point.value))return {year:point.year,value:null};
        const total=layers.reduce((sum,g)=>sum+g.points[i].value,0),residual=point.value-total;
        // Bound accumulated roundoff from taxon sums, allocation sums, carbon
        // conversion and the common denominator. Actual remaining groups stay in
        // Other even when their contributions are smaller than this bound.
        const tolerance=8*(summationTerms[i]+layers.length+1)*Number.EPSILON*
          Math.max(1,Math.abs(point.value),layers.reduce((sum,g)=>sum+Math.abs(g.points[i].value),0));
        let value=residual;
        if(layers.length&&remaining.every(g=>g.ppr[i]===0)&&Math.abs(residual)<=tolerance){
          const largest=layers.reduce((best,g,index)=>Math.abs(g.points[i].value)>Math.abs(layers[best].points[i].value)?index:best,0);
          const original=layers[largest].points[i].value,corrected=original+residual;
          if(original*corrected>=0){layers[largest].points[i].value=corrected;value=0;}
        }
        return {year:point.year,value};
      })});
    return {available:true,layers,ranking:'Cumulative included PPR over the displayed year range',
      unattributed_ppr:points.map((p,i)=>({year:p.year,value:finite(p.value)?unattributed[i]:null})),
      has_unattributed:unattributed.some((v,i)=>finite(points[i].value)&&Math.abs(v)>1e-8*Math.max(1,Math.abs(points[i].ppr||0)))};
  }

  function bounds(breakdown){
    if(!breakdown?.available)return [];
    return breakdown.layers[0].points.flatMap((_,i)=>{
      const values=breakdown.layers.map(layer=>layer.points[i].value);
      if(!values.every(finite))return [];
      return [values.reduce((sum,v)=>sum+Math.min(0,v),0),values.reduce((sum,v)=>sum+Math.max(0,v),0)];
    });
  }
  function draw(breakdown,{chart,svg,x,y}){
    if(!breakdown?.available)return;
    const positive=breakdown.layers[0].points.map(()=>0),negative=positive.map(()=>0);
    for(const layer of breakdown.layers){
      const segments=[];let segment=[];
      layer.points.forEach((point,i)=>{
        if(!finite(point.value)){if(segment.length)segments.push(segment);segment=[];return;}
        const base=point.value>=0?positive:negative,lower=base[i],upper=lower+point.value;
        base[i]=upper;
        // Opposite signs belong on opposite sides of zero; never join across it.
        if(segment.length&&segment.at(-1).negative!==(point.value<0)){segments.push(segment);segment=[];}
        segment.push({i,lower,upper,negative:point.value<0});
      });
      if(segment.length)segments.push(segment);
      const group=svg('g',{'data-group-layer':layer.id,'aria-label':layer.label});
      group.appendChild(svg('title',{},layer.label));
      for(const points of segments){
        if(points.length===1){const p=points[0];group.appendChild(svg('line',{x1:x(p.i),x2:x(p.i),y1:y(p.lower),y2:y(p.upper),stroke:layer.color,'stroke-width':5}));continue;}
        const path=points.map((p,i)=>`${i?'L':'M'}${x(p.i)},${y(p.upper)}`).join(' ')+' '+[...points].reverse().map(p=>`L${x(p.i)},${y(p.lower)}`).join(' ')+' Z';
        group.appendChild(svg('path',{d:path,fill:layer.color,'fill-opacity':'.82',stroke:'white','stroke-width':'.5'}));
      }
      chart.appendChild(group);
    }
  }
  function toCSV(result,state,original){
    const csv=original(result,state),breakdown=result.group_breakdown;
    if(!breakdown?.available)return csv;
    const escape=value=>value==null?'':`"${String(value).replaceAll('"','""')}"`;
    // Source/provenance fields can contain quoted newlines. Split CSV records,
    // not physical lines, before appending the annual contribution columns.
    const rows=[];let quoted=false,start=0;
    for(let i=0;i<csv.length;i++){
      if(csv[i]==='"'){
        if(quoted&&csv[i+1]==='"')i++;else quoted=!quoted;
      }else if(csv[i]==='\n'&&!quoted){rows.push(csv.slice(start,i));start=i+1;}
    }
    if(start<csv.length)rows.push(csv.slice(start));
    rows[0]+=','+breakdown.layers.map(l=>escape(l.label+' contribution')).join(',');
    for(let i=1;i<rows.length;i++)rows[i]+=','+breakdown.layers.map(l=>escape(l.points[i-1]?.value)).join(',');
    return rows.join('\n')+'\n';
  }
  return {compatible,build,bounds,draw,toCSV};
});
