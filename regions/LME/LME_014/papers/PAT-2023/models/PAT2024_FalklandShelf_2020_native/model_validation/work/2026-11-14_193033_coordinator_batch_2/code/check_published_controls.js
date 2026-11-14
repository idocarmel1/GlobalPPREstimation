const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=process.cwd(),pages=['index.html','trends.html'].map(n=>fs.readFileSync(path.join(root,'interactive_map',n),'utf8'));
function payload(page,name){const start=page.indexOf('const '+name+'=')+('const '+name+'=').length;const ends=[page.indexOf(';\n',start),page.indexOf(';</script>',start)].filter(i=>i>=0);return JSON.parse(page.slice(start,Math.min(...ends)));}
const db=payload(pages[0],'DB'),series=payload(pages[1],'SERIES_DB');
const reviewContext={};vm.createContext(reviewContext);vm.runInContext(fs.readFileSync(path.join(root,'tools/project_core/maps/researcher_review.js'),'utf8'),reviewContext);
const review=vm.runInContext('PPRResearcherReview',reviewContext),result={units:{},pages:{}};
const expected=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../inputs/display_exclusions.json'),'utf8'));
for(let i=0;i<pages.length;i++){
  const page=pages[i],start=page.indexOf('/* Shared annual denominator lookup.'),end=page.indexOf('/* Rank the full chosen geography;',start);
  if(i===0){assert(start>=0&&end>start);}
  const scripts=[...page.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)];
  for(const [,script] of scripts)if(script.trim())new vm.Script(script);
  result.pages[i?'trends.html':'index.html']={inline_scripts_parse:true};
}
function checkTrendFilter(page){
  const helperScripts=[...page.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)]
    .map(m=>m[1]).filter(s=>s.includes('/* Additional trend views reuse the existing selected-model calculations. */'));
  assert.equal(helperScripts.length,1,'Expected one embedded trends helper script');
  const helperContext={};vm.createContext(helperContext);vm.runInContext(helperScripts[0],helperContext);
  const extras=vm.runInContext('PPRTrendExtras',helperContext);
  assert.equal(typeof extras.selectedUnits,'function');
  const approved={id:'approved',verified:false,researcher_review:{status:'Validated by researcher'}},
    disqualified={id:'disqualified',verified:true,researcher_review:{status:'Disqualified by researcher'}},
    pending={id:'pending',verified:true,recorded_review_pending:{recorded_status:'Validated by researcher'}};
  const fixture={units:{
    A:{default_model:'approved',models:[approved,disqualified,pending]},
    B:{default_model:1,models:[approved,disqualified]},
    C:{default_model:'pending',models:[pending]},
    D:{default_model:0,models:[{id:'almost',researcher_review:{status:'validated by researcher'}}]}
  }};
  const state={units:['A','B','C','D','missing','A'],models:{},review_filter:'validated'},before=JSON.stringify({fixture,state});
  const selected=(db,options)=>Array.from(extras.selectedUnits(db,options));
  assert.deepEqual(selected(fixture,state),['A'],'Only exact positive reviews of chosen models qualify');
  assert.deepEqual(selected(fixture,{...state,review_filter:'all'}),['A','B','C','D','missing']);
  assert.deepEqual(selected(fixture,{...state,models:{A:'disqualified',B:'approved'}}),['B'],'Model-ID overrides must change eligibility');
  assert.deepEqual(selected(fixture,{...state,models:{A:1,B:0}}),['B'],'Numeric model-index overrides must change eligibility');
  assert.deepEqual(selected(fixture,{...state,models:{A:'absent'}}),[],'Missing chosen model must not inherit another model review');
  assert.equal(JSON.stringify({fixture,state}),before,'Filtering must not mutate selections or review evidence');
  const calculation=page.match(/const\s+calculationState\s*=\s*\(\)\s*=>\s*\(\{[^\n]*PPRTrendExtras\.selectedUnits\(db,\s*state\)[^\n]*\}\);/);
  assert(calculation,'Displayed calculation state must use the selected-model review filter');
  const event=page.match(/\$\('regionReviewFilter'\)\.addEventListener\('change',\(\)=>\{[^{}]*\}\);/);
  assert(event,'Actual review dropdown handler is missing');
  let handler,updates=0;
  const control={value:'validated',addEventListener:(type,fn)=>{assert.equal(type,'change');handler=fn;}};
  const uiState={...state,review_filter:'all'},ui={state:uiState,db:fixture,PPRTrendExtras:extras,
    $:id=>id==='regionReviewFilter'?control:{open:false},update:()=>updates++,renderPicker:()=>{}};
  vm.createContext(ui);vm.runInContext(calculation[0]+'\n'+event[0],ui);
  handler();assert.equal(uiState.review_filter,'validated');assert.equal(updates,1);
  assert.deepEqual(Array.from(vm.runInContext('calculationState().units',ui)),['A']);
  control.value='all';handler();assert.equal(updates,2);
  assert.deepEqual(Array.from(vm.runInContext('calculationState().units',ui)),['A','B','C','D','missing']);
  assert.match(page,/const\s+selection=calculationState\(\);[\s\S]{0,250}PPRTimeSeries\.compare\(db,selection\)/,
    'Trend calculation must consume the filtered unit selection');
  return {selected:selected(series,{units:Object.keys(expected),models:{},review_filter:'validated'}),
    exact_positive_review:true,disqualified_and_pending_excluded:true,chosen_model_overrides:true,
    independent_of_numerical_verified_flag:true,dropdown_handler_and_calculation_wiring:true};
}
result.trend_filter=checkTrendFilter(pages[1]);
if(process.argv.includes('--filter-only')){
  console.log(JSON.stringify({passed:true,scope:'Embedded trend filter behavior and wiring only; publication data checks not run',trend_filter:result.trend_filter}));
  process.exit(0);
}
const start=pages[0].indexOf('/* Shared annual denominator lookup.'),ctx={};vm.createContext(ctx);vm.runInContext(pages[0].slice(start,pages[0].indexOf('/* Rank the full chosen geography;',start)),ctx);
const groups=vm.runInContext('PPRGroups',ctx),metrics=vm.runInContext('PPRMetrics',ctx);
let availableCases=0;
for(const [u,excluded] of Object.entries(expected)){
  const unit=db.network.units[u],idx=unit.default_model,model=unit.models[idx],trend=series.units[u].models.find(m=>m.id===model.id);
  assert.deepEqual(model.researcher_review,trend.researcher_review);
  assert.equal(review.isValidated(model),u!=='LME_050');
  assert.deepEqual(model.display_ppr_excluded_group_ids,excluded);
  assert.deepEqual(trend.display_ppr_excluded_group_ids,excluded);
  if(u==='LME_050'){
    assert.equal(model.researcher_review.verdict,'MODEL DISQUALIFIED');
    assert.match(model.researcher_review.reason,/geographic fit.*57%/);
    assert.equal(model.researcher_review.sections.length,0);
    result.units[u]={validated_filter_eligible:false,exact_negative_review:true};continue;
  }
  const before=JSON.stringify(model),all=(model.group_data?.groups||[]).map(g=>g.id),initial=groups.selection(model),override=groups.selection(model,all);
  assert(all.length>0,u+' missing group controls');
  assert.equal(initial.count,all.length-excluded.length);
  assert.equal(override.count,all.length,'Select all must override initial exclusions');
  for(const name of excluded){assert(!initial.ids.includes(name));assert(override.ids.includes(name));}
  assert.equal(groups.selection(model,[]).count,0);
  let cases=0;
  for(const [scope,data] of Object.entries(model.scopes||{}))for(const method of data.methods||[]){
    const state={unit_id:u,mode:'ppr',scope,method,year:2019,catch_basis:'catch',unidentified:'method',simple_unit:db.network.simple_units[u]};
    const value=metrics.evaluate(unit,idx,state);
    if(Number.isFinite(value.value)){cases++;availableCases++;}
  }
  assert(cases>0,u+' no available displayed method');
  assert.equal(JSON.stringify(model),before,'Controls must not mutate review/scientific payload');
  result.units[u]={validated_filter_eligible:true,default_exclusions:excluded,group_count:all.length,manual_override_pass:true,available_cases:cases};
}
assert(pages[0].includes("reviewedOnly&&!PPRResearcherReview.isValidated"),'Map filter must use exact positive review');
assert.deepEqual(result.trend_filter.selected,Object.keys(expected).filter(u=>u!=='LME_050'),
  'Published trends filter must include the five positive reviews and exclude LME_050');
result.available_cases=availableCases;result.passed=true;
const out=path.resolve(__dirname,'../qa/published_controls.json');fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
