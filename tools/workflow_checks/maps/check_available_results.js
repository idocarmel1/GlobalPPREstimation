const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const pages=JSON.parse(fs.readFileSync(0,'utf8'));
function engine(page,end){
  const start=page.indexOf('/* Shared annual denominator lookup.'),context={};
  vm.createContext(context);vm.runInContext(page.slice(start,page.indexOf(end,start)),context);
  return context;
}
const trends=engine(pages['trends.html'],'</script>'),map=engine(pages['index.html'],'/* Rank the full chosen geography;');
const series=trends.PPRTimeSeries,metrics=vm.runInContext('PPRMetrics',map);
const copy=value=>JSON.parse(JSON.stringify(value));
const rec=ppr=>({status:'ok',ppr,catch:[5,5],covered_catch:[5,5]});
const unit=(id,a,b)=>({name:id,default_model:'m',models:[{id:'m',verified:true,scopes:{all:{methods:{EwE:rec(a),new_TE_EEfix:rec(b)}}}}],simple:rec([90,90]),npp:{npp:[100,100]}});
const db={years:[2018,2019],ppr_methods:[{id:'EwE',kind:'model',scopes:['all']},{id:'new_TE_EEfix',kind:'model',scopes:['all']}],npp_methods:[{id:'npp'}],units:{A:unit('A',[90,180],[180,360]),B:unit('B',[270,360],[null,90])},global_npp:{id:'fixed',unit_ids:['A','B','C'],values:[1000,2000]}};
const state={units:['A','B'],methods:['EwE'],scope:'all',mode:'ppr',catch_basis:'landings',unidentified:'method'};
let out=series.compare(db,state);
assert.deepEqual(copy(out.series[0].points.map(p=>p.value)),[40,60]);
const ew=copy(out.series[0].points.map(p=>p.value));
out=series.compare(db,{...state,methods:['EwE','new_TE_EEfix']});
assert.deepEqual(copy(out.series[0].points.map(p=>p.value)),ew,'Adding a partially available method must not shrink the EwE curve');
assert.deepEqual(copy(out.series[1].points.map(p=>p.value)),[20,50],'Every method sums its available ecosystem-year results');
assert.deepEqual(copy(out.series[1].points[0].included_ids),['A']);
assert.equal(out.series[1].points[0].missing_result_count,1);
assert.equal(out.series[1].points[0].excluded[0].id,'B');
assert.match(out.series[1].points[0].excluded[0].reason,/PPR/);
assert.equal(out.series[1].points[1].missing_result_count,0);
assert.deepEqual(copy(out.series[1].included),['A','B']);
assert.equal(out.series[1].excluded.length,0,'Series exclusions contain only ecosystems unavailable in every selected year');
const csv=series.comparisonToCSV(out,{...state,methods:['EwE','new_TE_EEfix']});
assert.match(csv,/missing_result_count,excluded_results/);
assert.match(csv,/PPR lacks a complete annual series/);
const csvRows=csv.trim().split('\n').map(row=>row.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/).map(cell=>cell.startsWith('"')?cell.slice(1,-1).replaceAll('""','"'):cell));
const csvObjects=csvRows.slice(1).map(row=>Object.fromEntries(csvRows[0].map((key,i)=>[key,row[i]])));
const partial=csvObjects.find(row=>row.year==='2018'&&row.ppr_method==='new_TE_EEfix');
assert.equal(partial.included_ecosystems,'1');assert.equal(partial.included_ids,'A');assert.equal(partial.missing_result_count,'1');
assert.equal(JSON.parse(partial.excluded_results)[0].id,'B','CSV identifies the missing ecosystem in that method/year');
// A gap must remain local to that ecosystem-year, including single-method views.
out=series.compare(db,{...state,units:['B'],methods:['new_TE_EEfix']});
assert.deepEqual(copy(out.points.map(p=>p.value)),[null,10],'A missing first year cannot exclude a region from its available later year');
assert.deepEqual(copy(out.points.map(p=>p.included_ids)),[[],['B']]);
assert.deepEqual(copy(out.points.map(p=>p.missing_result_count)),[1,0]);
assert.deepEqual(copy(out.included),['B']);
// MC quality failures apply to that curve, not independently selected methods.
const mcDb=copy(db);mcDb.ppr_methods.push({id:'MC_new_GE',kind:'model',scopes:['all']});
for(const id of ['A','B']){
  const selected=mcDb.units[id].models[0];
  selected.scopes.all.methods.MC_new_GE=rec([900,1800]);
  selected.mc_diagnostics={MC_new_GE:{n_samples:10,n_accepted:id==='A'?9:1}};
}
out=series.compare(mcDb,{...state,methods:['EwE','MC_new_GE']});
assert.deepEqual(copy(out.series[0].points.map(p=>p.value)),[40,60],'Selecting an MC method with a quality failure cannot change the existing deterministic curve');
assert.deepEqual(copy(out.series[1].points.map(p=>p.value)),[100,200]);
assert.deepEqual(copy(out.series[0].points.map(p=>p.included_ids)),[['A','B'],['A','B']]);
assert.equal(out.series[1].points[0].excluded[0].code,'mc_acceptance');
assert.match(out.series[1].points[0].excluded[0].reason,/1 of 10 runs accepted/);
// Normalized comparisons retain the existing common-cohort interpretation.
out=series.compare(db,{...state,methods:['EwE','new_TE_EEfix'],baseline:'EwE'});
assert.deepEqual(copy(out.included),['A']);
assert.deepEqual(copy(out.series[1].points.map(p=>p.value)),[2,2]);
out=series.compare(db,{...state,methods:['EwE','new_TE_EEfix'],mode:'ratio',npp_scope:'global'});
assert.deepEqual(copy(out.series[0].points.map(p=>p.value)),[4,3]);
assert.deepEqual(copy(out.series[1].points.map(p=>p.value)),[2,2.5]);
assert.deepEqual(copy(out.series[1].points.map(p=>p.npp)),[1000,2000]);
out=series.compare(db,{...state,mode:'npp',npp:'npp'});
assert.deepEqual(copy(out.points.map(p=>p.value)),[200,200],'Independent NPP is unaffected by method coverage');

const model={id:'m',verified:true,researcher_review:{status:'Validated by researcher'},review_flags:['GE FAIL'],
  group_data:{groups:[{id:'g'}],mappings:[[[0,1]],[[0,1]],[[0,1]]]},
  scopes:{all:{methods:['new_GE'],status:{new_GE:'DIVERGED: negative source-group SPPR'},values:[[9],[-18],[null]]}}};
const source={years:[2018,2019],taxa:['a','b','missing'],catch:[[2,2],[3,3],[1,1]],full_precision_catch:[[2,2],[3,3],[1,1]],landings:[[2,2],[3,3],[1,1]],catch_basis_policy:'explicit',models:[model]};
const ps={unit_id:'A',mode:'ppr',scope:'all',method:'new_GE',year:2019,catch_basis:'landings',unidentified:'method'};
const before=JSON.stringify(source);
let value=metrics.evaluate(source,0,ps);
assert.equal(value.value,-4,'Validated retained signed taxon SPPR contributes without discarding negative values');
assert.match(value.status,/DIVERGED/);assert.equal(value.catch,5);assert.equal(value.coverage,5/6);
assert.equal(JSON.stringify(source),before,'Display must not modify saved statuses or coefficients');
model.researcher_review.status='Disqualified by researcher';assert.equal(metrics.evaluate(source,0,ps).value,null);
model.researcher_review.status='Validated by researcher';model.verified=false;assert.equal(metrics.evaluate(source,0,ps).value,null);
model.verified=true;
model.scopes.all.status.new_GE='ok';
assert.equal(metrics.evaluate(source,0,ps).value,-4,'A retained negative coefficient cannot disappear solely because its saved annual status is ok');
for(const status of ['NOT_RUN','unavailable','did not resolve for any mapped group']){
  model.scopes.all.status.new_GE=status;assert.equal(metrics.evaluate(source,0,ps).value,null,status+' must remain unavailable');
}
model.scopes.all.status.new_GE='FAIL: retained numeric diagnostic';model.scopes.all.values=[[null],[null],[null]];
assert.equal(metrics.evaluate(source,0,ps).value,null,'Researcher validation cannot generate a missing coefficient');
model.scopes.all.values=[[9],[-18],[null]];
const tm=copy(model);tm.taxon_scopes=tm.scopes;tm.scopes={all:{methods:{new_GE:{status:'FAIL: retained numeric diagnostic',ppr:[null,null],covered_catch:[null,null]}}}};
const td={years:[2018,2019],ppr_methods:[{id:'new_GE',kind:'model',scopes:['all']}],npp_methods:[],units:{A:{name:'A',default_model:'m',models:[tm],simple:rec([90,90]),group_inputs:source}}};
const ts={...state,units:['A'],method:'new_GE',methods:['new_GE']};
const unchanged=JSON.stringify(td);out=series.compare(td,ts);
assert.deepEqual(copy(out.points.map(p=>p.value)),[-4,-4],'Suppressed annual values use only retained catch times retained signed taxon coefficients');
assert.match(out.points[0].status,/FAIL/);assert.equal(out.points[0].retained_numeric_display,true);
assert.equal(JSON.stringify(td),unchanged);
assert.match(series.comparisonToCSV(out,ts),/FAIL: retained numeric diagnostic/);
tm.taxon_scopes.all.values=[[null],[null],[null]];assert.equal(series.compare(td,ts).points[0].value,null);
tm.taxon_scopes.all.values=[[9],[-18],[null]];tm.group_data.mappings=[];
assert.equal(series.compare(td,ts).points[0].value,null,'Missing allocation evidence cannot restore suppressed annual results');
// Per-year availability must not repeatedly evaluate every other year's groups.
const grouped=copy(td),gm=grouped.units.A.models[0];
gm.group_data={groups:[{id:'positive'},{id:'negative'}],methods:['new_GE'],scopes:{all:[[9],[-18]]},mappings:[[[0,1]],[[1,1]],[[1,1]]]};
gm.scopes.all.methods.new_GE={status:'FAIL: retained numeric diagnostic',ppr:[-36,-36],covered_catch:[5,5]};
let evaluatedYears=[];const actualGroupEvaluate=trends.PPRGroups.evaluate;
trends.PPRGroups.evaluate=function(...args){evaluatedYears.push(args[2].year);return actualGroupEvaluate(...args);};
out=series.compare(grouped,{...ts,group_selections:{'A::m':['positive']}});
assert.deepEqual(copy(out.points.map(p=>p.value)),[2,2]);
assert.deepEqual(evaluatedYears,[2018,2019],'Each selected ecosystem-year group result is evaluated once per comparison');
trends.PPRGroups.evaluate=actualGroupEvaluate;
// The scale's simple-chain subtotal uses the same groups and a single-year aggregate.
const simpleGrouped=copy(grouped),simpleModel=simpleGrouped.units.A.models[0];
simpleGrouped.ppr_methods.push({id:'simple trophic chain',kind:'taxon',scopes:['all']});
simpleModel.taxon_scopes.all.methods.push('simple trophic chain');
simpleModel.taxon_scopes.all.status['simple trophic chain']='ok';
simpleModel.taxon_scopes.all.values=[[9,18],[-18,27],[null,null]];
simpleGrouped.units.A.group_inputs.simple_sppr=[18,27,null];
const simpleState={...ts,method:'simple trophic chain',methods:['simple trophic chain'],scope:'all',mode:'ppr',years:[2019],group_selections:{'A::m':['positive']}};
out=series.aggregate(simpleGrouped,simpleState);
assert.equal(out.points[0].value,4,'Simple chain includes 2 tonnes in the selected group × retained coefficient 18 / 9');
assert.equal(out.points[0].catch,2);assert.equal(out.points[0].covered_catch,2);assert.equal(out.points[0].coverage,1);
out=series.aggregate(simpleGrouped,{...simpleState,group_selections:{'A::m':['negative']}});
assert.equal(out.points[0].value,9,'Changing the selected group changes the scale subtotal to 3 × 27 / 9');
assert.equal(out.points[0].catch,4);assert.equal(out.points[0].covered_catch,3);assert.equal(out.points[0].coverage,.75);
simpleGrouped.units.A.group_inputs.landings[0][1]=null;
assert.equal(series.aggregate(simpleGrouped,simpleState).points[0].value,null,'Missing catch in the selected group cannot become a zero subtotal');
assert.equal(series.aggregate(simpleGrouped,{...simpleState,years:[2018]}).points[0].value,4,'A later missing catch does not invalidate the selected earlier year');
// Existing MC acceptance remains an independent quality gate even after validation.
const mc=copy(model);mc.scopes.all.methods=['MC_new_GE'];mc.scopes.all.status={MC_new_GE:'FAIL: retained numeric diagnostic'};mc.mc_diagnostics={MC_new_GE:{n_samples:10,n_accepted:1}};
assert.equal(metrics.evaluate({...source,models:[mc]},0,{...ps,method:'MC_new_GE'}).value,null);
console.log('Available-results checks passed: per-method/year cohorts, fixed NPP, normalized comparison, retained signed coefficients, missingness and diagnostics.');
