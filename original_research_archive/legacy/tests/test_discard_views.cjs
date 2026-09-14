const {test}=require('node:test');
const assert=require('node:assert/strict');
const map=require('../PPRAtlas/atlas/network_metrics.js');
const series=require('../PPRAtlas/atlas/time_series_metrics.js');
const bands=require('../PPRAtlas/atlas/discard_sensitivity.js');
const band={status:'assessed',min_tC:20/9,max_tC:40/9,route_ppr_tC:{SC:20/9,SM:40/9,SE:20/9},discard_fraction:.9,excluded_routes:{SR:'No source fate'},interpolated:true};
const state={year:2019,method:'m',scope:'all',mode:'ppr',catch_basis:'landings',uncertainty:true};
function mapData(){return {years:[2019],taxa:['Landed low TL','Discarded high TL'],catch_basis_policy:'three_bases',catch:[[10],[90]],full_precision_catch:[[10],[90]],landings:[[10],[0]],discards:[[0],[90]],models:[{verified:true,scopes:{all:{methods:['m'],status:{m:'ok'},values:[[2],[100]]}},discard_sensitivity:{all:{m:{method:[structuredClone(band)]}}}}]};}
test('each catch basis uses its own taxon vector, with sensitivity on landings only',()=>{
  const unit=mapData();
  assert.equal(map.evaluate(unit,0,state).value,20/9);
  assert.equal(map.evaluate(unit,0,{...state,catch_basis:'catch'}).value,9020/9);
  const discarded=map.evaluate(unit,0,{...state,catch_basis:'discards'});
  assert.equal(discarded.value,1000);assert.equal(discarded.sensitivity.hidden,true);
  assert.equal(map.evaluate(unit,0,state).sensitivity.upper,40/9);
  assert.equal(map.evaluate(unit,0,{...state,uncertainty:false}).sensitivity.hidden,true);
});
test('known zero landings are zero; missing classification and failed methods stay unavailable',()=>{
  const unit=mapData();unit.landings=[[0],[0]];
  assert.equal(map.evaluate(unit,0,state).value,0);
  delete unit.landings;assert.equal(map.evaluate(unit,0,state).value,null);
  unit.landings=[[10],[0]];unit.models[0].scopes.all.status.m='FAILED';
  assert.equal(map.evaluate(unit,0,state).value,null);
});
test('missing classification is not silently converted to a partial or zero catch vector',()=>{
  const unit=mapData();unit.landings[1][0]=null;
  assert.equal(map.evaluate(unit,0,state).value,null);
  unit.landings=[[10],[0]];unit.catch_accounting={classification_status:['missing_classification']};
  assert.equal(map.evaluate(unit,0,state).value,20/9);
  assert.equal(map.evaluate(unit,0,{...state,catch_basis:'catch'}).value,9020/9);
});
test('known selected catch remains available when another component is unknown; context is never zero-filled',()=>{
  const unit=mapData();unit.discards=[[null],[null]];
  const result=map.evaluate(unit,0,{...state,catch_basis:'catch'});
  assert.equal(result.value,9020/9);assert.equal(result.total_discards,null);
  assert.equal(map.evaluate(unit,0,state).value,20/9);
  const db=seriesData();db.units.a.simple.catch_bases.discards.catch=[null];
  const point=series.aggregate(db,{...state,units:['a']}).points[0];
  assert.equal(point.ppr,20/9);assert.equal(point.total_discards,null);
});
test('ratio endpoints use one selected NPP; missing NPP does not erase carbon endpoints',()=>{
  const unit=mapData(),s={...state,mode:'npp_ratio',npp_data:{years:[2019],values:[100]}};
  let r=map.evaluate(unit,0,s);assert.equal(r.sensitivity.upper,40/9);
  r=map.evaluate(unit,0,{...s,npp_data:{years:[2019],values:[200]}});assert.equal(r.sensitivity.upper,20/9);
  r=map.evaluate(unit,0,{...s,npp_data:{years:[2019],values:[null]}});
  assert.equal(r.value,null);assert.equal(r.sensitivity.upper,null);assert.equal(r.sensitivity.max_tC,40/9);
});
test('map CSV retains assessed carbon bounds when the selected annual NPP is missing',async()=>{
  const fs=require('node:fs'),vm=require('node:vm');
  const source=fs.readFileSync(require.resolve('../PPRAtlas/atlas/network_view.js'),'utf8');
  const body=source.slice(source.indexOf('function appendResultDownload('),source.indexOf('function appendTreatment('));
  let click,download,visible=true;
  const context={document:{createElement:()=>({addEventListener:(_event,fn)=>{click=fn;},click:()=>{}})},
    Blob,URL:{createObjectURL:blob=>{download=blob;return 'blob:test';},revokeObjectURL:()=>{}},setTimeout:()=>{},
    DB:{year:2019},metricState:{...state,mode:'npp_ratio'},PPRMetrics:map,
    showSensitivity:()=>visible,assessedSensitivity:()=>false};
  vm.createContext(context);vm.runInContext(body,context);
  const result=map.evaluate(mapData(),0,{...state,mode:'npp_ratio',npp_data:{years:[2019],values:[null]}});
  const read=async()=>{context.appendResultDownload({appendChild:()=>{}},{unit_id:'a'},{id:'test'},result);click();
    const rows=(await download.text()).trim().split('\n').map(line=>line.match(/"(?:[^"]|"")*"/g).map(cell=>cell.slice(1,-1).replaceAll('""','"')));
    return Object.fromEntries(rows[0].map((key,i)=>[key,rows[1][i]]));};
  let row=await read();
  assert.equal(row.central_value,'');assert.equal(row.sensitivity_upper,'');
  assert.equal(Number(row.sensitivity_min_tC),20/9);assert.equal(Number(row.sensitivity_max_tC),40/9);
  visible=false;row=await read();assert.equal(row.sensitivity_min_tC,'');assert.equal(row.sensitivity_max_tC,'');
});
test('aggregate uses matching named routes and never drops unsupported ecosystem bounds',()=>{
  const other={...band,route_ppr_tC:{SC:100,SM:80,SE:100},min_tC:80,max_tC:100};
  const combined=bands.combine([band,other]);
  assert.equal(combined.min_tC,80+40/9);assert.equal(combined.max_tC,100+20/9);
  assert.equal(bands.combine([band,{status:'not_assessed'}]).status,'not_assessed');
});
test('graph keeps audit downloads available when every selected year lacks NPP',()=>{
  const fs=require('node:fs'),vm=require('node:vm');
  const source=fs.readFileSync(require.resolve('../PPRAtlas/atlas/time_series_view.js'),'utf8');
  const body=source.slice(source.indexOf('  function update()'),source.indexOf('  function renderCoverage()'));
  const db=seriesData();db.years=[2019,2020];db.units.a.npp.npp=[null,100];db.sets=[];
  const nodes={};
  const context={db,state:{...state,mode:'ratio',units:['a'],methods:['m'],models:{},from:2019,to:2019,npp:'npp',npp_fill:'observed',unidentified:'method',uncertainty:'1'},
    result:null,focus:0,params:new URLSearchParams(),PPRTimeSeries:series,
    $:id=>nodes[id]??=( {} ),methodLabel:id=>id,catchBasisLabel:()=> 'Landings',taxonOnly:()=>false,nppInfo:()=>({label:'NPP'}),
    options:()=>{},renderCoverage:()=>{},draw:()=>{},saveURL:()=>{}};
  context.hasValues=()=>context.result.series.some(s=>s.points.some(p=>series.finite(p.value)));
  vm.createContext(context);vm.runInContext(body+'\nupdate();',context);
  assert.equal(nodes.emptyState.hidden,false);
  assert.equal(nodes.inspectYear.disabled,true);
  assert.equal(nodes.downloadCSV.disabled,false);
  const point=context.result.points[0];
  assert.equal(point.value,null);assert.equal(point.ppr,20/9);
  assert.equal(point.sensitivity.max_tC,40/9);
  const csv=series.comparisonToCSV(context.result,context.state);
  assert.match(csv,/sensitivity_max_tC/);assert.match(csv,/Annual NPP unavailable/);
});
function seriesData(){
  const bases={catch:{status:'ok',ppr:[9020],covered_catch:[100],catch:[100]},discards:{status:'ok',ppr:[9000],covered_catch:[90],catch:[90]}};
  const method={status:'ok',ppr:[20],covered_catch:[10],catch_bases:bases,sensitivity:[structuredClone(band)]};
  return {years:[2019],ppr_methods:[{id:'m',kind:'model',scopes:['all']}],npp_methods:[{id:'npp'}],units:{a:{name:'A',simple:{ppr:[20],catch:[10],covered_catch:[10],catch_bases:bases},models:[{id:'source',verified:true,scopes:{all:{methods:{m:method}}}}],default_model:'source',npp:{npp:[100]}}}};
}
test('map and annual graph agree on all three catch boundaries and downloads label them',()=>{
  const db=seriesData(),s={...state,units:['a'],npp:'npp'};
  for(const catch_basis of ['landings','catch','discards']){
    const opts={...s,catch_basis},r=series.aggregate(db,opts);
    assert.equal(r.points[0].ppr,map.evaluate(mapData(),0,opts).value);
    assert.equal(r.points[0].catch,{landings:10,catch:100,discards:90}[catch_basis]);
    assert.match(series.toCSV(r,opts),/catch_basis,sensitivity_visible/);
  }
});
test('invariant responses keep an explicit limitation; reference methods are not assigned zero uncertainty',()=>{
  const r=bands.display({...band,min_tC:1,max_tC:1,construction_invariant:true},state);
  assert.equal(r.construction_invariant,true);
  assert.equal(bands.display(null,state).status,'not_assessed');
});
