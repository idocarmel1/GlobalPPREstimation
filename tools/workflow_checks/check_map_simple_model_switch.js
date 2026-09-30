const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2]||path.join(__dirname,'../original_html_layout/index.html'),'utf8');
const start=html.indexOf('const originalDetails=renderDetails;'),end=html.indexOf('function updateLegend()',start);
assert(start>=0&&end>start,'Map detail renderer is available');

// Minimal DOM boundary: the production renderer owns the selector markup,
// options and change listener. Calculation and group selection use real code.
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.style={};this.textContent='';}
  set innerHTML(value){this.html=value;this.children=[];this.select=/<select id="modelFilter">/.test(value)?new Element('select'):null;}
  get innerHTML(){return this.html||'';}
  appendChild(child){this.children.push(child);if(child.selected)this.value=String(child.value);return child;}
  addEventListener(event,listener){this.listeners[event]=listener;}
  querySelector(selector){return selector==='select'?this.select:null;}
  querySelectorAll(){return [];}
}
const details=new Element('details');
details.querySelector=selector=>selector==='.metric-grid'?{replaceWith(panel){details.panel=panel;}}:null;
const method='simple trophic chain';
const model=id=>({id,verified:true,review_flags:['model-specific review flag'],group_data:{
  groups:[{id:'fish',name:'Fish'},{id:'producer',name:'Producer'}],mappings:[[[0,1]]],methods:[method]},
  scopes:{all:{methods:[method],status:{[method]:'ok'},values:[[100]]}}});
const selectedModels=[model('1970s'),model('2000s')];
const modelUnit={years:[2019],taxa:['fish'],catch:[[9]],simple_sppr:[100],models:selectedModels};
const simpleUnit={years:[2019],simple:{catch_bases:{catch:{status:'ok',ppr:[900],catch:[9],covered_catch:[9]}}}};
const selections={'LME_036::2000s':['fish']};
const context={console,URLSearchParams,
  document:{createElement:tag=>new Element(tag)},$:()=>details,renderDetails(){},
  PPRMetrics:require('../original_html_layout/calculation_modules/network_metrics.js'),
  network:{units:{LME_036:modelUnit},simple_units:{LME_036:simpleUnit}},chosenModels:{LME_036:1},
  metricState:{mode:'ppr',method,scope:'all',year:2019,catch_basis:'catch',unidentified:'method',group_selections:selections},DB:{year:2019},
  isIndependentSimple:()=>true,resultText:r=>String(r.networkResult.value),metricName:()=>method,escapeMetric:String,
  pct:String,precise:String,catchBasisLabel:()=> 'All catch',
  appendNpp(){},appendTreatment(){},appendSensitivity(){},
  appendResultDownload(panel,r,model){panel.downloadModel=model;}
};
const region={unit_id:'LME_036'};
context.applyYear=year=>{
  region.networkResult=context.PPRMetrics.evaluate(context.network.units[region.unit_id],context.chosenModels[region.unit_id],
    {...context.metricState,year,unit_id:region.unit_id,simple_unit:context.network.simple_units[region.unit_id]});
  context.renderDetails(region);
};
vm.createContext(context);vm.runInContext(html.slice(start,end),context);
const notes=()=>details.panel.children.map(e=>e.textContent).join('\n');
const selector=()=>details.panel.querySelector('select');
const switchModel=value=>{const select=selector();assert(select,'The model selector remains available');select.value=String(value);select.listeners.change();};

context.applyYear(2019);
assert.equal(region.networkResult.value,100,'Excluding the zero-catch producer keeps the total');
assert.equal(region.networkResult.group_selection.active,true);
assert.equal(selector().value,'1');
assert.match(notes(),/Selected groups use this model/);
switchModel(0);
assert.equal(region.networkResult.value,100,'No subset uses the independent simple-chain total');
assert.equal(region.networkResult.independent_simple,true);
assert(selector(),'Switching to a model without a group subset must keep the model selector');
assert.equal(selector().value,'0');
assert.equal(selector().children.length,2);
assert.match(notes(),/does not require an extracted article or Ecopath model/);
assert.doesNotMatch(notes(),/model-specific review flag/,'Independent calculations do not inherit model diagnosis flags');
assert.equal(details.panel.downloadModel,null,'Independent downloads have no computational model');
switchModel(1);
assert.equal(region.networkResult.value,100);
assert.equal(region.networkResult.group_selection.active,true,'Switching back restores the saved model group subset');
assert.deepEqual(region.networkResult.group_selection.ids,['fish']);
assert.equal(details.panel.downloadModel.id,'2000s');

// With neither model restricted, both choices retain the independent result.
delete selections['LME_036::2000s'];context.applyYear(2019);switchModel(0);switchModel(1);
assert.equal(region.networkResult.value,100);assert.equal(region.networkResult.independent_simple,true);
assert.equal(selector().value,'1');

// Ecosystems without an Ecopath model still show their simple-chain result.
delete context.network.units.LME_036;context.applyYear(2019);
assert.equal(region.networkResult.value,100);assert.equal(selector(),null);
assert.match(notes(),/does not require an extracted article or Ecopath model/);
console.log('Simple-chain model-switch checks passed: selector survives independent calculation; saved subsets and no-model ecosystems work.');
