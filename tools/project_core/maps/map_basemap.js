// This rendering fragment replaces only the historical tile-layer initialization.
const BASEMAP_LAND=__LAND_DATA__;
map.createPane('basemap');
map.getPane('basemap').style.zIndex=250;
map.getPane('basemap').style.pointerEvents='none';
map.getContainer().style.background='#dce9ef';
const landBasemap=L.geoJSON(BASEMAP_LAND,{
  pane:'basemap',interactive:false,bubblingMouseEvents:false,
  style:{color:'#bbc6c0',weight:.5,fillColor:'#e8ede7',fillOpacity:1},
  attribution:'Land: <a href="https://www.naturalearthdata.com/">Natural Earth</a> · <a href="https://www.seaaroundus.org/">Sea Around Us polygons</a>'
}).addTo(map);

let basemapStatusNode;
const basemapStatus=L.control({position:'bottomleft'});
basemapStatus.onAdd=function(){
  basemapStatusNode=L.DomUtil.create('div','leaflet-control');
  basemapStatusNode.style.cssText='max-width:270px;padding:7px 10px;background:rgba(255,255,255,.94);border-radius:4px;color:#304554;font:12px/1.4 system-ui;pointer-events:none';
  basemapStatusNode.setAttribute('role','status');
  basemapStatusNode.setAttribute('aria-live','polite');
  basemapStatusNode.hidden=true;
  return basemapStatusNode;
};
basemapStatus.addTo(map);
function setBasemapStatus(message){
  basemapStatusNode.textContent=message;
  basemapStatusNode.hidden=!message;
}

if(location.protocol==='http:'||location.protocol==='https:'){
  map.createPane('streets');
  map.getPane('streets').style.zIndex=300;
  map.getPane('streets').style.pointerEvents='none';
  const streetBasemap=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
    pane:'streets',maxZoom:18,opacity:.55,
    referrerPolicy:'strict-origin-when-cross-origin',
    attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · Sea Around Us polygons'
  });
  const basemapChoices=L.control.layers({'Street detail':streetBasemap,'Simple land map':landBasemap},null,
    {position:'topright',collapsed:false}).addTo(map);
  map.on('baselayerchange',()=>setBasemapStatus(''));
  streetBasemap.on('tileerror',()=>{
    if(!map.hasLayer(streetBasemap))return;
    map.removeLayer(streetBasemap);
    landBasemap.addTo(map);
    basemapChoices.removeLayer(streetBasemap);
    setBasemapStatus('Street detail is unavailable. Showing simple land map.');
  });
  map.removeLayer(landBasemap);
  streetBasemap.addTo(map);
}else{
  setBasemapStatus('Open map.cmd enables street detail.');
}
