from pathlib import Path
import json
run=Path(__file__).resolve().parents[1];root=next(p for p in run.parents if (p/'Project.xlsx').exists())
source=root/'regions/LME/LME_014/papers/PAT-2023/models/PAT2024_FalklandShelf_2020_native/model_validation/work/2026-11-14_193033_coordinator_batch_2'
expected=json.loads((source/'inputs/display_exclusions.json').read_text())
# Registration order follows actual staged Groups; all five identities remain exact.
expected['LME_022']=['DivingSeabirds','SurfaceFeedingSeabirds','Seals','ToothedWhales','BaleenWhales']
(run/'inputs/display_exclusions.json').write_text(json.dumps(expected,indent=2),encoding='utf-8')
reason='Reason - The pooled model is proposed for disqualification because unresolved production-budget inconsistencies in six groups cause all three SPPR methods to fail with EE floor ON at 0.1.'
negative=[{'unit_id':'LME_050','default_model':True,'reason_pattern':'geographic fit.*57%'},
 {'unit_id':'LME_024','model_id':'Hernvann_2020_Celtic_Sea_1985','reason':'Reason – unrealistic detritus SPPR'},
 {'unit_id':'LME_026','model_id':'Piroddi_2022_Mediterranean_1995','reason':reason},
 {'unit_id':'LME_026','model_id':'Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114','reason':reason,'source_only':True,'review_only':True}]
(run/'inputs/negative_reviews.json').write_text(json.dumps(negative,indent=2,ensure_ascii=False),encoding='utf-8')
s=(source/'code/check_published_controls.js').read_text()
s=s.replace("const expected=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../inputs/display_exclusions.json'),'utf8'));", "const expected=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../inputs/display_exclusions.json'),'utf8'));\nconst negatives=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../inputs/negative_reviews.json'),'utf8'));\nconst negativeUnits=new Set(negatives.map(item=>item.unit_id));\nresult.scope='Published payload and JavaScript control checks; no browser UI execution';\nresult.browser_UI_checked=false;")
s=s.replace("return {selected:selected(series,{units:Object.keys(expected),models:{},review_filter:'validated'}),", "const actualNegativeUnits=[...new Set(negatives.map(item=>item.unit_id))];\n  assert.deepEqual(selected(series,{units:actualNegativeUnits,models:{},review_filter:'validated'}),[],'Published negative defaults must be excluded');\n  const pooled=negatives.find(item=>item.review_only);\n  assert.deepEqual(selected(series,{units:[pooled.unit_id],models:{[pooled.unit_id]:pooled.model_id},review_filter:'validated'}),[],'Choosing pooled rejected source cannot enter validated filter');\n  return {selected:selected(series,{units:Object.keys(expected),models:{},review_filter:'validated'}),actual_negative_defaults_excluded:true,pooled_candidate_override_excluded:true,")
s=s.replace("assert.equal(review.isValidated(model),u!=='LME_050');", "assert.equal(review.isValidated(model),!negativeUnits.has(u));")
s=s.replace("if(u==='LME_050'){", "if(negativeUnits.has(u)){")
s=s.replace("    assert.match(model.researcher_review.reason,/geographic fit.*57%/);", "    const declaration=negatives.find(item=>item.unit_id===u&&(item.default_model||item.model_id===model.id));\n    assert(declaration,u+' default negative decision not declared');\n    if(declaration.reason_pattern)assert.match(model.researcher_review.reason,new RegExp(declaration.reason_pattern));\n    if(declaration.reason)assert.equal(model.researcher_review.reason,declaration.reason);")
s=s.replace("Object.keys(expected).filter(u=>u!=='LME_050')", "Object.keys(expected).filter(u=>!negativeUnits.has(u))")
s=s.replace("'Published trends filter must include the five positive reviews and exclude LME_050'", "'Published trends filter must retain prior positive reviews, include ICES and exclude all declared negative defaults'")
needle='result.available_cases=availableCases;result.passed=true;'
extra='''result.negative_models=[];
for(const declaration of negatives){
  const unit=db.network.units[declaration.unit_id],trendUnit=series.units[declaration.unit_id];
  assert(unit&&trendUnit,'Negative region missing');
  const modelId=declaration.default_model?unit.models[unit.default_model].id:declaration.model_id;
  const mapMatches=unit.models.filter(m=>m.id===modelId),trendMatches=trendUnit.models.filter(m=>m.id===modelId);
  assert.equal(mapMatches.length,1);assert.equal(trendMatches.length,1);
  const model=mapMatches[0],trend=trendMatches[0],before=JSON.stringify({model,trend});
  assert.deepEqual(model.researcher_review,trend.researcher_review);
  for(const item of [model,trend]){
    assert.equal(item.researcher_review.status,'Disqualified by researcher');
    assert.equal(item.researcher_review.verdict,'MODEL DISQUALIFIED');
    assert.equal(review.isValidated(item),false);
    assert.deepEqual(item.researcher_review.sections,[]);
    assert.deepEqual(item.researcher_review.excluded_group_ids,[]);
    assert.deepEqual(item.display_ppr_excluded_group_ids,[]);
    assert(!item.recorded_review_pending);
    if(declaration.reason)assert.equal(item.researcher_review.reason,declaration.reason);
    if(declaration.reason_pattern)assert.match(item.researcher_review.reason,new RegExp(declaration.reason_pattern));
    if(declaration.source_only)assert.equal(item.researcher_review.review_scope,'model_source');
    if(declaration.review_only){
      assert.equal(item.verified,false);assert.deepEqual(item.scopes,{});
      assert(!('workbook' in item));assert(!('values' in item));
      assert(!item.group_data?.groups?.length,'Rejected review-only source must not borrow group controls');
      assert(item.source.endsWith('/'+modelId+'/model.json'));
    }
  }
  assert.equal(JSON.stringify({model,trend}),before,'Negative checks must not mutate payload');
  result.negative_models.push({unit_id:declaration.unit_id,model_id:modelId,exact_negative_review:true,validated_filter_eligible:false,review_only:!!declaration.review_only});
}
assert(result.units.LME_022.manual_override_pass,'ICES initial exclusions and manual overrides must be exercised');
'''+needle
assert needle in s;s=s.replace(needle,extra)
(run/'code/check_published_controls.js').write_text(s,encoding='utf-8')
