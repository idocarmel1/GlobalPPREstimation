/* Saved EE-floor calculation assumptions. No parameter transformation occurs in the browser. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.PPREeFloor=api;})(globalThis,function(){
  'use strict';
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const number=value=>finite(value)?String(value):'Unavailable';
  const localLink=path=>'../'+String(path).split('/').map(encodeURIComponent).join('/');
  function label(provenance){
    if(typeof provenance?.use_ee_floor!=='boolean')return null;
    return provenance.use_ee_floor?'EE floor ON ('+number(provenance.ee_floor)+')':'EE floor OFF';
  }
  function append(parent,model){
    const provenance=model?.calculation_provenance,setting=label(provenance);if(!setting)return;
    const element=(tag,text)=>{const e=document.createElement(tag);if(text!=null)e.textContent=text;return e;};
    const wrap=element('div');wrap.className='ee-floor-provenance';
    wrap.appendChild(element('p','Calculation settings · '+setting));
    let note='The floor assumes a hypothetical external nonfishery mortality sink, excluded from catch and fishery PPR.';
    if(finite(provenance.affected_group_count))note+=' '+provenance.affected_group_count+' affected groups.';
    if(finite(provenance.external_mortality_export_total))note+=' External mortality export: '+number(provenance.external_mortality_export_total)+' in saved model flow units.';
    wrap.appendChild(element('p',note));
    wrap.appendChild(element('p',model.researcher_review||model.recorded_review_pending
      ?'The signed researcher review retains its original scope and does not approve this changed calculation assumption or transformed diagnostics.'
      :'This calculation assumption and its transformed diagnostics require separate researcher review.'));
    const diagnostics=Object.entries(model.health||{}).map(([option,state])=>option+': '+(state.status||'NOT_RUN'));
    if(diagnostics.length)wrap.appendChild(element('p','Current calculation diagnostics: '+diagnostics.join(' · ')));
    if(model.review_flags?.length)wrap.appendChild(element('p','Current calculation restrictions: '+model.review_flags.join(' · ')));
    const links=element('p');
    for(const [text,path] of [['Saved calculation settings and EE-floor ledger',model.workbook],['Calculator source export',model.source]]){
      if(!path)continue;if(links.children.length)links.appendChild(document.createTextNode(' · '));
      const a=element('a',text);a.href=localLink(path);links.appendChild(a);
    }
    if(links.children.length)wrap.appendChild(links);
    parent.appendChild(wrap);
  }
  function groupTooltip(group){
    const saved=group.ee_before_floor!=null||group.ee_floor_applied!=null||group.external_mortality_export!=null;
    const parts=[(saved?'Saved effective EE: ':'Saved EE: ')+number(group.ee),'Source EE: '+number(group.source_ee)];
    if(saved)parts.push('Completed EE before floor: '+number(group.ee_before_floor),
      'Source M0: '+number(group.source_m0),'Completed M0 before floor: '+number(group.m0_before_floor),
      'Effective M0: '+number(group.m0_effective),'Hypothetical external mortality export: '+number(group.external_mortality_export));
    if(group.ee_floor_reason)parts.push(String(group.ee_floor_reason));
    return parts.join('\n');
  }
  function exportResult(db,result,state){
    const settings={};
    if(state.mode!=='npp'){
      const mappings=[result.model_ids,...(result.series||[]).map(series=>series.model_ids),result.baseline_model_ids].filter(Boolean);
      for(const ids of mappings)for(const [unitId,modelId] of Object.entries(ids)){
        const model=db.units?.[unitId]?.models?.find(model=>model.id===modelId);
        if(model?.calculation_provenance)(settings[unitId]??={})[modelId]=model.calculation_provenance;
      }
    }
    return {...result,calculation_provenance:settings};
  }
  function toCSV(csv,provenance){
    const quoted='"'+JSON.stringify(provenance).replaceAll('"','""')+'"';
    return csv.trimEnd().split('\n').map((line,index)=>line+','+(index===0?'calculation_provenance':quoted)).join('\n')+'\n';
  }
  return {label,append,groupTooltip,exportResult,toCSV};
});
