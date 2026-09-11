const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(require.resolve('../PPRAtlas/atlas/network_view.js'),'utf8');
const fragment=(start,end)=>source.slice(source.indexOf(start),source.indexOf(end,source.indexOf(start)));
function fixture(){
  const nodes={},downloads=[];let panel;
  class Element{
    constructor(tag){this.tagName=tag;this.children=[];this.events={};this.style={};this.innerHTML='';this.textContent='';}
    appendChild(child){this.children.push(child);return child;}
    append(...children){this.children.push(...children);}
    replaceChildren(...children){this.children=children;}
    querySelector(selector){if(selector==='select'&&this.innerHTML.includes('modelFilter'))return this.select??=new Element('select');return null;}
    addEventListener(event,callback){this.events[event]=callback;}
    click(){this.events.click?.();}
  }
  const simple={years:[2019],name:'Outside pilot',type:'EEZ',simple:{ppr:[1111.1111101],catch:[12.345678901],covered_catch:[12.345678901]},sources:{workbook:'data/EEZ_001/EEZ_001.xlsx'}};
  const state={year:2019,method:'simple trophic chain',scope:'all',mode:'ppr',catch_basis:'landings',uncertainty:'0',npp:'ens_median_tC_yr',npp_fill:'observed',unidentified:'method'};
  const context={network:{units:{},simple_units:{EEZ_001:simple}},metricState:state,chosenModels:{},DB:{year:2019,annual:{2019:{}}},
    document:{createElement:tag=>new Element(tag)},$:id=>nodes[id]??=new Element('div'),
    renderDetails:()=>{},precise:v=>String(v),pct:v=>String(v*100)+'%',catchBasisLabel:()=> 'Landings',metricName:()=> 'Landings PPR (tonnes carbon)',
    resultText:r=>r.networkResult.value===null?'Unavailable':String(r.networkResult.value)+' t C',escapeMetric:value=>String(value??''),
    showSensitivity:()=>false,assessedSensitivity:()=>false,appendSensitivity:()=>{},appendTreatment:()=>{},appendNpp:()=>{},
    isIndependentSimple:()=>['ppr','npp_ratio'].includes(state.mode)&&state.method==='simple trophic chain',
    nppData:()=>({years:[2019],values:[10000]}),PPRMetrics:{finite:v=>typeof v==='number'&&Number.isFinite(v)},
    URLSearchParams,Blob,URL:{createObjectURL:blob=>{downloads.push(blob);return 'blob:test';},revokeObjectURL:()=>{}},setTimeout:()=>{},
    location:{search:'',hash:''},history:{replaceState:()=>{}},
    selectedId:null,colorExtent:[0,1],rankState:{set:'all',limit:'all',custom:'100'},curatedIds:new Set(),PPRMapRanking:require('../PPRAtlas/atlas/map_ranking.js'),regionGroup:{clearLayers:()=>{}},markerGroup:{clearLayers:()=>{}},addRegion:()=>{},updateLegend:()=>{},refresh:()=>{}};
  nodes.details={querySelectorAll:()=>[],querySelector:()=>({replaceWith:value=>{panel=value;}})};
  vm.createContext(context);
  return {context,nodes,downloads,simple,state,get panel(){return panel;},run(start,end){vm.runInContext(fragment(start,end),context);}};
}
const descendants=node=>[node,...(node.children||[]).flatMap(descendants)];

test('fresh map opens the independent simple method and preserves explicit model-method URLs',()=>{
  const initialize=search=>{
    const context={DB:{year:2019,network:{units:{}}},URLSearchParams,location:{search}};
    vm.createContext(context);
    vm.runInContext(source.slice(0,source.indexOf('const chosenModels'))+'\nglobalThis.initialState=metricState;',context);
    return context.initialState;
  };
  assert.equal(initialize('').method,'simple trophic chain');
  assert.equal(initialize('?method=new_GE').method,'new_GE');
  assert.equal(initialize('?scope=PP').method,'new_GE');
  assert.equal(initialize('?metric=ratio').method,'new_GE');
  assert.equal(initialize('?metric=npp_ratio').method,'simple trophic chain');
});

test('map offers independent simple chain without any model inventory, only in All scope',()=>{
  const app=fixture();app.run('function availableMethods()','function populateMethods()');
  assert.ok(app.context.availableMethods().includes('simple trophic chain'));
  app.state.scope='PP';assert.ok(!app.context.availableMethods().includes('simple trophic chain'));
});

test('nonpilot simple-chain details expose their value, graph link and central workbook without a model selector',async()=>{
  const app=fixture();app.run('function appendResultDownload(','function appendTreatment(');
  app.run('const originalDetails=renderDetails;','function updateLegend()');
  app.context.renderDetails({unit_id:'EEZ_001',networkResult:{value:123.4567890123,status:'ok',total_catch:12.345678901,catch:12.345678901,coverage:1}});
  assert.match(app.panel.innerHTML,/123.4567890123/);assert.doesNotMatch(app.panel.innerHTML,/modelFilter|No article is selected/);
  const children=descendants(app.panel),workbook=children.find(node=>node.href?.includes('EEZ_001.xlsx'));
  assert.ok(workbook);assert.ok(children.some(node=>node.href?.includes('trends.html?')&&node.href.includes('simple+trophic+chain')));
  const button=children.find(node=>node.textContent==='Download current estimate CSV');assert.ok(button);button.click();
  const csv=await app.downloads[0].text();assert.match(csv,/123.4567890123/);assert.match(csv,/12.345678901/);
  assert.match(csv,/data\/EEZ_001\/EEZ_001.xlsx/);
});

test('map year update passes independent data and reports catalog-sized availability',()=>{
  const app=fixture();let received;
  const region={unit_id:'EEZ_001'},other={unit_id:'EEZ_002'};app.context.regions=[region,other];
  app.context.PPRMetrics.evaluate=(_unit,_model,state)=>{if(state.simple_unit)received=state.simple_unit;return {value:state.simple_unit?100:null,status:state.simple_unit?'ok':'No catch',total_catch:10};};
  app.run('function applyYear(year) {','populateMethods();');app.context.applyYear(2019);
  assert.equal(received,app.simple);assert.equal(region.networkResult.value,100);
  assert.match(app.nodes.yearTotal.textContent,/1 of 2/);assert.doesNotMatch(app.nodes.yearTotal.textContent,/10 pilot/);
});

test('finite independent results color nonpilot regions',()=>{
  const app=fixture();app.context.mix=()=> '#colored';app.context.pprColor=()=>{};app.context.baseRegionStyle=()=>{};
  app.nodes.colorRegionsByPpr={checked:true};app.context.colorExtent=[1,100];
  app.run('pprColor = function(r) {','addRegion = function(r) {');
  const region={unit_id:'EEZ_001',networkResult:{value:50},cumulative_before_share:.5};
  assert.equal(app.context.pprColor(region),'#colored');assert.equal(app.context.baseRegionStyle(region).fillColor,'#colored');
});

test('display count uses current ensemble ranks and retains inherited search filtering',()=>{
  const app=fixture(),select={value:'25'};app.nodes.rankFilter=select;
  app.context.rankState={set:'atlas',limit:'25',custom:'100'};
  app.context.passRegion=r=>select.value==='all'&&r.region_type==='EEZ';
  app.run('const priorPassRegion=passRegion;',"$('rankSetFilter').value=");
  assert.equal(app.context.passRegion({inRankingSet:true,rank_position:1,region_type:'EEZ'}),true);
  assert.equal(select.value,'25');
  assert.equal(app.context.passRegion({inRankingSet:false,rank_position:1,region_type:'EEZ'}),false);
  assert.equal(app.context.passRegion({inRankingSet:true,rank_position:26,region_type:'EEZ'}),false);
  assert.equal(app.context.passRegion({inRankingSet:true,rank_position:1,region_type:'LME'}),false);
  app.context.rankState.limit='all';
  assert.equal(app.context.passRegion({inRankingSet:true,rank_position:null,region_type:'EEZ'}),true);
});

test('production palettes pass through yellow and preserve the method-ratio palette',()=>{
  const app=fixture();app.context.pprColor=()=>{};app.context.baseRegionStyle=()=>{};
  app.context.mix=(from,to,t)=>'#'+[1,3,5].map(i=>Math.round(parseInt(from.slice(i,i+2),16)*(1-t)+parseInt(to.slice(i,i+2),16)*t).toString(16).padStart(2,'0')).join('');
  app.run('pprColor = function(r) {','addRegion = function(r) {');
  const r={networkResult:{value:50},cumulative_before_share:0};
  assert.equal(app.context.pprColor(r),'#d73027');
  r.cumulative_before_share=.5;assert.equal(app.context.pprColor(r),'#fee08b');
  app.state.mode='npp';assert.equal(app.context.pprColor(r),'#fee08b');
  r.cumulative_before_share=0;assert.equal(app.context.pprColor(r),'#1a9850');
  r.networkResult.value=0;assert.equal(app.context.pprColor(r),'#d73027');
  app.state.mode='npp_ratio';app.context.colorExtent=[0,99];
  r.networkResult.value=9;assert.equal(app.context.pprColor(r),'#fee08b');
  r.networkResult.value=0;assert.equal(app.context.pprColor(r),'#1a9850');
  r.networkResult.value=99;assert.equal(app.context.pprColor(r),'#d73027');
  app.state.mode='ratio';
  r.networkResult.value=1;assert.equal(app.context.pprColor(r),'#f7fafb');
  r.networkResult.value=.25;assert.equal(app.context.pprColor(r),'#3278a1');
  r.networkResult.value=4;assert.equal(app.context.pprColor(r),'#b64b3a');
  r.networkResult.value=null;assert.equal(app.context.pprColor(r),'#b7c4ca');
});

test('NPP details display production without a selected Ecopath model',async()=>{
  const app=fixture();app.state.mode='npp';
  app.run('function appendResultDownload(','function appendTreatment(');
  app.run('const originalDetails=renderDetails;','function updateLegend()');
  app.context.renderDetails({unit_id:'outside',networkResult:{value:180,status:'ok'}});
  assert.match(app.panel.innerHTML,/180/);assert.doesNotMatch(app.panel.innerHTML,/modelFilter/);
  const children=descendants(app.panel);
  assert.ok(children.some(node=>node.href?.includes('metric=npp')));
  children.find(node=>node.textContent==='Download current estimate CSV').click();
  assert.match(await app.downloads[0].text(),/t C\/yr/);
});

test('no-catch independent region details keep missing coverage and still offer its NPP and graph',()=>{
  const app=fixture();app.simple.years=[];app.simple.simple={ppr:[],catch:[],covered_catch:[]};
  app.run('function appendResultDownload(','function appendTreatment(');
  app.run('const originalDetails=renderDetails;','function updateLegend()');
  app.context.renderDetails({unit_id:'EEZ_001',networkResult:{value:null,status:'Catch data are unavailable',coverage:null,total_catch:null,catch:null}});
  assert.match(app.panel.innerHTML,/Unavailable/);assert.match(app.panel.innerHTML,/Catch data are unavailable/);
  assert.ok(!descendants(app.panel).some(node=>node.textContent.includes('of annual landings included')));
  assert.ok(descendants(app.panel).some(node=>node.href?.includes('trends.html?')));
});
