const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2]||path.join(__dirname,'../../project_core/maps/original_html_layout/index.html'),'utf8');
function section(start,end){
  const a=html.indexOf(start),b=html.indexOf(end,a);
  assert(a>=0&&b>a,`Missing map lifecycle section: ${start}`);
  return html.slice(a,b);
}
const nodes={};
const node=id=>nodes[id]||=( {value:'all',checked:false,textContent:'',innerHTML:'',hidden:false,listeners:{},
  addEventListener(event,listener){this.listeners[event]=listener;}} );
for(const [id,value] of Object.entries({search:'South China Sea',rankFilter:'10',typeFilter:'all',downloadFilter:'all',rankBasisFilter:'metric'}))node(id).value=value;
const model=(id,value,status='ok')=>({id,verified:true,scopes:{all:{methods:['test_method'],status:{test_method:status},values:[[value]]}}});
const unit=models=>({default_model:0,years:[2019],taxa:['fish'],catch:[[9]],models});
const chosenModels={LME_036:0};
const network={units:{LME_036:unit([model('2000s',200),model('1970s',null,'Method unavailable')])}};
for(let i=0;i<10;i++){const id='other_'+i;network.units[id]=unit([model(id,100-i)]);chosenModels[id]=0;}
const regions=Object.keys(network.units).map(unit_id=>({unit_id,region_name:unit_id==='LME_036'?'South China Sea':unit_id,region_type:'LME'}));
const regionById=Object.fromEntries(regions.map(r=>[r.unit_id,r]));
const group={clearLayers(){}};
const context={console,URLSearchParams,
  PPRMetrics:require('../../project_core/maps/original_html_layout/calculation_modules/network_metrics.js'),
  document:{querySelector:selector=>node(selector.slice(1))},$:node,regions,regionById,network,chosenModels,byUnit:{},articles:[],
  selectedId:'LME_036',regionGroup:group,markerGroup:group,articleGroup:group,regionLayers:{},regionMarkers:{},articleLayers:{},
  DB:{year:2019,annual:{2019:{}}},metricState:{mode:'ppr',method:'test_method',scope:'all',catch_basis:'catch',unidentified:'method'},
  rankState:{set:'all',basis:'metric',limit:'10',custom:'10'},curatedIds:new Set(),referencePpr2019:{},groupStore:null,
  location:{search:'',hash:''},history:{replaceState(){}},nppData:()=>null,isIndependentSimple:()=>false,
  addRegion(){},updateLegend(){},
  // The renderer is deliberately a fixture: exercise the production refresh and
  // recalculation lifecycle without coupling this test to article-card markup.
  renderDetails(r){node('details').innerHTML='<select id="modelFilter"></select>';node('details').result=r.networkResult;},
  renderList(){node('regionList').visible=regions.filter(context.passRegion).map(r=>r.unit_id);}
};
vm.createContext(context);
vm.runInContext(section('/* Rank the full chosen geography;','/* Runs after the inherited atlas'),context);
vm.runInContext(section('function regionHasDownload','function renderList()'),context);
vm.runInContext(section('const priorPassRegion=','$(\'rankSetFilter\').value'),context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../../project_core/maps/researcher_review.js'),'utf8'),context);
vm.runInContext(section('function applyYear(','populateMethods();'),context);
vm.runInContext(section("$('rankSetFilter').value","const groupDialog="),context);

context.applyYear(2019);
assert.equal(context.selectedId,'LME_036');
assert.equal(node('details').result.value,200);
assert.deepEqual(node('regionList').visible,['LME_036']);

chosenModels.LME_036=1;
context.applyYear(2019);
assert.equal(regionById.LME_036.networkResult.value,null,'Failed model remains unavailable');
assert.deepEqual(node('regionList').visible,[],'Top-10 filter still excludes an unavailable result');
assert.equal(context.selectedId,'LME_036','Switching to an unavailable model must retain the selected ecosystem');
assert.match(node('details').innerHTML,/modelFilter/,'The model selector remains available for switching back');
assert.equal(node('details').result.value,null,'The open details display the new unavailable result');

chosenModels.LME_036=0;
context.applyYear(2019);
assert.equal(node('details').result.value,200,'Switching back restores the available result');
assert.deepEqual(node('regionList').visible,['LME_036']);

Object.assign(network.units.LME_036.models[1].scopes.all,{status:{test_method:'ok'},values:[[1]]});
chosenModels.LME_036=1;
context.applyYear(2019);
assert.equal(regionById.LME_036.rank_position,11);
assert.deepEqual(node('regionList').visible,[],'A finite result outside the top 10 is still filtered');
assert.equal(context.selectedId,'LME_036','A changed rank must not remove the open selector');
assert.equal(node('details').result.value,1);

node('rankFilter').listeners.change();
assert.equal(context.selectedId,null,'An explicit rank-filter change can clear an excluded selection');
assert.match(node('details').innerHTML,/Select a region/);

context.selectedId='LME_036';chosenModels.LME_036=0;context.applyYear(2019);
node('search').value='another ecosystem';context.refresh();
assert.equal(context.selectedId,null,'An explicit search filter still clears a nonmatching selection');
console.log('Map model-switch checks passed: unavailable and rank-excluded models retain details; switching back and explicit filters work.');

