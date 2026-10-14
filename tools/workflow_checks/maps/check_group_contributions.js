/* Literal catch × SPPR fixtures catch wrong rankings, dropped allocations and denominators. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const page=JSON.parse(fs.readFileSync(0,'utf8')),context={};
vm.createContext(context);
const start=page.indexOf('/* Additional trend views');
vm.runInContext(page.slice(start,page.indexOf('</script>',start)),context);
const engine=context.PPRTimeSeries,stack=context.PPRGroupContributions;
assert.ok(stack,'The production-linked page must provide group contributions');
const copy=value=>JSON.parse(JSON.stringify(value));
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);
const record=ppr=>({status:'ok',ppr,catch:[8,16],covered_catch:[8,16]});
const groups=Array.from({length:8},(_,i)=>({id:'g'+(i+1),name:'Group '+(i+1)}));
const model={id:'m',verified:true,group_data:{groups,methods:['EwE'],scopes:{all:groups.map((_,i)=>[9*(i+1)])},mappings:groups.map((_,i)=>[[i,1]])},
  taxon_scopes:{all:{methods:['EwE','simple trophic chain'],status:{EwE:'ok','simple trophic chain':'ok'},values:groups.map((_,i)=>[9*(i+1),9*(i+1)])}},
  scopes:{all:{methods:{EwE:record([324,648])}}}};
const unit={name:'Alpha',default_model:'m',models:[model],simple:record([324,648]),npp:{npp:[100,200]},
  group_inputs:{years:[2018,2019],taxa:groups.map(g=>g.id),landings:groups.map(()=>[1,2]),catch:groups.map(()=>[2,4]),
    full_precision_catch:groups.map(()=>[2,4]),discards:groups.map(()=>[1,2]),simple_sppr:groups.map((_,i)=>9*(i+1)),catch_basis_policy:'explicit'}};
model.scopes.all.methods.EwE.catch_bases={catch:record([648,1296]),discards:record([324,648])};
const db={years:[2018,2019],ppr_methods:[{id:'EwE',kind:'model',scopes:['all']},{id:'simple trophic chain',kind:'taxon',scopes:['all']}],
  npp_methods:[{id:'npp'}],global_npp:{id:'fixed',unit_ids:['A'],values:[1000,2000]},units:{A:unit}};
const state={units:['A'],methods:['EwE'],scope:'all',mode:'ppr',npp:'npp',catch_basis:'landings',unidentified:'method',years:db.years};
const snapshot=JSON.stringify({db,state});
const build=(s=state,d=db)=>{const result=context.PPRTrendExtras.scale(d,s,engine.compare(d,s),engine.aggregate);return {result,breakdown:stack.build(d,s,result)};};
const ids=b=>b.layers.filter(l=>!l.other).map(l=>l.group_id);
const checkTotals=({result,breakdown})=>result.points.forEach((p,i)=>{
  if(p.value===null)assert.ok(breakdown.layers.every(l=>l.points[i].value===null),'Unavailable totals leave every layer unavailable');
  else close(breakdown.layers.reduce((sum,l)=>sum+l.points[i].value,0),p.value);
});
let out=build();
assert.deepEqual(copy(ids(out.breakdown)),['g8','g7','g6','g5','g4']);
assert.deepEqual(copy(out.breakdown.layers.map(l=>l.points[0].value)),[8,7,6,5,4,6]);
assert.deepEqual(copy(out.breakdown.layers.map(l=>l.points[1].value)),[16,14,12,10,8,12]);
assert.equal(out.breakdown.layers.at(-1).label,'Other');checkTotals(out);
const selected=groups.map(g=>g.id);
out=build({...state,group_selections:{'A::m':selected.filter(id=>id!=='g1')}});
assert.deepEqual(copy(ids(out.breakdown)),['g8','g7','g6','g5','g4']);
assert.equal(out.breakdown.layers.at(-1).points[0].value,5);checkTotals(out);
out=build({...state,group_selections:{'A::m':selected.filter(id=>id!=='g8')}});
assert.deepEqual(copy(ids(out.breakdown)),['g7','g6','g5','g4','g3']);
assert.equal(out.result.points[0].value,28);assert.equal(out.breakdown.layers.at(-1).points[0].value,3);checkTotals(out);
for(const npp_scope of ['selected','global']){
  out=build({...state,mode:'ratio',npp_scope});checkTotals(out);
  close(out.breakdown.layers[0].points[0].value,npp_scope==='global'?.8:8);
}
out=build({...state,mode:'ratio',npp_scope:'global',global_estimate:true});checkTotals(out);
for(const catch_basis of ['catch','discards']){out=build({...state,catch_basis});checkTotals(out);}
out=build({...state,methods:['simple trophic chain']});checkTotals(out);
assert.deepEqual(copy(ids(out.breakdown)),['g8','g7','g6','g5','g4']);
// Rank over the displayed period rather than replacing labels at each annual peak.
const crossing=copy(db);
crossing.units.A.group_inputs.landings[0]=[100,0];
crossing.units.A.models[0].scopes.all.methods.EwE.ppr=[1215,630];
out=build(state,crossing);assert.deepEqual(copy(ids(out.breakdown)),['g1','g8','g7','g6','g5']);checkTotals(out);
out=build({...state,years:[2019]},crossing);assert.deepEqual(copy(ids(out.breakdown)),['g8','g7','g6','g5','g4']);checkTotals(out);
// Researcher defaults and explicit browser overrides use the existing selection policy.
const reviewed=copy(db);reviewed.units.A.models[0].display_ppr_excluded_group_ids=['g8'];
out=build(state,reviewed);assert.deepEqual(copy(ids(out.breakdown)),['g7','g6','g5','g4','g3']);checkTotals(out);
out=build({...state,group_selections:{'A::m':selected}},reviewed);
assert.deepEqual(copy(ids(out.breakdown)),['g8','g7','g6','g5','g4']);checkTotals(out);
// Original fractional allocation is retained when one of the two groups is unchecked.
const fractional=copy(db),fm=fractional.units.A.models[0];
fm.group_data.mappings[0]=[[0,.25],[7,.75]];
fm.taxon_scopes.all.values[0][0]=56.25;
fm.scopes.all.methods.EwE.ppr=[371.25,742.5];
out=build({...state,group_selections:{'A::m':['g1']}},fractional);
assert.equal(out.result.points[0].value,.25);close(out.breakdown.layers[0].points[0].value,.25);checkTotals(out);
// Missing annual results and NPP never become zero-valued layers.
const missing=copy(db);missing.units.A.models[0].scopes.all.methods.EwE.ppr[0]=null;
out=build(state,missing);assert.equal(out.result.points[0].value,null);checkTotals(out);
missing.units.A.npp.npp[1]=null;
out=build({...state,mode:'ratio',npp_scope:'selected'},missing);checkTotals(out);
out=build({...state,group_selections:{'A::m':[]}});assert.equal(out.result.points[0].value,0);checkTotals(out);
// Signed diagnostics retain the negative group's contribution and scientific flag.
const signed=copy(db),sm=signed.units.A.models[0];
sm.researcher_review={status:'Validated by researcher'};
sm.group_data.scopes.all[0][0]=-9;sm.taxon_scopes.all.values[0][0]=-9;
sm.scopes.all.methods.EwE.status=sm.taxon_scopes.all.status.EwE='FAIL: signed retained values';
sm.scopes.all.methods.EwE.ppr=[306,612];
out=build(state,signed);checkTotals(out);
assert.equal(out.breakdown.layers.at(-1).points[0].value,4);
out=build({...state,group_selections:{'A::m':['g1']}},signed);
assert.equal(out.result.points[0].value,-1);assert.equal(out.breakdown.layers[0].points[0].value,-1);checkTotals(out);
assert.match(out.result.points[0].status,/FAIL/);
assert.deepEqual(copy(stack.bounds(out.breakdown)),[-1,0,-2,0]);
// Same group names in different models are not presumed scientifically equivalent.
const multiple=copy(db);multiple.units.B=copy(unit);multiple.units.B.name='Beta';
out=build({...state,units:['A','B']},multiple);checkTotals(out);
assert.equal(new Set(out.breakdown.layers.filter(l=>!l.other).map(l=>l.id)).size,5);
assert.ok(out.breakdown.layers.filter(l=>!l.other).every(l=>l.label.includes('Alpha')||l.label.includes('Beta')));
// The fixed atlas denominator and group ranking do not include unavailable regions.
multiple.units.B.models[0].scopes.all.methods.EwE.ppr=[null,null];
out=build({...state,units:['A','B'],mode:'ratio',npp_scope:'global'},multiple);checkTotals(out);
assert.ok(out.breakdown.layers.filter(l=>!l.other).every(l=>l.unit_id==='A'));
// Retained totals with missing attribution stay honest in Other.
const noGroups=copy(db);delete noGroups.units.A.models[0].group_data;
out=build(state,noGroups);assert.equal(out.breakdown.layers.length,1);
assert.equal(out.breakdown.layers[0].points[0].value,36);assert.equal(out.breakdown.has_unattributed,true);checkTotals(out);
// Six-decimal taxon rounding cannot accumulate a spurious negative Other layer.
const rounded=copy(db),rm=rounded.units.A.models[0];
rm.group_data.scopes.all[0][0]=1/3;rm.taxon_scopes.all.values[0][0]=.333333;
rm.scopes.all.methods.EwE.ppr=[315.333333,630.666666];
out=build({...state,group_selections:{'A::m':['g1']}},rounded);checkTotals(out);
assert.equal(out.breakdown.layers.at(-1).points[0].value,0);
// The exported components use the same plot units and appear in JSON.
out=build({...state,mode:'ratio',npp_scope:'global'});
out.result.group_breakdown=out.breakdown;
const csv=stack.toCSV(out.result,state,engine.comparisonToCSV).trim().split('\n');
const cells=row=>row.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/).map(c=>c.startsWith('"')?c.slice(1,-1).replaceAll('""','"'):c);
assert.equal(cells(csv[0]).length,cells(csv[1]).length);
cells(csv[1]).slice(-6).map(Number).forEach((v,i)=>close(v,[.8,.7,.6,.5,.4,.6][i]));
assert.equal(JSON.parse(engine.comparisonToJSON(out.result,state)).result.group_breakdown.layers.at(-1).label,'Other');
// Summation-order noise must not create a signed Other band or a negative axis.
const noise=copy(db),nm=noise.units.A.models[0];
const coefficients=[53.400237,53.675261,37.694394,84.984066,26.433194],catches=[352.455,752.533,345.647,650.694,91.29];
nm.group_data.groups=nm.group_data.groups.slice(0,5);
nm.group_data.mappings=coefficients.map((_,i)=>[[i,1]]);
nm.group_data.scopes.all=coefficients.map(v=>[v]);nm.taxon_scopes.all.values=coefficients.map(v=>[v,v]);
noise.units.A.group_inputs.taxa=noise.units.A.group_inputs.taxa.slice(0,5);
noise.units.A.group_inputs.landings=catches.map(v=>[v,v]);
const wet=coefficients.reduce((sum,v,i)=>sum+v*catches[i],0);
nm.scopes.all.methods.EwE.ppr=[wet,wet];
out=build(state,noise);checkTotals(out);
assert.equal(out.breakdown.layers.at(-1).points[0].value,0);
assert.ok(stack.bounds(out.breakdown).every(v=>v>=0),'Rounding noise cannot make a positive PPR chart signed');
// Positive group coefficients rounded to zero must not create negative attribution.
const tiny=copy(db),tinyModel=tiny.units.A.models[0];
tinyModel.group_data.groups=tinyModel.group_data.groups.slice(0,2);
tinyModel.group_data.mappings=[[[0,.5],[1,.5]]];
tinyModel.group_data.scopes.all=[[.0000002],[.0000002]];
tinyModel.taxon_scopes.all.values=[[0,0]];tinyModel.scopes.all.methods.EwE.ppr=[0,0];
tiny.units.A.group_inputs.taxa=['g1'];tiny.units.A.group_inputs.landings=[[1000000,1000000]];
out=build(state,tiny);checkTotals(out);
assert.ok(out.breakdown.layers.every(l=>l.points.every(p=>p.value===0)),'Zero rounded taxon PPR has no artificial positive/negative pair');
// Roundoff grows with the number of taxa, not just the number of plotted layers.
const accumulated=copy(db),am=accumulated.units.A.models[0];
am.group_data.groups=[{id:'big',name:'Big'},{id:'small',name:'Small'}];
am.group_data.scopes.all=[[100],[1]];
am.group_data.mappings=[[[0,1]],...Array.from({length:200},()=>[[1,1]])];
am.taxon_scopes.all.values=[[100,100],...Array.from({length:200},()=>[1,1])];
accumulated.units.A.group_inputs.taxa=Array.from({length:201},(_,i)=>'taxon'+i);
accumulated.units.A.group_inputs.landings=[[1000000,1000000],...Array.from({length:200},()=>[.001004,.001004])];
const accumulatedWet=accumulated.units.A.group_inputs.landings.reduce((s,row,i)=>s+row[0]*(i?1:100),0);
am.scopes.all.methods.EwE.ppr=[accumulatedWet,accumulatedWet];
out=build(state,accumulated);checkTotals(out);
assert.equal(out.breakdown.layers.at(-1).points[0].value,0);
assert.ok(stack.bounds(out.breakdown).every(v=>v>=0),'Many summed taxa cannot create a false signed axis');
// Appending contribution columns must respect quoted multiline CSV fields.
out=build({...state,mode:'ratio',npp_scope:'global'});out.result.group_breakdown=out.breakdown;
out.result.series[0].points[0].npp_source='First source line\nSecond source line';
const multiline=stack.toCSV(out.result,{...state,mode:'ratio'},engine.comparisonToCSV);
assert.ok(multiline.includes('"First source line\nSecond source line"'),'The source field remains intact');
assert.equal(stack.build(db,{...state,methods:['EwE','simple trophic chain']},engine.compare(db,{...state,methods:['EwE','simple trophic chain']})).available,false);
assert.equal(stack.build(db,{...state,mode:'npp'},engine.compare(db,{...state,mode:'npp'})).available,false);
assert.equal(JSON.stringify({db,state}),snapshot,'Presentation leaves retained inputs and selections untouched');
console.log('Top-five reranking, additive PPR/ratios, original weights, gaps, diagnostics and model identity pass.');
