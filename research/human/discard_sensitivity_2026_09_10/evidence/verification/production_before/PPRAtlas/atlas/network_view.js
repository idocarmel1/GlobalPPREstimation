/* Runs after the inherited atlas has initialized its layers. */
const network = DB.network;
const mapParams=new URLSearchParams(location.search);
const metricState = {year:DB.year,scope:['all','inner','PP'].includes(mapParams.get('scope'))?mapParams.get('scope'):'all',mode:['ppr','ratio','npp_ratio','b','rho_living'].includes(mapParams.get('metric'))?mapParams.get('metric'):'ppr',method:mapParams.get('method')||'new_GE',denominator:mapParams.get('denominator')||'new_TE_EEfix',te:mapParams.get('te')==='TE'?'TE':'GE',
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
const metricName = () => ({ppr:'PPR (tonnes carbon)',npp_ratio:'PPR / NPP (%)',ratio:'Method ratio',b:'Recycling b',rho_living:'Rho living'})[metricState.mode];
const resultText = r => r.networkResult?.value == null ? 'Unavailable' : precise(r.networkResult.value)+(metricState.mode==='ppr'?' t C':metricState.mode==='ratio'?'×':metricState.mode==='npp_ratio'?'%':'');
const nppData=id=>({years:network.npp_years||[],values:network.npp?.[id]?.[metricState.npp],metadata:network.npp_metadata?.[id]});
function appendTreatment(panel,unit){
  const metadata=unit?.unidentified,yearIndex=unit?.years.indexOf(DB.year);
  const note=document.createElement('p');note.className='network-note';
  note.textContent=metricState.unidentified==='method'?'Unidentified catch: selected method’s own SPPR (default).':metricState.unidentified==='zero'?'Sensitivity: zero PPR for explicitly unidentified / NEI taxa, with all catch tonnage retained. This is a zero-cost scenario.':'Sensitivity: explicitly unidentified / NEI taxa use their reference-TL simple-chain SPPR (TE=0.1). Missing reference coefficients remain uncovered. Only total / All sources is supported; no source attribution is inferred.';
  if(metadata){
    const affected=metadata.catch?.[yearIndex],total=unit.catch.reduce((sum,values)=>sum+(values[yearIndex]||0),0),missing=metadata.missing_simple_catch?.[yearIndex];
    note.textContent+=` ${DB.year}: ${precise(affected)} tonnes explicitly unidentified / NEI${total>0 && affected!=null?' ('+precise(100*affected/total)+'% of total catch)':''}.`;
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
  return [...new Set(Object.values(network.units).flatMap(u=>u.models.flatMap(m=>m.scopes[metricState.scope]?.methods||[])))];
}
function populateMethods() {
  const methods=availableMethods();
  for(const [id,key,fallback] of [['methodFilter','method','new_GE'],['denominatorFilter','denominator','new_TE_EEfix']]){
    if(!methods.includes(metricState[key]))metricState[key]=methods.includes(fallback)?fallback:methods[0];
    $(id).replaceChildren(...methods.map(m=>{const o=document.createElement('option');o.value=m;o.textContent=m;o.selected=m===metricState[key];return o}));
  }
}
// Override color functions only after initialization, so old template setup remains safe.
pprColor = function(r) {
  const v=r.networkResult?.value;
  if(!network.units[r.unit_id]||!PPRMetrics.finite(v))return '#b7c4ca';
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
  const active=r.unit_id===selectedId,selected=!!network.units[r.unit_id],valid=selected&&PPRMetrics.finite(r.networkResult?.value);
  const color=$('colorRegionsByPpr').checked;
  return {color:active?'#bd8429':selected?'#527e8d':'#9facb3',weight:active?2.5:.9,
    fillColor:valid&&color?pprColor(r):'#c7d0d5',fillOpacity:valid&&color?.58:.07,opacity:.8};
};
addRegion = function(r) {
  const diagnostic=r.networkResult?.status||'Unavailable';
  const tooltip=`<b>${r.region_name}</b><br>${metricName()}: ${resultText(r)}<br>${escapeMetric(diagnostic)}`;
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
    b.innerHTML=`<span class="rank" style="background:${pprColor(r)}">${r.ppr_rank??'–'}</span><span><b>${r.region_name}</b><br><small>${network.units[r.unit_id]?resultText(r):'No selected pilot article'}</small></span>`;
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
  const unit=network.units[r.unit_id],result=r.networkResult;
  const trendLink=()=>{
    const model=unit?.models[chosenModels[r.unit_id]];
    const p=new URLSearchParams({units:r.unit_id,method:unit?metricState.method:'simple trophic chain',scope:unit?metricState.scope:'all',year:DB.year,metric:metricState.mode==='npp_ratio'?'ratio':'ppr',npp:metricState.npp,npp_fill:metricState.npp_fill,unidentified:metricState.unidentified});
    if(model)p.set('models',JSON.stringify({[r.unit_id]:model.id}));
    const link=document.createElement('a');link.href='trends.html?'+p.toString();link.textContent=unit?'PPR through time →':'PPR through time · catch-taxon TL →';
    const links=document.createElement('p');links.className='actions';links.appendChild(link);return links;
  };
  if(!unit){panel.innerHTML='<p>No article is selected for estimation in this pilot. This ecosystem remains uncolored.</p>';appendNpp(panel,r.unit_id);panel.appendChild(trendLink());old.replaceWith(panel);return}
  const idx=chosenModels[r.unit_id],model=unit.models[idx];
  panel.innerHTML=`<div class="field"><label for="modelFilter">Ecopath model for this ecosystem</label><select id="modelFilter"></select></div><div class="network-value">${resultText(r)}</div><div class="network-note">${metricName()} ${['ppr','ratio','npp_ratio'].includes(metricState.mode)?'· '+metricState.scope+' · '+DB.year+' · '+escapeMetric(metricState.method):'· '+metricState.te}</div><p class="network-status">${escapeMetric(result.status)}</p>`;
  const sel=panel.querySelector('select');
  unit.models.forEach((m,i)=>{const o=document.createElement('option');o.value=i;o.textContent=m.label||m.id.replaceAll('_',' ');o.selected=i===idx;sel.appendChild(o)});
  sel.addEventListener('change',()=>{chosenModels[r.unit_id]=Number(sel.value);applyYear(DB.year)});
  const notes=document.createElement('p');notes.className='network-note';notes.textContent=unit.note;panel.appendChild(notes);
  panel.appendChild(trendLink());
  if(!['b','rho_living'].includes(metricState.mode))appendTreatment(panel,unit);
  appendNpp(panel,r.unit_id);
  if(result.coverage!=null){const coverage=document.createElement('p');coverage.className='network-note';coverage.textContent=`${pct(result.coverage)} of annual catch included (${precise(result.catch)} tonnes). `+(metricState.mode==='ratio'?'Both methods use exactly these taxa.':'Missing method values are excluded; this is a partial footprint when coverage is below 100%.');panel.appendChild(coverage)}
  if(metricState.mode==='ratio'&&result.value!=null){const pair=document.createElement('p');pair.className='network-note';pair.textContent=`${metricState.method}: ${precise(result.numerator)} t C ÷ ${metricState.denominator}: ${precise(result.denominator)} t C`;panel.appendChild(pair)}
  if(model){
    const links=document.createElement('p');links.className='actions';
    for(const [label,path] of [['PPR and final taxon mappings',model.workbook],['SPPR and diagnostics',model.source],['Ecosystem workbook',unit.sources?.workbook]]){
      if(!path)continue;const a=document.createElement('a');a.textContent=label;a.href='../'+path.split('/').map(encodeURIComponent).join('/');links.appendChild(a);
    }
    panel.appendChild(links);
    if(result.config){const d=document.createElement('details');const summary=document.createElement('summary');summary.textContent='Diagnostic configuration';d.appendChild(summary);const pre=document.createElement('p');pre.className='network-note';pre.textContent=Object.entries(result.config).map(([k,v])=>`${k}: ${v}`).join('; ');d.appendChild(pre);panel.appendChild(d)}
  }
  old.replaceWith(panel);
};
function updateLegend() {
  const mode=metricState.mode, diagnostic=mode==='b'||mode==='rho_living';
  $('pprOptions').hidden=diagnostic;$('recyclingOptions').hidden=!diagnostic;$('denominatorField').hidden=mode!=='ratio';
  $('nppOptions').hidden=diagnostic;
  $('mapUnidentified').disabled=diagnostic;
  $('yearFilter').disabled=diagnostic;$('methodLabel').textContent=mode==='ratio'?'Numerator method':'Estimation method';
  $('metricLegendTitle').textContent=metricName();
  $('metricHelp').textContent=diagnostic?'Read directly from diagnose_sppr(). Values below 1 are necessary for convergence, but do not guarantee validity; inspect the reported status. TE has no recycling matrix, so its b is zero by construction, not evidence of absent ecological recycling. Diagnostics are fixed for the chosen model.':mode==='ratio'?'Numerator ÷ denominator, using only catch taxa available to both methods in the same year, model and source scope. Both PPR masses are shown in carbon (wet weight ÷ 9).':'PPR in tonnes carbon = annual catch × mapped SPPR ÷ 9. Model coefficients are fixed across years. Failed methods remain unavailable.';
  if(mode==='npp_ratio')$('metricHelp').textContent='PPR / NPP = 100 × annual PPR carbon / annual NPP carbon (%). PPR is converted from wet weight once at 1/9. Missing annual NPP leaves the ecosystem unavailable.';
  if(!diagnostic)$('metricHelp').textContent+=metricState.npp_fill==='earliest'?' Historical NPP estimates use each ecosystem’s earliest available value only for earlier missing years; internal and later gaps remain blank.':' Historical NPP is not inferred; unavailable years remain blank.';
  if(!diagnostic && metricState.unidentified!=='method')$('metricHelp').textContent+=metricState.unidentified==='zero'?' Unidentified-catch sensitivity: zero PPR for explicitly classified taxa; all catch tonnage retained.':' Unidentified-catch sensitivity: reference-TL simple-chain coefficients, All sources only. Missing reference coefficients remain uncovered.';
  $('metricGradient').style.background=diagnostic?'linear-gradient(90deg,#e4f0ec,#dfb34a 70%,#aa3030)':mode==='ratio'?'linear-gradient(90deg,#3278a1,#f7fafb,#b64b3a)':'linear-gradient(90deg,#cde7e8,#075c69)';
  $('metricLow').textContent=diagnostic?'0':mode==='ratio'?'≤0.25×':precise(colorExtent[0]);
  $('metricMiddle').textContent=diagnostic?'0.5':mode==='ratio'?'1×':'log scale';
  $('metricHigh').textContent=diagnostic?'≥1 · convergence fails':mode==='ratio'?'≥4×':precise(colorExtent[1]);
}
function applyYear(year) {
  DB.year=Number(year);metricState.year=DB.year;
  const annual=DB.annual[String(year)];
  regions.forEach(r=>{
    r.networkResult=PPRMetrics.evaluate(network.units[r.unit_id],chosenModels[r.unit_id],{...metricState,npp_data:nppData(r.unit_id)});
    r.ppr_species_2019=r.networkResult.value;
    r.total_catch_tonnes=annual?.[r.unit_id]?.[1]??null;
    r['data availability']=r.networkResult.value==null?'unavailable':'pilot';
  });
  regions.sort((a,b)=>(a.ppr_species_2019===null)-(b.ppr_species_2019===null)||(b.ppr_species_2019||0)-(a.ppr_species_2019||0)||a.unit_id.localeCompare(b.unit_id));
  const values=regions.map(r=>r.networkResult.value).filter(PPRMetrics.finite);
  colorExtent=values.length?[Math.min(...values),Math.max(...values)]:[0,1];
  const total=values.reduce((a,b)=>a+b,0);let rank=0,prior=null,cumulative=0;
  regions.forEach((r,i)=>{const v=r.networkResult.value;if(v==null){r.ppr_rank=null;r.global_ppr_share=null;r.cumulative_ppr_share=null;return}if(v!==prior)rank=i+1;prior=v;cumulative+=v;r.ppr_rank=rank;r.global_ppr_share=metricState.mode==='ppr'&&total?v/total:null;r.cumulative_ppr_share=metricState.mode==='ppr'&&total?cumulative/total:null});
  regionGroup.clearLayers();markerGroup.clearLayers();regions.forEach(addRegion);
  $('yearTotal').textContent=`${values.length} of 10 pilot ecosystems have this result. Models remain separate; rankings describe the current view.`;
  updateLegend();if(selectedId)renderDetails(regionById[selectedId]);refresh();
  const params=new URLSearchParams(location.search);params.set('metric',metricState.mode);params.set('year',DB.year);params.set('npp',metricState.npp);params.set('npp_fill',metricState.npp_fill);
  for(const key of ['scope','method','denominator','te','unidentified'])params.set(key,metricState[key]);
  const overrides=Object.fromEntries(Object.entries(chosenModels).filter(([id,index])=>index!==network.units[id].default_model).map(([id,index])=>[id,network.units[id].models[index].id]));
  if(Object.keys(overrides).length)params.set('models',JSON.stringify(overrides));else params.delete('models');
  try{history.replaceState(null,'','?'+params.toString()+location.hash);}catch{/* Local-file history may be restricted. */}
}
populateMethods();
const nppMethods=network.npp_methods||[];
if(!nppMethods.some(m=>m.id===metricState.npp))metricState.npp=nppMethods[0]?.id||'ens_median_tC_yr';
$('mapNppMethod').replaceChildren(...nppMethods.map(m=>{const o=document.createElement('option');o.value=m.id;o.textContent=m.label||m.id;return o;}));
$('mapNppMethod').value=metricState.npp;$('mapNppFill').value=metricState.npp_fill;$('metricMode').value=metricState.mode;$('scopeFilter').value=metricState.scope;$('teFilter').value=metricState.te;$('mapUnidentified').value=metricState.unidentified;
if(Object.hasOwn(DB.annual,mapParams.get('year')))DB.year=Number(mapParams.get('year'));
for(const [id,key] of [['metricMode','mode'],['scopeFilter','scope'],['methodFilter','method'],['denominatorFilter','denominator'],['teFilter','te'],['mapNppMethod','npp'],['mapNppFill','npp_fill'],['mapUnidentified','unidentified']]){
  $(id).addEventListener('change',()=>{metricState[key]=$(id).value;if(key==='scope')populateMethods();applyYear(DB.year)});
}
Object.keys(DB.annual).sort().reverse().forEach(year=>{const o=document.createElement('option');o.value=year;o.textContent=year;o.selected=Number(year)===DB.year;$('yearFilter').appendChild(o)});
$('yearFilter').addEventListener('change',()=>applyYear($('yearFilter').value));
$('colorRegionsByPpr').checked=true;$('showArticles').checked=false;
// The pilot filter is explicit membership, not whichever ten happen to rank first.
const priorPassRegion=passRegion;
passRegion=function(r){if($('rankFilter').value==='10'&&!network.units[r.unit_id])return false;return priorPassRegion(r)||($('rankFilter').value==='10'&&network.units[r.unit_id]&&(()=>{const previous=$('rankFilter').value;$('rankFilter').value='167';const match=priorPassRegion(r);$('rankFilter').value=previous;return match})())};
applyYear(DB.year);
