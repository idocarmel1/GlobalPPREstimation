// Read-only replay of the exact functions embedded in the current published view.
// Run from repository root; stdout is a compact JSON evidence record.
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const path='interactive_map/trends.html',bytes=fs.readFileSync(path),s=bytes.toString('utf8');
const assert=require('node:assert/strict');
const cohortPath='research/human/sppr_trophic_level_20261018_validated7/inputs/cohort.json';
const cohortBytes=fs.readFileSync(cohortPath),cohort=JSON.parse(cohortBytes.toString('utf8'));
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(sha(fs.readFileSync('Project.xlsx')),cohort.project_sha256,'Registry changed after cohort capture');
assert(s.includes(`<meta name="ppr-project-sha256" content="${cohort.project_sha256}">`),'Published view has a different registry identity');
for(const row of [...cohort.pairs,...cohort.excluded_pairs])assert.equal(sha(fs.readFileSync(row.validation_report_path)),row.validation_report_sha256,'Signed source changed');
const db=JSON.parse(s.match(/const SERIES_DB=(.*?);<\/script>/s)[1]);
const ctx={};vm.createContext(ctx);const start=s.indexOf('/* Shared annual denominator lookup.');
vm.runInContext(s.slice(start,s.indexOf('</script>',start)),ctx);
const ids=Object.keys(db.units).filter(id=>db.units[id].models.find(m=>m.id===db.units[id].default_model)?.researcher_review?.status==='Validated by researcher');
const expected=cohort.pairs.map(p=>[p.unit_id,p.model_id]).sort();
const actual=ids.map(id=>[id,db.units[id].default_model]).sort();
assert.deepEqual(actual,expected,'Published validated defaults differ from the exact pair cohort');
assert.equal(expected.length,7);
for(const row of cohort.excluded_pairs){
 const m=db.units[row.unit_id]?.models.find(m=>m.id===row.model_id);
 assert.equal(m?.researcher_review?.status,row.status_at_run,'Published excluded-pair review differs');
}
const out={cohort_manifest:cohortPath,cohort_sha256:sha(cohortBytes),project_sha256:cohort.project_sha256,pairs:actual,source:path,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),units:ids,comparisons:[],new_te:[],regions:[]};
const base={mode:'ppr',scope:'all',units:ids,catch_basis:'catch',unidentified:'method'};
for(const basis of ['catch','landings','discards']){
 const o=ctx.PPRTimeSeries.compare(db,{...base,catch_basis:basis,methods:['simple trophic chain'],baseline:'SPPR_1995_TE0.1'});
 out.comparisons.push({basis,included:o.included,excluded:o.excluded,points:o.points.map(p=>({year:p.year,ratio:p.value,ppr_tC:p.ppr,baseline_ppr_tC:p.baseline_ppr,catch:p.catch,covered_catch:p.covered_catch,baseline_covered_catch:p.baseline_covered_catch})),cumulative_ratio:o.points.reduce((a,p)=>a+p.ppr,0)/o.points.reduce((a,p)=>a+p.baseline_ppr,0)});
}
for(const scope of ['all','inner','PP'])for(const method of ['new_TE_EEfix','new_TE_noEEfix']){
 const o=ctx.PPRTimeSeries.aggregate(db,{...base,scope,method,years:[2019]});
 out.new_te.push({scope,method,included:o.included,excluded:o.excluded,points:o.points,reason:o.reason});
}
for(const id of ids){
 const u=db.units[id],m=u.models.find(x=>x.id===u.default_model);
 const o=ctx.PPRTimeSeries.compare(db,{...base,units:[id],years:[2019],methods:['simple trophic chain'],baseline:'SPPR_1995_TE0.1'});
 out.regions.push({id,name:u.name,model_id:m.id,excluded_groups:m.display_ppr_excluded_group_ids,point:o.points[0],flags:m.review_flags});
}
console.log(JSON.stringify(out,null,2));
