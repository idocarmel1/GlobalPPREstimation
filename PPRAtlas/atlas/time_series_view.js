/* No network requests: the published page also works when opened as a local file. */
(() => {
  'use strict';
  const db=SERIES_DB, $=id=>document.getElementById(id), finite=PPRTimeSeries.finite;
  const params=new URLSearchParams(location.search);
  const initialSet=db.sets.find(s=>s.id===(params.get('set')||'global')) || db.sets[0];
  const initialMethods=params.has('methods')?params.get('methods').split(',').filter(Boolean):params.getAll('method').filter(Boolean);
  let models={};try {const parsed=JSON.parse(params.get('models')||'{}');if(parsed && !Array.isArray(parsed) && typeof parsed==='object') models=parsed;} catch { /* Invalid optional model overrides remain unset. */ }
  const state={units:params.has('units')?[...new Set(params.get('units').split(',').filter(Boolean))]:[...initialSet.units],
    set:params.has('units')?'custom':initialSet.id,methods:[...new Set(params.has('methods')?initialMethods:initialMethods.length?initialMethods:['simple trophic chain'])],baseline:params.get('baseline')||null,
    scope:params.get('scope')||'all',mode:params.get('metric')==='ratio'?'ratio':'ppr',
    npp:params.get('npp')||'ens_median_tC_yr',models};
  let result,geometry,focus=Math.max(0,db.years.indexOf(Number(params.get('year')||db.years.at(-1))));
  const methodInfo=id=>db.ppr_methods.find(m=>m.id===id);
  const methodLabel=id=>methodInfo(id)?.label||id;
  const relevantMethods=()=>[...new Set([...state.methods,...(state.baseline?[state.baseline]:[])])];
  const usesModels=()=>relevantMethods().some(id=>methodInfo(id)?.kind==='model');
  const taxonOnly=()=>relevantMethods().length>0 && relevantMethods().every(id=>methodInfo(id)?.kind==='taxon');
  const hasValues=()=>result.series.some(s=>s.points.some(p=>finite(p.value)));
  const nppInfo=()=>db.npp_methods.find(m=>m.id===state.npp);
  if(taxonOnly())state.scope='all';
  const singleYears=state.units.length===1?db.years.filter((year,i)=>finite(db.units[state.units[0]]?.simple?.catch?.[i])):[];
  state.from=db.years.includes(Number(params.get('from')))?Number(params.get('from')):(singleYears[0]??db.years[0]);
  state.to=db.years.includes(Number(params.get('to')))?Number(params.get('to')):(singleYears.at(-1)??db.years.at(-1));
  if(state.from>state.to)[state.from,state.to]=[state.to,state.from];
  const fmt=v=>v==null?'Unavailable':v.toLocaleString(undefined,{maximumSignificantDigits:5});
  function element(tag,text,className) {const el=document.createElement(tag);if(text!=null)el.textContent=text;if(className)el.className=className;return el;}
  function options(select,items,value) {
    select.replaceChildren(...items.map(item=>{const option=element('option',item.label||item.id);option.value=item.id;return option;}));
    if(!items.some(item=>item.id===value)){const option=element('option',`${value} · unavailable`);option.value=value;select.appendChild(option);}
    select.value=value;
  }
  options($('baselineMethod'),[{id:'',label:'None'},...db.ppr_methods],state.baseline||'');
  options($('nppMethod'),db.npp_methods,state.npp);
  options($('ecosystemSet'),[...db.sets,{id:'custom',label:'Custom selection'}],state.set);
  const yearOptions=db.years.map(year=>({id:String(year),label:String(year)}));
  options($('fromYear'),yearOptions,String(state.from));options($('toYear'),yearOptions,String(state.to));
  $('metric').value=state.mode;$('sourceScope').value=state.scope;
  $('inspectYear').min=0;$('inspectYear').max=db.years.length-1;

  function methodParams(p) {
    if(state.methods.length===1)p.set('method',state.methods[0]);else p.set('methods',state.methods.join(','));
    if(state.baseline)p.set('baseline',state.baseline);
    return p;
  }
  function saveURL() {
    const p=new URLSearchParams();
    if(state.set==='custom')p.set('units',state.units.join(','));else p.set('set',state.set);
    p.set('metric',state.mode);methodParams(p);p.set('scope',state.scope);p.set('npp',state.npp);
    const overrides=Object.fromEntries(Object.entries(state.models).filter(([id])=>state.units.includes(id)));
    if(Object.keys(overrides).length)p.set('models',JSON.stringify(overrides));
    p.set('year',result.points[focus].year);p.set('from',state.from);p.set('to',state.to);
    try {history.replaceState(null,'','?'+p.toString());} catch { /* Some local-file browsers restrict history. */ }
  }
  function update() {
    const priorYear=result?.points[focus]?.year??Number(params.get('year')||db.years.at(-1));
    state.years=db.years.filter(y=>y>=state.from && y<=state.to);
    state.allow_gaps=state.units.length===1;
    result=PPRTimeSeries.compare(db,state);
    focus=result.points.findIndex(p=>p.year===priorYear);if(focus<0)focus=result.points.length-1;
    $('inspectYear').max=result.points.length-1;
    const ratio=state.mode==='ratio', single=state.units.length===1;
    const name=single?(db.units[state.units[0]]?.name||state.units[0]):db.sets.find(s=>s.id===state.set)?.label||'Custom selection';
    $('selectionTitle').textContent=`${name} · ${state.from}–${state.to}`;
    $('chooseEcosystems').textContent=`${state.units.length} ecosystem${single?'':'s'} · Change`;
    $('pprMethodText').textContent=state.methods.length===1?methodLabel(state.methods[0]):`${state.methods.length} methods selected`;
    $('pprMethod').title=state.methods.map(methodLabel).join('\n');
    $('chartTitle').textContent=result.normalized?`${ratio?'PPR / NPP':'PPR'} relative to baseline`:ratio?'PPR as a share of NPP':'Annual primary production required';
    $('cohortSummary').textContent=`${result.included.length} of ${result.selected} selected ecosystems included · ${result.included.length===result.selected?'Same':'Partial, fixed'} coverage across plotted years`;
    if(state.methods.length>1)$('cohortSummary').textContent+=' · Same ecosystems across available curves';
    if(result.included.length && result.series.some(s=>s.points.some(p=>p.value===null)))$('cohortSummary').textContent+=' · Gaps mark unavailable values';
    $('nppMethod').disabled=!ratio;$('sourceScope').disabled=taxonOnly();
    $('nppNote').hidden=!ratio;
    $('nppNote').textContent=result.annual_npp?'NPP varies by year. PPR and NPP use exactly the same ecosystems.':`Fixed ${db.npp_year} NPP repeated for every year · ${nppInfo()?.label||state.npp}. This graph does not represent historical changes in NPP.`;
    $('calculationNote').textContent=taxonOnly()?'PPR (tonnes carbon) = catch × (1 / 0.1)^(catch-taxon TL − 1) ÷ 9. Trophic levels are held fixed across years.':`PPR (tonnes carbon) = annual catch × SPPR ÷ 9, using ${state.scope==='PP'?'primary-producer':state.scope} sources. Model coefficients, trophic levels and taxon mappings are held fixed across years; missing taxa are excluded.`;
    if(ratio) $('calculationNote').textContent+=' PPR / NPP = 100 × ΣPPR carbon / ΣNPP carbon (%). Wet-weight PPR is converted to carbon once, at 1/9.';
    if(state.methods.length>1 || result.normalized)$('calculationNote').textContent+=' Available curves use the same ecosystems; the catch taxa covered by each method may differ.';
    if(result.normalized)$('calculationNote').textContent+=` Each curve is divided by ${methodLabel(state.baseline)} in the same year and ecosystems. Values are dimensionless multiples (×); missing or zero baselines leave gaps.${ratio?' The common NPP denominator cancels in this comparison.':''}`;
    const set=db.sets.find(s=>s.id===state.set);
    $('setNote').textContent=single?(db.units[state.units[0]]?.note||''):(set?.note||'Sum of selected ecosystems. Regional boundaries may overlap; this sum is not spatially deduplicated.');
    $('emptyState').hidden=hasValues();
    $('emptyReason').textContent=result.reason || (result.excluded.length?`${result.excluded[0].reason} See coverage below, or change the method, model or ecosystem set.`:'Select an ecosystem to plot its annual estimate.');
    $('downloadCSV').disabled=!hasValues();$('inspectYear').disabled=!hasValues();
    renderCoverage();draw();saveURL();
  }

  function renderCoverage() {
    $('coverageDetailsTitle').textContent=`Coverage and sources · ${result.included.length} included, ${result.excluded.length} excluded`;
    const included=element('div'),excluded=element('div');
    included.appendChild(element('h3','Included ecosystems'));
    const list=element('ul');
    for(const id of result.included){
      const unit=db.units[id], li=element('li');
      const link=element('a',`${unit.name} (${id})`),p=methodParams(new URLSearchParams({units:id,scope:state.scope,metric:state.mode,npp:state.npp,from:state.from,to:state.to}));
      if(state.models[id])p.set('models',JSON.stringify({[id]:state.models[id]}));
      link.href='trends.html?'+p.toString();li.appendChild(link);
      if(usesModels()){
        const model=unit.models.find(m=>m.id===(state.models[id]??unit.default_model));
        li.appendChild(document.createTextNode(' · '+(model?.label||model?.id||'No model')));
        if(model?.workbook){li.appendChild(document.createTextNode(' · '));const source=element('a','source workbook (wet weight)');source.href='../'+model.workbook.split('/').map(encodeURIComponent).join('/');li.appendChild(source);}
      }
      list.appendChild(li);
    }
    if(!result.included.length)list.appendChild(element('li','None for this selection.'));
    included.appendChild(list);
    excluded.appendChild(element('h3','Excluded from every plotted year'));
    const misses=element('ul');
    result.excluded.forEach(item=>misses.appendChild(element('li',`${item.name} (${item.id}) · ${item.reason}`)));
    if(!result.excluded.length)misses.appendChild(element('li','None.'));
    excluded.appendChild(misses);
    const unavailable=result.series.filter(s=>!s.points.some(p=>finite(p.value)));
    if(unavailable.length){
      excluded.appendChild(element('h3','Unavailable curves'));
      const failures=element('ul');
      unavailable.forEach(s=>failures.appendChild(element('li',`${methodLabel(s.method)} · ${seriesReason(s)}`)));
      excluded.appendChild(failures);
    }
    if(state.mode==='ratio') {
      const note=element('p',`NPP source: ${db.npp_year} Sea Around Us regional estimates. `),link=element('a','Source data');
      link.href='../NPPExtraction/NPP_2019_filled_SAU_regions.csv';note.appendChild(link);excluded.appendChild(note);
      if(state.npp==='ens_median_tC_yr')excluded.appendChild(element('p','Regional ensemble median: sum of each included region’s median across the five NPP models.'));
    }
    $('coverageBody').replaceChildren(included,excluded);
  }

  const NS='http://www.w3.org/2000/svg';
  function svg(tag,attrs={},text) {const el=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))el.setAttribute(k,v);if(text!=null)el.textContent=text;return el;}
  const palette=['#087a80','#c26724','#7155a3','#3976b5','#b64065','#63832b','#7d6251'];
  const lineStyle=index=>({color:palette[index%palette.length],dash:['none','8 4','2 4'][Math.floor(index/palette.length)%3]});
  const displayValue=value=>!finite(value)?'Unavailable':result.normalized?`${fmt(value)}×`:state.mode==='ratio'?`${fmt(value)}%`:`${fmt(value)} t C`;
  function seriesReason(series){return series.reason||[...new Set(series.excluded.map(item=>item.reason))].join(' ')||'No matching annual value.';}
  function draw() {
    const chart=$('chart'),box=$('plotWrap').getBoundingClientRect(),w=Math.max(280,box.width),h=box.height;
    const margin={left:w<500?60:77,right:25,top:31,bottom:43};
    const width=w-margin.left-margin.right,height=h-margin.top-margin.bottom;
    const values=result.series.flatMap(s=>s.points.map(p=>p.value)).filter(finite),max=values.length?Math.max(...values):1;
    const raw=(max||1)*1.08/4,power=10**Math.floor(Math.log10(raw)),fraction=raw/power;
    const step=(fraction<=1?1:fraction<=2?2:fraction<=2.5?2.5:fraction<=5?5:10)*power;
    const ymax=Math.ceil((max||1)*1.04/step)*step;
    const factor=result.normalized||state.mode==='ratio'?1:ymax>=1e9?1e9:ymax>=1e6?1e6:ymax>=1e3?1e3:1;
    const unit=result.normalized?'Multiple of baseline (×)':state.mode==='ratio'?'PPR / NPP (%)':`${factor===1e9?'Billion ':factor===1e6?'Million ':factor===1e3?'Thousand ':''}tonnes carbon`;
    const x=i=>margin.left+(result.points.length<2?.5:i/(result.points.length-1))*width;
    const y=v=>margin.top+height*(1-v/ymax);
    geometry={x,y,margin,width,height,w,h};
    chart.setAttribute('viewBox',`0 0 ${w} ${h}`);
    chart.replaceChildren(svg('title',{id:'svgTitle'},$('chartTitle').textContent),svg('desc',{id:'svgDesc'},`${state.from} to ${state.to}. ${result.included.length} ecosystems included. ${state.methods.map(methodLabel).join('; ')}.${result.normalized?' Divided by '+methodLabel(state.baseline)+'.':''} Use the Inspect year slider to read exact values, or download the plotted data.`));
    chart.appendChild(svg('text',{x:margin.left,y:15,fill:'#5d7480','font-size':10},unit));
    for(let tick=0;tick<=ymax+step/100;tick+=step){
      const py=y(tick);chart.appendChild(svg('line',{x1:margin.left,y1:py,x2:w-margin.right,y2:py,stroke:'#e5edef','stroke-dasharray':tick?'3 4':'none'}));
      chart.appendChild(svg('text',{x:margin.left-10,y:py+4,'text-anchor':'end',fill:'#5d7480','font-size':11},Number((tick/factor).toPrecision(3)).toLocaleString()));
    }
    const spacing=w<500?20:10;
    result.points.forEach((p,i)=>{if(i===0 || p.year%spacing===0 || i===result.points.length-1 && p.year%spacing>=spacing/2){
      chart.appendChild(svg('text',{x:x(i),y:h-20,'text-anchor':'middle',fill:'#5d7480','font-size':11},p.year));
    }});
    chart.appendChild(svg('text',{x:margin.left+width/2,y:h-2,'text-anchor':'middle',fill:'#5d7480','font-size':10},'Year'));
    result.series.forEach((series,index)=>{
      const style=lineStyle(index),group=svg('g',{'data-method':series.method,'aria-label':methodLabel(series.method)});
      const segments=[];let segment=[];
      series.points.forEach((p,i)=>{if(finite(p.value))segment.push({i,value:p.value});else if(segment.length){segments.push(segment);segment=[];}});
      if(segment.length)segments.push(segment);
      for(const points of segments){
        const path=points.map((p,i)=>`${i?'L':'M'}${x(p.i)},${y(p.value)}`).join(' ');
        if(result.series.length===1)group.appendChild(svg('path',{d:`${path} L${x(points.at(-1).i)},${y(0)} L${x(points[0].i)},${y(0)} Z`,fill:style.color,opacity:'.045','data-area':'true'}));
        group.appendChild(svg('path',{d:path,fill:'none',stroke:style.color,'stroke-width':2.6,'stroke-dasharray':style.dash,'stroke-linecap':'round','stroke-linejoin':'round','data-curve':'true'}));
        if(points.length===1)group.appendChild(svg('circle',{cx:x(points[0].i),cy:y(points[0].value),r:3,fill:style.color}));
      }
      chart.appendChild(group);
    });
    if(values.length){
      chart.appendChild(svg('line',{id:'focusLine',y1:margin.top,y2:margin.top+height,stroke:'#598d93','stroke-dasharray':'3 4'}));
      result.series.forEach((series,index)=>chart.appendChild(svg('circle',{id:'focusDot'+index,r:4.5,fill:lineStyle(index).color,stroke:'white','stroke-width':2})));
    }
    inspect(focus);
  }
  function inspect(index) {
    focus=Math.max(0,Math.min(result.points.length-1,Number(index)));
    const p=result.points[focus];
    const multiple=result.series.length>1;
    $('focusYear').textContent=p.year;$('focusValue').textContent=multiple?`${result.series.filter(s=>finite(s.points[focus].value)).length} of ${result.series.length} curves`:displayValue(p.value);
    const descriptions=result.series.map(s=>`${methodLabel(s.method)}: ${displayValue(s.points[focus].value)}`);
    $('inspectYear').value=focus;$('inspectYear').setAttribute('aria-valuetext',`${p.year}: ${descriptions.join('; ')||'No methods selected'}`);$('inspectValue').value=p.year;
    $('coverage').textContent=multiple?`${p.year} · Catch coverage is reported separately for each method below its value. Catch is measured in tonnes wet weight.`:p.coverage==null?(p.value===null?`${p.year} · No value is available.`:'Catch coverage unavailable.'): `${p.year} · ${fmt(p.coverage*100)}% of included ecosystems’ catch has a PPR coefficient (${fmt(p.covered_catch)} of ${fmt(p.catch)} tonnes).`;
    $('seriesLegend').hidden=!multiple;
    if(multiple)$('seriesLegend').replaceChildren(...result.series.map((series,index)=>{
      const point=series.points[focus],style=lineStyle(index),item=element('div',null,'series-key'),key=svg('svg',{width:26,height:10,viewBox:'0 0 26 10','aria-hidden':'true'});
      key.appendChild(svg('line',{x1:0,x2:26,y1:5,y2:5,stroke:style.color,'stroke-width':2.6,'stroke-dasharray':style.dash}));
      const text=element('div');text.appendChild(element('b',methodLabel(series.method)));
      const coverage=point.coverage==null?'Catch coverage unavailable':`${fmt(point.coverage*100)}% catch coverage`;
      const output=element('output',`${displayValue(point.value)} · ${coverage}`);
      if(!finite(point.value))output.appendChild(element('span',` · ${point.unavailable_reason||seriesReason(series)}`));
      text.appendChild(output);item.append(key,text);return item;
    }));
    if($('focusLine')){
      const px=geometry.x(focus);$('focusLine').setAttribute('x1',px);$('focusLine').setAttribute('x2',px);
      result.series.forEach((series,index)=>{const dot=$('focusDot'+index),value=series.points[focus].value;dot.style.display=finite(value)?'':'none';if(finite(value)){dot.setAttribute('cx',px);dot.setAttribute('cy',geometry.y(value));}});
    }
  }
  $('chart').addEventListener('pointermove',event=>{if(!hasValues())return;const rect=$('chart').getBoundingClientRect(),px=(event.clientX-rect.left)*geometry.w/rect.width;inspect(Math.round((px-geometry.margin.left)/geometry.width*(result.points.length-1)));});
  $('inspectYear').addEventListener('input',event=>inspect(event.target.value));
  $('inspectYear').addEventListener('change',saveURL);
  for(const [id,key,other,otherId] of [['fromYear','from','to','toYear'],['toYear','to','from','fromYear']]){
    $(id).addEventListener('change',()=>{state[key]=Number($(id).value);if(state.from>state.to){state[other]=state[key];$(otherId).value=state[other];}update();});
  }
  function methodsChanged(){if(taxonOnly()){state.scope='all';$('sourceScope').value='all';}update();}
  for(const [id,key] of [['metric','mode'],['baselineMethod','baseline'],['sourceScope','scope'],['nppMethod','npp']]){
    $(id).addEventListener('change',()=>{state[key]=$(id).value||null;methodsChanged();});
  }

  function renderMethods(){
    const catalog=[...db.ppr_methods,...state.methods.filter(id=>!methodInfo(id)).map(id=>({id,label:id,kind:'unknown',scopes:[]}))];
    $('methodList').replaceChildren(...catalog.map((method,index)=>{
      const row=element('div',null,'ecosystem-row'),label=element('label'),check=element('input');
      check.type='checkbox';check.id='method_'+index;check.checked=state.methods.includes(method.id);
      const text=element('span',method.label||method.id);
      text.appendChild(element('small',method.kind==='taxon'?'Catch-taxon trophic levels · all sources':method.kind==='model'?'Ecopath model · '+method.scopes.join(', '):'Unknown method · unavailable'));
      label.append(check,text);row.appendChild(label);
      check.addEventListener('change',()=>{if(check.checked)state.methods.push(method.id);else state.methods=state.methods.filter(id=>id!==method.id);methodsChanged();$('methodCount').textContent=`${state.methods.length} selected`;});
      return row;
    }));
    $('methodCount').textContent=`${state.methods.length} selected`;
  }
  $('pprMethod').addEventListener('click',()=>{renderMethods();$('methodDialog').showModal();});
  for(const id of ['closeMethods','doneMethods'])$(id).addEventListener('click',()=>$('methodDialog').close());
  $('selectAllMethods').addEventListener('click',()=>{state.methods=db.ppr_methods.map(m=>m.id);methodsChanged();renderMethods();});
  $('clearMethods').addEventListener('click',()=>{state.methods=[];methodsChanged();renderMethods();});

  const ordered=Object.entries(db.units).sort((a,b)=>a[1].name.localeCompare(b[1].name));
  const visibleUnits=()=>{const query=$('ecosystemSearch').value.trim().toLowerCase();return ordered.filter(([id,u])=>`${u.name} ${id} ${u.type}`.toLowerCase().includes(query));};
  function custom() {state.set='custom';$('ecosystemSet').value='custom';}
  function renderPicker() {
    const selected=new Set(state.units),network=usesModels(),rows=visibleUnits().map(([id,unit])=>{
      const row=element('div',null,'ecosystem-row'),label=element('label'),check=element('input');check.type='checkbox';check.id='pick_'+id;check.value=id;check.checked=selected.has(id);
      const text=element('span',unit.name);text.appendChild(element('small',`${id} · ${unit.type}${unit.pilot?' · Selected pilot':''}${!unit.simple?.ppr?.some(finite)?' · No catch estimate':''}`));
      label.append(check,text);row.appendChild(label);
      check.addEventListener('change',()=>{if(check.checked)state.units.push(id);else state.units=state.units.filter(v=>v!==id);const scroll=$('ecosystemList').scrollTop;custom();update();renderPicker();$('ecosystemList').scrollTop=scroll;$('pick_'+id).focus({preventScroll:true});});
      if(network && selected.has(id) && unit.models.length){
        const select=element('select');select.setAttribute('aria-label',`Ecopath model for ${unit.name}`);
        options(select,unit.models.map(m=>({id:m.id,label:(m.label||m.id)+(m.verified?'':' · no verified PPR')})),state.models[id]??unit.default_model);
        select.addEventListener('change',()=>{state.models[id]=select.value;update();});row.appendChild(select);
      }
      return row;
    });
    $('ecosystemList').replaceChildren(...(rows.length?rows:[element('p','No ecosystems match your search.')]));
    $('pickerCount').textContent=`${state.units.length} selected · ${rows.length} visible`;
    $('pickerNote').textContent=network?'Choose one Ecopath model per ecosystem. Failed methods and ecosystems without a verified model are excluded.':'You can select ecosystems without selected articles for the catch-taxon TL estimate. Map pilot coloring is unchanged.';
  }
  function openPicker(){renderPicker();$('ecosystemDialog').showModal();}
  $('chooseEcosystems').addEventListener('click',openPicker);$('emptyChoose').addEventListener('click',openPicker);
  for(const id of ['closeEcosystems','doneEcosystems'])$(id).addEventListener('click',()=>$('ecosystemDialog').close());
  $('ecosystemSearch').addEventListener('input',renderPicker);
  $('ecosystemSet').addEventListener('change',()=>{const set=db.sets.find(s=>s.id===$('ecosystemSet').value);state.set=$('ecosystemSet').value;if(set)state.units=[...set.units];update();renderPicker();});
  $('selectVisible').addEventListener('click',()=>{state.units=[...new Set([...state.units,...visibleUnits().map(([id])=>id)])];custom();update();renderPicker();});
  $('clearSelection').addEventListener('click',()=>{state.units=[];custom();update();renderPicker();});
  $('downloadCSV').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([PPRTimeSeries.comparisonToCSV(result,state)],{type:'text/csv;charset=utf-8'})),link=element('a');link.href=url;link.download=`ppr-${state.mode}${result.normalized?'-relative':''}-${state.set}-${state.from}-${state.to}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  new ResizeObserver(()=>{if(result)draw();}).observe($('plotWrap'));
  update();
})();
