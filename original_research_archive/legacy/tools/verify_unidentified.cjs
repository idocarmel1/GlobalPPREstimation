/* Compare the actual map and graph exports under every catch treatment. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const map=require('../PPRAtlas/atlas/network_metrics.js');
const graph=require('../PPRAtlas/atlas/time_series_metrics.js');
const network=JSON.parse(fs.readFileSync(path.join(root,'PPRAtlas/data/network_ppr.json'),'utf8'));
const trends=JSON.parse(fs.readFileSync(path.join(root,'PPRAtlas/data/time_series.json'),'utf8'));
const report={status:'ok',year:2019,comparisons:0,bay_of_bengal:{}};
for(const [id,unit] of Object.entries(network.units)) {
  for(const [mi,model] of unit.models.entries()) {
    if(!model.verified)continue;
    for(const [scope,data] of Object.entries(model.scopes)) {
      for(const method of data.methods) {
        // The stand-alone simple graph uses unrounded source catches/TLs, while
        // model books persist rounded coefficients; preserve that existing basis.
        if(method==='simple trophic chain')continue;
        for(const unidentified of ['method','zero','simple']) {
          const state={scope,method,year:report.year,unidentified,mode:'ppr'};
          const actual=map.evaluate(unit,mi,state);
          const expected=graph.aggregate(trends,{...state,units:[id],models:{[id]:model.id},years:[report.year]}).points[0];
          assert.equal(actual.value===null,expected.ppr===null,`${id}/${method}/${scope}/${unidentified}: availability`);
          if(actual.value!==null) {
            assert.ok(Math.abs(actual.value-expected.ppr)<=.001+Math.abs(expected.ppr)*1e-12,
              `${id}/${method}/${scope}/${unidentified}: ${actual.value} vs ${expected.ppr}`);
            assert.ok(Math.abs(actual.unidentified_share-expected.unidentified_share)<1e-8,
              `${id}: affected catch share differs`);
          }
          if(id==='LME_034' && scope==='all' && method==='SPPR_1995_TE0.1') {
            const npp=trends.units[id].npp.ens_median_tC_yr[trends.years.indexOf(report.year)];
            report.bay_of_bengal[unidentified]={ppr_tC:expected.ppr,npp_tC:npp,
              percentage:npp>0?100*expected.ppr/npp:null,affected_share:expected.unidentified_share};
          }
          report.comparisons++;
        }
      }
    }
  }
}
fs.writeFileSync(path.join(root,'data/unidentified_validation.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
