// Exercise actual current embedded numerical modules and exact review payloads.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=process.cwd(),run=path.resolve(__dirname,'..');
const base=JSON.parse(fs.readFileSync(path.join(run,'qa/baseline.json'),'utf8'));
const id='LME_028',modelId='28_646_Guinea_(1998)';
const clone=x=>JSON.parse(JSON.stringify(x));
function load(filename,variable,ending){
  const html=fs.readFileSync(filename,'utf8');
  const prefix='const '+variable+'=',dataStart=html.indexOf(prefix)+prefix.length;
  assert(dataStart>=prefix.length,'Missing '+variable);
  // The map data and its program share one script; end at the JSON object's
  // balanced closing brace, respecting JSON strings and escapes.
  let depth=0,inString=false,escaped=false,dataEnd=-1;
  for(let i=dataStart;i<html.length;i++){
    const c=html[i];
    if(inString){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c==='"')inString=false;continue;}
    if(c==='"')inString=true;
    else if(c==='{'||c==='[')depth++;
    else if(c==='}'||c===']'){depth--;if(depth===0){dataEnd=i+1;break;}}
  }
  assert(dataEnd>dataStart,'Unterminated '+variable);
  const payload=JSON.parse(html.slice(dataStart,dataEnd));
  const context={};vm.createContext(context);
  const start=html.indexOf('/* Shared annual denominator lookup.');
  vm.runInContext(html.slice(start,html.indexOf(ending,start)),context);
  return {html,payload,context};
}
const current=load('interactive_map/trends.html','SERIES_DB','</script>');
const old=load(path.join(base.temporary_rollback,'trends.html'),'SERIES_DB','</script>');
const map=load('interactive_map/index.html','DB','/* Rank the full chosen geography;');
const series=current.context.PPRTimeSeries,db=current.payload;
const model=db.units[id].models.find(m=>m.id===modelId);
assert.equal(model.researcher_review.status,'Disqualified by researcher');
assert.equal(model.researcher_review.researcher_name,'Ido Carmel');
assert.equal(model.researcher_review.review_date,'2026-10-18');
assert.deepEqual(model.display_ppr_excluded_group_ids,[]);
assert.equal(db.units[id].default_model,modelId);
assert(db.units[id].models.some(m=>m.id==='28_726_Guinea_(1985)'&&!m.researcher_review));
const groups=current.context.PPRGroups;
const all=groups.selection(model);
assert.equal(all.count,all.total);
const one=groups.selection(model,[model.group_data.groups[0].id]);
assert.equal(one.count,1);
const extras=require(path.join(root,'tools/project_core/maps/trend_extras.js'));
const beforeIds=base.positive_pairs_before.map(pair=>pair[0]);
const validated=extras.selectedUnits(db,{units:beforeIds,review_filter:'validated'});
assert.deepEqual([...validated].sort(),beforeIds.filter(x=>x!==id).sort());
assert.equal(validated.length,7);
assert(extras.selectedUnits(db,{units:beforeIds,review_filter:'all'}).includes(id));
const cases=[];
for(const [scope,basis,method] of [['inner','catch','new_TE_EEfix'],['all','landings','new_GE'],['all','landings','MC_new_GE'],['all','landings','MC_new_TE_EEfix'],['all','landings','simple trophic chain']]){
  const state={units:[id],mode:'ppr',scope,catch_basis:basis,unidentified:'method',method,years:[2019]};
  const before=old.context.PPRTimeSeries.aggregate(old.payload,state),after=series.aggregate(db,state);
  const a=after.points[0]?.value,b=before.points[0]?.value;
  if(method==='new_TE_EEfix'){
    assert.equal(a,null);assert(Number.isFinite(b));
    assert.match(after.reason+' '+after.excluded.map(x=>x.reason).join(' '),/IMPLAUSIBLE/);
  }else if(method==='MC_new_TE_EEfix')assert.equal(a,null);
  else {assert(Number.isFinite(a));assert(Math.abs(a-b)<=1e-10*Math.max(1,Math.abs(b)));}
  cases.push({scope,basis,method,before:b,after:a,reason:after.reason,excluded:after.excluded});
}
const state={units:validated,mode:'ppr',scope:'all',catch_basis:'catch',unidentified:'method',years:[2019],methods:['new_GE','simple trophic chain']};
const unnormalized=series.compare(db,state);
const normalized=series.compare(db,{...state,baseline:'SPPR_1995_TE0.1'});
assert.equal(unnormalized.normalized,false);assert.equal(normalized.normalized,true);
for(const result of [unnormalized,normalized]){
  assert(!result.included.includes(id));
  for(const row of result.series){
    assert(!row.included.includes(id));assert(!Object.hasOwn(row.model_ids||{},id));
  }
}
const exported=JSON.parse(series.comparisonToJSON(normalized,{...state,baseline:'SPPR_1995_TE0.1'}));
assert(!JSON.stringify(exported.result.model_ids||{}).includes(modelId));
assert(!series.comparisonToCSV(normalized,state).includes(modelId));
const ratioState={...state,mode:'ratio',npp_scope:'global',global_estimate:true};
const raw=series.compare(db,ratioState),scaled=extras.scale(db,ratioState,raw,series.aggregate);
for(const item of scaled.series)for(const point of item.points){
  assert(!point.selected_method_missing_ids.includes(id));
  if(point.scaling_reason)assert.equal(point.value,null);
}
// Rendering the exact current review through its production presentation code.
class Element{constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];this.className='';}appendChild(x){this.children.push(x);return x;}setAttribute(k,v){this[k]=v;}}
const document={createElement:t=>new Element(t),createTextNode:t=>new Element('#text',t)};
const presentation={document};vm.createContext(presentation);
vm.runInContext(fs.readFileSync(path.join(root,'tools/project_core/maps/researcher_review.js'),'utf8'),presentation);
const widget=vm.runInContext('PPRResearcherReview',presentation),panel=new Element('div');
widget.append(panel,model);
const text=e=>e.textContent+e.children.map(text).join('');
assert.equal(panel.children[0].children[0].textContent,'MODEL DISQUALIFIED');
assert.equal(panel.children[0].children[1].textContent,model.researcher_review.reason);
assert.equal(panel.children[0].children[0].className,'researcher-disqualified-name');
assert(!text(panel).includes('Model not yet validated'));
assert.equal(widget.isValidated(model),false);
const mapmodel=map.payload.network.units[id].models.find(m=>m.id===modelId);
assert.deepEqual(mapmodel.researcher_review,model.researcher_review);
const output={target:[id,modelId],validated_units:validated,default_all_groups:all.count,explicit_group_override:one.count,
  diagnostic_availability:cases,normalized_included:normalized.included,unnormalized_included:unnormalized.included,
  current_review_rendered_negative:true,downloads_and_global_scaling_checked:true};
fs.writeFileSync(path.join(run,'qa/view_verification.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify(output,null,2));
