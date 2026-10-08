const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const dir=require('node:path').resolve(__dirname,'../../project_core/maps/original_html_layout/calculation_modules');
let groups=require(dir+'/group_metrics.js'),metrics=require(dir+'/network_metrics.js'),trends=require(dir+'/time_series_metrics.js');
if(process.argv[2]){
  const map=fs.readFileSync(process.argv[2],'utf8'),ctx={};vm.createContext(ctx);
  vm.runInContext(map.slice(map.indexOf('/* Shared annual denominator lookup.'),map.indexOf('/* Rank the full chosen geography;')),ctx);
  groups=ctx.PPRGroups;metrics=vm.runInContext('PPRMetrics',ctx);
  const trend=fs.readFileSync(process.argv[3],'utf8'),tc={};vm.createContext(tc);
  const start=trend.indexOf('/* Shared annual denominator lookup.');vm.runInContext(trend.slice(start,trend.indexOf('</script>',start)),tc);trends=tc.PPRTimeSeries;
}
const model={id:'m',verified:true,display_ppr_excluded_group_ids:['Seabirds'],
  health:{GE:{b:.004,rho_living:.32,status:'WARN'}},
  group_data:{groups:[{id:'Fish',name:'Fish'},{id:'Seabirds',name:'Seabirds'}],methods:['new_GE'],
    scopes:{all:[[9],[90]]},mappings:[[[0,.75],[1,.25]],[[1,1]]]},
  scopes:{all:{methods:['new_GE','simple trophic chain'],status:{new_GE:'ok','simple trophic chain':'ok'},values:[[29.25,18],[90,27]]}}};
const unit={years:[2019],taxa:['split','bird'],models:[model],simple_sppr:[18,27],catch_basis_policy:'explicit',
  catch:[[4],[2]],full_precision_catch:[[4],[2]],landings:[[4],[2]],discards:[[1],[.5]],
  unidentified:{taxa:[{name:'bird',simple_sppr:27}]}};
const state={unit_id:'U',mode:'ppr',scope:'all',year:2019,method:'new_GE',catch_basis:'landings',unidentified:'method'};
assert.equal(groups.selection(model).count,1,'Mandatory exclusions apply with no saved browser selection');
assert.equal(groups.selection(model,['Fish','Seabirds']).count,process.argv[2]?2:1,'Current pages honor explicit inclusion of researcher-excluded groups');
const before=metrics.evaluate(unit,0,{...state,group_selections:{'U::m':['Fish','Seabirds']}});
assert.equal(before.value,process.argv[2]?33:3,'Explicit full selection restores original weighted PPR, carbon once');
assert.equal(before.total_catch,6,'Researcher exclusion leaves catch denominator unchanged');
assert.equal(before.catch,6,'Researcher exclusion leaves covered catch unchanged');
assert.equal(before.coverage,1,'Researcher exclusion leaves original catch coverage unchanged');
assert.equal(before.unidentified_catch,2,'Researcher exclusion leaves unidentified catch unchanged');
assert.equal(before.total_discards,1.5,'Researcher exclusion leaves discard totals unchanged');
assert.equal(metrics.evaluate(unit,0,{...state,method:'simple trophic chain',simple_unit:{years:[2019],simple:{status:'ok',ppr:[126],catch:[6],covered_catch:[6]}}}).value,6,'Simple chain uses retained original allocation shares');
assert.equal(metrics.evaluate(unit,0,{...state,mode:'b',te:'GE'}).value,.004,'Diagnostic b is unchanged');
assert.equal(metrics.evaluate(unit,0,{...state,mode:'rho_living',te:'GE'}).value,.32,'Diagnostic rho is unchanged');
assert.equal(metrics.evaluate(unit,0,{...state,mode:'npp',npp_data:{years:[2019],values:[100]}}).value,100,'NPP is unchanged');
assert.equal(metrics.evaluate(unit,0,{...state,mode:'npp_ratio',npp_data:{years:[2019],values:[100]}}).value,3,'PPR/NPP uses filtered PPR and unchanged NPP');
assert.equal(metrics.evaluate(unit,0,{...state,group_selections:{'U::m':['Fish']}}).total_catch,process.argv[2]?3:6,'An explicit user subset retains its original catch allocation shares');
if(process.argv[2]){
  assert.equal(groups.evaluate(unit,model,state,['Seabirds']).value,30,'User may include only a researcher-excluded group');
  assert.equal(groups.evaluate(unit,model,state,[]).value,0,'Clear all excludes every group');
  assert.equal(groups.evaluate(unit,model,state).total_catch,6,'Default review policy preserves the catch denominator');
  assert.equal(groups.rows(unit,model,{...state,method:'new_GE'})[1].ppr,30,'Group rows describe the group before selection');
  assert.deepEqual(model.display_ppr_excluded_group_ids,['Seabirds'],'User overrides preserve signed exclusion evidence');
}
const plain=structuredClone(model);delete plain.display_ppr_excluded_group_ids;
assert.equal(metrics.evaluate({...unit,models:[plain]},0,state).value,33,'Unreviewed model behavior is unchanged');
const annual={status:'ok',ppr:[297],catch:[6],covered_catch:[6]};
const tm=structuredClone(model);tm.taxon_scopes=tm.scopes;tm.scopes={all:{methods:{new_GE:annual}}};
const db={years:[2019],ppr_methods:[{id:'new_GE',kind:'model',scopes:['all']}],npp_methods:[],units:{U:{...unit,name:'U',default_model:'m',models:[tm],group_inputs:unit,simple:annual}}};
const out=trends.aggregate(db,{...state,units:['U']});assert.equal(out.points[0].value,3,'Trends share the display-only exclusions');assert.equal(out.points[0].catch,6);assert.equal(out.points[0].coverage,1);
if(process.argv[2]){
  model.scopes.all.status.new_GE='provisional: researcher display retains WARN';
  const preview=metrics.evaluate(unit,0,state);assert.equal(preview.value,3,'Mandatory exclusions retain explicitly authorized provisional availability');assert.match(preview.status,/provisional:/);
}
console.log('Researcher review filtering passed: signed defaults, explicit user overrides on current pages, original split weights, catch/coverage/NPP/diagnostics, simple chain, map/trends.');

