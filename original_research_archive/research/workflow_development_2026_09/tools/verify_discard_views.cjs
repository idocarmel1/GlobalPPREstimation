/* Independent map/graph consistency over actual published three-basis inputs. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const map=require('../PPRAtlas/atlas/network_metrics.js');
const graph=require('../PPRAtlas/atlas/time_series_metrics.js');
const network=JSON.parse(fs.readFileSync(path.join(root,'PPRAtlas/data/network_ppr.json'),'utf8'));
const trends=JSON.parse(fs.readFileSync(path.join(root,'PPRAtlas/data/time_series.json'),'utf8'));
const finite=v=>typeof v==='number'&&Number.isFinite(v);
const near=(a,b,label)=>{assert.equal(a==null,b==null,label+' availability');if(a!=null)assert.ok(Math.abs(a-b)<=.001+Math.abs(b)*1e-11,`${label}: ${a} versus ${b}`);};
const report={status:'ok',comparisons:0,assessed_2019:[],bay_of_bengal:{},bases:['catch','landings','discards'],years:[1950,1998,2019]};
for(const [id,unit]of Object.entries(network.units))for(const [mi,model]of unit.models.entries()){
  if(!model.verified)continue;
  assert.equal(unit.full_precision_catch.length,unit.landings.length);
  for(let t=0;t<unit.landings.length;t++)for(let y=0;y<unit.years.length;y++)near(unit.full_precision_catch[t][y],unit.landings[t][y]+unit.discards[t][y],id+' catch identity');
  for(const [scope,data]of Object.entries(model.scopes))for(const method of data.methods){
    if(method==='simple trophic chain')continue;
    for(const year of report.years)for(const catch_basis of report.bases)for(const unidentified of ['method','zero','simple']){
      const state={scope,method,year,catch_basis,unidentified,mode:'ppr',uncertainty:true};
      const actual=map.evaluate(unit,mi,state);
      const expected=graph.aggregate(trends,{...state,units:[id],models:{[id]:model.id},years:[year]}).points[0];
      const label=[id,model.id,scope,method,year,catch_basis,unidentified].join('/');
      near(actual.value,expected.ppr,label);
      if(finite(actual.value)){
        near(actual.catch,expected.covered_catch,label+' covered');
        near(actual.total_catch,expected.catch,label+' evaluation mass');
        near(actual.sensitivity?.lower,expected.sensitivity?.lower,label+' lower');
        near(actual.sensitivity?.upper,expected.sensitivity?.upper,label+' upper');
        if(catch_basis!=='landings')assert.equal(actual.sensitivity?.hidden,true);
        if(catch_basis==='landings'&&year===2019&&unidentified==='method'&&actual.sensitivity?.status==='assessed')report.assessed_2019.push({unit:id,model:model.id,method,scope,...actual.sensitivity});
      }
      if(id==='LME_034'&&scope==='all'&&method==='SPPR_1995_TE0.1'&&year===2019&&unidentified==='method'){
        const npp=trends.units[id].npp.ens_median_tC_yr[trends.years.indexOf(year)];
        report.bay_of_bengal[catch_basis]={ppr_tC:expected.ppr,npp_tC:npp,percentage:npp>0?100*expected.ppr/npp:null};
      }
      report.comparisons++;
    }
  }
}
fs.writeFileSync(path.join(root,'data/discard_views_validation.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,assessed_2019:report.assessed_2019.length}));
