const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2]||path.join(__dirname,'../../../interactive_map/index.html'),'utf8');
function section(start,end){
  const a=html.indexOf(start),b=html.indexOf(end,a);
  assert(a>=0&&b>a,`Missing map section: ${start}`);
  return html.slice(a,b);
}
const nodes={};
const node=id=>nodes[id]||=({value:'all',children:[],replaceChildren(){this.children=[];},appendChild(child){this.children.push(child);}});
node('search').value='';
const regions=[['A',60],['B',30],['C',10],['missing',null],['outside',900]].map(([unit_id,value])=>({
  unit_id,region_name:unit_id,region_type:unit_id==='B'?'EEZ':'LME',networkResult:{value}
}));
const members=new Set(['A','B','C','missing']);
const rankState={limit:'all',custom:'2'};
const context={console,regions,rankState,selectedId:null,metricState:{mode:'ppr'},byUnit:{},$:node,
  document:{querySelector:s=>node(s.slice(1)),createElement:()=>({})},
  pprColor:()=>'',resultText:r=>r.networkResult.value==null?'Unavailable':`${r.networkResult.value} t C`,
  pct:v=>v==null?'unknown':`${(v*100).toFixed(2)}%`,selectRegion(){},
  network:{units:{}},chosenModels:{}};
vm.createContext(context);
// Use the real review predicate; generated layouts may embed it in a larger
// script block or use a different JavaScript declaration than this harness.
vm.runInContext(fs.readFileSync(path.join(__dirname,'../../project_core/maps/researcher_review.js'),'utf8'),context);
vm.runInContext(section('/* Rank the full chosen geography;','/* Runs after the inherited atlas'),context);
vm.runInContext(section('function regionHasDownload','function renderList()'),context);
vm.runInContext(section('const priorPassRegion=','$(\'rankSetFilter\').value'),context);
vm.runInContext(section('renderList = function()','const originalDetails='),context);
const shares=()=>{
  context.renderList();
  return node('regionList').children.map(row=>{
    const match=row.innerHTML.match(/<small[^>]*>([^<]*cumulative PPR[^<]*)<\/small>/i);
    assert(match,'Each PPR row has a cumulative coverage line below its value');
    return match[1];
  });
};
context.PPRMapRanking.rank(regions,members);
assert.deepEqual(shares(),['60.00% cumulative PPR','90.00% cumulative PPR','100.00% cumulative PPR','Cumulative PPR unavailable']);
assert(node('regionList').children[0].innerHTML.includes('<small>60 t C</small><br><small'), 'Coverage sits beneath PPR with the same small-text styling');
node('typeFilter').value='LME';
assert.deepEqual(shares(),['60.00% cumulative PPR','70.00% cumulative PPR','Cumulative PPR unavailable'],'Type filters retain the full-set denominator');
node('search').value='C';
assert.deepEqual(shares(),['10.00% cumulative PPR'],'Search retains the full-set denominator');
node('search').value='';node('typeFilter').value='all';
rankState.limit='custom';
assert.deepEqual(shares(),['60.00% cumulative PPR','90.00% cumulative PPR'],'Display count retains the full-set denominator');
rankState.limit='all';
const values={A:10,B:60,C:30,missing:null,outside:900};
regions.forEach(r=>r.networkResult.value=values[r.unit_id]);
context.PPRMapRanking.rank(regions,members);
assert.deepEqual(shares(),['60.00% cumulative PPR','90.00% cumulative PPR','100.00% cumulative PPR','Cumulative PPR unavailable'],'New method/year results update order and coverage');
context.PPRMapRanking.rank(regions,null);
assert.deepEqual(shares(),['90.00% cumulative PPR','96.00% cumulative PPR','99.00% cumulative PPR','100.00% cumulative PPR','Cumulative PPR unavailable'],'Changing the ecosystem set updates the denominator');
context.PPRMapRanking.rank(regions,members);
if(html.includes('const reviewedOnly=')){
  context.network.units={A:{models:[{researcher_review:{status:'Validated by researcher'}}]},C:{models:[{researcher_review:{status:'Validated by researcher'}}]}};
  context.chosenModels={A:0,C:0};rankState.limit='validated';
  assert.deepEqual(shares(),['30.00% cumulative PPR','40.00% cumulative PPR'],'Researcher validation filter retains the full-set denominator');
  rankState.limit='all';
}
regions.forEach(r=>r.networkResult.value=r.unit_id==='missing'?null:0);
context.PPRMapRanking.rank(regions,members);
assert(shares().every(s=>s==='Cumulative PPR unavailable'),'Zero totals do not fabricate coverage');
regions.forEach(r=>r.networkResult.value=r.unit_id==='A'?60:r.unit_id==='B'?30:r.unit_id==='C'?30:null);
context.PPRMapRanking.rank(regions,members);
assert.deepEqual(shares(),['50.00% cumulative PPR','75.00% cumulative PPR','100.00% cumulative PPR','Cumulative PPR unavailable'],'Tied rows each add their own contribution');
regions.find(r=>r.unit_id==='C').networkResult.value=-10;
context.PPRMapRanking.rank(regions,members);
assert.deepEqual(shares(),['66.67% cumulative PPR','100.00% cumulative PPR','Cumulative PPR unavailable','Cumulative PPR unavailable'],'Negative provisional results do not create decreasing coverage');
context.metricState.mode='npp';context.renderList();
assert(node('regionList').children.every(row=>!row.innerHTML.includes('cumulative PPR')),'Other metrics do not show misleading PPR percentages');
console.log('Map cumulative PPR passed: row layout, ranking, set/method/year changes, search/type/count/review filters, ties, missing/zero/negative results and non-PPR modes.');

