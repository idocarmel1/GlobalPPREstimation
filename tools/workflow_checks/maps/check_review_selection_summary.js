/* Selected trend ecosystems must not inherit captions from saved other models. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.resolve(__dirname,'../../project_core/maps/researcher_review.js'),'utf8');
const units={
  reviewed:{default_model:0,models:[{id:'r',display_ppr_excluded_group_ids:['g1','g2','g3','g4','g5','g6']},{id:'plain'}]},
  pending:{default_model:'p',models:[{id:'p'}]}
};
const settings={models:{reviewed:'r',pending:'p'},selections:{'reviewed::r':['g0']}};
const original=JSON.stringify({units,settings}),ctx={};vm.createContext(ctx);vm.runInContext(source,ctx);
const summary=vm.runInContext('PPRResearcherReview.selectionSummary',ctx);
assert.equal(summary(units,settings,['pending']),'All model groups included','Unselected researcher exclusions and manual selections do not describe the trend');
assert.equal(summary(units,settings,['reviewed']),'6 groups excluded from displayed PPR by researcher · 1 models with user selections');
assert.equal(summary(units,settings,['reviewed','pending']),'6 groups excluded from displayed PPR by researcher · 1 models with user selections');
assert.equal(summary(units,settings),'6 groups excluded from displayed PPR by researcher · 1 models with user selections','Map keeps its complete context');
assert.equal(summary(units,settings,[]),'All model groups included');
assert.equal(summary(units,{...settings,models:{...settings.models,reviewed:'plain'}},['reviewed']),'All model groups included','Inactive model preferences do not describe the selected model');
assert.equal(summary(units,settings,['unknown']),'All model groups included');
assert.equal(JSON.stringify({units,settings}),original,'Captions must preserve saved preferences and model evidence');
for(const [index,filename] of process.argv.slice(2).entries()){
  const text=fs.readFileSync(filename,'utf8');
  const expression=text.match(/textContent=(PPRResearcherReview\.selectionSummary\([^;]+\));/)[1];
  const page={db:{units},groupStore:{data:settings},state:{units:['pending']}};
  if(index===0)page.network={units};
  vm.createContext(page);vm.runInContext(source,page);
  assert.equal(vm.runInContext(expression,page),index===0?'6 groups excluded from displayed PPR by researcher · 1 models with user selections':'All model groups included',filename+' overlay uses the displayed ecosystem context');
  if(index!==0){page.state.units=['reviewed'];assert.equal(vm.runInContext(expression,page),'6 groups excluded from displayed PPR by researcher · 1 models with user selections');}
}
assert.equal(JSON.stringify({units,settings}),original,'Overlay must preserve saved preferences');
console.log('Selection captions passed: selected trend units/models, both units, empty/unknown selections, full map context, generated overlays, unchanged preferences.');

