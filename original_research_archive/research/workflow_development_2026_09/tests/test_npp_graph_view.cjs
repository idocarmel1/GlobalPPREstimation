const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(require.resolve('../PPRAtlas/atlas/time_series_view.js'),'utf8');
const html=fs.readFileSync(require.resolve('../PPRAtlas/atlas/time_series.html'),'utf8');

// Run the real view and its event handlers against a minimal DOM. Numerical
// aggregation has separate tests; this fixture exercises control/state wiring.
function page(query='',pointOverride={},actualMetrics=false,configureDB=()=>{}) {
  const nodes={},downloads=[];
  class Element {
    constructor(tag='div'){this.tagName=tag;this.children=[];this.events={};this.style={};this.value='';this.textContent='';this.hidden=false;this.disabled=false;}
    set id(value){this._id=value;nodes[value]=this;}
    get id(){return this._id;}
    append(...children){this.children.push(...children);}
    appendChild(child){this.append(child);return child;}
    replaceChildren(...children){this.children=children;}
    setAttribute(key,value){this[key]=String(value);if(key==='id')nodes[value]=this;}
    addEventListener(name,callback){this.events[name]=callback;}
    getBoundingClientRect(){return {width:900,height:400,left:0};}
    click(){this.events.click?.({target:this});}
    showModal(){this.open=true;}
    close(){this.open=false;}
    focus(){}
  }
  for(const [,id]of html.matchAll(/id="([^"]+)"/g))nodes[id]=new Element();
  const reference={id:'atlas_lme_high_seas',label:'Atlas LME + High Seas reference',unit_ids:['a','b','c'],
    ensemble_convention:'Median of complete global model totals',geography:'Fixed represented LME and High Seas geography; not total world ocean',
    overlap_policy:'EEZs excluded',source:'annual_npp.csv',values:[10000],metadata:{2019:{status:'complete',model_count:5,model_names:['A','B','C','D','E'],missing_ids:[]}}};
  const db={years:[2019],sets:[{id:'global',label:'Global LME + High Seas',units:['a','b']}],
    ppr_methods:[{id:'m',label:'Model method',kind:'model',scopes:['all','PP']},{id:'other',label:'Other method',kind:'model',scopes:['all']}],
    npp_methods:[{id:'ens_median_tC_yr',label:'Ensemble median'},{id:'vgpm',label:'VGPM'}],global_npp:reference,
    units:Object.fromEntries(['a','b','c'].map(id=>[id,{name:id.toUpperCase(),type:'LME',models:[],npp:{vgpm:[1000]},simple:{ppr:[],catch:[]}}]))};
  configureDB(db);
  let url='',lastState;
  const metrics={finite:value=>typeof value==='number'&&Number.isFinite(value),
    compare(_db,state){lastState=structuredClone(state);const nppOnly=state.mode==='npp',global=state.npp_scope==='global'&&!nppOnly;
      const point={year:2019,value:nppOnly?4000:global?4:10,ppr:nppOnly?null:400,npp:global?10000:4000,npp_denominator:global?10000:4000,
        npp_scope:global?'global':'selected',npp_reference_id:global?reference.id:null,npp_ensemble_convention:reference.ensemble_convention,
        npp_reference_ids:global?reference.unit_ids:['a','b'],npp_available_ids:global?reference.unit_ids:['a','b'],npp_missing_ids:[],
        npp_reference_metadata:global?reference.metadata[2019]:null,npp_source_years:{a:2019,b:2019},npp_substituted_ids:[],
        npp_provenance:{a:{n_models:5,available_models:['A','B','C','D','E']},b:{n_models:5}},coverage:1,catch:200,covered_catch:200,...pointOverride};
      const result={mode:state.mode,npp_scope:global?'global':'selected',npp_reference:global?reference:null,npp_method:state.npp,
        annual_npp:true,normalized:!nppOnly&&Boolean(state.baseline),included:[...state.units],excluded:[],selected:state.units.length,points:[point]};
      result.series=(nppOnly?['npp']:state.methods).map(method=>({method,points:[point],excluded:[]}));return result;},
    comparisonToCSV:(result,state)=>`mode,npp_scope,npp_denominator\n${state.mode},${state.npp_scope},${result.points[0].npp}`,
    comparisonToJSON:(result,state)=>JSON.stringify({state,points:result.points})};
  const context={SERIES_DB:db,PPRTimeSeries:actualMetrics?require('../PPRAtlas/atlas/time_series_metrics.js'):metrics,document:{getElementById:id=>nodes[id]||null,createElement:tag=>new Element(tag),createElementNS:(_ns,tag)=>new Element(tag),createTextNode:text=>({textContent:text})},
    location:{search:query},history:{replaceState:(_a,_b,value)=>{url=value;}},URLSearchParams,Blob,
    URL:{createObjectURL:blob=>{downloads.push(blob);return 'blob:test';},revokeObjectURL:()=>{}},
    setTimeout:()=>{},ResizeObserver:class {observe(){}},console};
  vm.createContext(context);vm.runInContext(source,context);
  return {nodes,downloads,db,get state(){return lastState;},get params(){return new URLSearchParams(url.slice(1));},
    change(id,value){nodes[id].value=value;nodes[id].events.change({target:nodes[id]});}};
}

test('NPP mode survives URL state and disables PPR controls without discarding their selections',()=>{
  const app=page('?metric=npp&methods=m,other&baseline=m&scope=PP&npp=vgpm&catch_basis=discards&uncertainty=0');
  assert.equal(app.state.mode,'npp');
  for(const id of ['pprMethod','baselineMethod','catchBasis','uncertainty','sourceScope','unidentifiedTreatment'])assert.equal(app.nodes[id].disabled,true,id);
  assert.equal(app.nodes.nppMethod.disabled,false);assert.equal(app.nodes.nppFill.disabled,false);
  assert.match(app.nodes.chartTitle.textContent,/NPP/);assert.doesNotMatch(app.nodes.chartTitle.textContent,/baseline|Discards/);
  assert.doesNotMatch(app.nodes.focusValue.textContent,/%|×/);assert.match(app.nodes.focusValue.textContent,/yr/);
  assert.equal(app.nodes.sensitivityReadout.hidden,true);assert.equal(app.nodes.unidentifiedNote.hidden,true);
  assert.equal(app.params.get('metric'),'npp');assert.equal(app.params.get('baseline'),'m');
  app.change('metric','ppr');assert.equal(app.nodes.pprMethod.disabled,false);assert.equal(app.nodes.baselineMethod.value,'m');
  assert.equal(app.nodes.catchBasis.value,'discards');assert.deepEqual(app.state.methods,['m','other']);
});

test('global denominator selector round-trips and returns the selected NPP calculation when scope changes back',()=>{
  const app=page('?metric=ratio&method=m&npp=vgpm&npp_scope=global');
  assert.equal(app.state.npp_scope,'global');assert.equal(app.nodes.nppScope.value,'global');assert.equal(app.nodes.nppMethod.disabled,true);
  assert.equal(app.nodes.nppMethod.value,'global_reference_ensemble');assert.equal(app.state.npp,'vgpm');
  assert.match(app.nodes.nppNote.textContent,/global|atlas-wide/i);assert.match(app.nodes.nppNote.textContent,/Median of complete global model totals/);
  assert.match(app.nodes.nppNote.textContent,/not total world ocean/);assert.equal(app.params.get('npp_scope'),'global');
  assert.match(app.nodes.coverage.textContent,/10,000/);
  assert.match(app.nodes.globalNPPAvailability.textContent,/5 computed NPP model total/);
  assert.equal(page('?'+app.params.toString()).nodes.nppScope.value,'global');
  app.change('nppScope','selected');assert.equal(app.nodes.nppMethod.disabled,false);assert.equal(app.nodes.nppMethod.value,'vgpm');
  assert.equal(app.params.get('npp_scope'),'selected');
});

test('JSON and CSV downloads retain the chosen measure and denominator selection',async()=>{
  const app=page('?metric=ratio&method=m&npp_scope=global');
  app.nodes.downloadJSON.click();app.nodes.downloadCSV.click();
  assert.equal(app.downloads.length,2);
  const json=JSON.parse(await app.downloads[0].text());
  assert.equal(json.state.npp_scope,'global');assert.equal(json.points[0].npp_denominator,10000);
  assert.match(await app.downloads[1].text(),/ratio,global,10000/);
});

test('NPP-only gaps retain coverage details and audit downloads',()=>{
  const app=page('?metric=npp&method=m',{value:null,npp:null,npp_available_ids:['a'],npp_missing_ids:['b']});
  assert.equal(app.nodes.emptyState.hidden,false);assert.match(app.nodes.coverage.textContent,/1 of 2 selected ecosystems/);
  assert.match(app.nodes.coverage.textContent,/Missing NPP: b/);assert.equal(app.nodes.downloadJSON.disabled,false);
  assert.equal(app.nodes.downloadCSV.disabled,false);assert.doesNotMatch(app.nodes.coverage.textContent,/catch coverage|coefficient|Unidentified/);
});

test('historical NPP substitution is visible in the inspected year and curve',()=>{
  const app=page('?metric=npp&npp_fill=earliest',{npp_estimated:true,npp_substituted_ids:['a','b'],npp_source_years:{a:1998,b:1998}});
  assert.match(app.nodes.coverage.textContent,/a from 1998, b from 1998/);
  assert.match(app.nodes.nppAvailability_a.textContent,/historical estimate using 1998/);
  function descendants(node){return [node,...(node.children||[]).flatMap(descendants)];}
  assert.ok(descendants(app.nodes.chart).some(node=>node['data-curve']==='true'&&node['data-npp-estimate']==='true'));
  assert.equal(app.params.get('npp_fill'),'earliest');
});

test('real aggregation renders and exports NPP for ecosystems with no model or catch estimates',async()=>{
  const app=page('?metric=npp&methods=m,other&baseline=m&npp=vgpm',{},true);
  assert.equal(app.nodes.emptyState.hidden,true);assert.equal(app.nodes.focusValue.textContent,'2,000 t C / yr');
  assert.equal(app.nodes.seriesLegend.hidden,true);assert.match(app.nodes.cohortSummary.textContent,/2 of 2/);
  app.nodes.downloadJSON.click();const downloaded=JSON.parse(await app.downloads[0].text());
  assert.equal(downloaded.result.series.length,1);assert.equal(downloaded.result.points[0].value,2000);
  assert.equal(downloaded.result.points[0].ppr,null);assert.deepEqual(downloaded.result.included,['a','b']);
});

test('real global reference remains visible and exportable with no available PPR estimate',async()=>{
  const app=page('?metric=ratio&method=m&npp_scope=global',{},true);
  assert.equal(app.nodes.emptyState.hidden,false);assert.match(app.nodes.coverage.textContent,/10,000/);
  assert.match(app.nodes.globalNPPAvailability.textContent,/5 computed NPP model total/);
  app.nodes.downloadJSON.click();const downloaded=JSON.parse(await app.downloads[0].text());
  assert.equal(downloaded.result.points[0].value,null);assert.equal(downloaded.result.points[0].npp_denominator,10000);
  assert.equal(downloaded.result.npp_reference.ensemble_convention,app.db.global_npp.ensemble_convention);
});

test('finite global reference prominently discloses water-mask and day-weighted support limits',async()=>{
  const app=page('?metric=ratio&method=m&npp_scope=global',{},true,db=>{
    Object.assign(db.global_npp.metadata[2019],{complete:true,coverage_complete:false,coverage_limited:true,status:'coverage_limited',
      water_area_pct_of_polygon:80,coverage:{polygon_area_km2:1000,water_area_km2:800,
        central_support_pct_of_water_pixel_days:90,central_support_pct_of_polygon_pixel_days:72,excluded_far_pct_of_water_pixel_days:10}});
  });
  for(const id of ['nppNote','coverage','globalNPPAvailability']){
    assert.match(app.nodes[id].textContent,/Coverage-limited atlas reference/);
    assert.match(app.nodes[id].textContent,/80% of the reference polygon/);
    assert.match(app.nodes[id].textContent,/90% of supported water pixel-days/);
    assert.match(app.nodes[id].textContent,/72% of reference polygon pixel-days/);
  }
  assert.match(app.nodes.nppNote.textContent,/not observed world-ocean coverage/);
  app.nodes.downloadJSON.click();const downloaded=JSON.parse(await app.downloads[0].text());
  assert.equal(downloaded.result.points[0].npp_denominator,10000);
  assert.equal(downloaded.result.points[0].npp_reference_metadata.coverage_complete,false);
});

test('NPP-only explains regional median summation and overlapping selections without opening coverage',()=>{
  const app=page('?metric=npp&npp=ens_median_tC_yr');
  assert.equal(app.nodes.nppNote.hidden,false);
  assert.match(app.nodes.nppNote.textContent,/sum of regional ensemble medians/i);
  assert.match(app.nodes.nppNote.textContent,/overlap/i);
  assert.match(app.nodes.nppNote.textContent,/not an ensemble statistic of global model totals/i);
});

test('an NPP-only ecosystem does not inherit a misleading no-catch availability note',()=>{
  const catchNote='No catch series is available; annual estimates are unavailable.';
  const app=page('?metric=npp&units=HS_018&method=m&npp=vgpm',{},true,db=>{
    db.units.HS_018={name:'High Seas 18',type:'HS',models:[],simple:{ppr:[],catch:[]},
      npp:{vgpm:[24149000]},note:catchNote};
  });
  assert.equal(app.nodes.focusValue.textContent,'24,149,000 t C / yr');
  assert.doesNotMatch(app.nodes.setNote.textContent,/annual estimates are unavailable/);
  assert.match(app.nodes.setNote.textContent,/NPP/);
  app.change('metric','ppr');assert.equal(app.nodes.setNote.textContent,catchNote);
});

test('outside-coverage global gaps show their reason and a compact missing count, retaining all IDs',async()=>{
  const ids=Array.from({length:84},(_,i)=>'REGION_'+String(i+1).padStart(3,'0'));
  const reason='Annual satellite reference starts in 1998 and ends in 2019.';
  const app=page('?metric=ratio&method=m&npp_scope=global&year=1950',{},true,db=>{
    db.years=[1950];db.global_npp.unit_ids=ids;db.global_npp.values=[null];
    db.global_npp.metadata={1950:{status:'outside_source_coverage',reason,missing_ids:ids}};
  });
  assert.match(app.nodes.coverage.textContent,/Annual satellite reference starts in 1998/);
  assert.match(app.nodes.coverage.textContent,/84 ecosystems.*see Coverage and sources/i);
  assert.doesNotMatch(app.nodes.coverage.textContent,/REGION_001|REGION_084/);
  assert.equal(app.nodes.nppMissingDetails.hidden,false);assert.equal(app.nodes.nppMissingList.children.length,84);
  assert.match(app.nodes.nppMissingList.children[83].textContent,/REGION_084/);
  app.nodes.downloadJSON.click();const downloaded=JSON.parse(await app.downloads[0].text());
  assert.deepEqual(downloaded.result.points[0].npp_missing_ids,ids);
});
