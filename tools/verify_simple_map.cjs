/* Published independent simple-map values must match every graph year/basis/treatment. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const map=require('../PPRAtlas/atlas/network_metrics.js');
const graph=require('../PPRAtlas/atlas/time_series_metrics.js');
const read=relative=>JSON.parse(fs.readFileSync(path.join(root,relative),'utf8'));
const network=read('PPRAtlas/data/network_ppr.json'),trends=read('PPRAtlas/data/time_series.json');
const ids=['global_output','eez_output'].flatMap(directory=>read(`SeaAroundUsExtraction/${directory}/tables/units.json`).map(record=>record.unit_id)).sort();
assert.equal(ids.length,366,'All 366 ecosystem identities must remain in the atlas');
assert.deepEqual(Object.keys(network.simple_units||{}).sort(),ids,'Rebuild the independent simple-map export');
assert.deepEqual(Object.keys(trends.units).sort(),ids,'Graph and map identity sets must agree');
assert.deepEqual(Object.keys(network.units).sort(),Object.keys(read('data/atlas_selection.json').units).sort(),'Independent simple coverage must not expand the selected model pilot');
const finite=v=>typeof v==='number'&&Number.isFinite(v);
const near=(actual,expected,label)=>{
  assert.equal(actual==null,expected==null,label+' availability');
  if(expected!=null)assert.ok(finite(actual)&&Math.abs(actual-expected)<=1e-9+Math.abs(expected)*1e-12,`${label}: ${actual} != ${expected}`);
};
const report={status:'ok',units:ids.length,years:trends.years,bases:['landings','catch','discards'],treatments:['method','zero','simple'],annual_ppr_checks:0,annual_ratio_checks:0,source_hashes_checked:0,missing_catch:[],with_ppr_2019:0,with_regional_ratio_2019:0};
for(const id of ids){
  const unit=network.simple_units[id],graphUnit=trends.units[id];
  assert.equal(new Set(unit.years).size,unit.years.length,id+' unique catch years');
  assert.ok(!Object.hasOwn(unit,'models')&&!Object.hasOwn(unit,'landings'),id+' compact independent annual record');
  if(!unit.years.length){
    report.missing_catch.push(id);
    assert.deepEqual(unit.simple.ppr,[],id+' no fabricated no-catch years');
  }
  for(const [key,relative]of Object.entries(unit.sources)){
    assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,relative))).digest('hex'),unit.source_sha256[key],id+'/'+key+' source hash');
    report.source_hashes_checked++;
  }
  for(const catch_basis of report.bases)for(const unidentified of report.treatments){
    const common={method:'simple trophic chain',scope:'all',catch_basis,unidentified,npp:'ens_median_tC_yr',npp_fill:'observed',uncertainty:true};
    const graphState={...common,units:[id],models:{[id]:'deliberately absent'},allow_gaps:true,years:trends.years};
    const ppr=graph.aggregate(trends,{...graphState,mode:'ppr'}).points;
    const ratios=graph.aggregate(trends,{...graphState,mode:'ratio',npp_scope:'selected'}).points;
    for(const [i,year]of trends.years.entries()){
      const state={...common,year,simple_unit:unit,npp_data:{years:network.npp_years,values:network.npp[id]?.ens_median_tC_yr,metadata:network.npp_metadata[id]}};
      // An absent article/model is deliberately supplied on every evaluation.
      const actual=map.evaluate(undefined,999,{...state,mode:'ppr'});
      const ratio=map.evaluate(undefined,999,{...state,mode:'npp_ratio'});
      const label=[id,year,catch_basis,unidentified].join('/');
      near(actual.value,ppr[i].ppr,label+' PPR carbon');
      near(ratio.value,ratios[i].value,label+' regional PPR/NPP');
      if(finite(actual.value)){
        for(const [mapKey,graphKey]of [['catch','covered_catch'],['total_catch','catch'],['coverage','coverage'],['unidentified_catch','unidentified_catch'],['unidentified_missing_simple_catch','unidentified_missing_simple_catch'],['total_catch_all','total_catch_all'],['total_discards','total_discards']])near(actual[mapKey],ppr[i][graphKey],label+' '+mapKey);
        assert.equal(actual.independent_simple,true,label+' independent provenance');
        assert.equal(actual.sensitivity.status,'not_assessed',label+' fixed-TL uncertainty');
      }
      // The per-unit year lookup must agree with the common graph year axis.
      let record=unidentified==='method'?unit.simple:unit.simple['unidentified_'+unidentified];
      if(catch_basis!=='landings')record=record.catch_bases[catch_basis];
      const localIndex=unit.years.indexOf(year),wet=record.ppr[localIndex];
      near(actual.value,finite(wet)?wet/9:null,label+' single carbon conversion');
      report.annual_ppr_checks++;report.annual_ratio_checks++;
      if(year===2019&&catch_basis==='landings'&&unidentified==='method'){
        if(finite(actual.value))report.with_ppr_2019++;
        if(finite(ratio.value))report.with_regional_ratio_2019++;
        near(map.evaluate({models:[{verified:false}]},0,{...state,mode:'ppr'}).value,actual.value,id+' unverified model cannot gate simple');
        assert.equal(map.evaluate(undefined,0,{...state,scope:'PP',mode:'ppr'}).value,null,id+' All-scope only');
        assert.equal(map.evaluate(undefined,0,{...state,mode:'ratio'}).value,null,id+' model-method comparison remains gated');
      }
    }
  }
}
assert.deepEqual(report.missing_catch.sort(),['HS_018','LME_064']);
assert.equal(report.with_ppr_2019,364);
fs.writeFileSync(path.join(root,'data/simple_map_validation.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
