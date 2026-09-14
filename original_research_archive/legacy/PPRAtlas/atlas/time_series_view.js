/* No network requests: the published page also works when opened as a local file. */
(() => {
  'use strict';
  const db=SERIES_DB, $=id=>document.getElementById(id), finite=PPRTimeSeries.finite;
  const groupStore=typeof PPRGroupSettings==='undefined'?null:PPRGroupSettings.create({view:'trends'});
  const params=groupStore?.params||new URLSearchParams(location.search);
  const initialSet=db.sets.find(s=>s.id===(params.get('set')||'global')) || db.sets[0];
  const initialMethods=params.has('methods')?params.get('methods').split(',').filter(Boolean):params.getAll('method').filter(Boolean);
  let models={...groupStore?.data.models};try {const parsed=JSON.parse(params.get('models')||'{}');if(parsed && !Array.isArray(parsed) && typeof parsed==='object') models={...parsed,...models};} catch { /* Invalid optional model overrides remain unset. */ }
  const state={units:params.has('units')?[...new Set(params.get('units').split(',').filter(Boolean))]:[...initialSet.units],
    set:params.has('units')?'custom':initialSet.id,methods:[...new Set(params.has('methods')?initialMethods:initialMethods.length?initialMethods:['simple trophic chain'])],baseline:params.get('baseline')||null,
    scope:params.get('scope')||'all',mode:['ratio','npp'].includes(params.get('metric'))?params.get('metric'):'ppr',npp_scope:params.get('npp_scope')==='global'?'global':'selected',
    catch_basis:['catch','discards'].includes(params.get('catch_basis'))?params.get('catch_basis'):'landings',uncertainty:params.get('uncertainty')==='0'?'0':'1',
    npp:params.get('npp')||'ens_median_tC_yr',npp_fill:params.get('npp_fill')==='earliest'?'earliest':'observed',unidentified:['zero','simple'].includes(params.get('unidentified'))?params.get('unidentified'):'method',models};
  let result,geometry,focus=Math.max(0,db.years.indexOf(Number(params.get('year')||db.years.at(-1))));
  state.group_selections=groupStore?.data.selections||{};
  const methodInfo=id=>db.ppr_methods.find(m=>m.id===id);
  const methodLabel=id=>id==='npp'?`NPP · ${nppInfo()?.label||state.npp}`:methodInfo(id)?.label||id;
  const relevantMethods=()=>[...new Set([...state.methods,...(state.baseline?[state.baseline]:[])])];
  const hasGroupSubset=()=>state.units.some(id=>{const unit=db.units[id],model=unit?.models.find(m=>m.id===(state.models[id]??unit.default_model));return model&&typeof PPRGroups!=='undefined'&&PPRGroups.active(model,state.group_selections?.[PPRGroups.key(id,model)]);});
  const usesModels=()=>state.mode!=='npp'&&(relevantMethods().some(id=>methodInfo(id)?.kind==='model')||hasGroupSubset());
  const taxonOnly=()=>relevantMethods().length>0 && relevantMethods().every(id=>methodInfo(id)?.kind==='taxon');
  const hasValues=()=>result.series.some(s=>s.points.some(p=>finite(p.value)));
  const nppInfo=()=>db.npp_methods.find(m=>m.id===state.npp);
  const catchBasisLabel=()=>({landings:'Landings',catch:'All catch',discards:'Discards'})[state.catch_basis];
  if(state.mode!=='npp'&&taxonOnly())state.scope='all';
  const singleYears=state.mode!=='npp'&&state.units.length===1?db.years.filter((year,i)=>finite(db.units[state.units[0]]?.simple?.catch?.[i])):[];
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
  $('metric').value=state.mode;$('sourceScope').value=state.scope;$('nppFill').value=state.npp_fill;$('unidentifiedTreatment').value=state.unidentified;
  $('catchBasis').value=state.catch_basis;$('uncertainty').value=state.uncertainty;
  $('nppScope').value=state.npp_scope;
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
    p.set('npp_fill',state.npp_fill);p.set('npp_scope',state.npp_scope);
    p.set('unidentified',state.unidentified);
    p.set('catch_basis',state.catch_basis);p.set('uncertainty',state.uncertainty);
    const overrides=Object.fromEntries(Object.entries(state.models).filter(([id])=>state.units.includes(id)));
    if(Object.keys(overrides).length)p.set('models',JSON.stringify(overrides));
    p.set('year',result.points[focus].year);p.set('from',state.from);p.set('to',state.to);
    if(groupStore){Object.assign(groupStore.data.models,state.models);groupStore.save(p);groupStore.attach(p);groupStore.shareLinks();}
    try {history.replaceState(null,'','?'+p.toString());} catch { /* Some local-file browsers restrict history. */ }
  }
  function update() {
    const priorYear=result?.points[focus]?.year??Number(params.get('year')||db.years.at(-1));
    state.years=db.years.filter(y=>y>=state.from && y<=state.to);
    state.allow_gaps=state.units.length===1;
    result=PPRTimeSeries.compare(db,state);
    focus=result.points.findIndex(p=>p.year===priorYear);if(focus<0)focus=result.points.length-1;
    $('inspectYear').max=result.points.length-1;
    const ratio=state.mode==='ratio', nppOnly=state.mode==='npp', globalNPP=ratio&&state.npp_scope==='global', single=state.units.length===1;
    const name=single?(db.units[state.units[0]]?.name||state.units[0]):db.sets.find(s=>s.id===state.set)?.label||'Custom selection';
    $('selectionTitle').textContent=`${name} · ${state.from}–${state.to}`;
    $('chooseEcosystems').textContent=`${state.units.length} ecosystem${single?'':'s'} · Change`;
    $('pprMethodText').textContent=state.methods.length===1?methodLabel(state.methods[0]):`${state.methods.length} methods selected`;
    $('pprMethod').title=state.methods.map(methodLabel).join('\n');
    $('chartTitle').textContent=nppOnly?'Annual NPP · selected ecosystems':catchBasisLabel()+' · '+(result.normalized?`${ratio?'PPR / NPP':'PPR'} relative to baseline`:ratio?`PPR as a share of ${globalNPP?'global atlas':'selected ecosystems’'} NPP`:'Annual primary production required');
    if(!nppOnly&&state.unidentified!=='method')$('chartTitle').textContent+=' · unidentified-catch sensitivity';
    $('cohortSummary').textContent=`${result.included.length} of ${result.selected} selected ecosystems included · ${result.included.length===result.selected?'Same':'Partial, fixed'} coverage across plotted years`;
    if(!nppOnly&&state.methods.length>1)$('cohortSummary').textContent+=' · Same ecosystems across available curves';
    if(globalNPP)$('cohortSummary').textContent+=' · Numerator cohort only; global NPP reference stays fixed';
    if(result.included.length && result.series.some(s=>s.points.some(p=>p.value===null)))$('cohortSummary').textContent+=' · Gaps mark unavailable values';
    $('nppMethod').disabled=(!ratio&&!nppOnly)||globalNPP;$('nppFill').disabled=!ratio&&!nppOnly;$('sourceScope').disabled=nppOnly||taxonOnly();
    options($('nppMethod'),globalNPP?[{id:'global_reference_ensemble',label:'Global atlas reference ensemble'}]:db.npp_methods,globalNPP?'global_reference_ensemble':state.npp);
    $('nppScope').disabled=!ratio;$('pprMethod').disabled=nppOnly;$('baselineMethod').disabled=nppOnly;$('catchBasis').disabled=nppOnly;$('unidentifiedTreatment').disabled=nppOnly;
    $('nppMethod').title=globalNPP?'Global atlas NPP uses its fixed reference ensemble. Your selected regional calculation is retained for other modes.':'';
    $('nppScope').title='Selected ecosystems: PPR relative to their own production. Global atlas NPP: selected PPR as a share of a fixed atlas production reference.';
    $('uncertainty').disabled=nppOnly||state.catch_basis!=='landings'||result.normalized;
    $('sensitivityNote').hidden=nppOnly;$('unidentifiedNote').hidden=nppOnly;
    $('sensitivityNote').textContent=state.catch_basis!=='landings'?'Discard-routing envelopes are available for landings only.':result.normalized?'Discard-routing sensitivity is not assessed for normalized method comparisons.':state.uncertainty==='0'?'Discard-routing sensitivity envelope hidden.':'Shading shows hypothetical discard-routing scenarios on the same landings, with the same NPP denominator when displayed. The annual discard fraction comes from the catch data; uniform allocation within each source model is an assumption. This is not a confidence interval. Missing or invalid responses leave gaps; a routing-invariant reference does not establish zero ecological uncertainty.';
    $('nppNote').hidden=!ratio&&!nppOnly;
    const reference=result.npp_reference||db.global_npp;
    const historical=state.npp_fill==='earliest'?'Earlier missing years use the earliest available NPP for this calculation: a constant historical estimate, not measured historical change. Internal and later gaps remain blank. Dashed curve portions mark substituted estimates.':'Unavailable years remain blank; no historical NPP is inferred.';
    $('nppNote').textContent=globalNPP?`Coverage-limited atlas reference · Global atlas NPP · ${reference?.ensemble_convention||'Reference ensemble unavailable'}. ${reference?.geography||'A fixed atlas geography, not total world ocean NPP.'} ${reference?.coverage_warning||'Source-window water masks exclude never-retrieved cells; central NPP excludes far nearest-neighbour fills.'} The denominator is independent of ecosystem and PPR-method selections. Missing annual reference calculations leave a gap. ${historical}`:result.annual_npp?`Annual NPP · ${nppInfo()?.label||state.npp}. ${nppOnly?'Sum of the selected ecosystems, independent of catch and Ecopath-model availability.':'PPR and NPP use the same fixed ecosystem cohort.'} A year is blank when any included ecosystem lacks NPP. ${historical}`:`Fixed ${db.npp_year} NPP repeated for every year · ${nppInfo()?.label||state.npp}. This graph does not represent historical changes in NPP.`;
    if((ratio||nppOnly)&&!globalNPP&&state.npp.startsWith('ens_'))$('nppNote').textContent+=' Ensemble model support can change by ecosystem and year, including years with only one model. Inspect the model counts and names under Coverage and sources.';
    if(nppOnly){
      if(state.npp.startsWith('ens_'))$('nppNote').textContent+=` Sum of regional ensemble ${state.npp.includes('median')?'medians':state.npp.includes('min')?'minima':'maxima'} across each region’s available models; this is not an ensemble statistic of global model totals.`;
      $('nppNote').textContent+=' Selected boundaries may overlap: their regional totals are summed without spatial deduplication, so this is not a unique world-ocean total.';
    }
    $('nppNote').baseNote=$('nppNote').textContent;$('nppNote').className=globalNPP?'reference-warning':'';
    $('calculationNote').textContent=taxonOnly()?'PPR (tonnes carbon) = catch × (1 / 0.1)^(catch-taxon TL − 1) ÷ 9. Trophic levels are held fixed across years.':`PPR (tonnes carbon) = annual catch × SPPR ÷ 9, using ${state.scope==='PP'?'primary-producer':state.scope} sources. Model coefficients, trophic levels and taxon mappings are held fixed across years; missing taxa are excluded.`;
    $('calculationNote').textContent=$('calculationNote').textContent.replace('= catch ×','= '+catchBasisLabel().toLowerCase()+' ×').replace('= annual catch ×','= annual '+catchBasisLabel().toLowerCase()+' ×');
    if(typeof hasGroupSubset!=='undefined'&&hasGroupSubset())$('calculationNote').textContent+=' Selected groups retain their original model mapping weights; excluded catch is not reassigned.';
    if(ratio) $('calculationNote').textContent+=` PPR / NPP = 100 × selected PPR carbon / ${globalNPP?'fixed global atlas NPP reference':'NPP of the same included ecosystems'} (%). Wet-weight PPR is converted to carbon once, at 1/9.`;
    if(!nppOnly&&(state.methods.length>1 || result.normalized))$('calculationNote').textContent+=' Available curves use the same ecosystems; the catch taxa covered by each method may differ.';
    if(result.normalized)$('calculationNote').textContent+=` Each curve is divided by ${methodLabel(state.baseline)} in the same year and ecosystems. Values are dimensionless multiples (×); missing or zero baselines leave gaps.${ratio?' The common NPP denominator cancels in this comparison.':''}`;
    if(nppOnly)$('calculationNote').textContent='NPP = sum of annual regional net primary production in tonnes carbon per year. One curve represents the chosen NPP calculation for the selected ecosystems. NPP is already carbon; no wet-weight conversion or PPR baseline is applied.';
    $('unidentifiedNote').textContent=state.unidentified==='method'?'Unidentified catch uses the selected method’s own SPPR, including its existing mappings.':state.unidentified==='zero'?'Sensitivity: explicitly unidentified / NEI catch is assigned zero PPR; its tonnage remains in total catch and coverage. This is a zero-cost scenario, not an estimated correction.':'Sensitivity: explicitly unidentified / NEI catch uses each taxon’s reference-TL simple-chain SPPR at TE=0.1. Missing reference coefficients remain uncovered. This total-only fallback is available for All sources; it has no PP, detritus or imported-source attribution.';
    $('unidentifiedNote').textContent+=' Only explicit residual labels are classified; named genera and families are retained unless their catch label or common name explicitly says unidentified / NEI. See Coverage and sources for the exact list and classifier.';
    const set=db.sets.find(s=>s.id===state.set);
    $('setNote').textContent=nppOnly?'Availability depends on annual NPP source data, independently of catch or PPR availability.':single?(db.units[state.units[0]]?.note||''):(set?.note||'Sum of selected ecosystems. Regional boundaries may overlap; this sum is not spatially deduplicated.');
    $('emptyState').hidden=hasValues();
    $('emptyReason').textContent=result.reason || (result.excluded.length?`${result.excluded[0].reason} See coverage below, or change the method, model or ecosystem set.`:'Select an ecosystem to plot its annual estimate.');
    // Missing plotted ratios still have carbon totals, bounds and reasons to export.
    $('downloadCSV').disabled=!result.series.some(s=>s.points.length);$('downloadJSON').disabled=$('downloadCSV').disabled;$('inspectYear').disabled=!hasValues();
    renderCoverage();draw();saveURL();
    if(typeof groupStore!=='undefined'&&groupStore)$('groupFilterSummary').textContent=Object.keys(groupStore.data.selections).length?`${Object.keys(groupStore.data.selections).length} models with group selections`:'All model groups included';
  }

  function renderCoverage() {
    const nppOnly=state.mode==='npp',globalNPP=state.mode==='ratio'&&state.npp_scope==='global';
    $('coverageDetailsTitle').textContent=`Coverage and sources · ${result.included.length} included, ${result.excluded.length} excluded`;
    const included=element('div'),excluded=element('div');
    included.appendChild(element('h3',globalNPP?'PPR numerator ecosystems':'Included ecosystems'));
    const list=element('ul');
    for(const id of result.included){
      const unit=db.units[id], li=element('li');
      const link=element('a',`${unit.name} (${id})`),p=methodParams(new URLSearchParams({units:id,scope:state.scope,metric:state.mode,npp:state.npp,npp_fill:state.npp_fill,npp_scope:state.npp_scope,unidentified:state.unidentified,catch_basis:state.catch_basis,uncertainty:state.uncertainty,from:state.from,to:state.to}));
      if(state.models[id])p.set('models',JSON.stringify({[id]:state.models[id]}));
      link.href='trends.html?'+p.toString();li.appendChild(link);
      if(!nppOnly&&(relevantMethods().some(id=>methodInfo(id)?.kind==='model')||result.series.some(series=>series.model_ids?.[id]))){
        const model=unit.models.find(m=>m.id===(state.models[id]??unit.default_model));
        li.appendChild(document.createTextNode(' · '+(model?.label||model?.id||'No model')));
        if(model?.workbook){li.appendChild(document.createTextNode(' · '));const source=element('a','Source workbook · total-catch calculation and mappings');source.href='../'+model.workbook.split('/').map(encodeURIComponent).join('/');li.appendChild(source);}
      }
      if(unit.sources?.workbook){li.appendChild(document.createTextNode(' · '));const source=element('a',nppOnly?'Ecosystem source workbook · annual NPP':'Ecosystem source workbook · total-catch calculation');source.href='../'+unit.sources.workbook.split('/').map(encodeURIComponent).join('/');li.appendChild(source);}
      if((state.mode==='ratio'||nppOnly)&&!globalNPP){const support=element('div');support.id='nppAvailability_'+id;li.appendChild(support);}
      if(!nppOnly){
      const audit=element('details'),taxa=unit.unidentified?.taxa||[];
      audit.appendChild(element('summary',`Unidentified catch audit · ${taxa.length} classified taxa`));
      audit.appendChild(element('p',unit.unidentified?`${unit.unidentified.classifier_version}: ${unit.unidentified.rule_description}`:'Classifier metadata unavailable in this export.'));
      const auditYear=element('p');auditYear.id='unidentifiedAvailability_'+id;audit.appendChild(auditYear);
      const auditList=element('ul');
      for(const taxon of taxa)auditList.appendChild(element('li',`${taxon.name}${taxon.common_name && taxon.common_name!==taxon.name?' ('+taxon.common_name+')':''} · ${taxon.reason} · reference TL ${fmt(taxon.reference_tl)} · simple SPPR ${fmt(taxon.simple_sppr)}`));
      if(!taxa.length)auditList.appendChild(element('li','No explicitly unidentified catch taxa in the inventory.'));
      audit.appendChild(auditList);li.appendChild(audit);
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
    if(!nppOnly){const inventory=element('a','Complete unidentified-catch classifier and inventory');inventory.href='../data/unidentified_taxa.json';excluded.appendChild(inventory);}
    const unavailable=result.series.filter(s=>!s.points.some(p=>finite(p.value)));
    if(unavailable.length){
      excluded.appendChild(element('h3','Unavailable curves'));
      const failures=element('ul');
      unavailable.forEach(s=>failures.appendChild(element('li',`${methodLabel(s.method)} · ${seriesReason(s)}`)));
      excluded.appendChild(failures);
    }
    if(state.mode==='ratio'||nppOnly) {
      const note=element('p','NPP source: annual regional estimates with availability and provenance. '),link=element('a','Annual NPP source data');
      link.href='../'+(db.npp_source||'NPPExtraction/output/annual_npp.csv').split('/').map(encodeURIComponent).join('/');note.appendChild(link);excluded.appendChild(note);
      const missing=element('details'),missingSummary=element('summary'),missingList=element('ul');
      missing.id='nppMissingDetails';missingSummary.id='nppMissingSummary';missingList.id='nppMissingList';
      missing.append(missingSummary,missingList);excluded.appendChild(missing);
      if(!globalNPP&&state.npp==='ens_median_tC_yr')excluded.appendChild(element('p','Regional ensemble median: sum of each included region’s median across its available NPP models. Model counts and identities can change by year; a one-model median is not a five-model ensemble. The inspected year’s support is listed for each ecosystem.'));
      if(globalNPP){
        const reference=result.npp_reference||db.global_npp;
        excluded.appendChild(element('h3','Fixed global atlas NPP reference'));
        excluded.appendChild(element('p',`${reference?.label||'Unavailable reference'} · ${reference?.ensemble_convention||'No ensemble metadata'}. ${reference?.geography||''} ${reference?.overlap_policy||''}`));
        const annual=element('p');annual.id='globalNPPAvailability';excluded.appendChild(annual);
        const details=element('details'),regions=element('ul'),ids=reference?.unit_ids||[];
        details.appendChild(element('summary',`${ids.length} fixed reference regions · independent of PPR selection`));
        for(const id of ids)regions.appendChild(element('li',`${db.units[id]?.name||id} (${id})`));
        details.appendChild(regions);excluded.appendChild(details);
        if(reference?.source)excluded.appendChild(element('p','Reference provenance: '+(typeof reference.source==='string'?reference.source:JSON.stringify(reference.source))));
      }
    }
    $('coverageBody').replaceChildren(included,excluded);
  }

  const NS='http://www.w3.org/2000/svg';
  function svg(tag,attrs={},text) {const el=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))el.setAttribute(k,v);if(text!=null)el.textContent=text;return el;}
  const palette=['#087a80','#c26724','#7155a3','#3976b5','#b64065','#63832b','#7d6251'];
  const lineStyle=index=>({color:palette[index%palette.length],dash:['none','8 4','2 4'][Math.floor(index/palette.length)%3]});
  const displayValue=value=>!finite(value)?'Unavailable':result.normalized?`${fmt(value)}×`:state.mode==='ratio'?`${fmt(value)}%`:`${fmt(value)} t C${state.mode==='npp'?' / yr':''}`;
  function seriesReason(series){return series.reason||[...new Set(series.excluded.map(item=>item.reason))].join(' ')||'No matching annual value.';}
  const showSensitivity=()=>state.mode!=='npp'&&state.catch_basis==='landings'&&state.uncertainty!=='0'&&!result.normalized;
  const routeLabel=name=>({SC:'Catch removal',SM:'Mortality-to-detritus proxy',SE:'External loss',SR:'Documented discard return'})[name]||name;
  const assessedSensitivity=point=>showSensitivity()&&finite(point?.value)&&point?.sensitivity?.status==='assessed'&&!point.sensitivity.hidden&&finite(point.sensitivity.lower)&&finite(point.sensitivity.upper)&&point.sensitivity.lower<=point.sensitivity.upper;
  function sensitivitySegments(points){
    const segments=[];let segment=[];
    points.forEach((point,i)=>{
      if(!assessedSensitivity(point)){if(segment.length)segments.push(segment);segment=[];return;}
      if(segment.length&&point.year!==segment.at(-1).year+1){segments.push(segment);segment=[];}
      segment.push({...point,i});
    });
    if(segment.length)segments.push(segment);
    return segments;
  }
  function renderSensitivityReadout(){
    const container=$('sensitivityReadout');container.hidden=!showSensitivity();container.replaceChildren();
    if(container.hidden)return;
    result.series.forEach((series,index)=>{
      const point=series.points[focus],band=point.sensitivity,item=element('div',null,'sensitivity-card');
      item.appendChild(element('b',`${methodLabel(series.method)} · discard-routing sensitivity`));
      if(!assessedSensitivity(point)){item.appendChild(element('p','Not assessed. '+(band?.reason||point.unavailable_reason||'No compatible response is available for this selection.')));container.appendChild(item);return;}
      item.appendChild(element('p',`${displayValue(band.lower)}–${displayValue(band.upper)} · circle marks the central landings estimate.`));
      const minimum=Math.min(band.lower,point.value),maximum=Math.max(band.upper,point.value),span=maximum-minimum,x=value=>span?12+196*(value-minimum)/span:110;
      const interval=svg('svg',{viewBox:'0 0 220 28',class:'sensitivity-interval',role:'img','aria-label':`Scenario range ${displayValue(band.lower)} to ${displayValue(band.upper)}; central estimate ${displayValue(point.value)}`});
      interval.append(svg('line',{x1:12,x2:208,y1:14,y2:14,stroke:'#d9e4e7'}),svg('line',{x1:x(band.lower),x2:x(band.upper),y1:14,y2:14,stroke:lineStyle(index).color,'stroke-width':6}),svg('line',{x1:x(band.lower),x2:x(band.lower),y1:6,y2:22,stroke:lineStyle(index).color}),svg('line',{x1:x(band.upper),x2:x(band.upper),y1:6,y2:22,stroke:lineStyle(index).color}),svg('circle',{cx:x(point.value),cy:14,r:4.5,fill:'#183945',stroke:'white'}));item.appendChild(interval);
      const context=[];
      if(finite(band.discard_fraction))context.push(`Discards / all catch: ${fmt(100*band.discard_fraction)}%.`);
      if(band.interpolated)context.push('Interpolated between valid tested fractions.');
      if(band.construction_invariant)context.push('Routing-invariant by construction; this does not establish zero ecological uncertainty.');
      if(band.reason)context.push(band.reason);
      if(context.length)item.appendChild(element('p',context.join(' ')));
      const details=element('details'),sources=band.sources||[{model_id:band.model_id,source_hash:band.source_hash,study_version:band.study_version,discard_fraction:band.discard_fraction}],list=element('ul');
      details.appendChild(element('summary','Routes, exclusions and source'));
      for(const source of sources)list.appendChild(element('li',`${source.model_id||'Selected model'} · ${source.study_version||'Study version unavailable'} · discards / all catch ${finite(source.discard_fraction)?fmt(100*source.discard_fraction)+'%':'unavailable'} · source SHA-256 ${source.source_hash||'unavailable'}`));
      for(const [name,value]of Object.entries(band.route_ppr_tC||{}))list.appendChild(element('li',`${routeLabel(name)} (${name}): ${fmt(value)} t C on the same landings.`));
      const exclusions=Array.isArray(band.excluded_routes)?band.excluded_routes.map(name=>[name,'Unavailable in part of the selected cohort']):Object.entries(band.excluded_routes||{});
      for(const [name,reason]of exclusions)list.appendChild(element('li',`${routeLabel(name)} (${name}) excluded: ${reason}`));
      details.appendChild(list);item.appendChild(details);container.appendChild(item);
    });
  }
  function draw() {
    const chart=$('chart'),box=$('plotWrap').getBoundingClientRect(),w=Math.max(280,box.width),h=box.height;
    const margin={left:w<500?60:77,right:25,top:31,bottom:43};
    const width=w-margin.left-margin.right,height=h-margin.top-margin.bottom;
    const values=result.series.flatMap(s=>s.points.flatMap(p=>assessedSensitivity(p)?[p.value,p.sensitivity.upper]:[p.value])).filter(finite),max=values.length?Math.max(...values):1;
    const raw=(max||1)*1.08/4,power=10**Math.floor(Math.log10(raw)),fraction=raw/power;
    const step=(fraction<=1?1:fraction<=2?2:fraction<=2.5?2.5:fraction<=5?5:10)*power;
    const ymax=Math.ceil((max||1)*1.04/step)*step;
    const factor=result.normalized||state.mode==='ratio'?1:ymax>=1e9?1e9:ymax>=1e6?1e6:ymax>=1e3?1e3:1;
    const unit=result.normalized?'Multiple of baseline (×)':state.mode==='ratio'?`PPR / ${state.npp_scope==='global'?'global atlas ':''}NPP (%)`:`${factor===1e9?'Billion ':factor===1e6?'Million ':factor===1e3?'Thousand ':''}tonnes carbon${state.mode==='npp'?' per year':''}`;
    const x=i=>margin.left+(result.points.length<2?.5:i/(result.points.length-1))*width;
    const y=v=>margin.top+height*(1-v/ymax);
    geometry={x,y,margin,width,height,w,h};
    chart.setAttribute('viewBox',`0 0 ${w} ${h}`);
    chart.replaceChildren(svg('title',{id:'svgTitle'},$('chartTitle').textContent),svg('desc',{id:'svgDesc'},`${state.from} to ${state.to}. ${result.included.length} ecosystems included. ${result.series.map(s=>methodLabel(s.method)).join('; ')}.${result.normalized?' Divided by '+methodLabel(state.baseline)+'.':''} Use the Inspect year slider to read exact values, or download the plotted data.`));
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
      for(const points of sensitivitySegments(series.points)){
        if(points.length===1){const p=points[0];group.appendChild(svg('line',{x1:x(p.i),x2:x(p.i),y1:y(p.sensitivity.lower),y2:y(p.sensitivity.upper),stroke:style.color,'stroke-width':5,opacity:'.25','data-sensitivity-band':'isolated'}));continue;}
        const path=points.map((p,i)=>`${i?'L':'M'}${x(p.i)},${y(p.sensitivity.upper)}`).join(' ')+' '+[...points].reverse().map(p=>`L${x(p.i)},${y(p.sensitivity.lower)}`).join(' ')+' Z';
        group.appendChild(svg('path',{d:path,fill:style.color,opacity:'.16','data-sensitivity-band':'true'}));
      }
      const segments=[];let segment=[];
      series.points.forEach((p,i)=>{
        if(finite(p.value)){
          const point={i,value:p.value,estimated:Boolean(p.npp_estimated)};
          if(segment.length && segment.at(-1).estimated!==point.estimated){segments.push(segment);segment=[{...segment.at(-1),estimated:point.estimated}];}
          segment.push(point);
        }else if(segment.length){segments.push(segment);segment=[];}
      });
      if(segment.length)segments.push(segment);
      for(const points of segments){
        const path=points.map((p,i)=>`${i?'L':'M'}${x(p.i)},${y(p.value)}`).join(' ');
        group.appendChild(svg('path',{d:path,fill:'none',stroke:style.color,'stroke-width':2.6,'stroke-dasharray':points[0].estimated?'5 5':style.dash,'stroke-linecap':'round','stroke-linejoin':'round','data-curve':'true','data-npp-estimate':String(points[0].estimated)}));
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
  function globalCoverageDescription(metadata={}){
    const coverage=metadata.coverage||{},waterPct=metadata.water_area_pct_of_polygon??coverage.water_area_pct_of_polygon;
    const parts=['Coverage-limited atlas reference.'];
    if(finite(waterPct))parts.push(`Source-supported water mask: ${fmt(waterPct)}% of the reference polygon${finite(coverage.water_area_km2)&&finite(coverage.polygon_area_km2)?` (${fmt(coverage.water_area_km2)} of ${fmt(coverage.polygon_area_km2)} km²)`:''}.`);
    else parts.push('Annual supported-water area is unavailable.');
    const waterDays=coverage.central_support_pct_of_water_pixel_days,polygonDays=coverage.central_support_pct_of_polygon_pixel_days;
    if(finite(waterDays)||finite(polygonDays))parts.push(`Central estimate’s day-weighted included area: ${[finite(waterDays)?`${fmt(waterDays)}% of supported water pixel-days`:null,finite(polygonDays)?`${fmt(polygonDays)}% of reference polygon pixel-days`:null].filter(Boolean).join('; ')}.`);
    if(finite(coverage.excluded_far_pct_of_water_pixel_days))parts.push(`Far-fill exclusion: ${fmt(coverage.excluded_far_pct_of_water_pixel_days)}% of supported water pixel-days.`);
    parts.push('These are source-support measures, not observed world-ocean coverage.');
    return parts.join(' ');
  }
  function inspect(index) {
    focus=Math.max(0,Math.min(result.points.length-1,Number(index)));
    const p=result.points[focus];
    const multiple=result.series.length>1;
    $('focusYear').textContent=p.year;$('focusValue').textContent=multiple?`${result.series.filter(s=>finite(s.points[focus].value)).length} of ${result.series.length} curves`:displayValue(p.value);
    const descriptions=result.series.map(s=>`${methodLabel(s.method)}: ${displayValue(s.points[focus].value)}`);
    $('inspectYear').value=focus;$('inspectYear').setAttribute('aria-valuetext',`${p.year}: ${descriptions.join('; ')||'No methods selected'}`);$('inspectValue').value=p.year;
    if(state.mode==='npp'){
      const available=p.npp_available_ids?.length??(p.npp===null?'Unknown':result.included.length);
      $('coverage').textContent=`${p.year} · Annual NPP for ${available} of ${result.included.length} selected ecosystems. Catch and Ecopath-model availability do not restrict this curve.`;
    }else{
    $('coverage').textContent=multiple?`${p.year} · Catch coverage is reported separately for each method below its value. Catch is measured in tonnes wet weight.`:p.coverage==null?(p.value===null?`${p.year} · No value is available.`:'Catch coverage unavailable.'): `${p.year} · ${fmt(p.coverage*100)}% of included ecosystems’ catch has a PPR coefficient (${fmt(p.covered_catch)} of ${fmt(p.catch)} tonnes).`;
    const affected=result.series.find(s=>s.points[focus].unidentified_share!=null)?.points[focus]||p;
    $('coverage').textContent=$('coverage').textContent.replace(/catch/gi,catchBasisLabel().toLowerCase());
    $('coverage').textContent+=affected.unidentified_share==null?' Unidentified-catch share unavailable.':` Explicitly unidentified / NEI: ${fmt(100*affected.unidentified_share)}% of ${catchBasisLabel().toLowerCase()} (${fmt(affected.unidentified_catch)} tonnes).`;
    if(state.unidentified==='simple' && affected.unidentified_missing_simple_catch>0)$('coverage').textContent+=` ${fmt(affected.unidentified_missing_simple_catch)} tonnes of that catch lack a reference coefficient and remain uncovered.`;
    for(const id of result.included){
      const target=$('unidentifiedAvailability_'+id),unit=db.units[id],i=db.years.indexOf(p.year);if(!target)continue;
      const audit=unit.unidentified?.catch_bases?.[state.catch_basis]||(state.catch_basis==='landings'?unit.unidentified:null),basis=state.catch_basis==='landings'?unit.simple:unit.simple?.catch_bases?.[state.catch_basis];
      const catchValue=audit?.catch?.[i],total=basis?.catch?.[i],missing=audit?.missing_simple_catch?.[i];
      target.textContent=`${p.year}: ${fmt(catchValue)} tonnes explicitly unidentified / NEI${total>0 && catchValue!=null?' · '+fmt(100*catchValue/total)+'% of '+catchBasisLabel().toLowerCase():''}. Missing reference coefficient: ${fmt(missing)} tonnes.`;
    }
    }
    if(state.mode==='ratio'||state.mode==='npp'){
      const point=result.series.find(s=>s.points[focus].npp_estimated)?.points[focus]||p;
      const globalNPP=state.mode==='ratio'&&state.npp_scope==='global',label=globalNPP?'Fixed global atlas NPP denominator':state.mode==='ratio'?'Selected-cohort NPP denominator':'Selected NPP total';
      $('coverage').textContent+=point.npp===null?` ${label} unavailable. ${point.npp_reason||'Fixed reference coverage is incomplete.'}`:` ${label}: ${fmt(point.npp)} t C / yr.`;
      const missingIds=point.npp_missing_ids||[];
      if(missingIds.length)$('coverage').textContent+=missingIds.length>5?` Missing NPP for ${missingIds.length} ecosystems; see Coverage and sources.`:` Missing NPP: ${missingIds.join(', ')}.`;
      $('nppMissingDetails').hidden=!missingIds.length;
      $('nppMissingSummary').textContent=`${p.year} · ${missingIds.length} ecosystems missing annual NPP`;
      $('nppMissingList').replaceChildren(...missingIds.map(id=>element('li',`${db.units[id]?.name||id} (${id})`)));
      if(point.npp_estimated)$('coverage').textContent+=` Historical estimate: substituted NPP for ${(point.npp_substituted_ids||[]).map(id=>`${id} from ${point.npp_source_years?.[id]??'an earlier reference year'}`).join(', ')}.`;
      if(globalNPP){
        const metadata=point.npp_reference_metadata||{},target=$('globalNPPAvailability'),modelNames=metadata.model_names||metadata.available_models||[];
        const coverageDescription=globalCoverageDescription(metadata);
        $('coverage').textContent+=' '+coverageDescription;
        $('nppNote').textContent=$('nppNote').baseNote+` Inspected ${p.year}${point.npp_estimated?' (historical substitution)':''}: `+coverageDescription;
        if(target)target.textContent=`${p.year}: ${coverageDescription} ${fmt(point.npp)} t C / yr · ${metadata.model_count??metadata.n_models??'unknown number of'} computed NPP model total(s)${modelNames.length?' ('+modelNames.join(', ')+')':''}; calculation status: ${metadata.calculation_complete||metadata.complete?'complete':(metadata.status||'not recorded').replaceAll('_',' ')}. ${metadata.reason||''}${point.npp_estimated?' Historical substitution: '+JSON.stringify(point.npp_source_years||{}):''}`;
      }
      for(const id of result.included){
        const target=$('nppAvailability_'+id);if(!target)continue;
        const metadata=point.npp_provenance?.[id],sourceYear=point.npp_source_years?.[id];
        const available=metadata?.available_models,names=Array.isArray(available)?available.join(', '):available;
        target.textContent=`NPP ${p.year}: ${sourceYear==null?'unavailable':point.npp_substituted_ids?.includes(id)?'historical estimate using '+sourceYear:'annual source value'}`;
        if(state.npp.startsWith('ens_'))target.textContent+=` · ${metadata?.n_models??'unknown number of'} NPP model(s)${names?' ('+names+')':''}${metadata?.ensemble_basis?' · '+metadata.ensemble_basis:''}`;
      }
    }
    $('seriesLegend').hidden=!multiple;
    if(multiple)$('seriesLegend').replaceChildren(...result.series.map((series,index)=>{
      const point=series.points[focus],style=lineStyle(index),item=element('div',null,'series-key'),key=svg('svg',{width:26,height:10,viewBox:'0 0 26 10','aria-hidden':'true'});
      key.appendChild(svg('line',{x1:0,x2:26,y1:5,y2:5,stroke:style.color,'stroke-width':2.6,'stroke-dasharray':style.dash}));
      const text=element('div');text.appendChild(element('b',methodLabel(series.method)));
      const coverage=point.coverage==null?catchBasisLabel()+' coverage unavailable':`${fmt(point.coverage*100)}% ${catchBasisLabel().toLowerCase()} coverage`;
      const output=element('output',`${displayValue(point.value)}${point.npp_estimated?' · Historical NPP estimate':''} · ${coverage}`);
      if(!finite(point.value))output.appendChild(element('span',` · ${point.unavailable_reason||seriesReason(series)}`));
      text.appendChild(output);item.append(key,text);return item;
    }));
    renderSensitivityReadout();
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
  function methodsChanged(){if(state.mode!=='npp'&&taxonOnly()){state.scope='all';$('sourceScope').value='all';}update();}
  for(const [id,key] of [['metric','mode'],['baselineMethod','baseline'],['sourceScope','scope'],['nppMethod','npp'],['nppFill','npp_fill'],['nppScope','npp_scope'],['unidentifiedTreatment','unidentified'],['catchBasis','catch_basis'],['uncertainty','uncertainty']]){
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
    $('ecosystemHint').textContent=state.mode==='npp'?'The graph sums annual NPP for your selection. Catch data and Ecopath models are not required.':'The graph sums your selection. Each model version is used separately.';
    const selected=new Set(state.units),network=usesModels(),rows=visibleUnits().map(([id,unit])=>{
      const row=element('div',null,'ecosystem-row'),label=element('label'),check=element('input');check.type='checkbox';check.id='pick_'+id;check.value=id;check.checked=selected.has(id);
      const text=element('span',unit.name);text.appendChild(element('small',`${id} · ${unit.type}${unit.pilot?' · Selected pilot':''}${state.mode!=='npp'&&!unit.simple?.ppr?.some(finite)?' · No catch estimate':''}`));
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
    $('pickerNote').textContent=state.mode==='npp'?'NPP uses all selected ecosystems with annual NPP data, including those without catch data or an Ecopath model. A missing annual value leaves a gap for the fixed selection.':network?'Choose one Ecopath model per ecosystem. Failed methods and ecosystems without a verified model are excluded.':'You can select ecosystems without selected articles for the catch-taxon TL estimate. Map pilot coloring is unchanged.';
  }
  function openPicker(){renderPicker();$('ecosystemDialog').showModal();}
  $('chooseEcosystems').addEventListener('click',openPicker);$('emptyChoose').addEventListener('click',openPicker);
  for(const id of ['closeEcosystems','doneEcosystems'])$(id).addEventListener('click',()=>$('ecosystemDialog').close());
  $('ecosystemSearch').addEventListener('input',renderPicker);
  $('ecosystemSet').addEventListener('change',()=>{const set=db.sets.find(s=>s.id===$('ecosystemSet').value);state.set=$('ecosystemSet').value;if(set)state.units=[...set.units];update();renderPicker();});
  $('selectVisible').addEventListener('click',()=>{state.units=[...new Set([...state.units,...visibleUnits().map(([id])=>id)])];custom();update();renderPicker();});
  $('clearSelection').addEventListener('click',()=>{state.units=[];custom();update();renderPicker();});
  function download(format){
    const content=format==='csv'?PPRTimeSeries.comparisonToCSV(result,state):PPRTimeSeries.comparisonToJSON(result,state);
    const url=URL.createObjectURL(new Blob([typeof content==='string'?content:JSON.stringify(content,null,2)],{type:format==='csv'?'text/csv;charset=utf-8':'application/json;charset=utf-8'})),link=element('a');
    link.href=url;link.download=`${state.mode==='npp'?'npp':`ppr-${state.catch_basis}-${state.mode}${state.mode==='ratio'?'-'+state.npp_scope:''}${result.normalized?'-relative':''}`}-${state.set}-${state.from}-${state.to}.${format}`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  $('downloadCSV').addEventListener('click',()=>download('csv'));$('downloadJSON').addEventListener('click',()=>download('json'));
  new ResizeObserver(()=>{if(result)draw();}).observe($('plotWrap'));
  const groupDialog=groupStore?PPRGroupDialog.create({units:db.units,store:groupStore,
    getContext:()=>({...state,year:result?.points[focus]?.year??db.years[focus],method:state.methods[0]||'simple trophic chain'}),
    onChange:()=>{state.group_selections=groupStore.data.selections;Object.assign(state.models,groupStore.data.models);update();}
  }):null;
  if(groupDialog){
    $('openGroupFilter').addEventListener('click',()=>groupDialog.open(state.units.length===1?state.units[0]:undefined));
    groupStore.subscribe(()=>{state.group_selections=groupStore.data.selections;Object.assign(state.models,groupStore.data.models);update();groupDialog.refresh();});
  }
  update();
})();
