/* Runs after the inherited atlas has initialized its layers. */
const network = DB.network;
const mapParams=new URLSearchParams(location.search);
const defaultMethod=['inner','PP'].includes(mapParams.get('scope'))||['ratio','b','rho_living'].includes(mapParams.get('metric'))?'new_GE':'simple trophic chain';
const metricState = {year:DB.year,scope:['all','inner','PP'].includes(mapParams.get('scope'))?mapParams.get('scope'):'all',mode:['ppr','ratio','npp_ratio','b','rho_living'].includes(mapParams.get('metric'))?mapParams.get('metric'):'ppr',method:mapParams.get('method')||defaultMethod,denominator:mapParams.get('denominator')||'new_TE_EEfix',te:mapParams.get('te')==='TE'?'TE':'GE',
  catch_basis:['catch','discards'].includes(mapParams.get('catch_basis'))?mapParams.get('catch_basis'):'landings',uncertainty:mapParams.get('uncertainty')==='0'?'0':'1',
  npp:mapParams.get('npp')||'ens_median_tC_yr',npp_fill:mapParams.get('npp_fill')==='earliest'?'earliest':'observed',unidentified:['zero','simple'].includes(mapParams.get('unidentified'))?mapParams.get('unidentified'):'method'};
const chosenModels = Object.fromEntries(Object.entries(network.units).map(([id,u])=>[id,u.default_model]));
try{
  const saved=JSON.parse(mapParams.get('models')||'{}');
  for(const [id,model] of Object.entries(saved||{})){
    const index=network.units[id]?.models.findIndex(m=>m.id===model);
    if(index>=0)chosenModels[id]=index;
  }
}catch{/* Invalid optional model selections retain the verified defaults. */}
const $ = id => document.getElementById(id);
const escapeMetric = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const precise = v => v == null ? 'Unavailable' : v.toLocaleString(undefined,{maximumSignificantDigits:4});
const catchBasisLabel=()=>({landings:'Landings',catch:'All catch',discards:'Discards'})[metricState.catch_basis];
const isIndependentSimple=()=>['ppr','npp_ratio'].includes(metricState.mode)&&metricState.method==='simple trophic chain';
const metricName = () => ({ppr:catchBasisLabel()+' PPR (tonnes carbon)',npp_ratio:catchBasisLabel()+' PPR / NPP (%)',ratio:'Method ratio',b:'Recycling b',rho_living:'Rho living'})[metricState.mode];
const resultText = r => r.networkResult?.value == null ? 'Unavailable' : precise(r.networkResult.value)+(metricState.mode==='ppr'?' t C':metricState.mode==='ratio'?'×':metricState.mode==='npp_ratio'?'%':'');
const nppData=id=>({years:network.npp_years||[],values:network.npp?.[id]?.[metricState.npp],metadata:network.npp_metadata?.[id]});
const showSensitivity=()=>metricState.catch_basis==='landings'&&metricState.uncertainty!=='0'&&['ppr','npp_ratio'].includes(metricState.mode);
const assessedSensitivity=result=>showSensitivity()&&result?.sensitivity?.status==='assessed'&&!result.sensitivity.hidden&&PPRMetrics.finite(result.value)&&PPRMetrics.finite(result.sensitivity.lower)&&PPRMetrics.finite(result.sensitivity.upper)&&result.sensitivity.lower<=result.sensitivity.upper;
const excludedSensitivity=band=>Array.isArray(band?.excluded_routes)?band.excluded_routes.map(name=>[name,'Unavailable in part of the selected cohort']):Object.entries(band?.excluded_routes||{});
const routeLabel=name=>({SC:'Catch removal',SM:'Mortality-to-detritus proxy',SE:'External loss',SR:'Documented discard return'})[name]||name;
function sensitivityTooltip(result){
  if(!showSensitivity())return '';
  const band=result?.sensitivity,suffix=metricState.mode==='npp_ratio'?'%':' t C';
  if(!assessedSensitivity(result))return '<br>Discard-routing sensitivity: not assessed'+(band?.reason?'<br>'+escapeMetric(band.reason):'');
  const fraction=PPRMetrics.finite(band.discard_fraction)?precise(100*band.discard_fraction)+'%':'Unavailable';
  return `<br><b>Routing range:</b> ${precise(band.lower)}–${precise(band.upper)}${suffix}<br>Discards / all catch: ${fraction}<br>${escapeMetric(band.model_id||'Selected model')} · ${escapeMetric(band.study_version||'verified study')}${excludedSensitivity(band).length?'<br>Excluded: '+escapeMetric(excludedSensitivity(band).map(([name])=>name).join(', ')):''}`;
}
function appendSensitivity(panel,result){
  if(!showSensitivity())return;
  const band=result?.sensitivity,note=document.createElement('p');note.className='network-note';
  if(!assessedSensitivity(result)){note.textContent='Discard-routing sensitivity not assessed. '+(band?.reason||'No compatible response is available for this selection.');panel.appendChild(note);return;}
  const suffix=metricState.mode==='npp_ratio'?'%':' t C';
  note.textContent=`Hypothetical discard-routing envelope: ${precise(band.lower)}–${precise(band.upper)}${suffix}. Same landings for all routes${metricState.mode==='npp_ratio'?', with the same NPP denominator':''}; not a confidence interval. The annual discard fraction comes from the catch data; uniform allocation within the source model is an assumption.`;panel.appendChild(note);
  const minimum=Math.min(band.lower,result.value),maximum=Math.max(band.upper,result.value),span=maximum-minimum;
  const x=v=>span?12+196*(v-minimum)/span:110;
  const interval=document.createElement('div');
  interval.innerHTML=`<svg viewBox="0 0 220 28" style="display:block;width:100%;max-width:260px;height:34px" role="img" aria-label="Routing interval ${escapeMetric(precise(band.lower))} to ${escapeMetric(precise(band.upper))}; circle marks central estimate ${escapeMetric(precise(result.value))}"><line x1="12" x2="208" y1="14" y2="14" stroke="#d9e4e7"/><line x1="${x(band.lower)}" x2="${x(band.upper)}" y1="14" y2="14" stroke="#087a80" stroke-width="6"/><line x1="${x(band.lower)}" x2="${x(band.lower)}" y1="6" y2="22" stroke="#087a80"/><line x1="${x(band.upper)}" x2="${x(band.upper)}" y1="6" y2="22" stroke="#087a80"/><circle cx="${x(result.value)}" cy="14" r="4.5" fill="#183945" stroke="white"/></svg>`;panel.appendChild(interval);
  const fraction=PPRMetrics.finite(band.discard_fraction)?precise(100*band.discard_fraction)+'%':'Unavailable';
  const context=document.createElement('p');context.className='network-note';context.textContent=`Discards / all catch: ${fraction}. Circle: central landings estimate. ${band.interpolated?'Interpolated between valid tested fractions. ':''}${band.construction_invariant?'This reference is routing-invariant by construction; this does not establish zero ecological uncertainty. ':''}${band.reason||''}`;panel.appendChild(context);
  const audit=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Sensitivity routes and source';audit.appendChild(summary);
  const info=document.createElement('p');info.className='network-note';info.style.overflowWrap='anywhere';info.textContent=`${band.model_id||'Selected model'} · ${band.study_version||'Study version unavailable'} · source SHA-256 ${band.source_hash||'unavailable'}`;audit.appendChild(info);
  const list=document.createElement('ul');list.className='network-note';
  for(const [name,value] of Object.entries(band.route_ppr_tC||{})){const item=document.createElement('li');item.textContent=`${routeLabel(name)} (${name}): ${precise(value)} t C on the same landings.`;list.appendChild(item);}
  for(const [name,reason] of excludedSensitivity(band)){const item=document.createElement('li');item.textContent=`${routeLabel(name)} (${name}) excluded: ${reason}`;list.appendChild(item);}
  audit.appendChild(list);panel.appendChild(audit);
}
function appendResultDownload(panel,region,model,result,unit){
  const button=document.createElement('button');button.type='button';button.textContent='Download current estimate CSV';
  button.addEventListener('click',()=>{
    const band=result.sensitivity,visible=showSensitivity(),assessed=assessedSensitivity(result);
    const row={ecosystem:region.unit_id,year:DB.year,model:model?.id||null,method:metricState.method,source_files:unit?.sources,comparison_denominator:metricState.mode==='ratio'?metricState.denominator:null,diagnostic_basis:['b','rho_living'].includes(metricState.mode)?metricState.te:null,source_scope:metricState.scope,catch_basis:metricState.catch_basis,
      unidentified:metricState.unidentified,metric:metricState.mode,npp_method:metricState.npp,npp_fill:metricState.npp_fill,central_value:result.value,
      central_unit:metricState.mode==='ppr'?'t C':metricState.mode==='npp_ratio'?'percent':metricState.mode==='ratio'?'multiple':'dimensionless',status:result.status,
      selected_basis_tonnes:result.total_catch,covered_tonnes:result.catch,coverage:result.coverage,total_catch_tonnes:result.total_catch_all,discards_tonnes:result.total_discards,
      uncertainty:metricState.uncertainty,sensitivity_visible:visible,sensitivity_status:assessed?'assessed':visible?'not_assessed':'hidden',sensitivity_lower:assessed?band.lower:null,sensitivity_upper:assessed?band.upper:null,
      sensitivity_min_tC:visible&&PPRMetrics.finite(band?.min_tC)?band.min_tC:null,sensitivity_max_tC:visible&&PPRMetrics.finite(band?.max_tC)?band.max_tC:null,discard_fraction:band?.discard_fraction??(result.total_catch_all>0&&PPRMetrics.finite(result.total_discards)?result.total_discards/result.total_catch_all:null),
      sensitivity_routes:band?.route_ppr_tC,sensitivity_excluded_routes:band?.excluded_routes,sensitivity_reason:band?.reason,sensitivity_type:band?.uncertainty_type,sensitivity_source_hash:band?.source_hash,sensitivity_study_version:band?.study_version,sensitivity_route_evidence:band?.route_evidence,sensitivity_source_validity:band?.source_validity};
    const quote=value=>'"'+String(value==null?'':typeof value==='object'?JSON.stringify(value):value).replaceAll('"','""')+'"';
    const csv=Object.keys(row).map(quote).join(',')+'\n'+Object.values(row).map(quote).join(',')+'\n';
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),link=document.createElement('a');link.href=url;link.download=`ppr-${region.unit_id}-${metricState.catch_basis}-${DB.year}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });panel.appendChild(button);
}
function appendTreatment(panel,unit,result){
  const metadata=unit?.unidentified,yearIndex=unit?.years.indexOf(DB.year);
  const note=document.createElement('p');note.className='network-note';
  note.textContent=metricState.unidentified==='method'?'Unidentified catch: selected method’s own SPPR (default).':metricState.unidentified==='zero'?'Sensitivity: zero PPR for explicitly unidentified / NEI taxa, retaining all tonnage in the selected catch basis. This assumes zero PPR for these taxa.':'Sensitivity: explicitly unidentified / NEI taxa use their reference-TL simple-chain SPPR (TE=0.1). Missing reference coefficients remain uncovered. Only total / All sources is supported; no source attribution is inferred.';
  if(metadata){
    const affected=result?.unidentified_catch,total=result?.total_catch,missing=result?.unidentified_missing_simple_catch;
    note.textContent+=` ${DB.year}: ${precise(affected)} tonnes explicitly unidentified / NEI${total>0 && affected!=null?' ('+precise(100*affected/total)+'% of '+catchBasisLabel().toLowerCase()+')':''}.`;
    if(metricState.unidentified==='simple' && missing>0)note.textContent+=` ${precise(missing)} tonnes lack a reference coefficient and remain uncovered.`;
  }
  panel.appendChild(note);
  const audit=document.createElement('details'),summary=document.createElement('summary');summary.textContent=`Unidentified catch audit · ${metadata?.taxa?.length??0} classified taxa`;audit.appendChild(summary);
  const rule=document.createElement('p');rule.className='network-note';rule.textContent=metadata?`${metadata.classifier_version}: ${metadata.rule_description}`:'Classifier metadata unavailable in this export.';audit.appendChild(rule);
  const list=document.createElement('ul');list.className='network-note';
  for(const taxon of metadata?.taxa||[]){const li=document.createElement('li');li.textContent=`${taxon.name}${taxon.common_name && taxon.common_name!==taxon.name?' ('+taxon.common_name+')':''} · ${taxon.reason} · reference TL ${precise(taxon.reference_tl)} · simple SPPR ${precise(taxon.simple_sppr)}`;list.appendChild(li);}
  audit.appendChild(list);
  const inventory=document.createElement('a');inventory.textContent='Complete classifier and inventory';inventory.href='../data/unidentified_taxa.json';audit.appendChild(inventory);panel.appendChild(audit);
}
function appendNpp(panel,id){
  const data=nppData(id),npp=PPRAnnualNPP.resolve(data.years,data.values,DB.year,metricState.npp_fill,data.metadata);
  const text=document.createElement('p');text.className='network-note';
  const name=network.npp_methods?.find(m=>m.id===metricState.npp)?.label||metricState.npp;
  text.textContent=`NPP ${DB.year} · ${name}: ${precise(npp.value)}${npp.value===null?'':' t C'}. `+(npp.substituted?`Historical estimate using the constant ${npp.source_year} value; this is not an observation for ${DB.year}.`:npp.value===null?'No annual value is available.':'Annual source value.');
  panel.appendChild(text);
  if(metricState.npp.startsWith('ens_') && npp.metadata){
    const available=npp.metadata.available_models,modelNames=Array.isArray(available)?available.join(', '):available;
    const support=document.createElement('p');support.className='network-note';
    support.textContent=`Ensemble support for ${npp.source_year||DB.year}: ${npp.metadata.n_models??'unknown number of'} NPP model(s)${modelNames?' · '+modelNames:''}. ${npp.metadata.ensemble_basis||'Median of available models; model support can change between years.'}`;
    panel.appendChild(support);
  }
  if(npp.metadata){const note=document.createElement('p');note.className='network-note';note.textContent=[npp.metadata.status,npp.metadata.reason,npp.metadata.provenance].filter(Boolean).map(v=>typeof v==='object'?JSON.stringify(v):v).join(' · ');panel.appendChild(note);}
  const link=document.createElement('a');link.textContent='Annual NPP source and provenance';link.href='../'+(network.npp_source||'NPPExtraction/output/annual_npp.csv').split('/').map(encodeURIComponent).join('/');
  const links=document.createElement('p');links.className='actions';links.appendChild(link);panel.appendChild(links);
}
let colorExtent = [0,1];
function availableMethods() {
  const methods=Object.values(network.units).flatMap(u=>u.models.flatMap(m=>m.scopes[metricState.scope]?.methods||[]));
  if(metricState.scope==='all'&&['ppr','npp_ratio'].includes(metricState.mode))methods.push('simple trophic chain');
  return [...new Set(methods)];
}
function populateMethods() {
  if(isIndependentSimple()){metricState.scope='all';$('scopeFilter').value='all';}
  const methods=availableMethods();
  for(const [id,key,fallback] of [['methodFilter','method','new_GE'],['denominatorFilter','denominator','new_TE_EEfix']]){
    if(!methods.includes(metricState[key]))metricState[key]=methods.includes(fallback)?fallback:methods[0];
    $(id).replaceChildren(...methods.map(m=>{const o=document.createElement('option');o.value=m;o.textContent=m;o.selected=m===metricState[key];return o}));
  }
}
// Override color functions only after initialization, so old template setup remains safe.
pprColor = function(r) {
  const v=r.networkResult?.value;
  if(!PPRMetrics.finite(v))return '#b7c4ca';
  if(metricState.mode==='ratio'){
    const t=Math.max(-2,Math.min(2,Math.log2(Math.max(v,.000001))))/2;
    return t<0?mix('#f7fafb','#3278a1',-t):mix('#f7fafb','#b64b3a',t);
  }
  if(metricState.mode==='b'||metricState.mode==='rho_living'){
    const t=Math.max(0,Math.min(1,v));
    return t<.7?mix('#e4f0ec','#dfb34a',t/.7):mix('#dfb34a','#aa3030',(t-.7)/.3);
  }
  const lo=Math.log1p(colorExtent[0]),hi=Math.log1p(colorExtent[1]);
  return mix('#cde7e8','#075c69',hi===lo?.65:(Math.log1p(v)-lo)/(hi-lo));
};
baseRegionStyle = function(r) {
  const active=r.unit_id===selectedId,selected=!!network.units[r.unit_id],valid=PPRMetrics.finite(r.networkResult?.value);
  const color=$('colorRegionsByPpr').checked;
  return {color:active?'#bd8429':selected?'#527e8d':'#9facb3',weight:active?2.5:.9,
    fillColor:valid&&color?pprColor(r):'#c7d0d5',fillOpacity:valid&&color?.58:.07,opacity:.8};
};
addRegion = function(r) {
  const diagnostic=r.networkResult?.status||'Unavailable';
  const tooltip=`<b>${escapeMetric(r.region_name)}</b><br>${metricName()}: ${resultText(r)}<br>${escapeMetric(diagnostic)}${sensitivityTooltip(r.networkResult)}`;
  const lyr=L.geoJSON(regionFeature(r),{style:()=>baseRegionStyle(r),onEachFeature:(_,l)=>{l.on('click',()=>selectRegion(r.unit_id));l.bindTooltip(tooltip,{sticky:true})}});
  regionLayers[r.unit_id]=lyr;lyr.addTo(regionGroup);
  const marker=L.marker([r.marker_lat,r.marker_lon],{icon:L.divIcon({className:'ppr-marker',html:`<span style="background:${pprColor(r)};color:#09273b">${r.ppr_rank??'–'}</span>`,iconSize:[29,29],iconAnchor:[14,14]})});
  marker.on('click',()=>selectRegion(r.unit_id));marker.bindTooltip(tooltip);regionMarkers[r.unit_id]=marker;marker.addTo(markerGroup);
};
const originalPassArticle=passArticle;
passArticle=a=>!!network.units[a.unit_id]?.selected_articles.includes(a.article_id)&&originalPassArticle(a);
renderList = function() {
  $('regionList').replaceChildren();
  regions.filter(passRegion).forEach(r=>{
    const b=document.createElement('button');b.className='region-btn'+(selectedId===r.unit_id?' active':'');
    b.innerHTML=`<span class="rank" style="background:${pprColor(r)}">${r.ppr_rank??'–'}</span><span><b>${r.region_name}</b><br><small>${resultText(r)}</small></span>`;
    b.onclick=()=>selectRegion(r.unit_id);$('regionList').appendChild(b);
  });
};
const originalDetails=renderDetails;
renderDetails = function(r) {
  originalDetails(r);
  $('details').querySelectorAll('[data-article]').forEach(card=>{
    const chosen=network.units[r.unit_id]?.selected_articles.includes(card.dataset.article);
    const tag=card.querySelector('.chip');if(tag)tag.textContent=chosen?'Selected model source':'Archived alternative';
  });
  const old=$('details').querySelector('.metric-grid');
  const panel=document.createElement('div');panel.className='network-result';
  const independent=isIndependentSimple(),modelUnit=network.units[r.unit_id],unit=independent?network.simple_units?.[r.unit_id]:modelUnit,result=r.networkResult;
  const trendLink=()=>{
    const model=independent?null:modelUnit?.models[chosenModels[r.unit_id]];
    const p=new URLSearchParams({units:r.unit_id,method:unit?metricState.method:'simple trophic chain',scope:unit?metricState.scope:'all',year:DB.year,metric:metricState.mode==='npp_ratio'?'ratio':'ppr',npp:metricState.npp,npp_fill:metricState.npp_fill,unidentified:metricState.unidentified,catch_basis:metricState.catch_basis,uncertainty:metricState.uncertainty});
    if(model)p.set('models',JSON.stringify({[r.unit_id]:model.id}));
    const link=document.createElement('a');link.href='trends.html?'+p.toString();link.textContent=unit?'PPR through time →':'PPR through time · catch-taxon TL →';
    const links=document.createElement('p');links.className='actions';links.appendChild(link);return links;
  };
  if(!unit){panel.innerHTML=`<p>${escapeMetric(result?.status||(independent?'Catch-taxon inputs are unavailable for this ecosystem.':'No Ecopath model is selected for this ecosystem.'))}</p>`;appendNpp(panel,r.unit_id);panel.appendChild(trendLink());old.replaceWith(panel);return}
  const idx=chosenModels[r.unit_id],model=independent?null:modelUnit?.models[idx];
  panel.innerHTML=`${independent?'':'<div class="field"><label for="modelFilter">Ecopath model for this ecosystem</label><select id="modelFilter"></select></div>'}<div class="network-value">${resultText(r)}</div><div class="network-note">${metricName()} ${['ppr','ratio','npp_ratio'].includes(metricState.mode)?'· '+metricState.scope+' · '+DB.year+' · '+escapeMetric(metricState.method):'· '+metricState.te}</div><p class="network-status">${escapeMetric(result.status)}</p>`;
  const sel=panel.querySelector('select');
  if(sel){modelUnit.models.forEach((m,i)=>{const o=document.createElement('option');o.value=i;o.textContent=m.label||m.id.replaceAll('_',' ');o.selected=i===idx;sel.appendChild(o)});
    sel.addEventListener('change',()=>{chosenModels[r.unit_id]=Number(sel.value);applyYear(DB.year)});}
  const notes=document.createElement('p');notes.className='network-note';notes.textContent=independent?'Simple trophic chain uses catch-taxon trophic levels and TE=0.1. It does not require an extracted article or Ecopath model. Missing catch or trophic levels remain visible in coverage.':unit.note;panel.appendChild(notes);
  panel.appendChild(trendLink());
  if(!['b','rho_living'].includes(metricState.mode))appendTreatment(panel,unit,result);
  appendNpp(panel,r.unit_id);
  appendSensitivity(panel,result);
  if(result.coverage!=null){const coverage=document.createElement('p');coverage.className='network-note';coverage.textContent=`${pct(result.coverage)} of annual ${catchBasisLabel().toLowerCase()} included (${precise(result.catch)} tonnes). `+(metricState.mode==='ratio'?'Both methods use exactly these taxa.':'Missing method values are excluded; this is a partial footprint when coverage is below 100%.');panel.appendChild(coverage)}
  if(metricState.mode==='ratio'&&result.value!=null){const pair=document.createElement('p');pair.className='network-note';pair.textContent=`${metricState.method}: ${precise(result.numerator)} t C ÷ ${metricState.denominator}: ${precise(result.denominator)} t C`;panel.appendChild(pair)}
  if(model||unit.sources?.workbook){
    const links=document.createElement('p');links.className='actions';
    for(const [label,path] of [['Source workbook · total-catch calculation and mappings',model?.workbook],['SPPR and diagnostics',model?.source],['Ecosystem source workbook · total-catch calculation',unit.sources?.workbook]]){
      if(!path)continue;const a=document.createElement('a');a.textContent=label;a.href='../'+path.split('/').map(encodeURIComponent).join('/');links.appendChild(a);
    }
    panel.appendChild(links);
    if(result.config){const d=document.createElement('details');const summary=document.createElement('summary');summary.textContent='Diagnostic configuration';d.appendChild(summary);const pre=document.createElement('p');pre.className='network-note';pre.textContent=Object.entries(result.config).map(([k,v])=>`${k}: ${v}`).join('; ');d.appendChild(pre);panel.appendChild(d)}
  }
  appendResultDownload(panel,r,model,result,unit);
  old.replaceWith(panel);
};
function updateLegend() {
  const mode=metricState.mode, diagnostic=mode==='b'||mode==='rho_living',independent=isIndependentSimple();
  $('pprOptions').hidden=diagnostic;$('recyclingOptions').hidden=!diagnostic;$('denominatorField').hidden=mode!=='ratio';
  $('nppOptions').hidden=diagnostic;
  $('mapUnidentified').disabled=diagnostic;$('mapCatchBasis').disabled=diagnostic;
  $('scopeFilter').disabled=independent;
  $('mapUncertainty').disabled=diagnostic||mode==='ratio'||metricState.catch_basis!=='landings';
  $('mapSensitivityHelp').textContent=metricState.catch_basis!=='landings'?'Envelope hidden in this view. Select landings to assess discard routing.':mode==='ratio'?'No envelope is assessed for a ratio of methods.':'Where assessed, the range applies routing alternatives to the same landings. It is not a confidence interval.';
  $('yearFilter').disabled=diagnostic;$('methodLabel').textContent=mode==='ratio'?'Numerator method':'Estimation method';
  $('metricLegendTitle').textContent=metricName();
  $('metricHelp').textContent=diagnostic?'Read directly from diagnose_sppr(). Values below 1 are necessary for convergence, but do not guarantee validity; inspect the reported status. TE has no recycling matrix, so its b is zero by construction, not evidence of absent ecological recycling. Diagnostics are fixed for the chosen model.':mode==='ratio'?'Numerator ÷ denominator, using only catch taxa available to both methods in the same year, model and source scope. Both PPR masses are shown in carbon (wet weight ÷ 9).':'PPR in tonnes carbon = selected annual catch basis × mapped SPPR ÷ 9. Model coefficients are fixed across years. Failed methods remain unavailable.';
  if(independent)$('metricHelp').textContent='Simple trophic chain PPR (tonnes carbon) = selected catch × (1 / 0.1)^(catch-taxon TL − 1) ÷ 9. No extracted article or Ecopath model is required. Trophic levels stay fixed across years; unavailable catch or trophic levels remain missing or uncovered. This method has only an All-sources total.';
  if(mode==='npp_ratio')$('metricHelp').textContent='PPR / NPP = 100 × annual PPR carbon / annual NPP carbon (%). PPR is converted from wet weight once at 1/9. Missing annual NPP leaves the ecosystem unavailable.';
  if(independent&&mode==='npp_ratio')$('metricHelp').textContent+=' The numerator uses catch-taxon TL at TE=0.1 and requires no extracted article or Ecopath model.';
  if(!diagnostic)$('metricHelp').textContent+=metricState.npp_fill==='earliest'?' Historical NPP estimates use each ecosystem’s earliest available value only for earlier missing years; internal and later gaps remain blank.':' Historical NPP is not inferred; unavailable years remain blank.';
  if(!diagnostic && metricState.unidentified!=='method')$('metricHelp').textContent+=metricState.unidentified==='zero'?' Unidentified-catch sensitivity: zero PPR for explicitly classified taxa; selected catch tonnage retained.':' Unidentified-catch sensitivity: reference-TL simple-chain coefficients, All sources only. Missing reference coefficients remain uncovered.';
  $('metricGradient').style.background=diagnostic?'linear-gradient(90deg,#e4f0ec,#dfb34a 70%,#aa3030)':mode==='ratio'?'linear-gradient(90deg,#3278a1,#f7fafb,#b64b3a)':'linear-gradient(90deg,#cde7e8,#075c69)';
  $('metricLow').textContent=diagnostic?'0':mode==='ratio'?'≤0.25×':precise(colorExtent[0]);
  $('metricMiddle').textContent=diagnostic?'0.5':mode==='ratio'?'1×':'log scale';
  $('metricHigh').textContent=diagnostic?'≥1 · convergence fails':mode==='ratio'?'≥4×':precise(colorExtent[1]);
}
function applyYear(year) {
  DB.year=Number(year);metricState.year=DB.year;
  const annual=DB.annual[String(year)];
  regions.forEach(r=>{
    r.networkResult=PPRMetrics.evaluate(network.units[r.unit_id],chosenModels[r.unit_id],{...metricState,npp_data:nppData(r.unit_id),simple_unit:network.simple_units?.[r.unit_id]});
    r.ppr_species_2019=r.networkResult.value;
    r.total_catch_tonnes=r.networkResult.total_catch??(metricState.catch_basis==='catch'?annual?.[r.unit_id]?.[1]??null:null);
    r['data availability']=r.networkResult.value==null?'unavailable':isIndependentSimple()?'catch_trophic_levels':'pilot';
  });
  regions.sort((a,b)=>(a.ppr_species_2019===null)-(b.ppr_species_2019===null)||(b.ppr_species_2019||0)-(a.ppr_species_2019||0)||a.unit_id.localeCompare(b.unit_id));
  const values=regions.map(r=>r.networkResult.value).filter(PPRMetrics.finite);
  colorExtent=values.length?[Math.min(...values),Math.max(...values)]:[0,1];
  const total=values.reduce((a,b)=>a+b,0);let rank=0,prior=null,cumulative=0;
  regions.forEach((r,i)=>{const v=r.networkResult.value;if(v==null){r.ppr_rank=null;r.global_ppr_share=null;r.cumulative_ppr_share=null;return}if(v!==prior)rank=i+1;prior=v;cumulative+=v;r.ppr_rank=rank;r.global_ppr_share=metricState.mode==='ppr'&&total?v/total:null;r.cumulative_ppr_share=metricState.mode==='ppr'&&total?cumulative/total:null});
  regionGroup.clearLayers();markerGroup.clearLayers();regions.forEach(addRegion);
  $('yearTotal').textContent=`${values.length} of ${regions.length} atlas ecosystems have this result. ${isIndependentSimple()?'Simple chain uses available catch and catch-taxon TL independently of articles.':'Ecopath methods require a verified selected model; models remain separate.'} Rankings describe the current view.`;
  updateLegend();if(selectedId)renderDetails(regionById[selectedId]);refresh();
  const params=new URLSearchParams(location.search);params.set('metric',metricState.mode);params.set('year',DB.year);params.set('npp',metricState.npp);params.set('npp_fill',metricState.npp_fill);
  for(const key of ['scope','method','denominator','te','unidentified','catch_basis','uncertainty'])params.set(key,metricState[key]);
  const overrides=Object.fromEntries(Object.entries(chosenModels).filter(([id,index])=>index!==network.units[id].default_model).map(([id,index])=>[id,network.units[id].models[index].id]));
  if(Object.keys(overrides).length)params.set('models',JSON.stringify(overrides));else params.delete('models');
  try{history.replaceState(null,'','?'+params.toString()+location.hash);}catch{/* Local-file history may be restricted. */}
}
populateMethods();
const nppMethods=network.npp_methods||[];
if(!nppMethods.some(m=>m.id===metricState.npp))metricState.npp=nppMethods[0]?.id||'ens_median_tC_yr';
$('mapNppMethod').replaceChildren(...nppMethods.map(m=>{const o=document.createElement('option');o.value=m.id;o.textContent=m.label||m.id;return o;}));
$('mapNppMethod').value=metricState.npp;$('mapNppFill').value=metricState.npp_fill;$('metricMode').value=metricState.mode;$('scopeFilter').value=metricState.scope;$('teFilter').value=metricState.te;$('mapUnidentified').value=metricState.unidentified;$('mapCatchBasis').value=metricState.catch_basis;$('mapUncertainty').value=metricState.uncertainty;
if(Object.hasOwn(DB.annual,mapParams.get('year')))DB.year=Number(mapParams.get('year'));
for(const [id,key] of [['metricMode','mode'],['scopeFilter','scope'],['methodFilter','method'],['denominatorFilter','denominator'],['teFilter','te'],['mapNppMethod','npp'],['mapNppFill','npp_fill'],['mapUnidentified','unidentified'],['mapCatchBasis','catch_basis'],['mapUncertainty','uncertainty']]){
    $(id).addEventListener('change',()=>{metricState[key]=$(id).value;if(['scope','method','mode'].includes(key))populateMethods();applyYear(DB.year)});
}
Object.keys(DB.annual).sort().reverse().forEach(year=>{const o=document.createElement('option');o.value=year;o.textContent=year;o.selected=Number(year)===DB.year;$('yearFilter').appendChild(o)});
$('yearFilter').addEventListener('change',()=>applyYear($('yearFilter').value));
$('colorRegionsByPpr').checked=true;$('showArticles').checked=false;
// Pilot membership stays in network.units, separate from independent catch data.
const priorPassRegion=passRegion;
passRegion=function(r){
  const select=$('rankFilter'),options=Array.from(select.options),pilot=options.find(option=>/\bpilot\b/i.test(option.textContent));
  if(!pilot||select.value!==pilot.value)return priorPassRegion(r);
  if(!network.units[r.unit_id])return false;
  const all=options.find(option=>/^all\b/i.test(option.textContent));
  if(!all)return priorPassRegion(r);
  const previous=select.value;try{select.value=all.value;return priorPassRegion(r);}finally{select.value=previous;}
};
applyYear(DB.year);
