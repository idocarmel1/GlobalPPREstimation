const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2],'utf8');
assert(html.includes('<option value="validated">Validated by researcher</option>'),'Researcher validation display option is available');
function section(start,end){
  const a=html.indexOf(start),b=html.indexOf(end,a);
  assert(a>=0&&b>a,`Missing map section: ${start}`);
  return html.slice(a,b);
}
const nodes={};
const node=id=>nodes[id]||=({value:'all',hidden:false,listeners:{},addEventListener(event,fn){this.listeners[event]=fn;}});
node('search').value='';
node('rankFilter').value='validated';
const review={status:'Validated by researcher',researcher_name:'Researcher'};
const network={units:{
  approved:{default_model:0,models:[{researcher_review:review},{verified:true}]},
  alternative:{default_model:0,models:[{verified:true},{researcher_review:review},{researcher_review:{status:'Disqualified by researcher'}}]},
  available:{default_model:0,models:[{verified:true}]},
  outside:{default_model:0,models:[{researcher_review:review}]}
}};
const regions=['approved','alternative','available','missing','outside'].map((unit_id,i)=>({
  unit_id,region_name:unit_id,region_type:'LME',networkResult:{value:i===0?null:10-i}
}));
const chosenModels={approved:0,alternative:0,available:0,outside:0};
const rankState={set:'atlas',limit:'validated',custom:'2',basis:'metric'};
const context={console,URLSearchParams,network,regions,chosenModels,rankState,$:node,byUnit:{},
  document:{querySelector:selector=>node(selector.slice(1))},mapParams:new URLSearchParams('limit=validated'),
  DB:{year:2019},applyYear(){context.recompute();}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(require('node:path').resolve(__dirname,'../../project_core/maps/researcher_review.js'),'utf8'),context);
vm.runInContext(section('/* Rank the full chosen geography;','/* Runs after the inherited atlas'),context);
vm.runInContext(section('function regionHasDownload','function renderList()'),context);
vm.runInContext(section('const priorPassRegion=','$(\'rankSetFilter\').value'),context);
vm.runInContext(section("$('rankSetFilter').value",'const groupDialog='),context);
context.recompute=()=>context.PPRMapRanking.rank(regions,new Set(['approved','alternative','available','missing']));
context.recompute();
const visible=()=>regions.filter(context.passRegion).map(r=>r.unit_id).sort();
assert.deepEqual(visible(),['approved'],'Only the chosen researcher-reviewed model qualifies, even without a metric result');
chosenModels.alternative=1;
assert.deepEqual(visible(),['alternative','approved'],'Switching to a reviewed alternative updates eligibility');
chosenModels.approved=1;
assert.deepEqual(visible(),['alternative'],'Switching away from the reviewed model hides its ecosystem');
chosenModels.alternative=2;
assert.deepEqual(visible(),[],'A disqualified selected model never qualifies as validated');
chosenModels.alternative=1;
node('search').value='approved';
assert.deepEqual(visible(),[],'Search still intersects the validation filter');
chosenModels.approved=0;
assert.deepEqual(visible(),['approved']);
node('search').value='';node('typeFilter').value='EEZ';
assert.deepEqual(visible(),[],'Geography type still intersects the validation filter');
node('typeFilter').value='all';node('downloadFilter').value='with';
assert.deepEqual(visible(),[],'Download filter is retained');
context.byUnit.alternative=[{downloaded_file_count:1,title:'source',authors:'researcher'}];
assert.deepEqual(visible(),['alternative'],'Reviewed ecosystems with downloaded sources qualify');
node('downloadFilter').value='without';
assert.deepEqual(visible(),['approved'],'Reviewed ecosystems without downloads qualify');
node('downloadFilter').value='all';
node('rankFilter').value='all';node('rankFilter').listeners.change();
assert.deepEqual(visible(),['alternative','approved','available','missing'],'All restores the entire selected set');
node('rankFilter').value='custom';node('rankFilter').listeners.change();
assert.deepEqual(visible(),['alternative','available'],'Custom count retains its ranking behavior');
node('rankFilter').value='validated';node('rankFilter').listeners.change();
assert.equal(node('rankCustomField').hidden,true);
const stateContext={mapParams:new URLSearchParams('limit=validated')};
vm.runInNewContext(section('const rankState=','// Fixed, model-independent reference:')+'this.state=rankState;',stateContext);
assert.equal(stateContext.state.limit,'validated','Validation selection survives a saved URL');
console.log('Researcher validation filter passed: chosen models, unavailable results, set/search/type/download filters, model switching, All/custom and URL restore.');

