// Execute emitted basemap initialization at the Leaflet boundary, without network access.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const page=process.argv[2]||path.resolve(__dirname,'../../../interactive_map/index.html');
const text=fs.readFileSync(page,'utf8');
for(const match of text.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi))new vm.Script(match[1]);
const start=text.indexOf('const map=L.map('),end=text.indexOf('const regionGroup=',start);
assert(start>=0&&end>start,'map initialization boundary missing');
const raw=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../../common_reference_data/geography/basemaps/ne_50m_land.geojson'),'utf8'));
function run(protocol){
 const state={panes:{},layers:[],active:new Set(),events:{},controls:[],tileCalls:0,container:{style:{}}};
 const map={setView(center,zoom){state.view={center:Array.from(center),zoom};return this;},
  createPane(name){return state.panes[name]={style:{}};},getPane(name){return state.panes[name];},
  getContainer(){return state.container;},addLayer(layer){state.active.add(layer);return this;},
  removeLayer(layer){state.active.delete(layer);return this;},hasLayer(layer){return state.active.has(layer);},
  on(name,callback){state.events[name]=callback;return this;},fire(name,event){state.events[name]?.(event);}};
 const network=()=>{throw Error('basemap geometry must remain bundled');};
 function layer(data,options,url){const item={data,options,url,events:{},adds:0,
  addTo(target){assert.strictEqual(target,map);this.adds++;map.addLayer(this);return this;},
  on(name,callback){this.events[name]=callback;return this;},fire(name){this.events[name]?.({target:this});return this;}};
  state.layers.push(item);return item;}
 const control=options=>({options,addTo(target){assert.strictEqual(target,map);this.node=this.onAdd(target);state.controls.push(this);return this;}});
 control.layers=(bases,overlays,options)=>({bases:{...bases},options,
  addTo(target){assert.strictEqual(target,map);state.switcher=this;return this;},
  removeLayer(item){for(const [name,candidate] of Object.entries(this.bases))if(candidate===item)delete this.bases[name];return this;},
  select(name){const selected=this.bases[name];assert(selected,'available base choice');
   for(const item of Object.values(this.bases))if(item!==selected)map.removeLayer(item);
   selected.addTo(map);map.fire('baselayerchange',{layer:selected,name});}});
 const L={map(id,options){state.options=options;return map;},control,
  DomUtil:{create(){return {style:{},textContent:'',setAttribute(key,value){this[key]=value;}};}},
  geoJSON(data,options){return layer(data,options);},tileLayer(url,options){
   assert(['http:','https:'].includes(protocol),'file mode must not construct a tile layer');state.tileCalls++;return layer(null,options,url);}};
 vm.runInNewContext(text.slice(start,end),{L,location:{protocol},fetch:network,XMLHttpRequest:network},{timeout:10000});
 assert.equal(state.options.minZoom,1);assert.equal(state.options.maxZoom,protocol==='file:'?10:18);
 assert.equal(state.options.worldCopyJump,true);assert.equal(state.options.zoomControl,true);
 assert.deepStrictEqual(state.view,{center:[12,10],zoom:1});
 const land=state.layers.find(item=>item.data),pane=state.panes[land.options.pane];
 assert(pane);assert(Number(pane.style.zIndex)>200&&Number(pane.style.zIndex)<400);
 assert.equal(pane.style.pointerEvents,'none');assert.equal(land.options.interactive,false);
 assert.match(land.options.attribution,/Natural Earth/);assert.match(land.options.attribution,/Sea Around Us/);
 assert.deepStrictEqual(JSON.parse(JSON.stringify(land.data)),raw);
 assert(state.container.style.background);
 const status=state.controls.find(item=>item.node.role==='status')?.node;assert(status,'accessible status');
 if(protocol==='file:'){
  assert.equal(state.tileCalls,0);assert(state.active.has(land));assert.match(status.textContent,/Open map.cmd/);
 }else{
  assert.equal(state.tileCalls,1);const street=state.layers.find(item=>item.url);
  assert.equal(street.url,'https://tile.openstreetmap.org/{z}/{x}/{y}.png');
  assert.equal(street.options.referrerPolicy,'strict-origin-when-cross-origin');
  assert.equal(street.options.maxZoom,18);assert.equal(street.options.opacity,.55);
  assert.match(street.options.attribution,/<a href="https:\/\/www.openstreetmap.org\/copyright">OpenStreetMap contributors<\/a>/);
  assert.match(street.options.attribution,/Sea Around Us/);
  const streetPane=state.panes[street.options.pane];assert(Number(streetPane.style.zIndex)>Number(pane.style.zIndex)&&Number(streetPane.style.zIndex)<400);
  assert.equal(streetPane.style.pointerEvents,'none');assert(state.active.has(street));
  state.switcher.select('Simple land map');assert(state.active.has(land));assert(!state.active.has(street));
  state.switcher.select('Street detail');assert(state.active.has(street));assert(!state.active.has(land));
  street.fire('tileerror');assert(!state.active.has(street));assert(state.active.has(land));assert.match(status.textContent,/unavailable.*simple land map/i);
  assert(!Object.values(state.switcher.bases).includes(street),'failed layer cannot start a retry loop');
  const adds=land.adds;street.fire('tileerror');assert.equal(land.adds,adds);assert.equal(state.tileCalls,1);
 }
}
for(const protocol of ['file:','http:','https:'])run(protocol);
console.log('Basemap smoke passed: JavaScript syntax; file mode makes no tile requests; HTTP(S) street URL/referrer/attribution/zoom; manual switch; error fallback without retries; original embedded land geometry.');

