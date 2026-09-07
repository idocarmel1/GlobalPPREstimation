/* Runs after the inherited atlas has initialized its layers. */
const network = DB.network;
const metricState = {year:DB.year,scope:'all',mode:'ppr',method:'new_GE',denominator:'new_TE_EEfix',te:'GE'};
const chosenModels = Object.fromEntries(Object.entries(network.units).map(([id,u])=>[id,u.default_model]));
const $ = id => document.getElementById(id);
const escapeMetric = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const precise = v => v == null ? 'Unavailable' : v.toLocaleString(undefined,{maximumSignificantDigits:4});
const metricName = () => ({ppr:'PPR (tonnes carbon)',ratio:'Method ratio',b:'Recycling b',rho_living:'Rho living'})[metricState.mode];
const resultText = r => r.networkResult?.value == null ? 'Unavailable' : precise(r.networkResult.value)+(metricState.mode==='ppr'?' t C':metricState.mode==='ratio'?'×':'');
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
    const p=new URLSearchParams({units:r.unit_id,method:unit?metricState.method:'simple trophic chain',scope:unit?metricState.scope:'all',year:DB.year});
    if(model)p.set('models',JSON.stringify({[r.unit_id]:model.id}));
    const link=document.createElement('a');link.href='trends.html?'+p.toString();link.textContent=unit?'PPR through time →':'PPR through time · catch-taxon TL →';
    const links=document.createElement('p');links.className='actions';links.appendChild(link);return links;
  };
  if(!unit){panel.innerHTML='<p>No article is selected for estimation in this pilot. This ecosystem remains uncolored.</p>';panel.appendChild(trendLink());old.replaceWith(panel);return}
  const idx=chosenModels[r.unit_id],model=unit.models[idx];
  panel.innerHTML=`<div class="field"><label for="modelFilter">Ecopath model for this ecosystem</label><select id="modelFilter"></select></div><div class="network-value">${resultText(r)}</div><div class="network-note">${metricName()} ${metricState.mode==='ppr'||metricState.mode==='ratio'?'· '+metricState.scope+' · '+DB.year+' · '+escapeMetric(metricState.method):'· '+metricState.te}</div><p class="network-status">${escapeMetric(result.status)}</p>`;
  const sel=panel.querySelector('select');
  unit.models.forEach((m,i)=>{const o=document.createElement('option');o.value=i;o.textContent=m.label||m.id.replaceAll('_',' ');o.selected=i===idx;sel.appendChild(o)});
  sel.addEventListener('change',()=>{chosenModels[r.unit_id]=Number(sel.value);applyYear(DB.year)});
  const notes=document.createElement('p');notes.className='network-note';notes.textContent=unit.note;panel.appendChild(notes);
  panel.appendChild(trendLink());
  if(result.coverage!=null){const coverage=document.createElement('p');coverage.className='network-note';coverage.textContent=`${pct(result.coverage)} of annual catch included (${precise(result.catch)} tonnes). `+(metricState.mode==='ratio'?'Both methods use exactly these taxa.':'Missing method values are excluded; this is a partial footprint when coverage is below 100%.');panel.appendChild(coverage)}
  if(metricState.mode==='ratio'&&result.value!=null){const pair=document.createElement('p');pair.className='network-note';pair.textContent=`${metricState.method}: ${precise(result.numerator)} t C ÷ ${metricState.denominator}: ${precise(result.denominator)} t C`;panel.appendChild(pair)}
  if(model){
    const links=document.createElement('p');links.className='actions';
    for(const [label,path] of [['Source PPR workbook (wet weight)',model.workbook],['SPPR and diagnostics',model.source]]){
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
  $('yearFilter').disabled=diagnostic;$('methodLabel').textContent=mode==='ratio'?'Numerator method':'Estimation method';
  $('metricLegendTitle').textContent=metricName();
  $('metricHelp').textContent=diagnostic?'Read directly from diagnose_sppr(). Values below 1 are necessary for convergence, but do not guarantee validity; inspect the reported status. TE has no recycling matrix, so its b is zero by construction, not evidence of absent ecological recycling. Diagnostics are fixed for the chosen model.':mode==='ratio'?'Numerator ÷ denominator, using only catch taxa available to both methods in the same year, model and source scope. Both PPR masses are shown in carbon (wet weight ÷ 9).':'PPR in tonnes carbon = annual catch × mapped SPPR ÷ 9. Model coefficients are fixed across years. Failed methods remain unavailable.';
  $('metricGradient').style.background=diagnostic?'linear-gradient(90deg,#e4f0ec,#dfb34a 70%,#aa3030)':mode==='ratio'?'linear-gradient(90deg,#3278a1,#f7fafb,#b64b3a)':'linear-gradient(90deg,#cde7e8,#075c69)';
  $('metricLow').textContent=diagnostic?'0':mode==='ratio'?'≤0.25×':precise(colorExtent[0]);
  $('metricMiddle').textContent=diagnostic?'0.5':mode==='ratio'?'1×':'log scale';
  $('metricHigh').textContent=diagnostic?'≥1 · convergence fails':mode==='ratio'?'≥4×':precise(colorExtent[1]);
}
function applyYear(year) {
  DB.year=Number(year);metricState.year=DB.year;
  const annual=DB.annual[String(year)];
  regions.forEach(r=>{
    r.networkResult=PPRMetrics.evaluate(network.units[r.unit_id],chosenModels[r.unit_id],metricState);
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
}
populateMethods();
for(const [id,key] of [['metricMode','mode'],['scopeFilter','scope'],['methodFilter','method'],['denominatorFilter','denominator'],['teFilter','te']]){
  $(id).addEventListener('change',()=>{metricState[key]=$(id).value;if(key==='scope')populateMethods();applyYear(DB.year)});
}
Object.keys(DB.annual).sort().reverse().forEach(year=>{const o=document.createElement('option');o.value=year;o.textContent=year;o.selected=Number(year)===DB.year;$('yearFilter').appendChild(o)});
$('yearFilter').addEventListener('change',()=>applyYear($('yearFilter').value));
$('colorRegionsByPpr').checked=true;$('showArticles').checked=false;
// The pilot filter is explicit membership, not whichever ten happen to rank first.
const priorPassRegion=passRegion;
passRegion=function(r){if($('rankFilter').value==='10'&&!network.units[r.unit_id])return false;return priorPassRegion(r)||($('rankFilter').value==='10'&&network.units[r.unit_id]&&(()=>{const previous=$('rankFilter').value;$('rankFilter').value='167';const match=priorPassRegion(r);$('rankFilter').value=previous;return match})())};
applyYear(DB.year);
