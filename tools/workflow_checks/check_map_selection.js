const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const file=process.argv[2]||path.join(__dirname,'../original_html_layout/index.html');
const html=fs.readFileSync(file,'utf8');
const start=html.indexOf('/* Rank the full chosen geography;'),end=html.indexOf('/* Runs after the inherited atlas',start);
const context={module:{exports:{}}};
vm.runInNewContext(html.slice(start,end),context);
const ranking=context.module.exports;
const regions=[['A',10],['B',30],['C',20],['D',null],['E',40]].map(([unit_id,value])=>({unit_id,networkResult:{value}}));
const members=new Set(['A','B','C','D']);
const selected=limit=>regions.filter(r=>ranking.visible(r,limit,2)).map(r=>r.unit_id).sort();
ranking.rank(regions,members);
assert.deepEqual(selected('custom'),['B','C'],'default selects by displayed metric');
const metricSnapshot=JSON.stringify(regions);
const reference={A:90,B:10,C:null,D:90,E:1000};
ranking.rank(regions,members,reference);
assert.deepEqual(selected('custom'),['A','D'],'reference can select an ecosystem with no displayed result');
assert.deepEqual(selected('1'),['A'],'reference ties select exactly X, with stable unit-ID ordering');
assert.equal(regions.find(r=>r.unit_id==='A').ppr_rank,3,'marker still shows displayed-metric rank');
assert.deepEqual(regions.map(({selection_position,...rest})=>rest),JSON.parse(metricSnapshot).map(({selection_position,...rest})=>rest),'reference selection must not alter metric colors, shares, ranks, or order');
regions.forEach(r=>r.networkResult.value=r.unit_id==='C'?999:0);
ranking.rank(regions,members,reference);
assert.deepEqual(selected('custom'),['A','D'],'changing displayed results preserves reference selection');
assert.deepEqual(selected('all'),['A','B','C','D'],'All includes missing reference values');
assert.deepEqual(selected('0'),[]);
ranking.rank(regions,new Set(['B','C','D']),reference);
assert.deepEqual(selected('custom'),['B','D'],'reference ranks use the selected ecosystem set');
ranking.rank(regions,members);
assert.deepEqual(selected('1'),['C'],'switching back restores metric selection');
// Exercise the page's actual reference calculation: a different year, landings,
// or display setting must not accidentally become the ranking input.
const PPRMetrics=require('../original_html_layout/calculation_modules/network_metrics.js');
const baselineContext={regions:[{unit_id:'A'},{unit_id:'missing'}],PPRMetrics,
  network:{simple_units:{A:{years:[2018,2019],simple:{status:'ok',ppr:[900,450],catch:[10,10],covered_catch:[10,10],
    catch_bases:{catch:{status:'ok',ppr:[1800,900],catch:[20,20],covered_catch:[20,20]}}}}}},
  metricState:{year:2018,mode:'npp',catch_basis:'landings',unidentified:'zero',group_selections:{A:[]}}};
const referenceStart=html.indexOf('const referencePpr2019='),referenceEnd=html.indexOf('const curatedIds=',referenceStart);
vm.runInNewContext(html.slice(referenceStart,referenceEnd)+';this.values=referencePpr2019;',baselineContext);
assert.equal(baselineContext.values.A,100,'2019 all-catch PPR converted once from wet weight to carbon');
assert.equal(baselineContext.values.missing,null,'no reference data remains unavailable');
console.log('Map selection passed: independent reference selection, ties, missing values, set changes, All, and metric ranks/colors preserved.');
